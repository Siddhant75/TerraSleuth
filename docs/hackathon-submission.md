# TerraSleuth — Official Hackathon Submission

**SerpApi India Hackathon 2026 — AI Agents Track**  
**Autonomous Multi-Modal Visual & Geospatial OSINT Detective Swarm**  
**Certified Version:** `v0.5.0` (War Room 2.0 HUD & Advanced OSINT Feature Pack)

---

## 🚀 Executive Summary

The Internet is inundated with uncaptioned viral photographs, recycled crisis imagery, and deceptive marketplace listings. Identifying the true origin of a photo usually demands hours of tedious manual cross-referencing across reverse image databases, mapping platforms, and historical archives.

**TerraSleuth** is an autonomous multi-agent OSINT investigator powered by **LangGraph** and **SerpApi**. It accepts any suspect image, autonomously extracts architectural, botanical, and linguistic visual clues, triangulates geographic coordinates across Google Lens and Google Maps, verifies timeline provenance across Google News, exposes fraudulent listings and recirculated disinformation, and compiles a forensically verifiable, standalone offline intelligence dossier — all while strictly defending API quotas through a zero-cost local SQLite cache.

---

## ⚡ Live War Room 2.0 User Interface

TerraSleuth features a tactical **45/55 Split-Screen Command Deck** inspired by forensic war rooms:

| Left Column (Visual Forensic Inspector) | Right Column (Tactical Intelligence Deck) |
|---|---|
| **Suspect Target Evidence:** Photographic viewer with category-colored visual clue overlays. | **Satellite Reconnaissance:** High-contrast tactical map (Esri World Imagery) with glowing neon pin and consensus radius circle. |
| **Visual Twin Comparator:** 50/50 side-by-side alignment comparing suspect photo against authoritative Google Lens thumbnails with correspondence scores. | **Live Swarm Radar:** Monospace terminal displaying real-time agent deductions, timestamps, and SerpApi engine calls. |
| **Mission Briefing Deck:** 3 pre-cached, zero-credit scenarios (Gateway of India, Neuschwanstein Castle, Santorini Vacation Rental Scam). | **Investigation Sub-Tabs:** Chronological Provenance, Verifiable Citations, Advanced OSINT Dorks, and Executive Dossier. |

---

## 🔬 Deep SerpApi Multi-Engine Portfolio Integration

TerraSleuth deeply integrates **4 distinct SerpApi engines** to build an unbreakable chain of custody:

```
[Suspect Image] 
       │
       ▼
[Scene Deconstructor] ──> Extracts Visual Clues (Architecture, Signage, Flora, Landmarks)
       │
       ├─► 1. SerpApi Google Lens API ──────► Visual Twin Matches & Authoritative Domains
       │
       ├─► 2. SerpApi Google Maps / Local ──► WGS84 Coordinates, Address & Place Validation
       │
       ├─► 3. SerpApi Google News API ──────► Temporal Provenance & Earliest Publication
       │
       ├─► 4. SerpApi Google Search API ────► Advanced OSINT Dorks (Permits, Deeds, Directories)
       ▼
[Lead Detective Synthesizer] ───────────────► Fraud Unmasking & Standalone HTML Dossier Export
```

### 1. SerpApi Google Lens Engine (`engine="google_lens"`)
- Deconstructs visual twins and authoritative sources for suspect imagery.
- Automatically crops region bounding boxes when primary reverse matches are ambiguous.
- Harvests authoritative domain entities, titles, and match thumbnails.

### 2. SerpApi Google Maps & Local Places (`engine="google_maps"`)
- Converts visual clues and candidate place names into precise WGS84 coordinates (`latitude`, `longitude`).
- Validates formal municipal street addresses, place IDs (`place_id`), star ratings, and community reviews.
- Computes spatial consensus scores between visual hypotheses and physical entities.

### 3. SerpApi Google News Engine (`engine="google_news"`)
- Unearths the chronological publication history of the image.
- Identifies the earliest recorded news appearances to combat media recycling.
- Exposes temporal disinformation where historical event photos are falsely captioned as breaking crises.

### 4. SerpApi Google Search Engine (`engine="google"`)
- Formulates targeted **Advanced OSINT Google Dorks** based on resolved entity names:
  - **Municipal & Property Records:** `filetype:pdf ("<Target>") ("permit" OR "zoning" OR "property" OR "architectural" OR "report")`
  - **Investigative Press & Archives:** `"<Target>" ("investigation" OR "controversy" OR "renovation" OR "history" OR "lawsuit")`
  - **Government & Academic Registries:** `site:gov OR site:org OR site:edu ("<Target>")`
  - **Exposed Web Directories:** `intitle:"index of" "<Target>"`

