# Implementation History & Discussion Summary

**Purpose:** Capture all design discussions, decisions, implementation details, and lessons learned from project inception through Phase 2.

---

## Project Context

**Emergency Medical Triage** – AI-assisted emergency triage and hospital routing for rural India (RMPs). Python backend, AWS (Bedrock, Lambda, Aurora PostgreSQL, API Gateway, S3).

---

## Early Discussions (Pre-Implementation)

### Architecture Decisions
- **No Bedrock Agent for Phase 1 Triage:** Use Converse API with tool use for faster iteration; Bedrock Agent path exists in code but `BEDROCK_AGENT_ID` is empty.
- **Bedrock Agents for Hospital Matcher & Routing:** Use Bedrock Agents (not just Converse API) for Hospital Matcher and Routing services – per discussion.
- **Triage:** Converse API with `submit_triage_result` tool; Pydantic validates output.
- **Aurora PostgreSQL 15:** IAM auth, no password in Secrets Manager for Lambda.
- **Migrations:** Raw SQL in `infrastructure/migrations/` – no Alembic (no SQLAlchemy; append-only schema fits manual migrations).

### Schema Decisions (Phase 2)
| Topic | Decision | Rationale |
|-------|----------|-----------|
| **deleted_at** | Add | Soft delete support |
| **updated_at** | Omit | Append-only rows; no updates |
| **submitted_by / rmp_id** | Add | `submitted_by` column; API accepts `rmp_id` as alias |
| **hospital_match_id** | Add now | Phase 4 linkage; nullable UUID FK for future hospital match table |

---

## Phase 1: Triage Lambda + Bedrock Converse API

### Implemented
- **Models** (`src/triage/models/triage.py`): TriageRequest, TriageResult, SeverityLevel (critical/high/medium/low)
- **Core** (`src/triage/core/`): agent.py (Converse API + tool use), instructions.py, tools.py
- **API** (`src/triage/api/handler.py`): Lambda handler for POST /triage
- **Infra:** Triage Lambda, POST /triage, Bedrock IAM for us-east-1, us-east-2, us-west-2
- **Endpoint:** `POST https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev/triage`

### Issues & Fixes
| Issue | Fix |
|-------|-----|
| pydantic_core ImportError | Lambda runs Linux; build with `--platform manylinux2014_x86_64` |
| toolConfig strict rejected | Remove `strict` from Bedrock Converse; use JSON schema only |
| Model ID | Use inference profile, e.g. `us.anthropic.claude-sonnet-4-6` |
| AccessDeniedException | Add IAM for us-east-1, us-east-2, us-west-2 (inference routing) |

---

## Phase 2: Aurora Persistence

### Implemented
- **Migration** (`infrastructure/migrations/001_create_triage_assessments.sql`): Full schema with indexes
- **Persistence** (`src/triage/core/db.py`): IAM auth, `insert_triage_assessment()`
- **Handler:** Persists after assessment; returns `id` when successful
- **Infra:** Lambda in VPC, NAT Gateway, Aurora SG ingress from Lambda, Secrets Manager + RDS IAM

### Schema (triage_assessments)
- id, created_at, deleted_at
- symptoms, vitals, age_years, sex
- severity, confidence, recommendations, force_high_priority, safety_disclaimer
- request_id, bedrock_trace_id, model_id
- submitted_by, hospital_match_id

### Issues & Fixes
| Issue | Fix |
|-------|-----|
| Aurora PAM auth failure | RDS Data API used for migrations; password auth had persistent issues from psql/tunnel |
| psycopg2 "can't adapt type 'UUID'" | Convert UUID params to `str()` before passing to execute |
| bastion_allowed_cidr invalid | Use `0.0.0.0/0` not `0.0.0.0` |
| Duplicate IGW (bastion + nat) | Bastion uses `aws_internet_gateway.nat`; removed bastion's own IGW |
| Build: pip not found | Use `python3 -m pip` in build script |

### Migration Approach
- **RDS Data API** enabled on Aurora cluster for running migrations (IAM auth, no password)
- Manual migrations: `aws rds-data execute-statement` or psql via bastion
- One-time: `GRANT rds_iam TO triagemaster` for Lambda IAM auth

---

## Infrastructure Notes

### Bastion
- Optional (`enable_bastion` in tfvars)
- Uses IGW from nat.tf (no duplicate IGW)
- For migrations/debug: SSH tunnel or direct psql from bastion (with psql installed)
- Connection: `PGSSLMODE=require` for Aurora

