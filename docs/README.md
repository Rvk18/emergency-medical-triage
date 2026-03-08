# Documentation

Central documentation for the Emergency Medical Triage project.

---

## Hackathon submission

**Evaluators and judges:** Start with **[HACKATHON.md](../HACKATHON.md)** at the repo root. Also:

- **[PROJECT-SUMMARY.md](../PROJECT-SUMMARY.md)** — One-pager for submission (#5); fill in MVP/video/PPT links.
- **[SUBMISSION-CHECKLIST.md](../SUBMISSION-CHECKLIST.md)** — The Big 5 (PPT, video, MVP link, GitHub public, project summary).

---

## Roadmap (next phases)

**See [ROADMAP-MODULES.md](ROADMAP-MODULES.md)** for modules A/B/C/D (what is what, plan ahead) and **[ROADMAP-NEXT.md](ROADMAP-NEXT.md)** for the ordered plan:

- **RMP Learning (C)** — Backend complete; frontend team: [RMP-LEARNING-API.md](frontend/RMP-LEARNING-API.md).
- **Next:** A (Offline) → B (Multi-language) → D (Collective intelligence). AC-3 covered by comprehensive curl tests. Web app deploy and E2E testing last.

## Frontend (mobile & web)

| Document | Description |
|----------|-------------|
| **[API-Integration-Guide.md](frontend/API-Integration-Guide.md)** | **Start here.** Base URL, auth (Cognito Id Token), endpoints: GET /health, POST /triage, POST /hospitals, POST /route. Request/response examples, error handling, recommended flow (triage → hospitals → route). How to get API URL: `eval $(python3 scripts/load_api_config.py --exports)` or Terraform output. |
| **[triage-api-contract.md](frontend/triage-api-contract.md)** | Triage request (symptoms, vitals, age_years, sex, session_id) and response (severity, confidence, recommendations, force_high_priority, session_id). Mobile field mapping. **Eka:** When user asks for Indian brands or protocols, recommendations may include Indian drug names and protocol-style steps. |
| **[Hospital-Matcher-API.md](frontend/Hospital-Matcher-API.md)** | POST /hospitals – request/response, optional patient_location_lat/lon, per-hospital distance_km, duration_minutes, directions_url. |
| **[Route-API.md](frontend/Route-API.md)** | POST /route – origin/destination (lat/lon or address), distance_km, duration_minutes, directions_url (Google Maps). |
| **[openapi.yaml](openapi.yaml)** | **Full Swagger/OpenAPI 3.0** – all endpoints, request/response schemas, Bearer auth. Use for codegen or Swagger UI. |
| **[RMP-AUTH.md](frontend/RMP-AUTH.md)** | Cognito sign-in for RMPs; getting Id Token for Amplify / mobile / web. |
| **[RMP-LEARNING-API.md](frontend/RMP-LEARNING-API.md)** | RMP Learning: get_question, score_answer, GET /me, GET /leaderboard; frontend instructions. |
| [TESTING-Pipeline-curl.md](backend/TESTING-Pipeline-curl.md) | Curl examples for full pipeline (triage → hospitals → route); use with `get_rmp_token.py`. |
| [MVP-DEPLOY-RUNBOOK.md](MVP-DEPLOY-RUNBOOK.md) | Deploy web on AWS; mobile APK/Drive/internal testing for submission #3. |

---

## Backend

| Document | Description |
|----------|-------------|
| [requirements.md](backend/requirements.md) | User stories, acceptance criteria, glossary |
| [design.md](backend/design.md) | Architecture, components, data models |
| [secrets.md](backend/secrets.md) | Terraform-created secrets, api_config, gateway-config, load scripts |
| [TESTING-Pipeline-curl.md](backend/TESTING-Pipeline-curl.md) | Full pipeline curl (triage → hospitals → route), RMP token |
| [TESTING-Gateway-Eka.md](backend/TESTING-Gateway-Eka.md) | Unit/integration tests, **Eka triage test cases** (M1–M6 medications, P1–P6 protocols, C1–C2 combined) |
| [EKA-VALIDATION-RUNBOOK.md](backend/EKA-VALIDATION-RUNBOOK.md) | E1–E5: Eka config, direct Lambda test, response shape |
| [API-TEST-RESULTS.md](backend/API-TEST-RESULTS.md) | One-curl-per-endpoint test matrix; health, triage, hospitals, route, **RMP Learning**; Eka tools. |
| [DEPLOY.md](../DEPLOY.md) | Why post-Terraform scripts exist; deploy order (terraform → setup_agentcore_gateway → enable_gateway_on_* after agentcore deploy). |
| [HIPAA-Compliance-Checklist.md](backend/HIPAA-Compliance-Checklist.md) | H1–H4: PHI scope, encryption, access control, audit logging |
| [agentcore-gateway-manual-steps.md](backend/agentcore-gateway-manual-steps.md) | Gateway setup script, Eka on triage runtime (`enable_eka_on_runtime.py`) |
| [RELEASE-Gateway-Eka-Integration.md](backend/RELEASE-Gateway-Eka-Integration.md) | AC-1 release notes, Gateway + Eka config |
| [OBSERVABILITY.md](backend/OBSERVABILITY.md) | Triage/Hospital Matcher logs, CloudWatch, trace review |
| [TODO.md](backend/TODO.md) | Backend status and next steps |
| [implementation-history.md](backend/implementation-history.md) | Decisions, phases, fixes |

---

## Infrastructure

| Document | Description |
|----------|-------------|
| [bastion-setup.md](infrastructure/bastion-setup.md) | Bastion host for SSH tunnel to Aurora |
| [GOOGLE-MAPS-ACCOUNT-SETUP.md](infrastructure/GOOGLE-MAPS-ACCOUNT-SETUP.md) | Google Maps API key for POST /route |

---

## Roadmap

| Document | Description |
|----------|-------------|
| [ROADMAP-MODULES.md](ROADMAP-MODULES.md) | Modules A/B/C/D: what is what, plan ahead |
| [ROADMAP-NEXT.md](ROADMAP-NEXT.md) | Phases: A→B→D next, web deploy + E2E last |

---

## Architecture

| Document | Description |
|----------|-------------|
| [architecture-diagram-prompts.md](architecture/architecture-diagram-prompts.md) | Prompts for generating architecture diagrams |

---

## Folder summary

| Folder | Contents |
|--------|----------|
| **frontend** | API integration guide, triage contract, RMP auth, web/mobile workflows, tasks |
| **backend** | Requirements, design, secrets, Gateway/Eka testing, Eka runbook, AgentCore steps, TODO |
| **infrastructure** | Bastion, Google Maps setup |
| **architecture** | Diagram prompts |
