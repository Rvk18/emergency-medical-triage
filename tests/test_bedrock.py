"""
Bedrock model access test using managed identity and Secrets Manager.

- Config (region, model_id) from Secrets Manager — no credentials stored.
- AWS credentials via default chain (IAM role, aws configure, env).
- Run from project root: pytest tests/test_bedrock.py -v

Requires:
- Terraform applied with bedrock-config secret.
- Model access enabled in AWS Console → Bedrock → Model access.
"""

import json
import os

import boto3
import pytest

BEDROCK_CONFIG_SECRET = os.environ.get(
    "BEDROCK_CONFIG_SECRET",
    "emergency-medical-triage-dev/bedrock-config",
)


def _get_bedrock_config() -> dict:
    """Fetch Bedrock config from Secrets Manager. No credentials."""
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=BEDROCK_CONFIG_SECRET)
    return json.loads(response["SecretString"])


def test_bedrock_invoke():
    """Invoke Bedrock model using config from Secrets Manager and managed identity."""
    config = _get_bedrock_config()
    region = config["region"]
    model_id = config["model_id"]

    client = boto3.client("bedrock-runtime", region_name=region)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Reply with exactly: Bedrock is working."}
        ],
    }

    response = client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )
    result = json.loads(response["body"].read())
    text = result.get("content", [{}])[0].get("text", "").strip()

    assert "Bedrock is working" in text or len(text) > 0
