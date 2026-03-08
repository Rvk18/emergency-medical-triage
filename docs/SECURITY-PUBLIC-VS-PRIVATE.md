# Security: Public Web vs Private Backend

**Purpose:** Clarify what is “public” (reachable by anyone) vs “private” (only our services, no direct internet access), and how the web app stays secure while being public-facing.

---

## 1. What Is Public (Reachable by Anyone)

| Component | Public? | What “public” means |
|-----------|---------|----------------------|
| **Web app URL** (e.g. `https://xxx.cloudfront.net`) | ✅ Yes | Anyone with the link can open the app in a browser. They see the login page and static assets (HTML, JS, CSS). No secrets in the code — only logic and UI. |
| **API Gateway URL** (e.g. `https://xxx.execute-api.region.amazonaws.com/dev`) | ✅ Yes | The *URL* is reachable. Anyone can send an HTTP request to it from the internet. |

So both the **web app** and the **API** are “on the internet” in the sense that their URLs can be used from anywhere.

---

## 2. What Is Protected (Not Usable Without Auth)

| Component | How it’s protected |
|-----------|--------------------|
| **API Gateway – protected routes** (`/triage`, `/hospitals`, `/route`, `/rmp/learning/*`) | **Cognito authorizer.** Every request must include `Authorization: Bearer <Cognito Id Token>`. No token (or invalid/expired token) → **401 Unauthorized**. So only users who have logged in via our Cognito pool can call these endpoints. |
| **API Gateway – public routes** (`/health`, `/config`) | No auth by design. `/health` is liveness; `/config` returns non-secret config (e.g. Google Maps key, which is meant to be used client-side and restricted by domain in Google Cloud). |

So: **The web app is public (anyone can load it). The API is “public” only in the sense that its URL is reachable; actual use of triage/hospitals/route/learning is restricted to authenticated users.** No token ⇒ no data.

---

## 3. What Is Private (No Direct Internet Access)

These are **never** exposed to the internet. They are only used by our own AWS resources.

| Component | Why it’s private |
|-----------|-------------------|
| **Aurora PostgreSQL** | In a **private subnet**. No public IP. Only Lambdas (in our VPC) and allowed principals (e.g. IAM auth) can connect. Users and browsers cannot connect to Aurora. |
| **Lambdas** (Triage, Hospital Matcher, Route, RMP Learning, Config) | Invoked **only by API Gateway** (or other AWS services we control). No one can invoke them directly from the internet; they are not given a public URL. |
| **Bedrock AgentCore / MCP Gateway** | Used **only by our Lambdas**. Agents and gateway are not exposed to the internet; they are called server-side with IAM/OAuth we control. |
| **Secrets Manager** | Accessed **only by Lambdas** (and scripts with AWS credentials). No browser or public API can read secrets. |

So: **Aurora, Lambdas, agents, and secrets are private. Only API Gateway (and within it, Cognito) is the public entry point to “backend” functionality.**

---

## 4. CORS: What It Does and Doesn’t Do

- **CORS** is a **browser** rule. It says: “When a page from origin A (e.g. `https://our-app.cloudfront.net`) calls an API on origin B (e.g. `https://api.execute-api.region.amazonaws.com`), is that allowed?”
- **Our choice:** Allow **all origins** (`*`) so that:
  - Our web app (wherever it’s hosted — CloudFront, localhost, etc.) can call the API from the browser.
  - The web app stays **public-facing** (anyone can open the URL).

**Important:** CORS does **not** grant access to data. It only allows the browser to send the request. The API still:
- Returns **401** for `/triage`, `/hospitals`, `/route`, `/rmp/learning` if there is no valid Cognito token.
- Returns **200** only when the request includes a valid `Authorization: Bearer <token>`.

So: **“Allow all origins” for CORS = any site can *attempt* a request. Our API still enforces Cognito on protected routes. Aurora, Lambdas, and agents remain inaccessible from the internet.**

---

## 5. End-to-End Picture

```
[Anyone] → opens https://our-app.cloudfront.net
         → gets static files (HTML/JS/CSS) from CloudFront (S3). No secrets.

[User]   → logs in (email/password) → Cognito returns Id Token
         → token stored in browser (e.g. sessionStorage)

[Browser]→ calls API: GET /health, GET /config (no token needed)
         → calls API: POST /triage, POST /hospitals, POST /route with
            header: Authorization: Bearer <token>
         → API Gateway validates token → invokes Lambda → Lambda may call
            Aurora, Bedrock, MCP Gateway (all private). Response back to browser.

[Attacker]→ opens our web app URL → sees login page
          → without valid credentials, cannot get a token
          → if they call API without token → 401 on protected routes
          → cannot reach Aurora, Lambdas, or agents directly (no public URL)
```

---

## 6. Summary

| Question | Answer |
|----------|--------|
| Is the web app public? | Yes — anyone with the URL can load it. |
| Can anyone use our API to get triage/hospitals/route data? | No — only with a valid Cognito Id Token (i.e. after logging in). |
| Is CORS “allow all” a security risk for our data? | No — auth is enforced by Cognito at API Gateway; CORS only allows the browser to make the request. |
| Are Aurora, Lambdas, and agents public? | No — they are private; only API Gateway (and our Lambdas) talk to them. |
| So what is actually “public”? | The web app URL (static content) and the API Gateway URL (entry point). Everything else stays behind Cognito and IAM. |

This is the same security model you already have in the backend: **public entry points (web + API), private data and compute (Aurora, Lambdas, agents), and identity at the door (Cognito).**
