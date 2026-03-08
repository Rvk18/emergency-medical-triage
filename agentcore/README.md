# AgentCore Hospital Matcher & Triage

AgentCore Runtime deployments. Hospital Matcher is used when `USE_AGENTCORE=true`; Triage when `USE_AGENTCORE_TRIAGE=true` (AC-2).

## Redeploy AgentCore (e.g. after G3 prompt updates)

**Important:** After every `agentcore deploy` you **must** run the corresponding enable script so the runtime keeps Gateway (and Eka on Triage) env. Otherwise POST /hospitals, POST /route, or Eka triage will break. See [docs/DEPLOY.md](../docs/DEPLOY.md) § "After agentcore deploy".

To push the latest agent code (including G3 safety prompts) to all three runtimes:

1. **Prereqs:** From project root, `pip install bedrock-agentcore-starter-toolkit strands-agents` and AWS credentials configured.

2. **Hospital Matcher** (one runtime):
   ```bash
   cd agentcore/agent
   agentcore configure --entrypoint hospital_matcher_agent.py --non-interactive
   agentcore deploy
   ```
   Note the **Runtime ARN**; ensure `agent_runtime_arn` in `infrastructure/terraform.tfvars` matches (or update tfvars and run `terraform apply` so the Hospital Matcher Lambda uses it). **Then run** (from project root): `python3 scripts/enable_gateway_on_hospital_matcher_runtime.py`

3. **Triage** (separate runtime; has Eka tools):
   ```bash
   agentcore configure --entrypoint triage_agent.py --non-interactive
   agentcore deploy
   ```
   Note the **Runtime ARN**; ensure `triage_agent_runtime_arn` in `infrastructure/terraform.tfvars` matches. **Then re-apply Gateway env vars** so Eka stays enabled on the updated runtime:
   ```bash
   cd ../..   # project root
   python3 scripts/enable_eka_on_runtime.py
   ```

4. **Routing** (third runtime):
   ```bash
   cd agentcore/agent
   agentcore configure --entrypoint routing_agent.py --non-interactive
   agentcore deploy
   ```
   Update `routing_agent_runtime_arn` in `infrastructure/terraform.tfvars` if the ARN changed, then `terraform apply`. **Then run** (from project root): `python3 scripts/enable_gateway_on_routing_runtime.py`

5. **Verify:** Run a triage curl and a hospitals curl; confirm responses and that Eka brands appear when you ask for Indian medications.

---

## Setup (first time)

1. Install the starter toolkit:
   ```bash
   pip install bedrock-agentcore-starter-toolkit strands-agents
   ```

2. **Hospital Matcher** – configure and deploy:
   ```bash
   cd agentcore/agent
   agentcore configure --entrypoint hospital_matcher_agent.py --non-interactive
   agentcore deploy
   ```
   Set `USE_AGENTCORE=true` and `AGENT_RUNTIME_ARN=<arn>` on the Hospital Matcher Lambda.

3. **Triage (AC-2)** – deploy a second runtime for the triage agent:
   ```bash
   cd agentcore/agent
   agentcore configure --entrypoint triage_agent.py --non-interactive
   agentcore deploy
   ```
   Set `USE_AGENTCORE_TRIAGE=true` and `TRIAGE_AGENT_RUNTIME_ARN=<arn>` on the Triage Lambda (e.g. in Terraform: `use_agentcore_triage=true`, `triage_agent_runtime_arn="arn:..."`).

4. **Routing agent** – deploy a third runtime (used by Hospital Matcher via Gateway `routing-target___get_route`; agent uses Google Maps MCP):
   ```bash
   cd agentcore/agent
   agentcore configure --entrypoint routing_agent.py --non-interactive
   agentcore deploy
   ```
   Copy the **Runtime ARN** from the deploy output, set `routing_agent_runtime_arn = "arn:..."` in `infrastructure/terraform.tfvars`, then run `terraform apply`. The Gateway routing Lambda will then invoke this Runtime when Hospital Matcher calls `routing-target___get_route`.

## Local testing

**Hospital Matcher:**
```bash
cd agentcore/agent
agentcore deploy --local
# In another terminal:
agentcore invoke '{"severity":"high","recommendations":["Emergency department"],"limit":3}'
```

**Triage:**
```bash
agentcore configure --entrypoint triage_agent.py --non-interactive
agentcore deploy --local
agentcore invoke '{"symptoms":["chest pain","shortness of breath"],"vitals":{"heart_rate":110},"age_years":55,"sex":"M"}'
```

**Routing:**
```bash
agentcore configure --entrypoint routing_agent.py --non-interactive
agentcore deploy --local
agentcore invoke '{"origin":{"lat":12.97,"lon":77.59},"destination":{"lat":13.08,"lon":80.27}}'
```

## Architecture

- **Hospital Matcher**: Strands + Bedrock; uses **Gateway MCP** `get_hospitals` when Gateway env vars are set, else in-agent synthetic data.
- **Triage (AC-2)**: Strands + Bedrock; optional Eka tools (`search_indian_medications_tool`, `search_treatment_protocols_tool`) via Gateway when configured.
- **Routing**: AgentCore agent using Gateway MCP (maps-target). Invoked via Gateway `routing-target___get_route` by Hospital Matcher; also POST /route.
- **Lambda**: When `USE_AGENTCORE=true` / `USE_AGENTCORE_TRIAGE=true`, Lambdas call `InvokeAgentRuntime` instead of Converse API.
- **Gateway wiring**: Set on the Runtime (Console or deployment config) from `gateway_config.json`:
  - `GATEWAY_MCP_URL`, `GATEWAY_CLIENT_ID`, `GATEWAY_CLIENT_SECRET`, `GATEWAY_TOKEN_ENDPOINT`, optional `GATEWAY_SCOPE`
  - Then redeploy: `agentcore deploy`
