from enum import Enum
import time
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, field_validator


class ClueCategory(str, Enum):
    """Forensic categories of visual evidence."""
    ARCHITECTURE = "architecture"
    SIGNAGE = "signage"
    VEGETATION = "vegetation"
    INFRASTRUCTURE = "infrastructure"
    LANDMARK = "landmark"
    OTHER = "other"


class VisualClue(BaseModel):
    """An individual atomic forensic clue extracted from the image."""
    clue_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: ClueCategory = Field(description="Forensic category of the visual clue")
    description: str = Field(description="Forensic observation and visual evidence description")
    bounding_box: Optional[List[float]] = Field(
        default=None,
        min_length=4,
        max_length=4,
        description="Normalized bounding box [ymin, xmin, ymax, xmax] with coordinates in [0.0, 1.0]",
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence score from 0.0 to 1.0")
    suggested_query: Optional[str] = Field(default=None, description="Suggested SerpApi search query derived from this clue")

    @field_validator("bounding_box")
    @classmethod
    def validate_bounding_box_coordinates(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Ensure all bounding box coordinates are normalized floats within [0.0, 1.0]."""
        if v is not None:
            if len(v) != 4:
                raise ValueError("bounding_box must contain exactly 4 normalized coordinates [ymin, xmin, ymax, xmax].")
            for coord in v:
                if not (0.0 <= coord <= 1.0):
                    raise ValueError(f"Bounding box coordinate {coord} must be between 0.0 and 1.0.")
        return v


class GeoCandidate(BaseModel):
    """A triangulated geographic location candidate resolved via Google Maps or Lens."""
    name: str = Field(description="Resolved landmark or business name")
    address: Optional[str] = Field(default=None, description="Street address or administrative area")
    latitude: float = Field(description="WGS84 latitude coordinate")
    longitude: float = Field(description="WGS84 longitude coordinate")
    place_id: Optional[str] = Field(default=None, description="Google Maps Place ID if available")
    match_score: float = Field(ge=0.0, le=1.0, description="Evidence triangulation match confidence from 0.0 to 1.0")
    engine_source: str = Field(description="SerpApi engine that yielded this candidate (e.g. google_maps, google_lens)")
    evidence_snippet: Optional[str] = Field(default=None, description="Snippet or corroborating evidence text")
    source_url: Optional[str] = Field(default=None, description="Direct URL to Maps place or source page")


class TimelineEvent(BaseModel):
    """A chronological event documenting when and where an image or story surfaced."""
    date: str = Field(description="Date string or relative timestamp")
    title: str = Field(description="Event headline or article title")
    source: str = Field(description="Publishing source domain or outlet")
    url: Optional[str] = Field(default=None, description="Source article or image URL")
    snippet: str = Field(description="Corroborating text excerpt")
    is_origin: bool = Field(default=False, description="True if identified as the earliest known visual appearance")


class Citation(BaseModel):
    """An evidentiary citation anchoring a claim to a verifiable source."""
    title: str = Field(description="Title of citation source")
    url: str = Field(description="Verified URL link")
    engine: str = Field(description="SerpApi engine used (google_lens, google_maps, google_news, google)")
    snippet: str = Field(description="Relevant quotation or data snippet")


class CaseFile(BaseModel):
    """The synthesized digital forensic investigation dossier."""
    case_id: str = Field(default_factory=lambda: f"case_{int(time.time())}")
    title: str = Field(description="Case title or subject identification")
    case_summary: str = Field(description="Executive forensic summary markdown")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Overall investigation confidence score")
    resolved_location: Optional[GeoCandidate] = Field(default=None, description="Final triangulated geographic coordinates")
    visual_clues: List[VisualClue] = Field(default_factory=list, description="Forensic visual clues identified")
    lens_matches: List[dict] = Field(default_factory=list, description="Top visual twin matches from Google Lens")
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Chronological publication timeline")
    citations: List[Citation] = Field(default_factory=list, description="Verifiable proof citations")
    anomalies: List[dict] = Field(default_factory=list, description="Detected fraud or disinformation anomalies")
    dorks: List[dict] = Field(default_factory=list, description="Targeted OSINT Google Search dorks")
    refinement_hops: int = Field(default=0, description="Number of iterative disambiguation cycles performed")
    serp_queries_executed: int = Field(default=0, description="Total SerpApi search queries executed")
    adversarial_audit_score: Optional[float] = Field(default=None, description="Adversarial red-team audit score from 0.0 to 1.0")

