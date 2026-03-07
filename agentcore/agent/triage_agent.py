"""
Triage AgentCore agent.

Receives patient symptoms/vitals, optionally uses Eka Gateway tools (search_medications,
search_protocols), returns JSON matching TriageResult (severity, confidence,
recommendations, force_high_priority, safety_disclaimer).
"""

import json
import logging

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

from gateway_client import (
    _is_gateway_configured,
    search_medications_via_gateway,
    search_protocols_via_gateway,
)

logger = logging.getLogger(__name__)

TRIAGE_SYSTEM_PROMPT = """You are an emergency medical triage assistant for rural India. Assess patients based on symptoms and vitals using WHO IITT and ESI standards.

Severity: critical (Red/1), high (Red/2), medium (Yellow/3), low (Green/4-5).
If confidence < 85%, set force_high_priority to true.
Always include safety_disclaimer: "This is AI-assisted guidance. Seek professional medical care."

Safety boundaries: Triage only. Do not prescribe specific drugs or doses. Do not diagnose by condition name. Do not replace a physician. If the user asks something unrelated to emergency triage, return JSON with a single recommendation: "I can only assist with emergency triage. Please provide the patient's symptoms and vitals." and severity=medium, confidence=0.5, force_high_priority=false.

You may call search_indian_medications or search_treatment_protocols if needed for drug or protocol lookup. Then return a single JSON object with exactly: severity, confidence (0-1), recommendations (array of strings), force_high_priority (boolean), safety_disclaimer (string). No other text."""

app = BedrockAgentCoreApp()


@tool
def search_indian_medications_tool(
    drug_name: str | None = None,
    form: str | None = None,
    generic_names: str | None = None,
) -> str:
    """Search Indian branded drugs (Eka). Use for drug names, forms, or generic composition before finalizing triage."""
    if not _is_gateway_configured():
        return json.dumps({"medications": [], "message": "Gateway not configured"})
    out = search_medications_via_gateway(
        drug_name=drug_name,
        form=form,
        generic_names=generic_names,
    )
    return json.dumps(out.get("medications", out), indent=2)


@tool
def search_treatment_protocols_tool(queries: str) -> str:
    """Search Indian treatment protocols (ICMR, RSSDI). Pass a JSON string array of objects with query, tag, publisher."""
    if not _is_gateway_configured():
        return json.dumps({"protocols": [], "message": "Gateway not configured"})
    try:
        q = json.loads(queries) if isinstance(queries, str) else queries
    except json.JSONDecodeError:
        q = []
    out = search_protocols_via_gateway(queries=q)
    return json.dumps(out.get("protocols", out), indent=2)


def _build_prompt(payload: dict) -> str:
    parts = [
        "Assess this patient and return one JSON object with severity, confidence, recommendations, force_high_priority, safety_disclaimer.",
        "",
        "Symptoms: " + ", ".join(payload.get("symptoms", [])),
        "Vitals: " + json.dumps(payload.get("vitals") or {}),
    ]
    if payload.get("age_years") is not None:
        parts.append(f"Age: {payload['age_years']} years")
    if payload.get("sex"):
        parts.append(f"Sex: {payload['sex']}")
    return "\n".join(parts)


def _parse_triage_result(content: str) -> dict | None:
    """Extract TriageResult-shaped dict from agent response (JSON or markdown code block)."""
    content = (content or "").strip()
    if not content:
        return None
    if content.startswith("```"):
        lines = content.split("\n")
        start = next(
            (i for i, ln in enumerate(lines) if "```json" in ln or ln.strip() == "```"),
            0,
        )
        end = next(
            (i for i in range(start + 1, len(lines)) if lines[i].strip() == "```"),
            len(lines),
        )
        content = "\n".join(lines[start + 1 : end])
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    for key in ("severity", "confidence", "recommendations", "force_high_priority", "safety_disclaimer"):
        if key not in data:
            return None
    severity = data.get("severity", "high")
    if severity not in ("critical", "high", "medium", "low"):
        data["severity"] = "high"
    conf = data.get("confidence", 0.5)
    if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
        data["confidence"] = 0.5
    if not isinstance(data.get("recommendations"), list):
        data["recommendations"] = []
    if data.get("force_high_priority") is None:
        data["force_high_priority"] = data.get("confidence", 0.5) < 0.85
    if not data.get("safety_disclaimer"):
        data["safety_disclaimer"] = "This is AI-assisted guidance. Seek professional medical care."
    return data


@app.entrypoint
def triage(payload: dict) -> dict:
    """Entrypoint: triage assessment from symptoms/vitals. Returns TriageResult-shaped dict."""
    tools = [search_indian_medications_tool, search_treatment_protocols_tool]
    try:
        agent = Agent(tools=tools)
        prompt = TRIAGE_SYSTEM_PROMPT + "\n\n" + _build_prompt(payload)
        result = agent(prompt)
        msg = result.message if hasattr(result, "message") else result
        content = ""
        if isinstance(msg, dict):
            content = msg.get("content", "")
        elif hasattr(msg, "content"):
            content = msg.content or ""
        else:
            content = str(msg)
        if isinstance(content, list):
            content = "".join(
                c.get("text", "") if isinstance(c, dict) else str(getattr(c, "text", c))
                for c in content
            )
        parsed = _parse_triage_result(content)
        if parsed:
            return parsed
    except Exception as e:
        logger.exception("Triage agent failed: %s", e)
    return {
        "severity": "high",
        "confidence": 0.0,
        "recommendations": ["Unable to complete assessment. Treat as high priority."],
        "force_high_priority": True,
        "safety_disclaimer": "This is AI-assisted guidance. Seek professional medical care.",
    }


if __name__ == "__main__":
    app.run()
