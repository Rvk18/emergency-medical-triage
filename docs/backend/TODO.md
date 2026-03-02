# Backend TODO – AgentCore / Gateway

**Branch:** `feature/Agentcore-implementation`  
**Last updated:** Feb 15, 2026

---

## Order of Work

### Phase 1: Gateway Integration (A → B → C)

1. **A.** Wire Hospital Matcher agent to Gateway  
   - Use Gateway MCP `get_hospitals` instead of in-agent synthetic tool  
   - Connect agent to Gateway URL; OAuth token from Cognito

2. **B.** Add Eka as Gateway target  
   - Create Lambda target for Eka APIs (Indian drugs, protocols)  
   - Add Eka tool schema to Gateway  
   - Use `emergency-medical-triage-dev/eka-config` secret

3. **C.** Wire Triage agent to Eka tools  
   - Triage agent calls Eka tools via Gateway  
   - Indian drugs, treatment protocols

### Phase 2: AgentCore Phases (AC-2 → AC-3 → AC-4)

4. **AC-2.** Triage on AgentCore + Observability  
   - Triage agent on AgentCore Runtime  
   - Traces, CloudWatch dashboards, medical audit

5. **AC-3.** Memory + Hospital MCP  
   - Short/long-term Memory  
   - Hospital Matcher uses Gateway/MCP tools

6. **AC-4.** Routing + Identity  
   - Routing agent on AgentCore Runtime  
   - POST /route  
   - Cognito/IdP for RMP auth

---

## Key References

- [agentcore-implementation-plan.md](./agentcore-implementation-plan.md) – Phases, architecture
- [agentcore-gateway-manual-steps.md](./agentcore-gateway-manual-steps.md) – Gateway setup
- [implementation-history.md](./implementation-history.md) – History, fixes, lessons learned
