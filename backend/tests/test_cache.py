import os
import sqlite3
import tempfile
import time
from unittest.mock import MagicMock, patch
import pytest

from backend.app.services.cache_service import CacheService, generate_cache_key
from backend.app.services.serpapi_service import SerpApiService


@pytest.fixture
def temp_cache_service():
    """Create a CacheService using an isolated temporary SQLite database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    cache_service = CacheService(db_path=db_path)
    yield cache_service

    # Cleanup temp file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


def test_cache_key_generation_parameter_order_invariance():
    """Ensure parameters serialized in different orders generate the exact same SHA-256 hash."""
    params_a = {"engine": "google_maps", "q": "Gateway of India", "hl": "en", "type": "search"}
    params_b = {"type": "search", "hl": "en", "engine": "google_maps", "q": "Gateway of India"}

    hash_a = generate_cache_key("google_maps", params_a)
    hash_b = generate_cache_key("google_maps", params_b)

    assert hash_a == hash_b
    assert len(hash_a) == 64  # Valid SHA-256 hex string


def test_cache_key_generation_strips_api_keys():
    """Ensure secret API keys are never included in the cache hash."""
    params_with_key_1 = {"q": "Colaba", "api_key": "secret_key_aaa", "hl": "en"}
    params_with_key_2 = {"q": "Colaba", "api_key": "secret_key_bbb", "hl": "en"}
    params_without_key = {"q": "Colaba", "hl": "en"}

    hash_1 = generate_cache_key("google", params_with_key_1)
    hash_2 = generate_cache_key("google", params_with_key_2)
    hash_clean = generate_cache_key("google", params_without_key)

    assert hash_1 == hash_2 == hash_clean


def test_cache_key_generation_strips_transient_flags():
    """Ensure force_refresh and cache_ttl do not alter the canonical cache key."""
    base_params = {"q": "Mumbai Taj Palace", "hl": "en"}
    transient_params = {"q": "Mumbai Taj Palace", "hl": "en", "force_refresh": True, "ttl_seconds": 3600}

    assert generate_cache_key("google", base_params) == generate_cache_key("google", transient_params)


def test_cache_miss_then_hit(temp_cache_service):
    """Test standard write and read lifecycle."""
    engine = "google_lens"
    params = {"url": "https://example.com/arch.jpg", "hl": "en"}
    payload = {"visual_matches": [{"title": "Historic Gate", "link": "https://example.com"}]}

    # Initially cache should miss
    assert temp_cache_service.get_cached_response(engine, params) is None

    # Save to cache
    q_hash = temp_cache_service.set_cached_response(engine, params, payload)
    assert len(q_hash) == 64

    # Subsequent retrieval must return identical data
    cached_payload = temp_cache_service.get_cached_response(engine, params)
    assert cached_payload == payload


def test_cache_force_refresh_bypasses_cache(temp_cache_service):
    """Test that force_refresh=True ignores existing cached data."""
    engine = "google_maps"
    params = {"q": "Apollo Bandar Mumbai"}
    payload = {"local_results": [{"title": "Gateway of India"}]}

    temp_cache_service.set_cached_response(engine, params, payload)

    # Normal fetch hits cache
    assert temp_cache_service.get_cached_response(engine, params) is not None

    # force_refresh=True yields None (forcing re-fetch)
    assert temp_cache_service.get_cached_response(engine, params, force_refresh=True) is None


def test_cache_ttl_expiry(temp_cache_service):
    """Test that records past their TTL are considered expired."""
    engine = "google_news"
    params = {"q": "Mumbai Arch"}
    payload = {"news_results": [{"title": "Restoration update"}]}

    # Store with TTL of 1 second
    temp_cache_service.set_cached_response(engine, params, payload, ttl_seconds=1)

    # Immediately available
    assert temp_cache_service.get_cached_response(engine, params) == payload

    # Wait for TTL to expire
    time.sleep(1.2)

    # Should now return None
    assert temp_cache_service.get_cached_response(engine, params) is None


def test_golden_cases_seeding_and_retrieval(temp_cache_service):
    """Verify that seed_golden_cases creates the 3 golden cases and pre-caches mock responses."""
    count = temp_cache_service.seed_golden_cases()
    assert count == 3

    cases = temp_cache_service.list_golden_cases()
    assert len(cases) == 3
    case_ids = [c["case_id"] for c in cases]
    assert "case_gateway_mumbai" in case_ids
    assert "case_neuschwanstein" in case_ids
    assert "case_market_scam" in case_ids

    # Verify Gateway of India pre-cached Lens query
    lens_params = {"url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f", "hl": "en"}
    lens_cached = temp_cache_service.get_cached_response("google_lens", lens_params)
    assert lens_cached is not None
    assert len(lens_cached["visual_matches"]) == 2
    assert lens_cached["knowledge_graph"]["title"] == "Gateway of India"

    # Verify Gateway of India pre-cached Maps query
    maps_params = {"q": "Gateway of India Colaba Mumbai", "type": "search", "hl": "en"}
    maps_cached = temp_cache_service.get_cached_response("google_maps", maps_params)
    assert maps_cached is not None
    assert maps_cached["local_results"][0]["gps_coordinates"]["latitude"] == 18.9220


def test_serpapi_service_transparent_caching_defense(temp_cache_service):
    """Verify that SerpApiService transparently returns cached data without making network calls or needing an API key."""
    # Seed the golden demo data
    temp_cache_service.seed_golden_cases()

    # Create SerpApiService using the cache, with NO API key configured!
    service = SerpApiService(api_key=None, cache_service=temp_cache_service)

    # Query the seeded Gateway of India image
    result = service.search_lens("https://images.unsplash.com/photo-1570168007204-dfb528c6958f")

    # Successfully returned parsed Pydantic model without any live API call
    assert len(result.visual_matches) == 2
    assert result.visual_matches[0].title == "Gateway of India - Historic Waterfront Arch"
    assert result.knowledge_graph["title"] == "Gateway of India"

    # Query the seeded Maps candidate
    maps_res = service.search_maps("Gateway of India Colaba Mumbai")
    assert maps_res.total_results == 1
    assert maps_res.candidates[0].latitude == 18.9220
    assert maps_res.candidates[0].longitude == 72.8347
