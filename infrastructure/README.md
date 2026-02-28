# Infrastructure

Terraform configuration for Emergency Medical Triage AWS resources.

## Resources

| Resource | Description |
|----------|-------------|
| **S3** | Bucket with versioning and encryption for backups, audit logs, media |
| **RDS Aurora** | PostgreSQL 15.10, Serverless v2, in private subnets |
| **Bedrock** | IAM policy for invoking foundation models (enable model access in Console) |
| **API Gateway** | REST API with `/triage` and `/health` endpoints |

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

After apply, you'll get:

- `s3_bucket_name` / `s3_bucket_arn`
- `aurora_cluster_endpoint` / `aurora_cluster_reader_endpoint`
- `bedrock_policy_arn` (attach to Lambda/app role)
- `api_gateway_url` / `api_gateway_health_url`
