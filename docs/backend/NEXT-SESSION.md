# What to work on next (next session)

**Current sequence:**  
**1. New module (C first)** — RMP learning (Eka quiz + AgentCore scoring + gamification + leaderboard), then A → B → D → **2. AC-3 re-test** → **3. Web app deploy + frontend–backend integration** → **4. Comprehensive E2E testing** (web app + mobile app).  
See **[ROADMAP-NEXT.md](../ROADMAP-NEXT.md)** and **[NEW-MODULE-RMP-AUGMENTATION.md](./NEW-MODULE-RMP-AUGMENTATION.md)**.

**Already done:** ~~Redeploy AgentCore~~ ✅, ~~Policy~~ ✅, ~~HIPAA H1–H4~~ ✅, ~~Test 4 (POST /hospitals with location)~~ ✅, ~~RMP Learning (C first slice)~~ ✅.

---

## Phase 1: Redeploy AgentCore ✅ Done

Redeployed all three runtimes (Hospital Matcher, Triage + enable_eka_on_runtime, Routing). G3 safety prompts are live; Eka remains enabled on triage.

---

## Phases 2–4: Policy, HIPAA, AC-3

- **2. Policy:** ✅ Done. Policy engine on Gateway via [POLICY-RUNBOOK.md](./POLICY-RUNBOOK.md) and `scripts/setup_agentcore_policy.py`.
- **3. HIPAA (H1–H4):** ✅ Done. [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) §1, [HIPAA-Compliance-Checklist.md](./HIPAA-Compliance-Checklist.md).
- **4. AC-3 re-test:** Same `session_id` on triage and hospitals; [TESTING-Pipeline-curl.md](./TESTING-Pipeline-curl.md). **Do after the new module.**

---

## 1. New module (first — C then A → B → D)

**Scope:** ~~RMP learning first (Group C)~~ ✅ **First slice done:** Eka quiz (get_question + score_answer) + POST /rmp/learning deployed and tested. **Next:** Aurora rmp_scores/learning_answers, GET leaderboard, GET me, frontend; then Offline (A), Multi-language/audio (B), Collective intelligence (D). See **[NEW-MODULE-RMP-AUGMENTATION.md](./NEW-MODULE-RMP-AUGMENTATION.md)** §4–6.

| Order | Group | Content |
|-------|--------|--------|
| **1** | **C. RMP learning** | Eka quiz + AgentCore scoring + gamification + top scores; peer-to-peer later |
| 2 | A. Offline & resilience | Offline triage + cached hospital/routing; sync APIs |
| 3 | B. Multi-language & accessibility | Multi-language + audio for illiterate users |
| 4 | D. Collective intelligence | Every case improves the system for all providers |

**Start with C:** GET question (from Eka) → user answers → AgentCore scores → add points → leaderboard. Then A → B → D.

---

## 2. AC-3 re-test (session continuity)

Same `session_id` on triage and hospitals (and route if supported). Verify with curl or frontend. See [TESTING-Pipeline-curl.md](./TESTING-Pipeline-curl.md).

---

## Phase 5: Deploy web app + frontend integration

Deploy `frontend/web/` and wire it to the backend: API URL, Cognito auth, triage → hospitals → route flow, session_id. Full checklist: [ROADMAP-NEXT.md](../ROADMAP-NEXT.md) § Phase 5.

---

## Phase 6: Comprehensive E2E testing (web + mobile)

After web app deploy and integration, run end-to-end tests from both **frontend web app** and **mobile app** to confirm the full flow (triage → hospitals → route, auth, session_id) works. Document results and fix any issues.

---

## Key references

| Doc | Purpose |
|-----|--------|
| [ROADMAP-NEXT.md](../ROADMAP-NEXT.md) | Phases: New module → AC-3 → Web app → E2E testing |
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

- **RMP Learning (Group C first slice) done:** rmp_quiz_agent deployed (CreateAgentRuntime with agent_id null in yaml), Gateway enabled, Terraform apply created Lambda + POST /rmp/learning. get_question and score_answer return 200; first request may 504 (cold start), retry once. See [API-TEST-RESULTS.md](./API-TEST-RESULTS.md) § RMP Learning, [RMP-LEARNING-COMPLETE-RUNBOOK.md](./RMP-LEARNING-COMPLETE-RUNBOOK.md). Next: AC-3 re-test, then web app deploy, then E2E.
- **Test 4 (POST /hospitals with location) fixed:** RCA done; enrichment no longer calls get_hospitals a second time (uses only lat/lon from agent response). Deployed and re-tested → 200. See [API-TEST-RESULTS.md](./API-TEST-RESULTS.md) § Test 4 RCA. Next: new module when you return.
- **Gateway OAuth:** If setup script is run again and “Gateway already exists, reusing”, the script now updates the Gateway authorizer to the current OAuth so tokens from the secret work (avoids 401 Invalid Bearer token).
- **Route Lambda:** Uses scope from gateway-config secret (`client_info.scope`, e.g. `emergency-triage-hospitals/invoke`), MCP version `2025-03-26`, and http.client to call the Gateway so response body is always captured on 4xx.
- **Python:** Use `python3` in docs and CLI; `python` may not be on PATH (e.g. macOS).
