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
    - `intent: Optional[InvestigationIntent]`
    - `detected_objects: Annotated[List[DetectedObject], merge_lists]`
    - `itemized_dossier: Annotated[List[Dict[str, Any]], merge_lists]`
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
    - `api_key: Optional[str]`
    - `force_refresh: bool`
    - `status: str`
    - `error: Optional[str]`
    - `final_case_file: Optional[CaseFile]`
- **Function:** `merge_lists(a: List[Any], b: List[Any]) -> List[Any]`
  - Reducer for deduplicating state dictionaries and string lists across hops.
- **Function:** `create_initial_osint_state(...) -> OsintGraphState`
  - Instantiates initial state with configured budgets, credentials, and empty evidence buffers.

### 2.2 `tools.py`
- **Context Isolation & Configuration:**
  - `configure_serpapi_client(api_key: Optional[str] = None, force_refresh: bool = False) -> SerpApiService`: Binds a session-isolated client to the calling thread/ContextVar.
  - `reset_serpapi_client_context() -> None`: Cleans context var on task completion.
  - `get_current_serpapi_client() -> SerpApiService`: Retrieves context-isolated client or fallback.
- **Function:** `@tool tool_lens_search(image_url: Optional[str] = None, image_path: Optional[str] = None, crop_bbox: Optional[List[float]] = None) -> Dict[str, Any]`
  - Reverse visual search supporting remote URLs, local binary uploads, and regional bounding-box crops wrapped in CacheService zero-quota protection.
- **Function:** `@tool tool_maps_triangulate(query: str, lat_hint: Optional[float] = None, lon_hint: Optional[float] = None) -> Dict[str, Any]`
  - Spatial coordinates and local place details via Google Maps.
- **Function:** `@tool tool_news_audit(query: str, date_filter: Optional[str] = None) -> Dict[str, Any]`
  - Publication milestones and temporal records via Google News.
- **Function:** `@tool tool_google_dork(dork_query: str) -> Dict[str, Any]`
  - OSINT search dork execution via Google Search.
- **Function:** `@tool tool_crop_region(image_path: str, bbox: List[float], label: str = "crop") -> str`
  - Crops normalized bounding boxes and returns disk path.

### 2.3 `graph.py`
- **Function:** `create_osint_graph() -> CompiledStateGraph`
  - Assembles sequential investigative StateGraph (Level 3).
- **Function:** `create_dialectical_osint_graph() -> CompiledStateGraph`
  - Assembles Level 5 Hunter ⇄ Skeptic ⇄ Arbiter debate loop with dynamic intent branching (`fashion_hunter_node`) and circuit breakers.
- **Function:** `route_after_hunter(state: OsintGraphState) -> str`
  - Adaptive intent router: routes to `"fashion_hunter"` if `intent == InvestigationIntent.FASHION_PRODUCT`; otherwise routes to `"skeptic"`.
- **Function:** `should_audit_or_synthesize(state: OsintGraphState) -> str`
- **Function:** `should_refine_or_synthesize(state: OsintGraphState) -> str`
- **Function:** `should_refine_debate(state: OsintGraphState) -> str`
  - Evaluates audit score, fraud status, and fashion completion: immediately routes to synthesizer if `status == "fashion_analysis_completed"`, `fraud_unmasked`, or score >= 0.70.
- **Function:** `investigate_image(...) -> CaseFile`
- **Function:** `investigate_image_dialectical(...) -> CaseFile`
- **Function:** `stream_osint_investigation_sync(...) -> Generator[Dict[str, Any], None, None]`
- **Function:** `stream_dialectical_investigation_sync(...) -> Generator[Dict[str, Any], None, None]`

---

## 3. Dependencies
- **Internal:** `backend.app.agent.nodes.*`, `backend.app.models.case.*`, `backend.app.services.*`
- **External:** `langgraph`, `langchain_core.tools`, `pydantic`, `logging`
