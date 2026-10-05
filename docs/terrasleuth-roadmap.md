# TerraSleuth — Master Subagent Implementation & Review Roadmap

> **Status:** Release v0.3 Certified (`v0.3.0`) — All 3 Sprints 100% Completed  
> **Methodology:** Subagent-Driven Development (SDD) via `.agents/skills/hackathon-sdd-workflow/SKILL.md`  
> **Release Milestones:** `v0.1-dev` (Sprint 1: Certified `v0.1.0`) → `v0.2-dev` (Sprint 2: Certified `v0.2.0`) → `v0.3-dev` (Sprint 3: Certified `v0.3.0`) → `main`  
> **Single Source of Truth:** Tracks task blueprints, developer commits, adversarial code reviews, and verification gates.

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
- **Task 4.1:** Authentic High-Res OSINT Target Library & Pre-Seeded Scenarios (Real photographic assets, rental scam fraud scenario).
- **Task 4.2:** Split-Screen Command Deck & Tactical Dark Map (CartoDB Dark Matter, responsive flexbox telemetry badges, eliminating metric truncation).
- **Task 4.3:** Side-by-Side Visual Twin Comparator & Live Monospace Swarm Telemetry Terminal.
- **Task 4.4:** Full Regression Audit, Playwright Browser Re-Certification & Submission Packaging.

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
| **Task 4.1** | **Authentic High-Res OSINT Target Library**<br>• Real photography assets (Gateway, Neuschwanstein, Rental Scam)<br>• Golden cache seeding in SQLite | `architect` (Blueprint) | `code-reviewer` (Adversarial: PASS) | ✅ Completed | `fb61583` |
| **Task 4.2** | **Split-Screen Command Deck & Dark Map**<br>• 45/55 Command Deck (Visual Inspector + Tactical Map)<br>• CartoDB Dark Matter tiles & neon crosshair<br>• Zero-truncation flexbox telemetry cards | `architect` (Blueprint) | `code-reviewer` (Adversarial) | 🟡 Ready | Pending |
| **Task 4.3** | **Visual Twin Matcher & Cyber Telemetry Terminal**<br>• Side-by-side suspect image vs Google Lens match<br>• Live monospace terminal streaming agent logs | `architect` (Blueprint) | `code-reviewer` (Adversarial) | ⚪ Queued | Pending |
| **Task 4.4** | **Full Regression Audit & Release v0.4 Certification**<br>• Pytest 100% pass & Playwright re-certification<br>• Golden demo recording script update<br>• Tag `v0.4.0` | `architect` (Audit) | `code-reviewer` (Adversarial) | ⚪ Queued | Pending |


