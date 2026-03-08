"""Invoke RMP Quiz AgentCore runtime for get_question and score_answer."""

import json
import logging
import os
import uuid

import boto3

logger = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "us-east-1")
RMP_QUIZ_AGENT_RUNTIME_ARN = os.environ.get("RMP_QUIZ_AGENT_RUNTIME_ARN", "").strip()


def invoke_rmp_quiz(payload: dict) -> dict:
    """
    Invoke the RMP Quiz AgentCore runtime.
    payload: {"action": "get_question", "topic": "fever protocol"} or
             {"action": "score_answer", "question": "...", "reference_answer": "...", "user_answer": "..."}
    Returns the agent response (question + reference_answer + topic, or points + feedback).
    """
    if not RMP_QUIZ_AGENT_RUNTIME_ARN:
        return _fallback_response(payload, "RMP_QUIZ_AGENT_RUNTIME_ARN not set")

    client = boto3.client("bedrock-agentcore", region_name=REGION)
    session_id = str(uuid.uuid4())

    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=RMP_QUIZ_AGENT_RUNTIME_ARN,
            runtimeSessionId=session_id,
            payload=json.dumps(payload).encode("utf-8"),
        )
    except Exception as e:
        logger.exception("RMP Quiz AgentCore invocation failed: %s", e)
        return _fallback_response(payload, str(e))

    content_type = response.get("contentType", "")
    body_parts = []
    resp_stream = response.get("response")
    if resp_stream:
        for chunk in resp_stream:
            if chunk:
                body_parts.append(chunk.decode("utf-8"))

    raw = "".join(body_parts)
    if "text/event-stream" in content_type:
        for line in raw.splitlines():
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    data = json.loads(line[6:])
                    if isinstance(data, dict) and (data.get("question") or "points" in data):
                        return data
                except json.JSONDecodeError:
                    pass
    else:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError as e:
            logger.warning("RMP Quiz response not valid JSON: %s", e)

    return _fallback_response(payload, "Agent did not return structured response")


def _fallback_response(payload: dict, reason: str) -> dict:
    action = (payload.get("action") or "get_question").strip().lower()
    if action == "score_answer":
        return {"points": 0, "feedback": reason}
    return {
        "question": "What is the first step in assessing a patient with acute symptoms?",
        "reference_answer": "Assess ABC (Airway, Breathing, Circulation) and vital signs.",
        "topic": payload.get("topic", "general"),
    }
