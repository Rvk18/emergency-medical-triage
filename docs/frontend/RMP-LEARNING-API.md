# RMP Learning API – frontend integration

**Audience:** Frontend (web and mobile) teams implementing the Learning / quiz screen.  
**Purpose:** Contract and examples for **Eka quiz** (get question → submit answer → points + leaderboard). Same auth as triage/hospitals/route: **Cognito Id Token**.

**OpenAPI:** Full spec in [../openapi.yaml](../openapi.yaml) – paths `/rmp/learning`, `/rmp/learning/me`, `/rmp/learning/leaderboard`.

---

## Base URL and auth

- **Base URL:** Same as other APIs. From Terraform / `load_api_config`: `API_URL` (e.g. `https://xxxx.execute-api.us-east-1.amazonaws.com/dev/`). No trailing slash when appending path.
- **Auth:** All RMP Learning endpoints require **Cognito Id Token**. Header: `Authorization: Bearer <IdToken>`. Same sign-in as [RMP-AUTH.md](./RMP-AUTH.md).

---

## Endpoints summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| **/rmp/learning** | POST | Get a quiz question (**get_question**) or submit answer for scoring (**score_answer**). Points are persisted for the signed-in RMP. |
| **/rmp/learning/me** | GET | Current RMP's **total_points** and **rank** (1-based). Use for “My score” or profile. |
| **/rmp/learning/leaderboard** | GET | Top N RMPs by total points. Query `?limit=20` (default 20, max 100). |

---

## 1. POST /rmp/learning – get question

**Request:**

- **URL:** `{BASE_URL}/rmp/learning`
- **Headers:** `Content-Type: application/json`, `Authorization: Bearer <IdToken>`
- **Body:**

```json
{
  "action": "get_question",
  "topic": "fever protocol"
}
```

**Response:** `200`

```json
{
  "question": "What is the maximum daily dose of paracetamol for fever management in adults?",
  "reference_answer": "The maximum daily dose of paracetamol for adults is 4 grams per day...",
  "topic": "fever protocol"
}
```

- **Frontend use:** Show `question` to the user; store `reference_answer` and `question` for the next step (score_answer). You can suggest topics (e.g. “fever protocol”, “diabetes management”, “acute diarrhoea”) or leave topic generic.

---

## 2. POST /rmp/learning – score answer

**Request:**

- **URL:** `{BASE_URL}/rmp/learning`
- **Headers:** `Content-Type: application/json`, `Authorization: Bearer <IdToken>`
- **Body:** Use the same `question` and `reference_answer` from the last get_question response; send the user’s answer in `user_answer`.

```json
{
  "action": "score_answer",
  "question": "What is the maximum daily dose of paracetamol for fever management in adults?",
  "reference_answer": "The maximum daily dose of paracetamol for adults is 4 grams per day...",
  "user_answer": "4 grams per day, 0.5 to 1 gram every 4–6 hours"
}
```

**Response:** `200`

```json
{
  "points": 9,
  "feedback": "Correct maximum dose and dosing interval, but missing important safety information about reduced dose for alcoholics."
}
```

- **Frontend use:** Show `points` (0–10) and `feedback`. Points are automatically added to the RMP’s total and appear in **/rmp/learning/me** and **/rmp/learning/leaderboard**. Then offer “Next question” (call get_question again) or “View leaderboard”.

**Notes:**

- First request after cold start may return **504**; retry once.
- If the backend is unavailable, you may get **500**; show a generic error and allow retry.

---

## 3. GET /rmp/learning/me – my score

**Request:**

- **URL:** `{BASE_URL}/rmp/learning/me`
- **Headers:** `Authorization: Bearer <IdToken>`
- **Body:** None.

**Response:** `200`

```json
{
  "total_points": 42,
  "rank": 3
}
```

- **rank** is 1-based (1 = top). **rank** may be `null` if the user has not answered any question yet.
- **Frontend use:** “Your score: 42 points · Rank #3” or “You haven’t answered any questions yet” when `rank` is null.

---

## 4. GET /rmp/learning/leaderboard

**Request:**

- **URL:** `{BASE_URL}/rmp/learning/leaderboard` or `{BASE_URL}/rmp/learning/leaderboard?limit=10`
- **Headers:** `Authorization: Bearer <IdToken>`
- **Body:** None.

**Response:** `200`

```json
{
  "leaderboard": [
    { "rmp_id": "abc-123-cognito-sub", "total_points": 120, "rank": 1 },
    { "rmp_id": "def-456", "total_points": 95, "rank": 2 },
    { "rmp_id": "ghi-789", "total_points": 42, "rank": 3 }
  ]
}
```

- **rmp_id** is the Cognito sub (opaque). Do not display raw `rmp_id`; use “Rank 1”, “Rank 2”, or a display name if you have one from your user profile.
- **Frontend use:** List “Rank · Points” (e.g. “#1 – 120 pts”). Highlight the current user’s row if you match `rmp_id` to the token’s sub (from decode or a separate “me” call).

---

## Suggested Learning screen flow

1. **Entry:** Button “Start quiz” or “Practice” → call **get_question** with a chosen topic (or default “general”).
2. **Show question** from response; user types or selects answer.
3. **Submit** → call **score_answer** with stored `question`, `reference_answer`, and `user_answer`. Show **points** and **feedback**.
4. **Next:** “Next question” → get_question again; or “My score” → **GET /rmp/learning/me**; or “Leaderboard” → **GET /rmp/learning/leaderboard**.

---

## Error handling

| Status | Meaning | Frontend action |
|--------|--------|------------------|
| **400** | Invalid body (e.g. missing `action`, bad JSON) | Show validation message. |
| **401** | Missing or invalid token | Refresh token or redirect to sign-in ([RMP-AUTH.md](./RMP-AUTH.md)). |
| **500** | Server or agent error | Show “Something went wrong”, allow retry. |
| **504** | Timeout (often first request) | Retry once; then show “Service busy, try again”. |

---

## References

- [API-Integration-Guide.md](./API-Integration-Guide.md) – Base URL, auth, triage → hospitals → route.
- [RMP-AUTH.md](./RMP-AUTH.md) – Cognito sign-in and Id Token.
- [../openapi.yaml](../openapi.yaml) – Full OpenAPI 3 spec including RMP Learning schemas.
