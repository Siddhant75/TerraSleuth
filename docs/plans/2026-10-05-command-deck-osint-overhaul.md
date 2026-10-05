# Tactical OSINT Command Deck & Feature Pack Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Elevate TerraSleuth from a generic tabbed prototype to a tier-1, Palantir/Bellingcat-grade Tactical OSINT Command Deck featuring real photographic intelligence assets, CartoDB Dark Matter tactical mapping, side-by-side Visual Twin comparison via Google Lens, and live monospace cyber radar streaming.

**Architecture:** A unified 45/55 split-screen operational command deck replaces fragmented Streamlit tabs. The left deck houses the Visual Forensic Inspector (authentic photos, bounding box overlays) and a Side-by-Side Visual Twin Matcher (Input vs. SerpApi Google Lens Top Match). The right deck features a CartoDB Dark Matter Leaflet map with pulsing crosshair markers and an active Monospace Telemetry Terminal streaming real-time agent deductions and SerpApi engine queries.

**Tech Stack:** Python 3.11+, Streamlit, Folium / Leaflet (CartoDB Dark Matter), Pillow (PIL), LangGraph, SerpApi (Google Lens, Maps, News, Search), SQLite WAL cache, Playwright.

---

## 🧠 Part 1: Lessons Learned & Strategic Design Decisions

### 1.1 Critical Weaknesses Uncovered in Playwright Audit
1. **Synthetic Block Diagram Fallacy:** The pre-seeded test target used synthetic geometric block drawings (`target.jpg`), which immediately looked like an engineer's wireframe test fixture rather than an authentic surveillance or visual OSINT tool.
2. **Standard Metric Truncation:** Native Streamlit `st.metric` cards truncated coordinates on 5-column layouts (`Gatewa...`, `18.9220...`), hiding vital intelligence.
3. **Tab Disconnection:** Splitting the map, visual evidence, and timeline across separate tabs broke operational context—users could never view visual clues and spatial maps simultaneously.
4. **Daytime Map Disconnect:** Default OpenStreetMap daytime tiles clashed harshly with the dark forensic aesthetic.

### 1.2 Strategic Design Decisions
- **ADR-004: Tactical Command Deck Layout:** Replace the tabbed layout with an asynchronous split-screen deck:
  - **Left 45% Column:** Visual Forensic Inspector + Visual Twin Comparator + Extracted Clue Badges.
  - **Right 55% Column:** Tactical CartoDB Dark Matter Map + Live Monospace Swarm Telemetry Terminal + Evidentiary Citations.
- **ADR-005: Authentic Photographic Target Library:** Pre-seed high-resolution real photography for all Golden Mystery Targets in `frontend/assets/` and `cache_service.seed_golden_cases()`:
  - *Target A (Landmark):* Gateway of India waterfront basalt arch & Apollo Bunder promenade.
  - *Target B (Heritage):* Neuschwanstein Castle Bavarian alpine backdrop.
  - *Target C (Fraud Exposer):* Uncaptioned luxury rental listing interior unmasked by Google Lens as a boutique resort in Santorini, Greece.
- **ADR-006: Visual Twin Matcher Component:** Display the suspect input photo directly alongside the top authoritative Google Lens match thumbnail returned by SerpApi with calculated visual correspondence (`98% Match`).
- **ADR-007: CartoDB Dark Matter & Neon Crosshair:** Upgrade Folium maps to use high-contrast dark tiles with pulsing coordinate markers and radius consensus rings.

---

## ⚡ Part 2: SerpApi Engine Feature Matrix & Expansion

| Engine | Current Role | Expanded Command Deck Capability | Quota Boundary |
|---|---|---|---|
| **`google_lens`** | Visual provenance & KG title | **Visual Twin Matcher:** Side-by-side comparison of suspect image vs authoritative thumbnail. Extract visual correspondence score and domain provenance. | 1 call per run (100% pre-cached for Golden targets) |
| **`google_maps`** | WGS84 Lat/Lon & address | **Tactical Pinpointing:** CartoDB Dark Matter rendering, accuracy radius, and direct Google Maps satellite/street view link. | 1–2 calls per run (100% pre-cached) |
| **`google_news`** | Timeline verification | **Chrono Provenance Card:** Verified earliest publication milestone and viral circulation timeline. | 1 call per run (100% pre-cached) |
| **`google` (search)** | Organic search fallback | **Advanced OSINT Dorking:** Query formulations using `site:`, `filetype:pdf`, `before:`. | Optional hop (bounded by circuit breaker) |

