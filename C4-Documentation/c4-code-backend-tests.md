# C4 Code-Level Documentation: `backend/tests`

## 1. Overview
- **Name:** TerraSleuth Backend Automated Verification & Unit Test Suite
- **Description:** 16 comprehensive test modules verifying SerpApi client mechanics, SQLite disk caching, state machine transitions, vision deconstruction, quota budget enforcement, Level 4 ReAct tool execution, Level 5 Hunter/Skeptic debate loops, and anomaly detection.
- **Location:** [`backend/tests`](file:///d:/SerpAPI_hackathon/backend/tests)
- **Language:** Python 3.11+
- **Purpose:** Regression prevention and multi-gate verification ensuring 100% deterministic test execution, 0 live SerpApi credits burned during CI/CD, and robust schema compliance.

---

## 2. Code Elements & Test Suites

### 2.1 `test_serpapi.py` (SerpApi Client Unit Tests)
- Tests `SerpApiService` parameter formulation, error handling, and response parsing.
- Verifies `search_lens`, `search_maps`, `search_news`, and `search_google` with mocked HTTP responses (`httpx.Response`).
- Asserts that API keys are strictly sanitized and never leaked in log messages or exceptions (`_sanitize_message`).

### 2.2 `test_cache.py` (SQLite Disk Cache Tests)
- Tests deterministic SHA-256 hash generation (`generate_cache_key`), ensuring sensitive keys (`api_key`) and ephemeral flags (`force_refresh`) are excluded.
- Verifies TTL expiration logic, custom SQLite table creation, and cache statistics computation.

### 2.3 `test_quota.py` (Quota Budget Enforcement Tests)
- Tests `QuotaBudgetManager` credit tracking, consumption limits, and `QuotaExhaustedError` triggering.
- Validates the fundamental architectural invariant: cache hits NEVER decrement search quota; only live HTTP requests consume credits.

### 2.4 `test_vision.py` (Vision Deconstructor & Cropping Tests)
- Tests `crop_image_region` bounding box clamping, PIL pixel translation, and file generation.
- Tests `VisionService.deconstruct_scene` output parsing into typed `VisualClue` objects with normalized coordinates and valid `ClueCategory` enums.

### 2.5 `test_state.py` (TypedDict Schema & State Immutability Tests)
- Validates `OsintGraphState` TypedDict initialization, default values, and accumulation reducers.
- Tests state persistence and propagation across sequential pipeline stages.

### 2.6 `test_graph.py` (LangGraph Level 3 Workflow Tests)
- Tests the original 5-node LangGraph OSINT pipeline (`scene_deconstructor` -> `lens_hunter` -> `geo_triangulator` -> `chrono_auditor` -> `case_synthesizer`).
- Verifies conditional edge routing (`should_refine_search`) and budget termination circuit breakers.

### 2.7 `test_lens_geo_nodes.py` (Lens & Maps Node Tests)
- Isolated unit tests for `lens_hunter_node` and `geo_triangulator_node`.
- Validates spatial coordinate extraction and candidate scoring from SerpApi payloads.

### 2.8 `test_chrono_synthesizer_nodes.py` (Chrono Auditor & Synthesizer Tests)
- Tests `chrono_auditor_node` timeline extraction and earliest publication identification.
- Tests `case_synthesizer_node` compilation of `CaseFile`, executive summary generation, and citation formatting.

### 2.9 `test_golden_scenarios.py` (Offline Golden Demo Replay Tests)
- Verifies that all 3 golden targets (Gateway of India, Neuschwanstein Castle, Santorini Rental Scam) execute completely offline with 0 live API credit burn.
- Verifies presence of photographic assets in `frontend/assets/targets/`.

### 2.10 `test_anomaly_service.py` (Fraud & Disinformation Detection Tests)
- Tests `AnomalyService.detect_anomalies` against:
  1. Vacation rental scam photos unmasked as stolen hotel assets.
  2. Recirculated media claims with conflicting historical publication dates.
  3. Clean landmark photos producing zero false positives.

### 2.11 `test_dork_service.py` (Google OSINT Dork Tests)
- Tests `DorkService.generate_dorks` query formulation, URL encoding, and categorization across municipal, press, government, and directory searches.

### 2.12 `test_geoguessr_service.py` (Geoguessr Scoring & Spatial Tightening Tests)
- Tests Haversine geodesic distance calculations against known global coordinates.
- Validates 5,000-point exponential decay scoring curve and 4-phase progressive radius narrowing.

### 2.13 `test_tools.py` (Level 4 LangChain Tool Registry Tests)
- Verifies `@tool` definitions (`tool_lens_search`, `tool_maps_triangulate`, `tool_news_audit`, `tool_google_dork`, `tool_crop_region`).
- Asserts that tools route through `CacheService` to prevent credit consumption.

### 2.14 `test_react_supervisor.py` (Level 4 ReAct Supervisor Tests)
- Tests `AgentThought` creation, `ReActStepType` enum enforcement, and monospace terminal string formatting (`to_terminal_str`).

### 2.15 `test_swarm_debate.py` (Level 5 Dialectical Swarm Nodes Tests)
- Tests `hunter_node` hypothesis formulation and mapping into typed `GeoCandidate` models.
- Tests `skeptic_node` adversarial red-teaming, anomaly detection, and critique generation.
- Tests `arbiter_node` scoring synthesis and adversarial audit score computation.

### 2.16 `test_dialectical_graph.py` (Level 5 Graph Orchestration Tests)
- Tests `create_dialectical_osint_graph` graph compilation, state transitions, debate refinement loops, and circuit breakers.
- Tests synchronous streaming via `stream_dialectical_investigation_sync`.

---

## 3. Dependencies
- **Test Runner:** `pytest`
- **Internal:** All modules in `backend.app.services`, `backend.app.agent`, `backend.app.models`, and `backend.app.db`.
- **External:** `pytest`, `httpx`, `unittest.mock`, `tempfile`, `PIL`
