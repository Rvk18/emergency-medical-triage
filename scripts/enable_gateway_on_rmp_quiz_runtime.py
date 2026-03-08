#!/usr/bin/env python3
"""
Set Gateway (Eka) env vars on the RMP Quiz AgentCore Runtime so the quiz agent can call Eka tools.

Reads gateway config from Secrets Manager and RMP quiz runtime ARN from env or infrastructure/terraform.tfvars.

Prerequisites:
- Gateway setup: python3 scripts/setup_agentcore_gateway.py (with Eka)
- RMP Quiz agent deployed: cd agentcore/agent && agentcore deploy --agent rmp_quiz_agent
- Set rmp_quiz_agent_runtime_arn in terraform.tfvars (from deploy output)

Usage (from project root):

  python3 scripts/enable_gateway_on_rmp_quiz_runtime.py
  RMP_QUIZ_AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:...:runtime/rmp_quiz_agent-xxx python3 scripts/enable_gateway_on_rmp_quiz_runtime.py
  python3 scripts/enable_gateway_on_rmp_quiz_runtime.py --dry-run
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


def get_rmp_quiz_runtime_arn(tfvars_path: str | None = None) -> str:
    """Get RMP Quiz AgentCore runtime ARN from env or terraform.tfvars."""
    arn = (os.environ.get("RMP_QUIZ_AGENT_RUNTIME_ARN") or "").strip()
    if arn:
        return arn
    if tfvars_path and os.path.isfile(tfvars_path):
        try:
            with open(tfvars_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("rmp_quiz_agent_runtime_arn") and "=" in line:
                        m = re.search(r'["\']([^"\']+)["\']', line)
                        if m:
                            return m.group(1).strip()
        except OSError:
            pass
    repo_root = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
    cwd = os.getcwd()
    for path in [
        os.path.join(repo_root, "infrastructure", "terraform.tfvars"),
        os.path.join(cwd, "infrastructure", "terraform.tfvars"),
        os.path.join(cwd, "terraform.tfvars"),
    ]:
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("rmp_quiz_agent_runtime_arn") and "=" in line:
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
        "GATEWAY_SCOPE": (client_info.get("scope") or "bedrock-agentcore-gateway").strip() or "bedrock-agentcore-gateway",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Enable Gateway (Eka) on RMP Quiz AgentCore Runtime.")
    parser.add_argument("--dry-run", action="store_true", help="Print env vars and exit")
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
    gateway_vars = build_gateway_env_vars(config)
    if not gateway_vars.get("GATEWAY_MCP_URL"):
        print("ERROR: gateway_url missing in config.", file=sys.stderr)
        return 1

    arn = get_rmp_quiz_runtime_arn(tfvars_path=args.tfvars)
    if not arn:
        print("ERROR: RMP Quiz runtime ARN not set. Set RMP_QUIZ_AGENT_RUNTIME_ARN or add rmp_quiz_agent_runtime_arn to terraform.tfvars.", file=sys.stderr)
        return 1
    runtime_id = arn_to_runtime_id(arn)

    if args.dry_run:
        print("Dry run: would set Gateway env vars on runtime", runtime_id, file=sys.stderr)
        for k, v in gateway_vars.items():
            safe = "(set)" if k == "GATEWAY_CLIENT_SECRET" and v else v
            print(f"  {k}={safe}")
        return 0

    control = boto3.client("bedrock-agentcore-control", region_name=region)
    try:
        current = control.get_agent_runtime(agentRuntimeId=runtime_id)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"ERROR: Runtime not found: {runtime_id}. Deploy first: agentcore deploy --agent rmp_quiz_agent", file=sys.stderr)
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
        print(f"ERROR: update_agent_runtime: {e}", file=sys.stderr)
        return 1

    print(f"Updated runtime {runtime_id} with Gateway env vars. RMP Quiz can now call Eka tools.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
