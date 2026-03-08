# E2E Testing and Benchmarking

**Purpose:** Define scope and approach for end-to-end (E2E) tests and for a benchmarking document to accompany the submission. Aligns with [WEB-BACKEND-INTEGRATION-PLAN.md](WEB-BACKEND-INTEGRATION-PLAN.md).

---

## 1. E2E Testing

### Goals

- Automate critical user flows so regressions are caught before release.
- Support submission with evidence that the web app works against the real backend (or mock).
- Run locally and, optionally, in CI (with secrets for test user).

### Recommended Tool

- **Playwright** (Node.js): cross-browser, headless, good for SPAs and API mocking. Alternative: **Cypress**.

### Scope (MVP)

| # | Flow | Description | Priority |
|---|------|-------------|----------|
| 1 | **Smoke** | Load web app URL; expect no crash; login page or dashboard visible. | P0 |
| 2 | **Login** | Enter test credentials; submit; expect redirect to dashboard or triage. | P0 |
| 3 | **Triage (mock or real)** | Fill triage form (symptoms, vitals); submit; expect severity and recommendations displayed. | P0 |
| 4 | **Hospitals** | After triage (or with mock severity); request hospitals; expect list with at least one hospital. | P0 |
| 5 | **Route** | Call get directions (origin/destination); expect distance_km or directions_url (or mock). | P1 |
| 6 | **Admin dashboard** | Load admin view; expect patient list and hospital status (mock data). | P1 |

### Test User and Env

- Use a **dedicated Cognito test user** (e.g. `e2e-test@example.com`). Store credentials in env (e.g. `E2E_USER_EMAIL`, `E2E_USER_PASSWORD`) or in CI secrets; **never commit** passwords.
- **Base URL:** `VITE_APP_URL` or `BASE_URL` (localhost for dev, CloudFront URL for staging).
- **API:** Same as frontend (`VITE_API_URL`); tests run against real API when not using mocks.

### Where to Add Tests

- **Suggested path:** `frontend/web/e2e/` or `e2e/` at repo root.
- **Config:** `playwright.config.ts` with `baseURL`, `timeout`, `retries`; optionally `projects` for local vs CI.

### CI (Optional)

- GitHub Actions (or similar): run E2E on push/PR. Store `E2E_USER_EMAIL`, `E2E_USER_PASSWORD`, `VITE_API_URL`, `VITE_APP_URL` in repo secrets. Build web app with same env, serve or deploy to a test URL, then run Playwright.

### Deliverables

- [ ] Playwright (or Cypress) project under `e2e/` or `frontend/web/e2e/`.
- [ ] At least: smoke, login, triage, hospitals (P0).
- [ ] README or CONTRIBUTING note: how to run E2E locally and required env vars.
- [ ] Optional: CI workflow that runs E2E.

---

## 2. Benchmarking Document

### Goals

- Provide reviewers with a short, readable summary of **what was measured** and **how the system performs** (e.g. latency, throughput, or key user flows).
- Keep it factual and reproducible (tool, environment, steps).

### Suggested Sections

1. **Overview**
   - What is benchmarked: e.g. “API latency for triage and hospital match,” “E2E time for triage → hospitals → route,” “AgentCore runtime latency.”
   - Environment: region, stage (dev), cold vs warm Lambda, etc.

2. **Method**
   - Tool: e.g. curl + timing, Postman, k6, or Playwright (E2E timing).
   - Sample size: e.g. N requests per endpoint or N E2E runs.
   - How: e.g. “Sequential POST /triage with fixed payload; median and p95 latency.”

3. **Results**
   - Table or chart: endpoint (or flow) vs median / p95 / p99 latency (ms).
   - Optional: success rate, error rate.
   - Example:

     | Endpoint / Flow        | Median (ms) | p95 (ms) | Notes        |
     |------------------------|------------|----------|--------------|
     | GET /health            | 45         | 120      | No auth      |
     | POST /triage           | 3200       | 5500     | AgentCore    |
     | POST /hospitals        | 2100       | 4000     | AgentCore    |
     | POST /route            | 800        | 1500     | Gateway maps |
     | E2E: login→triage→hospitals | 8500  | 12000    | Browser      |

4. **Limitations**
   - E.g. dev stage, single region, no load test; AgentCore non-deterministic; cold start included.

5. **How to Reproduce**
   - Steps: e.g. “Run `scripts/benchmark_triage.sh`” or “Use k6 script in `e2e/load/` with `VITE_API_URL` and Cognito token.”

### Deliverables

- [ ] **BENCHMARKING.md** (or **docs/BENCHMARKING.md**) with the sections above, filled with real or placeholder numbers and clear “How to reproduce.”
- [ ] Optional: a small script or config (e.g. k6, or curl loop) that generates the numbers used in the doc.

---

## 3. Quick Reference

| Item | Location / Command |
|------|--------------------|
| E2E tests | `e2e/` or `frontend/web/e2e/` (to be added) |
| Run E2E | `npm run e2e` or `npx playwright test` (after setup) |
| Benchmarking doc | `docs/BENCHMARKING.md` (to be added) |
| API token for scripts | `scripts/get_rmp_token.py` (Cognito test user) |

---

## 4. Next Steps

1. Add Playwright (or Cypress) and implement P0 E2E tests (smoke, login, triage, hospitals).
2. Add optional P1 (route, admin dashboard).
3. Create **BENCHMARKING.md** with method, results table, and reproduction steps.
4. Optionally add a small benchmark script and wire E2E into CI.
