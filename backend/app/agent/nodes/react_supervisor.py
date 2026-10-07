import logging
from typing import Optional

from backend.app.models.react import AgentThought, ReActStepType

logger = logging.getLogger(__name__)


def generate_agent_thought(
    agent_role: str,
    thought: str,
    decision: str,
    tool_call: Optional[str] = None,
    observation: Optional[str] = None,
) -> str:
    """Format structured reasoning into a high-visibility terminal telemetry stream string."""
    role_tag = f"[{agent_role.upper()}]"
    parts = [f"{role_tag} {thought}"]
    if decision:
        parts.append(f"Decision: {decision}")
    if tool_call:
        parts.append(f"Action: {tool_call}()")
    if observation:
        parts.append(f"Observation: {observation}")
    return " | ".join(parts)
