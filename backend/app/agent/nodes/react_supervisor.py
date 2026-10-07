import logging
from typing import Any, Dict, Optional

from backend.app.models.react import AgentThought, ReActStepType

logger = logging.getLogger(__name__)


def create_agent_thought(
    agent_role: str,
    thought: str,
    decision: str,
    tool_call: Optional[str] = None,
    tool_args: Optional[Dict[str, Any]] = None,
    observation: Optional[str] = None,
    step_type: ReActStepType = ReActStepType.THOUGHT,
) -> AgentThought:
    """Create a validated Pydantic AgentThought instance."""
    return AgentThought(
        step_type=step_type,
        agent_role=agent_role,
        thought=thought,
        decision=decision,
        tool_call=tool_call,
        tool_args=tool_args,
        observation=observation,
    )


def generate_agent_thought(
    agent_role: str,
    thought: str,
    decision: str,
    tool_call: Optional[str] = None,
    observation: Optional[str] = None,
) -> str:
    """Format structured reasoning into a high-visibility terminal telemetry stream string."""
    at = create_agent_thought(
        agent_role=agent_role,
        thought=thought,
        decision=decision,
        tool_call=tool_call,
        observation=observation,
    )
    return at.to_terminal_str()
