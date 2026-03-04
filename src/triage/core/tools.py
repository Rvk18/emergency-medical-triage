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

# Eka Gateway tools (optional - when GATEWAY_MCP_URL etc. are set)
SEARCH_MEDICATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "drug_name": {"type": "string", "description": "Indian branded drug name e.g. Paracetamol 500mg"},
        "form": {"type": "string", "description": "Form e.g. Tablet, Syrup"},
        "generic_names": {"type": "string", "description": "Generic name(s), comma-separated"},
    },
}
SEARCH_PROTOCOLS_SCHEMA = {
    "type": "object",
    "properties": {
        "queries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "tag": {"type": "string"}, "publisher": {"type": "string"}},
                "required": ["query", "tag", "publisher"],
            },
            "description": "List of protocol search queries (ICMR, RSSDI)",
        },
    },
    "required": ["queries"],
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


def get_triage_tool_config_with_eka():
    """Tool config including Eka Gateway tools (search_medications, search_protocols). Use when Gateway is configured."""
    from triage.core.gateway_client import is_gateway_configured
    if not is_gateway_configured():
        return get_triage_tool_config()
    return {
        "tools": [
            {
                "toolSpec": {
                    "name": "search_indian_medications",
                    "description": "Search Indian branded drugs (Eka). Use for drug names, forms, or generic composition before finalizing triage.",
                    "inputSchema": {"json": SEARCH_MEDICATIONS_SCHEMA},
                }
            },
            {
                "toolSpec": {
                    "name": "search_treatment_protocols",
                    "description": "Search Indian treatment protocols (ICMR, RSSDI). Use for protocol guidance before finalizing triage.",
                    "inputSchema": {"json": SEARCH_PROTOCOLS_SCHEMA},
                }
            },
            {
                "toolSpec": {
                    "name": "submit_triage_result",
                    "description": "Submit the triage assessment result. Call this with severity, confidence, recommendations, force_high_priority, and safety_disclaimer.",
                    "inputSchema": {"json": SUBMIT_TRIAGE_RESULT_SCHEMA},
                }
            },
        ],
        "toolChoice": {"tool": {"name": "any"}},
    }
