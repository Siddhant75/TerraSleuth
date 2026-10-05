---
name: hackathon-sdd-workflow
description: Subagent-Driven Development (SDD) engineering and review protocol derived from high-stakes hackathon playbooks (FluentVoice/AssemblyAI). Enforces architect blueprinting, adversarial code reviews, multi-gate verification, and living roadmap maintenance.
---

# Hackathon Subagent-Driven Development (SDD) Playbook

> **Origin:** Proven methodology from **FluentVoice** (AssemblyAI Hackathon release cycles v2.0 - v2.3), now standard operating procedure for **VCSentry** and competitive hackathon projects.

---

## 🏛️ The Core Philosophy

Hackathons are won not by rushing messy prototypes, but by executing **surgical, production-grade iterations** where every single feature is architected, implemented, reviewed, tested, and documented with institutional rigor.

This playbook eliminates:
- Hallucinated or half-implemented features
- Regressions that break earlier working demos
- Quota exhaustion during development
- Unreviewed code vulnerabilities
- Fragmented project state

---

## 🔄 The 5-Stage SDD Execution Cycle

For **every single task or feature**, follow this strict five-stage pipeline:

```
┌────────────────────────┐
│ Stage 1: Blueprint     │  Architect subagent creates complete technical design
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Stage 2: Implement     │  Developer executes surgical code changes & tests
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Stage 3: Review Gate   │  Adversarial code-reviewer subagent reviews diffs
└───────────┬────────────┘  (Iterate until PASS / APPROVED)
            │
            ▼
┌────────────────────────┐
│ Stage 4: Multi-Gate    │  Unit tests + Build + E2E walkthrough validation
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Stage 5: Log & Commit  │  Conventional commit + Roadmap living doc update
└────────────────────────┘
```

---

### Stage 1: Architect Blueprint (`architect` subagent)
Before writing any code or modifying existing files:
1. Dispatch an `architect` subagent with the exact task scope, constraints, and dependencies.
2. The architect outputs:
   - File-by-file delta blueprint.
   - Pydantic/TypedDict schemas, API payloads, or graph node contracts.
   - Quota and performance boundaries (e.g. max SerpApi queries, cache hit expectations).
   - Test specifications (unit tests + UI acceptance criteria).

### Stage 2: Developer Implementation
1. Implement the exact specifications authored by the architect.
2. Maintain clean separation of concerns:
   - Data / Client wrappers in `services/`.
   - Graph state and nodes in `agent/`.
   - Visual components in `components/`.
3. Write unit tests concurrently with the code in `tests/`.

### Stage 3: Adversarial Code Review (`code-reviewer` subagent)
1. Dispatch the `code-reviewer` subagent immediately after code and tests are written.
2. The reviewer checks:
   - Memory leaks, runaway loops, unhandled edge cases, missing timeouts.
   - Cache bypass risks (accidental live API quota burn).
   - Type safety, error handling, clean async/sync boundaries.
   - Verification of tests.
3. **Hard Gate:** If the reviewer returns findings (Critical, High, or Medium), the developer MUST fix them surgically and request a second-pass review until the verdict is **`PASS (APPROVED)`**.

### Stage 4: Multi-Gate Verification
Before committing, all 3 gates must pass:
1. **Gate 1 (Unit & Integration Tests):** 100% pytest pass rate (`pytest -v`).
2. **Gate 2 (Build & Type Check):** Frontend and backend compile cleanly with zero errors.
3. **Gate 3 (End-to-End Walkthrough):** Local run succeeds without crashes or visual layout breaks.

### Stage 5: Commit & Living Roadmap Logging
1. Stage modified files and commit using Conventional Commits:
   `feat(agent): implement adversarial red-team audit node (Task 1.2)`
2. Update `docs/*-roadmap.md`:
   - Set status to `✅ Completed`.
   - Record commit hash and review verdict.
   - Summarize the verified behavior.
3. Keep `AGENTS.md` aligned with active project status and map.

---

## 🛡️ Critical Hackathon Guardrails

### 1. The Quota Defense Rule
- Never call live paid/rate-limited APIs (e.g. SerpApi, paid LLM endpoints) in raw test loops.
- Implement a **Day-1 disk cache decorator** (SQLite or JSON).
- Integration tests must hit cached fixtures or mocks unless explicitly performing live end-to-end certification.

### 2. The Golden Demo Principle
- The final judging submission requires a **demo video under 3 minutes**.
- Always build a toggle in the UI:
  - `Live Mode`: Queries real-time APIs for arbitrary user inputs.
  - `Pre-Cached / Golden Demo Mode`: Instant, zero-latency playback of rich pre-verified target profiles (e.g. Perplexity AI, Zepto) to guarantee 100% video reliability with zero network timeouts.

### 3. Living Documentation Rule
The project must always maintain 3 core living documents in `docs/`:
- **`docs/*-plan.md`**: Master architecture, competitive analysis, and tech decisions.
- **`docs/*-roadmap.md`**: Task matrix, subagent log, and commit history.
- **`docs/*-regression-audit.md`**: 100% health scorecard verifying all previously shipped features.

---

## 🌿 Milestone Branching & Versioning Strategy

To guarantee zero regressions and clean, reviewable history, feature work is strictly partitioned across milestone release branches:

```
main (Production certified releases)
  │
  ├── v0.1-dev (Sprint 1: Foundation, SQLite Disk Cache & SerpApi Service)
  │     ├── commit Task 1.1 (feat: SerpApi multi-engine client)
  │     ├── commit Task 1.2 (feat: SQLite disk cache decorator)
  │     └── commit Task 1.3 (test: foundation unit tests)
  │     └── [Merge to main -> Tag v0.1.0]
  │
  ├── v0.2-dev (Sprint 2: LangGraph Dialectical State Machine & Red-Team Engine)
  │     ├── commit Task 2.1 (feat: DueDiligenceState schema)
  │     ├── commit Task 2.2 (feat: Multi-node LangGraph execution)
  │     ├── commit Task 2.3 (feat: Adversarial Red-Team auditor)
  │     ├── commit Task 2.4 (feat: Dossier compiler)
  │     └── commit Task 2.5 (test: graph tests)
  │     └── [Merge to main -> Tag v0.2.0]
  │
  └── v0.3-dev (Sprint 3: Interactive Streamlit UI, Citations & Golden Walkthrough)
        ├── commit Task 3.1 (feat: Streamlit UI with live event streaming)
        ├── commit Task 3.2 (feat: Risk radar, timeline & citation components)
        ├── commit Task 3.3 (docs: regression audit scorecard & demo script)
        └── [Merge to main -> Tag v0.3.0 / v1.0.0]
```

### Commit-Per-Task Policy (Strict)
1. **One Commit Per Task:** Every completed task must have its own dedicated conventional commit:
   `<type>(<scope>): <subject> (Task <X.Y>)`
2. **Pre-Commit Verification:** A task commit is only permitted AFTER:
   - Developer implementation is complete.
   - `code-reviewer` subagent has certified `PASS (APPROVED)`.
   - Relevant unit tests pass.
3. **Roadmap Sync:** Immediately record the commit hash in `docs/*-roadmap.md` alongside the reviewer's verdict.
