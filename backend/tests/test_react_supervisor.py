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
    assert "Decision" in formatted
    assert "Action: tool_lens_search()" in formatted
