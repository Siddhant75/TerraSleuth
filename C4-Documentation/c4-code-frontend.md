# C4 Code-Level Documentation: `frontend`

## 1. Overview
- **Name:** TerraSleuth Web Application & Forensic Command Deck Entry Point
- **Description:** Interactive Streamlit web application providing pure product immersion, target image selection, swarm parameter controls, synchronous investigation streaming, and tactical command deck presentation.
- **Location:** [`frontend`](file:///d:/SerpAPI_hackathon/frontend)
- **Language:** Python 3.11+, Streamlit
- **Purpose:** Primary user interface for OSINT investigators and hackathon evaluators to conduct autonomous investigations, view real-time agent reasoning, inspect spatial consensus, and export forensic dossiers.

---

## 2. Code Elements

### 2.1 `app.py` (Streamlit Application Entry Point)
Coordinates session lifecycle, layout styling, input acquisition, background graph streaming, and view transitions.

- **Initialization:**
  - `init_db()`: Initializes SQLite database tables on boot.
  - `CacheService().seed_golden_cases()`: Seeds benchmark golden cases and SerpApi responses.
  - `st.set_page_config`: Configures wide layout, page title (`TerraSleuth // OSINT Forensic Command Deck`), and favicon (`🕵️`).
  - Custom CSS injection: Themes interface with high-contrast tactical cyber palette (`#07090e` background, `#0d121d` sidebar, cyan `#00f2fe` neon pulse animation, monospace typography).

- **Functions:**
  - **`render_sidebar() -> Dict[str, Any]`**:
    Renders left operational sidebar containing:
    1. Header badge (`🕵️ TERRASLEUTH // OSINT DETECTIVE SWARM`).
    2. Target input mode selector:
       - Mode A: Pre-seeded Golden Mystery Targets (Instant / Pre-Cached).
       - Mode B: File upload (`.jpg`, `.jpeg`, `.png`) with session-tracked temporary file lifecycle management.
       - Mode C: Remote direct image URL.
    3. Image preview widget.
    4. Swarm parameters:
       - Query budget slider (1–12 queries).
       - Refinement hops slider (1–3 hops).
       - Claimed context hint / metadata text input.
    Returns runtime configuration dictionary.

  - **`main() -> None`**:
    Main control flow and state machine:
    1. Evaluates session state (`case_file`, `last_state`, `swarm_telemetry_logs`).
    2. **State 1 (Idle / Unsolved):**
       - Renders Forensic Command Deck header banner (`render_war_room_header`).
       - Renders mission briefing cards (`render_mission_briefing`).
       - Displays prominent primary CTA button ("⚡ Launch Autonomous Investigation") on main canvas.
    3. **State 2 (Streaming / Live Execution):**
       - Dynamically selects graph runner: Level 5 dialectical swarm (`stream_dialectical_investigation_sync`) when available, fallback to Level 3 (`stream_osint_investigation_sync`).
       - Updates live visual status indicator for active agent nodes (Scene Deconstructor, Lens Hunter, Geo Triangulator, Chrono Auditor, Case Synthesizer).
       - Appends real-time timestamped entries (`[HUNTER]`, `[SKEPTIC]`, `[ARBITER]`, `[DECISION]`, `[ACTION]`) into `st.session_state["swarm_telemetry_logs"]`.
    4. **State 3 (Resolved / Command Deck Active):**
       - Invokes `render_tactical_command_deck` with compiled `CaseFile`.
       - Renders 45/55 split-screen layout with visual evidence, satellite map, Geoguessr score, provenance timeline, and 1-click HTML export.

---

## 3. Dependencies
- **Internal:**
  - `backend.app.agent.graph` (`stream_dialectical_investigation_sync`, `stream_osint_investigation_sync`)
  - `backend.app.db` (`init_db`, `get_golden_cases`)
  - `backend.app.models.case.CaseFile`
  - `backend.app.services.cache_service.CacheService`
  - `frontend.components.tactical_command_deck.render_tactical_command_deck`
  - `frontend.components.war_room_hud` (`render_war_room_header`, `render_mission_briefing`)
  - `frontend.components.swarm_telemetry_terminal` (`format_terminal_log_entry`, `generate_swarm_terminal_html`)
- **External:**
  - `streamlit`
  - `PIL.Image`
  - `os`, `sys`, `json`, `logging`, `tempfile`
