# What to work on next (next session)

**Branch to create:** Start from `main` (after merge), then create a new feature branch, e.g. `feature/ac4-continue` or `feature/roadmap-post-ac4`.

**Current state (as of merge):**
- **AC-4 routing pipeline is working:** POST /route returns stub (`distance_km`, `duration_minutes`, `directions_url`, `stub: true`) when Google Maps API key is not set. Full flow: RMP auth → Route Lambda → AgentCore Gateway (OAuth + MCP 2025-03-26) → maps-target___get_directions → Maps Lambda.
- **Triage, Hospitals, Route** all tested with curl; see [TESTING-Pipeline-curl.md](./TESTING-Pipeline-curl.md). Use `python3 scripts/get_rmp_token.py` for token (not `python` on macOS).

---

## Immediate next steps (pick one or more)

1. **Enable real Google Maps directions**
   - Add Google Maps API key to Secrets Manager (secret name in `GOOGLE_MAPS_CONFIG_SECRET_NAME`; shape `{"api_key":"YOUR_KEY"}`). See [GOOGLE-MAPS-ACCOUNT-SETUP.md](../infrastructure/GOOGLE-MAPS-ACCOUNT-SETUP.md).
   - Re-test POST /route; should return real `distance_km`, `duration_minutes`, `directions_url`.

2. **Eka validation (ROADMAP E1–E5)**
   - Confirm Eka Gateway returns useful data vs stub; document. See [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) §3.

3. **Guardrails & compliance (AC-4 scope)**
   - G1–G3 (input/output validation, safety prompts), Policy. See [AC4-Routing-Identity-Design.md](./AC4-Routing-Identity-Design.md) and [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) §2.

4. **HIPAA / health data (H1–H4)**
   - Document PHI scope, encryption, access, audit. See [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) §1.

---

## Key references

| Doc | Purpose |
|-----|--------|
| [TODO.md](./TODO.md) | Backend TODO and phase status |
| [ROADMAP-after-AC4.md](./ROADMAP-after-AC4.md) | Post AC-4 roadmap (Eka, HIPAA, guardrails) |
| [TESTING-Pipeline-curl.md](./TESTING-Pipeline-curl.md) | Curl tests for triage → hospitals → route |
| [agentcore-gateway-manual-steps.md](./agentcore-gateway-manual-steps.md) | Gateway setup; use `python3` for scripts |
| [GOOGLE-MAPS-ACCOUNT-SETUP.md](../infrastructure/GOOGLE-MAPS-ACCOUNT-SETUP.md) | Google Maps API key setup |

---

## Notes from this session

- **Gateway OAuth:** If setup script is run again and “Gateway already exists, reusing”, the script now updates the Gateway authorizer to the current OAuth so tokens from the secret work (avoids 401 Invalid Bearer token).
- **Route Lambda:** Uses scope from gateway-config secret (`client_info.scope`, e.g. `emergency-triage-hospitals/invoke`), MCP version `2025-03-26`, and http.client to call the Gateway so response body is always captured on 4xx.
- **Python:** Use `python3` in docs and CLI; `python` may not be on PATH (e.g. macOS).
