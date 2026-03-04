# AgentCore Hospital Matcher & Triage

AgentCore Runtime deployments. Hospital Matcher is used when `USE_AGENTCORE=true`; Triage when `USE_AGENTCORE_TRIAGE=true` (AC-2).

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

## Architecture

- **Hospital Matcher**: Strands + Bedrock; uses **Gateway MCP** `get_hospitals` when Gateway env vars are set, else in-agent synthetic data.
- **Triage (AC-2)**: Strands + Bedrock; optional Eka tools (`search_indian_medications_tool`, `search_treatment_protocols_tool`) via Gateway when configured.
- **Lambda**: When `USE_AGENTCORE=true` / `USE_AGENTCORE_TRIAGE=true`, Lambdas call `InvokeAgentRuntime` instead of Converse API.
- **Gateway wiring**: Set on the Runtime (Console or deployment config) from `gateway_config.json`:
  - `GATEWAY_MCP_URL`, `GATEWAY_CLIENT_ID`, `GATEWAY_CLIENT_SECRET`, `GATEWAY_TOKEN_ENDPOINT`, optional `GATEWAY_SCOPE`
  - Then redeploy: `agentcore deploy`
