"""
POST /route Lambda: get directions between origin and destination via Gateway.
Uses gateway_config from Secrets Manager (boto3); calls Gateway tool maps-target___get_directions
or routing-target___get_route. No secrets or config from env; Gateway URL and OAuth from secret.
RMP auth: Cognito; identity in requestContext.authorizer.
"""

import json
import logging
import os
import time
import urllib.error
import urllib.request
import urllib.parse
import http.client
import ssl

logger = logging.getLogger(__name__)

MAPS_TOOL_NAME = "maps-target___get_directions"
ROUTING_TOOL_NAME = "routing-target___get_route"
_token: str | None = None
_token_expires_at: float = 0


def _get_gateway_config() -> dict | None:
    secret_name = os.environ.get("GATEWAY_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        return None
    try:
        import boto3
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=secret_name)
        return json.loads(resp["SecretString"])
    except Exception as e:
        logger.warning("Could not load gateway config: %s", e)
        return None


def _get_token(config: dict) -> str:
    global _token, _token_expires_at
    now = time.time()
    if _token and _token_expires_at > now + 300:
        return _token
    ci = config.get("client_info") or {}
    endpoint = (ci.get("token_endpoint") or "").strip()
    cid = (ci.get("client_id") or "").strip()
    secret = (ci.get("client_secret") or "").strip()
    scope = (ci.get("scope") or "").strip() or "bedrock-agentcore-gateway"
    if not endpoint or not cid or not secret:
        raise ValueError("Missing client_info in gateway config")
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": secret,
        "scope": scope,
    }).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        body = json.loads(r.read().decode())
    _token = body.get("access_token")
    if not _token:
        raise ValueError("No access_token")
    _token_expires_at = now + int(body.get("expires_in", 3600)) - 300
    return _token


def _call_get_directions(config: dict, args: dict) -> dict:
    url = (config.get("gateway_url") or "").strip()
    if not url:
        raise ValueError("Missing gateway_url")
    if not url.endswith("/mcp"):
        url = url.rstrip("/") + "/mcp"
    token = _get_token(config)
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": MAPS_TOOL_NAME, "arguments": args}}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Mcp-Protocol-Version": "2025-03-26"}
    body_bytes = json.dumps(payload).encode("utf-8")

    # Use http.client so we can read response body for any status (e.g. 400) without exception handling
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    conn = http.client.HTTPSConnection(host, port=port, timeout=15, context=ssl.create_default_context())
    try:
        conn.request("POST", path, body=body_bytes, headers=headers)
        resp = conn.getresponse()
        resp_body = resp.read().decode("utf-8", errors="replace")
        if resp.status >= 400:
            try:
                err_obj = json.loads(resp_body) if resp_body else {}
                msg = err_obj.get("error", {}).get("message") if isinstance(err_obj.get("error"), dict) else (resp_body or resp.reason)
            except json.JSONDecodeError:
                msg = resp_body or resp.reason
            raise RuntimeError(f"Gateway HTTP {resp.status}: {msg}")
        result = json.loads(resp_body) if resp_body else {}
    finally:
        conn.close()

    if result.get("error"):
        err = result["error"]
        msg = err.get("message", err) if isinstance(err, dict) else str(err)
        raise RuntimeError(f"Gateway error: {msg}")
    res = result.get("result") or {}
    if isinstance(res, dict):
        if "content" in res and isinstance(res["content"], list) and res["content"]:
            first = res["content"][0]
            if isinstance(first, dict) and first.get("type") == "text" and "text" in first:
                try:
                    return json.loads(first["text"])
                except json.JSONDecodeError:
                    pass
        if "structuredContent" in res and isinstance(res["structuredContent"], dict):
            return res["structuredContent"]
    return res if isinstance(res, dict) else {}


def _rmp_from_event(event: dict) -> str | None:
    try:
        auth = (event.get("requestContext") or {}).get("authorizer") or {}
        if not isinstance(auth, dict):
            return None
        return auth.get("sub") or (auth.get("claims") or {}).get("sub") or auth.get("email") or (auth.get("claims") or {}).get("email")
    except Exception:
        return None


def handler(event: dict, context: object) -> dict:
    """
    API Gateway Lambda for POST /route. RMP auth required.
    Body: { "origin": { "lat", "lon" } or { "address": "..." }, "destination": { "lat", "lon" } or { "address": "..." } }
    """
    start = time.perf_counter()
    try:
        if event.get("httpMethod") != "POST":
            return _response(405, {"error": "Method not allowed"})
        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)
        origin = body.get("origin") or {}
        destination = body.get("destination") or {}
        if not isinstance(origin, dict) or not isinstance(destination, dict):
            return _response(400, {"error": "origin and destination must be objects"})
        # Build args for get_directions
        args = {}
        if origin.get("lat") is not None and origin.get("lon") is not None:
            args["origin_lat"] = float(origin["lat"])
            args["origin_lon"] = float(origin["lon"])
        elif origin.get("address"):
            args["origin_address"] = str(origin["address"]).strip()
        else:
            return _response(400, {"error": "origin must have lat+lon or address"})
        if destination.get("lat") is not None and destination.get("lon") is not None:
            args["dest_lat"] = float(destination["lat"])
            args["dest_lon"] = float(destination["lon"])
        elif destination.get("address"):
            args["dest_address"] = str(destination["address"]).strip()
        else:
            return _response(400, {"error": "destination must have lat+lon or address"})
        # Validate ranges
        for k in ["origin_lat", "origin_lon", "dest_lat", "dest_lon"]:
            if k in args:
                v = args[k]
                if k.endswith("_lat") and (v < -90 or v > 90):
                    return _response(400, {"error": "Latitude must be -90 to 90"})
                if k.endswith("_lon") and (v < -180 or v > 180):
                    return _response(400, {"error": "Longitude must be -180 to 180"})
        config = _get_gateway_config()
        if not config:
            return _response(503, {"error": "Gateway not configured", "distance_km": None, "duration_minutes": None, "directions_url": None})
        try:
            result = _call_get_directions(config, args)
        except RuntimeError as e:
            err_str = str(e)
            if "Gateway HTTP 400" in err_str or "Gateway HTTP 4" in err_str:
                return _response(400, {"error": "Gateway validation failed", "detail": err_str})
            raise
        duration_ms = (time.perf_counter() - start) * 1000
        request_id = getattr(context, "aws_request_id", None) if context else None
        logger.info("Routing source=gateway duration_ms=%.2f", duration_ms)
        if request_id:
            logger.info("Routing success request_id=%s", request_id)
        rmp = _rmp_from_event(event)
        if rmp:
            logger.info("Routing rmp_sub=%s", rmp)
        return _response(200, result)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            buf = getattr(e, "fp", None) or getattr(e, "file", None)
            if buf:
                body = buf.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        detail = body or f"HTTP {e.code} {e.reason}"
        return _response(400, {"error": "Gateway request failed", "detail": detail})
    except Exception as e:
        logger.exception("Route failed: %s", e)
        return _response(500, {"error": "Route failed", "detail": str(e)})


def _response(status_code: int, body: dict) -> dict:
    return {"statusCode": status_code, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body)}
