#!/usr/bin/env python3
"""
Set Gateway env vars on the Hospital Matcher AgentCore Runtime.

Enables the Hospital Matcher runtime to call Gateway tools: get_hospitals (real hospital
data with lat/lon) and get_route (Routing agent → Google Maps). Without these env vars,
the runtime uses in-agent synthetic hospitals (no lat/lon) and get_route_tool returns stub.

Normally this is done automatically when you run setup_agentcore_gateway.py (unless you pass
--skip-runtime-env). Re-run this script after redeploying the Hospital Matcher agent
(agentcore deploy), because deploy can overwrite runtime env vars.

Reads gateway config from Secrets Manager and Hospital Matcher runtime ARN from api_config
secret (set by Terraform) or env or infrastructure/terraform.tfvars (agent_runtime_arn).

Prerequisites:
- Gateway setup has been run: python3 scripts/setup_agentcore_gateway.py (with get_hospitals + routing targets)
- Hospital Matcher uses AgentCore: use_agentcore = true and agent_runtime_arn set in tfvars
- IAM: Your user/role needs bedrock-agentcore:GetAgentRuntime and bedrock-agentcore:UpdateAgentRuntime

Usage (from project root):

  # Use agent_runtime_arn from terraform.tfvars (default):
  python3 scripts/enable_gateway_on_hospital_matcher_runtime.py

  # Or set the ARN explicitly:
  AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/hospital_matcher_agent-xxx python3 scripts/enable_gateway_on_hospital_matcher_runtime.py

  # Dry run (print vars, do not call update):
  python3 scripts/enable_gateway_on_hospital_matcher_runtime.py --dry-run

  # Point to terraform.tfvars explicitly:
  python3 scripts/enable_gateway_on_hospital_matcher_runtime.py --tfvars /path/to/infrastructure/terraform.tfvars
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import boto3
from botocore.exceptions import ClientError

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
from load_gateway_config import get_gateway_config


def get_hospital_matcher_runtime_arn(tfvars_path: str | None = None) -> str:
    """Get Hospital Matcher AgentCore runtime ARN from api_config secret, env, or infrastructure/terraform.tfvars."""
    arn = (os.environ.get("AGENT_RUNTIME_ARN") or "").strip()
    if arn:
        return arn
    # Prefer api_config secret (set by Terraform when use_agentcore and agent_runtime_arn are set)
    try:
        sys.path.insert(0, _SCRIPT_DIR)
        from load_api_config import get_api_config
        cfg = get_api_config()
        arn = (cfg.get("agent_runtime_arn") or "").strip()
        if arn:
            return arn
    except Exception:
        pass
    if tfvars_path and os.path.isfile(tfvars_path):
        try:
            with open(tfvars_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("agent_runtime_arn") and "=" in line:
                        m = re.search(r'["\']([^"\']+)["\']', line)
                        if m:
                            return m.group(1).strip()
        except OSError:
            pass
    repo_root = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
    cwd = os.getcwd()
    candidates = [
        os.path.join(repo_root, "infrastructure", "terraform.tfvars"),
        os.path.join(cwd, "infrastructure", "terraform.tfvars"),
        os.path.join(cwd, "terraform.tfvars"),
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("agent_runtime_arn") and "=" in line:
                        m = re.search(r'["\']([^"\']+)["\']', line)
                        if m:
                            return m.group(1).strip()
        except OSError:
            continue
    return ""


def arn_to_runtime_id(arn: str) -> str:
    if "/" in arn:
        return arn.split("runtime/")[-1].strip()
    return arn


def build_gateway_env_vars(config: dict) -> dict[str, str]:
    client_info = config.get("client_info") or {}
    return {
        "GATEWAY_MCP_URL": (config.get("gateway_url") or "").strip(),
        "GATEWAY_CLIENT_ID": (client_info.get("client_id") or "").strip(),
        "GATEWAY_CLIENT_SECRET": (client_info.get("client_secret") or "").strip(),
        "GATEWAY_TOKEN_ENDPOINT": (client_info.get("token_endpoint") or "").strip(),
        "GATEWAY_SCOPE": (client_info.get("scope") or "bedrock-agentcore-gateway").strip()
        or "bedrock-agentcore-gateway",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enable Gateway on Hospital Matcher AgentCore Runtime (get_hospitals + get_route)."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print env vars and exit without updating")
    parser.add_argument("--tfvars", metavar="PATH", help="Path to terraform.tfvars")
    args = parser.parse_args()

    region = os.environ.get("AWS_REGION", "us-east-1")

    try:
        config = get_gateway_config()
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("ERROR: Gateway config secret not found. Run setup_agentcore_gateway.py first.", file=sys.stderr)
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    client_info = config.get("client_info") or {}
    if not client_info:
        print("ERROR: gateway config has no client_info. Run setup_agentcore_gateway.py first.", file=sys.stderr)
        return 1

    gateway_vars = build_gateway_env_vars(config)
    if not gateway_vars.get("GATEWAY_MCP_URL"):
        print("ERROR: gateway_url missing in config.", file=sys.stderr)
        return 1

    arn = get_hospital_matcher_runtime_arn(tfvars_path=args.tfvars)
    if not arn:
        print(
            "ERROR: Hospital Matcher runtime ARN not set. Set AGENT_RUNTIME_ARN or set agent_runtime_arn in infrastructure/terraform.tfvars.",
            file=sys.stderr,
        )
        return 1
    runtime_id = arn_to_runtime_id(arn)
    if not runtime_id:
        print("ERROR: Could not parse agentRuntimeId from ARN.", file=sys.stderr)
        return 1

    if args.dry_run:
        print("Dry run: would set these environment variables on runtime", runtime_id, file=sys.stderr)
        for k, v in gateway_vars.items():
            safe = "(set)" if k == "GATEWAY_CLIENT_SECRET" and v else v
            print(f"  {k}={safe}")
        return 0

    control = boto3.client("bedrock-agentcore-control", region_name=region)
    try:
        current = control.get_agent_runtime(agentRuntimeId=runtime_id)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"ERROR: Runtime not found: {runtime_id}. Check agent_runtime_arn.", file=sys.stderr)
        elif e.response["Error"]["Code"] == "AccessDeniedException":
            print(
                "ERROR: IAM missing GetAgentRuntime/UpdateAgentRuntime. See https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html",
                file=sys.stderr,
            )
        else:
            print(f"ERROR: get_agent_runtime: {e}", file=sys.stderr)
        return 1

    existing = current.get("environmentVariables") or {}
    merged = dict(existing)
    merged.update(gateway_vars)

    try:
        control.update_agent_runtime(
            agentRuntimeId=runtime_id,
            agentRuntimeArtifact=current["agentRuntimeArtifact"],
            networkConfiguration=current["networkConfiguration"],
            roleArn=current["roleArn"],
            environmentVariables=merged,
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "AccessDeniedException":
            print("ERROR: IAM missing UpdateAgentRuntime.", file=sys.stderr)
        else:
            print(f"ERROR: update_agent_runtime: {e}", file=sys.stderr)
        return 1

    print(f"Updated runtime {runtime_id} with Gateway env vars. Hospital Matcher can now use get_hospitals and get_route.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
