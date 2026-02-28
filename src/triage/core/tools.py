"""Tool definitions for triage (Claude Cookbook pattern: strict input_schema)."""

# JSON schema for submit_triage_result tool - matches TriageResult Pydantic model
SUBMIT_TRIAGE_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"],
            "description": "WHO IITT/ESI: critical=Red/1, high=Red/2, medium=Yellow/3, low=Green/4-5",
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confidence 0.0-1.0. If < 0.85, set force_high_priority to true.",
        },
        "recommendations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Recommended immediate actions",
        },
        "force_high_priority": {
            "type": "boolean",
            "description": "True when confidence < 85%; treat as high priority.",
        },
        "safety_disclaimer": {
            "type": "string",
            "description": "Required disclaimer for AI-generated medical guidance.",
        },
    },
    "required": ["severity", "confidence", "recommendations", "force_high_priority", "safety_disclaimer"],
    "additionalProperties": False,
}


def get_triage_tool_config():
    """Return Converse API toolConfig for submit_triage_result (tool use pattern)."""
    return {
        "tools": [
            {
                "toolSpec": {
                    "name": "submit_triage_result",
                    "description": "Submit the triage assessment result. Call this with severity, confidence, recommendations, force_high_priority, and safety_disclaimer.",
                    "inputSchema": {
                        "json": SUBMIT_TRIAGE_RESULT_SCHEMA,
                    },
                }
            }
        ],
        "toolChoice": {
            "tool": {
                "name": "submit_triage_result",
            }
        },
    }
