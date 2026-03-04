# Testing: Gateway & Eka Integration

This guide covers how to test the Gateway wiring (A, B, C) and Eka integration. See [RELEASE-Gateway-Eka-Integration.md](./RELEASE-Gateway-Eka-Integration.md) for what was released.

---

## 1. Prerequisites

- **Environment:** Python 3.10+, AWS CLI configured, Terraform and `terraform apply` run if testing deployed Lambdas.
- **Optional:** Eka API key in Terraform (`eka_api_key`) and Gateway setup script run so Eka target and `gateway_config.json` exist.

---

## 2. Unit / Local Tests

### 2.1 Triage tool config (no Gateway)

When Gateway env vars are **not** set, the triage tool config should be the standard single-tool config.

```bash
cd /path/to/AI_Hackathon_Triage
# Unset any Gateway vars so we test fallback
unset GATEWAY_MCP_URL GATEWAY_CLIENT_ID GATEWAY_CLIENT_SECRET GATEWAY_TOKEN_ENDPOINT
python -c "
from triage.core.tools import get_triage_tool_config, get_triage_tool_config_with_eka
c = get_triage_tool_config_with_eka()
assert c['toolChoice']['tool']['name'] == 'submit_triage_result' or len(c['tools']) == 1, 'Without Gateway should be single-tool or submit_triage_result only'
print('OK: get_triage_tool_config_with_eka fallback')
"
```

### 2.2 Triage tool config (with Gateway)

When Gateway env vars **are** set, the config should include Eka tools and `toolChoice: any`.

```bash
export GATEWAY_MCP_URL=https://test.gateway.example/mcp
export GATEWAY_CLIENT_ID=test
export GATEWAY_CLIENT_SECRET=test
export GATEWAY_TOKEN_ENDPOINT=https://test.auth.example/token
python -c "
from triage.core.tools import get_triage_tool_config_with_eka
c = get_triage_tool_config_with_eka()
names = [t['toolSpec']['name'] for t in c['tools']]
assert 'search_indian_medications' in names and 'search_treatment_protocols' in names and 'submit_triage_result' in names
assert c['toolChoice']['tool']['name'] == 'any'
print('OK: Eka tools present, toolChoice=any')
"
```

### 2.3 Gateway client (is_gateway_configured)

```bash
unset GATEWAY_MCP_URL
python -c "
from triage.core.gateway_client import is_gateway_configured
assert is_gateway_configured() is False
print('OK: Gateway not configured')
"
export GATEWAY_MCP_URL=https://x.example/mcp
export GATEWAY_CLIENT_ID=c
export GATEWAY_CLIENT_SECRET=s
export GATEWAY_TOKEN_ENDPOINT=https://t.example/token
python -c "
from triage.core.gateway_client import is_gateway_configured
assert is_gateway_configured() is True
print('OK: Gateway configured')
"
```

### 2.4 Eka Lambda handler (stub when no secret)

Run from the Lambda source directory so the handler is importable. Use a context object where `client_context.custom` is a **dict** (e.g. `custom = {"bedrockAgentCoreToolName": "eka-target___search_medications"}`):

```bash
cd infrastructure/gateway_eka_lambda_src
EKA_CONFIG_SECRET_NAME= python3 -c "
from lambda_handler import handler
class Ctx:
    class client_context:
        custom = {'bedrockAgentCoreToolName': 'eka-target___search_medications'}
event = {'drug_name': 'Paracetamol'}
out = handler(event, Ctx())
assert 'medications' in out
print('OK: Eka Lambda stub returns medications')
"
```

Automated tests for triage/Gateway (no Lambda import): from project root run  
`PYTHONPATH=src pytest tests/test_gateway_eka.py -v` (requires pytest). See checklist below.

### 2.5 Hospital Matcher agent gateway_client (is_gateway_configured)

```bash
cd agentcore/agent
unset GATEWAY_MCP_URL
python -c "
from gateway_client import _is_gateway_configured
assert _is_gateway_configured() is False
print('OK: Agent gateway not configured')
"
```

### 2.6 Run existing test suite

```bash
cd /path/to/AI_Hackathon_Triage
pip install -r requirements-dev.txt  # or pytest if needed
pytest tests/ -v
```

---

## 3. Integration Tests (Deployed)

These require Terraform-applied infrastructure and, for Gateway/Eka, the setup script and env vars.

### 3.1 POST /triage (no Eka)

