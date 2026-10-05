# VCSentry — Master Subagent Implementation & Review Roadmap

> **Status:** Active Working Branch: `v0.1-dev` (Release v0.1: Foundation, Caching & Multi-Engine Setup)  
> **Methodology:** Subagent-Driven Development (SDD) via `.agents/skills/hackathon-sdd-workflow/SKILL.md`  
> **Release Milestones:** `v0.1-dev` (Sprint 1) → `v0.2-dev` (Sprint 2) → `v0.3-dev` (Sprint 3) → `main`  
> **Single Source of Truth:** Tracks task blueprints, developer commits, adversarial code reviews, and verification gates.

---

## 🎯 Sprint Breakdown & Scope

### Sprint 1: Foundation, Caching & SerpApi Multi-Engine Service
- **Task 1.1:** SerpApi multi-engine client (`serpapi_service.py`) supporting Google Search, News, Scholar, and Patents.
- **Task 1.2:** SQLite/disk cache decorator (`cache_service.py`) with TTL and pre-seeded Golden Demo profiles.
- **Task 1.3:** Unit test suite verifying cache hit isolation and SerpApi mock execution.

### Sprint 2: LangGraph State Machine & Dialectical Red-Teaming
- **Task 2.1:** State schema (`state.py`) with typed inputs, hypotheses, evidence items, and query budget counters.
- **Task 2.2:** Graph construction (`graph.py`) with Intake, Planner, Search Router, Evidence Extractor, and Red-Team nodes.
- **Task 2.3:** Adversarial Red-Team Auditor with bounded verification loop (max 2 hops) and immutable circuit breaker.
- **Task 2.4:** Dossier Compiler generating structured IC Memo, Risk Radar metrics, Timeline, and Citation Ledger.

### Sprint 3: Interactive Streamlit Dashboard & E2E Walkthrough
- **Task 3.1:** Streamlit UI with live agent step streaming, inputs, and toggle for Golden Demo targets.
- **Task 3.2:** Visual Risk Radar Matrix, interactive Milestone Timeline, and Clickable Citation cards.
- **Task 3.3:** Comprehensive test verification, health audit (`vcsentry-regression-audit.md`), and demo video script.

---

## 📋 Task & Subagent Execution Matrix

| Task ID | Feature & Scope | Lead Architect Subagent | Lead Reviewer Subagent | Status | Commit Hash |
|---|---|---|---|---|---|
| **Task 1.1** | **SerpApi Multi-Engine Service**<br>• Wrapper for Search, News, Scholar, Patents<br>• Structured response normalization | `architect` (Blueprint) | `code-reviewer` (Adversarial) | ⏳ Ready to Start | — |
| **Task 1.2** | **SQLite Disk Cache & Quota Defense**<br>• Transparent `@cached_serp` decorator<br>• Golden Demo target profiles | `architect` (Blueprint) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
| **Task 1.3** | **Foundation Unit Tests**<br>• Mock SerpApi fixtures & cache hit validation<br>• Quota circuit breaker contract tests | `architect` (Test Plan) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
| **Task 2.1** | **LangGraph State & Node Contracts**<br>• `DueDiligenceState` TypedDict & Pydantic models<br>• Budget decrementing counters | `architect` (Blueprint) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
| **Task 2.2** | **Multi-Node StateGraph Execution**<br>• Intake, Planner, Searcher, Extractor<br>• Event streaming hooks | `architect` (Blueprint) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
| **Task 2.3** | **Adversarial Red-Team Auditor**<br>• Contradiction & controversy detector<br>• Bounded verification loop (max 2 hops) | `architect` (Blueprint) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
| **Task 2.4** | **Forensic Dossier Compiler**<br>• Risk Radar scoring algorithm (1-100)<br>• Milestone Timeline & Citation Ledger | `architect` (Blueprint) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
| **Task 3.1** | **Interactive Streamlit Dashboard**<br>• Real-time graph node streaming<br>• Live vs. Golden Demo mode toggle | `architect` (UI Plan) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
| **Task 3.2** | **Visual Dossier Components**<br>• Radar chart, timeline cards, citations<br>• PDF/Markdown export | `architect` (UI Plan) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
| **Task 3.3** | **Regression Audit & Demo Video**<br>• 100% health scorecard verification<br>• <3 min screen recording walkthrough | `architect` (Audit) | `code-reviewer` (Adversarial) | ⏳ Pending | — |
