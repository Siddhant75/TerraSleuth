# C4 Code-Level Documentation: `backend/app/agent/nodes`

## 1. Overview
- **Name:** OSINT Swarm Investigative & Dialectical Nodes
- **Description:** Specialized investigative agents and state machine nodes implementing visual deconstruction, reverse-image search, geospatial triangulation, chronological auditing, ReAct reasoning, and Level 5 adversarial Hunter-Skeptic debate.
- **Location:** [`backend/app/agent/nodes`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes)
- **Language:** Python 3.11+
- **Purpose:** Core investigative logic within the LangGraph OSINT execution graph, processing raw input targets into structured multi-modal intelligence evidence.

---

## 2. Code Elements

### 2.1 `scene_deconstructor.py`
- **Function:** `scene_deconstructor_node(state: OsintGraphState) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/nodes/scene_deconstructor.py#L11-L58`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/scene_deconstructor.py#L11-L58)
  - **Description:** Deconstructs suspect image into atomic forensic clues across architecture, signage scripts, flora/climate, and infrastructure bounding boxes.
  - **Dependencies:** `backend.app.agent.state.OsintGraphState`, `backend.app.services.vision_service.VisionService`.

### 2.2 `lens_hunter.py`
- **Function:** `lens_hunter_node(state: OsintGraphState) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/nodes/lens_hunter.py#L11-L80`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/lens_hunter.py#L11-L80)
  - **Description:** Executes SerpApi Google Lens visual provenance search to retrieve exact visual twins, knowledge graph entities, and publication links.
  - **Dependencies:** `backend.app.services.serpapi_service.SerpApiService`, `backend.app.models.case.Citation`.

### 2.3 `geo_triangulator.py`
- **Function:** `geo_triangulator_node(state: OsintGraphState) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/nodes/geo_triangulator.py#L11-L134`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/geo_triangulator.py#L11-L134)
  - **Description:** Triangulates physical coordinates, place IDs, and street addresses via SerpApi Google Maps based on hypotheses derived from Lens and scene clues.
  - **Dependencies:** `backend.app.services.serpapi_service.SerpApiService`, `backend.app.models.case.GeoCandidate`.

### 2.4 `chrono_auditor.py`
- **Function:** `chrono_auditor_node(state: OsintGraphState) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/nodes/chrono_auditor.py#L11-L114`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/chrono_auditor.py#L11-L114)
  - **Description:** Queries SerpApi Google News to audit temporal publication milestones, earliest image appearances, and historical events.
  - **Dependencies:** `backend.app.services.serpapi_service.SerpApiService`, `backend.app.models.case.TimelineEvent`.

### 2.5 `case_synthesizer.py`
- **Function:** `case_synthesizer_node(state: OsintGraphState) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/nodes/case_synthesizer.py#L170-L261`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/case_synthesizer.py#L170-L261)
  - **Description:** Compiles accumulated evidence, runs AnomalyService and DorkService, calculates overall confidence score, and synthesizes final `CaseFile`.
- **Helper Functions:**
  - `calculate_confidence_score(...) -> float`
  - `generate_case_summary_markdown(...) -> str`

### 2.6 `react_supervisor.py`
- **Function:** `create_agent_thought(...) -> AgentThought`
  - **Location:** [`backend/app/agent/nodes/react_supervisor.py#L9-L27`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/react_supervisor.py#L9-L27)
  - **Description:** Generates validated Pydantic `AgentThought` instances with structured step types.
- **Function:** `generate_agent_thought(...) -> str`
  - **Description:** Returns formatted monospace terminal telemetry stream string.

### 2.7 `swarm_nodes.py` (Level 5 Dialectical Swarm)
- **Function:** `hunter_node(state: OsintGraphState) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/nodes/swarm_nodes.py#L18-L120`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/swarm_nodes.py#L18-L120)
  - **Description:** Proposes optimistic geographic hypotheses, calls `tool_lens_search` and `tool_maps_triangulate`, dynamically extracts entity queries, and returns typed models.
- **Function:** `skeptic_node(state: OsintGraphState) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/nodes/swarm_nodes.py#L122-L198`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/swarm_nodes.py#L122-L198)
  - **Description:** Adversarial red-team auditor. Calls `tool_news_audit`, evaluates environmental contradictions and fraud via `AnomalyService.detect_anomalies`.
- **Function:** `arbiter_node(state: OsintGraphState) -> Dict[str, Any]`
  - **Location:** [`backend/app/agent/nodes/swarm_nodes.py#L200-L243`](file:///d:/SerpAPI_hackathon/backend/app/agent/nodes/swarm_nodes.py#L200-L243)
  - **Description:** Dialectical judge weighing Hunter hypotheses vs Skeptic critiques. Computes `AdversarialAuditScore`, issues certified consensus or `fraud_unmasked` verdict.

---

## 3. Dependencies
- **Internal:**
  - `backend.app.agent.state.OsintGraphState`
  - `backend.app.agent.tools.*`
  - `backend.app.services.serpapi_service.SerpApiService`
  - `backend.app.services.vision_service.VisionService`
  - `backend.app.services.anomaly_service.AnomalyService`
  - `backend.app.services.dork_service.DorkService`
  - `backend.app.models.case.*`
  - `backend.app.models.react.*`
- **External:** `langgraph`, `pydantic`, `logging`, `uuid`

---

## 4. Relationships (Mermaid)

```mermaid
graph TD
    SD["scene_deconstructor_node"] --> HN["hunter_node (Lens + Maps)"]
    HN --> SN["skeptic_node (News + Anomaly)"]
    SN --> AN["arbiter_node (Judge)"]
    AN -->|fraud_unmasked or Certified| CS["case_synthesizer_node"]
    AN -->|Refine & Score < 0.70| HN
```
