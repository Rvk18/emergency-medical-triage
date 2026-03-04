"""Bedrock Agent orchestration for triage assessment.

Uses best practices from:
- Claude Cookbooks: tool use for structured output, Pydantic validation
- Knowledge-work-plugins: triage taxonomy, priority framework
- Bedrock: Return Control for agent path, Converse API tool use for fallback
- AC-2: AgentCore Runtime when USE_AGENTCORE_TRIAGE and TRIAGE_AGENT_RUNTIME_ARN set
"""

import json
import logging
import os
import time
import uuid

import boto3

from triage.core.instructions import TRIAGE_SYSTEM_PROMPT
from triage.core.tools import get_triage_tool_config, get_triage_tool_config_with_eka
from triage.models.triage import TriageRequest, TriageResult

logger = logging.getLogger(__name__)

AGENT_ID = os.environ.get("BEDROCK_AGENT_ID", "")
AGENT_ALIAS_ID = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")
USE_AGENTCORE_TRIAGE = os.environ.get("USE_AGENTCORE_TRIAGE", "").lower() in ("1", "true", "yes")
TRIAGE_AGENT_RUNTIME_ARN = os.environ.get("TRIAGE_AGENT_RUNTIME_ARN", "")
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
    Invoke AgentCore (AC-2), Bedrock Agent, or Converse API for triage assessment.
    Uses tool use / Return Control for structured output; validates with Pydantic.
    When Gateway is configured, Converse can use Eka tools (search_medications, search_protocols) before submitting.
    """
    start = time.perf_counter()
    if USE_AGENTCORE_TRIAGE and TRIAGE_AGENT_RUNTIME_ARN:
        result = _assess_via_agentcore(request)
        _log_trace("agentcore", start)
        return result
    if AGENT_ID:
        result = _assess_via_agent(request)
        _log_trace("bedrock_agent", start)
        return result
    result = _assess_via_converse(request)
    _log_trace("converse", start)
    return result


def _log_trace(source: str, start: float) -> None:
    """Emit trace log for observability (CloudWatch Logs Insights)."""
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("Triage source=%s duration_ms=%.2f", source, duration_ms)


def _assess_via_agentcore(request: TriageRequest) -> TriageResult:
    """Invoke AgentCore Runtime triage agent (AC-2). Uses request.session_id for memory continuity (AC-3)."""
    client = boto3.client("bedrock-agentcore", region_name=REGION)
    # AgentCore requires runtimeSessionId length >= 33 (e.g. UUID); use client's if valid else generate
    raw_session = request.session_id or ""
    session_id = raw_session if len(raw_session) >= 33 else str(uuid.uuid4())
    payload = {
        "symptoms": request.symptoms,
        "vitals": request.vitals or {},
        "age_years": request.age_years,
        "sex": request.sex,
    }
    if request.patient_id:
        payload["patient_id"] = request.patient_id

    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=TRIAGE_AGENT_RUNTIME_ARN,
            runtimeSessionId=session_id,
            payload=json.dumps(payload).encode("utf-8"),
        )
    except Exception as e:
        logger.error("AgentCore triage invocation failed: %s", e)
        out = _safety_fallback(str(e))
        out.session_id = session_id
        return out

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
                    if isinstance(data, dict):
                        result = _tool_input_to_result(data)
                        if result:
                            result.session_id = session_id
                            return result
                except json.JSONDecodeError:
                    pass
    else:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                result = _tool_input_to_result(data)
                if result:
                    result.session_id = session_id
                    return result
        except json.JSONDecodeError as e:
            logger.warning("AgentCore triage response not valid JSON: %s", e)

    out = _safety_fallback("AgentCore did not return structured triage result")
    out.session_id = session_id
    return out


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
                        result.session_id = request.session_id
                        return result

    return _safety_fallback("Agent did not return structured triage result")


def _assess_via_converse(request: TriageRequest) -> TriageResult:
    """
    Use Converse API with tool use (Claude Cookbook pattern).
    When Gateway/Eka is configured, model may call search_indian_medications or search_treatment_protocols
    before submit_triage_result; we execute those via Gateway and loop until submit_triage_result.
    """
    from triage.core.gateway_client import is_gateway_configured, search_medications, search_protocols

    model_id = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-v2:0")
    client = boto3.client("bedrock-runtime", region_name=REGION)
    tool_config = get_triage_tool_config_with_eka()
    user_prompt = _build_user_prompt(request)

    messages = [
        {"role": "user", "content": [{"text": user_prompt}]},
    ]
    max_rounds = 8
    for _ in range(max_rounds):
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
            return _safety_fallback(str(e))
        output = response.get("output", {})
        stop_reason = response.get("stopReason", "")
        msg = output.get("message", {})

        if stop_reason == "tool_use":
            content = msg.get("content", [])
            tool_results = []
            for block in content:
                if "toolUse" in block:
                    tool = block["toolUse"]
                    name = tool.get("name", "")
                    tool_id = tool.get("toolUseId", "")
                    tool_input = tool.get("input", {}) or {}
                    if name == "submit_triage_result":
                        result = _tool_input_to_result(tool_input)
                        if result:
                            result.session_id = request.session_id
                            return result
                        tool_results.append({"toolUseId": tool_id, "text": "Invalid tool input."})
                    elif name == "search_indian_medications" and is_gateway_configured():
                        try:
                            out = search_medications(
                                drug_name=tool_input.get("drug_name"),
                                form=tool_input.get("form"),
                                generic_names=tool_input.get("generic_names"),
                            )
                            text = json.dumps(out.get("medications", out), indent=2)
                        except Exception as e:
                            text = f"Error: {e}"
                        tool_results.append({"toolUseId": tool_id, "text": text})
                    elif name == "search_treatment_protocols" and is_gateway_configured():
                        try:
                            out = search_protocols(queries=tool_input.get("queries", []))
                            text = json.dumps(out.get("protocols", out), indent=2)
                        except Exception as e:
                            text = f"Error: {e}"
                        tool_results.append({"toolUseId": tool_id, "text": text})
                    else:
                        tool_results.append({"toolUseId": tool_id, "text": "Tool not available."})
            if tool_results:
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": [
                        {"toolResult": {"toolUseId": tr["toolUseId"], "content": [{"text": tr["text"]}]}}
                        for tr in tool_results
                    ],
                })
            else:
                break
        else:
            break

    return _safety_fallback("Model did not call submit_triage_result tool")