---

## 🚨 Flagship Investigative Features

### 1. Vacation Rental & Marketplace Scam Exposer
Scammers frequently steal photos of world-class resorts to market nonexistent residential rentals. TerraSleuth's `AnomalyService` cross-examines Google Lens visual twins against claimed property listings, detecting discrepancies between claimed locations and authentic commercial properties.
- **Demo Golden Target:** A claimed local vacation apartment unmasked as a copyrighted marketing photo of *Canaves Oia Suites* in Santorini, Greece. Displays an unmissable glowing red alert banner with direct source verification.

### 2. Bellingcat-Grade Temporal Disinformation Debunker
During emergencies, bad actors recirculate old disaster photos to incite panic. TerraSleuth flags media appearing online prior to claimed incident timestamps as `RECIRCULATED_MEDIA`.

### 3. Standalone Offline HTML Dossier Exporter
Investigators often operate in air-gapped environments. With 1 click, TerraSleuth compiles a self-contained `.html` dossier with:
- Embedded Base64 suspect photography
- Responsive obsidian telemetry banner
- Visual clues breakdown table
- Satellite WGS84 coordinates & Google Maps link
- Chronological timeline & multi-engine citation ledger
- Targeted OSINT Google Dorks

### 4. Zero-Credit Invariant & Quota Defense
SerpApi free tiers provide 250 searches. TerraSleuth guarantees that developers, judges, and CI/CD never burn live credits unintentionally:
- **Transparent SQLite WAL Disk Cache (`terrasleuth.db`):** Pre-seeded with golden investigative scenarios for lag-free, zero-credit demos.
- **Parameter Normalization:** Canonical hashing strips transient query parameters and API keys.
- **Circuit Breakers:** Strictly decrements query budgets, skipping remote execution if the quota ceiling is reached.

---

## 🏆 Engineering Rigor & Test Scorecard

TerraSleuth was engineered under strict **Subagent-Driven Development (SDD)** with adversarial multi-agent code reviews (`architect` blueprinting + `code-reviewer` signoff):

| Metric | Measurement |
|---|---|
| **Total Automated Tests** | **84 passing / 84 total (100% pass rate)** |
| **Unit & Integration Test Time** | ~18.0 seconds |
| **Live SerpApi Credits Burned in Tests** | **0 credits** |
| **Security & XSS Protection** | Strict scheme allowlist (`http`, `https`, `mailto`) neutralizing `javascript:` injection |
| **Browser E2E Automation** | 9 verified Playwright visual screenshots (`tests/e2e/screenshots/`) |

---

## 📦 Quickstart & Running Instructions

### Option 1: Docker (Recommended for Judges)
```bash
# 1. Clone repository
git clone https://github.com/example/terrasleuth.git
cd terrasleuth

# 2. Launch container (Zero-credit pre-cached demo works immediately without API key)
docker-compose up --build

# 3. Open browser
http://localhost:8501
```

### Option 2: Python Virtual Environment
```bash
# 1. Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Provide SerpApi API key for live searches in .env
echo "SERPAPI_API_KEY=your_key_here" > .env

# 4. Launch the War Room 2.0 Dashboard
streamlit run frontend/app.py
```

### Option 3: Run Full Automated Test Suite
```bash
# Set PYTHONPATH and run all 84 automated tests
$env:PYTHONPATH="." ; pytest -v
```

---

## 🎬 3-Minute Demonstration Guide

1. **0:00 – 0:30 (Mission Briefing):** Review the 3 investigative scenarios in the War Room 2.0 HUD.
2. **0:30 – 1:15 (Landmark Pinpoint):** Select "The Waterfront Monument & Heritage Hotel", click **Launch Autonomous Investigation**, watch the LangGraph swarm extract clues, and pinpoint Gateway of India on satellite tiles with 96% confidence.
3. **1:15 – 1:55 (Visual Twin Comparator):** Switch to the Side-by-Side Visual Twin Matcher, inspecting exact visual alignment against authoritative Wikipedia images.
4. **1:55 – 2:30 (Fraud Unmasking):** Select "Vacation Rental Listing Fraud", launch investigation, and watch the red Anomaly Banner unmask the stolen Santorini luxury hotel photo.
5. **2:30 – 3:00 (Export & Offline Dossier):** Click "Download Standalone HTML Forensic Dossier" to inspect the self-contained intelligence report.
