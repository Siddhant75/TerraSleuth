import logging
import time
from typing import Any, Dict, List, Optional
import uuid

from backend.app.agent.state import OsintGraphState
from backend.app.models.case import CaseFile, GeoCandidate
from backend.app.services.anomaly_service import AnomalyService
from backend.app.services.dork_service import DorkService

logger = logging.getLogger(__name__)


def calculate_confidence_score(
    resolved_location: Optional[GeoCandidate],
    visual_clues_count: int,
    lens_matches_count: int,
    timeline_events_count: int,
) -> float:
    """Compute a holistic, explainable confidence score in [0.0, 1.0].
    
    Weights:
    - Geo candidate resolution match: 45%
    - Multi-modal visual forensic clues: 25%
    - Reverse-image provenance twin matches: 15%
    - Chronological/news timeline corroboration: 15%
    """
    if not resolved_location and lens_matches_count == 0:
        # Bare visual clues without geospatial resolution cannot exceed exploratory confidence
        return min(0.20, round(visual_clues_count * 0.05, 2))

    geo_score = (resolved_location.match_score if resolved_location else 0.0) * 0.45
    visual_score = min(1.0, visual_clues_count / 4.0) * 0.25
    lens_score = min(1.0, lens_matches_count / 2.0) * 0.15
    chrono_score = min(1.0, timeline_events_count / 2.0) * 0.15

    total = geo_score + visual_score + lens_score + chrono_score
    return round(min(1.0, max(0.0, total)), 2)


