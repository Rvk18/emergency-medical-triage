# API test results (all 3 agents + MCPs)

**Purpose:** Single place to see what is working vs not. Use this for **comprehensive endpoint testing** before moving to the next phase (e.g. web app integration). Re-run the curl commands below to refresh the status table.

---

## Comprehensive endpoint testing (run before Phase 5)

Run all of the following in order and record results in the **Status table** below. From project root:

```bash
eval $(python3 scripts/load_api_config.py --exports)
export RMP_TOKEN=$(python3 scripts/get_rmp_token.py)
BASE="${API_URL%/}"
# 1. Health
curl -s -w "\nHTTP:%{http_code}" "${BASE}/health" && echo ""
# 2. Triage
curl -s -w "\nHTTP:%{http_code}" -X POST "${BASE}/triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"symptoms":["chest pain"],"age_years":50,"sex":"M"}' && echo ""
# 3. Hospitals (no location)
curl -s -w "\nHTTP:%{http_code}" -X POST "${BASE}/hospitals" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"severity":"high","recommendations":["Emergency department"],"limit":2}' && echo ""
# 4. Hospitals (with location) – use limit=1 to avoid 504 (API Gw 29s limit)
curl -s -w "\nHTTP:%{http_code}" --max-time 45 -X POST "${BASE}/hospitals" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"severity":"high","recommendations":["Emergency department"],"limit":1,"patient_location_lat":12.97,"patient_location_lon":77.59}' && echo ""
# 5. Route
curl -s -w "\nHTTP:%{http_code}" -X POST "${BASE}/route" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"origin":{"lat":12.97,"lon":77.59},"destination":{"lat":12.8967,"lon":77.5982}}' && echo ""
```

Optional: run **Eka MCP tests** (see table in § Eka MCP tests) to confirm Indian medications and protocols. Once all rows in the Status table are ✅, proceed to the next phase (e.g. deploy web app + frontend integration).

---

## One curl per endpoint

From project root, set env then run each:

```bash
eval $(python3 scripts/load_api_config.py --exports)
export RMP_TOKEN=$(python3 scripts/get_rmp_token.py)
BASE="${API_URL%/}"
```

| # | Endpoint | Curl | Notes |
|---|----------|------|--------|
| 1 | **GET /health** | `curl -s -w "\n%{http_code}" "${BASE}/health"` | No auth. |
| 2 | **POST /triage** | `curl -s -w "\n%{http_code}" -X POST "${BASE}/triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"symptoms":["chest pain"],"age_years":50,"sex":"M"}'` | Triage agent + optional Eka MCP. |
| 3 | **POST /hospitals** (no location) | `curl -s -w "\n%{http_code}" -X POST "${BASE}/hospitals" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"severity":"high","recommendations":["Emergency department"],"limit":2}'` | Hospital Matcher agent + get_hospitals MCP. |
| 4 | **POST /hospitals** (with patient location) | `curl -s -w "\n%{http_code}" -X POST "${BASE}/hospitals" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"severity":"high","recommendations":["Emergency department"],"limit":2,"patient_location_lat":12.97,"patient_location_lon":77.59}'` | Uses get_route (Routing agent → maps MCP) for directions_url per hospital; can timeout if enrichment is slow. |
| 5 | **POST /route** | `curl -s -w "\n%{http_code}" -X POST "${BASE}/route" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"origin":{"lat":12.97,"lon":77.59},"destination":{"lat":12.8967,"lon":77.5982}}'` | Route Lambda → Gateway maps-target → gateway_maps Lambda (Google Maps). |

---

## Status table (working vs not)

