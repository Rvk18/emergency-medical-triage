# Roadmap: Next phases

**Priority order:** **New module A → B → D** (next) → **Web app deploy** (last) → **E2E testing** (last).  
**RMP Learning (C) backend is complete;** frontend team owns the Learning screen — see [RMP-LEARNING-API.md](frontend/RMP-LEARNING-API.md) for instructions.  
**AC-3 session continuity** is covered by comprehensive curl tests ([API-TEST-RESULTS.md](backend/API-TEST-RESULTS.md)); no separate phase.

---

## New module — next priority: A then B then D

**Goal:** Implement the remaining capability areas. **Group C (RMP learning) backend is done;** frontend team implements the Learning screen per [RMP-LEARNING-API.md](frontend/RMP-LEARNING-API.md). **Next:** A → B → D. Full scope: [NEW-MODULE-RMP-AUGMENTATION.md](backend/NEW-MODULE-RMP-AUGMENTATION.md).

| Order | Group | What |
|-------|--------|------|
| **1** | **A. Offline & resilience** | Offline triage + cached hospitals/routing; sync APIs (`/sync/upload`, `/sync/download`) |
| 2 | **B. Multi-language & accessibility** | Language + audio (e.g. TTS) for illiterate users |
| 3 | **C. RMP learning** | ✅ Backend done. Frontend team: Learning screen per [RMP-LEARNING-API.md](frontend/RMP-LEARNING-API.md). |
| 4 | **D. Collective intelligence** | Outcome aggregation; system improves from every case |

**Next priority:** Start with **A** (Offline & resilience), then **B** (Multi-language), then **D** (Collective intelligence). Web app deploy and E2E testing are **last**.

---

## Phase 1: Redeploy AgentCore (G3 prompts live) ✅ Done

**Goal:** Get the updated G3 safety prompts (refusal, “do not prescribe”) running on all three AgentCore runtimes.

**Status:** Completed. All three runtimes redeployed (Hospital Matcher, Triage + enable_eka_on_runtime, Routing). Tfvars verified; no ARN changes needed for Hospital Matcher or Routing.

**Steps:** See [agentcore/README.md](../agentcore/README.md) § **Redeploy AgentCore**.

- Deploy Hospital Matcher runtime (`hospital_matcher_agent.py`).
- Deploy Triage runtime (`triage_agent.py`), then run `python3 scripts/enable_eka_on_runtime.py` so Eka stays enabled.
- Deploy Routing runtime (`routing_agent.py`).
- Update tfvars if any ARN changed; `terraform apply` if needed.
- Quick verify: triage + hospitals curl; Eka test (Indian paracetamol brands).

---

## Phase 2: Policy (AgentCore Policy is GA) ✅ Done

**Goal:** Restrict which tools can be called through the Gateway; principle of least privilege.

**Status:** Implemented. A policy engine is created and attached to the Gateway.

**Steps (already done):**
- Run `python3 scripts/setup_agentcore_policy.py` after Gateway setup. This creates the policy engine, adds a Cedar permit policy that allows only the whitelisted tools (get_hospitals, Eka tools, get_route, get_directions, geocode_address), and attaches the engine to the Gateway in ENFORCE mode.
- **Runbook:** [POLICY-RUNBOOK.md](backend/POLICY-RUNBOOK.md) — allowlist, how to update, and optional per-runtime restriction with separate OAuth clients.
- See [AC4-Routing-Identity-Design.md](backend/AC4-Routing-Identity-Design.md) §4.

---

## Phase 3: HIPAA / compliance (H1–H4)

**Goal:** Document and harden for health data (PHI scope, encryption, access, audit).

**Steps:** See [ROADMAP-after-AC4.md](backend/ROADMAP-after-AC4.md) §1 and **[HIPAA-Compliance-Checklist.md](backend/HIPAA-Compliance-Checklist.md)** (H1–H4).

| # | Item | Action |
|---|------|--------|
| H1 | Document PHI scope | List what we store (symptoms, vitals, triage result, session/patient ids); classify as PHI/sensitive. |
| H2 | Encryption checklist | Confirm Aurora encryption at rest, TLS in transit, Secrets Manager; document. |
| H3 | Access control | IAM least privilege; no PHI in logs; restrict who can read api_config / gateway-config / eka. |
| H4 | Audit logging | Document request_id, triage_assessments.id, CloudWatch; add who-accessed-what if required. |

---

## Phase 4: AC-3 session continuity

