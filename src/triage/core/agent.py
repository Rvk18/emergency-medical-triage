"""Bedrock Agent orchestration for triage assessment.

Uses best practices from:
- Claude Cookbooks: tool use for structured output, Pydantic validation
- Knowledge-work-plugins: triage taxonomy, priority framework
- Bedrock: Return Control for agent path, Converse API tool use for fallback
"""

import json
import logging
import os
import uuid

import boto3

from triage.core.instructions import TRIAGE_SYSTEM_PROMPT
from triage.core.tools import get_triage_tool_config
from triage.models.triage import TriageRequest, TriageResult

logger = logging.getLogger(__name__)

AGENT_ID = os.environ.get("BEDROCK_AGENT_ID", "")
AGENT_ALIAS_ID = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")
REGION = os.environ.get("AWS_REGION", "us-east-1")


def _build_user_prompt(request: TriageRequest) -> str:
    """Build user prompt with patient context."""
    parts = [
        "Assess this patient and call submit_triage_result with your assessment.",
        "",
        "Symptoms: " + ", ".join(request.symptoms),
        "Vitals: " + (json.dumps(request.vitals) if request.vitals else "No vitals provided."),
    ]
    if request.age_years is not None:
        parts.append(f"Age: {request.age_years} years")
    if request.sex:
        parts.append(f"Sex: {request.sex}")
    return "\n".join(parts)


def _tool_input_to_result(tool_input: dict) -> TriageResult | None:
    """Validate tool input with Pydantic (Claude Cookbook pattern)."""
    try:
        return TriageResult.model_validate(tool_input)
    except Exception as e:
        logger.warning("TriageResult validation failed: %s", e)
        return None


def _params_to_triage_result(params: list[dict]) -> TriageResult | None:
    """Build TriageResult from Return Control function parameters (Bedrock Agent)."""
    param_map = {p["name"]: p.get("value", "") for p in params}
    try:
        severity = param_map.get("severity", "high")
        confidence = float(param_map.get("confidence", 0.5))
        recs = param_map.get("recommendations", "[]")
        recommendations = json.loads(recs) if isinstance(recs, str) else recs
        force = param_map.get("force_high_priority", "false").lower() in ("true", "1")
        disclaimer = param_map.get("safety_disclaimer") or None
        return TriageResult(
            severity=severity,
            confidence=confidence,
            recommendations=recommendations if isinstance(recommendations, list) else [],
            force_high_priority=force,
            safety_disclaimer=disclaimer,
        )
    except (ValueError, TypeError) as e:
        logger.warning("Failed to parse return control params: %s", e)
        return None


def _safety_fallback(reason: str) -> TriageResult:
    """Default to high priority when parsing or validation fails."""
    return TriageResult(
        severity="high",
        confidence=0.0,
        recommendations=[f"Unable to complete assessment: {reason}. Treat as high priority."],
        force_high_priority=True,
        safety_disclaimer="This is AI-assisted guidance. Seek professional medical care.",
    )


def assess_triage(request: TriageRequest) -> TriageResult:
    """
    Invoke Bedrock Agent or Converse API for triage assessment.
    Uses tool use / Return Control for structured output; validates with Pydantic.
    """
    if AGENT_ID:
        return _assess_via_agent(request)
    return _assess_via_converse(request)


def _assess_via_agent(request: TriageRequest) -> TriageResult:
    """Invoke Bedrock Agent; extract structured result from Return Control or tool use."""
    client = boto3.client("bedrock-agent-runtime", region_name=REGION)
    session_id = str(uuid.uuid4())
    user_prompt = _build_user_prompt(request)
    full_prompt = f"{TRIAGE_SYSTEM_PROMPT}\n\n{user_prompt}"

    try:
        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=full_prompt,
            enableTrace=True,
            endSession=True,
        )
    except Exception as e:
        logger.error("Agent invocation failed: %s", e)
        raise

    for event in response.get("completion", []):
        if "returnControl" in event:
            rc = event["returnControl"]
            for inv in rc.get("invocationInputs", []):
                fi = inv.get("functionInvocationInput", {})
                if fi.get("function") == "submit_triage_result":
                    params = fi.get("parameters", [])
                    result = _params_to_triage_result(params)
                    if result:
                        return result

    return _safety_fallback("Agent did not return structured triage result")


def _assess_via_converse(request: TriageRequest) -> TriageResult:
    """
    Use Converse API with tool use (Claude Cookbook pattern).
    Model calls submit_triage_result tool; we extract input and validate with Pydantic.
    """
    model_id = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-v2:0")
    client = boto3.client("bedrock-runtime", region_name=REGION)
    tool_config = get_triage_tool_config()
    user_prompt = _build_user_prompt(request)

    messages = [
        {"role": "user", "content": [{"text": user_prompt}]},
    ]

    try:
        response = client.converse(
            modelId=model_id,
            messages=messages,
            system=[{"text": TRIAGE_SYSTEM_PROMPT}],
            toolConfig=tool_config,
            inferenceConfig={"maxTokens": 1024},
        )
    except Exception as e:
        logger.error("Converse invocation failed: %s", e)
        raise

    output = response.get("output", {})
    stop_reason = response.get("stopReason", "")
    msg = output.get("message", {})

    if stop_reason == "tool_use":
        for block in msg.get("content", []):
            if "toolUse" in block:
                tool = block["toolUse"]
                if tool.get("name") == "submit_triage_result":
                    tool_input = tool.get("input", {})
                    result = _tool_input_to_result(tool_input)
                    if result:
                        return result

    return _safety_fallback("Model did not call submit_triage_result tool")
