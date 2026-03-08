"""Lambda handler for POST /rmp/learning (get_question or submit answer for scoring)."""

import json
import logging

from rmp_learning.core.agent import invoke_rmp_quiz

logger = logging.getLogger(__name__)


def _rmp_from_event(event: dict) -> str | None:
    """Extract RMP identifier from API Gateway Cognito authorizer."""
    try:
        auth = (event.get("requestContext") or {}).get("authorizer") or {}
        if not isinstance(auth, dict):
            return None
        sub = auth.get("sub") or (auth.get("claims") or {}).get("sub")
        return sub
    except Exception:
        return None


def handler(event: dict, context: object) -> dict:
    """
    API Gateway Lambda proxy for POST /rmp/learning.
    Body: {"action": "get_question", "topic": "fever protocol"} or
          {"action": "score_answer", "question": "...", "reference_answer": "...", "user_answer": "..."}
    RMP auth required (Cognito).
    """
    try:
        if event.get("httpMethod") != "POST":
            return _response(405, {"error": "Method not allowed"})

        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)

        if not isinstance(body, dict):
            return _response(400, {"error": "Body must be a JSON object"})

        rmp = _rmp_from_event(event)
        if rmp:
            logger.info("RMP Learning rmp_sub=%s action=%s", rmp, body.get("action"))

        result = invoke_rmp_quiz(body)
        return _response(200, result)
    except json.JSONDecodeError as e:
        logger.warning("Invalid JSON body: %s", e)
        return _response(400, {"error": "Invalid JSON body"})
    except Exception as e:
        logger.exception("RMP Learning failed")
        return _response(500, {"error": "RMP Learning failed", "detail": str(e)})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
