# Backend TODO – AgentCore / Gateway

**Branch:** `feature/Agentcore-implementation`  
**Last updated:** Feb 2026

---

## Status

- **AC-1 (Gateway + Eka):** Done. Hospital Matcher → Gateway (A), Eka as Gateway target (B), Triage → Eka (C). See [RELEASE-Gateway-Eka-Integration.md](./RELEASE-Gateway-Eka-Integration.md) and [TESTING-Gateway-Eka.md](./TESTING-Gateway-Eka.md).
- **Next:** Proceeding with **AC-2** (Triage on AgentCore + Observability), **AC-3** (Memory + Hospital MCP), **AC-4** (Routing + Identity).

---

## Order of Work

### Phase 1: Gateway Integration (A → B → C) — Done

1. **A.** Wire Hospital Matcher agent to Gateway — **Done**
2. **B.** Add Eka as Gateway target — **Done**
3. **C.** Wire Triage agent to Eka tools — **Done**

### Phase 2: AgentCore Phases (AC-2 → AC-3 → AC-4) — Next

4. **AC-2.** Triage on AgentCore + Observability  
   - Triage agent on AgentCore Runtime; traces, CloudWatch dashboards, medical audit
5. **AC-3.** Memory + Hospital MCP  
   - Short/long-term Memory; Hospital Matcher uses Gateway/MCP tools
6. **AC-4.** Routing + Identity  
   - Routing agent on AgentCore Runtime; POST /route; Cognito/IdP for RMP auth

---

## Key References

- [RELEASE-Gateway-Eka-Integration.md](./RELEASE-Gateway-Eka-Integration.md) – AC-1 release notes, config, quick test
- [TESTING-Gateway-Eka.md](./TESTING-Gateway-Eka.md) – Unit, integration, API tests
- [secrets.md](./secrets.md) – Terraform-created secrets, api_config keys, load script
- [agentcore-implementation-plan.md](./agentcore-implementation-plan.md) – Phases, architecture
- [agentcore-gateway-manual-steps.md](./agentcore-gateway-manual-steps.md) – Gateway setup
- [implementation-history.md](./implementation-history.md) – History, fixes
