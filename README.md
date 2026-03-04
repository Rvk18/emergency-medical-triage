# AI Hackathon Triage

**Emergency Medical Triage and Hospital Routing System** — an AI-powered platform that augments India's rural emergency response by supporting unqualified Rural Medical Practitioners (RMPs) with real-time triage, hospital matching, and routing.

## The Problem

In rural India, **68% of healthcare providers are unqualified RMPs** with no formal medical training, yet they handle most emergency cases where **70% of the population** lives. When emergencies occur, first responders often lack the ability to:

- Assess emergency severity reliably
- Know which hospitals have the right specialists and capacity
- Make safe triage decisions during the “golden hour”

## Our Solution

Instead of replacing RMPs (not feasible at scale), we **upgrade them** with:

1. **Real-time medical augmentation** — AI gives physician-level decision support and procedural guidance during emergencies  
2. **Continuous skill building** — Personalized medical education that improves RMP capabilities over time  
3. **Collective intelligence** — Every case improves the system for all providers across the network  
4. **Peer-to-peer learning** — A virtual medical college connecting isolated RMPs with experienced practitioners  

## Key Features

- **AI-assisted triage** — Symptom and vital-sign analysis with medical protocol validation, multi-model consensus, and safety guardrails (e.g. “treat as high priority” when confidence &lt; 85%)  
- **Hospital capability tracking** — Real-time bed availability, equipment, and specialist status  
- **Intelligent routing** — Top hospital recommendations by condition, capacity, and travel, with turn-by-turn navigation  
- **Multi-language support** — Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati; vernacular symptom input and audio output  
- **Offline capability** — Cached triage for common emergencies and cached hospital data for a 50 km radius  
- **RMP augmentation** — Real-time education, step-by-step procedural guidance (e.g. CPR, wound care), and telemedicine escalation when needed  

## Architecture Overview

- **Frontend:** Mobile app (Android/iOS), web dashboard, voice interface  
- **Core engines:** Triage AI, RMP Augmentation Engine, Collective Intelligence Network, Hospital Matcher, Routing Engine  
- **Integration:** MCP servers (Hospital Data, Medical Knowledge, Geographic Data, Emergency Services)  
- **Cloud:** Amazon Bedrock (foundation models), Kiro Platform (orchestration), AWS Lambda, Amazon DynamoDB  

See the design document for detailed architecture, data models, and correctness properties.

## Project Structure

```
AI_Hackathon_Triage/
├── README.md
├── pyproject.toml
├── requirements.txt
├── src/
│   ├── triage/           # Triage Lambda: Converse API, optional Eka via Gateway
│   │   ├── api/          # Lambda handlers
│   │   ├── core/         # Agent, tools, gateway_client (Eka)
│   │   └── models/
│   └── hospital_matcher/ # Hospital Matcher Lambda: AgentCore or Converse
│       ├── api/
│       ├── core/
│       └── models/
├── agentcore/            # AgentCore Runtime agents (Hospital Matcher)
│   └── agent/            # Strands + Gateway client, synthetic_hospitals
├── infrastructure/       # Terraform: Lambda, API Gateway, Aurora, Gateway Lambdas
├── scripts/              # Build, Gateway setup (setup_agentcore_gateway.py)
├── docs/backend/         # Design, implementation plan, release & testing docs
└── tests/
```

## Quick Start (for collaborators)

1. **Clone and setup**
   ```bash
   git clone https://github.com/Rvk18/emergency-medical-triage.git
   cd emergency-medical-triage
   python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Provision AWS** (see [infrastructure/README.md](infrastructure/README.md))
   ```bash
   cd infrastructure
   cp terraform.tfvars.example terraform.tfvars   # Edit db_username, db_password
   terraform init && terraform apply
   ```
   After apply, API URL and Gateway Lambda ARNs are in Secrets Manager (**api_config**). Terraform creates this secret on apply; it does not exist before. See [docs/backend/secrets.md](docs/backend/secrets.md). To load into the shell:
   ```bash
   eval $(python scripts/load_api_config.py --exports)   # sets API_URL, GATEWAY_*_LAMBDA_ARN
   curl -s "${API_URL}health"
   ```

## Documentation

| Document | Description |
|----------|-------------|
| [requirements.md](docs/backend/requirements.md) | User stories, acceptance criteria, glossary |
| [design.md](docs/backend/design.md) | Architecture, components, data models |
| [implementation-history.md](docs/backend/implementation-history.md) | Decisions, phases, fixes |
| [secrets.md](docs/backend/secrets.md) | Terraform-created secrets, api_config keys, load script |
| [OBSERVABILITY.md](docs/backend/OBSERVABILITY.md) | Triage/Hospital Matcher logs, CloudWatch Insights, trace review |
| [agentcore-implementation-plan.md](docs/backend/agentcore-implementation-plan.md) | AgentCore phases (AC-1–AC-4) |
| [RELEASE-Gateway-Eka-Integration.md](docs/backend/RELEASE-Gateway-Eka-Integration.md) | **AC-1 release:** Gateway + Eka wiring, config, quick test |
| [TESTING-Gateway-Eka.md](docs/backend/TESTING-Gateway-Eka.md) | Unit, integration, and API testing for Gateway/Eka |
| [agentcore-gateway-manual-steps.md](docs/backend/agentcore-gateway-manual-steps.md) | Gateway setup script and env vars |
| [TODO.md](docs/backend/TODO.md) | Backend TODO (Gateway done; AC-2–AC-4 next) |

## Tech Stack

- **AI:** Amazon Bedrock (Converse API, foundation models), **Bedrock AgentCore** (Runtime, Gateway, optional Eka for triage)
- **Backend:** AWS Lambda, Aurora PostgreSQL, API Gateway, S3
- **Integration:** AgentCore Gateway (MCP tools: get_hospitals, Eka search_medications / search_protocols)

## Requirements Summary

- Triage assessment with protocol validation and multi-model consensus  
- Real-time hospital capability and routing within defined SLAs  
- Multi-language and accessibility (including audio for illiterate users)  
- MCP-based integration with graceful degradation  
- Data privacy (AES-256, RBAC, Indian data protection), audit logs  
- Scalability (1000+ concurrent assessments, 99.9% uptime targets)  
- Offline triage and cached hospital/routing data  

## License

See repository license file (if present).
