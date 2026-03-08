# Emergency Medical Triage

**AI-powered triage and hospital routing for India's rural emergency response** — supporting unqualified Rural Medical Practitioners (RMPs) with real-time triage, **Indian drugs & protocols (Eka Care)**, hospital matching, turn-by-turn routing, and **RMP Learning** (quiz + leaderboard).

---

## The Problem

In rural India, **68% of healthcare providers are unqualified RMPs** with no formal medical training, yet they handle most emergency cases where **70% of the population** lives. When emergencies occur, first responders often lack the ability to:

- Assess emergency severity reliably
- Know which hospitals have the right specialists and capacity
- Access **Indian drug brands and treatment protocols** at point of care
- Make safe triage decisions during the "golden hour"

---

## Our Solution

We **augment RMPs** (not replace them) with:

1. **AI triage** — Symptom and vital-sign analysis with **Eka Care**: Indian medications and treatment protocols in recommendations.
2. **Hospital matching** — Real-time capability and capacity via MCP Gateway (get_hospitals).
3. **Intelligent routing** — Real driving distance, duration, and Google Maps directions (POST /route).
4. **RMP Learning** — Quiz flow (get question → submit answer → points, leaderboard) for skill building.
5. **Single-session flow** — Triage → Hospitals → Route with optional `session_id` for continuity.

---

## What We Built (MVP)

| Feature | Description |
|--------|-------------|
| **POST /triage** | Symptoms + vitals → severity, confidence, recommendations. Eka: Indian paracetamol brands, fever protocol, ORS/dehydration, etc. |
| **POST /hospitals** | Severity + recommendations → hospital list; optional patient location for distance/directions. |
| **POST /route** | Origin + destination → distance_km, duration_minutes, directions_url (Google Maps). |
| **POST /rmp/learning** | Get quiz question or submit answer → points + feedback; GET /me, GET /leaderboard. |
| **RMP auth** | Cognito Id Token; all POST endpoints require `Authorization: Bearer <IdToken>`. |
| **Frontend** | Web dashboard (`frontend/web/`) and Android app (`frontend/mobile-android/`) — see [API Integration Guide](docs/frontend/API-Integration-Guide.md). |

---

## Hackathon Submission — The Big 5

| # | Item | Link / action |
|---|------|----------------|
| 1 | Project PPT | You |
| 2 | Demo video | You (YouTube/Drive) |
| 3 | Working MVP link | Deploy web on AWS; mobile options: [MVP Deploy Runbook](docs/MVP-DEPLOY-RUNBOOK.md) |
| 4 | GitHub repository | **Ensure repo is Public:** https://github.com/Rvk18/emergency-medical-triage |
| 5 | Project summary | [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md) — one-pager; fill in MVP/video/PPT links |

**Full checklist:** [SUBMISSION-CHECKLIST.md](SUBMISSION-CHECKLIST.md)

---

## Quick Start

### 1. Clone and setup

```bash
git clone https://github.com/Rvk18/emergency-medical-triage.git
cd emergency-medical-triage
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Provision AWS

See [infrastructure/README.md](infrastructure/README.md).

```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars   # Edit db_username, db_password
terraform init && terraform apply
```

After apply, API URL and Gateway ARNs are in Secrets Manager (**api_config**). Load into shell:

```bash
eval $(python3 scripts/load_api_config.py --exports)
curl -s "${API_URL}health"
```

### 3. Get RMP token and run pipeline

```bash
RMP_TOKEN=$(python3 scripts/get_rmp_token.py)
# Triage
curl -s -X POST "${API_URL}triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" \
  -d '{"symptoms":["fever","patient wants Indian paracetamol brands"]}' | jq .
