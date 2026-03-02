#!/usr/bin/env bash
# Build Gateway get_hospitals Lambda deployment package (AgentCore Gateway target).
# No external dependencies - handler uses stdlib only. Package is built by Terraform
# via archive_file; this script is a no-op placeholder for consistency.
set -e
echo "Gateway get_hospitals Lambda: using infrastructure/gateway_get_hospitals_lambda_src/ (no build step)"
