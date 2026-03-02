"""Tool definitions for hospital matcher."""

SUBMIT_HOSPITAL_MATCHES_SCHEMA = {
    "type": "object",
    "properties": {
        "hospitals": {
            "type": "array",
            "description": "Top 3 hospital recommendations with id, name, score, match_reasons.",
            "items": {
                "type": "object",
                "properties": {
                    "hospital_id": {"type": "string", "description": "Unique ID (e.g. stub-1, hospital-001)"},
                    "name": {"type": "string", "description": "Hospital name"},
                    "match_score": {"type": "number", "minimum": 0, "maximum": 1, "description": "Relevance 0-1"},
                    "match_reasons": {"type": "array", "items": {"type": "string"}, "description": "Why this hospital fits"},
                    "estimated_minutes": {"type": "integer", "minimum": 0, "description": "Travel time if known"},
                    "specialties": {"type": "array", "items": {"type": "string"}, "description": "Relevant specialties"},
                },
                "required": ["hospital_id", "name", "match_score"],
            },
            "maxItems": 10,
        },
        "safety_disclaimer": {"type": "string", "description": "Required disclaimer for transport."},
    },
    "required": ["hospitals", "safety_disclaimer"],
}


def get_hospital_matcher_tool_config():
    """Return Converse API toolConfig for submit_hospital_matches."""
    return {
        "tools": [
            {
                "toolSpec": {
                    "name": "submit_hospital_matches",
                    "description": "Submit hospital match recommendations. Call with hospitals list and safety_disclaimer.",
                    "inputSchema": {"json": SUBMIT_HOSPITAL_MATCHES_SCHEMA},
                }
            }
        ],
        "toolChoice": {"tool": {"name": "submit_hospital_matches"}},
    }
