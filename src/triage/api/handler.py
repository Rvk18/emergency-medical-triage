"""Lambda handler for POST /triage."""

import json
import logging
import os
import uuid

from triage.core.agent import assess_triage
from triage.core.db import insert_triage_assessment
from triage.models.triage import TriageRequest

logger = logging.getLogger(__name__)


def handler(event: dict, context: object) -> dict:
    """
    API Gateway Lambda proxy handler for POST /triage.
    Expects body: {"symptoms": ["..."], "vitals": {...}, "age_years": int?, "sex": str?, "submitted_by": str?}
    """
    try:
        if event.get("httpMethod") != "POST":
            return _response(405, {"error": "Method not allowed"})

        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)
        # Accept rmp_id as alias for submitted_by
        if "rmp_id" in body and "submitted_by" not in body:
            body = {**body, "submitted_by": body["rmp_id"]}

        request = TriageRequest.model_validate(body)
    except Exception as e:
        logger.warning("Invalid request: %s", e)
        return _response(400, {"error": str(e)})

    try:
        result = assess_triage(request)
        request_id = uuid.uuid4()
        model_id = os.environ.get("BEDROCK_MODEL_ID")

        row_id = None
        try:
            row_id = insert_triage_assessment(
                symptoms=request.symptoms,
                vitals=request.vitals,
                age_years=request.age_years,
                sex=request.sex,
                severity=result.severity,
                confidence=result.confidence,
                recommendations=result.recommendations,
                force_high_priority=result.force_high_priority,
                safety_disclaimer=result.safety_disclaimer,
                request_id=request_id,
                bedrock_trace_id=None,
                model_id=model_id,
                submitted_by=request.submitted_by,
                hospital_match_id=None,
            )
            logger.info("Persisted triage assessment id=%s", row_id)
        except Exception as db_err:
            logger.exception("DB persist failed (assessment succeeded): %s", db_err)
            # Return 200 with result; persistence failure is logged but not fatal

        response_body = result.model_dump(mode="json")
        if row_id:
            response_body["id"] = str(row_id)
        return _response(200, response_body)
    except Exception as e:
        logger.exception("Triage assessment failed")
        return _response(500, {"error": "Triage assessment failed", "detail": str(e)})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
