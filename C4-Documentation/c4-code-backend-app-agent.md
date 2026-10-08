# C4 Code-Level Documentation: `backend/app/agent`

## 1. Overview
- **Name:** LangGraph Multi-Agent Orchestration & Tool Engine
- **Description:** Encapsulates the StateGraph definitions, typed multi-modal OSINT graph state, LangChain tool registry, and conditional execution routers for TerraSleuth.
- **Location:** [`backend/app/agent`](file:///d:/SerpAPI_hackathon/backend/app/agent)
- **Language:** Python 3.11+
- **Purpose:** Manages the stateful multi-agent execution pipeline, coordinating investigative nodes and dialectical debates with deterministic termination.

---

## 2. Code Elements

### 2.1 `state.py`
- **Class / Schema:** `OsintGraphState(TypedDict)`
  - **Location:** [`backend/app/agent/state.py#L29-L63`](file:///d:/SerpAPI_hackathon/backend/app/agent/state.py#L29-L63)
  - **Fields:**
    - `image_path: str`
    - `image_url: Optional[str]`
    - `context_hint: Optional[str]`
    - `visual_clues: Annotated[List[VisualClue], operator.add]`
    - `geo_candidates: Annotated[List[GeoCandidate], operator.add]`
    - `timeline_events: Annotated[List[TimelineEvent], operator.add]`
    - `lens_matches: Annotated[List[Dict[str, Any]], merge_lists]`
    - `citations: Annotated[List[Citation], operator.add]`
    - `hunter_hypotheses: Annotated[List[str], merge_lists]`
    - `skeptic_critiques: Annotated[List[str], merge_lists]`
    - `debate_history: Annotated[List[Dict[str, Any]], merge_lists]`
    - `audit_score: float`
    - `initial_budget: int`
    - `budget_remaining: int`
    - `refinement_hops: int`
    - `max_refinement_hops: int`
    - `status: str`
    - `error: Optional[str]`
    - `final_case_file: Optional[CaseFile]`
- **Function:** `merge_lists(a: List[Any], b: List[Any]) -> List[Any]`
  - Reducer for deduplicating state dictionaries and string lists across hops.
- **Function:** `create_initial_osint_state(...) -> OsintGraphState`
  - Instantiates initial state with configured budgets and empty evidence buffers.

### 2.2 `tools.py`
- **Function:** `@tool tool_lens_search(image_url: str, crop_bbox: Optional[List[float]] = None) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/tools.py#L18-L27`](file:///d:/SerpAPI_hackathon/backend/app/agent/tools.py#L18-L27)
  - Reverse visual search wrapped in CacheService zero-quota protection.
- **Function:** `@tool tool_maps_triangulate(query: str, lat_hint: Optional[float] = None, lon_hint: Optional[float] = None) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/tools.py#L30-L47`](file:///d:/SerpAPI_hackathon/backend/app/agent/tools.py#L30-L47)
  - Spatial coordinates and local place details via Google Maps.
- **Function:** `@tool tool_news_audit(query: str, date_filter: Optional[str] = None) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/tools.py#L50-L65`](file:///d:/SerpAPI_hackathon/backend/app/agent/tools.py#L50-L65)
  - Publication milestones and temporal records via Google News.
- **Function:** `@tool tool_google_dork(dork_query: str) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/tools.py#L68-L74`](file:///d:/SerpAPI_hackathon/backend/app/agent/tools.py#L68-L74)
  - OSINT search dork execution via Google Search.
- **Function:** `@tool tool_crop_region(image_path: str, bbox: List[float], label: str = "crop") -> str`
  - **Location:** [`backend/app/agent/tools.py#L77-L83`](file:///d:/SerpAPI_hackathon/backend/app/agent/tools.py#L77-L83)
  - Crops normalized bounding boxes and returns disk path.

### 2.3 `graph.py`
- **Function:** `create_osint_graph() -> CompiledStateGraph`
  - Assembles sequential investigative StateGraph (Level 3).
- **Function:** `create_dialectical_osint_graph() -> CompiledStateGraph`
  - Assembles Level 5 Hunter ⇄ Skeptic ⇄ Arbiter debate loop with circuit breakers.
- **Function:** `should_audit_or_synthesize(state: OsintGraphState) -> str`
- **Function:** `should_refine_or_synthesize(state: OsintGraphState) -> str`
- **Function:** `should_refine_debate(state: OsintGraphState) -> str`
  - Evaluates audit score and fraud status: immediately routes to synthesizer if `fraud_unmasked` or score >= 0.70.
- **Function:** `investigate_image(...) -> CaseFile`
- **Function:** `investigate_image_dialectical(...) -> CaseFile`
- **Function:** `stream_osint_investigation_sync(...) -> Generator[Dict[str, Any], None, None]`
- **Function:** `stream_dialectical_investigation_sync(...) -> Generator[Dict[str, Any], None, None]`

---

## 3. Dependencies
- **Internal:** `backend.app.agent.nodes.*`, `backend.app.models.case.*`, `backend.app.services.*`
- **External:** `langgraph`, `langchain_core.tools`, `pydantic`, `logging`
