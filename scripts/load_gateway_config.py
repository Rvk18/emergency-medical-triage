#!/usr/bin/env python3
"""
Load AgentCore Gateway config from AWS Secrets Manager and export env vars for OAuth.

The full config (including client_id, client_secret, token_endpoint) is stored in
Secrets Manager by setup_agentcore_gateway.py. This script reads it and prints
shell exports so you can set env vars on AgentCore runtimes or use locally.

Usage (from project root):

  # Export env vars into your shell (then set these on the AgentCore Runtime in Console):
  eval $(python scripts/load_gateway_config.py)

  # Or print the secret name only (e.g. for AWS Console lookup):
  python scripts/load_gateway_config.py --secret-name
"""

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError


def get_gateway_config() -> dict:
    """
    Fetch gateway config from Secrets Manager.
    Secret name from env GATEWAY_CONFIG_SECRET_NAME or api_config.gateway_config_secret_name or default.
    """
    secret_name = os.environ.get("GATEWAY_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        try:
            api_name = os.environ.get("API_CONFIG_SECRET_NAME", "").strip() or f"{os.environ.get('NAME_PREFIX', 'emergency-medical-triage-dev')}/api-config"
            region = os.environ.get("AWS_REGION", "us-east-1")
            client = boto3.client("secretsmanager", region_name=region)
            resp = client.get_secret_value(SecretId=api_name)
            api_cfg = json.loads(resp["SecretString"])
            secret_name = (api_cfg.get("gateway_config_secret_name") or "").strip()
        except Exception:
            pass
        if not secret_name:
            secret_name = f"{os.environ.get('NAME_PREFIX', 'emergency-medical-triage-dev')}/gateway-config"
    region = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("secretsmanager", region_name=region)
    resp = client.get_secret_value(SecretId=secret_name)
    return json.loads(resp["SecretString"])


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--secret-name":
        secret_name = (
            os.environ.get("GATEWAY_CONFIG_SECRET_NAME", "").strip()
            or f"{os.environ.get('NAME_PREFIX', 'emergency-medical-triage-dev')}/gateway-config"
        )
        try:
            api_name = os.environ.get("API_CONFIG_SECRET_NAME", "").strip() or f"{os.environ.get('NAME_PREFIX', 'emergency-medical-triage-dev')}/api-config"
            region = os.environ.get("AWS_REGION", "us-east-1")
            client = boto3.client("secretsmanager", region_name=region)
            resp = client.get_secret_value(SecretId=api_name)
            api_cfg = json.loads(resp["SecretString"])
            secret_name = (api_cfg.get("gateway_config_secret_name") or secret_name).strip()
        except Exception:
            pass
        print(secret_name)
        return

    config = get_gateway_config()
    client_info = config.get("client_info") or {}
    if not client_info:
        print("ERROR: gateway config has no client_info. Run setup_agentcore_gateway.py first.", file=sys.stderr)
        sys.exit(1)

    exports = [
        ("GATEWAY_MCP_URL", config.get("gateway_url", "")),
        ("GATEWAY_CLIENT_ID", client_info.get("client_id", "")),
        ("GATEWAY_CLIENT_SECRET", client_info.get("client_secret", "")),
        ("GATEWAY_TOKEN_ENDPOINT", client_info.get("token_endpoint", "")),
        ("GATEWAY_SCOPE", client_info.get("scope", "bedrock-agentcore-gateway") or "bedrock-agentcore-gateway"),
    ]
    for name, value in exports:
        safe = (value or "").replace("'", "'\"'\"'")
        print(f"export {name}='{safe}'")
    print("Loaded gateway config from Secrets Manager", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("ERROR: Gateway config secret not found. Run setup_agentcore_gateway.py after terraform apply.", file=sys.stderr)
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
