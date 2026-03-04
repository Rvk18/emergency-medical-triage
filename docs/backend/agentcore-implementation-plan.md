# AgentCore Implementation Plan

**Purpose:** Migrate Emergency Medical Triage AI layer from classic Bedrock Converse API / Agents to **Amazon Bedrock AgentCore** for better MCP integration, observability, memory, and production readiness.

> **References:** [Implementation Plan](./implementation-plan.md) | [Implementation History](./implementation-history.md) | [AgentCore Docs](https://docs.aws.amazon.com/bedrock-agentcore/?region=us-east-1)

---

## Agreed Approach (Feb 2026)

| Topic | Decision |
|-------|----------|
| **Experience** | No prior AgentCore use; Console access available |
| **AC-1 scope** | Hospital Matcher only; migrate Triage, Routing once stable |
| **Gateway data** | Try MCP for hospital knowledge if available; otherwise synthetic data only |
| **IaC** | Terraform if not too time-consuming; otherwise Console |
| **Cutover** | Converse fallback during migration; switch fully once AgentCore path is stable |
| **Hospital data** | No MCP server for hackathon; synthetic/stub data is acceptable |
| **AC-1 observability** | Include basic tracing/metrics in AC-1 |

---

## Why AgentCore

| Need | Current (Converse/Classic Agents) | AgentCore |
|------|----------------------------------|-----------|
| Hospital Data MCP | Manual integration, stubs | **Gateway** – expose MCP tools natively |
| Trace review / medical audit | Custom logging | **Observability** – tracing, OpenTelemetry, CloudWatch |
| Patient context across sessions | Aurora only | **Memory** – short-term + long-term |
| Safe agent boundaries | Prompts | **Policy** (preview) – explicit action control |
| RMP / Admin auth | Custom | **Identity** – Cognito/IdP integration |

---

## AgentCore Capabilities to Adopt

| Capability | Priority | Use Case |
|------------|----------|----------|
| **Runtime** | P0 | Host Triage, Hospital Matcher, Routing agents |
| **Gateway** | P0 | Expose Hospital Data MCP, triage tools |
| **Observability** | P0 | Trace review, medical audit, debugging |
| **Memory** | P1 | Patient context, repeat visits, follow-up |
| **Identity** | P1 | RMP auth when frontend ready |
| **Policy** | P2 | Stricter safety boundaries (when GA) |
| **Code Interpreter** | P3 | Optional: scoring, travel time calculations |
| **Browser** | P3 | Optional: hospital availability lookup |
| **Evaluations** | P3 | Quality measurement (when GA) |

---

## Architecture (Target)

```
                    ┌─────────────────────────────────────────┐
                    │           API Gateway                    │
                    │  /triage  /hospitals  /route  /health   │
                    └─────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
             ┌──────────┐      ┌──────────────┐   ┌──────────┐
             │  Triage  │      │Hospital Match│   │ Routing  │
             │  Lambda  │      │   Lambda     │   │  Lambda  │
             └────┬─────┘      └──────┬───────┘   └────┬─────┘
                  │                   │                 │
                  └───────────────────┼─────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │      Bedrock AgentCore            │
                    │  ┌─────────┐  ┌──────────────┐   │
                    │  │Runtime  │  │   Gateway    │   │
                    │  │(agents) │  │(MCP tools)   │   │
                    │  └────┬────┘  └──────┬───────┘   │
                    │       │              │           │
                    │  ┌────┴──────────────┴───────┐   │
                    │  │ Memory │ Observability    │   │
                    │  └──────────────────────────┘   │
                    └─────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │  Aurora (triage_assessments,      │
                    │  hospital_matches)                │
                    └──────────────────────────────────┘
```

---

## Phases

### Phase AC-1: Foundation — ✅ Done

**Goal:** Stand up AgentCore Runtime and Gateway; connect Hospital Matcher; add Eka for Triage; basic tracing.

**Deliverables:**
- [x] Hospital Matcher agent on AgentCore Runtime (Strands + Gateway/synthetic tool)
- [x] AgentCore Gateway: get_hospitals Lambda target; Eka Lambda target (search_medications, search_protocols)
- [x] POST /hospitals invokes AgentCore when `use_agentcore=true` (Converse fallback)
- [x] Triage uses Eka tools via Gateway when GATEWAY_* env set
- [x] Basic tracing (CloudWatch Logs: `HospitalMatcher source= duration_ms=`)
- [x] Terraform: api_config secret (API URL, Gateway ARNs); single requirements.txt; load_api_config.py (boto3)

**Manual step:** Deploy the agent with `agentcore deploy` from `agentcore/agent/`, then set `agent_runtime_arn` in tfvars. Run Gateway setup: `python scripts/setup_agentcore_gateway.py` (reads ARNs from api_config secret).

---

### Phase AC-2: Triage + Observability

**Goal:** Migrate Triage to AgentCore; enable full trace observability.

**Deliverables:**
- [ ] Triage agent on AgentCore Runtime
- [ ] AgentCore Observability: tracing, CloudWatch dashboards
- [ ] Trace review workflow for Admin/Dev (medical audit)
- [ ] POST /triage invokes AgentCore
- [ ] Persist triage to Aurora (unchanged)

---

### Phase AC-3: Memory + Hospital MCP

**Goal:** Add Memory for patient context; integrate Hospital Data MCP via Gateway.

**Deliverables:**
- [ ] AgentCore Memory: short-term (session) + long-term (patient)
- [ ] Gateway: Hospital Data MCP as tool source
- [ ] Hospital Matcher uses real hospital data (replace stubs)
- [ ] Patient context available across triage → hospital → routing flow

---

### Phase AC-4: Routing + Identity

**Goal:** Add Routing agent; enable Identity for RMP auth.

**Deliverables:**
- [ ] Routing agent on AgentCore Runtime
- [ ] POST /route endpoint
- [ ] AgentCore Identity: Cognito/IdP integration for RMP
- [ ] Policy (if GA): stricter agent action boundaries

---

## Migration Strategy

1. **Incremental:** Keep Converse API fallback until AgentCore path is stable; then hard cutover (no long-term feature flag).
2. **Feature flags:** `USE_AGENTCORE` env var to toggle during migration; remove once cutover complete.
3. **Preserve contracts:** API request/response schemas unchanged.
4. **Aurora unchanged:** Persistence layer stays; AgentCore replaces only the AI invocation path.

---

## Execution Order

| Phase | Focus | Status | Dependency |
|-------|-------|--------|------------|
| AC-1 | Runtime + Gateway + Hospital Matcher + Eka (A,B,C) | ✅ Done | None |
| **AC-2** | Triage on AgentCore + Observability | **Next** | AC-1 |
| **AC-3** | Memory + Hospital MCP | Pending | AC-1, AC-2 |
| **AC-4** | Routing + Identity | Pending | AC-1 |

---

## Next: AC-2, AC-3, AC-4

1. **AC-2** – Triage agent on AgentCore Runtime; full observability (traces, CloudWatch dashboards, medical audit); POST /triage invokes AgentCore; persist to Aurora unchanged.
2. **AC-3** – AgentCore Memory (short/long-term); Hospital Matcher uses Gateway/MCP tools; patient context across triage → hospital → routing.
3. **AC-4** – Routing agent on AgentCore Runtime; POST /route; AgentCore Identity (Cognito/IdP for RMP); Policy (if GA).

---

## Technical Notes

- **AgentCore SDK:** Python SDK on [GitHub](https://github.com/aws/amazon-bedrock-agentcore-sdk-python)
- **Gateway:** Transforms APIs/Lambda/MCP into tools; MCP support via [Gateway tutorials](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-tutorials.html)
- **Runtime:** Serverless; supports extended sessions; any framework (LangGraph, CrewAI, etc.)
- **Region:** AgentCore available in us-east-1; verify other regions as needed

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| AgentCore API changes / preview features | Pin SDK version; use feature flags |
| Migration breaks existing flows | Keep Converse fallback; A/B test |
| MCP not yet ready | Use Gateway with Lambda/API stubs until MCP available |

---
