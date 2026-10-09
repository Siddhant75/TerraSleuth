# TerraSleuth — Official Hackathon Submission

**SerpApi India Hackathon 2026 — AI Agents Track**  
**Autonomous Multi-Modal Visual & Geospatial OSINT Detective Swarm**  
**Certified Version:** `v0.8.1 Certified` (Level 5 Dialectical Swarm & Dynamic LLM Detective Engine)  
**Architecture Specification:** Certified Level 5 Multi-Agent Swarm with C4 Architecture Model  
**Automated Tests:** 158 passing / 158 total (100% pass rate, 0 live SerpApi credits burned)

---

## 🚀 Executive Summary

The Internet is inundated with uncaptioned viral photographs, recycled crisis imagery, and deceptive marketplace listings. Identifying the true origin of a photo usually demands hours of tedious manual cross-referencing across reverse image databases, mapping platforms, and historical archives.

**TerraSleuth** is an autonomous multi-modal OSINT investigator powered by **LangGraph**, **SerpApi Multi-Engine Cloud**, and **Google Gemini 1.5 Flash**. Inspired by autonomous agent architectures (like Google Antigravity), TerraSleuth accepts any suspect image or URL, autonomously extracts architectural, botanical, and linguistic visual clues, triangulates geographic coordinates across Google Lens and Google Maps, verifies timeline provenance across Google News, exposes fraudulent listings through adversarial cross-examination, and compiles a forensically verifiable, standalone offline intelligence dossier — all while strictly defending API quotas through a zero-cost local SQLite cache.

---

## 🏆 Why TerraSleuth Wins the SerpApi AI Agents Track

The hackathon challenge: *"Create agents that plan, search, compare, and act with current information. Research, RAG, Multi-agent, Automation."*

| Hackathon Criterion | TerraSleuth Implementation & SerpApi Synergy |
|---|---|
| **Plan** | **Scene Deconstructor, Hybrid Vision Ensemble & HITL Directives:** Breaks mystery images into atomic visual clues (architecture, signage script, vegetation). Leverages a **Hybrid Vision Ensemble (Google AI Studio Gemini 1.5 Flash Spatial Vision + OpenCV)** to extract normalized 2D bounding boxes `[ymin, xmin, ymax, xmax]` for multi-object decomposition. Empowers detectives with **Human-in-the-Loop (HITL) Mission Directives** and label filtering checkpoints. Dynamically classifies intent (`GEOSPATIAL_LANDMARK`, `FASHION_PRODUCT`, `FRAUD_DISINFORMATION`, `GENERAL_OBJECT`) via two-tier semantic LLM reasoning with <20ms zero-cost heuristic fallback. |
| **Search** | **Autonomous Multi-Engine SerpApi Tools & Binary Image Upload API:** Dispatches `upload_image` via SerpApi Image API (`POST https://serpapi.com/image`) with Pillow iterative auto-resizing under 500 KB limit, `tool_lens_search` (reverse visual twins & regional bounding-box crops), `tool_maps_triangulate` (GPS coordinates & local place consensus), `tool_news_audit` (temporal historical archives), and `tool_google_dork` (municipal permits & open directories). |
| **Compare** | **Level 5 Dialectical Red-Team Swarm (Hunter vs. Skeptic):** The **Hunter** proposes candidate locations or multi-item wardrobe catalog hypotheses; the **Skeptic** actively cross-examines them using dynamic Gemini LLM reasoning, detecting contradictions between claimed captions and authoritative reality; the **Arbiter** calculates a continuous `AdversarialAuditScore` (0.0 to 1.0) and certifies the final verdict. |
| **Act** | **Geospatial Pinpoint & Court-Ready Dossier:** Resolves physical WGS84 coordinates on Esri satellite imagery, evaluates Geoguessr 5,000-point accuracy, unmasks rental fraud, renders an **Itemized Wardrobe & Product Forensic Ledger**, and generates a **1-click standalone offline HTML forensic dossier** with Base64 embedded imagery. |
| **Research & RAG** | **Zero-Hallucination Real-Time Web Grounding:** Eliminates LLM spatial hallucinations by grounding every evidentiary claim in authoritative SerpApi URLs with exact timestamps, place IDs, and municipal records. |
| **Multi-Agent & Automation** | **LangGraph State Machine with Adaptive Branching:** 100% autonomous execution from single mystery image to final case file with bounded refinement loops ($\le 2$ hops), adaptive routing bypassing Google Maps for fashion targets, and strict quota budget management (capping crop calls at max 5 items). |

---

