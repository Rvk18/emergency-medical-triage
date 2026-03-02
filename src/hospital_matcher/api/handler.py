"""Lambda handler for POST /hospitals."""

import json
import logging

from hospital_matcher.core.agent import match_hospitals
from hospital_matcher.models.hospital import HospitalMatchRequest

logger = logging.getLogger(__name__)


def handler(event: dict, context: object) -> dict:
    """API Gateway Lambda proxy for POST /hospitals."""
    try:
        if event.get("httpMethod") != "POST":
            return _response(405, {"error": "Method not allowed"})

        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)

        request = HospitalMatchRequest.model_validate(body)
    except Exception as e:
        logger.warning("Invalid request: %s", e)
        return _response(400, {"error": str(e)})

    try:
        request_id = getattr(context, "aws_request_id", None) if context else None
        result = match_hospitals(request)
        if request_id:
            logger.info("HospitalMatcher success request_id=%s", request_id)
        return _response(200, result.model_dump(mode="json"))
    except Exception as e:
        logger.exception("Hospital matching failed")
        return _response(500, {"error": "Hospital matching failed", "detail": str(e)})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
