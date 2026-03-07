# Emergency Medical Triage – Hackathon Submission

**AI-powered triage and hospital routing for India’s rural emergency response** – supporting unqualified Rural Medical Practitioners (RMPs) with real-time triage, **Indian drugs & protocols (Eka Care)**, hospital matching, and turn-by-turn routing.

---

## Problem

In rural India, **68% of healthcare providers are unqualified RMPs** with no formal medical training, yet they serve **70% of the population**. During emergencies they often lack:

- Reliable severity assessment
- Knowledge of which hospitals have the right capacity and specialists
- **Access to Indian drug brands and treatment protocols** (ICMR-style) at point of care
- Safe triage decisions in the “golden hour”

## Solution

We **augment RMPs** (not replace them) with:

1. **AI triage** – Symptom/vital analysis with **Eka Care integration**: Indian branded medications and treatment protocols in recommendations.
2. **Hospital matching** – Real-time capability and capacity; MCP Gateway with get_hospitals.
3. **Routing** – POST /route returns real driving distance, duration, and Google Maps URL.
4. **Single session flow** – Triage → Hospitals → Route with optional `session_id` for memory continuity.

---

## Features (What We Built)

| Feature | Description |
|--------|-------------|
| **POST /triage** | Symptoms + vitals → severity, confidence, recommendations. **Eka:** When the user asks for “Indian paracetamol brands” or “fever protocol”, recommendations include real Indian brands (e.g. Modi Lifecare, Lyka Labs) and protocol-style guidance (e.g. ORS, WHO dehydration classification). |
| **POST /hospitals** | Severity + recommendations → list of hospitals (name, match_score, lat/lon). Optional patient location for distance. |
| **POST /route** | Origin + destination (lat/lon or address) → `distance_km`, `duration_minutes`, `directions_url` (open in Google Maps). |
| **RMP auth** | Cognito Id Token; all POST (except /health) require `Authorization: Bearer <IdToken>`. |
| **Eka on triage** | AgentCore triage runtime + MCP Gateway + Eka Lambda: `search_indian_medications`, `search_treatment_protocols`. Enabled via `python3 scripts/enable_eka_on_runtime.py`. |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **AI** | Amazon Bedrock (Converse API, foundation models), **Bedrock AgentCore** (Runtime, MCP Gateway) |
| **Eka** | Eka Care API (Indian medications, treatment protocols); Gateway Lambda with client_id/client_secret login |
| **Backend** | AWS Lambda, API Gateway, Aurora PostgreSQL, Secrets Manager |
| **Auth** | Cognito User Pools (RMP sign-in) |
| **Routing** | Google Maps Routes API (optional); POST /route returns directions_url |
| **Frontend** | Web (Next.js/Vite) and Android (Kotlin, Jetpack Compose) – see `frontend/` |

---

## Architecture (High Level)

```
[RMP App (Web/Android)] 
    → API Gateway (Cognito auth) 
    → Triage Lambda → AgentCore Triage Runtime (Eka tools via Gateway)
    → Hospitals Lambda → AgentCore Hospital Matcher (get_hospitals via Gateway)
    → Route Lambda → Gateway (maps/routing) → Directions
```

- **Triage:** AgentCore runtime with Eka tools (search_indian_medications, search_treatment_protocols) via MCP Gateway.
- **Hospitals:** AgentCore Hospital Matcher; Gateway target get_hospitals.
- **Route:** Route Lambda calls Gateway maps-target/routing-target for directions.

---

## Quick Start (Judges / Evaluators)

### 1. Get API URL and token

From **project root** (requires AWS credentials and Terraform-applied stack):

```bash
eval $(python3 scripts/load_api_config.py --exports)   # sets API_URL
RMP_TOKEN=$(python3 scripts/get_rmp_token.py)        # Id token from Cognito (reads Secrets Manager)
```

If you don’t have the stack: use the **demo base URL** provided by the team and a **demo token** (team will share).

### 2. Run the pipeline

