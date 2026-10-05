# TerraSleuth — Agent Navigation Guide

> **Purpose:** This file tells any AI coding agent exactly where to look, what files govern which concerns, and how the project is structured. Read this **first** before touching any code.

---

## 🚀 Active Project Status: Release v0.3 (Interactive Visual OSINT Dashboard & Golden Demo)

- **Project Name:** **TerraSleuth** (Autonomous Multi-Modal Visual & Geospatial OSINT Detective)
- **Hackathon:** SerpApi India Hackathon 2026 (AI Agents Track)
- **Active Working Branch:** `v0.3-dev` *(Branched from `main` @ `v0.2.0`; NEVER commit unverified code directly to `main`!)*
- **Milestone Branching Hierarchy:**
  - `main` — Certified release branch (`v0.1.0` and `v0.2.0` certified).
  - `v0.1-dev` — **Sprint 1 (Complete):** Foundation, SQLite Disk Cache & SerpApi Visual/Spatial Service.
  - `v0.2-dev` — **Sprint 2 (Complete):** LangGraph Multi-Agent OSINT Engine (Scene Deconstructor, Lens Hunter, Geo Triangulator, Chrono Auditor, Case Synthesizer).
  - `v0.3-dev` — **Sprint 3 (Active):** Interactive Visual OSINT Dashboard (Bounding box visualizer, Leaflet Map Pinpoint, Evidence Chain & Golden Demo Walkthrough).
