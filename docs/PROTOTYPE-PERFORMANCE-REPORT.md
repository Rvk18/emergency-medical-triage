# Prototype Performance — 1-slide summary

**Environment:** AWS dev (us-east-1), API Gateway + Lambda + Bedrock AgentCore. Cold start included in first request; retry if 504.

| Endpoint / flow           | Typical latency | Notes                    |
|---------------------------|-----------------|---------------------------|
| **GET /health**           | < 200 ms        | No auth                   |
| **POST /triage**          | 3–6 s           | AgentCore + optional Eka  |
| **POST /hospitals**       | 2–5 s           | AgentCore + get_hospitals |
| **POST /route**           | 0.5–2 s         | Google Maps via Gateway   |
| **POST /rmp/learning**    | 3–6 s           | AgentCore + Aurora        |
| **GET /rmp/learning/me**  | < 500 ms        | Aurora only               |
| **E2E: triage → hospitals → route** | ~10–20 s | Full flow (warm)          |

- **Constraints:** API Gateway max 29 s; first request per Lambda may 504 (cold start)—retry once.
- **Reproduce:** `eval $(python3 scripts/load_api_config.py --exports)` then `curl -w "%{time_total}\n" -s ...` per endpoint (see [API-TEST-RESULTS.md](backend/API-TEST-RESULTS.md)).
