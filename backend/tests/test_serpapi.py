from unittest.mock import MagicMock, patch
import httpx
import pytest

from backend.app.models.serp import (
    GoogleSearchResult,
    LensVisualMatchesResult,
    MapsSearchResult,
    NewsSearchResult,
)
from backend.app.services.serpapi_service import (
    SerpApiConfigError,
    SerpApiError,
    SerpApiRateLimitError,
    SerpApiService,
    SerpApiTimeoutError,
)


@pytest.fixture
def mock_service():
    """Create a SerpApiService instance with a mock API key."""
    return SerpApiService(api_key="test_serpapi_key_12345")


# ---------------------------------------------------------------------------
# Google Lens Tests
# ---------------------------------------------------------------------------

def test_lens_search_parsing_success(mock_service):
    mock_payload = {
        "visual_matches": [
            {
                "title": "Eiffel Tower at Twilight",
                "link": "https://example.com/eiffel-photo",
                "source": "example.com",
                "thumbnail": "https://example.com/thumb1.jpg",
                "date": "May 14, 2022",
            },
            {
                "title": "Champ de Mars Paris",
                "link": "https://parisguide.org/eiffel",
                "source": "parisguide.org",
                "thumbnail": "https://parisguide.org/thumb2.jpg",
            },
        ],
        "exact_matches": [
            {
                "title": "Exact Duplicate Photo",
                "link": "https://flickr.com/photos/original",
                "source": "flickr.com",
            }
        ],
        "knowledge_graph": {"title": "Eiffel Tower", "type": "Monument in Paris"},
    }

    with patch.object(mock_service, "_execute_query", return_value=mock_payload) as mock_exec:
        result = mock_service.search_lens("https://example.com/mystery.jpg")

        assert isinstance(result, LensVisualMatchesResult)
        assert len(result.visual_matches) == 2
        assert result.visual_matches[0].title == "Eiffel Tower at Twilight"
        assert result.visual_matches[0].source == "example.com"
        assert result.visual_matches[0].score == 1
        assert not result.visual_matches[0].is_exact

        assert len(result.exact_matches) == 1
        assert result.exact_matches[0].is_exact is True
        assert result.knowledge_graph["title"] == "Eiffel Tower"

        mock_exec.assert_called_once_with({
            "engine": "google_lens",
            "url": "https://example.com/mystery.jpg",
            "hl": "en",
        })


def test_lens_search_empty_url_validation(mock_service):
    with pytest.raises(ValueError, match="image_url must be provided"):
        mock_service.search_lens("")


# ---------------------------------------------------------------------------
# Google Maps Tests
# ---------------------------------------------------------------------------

def test_maps_search_parsing_local_results(mock_service):
    mock_payload = {
        "local_results": [
            {
                "title": "Gateway of India",
                "address": "Apollo Bandar, Colaba, Mumbai, Maharashtra 400001",
                "place_id": "ChIJ123Gateway",
                "gps_coordinates": {"latitude": 18.9220, "longitude": 72.8347},
                "rating": 4.6,
                "reviews": 125000,
                "type": "Historical monument",
                "photos": [{"thumbnail": "https://maps.google.com/p1.jpg"}],
            }
        ]
    }

    with patch.object(mock_service, "_execute_query", return_value=mock_payload) as mock_exec:
        result = mock_service.search_maps("Gateway of India Mumbai")

        assert isinstance(result, MapsSearchResult)
        assert result.total_results == 1
        candidate = result.candidates[0]
        assert candidate.title == "Gateway of India"
        assert candidate.latitude == 18.9220
        assert candidate.longitude == 72.8347
        assert candidate.place_id == "ChIJ123Gateway"
        assert candidate.rating == 4.6
        assert len(candidate.photos) == 1

        mock_exec.assert_called_once_with({
            "engine": "google_maps",
            "q": "Gateway of India Mumbai",
            "type": "search",
            "hl": "en",
        })


def test_maps_search_single_place_results_fallback(mock_service):
    mock_payload = {
        "place_results": {
            "name": "Taj Mahal Palace Hotel",
            "address": "Colaba, Mumbai",
            "data_cid": "987654321",
            "gps_coordinates": {"latitude": 18.9217, "longitude": 72.8332},
            "thumbnail": "https://maps.google.com/hotel.jpg",
        }
    }

    with patch.object(mock_service, "_execute_query", return_value=mock_payload):
        result = mock_service.search_maps("Taj Mahal Palace Mumbai")

        assert result.total_results == 1
        assert result.candidates[0].title == "Taj Mahal Palace Hotel"
        assert result.candidates[0].latitude == 18.9217
        assert result.candidates[0].longitude == 72.8332
        assert len(result.candidates[0].photos) == 1


