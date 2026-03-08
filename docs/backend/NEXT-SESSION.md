# What to work on next (next session)

**Current sequence:**  
**1. New module A → B → D (next priority)** — Offline & resilience (A), Multi-language & accessibility (B), Collective intelligence (D). **RMP Learning (C) backend is complete;** frontend team owns the Learning screen — see [RMP-LEARNING-API.md](../frontend/RMP-LEARNING-API.md) for instructions.  
**2. AC-3** — Covered by comprehensive curl tests ([API-TEST-RESULTS.md](./API-TEST-RESULTS.md)); no separate phase.  
**3. Web app deploy + frontend integration** — **Last.**  
**4. Comprehensive E2E testing** — **Last.**  
See **[ROADMAP-NEXT.md](../ROADMAP-NEXT.md)** and **[NEW-MODULE-RMP-AUGMENTATION.md](./NEW-MODULE-RMP-AUGMENTATION.md)**.

**Already done:** ~~Redeploy AgentCore~~ ✅, ~~Policy~~ ✅, ~~HIPAA H1–H4~~ ✅, ~~RMP Learning (C) backend~~ ✅.

---

## Phase 1: Redeploy AgentCore ✅ Done

Redeployed all three runtimes (Hospital Matcher, Triage + enable_eka_on_runtime, Routing). G3 safety prompts are live; Eka remains enabled on triage.

---

## Phases 2–4: Policy, HIPAA, AC-3

- **2. Policy:** ✅ Done. Policy engine on Gateway via [POLICY-RUNBOOK.md](./POLICY-RUNBOOK.md) and `scripts/setup_agentcore_policy.py`.
- **3. HIPAA (H1–H4):** ✅ Done. [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) §1, [HIPAA-Compliance-Checklist.md](./HIPAA-Compliance-Checklist.md).
- **4. AC-3 re-test:** Covered by comprehensive curl tests ([API-TEST-RESULTS.md](./API-TEST-RESULTS.md)); no separate phase. Use same `session_id` in pipeline curl when desired; see [TESTING-Pipeline-curl.md](./TESTING-Pipeline-curl.md).

---

## 1. New module — next priority: A → B → D

**Scope:** **RMP Learning (C) backend done.** Frontend team implements the Learning screen per [RMP-LEARNING-API.md](../frontend/RMP-LEARNING-API.md). **Next:** A (Offline & resilience) → B (Multi-language & accessibility) → D (Collective intelligence). See **[NEW-MODULE-RMP-AUGMENTATION.md](./NEW-MODULE-RMP-AUGMENTATION.md)** §4–6.

| Order | Group | Content |
|-------|--------|--------|
| **1** | **A. Offline & resilience** | Offline triage + cached hospital/routing; sync APIs |
| 2 | B. Multi-language & accessibility | Multi-language + audio for illiterate users |
| 3 | C. RMP learning | ✅ Backend done. Frontend team: [RMP-LEARNING-API.md](../frontend/RMP-LEARNING-API.md). |
| 4 | D. Collective intelligence | Every case improves the system for all providers |

**Start with A**, then B, then D. Web app deploy and E2E testing are **last**.

---

## 2. AC-3 (session continuity)

Covered by comprehensive curl tests ([API-TEST-RESULTS.md](./API-TEST-RESULTS.md)). No separate re-test phase. Optional: use same `session_id` in pipeline curl; see [TESTING-Pipeline-curl.md](./TESTING-Pipeline-curl.md).

---

## Phase 5: Deploy web app + frontend integration **(last)**

Deploy `frontend/web/` and wire it to the backend: API URL, Cognito auth, triage → hospitals → route flow, session_id. Full checklist: [ROADMAP-NEXT.md](../ROADMAP-NEXT.md) § Phase 5. **Do after** new modules A → B → D.

---

## Phase 6: Comprehensive E2E testing (web + mobile) **(last)**

After web app deploy and integration, run end-to-end tests from both **frontend web app** and **mobile app** to confirm the full flow (triage → hospitals → route, auth, session_id) works. Document results and fix any issues. **Do after** Phase 5.

---

## Key references

| Doc | Purpose |
|-----|--------|
| [ROADMAP-NEXT.md](../ROADMAP-NEXT.md) | Phases: New module A→B→D (next), Web app + E2E (last), AC-3 covered by curl |
| [TODO.md](./TODO.md) | Backend TODO and status |
| [NEW-MODULE-RMP-AUGMENTATION.md](./NEW-MODULE-RMP-AUGMENTATION.md) | New module: 5 areas in 4 groups (Offline, i18n/audio, Learning, Collective intel) |
| [AC4-Routing-Identity-Design.md](./AC4-Routing-Identity-Design.md) | §4: G1–G3 implementation notes |
| [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) | §2: Guardrails; §1: HIPAA |
| [TESTING-Pipeline-curl.md](./TESTING-Pipeline-curl.md) | Curl tests; use same session_id for AC-3 re-test |
| [EKA-VALIDATION-RUNBOOK.md](./EKA-VALIDATION-RUNBOOK.md) | Eka E1–E5 (done; reference) |
| [agentcore-gateway-manual-steps.md](./agentcore-gateway-manual-steps.md) | Gateway setup; use `python3` for scripts |
| [GOOGLE-MAPS-ACCOUNT-SETUP.md](../infrastructure/GOOGLE-MAPS-ACCOUNT-SETUP.md) | Google Maps API key (done; reference) |

---

## Notes from this session

- **RMP Learning (Group C) done:** Backend complete. Frontend team owns Learning screen — see [RMP-LEARNING-API.md](../frontend/RMP-LEARNING-API.md). Next: new module A → B → D.
- **Test 4 (POST /hospitals with location) fixed:** RCA done; enrichment no longer calls get_hospitals a second time (uses only lat/lon from agent response). Deployed and re-tested → 200. See [API-TEST-RESULTS.md](./API-TEST-RESULTS.md) § Test 4 RCA. Next: new module when you return.
- **Gateway OAuth:** If setup script is run again and “Gateway already exists, reusing”, the script now updates the Gateway authorizer to the current OAuth so tokens from the secret work (avoids 401 Invalid Bearer token).
- **Route Lambda:** Uses scope from gateway-config secret (`client_info.scope`, e.g. `emergency-triage-hospitals/invoke`), MCP version `2025-03-26`, and http.client to call the Gateway so response body is always captured on 4xx.
- **Python:** Use `python3` in docs and CLI; `python` may not be on PATH (e.g. macOS).
