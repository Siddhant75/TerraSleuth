import logging
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from backend.app.agent.nodes import (
    case_synthesizer_node,
    chrono_auditor_node,
    geo_triangulator_node,
    lens_hunter_node,
    scene_deconstructor_node,
)
from backend.app.agent.nodes.swarm_nodes import (
    arbiter_node,
    fashion_hunter_node,
    hunter_node,
    skeptic_node,
)
from backend.app.agent.state import (
    InvestigationIntent,
    OsintGraphState,
    create_initial_osint_state,
)
from backend.app.agent.tools import configure_serpapi_client, reset_serpapi_client_context
from backend.app.models.case import CaseFile

logger = logging.getLogger(__name__)


def refinement_router_node(state: OsintGraphState) -> Dict[str, Any]:
    """Circuit breaker node: Increments refinement hops and flags active disambiguation cycle."""
    hops = state.get("refinement_hops", 0)
    logger.info("Disambiguation loop triggered: incrementing refinement_hops from %d to %d", hops, hops + 1)
    return {
        "refinement_hops": hops + 1,
        "status": "refining_coordinates",
    }


def swarm_refinement_router_node(state: OsintGraphState) -> Dict[str, Any]:
    """Circuit breaker node for dialectical swarm: Increments refinement hops and decrements budget."""
    hops = state.get("refinement_hops", 0)
    budget = state.get("budget_remaining", 0)
    logger.info(
        "Dialectical refinement cycle triggered: hops %d -> %d, budget %d -> %d",
        hops,
        hops + 1,
        budget,
        max(0, budget - 1),
    )
    return {
        "refinement_hops": hops + 1,
        "budget_remaining": max(0, budget - 1),
        "status": "refining_debate",
    }


def should_audit_or_synthesize(state: OsintGraphState) -> str:
    """Conditional router after geo triangulation.
    
    If query budget remains, routes to chronological audit.
    If budget is exhausted, breaks directly to case synthesis.
    """
    budget = state.get("budget_remaining", 0)
    if budget > 0:
        return "chrono_auditor"
    logger.info("Budget exhausted (%d remaining): skipping directly to case_synthesizer", budget)
    return "case_synthesizer"


def should_refine_or_synthesize(state: OsintGraphState) -> str:
    """Conditional router after chronological audit.
    
    Evaluates if coordinates are ambiguous (top match score < 0.6) and
    refinement budget / hops allow a disambiguation pass.
    """
    candidates = state.get("geo_candidates", [])
    top_score = candidates[0].match_score if candidates else 0.0
    hops = state.get("refinement_hops", 0)
    max_hops = state.get("max_refinement_hops", 2)
    budget = state.get("budget_remaining", 0)

    # Disambiguation criteria: weak candidate, remaining budget, and hop limit not reached
    if candidates and top_score < 0.60 and hops < max_hops and budget > 0:
        logger.info(
            "Low spatial confidence (top score=%.2f < 0.60, hops=%d/%d): initiating refinement loop",
            top_score,
            hops,
            max_hops,
        )
        return "refinement_router"

    return "case_synthesizer"


def route_after_hunter(state: OsintGraphState) -> str:
    """Conditional router after Hunter agent hypothesis generation."""
    intent = state.get("intent")
    if intent in (InvestigationIntent.FASHION_PRODUCT, "FASHION_PRODUCT"):
        logger.info("Fashion intent detected: routing to fashion_hunter for multi-object decomposition")
        return "fashion_hunter"
    return "skeptic"


def should_refine_debate(state: OsintGraphState) -> str:
    """Conditional router after Arbiter audit in dialectical swarm mode.
    
    If intent is fashion or status is 'fraud_unmasked', halts debate immediately to synthesizer.
    If audit_score < 0.70, hops < max_hops, and budget > 0, loops back to hunter.
    Otherwise, circuit breaker forces transition to case_synthesizer.
    """
    status = state.get("status", "")
    intent = state.get("intent")
    audit_score = state.get("audit_score", 1.0)
    hops = state.get("refinement_hops", 0)
    max_hops = state.get("max_refinement_hops", 2)
    budget = state.get("budget_remaining", 0)

    if intent in (InvestigationIntent.FASHION_PRODUCT, "FASHION_PRODUCT"):
        logger.info("Fashion catalog certified: routing directly to case_synthesizer.")
        return "case_synthesizer"

    if status == "fraud_unmasked":
        logger.info("Fraud conclusively unmasked by Arbiter: routing directly to case_synthesizer.")
        return "case_synthesizer"

    if audit_score < 0.70 and hops < max_hops and budget > 0:
        logger.info(
            "Debate requires refinement (audit_score=%.2f < 0.70, hops=%d/%d, budget=%d): routing to swarm_refinement_router",
            audit_score,
            hops,
            max_hops,
            budget,
        )
        return "swarm_refinement_router"

    return "case_synthesizer"


