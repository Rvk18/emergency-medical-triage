# Estimated implementation cost per month

**Purpose:** Rough monthly cost for running the Emergency Medical Triage stack on AWS (dev or low-traffic production). Actual cost depends on traffic, Bedrock usage, and region.

---

## AWS components (us-east-1)

| Component | Configuration | Estimated monthly cost (low/medium usage) |
|-----------|----------------|-------------------------------------------|
| **NAT Gateway** | 1 NAT + EIP for Lambda VPC egress (Bedrock, etc.) | **~$32–35** (fixed: $0.045/hr + $0.045/GB processed) |
| **Aurora PostgreSQL Serverless v2** | 0.5–1 ACU (min 0.5, max 1) | **~$45–90** (~$0.12/ACU-hour × 730 hrs; scales with load) |
| **Lambda** | Health, Config, Triage, Hospital Matcher, Route, RMP Learning, Gateway Lambdas (Eka, Maps, Get Hospitals, Routing) | **~$2–10** (free tier covers 1M requests; beyond that ~$0.20/1M) |
| **API Gateway** | REST API, Cognito authorizer | **~$0–5** (first 1M calls free for 12 months; then $3.50/1M) |
| **Cognito User Pools** | RMP sign-in | **$0** (free tier 50k MAU) |
| **Secrets Manager** | ~6–8 secrets (RDS, Bedrock, Eka, Google Maps, API config, gateway, RMP test) | **~$3–4** ($0.40/secret/month) |
| **S3** | Main bucket + web bucket (static + APK) | **~$1–3** (storage + requests) |
| **CloudFront** | Web + APK (PriceClass_100) | **~$0–5** (free tier 1 TB egress; then low) |
| **Bedrock** | Converse API + AgentCore (triage, hospital matcher, routing, RMP quiz) | **~$20–150+** (per token / per request; scales with triage/learning volume) |
| **Bastion** (optional) | EC2 if `enable_bastion=true` | **~$5–15** (t3.micro or similar) |

---

## External / third-party

| Component | Notes | Estimated monthly cost |
|-----------|--------|------------------------|
| **Google Maps Platform** | Directions + Geocoding (India has higher free tier) | **$0** within India free tier (e.g. 70k requests); beyond that ~$1.50/1k events ([AC4-Product-Decisions.md](backend/AC4-Product-Decisions.md)) |
| **Eka Care API** | Indian drugs & protocols (if used) | Depends on Eka plan; often trial or usage-based |

---

## Estimated total per month

| Scenario | Range |
|----------|--------|
| **Dev / hackathon (low traffic)** | **~$110–200** (dominated by NAT + Aurora + Bedrock; Lambda/API Gateway/Cognito/S3/CloudFront in free tier or low) |
| **Low production (hundreds of sessions/month)** | **~$150–300** (Bedrock usage grows with triage/learning calls) |
| **Higher production** | **$300+** (scale Aurora ACU, Bedrock tokens, API Gateway, CloudFront; consider Reserved Capacity or savings plans for predictability) |

**Notes:**

- **NAT** is the largest fixed cost (~$32/mo). To reduce: use VPC Lambda without NAT where possible (e.g. config/health Lambdas are not in VPC), or consider NAT instances (cheaper but more ops).
- **Aurora Serverless v2** minimum 0.5 ACU runs 24/7; cost is relatively stable unless traffic spikes.
- **Bedrock** is the most variable: Converse and AgentCore invocations (triage, hospital match, routing, RMP quiz) charge per input/output token and per request. Set a budget alert in AWS Billing.
- **Google Maps**: Set a budget alert (e.g. $50/month) in Google Cloud; India free tier is generous for Routes/Geocoding.

---

## References

- [implementation-history.md](backend/implementation-history.md) – NAT cost note (~$32/month)
- [AC4-Product-Decisions.md](backend/AC4-Product-Decisions.md) – Google Maps cost and India free tier
- [GOOGLE-MAPS-ACCOUNT-SETUP.md](infrastructure/GOOGLE-MAPS-ACCOUNT-SETUP.md) – Budget alert recommendation
- [AWS Pricing Calculator](https://calculator.aws/) – Build a custom estimate from your Terraform resources
