"""Hospital Matcher - Bedrock Agent or Converse API."""

import json
import logging
import os
import uuid

import boto3

from hospital_matcher.core.instructions import HOSPITAL_MATCHER_SYSTEM_PROMPT
from hospital_matcher.core.tools import get_hospital_matcher_tool_config
from hospital_matcher.models.hospital import HospitalMatchRequest, HospitalMatchResult, MatchedHospital

logger = logging.getLogger(__name__)

AGENT_ID = os.environ.get("BEDROCK_HOSPITAL_MATCHER_AGENT_ID", "")
AGENT_ALIAS_ID = os.environ.get("BEDROCK_HOSPITAL_MATCHER_AGENT_ALIAS_ID", "TSTALIASID")
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
    """Invoke Bedrock Agent or Converse API for hospital matching."""
    if AGENT_ID:
        return _match_via_agent(req)
    return _match_via_converse(req)


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
