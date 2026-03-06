#!/usr/bin/env python3
"""
Get Cognito Id token for the test RMP user using credentials from AWS Secrets Manager (boto3).
No secrets on the command line; email and password are read from the rmp-test-credentials secret.

Usage (from project root):
  TOKEN=$(python scripts/get_rmp_token.py)
  curl -s -X POST "$API_URL/triage" -H "Authorization: Bearer $TOKEN" ...

Requires:
  - Terraform apply with rmp_test_email and rmp_test_password set in terraform.tfvars
    (stored in Secrets Manager at {prefix}/rmp-test-credentials)
  - api_config secret (has cognito_user_pool_id, cognito_app_client_id)
"""

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError


def _get_api_config() -> dict:
    secret_name = os.environ.get("API_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        secret_name = f"{os.environ.get('NAME_PREFIX', 'emergency-medical-triage-dev')}/api-config"
    region = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("secretsmanager", region_name=region)
    resp = client.get_secret_value(SecretId=secret_name)
    return json.loads(resp["SecretString"])


def _get_rmp_test_credentials(prefix: str) -> dict:
    secret_name = f"{prefix}/rmp-test-credentials"
    region = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("secretsmanager", region_name=region)
    resp = client.get_secret_value(SecretId=secret_name)
    return json.loads(resp["SecretString"])


def main() -> None:
    try:
        api_config = _get_api_config()
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("api_config secret not found. Run: cd infrastructure && terraform apply", file=sys.stderr)
        else:
            print(f"Failed to read api_config: {e}", file=sys.stderr)
        sys.exit(1)

    pool_id = (api_config.get("cognito_user_pool_id") or "").strip()
    client_id = (api_config.get("cognito_app_client_id") or "").strip()
    if not pool_id or not client_id:
        print("api_config missing cognito_user_pool_id or cognito_app_client_id. Re-run terraform apply.", file=sys.stderr)
        sys.exit(1)

    prefix = os.environ.get("NAME_PREFIX", "emergency-medical-triage-dev")
    if "/" in (api_config.get("api_config_secret_name") or ""):
        prefix = (api_config["api_config_secret_name"] or "").rsplit("/", 1)[0] or prefix

    try:
        creds = _get_rmp_test_credentials(prefix)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(
                f"Secret {prefix}/rmp-test-credentials not found. Set rmp_test_email and rmp_test_password in "
                "infrastructure/terraform.tfvars and run terraform apply.",
                file=sys.stderr,
            )
        else:
            print(f"Failed to read rmp-test-credentials: {e}", file=sys.stderr)
        sys.exit(1)

    email = (creds.get("email") or "").strip()
    password = creds.get("password") or ""
    if not email or not password:
        print("rmp-test-credentials must contain email and password.", file=sys.stderr)
        sys.exit(1)

    try:
        client = boto3.client("cognito-idp", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        resp = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": email, "PASSWORD": password},
        )
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        msg = e.response.get("Error", {}).get("Message", str(e))
        print(f"Cognito auth failed ({code}): {msg}", file=sys.stderr)
        sys.exit(1)

    result = resp.get("AuthenticationResult") or {}
    id_token = result.get("IdToken")
    if not id_token:
        print("No IdToken in Cognito response.", file=sys.stderr)
        sys.exit(1)

    print(id_token)


if __name__ == "__main__":
    main()