def create_osint_graph() -> CompiledStateGraph:
    """Constructs and compiles the TerraSleuth LangGraph OSINT investigative state machine."""
    workflow = StateGraph(OsintGraphState)

    # Register all investigative and dialectical nodes
    workflow.add_node("scene_deconstructor", scene_deconstructor_node)
    workflow.add_node("lens_hunter", lens_hunter_node)
    workflow.add_node("geo_triangulator", geo_triangulator_node)
    workflow.add_node("chrono_auditor", chrono_auditor_node)
    workflow.add_node("refinement_router", refinement_router_node)
    workflow.add_node("case_synthesizer", case_synthesizer_node)

    # Dialectical Swarm Nodes
    workflow.add_node("hunter", hunter_node)
    workflow.add_node("skeptic", skeptic_node)
    workflow.add_node("arbiter", arbiter_node)
    workflow.add_node("swarm_refinement_router", swarm_refinement_router_node)

    # Linear investigative spine
    workflow.add_edge(START, "scene_deconstructor")
    workflow.add_edge("scene_deconstructor", "lens_hunter")
    workflow.add_edge("lens_hunter", "geo_triangulator")

    # Conditional routing after spatial triangulation
    workflow.add_conditional_edges(
        "geo_triangulator",
        should_audit_or_synthesize,
        {
            "chrono_auditor": "chrono_auditor",
            "case_synthesizer": "case_synthesizer",
        },
    )

    # Conditional routing after chronological audit
    workflow.add_conditional_edges(
        "chrono_auditor",
        should_refine_or_synthesize,
        {
            "refinement_router": "refinement_router",
            "case_synthesizer": "case_synthesizer",
        },
    )

    # Refinement router loops back into geo_triangulator
    workflow.add_edge("refinement_router", "geo_triangulator")

    # Final dossier synthesis completes investigation
    workflow.add_edge("case_synthesizer", END)

    compiled_graph = workflow.compile()
    logger.info("Compiled TerraSleuth OSINT StateGraph successfully")
    return compiled_graph


def create_dialectical_osint_graph() -> CompiledStateGraph:
    """Constructs the Level 5 Dialectical Multi-Agent Swarm (Hunter, Skeptic, Arbiter) StateGraph."""
    workflow = StateGraph(OsintGraphState)

    workflow.add_node("scene_deconstructor", scene_deconstructor_node)
    workflow.add_node("hunter", hunter_node)
    workflow.add_node("fashion_hunter", fashion_hunter_node)
    workflow.add_node("skeptic", skeptic_node)
    workflow.add_node("arbiter", arbiter_node)
    workflow.add_node("swarm_refinement_router", swarm_refinement_router_node)
    workflow.add_node("case_synthesizer", case_synthesizer_node)

    workflow.add_edge(START, "scene_deconstructor")
    workflow.add_edge("scene_deconstructor", "hunter")
    workflow.add_conditional_edges(
        "hunter",
        route_after_hunter,
        {
            "fashion_hunter": "fashion_hunter",
            "skeptic": "skeptic",
        },
    )
    workflow.add_edge("fashion_hunter", "skeptic")
    workflow.add_edge("skeptic", "arbiter")

    workflow.add_conditional_edges(
        "arbiter",
        should_refine_debate,
        {
            "swarm_refinement_router": "swarm_refinement_router",
            "case_synthesizer": "case_synthesizer",
        },
    )

    workflow.add_edge("swarm_refinement_router", "hunter")
    workflow.add_edge("case_synthesizer", END)

    compiled_graph = workflow.compile()
    logger.info("Compiled TerraSleuth Dialectical OSINT StateGraph successfully")
    return compiled_graph


