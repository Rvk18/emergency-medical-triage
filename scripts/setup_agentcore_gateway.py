#!/usr/bin/env python3
"""
Setup AgentCore Gateway with get_hospitals tool.

Uses bedrock_agentcore_starter_toolkit GatewayClient to create MCP Gateway with
Cognito OAuth, adds our Lambda as target with get_hospitals tool schema,
and saves gateway_config.json.

Prerequisites:
  - pip install bedrock-agentcore-starter-toolkit boto3
  - Terraform apply (creates Lambdas and api_config secret)
  - Lambda ARN: from env GATEWAY_GET_HOSPITALS_LAMBDA_ARN, first arg, or api_config secret

Usage:
  python scripts/setup_agentcore_gateway.py
  python scripts/setup_agentcore_gateway.py <lambda_arn> [--gateway-id <id>] [--eka <eka_arn>]

  With no args, the script reads gateway_get_hospitals_lambda_arn and gateway_eka_lambda_arn
  from the api_config secret ({prefix}/api-config). Override with env or arguments.
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
from botocore.exceptions import ClientError

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
            "severity": {"type": "string", "description": "Triage severity: critical, high, medium, or low"},
            "limit": {"type": "integer", "description": "Max number of hospitals to return (default 3, max 10)"},
        },
        "required": ["severity"],
    },
}

# Eka Care tools (Indian drugs, treatment protocols)
EKA_SEARCH_MEDICATIONS_SCHEMA = {
    "name": "search_medications",
    "description": "Search Indian branded drugs by drug name, form, generic names, or volume. Returns medications with name, generic_name, manufacturer_name, product_type.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "drug_name": {"type": "string", "description": "Branded name e.g. Glim 1mg"},
            "form": {"type": "string", "description": "Form e.g. Tablet, Syrup"},
            "generic_names": {"type": "string", "description": "Generic name(s), comma-separated e.g. Glimeperide, Metformin"},
            "volumes": {"type": "string", "description": "Volume e.g. 650, 1000"},
        },
    },
}
EKA_SEARCH_PROTOCOLS_SCHEMA = {
    "name": "search_protocols",
    "description": "Search Indian treatment protocols (ICMR, RSSDI). Provide list of queries with query, tag, publisher.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "queries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Concise search phrase"},
                        "tag": {"type": "string", "description": "Condition/tag to filter"},
                        "publisher": {"type": "string", "description": "Publisher name"},
                    },
                    "required": ["query", "tag", "publisher"],
                },
            },
        },
        "required": ["queries"],
    },
}


def _load_api_config_from_secret() -> dict | None:
    """Load api_config from Secrets Manager (no Terraform output). Returns dict or None."""
    secret_name = os.environ.get("API_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        # Default: same prefix as Terraform local.name_prefix
        prefix = os.environ.get("NAME_PREFIX", "emergency-medical-triage-dev")
        secret_name = f"{prefix}/api-config"
    try:
        client = boto3.client("secretsmanager", region_name=REGION)
        resp = client.get_secret_value(SecretId=secret_name)
        return json.loads(resp["SecretString"])
    except Exception as e:
        logger.debug("Could not load api_config secret %s: %s", secret_name, e)
        return None


def parse_args() -> tuple[str, str | None, str | None]:
    """Return (hospitals_lambda_arn, existing_gateway_id or None, eka_lambda_arn or None)."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    gateway_id = None
    eka_arn = os.environ.get("GATEWAY_EKA_LAMBDA_ARN", "").strip() or None
    i = 0
    while i < len(sys.argv) - 1:
        if sys.argv[i] == "--gateway-id":
            gateway_id = sys.argv[i + 1]
            i += 2
            continue
        if sys.argv[i] == "--eka":
            eka_arn = sys.argv[i + 1]
            i += 2
            continue
        i += 1
    arn = os.environ.get("GATEWAY_GET_HOSPITALS_LAMBDA_ARN", "").strip() or (args[0] if args else None)
    config = _load_api_config_from_secret()
    if not arn or arn.startswith("--"):
        if config:
            arn = (config.get("gateway_get_hospitals_lambda_arn") or "").strip()
            if not eka_arn:
                eka_arn = (config.get("gateway_eka_lambda_arn") or "").strip() or None
        if not arn:
            print("ERROR: Lambda ARN required. Set GATEWAY_GET_HOSPITALS_LAMBDA_ARN, pass as first arg, or ensure api_config secret exists.")
            sys.exit(1)
    if not eka_arn and config:
        eka_arn = (config.get("gateway_eka_lambda_arn") or "").strip() or None
    return arn, gateway_id, eka_arn


def add_lambda_permission_for_gateway(lambda_arn: str, gateway_role_arn: str, statement_suffix: str = "") -> None:
    """Allow Gateway execution role to invoke our Lambda."""
    client = boto3.client("lambda", region_name=REGION)
    fn_name = lambda_arn.split(":")[-1]
    statement_id = "AllowAgentCoreGatewayInvoke" + (statement_suffix or "")
    try:
        client.add_permission(
            FunctionName=fn_name,
            StatementId=statement_id,
            Action="lambda:InvokeFunction",
            Principal=gateway_role_arn,
        )
        logger.info("Added Lambda permission for Gateway role")
    except client.exceptions.ResourceConflictException:
        logger.info("Lambda permission already exists")
    except Exception as e:
        logger.warning("Could not add Lambda permission: %s (you may need to add manually)", e)


def gateway_url_from_id(gateway_id: str) -> str:
    """Construct Gateway MCP URL from gateway ID."""
    return f"https://{gateway_id}.gateway.bedrock-agentcore.{REGION}.amazonaws.com/mcp"


