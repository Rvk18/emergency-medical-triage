# Backend TODO – AgentCore / Gateway

**Branch:** `feature/ac4-routing-identity` (merge to `main` when ready). For next work, create a new branch from `main`.  
**Last updated:** Mar 2026

---

## Status

- **AC-1 (Gateway + Eka):** Done. Hospital Matcher → Gateway (A), Eka as Gateway target (B), Triage → Eka (C). See [RELEASE-Gateway-Eka-Integration.md](./RELEASE-Gateway-Eka-Integration.md) and [TESTING-Gateway-Eka.md](./TESTING-Gateway-Eka.md).
- **AC-2 (Triage on AgentCore):** Done. Triage agent in `agentcore/agent/triage_agent.py`; POST /triage invokes AgentCore when `USE_AGENTCORE_TRIAGE` and `TRIAGE_AGENT_RUNTIME_ARN` set; observability in [OBSERVABILITY.md](./OBSERVABILITY.md).
- **AC-3 (Memory + Hospital MCP):** In progress. Optional `session_id` / `patient_id` on /triage and /hospitals; passed to AgentCore as `runtimeSessionId` for memory continuity. Hospital Matcher uses Gateway get_hospitals (MCP). See [agentcore-implementation-plan.md](./agentcore-implementation-plan.md).
- **AC-4 (Routing + Identity):** **Routing pipeline done.** POST /route works (Route Lambda → Gateway maps-target___get_directions → Maps Lambda; returns stub when Google Maps API key not set). RMP auth (Cognito) on /triage, /hospitals, /route. Routing agent and Gateway routing target exist; Hospital Matcher can call routing-target___get_route. **Next:** Guardrails G1–G3, Policy, optional real Google Maps. See [AC4-Routing-Identity-Design.md](./AC4-Routing-Identity-Design.md) and [NEXT-SESSION.md](./NEXT-SESSION.md) for what to work on tomorrow.

---

## What to work on next (tomorrow / next session)

See **[NEXT-SESSION.md](./NEXT-SESSION.md)** for a concise list: Google Maps key, Eka validation (E1–E5), guardrails (G1–G3), or HIPAA (H1–H4). After AC-4, see [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md).

---

## Order of Work

### Phase 1: Gateway Integration (A → B → C) — Done

1. **A.** Wire Hospital Matcher agent to Gateway — **Done**
2. **B.** Add Eka as Gateway target — **Done**
3. **C.** Wire Triage agent to Eka tools — **Done**

### Phase 2: AgentCore Phases (AC-2 → AC-3 → AC-4) — AC-4 routing done

4. **AC-2.** Triage on AgentCore + Observability — **Done**
5. **AC-3.** Memory + Hospital MCP — In progress
6. **AC-4.** Routing + Identity — **Routing pipeline done** (POST /route, Gateway maps + routing targets, RMP auth). Remaining: G1–G3, Policy, optional Google Maps key.

---

## Key References

- [NEXT-SESSION.md](./NEXT-SESSION.md) – What to work on next session (create new branch from main)
- [RELEASE-Gateway-Eka-Integration.md](./RELEASE-Gateway-Eka-Integration.md) – AC-1 release notes, config, quick test
- [TESTING-Pipeline-curl.md](./TESTING-Pipeline-curl.md) – Triage → Hospitals → Route curl; use `python3 scripts/get_rmp_token.py`
- [TESTING-Gateway-Eka.md](./TESTING-Gateway-Eka.md) – Unit, integration, API tests
- [secrets.md](./secrets.md) – Terraform-created secrets, api_config keys, gateway-config (client_info.scope), load scripts
- [agentcore-implementation-plan.md](./agentcore-implementation-plan.md) – Phases, architecture
- [agentcore-gateway-manual-steps.md](./agentcore-gateway-manual-steps.md) – Gateway setup (use `python3` for scripts)
- [OBSERVABILITY.md](./OBSERVABILITY.md) – Triage/Hospital Matcher logs, trace review
- [implementation-history.md](./implementation-history.md) – History, fixes
