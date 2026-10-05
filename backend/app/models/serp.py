from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LensMatch(BaseModel):
    """A visual match candidate returned by Google Lens."""

    title: str = Field(..., description="Title or caption of the matching webpage")
    link: str = Field(..., description="URL where the visual match appears")
    source: str = Field(..., description="Domain or publisher name (e.g. 'instagram.com', 'theguardian.com')")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL of the matched image")
    score: Optional[int] = Field(None, description="Index or relevance rank")
    is_exact: bool = Field(False, description="Flag indicating if the match is an exact duplicate image")
    source_date: Optional[str] = Field(None, description="Publication or indexing date if detected")


class LensVisualMatchesResult(BaseModel):
    """Normalized response from SerpApi Google Lens engine."""

    visual_matches: List[LensMatch] = Field(default_factory=list, description="List of visual matches")
    exact_matches: List[LensMatch] = Field(default_factory=list, description="Exact reverse-image duplicates")
    knowledge_graph: Optional[Dict[str, Any]] = Field(None, description="Identified entity card if recognized")
    search_metadata: Optional[Dict[str, Any]] = Field(None, description="Raw query timing & status metadata")


class MapsCandidate(BaseModel):
    """A geographic place or business candidate resolved by Google Maps."""

    place_id: Optional[str] = Field(None, description="Google Maps unique place ID or data_cid")
    title: str = Field(..., description="Name of the place, landmark, or establishment")
    address: Optional[str] = Field(None, description="Physical street address or city/state")
    latitude: Optional[float] = Field(None, description="GPS Latitude coordinate")
    longitude: Optional[float] = Field(None, description="GPS Longitude coordinate")
    rating: Optional[float] = Field(None, description="Average review rating out of 5")
    reviews_count: Optional[int] = Field(None, description="Total number of reviews")
    photos: List[str] = Field(default_factory=list, description="URLs of user-submitted photos")
    place_type: Optional[str] = Field(None, description="Category of place (e.g. 'Historical Landmark')")
    phone: Optional[str] = Field(None, description="Contact phone number if available")
    website: Optional[str] = Field(None, description="Official website if available")


class MapsSearchResult(BaseModel):
    """Normalized response from SerpApi Google Maps engine."""

    candidates: List[MapsCandidate] = Field(default_factory=list, description="List of geographic place candidates")
    search_query: str = Field(..., description="The query string dispatched to Maps")
    total_results: int = Field(0, description="Number of candidate places found")


class NewsItem(BaseModel):
    """A chronological news report returned by Google News."""

    title: str = Field(..., description="Headline of the news report")
    link: str = Field(..., description="Direct URL to the article")
    source: str = Field(..., description="News organization name (e.g. 'Reuters', 'BBC')")
    date: str = Field(..., description="Timestamp or publication age (e.g. '2 hours ago', 'Oct 12, 2023')")
    snippet: Optional[str] = Field(None, description="Article summary text")
    thumbnail: Optional[str] = Field(None, description="Article thumbnail image URL")


class NewsSearchResult(BaseModel):
    """Normalized response from SerpApi Google News engine."""

    items: List[NewsItem] = Field(default_factory=list, description="List of news reports")
    search_query: str = Field(..., description="The query string dispatched to Google News")


class OrganicResult(BaseModel):
    """An organic web search result returned by Google Search."""

    title: str = Field(..., description="Title of the web search result")
    link: str = Field(..., description="Destination URL")
    snippet: Optional[str] = Field(None, description="Contextual snippet")
    position: int = Field(0, description="Rank position in SERP")


class GoogleSearchResult(BaseModel):
    """Normalized response from SerpApi Google Search engine."""

    organic_results: List[OrganicResult] = Field(default_factory=list, description="Organic search results")
    knowledge_graph: Optional[Dict[str, Any]] = Field(None, description="Knowledge graph entity if present")
    search_query: str = Field(..., description="The query string dispatched to Google Search")
