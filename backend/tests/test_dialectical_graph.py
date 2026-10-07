import pytest
from backend.app.agent.graph import (
    create_dialectical_osint_graph,
    create_osint_graph,
    investigate_image_dialectical,
    should_refine_debate,
    swarm_refinement_router_node,
)
from backend.app.agent.state import create_initial_osint_state


def test_dialectical_graph_compilation_and_topology():
    graph = create_osint_graph()
    node_names = set(graph.nodes.keys())
    assert "hunter" in node_names
    assert "skeptic" in node_names
    assert "arbiter" in node_names
    assert "case_synthesizer" in node_names
    assert "swarm_refinement_router" in node_names


def test_swarm_refinement_router_decrements_budget_and_increments_hops():
    state = create_initial_osint_state("img.jpg", max_budget=5, max_refinement_hops=2)
    state["budget_remaining"] = 5
    state["refinement_hops"] = 0
    res = swarm_refinement_router_node(state)
    assert res["refinement_hops"] == 1
    assert res["budget_remaining"] == 4
    assert res["status"] == "refining_debate"


def test_should_refine_debate_router_circuit_breakers():
    # 1. Low score, hops remaining, budget remaining -> refine
    state = create_initial_osint_state("img.jpg", max_budget=5, max_refinement_hops=2)
    state["audit_score"] = 0.50
    state["refinement_hops"] = 0
    state["budget_remaining"] = 3
    assert should_refine_debate(state) == "swarm_refinement_router"

    # 2. Score >= 0.70 -> certified, synthesize directly
    state["audit_score"] = 0.94
    assert should_refine_debate(state) == "case_synthesizer"

    # 3. Max hops reached -> circuit breaker terminates to case_synthesizer
    state["audit_score"] = 0.50
    state["refinement_hops"] = 2
    assert should_refine_debate(state) == "case_synthesizer"

    # 4. Budget exhausted -> circuit breaker terminates to case_synthesizer
    state["refinement_hops"] = 0
    state["budget_remaining"] = 0
    assert should_refine_debate(state) == "case_synthesizer"


def test_golden_case_dialectical_execution():
    state = create_initial_osint_state(
        image_path="frontend/assets/targets/gateway_mumbai.jpg",
        image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        max_budget=8,
    )
    graph = create_dialectical_osint_graph()
    final_state = graph.invoke(state)

    assert final_state["audit_score"] >= 0.80
    assert len(final_state["debate_history"]) >= 2
    assert final_state["final_case_file"] is not None
    assert final_state["final_case_file"].resolved_location is not None
    assert "Mumbai" in final_state["final_case_file"].resolved_location.address or "Gateway" in final_state["final_case_file"].resolved_location.name
