#!/usr/bin/env python3
"""
Check which Bedrock models are available for Converse API.
Runs a minimal Converse call per model and reports which succeed.
"""

import os
import sys

# Add src for triage imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")

# Inference profiles and foundation model IDs to try (best first)
MODELS_TO_TRY = [
    # Claude Sonnet 4.6 (newest)
    "us.anthropic.claude-sonnet-4-6",
    "global.anthropic.claude-sonnet-4-6",
    "anthropic.claude-sonnet-4-6",
    # Claude Sonnet 4.5
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    # Claude 3.5 Sonnet v2 (widely available)
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "us.anthropic.claude-3-5-sonnet-v2:0",
    # Claude 3.5 Haiku
    "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    # Claude 3 Haiku
    "us.anthropic.claude-3-haiku-20240307-v1:0",
]


def try_model(client: boto3.client, model_id: str) -> tuple[bool, str]:
    """Try a minimal Converse call. Returns (success, message)."""
    try:
        response = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Reply with OK"}]}],
            inferenceConfig={"maxTokens": 10},
        )
        text = response.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")
        return True, text[:50] if text else "empty"
    except Exception as e:
        return False, str(e)


def main():
    client = boto3.client("bedrock-runtime", region_name=REGION)
    print(f"Checking Bedrock models in {REGION}...\n")
    working = []
    for model_id in MODELS_TO_TRY:
        ok, msg = try_model(client, model_id)
        status = "✓" if ok else "✗"
        print(f"  {status} {model_id}")
        if ok:
            working.append(model_id)
            print(f"      -> {msg}")
        else:
            print(f"      -> {msg[:80]}...")
        print()
    if working:
        print("=" * 60)
        print("Working models (use best first):")
        for m in working:
            print(f"  {m}")
        print("\nRecommended for bedrock_model_id:")
        print(f"  bedrock_model_id = \"{working[0]}\"")
    else:
        print("No models worked. Check IAM permissions and model access.")
        sys.exit(1)


if __name__ == "__main__":
    main()
