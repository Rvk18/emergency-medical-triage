# Web App ↔ Backend Integration & AWS Deploy — Plan

**Purpose:** Single source of truth for what’s done, what’s pending, and how to integrate the webapp with the backend and deploy on AWS. Use this for login config, auth flow, hosting choice, and E2E testing.

**Decisions (locked in):**
- **Admin dashboard:** Mock data only; showcase USP and functionality, not real data.
- **Mobile:** Provide Android APK (e.g. Google Drive link) in addition to web MVP link.
- **CORS:** Allow all origins (`*`) so the public-facing web app can call the API; backend remains protected by Cognito. See [SECURITY-PUBLIC-VS-PRIVATE.md](SECURITY-PUBLIC-VS-PRIVATE.md).
- **Hosting:** Terraform S3 + CloudFront from the start (scaling, security, single apply). Build and upload: `npm run build` then `aws s3 sync dist/ s3://WEB_APP_BUCKET --delete`.
- **E2E & benchmarking:** E2E tests (e.g. Playwright) plus a benchmarking document. See [E2E-AND-BENCHMARKING.md](E2E-AND-BENCHMARKING.md).

---

## 1. Stock: What Is Implemented

### Backend (API)

| Item | Status | Notes |
|------|--------|--------|
| **API Gateway** | ✅ | REST API, stage `dev`, Cognito authorizer on all except `/health` and `/config`. |
| **Endpoints** | ✅ | `GET /health`, `POST /triage`, `POST /hospitals`, `POST /route`, `POST /rmp/learning`, `GET /rmp/learning/me`, `GET /rmp/learning/leaderboard`, `GET /config`. |
| **Cognito** | ✅ | User Pool + app client; API Gateway uses Id Token in `Authorization: Bearer <token>`. |
| **Lambdas** | ✅ | Health, Triage, Hospital Matcher, Route, RMP Learning, Config (Google Maps key from Secrets Manager). |
| **Config API** | ✅ | `GET /config` (no auth) returns `google_maps_api_key`, `environment`. |
| **Secrets** | ✅ | api_config, gateway-config, rds-config, bedrock-config, rmp-test-credentials; optional google_maps_config. |
| **CORS** | ✅ | API Gateway Gateway Responses (4XX, 5XX, UNAUTHORIZED, ACCESS_DENIED) + CORS headers in all Lambda responses. Allow all origins. |

### Web App (frontend/web)

| Item | Status | Notes |
|------|--------|--------|
| **Stack** | ✅ | Vite, Vanilla JS + some React/TS, Tailwind, AWS Amplify (auth). |
| **Auth (Cognito)** | ✅ | `utils/auth.js`: Amplify, signIn, getIdToken, logout, getCurrentUser, refreshSession. Login page, profile dropdown. |
| **Env** | ✅ | `VITE_API_URL`, `VITE_USE_MOCK_API`, `VITE_GOOGLE_MAPS_API_KEY`; README also documents `VITE_COGNITO_*`. |
| **Config service** | ✅ | `services/config.js`: fetches `GET /config` for Google Maps key (with fallback). |
| **API – Admin** | ✅ | `services/admin-api.js`: uses `sessionStorage.idToken`, sends `Authorization: Bearer` on all admin calls. |
| **API – Triage / Hospitals** | ✅ | `api.js` sends `Authorization: Bearer` via `getAuthHeaders()`; `getRoute()` added. |
| **API – Route** | ✅ | `getRoute()` in `api.js` calls `POST /route` with auth. |
| **Pages** | ✅ | Login, Admin dashboard, Triage wizard, Hospital match, RMP dashboard, Analytics, etc. (many use mock). |
| **Router** | ✅ | Hash router; post-login redirect to admin. |
| **.env.example** | ⚠️ | Has `VITE_API_URL`, `VITE_GOOGLE_MAPS_API_KEY`; **Cognito vars** (`VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`, `VITE_COGNITO_REGION`) are in README but not in `.env.example` (easy to miss). |

### Infrastructure

| Item | Status | Notes |
|------|--------|--------|
| **Terraform** | ✅ | API Gateway, Lambdas, Cognito, Aurora, Secrets Manager, S3 (general bucket). |
| **S3** | ✅ | General bucket (existing); **web app bucket** (`*-web-*`) + CloudFront in Terraform. |
| **CloudFront** | ✅ | `web_hosting.tf`: distribution, OAC, SPA error pages. Outputs: `web_app_url`, `web_app_bucket_name`. |

### E2E Testing

| Item | Status | Notes |
|------|--------|--------|
| **E2E / Playwright / Cypress** | ❌ | No E2E tests in repo. |
| **Manual test docs** | ✅ | ADMIN-QUICK-START, IMPLEMENTATION-STATUS, curl/Postman flows in backend docs. |

---

## 2. What Is Pending (Gaps)

