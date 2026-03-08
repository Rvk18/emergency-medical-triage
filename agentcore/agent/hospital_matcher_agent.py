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
        "You are a hospital matching assistant. You only match hospitals to triage results. Do not give clinical advice. Do not ask the user for information that is already provided.",
        "Output only a single JSON object with keys 'hospitals' (array) and 'safety_disclaimer' (string). No other text before or after.",
        "",
        f"Match hospitals for: severity={severity}, recommendations=[{rec_str}], limit={limit}.",
        "Step 1: Call get_synthetic_hospitals_tool(severity=..., limit=...) to get the hospital list.",
        "Step 2: If patient_location_lat and patient_location_lon are provided below, for each hospital that has lat and lon, call get_route_tool(origin_lat=<patient_lat>, origin_lon=<patient_lon>, dest_lat=hospital.lat, dest_lon=hospital.lon) and add distance_km, duration_minutes, directions_url to that hospital object.",
        "Step 3: Return the JSON object with hospitals (and safety_disclaimer: 'Hospital availability may change. Confirm with facility before transport.').",
    ]
    plat = payload.get("patient_location_lat")
    plon = payload.get("patient_location_lon")
    if plat is not None and plon is not None:
        parts.append("")
        parts.append(f"Patient location (use these as origin for get_route_tool): patient_location_lat={plat}, patient_location_lon={plon}.")
    return "\n".join(parts)


def _enrich_hospitals_with_routes(data: dict, payload: dict) -> dict:
    """When patient location is provided and Gateway is configured, add distance_km, duration_minutes, directions_url to each hospital that has lat/lon and is missing them. Skip if agent already added route info to avoid duplicate Gateway calls (which contribute to API Gateway 29s timeout → 504). Uses only lat/lon from agent response (no second get_hospitals call) to stay under 29s."""
    plat = payload.get("patient_location_lat")
    plon = payload.get("patient_location_lon")
    if plat is None or plon is None or not _is_gateway_configured():
        return data
    hospitals = data.get("hospitals") or []
    if not hospitals:
        return data
    # Skip enrichment if agent already added route info for all hospitals (avoids duplicate get_route calls and reduces 504 risk)
    if all(
        h.get("directions_url") and h.get("distance_km") is not None
        for h in hospitals
    ):
        return data
    # Use only lat/lon from agent's hospital objects (from get_hospitals tool result). Do NOT call get_hospitals again here—that extra Gateway call was causing 504 (2× get_hospitals + N× get_route > 29s).
    enriched = []
    for h in hospitals:
        h = dict(h)
        lat, lon = h.get("lat"), h.get("lon")
        if lat is not None and lon is not None and (h.get("directions_url") is None or h.get("distance_km") is None):
            try:
                route = get_route_via_gateway(
                    origin_lat=float(plat),
                    origin_lon=float(plon),
                    dest_lat=float(lat),
                    dest_lon=float(lon),
                )
                h["distance_km"] = route.get("distance_km")
                h["duration_minutes"] = route.get("duration_minutes")
                h["directions_url"] = route.get("directions_url")
                if route.get("duration_minutes") is not None:
                    h["estimated_minutes"] = int(round(float(route["duration_minutes"])))
            except Exception as e:
                logger.warning("Enrich route for %s failed: %s", h.get("hospital_id"), e)
        enriched.append(h)
    data["hospitals"] = enriched
    return data


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
            # Enrich with route info when patient location provided and Gateway configured (guarantees directions)
            data = _enrich_hospitals_with_routes(data, payload)
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