# Hospitals, route, RMP Learning — see [HACKATHON.md](HACKATHON.md) § Quick Start
```

### 4. Frontend (web / Android)

Base URL, auth, and full flow: [docs/frontend/API-Integration-Guide.md](docs/frontend/API-Integration-Guide.md).  
Triage contract: [docs/frontend/triage-api-contract.md](docs/frontend/triage-api-contract.md).  
RMP sign-in: [docs/frontend/RMP-AUTH.md](docs/frontend/RMP-AUTH.md).  
RMP Learning API: [docs/frontend/RMP-LEARNING-API.md](docs/frontend/RMP-LEARNING-API.md).

---

## Project Structure

```
├── README.md
├── PROJECT-SUMMARY.md          # One-pager for submission (#5)
├── SUBMISSION-CHECKLIST.md     # Big 5 + GitHub + MVP runbook
├── HACKATHON.md                # Evaluators: problem, solution, quick start, doc index
├── src/
│   ├── triage/                 # Triage Lambda (AgentCore + Eka via Gateway)
│   ├── hospital_matcher/       # Hospital Matcher Lambda (AgentCore + get_hospitals)
│   ├── rmp_learning/          # RMP Learning Lambda (quiz, leaderboard, Aurora)
│   └── (route handled in infrastructure)
├── agentcore/agent/            # AgentCore agents (triage, hospital_matcher, routing, rmp_quiz)
├── infrastructure/             # Terraform: Lambda, API Gateway, Aurora, Gateway Lambdas
├── scripts/                    # load_api_config.py, get_rmp_token.py, setup_agentcore_gateway.py, enable_eka_on_runtime.py, run_rmp_learning_migration.py
├── docs/                       # API contracts, testing, runbooks, roadmap
│   ├── frontend/               # API-Integration-Guide, RMP-AUTH, RMP-LEARNING-API
│   ├── backend/                # API-TEST-RESULTS, Eka runbook, TODO
│   ├── infrastructure/         # Bastion, Google Maps
│   └── MVP-DEPLOY-RUNBOOK.md  # Deploy web + mobile availability for #3
└── frontend/
    ├── web/                    # Web dashboard
    └── mobile-android/         # Android app
```

---

## Documentation

| Document | Description |
|----------|-------------|
| **[HACKATHON.md](HACKATHON.md)** | **Evaluators:** problem, solution, quick start (curl), Eka tests, demo flow, doc index |
| **[PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)** | **Submission #5:** one-pager; fill in MVP/video/PPT links |
| **[SUBMISSION-CHECKLIST.md](SUBMISSION-CHECKLIST.md)** | Big 5 checklist, GitHub public, MVP runbook link |
| [docs/ROADMAP-MODULES.md](docs/ROADMAP-MODULES.md) | Modules A/B/C/D: what is what, plan ahead |
| [docs/frontend/API-Integration-Guide.md](docs/frontend/API-Integration-Guide.md) | Base URL, auth, triage → hospitals → route, RMP Learning |
| [docs/frontend/RMP-LEARNING-API.md](docs/frontend/RMP-LEARNING-API.md) | RMP Learning endpoints and frontend instructions |
| [docs/backend/API-TEST-RESULTS.md](docs/backend/API-TEST-RESULTS.md) | One-curl-per-endpoint test matrix, RMP Learning curls |
| [docs/MVP-DEPLOY-RUNBOOK.md](docs/MVP-DEPLOY-RUNBOOK.md) | Deploy web on AWS; mobile APK/Drive/internal testing |
| [docs/backend/secrets.md](docs/backend/secrets.md) | Terraform secrets, api_config, load scripts |
| [docs/backend/TODO.md](docs/backend/TODO.md) | Backend status and next steps |
| [docs/README.md](docs/README.md) | Full documentation index |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **AI** | Amazon Bedrock, Bedrock AgentCore (Runtime, MCP Gateway) |
| **Eka** | Eka Care API (Indian medications, protocols) via Gateway Lambda |
| **Backend** | AWS Lambda, API Gateway, Aurora PostgreSQL, Secrets Manager |
| **Auth** | Cognito User Pools (RMP sign-in) |
| **Routing** | Google Maps Routes API; POST /route → directions_url |
| **Frontend** | Web (Next.js/Vite), Android (Kotlin, Jetpack Compose) |

---

## License

See repository license file (if present).
