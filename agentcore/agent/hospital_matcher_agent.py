"""
Hospital Matcher AgentCore agent.

Receives triage input, uses get_hospitals from Gateway MCP (when configured) or in-agent
synthetic tool, returns JSON with hospitals + safety_disclaimer.
"""

import json
import logging

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

from gateway_client import _is_gateway_configured, get_hospitals_via_gateway
from synthetic_hospitals import get_synthetic_hospitals

logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()


@tool
def get_synthetic_hospitals_tool(severity: str, limit: int = 3) -> dict:
    """Get hospital recommendations for the given severity. Use this to fetch hospital options before returning your final recommendation. When Gateway is configured, uses Gateway MCP get_hospitals; otherwise synthetic data."""
    if _is_gateway_configured():
        try:
            return get_hospitals_via_gateway(severity=severity, limit=limit)
        except Exception as e:
            logger.warning("Gateway get_hospitals failed, falling back to synthetic: %s", e)
    return get_synthetic_hospitals(severity=severity, limit=limit)


def _build_prompt(payload: dict) -> str:
    severity = payload.get("severity", "medium")
    recommendations = payload.get("recommendations", [])
    limit = payload.get("limit", 3)
    rec_str = ", ".join(recommendations) if recommendations else "None"
    parts = [
        f"Match hospitals for: severity={severity}, recommendations=[{rec_str}], limit={limit}.",
        "Call get_synthetic_hospitals_tool, then return the top hospitals as JSON with hospitals and safety_disclaimer.",
    ]
    if payload.get("patient_location_lat") and payload.get("patient_location_lon"):
        parts.append(f"Patient location: {payload['patient_location_lat']}, {payload['patient_location_lon']}")
    return "\n".join(parts)


@app.entrypoint
def hospital_matcher(payload: dict) -> dict:
    """Entrypoint: match hospitals for triage result."""
    try:
        agent = Agent(tools=[get_synthetic_hospitals_tool])
        prompt = _build_prompt(payload)
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
        # Try to parse JSON from response
        content = (content or "").strip()
        if not content:
            return get_synthetic_hospitals(
                severity=payload.get("severity", "medium"),
                limit=payload.get("limit", 3),
            )
        if content.startswith("```"):
            lines = content.split("\n")
            start = next((i for i, ln in enumerate(lines) if "```json" in ln or ln.strip() == "```"), 0)
            end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "```"), len(lines))
            content = "\n".join(lines[start + 1 : end])
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return get_synthetic_hospitals(
                severity=payload.get("severity", "medium"),
                limit=payload.get("limit", 3),
            )
        if "hospitals" in data:
            return data
        # Fallback if model didn't return expected shape
        return get_synthetic_hospitals(
            severity=payload.get("severity", "medium"),
            limit=payload.get("limit", 3),
        )
    except Exception as e:
        logger.exception("Hospital matcher failed: %s", e)
        return get_synthetic_hospitals(
            severity=payload.get("severity", "medium"),
            limit=payload.get("limit", 3),
        )


if __name__ == "__main__":
    app.run()
