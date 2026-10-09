from typing import Optional
from pydantic import BaseModel, Field


class SkepticEvaluationResult(BaseModel):
    """Structured forensic evaluation produced by the Skeptic agent."""
    critique: str = Field(..., description="Forensic debunking critique detailing any evidentiary contradictions.")
    fraud_probability: float = Field(default=0.0, ge=0.0, le=1.0, description="Estimated probability of fraud/deception (0.0 to 1.0).")
    is_fraud: bool = Field(default=False, description="True if a critical contradiction or fraudulent listing was detected.")
    reasoning: Optional[str] = Field(default=None, description="Chain-of-thought rationale behind the evaluation.")


class ArbiterEvaluationResult(BaseModel):
    """Structured arbitration decision produced by the Arbiter agent."""
    adversarial_audit_score: float = Field(..., ge=0.0, le=1.0, description="Continuous credibility score (0.0=fraud/fabricated, 1.0=authentic).")
    verdict: str = Field(..., description="Verdict status: 'fraud_unmasked', 'debate_certified', or 'refining_debate'.")
    reasoning: str = Field(..., description="Detailed arbitration justification weighing Hunter vs Skeptic evidence.")
