import operator
import os
import tempfile
from unittest.mock import patch
import pytest

from backend.app.agent.nodes.case_synthesizer import case_synthesizer_node
from backend.app.agent.nodes.chrono_auditor import chrono_auditor_node
from backend.app.agent.nodes.geo_triangulator import geo_triangulator_node
from backend.app.agent.nodes.lens_hunter import lens_hunter_node
from backend.app.agent.nodes.scene_deconstructor import scene_deconstructor_node
from backend.app.agent.state import create_initial_osint_state, merge_lists
from backend.app.models.case import CaseFile, Citation, ClueCategory, GeoCandidate, TimelineEvent, VisualClue
from backend.app.services.cache_service import CacheService


@pytest.fixture
def primed_cache_service():
    """Create a temporary CacheService pre-seeded with the Golden Mystery cases."""
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


def test_chrono_auditor_golden_path(primed_cache_service):
    """Verify chrono_auditor_node extracts timeline events from pre-seeded Google News cache."""
    state = create_initial_osint_state(
        image_path="sample.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        max_budget=5,
    )
    # Populate state with resolved geo candidate from preceding node
    state["geo_candidates"] = [
        GeoCandidate(
            name="Gateway of India",
            address="Apollo Bandar, Colaba, Mumbai, Maharashtra 400001",
            latitude=18.9220,
            longitude=72.8347,
            match_score=0.95,
            engine_source="google_maps",
        )
    ]

    with patch("backend.app.agent.nodes.chrono_auditor.SerpApiService") as mock_serp_cls:
        from backend.app.services.serpapi_service import SerpApiService
        mock_serp_cls.return_value = SerpApiService(api_key=None, cache_service=primed_cache_service)

        update = chrono_auditor_node(state)

        assert update["status"] == "chrono_audited"
        assert update["budget_remaining"] == 4  # Consumed 1 query
        assert len(update["timeline_events"]) >= 1
        assert len(update["citations"]) >= 1
        assert update["timeline_events"][0].is_origin is True
        assert "Gateway of India" in update["timeline_events"][0].title or "Gateway" in update["timeline_events"][0].snippet
        assert update["citations"][0].engine == "google_news"


def test_chrono_auditor_skips_when_budget_zero():
    """Verify chrono_auditor_node skips execution when query budget is 0."""
    state = create_initial_osint_state(image_path="sample.jpg", max_budget=0)
    state["geo_candidates"] = [
        GeoCandidate(name="Gateway of India", latitude=18.9220, longitude=72.8347, match_score=0.9, engine_source="google_maps")
    ]
    update = chrono_auditor_node(state)
    assert update["status"] == "chrono_skipped_budget_exhausted"
    assert update["timeline_events"] == []
    assert update["budget_remaining"] == 0


def test_chrono_auditor_skips_when_no_query():
    """Verify chrono_auditor_node handles empty investigative state gracefully."""
    state = create_initial_osint_state(image_path="sample.jpg", max_budget=5)
    update = chrono_auditor_node(state)
    assert update["status"] == "chrono_skipped_no_query"
    assert update["timeline_events"] == []
    assert update["budget_remaining"] == 5


def test_case_synthesizer_high_confidence():
    """Verify case_synthesizer_node computes high confidence score and compiles CaseFile."""
    state = create_initial_osint_state(
        image_path="sample_gateway.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        max_budget=4,
    )
    # Supply rich forensic findings across all evidence channels
    state["visual_clues"] = [
        VisualClue(category=ClueCategory.ARCHITECTURE, description="Indo-Saracenic basalt arch", confidence=0.95),
        VisualClue(category=ClueCategory.LANDMARK, description="Prominent waterfront pier structure", confidence=0.92),
        VisualClue(category=ClueCategory.SIGNAGE, description="Devanagari script architectural plaque", confidence=0.88),
        VisualClue(category=ClueCategory.INFRASTRUCTURE, description="Black iron harbor bollards", confidence=0.85),
    ]
    state["geo_candidates"] = [
        GeoCandidate(
            name="Gateway of India",
            address="Apollo Bandar, Colaba, Mumbai, Maharashtra 400001",
            latitude=18.9220,
            longitude=72.8347,
            place_id="ChIJbU60Q_bQ5zsRz797rU461QQ",
            match_score=0.95,
            engine_source="google_maps",
            evidence_snippet="Triangulated basalt arch",
        )
    ]
    state["lens_matches"] = [
        {"title": "Gateway of India - Historic Waterfront Arch", "link": "https://en.wikipedia.org/wiki/Gateway_of_India"},
        {"title": "The Taj Mahal Palace, Mumbai", "link": "https://www.tajhotels.com"},
    ]
    state["timeline_events"] = [
        TimelineEvent(
            date="March 1911",
            title="Gateway of India foundation stone laid",
            source="Historical Archives",
            snippet="Built to commemorate the visit of King George V and Queen Mary.",
            is_origin=True,
        ),
        TimelineEvent(
            date="2 weeks ago",
            title="Structural restoration completed",
            source="The Times of India",
            snippet="Laser cleaning of basalt surfaces.",
            is_origin=False,
        ),
    ]
    state["citations"] = [
        Citation(title="Gateway of India Wikipedia", url="https://wikipedia.org", engine="google_lens", snippet="Visual twin match"),
        Citation(title="Gateway of India Maps", url="https://maps.google.com", engine="google_maps", snippet="Coordinates resolved"),
        Citation(title="Restoration Report", url="https://timesofindia.com", engine="google_news", snippet="News confirmation"),
    ]

    update = case_synthesizer_node(state)

    assert update["status"] == "case_closed"
    case_file: CaseFile = update["final_case_file"]
    assert isinstance(case_file, CaseFile)
    assert case_file.confidence_score >= 0.85
    assert case_file.resolved_location is not None
    assert case_file.resolved_location.latitude == 18.9220
    assert case_file.resolved_location.longitude == 72.8347
    assert "Gateway of India" in case_file.title
    assert "OSINT Forensic Dossier" in case_file.case_summary
    assert len(case_file.visual_clues) == 4
    assert len(case_file.timeline) == 2
    assert len(case_file.citations) == 3


