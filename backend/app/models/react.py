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
