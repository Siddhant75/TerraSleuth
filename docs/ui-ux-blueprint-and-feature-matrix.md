# TerraSleuth — UI/UX Redesign Blueprint & SerpApi Feature Matrix

> **Document Version:** v1.0.0 (Release v0.4+)  
> **Status:** Active Reference Architecture  
> **Interactive Companion:** [`docs/interactive-redesign-blueprint.html`](file:///d:/SerpAPI_hackathon/docs/interactive-redesign-blueprint.html)  
> **Related Specifications:** [`docs/terrasleuth-plan.md`](file:///d:/SerpAPI_hackathon/docs/terrasleuth-plan.md) | [`docs/terrasleuth-roadmap.md`](file:///d:/SerpAPI_hackathon/docs/terrasleuth-roadmap.md)

---

## 1. Executive Summary & Design Rationale

During the Sprint 3 release certification (`v0.3.0`), end-to-end browser audits conducted with Playwright revealed that while TerraSleuth's underlying multi-agent engine was functionally sound, the **User Experience (UX) and Visual Interface** fell short of the aesthetic and operational standard expected of a tier-1, hackathon-winning AI Agent product.

Standard Streamlit layouts (horizontal tab bars, basic `st.metric` cards, and static text boxes) broke the investigator's mental model:
- Viewing map coordinates forced users away from visual evidence.
- Numeric metrics truncated vital coordinates.
- Synthetic block diagrams destroyed visual forensic immersion.

This document formalizes the **Tactical Command Deck Redesign Blueprint**, synthesizes the **Screenshot Audit & Critique**, and establishes the **SerpApi Multi-Engine Feature Matrix** that guides the current and upcoming sprint implementations.

---

## 2. Screenshot Audit & Critique (Playwright Visual Evaluation)

A forensic review of the baseline UI screenshots (`tests/e2e/screenshots/`) identified five critical UX flaws:

| Flaw # | Observed Symptom | Root Cause | Operational Impact | Redesign Solution |
|---|---|---|---|---|
| **1** | **Synthetic Geometric Diagrams** | Pre-seeded target used tan/brown rectangle shapes (`target.jpg`). | Looked like an engineer's wireframe unit test, undermining forensic credibility for hackathon judges. | **Authentic Target Library:** High-resolution real photography (Apollo Bunder, Bavarian Alps, Aegean villa) in `frontend/assets/targets/`. |
| **2** | **Metric Value Truncation** | Coordinates rendered as `18.9220...` and names as `Gatewa...`. | Native `st.metric` cards in 5-column layouts do not accommodate long WGS84 decimal strings. | **Custom Flexbox Telemetry Bar:** Non-truncating HTML/CSS badges with monospace typography and full precision. |
| **3** | **Tab Fragmentation** | Map, visual clues, timeline, and citations isolated across 4 separate tabs. | Users could never cross-reference visual bounding clues with spatial map pins simultaneously. | **45/55 Split-Screen Command Deck:** Simultaneous left (visual inspector) and right (satellite map & intelligence) views. |
| **4** | **Daytime / Low-Res Cartography** | Default OpenStreetMap daytime tiles or watermarked tiles. | Clashed with dark forensic aesthetic and lacked military/reconnaissance fidelity. | **Esri World Imagery Satellite Recon:** High-resolution satellite tiles (zero watermarks) with glowing neon target crosshairs. |
| **5** | **Static Progress Alerts** | Plain green boxes: `✅ Scene Deconstructor — complete`. | Felt like a sequential Python batch script rather than an autonomous AI agent swarm. | **Monospace Cyber Swarm Terminal:** High-contrast terminal (`#090d16`) streaming live agent deductions in real time. |

---

## 3. Architectural Design Decisions (ADRs)

### ADR-004: Unified 45/55 Split-Screen Command Deck
- **Context:** An OSINT investigator cannot conduct visual analysis in isolation from geospatial maps.
- **Decision:** Split the main canvas into two synchronized operational decks:
  - **Left Deck (45%):** Visual Forensic Inspector (Authentic imagery, bounding box clue overlays, Side-by-Side Visual Twin Matcher).
  - **Right Deck (55%):** Tactical Map Deck (Esri Satellite Recon, consensus accuracy radius, Swarm Telemetry Terminal, intelligence sub-tabs).

### ADR-005: Authentic High-Resolution OSINT Target Library
- **Context:** Synthetic test shapes fail the "show, don't tell" test for hackathon evaluation.
- **Decision:** Seed the database and asset folder with 3 authentic photographic scenarios:
  1. *Target A (Landmark):* Gateway of India waterfront basalt arch & Apollo Bunder promenade.
  2. *Target B (Heritage):* Neuschwanstein Castle Bavarian alpine backdrop.
  3. *Target C (Fraud Exposer):* Uncaptioned vacation rental listing unmasked by Google Lens as a boutique resort in Santorini, Greece.

### ADR-006: Side-by-Side Visual Twin Matcher
- **Context:** Google Lens returns exact web matches, but showing only text links fails to communicate visual certainty.
- **Decision:** Implement a 50/50 comparison widget placing the mystery input photo beside the top Google Lens authoritative thumbnail, displaying visual correspondence score, domain provenance, and source links.

### ADR-007: Esri World Imagery Satellite Reconnaissance
- **Context:** Standard OSM daytime tiles clash with dark UI, while CartoCDN tiles now require API keys and superimpose watermarks.
- **Decision:** Transition to unwatermarked, high-resolution **Esri World Imagery** satellite tiles (`https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`) with pulsing neon crosshairs.

### ADR-008: Monospace Cyber Swarm Telemetry Terminal
- **Context:** Judges want proof that multi-agent orchestration is actually occurring in real time.
- **Decision:** Stream live deductions from each LangGraph node into an obsidian terminal container (`#090d16`) with timestamps, step tags, and agent reasoning.

---

## 4. SerpApi Multi-Engine Portfolio Feature Matrix

This matrix evaluates SerpApi's search engines against OSINT investigative workflows:

| SerpApi Engine | Role in TerraSleuth | OSINT Investigative Capability | Quota Boundary & Cache Strategy | Status in TerraSleuth |
|---|---|---|---|---|
| **`google_lens`** | **Visual Provenance Hunter** | Reverse image visual twins, Knowledge Graph entity extraction, OCR script detection, product matching. | 1 call per investigation; 100% pre-cached for Golden targets. | ✅ **Implemented** (Sprint 1, 2, 4) |
| **`google_maps` / Local** | **Geospatial Triangulator** | Resolves WGS84 lat/lon coordinates, place IDs, street addresses, business hours, and place consensus. | 1–2 calls per investigation; bounded by refinement circuit breaker. | ✅ **Implemented** (Sprint 1, 2, 4) |
| **`google_news`** | **Chrono Provenance Auditor** | Tracks earliest indexed appearance of media, detects recycled disaster imagery, builds temporal milestones. | 1 call per investigation; pre-cached for Golden targets. | ✅ **Implemented** (Sprint 1, 2, 4) |
| **`google` (search)** | **Advanced OSINT Dorker** | Executes targeted dorks (`site:`, `filetype:pdf`, `before:`, `after:`) for corporate filings, municipal records, or cached articles. | Optional fallback hop; bounded by query budget. | ✅ **Implemented** (Service ready; pending UI dork builder) |
| **`youtube`** | **Video Frame Provenance** | Analyzes viral conflict video keyframes and matches earliest YouTube upload timestamps. | 1–2 calls per video keyframe. | ⏳ **Backlog (Future Track)** |
| **`google_reverse_image`** | **Desktop Image Engine** | Cross-engine desktop reverse search for pages containing exact image dimensions. | 1 call fallback if Lens is ambiguous. | ⏳ **Backlog (Future Track)** |
| **`google_scholar` / Patents** | **Technical Artifact Verification** | Verifies specialized equipment, defense hardware, or industrial components in imagery. | Optional deep-research hop. | ⏳ **Backlog (Future Track)** |

---

## 5. OSINT Use Case Showcase (Judging Demonstrations)

### Scenario 1: Uncaptioned Landmark Triangulation (Apollo Bunder, Mumbai)
- **Challenge:** A user uploads a cropped, uncaptioned photo of an archway with maritime basalt structures.
- **Swarm Action:**
  - *Scene Deconstructor* identifies Indo-Saracenic basalt architecture and maritime waterfront.
  - *Lens Hunter* retrieves authoritative Wikipedia visual twins for "Gateway of India".
  - *Geo Triangulator* queries Google Maps and pinpoints `18.9220°N, 72.8347°E` (Apollo Bunder, Colaba).
  - *Chrono Auditor* retrieves 1924 inauguration history and modern restoration milestones.
- **Outcome:** Case closed with 96% confidence in <2 seconds.

### Scenario 2: Vacation Rental Fraud Unmasking (Santorini Luxury Villa Scam)
- **Challenge:** A rental listing advertises an exclusive beach property in Miami, Florida.
- **Swarm Action:**
  - *Lens Hunter* extracts visual matches and discovers identical room layouts on high-end hospitality sites in Oia, Santorini, Greece.
  - *Geo Triangulator* resolves true coordinates at `36.4618°N, 25.3753°E`.
  - *Case Synthesizer* flags discrepancy: listing location contradicts visual twin provenance.
- **Outcome:** Unmasks fraudulent listing with definitive evidence links.

### Scenario 3: Bellingcat Viral Media Recycled Disaster Debunker
- **Challenge:** Viral social media post claims a disaster photograph was taken during a breaking event yesterday.
- **Swarm Action:**
  - *Chrono Auditor* searches Google News and Google Search archives with temporal filters.
  - Identifies earliest indexed appearance dating back to 2021.
- **Outcome:** Automatically flags `[EARLIEST KNOWN APPEARANCE: 2021]` and debunks disinformation.

---

## 6. Implementation Traceability: Completed vs. Next To-Dos

| Feature / Blueprint Item | Planned Stage | Implemented In | Current Status |
|---|---|---|---|
| **Authentic Photographic Asset Library** | Sprint 4 | Task 4.1 (`fb61583`) | ✅ Certified in `v0.4.0` |
| **Unified 45/55 Split-Screen Command Deck** | Sprint 4 | Task 4.2 (`06195b1`) | ✅ Certified in `v0.4.0` |
| **Esri Satellite Reconnaissance Tiles** | Sprint 4 | Task 4.2 & 4.4 (`0b481a6`) | ✅ Certified in `v0.4.0` |
| **Side-by-Side Visual Twin Matcher** | Sprint 4 | Task 4.3 (`24c59a5`) | ✅ Certified in `v0.4.0` |
| **Monospace Cyber Swarm Telemetry Terminal** | Sprint 4 | Task 4.3 (`24c59a5`) | ✅ Certified in `v0.4.0` |
| **Zero-Truncation Flexbox Telemetry Badges** | Sprint 4 | Task 4.2 (`06195b1`) | ✅ Certified in `v0.4.0` |
| **Interactive HTML Redesign Prototype** | Planning | Artifact & Repo copy | ✅ Committed (`docs/interactive-redesign-blueprint.html`) |
| **Standalone Self-Contained HTML Dossier Exporter** | Sprint 5 | Task 5.1 | ⏳ **Next To-Do** |
| **Fraud Anomaly Alert Banner (Rental Scam Badge)** | Sprint 5 | Task 5.2 | ⏳ **Next To-Do** |
| **Docker Containerization (`Dockerfile` + compose)** | Sprint 5 | Task 5.3 | ⏳ **Next To-Do** |
| **Official Hackathon Submission Document** | Sprint 5 | Task 5.4 | ⏳ **Next To-Do** |
