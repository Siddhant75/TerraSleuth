import contextvars
import logging
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from backend.app.services.cache_service import CacheService, seed_golden_cases
from backend.app.services.serpapi_service import SerpApiService
from backend.app.services.vision_service import crop_image_region

logger = logging.getLogger(__name__)

# Ensure golden scenarios are seeded
seed_golden_cases()
_cache = CacheService()
_default_serp = SerpApiService(cache_service=_cache)

# Thread/Context-isolated client variable to prevent cross-session race conditions
_serpapi_context_var: contextvars.ContextVar[Optional[SerpApiService]] = contextvars.ContextVar(
    "_serpapi_context_var", default=None
)


def get_current_serpapi_client() -> SerpApiService:
    """Retrieve the context-isolated SerpApiService, or fallback to default client."""
    client = _serpapi_context_var.get()
    if client is not None:
        return client
    return _default_serp


def configure_serpapi_client(
    api_key: Optional[str] = None, force_refresh: bool = False
) -> SerpApiService:
    """Dynamically configure and bind a session-isolated SerpApiService client to the current context."""
    client = SerpApiService(
        api_key=api_key,
        cache_service=_cache,
        force_refresh=force_refresh,
    )
    _serpapi_context_var.set(client)
    logger.info(
        "Configured context-isolated SerpApi tool client: api_key_set=%s, force_refresh=%s",
        bool(client._api_key),
        force_refresh,
    )
    return client


def reset_serpapi_client_context() -> None:
    """Reset the context-isolated SerpApiService back to None (fallback to default)."""
    _serpapi_context_var.set(None)


@tool
def tool_lens_search(
    image_url: Optional[str] = None,
    image_path: Optional[str] = None,
    crop_bbox: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Search Google Lens for reverse visual twins and authoritative matches using URL or uploaded image."""
    logger.info("tool_lens_search invoked for url=%s, path=%s, crop_bbox=%s", image_url, image_path, crop_bbox)
    res = get_current_serpapi_client().search_lens(
        image_url=image_url, image_path=image_path, crop_bbox=crop_bbox
    )
    return {
        "visual_matches": [m.model_dump() for m in (res.visual_matches or [])[:6]],
        "knowledge_graph": res.knowledge_graph or {},
    }


@tool
def tool_maps_triangulate(
    query: str, lat_hint: Optional[float] = None, lon_hint: Optional[float] = None
) -> Dict[str, Any]:
    """Triangulate physical coordinates and place details using Google Maps."""
    logger.info("tool_maps_triangulate invoked for query: %s", query)
    res = get_current_serpapi_client().search_maps(query=query)
    candidates = []
    for c in (res.candidates or [])[:4]:
        candidates.append({
            "title": c.title,
            "address": c.address,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "place_id": c.place_id,
            "match_score": getattr(c, "match_score", 1.0),
        })
    return {"candidates": candidates}


@tool
def tool_news_audit(query: str, date_filter: Optional[str] = None) -> Dict[str, Any]:
    """Audit temporal milestones and earliest publication records in Google News."""
    logger.info("tool_news_audit invoked for query: %s", query)
    res = get_current_serpapi_client().search_news(query=query)
    events = []
    for item in (res.items or [])[:4]:
        events.append({
            "title": item.title,
            "source": item.source,
            "date": item.date,
            "link": item.link,
            "snippet": item.snippet,
        })
    return {"articles": events}


@tool
def tool_google_dork(dork_query: str) -> Dict[str, Any]:
    """Execute targeted OSINT search dorks for municipal permits and scam records."""
    logger.info("tool_google_dork invoked for query: %s", dork_query)
    res = get_current_serpapi_client().search_google(query=dork_query)
    return {
        "organic_results": [
            {"title": r.title, "link": r.link, "snippet": r.snippet}
            for r in res.organic_results[:5]
        ]
    }


@tool
def tool_crop_region(image_path: str, bbox: List[float], label: str = "crop") -> str:
    """Crop an isolated region from an image for targeted visual inspection."""
    logger.info("tool_crop_region invoked for: %s label: %s", image_path, label)
    return crop_image_region(image_path=image_path, bbox=bbox)
