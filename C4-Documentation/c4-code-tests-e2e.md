# C4 Code-Level Documentation: `tests/e2e`

## 1. Overview
- **Name:** TerraSleuth End-to-End Browser & Integration Test Suite
- **Description:** Headless browser automation and simulated Streamlit AppTest framework conducting full user journey audits, verifying interactive UI hydration, and capturing high-resolution forensic screenshots across all views.
- **Location:** [`tests/e2e`](file:///d:/SerpAPI_hackathon/tests/e2e)
- **Language:** Python 3.11+, Playwright Chromium
- **Purpose:** End-to-end integration verification ensuring the entire application flow—from target selection to swarm streaming, Leaflet/Folium map rendering, sub-tab navigation, and dossier export—functions without crashes or layout regressions.

---

## 2. Code Elements

### 2.1 `test_dashboard_e2e.py` (Streamlit AppTest Integration Suite)
In-memory Streamlit headless integration testing suite verifying complete reactive state transitions without launching a browser binary.

- **Fixtures:**
  - `prime_database()`: Automatically initializes SQLite database schema and pre-populates golden benchmark cases before test execution.
- **Tests:**
  - `test_app_loads_without_exceptions()`: Verifies that `frontend/app.py` compiles, hydrates session state, and mounts the Forensic Command Deck header without throwing exceptions.
  - `test_app_sidebar_configuration()`: Verifies radio selectors, pre-seeded case selectors, and parameter sliders in the sidebar.
  - `test_app_investigation_button_click()`: Simulates clicking the primary "⚡ Launch Autonomous Investigation" button, asserting that the investigation pipeline streams to completion and updates session state with a valid `CaseFile`.
  - `test_app_resolved_state_renders_command_deck()`: Verifies that after investigation completes, the 45/55 Split-Screen Command Deck, Folium map, and sub-tabs mount correctly.

### 2.2 `run_playwright_audit.py` (Playwright Real-Browser Audit Script)
Automates an actual Chromium browser session against a running Streamlit server at `http://localhost:8501`.

- **Configuration:**
  - Viewport: $1440 \times 900$ px at $1.5\times$ device scale factor.
  - Target Screenshot Directory: `tests/e2e/screenshots/`.
- **Workflow Steps & Captured Artifacts:**
  1. `01_initial_hero_command_deck.png`: Captures the initial landing view, mission briefing cards, and primary CTA button.
  2. `02_sidebar_target_selection.png`: Captures sidebar controls, scenario dropdown, and parameter sliders.
  3. `03_command_deck_overview_with_twin.png`: Triggers autonomous investigation, waits for swarm completion, and captures the 45/55 split-screen command deck with suspect image and side-by-side visual twin matcher.
  4. `04_deck_geoguessr_mode.png`: Navigates to Geoguessr mode sub-tab; captures 5,000-point accuracy meter and 4-phase tightening stages.
  5. `05_deck_chronology_provenance.png`: Navigates to Chronological Provenance sub-tab; captures timeline ledger.
  6. `06_deck_citation_chain.png`: Navigates to Citation Chain sub-tab; captures verified citation links.
  7. `07_deck_osint_dorks.png`: Navigates to OSINT Dorks sub-tab; captures municipal and archival query cards.
  8. `08_deck_executive_dossier.png`: Navigates to Executive Dossier sub-tab; captures investigative summary and Red-Team audit badge.
  9. `09_exported_html_dossier.png`: Verifies offline HTML dossier rendering.

---

## 3. Dependencies
- **Test Runners:** `pytest`, `playwright`
- **Internal:** `frontend.app`, `backend.app.services.cache_service`, `backend.app.db`
- **External:** `playwright.sync_api`, `streamlit.testing.v1.AppTest`, `pytest`, `os`, `time`
