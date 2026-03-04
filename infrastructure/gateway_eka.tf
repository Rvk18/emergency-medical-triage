# AgentCore Gateway Eka target Lambda (Indian drugs, treatment protocols).
# Add this Lambda as a second Gateway target via scripts/setup_agentcore_gateway.py --eka.

resource "null_resource" "build_gateway_eka_lambda" {
  triggers = {
    handler = filesha256("${path.module}/gateway_eka_lambda_src/lambda_handler.py")
  }
  provisioner "local-exec" {
    command     = "true"
    working_dir = path.module
  }
}

data "archive_file" "gateway_eka_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/gateway_eka_lambda_src"
  output_path = "${path.module}/gateway_eka_lambda.zip"
  depends_on  = [null_resource.build_gateway_eka_lambda]
}

resource "aws_iam_role" "gateway_eka_lambda" {
  name = "${local.name_prefix}-gateway-eka-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "gateway_eka_basic" {
  role       = aws_iam_role.gateway_eka_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Allow Lambda to read Eka config secret when it exists
resource "aws_iam_role_policy" "gateway_eka_secrets" {
  count = var.eka_api_key != "" ? 1 : 0

  name   = "${local.name_prefix}-gateway-eka-secrets"
  role   = aws_iam_role.gateway_eka_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [aws_secretsmanager_secret.eka_config[0].arn]
    }]
  })
}

resource "aws_lambda_function" "gateway_eka" {
  filename         = data.archive_file.gateway_eka_lambda.output_path
  function_name   = "${local.name_prefix}-gateway-eka"
  role            = aws_iam_role.gateway_eka_lambda.arn
  handler         = "lambda_handler.handler"
  source_code_hash = data.archive_file.gateway_eka_lambda.output_base64sha256
  runtime         = "python3.12"
  timeout         = 30

  environment {
    variables = {
      EKA_API_BASE           = "https://api.eka.care"
      EKA_CONFIG_SECRET_NAME = var.eka_api_key != "" ? aws_secretsmanager_secret.eka_config[0].name : ""
    }
  }
}

output "gateway_eka_lambda_arn" {
  description = "ARN of Eka Gateway Lambda for setup script (add as Gateway target)"
  value       = aws_lambda_function.gateway_eka.arn
}
