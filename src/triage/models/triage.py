"""Triage request and result models. Strict schema aligned with WHO IITT / ESI."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

SeverityLevel = Literal["critical", "high", "medium", "low"]

# G1: Input validation bounds
SYMPTOMS_MAX_ITEMS = 50
SYMPTOM_MAX_LENGTH = 500
VITALS_RANGES = {
    "heart_rate": (20, 300),
    "heartRateBpm": (20, 300),
    "blood_pressure_systolic": (50, 300),
    "bp": (50, 300),
    "blood_pressure_diastolic": (30, 200),
    "spo2": (0, 100),
    "temp_c": (30, 45),
    "temperature_f": (86, 113),
    "respiratory_rate": (5, 60),
}
RECOMMENDATIONS_MAX_ITEMS = 30
RECOMMENDATION_MAX_LENGTH = 500
SAFETY_DISCLAIMER_MAX_LENGTH = 1000


class TriageRequest(BaseModel):
    """Input for triage assessment. G1: validated lengths and vitals ranges."""

    symptoms: list[str] = Field(
        ...,
        min_length=1,
        max_length=SYMPTOMS_MAX_ITEMS,
        description="Patient symptoms (max 50 items)",
    )
    vitals: dict[str, float] = Field(default_factory=dict, description="Vital signs (validated ranges)")
    age_years: int | None = Field(default=None, ge=0, le=150)
    sex: str | None = None
    submitted_by: str | None = Field(default=None, max_length=256, description="RMP ID or user identifier")
    session_id: str | None = Field(default=None, max_length=256, description="Optional: reuse AgentCore session")
    patient_id: str | None = Field(default=None, max_length=256, description="Optional: patient identifier")

    @field_validator("symptoms", mode="before")
    @classmethod
    def symptoms_items_length(cls, v):
        if isinstance(v, list):
            for i, s in enumerate(v):
                if isinstance(s, str) and len(s) > SYMPTOM_MAX_LENGTH:
                    v = list(v)
                    v[i] = s[:SYMPTOM_MAX_LENGTH]
        return v

    @field_validator("vitals", mode="after")
    @classmethod
    def vitals_ranges(cls, v: dict[str, float]) -> dict[str, float]:
        if not v:
            return v
        out = {}
        for key, val in v.items():
            if not isinstance(val, (int, float)):
                continue
            r = VITALS_RANGES.get(key)
            if r:
                lo, hi = r
                out[key] = float(max(lo, min(hi, val)))
            else:
                out[key] = float(val)
        return out


class TriageResult(BaseModel):
    """Output of triage assessment. G2: validated enums and max lengths."""

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
    recommendations: list[str] = Field(
        default_factory=list,
        max_length=RECOMMENDATIONS_MAX_ITEMS,
        description="Action items (max 30, each max 500 chars)",
    )
    force_high_priority: bool = Field(
        default=False,
        description="True when confidence < 85%; treat as high priority.",
    )
    safety_disclaimer: str | None = Field(
        default=None,
        max_length=SAFETY_DISCLAIMER_MAX_LENGTH,
        description="Required disclaimer for AI-generated medical guidance.",
    )
    session_id: str | None = Field(
        default=None,
        max_length=256,
        description="Session ID used for AgentCore (echo or generated); use for /hospitals and /route.",
    )

    @field_validator("recommendations", mode="before")
    @classmethod
    def recommendations_truncate(cls, v):
        if isinstance(v, list):
            out = []
            for s in v[:RECOMMENDATIONS_MAX_ITEMS]:
                t = str(s)[:RECOMMENDATION_MAX_LENGTH] if s is not None else ""
                out.append(t)
            return out
        return v

    @field_validator("safety_disclaimer", mode="before")
    @classmethod
    def safety_disclaimer_truncate(cls, v):
        if v is not None and isinstance(v, str) and len(v) > SAFETY_DISCLAIMER_MAX_LENGTH:
            return v[:SAFETY_DISCLAIMER_MAX_LENGTH]
        return v
