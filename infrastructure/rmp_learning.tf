# RMP Learning Lambda + API Gateway POST /rmp/learning (Eka quiz + gamification)

resource "null_resource" "build_rmp_learning_lambda" {
  triggers = {
    src_agent = filesha256("${path.module}/../src/rmp_learning/core/agent.py")
    src_api   = filesha256("${path.module}/../src/rmp_learning/api/handler.py")
    script    = filesha256("${path.module}/../scripts/build_rmp_learning_lambda.sh")
  }
  provisioner "local-exec" {
    command     = "bash ${path.module}/../scripts/build_rmp_learning_lambda.sh"
    working_dir = path.module
  }
}

data "archive_file" "rmp_learning_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/rmp_learning_lambda_src"
  output_path = "${path.module}/rmp_learning_lambda.zip"
  depends_on  = [null_resource.build_rmp_learning_lambda]
}

resource "aws_iam_role" "rmp_learning_lambda" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  name = "${local.name_prefix}-rmp-learning-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "rmp_learning_basic" {
  count      = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0
  role       = aws_iam_role.rmp_learning_lambda[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "rmp_learning_agentcore_invoke" {
  count       = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0
  name        = "${local.name_prefix}-rmp-learning-agentcore-invoke"
  description = "Allow RMP Learning Lambda to invoke RMP Quiz AgentCore Runtime"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["bedrock-agentcore:InvokeAgentRuntime"]
        Resource = ["${var.rmp_quiz_agent_runtime_arn}", "${var.rmp_quiz_agent_runtime_arn}/*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rmp_learning_agentcore" {
  count      = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0
  role       = aws_iam_role.rmp_learning_lambda[0].name
  policy_arn = aws_iam_policy.rmp_learning_agentcore_invoke[0].arn
}

resource "aws_lambda_function" "rmp_learning" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  filename         = data.archive_file.rmp_learning_lambda.output_path
  function_name    = "${local.name_prefix}-rmp-learning"
  role             = aws_iam_role.rmp_learning_lambda[0].arn
  handler          = "lambda_handler.handler"
  source_code_hash = data.archive_file.rmp_learning_lambda.output_base64sha256
  runtime          = "python3.12"
  timeout          = 60

  environment {
    variables = {
      RMP_QUIZ_AGENT_RUNTIME_ARN = var.rmp_quiz_agent_runtime_arn
    }
  }
}

resource "aws_lambda_permission" "rmp_learning_api_gateway" {
  count = var.rmp_quiz_agent_runtime_arn != "" ? 1 : 0

  statement_id  = "AllowAPIGatewayInvokeRmpLearning"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rmp_learning[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*/rmp/learning"
}
