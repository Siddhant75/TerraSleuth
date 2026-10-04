# VCSentry — Agent Navigation Guide

> **Purpose:** This file tells any AI coding agent exactly where to look, what files govern which concerns, and how the project is structured. Read this **first** before touching any code.

---

## 🚀 Active Project Status: Foundation & Architecture (Sprint 1)

- **Project Name:** **VCSentry** (Autonomous Startup & Founder Due Diligence Agent)
- **Hackathon:** SerpApi India Hackathon 2026 (AI Agents Track)
- **Active Working Branch:** `main` (feature work moves to task branches / `v1.0-dev`)
- **Active Single Source of Truth:**
  - **[docs/vcsentry-roadmap.md](file:///d:/SerpAPI_hackathon/docs/vcsentry-roadmap.md)** — Master subagent blueprint, task execution matrix, review verdicts, and commit log.
  - **[docs/vcsentry-plan.md](file:///d:/SerpAPI_hackathon/docs/vcsentry-plan.md)** — Core architecture, LangGraph state machine design, and SerpApi multi-engine research.
  - **[docs/vcsentry-regression-audit.md](file:///d:/SerpAPI_hackathon/docs/vcsentry-regression-audit.md)** — Subsystem health scorecard and multi-point regression verification report.

---

## 🗺️ Project Map

```
d:/SerpAPI_hackathon/
├── AGENTS.md                                   ← YOU ARE HERE (Master agent navigation guide)
├── docs/                              
│   ├── vcsentry-roadmap.md                    ← ACTIVE RELEASE ROADMAP & SUBAGENT EXECUTION MATRIX
│   ├── vcsentry-plan.md                       ← Foundation system design & SerpApi multi-engine research
│   └── vcsentry-regression-audit.md           ← Regression audit & subsystem health scorecard
│
├── backend/                                   ← Python backend & agent engine
│   ├── app/
│   │   ├── main.py                            ← FastAPI entry point & SSE streaming endpoints
│   │   ├── config.py                          ← Environment configuration & settings
│   │   ├── db.py                              ← SQLite persistence & search cache (vcsentry.db)
│   │   ├── agent/                             ← LangGraph Multi-Agent Engine
│   │   │   ├── state.py                       ← Typed DueDiligenceState schema
│   │   │   ├── graph.py                       ← StateGraph construction & conditional edge routing
│   │   │   └── nodes/                         ← Modular graph execution nodes
│   │   │       ├── intake.py                  ← Input parsing & domain resolution
│   │   │       ├── planner.py                 ← Hypothesis formulation & engine search routing
│   │   │       ├── searcher.py                ← SerpApi multi-engine execution with cache
│   │   │       ├── red_team.py                ← Adversarial skeptic & contradiction auditor
│   │   │       └── synthesizer.py             ← Investment memo, risk radar & timeline compiler
│   │   ├── services/
│   │   │   ├── serpapi_service.py             ← SerpApi client wrapper (Search, News, Scholar, Patents)
│   │   │   └── cache_service.py               ← SQLite/file disk cache decorator (quota defense)
│   │   └── models/                            ← Pydantic / SQLModel schemas (Dossier, Citation, RiskRadar)
│   └── tests/
│       ├── test_serpapi.py                    ← SerpApi client & cache isolation tests
│       ├── test_graph.py                      ← LangGraph state transitions & circuit breaker tests
│       └── test_api.py                        ← REST / SSE streaming endpoint tests
│
├── frontend/                                  ← Modern Web Dashboard (Streamlit / Vite+React)
│   ├── app.py                                 ← Streamlit interactive due diligence dashboard
│   ├── components/                            ← Visual UI components
│   │   ├── risk_radar.py                      ← 4-pillar interactive Risk Radar matrix
│   │   ├── timeline.py                        ← Chronological company & founder milestone timeline
│   │   ├── citation_ledger.py                 ← Clickable citation provenance links
│   │   └── memo_view.py                       ← Formatted Institutional Investment Memo view
│   └── assets/                                ← Logos, badges, and style sheets
│
└── tests/
    └── e2e/
        └── run_vcsentry_e2e.py                ← Playwright / Cypress UI walkthrough test suite
```

---

## 📖 Where to Look for What

| Task | Read First |
|---|---|
| **Active Tasks & Subagent Matrix** | `docs/vcsentry-roadmap.md` |
| **Verify System Health & Regressions** | `docs/vcsentry-regression-audit.md` |
| **Understand Architecture & Graph Design** | `docs/vcsentry-plan.md` |
| **LangGraph State Schema & Graph Nodes** | `backend/app/agent/state.py` & `backend/app/agent/graph.py` |
| **SerpApi Multi-Engine Client & Cache** | `backend/app/services/serpapi_service.py` & `cache_service.py` |
| **Interactive Risk Radar & Citations** | `frontend/components/risk_radar.py` & `citation_ledger.py` |
| **Run Backend Unit & Graph Tests** | `$env:PYTHONPATH="." ; pytest backend/tests/ -v` |

---

## 🔑 Key Architectural Rules (VCSentry — Learned from FluentVoice)

1. **Subagent-Driven Development (SDD) Protocol:**
   - **Blueprint via `architect` subagent** before touching any code.
   - **Implement surgical changes** with developer execution.
   - **Run Adversarial Code Review loop** with `code-reviewer` subagent until explicit `PASS (APPROVED)`.
   - **Multi-Gate Verification:** Run unit tests, verify builds, and ensure zero regressions.
   - **Commit per task** with descriptive conventional commits and update the living roadmap.
2. **SerpApi Multi-Engine Triangulation:**
   - Never treat SerpApi as a single generic endpoint.
   - Route targeted queries across **Google Search** (claims, traction), **Google News** (chronological PR vs controversies), **Google Scholar** (founder papers, citations), and **Google Patents** (deep-tech defensibility).
3. **Mandatory Caching & Quota Defense:**
   - Wrap all SerpApi requests in an automatic SQLite/disk cache layer (`cache_service.py`).
   - Development, testing, and UI tuning MUST never burn live API credits for repeated queries.
4. **Deterministic Graph Boundaries:**
   - LangGraph state tracks `budget_remaining: int` and `loop_count: int`.
   - Adversarial red-team verification loops are capped (max 1–2 targeted refinement hops) with an immutable circuit breaker directing straight to `synthesizer`.
5. **Verifiable Citation Provenance:**
   - Every claim in the investment memo must reference a structured citation with exact URL, snippet, and engine source. Zero hallucinated metrics.
6. **Local Execution & Golden Demo Path:**
   - The project must run flawlessly locally.
   - The UI includes pre-cached "Golden Demo Targets" (e.g., Perplexity AI, Zepto) for instant, lag-free video recording.
