#!/usr/bin/env python3
"""
Create a Cognito test user for webapp login and API testing.
Uses the User Pool and App Client from Terraform (api_config).
User can log in immediately with the given password (no forced change).

Usage (from project root):
  # Get pool/client from Terraform, then create user:
  python scripts/create_cognito_test_user.py --email test@example.com --password 'YourSecurePass1!'

  # Or pass pool and client explicitly:
  python scripts/create_cognito_test_user.py --pool-id us-east-1_xxx --client-id xxx --email test@example.com --password 'YourSecurePass1!'

Requires: AWS credentials, Terraform apply already run (so User Pool exists).
Password must meet Cognito policy: 10+ chars, upper, lower, number, symbol.
"""

import argparse
import json
import os
import sys

import boto3
from botocore.exceptions import ClientError


def get_api_config() -> dict:
    secret_name = os.environ.get("API_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        prefix = os.environ.get("NAME_PREFIX", "emergency-medical-triage-dev")
        secret_name = f"{prefix}/api-config"
    region = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("secretsmanager", region_name=region)
    resp = client.get_secret_value(SecretId=secret_name)
    return json.loads(resp["SecretString"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Cognito test user for webapp login")
    parser.add_argument("--email", required=True, help="User email (used as username)")
    parser.add_argument("--password", required=True, help="Permanent password (must meet pool policy)")
    parser.add_argument("--pool-id", help="Cognito User Pool ID (default: from api_config)")
    parser.add_argument("--client-id", help="Cognito App Client ID (default: from api_config)")
    parser.add_argument("--region", default=os.environ.get("AWS_REGION", "us-east-1"), help="AWS region")
    args = parser.parse_args()

    email = args.email.strip()
    password = args.password
    region = args.region

    pool_id = args.pool_id
    client_id = args.client_id
    if not pool_id or not client_id:
        try:
            api_config = get_api_config()
            pool_id = pool_id or (api_config.get("cognito_user_pool_id") or "").strip()
            client_id = client_id or (api_config.get("cognito_app_client_id") or "").strip()
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print("api_config secret not found. Run: cd infrastructure && terraform apply", file=sys.stderr)
            else:
                print(f"Failed to read api_config: {e}", file=sys.stderr)
            return 1
    if not pool_id or not client_id:
        print("Missing cognito_user_pool_id or cognito_app_client_id. Pass --pool-id and --client-id or run terraform apply.", file=sys.stderr)
        return 1

    client = boto3.client("cognito-idp", region_name=region)

    # Create user with a temporary password first
    temp_password = "TempPass1!ChangeMe"
    try:
        client.admin_create_user(
            UserPoolId=pool_id,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ],
            TemporaryPassword=temp_password,
            MessageAction="SUPPRESS",  # Don't send welcome email
        )
        print(f"Created user {email}", file=sys.stderr)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code != "UsernameExistsException":
            print(f"admin_create_user failed ({code}): {e}", file=sys.stderr)
            return 1
        print(f"User {email} already exists; setting password.", file=sys.stderr)

    # Set permanent password so they can log in without "change password" flow
    try:
        client.admin_set_user_password(
            UserPoolId=pool_id,
            Username=email,
            Password=password,
            Permanent=True,
        )
        print(f"Password set for {email}", file=sys.stderr)
    except ClientError as e:
        print(f"admin_set_user_password failed: {e}", file=sys.stderr)
        return 1

    print(f"\nTest user ready. Use in webapp login:\n  Email: {email}\n  Password: (the one you passed)")
    print(f"\nCognito Pool ID: {pool_id}\nClient ID: {client_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
