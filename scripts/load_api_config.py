#!/usr/bin/env python3
"""
Load API and Gateway config from AWS Secrets Manager (boto3).

Config is already set by Terraform (api_config secret) when you run terraform apply.
Lambdas and the API read the same secret automatically. This script only loads it into
your shell for local testing (curl, scripts); run once per terminal.

  # Set env vars in shell for curl, etc.:
  eval $(python scripts/load_api_config.py --exports)
  curl -s "$API_URL"health

  # Get only API URL:
  API_URL=$(python scripts/load_api_config.py --url)

From Python (e.g. from project root with scripts on path):
  import sys
  sys.path.insert(0, "scripts")
  from load_api_config import get_api_config
  config = get_api_config()
  url = config["api_gateway_url"]
"""

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError


def get_api_config() -> dict:
    """
    Fetch api_config from Secrets Manager (boto3).
    The secret is created by Terraform when you run: cd infrastructure && terraform apply
    """
    secret_name = os.environ.get("API_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        prefix = os.environ.get("NAME_PREFIX", "emergency-medical-triage-dev")
        secret_name = f"{prefix}/api-config"
    region = os.environ.get("AWS_REGION", "us-east-1")
    try:
        client = boto3.client("secretsmanager", region_name=region)
        resp = client.get_secret_value(SecretId=secret_name)
        return json.loads(resp["SecretString"])
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise SystemExit(
                f"Secret '{secret_name}' not found. Create it by running: cd infrastructure && terraform apply"
            ) from e
        raise


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--url":
        config = get_api_config()
        print(config.get("api_gateway_url", ""))
        return
    config = get_api_config()
    exports = [
        ("API_URL", config.get("api_gateway_url", "")),
        ("API_HEALTH_URL", config.get("api_gateway_health_url", "")),
        ("GATEWAY_GET_HOSPITALS_LAMBDA_ARN", config.get("gateway_get_hospitals_lambda_arn", "")),
        ("GATEWAY_EKA_LAMBDA_ARN", config.get("gateway_eka_lambda_arn", "")),
        ("AWS_REGION", config.get("region", "")),
    ]
    for name, value in exports:
        safe = value.replace("'", "'\"'\"'") if value else ""
        print(f"export {name}='{safe}'")
    print("Loaded API config from Secrets Manager", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
