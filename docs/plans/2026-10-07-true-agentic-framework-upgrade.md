# Level 4 & Level 5 True Agentic Framework Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform TerraSleuth from an orchestrated LangGraph workflow into a true autonomous ReAct agent (Level 4) and an adversarial dialectical multi-agent swarm (Level 5) where Hunter, Skeptic, and Arbiter agents debate forensic hypotheses using dynamic SerpApi tool calling, deterministic offline fallbacks, and typed state integration.

**Architecture:** Refactor SerpApi client operations into LangChain `@tool` definitions protected by SQLite zero-quota caching. Introduce a ReAct OODA reasoning loop that streams structured thought telemetry to the UI terminal. Replace the linear node spine with a dialectical Hunter-Skeptic debate loop governed by an Arbiter that scores adversarial debunk risk, maps findings to typed Pydantic models, strictly guards loop counters, and certifies ground truth.

**Tech Stack:** LangGraph (`StateGraph`, conditional edges, state reducers), LangChain (`@tool`), Pydantic v2, Python 3.11+, Streamlit, Folium, Playwright, pytest.

---

### Task 1: LangChain SerpApi Tool Registry with Zero-Quota Cache Defense

**Files:**
- Create: `backend/app/agent/tools.py`
- Test: `backend/tests/test_tools.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_tools.py
import pytest
from backend.app.agent.tools import (
    tool_lens_search,
    tool_maps_triangulate,
    tool_news_audit,
    tool_google_dork,
    tool_crop_region,
)

def test_tools_registered_and_callable():
    assert callable(tool_lens_search.invoke)
    assert callable(tool_maps_triangulate.invoke)
    assert callable(tool_news_audit.invoke)
    assert callable(tool_google_dork.invoke)
    assert callable(tool_crop_region.invoke)

def test_tool_maps_triangulate_cached_execution():
    result = tool_maps_triangulate.invoke({"query": "Gateway of India Mumbai"})
    assert isinstance(result, dict)
    assert "candidates" in result
    assert len(result["candidates"]) > 0
    candidate = result["candidates"][0]
    assert "18.92" in str(candidate.get("latitude"))

def test_tool_lens_search_zero_quota_on_golden_target():
    result = tool_lens_search.invoke({
        "image_url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f"
    })
    assert isinstance(result, dict)
    assert "visual_matches" in result
    assert len(result["visual_matches"]) > 0
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_tools.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.app.agent.tools'`

**Step 3: Write minimal implementation**

```python
# backend/app/agent/tools.py
from typing import Any, Dict, List, Optional
from langchain_core.tools import tool
from backend.app.services.cache_service import CacheService
from backend.app.services.serpapi_service import SerpApiService
from backend.app.services.vision_service import crop_image_region

_cache = CacheService()
_serp = SerpApiService(cache_service=_cache)

@tool
def tool_lens_search(image_url: str, crop_bbox: Optional[List[float]] = None) -> Dict[str, Any]:
    """Search Google Lens for reverse visual twins and authoritative matches."""
    res = _serp.search_lens(image_url=image_url)
    return {
        "visual_matches": [m.model_dump() for m in res.visual_matches[:6]],
        "knowledge_graph": [k.model_dump() for k in res.knowledge_graph],
    }

@tool
def tool_maps_triangulate(query: str, lat_hint: Optional[float] = None, lon_hint: Optional[float] = None) -> Dict[str, Any]:
    """Triangulate physical coordinates and place details using Google Maps."""
    res = _serp.search_maps(query=query)
    candidates = []
    for c in res.candidates[:4]:
        candidates.append({
            "title": c.title,
            "address": c.address,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "place_id": c.place_id,
            "match_score": c.match_score,
        })
    return {"candidates": candidates}

@tool
def tool_news_audit(query: str, date_filter: Optional[str] = None) -> Dict[str, Any]:
    """Audit temporal milestones and earliest publication records in Google News."""
    res = _serp.search_news(query=query)
    events = []
    for item in res.articles[:4]:
        events.append({
            "title": item.title,
            "source": item.source,
            "date": item.date,
            "link": item.link,
            "snippet": item.snippet,
        })
    return {"articles": events}

@tool
def tool_google_dork(dork_query: str) -> Dict[str, Any]:
    """Execute targeted OSINT search dorks for municipal permits and scam records."""
    res = _serp.search_google(query=dork_query)
    return {
        "organic_results": [
            {"title": r.title, "link": r.link, "snippet": r.snippet}
            for r in res.organic_results[:5]
        ]
    }

@tool
def tool_crop_region(image_path: str, bbox: List[float], label: str) -> str:
    """Crop an isolated region from an image for targeted visual inspection."""
    return crop_image_region(image_path=image_path, bbox=bbox)
```

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_tools.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/agent/tools.py backend/tests/test_tools.py
git commit -m "feat(agent): register LangChain SerpApi and vision tools with cache defense (Task 1)"
```

---

### Task 2: Level 4 ReAct Structured Thought Schema & Reasoning Engine

**Files:**
- Create: `backend/app/models/react.py`
- Create: `backend/app/agent/nodes/react_supervisor.py`
- Test: `backend/tests/test_react_supervisor.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_react_supervisor.py
import pytest
from backend.app.models.react import AgentThought, ReActStepType
from backend.app.agent.nodes.react_supervisor import generate_agent_thought

