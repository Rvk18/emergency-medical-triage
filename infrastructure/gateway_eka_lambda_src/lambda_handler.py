"""
AgentCore Gateway Lambda target for Eka Care tools (Indian drugs, treatment protocols).

Tools: search_medications, search_protocols.
Uses Eka API (api.eka.care) with Bearer token from Secrets Manager when configured.
"""

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

DELIMITER = "___"
EKA_API_BASE = os.environ.get("EKA_API_BASE", "https://api.eka.care")
EKA_CONFIG_SECRET_NAME = os.environ.get("EKA_CONFIG_SECRET_NAME", "").strip()

_token: str | None = None


def _strip_tool_prefix(full_name: str) -> str:
    if not full_name or DELIMITER not in full_name:
        return full_name or ""
    return full_name[full_name.index(DELIMITER) + len(DELIMITER) :]


def _get_eka_token() -> str | None:
    """Get Eka API key from Secrets Manager (cached in Lambda warm start)."""
    global _token
    if _token:
        return _token
    if not EKA_CONFIG_SECRET_NAME:
        return None
    try:
        import boto3
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=EKA_CONFIG_SECRET_NAME)
        data = json.loads(resp["SecretString"])
        _token = data.get("api_key") or data.get("client_id")
        return _token
    except Exception as e:
        logger.warning("Failed to get Eka secret: %s", e)
        return None


def _eka_request(method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict | list:
    """Call Eka API with Bearer token."""
    token = _get_eka_token()
    if not token:
        return []
    url = f"{EKA_API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v is not None)
        if qs:
            url += "?" + qs
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    if body and method in ("POST", "PUT", "PATCH"):
        req.data = json.dumps(body).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        logger.warning("Eka API error %s: %s", e.code, e.read())
        return []
    except Exception as e:
        logger.warning("Eka request failed: %s", e)
        return []


def search_medications(drug_name: str | None = None, form: str | None = None, generic_names: str | None = None, volumes: str | None = None) -> dict:
    """Search Indian branded drugs. Returns list of {name, generic_name, manufacturer_name, product_type}."""
    if not EKA_CONFIG_SECRET_NAME:
        return {
            "medications": [
                {"name": "Paracetamol 500mg Tablet", "generic_name": "Paracetamol", "manufacturer_name": "Stub", "product_type": "Tablet"},
                {"name": "ORS Sachet", "generic_name": "Oral Rehydration Salts", "manufacturer_name": "Stub", "product_type": "Sachet"},
            ],
            "message": "Eka not configured; stub data.",
        }
    params = {}
    if drug_name:
        params["drug_name"] = drug_name
    if form:
        params["form"] = form
    if generic_names:
        params["generic_names"] = generic_names
    if volumes:
        params["volumes"] = volumes
    result = _eka_request("GET", "/eka-mcp/medications/v1/search", params=params)
    if isinstance(result, list):
        return {"medications": result}
    return {"medications": result.get("medications", result) if isinstance(result, dict) else []}


def search_protocols(queries: list[dict]) -> dict:
    """Search Indian treatment protocols (ICMR, RSSDI). Each query: {query, tag, publisher}."""
    if not EKA_CONFIG_SECRET_NAME:
        return {
            "protocols": [
                {"conditions": ["Acute fever"], "author": "ICMR", "source_url": None, "type": "pdf"},
            ],
            "message": "Eka not configured; stub data.",
        }
    if not queries or not isinstance(queries, list):
        return {"protocols": []}
    body = {"queries": [{"query": q.get("query", ""), "tag": q.get("tag", ""), "publisher": q.get("publisher", "")} for q in queries[:5]]}
    result = _eka_request("POST", "/eka-mcp/protocols/v1/search", body=body)
    if isinstance(result, list):
        return {"protocols": result}
    return {"protocols": result.get("protocols", result) if isinstance(result, dict) else []}


def handler(event: dict, context: object) -> dict:
    """
    Gateway Lambda target. Event has tool args; context has bedrockAgentCoreToolName (TARGET___tool_name).
    """
    tool_name = "search_medications"
    try:
        custom = getattr(context, "client_context", None)
        if custom and getattr(custom, "custom", None):
            raw = custom.custom.get("bedrockAgentCoreToolName")
            if raw:
                tool_name = _strip_tool_prefix(raw) or tool_name
    except Exception as e:
        logger.warning("Could not read tool name from context: %s", e)

    if tool_name == "search_medications":
        return search_medications(
            drug_name=event.get("drug_name"),
            form=event.get("form"),
            generic_names=event.get("generic_names"),
            volumes=event.get("volumes"),
        )
    if tool_name == "search_protocols":
        return search_protocols(queries=event.get("queries", []))
    return {"error": f"Unknown tool: {tool_name}", "medications": [], "protocols": []}
