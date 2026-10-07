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
_serp = SerpApiService(cache_service=_cache)


@tool
def tool_lens_search(image_url: str, crop_bbox: Optional[List[float]] = None) -> Dict[str, Any]:
    """Search Google Lens for reverse visual twins and authoritative matches."""
    logger.info("tool_lens_search invoked for url: %s", image_url)
    res = _serp.search_lens(image_url=image_url)
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
    res = _serp.search_maps(query=query)
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
    res = _serp.search_news(query=query)
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
    res = _serp.search_google(query=dork_query)
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
