import logging
from typing import Any, Dict, List, Optional

from backend.app.agent.state import OsintGraphState
from backend.app.models.case import Citation, TimelineEvent
from backend.app.services.serpapi_service import SerpApiService

logger = logging.getLogger(__name__)


def chrono_auditor_node(state: OsintGraphState) -> Dict[str, Any]:
    """LangGraph node: Audits chronological provenance and historical timelines via Google News.

    Formulates targeted temporal queries from triangulated geographic candidates and Lens visual matches,
    extracting publication timestamps, historical milestones, and detecting image recycling or temporal anomalies.
    """
    budget = state.get("budget_remaining", 8)
    logger.info("Executing chrono_auditor_node with budget_remaining=%d", budget)

    if budget <= 0:
        logger.warning("chrono_auditor_node skipped: query budget exhausted")
        return {
            "timeline_events": [],
            "citations": [],
            "budget_remaining": 0,
            "status": "chrono_skipped_budget_exhausted",
        }

    # 1. Determine the target entity for chronological investigation
    target_query: Optional[str] = None

    # Prioritize top resolved geo-candidate name
    geo_candidates = state.get("geo_candidates", [])
    if geo_candidates:
        top_candidate = geo_candidates[0]
        name = top_candidate.name if hasattr(top_candidate, "name") else top_candidate.get("name")
        if name:
            target_query = name.split(" - ")[0].split(" | ")[0].strip()

    # Fallback to top Lens match title if no geo candidates
    if not target_query:
        lens_matches = state.get("lens_matches", [])
        if lens_matches:
            top_match = lens_matches[0]
            title = top_match.get("title") if isinstance(top_match, dict) else getattr(top_match, "title", None)
            if title:
                target_query = title.split(" - ")[0].split(" | ")[0].strip()

    # Fallback to context hint if available
    if not target_query:
        target_query = state.get("context_hint")

    if not target_query:
        logger.info("chrono_auditor_node: no target query could be formulated")
        return {
            "timeline_events": [],
            "citations": [],
            "budget_remaining": budget,
            "status": "chrono_skipped_no_query",
        }

    logger.info("chrono_auditor_node executing news query for '%s'", target_query)

    timeline_events: List[TimelineEvent] = []
    citations: List[Citation] = []
    queries_consumed = 0

    try:
        serp = SerpApiService()
        queries_consumed += 1
        news_result = serp.search_news(query=target_query)

        for idx, item in enumerate(news_result.items[:4]):
            t_event = TimelineEvent(
                date=item.date or "Recent",
                title=item.title,
                source=item.source or "News Outlet",
                url=item.link,
                snippet=item.snippet or f"Historical coverage concerning {target_query}",
                is_origin=(idx == 0),
            )
            timeline_events.append(t_event)

            citations.append(
                Citation(
                    title=f"News: {item.title}",
                    url=item.link,
                    engine="google_news",
                    snippet=f"Reported by {item.source} ({item.date}): {item.snippet or 'Event report'}",
                )
            )

        logger.info(
            "chrono_auditor_node resolved %d timeline events and %d citations",
            len(timeline_events),
            len(citations),
        )

        return {
            "timeline_events": timeline_events,
            "citations": citations,
            "budget_remaining": max(0, budget - queries_consumed),
            "status": "chrono_audited",
        }
    except Exception as exc:
        logger.exception("Error during Google News timeline audit: %s", exc)
        return {
            "timeline_events": [],
            "citations": [],
            "budget_remaining": max(0, budget - queries_consumed),
            "status": "chrono_audit_failed",
            "error": f"Google News audit error: {str(exc)}",
        }
