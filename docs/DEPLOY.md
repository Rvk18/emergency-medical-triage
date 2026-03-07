# Deploy and configuration (why scripts, who runs them)

**Audience:** DevOps, frontend leads, hackathon evaluators.

---

## Why run scripts after Terraform?

- **Terraform** creates and configures: API Gateway, Lambdas (triage, hospital matcher, route, gateway_get_hospitals, gateway_maps, gateway_routing, gateway_eka), Secrets Manager **secret names** (e.g. `api-config`, `gateway-config`), IAM, RDS, etc. Lambdas get their config via **env vars** (e.g. `GATEWAY_CONFIG_SECRET_NAME`) and read secret values at runtime. So **Lambdas do not need any script to be run** for normal operation.

- The **AgentCore Gateway** and **gateway_config** secret **value** are not created by Terraform:
  - The **Gateway** (MCP + Cognito OAuth + targets like get_hospitals, maps, routing) is created by **`scripts/setup_agentcore_gateway.py`** using the Bedrock AgentCore Control API.
  - The **gateway_config** secret is created by Terraform as an **empty** secret; the **setup script** writes the Gateway URL, OAuth client_id/client_secret/token_endpoint/scope into it. So **POST /route** and any runtime that calls the Gateway need this secret to be **populated** by running the setup script once.

- **AgentCore runtimes** (Hospital Matcher, Triage, Routing) are created/updated by **`agentcore deploy`** (CLI), not Terraform. Their **environment variables** (e.g. Gateway URL, OAuth) are set via the Bedrock AgentCore Control API. Terraform has no provider that manages these runtimes. So we use a **script** that calls `UpdateAgentRuntime` to set the five Gateway env vars. The setup script does this by default so that after one run, both the Gateway and the runtimes are ready.

**Who runs the scripts when deploying to Lambda/EC2?**

- **First-time deploy (or new environment):** The person or CI pipeline that deploys the stack runs, in order:
  1. **`terraform apply`** – creates all AWS resources and secrets (with empty gateway_config).
  2. **`python3 scripts/setup_agentcore_gateway.py`** – creates the Gateway, populates gateway_config, and sets Gateway env vars on the Hospital Matcher and Routing runtimes.

- **Subsequent deploys:** If you only change Lambda code (e.g. Terraform apply again), you do **not** need to re-run the setup script unless you recreated the Gateway or the secret. If you **redeploy an AgentCore agent** (e.g. `agentcore deploy` for hospital_matcher_agent), that deploy can overwrite the runtime’s env vars; then re-run **`python3 scripts/enable_gateway_on_hospital_matcher_runtime.py`** (or **`enable_gateway_on_routing_runtime.py`**) to re-apply Gateway env vars. So the “scripts” are either **one-time** (Gateway setup) or **only after an agentcore deploy** (re-apply env to that runtime).

- **CI/CD:** Treat “deploy” as: `terraform apply` then `python3 scripts/setup_agentcore_gateway.py` (with AWS creds and optional `--skip-runtime-env` if you manage runtimes elsewhere). After any `agentcore deploy` in the same pipeline, add a step to run the corresponding `enable_gateway_on_*_runtime.py` for the agents you deployed.

---

## Deploy order (recommended)

| Step | Command | Purpose |
|------|---------|--------|
| 1 | `cd infrastructure && terraform apply` | Create API Gateway, Lambdas, secrets (api_config, gateway_config placeholder), RDS, etc. |
| 2 | `python3 scripts/setup_agentcore_gateway.py` | Create AgentCore Gateway, populate gateway_config, set Gateway env on Hospital Matcher and Routing runtimes. |
| 3 | (Optional) If you later run `agentcore deploy` for hospital_matcher or routing | Re-run `python3 scripts/enable_gateway_on_hospital_matcher_runtime.py` or `enable_gateway_on_routing_runtime.py` so that runtime has Gateway env again. |

**Getting API URL for frontend:** After step 1, the API URL is in the **api_config** secret. Run `eval $(python3 scripts/load_api_config.py --exports)` to set `API_URL` in your shell, or read the secret from your app (e.g. from a backend that exposes config). Terraform does not need to “run” anything else for Lambdas to work; they read secrets at runtime.

---

## Why POST /route or directions might fail after “it worked this afternoon”

- **gateway_config** is populated only by the setup script. If the secret was recreated (e.g. Terraform destroy/apply) or overwritten, it would be empty again and **POST /route** would return 503 (Gateway not configured) or 500 (e.g. token fetch failure).
- **Gateway OAuth** (Cognito) or **maps target** (gateway_maps Lambda) might be misconfigured or the Google Maps API key might be missing/invalid in the maps Lambda env.
- **Routing / Hospital Matcher runtimes** lose Gateway env vars after an **agentcore deploy**; re-run the enable script for the runtime you redeployed.

To fix: Re-run **`python3 scripts/setup_agentcore_gateway.py`** (and ensure `google_maps_api_key` is set in tfvars so the maps Lambda has the key). Then test **POST /route** again.

---

## Summary

| Question | Answer |
|----------|--------|
| Do Lambdas need scripts to run on each deploy? | No. Lambdas get config from Terraform (env) and read Secrets Manager at runtime. |
| Who runs the Gateway setup script? | Whoever does the first-time deploy (or CI), once per environment. |
| Who runs enable_gateway_on_*_runtime? | Only after you run **agentcore deploy** for that agent, to re-apply Gateway env vars. |
| Is this a good method? | Yes for the current split: Terraform owns infra and Lambdas; AgentCore Gateway and runtime env are owned by the Control API and are configured by the scripts. For a fully Terraform-only deploy you would need an AgentCore Terraform provider (or a Lambda that runs on a schedule/custom resource to call UpdateAgentRuntime). |
