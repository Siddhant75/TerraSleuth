import logging
import os
from typing import Any, Dict, List, Optional

from backend.app.agent.state import OsintGraphState
from backend.app.models.case import Citation
from backend.app.services.serpapi_service import SerpApiService

logger = logging.getLogger(__name__)


def lens_hunter_node(state: OsintGraphState) -> Dict[str, Any]:
    """LangGraph node: Performs reverse-image provenance search using SerpApi Google Lens.
    
    Identifies exact visual matches, knowledge graph entities, and original publication
    links to establish image history and extract location hypotheses.
    """
    image_url = state.get("image_url")
    budget = state.get("budget_remaining", 8)

    logger.info("Executing lens_hunter_node: image_url=%s, budget_remaining=%d", image_url, budget)

    if budget <= 0:
        logger.warning("lens_hunter_node skipped: query budget exhausted")
        return {
            "lens_matches": [],
            "citations": [],
            "budget_remaining": 0,
            "status": "lens_skipped_budget_exhausted",
        }

    image_path = state.get("image_path")

    if not image_url and (not image_path or not os.path.exists(image_path)):
        logger.info("lens_hunter_node skipped: neither image_url nor existing image_path provided")
        return {
            "lens_matches": [],
            "citations": [],
            "budget_remaining": budget,
            "status": "lens_skipped_no_url",
        }

    try:
        serp = SerpApiService(
            api_key=state.get("api_key"),
            force_refresh=state.get("force_refresh", False),
        )
        lens_result = serp.search_lens(image_url=image_url, image_path=image_path)

        visual_matches = [m.model_dump() for m in lens_result.visual_matches[:6]]
        citations: List[Citation] = []

        # Formulate citations from top visual matches
        for match in lens_result.visual_matches[:4]:
            if match.link:
                citations.append(
                    Citation(
                        title=match.title or "Google Lens Visual Match",
                        url=match.link,
                        engine="google_lens",
                        snippet=f"Visual twin match via {match.source or 'web source'}",
                    )
                )

        logger.info(
            "lens_hunter_node retrieved %d visual matches and %d citations",
            len(visual_matches),
            len(citations),
        )

        return {
            "lens_matches": visual_matches,
            "citations": citations,
            "budget_remaining": max(0, budget - 1),
            "status": "lens_searched",
        }
    except Exception as exc:
        logger.exception("Error during Google Lens visual provenance search: %s", exc)
        return {
            "lens_matches": [],
            "citations": [],
            "budget_remaining": max(0, budget - 1),
            "status": "lens_search_failed",
            "error": f"Google Lens search error: {str(exc)}",
        }
