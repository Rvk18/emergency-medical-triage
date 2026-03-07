# HIPAA / health data compliance checklist (H1–H4)

**Purpose:** Document PHI scope, encryption, access control, and audit logging so the system is suitable for handling protected health information (PHI). See [ROADMAP-NEXT.md](../ROADMAP-NEXT.md) Phase 3 and [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) §1.

---

## H1: Document PHI scope

**Goal:** List what we store and classify as PHI/sensitive.

| Data | Where stored | Classification |
|------|--------------|----------------|
| Symptoms (free text) | Request body → Lambda → AgentCore; optionally `triage_assessments` (Aurora) | **PHI** – health-related; can identify condition |
| Vitals (heart_rate, blood_pressure_systolic/diastolic, temperature_celsius, respiratory_rate, spo2) | Request body → Lambda → AgentCore; optionally DB | **PHI** |
| Age, sex | Request body → Lambda → AgentCore; optionally DB | **PHI** (demographic) |
| Triage result (severity, confidence, recommendations, force_high_priority) | Response; optionally `triage_assessments` | **PHI** – clinical assessment |
| Session ID / patient ID | Request body; passed to AgentCore as `runtimeSessionId`; optionally DB | **Identifier** – links to PHI |
| Hospital list, route (origin/destination, directions_url) | Response; not persisted by default | **Context** – location; can be sensitive |
| RMP auth (Cognito Id Token) | API Gateway / Lambda (not stored in app DB) | **Auth** – AWS handles per Cognito |

**Scope summary:** Symptoms, vitals, age, sex, triage result, and session/patient identifiers are PHI or directly link to PHI. Treat all triage and hospital-match payloads as containing or referencing PHI.

---

## H2: Encryption checklist

**Goal:** Confirm encryption at rest and in transit; document.

| Item | Status | Notes |
|------|--------|--------|
| **Aurora encryption at rest** | ✅ | `storage_encrypted = true` in [infrastructure/rds.tf](../../infrastructure/rds.tf). AWS-managed keys. |
| **Secrets Manager** | ✅ | API config, gateway-config, RDS config, Eka config. AWS encrypts at rest; TLS in transit. |
| **TLS in transit** | ✅ | API Gateway HTTPS only; Lambda ↔ Aurora via Data API (HTTPS); Lambda ↔ Bedrock/Gateway over HTTPS. |
| **S3 (if used)** | ✅ | [infrastructure/s3.tf](../../infrastructure/s3.tf) – server-side encryption configured for deployment buckets. |

No PHI is stored in S3 by the application; deployment artifacts only. **Conclusion:** Encryption at rest (Aurora, Secrets Manager, S3) and in transit (HTTPS) is in place.

---

## H3: Access control

**Goal:** IAM least privilege; no PHI in logs; restrict who can read api_config / gateway-config / Eka.

| Item | Action / status |
|------|------------------|
| **IAM least privilege** | Lambdas use execution roles scoped to the resources they need (Bedrock, Secrets Manager, RDS Data API, Gateway invoke). No broad `*` on sensitive APIs. |
| **No PHI in log messages** | Application code must not log symptoms, vitals, or full request/response bodies. Log `request_id`, severity, and non-identifying metadata only. Review: [OBSERVABILITY.md](./OBSERVABILITY.md). |
| **Secrets access** | Restrict IAM policies so only the Lambdas (and approved scripts) can read `api_config`, `gateway_config`, `eka_config`, and `rds_config`. No broad `secretsmanager:GetSecretValue` on `*`. |
| **API Gateway** | RMP auth (Cognito) restricts who can call POST /triage, /hospitals, /route. |

**Follow-up:** Audit Lambda roles for minimal Secrets Manager and RDS permissions; confirm no PHI in CloudWatch log streams (search for symptom-like strings).

---

## H4: Audit logging

**Goal:** Document what we have; add who-accessed-what if required.

| Item | Status | Notes |
|------|--------|--------|
| **Request ID** | ✅ | Propagated in API and Lambda; can correlate logs. |
| **triage_assessments.id** | ✅ | Primary key for stored assessments; supports “what was recorded.” |
| **CloudWatch Logs** | ✅ | Lambda logs (with request_id); Bedrock AgentCore runtime logs. |
| **Who accessed what** | Optional | Not yet implemented. If required: add audit table (e.g. `api_access_log`: timestamp, request_id, endpoint, principal_id from Cognito, resource_id); or rely on CloudTrail for API Gateway + Lambda invocations and document how to correlate with request_id. |

**Conclusion:** Basic audit trail exists (request_id, DB ids, CloudWatch). For stricter “who accessed which assessment,” add an audit table or CloudTrail + log review process and document in this checklist.

---

## Summary

| # | Item | Status |
|---|------|--------|
| H1 | Document PHI scope | ✅ Done – symptoms, vitals, age, sex, triage result, session/patient ids classified. |
| H2 | Encryption checklist | ✅ Done – Aurora, Secrets Manager, TLS, S3 documented. |
| H3 | Access control | Documented; recommend auditing Lambda roles and log content. |
| H4 | Audit logging | request_id, triage_assessments.id, CloudWatch documented; who-accessed-what optional. |

For H5 (data retention & deletion) and H6 (BAA/DPA), see [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) §1 (policy/legal).
