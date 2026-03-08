# Project Summary — Emergency Medical Triage

**One-pager for hackathon submission (Big 5 — Project Summary).**

---

## Project name

**Emergency Medical Triage and Hospital Routing System**

---

## Problem

In rural India, **68% of healthcare providers are unqualified RMPs** (Rural Medical Practitioners) with no formal medical training, yet they serve **70% of the population**. During emergencies they often lack:

- Reliable severity assessment
- Knowledge of which hospitals have the right capacity and specialists
- Access to **Indian drug brands and treatment protocols** (ICMR-style) at point of care
- Safe triage decisions in the “golden hour”

---

## Solution

We **augment RMPs** (not replace them) with an AI-powered platform:

1. **AI triage** — Symptom and vital-sign analysis with **Eka Care integration**: Indian branded medications and treatment protocols in recommendations.
2. **Hospital matching** — Real-time capability and capacity via MCP Gateway (get_hospitals).
3. **Intelligent routing** — Real driving distance, duration, and Google Maps directions (POST /route).
4. **RMP Learning** — Quiz flow (get question → submit answer → points, leaderboard) for continuous skill building.
5. **Single-session flow** — Triage → Hospitals → Route with optional `session_id` for continuity.

---

## What we built (MVP)

| Component | Description |
|-----------|-------------|
| **POST /triage** | Symptoms + vitals → severity, confidence, recommendations. Eka: Indian paracetamol brands, fever protocol, ORS/dehydration protocol, etc. |
| **POST /hospitals** | Severity + recommendations → hospital list; optional patient location for distance/directions. |
| **POST /route** | Origin + destination → `distance_km`, `duration_minutes`, `directions_url` (Google Maps). |
| **POST /rmp/learning** | Get quiz question or submit answer → points + feedback; GET /rmp/learning/me, GET /rmp/learning/leaderboard. |
| **RMP auth** | Cognito Id Token; all POST endpoints require `Authorization: Bearer <IdToken>`. |
| **Frontend** | Web dashboard (`frontend/web/`) and Android app (`frontend/mobile-android/`) — integrate with above APIs. |

---

## Tech stack

| Layer | Technology |
|-------|------------|
| **AI** | Amazon Bedrock, Bedrock AgentCore (Runtime, MCP Gateway) |
| **Eka** | Eka Care API (Indian medications, treatment protocols) via Gateway Lambda |
| **Backend** | AWS Lambda, API Gateway, Aurora PostgreSQL, Secrets Manager |
| **Auth** | Cognito User Pools (RMP sign-in) |
| **Routing** | Google Maps Routes API; POST /route returns directions_url |
| **Frontend** | Web (Next.js/Vite), Android (Kotlin, Jetpack Compose) |

---

## Links (fill in for submission)

| Item | Link |
|------|------|
| **Working MVP (web)** | _[Deploy web app and add URL here]_ |
| **Demo video** | _[YouTube or Drive link]_ |
| **Project PPT** | _[Link to presentation]_ |
| **GitHub repository** | https://github.com/Rvk18/emergency-medical-triage **(ensure repo is Public)** |
| **Mobile app (optional)** | _[APK download or store link — see docs/MVP-DEPLOY-RUNBOOK.md]_ |

---

## How to run / evaluate

1. **API + token** (from project root, with AWS stack applied):  
   `eval $(python3 scripts/load_api_config.py --exports)` and `RMP_TOKEN=$(python3 scripts/get_rmp_token.py)`
2. **Quick curl:** See [HACKATHON.md](HACKATHON.md) § Quick Start — health, triage, hospitals, route, RMP Learning.
3. **Full test matrix:** [docs/backend/API-TEST-RESULTS.md](docs/backend/API-TEST-RESULTS.md).

---

## Repository structure

- **src/** — Lambda handlers (triage, hospital_matcher, route, rmp_learning)
- **agentcore/agent/** — AgentCore agents (triage, hospital_matcher, routing, rmp_quiz)
- **infrastructure/** — Terraform (Lambda, API Gateway, Aurora, Gateway Lambdas)
- **frontend/web/** — Web dashboard  
- **frontend/mobile-android/** — Android app  
- **docs/** — API contracts, testing, runbooks, roadmap  

---

## Documentation

- **Evaluators:** [HACKATHON.md](HACKATHON.md) — problem, solution, quick start, demo flow, doc index  
- **Submission checklist:** [SUBMISSION-CHECKLIST.md](SUBMISSION-CHECKLIST.md) — Big 5, GitHub, MVP deploy  
- **Frontend integration:** [docs/frontend/API-Integration-Guide.md](docs/frontend/API-Integration-Guide.md)  
- **OpenAPI:** [docs/openapi.yaml](docs/openapi.yaml)
