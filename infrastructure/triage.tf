# Triage Lambda and API Gateway POST /triage

resource "null_resource" "build_triage_lambda" {
  triggers = {
    src = filesha256("${path.module}/../src/triage/models/triage.py")
    script = filesha256("${path.module}/../scripts/build_triage_lambda.sh")
  }
  provisioner "local-exec" {
    command     = "bash ${path.module}/../scripts/build_triage_lambda.sh"
    working_dir = path.module
  }
}

data "archive_file" "triage_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/triage_lambda_src"
  output_path = "${path.module}/triage_lambda.zip"
  depends_on  = [null_resource.build_triage_lambda]
}

resource "aws_iam_role" "triage_lambda" {
  name = "${local.name_prefix}-triage-lambda-role"

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

resource "aws_iam_role_policy_attachment" "triage_lambda_basic" {
  role       = aws_iam_role.triage_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "triage_lambda_bedrock" {
  role       = aws_iam_role.triage_lambda.name
  policy_arn = aws_iam_policy.bedrock_invoke.arn
}

resource "aws_lambda_function" "triage" {
  filename         = data.archive_file.triage_lambda.output_path
  function_name    = "${local.name_prefix}-triage"
  role             = aws_iam_role.triage_lambda.arn
  handler          = "lambda_handler.handler"
  source_code_hash = data.archive_file.triage_lambda.output_base64sha256
  runtime          = "python3.12"
  timeout          = 120

  environment {
    variables = {
      BEDROCK_AGENT_ID    = var.bedrock_agent_id
      BEDROCK_AGENT_ALIAS_ID = var.bedrock_agent_alias_id
      BEDROCK_MODEL_ID    = var.bedrock_model_id
    }
  }
}

resource "aws_lambda_permission" "triage_api_gateway" {
  statement_id  = "AllowAPIGatewayInvokeTriage"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.triage.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*/triage"
}
