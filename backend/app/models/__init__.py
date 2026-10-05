"""Data models for TerraSleuth."""
from backend.app.models.serp import (
    GoogleSearchResult,
    LensMatch,
    LensVisualMatchesResult,
    MapsCandidate,
    MapsSearchResult,
    NewsItem,
    NewsSearchResult,
    OrganicResult,
)
from backend.app.models.case import (
    CaseFile,
    Citation,
    ClueCategory,
    GeoCandidate,
    TimelineEvent,
    VisualClue,
)

__all__ = [
    # Serp models
    "LensMatch",
    "LensVisualMatchesResult",
    "MapsCandidate",
    "MapsSearchResult",
    "NewsItem",
    "NewsSearchResult",
    "OrganicResult",
    "GoogleSearchResult",
    # OSINT Case models
    "CaseFile",
    "Citation",
    "ClueCategory",
    "GeoCandidate",
    "TimelineEvent",
    "VisualClue",
]
