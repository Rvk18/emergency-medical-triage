# Triage Lambda and API Gateway POST /triage

resource "null_resource" "build_triage_lambda" {
  triggers = {
    src_models = filesha256("${path.module}/../src/triage/models/triage.py")
    src_db     = filesha256("${path.module}/../src/triage/core/db.py")
    src_agent  = filesha256("${path.module}/../src/triage/core/agent.py")
    src_tools  = filesha256("${path.module}/../src/triage/core/tools.py")
    src_gw     = filesha256("${path.module}/../src/triage/core/gateway_client.py")
    script     = filesha256("${path.module}/../scripts/build_triage_lambda.sh")
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

resource "aws_iam_role_policy_attachment" "triage_lambda_vpc" {
  role       = aws_iam_role.triage_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "triage_lambda_rds" {
  name   = "${local.name_prefix}-triage-rds"
  role   = aws_iam_role.triage_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = aws_secretsmanager_secret.rds_config.arn
      },
      {
        Effect   = "Allow"
        Action   = ["rds-db:connect"]
        Resource = "arn:aws:rds-db:${var.aws_region}:${data.aws_caller_identity.current.account_id}:dbuser:${aws_rds_cluster.aurora.cluster_resource_id}/${var.db_username}"
      }
    ]
  })
}

resource "aws_security_group" "triage_lambda" {
  name        = "${local.name_prefix}-triage-lambda-sg"
  description = "Triage Lambda - egress to Aurora"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-triage-lambda-sg"
  }
}

resource "aws_security_group_rule" "aurora_from_triage_lambda" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.aurora.id
  source_security_group_id = aws_security_group.triage_lambda.id
  description              = "Triage Lambda to Aurora"
}

resource "aws_lambda_function" "triage" {
  filename         = data.archive_file.triage_lambda.output_path
  function_name    = "${local.name_prefix}-triage"
  role             = aws_iam_role.triage_lambda.arn
  handler          = "lambda_handler.handler"
  source_code_hash = data.archive_file.triage_lambda.output_base64sha256
  runtime          = "python3.12"
  timeout          = 120

  vpc_config {
    subnet_ids         = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_group_ids = [aws_security_group.triage_lambda.id]
  }

  environment {
    variables = {
      BEDROCK_AGENT_ID            = var.bedrock_agent_id
      BEDROCK_AGENT_ALIAS_ID      = var.bedrock_agent_alias_id
      BEDROCK_MODEL_ID            = var.bedrock_model_id
      RDS_CONFIG_SECRET           = aws_secretsmanager_secret.rds_config.name
      USE_AGENTCORE_TRIAGE        = tostring(var.use_agentcore_triage)
      TRIAGE_AGENT_RUNTIME_ARN    = var.triage_agent_runtime_arn
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
