# C4 Code-Level Documentation: `backend/app/services`

## 1. Overview
- **Name:** TerraSleuth Core Domain Services & SerpApi Integration Engine
- **Description:** Encapsulates external search API clients (Google Lens, Maps, News, Organic Search), SQLite quota-defense caching, multi-modal image cropping & deconstruction, investigative fraud detection, advanced OSINT dork generation, and Geoguessr spatial scoring.
- **Location:** [`backend/app/services`](file:///d:/SerpAPI_hackathon/backend/app/services)
- **Language:** Python 3.11+
- **Purpose:** Provides resilient, cached, and audited service layer abstractions powering both Level 4 ReAct tool execution and Level 5 multi-agent swarm deliberations.

---

## 2. Code Elements

### 2.1 `serpapi_service.py` (Unified Multi-Engine Client)
Unified wrapper for SerpApi with strict parameter sanitization, automatic SQLite disk caching, and circuit-breaker quota defense.

- **Exceptions:**
  - `SerpApiError(Exception)`: Base exception.
  - `SerpApiConfigError(SerpApiError)`: Raised when `SERPAPI_API_KEY` is missing or placeholder.
  - `SerpApiTimeoutError(SerpApiError)`: Raised on query timeout.
  - `SerpApiRateLimitError(SerpApiError)`: Raised on rate-limit / 429 status.

- **Class:** `SerpApiService`
  - **`__init__(self, api_key: Optional[str] = None, timeout_seconds: Optional[int] = None, client: Optional[httpx.Client] = None, cache_service: Optional[CacheService] = None, use_cache: bool = True, budget_manager: Optional[QuotaBudgetManager] = None)`**
    Initializes HTTP client, credentials, cache link, and quota budget manager.
  - **`close(self) -> None`**: Closes underlying `httpx.Client`.
  - **`upload_image(self, image_path: str, max_size_bytes: int = 500 * 1024) -> str`**:
    Uploads a local image file to SerpApi Image API (`POST https://serpapi.com/image`) to obtain an `image_id` for Google Lens. Performs iterative Pillow compression and resizing if the file exceeds 500 KB, caches the resulting `image_id` by SHA-256 hash in SQLite, and masks credentials in logs and exceptions (`from None`).
  - **`search_lens(self, image_url: Optional[str] = None, image_path: Optional[str] = None, image_id: Optional[str] = None, crop_bbox: Optional[List[float]] = None, hl: str = "en", force_refresh: bool = False) -> LensVisualMatchesResult`**:
    Executes visual reverse-image query via SerpApi Google Lens engine (`engine=google_lens`). Supports remote image URLs, local image uploads via `upload_image`, or cropped bounding boxes (`crop_bbox`) for targeted visual inspection of garments, accessories, or architectural signage.
  - **`search_maps(self, query: str, ll: Optional[str] = None, hl: str = "en", force_refresh: bool = False) -> MapsSearchResult`**:
    Queries Google Maps places and coordinates (`engine=google_maps`). Supports GPS bounding center (`ll`).
  - **`search_news(self, query: str, time_range: Optional[str] = None, gl: str = "us", hl: str = "en", force_refresh: bool = False) -> NewsSearchResult`**:
    Queries Google News engine (`engine=google_news`) for chronological timeline verification.
  - **`search_google(self, query: str, gl: str = "us", hl: str = "en", force_refresh: bool = False) -> GoogleSearchResult`**:
    Performs standard organic Google search and extracts knowledge graph.
  - **Internal Methods:**
    - `_get_api_key() -> str`: Validates API key formatting.
    - `_sanitize_message(message: str) -> str`: Masks API keys in logs and exception messages.
    - `_execute_query(params: Dict[str, Any], force_refresh: bool = False) -> Dict[str, Any]`: Checks cache, consumes budget credit on miss, dispatches HTTP GET to SerpApi, and caches successful responses.
    - `_parse_lens_response(raw_data: Dict[str, Any]) -> LensVisualMatchesResult`
    - `_parse_maps_response(raw_data: Dict[str, Any], query: str) -> MapsSearchResult`
    - `_parse_news_response(raw_data: Dict[str, Any], query: str) -> NewsSearchResult`
    - `_parse_google_response(raw_data: Dict[str, Any], query: str) -> GoogleSearchResult`

### 2.2 `cache_service.py` (Quota Defense & SQLite Disk Cache)
Persistent search caching engine ensuring zero live API credit consumption during repeated development, testing, and Golden Demo walk-throughs.

- **Functions:**
  - `generate_cache_key(engine: str, params: Dict[str, Any]) -> str`: Generates deterministic SHA-256 hash after stripping transient flags and credentials (`api_key`, `force_refresh`).
  - `cached_serp_call(engine: str, ttl_seconds: int = 604800)`: Python function decorator caching SerpApi queries.

- **Class:** `CacheService`
  - **`__init__(self, db_path: Optional[str] = None)`**: Connects to SQLite and invokes `init_db`.
  - **`get_cached_response(self, engine: str, params: Dict[str, Any], force_refresh: bool = False) -> Optional[Dict[str, Any]]`**:
    Queries `serp_cache` table by SHA-256 hash; evaluates TTL expiration.
  - **`set_cached_response(self, engine: str, params: Dict[str, Any], response_data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> bool`**:
    Serializes and stores query responses in SQLite.
  - **`clear_cache(self, engine: Optional[str] = None) -> int`**: Clears cached records.
  - **`get_cache_stats(self) -> Dict[str, Any]`**: Computes total queries, total cache entries, and hit count metrics.
  - **`seed_golden_cases(self) -> int`**: Pre-populates the database with 3 golden targets (Gateway of India, Neuschwanstein Castle, Santorini Rental Scam) and their complete SerpApi responses (Google Lens, Maps, News) for 100% offline replay.
  - **`get_golden_cases(self) -> List[Dict[str, Any]]`**: Returns pre-seeded benchmark targets.

### 2.3 `vision_service.py` (Visual Forensic Deconstructor & Image Cropping)
Multi-modal vision analysis module for detecting architectural motifs, infrastructure, text signage, and vegetation clues.

- **Functions:**
  - `crop_image_region(image_path: str, bbox: List[float], output_path: Optional[str] = None) -> str`:
    Extracts a sub-region defined by normalized `[ymin, xmin, ymax, xmax]` bounding box using Pillow and writes a clamped JPEG crop.

- **Class:** `VisionService`
  - **`__init__(self, gemini_api_key: Optional[str] = None, openai_api_key: Optional[str] = None)`**:
    Initializes Vision LLM clients or offline heuristic fallback engine.
  - **`deconstruct_scene(self, image_path: str, context_hint: Optional[str] = None) -> List[VisualClue]`**:
    Analyzes suspect image. When analyzing pre-seeded golden targets or running offline, returns authoritative visual clues with exact bounding boxes without burning credits. Supports dynamic LLM deconstruction when API keys are present.

### 2.4 `quota_service.py` (Session Search Budget Manager)
Enforces strict quota caps on live SerpApi calls to protect developer credits and prevent runaway agent loops.

- **Class:** `QuotaExhaustedError(Exception)`: Raised when session budget limit is breached.
- **Class:** `QuotaBudgetManager`
  - **`__init__(self, max_budget: int = 8)`**: Initializes session budget ceiling.
  - **`can_consume(self, count: int = 1) -> bool`**: Checks remaining allowance.
  - **`consume(self, count: int = 1) -> None`**: Decrements budget or raises `QuotaExhaustedError`.
  - **`remaining_budget(self) -> int`**: Returns available queries.
  - **`consumed_budget(self) -> int`**: Returns spent queries.
  - **`reset(self, new_max_budget: Optional[int] = None) -> None`**: Resets session counter.

### 2.5 `anomaly_service.py` (Forensic Contradiction & Fraud Detector)
Detects rental scams, recycled media, and geographic contradictions by correlating vision observations, SerpApi Lens results, and Maps triangulation.

- **Class:** `AnomalyService`
  - **`detect_anomalies(context_hint: Optional[str] = None, image_path: Optional[str] = None, resolved_location: Optional[GeoCandidate] = None, lens_matches: Optional[List[Dict[str, Any]]] = None, timeline_events: Optional[List[TimelineEvent]] = None) -> List[AnomalyReport]`**:
    Executes forensic rules:
    1. *Rental Scam / Stolen Hospitality Asset:* Flags residential rental claims whose Lens matches resolve to foreign luxury hotels or resorts.
    2. *Recirculated Media / Disinformation:* Flags images claiming current events when chronological archives show publication years prior.
    3. *Geographic Contradiction:* Flags architectural or vegetation mismatches against candidate coordinates.

### 2.6 `dork_service.py` (Advanced Google Search OSINT Dorking)
Formulates specialized Google Search dorks for investigating property permits, historical archives, and exposed files.

- **Class:** `DorkService`
  - **`generate_dorks(entity_name: str, location_address: str = "") -> List[OsintDork]`**:
    Constructs 4 operational dork categories:
    1. Municipal & Property Records (`filetype:pdf ("entity") ("permit" OR "zoning")`)
    2. Investigative Press & Archives (`"entity" ("investigation" OR "controversy")`)
    3. Government & Academic Registries (`site:gov OR site:org ("entity")`)
    4. Exposed Web Directories (`intitle:"index of" "entity"`)

### 2.7 `geoguessr_service.py` (Spatial Pinpoint Scoring & Radius Narrowing)
Provides competitive Geoguessr scoring and 4-phase spatial radius narrowing.

- **Class:** `GeoguessrService`
  - **`calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float`**:
    Computes geodesic WGS84 distance using Haversine formula with `EARTH_RADIUS_KM = 6371.0088`.
  - **`calculate_geoguessr_score(distance_km: float) -> int`**:
    Computes exponential decay 5,000-point score: $5000 \cdot e^{-d / 1492.7}$ with $\le 50\text{m} = 5000$.
  - **`determine_accuracy_tier(distance_km: float) -> Tuple[str, str]`**:
    Returns tier label (`Sub-50m Tactical Pinpoint`, `Street Lock`, etc.) and detective verdict.
  - **`generate_tightening_stages(distance_km: float, location_name: str, candidate_name: str) -> List[TighteningStage]`**:
    Computes 4 progressive stages: Continental ($2,500\text{km}$), Regional ($250\text{km}$), Sub-Urban ($25\text{km}$), Ground Truth ($<50\text{m}$).
  - **`evaluate_guess(candidate: GeoCandidate, ground_truth_lat: float, ground_truth_lon: float, ground_truth_name: str) -> GeoguessrResult`**:
    Generates complete evaluation payload.

### 2.8 `intent_service.py` (Dynamic Investigation Intent Classification)
Fast (<20ms) rule-based intent classification engine operating without external LLM dependencies to adaptively route multi-modal queries.

- **Class:** `IntentClassificationService`
  - **`classify_intent(lens_data: Dict[str, Any], context_hint: Optional[str] = None, image_path: Optional[str] = None) -> InvestigationIntent`**:
    Evaluates Google Lens Knowledge Graph `type` (e.g. `Clothing`, `Tourist attraction`), domain authority heuristics (`shein.com`, `zara.com`, `vogue.com` vs `wikipedia.org`, `tripadvisor.com`), match titles, and context cues. Returns `InvestigationIntent` (`FASHION_PRODUCT`, `GEOSPATIAL_LANDMARK`, `FRAUD_DISINFORMATION`, `GENERAL_OBJECT`).

### 2.9 `object_separation_service.py` (Hybrid Computer Vision & Multi-Modal Vision Ensemble)
Two-tier multi-object segmentation engine combining cloud-based multi-modal spatial reasoning with local OpenCV computer vision for multi-item moodboard, flat-lay, and wardrobe images.

- **Class:** `ObjectSeparationService`
  - **`segment_image(image_path: str, max_objects: int = 6, user_directive: Optional[str] = None, gemini_api_key: Optional[str] = None, timeout_seconds: float = 8.0) -> List[DetectedObject]`**:
    - **Tier 1 (Multi-Modal Vision LLM):** Dispatches base64 image to Google AI Studio Gemini 1.5 Flash Vision endpoint with Human-in-the-Loop (HITL) detective directives. Prompts Gemini to locate fine-grained items, normalizing coordinates from 0-1000 scale to `[ymin, xmin, ymax, xmax]` floats in `[0.0, 1.0]`.
    - **Tier 2 (Offline OpenCV Fallback):** Engages native OpenCV grayscale conversion, Otsu adaptive thresholding, and morphological opening/closing when API keys are absent or requests time out. Detects salient non-background contours, performs chromatic/spatial cluster splitting (`_split_cluster`) to separate touching items, clamps normalized bounding boxes, and infers category tags (`apparel`, `accessory`, `footwear`, `jewelry`).

### 2.10 `llm_reasoning_service.py` (Dynamic Intent & Entity Disambiguation Engine)
Hybrid semantic reasoning service providing Tier-1 semantic agentic deduction over raw Google Lens matches while maintaining a zero-credit deterministic fallback.

- **Class:** `LLMSemanticReasoningService`
  - **`disambiguate_with_gemini(visual_matches: List[Dict[str, Any]], knowledge_graph: Optional[Dict[str, Any]] = None, context_hint: Optional[str] = None, gemini_api_key: Optional[str] = None, timeout_seconds: float = 8.0) -> Optional[SemanticDisambiguationResult]`**:
    Invokes Google AI Studio Gemini 1.5 Flash REST API with `x-goog-api-key` header. Parses structured chain-of-thought JSON extracting `intent`, `primary_entity`, `target_query`, and `confidence`.
  - **`disambiguate_with_openai(visual_matches: List[Dict[str, Any]], knowledge_graph: Optional[Dict[str, Any]] = None, context_hint: Optional[str] = None, openai_api_key: Optional[str] = None, timeout_seconds: float = 8.0) -> Optional[SemanticDisambiguationResult]`**:
    Secondary provider fallback invoking OpenAI `gpt-4o-mini`.
  - **`classify_and_disambiguate(visual_matches: List[Dict[str, Any]], knowledge_graph: Optional[Dict[str, Any]] = None, context_hint: Optional[str] = None, image_path: Optional[str] = None, gemini_api_key: Optional[str] = None, openai_api_key: Optional[str] = None) -> SemanticDisambiguationResult`**:
    Master hybrid entry point trying Tier-1 Gemini, then Tier-1 OpenAI, and seamlessly degrading to Tier-2 `IntentClassificationService` heuristics on network timeout or missing credentials.

### 2.11 `llm_agent_service.py` (Antigravity-Style Dynamic LLM Decision Engine)
Institutional-grade dynamic decision engine powering Antigravity-style autonomous agentic reasoning across Skeptic, Arbiter, and Synthesizer nodes using Google AI Studio (Gemini 1.5 Flash), strictly preserving a zero-credit deterministic fallback.

- **Class:** `LLMDetectiveAgentService`
  - **`evaluate_skeptic(claimed_context: Optional[str], visual_clues: List[Any], lens_matches: List[Any], geo_candidate: Optional[Any], timeline_events: List[Any], gemini_api_key: Optional[str] = None, timeout_seconds: float = 8.0) -> Optional[SkepticEvaluationResult]`**:
    Performs dynamic semantic cross-examination comparing user caption against SerpApi Google Lens matches, Maps place data, and News historical timeline. Deduces architectural, geographic, or temporal contradictions and outputs `SkepticEvaluationResult` with `critique`, `fraud_probability`, and `is_fraud`.
  - **`arbitrate_case(hunter_hypotheses: List[str], skeptic_critique: str, fraud_probability: float, geo_candidate: Optional[Any], lens_matches: List[Any], gemini_api_key: Optional[str] = None, timeout_seconds: float = 8.0) -> Optional[ArbiterEvaluationResult]`**:
    Weighs Hunter's location hypotheses vs Skeptic's counter-arguments to calculate a continuous `adversarial_audit_score` (0.0 to 1.0) and official verdict (`fraud_unmasked`, `debate_certified`, `refining_debate`).
  - **`synthesize_summary(case_title: str, confidence_score: float, audit_score: Optional[float], resolved_location: Optional[Any], is_fraud: bool, anomalies: Optional[List[Dict[str, Any]]], gemini_api_key: Optional[str] = None, timeout_seconds: float = 8.0) -> Optional[str]`**:
    Generates a bespoke, context-rich executive forensic intelligence narrative for the final CaseFile.
  - **Security & Reliability:**
    - API key masking (`_mask_key`) ensuring keys are never printed in plaintext logs or error traces.
    - JSON markdown fence stripping (`_clean_json_markdown`) protecting Pydantic parsing.
    - Strict 8-second HTTP timeout with `httpx.TimeoutException` catch and fallback.

---

## 3. Dependencies
- **Internal:**
  - `backend.app.config.settings`
  - `backend.app.db` (`get_db_connection`, `init_db`)
  - `backend.app.models.serp`
  - `backend.app.models.case`
  - `backend.app.models.anomaly`
  - `backend.app.models.dork`
  - `backend.app.models.geoguessr`
  - `backend.app.models.llm` (`SemanticDisambiguationResult`)
  - `backend.app.models.llm_agent` (`SkepticEvaluationResult`, `ArbiterEvaluationResult`)
  - `backend.app.agent.state` (`DetectedObject`, `InvestigationIntent`)
- **External:**
  - `httpx` (HTTP client for SerpApi and Google AI Studio REST calls)
  - `sqlite3` (disk caching under WAL mode)
  - `PIL.Image` (Pillow image processing and regional cropping)
  - `cv2` (OpenCV computer vision)
  - `numpy` (array processing)
  - `pydantic` (V2 validation models)
  - `hashlib`, `math`, `urllib.parse`