def test_case_synthesizer_empty_state_fallback():
    """Verify case_synthesizer_node produces safe low-confidence report on empty investigative state."""
    state = create_initial_osint_state(image_path="mystery_blank.jpg", max_budget=8)
    update = case_synthesizer_node(state)

    assert update["status"] == "case_closed"
    case_file: CaseFile = update["final_case_file"]
    assert isinstance(case_file, CaseFile)
    assert case_file.resolved_location is None
    assert case_file.confidence_score <= 0.20
    assert "Mystery Visual Target" in case_file.title


def test_full_pipeline_sequential_execution(primed_cache_service):
    """Test full sequential 5-node OSINT pipeline execution end-to-end with zero credit usage."""
    current_state = create_initial_osint_state(
        image_path="sample_gateway.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        context_hint="Historic arch waterfront",
        max_budget=7,
    )

    # 1. Scene Deconstructor
    update1 = scene_deconstructor_node(current_state)
    current_state["visual_clues"] = operator.add(current_state["visual_clues"], update1["visual_clues"])
    current_state["status"] = update1["status"]
    assert len(current_state["visual_clues"]) == 4

    # 2. Lens Hunter
    with patch("backend.app.agent.nodes.lens_hunter.SerpApiService") as mock_serp:
        from backend.app.services.serpapi_service import SerpApiService
        mock_serp.return_value = SerpApiService(api_key=None, cache_service=primed_cache_service)
        update2 = lens_hunter_node(current_state)

        current_state["lens_matches"] = merge_lists(current_state["lens_matches"], update2["lens_matches"])
        current_state["citations"] = operator.add(current_state["citations"], update2["citations"])
        current_state["budget_remaining"] = update2["budget_remaining"]
        current_state["status"] = update2["status"]
        assert current_state["budget_remaining"] == 6

    # 3. Geo Triangulator
    with patch("backend.app.agent.nodes.geo_triangulator.SerpApiService") as mock_serp:
        from backend.app.services.serpapi_service import SerpApiService
        mock_serp.return_value = SerpApiService(api_key=None, cache_service=primed_cache_service)
        update3 = geo_triangulator_node(current_state)

        current_state["geo_candidates"] = operator.add(current_state["geo_candidates"], update3["geo_candidates"])
        current_state["citations"] = operator.add(current_state["citations"], update3["citations"])
        current_state["budget_remaining"] = update3["budget_remaining"]
        current_state["status"] = update3["status"]
        assert current_state["budget_remaining"] == 4  # Consumed 2 queries

    # 4. Chrono Auditor
    with patch("backend.app.agent.nodes.chrono_auditor.SerpApiService") as mock_serp:
        from backend.app.services.serpapi_service import SerpApiService
        mock_serp.return_value = SerpApiService(api_key=None, cache_service=primed_cache_service)
        update4 = chrono_auditor_node(current_state)

        current_state["timeline_events"] = operator.add(current_state["timeline_events"], update4["timeline_events"])
        current_state["citations"] = operator.add(current_state["citations"], update4["citations"])
        current_state["budget_remaining"] = update4["budget_remaining"]
        current_state["status"] = update4["status"]
        assert current_state["budget_remaining"] == 3  # Consumed 1 query
        assert len(current_state["timeline_events"]) >= 1

    # 5. Case Synthesizer
    update5 = case_synthesizer_node(current_state)
    current_state["final_case_file"] = update5["final_case_file"]
    current_state["status"] = update5["status"]

    assert current_state["status"] == "case_closed"
    case_file = current_state["final_case_file"]
    assert isinstance(case_file, CaseFile)
    assert case_file.resolved_location.latitude == 18.9220
    assert case_file.resolved_location.longitude == 72.8347
    assert case_file.confidence_score >= 0.85
    assert case_file.serp_queries_executed == 4

    # Check multi-engine citation integrity
    citation_engines = {c.engine for c in case_file.citations}
    assert "google_lens" in citation_engines
    assert "google_maps" in citation_engines
    assert "google_news" in citation_engines
