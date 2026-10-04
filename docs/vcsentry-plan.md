# VCSentry — Foundation Architecture & System Design Plan

> **Project:** VCSentry (Autonomous Startup & Founder Due Diligence Agent)  
> **Hackathon:** SerpApi India Hackathon 2026 (AI Agents Track)  
> **Status:** Architecture Certified (Sprint 1)  
> **Author:** Architecture Lead & Project Partner

---

## 1. Executive Summary

**VCSentry** is an autonomous, multi-agent due diligence system designed for angel investors, venture capital analysts, and accelerator screening committees. 

Unlike conventional search wrappers that run a single prompt against a basic search endpoint, VCSentry uses a **LangGraph state machine** to execute an autonomous dialectical investigation:
1. It formulates investigative hypotheses across 4 forensic risk pillars: **Founder Credibility**, **Market & Competitor Saturation**, **Traction Authenticity**, and **Technical/IP Moat**.
2. It routes precision queries across **4 specialized SerpApi search engines** (Google Organic Search & Knowledge Graph, Google News, Google Scholar, and Google Patents).
3. It deploys an internal **Adversarial Red-Team Auditor** that actively hunts for discrepancies, past litigations, and exaggerated claims.
4. It compiles an institutional-grade **Investment Committee Dossier** complete with an interactive **Risk Radar Matrix**, **Temporal Milestone Timeline**, and a **Clickable Citation Ledger** tying every assertion directly to verified SERP sources.

---

## 2. Competitive Analysis & Edge

Reviewing the 185 community projects in `#BuiltWithSerpApi` revealed clear differentiators:
- Most submissions were linear scripts that summarized Google Search results into generic markdown.
- Top-scoring projects (*SignalWatch*, *PatentPincer*, *Research Brief Bot*) succeeded by utilizing multi-engine data or forensic verification.
- **VCSentry's Edge:** It is the first project to combine **LangGraph cyclical state machines** with **Adversarial Dialectical Audit (Bull vs. Bear)** and **multi-engine SerpApi triangulation** (Search + News + Scholar + Patents) wrapped in a polished interactive Streamlit dashboard.

---

## 3. High-Level System Architecture

```
                               ┌─────────────────────────────────┐
                               │ User Input: Startup Name/Domain │
                               └────────────────┬────────────────┘
                                                │
                                                ▼
                               ┌─────────────────────────────────┐
                               │ Intake & Domain Resolution Node │
                               └────────────────┬────────────────┘
                                                │
                                                ▼
                               ┌─────────────────────────────────┐
                               │ Hypothesis & Query Router Node  │
                               └────────────────┬────────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
        ┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
        │  Google Search   │           │   Google News    │           │  Google Scholar  │
        │ & Knowledge Graph│           │ (Timeline & PR)  │           │   & Patents      │
        └────────┬─────────┘           └────────┬─────────┘           └────────┬─────────┘
                 └──────────────────────────────┼──────────────────────────────┘
                                                ▼
                               ┌─────────────────────────────────┐
                               │   Evidence Extraction & Graph   │
                               └────────────────┬────────────────┘
                                                │
                                                ▼
                               ┌─────────────────────────────────┐
                               │ Adversarial Red-Team Auditor    │◄───┐
                               │ (Discrepancies & Contradictions)│    │ Verification Loop
                               └────────────────┬────────────────┘    │ (Max 2 hops)
                                                │─────────────────────┘
                                                ▼
                               ┌─────────────────────────────────┐
                               │ Institutional Dossier Compiler  │
                               └────────────────┬────────────────┘
                                                │
                        ┌───────────────────────┼───────────────────────┐
                        ▼                       ▼                       ▼
               ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
               │   Risk Radar   │      │ Milestone Time │      │ Clickable SERP │
               │  Scorecard     │      │     -line      │      │ Citation Ledger│
               └────────────────┘      └────────────────┘      └────────────────┘
```

---

## 4. Multi-Engine SerpApi Integration Strategy

| SerpApi Engine | Role in Due Diligence | Key Extracted Fields |
|---|---|---|
| **Google Search & Knowledge Graph** | Baseline entity resolution, market positioning, organic customer discussions (Reddit/X/Forums). | `knowledge_graph`, `organic_results`, `related_questions` |
| **Google News** | Chronological timeline reconstruction, funding announcements, regulatory scrutiny, executive departures. | `news_results`, `date`, `source`, `snippet` |
| **Google Scholar** | Founder academic pedigree, peer-reviewed publications, verification of scientific/AI claims. | `organic_results`, `publication_info`, `inline_links.cited_by` |
| **Google Patents** | Deep-tech moat validation, prior art existence, verification of proprietary IP claims. | `organic_results`, `patent_id`, `filing_date`, `assignee` |

---

## 5. Quota Defense & Caching Architecture

To prevent depleting the 250 free monthly queries during development and testing:
- **`cache_service.py`**: A transparent SQLite-backed disk cache (`vcsentry.db`) wrapping `SerpApiClient`.
- Any query with matching parameters (`engine`, `q`, `location`) returns instant cached JSON.
- **Golden Demo Profiles**: Pre-seeded caches for flagship companies (e.g., *Perplexity AI*, *Zepto*) guarantee instant sub-second execution during live video recordings.