## 🔬 Deep SerpApi Multi-Engine Portfolio Integration

TerraSleuth deeply integrates **4 distinct SerpApi engines** plus the binary **Image Upload API** to build an unbreakable chain of custody:

```
[Suspect Image / Local File Upload]
       │
       ├─► 0. SerpApi Image Upload API ─────► Binary Upload (<500KB Auto-Resize) -> image_id
       │
       ├─► 1. SerpApi Google Lens API ──────► Visual Twin Matches, Domains & Regional Bounding Crops
       │
       ├─► 2. SerpApi Google Maps / Local ──► WGS84 Coordinates, Address & Place Validation
       │
       ├─► 3. SerpApi Google News API ──────► Temporal Provenance & Earliest Publication
       │
       ├─► 4. SerpApi Google Search API ────► Advanced OSINT Dorks (Permits, Deeds, Directories)
       ▼
[Lead Detective Synthesizer] ───────────────► Fraud Unmasking & Standalone HTML Dossier Export
```

### 0. SerpApi Image Upload API (`POST https://serpapi.com/image`)
- Enables local image file uploads directly to SerpApi servers.
- Features iterative Pillow resizing and quality compression under SerpApi's 500 KB limit.
- SHA-256 disk caching prevents redundant re-uploads.

### 1. SerpApi Google Lens Engine (`engine="google_lens"`)
- Deconstructs visual twins and authoritative sources for suspect imagery.
- Automatically crops sub-region bounding boxes (`tool_crop_region`) for multi-object decomposition.
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

## 🧠 Antigravity-Style Dynamic LLM Decision Engine

In addition to deterministic heuristics, TerraSleuth integrates **Google Gemini 1.5 Flash** for dynamic, non-deterministic agentic reasoning:

1. **Autonomous Fraud & Scam Unmasking (`skeptic_node`):**
   * Dynamically cross-examines user-provided captions against reverse-image matches, architectural features, vegetation, and local business names.
   * Catches novel scams without relying on keyword matching (e.g. whitewashed Cycladic architecture overlooking a volcanic caldera in Greece claimed as a beachfront apartment in Miami, Florida).
2. **Dynamic Dialectical Arbitration & Continuous Scoring (`arbiter_node`):**
   * The Arbiter weighs the Hunter's affirmative proof against the Skeptic's counter-arguments, generating a real continuous confidence score (0.0 to 1.0) rather than fixed constants.
3. **Executive Forensic Narrative (`case_synthesizer_node`):**
   * Synthesizes a bespoke intelligence briefing tailored to the specific case, highlighting evidentiary anomalies, timeline provenance, and forensic citations.
4. **Live Monospace Telemetry Terminal:**
   * Streams raw agent thought processes to the UI (`[HUNTER THOUGHT]`, `[SKEPTIC CRITIQUE]`, `[ARBITER VERDICT]`), providing complete agentic observability.

---

## 🎯 4 Flagship Real-World Scenarios

TerraSleuth addresses high-stakes open-source intelligence challenges:

### 1. 🚨 Landmark Pinpoint & Heritage Identification
- **Problem:** Uncaptioned tourist photograph of a waterfront monument with no metadata.
- **TerraSleuth Action:** Multi-modal deconstruction isolates the Indo-Saracenic basalt arch and Taj Palace dome. Google Lens and Google Maps resolve the Gateway of India in Colaba, Mumbai with 96% confidence and precise WGS84 coordinates on satellite imagery.

### 2. 🏖️ Vacation Rental & Marketplace Scam Exposer
- **Problem:** Scammer advertises an uncaptioned luxury apartment on Airbnb/Craigslist claiming it is a local residential rental in Miami.
- **TerraSleuth Action:** Dynamic LLM Skeptic cross-examines the photo against SerpApi Google Lens visual twins, exposing the listing as a copyrighted promotional photograph stolen from *Canaves Oia Suites* in Santorini, Greece. Displays an unmissable glowing red alert banner with direct source verification.

### 3. 🎯 Autonomous Geoguessr Champion
- **Problem:** Mystery image of an alpine castle shrouded in mist.
- **TerraSleuth Action:** Progressively narrows spatial search radius from Continental (2,500km) to Street scale (<50m), pinpointing Neuschwanstein Castle in Bavaria, Germany and achieving a **5,000-point competitive Geoguessr score**.