| Endpoint | Agent / MCP | Expected | Last run result | Working? |
|----------|-------------|----------|-----------------|----------|
| **GET /health** | — | 200, `{"status":"ok",...}` | 200 | ✅ Yes |
| **POST /triage** | Triage AgentCore, optional Eka MCP | 200, `severity`, `recommendations`, `session_id` | 200, severity critical | ✅ Yes |
| **POST /hospitals** (no location) | Hospital Matcher AgentCore, get_hospitals MCP | 200, `hospitals` (e.g. blr-apollo-1), `safety_disclaimer` | 200, real hospitals | ✅ Yes |
| **POST /hospitals** (with patient location) | Hospital Matcher + get_route → Routing agent → maps MCP | 200, each hospital has `directions_url`, `distance_km`, `duration_minutes` | 504 (API Gateway 29s timeout; use limit=1 may still timeout) | ⚠️ See **Test 4 RCA** |
| **POST /route** | Route Lambda → maps-target (get_directions) | 200, `distance_km`, `duration_minutes`, `directions_url` | 200, 10.62 km, 32 min, directions_url | ✅ Yes |
| **Eka get_protocol_publishers** | Direct Lambda or via triage | 200 / publishers list | — | See § New Eka tools |
| **Eka search_pharmacology** | Direct Lambda or via triage | 200 / pharmacology result | — | See § New Eka tools |

## Test 4 RCA (POST /hospitals with location → 504)

**Root cause:** AWS API Gateway has a **hard limit of 29 seconds** for integration timeout. The Hospital Matcher Lambda invokes the AgentCore runtime, which (when `patient_location_lat/lon` are provided) calls `get_route` for each hospital to add `distance_km`, `duration_minutes`, and `directions_url`. With `limit=2`, the total agent work can exceed 29 seconds, so API Gateway returns **504 Gateway Timeout** before the Lambda completes. Increasing the Lambda timeout (e.g. to 120s) does **not** extend the API Gateway limit.

**Mitigation:** For the comprehensive test, use `limit=1` so the request often completes within 29s, or accept 504 for `limit≥2`. A longer-term fix would be to return hospitals without enrichment first (200), then enrich asynchronously or via a separate call.

---

- **POST /route 502/500:** Run `python3 scripts/setup_agentcore_gateway.py` so **gateway_config** secret has `gateway_url` and `client_info`. Ensure **google_maps_api_key** is set in tfvars and Terraform applied so gateway_maps Lambda has the key. If Policy is ENFORCE and route returns "Tool Execution Denied", the Cedar action/resource at request time may not match the policy; use `python3 scripts/setup_agentcore_policy.py --log-only` so route works, then check Observability for the actual Cedar request.
- **POST /hospitals with location → 504:** **RCA:** API Gateway has a **maximum integration timeout of 29 seconds**. The Hospital Matcher agent (with patient location) calls get_route per hospital to enrich with distance/directions; with limit=2 this can exceed 29s. **Fix:** Use `limit=1` for the test, or accept 504 for limit≥2. Lambda timeout (60s) does not extend the API Gateway integration limit.
- **401 on any POST:** Get a fresh RMP token: `RMP_TOKEN=$(python3 scripts/get_rmp_token.py)`.

---

## Eka MCP tests (POST /triage with Eka-triggering prompts)

Eka is **not** a separate REST API; it is used by the **Triage agent** via the Gateway when the user asks for Indian medications or treatment protocols. The Gateway calls the Eka Lambda tools: `search_medications` (→ `search_indian_medications`), `search_protocols` (→ `search_treatment_protocols`). Full test cases: [TESTING-Gateway-Eka.md](./TESTING-Gateway-Eka.md) §4b.

**Prereq:** Triage runtime has Gateway env vars; run `python3 scripts/enable_eka_on_runtime.py` after triage deploy.

