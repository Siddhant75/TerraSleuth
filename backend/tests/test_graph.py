import os
import tempfile
from unittest.mock import patch
import pytest

from backend.app.agent.graph import (
    create_osint_graph,
    investigate_image,
    should_audit_or_synthesize,
    should_refine_or_synthesize,
    stream_osint_investigation,
    stream_osint_investigation_sync,
)
from backend.app.agent.state import create_initial_osint_state
from backend.app.models.case import CaseFile, GeoCandidate
from backend.app.services.cache_service import CacheService


@pytest.fixture
def primed_cache_service():
    """Create a temporary CacheService pre-seeded with Golden Mystery cases."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    cache_service = CacheService(db_path=db_path)
    cache_service.seed_golden_cases()
    yield cache_service

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


def test_create_osint_graph_structure():
    """Verify that the StateGraph builds and compiles with all required nodes."""
    graph = create_osint_graph()
    assert graph is not None
    # Verify node registration in the graph structure
    node_names = set(graph.nodes.keys())
    assert "scene_deconstructor" in node_names
    assert "lens_hunter" in node_names
    assert "geo_triangulator" in node_names
    assert "chrono_auditor" in node_names
    assert "refinement_router" in node_names
    assert "case_synthesizer" in node_names


def test_conditional_routers():
    """Verify routing logic and circuit breaker invariants."""
    # 1. should_audit_or_synthesize
    state_with_budget = create_initial_osint_state("img.jpg", max_budget=2)
    state_with_budget["budget_remaining"] = 2
    assert should_audit_or_synthesize(state_with_budget) == "chrono_auditor"

    state_no_budget = create_initial_osint_state("img.jpg", max_budget=0)
    state_no_budget["budget_remaining"] = 0
    assert should_audit_or_synthesize(state_no_budget) == "case_synthesizer"

    # 2. should_refine_or_synthesize
    ambiguous_candidate = GeoCandidate(
        name="Vague Monument",
        latitude=10.0,
        longitude=10.0,
        match_score=0.45,  # Low score < 0.60
        engine_source="google_maps",
    )
    strong_candidate = GeoCandidate(
        name="Gateway of India",
        latitude=18.9220,
        longitude=72.8347,
        match_score=0.95,  # High score >= 0.60
        engine_source="google_maps",
    )

    state_ambiguous = create_initial_osint_state("img.jpg", max_budget=5, max_refinement_hops=2)
    state_ambiguous["geo_candidates"] = [ambiguous_candidate]
    state_ambiguous["budget_remaining"] = 3
    state_ambiguous["refinement_hops"] = 0
    assert should_refine_or_synthesize(state_ambiguous) == "refinement_router"

    # Circuit breaker: max hops reached -> must synthesize
    state_ambiguous["refinement_hops"] = 2
    assert should_refine_or_synthesize(state_ambiguous) == "case_synthesizer"

    # Circuit breaker: budget exhausted -> must synthesize
    state_ambiguous["refinement_hops"] = 0
    state_ambiguous["budget_remaining"] = 0
    assert should_refine_or_synthesize(state_ambiguous) == "case_synthesizer"

    # Strong candidate -> no need to refine, synthesize directly
    state_strong = create_initial_osint_state("img.jpg", max_budget=5)
    state_strong["geo_candidates"] = [strong_candidate]
    state_strong["budget_remaining"] = 3
    assert should_refine_or_synthesize(state_strong) == "case_synthesizer"


def test_investigate_image_golden_case(primed_cache_service):
    """Verify full end-to-end OSINT investigation execution against Gateway of India Golden Case."""
    with patch("backend.app.agent.nodes.lens_hunter.SerpApiService") as mock_lens, \
         patch("backend.app.agent.nodes.geo_triangulator.SerpApiService") as mock_geo, \
         patch("backend.app.agent.nodes.chrono_auditor.SerpApiService") as mock_chrono:

        from backend.app.services.serpapi_service import SerpApiService
        mock_service = SerpApiService(api_key=None, cache_service=primed_cache_service)
        mock_lens.return_value = mock_service
        mock_geo.return_value = mock_service
        mock_chrono.return_value = mock_service

        case_file = investigate_image(
            image_path="sample_gateway.jpg",
            image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
            context_hint="Historic arch waterfront",
            max_budget=7,
        )

        assert isinstance(case_file, CaseFile)
        assert case_file.confidence_score >= 0.85
        assert case_file.resolved_location is not None
        assert case_file.resolved_location.latitude == 18.9220
        assert case_file.resolved_location.longitude == 72.8347
        assert "Gateway of India" in case_file.title
        assert len(case_file.visual_clues) >= 4
        assert len(case_file.timeline) >= 1
        assert len(case_file.citations) >= 3

        # Verify multi-engine citation integrity
        engines = {c.engine for c in case_file.citations}
        assert "google_lens" in engines
        assert "google_maps" in engines
        assert "google_news" in engines


def test_investigate_image_zero_budget_circuit_breaker():
    """Verify that graph terminates cleanly with a valid CaseFile even with zero budget."""
    case_file = investigate_image(
        image_path="sample_zero_budget.jpg",
        image_url=None,
        max_budget=0,
    )
    assert isinstance(case_file, CaseFile)
    assert case_file.confidence_score <= 0.20
    assert case_file.resolved_location is None
    assert case_file.serp_queries_executed == 0


def test_stream_osint_investigation_sync(primed_cache_service):
    """Verify synchronous streaming generator yields events for each investigative node."""
    with patch("backend.app.agent.nodes.lens_hunter.SerpApiService") as mock_lens, \
         patch("backend.app.agent.nodes.geo_triangulator.SerpApiService") as mock_geo, \
         patch("backend.app.agent.nodes.chrono_auditor.SerpApiService") as mock_chrono:

        from backend.app.services.serpapi_service import SerpApiService
        mock_service = SerpApiService(api_key=None, cache_service=primed_cache_service)
        mock_lens.return_value = mock_service
        mock_geo.return_value = mock_service
        mock_chrono.return_value = mock_service

        events = list(
            stream_osint_investigation_sync(
                image_path="sample_gateway.jpg",
                image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
                max_budget=7,
            )
        )

        assert len(events) >= 5
        executed_nodes = [list(event.keys())[0] for event in events]
        assert "scene_deconstructor" in executed_nodes
        assert "lens_hunter" in executed_nodes
        assert "geo_triangulator" in executed_nodes
        assert "chrono_auditor" in executed_nodes
        assert "case_synthesizer" in executed_nodes


@pytest.mark.asyncio
async def test_stream_osint_investigation_async(primed_cache_service):
    """Verify asynchronous streaming generator yields events for UI/SSE endpoints."""
    with patch("backend.app.agent.nodes.lens_hunter.SerpApiService") as mock_lens, \
         patch("backend.app.agent.nodes.geo_triangulator.SerpApiService") as mock_geo, \
         patch("backend.app.agent.nodes.chrono_auditor.SerpApiService") as mock_chrono:

        from backend.app.services.serpapi_service import SerpApiService
        mock_service = SerpApiService(api_key=None, cache_service=primed_cache_service)
        mock_lens.return_value = mock_service
        mock_geo.return_value = mock_service
        mock_chrono.return_value = mock_service

        events = []
        async for event in stream_osint_investigation(
            image_path="sample_gateway.jpg",
            image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
            max_budget=7,
        ):
            events.append(event)

        assert len(events) >= 5
        last_event = events[-1]
        assert "case_synthesizer" in last_event
        case_file = last_event["case_synthesizer"]["final_case_file"]
        assert isinstance(case_file, CaseFile)
        assert case_file.confidence_score >= 0.85
