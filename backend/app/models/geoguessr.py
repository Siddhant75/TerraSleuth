"""Pydantic models for Autonomous Geoguessr Mode and spatial radius tightening."""

from typing import List
from pydantic import BaseModel, Field


class TighteningStage(BaseModel):
    """Represents a progressive spatial radius narrowing phase."""

    stage_num: int = Field(..., description="Stage sequence index (1-4)")
    name: str = Field(..., description="Stage title, e.g. Continental, Regional, Urban, Pinpoint")
    radius_km: float = Field(..., description="Effective bounding search radius in kilometers")
    description: str = Field(..., description="Investigation mechanism and clues leveraged")
    clues_resolved: str = Field(..., description="Forensic signals that resolved this stage")


class GeoguessrResult(BaseModel):
    """Complete scoring and spatial evaluation result for Geoguessr mode."""

    distance_km: float = Field(..., description="Geodesic distance error from ground truth in kilometers")
    distance_meters: float = Field(..., description="Geodesic distance error in meters")
    score: int = Field(..., description="Standard Geoguessr score from 0 to 5,000")
    max_score: int = Field(default=5000, description="Maximum possible Geoguessr score")
    accuracy_tier: str = Field(..., description="Categorical rating, e.g. Legendary Pinpoint, Metro Master")
    verdict: str = Field(..., description="Forensic detective performance verdict")
    tightening_stages: List[TighteningStage] = Field(
        default_factory=list, description="4-phase spatial radius narrowing progression"
    )
