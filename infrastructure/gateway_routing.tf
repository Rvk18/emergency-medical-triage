# Gateway target Lambda for the Routing agent.
# When Gateway calls routing-target___get_route, this Lambda invokes the Routing agent on the Runtime.
# The Routing agent uses the Google Maps MCP. Hospital Matcher calls this via Gateway.

resource "null_resource" "build_gateway_routing_lambda" {
  triggers = {
    handler = filesha256("${path.module}/gateway_routing_lambda_src/lambda_handler.py")
  }
  provisioner "local-exec" {
    command     = "true"
    working_dir = path.module
  }
}

data "archive_file" "gateway_routing_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/gateway_routing_lambda_src"
  output_path = "${path.module}/gateway_routing_lambda.zip"
  depends_on  = [null_resource.build_gateway_routing_lambda]
}

resource "aws_iam_role" "gateway_routing_lambda" {
  name = "${local.name_prefix}-gateway-routing-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "gateway_routing_basic" {
  role       = aws_iam_role.gateway_routing_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "gateway_routing_agentcore" {
  count = var.routing_agent_runtime_arn != "" ? 1 : 0

  name   = "${local.name_prefix}-gateway-routing-agentcore"
  role   = aws_iam_role.gateway_routing_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["bedrock-agentcore:InvokeAgentRuntime"]
      Resource = ["${var.routing_agent_runtime_arn}", "${var.routing_agent_runtime_arn}/*"]
    }]
  })
}

resource "aws_lambda_function" "gateway_routing" {
  filename          = data.archive_file.gateway_routing_lambda.output_path
  function_name     = "${local.name_prefix}-gateway-routing"
  role              = aws_iam_role.gateway_routing_lambda.arn
  handler           = "lambda_handler.handler"
  source_code_hash  = data.archive_file.gateway_routing_lambda.output_base64sha256
  runtime           = "python3.12"
  timeout           = 30

  environment {
    variables = {
      ROUTING_AGENT_RUNTIME_ARN = var.routing_agent_runtime_arn
    }
  }
}

output "gateway_routing_lambda_arn" {
  description = "ARN of Routing agent Gateway Lambda for setup script (routing-target)"
  value       = aws_lambda_function.gateway_routing.arn
}
