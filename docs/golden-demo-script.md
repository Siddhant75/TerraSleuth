# TerraSleuth — Official Demonstration Video & Walkthrough Script (< 3 Minutes)

> **Official Demo Video:** [https://youtu.be/OuB36Ju8StM](https://youtu.be/OuB36Ju8StM) (Runtime: 2m 16s @ 1080p 60fps)  
> **Track:** SerpApi India Hackathon 2026 (AI Agents Track)  
> **Core Stack:** LangChain, LangGraph, SerpApi (Lens, Maps, News, Search), Google AI Studio (Gemini 1.5 Flash), Streamlit, Folium  

---

## 🎬 Video Overview & Two-Act Narrative Structure

The official demonstration video is structured into two distinct, high-impact acts that prove TerraSleuth's autonomous multi-modal investigative power across real-world OSINT challenges:

---

### 🏛️ Act 1: Mystery Landmark Pinpoint & Gemini LLM Forensic Briefing (0:00 – 1:05)

- **Target Scenario:** High-resolution uncaptioned architectural photo (`test1..jpeg` — Vancouver Lookout / Harbour Centre).
- **Interactive Detective Directive:** Main-canvas directive instructing the vision ensemble to extract prominent urban structures and architectural elements.
- **Visual Flow & Execution:**
  1. **Main Canvas Directive Input:** Shows user configuring directives and launching the LangGraph multi-agent swarm.
  2. **Real-Time Telemetry Terminal:** Monospace cyber terminal streams live agent steps (`[HUNTER]`, `[SKEPTIC]`, `[ARBITER]`, `[SYNTHESIZER]`).
  3. **Prominent Gemini 1.5 Flash Forensic Intelligence Briefing:** Renders executive case summary, architectural analysis, and evidentiary deductions.
  4. **45/55 Split-Screen Command Deck:** Visual Inspector highlights bounding boxes; Folium satellite map pinpoints exact coordinates down to the street level with tight accuracy circles.
  5. **Verifiable Citation Ledger:** Full provenance chain backed by clickable Google Lens visual matches, Google Maps place IDs, and historical news archives.
- **Voiceover / Narration:**
  > *"Every day, human investigators and journalists encounter mystery images—uncaptioned photos, viral claims, or marketplace scam listings. Standard LLMs hallucinate locations when given an image.  
  > Meet TerraSleuth: an autonomous multi-modal OSINT detective powered by LangGraph, SerpApi, and Google Gemini that forensic-analyzes mystery photos, triangulates physical coordinates, and audits publication timelines with zero hallucinations.  
  > Watch the LangGraph state machine execute in real-time. In seconds, Gemini 1.5 Flash generates an executive forensic briefing, while SerpApi Google Lens and Maps triangulate the exact landmark down to the street level with zero hallucinations."*

---

### 🚨 Act 2: Santorini Vacation Rental Listing Fraud Unmasked & Autonomous Geoguessr (1:05 – 2:16)

- **Target Scenario:** Flagship fraud benchmark — Stolen luxury villa listing claimed as "Miami Beachfront Penthouse" ($4,500/night).
- **Suspect Story Context:** Listing owner claims the apartment is located in Miami Beach, FL.
- **Visual Flow & Execution:**
  1. **Dialectical Swarm Cross-Examination (Skeptic Node):** Gemini 1.5 Flash debunker cross-examines the suspect story against SerpApi evidence, detecting Cycladic whitewashed volcanic cliffside architecture native to Santorini, Greece.
  2. **Fraud Unmasked & Arbiter Penalty:** Skeptic issues a 95% fraud probability; Arbiter penalizes credibility down to 35% with an immediate `[🚨 FRAUD DETECTED]` warning.
  3. **Visual Twin Matcher:** Side-by-side comparison reveals the exact stolen photo matched to *Canaves Oia Suites in Santorini, Greece* via SerpApi Google Lens.
  4. **Autonomous Geoguessr Challenge:** TerraSleuth calculates an exponential decay score of **4,975 / 5,000 points** across 4-phase progressive spatial radius tightening.
  5. **Standalone Court-Ready HTML Dossier:** One-click download of the complete offline, self-contained forensic dossier with Base64 embedded imagery and sanitized citations.
- **Voiceover / Narration:**
  > *"Next, we test TerraSleuth against a sophisticated real-world rental scam: a luxury listing claiming to be a beachfront penthouse in Miami Beach.  
  > Watch our Level 5 Dialectical Swarm in action. The Skeptic Agent cross-examines the suspect's claim against live SerpApi records, deducing that the architecture belongs to the Cycladic cliffs of Greece.  
  > The Arbiter slashes credibility to 35%, unmasking the fraud. Our Visual Twin Matcher catches the exact match to a luxury resort in Santorini, while our Geoguessr engine scores 4,975 out of 5,000 points.  
  > Finally, investigators can export a complete, court-ready standalone HTML dossier with a single click.  
  > TerraSleuth: Autonomous visual intelligence with verifiable real-world provenance."*

---

## 🏆 Key Capabilities Demonstrated

1. **Multi-Engine SerpApi Synergy:** Google Lens (image upload & visual matches), Google Maps (spatial coordinate triangulation), Google News (historical timeline audit), and targeted Google Search Dorks.
2. **Hybrid Vision Ensemble:** Google AI Studio Gemini 1.5 Flash Vision bounding box spatial reasoning + local OpenCV contour detection.
3. **Dialectical Multi-Agent Swarm (LangGraph):** Hunter (candidate discovery), Skeptic (red-team cross-examination & fraud debunker), and Arbiter (consensus certification & continuous penalty scoring).
4. **Zero-Credit Cache Defense:** 100% reproducible offline benchmark execution via SQLite disk caching (`terrasleuth.db`), burning 0 live credits.
5. **Court-Ready Exportability:** Standalone offline HTML dossier with zero external script dependencies and strict XSS neutralization.
