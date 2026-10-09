"""Pydantic schemas for LLM-powered semantic reasoning and disambiguation."""

from typing import Optional
from pydantic import BaseModel, Field

from backend.app.agent.state import InvestigationIntent


class SemanticDisambiguationResult(BaseModel):
    """Structured output from LLM semantic intent & entity disambiguation."""

    intent: InvestigationIntent = Field(
        description="The deduced investigative intent category."
    )
    primary_entity: str = Field(
        description="The genuine core entity, filtering out generic stock photo or commercial noise."
    )
    target_query: str = Field(
        description="The optimal search query for downstream Google Maps place triangulation or Search."
    )
    reasoning: str = Field(
        description="Chain-of-thought rationale explaining why this conclusion was deduced from visual evidence."
    )
    confidence: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Confidence score for the deduced entity and intent.",
    )