---

## 📋 Part 3: Task Breakdown (Subagent-Driven Execution)

### Task 4.1: Authentic High-Res OSINT Target Library & Pre-Seeded Scenarios
- **Files to Modify:**
  - Create: `frontend/assets/gateway_mumbai.jpg`, `frontend/assets/rental_scam_santorini.jpg`, `frontend/assets/neuschwanstein.jpg`
  - Modify: `backend/app/services/cache_service.py` (update `seed_golden_cases()` with rich photo paths and rental scam scenario)
  - Modify: `backend/app/db.py` (ensure row schema and WAL mode persist rich golden targets)
- **Step 1: Write failing test** in `backend/tests/test_golden_scenarios.py` verifying real photographic files exist and load into SQLite with correct metadata.
- **Step 2: Run test to verify it fails.**
- **Step 3: Implement asset generation / download and cache seeding.**
- **Step 4: Run test to verify it passes.**
- **Step 5: Code Review Gate via `code-reviewer` subagent.**
- **Step 6: Commit:** `feat(assets): seed high-res photographic OSINT target library (Task 4.1)`

### Task 4.2: Split-Screen Command Deck & Tactical Dark Map (CartoDB Dark Matter)
- **Files to Modify:**
  - Modify: `frontend/components/geo_map.py` (switch to `cartodbdark_matter` tiles, glowing neon pin, and responsive metrics)
  - Modify: `frontend/app.py` (refactor from tabs into 45/55 split-screen Command Deck layout; eliminate metric truncation using custom CSS flexbox badges)
- **Step 1: Write UI component unit test** in `frontend/tests/test_command_deck_ui.py` asserting CartoDB tile generation and no truncated text.
- **Step 2: Run test to verify failure.**
- **Step 3: Implement split-screen layout and CartoDB map updates.**
- **Step 4: Run test to verify pass.**
- **Step 5: Code Review Gate via `code-reviewer` subagent.**
- **Step 6: Commit:** `feat(ui): implement split-screen OSINT command deck and CartoDB dark map (Task 4.2)`

### Task 4.3: Side-by-Side Visual Twin Comparator & Live Monospace Swarm Telemetry Terminal
- **Files to Modify:**
  - Create: `frontend/components/visual_twin_comparator.py` (Side-by-side suspect image vs SerpApi Google Lens top match)
  - Modify: `frontend/app.py` (integrate comparator into left deck; integrate live scrolling monospace cyber terminal into right deck)
- **Step 1: Write unit test** in `frontend/tests/test_visual_twin.py` checking image comparison layout and fallback.
- **Step 2: Run test to verify failure.**
- **Step 3: Implement comparator component and monospace terminal.**
- **Step 4: Run test to verify pass.**
- **Step 5: Code Review Gate via `code-reviewer` subagent.**
- **Step 6: Commit:** `feat(ui): add visual twin comparator and monospace cyber radar terminal (Task 4.3)`

### Task 4.4: Full Regression Audit, Playwright Browser Re-Certification & Submission Packaging
- **Files to Modify:**
  - Modify: `tests/e2e/run_playwright_audit.py` (update selectors for Command Deck layout and capture fresh screenshots)
  - Modify: `docs/terrasleuth-regression-audit.md` (audit all tests and browser captures)
  - Modify: `docs/terrasleuth-roadmap.md` (record commits and review verdicts)
  - Modify: `README.md` (update screenshot gallery and feature highlights)
- **Step 1: Run full automated pytest suite (`python -m pytest -v`).**
- **Step 2: Run Playwright browser audit (`python tests/e2e/run_playwright_audit.py`).**
- **Step 3: Verify all newly captured screenshots in `tests/e2e/screenshots/`.**
- **Step 4: Code Review Gate via `code-reviewer` subagent.**
- **Step 5: Merge `v0.4-dev` into `main`, tag `v0.4.0`.**
- **Step 6: Commit:** `chore(release): certify Release v0.4.0 Command Deck overhaul (Task 4.4)`
