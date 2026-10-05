import logging
from typing import Any, AsyncGenerator, Dict, Generator, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from backend.app.agent.nodes import (
    case_synthesizer_node,
    chrono_auditor_node,
    geo_triangulator_node,
    lens_hunter_node,
    scene_deconstructor_node,
)
from backend.app.agent.state import OsintGraphState, create_initial_osint_state
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


def create_osint_graph() -> CompiledStateGraph:
    """Constructs and compiles the TerraSleuth LangGraph OSINT investigative state machine."""
    workflow = StateGraph(OsintGraphState)

    # Register investigative nodes
    workflow.add_node("scene_deconstructor", scene_deconstructor_node)
    workflow.add_node("lens_hunter", lens_hunter_node)
    workflow.add_node("geo_triangulator", geo_triangulator_node)
    workflow.add_node("chrono_auditor", chrono_auditor_node)
    workflow.add_node("refinement_router", refinement_router_node)
    workflow.add_node("case_synthesizer", case_synthesizer_node)

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


def stream_osint_investigation_sync(
    image_path: str,
    image_url: Optional[str] = None,
    context_hint: Optional[str] = None,
    max_budget: int = 8,
    max_refinement_hops: int = 2,
) -> Generator[Dict[str, Any], None, None]:
    """Synchronous generator yielding node execution updates for UI streaming."""
    graph = create_osint_graph()
    initial_state = create_initial_osint_state(
        image_path=image_path,
        image_url=image_url,
        context_hint=context_hint,
        max_budget=max_budget,
        max_refinement_hops=max_refinement_hops,
    )
    for event in graph.stream(initial_state):
        yield event


async def stream_osint_investigation(
    image_path: str,
    image_url: Optional[str] = None,
    context_hint: Optional[str] = None,
    max_budget: int = 8,
    max_refinement_hops: int = 2,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Asynchronous generator yielding node execution updates for FastAPI / SSE streaming."""
    graph = create_osint_graph()
    initial_state = create_initial_osint_state(
        image_path=image_path,
        image_url=image_url,
        context_hint=context_hint,
        max_budget=max_budget,
        max_refinement_hops=max_refinement_hops,
    )
    async for event in graph.astream(initial_state):
        yield event
