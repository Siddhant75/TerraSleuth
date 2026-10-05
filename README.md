# 🌍 TerraSleuth — Autonomous Multi-Modal Visual & Geospatial OSINT Detective

> **SerpApi India Hackathon 2026** — *AI Agents Track*  
> Powered by **SerpApi (Google Lens, Google Maps, Google News, Google Search)** & **LangGraph Multi-Agent Swarm**

[![Hackathon Track](https://img.shields.io/badge/SerpApi%20Hackathon-AI%20Agents%20Track-blue.svg)](https://serpapi.github.io/serpapi-india-hackathon-2026/#tracks)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-green.svg)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-77%2F77%20Passing%20(100%25)-brightgreen.svg)](docs/terrasleuth-regression-audit.md)
[![Release Certified](https://img.shields.io/badge/Release-v0.4.0--certified-blueviolet.svg)](AGENTS.md)
[![Quota Defense](https://img.shields.io/badge/Quota%20Defense-Zero--Credit%20Testing-success.svg)](backend/app/services/cache_service.py)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🔍 What is TerraSleuth?

Standard LLMs hallucinate physical locations, invent dates, and operate in a digital vacuum.

**TerraSleuth** transforms the AI agent into an autonomous **Digital Forensic OSINT Detective**. Given an uncaptioned photograph, a viral breaking-news image, or a suspicious marketplace photo:

1. **Deconstructs the Scene**: Extracts atomic visual clues—architectural styles, street signage scripts (Devanagari, Cyrillic, Latin), vehicle driving sides, and flora/climate—binding them to normalized bounding box coordinates.
2. **Hunts Visual Provenance (Google Lens API)**: Searches the global visual web to unearth where the photo originated, finding exact matches and initial indexing timestamps.
3. **Triangulates Physical Coordinates (Google Maps & Local API)**: Correlates street names, business signs, and landmarks into precise WGS84 latitude, longitude, and physical addresses with a spatial consensus radius.
4. **Audits Chronology & News (Google News & Search APIs)**: Validates historical milestones, news reports, and viral cycles to verify whether the image represents breaking reality or recycled media.
5. **Compiles an Interactive Case File**: Synthesizes findings into a verifiable forensic dossier featuring an interactive Leaflet map, visual evidence board, chronological timeline, and multi-engine citation ledger.

---

## 🗺️ System Architecture

```
                                Input Mystery Image
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │   Scene Deconstructor    │
                           │ (Pillow / Vision Clues)  │
                           └────────────┬─────────────┘
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │       Lens Hunter        │
                           │   (SerpApi Google Lens)  │
                           └────────────┬─────────────┘
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │     Geo Triangulator     │
                           │   (SerpApi Google Maps)  │
                           └────────────┬─────────────┘
                                        │
                         [Budget & Ambiguity Routing]
                                        ├── (Refine if ambiguous) ──┐
                                        │                           │
                                        ▼                           │
                           ┌──────────────────────────┐             │
                           │      Chrono Auditor      │             │
                           │   (SerpApi Google News)  │             │
                           └────────────┬─────────────┘             │
                                        │                           │
                                        └─────────────┬─────────────┘
                                                      │
                                                      ▼
                                       ┌─────────────────────────────┐
                                       │   Lead Detective Synthesizer│
                                       │ (LangGraph Consensus Engine)│
                                       └──────────────┬──────────────┘
                                                      │
                                                      ▼
                       ┌──────────────────────────────────────────────────────────┐
                       │          Tactical OSINT Command Deck (v0.4.0)            │
                       │  • 🎯 Visual Forensic Inspector & Bounding Clues         │
                       │  • 🔬 Side-by-Side Visual Twin Matcher (Google Lens)     │
                       │  • 📡 Live Monospace Swarm Telemetry Terminal (Cyber HUD)│
                       │  • 🗺️ Satellite Recon Pinpoint (Esri World Imagery)       │
                       │  • ⏱️ Chronological Provenance & Media Timeline          │
                       │  • 🔗 Verifiable Multi-Engine SERP Citation Ledger       │
                       └──────────────────────────────────────────────────────────┘
```

---

## 🕹️ Tactical OSINT Command Deck (v0.4.0)

TerraSleuth features a Bellingcat/Palantir-grade Command Deck:

- **Authentic Photographic Target Library**: Pre-seeded with real high-resolution surveillance and OSINT challenge images (*Waterfront Monument at Apollo Bunder*, *Neuschwanstein Alpine Palace*, *Santorini Rental Scam Fraud Exposer*).
- **Split-Screen Command Deck (45/55 Layout)**: Left deck inspects visual evidence; right deck provides tactical geospatial maps, telemetry, and intelligence.
- **Side-by-Side Visual Twin Matcher**: Directly aligns the suspect photo against the top Google Lens authoritative thumbnail with an explainable `Visual Correspondence %` score.
- **Live Monospace Swarm Telemetry Terminal**: High-contrast obsidian cyber terminal (`#090d16`) streaming real-time agent deductions and SerpApi engine queries.
- **Tactical Satellite Reconnaissance (Esri World Imagery)**: Crystal-clear aerial satellite imagery with pulsating crosshair pin and consensus accuracy circle (zero watermarks).
- **Non-Truncating Flexbox Telemetry Bar**: Real-time WGS84 coordinates, verifiability rating, and query budget counter with responsive layouts.
- **Verifiable Citation Ledger**: Clickable evidence trails grouped by SerpApi engine (Google Lens, Maps, News, Search) with strict URL sanitization.
- **Export Dossier**: One-click download of the completed `CaseFile` in JSON or Markdown format.

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.11 or 3.12
- SerpApi API Key ([Sign up for free 250 credits/mo](https://serpapi.com/users/sign_up?plan=free))

### 2. Installation
```bash
git clone https://github.com/Siddhant75/TerraSleuth.git
cd TerraSleuth
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Environment Configuration
```bash
cp .env.example .env
# Edit .env and enter your SERPAPI_API_KEY
```

*(Note: Golden Mystery Targets and automated test suites run completely offline against the local SQLite cache without consuming API credits).*

### 4. Run the Interactive Dashboard
```bash
streamlit run frontend/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 5. Run the Full Automated Test Suite (77/77 Passing)
```bash
# Run all unit, integration, and end-to-end tests
pytest -v
```

---

## 🛡️ Hackathon Engineering Disciplines

1. **Subagent-Driven Development (SDD):** Built strictly following the SDD engineering protocol (`architect` blueprinting $\to$ surgical development $\to$ adversarial review via `code-reviewer` $\to$ multi-gate verification).
2. **Strict Quota Defense:** Wrapped in a SQLite WAL disk cache (`terrasleuth.db`) with SHA-256 parameter hashing (stripping API keys and transient flags). Zero live credits are consumed during test suites or offline golden demos.
3. **Zero Hallucination Guarantee:** Every geographical coordinate and timeline event is strictly anchored to an authoritative SerpApi result in the citation ledger.
4. **XSS & Security Hardening:** Comprehensive HTML escaping on all scraped/external strings and strict URL scheme allowlisting (`http://` / `https://` only) preventing script execution in Markdown or Folium popups.
5. **Memory & Disk Hygiene:** Session-state-managed file upload rotation unlinks orphan temporary files upon subsequent reruns.

---

## 🎬 Golden Demo Walkthrough

Review our step-by-step 3-minute video presentation script in [docs/golden-demo-script.md](docs/golden-demo-script.md).

---

## 📜 Repository Governance

- **[AGENTS.md](AGENTS.md):** Master architecture and subagent navigation guide.
- **[docs/terrasleuth-roadmap.md](docs/terrasleuth-roadmap.md):** Living roadmap and subagent execution matrix.
- **[docs/terrasleuth-regression-audit.md](docs/terrasleuth-regression-audit.md):** Living regression audit and 65-test health scorecard.
- **[docs/terrasleuth-plan.md](docs/terrasleuth-plan.md):** Multi-engine SerpApi integration plan and LangGraph state machine design.
