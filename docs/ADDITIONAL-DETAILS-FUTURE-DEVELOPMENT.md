# Additional Details & Future Development — 1–2 slides

Copy-paste bullets for your deck.

---

## Slide 1: Additional Details

- **Current scope:** AI triage (Bedrock AgentCore) + Eka Care (Indian drugs & protocols), hospital matching, Google Maps routing, RMP Learning (quiz, leaderboard), Cognito auth; web + Android MVP.
- **Guardrails:** Input/output validation (symptoms, vitals, severity, limits); safety prompts (“do not prescribe”, “emergency triage only”); AgentCore policy for tool allowlist.
- **Session continuity:** Optional `session_id` / `patient_id` across triage → hospitals → route for single-session flow.
- **Constraints:** API Gateway 29 s max; first Lambda request may 504 (cold start)—retry once; Eka optional (stub or live key).

---

## Slide 2: Future Development

- **Offline & resilience (A):** Sync APIs, cached hospitals/routes, offline triage for low-connectivity areas.
- **Multi-language & accessibility (B):** Vernacular UI, TTS/audio for recommendations, language selector.
- **RMP Learning (C):** Backend done; complete Learning screen on web/mobile; later: peer-to-peer consultation.
- **Collective intelligence (D):** Anonymized outcome ingestion, protocol/pattern updates, regional insights.
- **Compliance & scale:** PHI documentation, encryption/audit checklist, retention; optional Bedrock Guardrails, rate limiting; E2E tests + CI.
