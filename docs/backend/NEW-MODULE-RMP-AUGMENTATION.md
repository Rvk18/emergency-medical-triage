# New Module: RMP Augmentation & Accessibility (grouped scope)

**Purpose:** Capture the five capability areas we have not yet implemented, group them for development, and define implementation order. Once this module is in progress, we proceed to AC-3 re-test → web app deploy → comprehensive E2E testing.

**References:** [design.md](./design.md), [requirements.md](./requirements.md), README.md § Our Solution / Key Features.

---

## 1. Confirmed: untouched areas

| # | Capability | In design/requirements? | Backend implemented? | Frontend |
|---|------------|------------------------|----------------------|----------|
| 1 | **Continuous skill building** — Personalized medical education that improves RMP capabilities over time | ✅ design.md, requirements.md | ❌ No | Mobile: LearningScreen stub, `getLearningModules()` placeholder |
| 2 | **Collective intelligence** — Every case improves the system for all providers across the network | ✅ design.md, requirements.md | ❌ No | Planned in workflow; no APIs |
| 3 | **Peer-to-peer learning** — Virtual medical college connecting isolated RMPs with experienced practitioners | ✅ design.md, requirements.md | ❌ No | Planned; no APIs |
| 4 | **Multi-language and accessibility** — Including audio for illiterate users | ✅ requirements.md §4, design.md §8 | ❌ No | Language/audio in mobile plan; no backend |
| 5 | **Offline triage and cached hospital/routing data** | ✅ requirements.md §9, design.md Properties 12–13 | ❌ No sync/cache APIs | Mobile: OfflineBanner, offline state; no real cache or sync |

**Conclusion:** All five are correctly identified as not yet implemented. Design and frontend stubs exist; backend APIs and full E2E flows are missing.

---

## 2. Grouping for implementation

We group by **theme** so that related backend and frontend work can be done together.

### Group A: Offline & resilience  
**Offline triage and cached hospital/routing data**

- **Why first:** Unblocks low-connectivity deployment; high impact for rural RMPs.
- **Backend:** Sync endpoints (e.g. `POST /sync/upload`, `GET /sync/download`), cache payloads (hospitals 50 km, routing, common triage scenarios), offline-safe defaults.
- **Frontend:** Already has OfflineBanner; add real cache storage, offline triage flow, sync-on-reconnect.
- **Docs:** requirements.md §9 (Offline), design.md Properties 12–13.

### Group B: Multi-language & accessibility  
**Multi-language and audio for illiterate users**

- **Why second:** Broad accessibility; audio is critical for non-readers.
- **Backend:** Language selection and/or translation for symptoms/recommendations; TTS or audio URL API (e.g. `POST /language/audio` or integrate Polly).
- **Frontend:** Language selector (7 languages), vernacular symptom input, audio playback for recommendations and instructions.
- **Docs:** requirements.md §4, design.md §8 Multi-Language Support.

### Group C: RMP learning (skill building + peer-to-peer)  
**Continuous skill building** and **Peer-to-peer learning**

- **Why together:** Both are “RMP education”; peer learning can use the same RMP identity and later feed collective intelligence.
- **Backend:**  
  - **Skill building:** Learning modules API (e.g. `GET /rmp/learning/modules`), optional competency/skills store, progress.  
  - **Peer-to-peer:** RMP profiles, consultation request/match, session or chat (e.g. `POST /rmp/consultation/request`, session endpoint).
- **Frontend:** Learning screen (mobile has stub), micro-learning UI; peer consult UI (request help, view sessions).
- **Docs:** design.md RMP Augmentation Engine, Collective Intelligence (peer consultation).

### Group D: Collective intelligence  
**Every case improves the system for all providers**

- **Why last:** Depends on real usage and outcome data; benefits from Groups A–C being in place.
- **Backend:** Anonymized outcome ingestion (e.g. triage + outcome), aggregation, protocol/pattern updates, optional outbreak signals; read APIs for “regional insights” or protocol updates.
- **Frontend:** Optional dashboard or “network insights” for RMPs; can start backend-only.
- **Docs:** design.md § Collective Intelligence Network, requirements.md §13.

---

## 3. Implementation order: **C first**, then A → B → D

We start with **Group C (RMP learning)** using a simple, high-value design: Eka MCP for questions, AgentCore to score answers, points + leaderboard. Then **A → B → D**.

| Order | Group | Scope | Outcome |
|-------|--------|--------|---------|
| **1** | **C. RMP learning (skill + peer)** | Eka MCP → questions; AgentCore → score answer → points; gamification + leaderboard | Quiz flow + top scores; peer can come later |
| **2** | **A. Offline & resilience** | Sync APIs, cache download (hospitals, routing, triage scenarios), offline defaults | Offline triage and cached data work end-to-end |
| **3** | **B. Multi-language & accessibility** | Language/translation + audio API; frontend language + audio playback | Multi-language and audio for illiterate users |
| **4** | **D. Collective intelligence** | Outcome aggregation, protocol updates, optional insights API | System improves from every case |

