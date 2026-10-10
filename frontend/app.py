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

from backend.app.agent.graph import (
    stream_dialectical_investigation_sync,
    stream_osint_investigation_sync,
)
from backend.app.db import get_golden_cases, init_db
from backend.app.models.case import CaseFile
from backend.app.services.cache_service import CacheService
from frontend.components.swarm_telemetry_terminal import (
    format_terminal_log_entry,
    generate_swarm_terminal_html,
)
from frontend.components.tactical_command_deck import render_tactical_command_deck
from frontend.components.war_room_hud import (
    render_mission_briefing,
    render_war_room_header,
)

logger = logging.getLogger(__name__)

# Initialize database and prime caches on startup
init_db()
cache_service = CacheService()
cache_service.seed_golden_cases()

# Streamlit Page Setup
st.set_page_config(
    page_title="TerraSleuth // OSINT Forensic Command Deck",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Contrast Tactical Cyber Theme CSS with Neon Pulse Animation
st.markdown(
    """
    <style>
    @keyframes pulse-cyan {
        0%, 100% { box-shadow: 0 0 15px rgba(0, 242, 254, 0.3); border-color: rgba(0, 242, 254, 0.4); }
        50% { box-shadow: 0 0 25px rgba(0, 242, 254, 0.6); border-color: rgba(0, 242, 254, 0.7); }
    }
    .neon-pulse {
        animation: pulse-cyan 3s infinite;
    }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #07090e !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0d121d !important;
        border-right: 1px solid rgba(0, 242, 254, 0.2) !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }
    /* Button Cyber Overrides */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.6) !important;
        border-color: #38bdf8 !important;
    }
    [data-testid="stTabs"] button {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #0284c7 !important;
    }
    .radar-node-badge {
        background: #111726;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: ui-monospace, monospace;
        font-size: 12px;
    }
    .radar-node-active {
        border-color: #38bdf8;
        background: rgba(14, 165, 233, 0.1);
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_sidebar():
    """Render interactive sidebar for target configuration and telemetry."""
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <span style="font-size: 28px;">🕵️</span>
            <div>
                <b style="font-size: 18px; color: #38bdf8; letter-spacing: 0.5px;">TERRASLEUTH</b><br>
                <span style="font-size: 11px; color: #94a3b8; font-family: ui-monospace, monospace;">OSINT DETECTIVE SWARM</span>
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
    truth_lat = None
    truth_lon = None

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
            context_hint = chosen.get("context_hint", "")
            truth_lat = chosen.get("ground_truth_lat")
            truth_lon = chosen.get("ground_truth_lon")
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
    st.sidebar.markdown("### 🔑 SerpApi Credentials & Mode")
    env_api_key = os.environ.get("SERPAPI_API_KEY", "")
    session_key = st.session_state.get("serpapi_api_key", env_api_key)

    api_key_input = st.sidebar.text_input(
        "SerpApi API Key:",
        value=session_key,
        type="password",
        placeholder="Enter your SerpApi API key...",
        help="Enter your SerpApi API key to execute live web queries across Google Lens, Maps, News, and Search.",
    )
    if api_key_input:
        st.session_state["serpapi_api_key"] = api_key_input.strip()

    has_valid_key = bool(
        st.session_state.get("serpapi_api_key")
        and str(st.session_state.get("serpapi_api_key")).strip() != ""
        and "your_serpapi" not in str(st.session_state.get("serpapi_api_key")).lower()
    )

    if has_valid_key:
        st.sidebar.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 6px; padding: 6px 10px; margin-bottom: 8px;">
                <span style="color: #10b981; font-weight: 600; font-size: 12px;">🟢 Live SerpApi Connected</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        live_mode = st.sidebar.checkbox(
            "🌐 Live Network Mode (Bypass Cache)",
            value=st.session_state.get("live_network_mode", False),
            help="When enabled, bypasses SQLite disk cache and dispatches real-time queries directly to SerpApi.",
        )
        st.session_state["live_network_mode"] = live_mode
    else:
        st.sidebar.markdown(
            """
            <div style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px;">
                <span style="color: #38bdf8; font-weight: 600; font-size: 12px;">🛡️ Offline Zero-Credit Mode</span><br>
                <span style="color: #94a3b8; font-size: 11px;">Golden benchmarks execute 100% cached. Enter API key above for live web search.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        live_mode = False
        st.session_state["live_network_mode"] = False

    # Optional Google AI Studio (Gemini) Key for Semantic Intent & Entity Disambiguation
    env_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    session_gemini_key = st.session_state.get("gemini_api_key", env_gemini_key)

    gemini_key_input = st.sidebar.text_input(
        "Google AI Studio Key (Optional):",
        value=session_gemini_key,
        type="password",
        placeholder="Enter Gemini API key for semantic reasoning...",
        help="Enables Level 4/5 semantic intent & entity reasoning across open-world imagery.",
    )
    if gemini_key_input:
        st.session_state["gemini_api_key"] = gemini_key_input.strip()

    has_valid_gemini = bool(
        st.session_state.get("gemini_api_key")
        and str(st.session_state.get("gemini_api_key")).strip() != ""
        and "your_gemini" not in str(st.session_state.get("gemini_api_key")).lower()
    )

    if has_valid_gemini:
        st.sidebar.markdown(
            """
            <div style="background: rgba(168, 85, 247, 0.15); border: 1px solid #a855f7; border-radius: 6px; padding: 6px 10px; margin-bottom: 8px;">
                <span style="color: #c084fc; font-weight: 600; font-size: 12px;">🟣 Gemini AI Reasoner Active</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px;">
                <span style="color: #fbbf24; font-weight: 600; font-size: 12px;">⚡ Deterministic Heuristics Active</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Swarm Parameters")
    max_budget = st.sidebar.slider("SerpApi Query Budget:", min_value=1, max_value=12, value=8, help="Strict credit limit per OSINT investigation.")
    max_hops = st.sidebar.slider("Max Disambiguation Refinements:", min_value=1, max_value=3, value=2, help="Disambiguation iterations on ambiguous candidates.")
    context_hint_input = st.sidebar.text_input("Claimed Context Hint / Metadata:", value=context_hint or "", placeholder="e.g. Miami rental listing, Breaking 2026 disaster...")

    user_directive_input = st.sidebar.text_input(
        "🎯 Mission Directive (HITL Prompt):",
        value=st.session_state.get("user_directive", ""),
        placeholder="e.g. Focus on handbag & watch, check Kyoto temple...",
        help="Natural language directive guiding Vision LLM detection and crop prioritization.",
    )
    if user_directive_input:
        st.session_state["user_directive"] = user_directive_input.strip()

    return {
        "image_path": image_path,
        "image_url": image_url,
        "context_hint": context_hint_input,
        "max_budget": max_budget,
        "max_hops": max_hops,
        "active_image": active_image,
        "truth_lat": truth_lat,
        "truth_lon": truth_lon,
        "api_key": st.session_state.get("serpapi_api_key") if has_valid_key else None,
        "live_mode": live_mode,
        "gemini_api_key": st.session_state.get("gemini_api_key") if has_valid_gemini else None,
        "user_directive": st.session_state.get("user_directive"),
        "selected_object_labels": st.session_state.get("selected_object_labels"),
    }


def main():
    config = render_sidebar()

    # Render Forensic Command Deck Header Banner
    render_war_room_header()

    # Session State Persistence
    if "case_file" not in st.session_state:
        st.session_state["case_file"] = None
    if "last_state" not in st.session_state:
        st.session_state["last_state"] = None
    if "swarm_telemetry_logs" not in st.session_state:
        st.session_state["swarm_telemetry_logs"] = []

    # Pure Product Experience: Tactical Command Deck is the Primary Mission View
    if not st.session_state.get("case_file"):
        render_mission_briefing()

        # Primary Launch Trigger Button centered on Main Canvas
        launch_col1, launch_col2, launch_col3 = st.columns([1, 4, 1])
        with launch_col2:
            start_investigation = st.button(
                "⚡ Launch Autonomous Investigation (Execute Swarm)",
                type="primary",
                use_container_width=True,
                key="launch_swarm_btn",
                help="Execute LangGraph multi-agent swarm across Google Lens, Google Maps, and Google News.",
            )
    else:
        start_investigation = False

    if start_investigation:
        if not config["image_path"] and not config["image_url"]:
            st.error("Please provide an image file, URL, or select a Golden Mystery Target to begin.")
            return

        st.markdown("---")
        st.markdown("### 📡 Live Multi-Agent Swarm Radar")

        radar_col, terminal_col = st.columns([1, 1])
        step_placeholders = {}

        node_descriptions = {
            "scene_deconstructor": ("🔍 SCENE_DECONSTRUCTOR", "Extracting visual clues: architecture, signage, and vegetation"),
            "hunter": ("🎯 HUNTER_SWARM", "Autonomous ReAct Agent: Dynamic Lens visual search & Maps geolocation"),
            "skeptic": ("🛡️ SKEPTIC_AUDITOR", "Adversarial Red-Team: Debunking contradictions & verifying provenance"),
            "arbiter": ("⚖️ ARBITER_JUDGE", "Weighing dialectical evidence, computing audit score & resolving consensus"),
            "swarm_refinement_router": ("🔄 REFINE_ROUTER", "Resolving dialectical contention with a targeted search hop"),
            "case_synthesizer": ("📜 CASE_SYNTHESIZER", "Compiling certified OSINT dossier with adversarial red-team audit"),
        }

        with radar_col:
            for node_name, (title, desc) in node_descriptions.items():
                step_placeholders[node_name] = st.empty()
                step_placeholders[node_name].markdown(
                    f'<div class="radar-node-badge"><span>{title}</span><span style="color: #64748b;">STANDBY</span></div>',
                    unsafe_allow_html=True,
                )

        with terminal_col:
            terminal_placeholder = st.empty()

        # Run Live Streaming State Machine
        final_case_file: Optional[CaseFile] = None
        accumulated_state = None
        swarm_logs = []

        with st.spinner("Autonomous OSINT Swarm active across SerpApi engines..."):
            for event in stream_dialectical_investigation_sync(
                image_path=config["image_path"] or "target.jpg",
                image_url=config["image_url"],
                context_hint=config["context_hint"],
                max_budget=config["max_budget"],
                max_refinement_hops=config["max_hops"],
                api_key=config.get("api_key"),
                force_refresh=config.get("live_mode", False),
                gemini_api_key=config.get("gemini_api_key"),
                user_directive=config.get("user_directive"),
                selected_object_labels=config.get("selected_object_labels"),
            ):
                node_name = list(event.keys())[0]
                node_output = event[node_name]

                title, desc = node_descriptions.get(node_name, (node_name.upper(), "Processing..."))
                status_text = node_output.get("status", "complete")

                if node_name in step_placeholders:
                    step_placeholders[node_name].markdown(
                        f'<div class="radar-node-badge radar-node-active"><span>{title}</span><span style="color: #38bdf8; font-weight: 700;">● {status_text.upper()}</span></div>',
                        unsafe_allow_html=True,
                    )

                # Generate clean telemetry deduction for monospace radar terminal
                if node_name == "scene_deconstructor":
                    clues = node_output.get("visual_clues", [])
                    log_msg = f"Visual deconstruction completed. {len(clues)} forensic features cataloged."
                    swarm_logs.append(format_terminal_log_entry("SCENE", log_msg))
                elif node_name == "hunter":
                    hyps = node_output.get("hunter_hypotheses", [])
                    top_hyp = hyps[0] if hyps else "Investigating visual clues..."
                    matches = node_output.get("lens_matches", [])
                    cands = node_output.get("geo_candidates", [])
                    top_cand_name = cands[0].name if cands else "Target"
                    log_msg = f"Hypothesis generated: '{top_hyp[:55]}' | Resolved: {top_cand_name} ({len(matches)} matches)."
                    swarm_logs.append(format_terminal_log_entry("HUNTER", log_msg))
                elif node_name == "fashion_hunter":
                    dossier = node_output.get("itemized_dossier", [])
                    log_msg = f"Forensic decomposition: {len(dossier)} items isolated & searched via regional crops."
                    swarm_logs.append(format_terminal_log_entry("FASHION", log_msg))
                elif node_name == "skeptic":
                    critiques = node_output.get("skeptic_critiques", [])
                    top_critique = critiques[0] if critiques else "Audit completed."
                    anoms = node_output.get("anomalies", [])
                    log_msg = f"Red-team audit: '{top_critique[:60]}' ({len(anoms)} anomalies probed)."
                    swarm_logs.append(format_terminal_log_entry("SKEPTIC", log_msg))
                elif node_name == "arbiter":
                    score = node_output.get("audit_score", 0.9)
                    verdict = "VERIFIED CONSENSUS" if score >= 0.7 else "FRAUD / CONTRADICTION DETECTED"
                    log_msg = f"Dialectical synthesis: {verdict} (Audit Confidence: {int(score * 100)}%)."
                    swarm_logs.append(format_terminal_log_entry("ARBITER", log_msg))
                elif node_name == "swarm_refinement_router":
                    hops = node_output.get("refinement_hops", 1)
                    budget = node_output.get("budget_remaining", 0)
                    log_msg = f"Refinement hop #{hops} triggered (Budget remaining: {budget} queries)."
                    swarm_logs.append(format_terminal_log_entry("ROUTER", log_msg))
                elif node_name == "case_synthesizer":
                    cf = node_output.get("final_case_file")
                    conf = int(cf.confidence_score * 100) if cf else 95
                    anom_count = len(cf.anomalies) if cf else 0
                    audit_val = getattr(cf, "adversarial_audit_score", None) if cf else None
                    audit_label = f" | Audit Score: {int(audit_val * 100)}%" if audit_val is not None else ""
                    log_msg = f"Synthesizer certified case dossier with {conf}% confidence ({anom_count} anomalies flagged{audit_label})."
                    swarm_logs.append(format_terminal_log_entry("ARBITER", log_msg))
                elif node_name == "lens_hunter":
                    matches = node_output.get("lens_matches", [])
                    top_title = matches[0].get("title", "entity") if matches else "No match"
                    log_msg = f"SerpApi Google Lens reverse search -> {len(matches)} visual twins found. Top: '{top_title[:45]}'."
                    swarm_logs.append(format_terminal_log_entry("HUNTER", log_msg))
                elif node_name == "geo_triangulator":
                    candidates = node_output.get("geo_candidates", [])
                    top_cand = candidates[0] if candidates else None
                    if top_cand:
                        lat_val = getattr(top_cand, "latitude", 0.0)
                        lon_val = getattr(top_cand, "longitude", 0.0)
                        log_msg = f"SerpApi Google Maps resolved {top_cand.name} ({lat_val:.4f}°N, {lon_val:.4f}°E)."
                    else:
                        log_msg = "Google Maps spatial query completed with 0 high-confidence candidates."
                    swarm_logs.append(format_terminal_log_entry("GEO", log_msg))
                elif node_name == "chrono_auditor":
                    events = node_output.get("timeline_events", [])
                    log_msg = f"SerpApi Google News archival audit -> {len(events)} temporal milestones verified."
                    swarm_logs.append(format_terminal_log_entry("SKEPTIC", log_msg))
                else:
                    log_msg = f"Executed node transition: {node_name}."
                    swarm_logs.append(format_terminal_log_entry("SYS", log_msg))

                terminal_placeholder.markdown(
                    generate_swarm_terminal_html(swarm_logs, max_height_px=220),
                    unsafe_allow_html=True,
                )

                if "final_case_file" in node_output and node_output["final_case_file"]:
                    final_case_file = node_output["final_case_file"]
                accumulated_state = node_output

        st.session_state["case_file"] = final_case_file
        st.session_state["last_state"] = accumulated_state
        st.session_state["swarm_telemetry_logs"] = swarm_logs

    # Render High-Fidelity Tactical Command Deck if Case File exists
    case_file: Optional[CaseFile] = st.session_state.get("case_file")
    if case_file:
        st.markdown("---")
        render_tactical_command_deck(
            case_file=case_file,
            config=config,
            ground_truth_lat=config.get("truth_lat"),
            ground_truth_lon=config.get("truth_lon"),
        )


if __name__ == "__main__":
    main()
