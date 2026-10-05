# 🌍 TerraSleuth — Autonomous Multi-Modal Visual & Geospatial OSINT Detective

> **SerpApi India Hackathon 2026** — *AI Agents Track*  
> Powered by **SerpApi (Google Lens, Google Maps, Google News, Google Search)** & **LangGraph**

[![Hackathon Track](https://img.shields.io/badge/SerpApi%20Hackathon-AI%20Agents%20Track-blue.svg)](https://serpapi.github.io/serpapi-india-hackathon-2026/#tracks)
[![Python Version](https://img.shields.io/badge/Python-3.11-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Release-v0.1--dev-orange.svg)](AGENTS.md)

---

## 🔍 What is TerraSleuth?

Standard AI agents operate in a digital vacuum—they hallucinate coordinates, invent facts, and are blind to the open visual web. 

**TerraSleuth** transforms the AI Agent into an autonomous **Digital Forensic Detective (OSINT)**. Given an uncaptioned photograph, a viral breaking-news image, or a suspicious marketplace photo:
1. **Deconstructs the Scene**: Extracts atomic visual clues—architectural styles, street signage scripts (Devanagari, Cyrillic, Latin), vehicle driving sides, and flora/climate.
2. **Hunts Visual Provenance (Google Lens API)**: Searches the global visual web to unearth where the photo originated, finding exact matches and initial indexing timestamps.
3. **Triangulates Physical Coordinates (Google Maps & Local API)**: Correlates street names, business signs, and landmarks into precise latitude, longitude, and physical addresses.
4. **Audits Chronology & News (Google News & Search APIs)**: Validates historical events, weather reports, and local news to verify whether the image represents breaking reality or recycled media.
5. **Compiles an Interactive Case File**: Delivers an annotated visual evidence board, live interactive Leaflet map coordinate pinpoint, and a verifiable citation ledger.

---

## 🗺️ System Architecture

```
  Input Mystery Image
          │
          ▼
  Visual Scene Deconstructor
  (Multi-Modal Clue Extraction)
          │
   ┌──────┴───────────────────────────┬───────────────────────────┐
   ▼                                  ▼                           ▼
Lens Hunter                   Geo Triangulator             Chrono Auditor
(SerpApi Google Lens)        (SerpApi Google Maps)        (SerpApi News & Search)
   │                                  │                           │
   └──────┬───────────────────────────┴───────────────────────────┘
          ▼
  Lead Detective (LangGraph Dialectical Case Resolver)
          │
          ▼
  Interactive OSINT Case Dossier:
  • Visual Evidence Board (with Bounding Clues)
  • Interactive Map Pinpoint (Lat/Lon Coordinates)
  • Chronological Provenance Timeline
  • Clickable SERP Citation Ledger
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.11+
- SerpApi API Key ([Sign up for free 250 credits/mo](https://serpapi.com/users/sign_up?plan=free))

### 2. Installation
```bash
git clone https://github.com/Siddhant75/TerraSleuth.git
cd TerraSleuth
pip install -r backend/requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Add your SERPAPI_API_KEY and LLM API Key (OpenAI / Gemini / Anthropic)
```

### 4. Run Interactive Dashboard
```bash
streamlit run frontend/app.py
```

---

## 🔑 Key Engineering Rules
- **Subagent-Driven Development (SDD)**: Architect blueprinting, developer execution, adversarial code review (`code-reviewer`), and multi-gate verification.
- **Quota Defense**: SQLite disk-cache layer (`terrasleuth.db`) wrapping all SerpApi requests so development and tests burn zero unnecessary credits.
- **Golden Mystery Demo Mode**: Pre-cached targets for instant, lag-free <3 minute video recording.

---

## 📜 Governance
Read [AGENTS.md](file:///d:/SerpAPI_hackathon/AGENTS.md) for master architecture and [docs/terrasleuth-roadmap.md](file:///d:/SerpAPI_hackathon/docs/terrasleuth-roadmap.md) for active task execution status.
