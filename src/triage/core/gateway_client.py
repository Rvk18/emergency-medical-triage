"""
Gateway MCP client for Lambda (sync). Used by Triage to call Eka tools when configured.
"""

import json
import logging
import os
import time
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

_TOKEN_BUFFER = 300

_token: str | None = None
_token_expires_at: float = 0


def is_gateway_configured() -> bool:
    """True when all required Gateway OAuth env vars are set (read at call time)."""
    url = os.environ.get("GATEWAY_MCP_URL", "").strip()
    cid = os.environ.get("GATEWAY_CLIENT_ID", "").strip()
    secret = os.environ.get("GATEWAY_CLIENT_SECRET", "").strip()
    endpoint = os.environ.get("GATEWAY_TOKEN_ENDPOINT", "").strip()
    return bool(url and cid and secret and endpoint)


def _get_token() -> str:
    global _token, _token_expires_at
    now = time.time()
    if _token and _token_expires_at > now + _TOKEN_BUFFER:
        return _token
    url = os.environ.get("GATEWAY_MCP_URL", "").strip()
    cid = os.environ.get("GATEWAY_CLIENT_ID", "").strip()
    secret = os.environ.get("GATEWAY_CLIENT_SECRET", "").strip()
    endpoint = os.environ.get("GATEWAY_TOKEN_ENDPOINT", "").strip()
    scope = os.environ.get("GATEWAY_SCOPE", "").strip() or "bedrock-agentcore-gateway"
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
    _token_expires_at = now + max(int(body.get("expires_in", 3600)) - _TOKEN_BUFFER, 60)
    return _token


def call_gateway_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call Gateway MCP tools/call. Returns result dict."""
    token = _get_token()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    url = os.environ.get("GATEWAY_MCP_URL", "").strip()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if "error" in result:
        raise RuntimeError(f"Gateway tool error: {result['error']}")
    return result.get("result") or {}


def search_medications(drug_name: str | None = None, form: str | None = None, generic_names: str | None = None) -> dict:
    """Call eka-target___search_medications."""
    args = {}
    if drug_name:
        args["drug_name"] = drug_name
    if form:
        args["form"] = form
    if generic_names:
        args["generic_names"] = generic_names
    return call_gateway_tool("eka-target___search_medications", args)


def search_protocols(queries: list[dict]) -> dict:
    """Call eka-target___search_protocols. queries: list of {query, tag, publisher}."""
    return call_gateway_tool("eka-target___search_protocols", {"queries": queries})
