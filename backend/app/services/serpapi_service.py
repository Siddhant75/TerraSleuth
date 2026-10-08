import hashlib
from io import BytesIO
import logging
import os
from typing import Any, Dict, List, Optional
import httpx
from PIL import Image

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
from backend.app.services.cache_service import CacheService
from backend.app.services.quota_service import QuotaBudgetManager, QuotaExhaustedError

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
        cache_service: Optional[CacheService] = None,
        use_cache: bool = True,
        budget_manager: Optional[QuotaBudgetManager] = None,
        force_refresh: bool = False,
    ):
        self._api_key = api_key or settings.SERPAPI_API_KEY
        self.base_url = settings.SERPAPI_BASE_URL
        self.timeout = timeout_seconds or settings.SERPAPI_TIMEOUT_SECONDS
        self._client = client or httpx.Client(timeout=self.timeout)
        self._owns_client = client is None
        self._cache = (
            cache_service
            if cache_service is not None
            else (CacheService() if (use_cache and settings.CACHE_ENABLED) else None)
        )
        self._budget_manager = budget_manager
        self.force_refresh = force_refresh

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
        import os
        key = self._api_key or os.environ.get("SERPAPI_API_KEY") or settings.SERPAPI_API_KEY
        if not key or str(key).strip() == "" or "your_serpapi" in str(key).lower():
            raise SerpApiConfigError(
                "SERPAPI_API_KEY is not configured. Set SERPAPI_API_KEY in .env or provide it directly."
            )
        return str(key).strip()

    def _sanitize_message(self, message: str) -> str:
        """Mask the API key from any error message, exception string, or URL representation."""
        if not message:
            return ""
        import os
        sanitized = message
        active_key = self._api_key or os.environ.get("SERPAPI_API_KEY") or settings.SERPAPI_API_KEY
        if active_key and active_key in sanitized:
            sanitized = sanitized.replace(active_key, "***")
        return sanitized

    def _execute_query(self, params: Dict[str, Any], force_refresh: bool = False) -> Dict[str, Any]:
        """Dispatch a query to SerpApi with cache check, error handling, and sanitized parameters."""
        engine = str(params.get("engine", "google"))
        should_force = force_refresh or self.force_refresh

        # 1. Quota Defense: Check persistent disk cache first
        if self._cache and not should_force:
            cached_data = self._cache.get_cached_response(engine, params)
            if cached_data is not None:
                logger.info("SerpApi disk cache HIT for engine=%s", engine)
                return cached_data

        # 2. Quota Circuit Breaker: Consume budget for live external query
        if self._budget_manager:
            self._budget_manager.consume()

        # 3. Cache miss: Validate API key and dispatch network request
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

            # 3. Store valid response in cache
            if self._cache:
                self._cache.set_cached_response(engine, params, data)

            return data

        except httpx.TimeoutException as exc:
            logger.error(f"SerpApi query timed out after {self.timeout}s for engine: {params.get('engine')}")
            raise SerpApiTimeoutError(f"SerpApi request timed out after {self.timeout}s") from None
        except (SerpApiError, SerpApiConfigError, SerpApiRateLimitError, SerpApiTimeoutError):
            raise
        except Exception as exc:
            sanitized_err = self._sanitize_message(str(exc))
            logger.error(f"Unexpected error communicating with SerpApi: {sanitized_err}")
            raise SerpApiError(f"Failed to query SerpApi: {sanitized_err}") from None

    def upload_image(self, image_path: str, max_size_bytes: int = 500 * 1024) -> str:
        """Upload a local image file to SerpApi Image API to obtain an image_id for Google Lens.

        Includes SHA-256 caching (to avoid redundant uploads), automatic iterative Pillow compression
        if the image exceeds SerpApi's 500 KB limit, quota tracking, and masked error handling.
        """
        if not image_path or not os.path.exists(image_path):
            raise FileNotFoundError(f"Local image file not found for upload: {image_path}")

        # 1. Read file and compute SHA-256 hash for cache lookup
        with open(image_path, "rb") as f:
            file_data = f.read()

        file_hash = hashlib.sha256(file_data).hexdigest()
        cache_key_params = {"action": "upload", "hash": file_hash}

        # 2. Quota Defense: Check persistent disk cache first
        if self._cache and not self.force_refresh:
            cached_res = self._cache.get_cached_response("google_lens_upload", cache_key_params)
            if cached_res and "image_id" in cached_res:
                logger.info("SerpApi image upload disk cache HIT for hash=%s", file_hash[:10])
                return str(cached_res["image_id"])

        # 3. Compress if size exceeds SerpApi limit (500 KB)
        if len(file_data) > max_size_bytes:
            logger.info("Image size %d bytes exceeds 500 KB limit; compressing...", len(file_data))
            try:
                img = Image.open(BytesIO(file_data))
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                # Iterative compression loop with floor constraint
                quality = 85
                out_io = BytesIO()
                img.save(out_io, format="JPEG", optimize=True, quality=quality)
                compressed = out_io.getvalue()

                while len(compressed) > max_size_bytes and quality > 20:
                    quality -= 15
                    out_io = BytesIO()
                    img.save(out_io, format="JPEG", optimize=True, quality=quality)
                    compressed = out_io.getvalue()

                # If still too large, downscale dimensions
                while len(compressed) > max_size_bytes and img.width > 400:
                    new_size = (int(img.width * 0.75), int(img.height * 0.75))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    out_io = BytesIO()
                    img.save(out_io, format="JPEG", optimize=True, quality=65)
                    compressed = out_io.getvalue()

                file_data = compressed
                logger.info("Compressed image to %d bytes (quality=%d)", len(file_data), quality)
            except Exception as e:
                logger.warning("Failed to compress image with Pillow: %s", e)

        # 4. Quota Budget Enforcement
        if self._budget_manager:
            self._budget_manager.consume()

        # 5. Dispatch multipart upload to SerpApi
        api_key = self._get_api_key()
        upload_url = "https://serpapi.com/image"

        try:
            filename = os.path.basename(image_path) or "image.jpg"
            files = {"image": (filename, file_data, "image/jpeg")}
            data = {"api_key": api_key}

            response = self._client.post(upload_url, data=data, files=files)

            if response.status_code == 429:
                raise SerpApiRateLimitError("SerpApi quota or rate limit exceeded during image upload (HTTP 429).")
            elif response.status_code in (401, 403):
                raise SerpApiConfigError("Invalid SerpApi API key or unauthorized access during image upload.")
            elif response.status_code >= 500:
                raise SerpApiError(f"SerpApi image upload server error (HTTP {response.status_code}).")

            response.raise_for_status()
            res_data = response.json()

            if "error" in res_data:
                err_msg = self._sanitize_message(res_data["error"])
                raise SerpApiError(f"SerpApi image upload error: {err_msg}")

            image_id = res_data.get("image_id")
            if not image_id:
                raise SerpApiError("No image_id returned from SerpApi Image API.")

            logger.info("Successfully uploaded image to SerpApi: image_id=%s", image_id)

            # 6. Store in cache
            if self._cache:
                self._cache.set_cached_response(
                    "google_lens_upload", cache_key_params, {"image_id": image_id}
                )

            return str(image_id)

        except httpx.TimeoutException as exc:
            logger.error("SerpApi image upload timed out after %ds", self.timeout)
            raise SerpApiTimeoutError(f"SerpApi image upload timed out after {self.timeout}s") from None
        except (SerpApiError, SerpApiConfigError, SerpApiRateLimitError, SerpApiTimeoutError):
            raise
        except Exception as exc:
            sanitized_err = self._sanitize_message(str(exc))
            logger.error("Unexpected error during SerpApi image upload: %s", sanitized_err)
            raise SerpApiError(f"Failed to upload image to SerpApi: {sanitized_err}") from None

    def search_lens(
        self,
        image_url: Optional[str] = None,
        image_path: Optional[str] = None,
        image_id: Optional[str] = None,
        crop_bbox: Optional[List[float]] = None,
        hl: str = "en",
        force_refresh: bool = False,
    ) -> LensVisualMatchesResult:
        """Execute a visual reverse-image search using Google Lens API.

        Accepts either a public image_url, a local image_path (which is automatically uploaded
        via SerpApi Image API to get an image_id), a pre-existing image_id, or an optional crop_bbox
        for targeted visual inspection of garments, signs, or objects.
        """
        if not image_url and not image_path and not image_id:
            raise ValueError("image_url must be provided (or local image_path / image_id).")

        active_image_id = image_id
        active_url = image_url

        # Handle local image cropping or upload if no remote image_url or image_id is provided,
        # or if a targeted crop_bbox is requested for item/outfit/signage search.
        if not active_image_id and ((not active_url) or (crop_bbox and len(crop_bbox) == 4)) and image_path and os.path.exists(image_path):
            target_path = image_path
            tmp_crop_path = None

            try:
                # If bounding box is specified, crop the targeted region first
                if crop_bbox and len(crop_bbox) == 4:
                    from backend.app.services.vision_service import crop_image_region
                    tmp_crop_path = crop_image_region(image_path=image_path, bbox=crop_bbox)
                    target_path = tmp_crop_path

                # Upload to SerpApi Image API to obtain image_id
                active_image_id = self.upload_image(target_path)
            finally:
                # Guarantee cleanup of temporary cropped file
                if tmp_crop_path and os.path.exists(tmp_crop_path):
                    try:
                        os.remove(tmp_crop_path)
                    except OSError:
                        pass

        params: Dict[str, Any] = {
            "engine": "google_lens",
            "hl": hl,
        }

        if active_image_id:
            params["image_id"] = active_image_id
        elif active_url:
            params["url"] = active_url.strip()
        else:
            raise ValueError("No valid image_url, existing image_path, or image_id available for Google Lens.")

        raw_data = self._execute_query(params, force_refresh=True) if force_refresh else self._execute_query(params)
        return self._parse_lens_response(raw_data)

    def search_maps(
        self,
        query: str,
        ll: Optional[str] = None,
        hl: str = "en",
        force_refresh: bool = False,
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

        raw_data = self._execute_query(params, force_refresh=True) if force_refresh else self._execute_query(params)
        return self._parse_maps_response(raw_data, query=query)

    def search_news(
        self,
        query: str,
        time_range: Optional[str] = None,
        gl: str = "us",
        hl: str = "en",
        force_refresh: bool = False,
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

        raw_data = self._execute_query(params, force_refresh=True) if force_refresh else self._execute_query(params)
        return self._parse_news_response(raw_data, query=query)

    def search_google(
        self,
        query: str,
        gl: str = "us",
        hl: str = "en",
        force_refresh: bool = False,
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
        raw_data = self._execute_query(params, force_refresh=True) if force_refresh else self._execute_query(params)
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
