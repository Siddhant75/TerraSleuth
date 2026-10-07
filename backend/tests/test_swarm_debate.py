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
    cand = res["geo_candidates"][0]
    assert hasattr(cand, "latitude")
    assert hasattr(cand, "longitude")
    assert "18.92" in str(cand.latitude) or "Mumbai" in cand.address or "Gateway" in cand.name
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


def test_debate_history_contains_structured_agent_thought_fields():
    state = create_initial_osint_state(
        image_path="frontend/assets/targets/gateway_mumbai.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
    )
    hunter_res = hunter_node(state)
    for entry in hunter_res["debate_history"]:
        assert "role" in entry
        assert "content" in entry
        assert "step_type" in entry
        assert "thought" in entry
        assert "decision" in entry

    state["hunter_hypotheses"] = hunter_res["hunter_hypotheses"]
    state["geo_candidates"] = hunter_res["geo_candidates"]
    skeptic_res = skeptic_node(state)
    for entry in skeptic_res["debate_history"]:
        assert "role" in entry
        assert "step_type" in entry
        assert "thought" in entry

    arbiter_res = arbiter_node(state)
    for entry in arbiter_res["debate_history"]:
        assert "role" in entry
        assert "step_type" in entry


def test_fraud_unmasked_bypasses_refinement_loop():
    from backend.app.agent.graph import should_refine_debate

    state = create_initial_osint_state(
        image_path="frontend/assets/targets/rental_scam_santorini.jpg",
        context_hint="Exclusive beachfront villa rental in Miami, FL",
    )
    state["status"] = "fraud_unmasked"
    state["audit_score"] = 0.35
    state["refinement_hops"] = 0
    state["max_refinement_hops"] = 2
    state["budget_remaining"] = 6

    # When fraud is unmasked, router must immediately transition to case_synthesizer
    decision = should_refine_debate(state)
    assert decision == "case_synthesizer"

