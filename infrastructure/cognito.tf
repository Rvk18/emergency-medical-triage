# RMP (Registered Medical Practitioner) authentication – Cognito User Pool
# Protects POST /triage, POST /hospitals, POST /route. Frontend sends IdToken in Authorization header.

resource "aws_cognito_user_pool" "rmp" {
  name = "${local.name_prefix}-rmp-users"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 10
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }

  schema {
    name                = "name"
    attribute_data_type = "String"
    required            = false
    mutable             = true
  }

  tags = {
    Name    = "${local.name_prefix}-rmp-user-pool"
    Project = var.project_name
  }

  # Cognito does not allow modifying schema after creation; ignore drift/normalization.
  lifecycle {
    ignore_changes = [schema]
  }
}

# App client for frontend (SPA / mobile). No client secret – public client.
resource "aws_cognito_user_pool_client" "rmp_app" {
  name         = "${local.name_prefix}-rmp-app"
  user_pool_id = aws_cognito_user_pool.rmp.id

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]

  access_token_validity  = 60   # minutes
  id_token_validity      = 60   # minutes
  refresh_token_validity  = 30  # days
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  read_attributes  = ["email", "name"]
  write_attributes = ["email", "name"]

  prevent_user_existence_errors = "ENABLED"
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID for RMP auth (frontend: use this + client_id)"
  value       = aws_cognito_user_pool.rmp.id
}

output "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN (for API Gateway authorizer)"
  value       = aws_cognito_user_pool.rmp.arn
}

output "cognito_app_client_id" {
  description = "Cognito App Client ID for frontend"
  value       = aws_cognito_user_pool_client.rmp_app.id
}
