"""
AgentCore Gateway Lambda: Google Maps (Directions + Geocoding).

Tools:
- get_directions: origin_lat, origin_lon, dest_lat, dest_lon (or origin_address, dest_address for geocoding).
  Returns distance_km, duration_minutes, directions_url.
- geocode_address: address string -> lat, lon (for use when caller has address only).

Requires GOOGLE_MAPS_CONFIG_SECRET_NAME env and secret with api_key. If not set, returns stub.
"""

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

DELIMITER = "___"


def _get_api_key() -> str | None:
    secret_name = os.environ.get("GOOGLE_MAPS_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        return None
    try:
        import boto3
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=secret_name)
        data = json.loads(resp["SecretString"])
        return (data.get("api_key") or "").strip() or None
    except Exception as e:
        logger.warning("Could not read Google Maps secret: %s", e)
        return None


def _geocode(address: str, api_key: str) -> tuple[float, float] | None:
    """Return (lat, lon) or None."""
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + urllib.parse.urlencode({
        "address": address,
        "key": api_key,
    })
    try:
        with urllib.request.urlopen(urllib.request.Request(url), timeout=10) as r:
            data = json.loads(r.read().decode())
        if data.get("status") != "OK" or not data.get("results"):
            return None
        loc = data["results"][0]["geometry"]["location"]
        return (float(loc["lat"]), float(loc["lng"]))
    except Exception as e:
        logger.warning("Geocode failed: %s", e)
        return None


def _parse_duration_seconds(dur_str: str) -> int:
    """Parse Routes API duration (e.g. '3600s') to seconds."""
    if not dur_str or not isinstance(dur_str, str):
        return 0
    s = dur_str.strip().rstrip("s").strip()
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return 0


def _directions(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float, api_key: str) -> dict | None:
    """Call Routes API (v2) computeRoutes. Return dict with distance_km, duration_minutes, directions_url or error.
    Uses POST routes.googleapis.com/directions/v2:computeRoutes (legacy Directions API is deprecated for new projects)."""
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    payload = {
        "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lon}}},
        "destination": {"location": {"latLng": {"latitude": dest_lat, "longitude": dest_lon}}},
        "travelMode": "DRIVE",
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body_str = ""
        try:
            if getattr(e, "fp", None):
                body_str = e.fp.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        logger.warning("Routes API HTTP %s: %s", e.code, body_str[:500])
        return {"error": "Directions failed", "detail": f"HTTP {e.code}: {body_str[:300]}"}
    except Exception as e:
        logger.warning("Directions failed: %s", e)
        return {"error": "Directions failed", "detail": str(e)}

    routes = data.get("routes") or []
    if not routes:
        err = data.get("error", {})
        msg = err.get("message", err) if isinstance(err, dict) else json.dumps(data)[:200]
        logger.warning("Routes API no routes: %s", msg)
        return {"error": "Directions failed", "detail": msg or "No routes returned"}

    route = routes[0]
    dist_m = route.get("distanceMeters") or 0
    dur_str = route.get("duration") or "0s"
    dur_s = _parse_duration_seconds(dur_str)
    origin = f"{origin_lat},{origin_lon}"
    dest = f"{dest_lat},{dest_lon}"
    dir_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}&travelmode=driving"
    return {
        "distance_km": round(dist_m / 1000, 2),
        "duration_minutes": max(1, round(dur_s / 60)),
        "directions_url": dir_url,
    }


def _strip_tool_prefix(full_name: str) -> str:
    if not full_name or DELIMITER not in full_name:
        return full_name or ""
    return full_name[full_name.index(DELIMITER) + len(DELIMITER):]


def handler(event: dict, context: object) -> dict:
    """
    Gateway tool handler. Event keys: tool name (from context or event), then args.
    Tools: get_directions(origin_lat, origin_lon, dest_lat, dest_lon | origin_address, dest_address),
          geocode_address(address).
    """
    tool_name = "get_directions"
    try:
        custom = getattr(context, "client_context", None)
        if custom and hasattr(custom, "custom") and custom.custom:
            raw = custom.custom.get("bedrockAgentCoreToolName")
            if raw:
                tool_name = _strip_tool_prefix(raw) or "get_directions"
    except Exception:
        pass

    api_key = _get_api_key()

    if tool_name == "geocode_address":
        address = (event.get("address") or "").strip()
        if not address:
            return {"error": "address required", "lat": None, "lon": None}
        if not api_key:
            return {"lat": 0.0, "lon": 0.0, "stub": True}
        pt = _geocode(address, api_key)
        if pt is None:
            return {"error": "geocode failed", "lat": None, "lon": None}
        return {"lat": pt[0], "lon": pt[1]}

    # get_directions
    origin_lat = event.get("origin_lat")
    origin_lon = event.get("origin_lon")
    dest_lat = event.get("dest_lat")
    dest_lon = event.get("dest_lon")
    origin_address = (event.get("origin_address") or "").strip()
    dest_address = (event.get("dest_address") or "").strip()

    if origin_address and (origin_lat is None or origin_lon is None) and api_key:
        pt = _geocode(origin_address, api_key)
        if pt:
            origin_lat, origin_lon = pt
    if dest_address and (dest_lat is None or dest_lon is None) and api_key:
        pt = _geocode(dest_address, api_key)
        if pt:
            dest_lat, dest_lon = pt

    try:
        origin_lat = float(origin_lat) if origin_lat is not None else None
        origin_lon = float(origin_lon) if origin_lon is not None else None
        dest_lat = float(dest_lat) if dest_lat is not None else None
        dest_lon = float(dest_lon) if dest_lon is not None else None
    except (TypeError, ValueError):
        return {"error": "Invalid coordinates", "distance_km": None, "duration_minutes": None, "directions_url": None}

    if None in (origin_lat, origin_lon, dest_lat, dest_lon):
        return {"error": "origin and destination coordinates (or addresses) required", "distance_km": None, "duration_minutes": None, "directions_url": None}

    if not api_key:
        # Stub for when key not configured
        return {
            "distance_km": 5.0,
            "duration_minutes": 15,
            "directions_url": None,
            "stub": True,
        }

    result = _directions(origin_lat, origin_lon, dest_lat, dest_lon, api_key)
    if result is None:
        return {"error": "Directions failed", "distance_km": None, "duration_minutes": None, "directions_url": None}
    if result.get("error"):
        return {**result, "distance_km": result.get("distance_km"), "duration_minutes": result.get("duration_minutes"), "directions_url": result.get("directions_url")}
    return result
