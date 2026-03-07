"""
Gateway MCP client for Lambda (sync). Used by Triage to call Eka tools when configured.

Supports two modes:
- Env vars: GATEWAY_MCP_URL, GATEWAY_CLIENT_ID, GATEWAY_CLIENT_SECRET, GATEWAY_TOKEN_ENDPOINT
- Secret: GATEWAY_CONFIG_SECRET_NAME set → load gateway_url and client_info from Secrets Manager (same as Route Lambda)
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
_cached_config: dict | None = None


def _load_gateway_config_from_secret() -> dict | None:
    """Load gateway config from Secrets Manager when GATEWAY_CONFIG_SECRET_NAME is set."""
    global _cached_config
    if _cached_config is not None:
        return _cached_config
    secret_name = os.environ.get("GATEWAY_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        return None
    try:
        import boto3
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=secret_name)
        _cached_config = json.loads(resp["SecretString"])
        return _cached_config
    except Exception as e:
        logger.warning("Could not load gateway config from secret: %s", e)
        return None


def is_gateway_configured() -> bool:
    """True when Gateway is available: either env vars set or gateway_config secret has gateway_url and client_info."""
    if os.environ.get("GATEWAY_MCP_URL", "").strip():
        cid = os.environ.get("GATEWAY_CLIENT_ID", "").strip()
        secret = os.environ.get("GATEWAY_CLIENT_SECRET", "").strip()
        endpoint = os.environ.get("GATEWAY_TOKEN_ENDPOINT", "").strip()
        return bool(cid and secret and endpoint)
    config = _load_gateway_config_from_secret()
    if not config:
        return False
    url = (config.get("gateway_url") or "").strip()
    ci = config.get("client_info") or {}
    return bool(url and ci.get("client_id") and ci.get("client_secret") and ci.get("token_endpoint"))


def _get_gateway_url() -> str:
    """Gateway MCP URL (with /mcp if needed)."""
    url = os.environ.get("GATEWAY_MCP_URL", "").strip()
    if not url:
        config = _load_gateway_config_from_secret()
        if config:
            url = (config.get("gateway_url") or "").strip()
    if not url:
        return ""
    if not url.endswith("/mcp"):
        url = url.rstrip("/") + "/mcp"
    return url


def _get_token() -> str:
    global _token, _token_expires_at
    now = time.time()
    if _token and _token_expires_at > now + _TOKEN_BUFFER:
        return _token

    config = _load_gateway_config_from_secret()
    if config:
        ci = config.get("client_info") or {}
        endpoint = (ci.get("token_endpoint") or "").strip()
        cid = (ci.get("client_id") or "").strip()
        secret = (ci.get("client_secret") or "").strip()
        scope = (ci.get("scope") or "").strip() or "bedrock-agentcore-gateway"
    else:
        endpoint = os.environ.get("GATEWAY_TOKEN_ENDPOINT", "").strip()
        cid = os.environ.get("GATEWAY_CLIENT_ID", "").strip()
        secret = os.environ.get("GATEWAY_CLIENT_SECRET", "").strip()
        scope = os.environ.get("GATEWAY_SCOPE", "").strip() or "bedrock-agentcore-gateway"

    if not endpoint or not cid or not secret:
        raise ValueError("Missing Gateway OAuth config (set env vars or GATEWAY_CONFIG_SECRET_NAME)")

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
    url = _get_gateway_url()
    if not url:
        raise ValueError("Gateway URL not configured")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
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
