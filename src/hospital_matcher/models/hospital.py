"""Hospital matching request and result models."""

from pydantic import BaseModel, Field


class MatchedHospital(BaseModel):
    """A single hospital match recommendation."""

    hospital_id: str = Field(..., description="Hospital identifier")
    name: str = Field(..., description="Hospital name")
    match_score: float = Field(..., ge=0, le=1, description="Match score 0–1")
    match_reasons: list[str] = Field(default_factory=list)
    estimated_minutes: int | None = Field(default=None, ge=0)
    specialties: list[str] = Field(default_factory=list)


class HospitalMatchRequest(BaseModel):
    """Input for hospital matching."""

    triage_assessment_id: str | None = Field(default=None)
    severity: str = Field(..., description="critical|high|medium|low")
    recommendations: list[str] = Field(default_factory=list)
    patient_location_lat: float | None = None
    patient_location_lon: float | None = None
    limit: int = Field(default=3, ge=1, le=10)


class HospitalMatchResult(BaseModel):
    """Output of hospital matching."""

    hospitals: list[MatchedHospital] = Field(default_factory=list)
    safety_disclaimer: str | None = None
