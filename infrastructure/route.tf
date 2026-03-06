# Route Lambda: POST /route – directions via Gateway maps tool. RMP auth required.

resource "null_resource" "build_route_lambda" {
  triggers = {
    handler = filesha256("${path.module}/route_lambda_src/lambda_handler.py")
  }
  provisioner "local-exec" {
    command     = "true"
    working_dir = path.module
  }
}

data "archive_file" "route_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/route_lambda_src"
  output_path = "${path.module}/route_lambda.zip"
  depends_on  = [null_resource.build_route_lambda]
}

resource "aws_iam_role" "route_lambda" {
  name = "${local.name_prefix}-route-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "route_lambda_basic" {
  role       = aws_iam_role.route_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "route_lambda_gateway_config" {
  name   = "${local.name_prefix}-route-gateway-config"
  role   = aws_iam_role.route_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [aws_secretsmanager_secret.gateway_config.arn]
    }]
  })
}

resource "aws_lambda_function" "route" {
  filename          = data.archive_file.route_lambda.output_path
  function_name     = "${local.name_prefix}-route"
  role              = aws_iam_role.route_lambda.arn
  handler           = "lambda_handler.handler"
  source_code_hash  = data.archive_file.route_lambda.output_base64sha256
  runtime           = "python3.12"
  timeout           = 30

  environment {
    variables = {
      GATEWAY_CONFIG_SECRET_NAME = aws_secretsmanager_secret.gateway_config.name
    }
  }
}

resource "aws_lambda_permission" "route_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.route.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*/route"
}
