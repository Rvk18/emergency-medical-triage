#!/usr/bin/env python3
"""
Create an AgentCore Policy Engine and attach it to the existing Gateway.

Restricts Gateway tool calls to a whitelist (principle of least privilege).
Run after setup_agentcore_gateway.py. Uses the same gateway config from Secrets Manager.

Cedar format (correct):
  - Actions: target___tool (triple underscore). Do NOT use gateway ARN in the action.
  - Resource: AgentCore::Gateway::"arn:aws:bedrock-agentcore:...:gateway/<gateway_id>"
  - ALLOWED_ACTIONS must list only tools that actually exist on the gateway (schema).
    "Unrecognized action" means either wrong format OR the tool is not in the gateway schema.

See docs/backend/POLICY-RCA.md for root cause analysis and how to define policies for other gateways.

Docs:
  Policy:        https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html
  Create policy: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-create-policies.html
  Add to engine: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/add-policies-to-engine.html
  Examples:       https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/example-policies.html

Usage:
  python scripts/setup_agentcore_policy.py              # Default: target___tool + IGNORE_ALL_FINDINGS (policy enforces; console may show findings)
  python scripts/setup_agentcore_policy.py --log-only # Attach in LOG_ONLY
  python scripts/setup_agentcore_policy.py --strict-validation  # ARN-prefixed + FAIL_ON_ANY_FINDINGS (fails: validator rejects all formats on this gateway)
  python scripts/setup_agentcore_policy.py --dry-run  # Print Cedar and exit
"""

import json
import logging
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from load_gateway_config import get_gateway_config

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "us-east-1")
POLICY_ENGINE_NAME = "emergency_triage_gateway_policy"

# Allowed Gateway tools. MUST match tools actually registered on the gateway (Cedar schema).
# Do not assume names: only include tools that exist on the gateway. "Unrecognized action" = tool not in schema.
# Format: target___tool (triple underscore), per MCP gateway tool naming.
# Include get_protocol_publishers and search_pharmacology only after running setup_agentcore_gateway.py
# (so Eka target has all four tools), then enable_gateway_on_*_runtime / enable_eka_on_runtime. See POLICY-RCA.md.
ALLOWED_ACTIONS = [
    "eka-target___search_medications",
    "eka-target___search_protocols",
    "eka-target___get_protocol_publishers",
    "eka-target___search_pharmacology",
    "maps-target___get_directions",
    "maps-target___geocode_address",
    "routing-target___get_route",
    "get-hospitals-target___get_hospitals",
]

# Validator rejects all formats (plain target___tool and ARN-prefixed). Runtime uses target___tool (Overly Permissive warning).
# Default: use target___tool + IGNORE_ALL_FINDINGS so policy is created and enforces correctly; console may still show findings.
def _schema_actions(gateway_arn: str, use_arn_prefix: bool = False) -> list[str]:
    """Action IDs: use_arn_prefix -> gateway_arn__target__tool; else target___tool (runtime format)."""
    if use_arn_prefix:
        return [f"{gateway_arn}__{a.replace('___', '__')}" for a in ALLOWED_ACTIONS]
    return list(ALLOWED_ACTIONS)


def _gateway_arn(control_client, gateway_id: str) -> str:
    """Return Gateway ARN for Cedar resource. Build from get_gateway or construct."""
    try:
        resp = control_client.get_gateway(gatewayIdentifier=gateway_id)
        gw = resp.get("gateway") or resp
        arn = gw.get("gatewayArn")
        if arn:
            return arn
    except Exception as e:
        logger.warning("get_gateway for ARN: %s", e)
    sts = boto3.client("sts", region_name=REGION)
    account = sts.get_caller_identity()["Account"]
    return f"arn:aws:bedrock-agentcore:{REGION}:{account}:gateway/{gateway_id}"