def test_agent_thought_schema():
    thought = AgentThought(
        step_type=ReActStepType.THOUGHT,
        agent_role="lead_detective",
        thought="Basalt arch indicates Western Indian architectural style.",
        decision="Invoke Google Maps on Apollo Bunder.",
        tool_call="tool_maps_triangulate",
        tool_args={"query": "Apollo Bunder Mumbai"},
        observation="Found Gateway of India at 18.9220 N, 72.8347 E",
    )
    assert thought.agent_role == "lead_detective"
    assert thought.tool_call == "tool_maps_triangulate"

def test_generate_agent_thought_formatting():
    formatted = generate_agent_thought(
        agent_role="hunter",
        thought="Detected iconic red dome.",
        decision="Verify adjacent heritage hotel.",
        tool_call="tool_lens_search",
        observation="Visual twin: Taj Mahal Palace.",
    )
    assert "[HUNTER]" in formatted
    assert "Taj Mahal Palace" in formatted
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_react_supervisor.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.app.models.react'`

**Step 3: Write minimal implementation**

```python
# backend/app/models/react.py
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ReActStepType(str, Enum):
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    SYNTHESIS = "synthesis"

class AgentThought(BaseModel):
    step_type: ReActStepType = ReActStepType.THOUGHT
    agent_role: str = Field(description="Role: hunter, skeptic, or arbiter")
    thought: str = Field(description="Internal reasoning monologue")
    decision: str = Field(description="Actionable next step")
    tool_call: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None

# backend/app/agent/nodes/react_supervisor.py
from typing import Optional
from backend.app.models.react import AgentThought, ReActStepType

def generate_agent_thought(
    agent_role: str,
    thought: str,
    decision: str,
    tool_call: Optional[str] = None,
    observation: Optional[str] = None,
) -> str:
    role_tag = f"[{agent_role.upper()}]"
    lines = [f"{role_tag} {thought}"]
    if decision:
        lines.append(f"Decision: {decision}")
    if tool_call:
        lines.append(f"Action: {tool_call}()")
    if observation:
        lines.append(f"Observation: {observation}")
    return " | ".join(lines)
```

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_react_supervisor.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models/react.py backend/app/agent/nodes/react_supervisor.py backend/tests/test_react_supervisor.py
git commit -m "feat(react): implement structured ReAct thought schema and stream formatter (Task 2)"
```

---

### Task 3: Level 5 Dialectical Swarm Nodes with Pydantic State Mapping & Deterministic Fallbacks

**Files:**
- Modify: `backend/app/agent/state.py` (add `hunter_hypotheses`, `skeptic_critiques`, `debate_history`, `audit_score`)
- Create: `backend/app/agent/nodes/swarm_nodes.py`
- Test: `backend/tests/test_swarm_debate.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_swarm_debate.py
import pytest
from backend.app.agent.state import create_initial_osint_state
from backend.app.agent.nodes.swarm_nodes import hunter_node, skeptic_node, arbiter_node

def test_hunter_node_populates_typed_geo_candidates_and_hypotheses():
    state = create_initial_osint_state(
        image_path="frontend/assets/targets/gateway_mumbai.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
    )
    res = hunter_node(state)
    assert len(res["hunter_hypotheses"]) > 0
    assert "geo_candidates" in res
    assert len(res["geo_candidates"]) > 0
    # Must be valid GeoCandidate Pydantic models
    cand = res["geo_candidates"][0]
    assert hasattr(cand, "latitude")
    assert hasattr(cand, "longitude")
    assert "Mumbai" in cand.address or "Gateway" in cand.title
    assert len(res["debate_history"]) > 0

def test_skeptic_node_evaluates_contradictions_and_timeline():
    state = create_initial_osint_state(
        image_path="frontend/assets/targets/gateway_mumbai.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
    )
    state["hunter_hypotheses"] = ["Apollo Bunder Waterfront Arch, Mumbai"]
    res = skeptic_node(state)
    assert len(res["skeptic_critiques"]) > 0
    assert "timeline_events" in res
    assert len(res["debate_history"]) > 0

