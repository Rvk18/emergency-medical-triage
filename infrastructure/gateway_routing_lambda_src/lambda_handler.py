"""
Gateway target Lambda for the Routing agent.

When the Gateway calls routing-target___get_route, it invokes this Lambda.
This Lambda invokes the Routing agent on the AgentCore Runtime; the Routing agent uses the Google Maps MCP.
"""

import json
import logging
import os
import uuid

logger = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "us-east-1")
ROUTING_AGENT_RUNTIME_ARN = os.environ.get("ROUTING_AGENT_RUNTIME_ARN", "").strip()


def handler(event: dict, context: object) -> dict:
    """
    Gateway tool handler. Event: { origin_lat, origin_lon, dest_lat, dest_lon } or origin_address, dest_address.
    Invokes the Routing agent on the Runtime and returns { distance_km, duration_minutes, directions_url }.
    """
    if not ROUTING_AGENT_RUNTIME_ARN:
        logger.warning("ROUTING_AGENT_RUNTIME_ARN not set; returning stub")
        return {"distance_km": None, "duration_minutes": None, "directions_url": None, "stub": True}

    origin = {}
    dest = {}
    if event.get("origin_lat") is not None and event.get("origin_lon") is not None:
        origin["lat"] = event["origin_lat"]
        origin["lon"] = event["origin_lon"]
    elif event.get("origin_address"):
        origin["address"] = event["origin_address"]
    if event.get("dest_lat") is not None and event.get("dest_lon") is not None:
        dest["lat"] = event["dest_lat"]
        dest["lon"] = event["dest_lon"]
    elif event.get("dest_address"):
        dest["address"] = event["dest_address"]

    if not origin or not dest:
        return {"error": "origin and destination required", "distance_km": None, "duration_minutes": None, "directions_url": None}

    payload = {"origin": origin, "destination": dest}
    session_id = str(uuid.uuid4())

    try:
        import boto3
        client = boto3.client("bedrock-agentcore", region_name=REGION)
        response = client.invoke_agent_runtime(
            agentRuntimeArn=ROUTING_AGENT_RUNTIME_ARN,
            runtimeSessionId=session_id,
            payload=json.dumps(payload).encode("utf-8"),
        )
    except Exception as e:
        logger.exception("Routing agent invoke failed: %s", e)
        return {"error": str(e), "distance_km": None, "duration_minutes": None, "directions_url": None}

    content_type = response.get("contentType", "")
    body_parts = []
    for chunk in response.get("response") or []:
        if chunk:
            body_parts.append(chunk.decode("utf-8"))
    raw = "".join(body_parts)

    try:
        if "text/event-stream" in content_type:
            for line in raw.splitlines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    try:
                        data = json.loads(line[6:])
                        if isinstance(data, dict) and ("distance_km" in data or "directions_url" in data or "error" in data):
                            return data
                    except json.JSONDecodeError:
                        pass
        else:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
    except json.JSONDecodeError as e:
        logger.warning("Routing agent response not JSON: %s", e)

    return {"error": "No route result", "distance_km": None, "duration_minutes": None, "directions_url": None}
