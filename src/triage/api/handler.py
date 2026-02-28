"""Lambda handler for POST /triage."""

import json
import logging

from triage.core.agent import assess_triage
from triage.models.triage import TriageRequest

logger = logging.getLogger(__name__)


def handler(event: dict, context: object) -> dict:
    """
    API Gateway Lambda proxy handler for POST /triage.
    Expects body: {"symptoms": ["..."], "vitals": {...}, "age_years": int?, "sex": str?}
    """
    try:
        if event.get("httpMethod") != "POST":
            return _response(405, {"error": "Method not allowed"})

        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)

        request = TriageRequest.model_validate(body)
    except Exception as e:
        logger.warning("Invalid request: %s", e)
        return _response(400, {"error": str(e)})

    try:
        result = assess_triage(request)
        return _response(200, result.model_dump(mode="json"))
    except Exception as e:
        logger.exception("Triage assessment failed")
        return _response(500, {"error": "Triage assessment failed", "detail": str(e)})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
