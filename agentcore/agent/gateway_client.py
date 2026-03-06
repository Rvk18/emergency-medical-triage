"""
Call AgentCore Gateway MCP tools via HTTP (OAuth client_credentials + JSON-RPC tools/call).

Used by the Hospital Matcher agent when GATEWAY_MCP_URL and OAuth env vars are set.
Tool name for get_hospitals: get-hospitals-target___get_hospitals
"""

import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

GET_HOSPITALS_TOOL_NAME = "get-hospitals-target___get_hospitals"

_token: str | None = None
_token_expires_at: float = 0
_TOKEN_BUFFER_SECONDS = 300


def _is_gateway_configured() -> bool:
    """True when all required Gateway OAuth env vars are set (read at call time)."""
    url = os.environ.get("GATEWAY_MCP_URL", "").strip()
    cid = os.environ.get("GATEWAY_CLIENT_ID", "").strip()
    secret = os.environ.get("GATEWAY_CLIENT_SECRET", "").strip()
    endpoint = os.environ.get("GATEWAY_TOKEN_ENDPOINT", "").strip()
    return bool(url and cid and secret and endpoint)


def _get_token() -> str:
    """Sync OAuth client_credentials token; cache with buffer."""
    global _token, _token_expires_at
    now = time.time()
    if _token and _token_expires_at > now + _TOKEN_BUFFER_SECONDS:
        return _token

    url = os.environ.get("GATEWAY_MCP_URL", "").strip()
    cid = os.environ.get("GATEWAY_CLIENT_ID", "").strip()
    secret = os.environ.get("GATEWAY_CLIENT_SECRET", "").strip()
    endpoint = os.environ.get("GATEWAY_TOKEN_ENDPOINT", "").strip()
    scope = os.environ.get("GATEWAY_SCOPE", "").strip() or "bedrock-agentcore-gateway"

    try:
        import urllib.request
        import urllib.parse

        data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": cid,
            "client_secret": secret,
            "scope": scope,
        }).encode("utf-8")

        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        _token = body.get("access_token")
        if not _token:
            raise ValueError("No access_token in OAuth response")
        expires_in = int(body.get("expires_in", 3600)) - _TOKEN_BUFFER_SECONDS
        _token_expires_at = now + max(expires_in, 60)
        return _token
    except Exception as e:
        logger.warning("Gateway OAuth token fetch failed: %s", e)
        raise


def call_gateway_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Call a Gateway MCP tool via JSON-RPC tools/call.
    Returns the tool result dict; raises on error.
    """
    token = _get_token()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    url = os.environ.get("GATEWAY_MCP_URL", "").strip()
    import urllib.request

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    if "error" in result:
        raise RuntimeError(f"Gateway tool error: {result['error']}")

    return result.get("result") or {}


def get_hospitals_via_gateway(severity: str, limit: int = 3) -> dict[str, Any]:
    """
    Call Gateway get_hospitals tool. Returns {hospitals: [...], safety_disclaimer: str}.
    """
    return call_gateway_tool(
        GET_HOSPITALS_TOOL_NAME,
        {"severity": severity, "limit": limit},
    )


# Eka tools (for Triage agent; same Gateway, eka-target)
EKA_SEARCH_MEDICATIONS = "eka-target___search_medications"
EKA_SEARCH_PROTOCOLS = "eka-target___search_protocols"


def search_medications_via_gateway(
    drug_name: str | None = None,
    form: str | None = None,
    generic_names: str | None = None,
) -> dict[str, Any]:
    """Call Gateway Eka search_medications. Returns {medications: [...]} or stub."""
    args = {}
    if drug_name:
        args["drug_name"] = drug_name
    if form:
        args["form"] = form
    if generic_names:
        args["generic_names"] = generic_names
    try:
        return call_gateway_tool(EKA_SEARCH_MEDICATIONS, args)
    except Exception as e:
        logger.warning("Eka search_medications failed: %s", e)
        return {"medications": [], "error": str(e)}


def search_protocols_via_gateway(queries: list[dict] | None = None) -> dict[str, Any]:
    """Call Gateway Eka search_protocols. Returns {protocols: [...]} or stub."""
    try:
        return call_gateway_tool(EKA_SEARCH_PROTOCOLS, {"queries": queries or []})
    except Exception as e:
        logger.warning("Eka search_protocols failed: %s", e)
        return {"protocols": [], "error": str(e)}


# Maps tool (for Hospital Matcher – directions between origin and destination)
GET_DIRECTIONS_TOOL_NAME = "maps-target___get_directions"
ROUTING_TARGET_GET_ROUTE = "routing-target___get_route"


def get_directions_via_gateway(
    origin_lat: float | None = None,
    origin_lon: float | None = None,
    dest_lat: float | None = None,
    dest_lon: float | None = None,
    origin_address: str | None = None,
    dest_address: str | None = None,
) -> dict[str, Any]:
    """
    Call Gateway get_directions tool. Returns {distance_km, duration_minutes, directions_url} or stub.
    """
    args: dict[str, Any] = {}
    if origin_lat is not None and origin_lon is not None:
        args["origin_lat"] = origin_lat
        args["origin_lon"] = origin_lon
    if dest_lat is not None and dest_lon is not None:
        args["dest_lat"] = dest_lat
        args["dest_lon"] = dest_lon
    if origin_address:
        args["origin_address"] = origin_address
    if dest_address:
        args["dest_address"] = dest_address
    try:
        return call_gateway_tool(GET_DIRECTIONS_TOOL_NAME, args)
    except Exception as e:
        logger.warning("Gateway get_directions failed: %s", e)
        return {"error": str(e), "distance_km": None, "duration_minutes": None, "directions_url": None}


def get_route_via_gateway(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> dict[str, Any]:
    """Call the Routing agent via Gateway (routing-target___get_route). The Routing agent uses Google Maps MCP."""
    args = {"origin_lat": origin_lat, "origin_lon": origin_lon, "dest_lat": dest_lat, "dest_lon": dest_lon}
    try:
        return call_gateway_tool(ROUTING_TARGET_GET_ROUTE, args)
    except Exception as e:
        logger.warning("Gateway get_route (Routing agent) failed: %s", e)
        return {"error": str(e), "distance_km": None, "duration_minutes": None, "directions_url": None}
