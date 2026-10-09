from enum import Enum
import operator
from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from backend.app.models.case import (
    CaseFile,
    Citation,
    GeoCandidate,
    TimelineEvent,
    VisualClue,
)


class InvestigationIntent(str, Enum):
    """Categorized investigative intent determined dynamically by the swarm."""
    GEOSPATIAL_LANDMARK = "GEOSPATIAL_LANDMARK"
    FASHION_PRODUCT = "FASHION_PRODUCT"
    FRAUD_DISINFORMATION = "FRAUD_DISINFORMATION"
    GENERAL_OBJECT = "GENERAL_OBJECT"


class DetectedObject(BaseModel):
    """A discrete visual object detected and segmented from the input image."""
    label: str
    category: str = "apparel"
    bounding_box: List[float] = Field(..., description="[ymin, xmin, ymax, xmax] normalized coordinates")
    confidence: float = 0.90
    lens_match: Optional[Dict[str, Any]] = None


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

    # Human-In-The-Loop (HITL) Directives & Object Filters
    user_directive: Optional[str]
    selected_object_labels: Optional[List[str]]

    # Dynamic Intent & Multi-Object Decomposition
    intent: Optional[InvestigationIntent]
    detected_objects: Annotated[List[DetectedObject], merge_lists]
    itemized_dossier: Annotated[List[Dict[str, Any]], merge_lists]

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
    gemini_api_key: Optional[str]
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
    gemini_api_key: Optional[str] = None,
    user_directive: Optional[str] = None,
    selected_object_labels: Optional[List[str]] = None,
) -> OsintGraphState:
    """Create a pristine initial OsintGraphState for an investigative run."""
    return {
        "image_path": image_path,
        "image_url": image_url,
        "context_hint": context_hint,
        "user_directive": user_directive,
        "selected_object_labels": selected_object_labels,
        "intent": None,
        "detected_objects": [],
        "itemized_dossier": [],
        "api_key": api_key,
        "gemini_api_key": gemini_api_key,
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
