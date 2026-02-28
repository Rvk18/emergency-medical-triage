output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.main.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.main.arn
}

output "aurora_cluster_endpoint" {
  description = "Aurora cluster endpoint"
  value       = aws_rds_cluster.aurora.endpoint
}

output "aurora_cluster_reader_endpoint" {
  description = "Aurora cluster reader endpoint"
  value       = aws_rds_cluster.aurora.reader_endpoint
}

output "aurora_database_name" {
  description = "Aurora database name"
  value       = aws_rds_cluster.aurora.database_name
}

output "bedrock_policy_arn" {
  description = "IAM policy ARN for Bedrock invocation"
  value       = aws_iam_policy.bedrock_invoke.arn
}

output "api_gateway_url" {
  description = "API Gateway base URL"
  value       = "${aws_api_gateway_stage.main.invoke_url}/"
}

output "api_gateway_health_url" {
  description = "API Gateway health check URL"
  value       = "${aws_api_gateway_stage.main.invoke_url}/health"
}
