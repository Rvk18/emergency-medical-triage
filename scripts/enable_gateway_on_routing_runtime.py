#!/usr/bin/env python3
"""
Set Gateway env vars on the Routing AgentCore Runtime.

The Routing agent calls maps-target___get_directions (Gateway → gateway_maps Lambda) to get
distance_km, duration_minutes, and directions_url (the Google Maps link). Without these env vars,
get_directions_tool returns stub and directions_url is null.

Normally this is done automatically when you run setup_agentcore_gateway.py (unless you pass
--skip-runtime-env). Re-run this script after redeploying the Routing agent (agentcore deploy),
because deploy can overwrite runtime env vars.

Reads gateway config from Secrets Manager and Routing runtime ARN from api_config secret
(set by Terraform) or env ROUTING_AGENT_RUNTIME_ARN or infrastructure/terraform.tfvars.

Usage (from project root):

  python3 scripts/enable_gateway_on_routing_runtime.py
  ROUTING_AGENT_RUNTIME_ARN=arn:... python3 scripts/enable_gateway_on_routing_runtime.py
  python3 scripts/enable_gateway_on_routing_runtime.py --dry-run
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


def get_routing_runtime_arn(tfvars_path: str | None = None) -> str:
    """Get Routing AgentCore runtime ARN from api_config secret, env, or tfvars."""
    arn = (os.environ.get("ROUTING_AGENT_RUNTIME_ARN") or "").strip()
    if arn:
        return arn
    try:
        from load_api_config import get_api_config
        cfg = get_api_config()
        arn = (cfg.get("routing_agent_runtime_arn") or "").strip()
        if arn:
            return arn
    except Exception:
        pass
    if tfvars_path and os.path.isfile(tfvars_path):
        try:
            with open(tfvars_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("routing_agent_runtime_arn") and "=" in line:
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
                    if line.startswith("routing_agent_runtime_arn") and "=" in line:
                        m = re.search(r'["\']([^"\']+)["\']', line)
                        if m:
                            return m.group(1).strip()
        except OSError:
            continue
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Enable Gateway on Routing AgentCore Runtime (directions_url).")
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
        print("ERROR: gateway config has no client_info.", file=sys.stderr)
        return 1

    gateway_vars = {
        "GATEWAY_MCP_URL": (config.get("gateway_url") or "").strip(),
        "GATEWAY_CLIENT_ID": (client_info.get("client_id") or "").strip(),
        "GATEWAY_CLIENT_SECRET": (client_info.get("client_secret") or "").strip(),
        "GATEWAY_TOKEN_ENDPOINT": (client_info.get("token_endpoint") or "").strip(),
        "GATEWAY_SCOPE": (client_info.get("scope") or "bedrock-agentcore-gateway").strip() or "bedrock-agentcore-gateway",
    }
    if not gateway_vars.get("GATEWAY_MCP_URL"):
        print("ERROR: gateway_url missing in config.", file=sys.stderr)
        return 1

    arn = get_routing_runtime_arn(tfvars_path=args.tfvars)
    if not arn:
        print("ERROR: Routing runtime ARN not set. Set ROUTING_AGENT_RUNTIME_ARN or routing_agent_runtime_arn in tfvars.", file=sys.stderr)
        return 1
    runtime_id = arn.split("runtime/")[-1].strip() if "/" in arn else arn

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
            print(f"ERROR: Runtime not found: {runtime_id}.", file=sys.stderr)
        elif e.response["Error"]["Code"] == "AccessDeniedException":
            print("ERROR: IAM missing GetAgentRuntime/UpdateAgentRuntime.", file=sys.stderr)
        else:
            print(f"ERROR: get_agent_runtime: {e}", file=sys.stderr)
        return 1

    existing = current.get("environmentVariables") or {}
    merged = {**existing, **gateway_vars}

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

    print("Updated Routing runtime with Gateway env vars. directions_url will work via maps-target.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