1. **Web → Backend auth**
   - **api.js** does not send `Authorization: Bearer <idToken>` on `performTriage`, `matchHospitals`, or any future `getRoute`. So after login, triage/hospitals (and route) calls get **401** from API Gateway.
   - **Fix:** Add a shared helper that returns headers with Id Token (or null if not logged in) and use it in all `api.js` (and any route) calls. Use the same pattern as `admin-api.js`.

2. **Route API in frontend**
   - Backend has `POST /route`; frontend has no `getRoute()` or equivalent in `api.js`. Directions flow cannot hit the real API until this is added.
   - **Fix:** Add `getRoute(body)` in `api.js` calling `POST /route` with `Authorization` header (and optional session_id if backend expects it).

3. **CORS**
   - Only Config Lambda returns CORS. For browser requests from the web app origin (localhost or Amplify/CloudFront URL), API Gateway must either:
     - Add CORS via **API Gateway Gateway Responses** (recommended), or
     - Have each Lambda return `Access-Control-Allow-Origin` (and related headers) in every response.
   - **Fix:** Prefer API Gateway CORS (OPTIONS + response headers) so all endpoints behave consistently.

4. **Login / credentials configuration**
   - **Cognito:** User Pool ID and App Client ID must be in `.env` (e.g. `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`, `VITE_COGNITO_REGION`). Get from Terraform: `terraform output cognito_user_pool_id`, `cognito_app_client_id`.
   - **Test user:** Create in Cognito (Console or `aws cognito-idp admin-create-user`) and optionally store in Secrets Manager for scripts; frontend uses same pool for login.
   - **Fix:** Add Cognito vars to `.env.example` and document “run `terraform output` and create a test user”.

5. **Hosting the web app**
   - Current S3 bucket is not set up for static website hosting; no CloudFront.
   - **Options (from MVP-DEPLOY-RUNBOOK):**
     - **A) AWS Amplify** — Connect repo, root `frontend/web`, build `npm ci && npm run build`, output `dist`, set env vars (API URL, Cognito, optional Google Maps key). Easiest for “one URL that works.”
     - **B) S3 + CloudFront** — New or existing bucket with static website hosting (or origin), CloudFront distribution, build with correct `VITE_*` at build time. More control, more Terraform/ops.
     - **C) Vercel / Netlify** — Same idea: connect repo, set env, deploy. Ensure API Gateway CORS allows that origin.
   - **Recommendation:** Start with **Amplify** for speed; add Terraform for S3+CloudFront later if you want everything in code.

6. **E2E testing**
   - No automated E2E tests yet.
   - **Fix:** Add a minimal E2E suite (e.g. Playwright or Cypress) that: (1) opens app, (2) optionally logs in (or uses mock), (3) runs triage → hospitals → route (or at least triage → hospitals) and asserts on visible result. Run in CI or locally before release.

---

## 3. What Needs to Be Done (Ordered)

| # | Task | Owner | Notes |
|---|------|--------|--------|
| 1 | Add **Authorization** header to all backend calls in `api.js` (triage, hospitals, and later route) using Id Token from auth.js. | Dev | Required for real API after login. |
| 2 | Add **POST /route** in `api.js` (e.g. `getRoute({ origin_lat, origin_lon, dest_lat, dest_lon }` or address-based) and use it in the directions/navigation flow. | Dev | Match backend contract from openapi.yaml. |
| 3 | Add **CORS** for API Gateway (Gateway Responses or Lambda headers) so browser allows requests from web app origin. | Infra / Dev | Needed for both localhost and deployed URL. |
| 4 | Update **.env.example** with `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`, `VITE_COGNITO_REGION`. | Dev | Reduces “login not working” setup issues. |
| 5 | Document **login credentials**: get Cognito IDs from Terraform, create test user, set env. | Docs | Short “Configure Login” section in ADMIN-QUICK-START or SETUP. |
| 6 | **Deploy web app** (Amplify or S3+CloudFront), set production env vars, use deployed URL as Working MVP link. | Ops | See MVP-DEPLOY-RUNBOOK. |
| 7 | **E2E tests**: add Playwright/Cypress (or similar), at least login + triage → hospitals (and route if UI exists). | QA / Dev | Run in CI or pre-release. |

---

## 4. Best Way to Host the Web App

- **Chosen: S3 + CloudFront (Terraform).**
  - **infrastructure/web_hosting.tf:** Dedicated S3 bucket for web app (private), CloudFront with OAC, default root `index.html`, SPA error pages (403/404 → index.html). Outputs: `web_app_url`, `web_app_bucket_name`.
  - **Deploy:** From repo root: `cd frontend/web && npm run build`. Then: `aws s3 sync dist/ s3://$(terraform -chdir=infrastructure output -raw web_app_bucket_name) --delete`. Invalidate CloudFront cache if needed: `aws cloudfront create-invalidation --distribution-id ID --paths "/*"`.
  - **Env at build time:** Set `VITE_API_URL`, `VITE_COGNITO_*`, etc. when running `npm run build` (e.g. in CI or locally before sync).
- **Security:** Web app URL is public; API and data remain protected by Cognito and private resources. See [SECURITY-PUBLIC-VS-PRIVATE.md](SECURITY-PUBLIC-VS-PRIVATE.md).

