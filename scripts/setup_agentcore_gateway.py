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
  python scripts/setup_agentcore_gateway.py --save-to-secrets-only   # Migrate existing gateway_config.json (with client_info) to Secrets Manager only

  With no args, the script reads gateway_get_hospitals_lambda_arn and gateway_eka_lambda_arn
  from the api_config secret ({prefix}/api-config). Full config (incl. OAuth) is saved to
  Secrets Manager ({prefix}/gateway-config); only non-sensitive fields are written to gateway_config.json.
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
EKA_GET_PUBLISHERS_SCHEMA = {
    "name": "get_protocol_publishers",
    "description": "Get list of protocol publishers (e.g. ICMR, RSSDI). Call before search_protocols to get valid publisher names.",
    "inputSchema": {"type": "object", "properties": {}},
}
EKA_SEARCH_PHARMACOLOGY_SCHEMA = {
    "name": "search_pharmacology",
    "description": "Search generic pharmacology (National Formulary of India): dose, indications, contraindications, pregnancy_category, adverse_effects. Use for dosing and safety.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Drug name e.g. Paracetamol or compound e.g. Rifampicin + Isoniazid"},
            "category": {"type": "string", "description": "Filter by category e.g. Antibiotics, Analgesics"},
            "limit": {"type": "integer", "description": "Max results (default 10)"},
            "exact_match": {"type": "boolean", "description": "Only exact matches"},
            "relevance_threshold": {"type": "integer", "description": "Min relevance score (default 100)"},
        },
    },
}

# Google Maps (Directions + Geocoding for routing)
GET_DIRECTIONS_SCHEMA = {
    "name": "get_directions",
    "description": "Get driving distance, duration, and directions URL between origin and destination. Pass coordinates (origin_lat, origin_lon, dest_lat, dest_lon) or addresses (origin_address, dest_address).",
    "inputSchema": {
        "type": "object",
        "properties": {
            "origin_lat": {"type": "number", "description": "Origin latitude"},
            "origin_lon": {"type": "number", "description": "Origin longitude"},
            "dest_lat": {"type": "number", "description": "Destination latitude"},
            "dest_lon": {"type": "number", "description": "Destination longitude"},
            "origin_address": {"type": "string", "description": "Origin address (geocoded if coordinates not provided)"},
            "dest_address": {"type": "string", "description": "Destination address (geocoded if coordinates not provided)"},
        },
        "required": [],
    },
}
GEOCODE_ADDRESS_SCHEMA = {
    "name": "geocode_address",
    "description": "Convert an address string to latitude and longitude.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "address": {"type": "string", "description": "Address to geocode"},
        },
        "required": ["address"],
    },
}

