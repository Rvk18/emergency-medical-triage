# Secrets Manager – Created by Terraform

All of these secrets are **created and updated by Terraform** when you run `terraform apply`. They do not exist until then. Do not create them manually; use `cd infrastructure && terraform apply`.

---

## Secrets (name prefix: `{project_name}-{environment}` e.g. `emergency-medical-triage-dev`)

| Secret name | Description | Keys |
|-------------|-------------|------|
| **api-config** | API URL, Gateway Lambda ARNs, region, other secret names | `api_gateway_url`, `api_gateway_health_url`, `gateway_get_hospitals_lambda_arn`, `gateway_eka_lambda_arn`, `region`, `api_config_secret_name`, `bedrock_config_secret_name`, `rds_config_secret_name`, `eka_config_secret_name` (null if no Eka key) |
| **bedrock-config** | Bedrock region and model | `region`, `model_id` |
| **rds-config** | Aurora connection (IAM auth, no password) | `host`, `port`, `database`, `username`, `region` |
| **eka-config** | Eka Care API (only if `eka_api_key` set in tfvars) | `api_key`, `client_id` |

---

## Using api-config (no Terraform output)

Scripts and curl can load config from the **api-config** secret after apply:

```bash
eval $(python scripts/load_api_config.py --exports)
curl -s "$API_URL"health
```

If the secret does not exist, the script exits with:  
`Secret '...' not found. Create it by running: cd infrastructure && terraform apply`

---

## Overriding the secret name

- **API_CONFIG_SECRET_NAME** – full secret name (e.g. `my-stack/api-config`)
- **NAME_PREFIX** – prefix only (default `emergency-medical-triage-dev`); script uses `{NAME_PREFIX}/api-config`
