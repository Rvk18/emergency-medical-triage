"""Hospital Matcher - AgentCore, Bedrock Agent, or Converse API."""

import json
import logging
import os
import time
import uuid

import boto3

from hospital_matcher.core.instructions import HOSPITAL_MATCHER_SYSTEM_PROMPT
from hospital_matcher.core.tools import get_hospital_matcher_tool_config
from hospital_matcher.models.hospital import HospitalMatchRequest, HospitalMatchResult, MatchedHospital

logger = logging.getLogger(__name__)

AGENT_ID = os.environ.get("BEDROCK_HOSPITAL_MATCHER_AGENT_ID", "")
AGENT_ALIAS_ID = os.environ.get("BEDROCK_HOSPITAL_MATCHER_AGENT_ALIAS_ID", "TSTALIASID")
USE_AGENTCORE = os.environ.get("USE_AGENTCORE", "").lower() in ("1", "true", "yes")
AGENT_RUNTIME_ARN = os.environ.get("AGENT_RUNTIME_ARN", "")
REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6")


def _build_user_prompt(req: HospitalMatchRequest) -> str:
    parts = [
        "Match hospitals for this triage result. Call submit_hospital_matches with top 3 recommendations.",
        "",
        f"Severity: {req.severity}",
        f"Recommendations: {', '.join(req.recommendations) if req.recommendations else 'None'}",
        f"Limit: {req.limit} hospitals",
    ]
    if req.patient_location_lat and req.patient_location_lon:
        parts.append(f"Patient location: {req.patient_location_lat}, {req.patient_location_lon}")
    return "\n".join(parts)


def _tool_input_to_result(tool_input: dict) -> HospitalMatchResult | None:
    try:
        hospitals = [MatchedHospital.model_validate(h) for h in tool_input.get("hospitals", [])]
        return HospitalMatchResult(
            hospitals=hospitals,
            safety_disclaimer=tool_input.get("safety_disclaimer"),
        )
    except Exception as e:
        logger.warning("HospitalMatchResult validation failed: %s", e)
        return None


def _fallback_result(reason: str) -> HospitalMatchResult:
    """Return stub when agent fails."""
    return HospitalMatchResult(
        hospitals=[
            MatchedHospital(
                hospital_id="stub-1",
                name="District Hospital (Stub)",
                match_score=0.8,
                match_reasons=[reason, "Mock data - MCP not integrated"],
            ),
        ],
        safety_disclaimer="Hospital availability may change. Confirm with facility before transport.",
    )


def match_hospitals(req: HospitalMatchRequest) -> HospitalMatchResult:
    """Invoke AgentCore, Bedrock Agent, or Converse API for hospital matching."""
    start = time.perf_counter()
    if USE_AGENTCORE and AGENT_RUNTIME_ARN:
        result = _match_via_agentcore(req)
        _log_trace("agentcore", start)
        return result
    if AGENT_ID:
        result = _match_via_agent(req)
        _log_trace("bedrock_agent", start)
        return result
    result = _match_via_converse(req)
    _log_trace("converse", start)
    return result


def _log_trace(source: str, start: float) -> None:
    """Emit basic trace log for observability (queryable in CloudWatch Logs Insights)."""
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("HospitalMatcher source=%s duration_ms=%.2f", source, duration_ms)