def find_existing_gateway(control_client, name: str) -> dict | None:
    """Find gateway by name. Return gateway dict with gatewayId, gatewayUrl."""
    paginator = control_client.get_paginator("list_gateways")
    for page in paginator.paginate():
        for gw in page.get("items", []):
            if gw.get("name") == name:
                gid = gw.get("gatewayId")
                if gid:
                    url = gw.get("gatewayUrl") or gateway_url_from_id(gid)
                    return {"gatewayId": gid, "gatewayUrl": url}
    return None


def setup_gateway() -> dict:
    lambda_arn, existing_gateway_id, eka_lambda_arn = parse_args()
    logger.info("Using Lambda ARN: %s", lambda_arn)
    if eka_lambda_arn:
        logger.info("Eka Lambda ARN: %s", eka_lambda_arn)

    control_client = boto3.client("bedrock-agentcore-control", region_name=REGION)
    client = GatewayClient(region_name=REGION)
    client.logger.setLevel(logging.INFO)

    gateway = None
    cognito_response = {"client_info": None}

    if existing_gateway_id:
        logger.info("Using existing Gateway ID: %s", existing_gateway_id)
        detail = control_client.get_gateway(gatewayIdentifier=existing_gateway_id)
        g = detail.get("gateway", {})
        url = g.get("gatewayUrl") or gateway_url_from_id(existing_gateway_id)
        gateway = {"gatewayId": existing_gateway_id, "gatewayUrl": url}
    else:
        # 1. Create OAuth authorizer with Cognito
        logger.info("Creating OAuth authorization server...")
        cognito_response = client.create_oauth_authorizer_with_cognito(GATEWAY_NAME)
        logger.info("OAuth authorizer created")

        # 2. Create MCP Gateway
        logger.info("Creating MCP Gateway...")
        try:
            gateway = client.create_mcp_gateway(
                name=GATEWAY_NAME,
                role_arn=None,
                authorizer_config=cognito_response["authorizer_config"],
                enable_semantic_search=True,
            )
            logger.info("Gateway created: %s", gateway.get("gatewayUrl"))
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") != "ConflictException":
                raise
            logger.info("Gateway '%s' already exists, reusing...", GATEWAY_NAME)
            gateway = find_existing_gateway(control_client, GATEWAY_NAME)
            if not gateway:
                raise RuntimeError(f"Gateway '{GATEWAY_NAME}' exists but could not be found. Use --gateway-id <id>.")
            cognito_response["client_info"] = None  # Use existing auth; client_info from prior run

        # Fix IAM permissions (if toolkit created a role)
        try:
            client.fix_iam_permissions(gateway)
            logger.info("Waiting 30s for IAM propagation...")
            time.sleep(30)
        except Exception as e:
            logger.warning("fix_iam_permissions: %s", e)

    # 3. Add Lambda target with get_hospitals tool
    gateway_id = gateway["gatewayId"]
    target_name = "get-hospitals-target"

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

    # 3b. Optionally add Eka target (search_medications, search_protocols)
    if eka_lambda_arn:
        eka_target_name = "eka-target"
        logger.info("Adding Eka Lambda target (%s)...", eka_target_name)
        try:
            control_client.create_gateway_target(
                gatewayIdentifier=gateway_id,
                name=eka_target_name,
                description="Eka Care tools: Indian drugs and treatment protocols",
                targetConfiguration={
                    "mcp": {
                        "lambda": {
                            "lambdaArn": eka_lambda_arn,
                            "toolSchema": {
                                "inlinePayload": [EKA_SEARCH_MEDICATIONS_SCHEMA, EKA_SEARCH_PROTOCOLS_SCHEMA],
                            },
                        }
                    }
                },
                credentialProviderConfigurations=[
                    {"credentialProviderType": "GATEWAY_IAM_ROLE"},
                ],
            )
            logger.info("Eka target added. Tool names: %s___search_medications, %s___search_protocols", eka_target_name, eka_target_name)
            try:
                gw_response = control_client.get_gateway(gatewayIdentifier=gateway_id)
                role_arn = gw_response.get("gateway", {}).get("executionRoleArn")
        if role_arn:
            add_lambda_permission_for_gateway(eka_lambda_arn, role_arn, "Eka")
            except Exception as e:
                logger.warning("Could not add Eka Lambda permission: %s", e)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConflictException":
                logger.info("Eka target already exists")
            else:
                raise

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
    gateway_url = gateway.get("gatewayUrl") or gateway_url_from_id(gateway["gatewayId"])
    config = {
        "gateway_url": gateway_url,
        "gateway_id": gateway_id,
        "region": REGION,
        "client_info": cognito_response["client_info"],
        "target_name": target_name,
        "lambda_arn": lambda_arn,
    }
    if eka_lambda_arn:
        config["eka_target_name"] = "eka-target"
        config["eka_lambda_arn"] = eka_lambda_arn

    output_path = os.path.join(PROJECT_ROOT, "gateway_config.json")
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    logger.info("Configuration saved to %s", output_path)
    print("\n" + "=" * 60)
    print("Gateway setup complete!")
    print("Gateway URL:", config["gateway_url"])
    print("Gateway ID:", config["gateway_id"])
    print(f"Tool name (MCP): {target_name}___get_hospitals")
    if eka_lambda_arn:
        print("Eka tools: eka-target___search_medications, eka-target___search_protocols")
    print("Config saved to: gateway_config.json")
    print("=" * 60)

    return config


if __name__ == "__main__":
    setup_gateway()
