# Hospital Matcher Lambda + API Gateway POST /hospitals

resource "null_resource" "build_hospital_matcher_lambda" {
  triggers = {
    src_agent        = filesha256("${path.module}/../src/hospital_matcher/core/agent.py")
    src_tools        = filesha256("${path.module}/../src/hospital_matcher/core/tools.py")
    src_instructions = filesha256("${path.module}/../src/hospital_matcher/core/instructions.py")
    src_models       = filesha256("${path.module}/../src/hospital_matcher/models/hospital.py")
    script           = filesha256("${path.module}/../scripts/build_hospital_matcher_lambda.sh")
  }
  provisioner "local-exec" {
    command     = "bash ${path.module}/../scripts/build_hospital_matcher_lambda.sh"
    working_dir = path.module
  }
}

data "archive_file" "hospital_matcher_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/hospital_matcher_lambda_src"
  output_path = "${path.module}/hospital_matcher_lambda.zip"
  depends_on  = [null_resource.build_hospital_matcher_lambda]
}

resource "aws_iam_role" "hospital_matcher_lambda" {
  name = "${local.name_prefix}-hospital-matcher-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "hospital_matcher_basic" {
  role       = aws_iam_role.hospital_matcher_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "hospital_matcher_bedrock" {
  role       = aws_iam_role.hospital_matcher_lambda.name
  policy_arn = aws_iam_policy.bedrock_invoke.arn
}

resource "aws_lambda_function" "hospital_matcher" {
  filename         = data.archive_file.hospital_matcher_lambda.output_path
  function_name    = "${local.name_prefix}-hospital-matcher"
  role             = aws_iam_role.hospital_matcher_lambda.arn
  handler          = "lambda_handler.handler"
  source_code_hash = data.archive_file.hospital_matcher_lambda.output_base64sha256
  runtime          = "python3.12"
  timeout          = 60

  environment {
    variables = {
      BEDROCK_HOSPITAL_MATCHER_AGENT_ID       = var.bedrock_hospital_matcher_agent_id
      BEDROCK_HOSPITAL_MATCHER_AGENT_ALIAS_ID = var.bedrock_hospital_matcher_agent_alias_id
      BEDROCK_MODEL_ID                        = var.bedrock_model_id
    }
  }
}

resource "aws_lambda_permission" "hospital_matcher_api_gateway" {
  statement_id  = "AllowAPIGatewayInvokeHospitalMatcher"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hospital_matcher.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*/hospitals"
}
