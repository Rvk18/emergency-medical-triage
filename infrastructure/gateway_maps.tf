# AgentCore Gateway Google Maps target (Directions + Geocoding for routing).
# Add as maps target via scripts/setup_agentcore_gateway.py (--maps).

resource "null_resource" "build_gateway_maps_lambda" {
  triggers = {
    handler = filesha256("${path.module}/gateway_maps_lambda_src/lambda_handler.py")
  }
  provisioner "local-exec" {
    command     = "true"
    working_dir = path.module
  }
}

data "archive_file" "gateway_maps_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/gateway_maps_lambda_src"
  output_path = "${path.module}/gateway_maps_lambda.zip"
  depends_on  = [null_resource.build_gateway_maps_lambda]
}

resource "aws_iam_role" "gateway_maps_lambda" {
  name = "${local.name_prefix}-gateway-maps-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "gateway_maps_basic" {
  role       = aws_iam_role.gateway_maps_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "gateway_maps_secrets" {
  count = var.google_maps_api_key != "" ? 1 : 0

  name   = "${local.name_prefix}-gateway-maps-secrets"
  role   = aws_iam_role.gateway_maps_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [aws_secretsmanager_secret.google_maps_config[0].arn]
    }]
  })
}

resource "aws_lambda_function" "gateway_maps" {
  filename          = data.archive_file.gateway_maps_lambda.output_path
  function_name    = "${local.name_prefix}-gateway-maps"
  role             = aws_iam_role.gateway_maps_lambda.arn
  handler          = "lambda_handler.handler"
  source_code_hash = data.archive_file.gateway_maps_lambda.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  environment {
    variables = {
      GOOGLE_MAPS_CONFIG_SECRET_NAME = var.google_maps_api_key != "" ? aws_secretsmanager_secret.google_maps_config[0].name : ""
    }
  }
}

output "gateway_maps_lambda_arn" {
  description = "ARN of Google Maps Gateway Lambda for setup script"
  value       = aws_lambda_function.gateway_maps.arn
}
