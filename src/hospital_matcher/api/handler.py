"""Lambda handler for POST /hospitals."""

import json
import logging

from hospital_matcher.core.agent import match_hospitals
from hospital_matcher.models.hospital import HospitalMatchRequest

logger = logging.getLogger(__name__)


def _rmp_from_event(event: dict) -> str | None:
    """Extract RMP identifier from API Gateway Cognito authorizer."""
    try:
        auth = (event.get("requestContext") or {}).get("authorizer") or {}
        if not isinstance(auth, dict):
            return None
        sub = auth.get("sub") or (auth.get("claims") or {}).get("sub")
        email = auth.get("email") or (auth.get("claims") or {}).get("email")
        return sub or email
    except Exception:
        return None


def handler(event: dict, context: object) -> dict:
    """API Gateway Lambda proxy for POST /hospitals. RMP auth required (Cognito)."""
    try:
        if event.get("httpMethod") != "POST":
            return _response(405, {"error": "Method not allowed"})

        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)

        request = HospitalMatchRequest.model_validate(body)
    except Exception as e:
        logger.warning("Invalid request: %s", type(e).__name__)
        return _response(400, {"error": str(e)})

    try:
        request_id = getattr(context, "aws_request_id", None) if context else None
        rmp = _rmp_from_event(event)
        if rmp:
            logger.info("HospitalMatcher rmp_sub=%s", rmp)
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
