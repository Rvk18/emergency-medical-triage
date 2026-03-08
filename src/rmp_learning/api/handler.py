"""Lambda handler for RMP Learning: POST /rmp/learning, GET /rmp/learning/me, GET /rmp/learning/leaderboard."""

import json
import logging

from rmp_learning.core.agent import invoke_rmp_quiz
from rmp_learning.core.db import get_leaderboard, get_my_score, insert_learning_answer, upsert_rmp_score

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
    Route by method and path:
    - GET .../rmp/learning/me -> current user's total_points and rank
    - GET .../rmp/learning/leaderboard -> top N (query limit, default 20)
    - POST .../rmp/learning -> get_question or score_answer (body)
    RMP auth required (Cognito) for all.
    """
    try:
        method = (event.get("httpMethod") or "").upper()
        path = (event.get("path") or event.get("resource") or "").lower()

        if method == "GET":
            if "learning/me" in path or path.endswith("/me"):
                return _handle_get_me(event)
            if "learning/leaderboard" in path or path.endswith("/leaderboard"):
                return _handle_get_leaderboard(event)
            return _response(404, {"error": "Not found"})

        if method != "POST":
            return _response(405, {"error": "Method not allowed"})

        # POST /rmp/learning
        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)

        if not isinstance(body, dict):
            return _response(400, {"error": "Body must be a JSON object"})

        rmp = _rmp_from_event(event)
        if rmp:
            logger.info("RMP Learning rmp_sub=%s action=%s", rmp, body.get("action"))

        result = invoke_rmp_quiz(body)

        # Persist score when action is score_answer and we have an RMP id
        if (body.get("action") or "").strip().lower() == "score_answer" and rmp:
            points = result.get("points")
            if isinstance(points, (int, float)) and points >= 0:
                try:
                    upsert_rmp_score(rmp, int(points))
                    insert_learning_answer(
                        rmp_id=rmp,
                        question_ref=(body.get("question") or "")[:2000],
                        user_answer=(body.get("user_answer") or "")[:5000],
                        points=int(points),
                    )
                except Exception as e:
                    logger.exception("RMP Learning DB persist failed: %s", e)
                    # Still return 200 with agent result

        return _response(200, result)
    except json.JSONDecodeError as e:
        logger.warning("Invalid JSON body: %s", e)
        return _response(400, {"error": "Invalid JSON body"})
    except Exception as e:
        logger.exception("RMP Learning failed")
        return _response(500, {"error": "RMP Learning failed", "detail": str(e)})


def _handle_get_me(event: dict) -> dict:
    rmp = _rmp_from_event(event)
    if not rmp:
        return _response(401, {"error": "Unauthorized"})
    try:
        data = get_my_score(rmp)
        return _response(200, data)
    except Exception as e:
        logger.exception("get_my_score failed: %s", e)
        return _response(500, {"error": "Failed to load score", "detail": str(e)})


def _handle_get_leaderboard(event: dict) -> dict:
    limit = 20
    qs = event.get("queryStringParameters") or {}
    if "limit" in qs:
        try:
            limit = max(1, min(100, int(qs["limit"])))
        except ValueError:
            pass
    try:
        data = get_leaderboard(limit=limit)
        return _response(200, {"leaderboard": data})
    except Exception as e:
        logger.exception("get_leaderboard failed: %s", e)
        return _response(500, {"error": "Failed to load leaderboard", "detail": str(e)})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
