# API test results (all 3 agents + MCPs)

**Purpose:** Single place to see what is working vs not. Re-run the curl commands below to refresh.

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
| **POST /hospitals** (with patient location) | Hospital Matcher + get_route → Routing agent → maps MCP | 200, each hospital has `directions_url`, `distance_km`, `duration_minutes` | 200, both hospitals have distance + directions_url | ✅ Yes |
| **POST /route** | Route Lambda → maps-target (get_directions) | 200, `distance_km`, `duration_minutes`, `directions_url` | 200, 10.62 km, 32 min, directions_url | ✅ Yes |

---

## How to fix failures

- **POST /route 502/500:** Run `python3 scripts/setup_agentcore_gateway.py` so **gateway_config** secret has `gateway_url` and `client_info`. Ensure **google_maps_api_key** is set in tfvars and Terraform applied so gateway_maps Lambda has the key.
- **POST /hospitals with location → 504:** Enrichment calls get_route per hospital; reduce `limit` (e.g. 2) or increase API Gateway/Lambda timeout. If directions_url is null, ensure **Routing runtime** has Gateway env vars: run `python3 scripts/enable_gateway_on_routing_runtime.py` after any routing agent deploy.
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

**Other Eka Lambda tools** (not exposed to triage model by default): `get_protocol_publishers`, `search_pharmacology`. To test those, use direct Lambda invoke or add tools to the Gateway/triage config.

**Quick curl (Eka medications + protocol):**

```bash
eval $(python3 scripts/load_api_config.py --exports)
export RMP_TOKEN=$(python3 scripts/get_rmp_token.py)
curl -s -X POST "${API_URL}triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" \
  -d '{"symptoms": ["fever", "patient wants Indian paracetamol brands"]}' | jq .recommendations
curl -s -X POST "${API_URL}triage" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" \
  -d '{"symptoms": ["acute diarrhoea", "ORS and dehydration protocol"]}' | jq .recommendations
```

