# 3-minute pitch script — Architecture & USP first, Web & Mobile you manage

**Structure:** Important things (Architecture + USP) in the **first ~2 minutes**. Web app and mobile app in the **last ~1 minute** — short bullets for you to expand. Speak at a relaxed pace (~140 words/min). Total ~420 words ≈ 3 min.

---

## [0:00–0:35] Problem and USP

In rural India, **68% of healthcare providers are unqualified RMPs** — no formal training — yet they serve **70% of the population**. In emergencies they lack reliable severity assessment, don’t know which hospitals have the right capacity or specialists, and don’t have **Indian drug brands and treatment protocols** at point of care. **Our USP:** we **augment** RMPs, not replace them — AI triage with **Eka Care** (Indian medications and protocols), hospital matching, **real Google Maps routing**, and **RMP Learning** (quiz + leaderboard) so they can make safer decisions in the golden hour.

---

## [0:35–1:25] Architecture — the important bits

**Single entry:** RMPs hit **API Gateway** with **Cognito** sign-in. **Lambda** functions handle triage, hospital matching, routing, and RMP Learning.

**AI layer:** Everything runs on **Amazon Bedrock** and **Bedrock AgentCore** — we have **four runtimes**: Triage, Hospital Matcher, Routing, and RMP Quiz. The **Triage** runtime is wired to **Eka Care** via an **MCP Gateway**: when an RMP asks for “Indian paracetamol brands” or “fever protocol,” recommendations include real Indian brands and protocol-style steps. **Hospital Matcher** uses a **get_hospitals** tool; **routing** uses **Google Maps** for distance, duration, and turn-by-turn directions. We persist triage and learning scores in **Aurora PostgreSQL**. **Security:** only health and config are public; all other endpoints require a Cognito Id Token. API keys and config live in **Secrets Manager** — nothing in the frontend. **Infra:** Terraform — Lambda, API Gateway, Cognito, Aurora, Gateway Lambdas for Eka and maps.

---

## [1:25–2:00] Architecture — flow and guardrails

**Flow:** Triage → AgentCore Triage runtime → Eka tools when needed → severity and recommendations. Hospitals → AgentCore Hospital Matcher → get_hospitals → optional distance/directions per hospital. Route → Gateway maps Lambda → Google Maps → directions URL. RMP Learning → AgentCore RMP Quiz + Aurora for points and leaderboard. We use **session_id** so one patient’s triage, hospitals, and route stay in one session. **Guardrails:** input and output validation, safety prompts (“do not prescribe,” “emergency triage only”), and an AgentCore **policy** on the Gateway so only whitelisted tools can be called.

---

## [2:00–2:35] Web app — you manage

- **Web app:** Vite-based dashboard; Cognito login; triage (symptoms, vitals) → severity and recommendations (including Eka when relevant) → hospital list → route with Google Maps link; admin view with live map.
- Hosted on **S3 + CloudFront**; map key from backend **GET /config**, no keys in frontend.
- *[Add your own points: UX, admin features, map, etc.]*

---

## [2:35–3:00] Mobile app — you manage

- **Android app:** Kotlin, Jetpack Compose; same APIs — triage, hospitals, route, RMP Learning — with Cognito Id Token in **Authorization: Bearer** header.
- Same backend; mobile for field use, web for desktop/admin.
- *[Add your own points: offline banner, UX, form flow, etc.]*

**Closing (optional):** So in three minutes: we’re helping rural RMPs with **AI triage**, **Eka for Indian drugs and protocols**, **hospital matching**, and **real routing** — on **web and Android**, one backend. Thank you.

---

## Quick reference — one-liners

| Topic | One-liner |
|-------|-----------|
| **Problem** | 68% of rural providers are unqualified RMPs serving 70%; they lack severity assessment, hospital knowledge, Indian drug/protocol access. |
| **USP** | Augment RMPs (not replace): AI triage + Eka (Indian drugs/protocols) + hospital matching + Google Maps routing + RMP Learning; one backend, web + Android. |
| **Architecture** | API Gateway + Cognito → Lambdas (triage, hospitals, route, RMP Learning) → Bedrock AgentCore (4 runtimes) → MCP Gateway → Eka, get_hospitals, Google Maps; Aurora; Secrets Manager; no secrets in frontend. |
| **Web** | Vite dashboard, S3 + CloudFront, GET /config for map key; triage → hospitals → route + admin map. |
| **Mobile** | Android, Kotlin + Compose, same APIs with Cognito Id Token; you manage the rest. |
