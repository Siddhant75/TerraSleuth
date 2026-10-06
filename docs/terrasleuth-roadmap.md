# TerraSleuth — Master Subagent Implementation & Review Roadmap

> **Status:** Release v0.5 Certified (`v0.5.0`) — All Sprints (1 to 5) Complete; Ready for Submission  
> **Methodology:** Subagent-Driven Development (SDD) via `.agents/skills/hackathon-sdd-workflow/SKILL.md`  
> **Release Milestones:** `v0.1-dev` (Sprint 1: `v0.1.0`) → `v0.2-dev` (Sprint 2: `v0.2.0`) → `v0.3-dev` (Sprint 3: `v0.3.0`) → `v0.4-dev` (Sprint 4: `v0.4.0`) → `v0.5-dev` (Sprint 5: `v0.5.0`) → `main`  
> **Single Sources of Truth:**
> - [docs/hackathon-submission.md](file:///d:/SerpAPI_hackathon/docs/hackathon-submission.md) — Official hackathon submission document and judging writeup.
> - [docs/ui-ux-blueprint-and-feature-matrix.md](file:///d:/SerpAPI_hackathon/docs/ui-ux-blueprint-and-feature-matrix.md) — Screenshot audit critique, design ADRs, SerpApi engine comparison matrix.
> - [docs/interactive-redesign-blueprint.html](file:///d:/SerpAPI_hackathon/docs/interactive-redesign-blueprint.html) — Interactive HTML War Room prototype and feature matrix.
> - [docs/terrasleuth-regression-audit.md](file:///d:/SerpAPI_hackathon/docs/terrasleuth-regression-audit.md) — 84/84 test scorecard and verification invariants.
> - [docs/golden-demo-script.md](file:///d:/SerpAPI_hackathon/docs/golden-demo-script.md) — <3 min video recording walkthrough.

---

## 🎯 Sprint Breakdown & Scope

### Sprint 1: Foundation, Caching & SerpApi Visual/Spatial Service (`v0.1-dev`)
- **Task 1.1:** SerpApi multi-engine client (`serpapi_service.py`) supporting Google Lens, Google Maps/Local, Google News, and Google Search.
- **Task 1.2:** SQLite disk cache decorator (`cache_service.py`) with TTL and pre-seeded Golden Mystery targets.
- **Task 1.3:** Unit test suite verifying cache hit isolation and SerpApi mock execution across Lens and Maps.

### Sprint 2: LangGraph Multi-Agent OSINT Engine (`v0.2-dev`)
- **Task 2.1:** State schema (`state.py`) with typed `VisualClue`, `GeoCandidate`, and query budget counters.
- **Task 2.2:** Vision service (`vision_service.py`) and Scene Deconstructor node extracting architectural, signage, and flora clues.
- **Task 2.3:** Lens Hunter & Geo Triangulator nodes routing visual matches and spatial coordinate resolution.
- **Task 2.4:** Chrono Auditor & Lead Detective Synthesizer resolving candidate conflicts and compiling the final Case File.
- **Task 2.5:** Graph integration test suite (`test_graph.py`) testing full OSINT flow with mock search fixtures.

### Sprint 3: Interactive Visual OSINT Dashboard & Golden Walkthrough (`v0.3-dev`)
- **Task 3.1:** Streamlit UI with image upload, live agent step streaming, and Golden Mystery target toggle.
- **Task 3.2:** Interactive Leaflet/Folium map component with target pin, coordinate radius, and Visual Evidence Board with bounding clues.
- **Task 3.3:** Full regression audit scorecard (`terrasleuth-regression-audit.md`), demo walkthrough verification, and final submission packaging.

### Sprint 4: Tactical OSINT Command Deck & Feature Pack (`v0.4-dev`)
- **Task 4.1:** Authentic High-Res OSINT Target Library & Pre-Seeded Scenarios (Real photography assets, rental scam fraud scenario).
- **Task 4.2:** Split-Screen Command Deck & Tactical Dark Map (CartoDB Dark Matter / Esri World Imagery, responsive flexbox telemetry badges, eliminating metric truncation).
- **Task 4.3:** Side-by-Side Visual Twin Comparator & Live Monospace Swarm Telemetry Terminal.
- **Task 4.4:** Full Regression Audit, Playwright Browser Re-Certification & Release v0.4 Certification.

### Sprint 5: War Room 2.0 HUD, Advanced OSINT Features & Submission Packaging (`v0.5-dev`)
- **Task 5.1:** Anomaly & Fraud Engine (`backend/app/models/anomaly.py`, `backend/app/services/anomaly_service.py`) detecting rental scams and temporal disinformation.
- **Task 5.2:** Advanced OSINT Google Dorks (`backend/app/models/dork.py`, `backend/app/services/dork_service.py`) across municipal records, archives, and directories.
- **Task 5.3:** Standalone Self-Contained HTML Forensic Dossier Exporter (`frontend/components/dossier_exporter.py`) with Base64 embedded imagery and strict URL sanitization.
- **Task 5.4:** War Room 2.0 HUD Overhaul (`war_room_hud.py`, `app.py`), Docker suite (`Dockerfile`, `docker-compose.yml`), submission documentation (`docs/hackathon-submission.md`), and Release v0.5 Certification.

### Sprint 6: 1:1 Blueprint Alignment, Autonomous Geoguessr Mode & SDD Automation Hooks (`v0.6-dev`)
- **Task 6.1:** Master 4-Tab Blueprint Navigation & CommonMark Indentation Safety (`blueprint_views.py`, `app.py`).
- **Task 6.2:** Tactical Command Deck Refinement (`tactical_command_deck.py` with embedded Side-by-Side Visual Twin Matcher, `.neon-pulse` container, 5-badge telemetry bar).
- **Task 6.3:** Autonomous Geoguessr Mode (`backend/app/models/geoguessr.py`, `backend/app/services/geoguessr_service.py`, `frontend/components/geoguessr_view.py` with 5,000-point decay score and 4-phase spatial radius tightening).
- **Task 6.4:** Developer & SDD Hooks Setup (`.claude/hookify.quota-defense.local.md`, `.git/hooks/pre-commit`).
- **Task 6.5:** Full Regression Audit (91/91 tests), 9-Tab Playwright Browser Re-Certification & Release v0.6 Certification (`v0.6.0`).

---

## 📋 Task & Subagent Execution Matrix

| Task ID | Feature & Scope | Lead Architect Subagent | Lead Reviewer Subagent | Status | Commit Hash |
|---|---|---|---|---|---|
| **Task 1.1** | **SerpApi Visual & Spatial Client**<br>• Google Lens (reverse search & visual matches)<br>• Google Maps/Local (coordinates, place details)<br>• Google News & Search (timeline & context) | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `2a4db89` |
| **Task 1.2** | **SQLite Disk Cache & Quota Defense**<br>• Transparent `@cached_serp` decorator<br>• Pre-seeded Golden Mystery profiles (`terrasleuth.db`) | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `8532915` |
| **Task 1.3** | **Foundation Unit Tests**<br>• Mock SerpApi fixtures (Lens, Maps, News)<br>• Quota circuit breaker & cache contract tests | `architect` (Test Plan) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `4846c8b` |
| **Task 2.1** | **LangGraph OSINT State Schema**<br>• `OsintState`, `VisualClue`, `GeoCandidate`<br>• Budget decrementing counters | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `49e91f3` |
| **Task 2.2** | **Scene Deconstructor & Vision Service**<br>• Multi-modal clue extraction<br>• Architectural, signage, and flora parsing | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `bf886ac` |
| **Task 2.3** | **Lens Hunter & Geo Triangulator Nodes**<br>• Reverse-image provenance matching<br>• Spatial coordinate triangulation | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `90e606c` |
| **Task 2.4** | **Chrono Auditor & Case Synthesizer**<br>• Timeline conflict resolution (max 2 hops)<br>• Case File dossier compilation | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `fdac237` |
| **Task 2.5** | **Graph Integration Tests**<br>• Full dialectical OSINT execution<br>• Multi-candidate tie-breaking tests | `architect` (Test Plan) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `927f356` |
| **Task 3.1** | **Interactive Streamlit Dashboard**<br>• Image upload & live node streaming<br>• Live vs. Golden Mystery mode toggle | `architect` (UI Plan) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `e7ef44a` |
| **Task 3.2** | **Visual Evidence Board & Leaflet Map**<br>• Bounding-box clue overlays<br>• Interactive Leaflet map coordinate pinning | `architect` (UI Plan) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `e7ef44a` |
| **Task 3.3** | **Regression Audit & Demo Video Walkthrough**<br>• 100% health scorecard verification<br>• <3 min screen recording walkthrough | `architect` (Audit) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `c20eea4` |
| **Post-v0.3** | **Browser E2E Automation & Visual Audit**<br>• Playwright multi-tab browser automation<br>• High-contrast dark theme verification<br>• Timeline HTML rendering patch (0 live credits burned) | `developer` | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `f01ee91` |
| **Design** | **UI/UX Redesign Blueprint & Feature Matrix**<br>• Screenshot audit & critique<br>• SerpApi multi-engine matrix & OSINT use cases<br>• Interactive HTML prototype (`docs/interactive-redesign-blueprint.html`) | `planner` / `architect` | Parent Agent Verification | ✅ Completed | `docs/` |
| **Task 4.1** | **Authentic High-Res OSINT Target Library**<br>• Real photography assets (Gateway, Neuschwanstein, Rental Scam)<br>• Golden cache seeding in SQLite | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `fb61583` |
| **Task 4.2** | **Split-Screen Command Deck & Dark Map**<br>• 45/55 Command Deck (Visual Inspector + Tactical Map)<br>• Esri Satellite tiles & neon crosshair<br>• Zero-truncation flexbox telemetry cards | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `06195b1` |
| **Task 4.3** | **Visual Twin Matcher & Cyber Telemetry Terminal**<br>• Side-by-Side suspect image vs Google Lens match<br>• Live monospace terminal streaming agent logs | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `24c59a5` |
| **Task 4.4** | **Full Regression Audit & Release v0.4 Certification**<br>• Pytest 100% pass (77/77) & Playwright re-certification<br>• Golden demo recording script update<br>• Tag `v0.4.0` | `architect` (Audit) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `0b481a6` |
| **Task 5.1** | **Anomaly & Fraud Detection Engine**<br>• Pydantic AnomalyReport schema<br>• Rental scam unmasking & recycled media detector | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `v0.5-dev` |
| **Task 5.2** | **Advanced OSINT Google Dorking Assistant**<br>• Targeted Google search queries<br>• Municipal permits, news archives, open directories | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `v0.5-dev` |
| **Task 5.3** | **Standalone HTML Forensic Dossier Exporter**<br>• Self-contained offline report with base64 imagery<br>• Strict URL sanitization neutralizing javascript: XSS | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `v0.5-dev` |
| **Task 5.4** | **War Room 2.0 HUD & Release v0.5 Certification**<br>• 1:1 War Room HUD alignment, Docker containerization<br>• 84/84 tests (100% pass) & 9 verified Playwright screenshots | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `v0.5.0` |
| **Task 6.1** | **Master 4-Tab Blueprint Navigation**<br>• Screenshot audit critique, SerpApi engine matrix<br>• CommonMark code block indentation safety | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `223a74e` |
| **Task 6.2** | **Tactical Command Deck Refinement**<br>• Embedded Side-by-Side Visual Twin Matcher<br>• `.neon-pulse` container & 5-badge telemetry bar | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `223a74e` |
| **Task 6.3** | **Autonomous Geoguessr Mode**<br>• 5,000-point exponential decay scoring curve<br>• 4-stage progressive spatial radius tightening | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `223a74e` |
| **Task 6.4** | **Developer & SDD Hooks Setup**<br>• `.claude/hookify.quota-defense.local.md` guardrail<br>• `.git/hooks/pre-commit` test automation gate | `developer` | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `223a74e` |
| **Task 6.5** | **Regression Audit & Release v0.6 Certification**<br>• 91/91 tests (100% pass) & 9 verified Playwright screenshots<br>• Release `v0.6.0` certification | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `v0.6.0` |

