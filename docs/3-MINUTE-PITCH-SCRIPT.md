# 3-minute pitch script — Architecture, mobile app & web app

**Use this for a live demo or presentation.** Speak at a relaxed pace (~140 words per minute). Total: ~420 words ≈ 3 minutes.

---

## [0:00–0:35] Problem and why we built this

In rural India, **68% of healthcare providers are unqualified RMPs** — Rural Medical Practitioners — with no formal training. Yet they serve **70% of the population**. In emergencies they often lack reliable severity assessment, don’t know which hospitals have the right capacity or specialists, and don’t have access to **Indian drug brands and treatment protocols** at the point of care. We’re not replacing RMPs; we’re **augmenting** them with an AI-powered platform so they can make safer triage decisions in the golden hour.

---

## [0:35–1:20] What we built — backend and APIs

We built an end-to-end system. On the **backend**, RMPs hit a single **API Gateway** with **Cognito** sign-in. From there, **Lambda** functions handle triage, hospital matching, routing, and RMP Learning. **AI** runs on **Amazon Bedrock** and **Bedrock AgentCore**: we have four runtimes — Triage, Hospital Matcher, Routing, and RMP Quiz. The Triage runtime is wired to **Eka Care** via an MCP Gateway, so when an RMP asks for “Indian paracetamol brands” or “fever protocol,” recommendations include real Indian brands and protocol-style steps. Hospital matching uses a **get_hospitals** tool; routing uses **Google Maps** for real distance, duration, and turn-by-turn directions. We persist triage and learning scores in **Aurora PostgreSQL**. All of this is deployed with **Terraform** — Lambda, API Gateway, Cognito, Aurora, Secrets Manager, and the Gateway Lambdas for Eka and maps.

---

## [1:20–2:05] Web app and mobile app

We have **two frontends** that share the same APIs. The **web app** is a Vite-based dashboard. RMPs sign in with Cognito, then run through triage — symptoms and vitals — and get severity and recommendations, including Eka content when relevant. They then get a list of matched hospitals and can request a route with a Google Maps link. We also have an admin view with a **live map** of patients and hospitals. The web app is hosted on **S3 and CloudFront**; we don’t put API keys in the frontend — the map key is served from our backend via a **GET /config** endpoint. The **Android app** is built with **Kotlin and Jetpack Compose**. It does the same flow: sign in with Cognito, get an Id Token, and call the same APIs — triage, hospitals, route, and RMP Learning — with the **Authorization: Bearer** header. We documented how mobile gets the token and attaches it to every request in our **MOBILE-COGNITO-API-AUTH** doc. Both clients talk to the same API Gateway; the only difference is the UI — web for desktop or admin, mobile for field use.

---

## [2:05–2:50] End-to-end flow and takeaway

The **demo flow** is: sign in, enter symptoms — for example “fever, patient wants Indian paracetamol brands” — get severity and recommendations with Indian brands and protocols, then get hospital matches and pick one to get driving directions and a Google Maps link. RMP Learning adds a quiz: get a question, submit an answer, earn points, and see a leaderboard. **Security**: only public routes are health and config; everything else requires a Cognito Id Token. We use **Secrets Manager** for API keys and config; no secrets in the frontend. **Cost** for dev or low traffic is roughly **110 to 200 dollars per month** on AWS, driven by NAT, Aurora Serverless, and Bedrock.

---

## [2:50–3:00] Closing

So in three minutes: we’re helping rural RMPs with **AI triage**, **Eka for Indian drugs and protocols**, **hospital matching**, and **real routing** — on both **web and Android**, against one backend. Thank you.

---

## Quick reference — one-liners

- **Problem:** 68% of rural providers are unqualified RMPs serving 70% of the population; they lack severity assessment, hospital knowledge, and Indian drug/protocol access.
- **Solution:** Augment RMPs with AI triage (Eka), hospital matching, routing (Google Maps), and RMP Learning; one backend, web + Android.
- **Backend:** API Gateway + Cognito → Lambdas (triage, hospitals, route, RMP Learning) → Bedrock AgentCore (4 runtimes) → MCP Gateway → Eka, get_hospitals, Google Maps; Aurora for persistence.
- **Web:** Vite dashboard, S3 + CloudFront, Cognito login, GET /config for map key; triage → hospitals → route + admin map.
- **Mobile:** Android, Kotlin + Compose, same APIs with Cognito Id Token; triage, hospitals, route, RMP Learning.
- **Security:** Cognito on all protected routes; config from backend; Secrets Manager, no secrets in frontend.