### NAT
- Required for Lambda in VPC to reach Bedrock
- Private subnets route via NAT Gateway
- Cost: ~$32/month for NAT

---

## Tech Stack

- Python 3.12, Pydantic, boto3, psycopg2-binary
- Aurora PostgreSQL 15, IAM auth, RDS Data API
- Bedrock Converse API with tool use (Bedrock Agents optional)
- Terraform for infrastructure

---

## Phase 4: Hospital Matcher (Started)

### Implemented
- **Models** (`src/hospital_matcher/models/`): HospitalMatchRequest, HospitalMatchResult, MatchedHospital
- **Core** (`src/hospital_matcher/core/`): agent.py (Converse API + optional Bedrock Agent), instructions, tools
- **API** (`src/hospital_matcher/api/`): Lambda handler for POST /hospitals
- **Infra:** Hospital Matcher Lambda, POST /hospitals, Bedrock IAM
- **Schema:** `hospital_matches` table (002 migration); `triage_assessments.hospital_match_id` links to it
- **Env vars:** `BEDROCK_HOSPITAL_MATCHER_AGENT_ID`, `BEDROCK_HOSPITAL_MATCHER_AGENT_ALIAS_ID` – when set, uses Bedrock Agent; else Converse API

### Request (POST /hospitals)
- severity, recommendations, triage_assessment_id?, patient_location_lat/lon?, limit

### Response
- hospitals: [{ hospital_id, name, match_score, match_reasons, estimated_minutes?, specialties? }]
- safety_disclaimer

---

## AgentCore Gateway get_hospitals (Mar 2026)

### Implemented
- **Lambda** (`infrastructure/gateway_get_hospitals_lambda_src/lambda_handler.py`): AgentCore Gateway target implementing `get_hospitals` tool. Event has `severity`, `limit`; context has `bedrockAgentCoreToolName` (strip `TARGET___` prefix). Returns synthetic Indian hospital data (same structure as `agentcore/agent/synthetic_hospitals.py`).
- **Terraform** (`infrastructure/gateway_get_hospitals.tf`): Creates Lambda + IAM role. Outputs `gateway_get_hospitals_lambda_arn` for setup script.
- **Setup script** (`scripts/setup_agentcore_gateway.py`): Uses `bedrock_agentcore_starter_toolkit` GatewayClient to create MCP Gateway with Cognito OAuth, adds Lambda target with get_hospitals tool schema, saves `gateway_config.json`.
- **Docs** (`docs/backend/agentcore-gateway-manual-steps.md`): Manual steps for Gateway setup (Terraform creates Lambda; script creates Gateway).

### Flow
1. `terraform apply` → Lambda created
2. `python scripts/setup_agentcore_gateway.py <lambda_arn>` → Gateway + target + gateway_config.json
3. Agents use Gateway MCP URL with OAuth token; tool name `{target_name}___get_hospitals`

---

## Cleanup: Bedrock Agent Removed (AgentCore Migration)

- **Removed:** Classic Bedrock Agent Terraform (`bedrock_agent_hospital_matcher.tf`) – PrepareAgent/version detection was unreliable.
- **Hospital Matcher:** Uses Converse API (fallback) when `BEDROCK_HOSPITAL_MATCHER_AGENT_ID` empty.
- **Decision:** Migrate to **Bedrock AgentCore** – see [agentcore-implementation-plan.md](./agentcore-implementation-plan.md).

---

## AgentCore AC-1 Complete (Mar 2026)

### Implemented
- **Hospital Matcher** on AgentCore Runtime (Strands + synthetic tool)
- **Lambda** calls `InvokeAgentRuntime` when `use_agentcore=true`
- **Eka config** in Secrets Manager (`eka_api_key` variable → `{project}/eka-config`)
- **Gateway setup script** fixes: target name `get-hospitals-target` (no underscores), ConflictException handling for re-runs, `--gateway-id` for existing gateways

### Gateway Status
- MCP Gateway created, `get_hospitals` Lambda target added
- `gateway_config.json` with gateway_url, gateway_id (gitignored)

---

## Next Steps (TODO)

1. **A:** Wire Hospital Matcher agent to Gateway (use get_hospitals from Gateway instead of in-agent tool)
2. **B:** Add Eka as Gateway target (Lambda/API); wire Triage to use Indian drugs/protocols
3. **C:** (Combined with A/B as needed)
4. **AC-2:** Triage on AgentCore + full Observability
5. **AC-3:** Memory + Hospital MCP integration
6. **AC-4:** Routing agent + POST /route + Identity
