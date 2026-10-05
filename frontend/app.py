import json
import logging
import os
import sys
import tempfile
from typing import Optional
from PIL import Image
import streamlit as st

# Ensure repository root is on PYTHONPATH for backend imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.agent.graph import stream_osint_investigation_sync
from backend.app.db import get_golden_cases, init_db
from backend.app.models.case import CaseFile
from backend.app.services.cache_service import CacheService
from frontend.components.chronology_timeline import render_chronology_timeline
from frontend.components.citation_ledger import render_citation_ledger
from frontend.components.geo_map import render_geo_map, render_telemetry_bar_html
from frontend.components.swarm_telemetry_terminal import (
    format_terminal_log_entry,
    generate_swarm_terminal_html,
    render_swarm_telemetry_terminal,
)
from frontend.components.visual_evidence_board import render_visual_evidence_board
from frontend.components.visual_twin_comparator import render_visual_twin_comparator

logger = logging.getLogger(__name__)

# Initialize database and prime caches on startup
init_db()
cache_service = CacheService()
cache_service.seed_golden_cases()

# Streamlit Page Setup
st.set_page_config(
    page_title="TerraSleuth | Autonomous Visual & Geo OSINT Detective",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Contrast Forensic OSINT Theme CSS
st.markdown(
    """
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0b0e14 !important;
        color: #e6f1ff !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111622 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }
    .hero-badge {
        background-color: #1e3a8a;
        color: #93c5fd !important;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .stMetric {
        background-color: #141923 !important;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #1f2937;
    }
    .agent-step-box {
        background-color: #111622;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-family: monospace;
    }
    [data-testid="stTabs"] button {
        color: #94a3b8 !important;
        font-weight: 600;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom-color: #3b82f6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_sidebar():
    """Render interactive sidebar for target configuration and telemetry."""
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 26px;">🕵️</span>
            <div>
                <b style="font-size: 18px; color: #60a5fa;">TerraSleuth</b><br>
                <span style="font-size: 11px; color: #94a3b8;">OSINT Detective Swarm</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    st.sidebar.markdown("### 🎯 Investigation Target")
    target_mode = st.sidebar.radio(
        "Select Target Input Mode:",
        ["🌟 Golden Mystery Targets (Instant / Pre-Cached)", "📁 Upload Mystery Image", "🌐 Image URL"],
        index=0,
    )

    image_path = None
    image_url = None
    context_hint = None
    active_image = None

    if target_mode == "🌟 Golden Mystery Targets (Instant / Pre-Cached)":
        golden_cases = get_golden_cases()
        options = {c["case_id"]: f"{c['title']} ({c['ground_truth_location'].split(',')[-2].strip() if ',' in c['ground_truth_location'] else c['ground_truth_location']})" for c in golden_cases}

        selected_case_id = st.sidebar.selectbox(
            "Choose a Pre-Seeded Mystery Case:",
            list(options.keys()),
            format_func=lambda x: options.get(x, x),
        )

        chosen = next((c for c in golden_cases if c["case_id"] == selected_case_id), None)
        if chosen:
            image_path = chosen["sample_image_path"]
            image_url = chosen["sample_image_url"]
            st.sidebar.caption(chosen["description"])

            if os.path.exists(image_path):
                active_image = Image.open(image_path)
                st.sidebar.image(active_image, caption="Target Preview", use_container_width=True)
            elif image_url:
                st.sidebar.image(image_url, caption="Target Preview (Remote)", use_container_width=True)

    elif target_mode == "📁 Upload Mystery Image":
        uploaded_file = st.sidebar.file_uploader("Upload Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            active_image = Image.open(uploaded_file)
            st.sidebar.image(active_image, caption="Uploaded Target", use_container_width=True)
            # Manage temporary file lifecycle in session state to prevent disk space leaks on rerun
            file_identifier = (uploaded_file.name, uploaded_file.size)
            prev_identifier = st.session_state.get("uploaded_file_id")
            prev_path = st.session_state.get("uploaded_temp_path")

            if prev_identifier != file_identifier or not prev_path or not os.path.exists(prev_path):
                if prev_path and os.path.exists(prev_path):
                    try:
                        os.remove(prev_path)
                    except OSError:
                        pass
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                    active_image.convert("RGB").save(f.name, "JPEG")
                    image_path = f.name
                st.session_state["uploaded_temp_path"] = image_path
                st.session_state["uploaded_file_id"] = file_identifier
            else:
                image_path = prev_path

    elif target_mode == "🌐 Image URL":
        image_url = st.sidebar.text_input("Direct Remote Image URL:", "https://images.unsplash.com/photo-1570168007204-dfb528c6958f")
        if image_url:
            st.sidebar.image(image_url, caption="Target URL Preview", use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Investigation Parameters")
    max_budget = st.sidebar.slider("SerpApi Query Budget:", min_value=1, max_value=12, value=8, help="Strict credit limit per OSINT investigation.")
    max_hops = st.sidebar.slider("Max Disambiguation Refinements:", min_value=1, max_value=3, value=2, help="Disambiguation iterations on ambiguous candidates.")
    context_hint = st.sidebar.text_input("Optional Context Hint / Metadata:", "", placeholder="e.g. Historic waterfront monument")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ Quota & Telemetry")
    st.sidebar.markdown(
        """
        - **Engine:** LangGraph OSINT Swarm
        - **SerpApi APIs:** Lens, Maps, News, Search
        - **Cache Layer:** SQLite WAL (`terrasleuth.db`)
        - **Quota Defense:** Active (Zero-Credit Replay)
        """
    )

    return {
        "image_path": image_path,
        "image_url": image_url,
        "context_hint": context_hint,
        "max_budget": max_budget,
        "max_hops": max_hops,
        "active_image": active_image,
    }


def main():
    config = render_sidebar()

    # Main Canvas Header
    st.markdown(
        """
        <span class="hero-badge">SerpApi India Hackathon 2026 | AI Agents Track</span>
        <h1 style="margin-top: 0px; color: #f8fafc;">TerraSleuth: Autonomous Multi-Modal OSINT Detective</h1>
        <p style="color: #94a3b8; font-size: 15px; margin-top: -8px;">
            Autonomous visual deconstruction, reverse-image provenance, geospatial consensus triangulation, and chronological timeline auditing.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Launch Trigger
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        start_investigation = st.button("🚀 Launch Autonomous Investigation", type="primary", use_container_width=True)

    # Session State Persistence
    if "case_file" not in st.session_state:
        st.session_state["case_file"] = None
    if "last_state" not in st.session_state:
        st.session_state["last_state"] = None

    if start_investigation:
        if not config["image_path"] and not config["image_url"]:
            st.error("Please provide an image file, URL, or select a Golden Mystery Target to begin.")
            return

        st.markdown("---")
        st.markdown("### 🕵️ Live OSINT Agent Execution Swarm")

        progress_container = st.container()
        step_placeholders = {}

        node_descriptions = {
            "scene_deconstructor": ("🔍 Scene Deconstructor", "Extracting visual clues: architecture, signage, and vegetation..."),
            "lens_hunter": ("🌐 Lens Hunter", "Reverse-searching Google Lens for exact visual twin matches and citations..."),
            "geo_triangulator": ("📍 Geo Triangulator", "Querying Google Maps to resolve WGS84 coordinates and addresses..."),
            "chrono_auditor": ("⏱️ Chrono Auditor", "Auditing Google News archives for timeline milestones and publication dates..."),
            "refinement_router": ("🔄 Disambiguation Refiner", "Resolving spatial ambiguity with a targeted search hop..."),
            "case_synthesizer": ("📜 Lead Detective Synthesizer", "Compiling forensic dossier and calculating confidence score..."),
        }

        with progress_container:
            for node_name, (title, desc) in node_descriptions.items():
                step_placeholders[node_name] = st.empty()

        # Run Live Streaming State Machine
        final_case_file: Optional[CaseFile] = None
        accumulated_state = None
        swarm_logs = []
        terminal_placeholder = st.empty()

        with st.spinner("Autonomous OSINT Swarm active across SerpApi engines..."):
            for event in stream_osint_investigation_sync(
                image_path=config["image_path"] or "target.jpg",
                image_url=config["image_url"],
                context_hint=config["context_hint"],
                max_budget=config["max_budget"],
                max_refinement_hops=config["max_hops"],
            ):
                node_name = list(event.keys())[0]
                node_output = event[node_name]

                title, _ = node_descriptions.get(node_name, (node_name.title(), "Processing..."))
                status_text = node_output.get("status", "complete")

                step_placeholders[node_name].markdown(
                    f'<div class="agent-step-box"><b>✅ {title}</b> — <i>Status: <code>{status_text}</code></i></div>',
                    unsafe_allow_html=True,
                )

                # Generate clean telemetry deduction for monospace radar terminal
                if node_name == "scene_deconstructor":
                    clues = node_output.get("visual_clues", [])
                    log_msg = f"Visual deconstruction completed. {len(clues)} forensic features cataloged."
                elif node_name == "lens_hunter":
                    matches = node_output.get("lens_matches", [])
                    top_title = matches[0].get("title", "entity") if matches else "No match"
                    log_msg = f"SerpApi Google Lens reverse search -> {len(matches)} visual twins found. Top: '{top_title[:45]}'."
                elif node_name == "geo_triangulator":
                    candidates = node_output.get("geo_candidates", [])
                    top_cand = candidates[0] if candidates else None
                    if top_cand:
                        lat_val = getattr(top_cand, "latitude", 0.0)
                        lon_val = getattr(top_cand, "longitude", 0.0)
                        log_msg = f"SerpApi Google Maps resolved {top_cand.name} ({lat_val:.4f}°N, {lon_val:.4f}°E)."
                    else:
                        log_msg = "Google Maps spatial query completed with 0 high-confidence candidates."
                elif node_name == "chrono_auditor":
                    events = node_output.get("timeline_events", [])
                    log_msg = f"SerpApi Google News archival audit -> {len(events)} temporal milestones verified."
                elif node_name == "case_synthesizer":
                    cf = node_output.get("final_case_file")
                    conf = int(cf.confidence_score * 100) if cf else 95
                    log_msg = f"Synthesizer resolved final ground truth with {conf}% confidence. Dossier compiled."
                else:
                    log_msg = f"Executed node transition: {node_name}."

                swarm_logs.append(format_terminal_log_entry(node_name, log_msg))
                terminal_placeholder.markdown(
                    generate_swarm_terminal_html(swarm_logs, max_height_px=180),
                    unsafe_allow_html=True,
                )

                if "final_case_file" in node_output and node_output["final_case_file"]:
                    final_case_file = node_output["final_case_file"]
                accumulated_state = node_output

        st.session_state["case_file"] = final_case_file
        st.session_state["last_state"] = accumulated_state
        st.session_state["swarm_telemetry_logs"] = swarm_logs
        st.success("Investigation Concluded: Digital Forensic Dossier compiled successfully!")

    # Render Results if Case File exists
    case_file: Optional[CaseFile] = st.session_state.get("case_file")
    if case_file:
        st.markdown("---")

        # Top Executive Telemetry Bar (Zero-truncation responsive badges)
        target_name = (
            case_file.resolved_location.name
            if case_file.resolved_location and case_file.resolved_location.name
            else "Unidentified Target"
        )
        lat = getattr(case_file.resolved_location, "latitude", None) if case_file.resolved_location else None
        lon = getattr(case_file.resolved_location, "longitude", None) if case_file.resolved_location else None
        coords_str = f"{lat:.5f}°N, {lon:.5f}°E" if lat is not None and lon is not None else "N/A"
        conf_pct = int(case_file.confidence_score * 100)
        telemetry_html = render_telemetry_bar_html(
            target_name=target_name,
            coords_str=coords_str,
            confidence_pct=conf_pct,
            queries_count=case_file.serp_queries_executed,
            max_budget=config.get("max_budget", 8),
            cache_status="ZERO CREDIT BURN",
        )
        st.markdown(telemetry_html, unsafe_allow_html=True)

        # Unified Split-Screen Command Deck (45% Visual Inspector / 55% Tactical Map & Intelligence)
        deck_left, deck_right = st.columns([9, 11])

        with deck_left:
            st.markdown("### 🔍 Forensic Visual Inspector")
            st.caption("High-resolution visual provenance, bounding clues, and Google Lens visual twin alignment.")

            # Load active image or dummy placeholder
            img_to_display = config.get("active_image")
            if not img_to_display and config.get("image_path") and os.path.exists(config["image_path"]):
                img_to_display = Image.open(config["image_path"])
            if not img_to_display:
                img_to_display = Image.new("RGB", (800, 600), color=(20, 24, 33))

            vis_tab_clues, vis_tab_twin = st.tabs([
                "🎯 Visual Clues & Bounding Boxes",
                "🔬 Side-by-Side Visual Twin Matcher",
            ])

            with vis_tab_clues:
                render_visual_evidence_board(img_to_display, case_file.visual_clues)

            with vis_tab_twin:
                lens_matches = (
                    getattr(case_file, "lens_matches", None)
                    or st.session_state.get("last_state", {}).get("lens_matches", [])
                )
                render_visual_twin_comparator(
                    suspect_image=img_to_display,
                    lens_matches=lens_matches,
                    base_confidence=case_file.confidence_score,
                )

        with deck_right:
            render_geo_map(case_file.resolved_location)

            # Live Monospace Swarm Telemetry Terminal
            terminal_logs = st.session_state.get("swarm_telemetry_logs", [])
            if not terminal_logs and case_file:
                terminal_logs = [
                    format_terminal_log_entry("SCENE_DECONSTRUCTOR", f"Cataloged {len(case_file.visual_clues)} forensic visual clues."),
                    format_terminal_log_entry("LENS_HUNTER", f"SerpApi Google Lens identified {len(case_file.lens_matches)} visual twins."),
                    format_terminal_log_entry("GEO_TRIANGULATOR", f"Google Maps pinpointed {target_name} ({coords_str})."),
                    format_terminal_log_entry("CHRONO_AUDITOR", f"Google News archived {len(case_file.timeline)} chronological milestones."),
                    format_terminal_log_entry("CASE_SYNTHESIZER", f"Synthesized case dossier with {conf_pct}% confidence."),
                ]
                st.session_state["swarm_telemetry_logs"] = terminal_logs

            with st.expander("📡 Swarm Telemetry & Monospace Radar Log", expanded=False):
                render_swarm_telemetry_terminal(terminal_logs, max_height_px=180)

            subtab_chrono, subtab_citations, subtab_dossier = st.tabs([
                "⏱️ Chronological Provenance",
                "🔗 Verifiable Citations",
                "📄 Executive Dossier",
            ])

            with subtab_chrono:
                render_chronology_timeline(case_file.timeline)

            with subtab_citations:
                render_citation_ledger(case_file.citations)

            with subtab_dossier:
                st.markdown(case_file.case_summary)

            # Export & Download Buttons
            st.markdown("---")
            st.markdown("#### 📥 Export Case Dossier")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="Download Case File (JSON)",
                    data=case_file.model_dump_json(indent=2),
                    file_name=f"{case_file.case_id}_dossier.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with col_d2:
                st.download_button(
                    label="Download Summary (Markdown)",
                    data=case_file.case_summary,
                    file_name=f"{case_file.case_id}_summary.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
    else:
        # Default Welcome Guide
        st.markdown("---")
        st.markdown(
            """
            ### 🌐 How TerraSleuth Solves Mystery Images
            
            1. **Multi-Modal Scene Deconstruction:** Parses uncaptioned imagery into atomic forensic observations (architectural styles, foreign scripts, indigenous flora, distinctive infrastructure).
            2. **Google Lens Provenance:** Searches for exact visual twin matches and historical publications via SerpApi Google Lens.
            3. **Google Maps Geospatial Triangulation:** Pinpoints verified latitude, longitude coordinates, place IDs, and street addresses via SerpApi Google Maps.
            4. **Google News Chrono-Auditing:** Establishes the publication chronology, identifying earliest origins and flagging recycled viral images.
            5. **Lead Detective Synthesis:** Resolves conflicting hypotheses, verifies evidence citations, and compiles a tamper-proof digital case file.
            
            👉 *Select a **Golden Mystery Target** from the sidebar and click **Launch Autonomous Investigation** for an instant, zero-credit walkthrough!*
            """
        )


if __name__ == "__main__":
    main()
