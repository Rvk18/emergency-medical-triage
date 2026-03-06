"""
Routing AgentCore agent.

Gets driving route between origin and destination using the Google Maps MCP (Gateway maps-target).
Called by the Hospital Matcher agent via Gateway tool routing-target___get_route, and by POST /route.
"""

import json
import logging

from bedrock_agentcore import BedrockAgentCoreApp
from strands import tool

from gateway_client import _is_gateway_configured, get_directions_via_gateway

logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()


@tool
def get_directions_tool(
    origin_lat: float | None = None,
    origin_lon: float | None = None,
    dest_lat: float | None = None,
    dest_lon: float | None = None,
    origin_address: str | None = None,
    dest_address: str | None = None,
) -> dict:
    """Get driving distance, duration, and directions URL from origin to destination (Google Maps MCP). Pass coordinates or addresses."""
    if not _is_gateway_configured():
        return {"distance_km": None, "duration_minutes": None, "directions_url": None, "stub": True}
    try:
        return get_directions_via_gateway(
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
            origin_address=origin_address,
            dest_address=dest_address,
        )
    except Exception as e:
        logger.warning("get_directions_tool failed: %s", e)
        return {"error": str(e), "distance_km": None, "duration_minutes": None, "directions_url": None}


@app.entrypoint
def routing_agent(payload: dict) -> dict:
    """
    Entrypoint: return route info between origin and destination.
    Payload: origin { lat, lon } or { address }, destination { lat, lon } or { address }.
    Uses Google Maps MCP (get_directions_tool) and returns distance_km, duration_minutes, directions_url.
    """
    origin = payload.get("origin") or {}
    destination = payload.get("destination") or {}
    if not isinstance(origin, dict) or not isinstance(destination, dict):
        return {"error": "origin and destination must be objects", "distance_km": None, "duration_minutes": None, "directions_url": None}

    kwargs = {}
    if origin.get("lat") is not None and origin.get("lon") is not None:
        kwargs["origin_lat"] = float(origin["lat"])
        kwargs["origin_lon"] = float(origin["lon"])
    elif origin.get("address"):
        kwargs["origin_address"] = str(origin["address"]).strip()
    else:
        return {"error": "origin must have lat+lon or address", "distance_km": None, "duration_minutes": None, "directions_url": None}

    if destination.get("lat") is not None and destination.get("lon") is not None:
        kwargs["dest_lat"] = float(destination["lat"])
        kwargs["dest_lon"] = float(destination["lon"])
    elif destination.get("address"):
        kwargs["dest_address"] = str(destination["address"]).strip()
    else:
        return {"error": "destination must have lat+lon or address", "distance_km": None, "duration_minutes": None, "directions_url": None}

    try:
        return get_directions_tool(**kwargs)
    except Exception as e:
        logger.exception("Routing agent failed: %s", e)
        return {"error": str(e), "distance_km": None, "duration_minutes": None, "directions_url": None}


if __name__ == "__main__":
    app.run()
