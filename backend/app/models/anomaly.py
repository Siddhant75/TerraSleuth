from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class AnomalyType(str, Enum):
    """Categorization of detected investigative contradictions."""
    FRAUDULENT_LISTING = "fraudulent_listing"
    RECIRCULATED_MEDIA = "recirculated_media"
    LOCATION_CONTRADICTION = "location_contradiction"
    METADATA_MISMATCH = "metadata_mismatch"


class AnomalySeverity(str, Enum):
    """Severity levels for detected anomalies."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AnomalyReport(BaseModel):
    """A detected contradiction between user claims/context and SerpApi ground truth."""
    anomaly_type: AnomalyType = Field(description="Type of anomaly detected")
    severity: AnomalySeverity = Field(default=AnomalySeverity.WARNING, description="Severity rating")
    title: str = Field(description="Short descriptive anomaly headline")
    description: str = Field(description="Detailed explanation of the contradiction")
    claimed_context: Optional[str] = Field(default=None, description="What the listing or context claimed")
    authoritative_truth: str = Field(description="What SerpApi visual/spatial ground truth verified")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the anomaly detection")
    evidence_url: Optional[str] = Field(default=None, description="URL verifying the true source")
