# Talking Points — Emergency Medical Triage

**Use this document as your speaking reference.** Bullet points are short phrases you can glance at while presenting. Order follows a natural pitch flow: problem → solution → architecture → apps → demo → close.

---

## 1. Problem

- In rural India, **68% of healthcare providers are unqualified RMPs** — no formal training.
- They serve **70% of the population**.
- In emergencies they lack:
  - Reliable **severity assessment**
  - Knowledge of which **hospitals** have the right capacity and specialists
  - Access to **Indian drug brands and treatment protocols** at point of care
- They need to make safe triage decisions in the **“golden hour.”**

---

## 2. Our USP (Solution)

- We **augment RMPs**, not replace them.
- **AI triage** with **Eka Care** — Indian medications and treatment protocols in recommendations.
- **Hospital matching** — real-time capability and capacity (get_hospitals).
- **Intelligent routing** — real driving distance, duration, **Google Maps** turn-by-turn directions.
- **RMP Learning** — quiz (get question → submit answer → points) and **leaderboard** for skill building.
- **Single-session flow** — triage → hospitals → route with optional `session_id`.
- **One backend**, **web + Android** clients.

---

## 3. Architecture — Entry & Backend

- **Single entry:** **API Gateway** with **Cognito** sign-in.
- **Lambdas:** Health, Triage, Hospital Matcher, Route, RMP Learning.
- **AI:** **Amazon Bedrock** + **Bedrock AgentCore** — **four runtimes**: Triage, Hospital Matcher, Routing, RMP Quiz.
- **Triage runtime** → wired to **Eka Care** via **MCP Gateway** — Indian brands and protocol-style steps in recommendations.
- **Hospital Matcher** → **get_hospitals** tool.
- **Routing** → **Google Maps** (distance, duration, directions URL).
- **Data:** **Aurora PostgreSQL** — triage assessments, learning scores, leaderboard.
- **Infra:** **Terraform** — Lambda, API Gateway, Cognito, Aurora, Gateway Lambdas (Eka, maps).

---

## 4. Architecture — Flow & Guardrails

- **Flow:** Triage → AgentCore Triage (+ Eka when needed) → severity & recommendations. Hospitals → AgentCore Hospital Matcher → get_hospitals → optional distance/directions per hospital. Route → Gateway maps Lambda → Google Maps → directions URL. RMP Learning → AgentCore RMP Quiz + Aurora (points, leaderboard).
- **Session:** `session_id` keeps one patient’s triage, hospitals, and route in one session.
- **Guardrails:** Input/output validation; safety prompts (“do not prescribe,” “emergency triage only”); **AgentCore policy** on Gateway — only whitelisted tools.

---

## 5. Security & Config

- Only **health** and **config** are public; all other endpoints require **Cognito Id Token**.
- **Secrets Manager** for API keys and config — **no secrets in the frontend**.
- Map key served from backend **GET /config**.

---

## 6. Web App

- **Vite**-based dashboard.
- **Cognito** login → triage (symptoms, vitals) → severity & recommendations (Eka when relevant) → hospital list → route with **Google Maps** link.
- **Admin view** with live map (patients, hospitals).
- Hosted on **S3 + CloudFront**; map key from backend.

---

## 7. Mobile App

- **Android** — **Kotlin**, **Jetpack Compose**.
- Same APIs: triage, hospitals, route, RMP Learning.
- **Cognito Id Token** in **Authorization: Bearer** header on every request.
- Same backend; mobile for **field use**, web for desktop/admin.

---

## 8. Demo Flow (if you demo)

- Sign in (Cognito).
- Enter symptoms — e.g. “fever, patient wants Indian paracetamol brands.”
- Get **severity** and **recommendations** (Indian brands, protocol steps).
- Get **hospital list**; pick one.
- Get **route** — distance, duration, **Google Maps** link.
- Optional: **RMP Learning** — get question → submit answer → points → leaderboard.

---

## 9. Optional — Cost & Closing

- **Cost:** ~**$110–200/month** (dev/low traffic) — NAT, Aurora Serverless, Bedrock.
- **Closing:** We’re helping rural RMPs with **AI triage**, **Eka** (Indian drugs & protocols), **hospital matching**, and **real routing** — **web and Android**, one backend. Thank you.

---

## One-liners (quick reference)

| Topic        | One-liner |
|-------------|-----------|
| **Problem** | 68% RMPs, 70% population; lack severity assessment, hospital knowledge, Indian drug/protocol access. |
| **USP**     | Augment RMPs: AI triage + Eka + hospital matching + Google Maps + RMP Learning; one backend, web + Android. |
| **Architecture** | API Gateway + Cognito → Lambdas → Bedrock AgentCore (4 runtimes) → MCP Gateway → Eka, get_hospitals, Google Maps; Aurora; Secrets Manager. |
| **Web**     | Vite dashboard, S3 + CloudFront, triage → hospitals → route + admin map. |
| **Mobile**  | Android, Kotlin + Compose, same APIs with Cognito Id Token. |
