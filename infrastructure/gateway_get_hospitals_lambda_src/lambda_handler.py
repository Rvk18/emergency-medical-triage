"""
AgentCore Gateway Lambda handler for get_hospitals tool.

Event: tool input props (severity, limit).
Context: bedrockAgentCoreToolName in client_context.custom (format: TARGET___tool_name).
Returns: synthetic Indian hospital data matching agentcore/agent/synthetic_hospitals.py.
"""

import json
import logging

logger = logging.getLogger(__name__)

DELIMITER = "___"
SAFETY_DISCLAIMER = "Hospital availability may change. Confirm with facility before transport."

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


def get_synthetic_hospitals(severity: str, limit: int = 3) -> dict:
    """Return synthetic hospital matches for the given severity."""
    severity_key = (severity or "medium").lower()
    pool = HOSPITAL_POOL.get(severity_key, HOSPITAL_POOL["medium"])
    selected = pool[: min(limit, len(pool))]
    hospitals = [
        {"hospital_id": h[0], "name": h[1], "match_score": h[2], "match_reasons": h[3]}
        for h in selected
    ]
    return {"hospitals": hospitals, "safety_disclaimer": SAFETY_DISCLAIMER}


def _strip_tool_prefix(full_name: str) -> str:
    """Strip TARGET___ prefix from tool name."""
    if not full_name or DELIMITER not in full_name:
        return full_name or ""
    return full_name[full_name.index(DELIMITER) + len(DELIMITER) :]


def handler(event: dict, context: object) -> dict:
    """
    Gateway Lambda target handler.
    Event: {severity: str, limit?: int}
    Context: client_context.custom has bedrockAgentCoreToolName (e.g. TARGET___get_hospitals)
    """
    tool_name = "get_hospitals"
    try:
        custom = getattr(context, "client_context", None)
        if custom and hasattr(custom, "custom") and custom.custom:
            raw = custom.custom.get("bedrockAgentCoreToolName")
            if raw:
                tool_name = _strip_tool_prefix(raw) or "get_hospitals"
    except Exception as e:
        logger.warning("Could not read tool name from context: %s", e)

    if tool_name != "get_hospitals":
        return {
            "error": f"Unknown tool: {tool_name}",
            "hospitals": [],
            "safety_disclaimer": SAFETY_DISCLAIMER,
        }

    severity = event.get("severity", "medium")
    limit = event.get("limit", 3)
    try:
        limit = int(limit) if limit is not None else 3
    except (TypeError, ValueError):
        limit = 3
    limit = max(1, min(limit, 10))

    result = get_synthetic_hospitals(severity=severity, limit=limit)
    return result