def _cedar_permit_statement(gateway_arn: str, actions: list[str]) -> str:
    """Single permit policy: any OAuthUser may call only the allowed tools on this gateway."""
    actions_str = ", ".join(
        f'AgentCore::Action::"{a}"' for a in actions
    )
    return (
        f'permit(\n'
        f'  principal is AgentCore::OAuthUser,\n'
        f'  action in [{actions_str}],\n'
        f'  resource == AgentCore::Gateway::"{gateway_arn}"\n'
        f');'
    )


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    log_only = "--log-only" in sys.argv
    # Default: target___tool + IGNORE_ALL_FINDINGS (validator rejects all formats; runtime uses target___tool).
    # Use --strict-validation to try ARN-prefixed + FAIL_ON_ANY_FINDINGS (still fails on this gateway).
    ignore_validation = "--strict-validation" not in sys.argv
    config = get_gateway_config()
    gateway_id = (config.get("gateway_id") or "").strip()
    if not gateway_id:
        logger.error("gateway_id missing in gateway config. Run setup_agentcore_gateway.py first.")
        return 1

    control_client = boto3.client("bedrock-agentcore-control", region_name=REGION)
    gateway_arn = _gateway_arn(control_client, gateway_id)
    schema_actions = _schema_actions(gateway_arn, use_arn_prefix=not ignore_validation)

    if dry_run:
        print("Cedar policy statement (action = target___tool per Overly Permissive warning):")
        print(_cedar_permit_statement(gateway_arn, schema_actions))
        print("\nActions:", schema_actions)
        return 0

    # Create policy engine
    try:
        create_resp = control_client.create_policy_engine(
            name=POLICY_ENGINE_NAME,
            description="Allow only whitelisted Gateway tools for emergency triage (Triage, Hospital Matcher, Routing).",
        )
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ConflictException":
            logger.info("Policy engine %s already exists; reusing.", POLICY_ENGINE_NAME)
            policy_engine_id = None
            policy_engine_arn = None
            paginator = control_client.get_paginator("list_policy_engines")
            for page in paginator.paginate():
                for pe in page.get("policyEngines", []):
                    if pe.get("name") == POLICY_ENGINE_NAME:
                        policy_engine_id = pe.get("policyEngineId")
                        policy_engine_arn = pe.get("policyEngineArn")
                        break
                if policy_engine_id is not None:
                    break
            if policy_engine_id is None:
                logger.error("Could not find existing policy engine %s", POLICY_ENGINE_NAME)
                return 1
        else:
            raise
    else:
        policy_engine_id = create_resp.get("policyEngineId")
        policy_engine_arn = create_resp.get("policyEngineArn")
        logger.info("Created policy engine: %s", policy_engine_arn)

    # Wait for policy engine ACTIVE
    for _ in range(30):
        try:
            pe_status = control_client.get_policy_engine(policyEngineId=policy_engine_id)
            status = (pe_status.get("policyEngine") or pe_status).get("status", "")
            if status == "ACTIVE":
                break
            logger.info("Policy engine status: %s; waiting...", status)
        except Exception as e:
            logger.warning("get_policy_engine: %s", e)
        time.sleep(2)
    else:
        logger.warning("Policy engine not yet ACTIVE; continuing anyway.")

    # Attach policy engine to gateway FIRST so Cedar schema is available from gateway tool manifest.
    # Policies are validated against this schema; creating policies before attach causes "Create failed".
    gw_detail = control_client.get_gateway(gatewayIdentifier=gateway_id)
    gw = gw_detail.get("gateway") or gw_detail
    update_params = {
        "gatewayIdentifier": gateway_id,
        "name": gw.get("name") or "emergency-triage-hospitals",
        "roleArn": gw.get("roleArn") or "",
        "protocolType": gw.get("protocolType") or "MCP",
        "authorizerType": gw.get("authorizerType") or "CUSTOM_JWT",
        "policyEngineConfiguration": {
            "mode": "LOG_ONLY" if log_only else "ENFORCE",
            "arn": policy_engine_arn,
        },
    }
    if gw.get("authorizerConfiguration"):
        update_params["authorizerConfiguration"] = gw["authorizerConfiguration"]
    control_client.update_gateway(**update_params)
    mode = "LOG_ONLY" if log_only else "ENFORCE"
    logger.info("Attached policy engine to gateway %s (%s) so schema is available", gateway_id, mode)
    time.sleep(5)  # Allow schema propagation

    # Delete any existing failed (or old) policies so we can create fresh.
    try:
        deleted_any = False
        for page in control_client.get_paginator("list_policies").paginate(policyEngineId=policy_engine_id):
            for p in page.get("policies", []):
                pid, pname = p.get("policyId"), p.get("name") or ""
                if pid and (pname == "allow_whitelisted_tools" or (pname or "").startswith("allow_whitelisted_tools")):
                    try:
                        control_client.delete_policy(policyEngineId=policy_engine_id, policyId=pid)
                        logger.info("Deleted existing policy: %s", pname)
                        deleted_any = True
                    except ClientError as e:
                        logger.warning("Could not delete policy %s: %s", pname, e)
        if deleted_any:
            time.sleep(10)  # Allow delete to complete before creating
    except Exception as e:
        logger.warning("list_policies/delete: %s", e)

    # Create single policy. Runtime uses action=target___tool; validation schema expects ARN prefix.
    # Use IGNORE_ALL_FINDINGS with --ignore-validation so policy is created and enforced correctly at runtime.
    policy_name = "allow_whitelisted_tools"
    cedar_stmt = _cedar_permit_statement(gateway_arn, schema_actions)
    if ignore_validation:
        logger.info("Using validationMode=IGNORE_ALL_FINDINGS (action=target___tool; validator rejects all formats on this gateway)")
    try:
        control_client.create_policy(
            policyEngineId=policy_engine_id,
            name=policy_name,
            description="Permit only whitelisted Gateway tools; default deny all others.",
            definition={"cedar": {"statement": cedar_stmt}},
            validationMode="IGNORE_ALL_FINDINGS" if ignore_validation else "FAIL_ON_ANY_FINDINGS",
        )
        logger.info("Created policy: %s", policy_name)
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ConflictException":
            logger.info("Policy %s already exists; skipping.", policy_name)
        else:
            raise

    print("\nPolicy setup complete. Gateway policy mode:", mode)
    print("Allowed tools:", schema_actions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
