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

    def to_terminal_str(self) -> str:
        """Format thought into a clean monospace telemetry string."""
        role_tag = f"[{self.agent_role.upper()}]"
        parts = [f"{role_tag} {self.thought}"]
        if self.decision:
            parts.append(f"Decision: {self.decision}")
        if self.tool_call:
            args_str = f"({self.tool_args})" if self.tool_args else "()"
            parts.append(f"Action: {self.tool_call}{args_str}")
        if self.observation:
            parts.append(f"Observation: {self.observation}")
        return " | ".join(parts)
