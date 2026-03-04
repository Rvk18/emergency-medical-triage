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
# Set eka_api_key in terraform.tfvars or via -var="eka_api_key=..."
resource "aws_secretsmanager_secret" "eka_config" {
  count       = var.eka_api_key != "" ? 1 : 0
  name        = "${local.name_prefix}/eka-config"
  description = "Eka Care API credentials for MCP (drugs, treatment protocols)"

  tags = {
    Name    = "${local.name_prefix}-eka-config"
    Project = var.project_name
  }
}

resource "aws_secretsmanager_secret_version" "eka_config" {
  count     = var.eka_api_key != "" ? 1 : 0
  secret_id = aws_secretsmanager_secret.eka_config[0].id
  secret_string = jsonencode({
    api_key  = var.eka_api_key
    client_id = var.eka_api_key
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

resource "aws_secretsmanager_secret_version" "api_config" {
  secret_id = aws_secretsmanager_secret.api_config.id
  secret_string = jsonencode({
    api_gateway_url                  = "${aws_api_gateway_stage.main.invoke_url}/"
    api_gateway_health_url           = "${aws_api_gateway_stage.main.invoke_url}/health"
    gateway_get_hospitals_lambda_arn = aws_lambda_function.gateway_get_hospitals.arn
    gateway_eka_lambda_arn           = aws_lambda_function.gateway_eka.arn
    region                           = var.aws_region
    api_config_secret_name           = aws_secretsmanager_secret.api_config.name
    bedrock_config_secret_name       = aws_secretsmanager_secret.bedrock_config.name
    rds_config_secret_name           = aws_secretsmanager_secret.rds_config.name
    eka_config_secret_name           = one(aws_secretsmanager_secret.eka_config[*].name)
  })
}
