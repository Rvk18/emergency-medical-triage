"""Triage request and result models. Strict schema aligned with WHO IITT / ESI."""

from typing import Literal

from pydantic import BaseModel, Field

SeverityLevel = Literal["critical", "high", "medium", "low"]


class TriageRequest(BaseModel):
    """Input for triage assessment."""

    symptoms: list[str] = Field(..., min_length=1, description="Patient symptoms")
    vitals: dict[str, float] = Field(default_factory=dict, description="Vital signs")
    age_years: int | None = Field(default=None, ge=0, le=150)
    sex: str | None = None


class TriageResult(BaseModel):
    """Output of triage assessment. Validate all agent output with this schema."""

    severity: SeverityLevel = Field(
        ...,
        description="WHO IITT / ESI: critical=Red/1, high=Red/2, medium=Yellow/3, low=Green/4-5",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence 0.0–1.0. If < 0.85, force_high_priority must be True.",
    )
    recommendations: list[str] = Field(default_factory=list)
    force_high_priority: bool = Field(
        default=False,
        description="True when confidence < 85%; treat as high priority.",
    )
    safety_disclaimer: str | None = Field(
        default=None,
        description="Required disclaimer for AI-generated medical guidance.",
    )
