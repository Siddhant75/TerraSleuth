import operator
import os
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from backend.app.agent.nodes.geo_triangulator import geo_triangulator_node
from backend.app.agent.nodes.lens_hunter import lens_hunter_node
from backend.app.agent.nodes.scene_deconstructor import scene_deconstructor_node
from backend.app.agent.state import create_initial_osint_state, merge_lists
from backend.app.models.case import ClueCategory, VisualClue
from backend.app.services.cache_service import CacheService


@pytest.fixture
def primed_cache_service():
    """Create a temporary CacheService seeded with the Golden Mystery cases."""
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


def test_lens_hunter_node_golden_case(primed_cache_service):
    """Test lens_hunter_node against seeded Gateway of India image."""
    state = create_initial_osint_state(
        image_path="sample.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        max_budget=5,
    )

    with patch("backend.app.agent.nodes.lens_hunter.SerpApiService") as mock_serp_cls:
        # Wire mock to use the primed cache service
        from backend.app.services.serpapi_service import SerpApiService
        real_service = SerpApiService(api_key=None, cache_service=primed_cache_service)
        mock_serp_cls.return_value = real_service

        update = lens_hunter_node(state)

        assert update["status"] == "lens_searched"
        assert update.get("budget_remaining") == 4
        assert len(update["lens_matches"]) >= 2
        assert len(update["citations"]) >= 2
        assert any("Gateway of India" in m.get("title", "") for m in update["lens_matches"])
        assert update["citations"][0].engine == "google_lens"


def test_lens_hunter_node_skips_when_budget_zero():
    """Verify lens_hunter_node skips execution if query budget is 0."""
    state = create_initial_osint_state(
        image_path="sample.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        max_budget=0,
    )
    update = lens_hunter_node(state)
    assert update["status"] == "lens_skipped_budget_exhausted"
    assert update["lens_matches"] == []
    assert update.get("budget_remaining") == 0


def test_lens_hunter_node_skips_when_no_image_url():
    """Verify lens_hunter_node handles local-only image gracefully."""
    state = create_initial_osint_state(
        image_path="sample_local.jpg",
        image_url=None,
        max_budget=5,
    )
    update = lens_hunter_node(state)
    assert update["status"] == "lens_skipped_no_url"
    assert update.get("budget_remaining") == 5


def test_geo_triangulator_node_golden_case(primed_cache_service):
    """Test geo_triangulator_node resolving Gateway of India coordinates."""
    state = create_initial_osint_state(
        image_path="sample.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        max_budget=5,
    )
    # Populate state with Lens match from previous step
    state["lens_matches"] = [
        {"title": "Gateway of India Colaba Mumbai - Historic Waterfront Arch", "link": "https://example.com"}
    ]

    with patch("backend.app.agent.nodes.geo_triangulator.SerpApiService") as mock_serp_cls:
        from backend.app.services.serpapi_service import SerpApiService
        real_service = SerpApiService(api_key=None, cache_service=primed_cache_service)
        mock_serp_cls.return_value = real_service

        update = geo_triangulator_node(state)

        assert update["status"] == "geo_triangulated"
        assert len(update["geo_candidates"]) >= 1
        assert update["budget_remaining"] == 4  # Consumed 1 query
        top_candidate = update["geo_candidates"][0]
        assert top_candidate.latitude == 18.9220
        assert top_candidate.longitude == 72.8347
        assert "Gateway of India" in top_candidate.name
        assert len(update["citations"]) >= 1
        assert update["citations"][0].engine == "google_maps"


def test_geo_triangulator_node_skips_when_budget_zero():
    """Verify geo_triangulator_node skips when budget is 0."""
    state = create_initial_osint_state(image_path="sample.jpg", max_budget=0)
    update = geo_triangulator_node(state)
    assert update["status"] == "geo_skipped_budget_exhausted"
    assert update["geo_candidates"] == []
    assert update.get("budget_remaining") == 0


def test_multi_node_sequential_accumulation(primed_cache_service):
    """Simulate sequential pipeline execution: SceneDeconstructor -> LensHunter -> GeoTriangulator."""
    current_state = create_initial_osint_state(
        image_path="sample_gateway.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        context_hint="Historic arch waterfront",
        max_budget=6,
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
        assert len(current_state["lens_matches"]) >= 2
        assert len(current_state["citations"]) >= 2
        assert current_state["budget_remaining"] == 5

    # 3. Geo Triangulator
    with patch("backend.app.agent.nodes.geo_triangulator.SerpApiService") as mock_serp:
        from backend.app.services.serpapi_service import SerpApiService
        mock_serp.return_value = SerpApiService(api_key=None, cache_service=primed_cache_service)
        update3 = geo_triangulator_node(current_state)

        current_state["geo_candidates"] = operator.add(current_state["geo_candidates"], update3["geo_candidates"])
        current_state["citations"] = operator.add(current_state["citations"], update3["citations"])
        current_state["budget_remaining"] = update3["budget_remaining"]
        current_state["status"] = update3["status"]

        assert len(current_state["geo_candidates"]) >= 1
        assert current_state["geo_candidates"][0].latitude == 18.9220
        assert current_state["budget_remaining"] == 3  # Consumed 2 spatial queries
        # Combined citations from both Lens and Maps!
        assert len(current_state["citations"]) >= 3
        citation_engines = {c.engine for c in current_state["citations"]}
        assert "google_lens" in citation_engines
        assert "google_maps" in citation_engines
