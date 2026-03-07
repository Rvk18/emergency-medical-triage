"""
Hospital Matcher AgentCore agent.

Receives triage input, uses get_hospitals from Gateway MCP (when configured) or in-agent
synthetic tool, returns JSON with hospitals + safety_disclaimer.
When patient location is provided, can call get_route_tool (Gateway maps) to add per-hospital
distance_km, duration_minutes, directions_url – Hospital Matcher calls routing (maps) via Gateway.
"""

import json
import logging

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

from gateway_client import (
    _is_gateway_configured,
    get_hospitals_via_gateway,
    get_route_via_gateway,
)
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


@tool
def get_route_tool(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
) -> dict:
    """Get driving distance, duration, and directions URL from origin to destination. Use when patient location and hospital lat/lon are known. Returns distance_km, duration_minutes, directions_url."""
    if not _is_gateway_configured():
        return {"distance_km": None, "duration_minutes": None, "directions_url": None, "stub": True}
    try:
        return get_route_via_gateway(
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
        )
    except Exception as e:
        logger.warning("get_route_tool failed: %s", e)
        return {"error": str(e), "distance_km": None, "duration_minutes": None, "directions_url": None}


def _build_prompt(payload: dict) -> str:
    """Build user prompt. G3: safety boundary—hospital matching only."""
    severity = payload.get("severity", "medium")
    recommendations = payload.get("recommendations", [])
    limit = payload.get("limit", 3)
    rec_str = ", ".join(recommendations) if recommendations else "None"
    parts = [
        "You are a hospital matching assistant. You only match hospitals to triage results. Do not give clinical advice. Always include safety_disclaimer: 'Hospital availability may change. Confirm with facility before transport.'",
        "",
        f"Match hospitals for: severity={severity}, recommendations=[{rec_str}], limit={limit}.",
        "Call get_synthetic_hospitals_tool, then return the top hospitals as JSON with hospitals and safety_disclaimer.",
    ]
    if payload.get("patient_location_lat") is not None and payload.get("patient_location_lon") is not None:
        parts.append(
            "Patient location is provided. For each hospital that has lat and lon, call get_route_tool(origin_lat=patient_location_lat, origin_lon=patient_location_lon, dest_lat=hospital.lat, dest_lon=hospital.lon) and add distance_km, duration_minutes, and directions_url to that hospital in your final JSON."
        )
    return "\n".join(parts)


@app.entrypoint
def hospital_matcher(payload: dict) -> dict:
    """Entrypoint: match hospitals for triage result. When patient location given, includes route info via get_route_tool."""
    try:
        agent = Agent(tools=[get_synthetic_hospitals_tool, get_route_tool])
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