def test_arbiter_node_computes_audit_score_and_certifies_verdict():
    state = create_initial_osint_state(
        image_path="frontend/assets/targets/gateway_mumbai.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
    )
    state["hunter_hypotheses"] = ["Gateway of India, Mumbai"]
    state["skeptic_critiques"] = ["No architectural or vegetation contradiction found."]
    res = arbiter_node(state)
    assert 0.0 <= res["audit_score"] <= 1.0
    assert res["audit_score"] >= 0.8
    assert res["status"] in ("debate_certified", "refining_coordinates")
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_swarm_debate.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.app.agent.nodes.swarm_nodes'`

**Step 3: Write minimal implementation**

1. Update `backend/app/agent/state.py`:
```python
# Add to OsintGraphState:
hunter_hypotheses: Annotated[List[str], merge_lists]
skeptic_critiques: Annotated[List[str], merge_lists]
debate_history: Annotated[List[Dict[str, str]], merge_lists]
audit_score: float
```

2. Implement `backend/app/agent/nodes/swarm_nodes.py`:
   - `hunter_node(state)`:
     * Calls `tool_lens_search` and `tool_maps_triangulate`.
     * **Crucial State Mapping:** Converts dictionary candidates from tools into fully validated `GeoCandidate` Pydantic models.
     * Generates `AgentThought` with `[HUNTER]` tag and adds to `debate_history`.
     * Has deterministic offline fallback for the 3 golden cases if API keys are unset.
   - `skeptic_node(state)`:
     * Analyzes Hunter's candidates against clues, vegetation, architecture, and news timelines.
     * **Crucial State Mapping:** Populates `timeline_events: List[TimelineEvent]` and `citations: List[Citation]`.
     * If fraud scenario (Santorini rental scam), flags `FRAUDULENT_LISTING` contradiction.
     * Generates `AgentThought` with `[SKEPTIC]` tag and adds to `debate_history`.
   - `arbiter_node(state)`:
     * Evaluates debunk probability.
     * If Hunter and Skeptic agree without contradiction: `audit_score = 0.94` (`status = "debate_certified"`).
     * If fatal contradiction (rental scam): `audit_score = 0.35` (`status = "fraud_unmasked"`).
     * If weak candidate: `audit_score = 0.55` (`status = "refining_coordinates"`).

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_swarm_debate.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/agent/state.py backend/app/agent/nodes/swarm_nodes.py backend/tests/test_swarm_debate.py
git commit -m "feat(swarm): implement Hunter, Skeptic, and Arbiter nodes with Pydantic state mapping (Task 3)"
```

---

### Task 4: LangGraph State Machine Integration with Strict Loop Termination

**Files:**
- Modify: `backend/app/agent/graph.py`
- Test: `backend/tests/test_dialectical_graph.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_dialectical_graph.py
import pytest
from backend.app.agent.graph import create_osint_graph
from backend.app.agent.state import create_initial_osint_state

def test_dialectical_graph_compilation_and_topology():
    graph = create_osint_graph()
    nodes = graph.nodes
    assert "hunter" in nodes
    assert "skeptic" in nodes
    assert "arbiter" in nodes
    assert "case_synthesizer" in nodes

def test_golden_case_dialectical_execution():
    graph = create_osint_graph()
    state = create_initial_osint_state(
        image_path="frontend/assets/targets/gateway_mumbai.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        max_budget=8,
    )
    final_state = graph.invoke(state)
    assert final_state["audit_score"] >= 0.8
    assert len(final_state["debate_history"]) >= 2
    assert final_state["final_case_file"] is not None
    assert final_state["final_case_file"].resolved_location is not None

def test_dialectical_graph_loop_termination_bound():
    # Verify that a low audit score respects max_refinement_hops and terminates cleanly
    graph = create_osint_graph()
    state = create_initial_osint_state(
        image_path="frontend/assets/targets/gateway_mumbai.jpg",
        max_budget=1,
        max_refinement_hops=1,
    )
    final_state = graph.invoke(state)
    assert final_state["refinement_hops"] <= 1
    assert final_state["final_case_file"] is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_dialectical_graph.py -v`  
Expected: FAIL with missing nodes in graph

**Step 3: Write minimal implementation**

Update `backend/app/agent/graph.py`:
- Add `swarm_refinement_router(state: OsintGraphState) -> Dict[str, Any]`:
  * Explicitly increments `refinement_hops += 1`
  * Explicitly decrements `budget_remaining -= 1`
  * Logs loop iteration.
- Implement conditional edge `should_refine_debate(state: OsintGraphState) -> str`:
  * If `state.get("audit_score", 1.0) < 0.70 and state.get("refinement_hops", 0) < state.get("max_refinement_hops", 2) and state.get("budget_remaining", 0) > 0`:
    ➔ returns `"swarm_refinement_router"`
  * Else:
    ➔ returns `"case_synthesizer"`
- Wire graph edges:
  * `START` ➔ `scene_deconstructor` ➔ `hunter` ➔ `skeptic` ➔ `arbiter`
  * `arbiter` ➔ conditional edge (`should_refine_debate`):
    - `"swarm_refinement_router"` ➔ `hunter` (loops back safely!)
    - `"case_synthesizer"` ➔ `END`

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_dialectical_graph.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/agent/graph.py backend/tests/test_dialectical_graph.py
git commit -m "feat(graph): wire dialectical Hunter-Skeptic debate loop with strict loop bounds (Task 4)"
```

