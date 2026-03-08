# Modules: What Is What & Plan Ahead

Single reference for the augmentation modules and how we plan to tackle them.

---

## 1. What is what (modules at a glance)

| Module | Name | What it is (one line) | Backend scope | Frontend scope |
|--------|------|------------------------|---------------|----------------|
| **A** | **Offline & resilience** | Offline triage and cached hospital/routing data for low-connectivity areas | Sync APIs (`GET /sync/download`, `POST /sync/upload`), cache payloads (hospitals ~50 km, routing, triage scenarios), offline-safe defaults | Real cache storage, offline triage flow, sync-on-reconnect (OfflineBanner exists) |
| **B** | **Multi-language & accessibility** | Multi-language and audio for illiterate users | Language/translation for symptoms & recommendations; TTS/audio API (e.g. Polly, `POST /language/audio`) | Language selector (e.g. 7 languages), vernacular symptom input, audio playback for recommendations |
| **C** | **RMP learning (skill + peer)** | **Backend complete.** Frontend Learning screen pending (frontend team). | Eka quiz: get_question, score_answer, points, leaderboard, GET /me ✅. Later: learning modules, peer consultation APIs | Learning screen (get question → submit answer → points, my score, leaderboard). Later: peer consult UI |
| **D** | **Collective intelligence** | Every case improves the system for all providers | Anonymized outcome ingestion, aggregation, protocol/pattern updates, optional outbreak signals; read APIs (e.g. regional insights) | Optional dashboard or “network insights”; can start backend-only |

---

## 2. Plan ahead (status and next steps)

| Module | Status | Plan ahead |
|--------|--------|------------|
| **A. Offline & resilience** | Not started | **Future.** Full implementation (backend + frontend) is multi-day. When we start: design/contract first, then sync API + cache content, then frontend cache + offline flow. |
| **B. Multi-language & accessibility** | Not started | **Future.** Full implementation (i18n + TTS + frontend) is multi-day. When we start: language/translation API and audio API, then frontend language selector and audio playback. |
| **C. RMP learning** | **Backend done** | **Backend complete.** Frontend: Learning screen owned by frontend team — see [RMP-LEARNING-API.md](frontend/RMP-LEARNING-API.md). **Later:** peer-to-peer (consultation request/session). |
| **D. Collective intelligence** | Not started | **Future.** Depends on real usage/outcome data; benefits from A–C. When we start: outcome ingestion + aggregation, then optional insights API and dashboard. |

---

## 3. Implementation order (when we do them)

1. **C** — RMP learning (**backend complete** ✅; frontend team doing Learning screen).  
2. **A** — Offline & resilience (future).  
3. **B** — Multi-language & accessibility (future).  
4. **D** — Collective intelligence (future).  

**After modules (last):** Web app deploy + frontend–backend integration → Comprehensive E2E testing (web + mobile).

---

## 4. References

- Full scope and grouping: [NEW-MODULE-RMP-AUGMENTATION.md](backend/NEW-MODULE-RMP-AUGMENTATION.md)
- Current sequence and phases: [ROADMAP-NEXT.md](ROADMAP-NEXT.md), [NEXT-SESSION.md](backend/NEXT-SESSION.md)
- RMP Learning API (frontend): [RMP-LEARNING-API.md](frontend/RMP-LEARNING-API.md)