# ---------------------------------------------------------------------------
# Google News Tests
# ---------------------------------------------------------------------------

def test_news_search_parsing_success(mock_service):
    mock_payload = {
        "news_results": [
            {
                "title": "Historic Arch Restored in Old Town",
                "link": "https://news.example.com/arch",
                "source": {"name": "World Heritage News"},
                "date": "3 days ago",
                "snippet": "Municipal officials unveiled the restored 18th-century arch.",
            }
        ]
    }

    with patch.object(mock_service, "_execute_query", return_value=mock_payload) as mock_exec:
        result = mock_service.search_news("historic arch restoration", time_range="qdr:w")

        assert isinstance(result, NewsSearchResult)
        assert len(result.items) == 1
        item = result.items[0]
        assert item.title == "Historic Arch Restored in Old Town"
        assert item.source == "World Heritage News"
        assert item.date == "3 days ago"

        mock_exec.assert_called_once_with({
            "engine": "google_news",
            "q": "historic arch restoration",
            "gl": "us",
            "hl": "en",
            "tbs": "qdr:w",
        })


# ---------------------------------------------------------------------------
# Google Search Tests
# ---------------------------------------------------------------------------

def test_google_search_parsing_success(mock_service):
    mock_payload = {
        "organic_results": [
            {
                "title": "Colaba Municipal Ward Office",
                "link": "https://mumbai.gov.in/colaba",
                "snippet": "Official portal for Colaba administrative ward.",
                "position": 1,
            }
        ],
        "knowledge_graph": {"title": "Colaba", "type": "Neighborhood in Mumbai"},
    }

    with patch.object(mock_service, "_execute_query", return_value=mock_payload):
        result = mock_service.search_google("Colaba Mumbai ward")

        assert isinstance(result, GoogleSearchResult)
        assert len(result.organic_results) == 1
        assert result.organic_results[0].title == "Colaba Municipal Ward Office"
        assert result.knowledge_graph["title"] == "Colaba"


# ---------------------------------------------------------------------------
# Error & Edge Case Tests
# ---------------------------------------------------------------------------

def test_missing_api_key_raises_config_error(monkeypatch):
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    monkeypatch.setattr("backend.app.services.serpapi_service.settings.SERPAPI_API_KEY", None)
    service = SerpApiService(api_key=None)
    with pytest.raises(SerpApiConfigError, match="SERPAPI_API_KEY is not configured"):
        service.search_maps("Test query")


def test_timeout_raises_serpapi_timeout_error(mock_service):
    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Connection timed out")):
        with pytest.raises(SerpApiTimeoutError, match="timed out after"):
            mock_service.search_maps("Test query")


def test_rate_limit_raises_serpapi_rate_limit_error(mock_service):
    mock_response = MagicMock()
    mock_response.status_code = 429
    with patch("httpx.Client.get", return_value=mock_response):
        with pytest.raises(SerpApiRateLimitError, match="quota or rate limit exceeded"):
            mock_service.search_maps("Test query")


def test_empty_results_handled_gracefully(mock_service):
    with patch.object(mock_service, "_execute_query", return_value={}):
        lens_res = mock_service.search_lens("https://example.com/blank.jpg")
        assert len(lens_res.visual_matches) == 0
        assert len(lens_res.exact_matches) == 0

        maps_res = mock_service.search_maps("nowhere_land_xyz")
        assert maps_res.total_results == 0
        assert len(maps_res.candidates) == 0

        news_res = mock_service.search_news("nonexistent_news_query_xyz")
        assert len(news_res.items) == 0


def test_api_key_masked_in_exceptions():
    test_key = "super_secret_serp_key_999"
    service = SerpApiService(api_key=test_key)
    with patch.object(service._client, "get", side_effect=Exception(f"Failed connecting to https://serpapi.com?api_key={test_key}&engine=google")):
        with pytest.raises(SerpApiError) as exc_info:
            service.search_maps("Test query")
        assert test_key not in str(exc_info.value)
        assert "***" in str(exc_info.value)
    service.close()


def test_client_lifecycle_and_context_manager():
    with SerpApiService(api_key="valid_dummy_key_123") as service:
        assert not service._client.is_closed
    # After exiting context manager, client should be closed
    assert service._client.is_closed