---

### Task 5: UI Dialectical Stream, Streaming Compatibility, and Red-Team Audit Badge

**Files:**
- Modify: `frontend/components/swarm_telemetry_terminal.py`
- Modify: `frontend/components/dossier_exporter.py`
- Modify: `frontend/components/tactical_command_deck.py`
- Modify: `frontend/app.py`
- Test: `frontend/tests/test_swarm_ui.py`

**Step 1: Write the failing test**

```python
# frontend/tests/test_swarm_ui.py
import pytest
from frontend.components.swarm_telemetry_terminal import generate_swarm_terminal_html

def test_swarm_terminal_renders_role_badges():
    logs = [
        "[HUNTER] Proposing Gateway of India based on basalt arch matches.",
        "[SKEPTIC] Auditing flora and municipal records... No contradiction.",
        "[ARBITER] Audit certified with 96% confidence score.",
    ]
    html = generate_swarm_terminal_html(logs)
    assert "HUNTER" in html
    assert "SKEPTIC" in html
    assert "ARBITER" in html
```

**Step 2: Run test to verify it fails**

Run: `pytest frontend/tests/test_swarm_ui.py -v`  
Expected: FAIL with missing styling or badge tags

**Step 3: Write minimal implementation**

1. In `frontend/components/swarm_telemetry_terminal.py`:
   - Enhance `generate_swarm_terminal_html`:
     * Style `[HUNTER]` in glowing Cyan (`#00f2fe`).
     * Style `[SKEPTIC]` in glowing Crimson (`#ef4444`).
     * Style `[ARBITER]` in glowing Emerald (`#10b981`).
     * Style `[THOUGHT]` in glowing Amber (`#f59e0b`).
2. In `frontend/app.py`:
   - Update `stream_osint_investigation_sync` streaming mapper:
     * When `node_name == "hunter"`, render status: `🎯 Hunter: Formulating Hypotheses & Visual Twins`.
     * When `node_name == "skeptic"`, render status: `🔬 Skeptic: Red-Team Forensic Counter-Probe`.
     * When `node_name == "arbiter"`, render status: `⚖️ Arbiter: Dialectical Audit & Resolution`.
   - Ensure all `geo_candidates`, `visual_clues`, and `lens_matches` pass cleanly to `TacticalCommandDeck`.
3. In `frontend/components/dossier_exporter.py` & `tactical_command_deck.py`:
   - Render `🛡️ RED-TEAM VERIFIED` badge when `audit_score >= 0.8`.
   - Render `🚨 ADVERSARIALLY DEBUNKED (FRAUD DETECTED)` badge when anomalies are confirmed.

**Step 4: Run test to verify it passes**

Run: `pytest frontend/tests/test_swarm_ui.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/components/swarm_telemetry_terminal.py frontend/components/dossier_exporter.py frontend/components/tactical_command_deck.py frontend/app.py frontend/tests/test_swarm_ui.py
git commit -m "feat(ui): stream dialectical swarm roles and red-team audit badges (Task 5)"
```

---

### Task 6: Multi-Gate Regression & Playwright Browser Audit

**Files:**
- Verify: Full pytest suite (`backend/tests/`, `frontend/tests/`, `tests/e2e/test_dashboard_e2e.py`)
- Run: `tests/e2e/run_playwright_audit.py`
- Update: `docs/terrasleuth-roadmap.md` & `AGENTS.md`

**Step 1: Run complete pytest suite**

Run: `$env:PYTHONPATH="." ; pytest backend/tests/ frontend/tests/ tests/e2e/test_dashboard_e2e.py -v`  
Expected: 100% PASS (all existing 91 tests + new dialectical tests passing) with 0 live SerpApi credits burned.

**Step 2: Run Playwright automated browser verification**

Run: `python tests/e2e/run_playwright_audit.py`  
Expected: Exit code 0, 9 verified screenshots captured.

**Step 3: Adversarial Code Review**

Dispatch `code-reviewer` subagent for Stage 3 review until `PASS (APPROVED)`.

**Step 4: Commit & Tag**

```bash
git add docs/terrasleuth-roadmap.md tests/e2e/screenshots/
git commit -m "chore(release): certify Level 4 and Level 5 True Agentic Framework (Sprint 8 / v0.8.0)"
```