| Test | Eka feature | Symptoms (request) | Last run | Pass criteria |
|------|------------|-------------------|----------|----------------|
| **M1** | search_indian_medications | `["fever", "patient wants Indian paracetamol brands"]` | 200 | ✅ Indian brands in recommendations (e.g. Crocin, Calpol, Dolo, Paracip) |
| **M2** | search_indian_medications | `["sore throat", "need Indian amoxicillin or equivalent"]` | 200 | ✅ 200; Indian brands may or may not appear (model-dependent) |
| **M5** | search_indian_medications | `["diabetes", "patient asks for metformin brands available in India"]` | 200 | ✅ Indian metformin brands (e.g. Glycomet, Diabex, Glucophage) |
| **P1** | search_treatment_protocols | `["fever", "what is the recommended treatment protocol for fever?"]` | 200 | ✅ Protocol-style steps (monitor temp, dosing, danger signs) |
| **P2** | search_treatment_protocols | `["high blood sugar", "diabetes management protocol"]` | 200 | ✅ Protocol-style guidance (glucose check, DKA signs, referral) |
| **P4** | search_treatment_protocols | `["acute diarrhoea", "ORS and dehydration protocol"]` | 200 | ✅ ORS/WHO-ORS, dehydration signs, zinc supplementation |
| **C1** | both | `["fever and cough", "Indian paracetamol brands and fever protocol"]` | 200 | ✅ Indian brands (Crocin, Dolo) + protocol steps |

**Other Eka Lambda tools** (now on Gateway and in policy): `get_protocol_publishers`, `search_pharmacology`. Test via **POST /triage** with prompts below, or **direct Lambda invoke** (curl examples in § New Eka tools: get_protocol_publishers, search_pharmacology).

**Quick curl (Eka medications + protocol):**

```bash
eval $(python3 scripts/load_api_config.py --exports)
export RMP_TOKEN=$(python3 scripts/get_rmp_token.py)
curl -s -X POST "${API_URL}triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" \
  -d '{"symptoms": ["fever", "patient wants Indian paracetamol brands"]}' | jq .recommendations
curl -s -X POST "${API_URL}triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" \
  -d '{"symptoms": ["acute diarrhoea", "ORS and dehydration protocol"]}' | jq .recommendations
```

---

## New Eka tools: get_protocol_publishers, search_pharmacology

These two tools are on the Gateway (Eka target) and in the policy allowlist. Test them via **POST /triage** (if the triage agent calls them) or **direct Lambda invoke**.

### Via POST /triage (prompts that may trigger the tools)

| Tool | Test | Pass criteria |
|------|------|---------------|
| **get_protocol_publishers** | `curl -s -w "\n%{http_code}" -X POST "${BASE}/triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"symptoms":["diabetes","which protocol publishers are available for treatment protocols?"],"age_years":45,"sex":"F"}'` | 200; recommendations may reference publishers (ICMR, RSSDI) |
| **search_pharmacology** | `curl -s -w "\n%{http_code}" -X POST "${BASE}/triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"symptoms":["fever","what is paracetamol dosing and safety in pregnancy?"],"age_years":30,"sex":"F"}'` | 200; recommendations may include dosing/safety (NFI-style) |

Use same `eval` and `RMP_TOKEN` as in § Comprehensive endpoint testing; `BASE="${API_URL%/}"`.

### Via direct Lambda invoke (AWS CLI)

```bash
eval $(python3 scripts/load_api_config.py --exports)
# get_protocol_publishers (no extra params)
aws lambda invoke --function-name "$GATEWAY_EKA_LAMBDA_ARN" --payload '{"tool":"get_protocol_publishers"}' eka_out.json --cli-binary-format raw-in-base64-out && cat eka_out.json | jq .

# search_pharmacology (query required for meaningful result)
aws lambda invoke --function-name "$GATEWAY_EKA_LAMBDA_ARN" --payload '{"tool":"search_pharmacology","query":"Paracetamol"}' eka_out.json --cli-binary-format raw-in-base64-out && cat eka_out.json | jq .
```

Run from project root so `eka_out.json` is written in the repo (or use `/tmp/eka_out.json` if you prefer). Expected: JSON body with `publishers` (get_protocol_publishers) or pharmacology results (search_pharmacology). Check the output file for Eka API errors.
