#!/usr/bin/env python3
"""
Setup AgentCore Gateway with get_hospitals tool.

Uses bedrock_agentcore_starter_toolkit GatewayClient to create MCP Gateway with
Cognito OAuth, adds our Lambda as target with get_hospitals tool schema,
and saves gateway_config.json.

Prerequisites:
  - pip install bedrock-agentcore-starter-toolkit boto3
  - Terraform apply (creates get_hospitals Lambda)
  - Set GATEWAY_GET_HOSPITALS_LAMBDA_ARN or pass as first arg

Usage:
  python scripts/setup_agentcore_gateway.py
  python scripts/setup_agentcore_gateway.py arn:aws:lambda:us-east-1:ACCOUNT:function:NAME
"""

import json
import logging
import os
import sys
import time

# Add project root for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

try:
    from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
except ImportError:
    print("ERROR: bedrock-agentcore-starter-toolkit not installed.")
    print("Run: pip install bedrock-agentcore-starter-toolkit boto3")
    sys.exit(1)

import boto3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REGION = os.environ.get("AWS_REGION", "us-east-1")
GATEWAY_NAME = "emergency-triage-hospitals"

GET_HOSPITALS_TOOL_SCHEMA = {
    "name": "get_hospitals",
    "description": "Get synthetic hospital recommendations for a given severity (critical, high, medium, low). Returns Indian hospital data with match_score and match_reasons.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "severity": {
                "type": "string",
                "description": "Triage severity: critical, high, medium, or low",
            },
            "limit": {
                "type": "integer",
                "description": "Max number of hospitals to return (default 3, max 10)",
            },
        },
        "required": ["severity"],
    },
}


def get_lambda_arn() -> str:
    arn = os.environ.get("GATEWAY_GET_HOSPITALS_LAMBDA_ARN") or (
        sys.argv[1] if len(sys.argv) > 1 else None
    )
    if not arn:
        print("ERROR: Lambda ARN required.")
        print("Set GATEWAY_GET_HOSPITALS_LAMBDA_ARN or pass as first argument.")
        print("Example: python setup_agentcore_gateway.py arn:aws:lambda:us-east-1:123456789:function:emergency-medical-triage-dev-gateway-get-hospitals")
        sys.exit(1)
    return arn


def add_lambda_permission_for_gateway(lambda_arn: str, gateway_role_arn: str) -> None:
    """Allow Gateway execution role to invoke our Lambda."""
    client = boto3.client("lambda", region_name=REGION)
    fn_name = lambda_arn.split(":")[-1]
    try:
        client.add_permission(
            FunctionName=fn_name,
            StatementId="AllowAgentCoreGatewayInvoke",
            Action="lambda:InvokeFunction",
            Principal=gateway_role_arn,
        )
        logger.info("Added Lambda permission for Gateway role")
    except client.exceptions.ResourceConflictException:
        logger.info("Lambda permission already exists")
    except Exception as e:
        logger.warning("Could not add Lambda permission: %s (you may need to add manually)", e)


def setup_gateway() -> dict:
    lambda_arn = get_lambda_arn()
    logger.info("Using Lambda ARN: %s", lambda_arn)

    client = GatewayClient(region_name=REGION)
    client.logger.setLevel(logging.INFO)

    # 1. Create OAuth authorizer with Cognito
    logger.info("Creating OAuth authorization server...")
    cognito_response = client.create_oauth_authorizer_with_cognito(GATEWAY_NAME)
    logger.info("OAuth authorizer created")

    # 2. Create MCP Gateway
    logger.info("Creating MCP Gateway...")
    gateway = client.create_mcp_gateway(
        name=GATEWAY_NAME,
        role_arn=None,
        authorizer_config=cognito_response["authorizer_config"],
        enable_semantic_search=True,
    )
    logger.info("Gateway created: %s", gateway.get("gatewayUrl"))

    # Fix IAM permissions (if toolkit created a role)
    try:
        client.fix_iam_permissions(gateway)
        logger.info("Waiting 30s for IAM propagation...")
        time.sleep(30)
    except Exception as e:
        logger.warning("fix_iam_permissions: %s", e)

    # 3. Add Lambda target with get_hospitals tool (use boto3 for full control)
    control_client = boto3.client("bedrock-agentcore-control", region_name=REGION)
    gateway_id = gateway["gatewayId"]
    target_name = "get_hospitals_target"

    logger.info("Adding Lambda target with get_hospitals tool...")
    control_client.create_gateway_target(
        gatewayIdentifier=gateway_id,
        name=target_name,
        description="get_hospitals tool for hospital recommendations",
        targetConfiguration={
            "mcp": {
                "lambda": {
                    "lambdaArn": lambda_arn,
                    "toolSchema": {
                        "inlinePayload": [GET_HOSPITALS_TOOL_SCHEMA],
                    },
                }
            }
        },
        credentialProviderConfigurations=[
            {"credentialProviderType": "GATEWAY_IAM_ROLE"},
        ],
    )
    logger.info("Lambda target added")

    # 4. Add Lambda permission for Gateway to invoke our function
    # Get Gateway details to find execution role
    try:
        gw_response = control_client.get_gateway(gatewayIdentifier=gateway_id)
        role_arn = gw_response.get("gateway", {}).get("executionRoleArn")
        if role_arn:
            add_lambda_permission_for_gateway(lambda_arn, role_arn)
        else:
            logger.warning("Gateway execution role not found; ensure Lambda is invokable by Gateway")
    except Exception as e:
        logger.warning("Could not fetch Gateway role for Lambda permission: %s", e)

    # 5. Save config
    config = {
        "gateway_url": gateway["gatewayUrl"],
        "gateway_id": gateway_id,
        "region": REGION,
        "client_info": cognito_response["client_info"],
        "target_name": target_name,
        "lambda_arn": lambda_arn,
    }

    output_path = os.path.join(PROJECT_ROOT, "gateway_config.json")
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    logger.info("Configuration saved to %s", output_path)
    print("\n" + "=" * 60)
    print("Gateway setup complete!")
    print("Gateway URL:", config["gateway_url"])
    print("Gateway ID:", config["gateway_id"])
    print(f"Tool name (MCP): {target_name}___get_hospitals")
    print("Config saved to: gateway_config.json")
    print("=" * 60)

    return config


if __name__ == "__main__":
    setup_gateway()
