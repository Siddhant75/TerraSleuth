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
from frontend.components.geo_map import render_geo_map
from frontend.components.visual_evidence_board import render_visual_evidence_board

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
    .main {
        background-color: #0b0e14;
        color: #e6f1ff;
    }
    .stMetric {
        background-color: #141923;
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
    .hero-badge {
        background-color: #1e3a8a;
        color: #93c5fd;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 8px;
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
                    f"""
                    <div class="agent-step-box">
                        <b>✅ {title}</b> — <i>Status: <code>{status_text}</code></i>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if "final_case_file" in node_output and node_output["final_case_file"]:
                    final_case_file = node_output["final_case_file"]
                accumulated_state = node_output

        st.session_state["case_file"] = final_case_file
        st.session_state["last_state"] = accumulated_state
        st.success("Investigation Concluded: Digital Forensic Dossier compiled successfully!")

    # Render Results if Case File exists
    case_file: Optional[CaseFile] = st.session_state.get("case_file")
    if case_file:
        st.markdown("---")

        # Top Executive Metrics Bar
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Primary Target", case_file.resolved_location.name if case_file.resolved_location else "Unidentified")
        with m2:
            st.metric(
                "Coordinates",
                f"{case_file.resolved_location.latitude:.4f}, {case_file.resolved_location.longitude:.4f}"
                if case_file.resolved_location else "N/A",
            )
        with m3:
            conf_pct = int(case_file.confidence_score * 100)
            st.metric("Confidence Score", f"{conf_pct}%", delta="High Verifiability" if conf_pct >= 80 else "Moderate")
        with m4:
            st.metric("SerpApi Queries Executed", case_file.serp_queries_executed)
        with m5:
            st.metric("Refinement Cycles", case_file.refinement_hops)

        # 4 Interactive Evidence Tabs
        tab_map, tab_vision, tab_chrono, tab_citations, tab_dossier = st.tabs([
            "🗺️ Geospatial Pinpoint & Map",
            "🔍 Visual Evidence Board",
            "⏱️ Chronological Provenance",
            "🔗 Verifiable Citation Chain",
            "📄 Executive Markdown Dossier",
        ])

        with tab_map:
            render_geo_map(case_file.resolved_location)

        with tab_vision:
            # Load active image or dummy placeholder
            img_to_display = config.get("active_image")
            if not img_to_display and config.get("image_path") and os.path.exists(config["image_path"]):
                img_to_display = Image.open(config["image_path"])
            if not img_to_display:
                img_to_display = Image.new("RGB", (800, 600), color=(20, 24, 33))

            render_visual_evidence_board(img_to_display, case_file.visual_clues)

        with tab_chrono:
            render_chronology_timeline(case_file.timeline)

        with tab_citations:
            render_citation_ledger(case_file.citations)

        with tab_dossier:
            st.markdown(case_file.case_summary)

        # Export & Download Buttons
        st.markdown("---")
        st.markdown("### 📥 Export Case Dossier")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="Download Case Dossier (JSON)",
                data=case_file.model_dump_json(indent=2),
                file_name=f"{case_file.case_id}_dossier.json",
                mime="application/json",
                use_container_width=True,
            )
        with col_d2:
            st.download_button(
                label="Download Executive Summary (Markdown)",
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
