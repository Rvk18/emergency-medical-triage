# CORS: allow all origins for public-facing web app.
# API Gateway Gateway Responses add CORS headers to gateway-generated responses (401, 403, 4XX, 5XX).
# Lambdas must return CORS headers on 200/400/500 (see Lambda code).
# Security: Protected routes still require Cognito; CORS only allows the browser to send the request.
# See docs/SECURITY-PUBLIC-VS-PRIVATE.md.

locals {
  cors_headers = {
    "gatewayresponse.header.Access-Control-Allow-Origin"   = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers"  = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'"
    "gatewayresponse.header.Access-Control-Allow-Methods"   = "'GET,POST,OPTIONS'"
    "gatewayresponse.header.Access-Control-Expose-Headers"  = "'Content-Type'"
  }
}

resource "aws_api_gateway_gateway_response" "default_4xx" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "DEFAULT_4XX"
  response_parameters = local.cors_headers
  response_templates = {
    "application/json" = "{\"message\":\"$context.error.message\"}"
  }
}

resource "aws_api_gateway_gateway_response" "default_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "DEFAULT_5XX"
  response_parameters = local.cors_headers
  response_templates = {
    "application/json" = "{\"message\":\"$context.error.message\"}"
  }
}

resource "aws_api_gateway_gateway_response" "unauthorized" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "UNAUTHORIZED"
  response_parameters = local.cors_headers
}

resource "aws_api_gateway_gateway_response" "access_denied" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  response_type = "ACCESS_DENIED"
  response_parameters = local.cors_headers
}
