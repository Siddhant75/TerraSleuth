import operator
from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict

from backend.app.models.case import (
    CaseFile,
    Citation,
    GeoCandidate,
    TimelineEvent,
    VisualClue,
)


def merge_lists(left: list, right: list) -> list:
    """Safely merge two lists without duplicating identical elements, guaranteeing functional immutability."""
    if not left:
        return list(right) if right else []
    if not right:
        return list(left) if left else []
    return list(left) + [item for item in right if item not in left]


class OsintGraphState(TypedDict):
    """The central state schema for the TerraSleuth LangGraph investigative state machine.
    
    Fields marked with `Annotated[..., operator.add]` or `merge_lists` use LangGraph
    reducers to accumulate findings across distributed subagent nodes.
    Scalar fields (budget_remaining, refinement_hops, status, error, final_case_file)
    use standard last-write-wins semantics.
    """

    # Investigative Inputs
    image_path: str
    image_url: Optional[str]
    context_hint: Optional[str]

    # Accumulated OSINT Evidence (Reducers)
    visual_clues: Annotated[List[VisualClue], operator.add]
    geo_candidates: Annotated[List[GeoCandidate], operator.add]
    timeline_events: Annotated[List[TimelineEvent], operator.add]
    lens_matches: Annotated[List[Dict[str, Any]], merge_lists]
    citations: Annotated[List[Citation], operator.add]

    # Level 5 Dialectical Swarm Evidence & Debates
    hunter_hypotheses: Annotated[List[str], merge_lists]
    skeptic_critiques: Annotated[List[str], merge_lists]
    debate_history: Annotated[List[Dict[str, Any]], merge_lists]
    audit_score: float

    # Deterministic Circuit Breakers & Query Budgets
    initial_budget: int
    budget_remaining: int
    refinement_hops: int
    max_refinement_hops: int

    # Lifecycle State
    status: str
    error: Optional[str]

    # Session Credentials & Network Mode (Isolated per run)
    api_key: Optional[str]
    force_refresh: bool

    # Final Dossier Synthesis
    final_case_file: Optional[CaseFile]


def create_initial_osint_state(
    image_path: str,
    image_url: Optional[str] = None,
    context_hint: Optional[str] = None,
    max_budget: int = 8,
    max_refinement_hops: int = 2,
    api_key: Optional[str] = None,
    force_refresh: bool = False,
) -> OsintGraphState:
    """Create a pristine initial OsintGraphState for an investigative run."""
    return {
        "image_path": image_path,
        "image_url": image_url,
        "context_hint": context_hint,
        "api_key": api_key,
        "force_refresh": force_refresh,
        "visual_clues": [],
        "geo_candidates": [],
        "timeline_events": [],
        "lens_matches": [],
        "citations": [],
        "hunter_hypotheses": [],
        "skeptic_critiques": [],
        "debate_history": [],
        "audit_score": 1.0,
        "initial_budget": max(0, max_budget),
        "budget_remaining": max(0, max_budget),
        "refinement_hops": 0,
        "max_refinement_hops": max(0, max_refinement_hops),
        "status": "initialized",
        "error": None,
        "final_case_file": None,
    }
