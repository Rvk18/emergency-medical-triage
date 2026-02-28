# Implementation Plan: AI Layer + Backend Services

**Scope:** AI layer (Bedrock, severity classification, confidence scoring, multi-model consensus) and backend Lambda services.  
**Out of scope (other team):** Frontend, Auth, MCP servers, External integrations.

---

## Captured Decisions

| Topic | Decision |
|-------|----------|
| **confidence < 85% → high priority** | Enforced by **reasoning agent** via action group (not post-processing only) |
| **Severity/confidence schema** | **Strict schema** required; align with WHO IITT / ESI |
| **Trace review (medical audit)** | **Admin** and **Dev** review traces |
| **Load tests** | Not now; follow standard practices for timeouts |
| **Tools in critical path** | Required only; no overengineering |
| **Severity/confidence values** | Follow WHO/ESI standards; refer to web for current practices |
| **Action groups** | **Lambda + Knowledge Base** |
| **Model** | **Claude Sonnet** |
| **force_high_priority** | Implement as **action group** |
| **Multi-model** | Phase 3; multiple agents |
| **Knowledge Base** | WHO guidelines via MCP or Aurora; RAG for validation. No prod data for hackathon—use MCP or synthetic data |

---

## Phase 1: Triage Lambda + Bedrock Agents

**Goal:** End-to-end triage flow using **Bedrock Agents** — reasoning agent with action groups (Lambda + KB). Receive symptoms/vitals, return severity + confidence + recommended actions.

### Architecture
- **Triage Agent**: Bedrock Agent (Claude Sonnet) with action groups.
- **Action groups**: Lambda (business logic) + Knowledge Base (RAG for WHO guidelines).
- **force_high_priority**: Dedicated action group invoked when confidence < 85%.

### Deliverables
- [ ] **Models** (`src/triage/models/`): TriageRequest, TriageResult, SeverityLevel (critical/high/medium/low) — strict Pydantic schema
- [ ] **Agent setup**: Bedrock Agent, action groups (Lambda + KB), OpenAPI/function schema
- [ ] **Core** (`src/triage/core/`): Agent orchestration, severity extraction, confidence scoring
- [ ] **Safety:** Reasoning agent enforces confidence < 85% → force_high_priority via action group
- [ ] **API** (`src/triage/api/`): Lambda handler for POST /triage
- [ ] **Infra:** Triage Lambda, API Gateway POST /triage, Bedrock Agents, KB, Secrets Manager

### Acceptance
- POST /triage with symptoms returns structured triage result
- Confidence < 85% triggers high-priority recommendation (via reasoning agent)
- Response within 2 minutes

---

## Phase 2: Aurora Schema + Persist Triage Results

**Goal:** Store triage assessments in Aurora for audit and downstream use.

### Deliverables
- [ ] Aurora schema: `triage_assessments` table (id, symptoms, vitals, severity, confidence, recommendations, created_at, etc.)
- [ ] `src/triage/core/db.py`: IAM auth connection, insert triage record
- [ ] Triage Lambda: after assessment, persist to Aurora
- [ ] Infra: Lambda in VPC, Aurora SG allows Lambda

---

## Phase 3: Multi-Model Consensus + Safety Guardrails

**Goal:** Use 2+ Bedrock models for critical cases; stricter safety rules; multiple agents.

### Deliverables
- [ ] Multi-model: invoke 2 models for severity=critical, consensus logic
- [ ] Multiple agents: Triage, Hospital Matcher, Routing
- [ ] Request additional info when symptom data incomplete
- [ ] Flag cases for human review (complex multi-system symptoms)
- [ ] Structured triage report with safety disclaimers
- [ ] Trace review: Admin + Dev for medical audit

---

## Phase 4: Hospital Matcher + Routing Services

**Goal:** Hospital Matcher and Routing Lambdas (stubs; MCP integration later by other team).

### Deliverables
- [ ] Hospital Matcher Lambda: accepts triage result, returns top hospitals (mock/stub until MCP)
- [ ] Routing Lambda: accepts origin + hospital, returns route (mock until Geographic MCP)
- [ ] API Gateway: /hospitals, /route endpoints

---

## Knowledge Base Strategy

| Item | Approach |
|------|----------|
| **WHO guidelines** | Fetch via MCP or store in Aurora |
| **Prod data** | None for hackathon |
| **Hackathon data** | MCP or synthetic data |
| **RAG** | Use for validation against medical protocols |

---

## Execution Order

| Phase | Focus                    | Dependency |
|-------|--------------------------|------------|
| 1     | Triage + Bedrock Agents  | None       |
| 2     | Aurora persist           | Phase 1    |
| 3     | Multi-model + guardrails | Phase 1    |
| 4     | Hospital + Routing       | Phase 1    |

Phase 2 and 3 can run in parallel after Phase 1.
