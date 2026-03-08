# Config API Lambda - Returns frontend configuration (Google Maps API key, etc.)

data "archive_file" "config_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/config_lambda_src"
  output_path = "${path.module}/.terraform/archives/config_lambda.zip"
}

resource "aws_iam_role" "config_lambda" {
  name = "${local.name_prefix}-config-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "config_lambda_basic" {
  role       = aws_iam_role.config_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "config" {
  function_name    = "${local.name_prefix}-config"
  role             = aws_iam_role.config_lambda.arn
  handler          = "lambda_handler.handler"
  runtime          = "python3.12"
  timeout          = 10
  memory_size      = 128
  filename         = data.archive_file.config_lambda_zip.output_path
  source_code_hash = data.archive_file.config_lambda_zip.output_base64sha256

  environment {
    variables = {
      GOOGLE_MAPS_CONFIG_SECRET_NAME = var.google_maps_api_key != "" ? aws_secretsmanager_secret.google_maps_config[0].name : ""
      ENVIRONMENT                    = var.environment
    }
  }

  tags = {
    Name        = "${local.name_prefix}-config"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "config" {
  name              = "/aws/lambda/${aws_lambda_function.config.function_name}"
  retention_in_days = 7
}

# API Gateway resource for /config
resource "aws_api_gateway_resource" "config" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "config"
}

# GET /config (no auth required - public endpoint)
resource "aws_api_gateway_method" "config_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.config.id
  http_method   = "GET"
  authorization = "NONE"
}

# OPTIONS /config for CORS preflight (browser sends this before GET from CloudFront)
resource "aws_api_gateway_method" "config_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.config.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "config_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.config.id
  http_method = aws_api_gateway_method.config_options.http_method

  type                    = "MOCK"
  request_templates      = { "application/json" = "{\"statusCode\": 200}" }
  passthrough_behavior    = "WHEN_NO_MATCH"
}

resource "aws_api_gateway_method_response" "config_options_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.config.id
  http_method = aws_api_gateway_method.config_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"   = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods"  = true
  }
  response_models = { "application/json" = "Empty" }
}

resource "aws_api_gateway_integration_response" "config_options_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.config.id
  http_method = aws_api_gateway_method.config_options.http_method
  status_code = aws_api_gateway_method_response.config_options_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"   = "'*'"
    "method.response.header.Access-Control-Allow-Headers"  = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'"
    "method.response.header.Access-Control-Allow-Methods"  = "'GET,OPTIONS'"
  }
}

resource "aws_api_gateway_integration" "config_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.config.id
  http_method             = aws_api_gateway_method.config_get.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.config.invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "config_api_gateway" {
  statement_id  = "AllowAPIGatewayInvokeConfig"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.config.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*/config"
}

# Grant Lambda permission to read Google Maps secret
resource "aws_iam_role_policy" "config_secrets" {
  count = var.google_maps_api_key != "" ? 1 : 0
  name  = "config-secrets-access"
  role  = aws_iam_role.config_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.google_maps_config[0].arn
      }
    ]
  })
}