- **Commit Policy:** Strict commit per task on the active development branch using `<type>(<scope>): <description> (Task <X.Y>)`.
- **Active Single Source of Truth:**
  - **[docs/terrasleuth-roadmap.md](file:///d:/SerpAPI_hackathon/docs/terrasleuth-roadmap.md)** — Master subagent blueprint, task execution matrix, review verdicts, and commit log.
  - **[docs/terrasleuth-plan.md](file:///d:/SerpAPI_hackathon/docs/terrasleuth-plan.md)** — Core architecture, LangGraph OSINT state machine design, and SerpApi multi-engine research.
  - **[docs/terrasleuth-regression-audit.md](file:///d:/SerpAPI_hackathon/docs/terrasleuth-regression-audit.md)** — Subsystem health scorecard and multi-point regression verification report.

---

## 🗺️ Project Map

```
d:/SerpAPI_hackathon/
├── AGENTS.md                                   ← YOU ARE HERE (Master agent navigation guide)
├── README.md                                   ← Project overview, architecture, and quickstart
├── docs/                              
│   ├── terrasleuth-roadmap.md                 ← ACTIVE RELEASE ROADMAP & SUBAGENT EXECUTION MATRIX
│   ├── terrasleuth-plan.md                    ← Foundation system design & SerpApi multi-engine research
│   └── terrasleuth-regression-audit.md        ← Regression audit & subsystem health scorecard
│
├── backend/                                   ← Python backend & OSINT agent engine
│   ├── app/
│   │   ├── main.py                            ← FastAPI entry point & SSE streaming endpoints
│   │   ├── config.py                          ← Environment configuration & settings
│   │   ├── db.py                              ← SQLite persistence & search cache (terrasleuth.db)
│   │   ├── agent/                             ← LangGraph Multi-Agent OSINT Swarm
│   │   │   ├── state.py                       ← Typed OsintState schema (image, visual clues, candidates, coordinates)
│   │   │   ├── graph.py                       ← StateGraph construction & conditional routing
│   │   │   └── nodes/                         ← Modular investigative nodes
│   │   │       ├── scene_deconstructor.py     ← Multi-modal vision analysis (architecture, script, flora, crop extraction)
│   │   │       ├── lens_hunter.py             ← SerpApi Google Lens visual provenance & exact image match search
│   │   │       ├── geo_triangulator.py        ← SerpApi Google Maps & Local places triangulation (lat/lon resolution)
│   │   │       ├── chrono_auditor.py          ← SerpApi Google News & Search timeline verification
│   │   │       └── case_synthesizer.py        ← Lead detective hypothesis resolver & case file compiler
│   │   ├── services/
│   │   │   ├── serpapi_service.py             ← SerpApi wrapper (Google Lens, Maps/Local, News, Search)
│   │   │   ├── vision_service.py              ← Vision LLM wrapper for image deconstruction & crop bounding
│   │   │   └── cache_service.py               ← SQLite/file disk cache decorator (quota defense)
│   │   └── models/                            ← Pydantic schemas (CaseFile, VisualClue, GeoCandidate, Citation)
│   └── tests/
│       ├── test_serpapi.py                    ← SerpApi client & cache isolation tests
│       ├── test_vision.py                     ← Visual scene deconstructor parser tests
│       ├── test_graph.py                      ← LangGraph OSINT state transitions & tie-breaker tests
│       └── test_api.py                        ← REST / SSE streaming endpoint tests
│
├── frontend/                                  ← Modern Interactive Web Dashboard (Streamlit / Folium / Leaflet)
│   ├── app.py                                 ← Streamlit OSINT detective dashboard
│   ├── components/                            ← Visual UI components
│   │   ├── visual_evidence_board.py           ← Image with interactive bounding boxes & visual clues
│   │   ├── geo_map.py                         ← Interactive Leaflet/Folium map with coordinate pin & radius
│   │   ├── chronology_timeline.py             ← Image origin vs viral circulation timeline
│   │   └── citation_ledger.py                 ← Clickable citation links (Lens matches, Maps entries, News)
│   └── assets/                                ← Logos, sample case images, badges, and style sheets
│
└── tests/
    └── e2e/
        └── run_terrasleuth_e2e.py             ← Playwright UI walkthrough test suite
```

---

## 📖 Where to Look for What

| Task | Read First |
|---|---|
| **Active Tasks & Subagent Matrix** | `docs/terrasleuth-roadmap.md` |
| **Verify System Health & Regressions** | `docs/terrasleuth-regression-audit.md` |
| **Understand Architecture & OSINT Graph** | `docs/terrasleuth-plan.md` |
| **LangGraph OSINT State & Nodes** | `backend/app/agent/state.py` & `backend/app/agent/graph.py` |
| **SerpApi Lens & Maps Client & Cache** | `backend/app/services/serpapi_service.py` & `cache_service.py` |
| **Interactive Map & Visual Evidence Board** | `frontend/components/visual_evidence_board.py` & `geo_map.py` |
| **Run Backend Unit & Graph Tests** | `$env:PYTHONPATH="." ; pytest backend/tests/ -v` |

---

## 🔑 Key Architectural Rules (TerraSleuth)

1. **Subagent-Driven Development (SDD) Protocol:**
   - **Blueprint via `architect` subagent** before touching any code.
   - **Implement surgical changes** with developer execution.
   - **Run Adversarial Code Review loop** with `code-reviewer` subagent until explicit `PASS (APPROVED)`.
   - **Multi-Gate Verification:** Run unit tests, verify builds, and ensure zero regressions.
   - **Commit per task** with descriptive conventional commits and update the living roadmap.
2. **SerpApi Multi-Modal & Spatial Triangulation:**
   - Deeply utilize **Google Lens API** (full image and cropped visual bounding regions).
   - Resolve physical coordinates, place IDs, and street addresses with **Google Maps / Local API**.
   - Verify historical timestamps and context with **Google Search** and **Google News**.
3. **Mandatory Caching & Quota Defense:**
   - Wrap all SerpApi requests in an automatic SQLite/disk cache layer (`cache_service.py`).
   - Development, testing, and UI tuning MUST never burn live API credits for repeated queries.
4. **Deterministic Graph Boundaries:**
   - LangGraph state tracks `budget_remaining: int` and `refinement_hops: int`.
   - Ambiguity tie-breakers are capped (max 1–2 targeted refinement hops) with an immutable circuit breaker directing to `case_synthesizer`.
5. **Verifiable Visual & Spatial Provenance:**
   - Every claim in the case dossier must cite an exact Google Lens match URL, Google Maps place entry, or News report snippet. Zero hallucinations.
6. **Local Execution & Golden Demo Path:**
   - The project must run flawlessly locally.
   - The UI includes pre-cached "Golden Mystery Targets" (e.g., mysterious viral photo, uncaptioned global landmark, marketplace scam) for instant, lag-free video recording.
