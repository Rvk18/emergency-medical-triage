# Infrastructure

Terraform configuration for Emergency Medical Triage AWS resources.

## Resources

| Resource | Description |
|----------|-------------|
| **S3** | Bucket with versioning and encryption |
| **RDS Aurora** | PostgreSQL 15, Serverless v2, private subnets, IAM auth |
| **Bedrock** | IAM for Converse API and AgentCore InvokeAgentRuntime |
| **API Gateway** | REST API: `/triage`, `/hospitals`, `/health` |
| **Lambdas** | Triage, Hospital Matcher, Gateway get_hospitals, Gateway Eka (optional) |
| **AgentCore Gateway** | Created by `scripts/setup_agentcore_gateway.py` (not Terraform); MCP tools: get_hospitals, Eka search_medications/search_protocols |

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.0
- AWS CLI configured with credentials

## Usage

1. Copy the example tfvars and set your DB credentials:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars - set db_username and db_password
   ```

2. Initialize and apply:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

3. **Bedrock**: Enable model access in AWS Console → Bedrock → Model access (left menu) → Manage → Enable Claude or other models.

4. **Aurora**: The cluster is in private subnets. To connect, use a bastion, VPN, or run your app (e.g. Lambda) in the same VPC. IAM database auth is enabled. One-time: connect with password and run `GRANT rds_iam TO <db_username>;` to allow IAM auth.

## Outputs

After apply:

- **API:** `api_gateway_url`, `api_gateway_health_url`
- **Lambdas:** `gateway_get_hospitals_lambda_arn`, `gateway_eka_lambda_arn` (for Gateway setup script)
- **Aurora:** `aurora_cluster_endpoint`, `aurora_cluster_reader_endpoint`
- **S3:** `s3_bucket_name`, `s3_bucket_arn`
- **Secrets:** `eka_config_secret_name` (when `eka_api_key` set; sensitive)