- **Expect:** 200, JSON with `severity`, `recommendations`, `safety_disclaimer`, etc. Model uses only `submit_triage_result` (no Eka tools) when Triage Lambda has no `GATEWAY_*` env vars.

```bash
API_URL=$(cd infrastructure && terraform output -raw api_gateway_url 2>/dev/null || echo "https://YOUR_API.execute-api.us-east-1.amazonaws.com/dev")
curl -s -X POST "${API_URL}triage" \
  -H "Content-Type: application/json" \
  -d '{"symptoms":["chest pain"],"vitals":{"heart_rate":110}}' | jq .
```

### 3.2 POST /triage (with Eka)

- **Prereq:** Triage Lambda has `GATEWAY_MCP_URL`, `GATEWAY_CLIENT_ID`, `GATEWAY_CLIENT_SECRET`, `GATEWAY_TOKEN_ENDPOINT` set; Eka target added to Gateway.
- **Expect:** 200. The model may call `search_indian_medications` or `search_treatment_protocols` before `submit_triage_result`; behaviour depends on prompt and model.

Same `curl` as above; ensure Gateway and Eka are configured.

### 3.3 POST /hospitals (AgentCore, no Gateway on Runtime)

- **Prereq:** `USE_AGENTCORE=true`, `AGENT_RUNTIME_ARN` set on Hospital Matcher Lambda; Runtime **without** Gateway env vars.
- **Expect:** 200, `hospitals` array (synthetic data from in-agent tool).

```bash
curl -s -X POST "${API_URL}hospitals" \
  -H "Content-Type: application/json" \
  -d '{"severity":"high","recommendations":["Emergency department"],"limit":3}' | jq .
```

### 3.4 POST /hospitals (AgentCore + Gateway on Runtime)

- **Prereq:** Runtime has Gateway env vars set; agent redeployed.
- **Expect:** 200, `hospitals` from Gateway Lambda (same shape; may be same synthetic data if Gateway target is the same Lambda).

Same `curl` as 3.3.

### 3.5 Gateway setup script (dry run)

- **Prereq:** Terraform applied; `gateway_get_hospitals_lambda_arn` output.
- **Action:** Run setup script with hospitals Lambda ARN only (no `--eka` if you want to test hospitals target only).

```bash
export GATEWAY_GET_HOSPITALS_LAMBDA_ARN=$(cd infrastructure && terraform output -raw gateway_get_hospitals_lambda_arn)
python scripts/setup_agentcore_gateway.py
# Check gateway_config.json for gateway_url, gateway_id, client_info
```

With Eka Lambda:

```bash
export GATEWAY_EKA_LAMBDA_ARN=$(cd infrastructure && terraform output -raw gateway_eka_lambda_arn)
python scripts/setup_agentcore_gateway.py
# Config should include eka_target_name, eka_lambda_arn
```

---

## 4. Sample Payloads

### Triage

```json
{
  "symptoms": ["fever", "headache"],
  "vitals": {"temperature_f": 102, "heart_rate": 90},
  "age_years": 35,
  "sex": "male"
}
```

### Hospitals

```json
{
  "severity": "high",
  "recommendations": ["Emergency department", "Stabilisation"],
  "limit": 3
}
```

---

## 5. Checklist

| Test | Description | Pass |
|------|-------------|------|
| Triage tool config without Gateway | `get_triage_tool_config_with_eka()` returns single-tool config | ☐ |
| Triage tool config with Gateway | Eka tools + toolChoice any | ☐ |
| `is_gateway_configured()` | True only when all required env set | ☐ |
| Eka Lambda stub | Returns medications stub when no secret; context `client_context.custom` = dict | ☐ |
| Agent `_is_gateway_configured()` | False when GATEWAY_MCP_URL unset | ☐ |
| `PYTHONPATH=src pytest tests/` | Existing and gateway_eka tests pass | ☐ |
| POST /triage (no Eka) | 200, valid triage result | ☐ |
| POST /triage (with Eka) | 200 when Gateway + Eka configured | ☐ |
| POST /hospitals (AgentCore) | 200, hospitals array | ☐ |
| Gateway setup script | Creates/updates Gateway and config | ☐ |

---

## 6. References

- [RELEASE-Gateway-Eka-Integration.md](./RELEASE-Gateway-Eka-Integration.md)
- [agentcore-gateway-manual-steps.md](./agentcore-gateway-manual-steps.md)
