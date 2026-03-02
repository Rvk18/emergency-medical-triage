"""Synthetic hospital data for AgentCore Hospital Matcher (hackathon)."""

# Plausible Indian hospital names by tier
HOSPITAL_POOL = {
    "critical": [
        ("stub-1", "District Government Hospital - ICU", 0.95, ["24/7 ICU", "Emergency surgery", "Critical care"]),
        ("stub-2", "Medical College Hospital", 0.92, ["Multi-specialty", "Trauma center", "Blood bank"]),
        ("stub-3", "Apollo Speciality Hospital", 0.88, ["Critical care", "Ventilator support", "Nephrology"]),
    ],
    "high": [
        ("stub-1", "District Government Hospital - Emergency", 0.9, ["Emergency department", "Stabilisation", "X-ray/CT"]),
        ("stub-2", "Community Health Centre (CHC)", 0.85, ["Emergency care", "Minor surgery", "Lab facilities"]),
        ("stub-3", "Mission Hospital", 0.82, ["Emergency ward", "Obstetrics", "Paediatric care"]),
    ],
    "medium": [
        ("stub-1", "Primary Health Centre (PHC)", 0.85, ["General ward", "Basic emergency", "Outpatient"]),
        ("stub-2", "Sub-centre Clinic", 0.78, ["First aid", "Referral coordination", "Follow-up care"]),
        ("stub-3", "District Hospital - OPD", 0.75, ["General OPD", "Minor procedures", "Pharmacy"]),
    ],
    "low": [
        ("stub-1", "Primary Health Centre - OPD", 0.85, ["Outpatient", "Follow-up", "Prescriptions"]),
        ("stub-2", "Sub-centre", 0.8, ["Basic consultation", "Referral if needed"]),
        ("stub-3", "District Hospital - OPD", 0.78, ["Follow-up care", "Lab tests"]),
    ],
}

SAFETY_DISCLAIMER = "Hospital availability may change. Confirm with facility before transport."


def get_synthetic_hospitals(severity: str, limit: int = 3) -> dict:
    """Return synthetic hospital matches for the given severity."""
    severity_key = severity.lower() if severity else "medium"
    pool = HOSPITAL_POOL.get(severity_key, HOSPITAL_POOL["medium"])
    selected = pool[: min(limit, len(pool))]
    hospitals = [
        {"hospital_id": h[0], "name": h[1], "match_score": h[2], "match_reasons": h[3]}
        for h in selected
    ]
    return {"hospitals": hospitals, "safety_disclaimer": SAFETY_DISCLAIMER}
