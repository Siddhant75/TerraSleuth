import html
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import streamlit as st
from PIL import Image


def calculate_correspondence_score(rank: int, base_confidence: float = 0.96) -> float:
    """Calculate an explainable visual correspondence score decaying with rank."""
    decay = rank * 0.035
    score = max(0.50, min(0.995, base_confidence - decay))
    return round(score, 3)


def extract_visual_twin_metadata(
    match: Optional[Dict[str, Any]],
    rank: int = 0,
    base_confidence: float = 0.96,
) -> Dict[str, Any]:
    """Extract and sanitize forensic metadata for a Google Lens visual twin."""
    if match is None:
        return {
            "title": "No Visual Twin Identified",
            "domain": "N/A",
            "link": "#",
            "thumbnail_url": None,
            "has_thumbnail": False,
            "score": 0.0,
            "score_label": "0.0% Visual Match",
            "snippet": "No visual provenance matches returned for this target.",
        }

    raw_title = match.get("title") or "Unspecified Match"
    raw_link = match.get("link") or "#"
    if not (raw_link.startswith("http://") or raw_link.startswith("https://")):
        raw_link = "#"
    raw_source = match.get("source") or ""
    thumbnail_url = match.get("thumbnail")
    snippet = match.get("snippet") or ""

    domain = raw_source
    if not domain and raw_link and raw_link != "#":
        try:
            parsed = urlparse(raw_link)
            domain = parsed.netloc or "Unknown Domain"
        except Exception:
            domain = "Unknown Domain"
    if not domain:
        domain = "Unknown Domain"

    score = calculate_correspondence_score(rank, base_confidence)
    score_label = f"{score * 100:.1f}% Visual Correspondence"

    return {
        "title": raw_title,
        "domain": domain,
        "link": raw_link,
        "thumbnail_url": thumbnail_url,
        "has_thumbnail": bool(thumbnail_url and str(thumbnail_url).strip()),
        "score": score,
        "score_label": score_label,
        "snippet": snippet,
    }


def render_visual_twin_comparator(
    suspect_image: Any,
    lens_matches: Optional[List[Dict[str, Any]]],
    base_confidence: float = 0.96,
) -> None:
    """Render side-by-side comparison of suspect image and top Google Lens match."""
    st.markdown("#### 🔬 Visual Twin Forensic Comparator")
    st.caption("Direct visual alignment between submitted evidence and Google Lens authoritative match.")

    matches = lens_matches or []
    if not matches:
        st.info("ℹ️ No Google Lens visual matches identified for this target.")
        if suspect_image:
            st.image(suspect_image, caption="Suspect Target (Unmatched)", use_container_width=True)
        return

    # Match selector if multiple matches exist
    selected_idx = 0
    if len(matches) > 1:
        match_options = [
            f"#{i+1}: {m.get('title', 'Match')[:40]} ({m.get('source', 'Web')})"
            for i, m in enumerate(matches[:5])
        ]
        chosen = st.selectbox(
            "Select Authoritative Twin to Compare:",
            options=match_options,
            index=0,
            key="visual_twin_selector",
        )
        selected_idx = match_options.index(chosen)

    primary_match = matches[selected_idx]
    meta = extract_visual_twin_metadata(primary_match, rank=selected_idx, base_confidence=base_confidence)

    # 50/50 Side-by-Side Visual Alignment Columns
    col_suspect, col_match = st.columns(2)

    with col_suspect:
        st.markdown(
            """
            <div style="background: #111827; border: 1px solid #374151; border-top: 3px solid #ef4444; padding: 6px 10px; border-radius: 4px; margin-bottom: 8px;">
                <span style="font-size: 11px; font-weight: 700; font-family: monospace; color: #f87171;">SUSPECT TARGET [EVIDENCE]</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if suspect_image:
            st.image(suspect_image, use_container_width=True)
        else:
            st.warning("Suspect image source unavailable.")

    with col_match:
        st.markdown(
            f"""
            <div style="background: #111827; border: 1px solid #374151; border-top: 3px solid #10b981; padding: 6px 10px; border-radius: 4px; margin-bottom: 8px;">
                <span style="font-size: 11px; font-weight: 700; font-family: monospace; color: #34d399;">AUTHORITATIVE MATCH [GOOGLE LENS]</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if meta["has_thumbnail"]:
            try:
                st.image(meta["thumbnail_url"], use_container_width=True)
            except Exception:
                st.markdown(
                    """
                    <div style="background: #090d16; border: 1px dashed #334155; border-radius: 6px; padding: 30px; text-align: center; color: #94a3b8;">
                        <div style="font-size: 24px;">🌐</div>
                        <div style="font-size: 12px; margin-top: 8px;">Remote thumbnail protected or unreachable</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div style="background: #090d16; border: 1px dashed #334155; border-radius: 6px; padding: 30px; text-align: center; color: #94a3b8;">
                    <div style="font-size: 24px;">🔍</div>
                    <div style="font-size: 12px; margin-top: 8px;">Authoritative textual match verified (no thumbnail)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Forensic Verification Card
    safe_title = html.escape(str(meta["title"]))
    safe_domain = html.escape(str(meta["domain"]))
    safe_score_label = html.escape(str(meta["score_label"]))
    safe_link = html.escape(str(meta["link"]))

    st.markdown(
        f"""
        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 12px 16px; margin-top: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div style="font-size: 11px; font-family: monospace; color: #94a3b8; text-transform: uppercase;">VERIFIED VISUAL SOURCE</div>
                    <div style="font-size: 15px; font-weight: 700; color: #38bdf8; margin-top: 2px;">{safe_title}</div>
                    <div style="font-size: 12px; font-family: monospace; color: #a5b4fc; margin-top: 2px;">Provenance Domain: {safe_domain}</div>
                </div>
                <div style="background: #064e3b; border: 1px solid #059669; padding: 6px 12px; border-radius: 20px;">
                    <span style="font-size: 12px; font-weight: 700; font-family: monospace; color: #6ee7b7;">🎯 {safe_score_label}</span>
                </div>
            </div>
            <div style="margin-top: 10px; border-top: 1px solid #1e293b; padding-top: 8px;">
                <a href="{safe_link}" target="_blank" style="color: #60a5fa; font-size: 12px; font-family: monospace; text-decoration: none;">
                    🔗 Inspect Original Source Publication &rarr;
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
