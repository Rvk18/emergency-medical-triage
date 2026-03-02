# AgentCore Hospital Matcher

AgentCore Runtime deployment for the Hospital Matcher agent. Used when `USE_AGENTCORE=true`.

## Setup (first time)

1. Install the starter toolkit:
   ```bash
   pip install bedrock-agentcore-starter-toolkit strands-agents
   ```

2. Configure and deploy:
   ```bash
   cd agentcore/agent
   agentcore configure --entrypoint hospital_matcher_agent.py --non-interactive
   agentcore deploy
   ```

3. Note the **Agent Runtime ARN** from the deploy output. Set it in Lambda:
   - `USE_AGENTCORE=true`
   - `AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:...`

## Local testing

```bash
cd agentcore/agent
agentcore deploy --local
# In another terminal:
agentcore invoke '{"severity":"high","recommendations":["Emergency department"],"limit":3}'
```

## Architecture

- **Agent**: Strands + Bedrock; uses `get_synthetic_hospitals` tool for mock Indian hospital data.
- **Lambda**: When `USE_AGENTCORE=true`, calls `InvokeAgentRuntime` instead of Converse API.
- **Gateway**: To be added in AC-3 (Hospital MCP).
