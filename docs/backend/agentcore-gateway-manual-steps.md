# AgentCore Gateway: Manual Setup Steps

**Release and testing:** See [RELEASE-Gateway-Eka-Integration.md](./RELEASE-Gateway-Eka-Integration.md) and [TESTING-Gateway-Eka.md](./TESTING-Gateway-Eka.md).

The Gateway itself is not managed by Terraform. Terraform creates the **get_hospitals** and **gateway_eka** Lambdas and writes their ARNs (and the API URL) to the **api_config** secret so you don't need to rely on Terraform outputs.

## Prerequisites

- Terraform apply completed (creates `gateway-get-hospitals` Lambda)
- Python 3.10+ with `bedrock-agentcore-starter-toolkit` and `boto3`
- AWS credentials configured (`aws configure` or env vars)
- Region: us-east-1 (or match `terraform.tfvars`)

## Step 1: Deploy Lambda via Terraform

```bash
cd infrastructure
terraform apply
```

Terraform creates the Lambdas and writes **api_config** to Secrets Manager (`{prefix}/api-config`) with `api_gateway_url`, `api_gateway_health_url`, `gateway_get_hospitals_lambda_arn`, `gateway_eka_lambda_arn`. Use the secret for scripts and curl (no need to run `terraform output`).

## Step 2: Install Setup Script Dependencies

```bash
pip install bedrock-agentcore-starter-toolkit boto3
```

## Step 3: Run Gateway Setup Script

No Terraform output needed: the script reads Lambda ARNs from the **api_config** secret if env vars are not set.

```bash
# Option A: load config from secret (boto3), then run setup
eval $(python scripts/load_api_config.py --exports)
python scripts/setup_agentcore_gateway.py

# Option B: run with no args; script reads api_config secret via boto3
python scripts/setup_agentcore_gateway.py
```

To pass ARNs explicitly: `GATEWAY_GET_HOSPITALS_LAMBDA_ARN`, `GATEWAY_EKA_LAMBDA_ARN`, or first arg and `--eka <arn>`. Use `--gateway-id <id>` when reusing an existing Gateway.

The script will:

1. Create Cognito OAuth authorizer
2. Create MCP Gateway with Cognito auth
3. Add the get_hospitals Lambda as a target with tool schema
4. Add Lambda permission for the Gateway execution role
5. Save `gateway_config.json` with `gateway_url`, `gateway_id`, `region`, `client_info`

## Step 4: Use the Gateway

- **MCP URL**: From `gateway_config.json` → `gateway_url`
- **Tool name**: `get-hospitals-target___get_hospitals` (target name + `___` + tool name)
- **Auth**: Use `client_info` (client_id, client_secret, token_endpoint, scope) for OAuth client-credentials flow

### Step 4b: Wire Hospital Matcher agent to Gateway (optional)

To have the agent use the Gateway instead of in-agent synthetic data, set these **environment variables on the AgentCore Runtime** (e.g. in AWS Console → Bedrock AgentCore → your runtime, or in your deployment config). Values come from `gateway_config.json` and `client_info`:

- `GATEWAY_MCP_URL` = `gateway_url` from config
- `GATEWAY_CLIENT_ID` = `client_info.client_id` (if present)
- `GATEWAY_CLIENT_SECRET` = `client_info.client_secret`
- `GATEWAY_TOKEN_ENDPOINT` = `client_info.token_endpoint`
- `GATEWAY_SCOPE` = `client_info.scope` or `bedrock-agentcore-gateway`

If `client_info` is null (e.g. reusing an existing Gateway), create a Cognito app client for the same user pool and use its id/secret. Then redeploy the agent: `cd agentcore/agent && agentcore deploy`.

### Step 4c: Wire Triage to Eka (optional)

To let the Triage Converse flow use Eka tools (search_indian_medications, search_treatment_protocols), set the same Gateway env vars on the **Triage Lambda** (e.g. in Console or Terraform):

- `GATEWAY_MCP_URL`, `GATEWAY_CLIENT_ID`, `GATEWAY_CLIENT_SECRET`, `GATEWAY_TOKEN_ENDPOINT`, optional `GATEWAY_SCOPE`

Ensure the Eka target is added to the Gateway (run setup script with `--eka <eka_lambda_arn>`). Then POST /triage will use Eka when the model requests drug or protocol lookups.

## Lambda Handler Format (Reference)

The Gateway invokes the Lambda with:

- **Event**: `{ "severity": "high", "limit": 3 }` (tool input props)
- **Context**: `client_context.custom["bedrockAgentCoreToolName"]` = `TARGET___get_hospitals`
- **Response**: `{ "hospitals": [...], "safety_disclaimer": "..." }`

Strip the `TARGET___` prefix to identify the tool when multiple tools share one Lambda.

## Troubleshooting

| Issue | Action |
|-------|--------|
| "Lambda permission already exists" | Safe to ignore; permission was added previously |
| "Could not add Lambda permission" | Manually add resource policy: allow `bedrock-agentcore.amazonaws.com` or Gateway execution role to invoke the Lambda |
| Toolkit creates default Lambda | Use boto3 `create_gateway_target` (as in the script) with your Lambda ARN and tool schema; do not use `target_payload=None` |
| Tool not found in MCP | Verify target name; full tool name is `{target_name}___get_hospitals` |

---

## See also

- [RELEASE-Gateway-Eka-Integration.md](./RELEASE-Gateway-Eka-Integration.md) – Release notes and configuration reference  
- [TESTING-Gateway-Eka.md](./TESTING-Gateway-Eka.md) – Unit, integration, and API testing steps
