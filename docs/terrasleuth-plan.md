# TerraSleuth — Foundation Architecture & System Design Plan

> **Project:** TerraSleuth (Autonomous Multi-Modal Visual & Geospatial OSINT Detective)  
> **Hackathon:** SerpApi India Hackathon 2026 (AI Agents Track)  
> **Status:** Architecture Certified (Sprint 1)  
> **Author:** Architecture Lead & Project Partner

---

## 1. Executive Summary

**TerraSleuth** is an autonomous multi-modal investigative agent that solves real-world visual mysteries, geolocates uncaptioned photographs, and debunks viral visual misinformation using **SerpApi's visual and geospatial search engines**.

While standard AI agents operate in a purely textual vacuum—hallucinating coordinates and regurgitating stale training data—TerraSleuth operates like an elite **digital forensic investigator (OSINT)**:
1. **Multi-Modal Visual Deconstruction**: It breaks down an input image into atomic forensic clues: architectural styles, signage scripts (Devanagari, Cyrillic, Latin), driving side of vehicles, unique flora/climate, and landmark bounding crops.
2. **Visual Provenance & Twin Matching**: It queries **SerpApi's Google Lens API** to find exact matches across the open web, uncovering where and when the image first surfaced.
3. **Geospatial Triangulation**: It passes identified business names, street intersections, and landmark combinations into **SerpApi's Google Maps & Local API**, resolving precise latitude/longitude coordinates and street addresses.
4. **Chronological Verification**: It cross-references the location and entities against **Google News & Search APIs** to verify if reported events, weather, or protests actually match the photo's timestamp.
5. **Interactive Evidence Dossier**: It compiles an interactive case file featuring an **annotated visual evidence board**, a **live interactive map pinpoint**, a **chronological timeline**, and **verifiable source citations**.

---

## 2. Competitive Edge & Hackathon Alignment

In our analysis of the 185 community projects on `#BuiltWithSerpApi`:
- **111 projects** relied on standard Google Web Search (text in $\to$ text out).
- **Only 16 projects** used Images, and **only 1 project** touched Google Lens.
- **Zero projects** combined **Google Lens + Google Maps + Google News** into an autonomous investigative swarm.
- **TerraSleuth's Edge:** It directly showcases SerpApi's underutilized, high-value visual and spatial endpoints, producing an interactive, cinematic 3-minute demo that stands in a league of its own for the AI Agents track.

---

## 3. Multi-Agent OSINT Swarm Architecture

```
                                ┌───────────────────────────────┐
                                │   Input Mystery Image / URL   │
                                └───────────────┬───────────────┘
                                                │
                                                ▼
                                ┌───────────────────────────────┐
                                │ Visual Scene Deconstructor    │
                                │ (Architectural, Script, Crops)│
                                └───────────────┬───────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
        ┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
        │   Lens Hunter    │           │ Geo Triangulator │           │  Chrono Auditor  │
        │(SerpApi Google   │           │ (SerpApi Google  │           │ (SerpApi Google  │
        │     Lens)        │           │   Maps/Local)    │           │   News/Search)   │
        └────────┬─────────┘           └────────┬─────────┘           └────────┬─────────┘
                 └──────────────────────────────┼──────────────────────────────┘
                                                ▼
                                ┌───────────────────────────────┐
                                │ Lead Detective & Tie-Breaker  │◄──┐
                                │ (Dialectical Hypothesis Pruner│   │ Disambiguation Refinement
                                └───────────────┬───────────────┘   │ (Max 2 hops)
                                                │───────────────────┘
                                                ▼
                                ┌───────────────────────────────┐
                                │ Interactive Case Dossier      │
                                └───────────────┬───────────────┘
                                                │
                        ┌───────────────────────┼───────────────────────┐
                        ▼                       ▼                       ▼
               ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
               │ Visual Evidence│      │ Leaflet / Folium│      │ Clickable SERP │
               │     Board      │      │ Geo Pinpoint   │      │ Citation Ledger│
               └────────────────┘      └────────────────┘      └────────────────┘
```

---

## 4. Multi-Engine SerpApi Integration Strategy

| SerpApi Engine | Role in OSINT Investigation | Key Extracted Fields |
|---|---|---|
| **Google Lens API** | Reverse-image provenance, exact web matches, visual bounding box object matching. | `visual_matches`, `source_url`, `title`, `thumbnail`, `first_detected_date` |
| **Google Maps / Local API** | Pinpoints exact geographic coordinates, verifies business names, retrieves street addresses and user photos. | `place_results.gps_coordinates`, `address`, `title`, `reviews`, `photos` |
| **Google News API** | Reconstructs the timeline of events at the candidate location to verify breaking news vs. recycled imagery. | `news_results.date`, `source`, `snippet`, `title` |
| **Google Organic Search** | Entity lookup, verifying regional language scripts, municipal records, weather on specific dates. | `knowledge_graph`, `organic_results`, `snippet` |

---

## 5. LangGraph State Schema Design

```python
class VisualClue(TypedDict):
    category: str        # 'architecture', 'signage', 'vegetation', 'infrastructure', 'landmark'
    description: str     # 'Gothic arched spire with copper patina'
    confidence: float   # 0.0 - 1.0
    bounding_box: Optional[List[int]]  # [ymin, xmin, ymax, xmax]

class GeoCandidate(TypedDict):
    name: str            # 'St. Michael's Church'
    address: str         # 'Rathausplatz 2, Vienna, Austria'
    latitude: float      # 48.2082
    longitude: float     # 16.3738
    match_score: float   # 0.0 - 1.0
    evidence_snippet: str
    source_url: str

class OsintState(TypedDict):
    # Input
    image_path: str
    image_url: Optional[str]
    context_hint: Optional[str]
    
    # Visual Extraction
    visual_clues: List[VisualClue]
    crops_to_search: List[str]
    
    # SerpApi Intelligence
    lens_matches: List[Dict[str, Any]]
    geo_candidates: List[GeoCandidate]
    chrono_reports: List[Dict[str, Any]]
    serp_queries_executed: List[Dict[str, Any]]
    budget_remaining: int
    refinement_hops: int
    
    # Final Verdict
    resolved_location: Optional[GeoCandidate]
    incident_timeline: List[Dict[str, Any]]
    confidence_score: float
    case_summary_markdown: str
    citations: List[Dict[str, str]]
```

---

## 6. Quota Defense & Caching Architecture

To preserve SerpApi credits during active development and UI fine-tuning:
- **`cache_service.py`**: Intercepts all calls to Google Lens, Google Maps, Google News, and Search.
- Stores query parameters and raw JSON payloads in a local SQLite database (`terrasleuth.db`).
- **Golden Mystery Profiles**:
  1. *The Uncaptioned Architectural Mystery* (locates a distinctive historic landmark from background clues).
  2. *The Recycled Disaster Photo* (unmasks a viral "breaking news" flood photo as a 2021 event using Lens timeline).
  3. *The Marketplace Rental Scam* (proves a luxury apartment photo was stolen from a luxury hotel in another country).
- Pre-cached Golden targets guarantee instant, lag-free execution for the <3 minute judging video demo.