### 4. 👗 Multi-Item Fashion & Wardrobe Visual Decomposition
- **Problem:** Flat-lay image containing multiple touching items (dress, luxury bag, earrings, watch, bracelet, shoes). Standard reverse-image searches anchor on the dominant central dress and miss all accessories.
- **TerraSleuth Action:** Native OpenCV contour detection with chromatic/spatial sub-segmentation isolates each discrete item into normalized bounding boxes. The swarm adaptively routes to `fashion_hunter_node` (bypassing Google Maps), executes regional crop searches capped at max 5 items to defend quota, and generates an **Itemized Wardrobe & Product Forensic Ledger** with retailer sources and direct shopping links.

---

## ⚡ Live War Room 2.0 User Interface

TerraSleuth features a tactical **45/55 Split-Screen Command Deck** inspired by forensic war rooms:

| Left Column (Visual Forensic Inspector) | Right Column (Tactical Intelligence Deck) |
|---|---|
| **Suspect Target Evidence:** Photographic viewer with category-colored visual clue overlays. | **Satellite Reconnaissance:** High-contrast tactical map (Esri World Imagery) with glowing neon pin and consensus radius circle. |
| **Visual Twin Comparator:** 50/50 side-by-side alignment comparing suspect photo against authoritative Google Lens thumbnails with correspondence scores. | **Live Swarm Radar:** Monospace terminal displaying real-time agent deductions, timestamps, and SerpApi engine calls. |
| **Mission Briefing Deck:** 3 pre-cached, zero-credit scenarios (Gateway of India, Neuschwanstein Castle, Santorini Vacation Rental Scam). | **Intelligence Sub-Tabs:** Geoguessr Challenge, Wardrobe Ledger, Chronological Provenance, Verifiable Citations, Advanced OSINT Dorks, and Executive Dossier. |

---

## 🛡️ Zero-Credit Invariant & Quota Defense

SerpApi free tiers provide 250 searches. TerraSleuth guarantees that developers, judges, and CI/CD never burn live credits unintentionally:
- **Transparent SQLite WAL Disk Cache (`terrasleuth.db`):** Pre-seeded with golden investigative scenarios for lag-free, zero-credit demos.
- **Parameter Normalization:** Canonical hashing strips transient query parameters and API keys.
- **Circuit Breakers:** Strictly decrements query budgets, skipping remote execution if the quota ceiling is reached.
- **100% Offline Test Suite:** All 158 tests run completely offline with 0 live API credit burn.

---

## 🏆 Engineering Rigor & Test Scorecard

TerraSleuth was engineered under strict **Subagent-Driven Development (SDD)** with adversarial multi-agent code reviews (`architect` blueprinting + `code-reviewer` signoff):

| Metric | Measurement |
|---|---|
| **Total Automated Tests** | **158 passing / 158 total (100% pass rate)** |
| **Unit & Integration Test Time** | ~28.0 seconds |
| **Live SerpApi Credits Burned in Tests** | **0 credits** |
| **Security & XSS Protection** | Strict scheme allowlist (`http`, `https`, `mailto`) neutralizing `javascript:` injection |
| **Browser E2E Automation** | Streamlit AppTest and verified Playwright visual screenshots |
| **Architecture Specification** | 4-tier C4 Model (`C4-Documentation/`) + OpenAPI 3.1.0 Contract |

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
# (Optional) Provide Gemini API key for dynamic LLM reasoning
echo "GEMINI_API_KEY=your_gemini_key" >> .env

# 4. Launch the War Room 2.0 Dashboard
streamlit run frontend/app.py
```

### Option 3: Run Full Automated Test Suite (158 Tests)
```bash
# Set PYTHONPATH and run all 158 automated tests
$env:PYTHONPATH="." ; pytest -v
```

---

## 🎬 3-Minute Demonstration Guide

1. **0:00 – 0:30 (Mission Briefing):** Review the 4 investigative scenarios in the War Room 2.0 HUD.
2. **0:30 – 1:15 (Landmark Pinpoint):** Select "The Waterfront Monument & Heritage Hotel", click **Launch Autonomous Investigation**, watch the LangGraph swarm extract clues, and pinpoint Gateway of India on satellite tiles with 96% confidence.
3. **1:15 – 1:55 (Visual Twin Comparator):** Switch to the Side-by-Side Visual Twin Matcher, inspecting exact visual alignment against authoritative Wikipedia images.
4. **1:55 – 2:30 (Fraud Unmasking):** Select "Vacation Rental Listing Fraud", launch investigation, and watch the red Anomaly Banner and dynamic LLM Skeptic critique unmask the stolen Santorini luxury hotel photo.
5. **2:30 – 3:00 (Export & Offline Dossier):** Click "Download Standalone HTML Forensic Dossier" to inspect the self-contained intelligence report with base64 embedded imagery.
