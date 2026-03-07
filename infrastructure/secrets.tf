# Bedrock config - region, model_id. No credentials stored here.
# AWS credentials use the default chain (IAM role, aws configure).
resource "aws_secretsmanager_secret" "bedrock_config" {
  name        = "${local.name_prefix}/bedrock-config"
  description = "Bedrock configuration (region, model_id)"

  tags = {
    Name    = "${local.name_prefix}-bedrock-config"
    Project = var.project_name
  }
}

resource "aws_secretsmanager_secret_version" "bedrock_config" {
  secret_id = aws_secretsmanager_secret.bedrock_config.id
  secret_string = jsonencode({
    region   = var.aws_region
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
  })
}

# RDS connection config for IAM auth - no password stored. Use boto3 generate_db_auth_token.
# One-time: connect with password and run: GRANT rds_iam TO triagemaster;
resource "aws_secretsmanager_secret" "rds_config" {
  name        = "${local.name_prefix}/rds-config"
  description = "RDS connection config (host, port, database, username) for IAM auth"

  tags = {
    Name    = "${local.name_prefix}-rds-config"
    Project = var.project_name
  }
}

resource "aws_secretsmanager_secret_version" "rds_config" {
  secret_id = aws_secretsmanager_secret.rds_config.id
  secret_string = jsonencode({
    host     = aws_rds_cluster.aurora.endpoint
    port     = 5432
    database = aws_rds_cluster.aurora.database_name
    username = var.db_username
    region   = var.aws_region
  })
}

# Eka Care API (for Eka MCP - Indian drugs, treatment protocols)
# Eka requires Client ID + Client Secret; call POST /connect-auth/v1/account/login to get access_token, then use as Bearer.
# Set eka_api_key (Client ID) and eka_client_secret in terraform.tfvars.
resource "aws_secretsmanager_secret" "eka_config" {
  count       = var.eka_api_key != "" ? 1 : 0
  name        = "${local.name_prefix}/eka-config"
  description = "Eka Care API credentials for MCP (client_id, client_secret for login)"

  tags = {
    Name    = "${local.name_prefix}-eka-config"
    Project = var.project_name
  }
}

resource "aws_secretsmanager_secret_version" "eka_config" {
  count     = var.eka_api_key != "" ? 1 : 0
  secret_id = aws_secretsmanager_secret.eka_config[0].id
  secret_string = jsonencode({
    api_key       = var.eka_api_key
    client_id     = var.eka_api_key
    client_secret = var.eka_client_secret
  })
}

# Google Maps Platform (Directions + Geocoding for routing)
resource "aws_secretsmanager_secret" "google_maps_config" {
  count       = var.google_maps_api_key != "" ? 1 : 0
  name        = "${local.name_prefix}/google-maps-config"
  description = "Google Maps Platform API key (Directions, Geocoding)"

  tags = {
    Name    = "${local.name_prefix}-google-maps-config"
    Project = var.project_name
  }
}

resource "aws_secretsmanager_secret_version" "google_maps_config" {
  count     = var.google_maps_api_key != "" ? 1 : 0
  secret_id = aws_secretsmanager_secret.google_maps_config[0].id
  secret_string = jsonencode({
    api_key = var.google_maps_api_key
  })
}

# API and Gateway config - created by Terraform on apply. Scripts read this (no terraform output needed).
resource "aws_secretsmanager_secret" "api_config" {
  name        = "${local.name_prefix}/api-config"
  description = "API Gateway URL, health URL, Gateway Lambda ARNs, region, and secret names. Created by Terraform."

  tags = {
    Name    = "${local.name_prefix}-api-config"
    Project = var.project_name
  }
}

# AgentCore Gateway OAuth and config. Secret is created by Terraform; value is populated by setup_agentcore_gateway.py (never store in code).
resource "aws_secretsmanager_secret" "gateway_config" {
  name        = "${local.name_prefix}/gateway-config"
  description = "AgentCore Gateway config and OAuth (gateway_url, client_id, client_secret, token_endpoint). Populated by setup_agentcore_gateway.py."

  tags = {
    Name    = "${local.name_prefix}-gateway-config"
    Project = var.project_name
  }
}

# RMP test user credentials for pipeline testing. Scripts (e.g. get_rmp_token.py) read via boto3; no secrets on CLI.
resource "aws_secretsmanager_secret" "rmp_test_credentials" {
  count       = var.rmp_test_password != "" ? 1 : 0
  name        = "${local.name_prefix}/rmp-test-credentials"
  description = "Test RMP user email and password for pipeline/curl testing (Cognito). Used by get_rmp_token.py via boto3."

  tags = {
    Name    = "${local.name_prefix}-rmp-test-credentials"
    Project = var.project_name
  }
}

resource "aws_secretsmanager_secret_version" "rmp_test_credentials" {
  count     = var.rmp_test_password != "" ? 1 : 0
  secret_id = aws_secretsmanager_secret.rmp_test_credentials[0].id
  secret_string = jsonencode({
    email    = var.rmp_test_email
    password = var.rmp_test_password
  })
}

resource "aws_secretsmanager_secret_version" "api_config" {
  secret_id = aws_secretsmanager_secret.api_config.id
  secret_string = jsonencode({
    api_gateway_url                  = "${aws_api_gateway_stage.main.invoke_url}/"
    api_gateway_health_url           = "${aws_api_gateway_stage.main.invoke_url}/health"
    cognito_user_pool_id             = aws_cognito_user_pool.rmp.id
    cognito_app_client_id            = aws_cognito_user_pool_client.rmp_app.id
    gateway_get_hospitals_lambda_arn  = aws_lambda_function.gateway_get_hospitals.arn
    gateway_eka_lambda_arn           = aws_lambda_function.gateway_eka.arn
    gateway_maps_lambda_arn          = aws_lambda_function.gateway_maps.arn
    gateway_routing_lambda_arn       = aws_lambda_function.gateway_routing.arn
    region                           = var.aws_region
    api_config_secret_name           = aws_secretsmanager_secret.api_config.name
    gateway_config_secret_name       = aws_secretsmanager_secret.gateway_config.name
    bedrock_config_secret_name       = aws_secretsmanager_secret.bedrock_config.name
    rds_config_secret_name           = aws_secretsmanager_secret.rds_config.name
    eka_config_secret_name           = var.eka_api_key != "" ? aws_secretsmanager_secret.eka_config[0].name : ""
  })
}