def generate_case_summary_markdown(
    case_title: str,
    confidence_score: float,
    resolved_location: Optional[GeoCandidate],
    state: OsintGraphState,
    anomalies: Optional[List[Dict[str, Any]]] = None,
    dorks: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Generate structured forensic investigation summary in Markdown format."""
    lines: List[str] = [
        f"# 🔍 OSINT Forensic Dossier: {case_title}",
        "",
        f"**Investigative Status:** Case Closed  ",
        f"**Confidence Rating:** `{int(confidence_score * 100)}%` ({'High Verifiability' if confidence_score >= 0.8 else 'Moderate Confidence' if confidence_score >= 0.5 else 'Low / Tentative'})  ",
        f"**Refinement Cycles:** {state.get('refinement_hops', 0)}  ",
        "",
    ]

    # Insert prominent anomaly & fraud warnings if detected
    if anomalies:
        lines.extend([
            "---",
            "",
            "## 🚨 Detected Forensic Contradictions & Fraud Alerts",
            "",
        ])
        for a in anomalies:
            lines.append(f"### {a.get('title', 'Anomaly Detected')}")
            lines.append(f"> **Severity:** `{a.get('severity', 'warning').upper()}` | **Confidence:** `{int(a.get('confidence', 0.9) * 100)}%`")
            lines.append(f"> {a.get('description', '')}")
            if a.get("claimed_context"):
                lines.append(f"- **Claimed Context:** *{a['claimed_context']}*")
            lines.append(f"- **Authoritative SerpApi Finding:** **{a.get('authoritative_truth', '')}**")
            if a.get("evidence_url"):
                lines.append(f"- **Verification Evidence:** [Direct Source Link]({a['evidence_url']})")
            lines.append("")

    lines.extend([
        "---",
        "",
        "## 📍 Primary Ground Truth & Triangulation",
    ])

    if resolved_location:
        lines.extend([
            f"- **Resolved Landmark / Target:** **{resolved_location.name}**",
            f"- **Street Address:** {resolved_location.address or 'Unspecified vicinity'}",
            f"- **Coordinates (WGS84):** `{resolved_location.latitude:.5f}, {resolved_location.longitude:.5f}`",
            f"- **Place Identifier:** `{resolved_location.place_id or 'N/A'}`",
            f"- **Triangulation Source:** `{resolved_location.engine_source}` (Match Score: `{resolved_location.match_score:.2f}`)",
            f"- **Evidence Note:** {resolved_location.evidence_snippet or 'Direct spatial consensus'}",
        ])
        if resolved_location.source_url:
            lines.append(f"- **Map Reference:** [View on Google Maps]({resolved_location.source_url})")
    else:
        lines.append("- *No definitive geographic coordinates could be confirmed.*")

    lines.extend([
        "",
        "## 🏛️ Forensic Visual Evidence",
    ])
    clues = state.get("visual_clues", [])
    if clues:
        for clue in clues:
            cat = clue.category.value if hasattr(clue.category, "value") else str(clue.category)
            lines.append(f"- `[{cat.upper()}]` **{clue.description}** (Confidence: `{clue.confidence:.2f}`)")
    else:
        lines.append("- *No visual clues decomposed.*")

    lines.extend([
        "",
        "## 🔬 Google Lens Visual Twin Matches",
    ])
    lens_matches = state.get("lens_matches", [])
    if lens_matches:
        for idx, m in enumerate(lens_matches[:3], 1):
            title = m.get("title", "Visual Match")
            source = m.get("source", "Web")
            link = m.get("link", "#")
            lines.append(f"{idx}. **[{title}]({link})** (Source: `{source}`)")
    else:
        lines.append("- *Zero visual twin matches detected.*")

    lines.extend([
        "",
        "## ⏱️ Chronological Provenance & Media Timeline",
    ])
    timeline = state.get("timeline_events", [])
    if timeline:
        for event in timeline:
            origin_badge = " 🟢 *[Earliest Appearance]*" if event.is_origin else ""
            lines.append(f"- **{event.date}** — **{event.title}** ({event.source}){origin_badge}: {event.snippet}")
    else:
        lines.append("- *No external chronological records discovered.*")

    lines.extend([
        "",
        "## 🔗 Verifiable Citation Chain",
    ])
    citations = state.get("citations", [])
    if citations:
        for idx, cit in enumerate(citations, 1):
            lines.append(f"{idx}. `[{cit.engine}]` [{cit.title}]({cit.url}) — *{cit.snippet}*")
    else:
        lines.append("- *Zero external citations.*")

    if dorks:
        lines.extend([
            "",
            "## 🕵️ Targeted OSINT Google Search Dorks",
        ])
        for d in dorks:
            lines.append(f"- **{d.get('category')}:** `{d.get('query')}` — [Execute Query ↗]({d.get('search_url')})")

    return "\n".join(lines)


def case_synthesizer_node(state: OsintGraphState) -> Dict[str, Any]:
    """LangGraph node: Lead Detective synthesis and CaseFile compilation.
    
    Synthesizes multi-engine visual clues, Lens reverse matches, Maps coordinates,
    and News timeline into an authoritative digital forensic dossier.
    """
    logger.info("Executing case_synthesizer_node")

    visual_clues = state.get("visual_clues", [])
    geo_candidates = state.get("geo_candidates", [])
    timeline_events = state.get("timeline_events", [])
    lens_matches = state.get("lens_matches", [])
    citations = state.get("citations", [])
    refinement_hops = state.get("refinement_hops", 0)

    # 1. Resolve primary winning geographic candidate (highest match score)
    resolved_location: Optional[GeoCandidate] = None
    if geo_candidates:
        sorted_candidates = sorted(geo_candidates, key=lambda c: c.match_score, reverse=True)
        resolved_location = sorted_candidates[0]

    # 2. Formulate case title
    top_lens_title = None
    if lens_matches:
        top_m = lens_matches[0]
        top_lens_title = top_m.get("title") if isinstance(top_m, dict) else getattr(top_m, "title", None)

    if resolved_location:
        case_title = f"{resolved_location.name} ({resolved_location.address or 'Identified Vicinity'})"
    elif top_lens_title:
        case_title = f"{top_lens_title}"
    elif state.get("context_hint"):
        case_title = f"{state.get('context_hint')}"
    else:
        case_title = "Mystery Visual Target"

    # 3. Detect anomalies, contradictions, and fraud
    anomalies_objs = AnomalyService.detect_anomalies(
        context_hint=state.get("context_hint"),
        image_path=state.get("image_path"),
        resolved_location=resolved_location,
        lens_matches=lens_matches,
        timeline_events=timeline_events,
    )
    anomalies_dicts = [a.model_dump() for a in anomalies_objs]

    # 4. Generate targeted OSINT Google search dorks
    entity_name = resolved_location.name if resolved_location else (top_lens_title or case_title)
    location_addr = resolved_location.address if resolved_location else ""
    dorks_objs = DorkService.generate_dorks(entity_name, location_addr)
    dorks_dicts = [d.model_dump() for d in dorks_objs]

    # 5. Calculate holistic confidence score
    confidence_score = calculate_confidence_score(
        resolved_location=resolved_location,
        visual_clues_count=len(visual_clues),
        lens_matches_count=len(lens_matches),
        timeline_events_count=len(timeline_events),
    )

    # 6. Generate structured summary Markdown
    summary_markdown = generate_case_summary_markdown(
        case_title=case_title,
        confidence_score=confidence_score,
        resolved_location=resolved_location,
        state=state,
        anomalies=anomalies_dicts,
        dorks=dorks_dicts,
    )

    # 7. Compile final CaseFile
    initial_budget = state.get("initial_budget", 8)
    remaining_budget = state.get("budget_remaining", initial_budget)
    queries_executed = max(0, initial_budget - remaining_budget)

    case_file = CaseFile(
        case_id=f"case_{uuid.uuid4().hex[:8]}",
        title=case_title,
        case_summary=summary_markdown,
        confidence_score=confidence_score,
        resolved_location=resolved_location,
        visual_clues=visual_clues,
        lens_matches=lens_matches,
        timeline=timeline_events,
        citations=citations,
        anomalies=anomalies_dicts,
        dorks=dorks_dicts,
        refinement_hops=refinement_hops,
        serp_queries_executed=queries_executed,
    )

    logger.info(
        "case_synthesizer_node finalized CaseFile '%s' with confidence=%.2f, anomalies=%d, dorks=%d",
        case_file.case_id,
        case_file.confidence_score,
        len(anomalies_dicts),
        len(dorks_dicts),
    )

    return {
        "final_case_file": case_file,
        "status": "case_closed",
    }