**Status:** **Covered by comprehensive curl tests.** No separate re-test phase. When you run the full curl suite in [API-TEST-RESULTS.md](backend/API-TEST-RESULTS.md) (triage → hospitals → route, optionally with the same `session_id`), session continuity is exercised. See [TESTING-Pipeline-curl.md](backend/TESTING-Pipeline-curl.md) for pipeline curl.

---

## Phase 5: Deploy web app + frontend–backend integration **(last)**

**Goal:** Deploy the web dashboard (MedTriage) and wire it to the backend APIs. **Do this after** new modules A → B → D.

**Backend (already in place):**

- API base URL from Secrets Manager (`eval $(python3 scripts/load_api_config.py --exports)` → `API_URL`).
- RMP auth: Cognito Id Token; see [RMP-AUTH.md](frontend/RMP-AUTH.md).
- Endpoints: GET /health, POST /triage, POST /hospitals, POST /route. See [API-Integration-Guide.md](frontend/API-Integration-Guide.md).

**Frontend (web app):**

- **Location:** `frontend/web/` (Next.js / Vite, TypeScript). See [frontend/web/README.md](../frontend/web/README.md).
- **Integration checklist:**
  1. **Config:** Set API base URL (from env or build-time config). Use same value as `API_URL` from load_api_config (or Terraform output).
  2. **Auth:** Implement Cognito sign-in; get Id Token and send `Authorization: Bearer <IdToken>` on every POST to triage, hospitals, route. See [RMP-AUTH.md](frontend/RMP-AUTH.md).
  3. **Flow:** Implement triage form → POST /triage → show severity + recommendations; then hospital step → POST /hospitals with severity + recommendations + optional patient location; then route step → POST /route with origin/destination → show distance_km, duration_minutes, directions_url (open in Google Maps).
  4. **Session:** Generate one `session_id` (UUID) at flow start; send it in triage and hospitals (and route if supported) for AC-3 memory continuity. See [triage-api-contract.md](frontend/triage-api-contract.md).
  5. **Error handling:** 401 → refresh token or re-login; 400 → show validation message; 500 → generic error.
- **Deploy:** Build and host the web app (e.g. Vercel, S3+CloudFront, or your chosen host). Ensure CORS allows your API Gateway origin if needed; use the same API base URL in production.

**References:**

- [API-Integration-Guide.md](frontend/API-Integration-Guide.md) – Base URL, auth, endpoints, flow.
- [triage-api-contract.md](frontend/triage-api-contract.md) – Triage request/response, session_id, Eka behavior.
- [RMP-AUTH.md](frontend/RMP-AUTH.md) – Cognito sign-in and Id Token.

---

## Phase 6: Comprehensive E2E testing (web + mobile) **(last)**

**Goal:** Confirm the full flow works end-to-end from both the **web app** and **mobile app**. **Do this after** web app deploy (Phase 5).

**Steps:**

1. From **frontend web app:** Sign in (Cognito), run triage → hospitals → route with one session_id; verify responses, directions_url, and any errors.
2. From **mobile app:** Same flow; verify API URL, auth, and triage → hospitals → route.
3. Document results (pass/fail per client and endpoint); fix any issues.
4. Treat as done when both web and mobile complete the flow successfully against the live backend.

---

## Summary

| Phase | What | Done when |
|-------|------|-----------|
| **New module** | **A → B → D next.** C (RMP Learning) backend done; frontend team: [RMP-LEARNING-API.md](frontend/RMP-LEARNING-API.md). | A, B, D implemented per [NEW-MODULE-RMP-AUGMENTATION.md](backend/NEW-MODULE-RMP-AUGMENTATION.md). |
| 1 | Redeploy AgentCore (all 3 runtimes + enable_eka_on_runtime) | ✅ G3 prompts live; Eka still on triage. |
| 2 | Policy (GA) | ✅ Policy engine on Gateway via `scripts/setup_agentcore_policy.py`; see [POLICY-RUNBOOK.md](backend/POLICY-RUNBOOK.md). |
| 3 | HIPAA H1–H4 | ✅ PHI scope, encryption, access, audit documented. See [HIPAA-Compliance-Checklist.md](backend/HIPAA-Compliance-Checklist.md). |
| 4 | AC-3 session continuity | ✅ Covered by comprehensive curl tests ([API-TEST-RESULTS.md](backend/API-TEST-RESULTS.md)); no separate phase. |
| 5 | Web app deploy + frontend integration | **Last.** App deployed; API_URL, Cognito, triage → hospitals → route; session_id. |
| 6 | Comprehensive E2E testing (web + mobile) | **Last.** Web and mobile complete full flow; results documented.
