import contextvars
import os
import pytest
import httpx
from backend.app.services.serpapi_service import (
    SerpApiService,
    SerpApiConfigError,
    SerpApiError,
    SerpApiTimeoutError,
)
from backend.app.agent.tools import (
    configure_serpapi_client,
    get_current_serpapi_client,
    reset_serpapi_client_context,
    _default_serp,
)


def test_serpapi_get_api_key_precedence(monkeypatch):
    # Case 1: Constructor argument takes highest priority
    monkeypatch.setenv("SERPAPI_API_KEY", "env_key_456")
    service = SerpApiService(api_key="constructor_key_123", use_cache=False)
    assert service._get_api_key() == "constructor_key_123"

    # Case 2: Environment variable used if constructor arg is None
    service_env = SerpApiService(api_key=None, use_cache=False)
    assert service_env._get_api_key() == "env_key_456"

    # Case 3: Empty / placeholder key raises SerpApiConfigError
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    service_empty = SerpApiService(api_key="", use_cache=False)
    with pytest.raises(SerpApiConfigError) as exc_info:
        service_empty._get_api_key()
    assert "SERPAPI_API_KEY is not configured" in str(exc_info.value)

    service_placeholder = SerpApiService(api_key="your_serpapi_key_here", use_cache=False)
    with pytest.raises(SerpApiConfigError) as exc_info:
        service_placeholder._get_api_key()
    assert "SERPAPI_API_KEY is not configured" in str(exc_info.value)


def test_serpapi_sanitize_message_masks_key(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "secret_live_key_xyz987")
    service = SerpApiService(api_key="secret_live_key_xyz987", use_cache=False)

    raw_msg = "Request to https://serpapi.com/search?api_key=secret_live_key_xyz987&engine=google failed"
    sanitized = service._sanitize_message(raw_msg)

    assert "secret_live_key_xyz987" not in sanitized
    assert "api_key=***&engine=google" in sanitized
    assert service._sanitize_message("") == ""
    assert service._sanitize_message(None) == ""


def test_exception_chaining_suppressed_to_prevent_leakage(monkeypatch):
    """Verify that exceptions raised by SerpApiService suppress __cause__ (from None)."""
    service = SerpApiService(api_key="leaked_key_999", use_cache=False)

    # Mock client.get to raise httpx.RequestError containing URL with secret key
    def mock_get(*args, **kwargs):
        raise httpx.ConnectError("Connection failed to https://serpapi.com?api_key=leaked_key_999")

    monkeypatch.setattr(service._client, "get", mock_get)

    with pytest.raises(SerpApiError) as exc_info:
        service._execute_query({"engine": "google", "q": "test"})

    # Check that __cause__ is None (suppressed via `from None`)
    assert exc_info.value.__cause__ is None
    # Check that error message itself masked the key
    assert "leaked_key_999" not in str(exc_info.value)


def test_context_isolated_serpapi_client():
    """Verify that configure_serpapi_client isolates clients across thread contexts (Streamlit sessions)."""
    import concurrent.futures

    # Ensure clean slate before test execution
    reset_serpapi_client_context()
    assert get_current_serpapi_client() == _default_serp

    # Configure client in context A
    client_a = configure_serpapi_client(api_key="user_a_key", force_refresh=True)
    assert get_current_serpapi_client() == client_a
    assert client_a._api_key == "user_a_key"
    assert client_a.force_refresh is True

    # Verify that in a separate thread (e.g. concurrent user session), it has clean default state
    def run_in_separate_thread():
        # New thread should return default client, not client_a
        isolated = get_current_serpapi_client()
        assert isolated == _default_serp
        # Configure client in thread B
        client_b = configure_serpapi_client(api_key="user_b_key", force_refresh=False)
        assert get_current_serpapi_client() == client_b
        assert client_b._api_key == "user_b_key"
        assert client_b.force_refresh is False
        reset_serpapi_client_context()
        return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_in_separate_thread)
        assert future.result() is True

    # Context A remains intact and unchanged
    assert get_current_serpapi_client() == client_a
    assert get_current_serpapi_client()._api_key == "user_a_key"

    # Reset context A back to default for test isolation
    reset_serpapi_client_context()
    assert get_current_serpapi_client() == _default_serp
