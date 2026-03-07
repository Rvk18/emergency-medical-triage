"""Hospital matching request and result models. G1/G2: input and output validation."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

SeverityLevel = Literal["critical", "high", "medium", "low"]

# G1/G2 bounds
RECOMMENDATIONS_MAX_ITEMS = 100
HOSPITALS_MAX_ITEMS = 20
SAFETY_DISCLAIMER_MAX_LENGTH = 1000
HOSPITAL_NAME_MAX_LENGTH = 200
MATCH_REASONS_MAX_ITEMS = 20
MATCH_REASON_MAX_LENGTH = 200


class MatchedHospital(BaseModel):
    """A single hospital match recommendation. G2: max lengths."""

    hospital_id: str = Field(..., max_length=64, description="Hospital identifier")
    name: str = Field(..., max_length=HOSPITAL_NAME_MAX_LENGTH, description="Hospital name")
    match_score: float = Field(..., ge=0, le=1, description="Match score 0–1")
    match_reasons: list[str] = Field(default_factory=list, max_length=MATCH_REASONS_MAX_ITEMS)
    estimated_minutes: int | None = Field(default=None, ge=0)
    specialties: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("match_reasons", mode="before")
    @classmethod
    def match_reasons_truncate(cls, v):
        if isinstance(v, list):
            return [str(x)[:MATCH_REASON_MAX_LENGTH] if x is not None else "" for x in v[:MATCH_REASONS_MAX_ITEMS]]
        return v


class HospitalMatchRequest(BaseModel):
    """Input for hospital matching. G1: severity enum, limit, lat/lon bounds."""

    triage_assessment_id: str | None = Field(default=None, max_length=64)
    severity: SeverityLevel = Field(..., description="critical|high|medium|low")
    recommendations: list[str] = Field(default_factory=list, max_length=RECOMMENDATIONS_MAX_ITEMS)
    patient_location_lat: float | None = Field(default=None, ge=-90, le=90)
    patient_location_lon: float | None = Field(default=None, ge=-180, le=180)
    limit: int = Field(default=3, ge=1, le=10)
    session_id: str | None = Field(default=None, max_length=256)
    patient_id: str | None = Field(default=None, max_length=256)


class HospitalMatchResult(BaseModel):
    """Output of hospital matching. G2: max hospitals count and disclaimer length."""

    hospitals: list[MatchedHospital] = Field(default_factory=list, max_length=HOSPITALS_MAX_ITEMS)
    safety_disclaimer: str | None = Field(default=None, max_length=SAFETY_DISCLAIMER_MAX_LENGTH)

    @field_validator("hospitals", mode="before")
    @classmethod
    def hospitals_truncate(cls, v):
        if isinstance(v, list):
            return v[:HOSPITALS_MAX_ITEMS]
        return v

    @field_validator("safety_disclaimer", mode="before")
    @classmethod
    def safety_disclaimer_truncate(cls, v):
        if v is not None and isinstance(v, str) and len(v) > SAFETY_DISCLAIMER_MAX_LENGTH:
            return v[:SAFETY_DISCLAIMER_MAX_LENGTH]
        return v
