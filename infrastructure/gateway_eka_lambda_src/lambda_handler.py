"""
AgentCore Gateway Lambda target for Eka Care tools (Indian drugs, treatment protocols).

Tools: search_medications, search_protocols.
Uses Eka API (api.eka.care). Eka requires OAuth-style login:
  - POST /connect-auth/v1/account/login with client_id + client_secret -> access_token (+ refresh_token)
  - Use access_token as Bearer for medications/protocols APIs.
  - On 401, POST /connect-auth/v1/account/refresh-token to get new access_token.
See: https://developer.eka.care/user-guides/get-started
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

# Cached after login (Lambda warm start)
_access_token: str | None = None
_refresh_token: str | None = None
_client_id: str | None = None


def _strip_tool_prefix(full_name: str) -> str:
    if not full_name or DELIMITER not in full_name:
        return full_name or ""
    return full_name[full_name.index(DELIMITER) + len(DELIMITER) :]


def _load_eka_credentials() -> tuple[str | None, str | None]:
    """Load client_id and client_secret from Secrets Manager. Returns (client_id, client_secret)."""
    if not EKA_CONFIG_SECRET_NAME:
        return None, None
    try:
        import boto3
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=EKA_CONFIG_SECRET_NAME)
        data = json.loads(resp["SecretString"])
        cid = (data.get("client_id") or data.get("api_key") or "").strip() or None
        secret = (data.get("client_secret") or "").strip() or None
        return cid, secret
    except Exception as e:
        logger.warning("Failed to get Eka secret: %s", e)
        return None, None


def _http_request(
    method: str,
    url: str,
    body: dict | None = None,
    headers: dict | None = None,
    timeout: int = 15,
) -> tuple[int, bytes]:
    """Send HTTP request; return (status_code, body_bytes)."""
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            if v:
                req.add_header(k, v)
    if body and method in ("POST", "PUT", "PATCH"):
        req.data = json.dumps(body).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b""
    except Exception as e:
        logger.warning("HTTP request failed: %s", e)
        return 0, b""


def _eka_login() -> bool:
    """Call Eka login API; set global _access_token and _refresh_token. Returns True on success."""
    global _access_token, _refresh_token, _client_id
    _client_id, client_secret = _load_eka_credentials()
    if not _client_id or not client_secret:
        logger.warning("Eka: missing client_id or client_secret in secret; need both for login.")
        return False
    url = f"{EKA_API_BASE}/connect-auth/v1/account/login"
    status, raw = _http_request("POST", url, body={"client_id": _client_id, "client_secret": client_secret})
    if status != 200:
        logger.warning("Eka login failed %s: %s", status, raw.decode("utf-8", errors="replace")[:500])
        return False
    try:
        data = json.loads(raw.decode("utf-8"))
        _access_token = (data.get("access_token") or "").strip() or None
        _refresh_token = (data.get("refresh_token") or "").strip() or None
        if not _access_token:
            logger.warning("Eka login response missing access_token")
            return False
        return True
    except Exception as e:
        logger.warning("Eka login parse error: %s", e)
        return False


def _eka_refresh() -> bool:
    """Use refresh_token to get new access_token. Returns True on success."""
    global _access_token, _refresh_token
    if not _refresh_token or not _client_id or not _access_token:
        return False
    url = f"{EKA_API_BASE}/connect-auth/v1/account/refresh-token"
    headers = {
        "Authorization": f"Bearer {_access_token}",
        "Client-Id": _client_id,
    }
    status, raw = _http_request("POST", url, body={"refresh_token": _refresh_token}, headers=headers)
    if status != 200:
        logger.warning("Eka refresh failed %s: %s", status, raw.decode("utf-8", errors="replace")[:500])
        return False
    try:
        data = json.loads(raw.decode("utf-8"))
        _access_token = (data.get("access_token") or "").strip() or None
        _refresh_token = (data.get("refresh_token") or "").strip() or _refresh_token
        return bool(_access_token)
    except Exception as e:
        logger.warning("Eka refresh parse error: %s", e)
        return False


def _get_eka_token() -> str | None:
    """
    Return Bearer token for Eka API. Uses client_id+client_secret login when available;
    otherwise falls back to single api_key/client_id as Bearer (legacy; may get 403).
    """
    global _access_token
    if _access_token:
        return _access_token
    client_id, client_secret = _load_eka_credentials()
    if client_id and client_secret:
        if _eka_login():
            return _access_token
        return None
    # Legacy: single key as Bearer (Eka may return 403; they require login)
    if client_id:
        logger.warning("Eka: using client_id as Bearer (legacy). For full auth set client_secret and use login.")
        return client_id
    return None


def _eka_request(method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict | list:
    """Call Eka API with Bearer token. On 401, tries refresh once and retries."""
    token = _get_eka_token()
    if not token:
        return []
    url = f"{EKA_API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v is not None)
        if qs:
            url += "?" + qs
    headers = {"Authorization": f"Bearer {token}"}
    status, raw = _http_request(method, url, body=body, headers=headers)
    if status == 401 and _eka_refresh():
        token = _get_eka_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
            status, raw = _http_request(method, url, body=body, headers=headers)
    if status != 200:
        logger.warning("Eka API error %s: %s", status, raw[:500] if raw else b"")
        return []
    if not raw:
        return []
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        logger.warning("Eka response parse error: %s", e)
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


def get_protocol_publishers() -> dict:
    """Get list of protocol publishers (e.g. ICMR, RSSDI). Use before search_protocols to pass valid publisher."""
    if not EKA_CONFIG_SECRET_NAME:
        return {"publishers": ["ICMR", "RSSDI"], "message": "Eka not configured; stub data."}
    result = _eka_request("GET", "/eka-mcp/protocols/v1/publishers/all")
    if isinstance(result, list):
        return {"publishers": result}
    return {"publishers": result.get("publishers", result) if isinstance(result, dict) else []}


def search_pharmacology(
    query: str | None = None,
    category: str | None = None,
    limit: int = 10,
    exact_match: bool = False,
    relevance_threshold: int = 100,
) -> dict:
    """Search generic (NFI) pharmacology: dose, indications, contraindications, pregnancy_category, etc."""
    if not EKA_CONFIG_SECRET_NAME:
        return {"results": [], "message": "Eka not configured; stub data."}
    params = {"limit": limit, "exact_match": exact_match, "relevance_threshold": relevance_threshold}
    if query:
        params["query"] = query
    if category:
        params["category"] = category
    result = _eka_request("GET", "/eka-mcp/pharmacology/v1/search", params=params)
    if isinstance(result, dict) and "results" in result:
        return result
    return {"results": result if isinstance(result, list) else [], "search_info": {}}


def handler(event: dict, context: object) -> dict:
    """
    Gateway Lambda target. Event has tool args; context has bedrockAgentCoreToolName (TARGET___tool_name).
    For direct Lambda invoke, event may include "tool": "search_medications" | "search_protocols" | "get_protocol_publishers" | "search_pharmacology".
    """
    tool_name = "search_medications"
    allowed = ("search_medications", "search_protocols", "get_protocol_publishers", "search_pharmacology")
    if event.get("tool") in allowed:
        tool_name = event["tool"]
    else:
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
    if tool_name == "get_protocol_publishers":
        return get_protocol_publishers()
    if tool_name == "search_pharmacology":
        return search_pharmacology(
            query=event.get("query"),
            category=event.get("category"),
            limit=event.get("limit", 10),
            exact_match=event.get("exact_match", False),
            relevance_threshold=event.get("relevance_threshold", 100),
        )
    return {"error": f"Unknown tool: {tool_name}", "medications": [], "protocols": [], "publishers": [], "results": []}