---

## 4. Group C (RMP Learning) — Eka quiz + gamification (start here)

**Idea:** Use Eka MCP for content → ask questions → AgentCore scores the answer → add points → gamify → track top scores.

### Flow

1. **Get question:** Backend (or AgentCore) calls Eka: `search_protocols` / `search_pharmacology` / `get_protocol_publishers` for a topic → form a short quiz question + reference answer (e.g. “What is the first step in fever protocol?”). Return question to client (web/mobile).
2. **Submit answer:** Client sends RMP’s answer (e.g. `POST /rmp/learning/submit-answer` with `question_id`, `answer`). Backend invokes AgentCore with (question, reference_answer, user_answer) → model returns points (e.g. 0–10) + short feedback.
3. **Points + persistence:** Add points to RMP’s total; store in DB (e.g. `rmp_scores`, `learning_answers` in Aurora).
4. **Gamification:** Leaderboard: `GET /rmp/learning/leaderboard` (top scores, optional period). Optional: badges, streaks, levels later.

### Building blocks

| Piece | What |
|-------|------|
| **Eka MCP** | Already there: `search_protocols`, `search_pharmacology`, `get_protocol_publishers`, `search_medications`. Use to generate question content. |
| **AgentCore** | New “RMP Quiz” agent (or two flows): (1) given Eka content → return one question + reference answer; (2) given (question, reference, user_answer) → return points + feedback. |
| **Backend API** | `GET /rmp/learning/question` (topic or random), `POST /rmp/learning/submit-answer`, `GET /rmp/learning/leaderboard`, `GET /rmp/learning/me` (my score). |
| **Persistence** | Aurora: e.g. `rmp_scores(rmp_id, total_points, updated_at)`, `learning_answers(id, rmp_id, question_ref, user_answer, points, created_at)`. |
| **Auth** | Use same RMP auth (Cognito / session) so points are per RMP. |

### Tasks (to implement)

- [x] **AgentCore RMP Quiz agent:** Done: `agentcore/agent/rmp_quiz_agent.py` (get_question + score_answer).
- [x] **Lambda + API:** POST /rmp/learning with action get_question | score_answer. Leaderboard/me when DB added.
- [ ] **Aurora schema:** `rmp_scores`, `learning_answers` (migration).
- [x] **Policy:** Eka tools in Gateway; run `enable_gateway_on_rmp_quiz_runtime.py` after deploy.
- [ ] **Frontend (web/mobile):** Call POST /rmp/learning; leaderboard when DB ready.

Peer-to-peer (e.g. “ask an expert”) can be a later extension once this flow works.

---

## 5. Checklist (to be updated as we implement)

- [x] **Group C (first slice):** RMP learning — Eka quiz (get_question + score_answer) + POST /rmp/learning deployed and tested. DB + leaderboard + frontend next; then peer-to-peer later.
- [ ] **Group A:** Offline & resilience — sync + cache APIs; frontend cache + offline flow
- [ ] **Group B:** Multi-language & accessibility — language + audio APIs; frontend i18n + audio
- [ ] **Group D:** Collective intelligence — outcome aggregation + protocol/insights

After this module (or incrementally), proceed to **AC-3 re-test** → **Web app deploy + integration** → **Comprehensive E2E testing (web + mobile)**.

---

## 6. Implemented — deploy and test (Group C first slice)

- **agentcore/agent/gateway_client.py:** `get_protocol_publishers_via_gateway()`, `search_pharmacology_via_gateway()`.
- **agentcore/agent/rmp_quiz_agent.py:** Agent with get_question (Eka) and score_answer (points + feedback).
- **src/rmp_learning/:** Lambda + POST /rmp/learning. Body: `{"action": "get_question", "topic": "..."}` or `{"action": "score_answer", "question", "reference_answer", "user_answer"}`.
- **infrastructure:** rmp_learning.tf, api_gateway.tf (POST /rmp/learning), variables (rmp_quiz_agent_runtime_arn), build_rmp_learning_lambda.sh, enable_gateway_on_rmp_quiz_runtime.py.

**Deploy:** First-time deploy: set `agent_id: null` and `agent_arn: null` for `rmp_quiz_agent` in `.bedrock_agentcore.yaml` so the toolkit calls **CreateAgentRuntime** (UpdateAgentRuntime returns AccessDenied when the runtime does not exist). After a successful deploy, the toolkit writes the new runtime ID/ARN back. Then add the runtime ARN to `terraform.tfvars`, run `enable_gateway_on_rmp_quiz_runtime.py`, and `terraform apply`. **Tested:** get_question and score_answer return 200; first request may 504 (cold start), retry once. See [RMP-LEARNING-COMPLETE-RUNBOOK.md](./RMP-LEARNING-COMPLETE-RUNBOOK.md) for full steps.

**Still to do:** Aurora rmp_scores/learning_answers, GET leaderboard, GET me, frontend.
