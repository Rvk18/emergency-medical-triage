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
