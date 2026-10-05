import html
import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


def sanitize_url(url: Optional[str]) -> Optional[str]:
    """Ensure URL strictly uses http or https schemes."""
    if url and (url.startswith("http://") or url.startswith("https://")):
        return html.escape(url, quote=True)
    return None


def render_chronology_timeline(
    timeline_events: List[Any],
    streamlit_context: Any = None,
):
    """Render the chronological provenance timeline in Streamlit."""
    import streamlit as st

    ctx = streamlit_context or st

    ctx.markdown("### ⏱️ Chronological Provenance & Media Timeline")
    ctx.caption("Audited historical publication milestones and viral circulation timeline via Google News.")

    if not timeline_events:
        ctx.info("No chronological events or media appearances documented.")
        return

    for idx, event in enumerate(timeline_events):
        raw_date = getattr(event, "date", "Unknown Date") or "Unknown Date"
        raw_title = getattr(event, "title", "Media Event") or "Media Event"
        raw_source = getattr(event, "source", "News Source") or "News Source"
        raw_snippet = getattr(event, "snippet", "") or ""
        raw_url = getattr(event, "url", None)
        is_origin = getattr(event, "is_origin", False)

        safe_date = html.escape(str(raw_date))
        safe_title = html.escape(str(raw_title))
        safe_source = html.escape(str(raw_source))
        safe_snippet = html.escape(str(raw_snippet))
        safe_url = sanitize_url(raw_url)

        badge_html = """
        <span style="background-color: #27ae60; color: white; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 600; margin-left: 8px;">
            EARLIEST KNOWN APPEARANCE
        </span>
        """ if is_origin else ""

        border_color = "#2ecc71" if is_origin else "#34495e"

        st.markdown(
            f"""
            <div style="background-color: #1a1e24; padding: 14px 18px; border-radius: 8px; border-left: 5px solid {border_color}; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-size: 13px; font-weight: 700; color: #64ffda;">📅 {safe_date}</span>
                    <span style="font-size: 12px; color: #8892b0;">Published by: <b>{safe_source}</b></span>
                </div>
                <div style="font-size: 15px; font-weight: 600; color: #ffffff; margin-top: 6px;">
                    {safe_title} {badge_html}
                </div>
                <div style="font-size: 13px; color: #ccd6f6; margin-top: 6px; line-height: 1.4;">
                    "{safe_snippet}"
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if safe_url:
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;🔗 [Read full article / source archive]({safe_url})")
