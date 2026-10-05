import logging
from typing import Any, Dict, List, Set

from backend.app.agent.state import OsintGraphState
from backend.app.models.case import Citation, GeoCandidate
from backend.app.services.serpapi_service import SerpApiService

logger = logging.getLogger(__name__)


def geo_triangulator_node(state: OsintGraphState) -> Dict[str, Any]:
    """LangGraph node: Triangulates physical coordinates and street addresses via Google Maps.
    
    Synthesizes entity hypotheses from Lens visual twin matches and visual forensic clues,
    executing targeted spatial searches to pinpoint ground-truth latitude and longitude.
    """
    budget = state.get("budget_remaining", 8)
    logger.info("Executing geo_triangulator_node with budget_remaining=%d", budget)

    if budget <= 0:
        logger.warning("geo_triangulator_node skipped: query budget exhausted")
        return {
            "geo_candidates": [],
            "citations": [],
            "budget_remaining": 0,
            "status": "geo_skipped_budget_exhausted",
        }

    # Extract target queries from Lens matches and Visual Clues
    candidate_queries: List[str] = []
    seen_queries: Set[str] = set()

    # 1. Prioritize entity titles from Lens matches
    for match in state.get("lens_matches", []):
        title = match.get("title") if isinstance(match, dict) else getattr(match, "title", None)
        if title and title not in seen_queries:
            # Strip noise words like 'Wikipedia' or file extensions
            clean_title = title.split(" - ")[0].split(" | ")[0].strip()
            if clean_title and clean_title not in seen_queries:
                candidate_queries.append(clean_title)
                seen_queries.add(clean_title)

    # 2. Add suggested queries from high-confidence visual clues
    for clue in state.get("visual_clues", []):
        sq = clue.suggested_query if hasattr(clue, "suggested_query") else clue.get("suggested_query")
        if sq and sq not in seen_queries:
            candidate_queries.append(sq)
            seen_queries.add(sq)

    # Fallback default query if no specific clues exist
    if not candidate_queries:
        context_hint = state.get("context_hint")
        if context_hint:
            candidate_queries.append(context_hint)
        else:
            logger.info("geo_triangulator_node: no viable spatial queries formulated")
            return {
                "geo_candidates": [],
                "citations": [],
                "budget_remaining": budget,
                "status": "geo_triangulation_empty",
            }

    # Enforce strict budget cap: maximum 2 spatial queries per node execution
    queries_to_execute = candidate_queries[:2]
    serp = SerpApiService()
    geo_candidates: List[GeoCandidate] = []
    citations: List[Citation] = []
    queries_count = 0

    try:
        for q in queries_to_execute:
            if budget - queries_count <= 0:
                break

            logger.info("Triangulating spatial query: %s", q)
            try:
                maps_result = serp.search_maps(query=q)
                queries_count += 1

                for candidate in maps_result.candidates[:3]:
                    # Construct verified Google Maps link
                    map_url = (
                        f"https://www.google.com/maps/search/?api=1&query={candidate.latitude},{candidate.longitude}"
                    )

                    geo_obj = GeoCandidate(
                        name=candidate.title,
                        address=candidate.address,
                        latitude=candidate.latitude,
                        longitude=candidate.longitude,
                        place_id=candidate.place_id,
                        match_score=0.92 if queries_count == 1 else 0.85,
                        engine_source="google_maps",
                        evidence_snippet=f"Triangulated from search query '{q}' via Google Maps",
                        source_url=map_url,
                    )
                    geo_candidates.append(geo_obj)

                    citations.append(
                        Citation(
                            title=f"Google Maps: {candidate.title}",
                            url=map_url,
                            engine="google_maps",
                            snippet=f"Resolved coordinates ({candidate.latitude}, {candidate.longitude}) at {candidate.address or candidate.title}",
                        )
                    )
            except Exception as query_exc:
                logger.warning("Spatial query '%s' failed: %s", q, query_exc)
                continue

        logger.info(
            "geo_triangulator_node resolved %d spatial candidates and %d citations (executed %d queries)",
            len(geo_candidates),
            len(citations),
            queries_count,
        )

        return {
            "geo_candidates": geo_candidates,
            "citations": citations,
            "budget_remaining": max(0, budget - queries_count),
            "status": "geo_triangulated",
        }
    except Exception as exc:
        logger.exception("Error during Google Maps spatial triangulation: %s", exc)
        return {
            "geo_candidates": geo_candidates,
            "citations": citations,
            "budget_remaining": max(0, budget - queries_count),
            "status": "geo_triangulation_failed",
            "error": f"Google Maps triangulation error: {str(exc)}",
        }
