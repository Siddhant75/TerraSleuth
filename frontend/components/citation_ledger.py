import html
from collections import defaultdict
import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

ENGINE_LABELS = {
    "google_lens": ("Google Lens", "🔍", "#3498db"),
    "google_maps": ("Google Maps & Local", "📍", "#e74c3c"),
    "google_news": ("Google News", "📰", "#2ecc71"),
    "google": ("Google Search", "🌐", "#f39c12"),
}


def sanitize_url(url: Optional[str]) -> str:
    """Ensure URL strictly uses http or https schemes."""
    if url and (url.startswith("http://") or url.startswith("https://")):
        return html.escape(url, quote=True)
    return "#"


def render_citation_ledger(
    citations: List[Any],
    streamlit_context: Any = None,
):
    """Render verifiable multi-engine citation ledger grouped by SerpApi engine in Streamlit."""
    import streamlit as st

    ctx = streamlit_context or st

    ctx.markdown("### 🔗 Verifiable Evidentiary Citation Ledger")
    ctx.caption("Chain-of-custody verification: all forensic deductions anchored directly to authoritative SerpApi search records.")

    if not citations:
        ctx.info("No external citations compiled in this investigation.")
        return

    # Group citations by engine
    grouped = defaultdict(list)
    for cit in citations:
        engine = getattr(cit, "engine", "google").lower()
        grouped[engine].append(cit)

    # Render counts summary pills
    summary_cols = ctx.columns(max(1, len(grouped)))
    for idx, (engine, items) in enumerate(grouped.items()):
        label, icon, color = ENGINE_LABELS.get(engine, (engine.title(), "📄", "#95a5a6"))
        with summary_cols[idx % len(summary_cols)]:
            st.metric(f"{icon} {label}", f"{len(items)} sources")

    ctx.markdown("---")

    # Render citations by engine tab / section
    for engine, items in grouped.items():
        label, icon, color = ENGINE_LABELS.get(engine, (engine.title(), "📄", "#95a5a6"))
        with ctx.expander(f"{icon} {label} Evidence Trail ({len(items)} citations)", expanded=True):
            for i, cit in enumerate(items, 1):
                raw_title = getattr(cit, "title", "Evidentiary Match") or "Evidentiary Match"
                raw_url = getattr(cit, "url", "#")
                raw_snippet = getattr(cit, "snippet", "") or ""

                safe_title = html.escape(str(raw_title))
                safe_snippet = html.escape(str(raw_snippet))
                safe_url = sanitize_url(raw_url)

                st.markdown(
                    f"""
                    <div style="background-color: #14171d; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid {color};">
                        <div style="font-size: 14px; font-weight: 600;">
                            <a href="{safe_url}" target="_blank" style="color: #64ffda; text-decoration: none;">
                                {i}. {safe_title} ↗
                            </a>
                        </div>
                        <div style="font-size: 12px; color: #a8b2d1; margin-top: 4px;">
                            <i>"{safe_snippet}"</i>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