---

## 5. Configure Login Credentials

1. **Get Cognito IDs**
   - From repo root: `cd infrastructure && terraform output cognito_user_pool_id cognito_app_client_id`
   - Or from AWS Console: Cognito → User Pools → your pool → User pool ID; App integration → App client ID.

2. **Create a test user**
   - Console: Cognito → User Pools → Users → Create user (email, temporary password).
   - CLI: `aws cognito-idp admin-create-user --user-pool-id <id> --username admin@example.com --user-attributes Name=email,Value=admin@example.com Name=email_verified,Value=true --temporary-password "TempPass123!"`

3. **Frontend .env**
   - Copy `.env.example` to `.env`.
   - Set:
     - `VITE_API_URL=https://<api-id>.execute-api.<region>.amazonaws.com/dev`
     - `VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxx`
     - `VITE_COGNITO_CLIENT_ID=xxxxx`
     - `VITE_COGNITO_REGION=us-east-1`
   - Optional: `VITE_GOOGLE_MAPS_API_KEY` (or rely on GET /config).
   - For local dev without backend: `VITE_USE_MOCK_API=true`.

4. **Amplify (production)**
   - In Amplify Console → App → Environment variables, add the same keys (with production API URL and Cognito if different).

---

## 6. Auth Flow (E2E)

1. User opens web app (localhost or deployed URL).
2. If not logged in, router shows **Login**; user enters email/password.
3. **auth.js** calls Amplify `signIn` → Cognito returns tokens; app stores `idToken` (and accessToken) in sessionStorage, user in localStorage.
4. Router redirects to **Admin** (or triage, depending on product choice).
5. On every **API call** (triage, hospitals, route, admin):
   - Read `idToken` from sessionStorage (e.g. via `getIdToken()`).
   - Set header `Authorization: Bearer <idToken>`.
   - If 401, optionally call `refreshSession()` and retry once; if still 401, redirect to login.
6. **Logout:** Amplify signOut, clear sessionStorage/localStorage, redirect to login.

**Current gap:** Steps 5–6 are implemented in `admin-api.js` but **not** in `api.js` (triage/hospitals/route). Fix: centralize “headers with auth” and use in `api.js`.

---

## 7. E2E Testing for Web App

- **Goal:** Automate: load app → (optional) login → perform triage → get hospitals → (optional) get route → assert on visible outcome.
- **Options:**
  - **Playwright:** Good for cross-browser, headless in CI. Example: open app, fill triage form, submit, expect severity and hospital list in DOM.
  - **Cypress:** Similar; many teams use it for SPAs.
- **Suggested scope for MVP:**
  1. Smoke: load `/`, expect no crash and login or dashboard visible.
  2. With mock API: run triage flow, assert severity and recommendations shown.
  3. With real API (or test env): login with test user, run triage → hospitals, assert 200 and data shown.
  4. Optional: route flow if UI and API are wired.
- **Credentials in E2E:** Use a dedicated test user and either (a) env vars for email/password, or (b) mock auth / bypass for some tests. Do not commit real passwords.

---

## 8. Quick Reference

| Need | Where |
|------|--------|
| API base URL | `terraform output api_gateway_url` (infrastructure/) or `scripts/load_api_config.py` |
| Cognito IDs | `terraform output cognito_user_pool_id cognito_app_client_id` |
| Web app code | `frontend/web/` |
| Build web app | `cd frontend/web && npm ci && npm run build` → `dist/` |
| Deploy & manual test | [DEPLOY-WEBAPP-MANUAL-TEST.md](DEPLOY-WEBAPP-MANUAL-TEST.md) — Terraform, create Cognito user, .env, build, upload, test |
| Deploy options | [MVP-DEPLOY-RUNBOOK.md](MVP-DEPLOY-RUNBOOK.md) |
| Backend API spec | [openapi.yaml](openapi.yaml) |
| Auth (frontend) | `frontend/web/src/utils/auth.js`, `services/admin-api.js`, `api.js` (getAuthHeaders) |
| Security (public vs private) | [SECURITY-PUBLIC-VS-PRIVATE.md](SECURITY-PUBLIC-VS-PRIVATE.md) |

---

## 9. Next Steps (Recommended Order)

1. **Implement:** Add auth headers and route API in `api.js` (see §3).
2. **Implement:** Add CORS to API Gateway (or Lambda responses).
3. **Docs:** Update `.env.example` and “Configure Login” in ADMIN-QUICK-START or SETUP.
4. **Terraform apply** to create web bucket + CloudFront and CORS. Build frontend with env vars and upload `dist/` to `web_app_bucket_name`.
5. **APK:** Build Android release APK; upload to Google Drive; add link to submission.
6. **E2E:** Add Playwright (or Cypress) suite and benchmarking document per E2E-AND-BENCHMARKING.md.
7. **Manual test:** Login, triage, hospitals, route; confirm admin dashboard (mock) and web URL public.

Once these are done, the web app is integrated with the backend and deployable on AWS with a clear auth and E2E story.