GET_ROUTE_SCHEMA = {
    "name": "get_route",
    "description": "Get driving route from origin to destination. Calls the Routing agent (which uses Google Maps MCP).",
    "inputSchema": {
        "type": "object",
        "properties": {
            "origin_lat": {"type": "number"},
            "origin_lon": {"type": "number"},
            "dest_lat": {"type": "number"},
            "dest_lon": {"type": "number"},
        },
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


def parse_args() -> tuple[str, str | None, str | None, str | None, str | None]:
    """Return (hospitals_lambda_arn, gateway_id or None, eka_arn, maps_arn, routing_arn)."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    gateway_id = None
    eka_arn = os.environ.get("GATEWAY_EKA_LAMBDA_ARN", "").strip() or None
    maps_arn = os.environ.get("GATEWAY_MAPS_LAMBDA_ARN", "").strip() or None
    routing_arn = os.environ.get("GATEWAY_ROUTING_LAMBDA_ARN", "").strip() or None
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
        if sys.argv[i] == "--maps":
            maps_arn = sys.argv[i + 1]
            i += 2
            continue
        if sys.argv[i] == "--routing":
            routing_arn = sys.argv[i + 1]
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
            if not maps_arn:
                maps_arn = (config.get("gateway_maps_lambda_arn") or "").strip() or None
            if not routing_arn:
                routing_arn = (config.get("gateway_routing_lambda_arn") or "").strip() or None
        if not arn:
            print("ERROR: Lambda ARN required. Set GATEWAY_GET_HOSPITALS_LAMBDA_ARN, pass as first arg, or ensure api_config secret exists.")
            sys.exit(1)
    if not eka_arn and config:
        eka_arn = (config.get("gateway_eka_lambda_arn") or "").strip() or None
    if not maps_arn and config:
        maps_arn = (config.get("gateway_maps_lambda_arn") or "").strip() or None
    if not routing_arn and config:
        routing_arn = (config.get("gateway_routing_lambda_arn") or "").strip() or None
    return arn, gateway_id, eka_arn, maps_arn, routing_arn


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


def _migrate_gateway_config_to_secrets() -> None:
    """One-time: read gateway_config.json (if it has client_info), save to Secrets Manager, overwrite file with minimal."""
    path = os.path.join(PROJECT_ROOT, "gateway_config.json")
    if not os.path.isfile(path):
        print("ERROR: gateway_config.json not found. Run setup_agentcore_gateway.py first.", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        config = json.load(f)
    client_info = config.get("client_info")
    if not client_info or not isinstance(client_info, dict):
        print("ERROR: gateway_config.json has no client_info. Run full setup_agentcore_gateway.py.", file=sys.stderr)
        sys.exit(1)
    api_cfg = _load_api_config_from_secret()
    secret_name = (
        os.environ.get("GATEWAY_CONFIG_SECRET_NAME", "").strip()
        or (api_cfg.get("gateway_config_secret_name") if api_cfg else None)
        or f"{os.environ.get('NAME_PREFIX', 'emergency-medical-triage-dev')}/gateway-config"
    )
    try:
        sm = boto3.client("secretsmanager", region_name=REGION)
        sm.put_secret_value(SecretId=secret_name, SecretString=json.dumps(config, indent=2))
        logger.info("Migrated gateway config to Secrets Manager: %s", secret_name)
    except Exception as e:
        print(f"ERROR: Could not save to Secrets Manager: {e}", file=sys.stderr)
        sys.exit(1)
    local_config = {
        "gateway_url": config.get("gateway_url", ""),
        "gateway_id": config.get("gateway_id", ""),
        "region": config.get("region", REGION),
        "target_name": config.get("target_name", "get-hospitals-target"),
        "lambda_arn": config.get("lambda_arn", ""),
        "client_info": "Stored in Secrets Manager; use scripts/load_gateway_config.py or AWS Console",
    }
    if config.get("eka_lambda_arn"):
        local_config["eka_target_name"] = "eka-target"
        local_config["eka_lambda_arn"] = config["eka_lambda_arn"]
    with open(path, "w") as f:
        json.dump(local_config, f, indent=2)
    print("Migrated client_info to Secrets Manager and updated gateway_config.json (no secrets in file).")
    print("Secret:", secret_name)


def setup_gateway() -> dict:
    if "--save-to-secrets-only" in sys.argv:
        _migrate_gateway_config_to_secrets()
        return {}
    lambda_arn, existing_gateway_id, eka_lambda_arn, maps_lambda_arn, routing_lambda_arn = parse_args()
    logger.info("Using Lambda ARN: %s", lambda_arn)
    if eka_lambda_arn:
        logger.info("Eka Lambda ARN: %s", eka_lambda_arn)
    if maps_lambda_arn:
        logger.info("Maps Lambda ARN: %s", maps_lambda_arn)
    if routing_lambda_arn:
        logger.info("Routing Lambda ARN: %s", routing_lambda_arn)

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
            # Sync authorizer to this run's OAuth so tokens from client_info work (Gateway was created with an older OAuth)
            try:
                ci = cognito_response.get("client_info") or {}
                user_pool_id = (ci.get("user_pool_id") or "").strip()
                client_id = (ci.get("client_id") or "").strip()
                scope = (ci.get("scope") or "emergency-triage-hospitals/invoke").strip()
                if user_pool_id and client_id:
                    discovery_url = f"https://cognito-idp.{REGION}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
                    gw_detail = control_client.get_gateway(gatewayIdentifier=gateway["gatewayId"])
                    control_client.update_gateway(
                        gatewayIdentifier=gateway["gatewayId"],
                        name=gw_detail.get("name") or GATEWAY_NAME,
                        roleArn=gw_detail.get("roleArn") or "",
                        protocolType=gw_detail.get("protocolType") or "MCP",
                        authorizerType="CUSTOM_JWT",
                        authorizerConfiguration={
                            "customJWTAuthorizer": {
                                "discoveryUrl": discovery_url,
                                "allowedClients": [client_id],
                                "allowedScopes": [scope],
                            },
                        },
                    )
                    logger.info("Gateway authorizer updated to use current OAuth (client_info)")
                else:
                    logger.warning("client_info missing user_pool_id or client_id; Gateway may reject tokens from secret")
            except Exception as err:
                logger.warning("Could not update Gateway authorizer: %s", err)
            # Keep cognito_response["client_info"] from create_oauth_authorizer so config gets OAuth credentials

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
    try:
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
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ConflictException":
            logger.info("get_hospitals target already exists")
        else:
            raise

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
                                "inlinePayload": [EKA_SEARCH_MEDICATIONS_SCHEMA, EKA_SEARCH_PROTOCOLS_SCHEMA, EKA_GET_PUBLISHERS_SCHEMA, EKA_SEARCH_PHARMACOLOGY_SCHEMA],
                            },
                        }
                    }
                },
                credentialProviderConfigurations=[
                    {"credentialProviderType": "GATEWAY_IAM_ROLE"},
                ],
            )
            logger.info("Eka target added. Tools: %s___search_medications, search_protocols, get_protocol_publishers, search_pharmacology", eka_target_name)
            try:
                gw_response = control_client.get_gateway(gatewayIdentifier=gateway_id)
                role_arn = gw_response.get("roleArn") or gw_response.get("gateway", {}).get("executionRoleArn")
                if role_arn:
                    add_lambda_permission_for_gateway(eka_lambda_arn, role_arn, "Eka")
            except Exception as e:
                logger.warning("Could not add Eka Lambda permission: %s", e)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConflictException":
                logger.info("Eka target already exists")
            else:
                raise

    # 3c. Optionally add Maps target (get_directions, geocode_address)
    if maps_lambda_arn:
        maps_target_name = "maps-target"
        logger.info("Adding Maps Lambda target (%s)...", maps_target_name)
        try:
            control_client.create_gateway_target(
                gatewayIdentifier=gateway_id,
                name=maps_target_name,
                description="Google Maps: directions and geocoding for routing",
                targetConfiguration={
                    "mcp": {
                        "lambda": {
                            "lambdaArn": maps_lambda_arn,
                            "toolSchema": {
                                "inlinePayload": [GET_DIRECTIONS_SCHEMA, GEOCODE_ADDRESS_SCHEMA],
                            },
                        }
                    }
                },
                credentialProviderConfigurations=[
                    {"credentialProviderType": "GATEWAY_IAM_ROLE"},
                ],
            )
            logger.info("Maps target added. Tool names: %s___get_directions, %s___geocode_address", maps_target_name, maps_target_name)
            try:
                gw_response = control_client.get_gateway(gatewayIdentifier=gateway_id)
                role_arn = gw_response.get("roleArn") or gw_response.get("gateway", {}).get("executionRoleArn")
                if role_arn:
                    add_lambda_permission_for_gateway(maps_lambda_arn, role_arn, "Maps")
            except Exception as e:
                logger.warning("Could not add Maps Lambda permission: %s", e)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConflictException":
                logger.info("Maps target already exists; updating schema so Gateway accepts coordinate-only payloads")
                try:
                    paginator = control_client.get_paginator("list_gateway_targets")
                    for page in paginator.paginate(gatewayIdentifier=gateway_id):
                        for t in page.get("items", []):
                            if t.get("name") == maps_target_name:
                                target_id = t.get("targetId")
                                if target_id:
                                    control_client.update_gateway_target(
                                        gatewayIdentifier=gateway_id,
                                        targetId=target_id,
                                        name=maps_target_name,
                                        description="Google Maps: directions and geocoding for routing",
                                        targetConfiguration={
                                            "mcp": {
                                                "lambda": {
                                                    "lambdaArn": maps_lambda_arn,
                                                    "toolSchema": {
                                                        "inlinePayload": [GET_DIRECTIONS_SCHEMA, GEOCODE_ADDRESS_SCHEMA],
                                                    },
                                                }
                                            }
                                        },
                                        credentialProviderConfigurations=[
                                            {"credentialProviderType": "GATEWAY_IAM_ROLE"},
                                        ],
                                    )
                                    logger.info("Maps target schema updated")
                                break
                        else:
                            continue
                        break
                except ClientError as err:
                    logger.warning("Could not update maps target schema: %s", err)
            else:
                raise

    # 3d. Routing agent target (get_route – Hospital Matcher calls this; agent uses Google Maps MCP)
    if routing_lambda_arn:
        routing_target_name = "routing-target"
        logger.info("Adding Routing agent Lambda target (%s)...", routing_target_name)
        try:
            control_client.create_gateway_target(
                gatewayIdentifier=gateway_id,
                name=routing_target_name,
                description="Routing agent: get_route (agent uses Google Maps MCP)",
                targetConfiguration={
                    "mcp": {
                        "lambda": {
                            "lambdaArn": routing_lambda_arn,
                            "toolSchema": {"inlinePayload": [GET_ROUTE_SCHEMA]},
                        }
                    }
                },
                credentialProviderConfigurations=[{"credentialProviderType": "GATEWAY_IAM_ROLE"}],
            )
            logger.info("Routing target added. Tool name: %s___get_route", routing_target_name)
            try:
                gw_response = control_client.get_gateway(gatewayIdentifier=gateway_id)
                role_arn = gw_response.get("roleArn") or gw_response.get("gateway", {}).get("executionRoleArn")
                if role_arn:
                    add_lambda_permission_for_gateway(routing_lambda_arn, role_arn, "Routing")
            except Exception as e:
                logger.warning("Could not add Routing Lambda permission: %s", e)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConflictException":
                logger.info("Routing target already exists")
            else:
                raise

    # 4. Add Lambda permission for Gateway to invoke our function
    # Get Gateway details to find execution role
    try:
        gw_response = control_client.get_gateway(gatewayIdentifier=gateway_id)
        role_arn = gw_response.get("roleArn") or gw_response.get("gateway", {}).get("executionRoleArn")
        if role_arn:
            add_lambda_permission_for_gateway(lambda_arn, role_arn)
        else:
            logger.warning("Gateway execution role not found; ensure Lambda is invokable by Gateway")
    except Exception as e:
        logger.warning("Could not fetch Gateway role for Lambda permission: %s", e)

    # 5. Save config: full config (including client_info) to Secrets Manager; minimal config to local file
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
    if maps_lambda_arn:
        config["maps_target_name"] = "maps-target"
        config["maps_lambda_arn"] = maps_lambda_arn
    if routing_lambda_arn:
        config["routing_target_name"] = "routing-target"
        config["routing_lambda_arn"] = routing_lambda_arn

    # Write full config to Secrets Manager
    api_cfg = _load_api_config_from_secret()
    secret_name = (
        os.environ.get("GATEWAY_CONFIG_SECRET_NAME", "").strip()
        or (api_cfg.get("gateway_config_secret_name") if api_cfg else None)
        or f"{os.environ.get('NAME_PREFIX', 'emergency-medical-triage-dev')}/gateway-config"
    )
    try:
        sm = boto3.client("secretsmanager", region_name=REGION)
        sm.put_secret_value(SecretId=secret_name, SecretString=json.dumps(config, indent=2))
        logger.info("Gateway config (including client_info) saved to Secrets Manager: %s", secret_name)
    except Exception as e:
        logger.warning("Could not save to Secrets Manager %s: %s", secret_name, e)
        logger.info("Run terraform apply to create the secret, then re-run this script.")

    # Local file: non-sensitive only (client_info never in repo)
    local_config = {
        "gateway_url": config["gateway_url"],
        "gateway_id": config["gateway_id"],
        "region": config["region"],
        "target_name": target_name,
        "lambda_arn": config["lambda_arn"],
        "client_info": "Stored in Secrets Manager; use scripts/load_gateway_config.py or AWS Console",
    }
    if eka_lambda_arn:
        local_config["eka_target_name"] = "eka-target"
        local_config["eka_lambda_arn"] = eka_lambda_arn
    if maps_lambda_arn:
        local_config["maps_target_name"] = "maps-target"
        local_config["maps_lambda_arn"] = maps_lambda_arn
    if routing_lambda_arn:
        local_config["routing_target_name"] = "routing-target"
        local_config["routing_lambda_arn"] = routing_lambda_arn

    output_path = os.path.join(PROJECT_ROOT, "gateway_config.json")
    with open(output_path, "w") as f:
        json.dump(local_config, f, indent=2)

    logger.info("Configuration saved to %s (sensitive values in Secrets Manager only)", output_path)
    print("\n" + "=" * 60)
    print("Gateway setup complete!")
    print("Gateway URL:", config["gateway_url"])
    print("Gateway ID:", config["gateway_id"])
    print(f"Tool name (MCP): {target_name}___get_hospitals")
    if eka_lambda_arn:
        print("Eka tools: eka-target___search_medications, search_protocols, get_protocol_publishers, search_pharmacology")
    if maps_lambda_arn:
        print("Maps tools: maps-target___get_directions, maps-target___geocode_address")
    if routing_lambda_arn:
        print("Routing agent: routing-target___get_route (agent uses Google Maps MCP)")
    print("Full config (incl. OAuth) saved to Secrets Manager:", secret_name)
    print("Local gateway_config.json has no secrets; use load_gateway_config.py to export env vars.")
    print("=" * 60)

    return config


if __name__ == "__main__":
    setup_gateway()
