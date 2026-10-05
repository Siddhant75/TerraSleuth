# TerraSleuth — Golden Demo Walkthrough Script (< 3 Minutes)

> **Goal:** High-impact, concise screen-recording walkthrough (< 180 seconds) demonstrating autonomous multi-modal visual & geospatial OSINT investigation for SerpApi India Hackathon 2026 (AI Agents Track).

---

## ⏱️ Video Timeline & Scene Breakdown

### 🎬 Scene 1: The OSINT Challenge (0:00 – 0:30)
- **Visual:** Open TerraSleuth Streamlit Web Dashboard (`http://localhost:8501`). Dark forensic theme.
- **Action:** Show the investigation target options in the sidebar:
  1. *Golden Mystery Target (Instant / Pre-Cached)*: Select **"Mystery Case #1: Uncaptioned Waterfront Monument"**.
  2. Point out the parameter controls: Query Budget (8 calls), Max Disambiguation Hops (2), Context hint.
  3. Show the active Quota & Telemetry meter demonstrating zero credit waste defense.
- **Voiceover / Narration:**
  > *"Every day, human investigators and journalists encounter mystery images—uncaptioned photos, viral claims, or marketplace scam listings. Standard LLMs hallucinate locations when given an image.  
  > Meet **TerraSleuth**: an autonomous multi-modal OSINT detective powered by LangGraph and SerpApi that forensic-analyzes mystery photos, triangulates physical coordinates, and audits publication timelines with zero hallucinations."*

---

### 🔍 Scene 2: Autonomous Multi-Modal Vision Deconstruction (0:30 – 1:15)
- **Visual:** Click **"🚀 Launch Autonomous Investigation"**.
- **Action:** Watch the live Agent Execution Swarm progress cards light up:
  - `🔍 Scene Deconstructor` extracts visual clues in real-time.
  - Switch to **Tab 2: 🔍 Forensic Visual Evidence Board**.
  - Show the original image dynamically overlaid with color-coded bounding boxes:
    - **Dodger Blue:** Indo-Saracenic basalt waterfront arch (Architecture - 96% confidence).
    - **Crimson Red:** Bilingual maritime harbor signage (Signage - 88% confidence).
    - **Sun Yellow:** Historic dome monument landmark (Landmark - 92% confidence).
- **Voiceover / Narration:**
  > *"The moment we launch, TerraSleuth's Scene Deconstructor decomposes the image into isolated forensic clues. Instead of guessing, it extracts architectural motifs, scripts, vegetation, and landmarks, binding them to normalized bounding coordinates ready for targeted reverse search."*

---

### 🌐 Scene 3: SerpApi Cross-Engine Triangulation (1:15 – 1:55)
- **Visual:** Step `🌐 Lens Hunter` and Step `📍 Geo Triangulator` complete.
- **Action:** Switch to **Tab 1: 🗺️ Triangulated Geospatial Pinpoint**.
  - Show the interactive Folium/Leaflet map centering directly on **Gateway of India, Colaba, Mumbai** (`18.92200° N, 72.83470° E`).
  - Hover over the red crosshair pinpoint and highlight the consensus accuracy radius circle (150m).
  - Point out the match confidence score badge (95%) and the one-click Google Maps verification link.
- **Voiceover / Narration:**
  > *"Next, the agent dispatches targeted visual queries to SerpApi Google Lens. Rather than relying on a single match, the Geo Triangulator takes the top visual twin candidates and queries SerpApi Google Maps and Local places.  
  > It computes spatial consensus and pinpoints exact GPS coordinates down to a 150-meter radius on an interactive map."*

---

### ⏱️ Scene 4: Chronological Audit & Citation Ledger (1:55 – 2:30)
- **Visual:** Step `⏱️ Chrono Auditor` and Step `📜 Lead Detective Synthesizer` complete.
- **Action:**
  - Switch to **Tab 3: ⏱️ Chronological Provenance & Media Timeline**:
    - Highlight the green `EARLIEST KNOWN APPEARANCE` badge (Apollo Bunder maritime commemoration, December 1911 / 1924 completion).
    - Show subsequent viral news and restoration milestones.
  - Switch to **Tab 4: 🔗 Verifiable Citation Ledger**:
    - Expand Google Lens, Google Maps, and Google News sections with clickable source URLs and extracted text snippets.
- **Voiceover / Narration:**
  > *"Is the image original or recycled? The Chrono Auditor queries SerpApi Google News to reconstruct the media timeline, pinpointing the earliest known appearance and provenance history.  
  > Finally, every forensic finding is logged in our Verifiable Citation Ledger—anchored directly to live search records so human analysts can audit every step of the chain of custody."*

---

### 🛡️ Scene 5: Quota Defense & Dialectical Architecture (2:30 – 3:00)
- **Visual:** Show terminal / architecture diagram / Case File download.
- **Action:**
  - Click **"📥 Download Forensic Dossier (Markdown)"** to show the generated case file.
  - Show the terminal logs displaying **SQLite Disk Cache hits** and `0 live SerpApi credits consumed`.
- **Voiceover / Narration:**
  > *"Under the hood, TerraSleuth runs a LangGraph state machine with automatic ambiguity tie-breakers and strict credit circuit breakers. Backed by our SQLite cache layer, pre-seeded cases run with zero API credit burn.  
  > TerraSleuth: Autonomous visual intelligence with verifiable real-world provenance. Thank you!"*