def _match_via_agentcore(req: HospitalMatchRequest) -> HospitalMatchResult:
    """Invoke AgentCore Runtime agent. Uses req.session_id for memory continuity (AC-3)."""
    client = boto3.client("bedrock-agentcore", region_name=REGION)
    # AgentCore requires runtimeSessionId length >= 33 (e.g. UUID); use client's if valid else generate
    raw_session = req.session_id or ""
    session_id = raw_session if len(raw_session) >= 33 else str(uuid.uuid4())
    payload = {
        "severity": req.severity,
        "recommendations": req.recommendations,
        "limit": req.limit,
    }
    if req.triage_assessment_id:
        payload["triage_assessment_id"] = req.triage_assessment_id
    if req.patient_location_lat is not None and req.patient_location_lon is not None:
        payload["patient_location_lat"] = req.patient_location_lat
        payload["patient_location_lon"] = req.patient_location_lon
    if req.patient_id:
        payload["patient_id"] = req.patient_id

    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=session_id,
            payload=json.dumps(payload).encode("utf-8"),
        )
    except Exception as e:
        logger.error("AgentCore invocation failed: %s", e)
        return _fallback_result(str(e))

    # Parse response (streaming or JSON)
    content_type = response.get("contentType", "")
    body_parts = []
    resp_stream = response.get("response")
    if resp_stream:
        for chunk in resp_stream:
            if chunk:
                body_parts.append(chunk.decode("utf-8"))

    if "text/event-stream" in content_type:
        full_text = "".join(body_parts)
        for line in full_text.splitlines():
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    data = json.loads(line[6:])
                    if isinstance(data, dict) and "hospitals" in data:
                        result = _tool_input_to_result(data)
                        if result:
                            return result
                except json.JSONDecodeError:
                    pass
    else:
        try:
            data = json.loads("".join(body_parts))
            if isinstance(data, dict) and "hospitals" in data:
                result = _tool_input_to_result(data)
                if result:
                    return result
        except json.JSONDecodeError as e:
            logger.warning("AgentCore response not valid JSON: %s", e)

    return _fallback_result("AgentCore did not return structured matches")


def _match_via_agent(req: HospitalMatchRequest) -> HospitalMatchResult:
    """Invoke Bedrock Agent (Return Control)."""
    client = boto3.client("bedrock-agent-runtime", region_name=REGION)
    session_id = str(uuid.uuid4())
    user_prompt = _build_user_prompt(req)
    full_prompt = f"{HOSPITAL_MATCHER_SYSTEM_PROMPT}\n\n{user_prompt}"

    try:
        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=full_prompt,
            endSession=True,
        )
    except Exception as e:
        logger.error("Hospital Matcher Agent failed: %s", e)
        return _fallback_result(str(e))

    for event in response.get("completion", []):
        if "returnControl" in event:
            rc = event["returnControl"]
            for inv in rc.get("invocationInputs", []):
                fi = inv.get("functionInvocationInput", {})
                if fi.get("function") == "submit_hospital_matches":
                    params = fi.get("parameters", [])
                    param_map = {p["name"]: p.get("value", "") for p in params}
                    recs = param_map.get("hospitals", "[]")
                    hospitals_data = json.loads(recs) if isinstance(recs, str) else recs
                    disclaimer = param_map.get("safety_disclaimer") or ""
                    result = _tool_input_to_result({"hospitals": hospitals_data, "safety_disclaimer": disclaimer})
                    if result:
                        return result

    return _fallback_result("Agent did not return structured matches")


def _match_via_converse(req: HospitalMatchRequest) -> HospitalMatchResult:
    """Use Converse API with tool use."""
    client = boto3.client("bedrock-runtime", region_name=REGION)
    tool_config = get_hospital_matcher_tool_config()
    user_prompt = _build_user_prompt(req)

    messages = [{"role": "user", "content": [{"text": user_prompt}]}]

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=messages,
            system=[{"text": HOSPITAL_MATCHER_SYSTEM_PROMPT}],
            toolConfig=tool_config,
            inferenceConfig={"maxTokens": 1024},
        )
    except Exception as e:
        logger.error("Converse invocation failed: %s", e)
        return _fallback_result(str(e))

    output = response.get("output", {})
    stop_reason = response.get("stopReason", "")  # top-level, not in output
    msg = output.get("message", {})

    if stop_reason == "tool_use":
        for block in msg.get("content", []):
            if "toolUse" in block:
                tool = block["toolUse"]
                if tool.get("name") == "submit_hospital_matches":
                    result = _tool_input_to_result(tool.get("input", {}))
                    if result:
                        return result

    return _fallback_result("Model did not call submit_hospital_matches")
