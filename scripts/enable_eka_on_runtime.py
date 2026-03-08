#!/usr/bin/env python3
"""
Set Gateway (Eka) env vars on the triage AgentCore Runtime so triage can call Eka tools.

Keeps AgentCore triage and enables Eka on the Runtime by updating the runtime's
environment variables via the Bedrock AgentCore Control API. Reads gateway config
from Secrets Manager and triage runtime ARN from env or infrastructure/terraform.tfvars.

Prerequisites:
- Gateway setup has been run: python3 scripts/setup_agentcore_gateway.py (with Eka)
- Triage uses AgentCore: use_agentcore_triage = true and triage_agent_runtime_arn set
- IAM: Your user/role needs bedrock-agentcore:GetAgentRuntime and bedrock-agentcore:UpdateAgentRuntime
  (see https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html)

Usage (from project root):

  # Use triage runtime ARN from terraform.tfvars (default):
  python3 scripts/enable_eka_on_runtime.py

  # Or set the ARN explicitly:
  TRIAGE_AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/triage_agent-xxx python3 scripts/enable_eka_on_runtime.py

  # Dry run (print vars, do not call update):
  python3 scripts/enable_eka_on_runtime.py --dry-run

  # Point to terraform.tfvars explicitly if auto-discovery fails:
  python3 scripts/enable_eka_on_runtime.py --tfvars /path/to/infrastructure/terraform.tfvars
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import boto3
from botocore.exceptions import ClientError

# Allow importing from same directory when run as script
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
from load_gateway_config import get_gateway_config


def get_triage_runtime_arn(tfvars_path: str | None = None) -> str:
    """Get triage AgentCore runtime ARN from env or infrastructure/terraform.tfvars."""
    arn = (os.environ.get("TRIAGE_AGENT_RUNTIME_ARN") or "").strip()
    if arn:
        return arn
    # Explicit path from --tfvars
    if tfvars_path and os.path.isfile(tfvars_path):
        try:
            with open(tfvars_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("triage_agent_runtime_arn") and "=" in line:
                        m = re.search(r'["\']([^"\']+)["\']', line)
                        if m:
                            return m.group(1).strip()
        except OSError:
            pass
    # Try several locations for terraform.tfvars (repo root relative to script, then cwd)
    repo_root = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
    cwd = os.getcwd()
    candidates = [
        os.path.join(repo_root, "infrastructure", "terraform.tfvars"),
        os.path.join(cwd, "infrastructure", "terraform.tfvars"),
        os.path.join(cwd, "terraform.tfvars"),
    ]
    for tfvars_path in candidates:
        if not os.path.isfile(tfvars_path):
            continue
        try:
            with open(tfvars_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("triage_agent_runtime_arn") and "=" in line:
                        m = re.search(r'["\']([^"\']+)["\']', line)
                        if m:
                            return m.group(1).strip()
        except OSError:
            continue
    return ""


def arn_to_runtime_id(arn: str) -> str:
    """Extract agentRuntimeId from ARN (part after 'runtime/')."""
    if "/" in arn:
        return arn.split("runtime/")[-1].strip()
    return arn


def build_gateway_env_vars(config: dict) -> dict[str, str]:
    """Build the five Gateway env vars from gateway config (for Eka on triage)."""
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
    parser = argparse.ArgumentParser(description="Enable Eka on triage AgentCore Runtime by setting Gateway env vars.")
    parser.add_argument("--dry-run", action="store_true", help="Print env vars and exit without calling UpdateAgentRuntime")
    parser.add_argument("--tfvars", metavar="PATH", help="Path to terraform.tfvars (default: auto-detect from repo or cwd)")
    args = parser.parse_args()

    region = os.environ.get("AWS_REGION", "us-east-1")

    # 1. Gateway config from Secrets Manager
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

    # 2. Triage runtime ARN
    arn = get_triage_runtime_arn(tfvars_path=args.tfvars)
    if not arn:
        print(
            "ERROR: Triage runtime ARN not set. Set TRIAGE_AGENT_RUNTIME_ARN or run from repo with infrastructure/terraform.tfvars containing triage_agent_runtime_arn.",
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

    # 3. Get current runtime config
    control = boto3.client("bedrock-agentcore-control", region_name=region)
    try:
        current = control.get_agent_runtime(agentRuntimeId=runtime_id)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"ERROR: Runtime not found: {runtime_id}. Check triage_agent_runtime_arn.", file=sys.stderr)
        elif e.response["Error"]["Code"] == "AccessDeniedException":
            print(
                "ERROR: Your IAM user/role is not allowed to call GetAgentRuntime. Add these permissions:",
                file=sys.stderr,
            )
            print(
                "  bedrock-agentcore:GetAgentRuntime, bedrock-agentcore:UpdateAgentRuntime",
                file=sys.stderr,
            )
            print(
                "  (See https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html)",
                file=sys.stderr,
            )
        else:
            print(f"ERROR: get_agent_runtime: {e}", file=sys.stderr)
        return 1

    # 4. Merge env vars: existing + Gateway (Gateway overrides)
    existing = current.get("environmentVariables") or {}
    merged = dict(existing)
    merged.update(gateway_vars)

    # 5. Update runtime (required: agentRuntimeArtifact, networkConfiguration, roleArn)
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
            print(
                "ERROR: Your IAM user/role is not allowed to call UpdateAgentRuntime. Add permission: bedrock-agentcore:UpdateAgentRuntime",
                file=sys.stderr,
            )
        else:
            print(f"ERROR: update_agent_runtime: {e}", file=sys.stderr)
        return 1

    print(f"Updated runtime {runtime_id} with Gateway env vars. Eka is enabled for triage.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