def investigate_image(
    image_path: str,
    image_url: Optional[str] = None,
    context_hint: Optional[str] = None,
    max_budget: int = 8,
    max_refinement_hops: int = 2,
) -> CaseFile:
    """Execute the OSINT investigation end-to-end and return the compiled CaseFile."""
    graph = create_osint_graph()
    initial_state = create_initial_osint_state(
        image_path=image_path,
        image_url=image_url,
        context_hint=context_hint,
        max_budget=max_budget,
        max_refinement_hops=max_refinement_hops,
    )
    final_state = graph.invoke(initial_state)
    case_file = final_state.get("final_case_file")
    if not case_file:
        raise RuntimeError("Investigation concluded without compiling a valid CaseFile")
    return case_file


def investigate_image_dialectical(
    image_path: str,
    image_url: Optional[str] = None,
    context_hint: Optional[str] = None,
    max_budget: int = 8,
    max_refinement_hops: int = 2,
) -> CaseFile:
    """Execute the dialectical OSINT swarm investigation end-to-end and return the compiled CaseFile."""
    graph = create_dialectical_osint_graph()
    initial_state = create_initial_osint_state(
        image_path=image_path,
        image_url=image_url,
        context_hint=context_hint,
        max_budget=max_budget,
        max_refinement_hops=max_refinement_hops,
    )
    final_state = graph.invoke(initial_state)
    case_file = final_state.get("final_case_file")
    if not case_file:
        raise RuntimeError("Dialectical investigation concluded without compiling a valid CaseFile")
    return case_file


def stream_osint_investigation_sync(
    image_path: str,
    image_url: Optional[str] = None,
    context_hint: Optional[str] = None,
    max_budget: int = 8,
    max_refinement_hops: int = 2,
    dialectical: bool = False,
    api_key: Optional[str] = None,
    force_refresh: bool = False,
    gemini_api_key: Optional[str] = None,
    user_directive: Optional[str] = None,
    selected_object_labels: Optional[List[str]] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Synchronous generator yielding node execution updates for UI streaming."""
    configure_serpapi_client(api_key=api_key, force_refresh=force_refresh)
    try:
        graph = create_dialectical_osint_graph() if dialectical else create_osint_graph()
        initial_state = create_initial_osint_state(
            image_path=image_path,
            image_url=image_url,
            context_hint=context_hint,
            max_budget=max_budget,
            max_refinement_hops=max_refinement_hops,
            api_key=api_key,
            force_refresh=force_refresh,
            gemini_api_key=gemini_api_key,
            user_directive=user_directive,
            selected_object_labels=selected_object_labels,
        )
        for event in graph.stream(initial_state):
            yield event
    finally:
        reset_serpapi_client_context()


def stream_dialectical_investigation_sync(
    image_path: str,
    image_url: Optional[str] = None,
    context_hint: Optional[str] = None,
    max_budget: int = 8,
    max_refinement_hops: int = 2,
    api_key: Optional[str] = None,
    force_refresh: bool = False,
    gemini_api_key: Optional[str] = None,
    user_directive: Optional[str] = None,
    selected_object_labels: Optional[List[str]] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Synchronous generator yielding dialectical swarm updates for the UI."""
    return stream_osint_investigation_sync(
        image_path=image_path,
        image_url=image_url,
        context_hint=context_hint,
        max_budget=max_budget,
        max_refinement_hops=max_refinement_hops,
        dialectical=True,
        api_key=api_key,
        force_refresh=force_refresh,
        gemini_api_key=gemini_api_key,
        user_directive=user_directive,
        selected_object_labels=selected_object_labels,
    )


async def stream_osint_investigation(
    image_path: str,
    image_url: Optional[str] = None,
    context_hint: Optional[str] = None,
    max_budget: int = 8,
    max_refinement_hops: int = 2,
    dialectical: bool = False,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Asynchronous generator yielding node execution updates for FastAPI / SSE streaming."""
    graph = create_dialectical_osint_graph() if dialectical else create_osint_graph()
    initial_state = create_initial_osint_state(
        image_path=image_path,
        image_url=image_url,
        context_hint=context_hint,
        max_budget=max_budget,
        max_refinement_hops=max_refinement_hops,
    )
    async for event in graph.astream(initial_state):
        yield event
