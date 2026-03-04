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