```bash
# Health
curl -s "${API_URL}health" | jq .

# Triage (Eka: Indian brands + protocols in recommendations)
curl -s -X POST "${API_URL}triage" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RMP_TOKEN" \
  -d '{"symptoms": ["fever", "patient wants Indian paracetamol brands"]}' | jq .

# Hospitals (use severity from triage)
curl -s -X POST "${API_URL}hospitals" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RMP_TOKEN" \
  -d '{"severity":"medium","recommendations":["Paracetamol 500mg"],"limit":3}' | jq .

# Route (real directions)
curl -s -X POST "${API_URL}route" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RMP_TOKEN" \
  -d '{"origin":{"lat":12.97,"lon":77.59},"destination":{"lat":13.08,"lon":80.27}}' | jq .
```

### 3. Eka test cases (triage)

See **docs/backend/TESTING-Gateway-Eka.md** §4b for full list. Examples:

- **Medications:** `["sore throat", "need Indian amoxicillin brands"]` → recommendations include Indian brands.
- **Protocols:** `["acute diarrhoea", "ORS and dehydration protocol"]` → WHO-style protocol in recommendations.
- **Combined:** `["fever and cough", "Indian paracetamol brands and fever protocol"]` → both brands and protocol.

---

## Documentation Index

| Doc | Purpose |
|-----|--------|
| [README.md](README.md) | Project overview, structure, quick start |
| [docs/README.md](docs/README.md) | Full documentation index (frontend, backend, infra) |
| [docs/frontend/API-Integration-Guide.md](docs/frontend/API-Integration-Guide.md) | **Frontend:** Base URL, auth, triage → hospitals → route, error handling |
| [docs/frontend/triage-api-contract.md](docs/frontend/triage-api-contract.md) | **Frontend:** Triage request/response, session_id, Eka behavior |
| [docs/frontend/RMP-AUTH.md](docs/frontend/RMP-AUTH.md) | Cognito sign-in, Id Token for mobile/web |
| [docs/backend/TESTING-Pipeline-curl.md](docs/backend/TESTING-Pipeline-curl.md) | Full pipeline curl (triage → hospitals → route) |
| [docs/backend/TESTING-Gateway-Eka.md](docs/backend/TESTING-Gateway-Eka.md) | Eka triage test cases (medications, protocols, combined) |
| [docs/backend/EKA-VALIDATION-RUNBOOK.md](docs/backend/EKA-VALIDATION-RUNBOOK.md) | Eka config, Lambda test, response shape |
| [docs/backend/agentcore-gateway-manual-steps.md](docs/backend/agentcore-gateway-manual-steps.md) | Gateway setup, Eka on triage runtime |
| [docs/backend/secrets.md](docs/backend/secrets.md) | Terraform secrets, api_config, load scripts |

---

## Repo Structure

```
├── README.md
├── HACKATHON.md              ← This file (submission summary)
├── src/                      # Lambda handlers (triage, hospital_matcher, route)
├── agentcore/agent/          # AgentCore agents (triage, hospital_matcher, routing)
├── infrastructure/           # Terraform (Lambda, API Gateway, Aurora, Eka secret)
├── scripts/                  # load_api_config.py, get_rmp_token.py, setup_agentcore_gateway.py, enable_eka_on_runtime.py
├── docs/
│   ├── frontend/             # API integration, triage contract, RMP auth
│   ├── backend/              # Testing, Eka runbook, Gateway steps, TODO
│   └── infrastructure/       # Bastion, Google Maps setup
└── frontend/
    ├── web/                  # Web dashboard
    └── mobile-android/       # Android app
```

---

## Demo Flow (For Judges)

1. **Sign in** (Cognito) → get Id Token.
2. **Triage:** Enter symptoms (e.g. “fever, patient wants Indian paracetamol brands”) → get severity, recommendations with **Indian brands** (e.g. Modi Lifecare, Lyka Labs) and/or **protocol** steps.
3. **Hospitals:** Send severity + recommendations → get hospital list (with optional patient location).
4. **Route:** Pick a hospital → get distance, duration, and **directions_url** → open in Google Maps.

Frontend (web/mobile) uses the same APIs; see **docs/frontend/API-Integration-Guide.md** for integration details.

---

## License

See repository license file.
