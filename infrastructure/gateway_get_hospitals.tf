# AgentCore Gateway get_hospitals Lambda target
#
# This Lambda implements the get_hospitals tool for AgentCore Gateway.
# The Gateway is created by scripts/setup_agentcore_gateway.py (not Terraform).
# Terraform creates the Lambda; the setup script adds it as a Gateway target.

resource "null_resource" "build_gateway_get_hospitals_lambda" {
  triggers = {
    handler = filesha256("${path.module}/gateway_get_hospitals_lambda_src/lambda_handler.py")
    script  = filesha256("${path.module}/../scripts/build_gateway_get_hospitals_lambda.sh")
  }
  provisioner "local-exec" {
    command     = "bash ${path.module}/../scripts/build_gateway_get_hospitals_lambda.sh"
    working_dir = path.module
  }
}

data "archive_file" "gateway_get_hospitals_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/gateway_get_hospitals_lambda_src"
  output_path = "${path.module}/gateway_get_hospitals_lambda.zip"
  depends_on  = [null_resource.build_gateway_get_hospitals_lambda]
}

resource "aws_iam_role" "gateway_get_hospitals_lambda" {
  name = "${local.name_prefix}-gateway-get-hospitals-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "gateway_get_hospitals_basic" {
  role       = aws_iam_role.gateway_get_hospitals_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "gateway_get_hospitals" {
  filename         = data.archive_file.gateway_get_hospitals_lambda.output_path
  function_name    = "${local.name_prefix}-gateway-get-hospitals"
  role             = aws_iam_role.gateway_get_hospitals_lambda.arn
  handler          = "lambda_handler.handler"
  source_code_hash = data.archive_file.gateway_get_hospitals_lambda.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  # No env vars - synthetic data only
}

output "gateway_get_hospitals_lambda_arn" {
  description = "ARN of get_hospitals Lambda for AgentCore Gateway setup script"
  value       = aws_lambda_function.gateway_get_hospitals.arn
}
