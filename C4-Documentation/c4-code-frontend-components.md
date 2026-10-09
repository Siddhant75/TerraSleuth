# C4 Code-Level Documentation: `frontend/components`

## 1. Overview
- **Name:** TerraSleuth Interactive Visual OSINT Components
- **Description:** Modular UI components built for Streamlit, Folium, and custom HTML/CSS, providing tactical split-screen surveillance, Leaflet/Esri satellite pinpointing, side-by-side visual twin comparison, live monospace swarm telemetry, Geoguessr gamification, and standalone offline HTML dossier exporting.
- **Location:** [`frontend/components`](file:///d:/SerpAPI_hackathon/frontend/components)
- **Language:** Python 3.11+, HTML5, CSS3, JavaScript (Folium/Leaflet)
- **Purpose:** Renders the heroic OSINT War Room 2.0 interface with rich visual evidence overlays and zero XSS vulnerabilities.

---

## 2. Code Elements

### 2.1 `tactical_command_deck.py` (Master 45/55 Split-Screen Command Deck)
The primary operational container coordinating all evidence sub-views.

- **Function:** `render_tactical_command_deck(case_file: CaseFile, config: Dict[str, Any], ground_truth_lat: Optional[float] = None, ground_truth_lon: Optional[float] = None) -> None`
  - Wraps the deck in a `.neon-pulse` obsidian container (`#0b0e17`).
  - Renders top 5-badge telemetry ribbon: Target Entity, WGS84 Coordinates, Confidence, SerpApi Queries Executed, Zero-Credit Cache Status. Adapts to `👗 WARDROBE CATALOG` when fashion intent is detected.
  - Renders 1-Click Action Bar: "📥 Export Offline HTML Dossier" and "🔄 New Investigation".
  - Orchestrates 45/55 split-screen columns:
    - **Left Column (45%):** Visual Forensic Inspector with bounding boxes (`render_visual_evidence_board`) and Side-by-Side Visual Twin Matcher (`render_visual_twin_comparator`) stacked below.
    - **Right Column (55%):** Esri Satellite Recon Map (`render_geo_map`), Consensus Address Banner, Itemized Wardrobe Ledger (`render_itemized_wardrobe_ledger`), Live Monospace Swarm Telemetry Terminal (`render_swarm_telemetry_terminal`), and intelligence tabs (`🎯 Geoguessr Mode`, `👗 Wardrobe Ledger`, `⏱️ Chronology`, `🔗 Citations`, `🔍 OSINT Dorks`, `📄 Executive Dossier`).
- **Function:** `render_itemized_wardrobe_ledger(dossier_items: List[Dict[str, Any]]) -> None`
  - Renders multi-item wardrobe catalog cards with category badges, match titles, retailer sources, confidence percentages, and retail URLs.

### 2.2 `war_room_hud.py` (War Room Header, Mission Briefings & Alert Banners)
Provides tactical headers, mission briefing selector cards, and glowing alert banners.

- **Functions:**
  - `render_war_room_header() -> None`: Renders tactical top status header with blinking surveillance indicator.
  - `render_mission_briefing_cards(golden_cases: List[Dict[str, Any]]) -> Optional[str]`: Renders 3 interactive target briefing cards with 1-click select buttons.
  - `render_anomaly_alert(anomalies: List[Dict[str, Any]]) -> None`: Renders neon crimson/amber alert boxes highlighting fraud (e.g., rental scam) or disinformation.
  - `render_osint_dorks(dorks: List[Dict[str, Any]]) -> None`: Renders clickable Google Search OSINT dork cards.

### 2.3 `geo_map.py` (Tactical Geospatial Folium & Esri Satellite Map)
Interactive Leaflet/Folium geospatial map supporting Dark Matter and Satellite Recon tiles.

- **Functions:**
  - `create_folium_map(candidate: Optional[GeoCandidate], map_layer: str = "satellite") -> folium.Map`:
    Constructs a Leaflet map with CartoDB Dark Matter or Esri World Imagery tiles, glowing cyan crosshairs, and consensus accuracy circles (`folium.Circle`).
  - `render_geo_map(candidate: Optional[GeoCandidate], map_height: int = 420) -> None`:
    Embeds Folium map inside Streamlit using `folium_static`.
  - `render_telemetry_bar_html(candidate: Optional[GeoCandidate], confidence: float, queries_count: int = 0) -> str`:
    Generates non-truncating flexbox telemetry badge HTML.

### 2.4 `visual_evidence_board.py` (Forensic Bounding Box Overlay)
Renders suspect photograph overlaid with color-coded bounding boxes and forensic clue cards.

- **Functions:**
  - `draw_bounding_boxes(image: Image.Image, clues: List[Any]) -> Image.Image`:
    Draws PIL color-coded bounding box rectangles with labeled badge tags across architecture, signage, vegetation, and fashion categories (`apparel` `#a855f7`, `accessory` `#3b82f6`, `footwear` `#f97316`, `jewelry` `#eab308`).
  - `render_visual_evidence_board(image: Image.Image, visual_clues: List[Any]) -> None`:
    Displays annotated image and expandable forensic clue cards with category pills.

### 2.5 `visual_twin_comparator.py` (Side-by-Side Visual Matcher)
Places suspect image side-by-side with the top authoritative Google Lens match retrieved via SerpApi.

- **Functions:**
  - `calculate_correspondence_score(rank: int, total: int = 10) -> float`: Computes rank-decay match percentage.
  - `extract_visual_twin_metadata(match: Dict[str, Any]) -> Dict[str, Any]`: Defensively parses title, domain, link, and thumbnail URL.
  - `render_visual_twin_comparator(suspect_image: Any, lens_matches: List[Dict[str, Any]], primary_match: Optional[Dict[str, Any]] = None) -> None`:
    Renders 50/50 comparison pane with correspondence score pill and provenance URL.

### 2.6 `chronology_timeline.py` (Temporal Provenance & Disinformation Ledger)
Visualizes historical discovery vs viral circulation events.

- **Function:** `render_chronology_timeline(events: List[TimelineEvent]) -> None`
  - Renders interactive vertical timeline with emerald badges for origin publications and cyan badges for syndication.

### 2.7 `citation_ledger.py` (Verifiable Evidence Ledger)
Tabulates external citations providing provenance for all claims.

- **Function:** `render_citation_ledger(citations: List[Citation]) -> None`
  - Renders verified citation table linking directly to Google Lens matches, Google Maps places, and Google News articles with XSS sanitization.

### 2.8 `geoguessr_view.py` (Gamified Spatial Accuracy Scorecard)
Visualizes competitive Geoguessr performance.

- **Function:** `render_geoguessr_challenge_view(result: GeoguessrResult, candidate_name: str, ground_truth_name: str) -> None`
  - Renders 5,000-point score meter, distance error in meters/km, accuracy tier badge, and 4-phase tightening stage progression.

### 2.9 `swarm_telemetry_terminal.py` (Live Monospace OSINT Terminal)
Renders glass-box agent thought processes in real time.

- **Functions:**
  - `format_terminal_log_entry(step_name: str, message: str, agent_role: Optional[str] = None) -> Dict[str, str]`
  - `generate_swarm_terminal_html(logs: List[Dict[str, str]]) -> str`: Generates high-contrast monospace terminal HTML (`#090d16` background) with colored role tags (`[HUNTER]`, `[SKEPTIC]`, `[ARBITER]`).
  - `render_swarm_telemetry_terminal(logs: List[Dict[str, str]], height: int = 260) -> None`

### 2.10 `dossier_exporter.py` (Standalone Offline HTML Dossier Generator)
Generates self-contained, zero-dependency offline investigative reports.

- **Functions:**
  - `sanitize_url(url: Optional[str]) -> str`: Enforces safe HTTP/HTTPS URL protocols.
  - `image_to_base64_data_uri(img: Optional[Image.Image]) -> Optional[str]`: Embeds suspect image as Base64 JPEG data URI.
  - `generate_standalone_html_dossier(case_file: CaseFile, target_image: Optional[Image.Image] = None) -> str`:
    Compiles complete HTML document containing embedded styles, telemetry ribbon, Itemized Wardrobe & Product Forensic Ledger table (if fashion target), forensic anomalies, visual twin comparison, Red-Team audit badge, citation chain, and print stylesheets.

### 2.11 `blueprint_views.py` (Blueprint Audit & Milestone Views)
Renders supplementary architectural critique and release roadmap views for hackathon judges.

- **Functions:**
  - `render_screenshot_critique_view() -> None`: Displays initial UI flaws and remediation cards.
  - `render_serpapi_features_view() -> None`: Renders multi-engine coverage table and feature highlights.
  - `render_implementation_roadmap_view() -> None`: Renders release milestone cards (Sprints 1 through 8).

---

## 3. Dependencies
- **Internal:**
  - `backend.app.models.case`
  - `backend.app.models.geoguessr`
  - `backend.app.services.geoguessr_service`
- **External:**
  - `streamlit`
  - `folium`, `streamlit_folium`
  - `PIL`
  - `html`, `base64`, `io`
