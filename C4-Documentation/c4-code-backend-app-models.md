# C4 Code-Level Documentation: `backend/app/models`

## 1. Overview
- **Name:** TerraSleuth Domain & Evidence Schemas
- **Description:** Pydantic models governing investigative evidence, SerpApi response normalization, fraud anomaly reports, OSINT dorks, Geoguessr scoring, and ReAct agent thoughts.
- **Location:** [`backend/app/models`](file:///d:/SerpAPI_hackathon/backend/app/models)
- **Language:** Python 3.11+
- **Purpose:** Strict typing and runtime schema validation ensuring zero hallucinations and deterministic cross-component data transfer.

---

## 2. Code Elements

### 2.1 `case.py` (Forensic Case Schema)
- **Class:** `ClueCategory(str, Enum)`: `ARCHITECTURE`, `SIGNAGE`, `VEGETATION`, `VEHICLE`, `INFRASTRUCTURE`, `LANDMARK`, `ANOMALY`.
- **Class:** `VisualClue(BaseModel)`
  - `category: ClueCategory`
  - `description: str`
  - `bounding_box: Optional[List[float]]` (normalized `[ymin, xmin, ymax, xmax]` in `[0.0, 1.0]`)
  - `confidence: float` (`0.0 <= c <= 1.0`)
  - `suggested_query: Optional[str]`
- **Class:** `GeoCandidate(BaseModel)`
  - `name: str`
  - `address: Optional[str]`
  - `latitude: float`, `longitude: float`
  - `place_id: Optional[str]`
  - `match_score: float` (`0.0 <= s <= 1.0`)
  - `engine_source: str` (`google_maps`, `google_lens`)
  - `evidence_snippet: Optional[str]`
  - `source_url: Optional[str]`
- **Class:** `TimelineEvent(BaseModel)`
  - `date: str`, `title: str`, `source: str`, `url: Optional[str]`, `snippet: str`, `is_origin: bool`
- **Class:** `Citation(BaseModel)`
  - `title: str`, `url: str`, `engine: str`, `snippet: str`
- **Class:** `CaseFile(BaseModel)`
  - `case_id: str`, `title: str`, `case_summary: str`, `confidence_score: float`
  - `intent: Optional[str]` (`FASHION_PRODUCT`, `GEOSPATIAL_LANDMARK`, etc.)
  - `resolved_location: Optional[GeoCandidate]`
  - `itemized_dossier: List[dict]` (Wardrobe and product items decomposed with bounding boxes, match titles, retailer sources, and retail URLs)
  - `visual_clues: List[VisualClue]`, `lens_matches: List[dict]`, `timeline: List[TimelineEvent]`, `citations: List[Citation]`
  - `anomalies: List[dict]`, `dorks: List[dict]`, `refinement_hops: int`, `serp_queries_executed: int`
  - `adversarial_audit_score: Optional[float]`

- **Class:** `InvestigationIntent(str, Enum)` (in `backend.app.agent.state`)
  - `GEOSPATIAL_LANDMARK`, `FASHION_PRODUCT`, `FRAUD_DISINFORMATION`, `GENERAL_OBJECT`

- **Class:** `DetectedObject(BaseModel)` (in `backend.app.agent.state`)
  - `label: str`, `category: str`, `bounding_box: List[float]`, `confidence: float`, `lens_match: Optional[dict]`

### 2.2 `serp.py` (SerpApi Response Normalization)
- **Class:** `LensMatch(BaseModel)`: `title: str`, `link: str`, `source: str`, `thumbnail: Optional[str]`, `score: Optional[int]`, `is_exact: bool`
- **Class:** `LensVisualMatchesResult(BaseModel)`: `visual_matches: List[LensMatch]`, `exact_matches: List[LensMatch]`, `knowledge_graph: Optional[Dict[str, Any]]`
- **Class:** `MapsCandidate(BaseModel)`: `place_id: Optional[str]`, `title: str`, `address: Optional[str]`, `latitude: Optional[float]`, `longitude: Optional[float]`, `rating: Optional[float]`, `reviews_count: Optional[int]`
- **Class:** `MapsSearchResult(BaseModel)`: `candidates: List[MapsCandidate]`, `search_query: str`, `total_results: int`
- **Class:** `NewsItem(BaseModel)`: `title: str`, `link: str`, `source: str`, `date: str`, `snippet: Optional[str]`
- **Class:** `NewsSearchResult(BaseModel)`: `items: List[NewsItem]`, `search_query: str`
- **Class:** `OrganicResult(BaseModel)`: `title: str`, `link: str`, `snippet: Optional[str]`, `position: int`
- **Class:** `GoogleSearchResult(BaseModel)`: `organic_results: List[OrganicResult]`, `knowledge_graph: Optional[Dict[str, Any]]`

### 2.3 `anomaly.py` (Fraud & Contradiction Reports)
- **Class:** `AnomalyType(str, Enum)`: `FRAUDULENT_LISTING`, `RECIRCULATED_MEDIA`, `LOCATION_CONTRADICTION`, `METADATA_MISMATCH`
- **Class:** `AnomalySeverity(str, Enum)`: `CRITICAL`, `WARNING`, `INFO`
- **Class:** `AnomalyReport(BaseModel)`: `anomaly_type: AnomalyType`, `severity: AnomalySeverity`, `title: str`, `description: str`, `claimed_context: Optional[str]`, `authoritative_truth: str`, `confidence: float`, `evidence_url: Optional[str]`

### 2.4 `dork.py` (Advanced Google Dorks)
- **Class:** `OsintDork(BaseModel)`: `category: str`, `query: str`, `explanation: str`, `search_url: str`

### 2.5 `geoguessr.py` (Spatial Evaluation & Scoring)
- **Class:** `TighteningStage(BaseModel)`: `stage_num: int`, `name: str`, `radius_km: float`, `description: str`, `clues_resolved: str`
- **Class:** `GeoguessrResult(BaseModel)`: `distance_km: float`, `distance_meters: float`, `score: int`, `max_score: int = 5000`, `accuracy_tier: str`, `verdict: str`, `tightening_stages: List[TighteningStage]`

### 2.6 `react.py` (ReAct Reasoning Schemas)
- **Class:** `ReActStepType(str, Enum)`: `THOUGHT`, `ACTION`, `OBSERVATION`, `SYNTHESIS`
- **Class:** `AgentThought(BaseModel)`: `step_type: ReActStepType`, `agent_role: str`, `thought: str`, `decision: str`, `tool_call: Optional[str]`, `tool_args: Optional[Dict[str, Any]]`, `observation: Optional[str]`
  - **Method:** `to_terminal_str() -> str`: Formats monospace terminal log entry.

### 2.7 `llm.py` (LLM Semantic Disambiguation Schemas)
- **Class:** `SemanticDisambiguationResult(BaseModel)`: `intent: InvestigationIntent`, `primary_entity: str`, `target_query: str`, `reasoning: str`, `confidence: float = 0.9`

### 2.8 `llm_agent.py` (Dynamic Agent Decision Schemas)
- **Class:** `SkepticEvaluationResult(BaseModel)`: `critique: str`, `fraud_probability: float = 0.0`, `is_fraud: bool = False`, `reasoning: Optional[str] = None`
- **Class:** `ArbiterEvaluationResult(BaseModel)`: `adversarial_audit_score: float`, `verdict: str`, `reasoning: str`

---

## 3. Dependencies
- **Internal:** `backend.app.agent.state.InvestigationIntent`
- **External:** `pydantic` (v2), `enum`, `typing`, `time`
