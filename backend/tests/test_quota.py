import os
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from backend.app.services.cache_service import CacheService
from backend.app.services.quota_service import QuotaBudgetManager, QuotaExhaustedError
from backend.app.services.serpapi_service import SerpApiService


@pytest.fixture
def temp_cache_service():
    """Create a temporary isolated CacheService instance."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    cache_service = CacheService(db_path=db_path)
    yield cache_service

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


def test_budget_manager_lifecycle():
    """Verify standard QuotaBudgetManager consumption, checks, and reset."""
    manager = QuotaBudgetManager(max_budget=3)
    assert manager.remaining_budget() == 3
    assert manager.consumed_budget() == 0
    assert manager.can_consume(1) is True
    assert manager.can_consume(4) is False

    # Consume 2 credits
    manager.consume(2)
    assert manager.remaining_budget() == 1
    assert manager.consumed_budget() == 2

    # Consume final 1 credit
    manager.consume(1)
    assert manager.remaining_budget() == 0
    assert manager.consumed_budget() == 3
    assert manager.can_consume(1) is False

    # Over-consumption raises QuotaExhaustedError
    with pytest.raises(QuotaExhaustedError, match="SerpApi query budget exhausted"):
        manager.consume(1)

    # Reset
    manager.reset(new_max_budget=5)
    assert manager.remaining_budget() == 5
    assert manager.consumed_budget() == 0


def test_quota_exhaustion_on_live_calls():
    """Verify that SerpApiService triggers the circuit breaker before executing a network request."""
    manager = QuotaBudgetManager(max_budget=1)
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"organic_results": [{"title": "Result 1", "link": "https://example.com"}]}
    mock_client.get.return_value = mock_resp

    service = SerpApiService(
        api_key="mock_test_key_xyz",
        client=mock_client,
        budget_manager=manager,
        use_cache=False,  # Force live calls
    )

    # First call succeeds and consumes 1 credit
    res1 = service.search_google("First query")
    assert len(res1.organic_results) == 1
    assert manager.consumed_budget() == 1
    assert manager.remaining_budget() == 0
    assert mock_client.get.call_count == 1

    # Second call must raise QuotaExhaustedError without calling HTTP client
    with pytest.raises(QuotaExhaustedError, match="budget exhausted"):
        service.search_google("Second query")

    # Confirm network client was not called again
    assert mock_client.get.call_count == 1


def test_cache_hit_bypasses_budget(temp_cache_service):
    """Verify that cached queries (e.g. Golden Mystery targets) NEVER consume budget even if budget is 0."""
    temp_cache_service.seed_golden_cases()

    # Zero budget manager!
    zero_budget_manager = QuotaBudgetManager(max_budget=0)
    assert zero_budget_manager.remaining_budget() == 0

    mock_client = MagicMock()

    service = SerpApiService(
        api_key="mock_key",
        client=mock_client,
        cache_service=temp_cache_service,
        budget_manager=zero_budget_manager,
    )

    # Calling seeded Golden case query should succeed 100% via cache
    lens_res = service.search_lens("https://images.unsplash.com/photo-1570168007204-dfb528c6958f")
    assert len(lens_res.visual_matches) == 2
    assert lens_res.knowledge_graph["title"] == "Gateway of India"

    # Crucial assertion: 0 budget consumed, 0 network calls made!
    assert zero_budget_manager.consumed_budget() == 0
    assert mock_client.get.call_count == 0


def test_force_refresh_consumes_budget_and_triggers_circuit_breaker(temp_cache_service):
    """Verify that force_refresh=True on a cached query attempts a live call and triggers the circuit breaker."""
    temp_cache_service.seed_golden_cases()

    # Budget has 0 credits
    zero_budget_manager = QuotaBudgetManager(max_budget=0)

    service = SerpApiService(
        api_key="mock_key",
        cache_service=temp_cache_service,
        budget_manager=zero_budget_manager,
    )

    # Bypassing cache with force_refresh=True must raise QuotaExhaustedError
    with pytest.raises(QuotaExhaustedError, match="budget exhausted"):
        service.search_lens(
            "https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
            force_refresh=True,
        )
