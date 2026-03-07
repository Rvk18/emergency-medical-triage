# Documentation

Central documentation for the Emergency Medical Triage project.

---

## Hackathon submission

**Evaluators and judges:** Start with **[HACKATHON.md](../HACKATHON.md)** at the repo root. It contains:

- Problem and solution summary  
- Features (triage with Eka, hospitals, route, RMP auth)  
- Quick start (API URL, token, curl for triage → hospitals → route)  
- Eka triage test cases (medications, protocols)  
- Demo flow and full documentation index  

---

## Frontend (mobile & web)

| Document | Description |
|----------|-------------|
| **[API-Integration-Guide.md](frontend/API-Integration-Guide.md)** | **Start here.** Base URL, auth (Cognito Id Token), endpoints: GET /health, POST /triage, POST /hospitals, POST /route. Request/response examples, error handling, recommended flow (triage → hospitals → route). How to get API URL: `eval $(python3 scripts/load_api_config.py --exports)` or Terraform output. |
| **[triage-api-contract.md](frontend/triage-api-contract.md)** | Triage request (symptoms, vitals, age_years, sex, session_id) and response (severity, confidence, recommendations, force_high_priority, session_id). Mobile field mapping. **Eka:** When user asks for Indian brands or protocols, recommendations may include Indian drug names and protocol-style steps. |
| **[RMP-AUTH.md](frontend/RMP-AUTH.md)** | Cognito sign-in for RMPs; getting Id Token for Amplify / mobile / web. |
| [TESTING-Pipeline-curl.md](backend/TESTING-Pipeline-curl.md) | Curl examples for full pipeline (triage → hospitals → route); use with `get_rmp_token.py`. |

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
