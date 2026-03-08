resource "aws_api_gateway_rest_api" "main" {
  name        = "${local.name_prefix}-api"
  description = "Emergency Medical Triage API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${local.name_prefix}-api"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_api_gateway_resource" "triage" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "triage"
}

resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_resource" "hospitals" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "hospitals"
}

resource "aws_api_gateway_resource" "route" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "route"
}

resource "aws_api_gateway_resource" "rmp" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "rmp"
}

resource "aws_api_gateway_resource" "rmp_learning" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.rmp.id
  path_part   = "learning"
}

resource "aws_api_gateway_resource" "rmp_learning_me" {
  count       = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.rmp_learning.id
  path_part   = "me"
}

resource "aws_api_gateway_resource" "rmp_learning_leaderboard" {
  count       = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.rmp_learning.id
  path_part   = "leaderboard"
}

# RMP auth: Cognito User Pool authorizer for /triage, /hospitals, /route
resource "aws_api_gateway_authorizer" "rmp" {
  name            = "rmp-cognito"
  rest_api_id     = aws_api_gateway_rest_api.main.id
  type            = "COGNITO_USER_POOLS"
  provider_arns   = [aws_cognito_user_pool.rmp.arn]
  identity_source = "method.request.header.Authorization"
}

resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {}
}

resource "aws_api_gateway_integration" "health_mock" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.health.id
  http_method             = aws_api_gateway_method.health_get.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.health.invoke_arn
}

# POST /hospitals (RMP auth required)
resource "aws_api_gateway_method" "hospitals_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.hospitals.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.rmp.id
}

resource "aws_api_gateway_integration" "hospitals_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.hospitals.id
  http_method             = aws_api_gateway_method.hospitals_post.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.hospital_matcher.invoke_arn
}

# POST /triage (RMP auth required)
resource "aws_api_gateway_method" "triage_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.triage.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.rmp.id

  request_parameters = {}
}

resource "aws_api_gateway_integration" "triage_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.triage.id
  http_method             = aws_api_gateway_method.triage_post.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.triage.invoke_arn
}

# POST /route (RMP auth required)
resource "aws_api_gateway_method" "route_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.route.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.rmp.id
}

resource "aws_api_gateway_integration" "route_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.route.id
  http_method             = aws_api_gateway_method.route_post.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.route.invoke_arn
}

# POST /rmp/learning (RMP auth) - Eka quiz get_question / score_answer
resource "aws_api_gateway_method" "rmp_learning_post" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.rmp_learning.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.rmp.id
}

resource "aws_api_gateway_integration" "rmp_learning_post" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.rmp_learning.id
  http_method             = aws_api_gateway_method.rmp_learning_post[0].http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.rmp_learning[0].invoke_arn
}

# GET /rmp/learning/me (RMP auth) - current user's total_points and rank
resource "aws_api_gateway_method" "rmp_learning_me_get" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.rmp_learning_me[0].id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.rmp.id
}

resource "aws_api_gateway_integration" "rmp_learning_me_get" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.rmp_learning_me[0].id
  http_method             = aws_api_gateway_method.rmp_learning_me_get[0].http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.rmp_learning[0].invoke_arn
}

# GET /rmp/learning/leaderboard (RMP auth) - top N by total_points, ?limit=20
resource "aws_api_gateway_method" "rmp_learning_leaderboard_get" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.rmp_learning_leaderboard[0].id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.rmp.id
}

resource "aws_api_gateway_integration" "rmp_learning_leaderboard_get" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.rmp_learning_leaderboard[0].id
  http_method             = aws_api_gateway_method.rmp_learning_leaderboard_get[0].http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.rmp_learning[0].invoke_arn
}

# AWS_PROXY passes response through from Lambda; no method/integration response needed

resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.triage.id,
      aws_api_gateway_resource.health.id,
      aws_api_gateway_resource.hospitals.id,
      aws_api_gateway_resource.route.id,
      aws_api_gateway_resource.config.id,
      aws_api_gateway_resource.rmp.id,
      aws_api_gateway_resource.rmp_learning.id,
      aws_api_gateway_method.health_get.id,
      aws_api_gateway_integration.health_mock.id,
      aws_api_gateway_method.triage_post.id,
      aws_api_gateway_integration.triage_post.id,
      aws_api_gateway_method.hospitals_post.id,
      aws_api_gateway_integration.hospitals_post.id,
      aws_api_gateway_method.route_post.id,
      aws_api_gateway_integration.route_post.id,
      aws_api_gateway_method.config_get.id,
      aws_api_gateway_integration.config_get.id,
      aws_api_gateway_authorizer.rmp.id,
      length(aws_lambda_function.rmp_learning) > 0 ? aws_api_gateway_method.rmp_learning_post[0].id : "",
      length(aws_lambda_function.rmp_learning) > 0 ? aws_api_gateway_integration.rmp_learning_post[0].id : "",
      length(aws_lambda_function.rmp_learning) > 0 ? aws_api_gateway_resource.rmp_learning_me[0].id : "",
      length(aws_lambda_function.rmp_learning) > 0 ? aws_api_gateway_method.rmp_learning_me_get[0].id : "",
      length(aws_lambda_function.rmp_learning) > 0 ? aws_api_gateway_integration.rmp_learning_me_get[0].id : "",
      length(aws_lambda_function.rmp_learning) > 0 ? aws_api_gateway_resource.rmp_learning_leaderboard[0].id : "",
      length(aws_lambda_function.rmp_learning) > 0 ? aws_api_gateway_method.rmp_learning_leaderboard_get[0].id : "",
      length(aws_lambda_function.rmp_learning) > 0 ? aws_api_gateway_integration.rmp_learning_leaderboard_get[0].id : "",
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.environment
}
