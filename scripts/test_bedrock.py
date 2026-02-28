#!/usr/bin/env python3
"""
Test Bedrock model access.

Fetches config (region, model_id) from AWS Secrets Manager.
AWS credentials: use default chain (aws configure, IAM role, env).
Run: python scripts/test_bedrock.py
Requires: Model access enabled in Bedrock console → Model access
"""

import json
import os

import boto3

SECRET_NAME = os.environ.get(
    "BEDROCK_CONFIG_SECRET",
    "emergency-medical-triage-dev/bedrock-config",
)


def _get_config_from_secrets() -> dict:
    """Fetch Bedrock config from Secrets Manager. No .env or hardcoded values."""
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=SECRET_NAME)
    return json.loads(response["SecretString"])


def test_bedrock() -> bool:
    print("Testing Bedrock access...")
    print(f"Fetching config from Secrets Manager: {SECRET_NAME}\n")

    config = _get_config_from_secrets()
    region = config["region"]
    model_id = config["model_id"]

    print(f"Region: {region}, Model: {model_id}\n")

    client = boto3.client("bedrock-runtime", region_name=region)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Reply with exactly: Bedrock is working."}
        ],
    }

    try:
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        result = json.loads(response["body"].read())
        text = result.get("content", [{}])[0].get("text", "").strip()
        print("✓ Success! Model response:")
        print(text)
        return True
    except Exception as e:
        err = str(e).lower()
        if "validation" in err and "model" in err:
            print(
                "⚠ Model not found. Enable it in AWS Console → Bedrock → Model access"
            )
        elif "accessdenied" in err or "access denied" in err:
            print("⚠ Access denied. Check IAM permissions for bedrock:InvokeModel")
        elif "resourcenotfound" in err or "secret" in err:
            print(
                "⚠ Secret not found. Run: cd infrastructure && terraform apply"
            )
        else:
            print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    ok = test_bedrock()
    exit(0 if ok else 1)
