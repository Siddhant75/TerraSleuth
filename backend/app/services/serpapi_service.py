import logging
from typing import Any, Dict, List, Optional
import httpx

from backend.app.config import settings
from backend.app.models.serp import (
    GoogleSearchResult,
    LensMatch,
    LensVisualMatchesResult,
    MapsCandidate,
    MapsSearchResult,
    NewsItem,
    NewsSearchResult,
    OrganicResult,
)

logger = logging.getLogger(__name__)


class SerpApiError(Exception):
    """Base exception for SerpApi operations."""
    pass


class SerpApiConfigError(SerpApiError):
    """Raised when SerpApi configuration (e.g. API key) is invalid or missing."""
    pass


class SerpApiTimeoutError(SerpApiError):
    """Raised when a SerpApi request times out."""
    pass


class SerpApiRateLimitError(SerpApiError):
    """Raised when SerpApi rate limit or credit quota is exceeded."""
    pass


class SerpApiService:
    """Unified client service for SerpApi's multi-modal, spatial, and news search engines."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        client: Optional[httpx.Client] = None,
    ):
        self._api_key = api_key or settings.SERPAPI_API_KEY
        self.base_url = settings.SERPAPI_BASE_URL
        self.timeout = timeout_seconds or settings.SERPAPI_TIMEOUT_SECONDS
        self._client = client or httpx.Client(timeout=self.timeout)
        self._owns_client = client is None

    def close(self) -> None:
        """Close the underlying HTTP client session."""
        if self._owns_client and hasattr(self, "_client") and not self._client.is_closed:
            self._client.close()

    def __enter__(self) -> "SerpApiService":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _get_api_key(self) -> str:
        """Resolve and validate the API key, raising clean errors if missing."""
        if not self._api_key or self._api_key.strip() == "" or "your_serpapi" in self._api_key.lower():
            raise SerpApiConfigError(
                "SERPAPI_API_KEY is not configured. Set SERPAPI_API_KEY in .env or provide it directly."
            )
        return self._api_key.strip()

    def _sanitize_message(self, message: str) -> str:
        """Mask the API key from any error message, exception string, or URL representation."""
        if not message:
            return ""
        sanitized = message
        if self._api_key and self._api_key in sanitized:
            sanitized = sanitized.replace(self._api_key, "***")
        return sanitized

    def _execute_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a query to SerpApi with error handling and sanitized parameters."""
        api_key = self._get_api_key()
        query_params = {**params, "api_key": api_key}

        try:
            response = self._client.get(self.base_url, params=query_params)

            if response.status_code == 429:
                raise SerpApiRateLimitError("SerpApi quota or rate limit exceeded (HTTP 429).")
            elif response.status_code == 401 or response.status_code == 403:
                raise SerpApiConfigError("Invalid SerpApi API key or unauthorized access.")
            elif response.status_code >= 500:
                raise SerpApiError(f"SerpApi remote server error (HTTP {response.status_code}).")

            response.raise_for_status()
            data = response.json()

            if "error" in data:
                err_msg = self._sanitize_message(data["error"])
                if "Monthly search limit reached" in err_msg or "quota" in err_msg.lower():
                    raise SerpApiRateLimitError(f"SerpApi quota limit: {err_msg}")
                raise SerpApiError(f"SerpApi query error: {err_msg}")

            return data

        except httpx.TimeoutException as exc:
            logger.error(f"SerpApi query timed out after {self.timeout}s for engine: {params.get('engine')}")
            raise SerpApiTimeoutError(f"SerpApi request timed out after {self.timeout}s") from exc
        except (SerpApiError, SerpApiConfigError, SerpApiRateLimitError, SerpApiTimeoutError):
            raise
        except Exception as exc:
            sanitized_err = self._sanitize_message(str(exc))
            logger.error(f"Unexpected error communicating with SerpApi: {sanitized_err}")
            raise SerpApiError(f"Failed to query SerpApi: {sanitized_err}") from exc

    def search_lens(self, image_url: str, hl: str = "en") -> LensVisualMatchesResult:
        """Execute a visual reverse-image search using Google Lens API."""
        if not image_url or not image_url.strip():
            raise ValueError("image_url must be provided for Google Lens visual search.")

        params = {
            "engine": "google_lens",
            "url": image_url.strip(),
            "hl": hl,
        }
        raw_data = self._execute_query(params)
        return self._parse_lens_response(raw_data)

    def search_maps(
        self, query: str, ll: Optional[str] = None, hl: str = "en"
    ) -> MapsSearchResult:
        """Execute a spatial places and coordinate search using Google Maps API."""
        if not query or not query.strip():
            raise ValueError("Query string must be provided for Google Maps search.")

        params: Dict[str, Any] = {
            "engine": "google_maps",
            "q": query.strip(),
            "type": "search",
            "hl": hl,
        }
        if ll:
            params["ll"] = ll.strip()

        raw_data = self._execute_query(params)
        return self._parse_maps_response(raw_data, query=query)

    def search_news(
        self,
        query: str,
        time_range: Optional[str] = None,
        gl: str = "us",
        hl: str = "en",
    ) -> NewsSearchResult:
        """Search chronological breaking news and historical events via Google News API."""
        if not query or not query.strip():
            raise ValueError("Query string must be provided for Google News search.")

        params: Dict[str, Any] = {
            "engine": "google_news",
            "q": query.strip(),
            "gl": gl,
            "hl": hl,
        }
        if time_range:
            params["tbs"] = time_range.strip()

        raw_data = self._execute_query(params)
        return self._parse_news_response(raw_data, query=query)

    def search_google(
        self, query: str, gl: str = "us", hl: str = "en"
    ) -> GoogleSearchResult:
        """Perform contextual organic search and knowledge graph retrieval via Google Search API."""
        if not query or not query.strip():
            raise ValueError("Query string must be provided for Google Search.")

        params = {
            "engine": "google",
            "q": query.strip(),
            "gl": gl,
            "hl": hl,
        }
        raw_data = self._execute_query(params)
        return self._parse_google_response(raw_data, query=query)

    # -------------------------------------------------------------------------
    # Response Parsers
    # -------------------------------------------------------------------------

    def _parse_lens_response(self, raw_data: Dict[str, Any]) -> LensVisualMatchesResult:
        """Parse raw SerpApi Google Lens payload into LensVisualMatchesResult."""
        visual_matches: List[LensMatch] = []
        exact_matches: List[LensMatch] = []

        # Parse visual_matches
        raw_matches = raw_data.get("visual_matches", [])
        for idx, item in enumerate(raw_matches):
            title = item.get("title") or "Untitled Match"
            link = item.get("link") or ""
            source = item.get("source") or ""
            thumbnail = item.get("thumbnail")

            match_obj = LensMatch(
                title=title,
                link=link,
                source=source,
                thumbnail=thumbnail,
                score=idx + 1,
                is_exact=False,
                source_date=item.get("date"),
            )
            visual_matches.append(match_obj)

        # Parse exact_matches if provided by Google Lens
        raw_exact = raw_data.get("exact_matches", [])
        for idx, item in enumerate(raw_exact):
            title = item.get("title") or "Exact Match"
            link = item.get("link") or ""
            source = item.get("source") or ""
            thumbnail = item.get("thumbnail")

            exact_obj = LensMatch(
                title=title,
                link=link,
                source=source,
                thumbnail=thumbnail,
                score=idx + 1,
                is_exact=True,
                source_date=item.get("date"),
            )
            exact_matches.append(exact_obj)

        knowledge_graph = raw_data.get("knowledge_graph")
        search_metadata = raw_data.get("search_metadata")

        return LensVisualMatchesResult(
            visual_matches=visual_matches,
            exact_matches=exact_matches,
            knowledge_graph=knowledge_graph,
            search_metadata=search_metadata,
        )

    def _parse_maps_response(
        self, raw_data: Dict[str, Any], query: str
    ) -> MapsSearchResult:
        """Parse raw SerpApi Google Maps payload into MapsSearchResult."""
        candidates: List[MapsCandidate] = []

        # Handle local_results (list of places) or place_results (single place)
        place_items = raw_data.get("local_results", [])
        if not place_items and "place_results" in raw_data:
            place_items = [raw_data["place_results"]]

        for item in place_items:
            title = item.get("title") or item.get("name") or "Unnamed Place"
            address = item.get("address")
            place_id = item.get("place_id") or item.get("data_cid") or str(item.get("position", ""))

            gps = item.get("gps_coordinates", {})
            latitude = gps.get("latitude")
            longitude = gps.get("longitude")

            rating = item.get("rating")
            reviews = item.get("reviews") or item.get("reviews_count")
            photos = [p.get("thumbnail") for p in item.get("photos", []) if isinstance(p, dict) and p.get("thumbnail")]
            if not photos and item.get("thumbnail"):
                photos = [item["thumbnail"]]

            place_type = item.get("type") or item.get("place_type")
            phone = item.get("phone")
            website = item.get("website")

            candidate = MapsCandidate(
                place_id=place_id,
                title=title,
                address=address,
                latitude=latitude,
                longitude=longitude,
                rating=rating,
                reviews_count=reviews,
                photos=photos,
                place_type=place_type,
                phone=phone,
                website=website,
            )
            candidates.append(candidate)

        return MapsSearchResult(
            candidates=candidates,
            search_query=query,
            total_results=len(candidates),
        )

    def _parse_news_response(
        self, raw_data: Dict[str, Any], query: str
    ) -> NewsSearchResult:
        """Parse raw SerpApi Google News payload into NewsSearchResult."""
        items: List[NewsItem] = []
        raw_news = raw_data.get("news_results", [])

        for item in raw_news:
            title = item.get("title") or "Untitled News"
            link = item.get("link") or ""
            source_info = item.get("source", {})
            source = source_info.get("name") if isinstance(source_info, dict) else str(source_info or "Unknown")
            date = item.get("date") or "Recently"
            snippet = item.get("snippet")
            thumbnail = item.get("thumbnail")

            news_obj = NewsItem(
                title=title,
                link=link,
                source=source,
                date=date,
                snippet=snippet,
                thumbnail=thumbnail,
            )
            items.append(news_obj)

        return NewsSearchResult(items=items, search_query=query)

    def _parse_google_response(
        self, raw_data: Dict[str, Any], query: str
    ) -> GoogleSearchResult:
        """Parse raw SerpApi Google Search payload into GoogleSearchResult."""
        organic_results: List[OrganicResult] = []
        raw_organic = raw_data.get("organic_results", [])

        for idx, item in enumerate(raw_organic):
            title = item.get("title") or "Untitled Result"
            link = item.get("link") or ""
            snippet = item.get("snippet")
            position = item.get("position", idx + 1)

            res = OrganicResult(
                title=title,
                link=link,
                snippet=snippet,
                position=position,
            )
            organic_results.append(res)

        knowledge_graph = raw_data.get("knowledge_graph")

        return GoogleSearchResult(
            organic_results=organic_results,
            knowledge_graph=knowledge_graph,
            search_query=query,
        )
