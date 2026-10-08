# C4 Code-Level Documentation: `frontend/tests`

## 1. Overview
- **Name:** TerraSleuth Frontend UI Component Verification Suite
- **Description:** Unit test suite covering frontend visualization components, Folium map rendering, HTML dossier generation, Geoguessr views, visual twin comparisons, and XSS sanitization boundaries.
- **Location:** [`frontend/tests`](file:///d:/SerpAPI_hackathon/frontend/tests)
- **Language:** Python 3.11+
- **Purpose:** Verifies that UI layout engines, HTML generators, and Folium maps assemble correctly without runtime exceptions, data truncation, or XSS vulnerabilities.

---

## 2. Code Elements & Test Suites

### 2.1 `test_command_deck_ui.py`
- Tests `create_folium_map` generation with `CartoDB dark_matter` and `Esri World Imagery` tile configurations.
- Tests `render_telemetry_bar_html` flexbox rendering, asserting that entity names and high-precision WGS84 coordinates render fully without truncation ellipses.
- Validates proper handling when `GeoCandidate` is `None`.

### 2.2 `test_dossier_exporter.py`
- Tests `sanitize_url` against javascript injection vectors, asserting that `javascript:...` URLs are stripped to `#`.
- Tests `image_to_base64_data_uri` with PIL images and null inputs.
- Tests `generate_standalone_html_dossier` output, verifying inclusion of CSS styling tokens, embedded Base64 image strings, anomalies, citations, and print styles.

### 2.3 `test_geoguessr_and_blueprint_ui.py`
- Tests `render_geoguessr_challenge_view` rendering logic with simulated 5,000-point perfect pinpoint scores and multi-kilometer misses.
- Tests `render_screenshot_critique_view`, `render_serpapi_features_view`, and `render_implementation_roadmap_view` to ensure CommonMark formatting integrity.

### 2.4 `test_swarm_ui.py`
- Tests `generate_swarm_terminal_html` with Level 5 dialectical swarm messages (`[HUNTER]`, `[SKEPTIC]`, `[ARBITER]`).
- Asserts that special characters in terminal logs are strictly escaped via `html.escape`.

### 2.5 `test_ui_components.py`
- Tests `draw_bounding_boxes` PIL rectangle drawing routines and coordinate transformations.
- Tests `render_chronology_timeline` and `render_citation_ledger` with empty and populated datasets.

### 2.6 `test_visual_twin.py`
- Tests `calculate_correspondence_score` decay bounds within $[0.50, 0.995]$.
- Tests `extract_visual_twin_metadata` defensive extraction with missing fields and null URLs.
- Tests `format_terminal_log_entry` dictionary structure.

---

## 3. Dependencies
- **Test Runner:** `pytest`
- **Internal:** `frontend.components.*`, `backend.app.models.*`
- **External:** `pytest`, `unittest.mock`, `PIL`, `folium`, `html`
