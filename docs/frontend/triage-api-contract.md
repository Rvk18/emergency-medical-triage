# Triage API Contract (Backend ↔ Mobile)

**Real API base URL:** `https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev`  
**Triage endpoint:** `POST https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev/triage`

This doc matches the backend implementation and what the mobile app must send/receive.

---

## How the backend works

1. **API Gateway** forwards `POST /triage` to the **Triage Lambda**.
2. **Lambda** (`src/triage/api/handler.py`) parses JSON body into `TriageRequest`, calls `assess_triage(request)`.
3. **Core** (`src/triage/core/agent.py`) uses Bedrock (Agent or Converse API) with a tool `submit_triage_result`; the model returns severity, confidence, recommendations; if confidence < 85%, backend sets `force_high_priority: true`.
4. **Response** is validated with `TriageResult` Pydantic model and returned as JSON.

---

## Request (what the mobile app must send)

**Method:** `POST`  
**Headers:** `Content-Type: application/json`  
**Body:** JSON matching backend `TriageRequest`:

| Field        | Type           | Required | Notes |
|-------------|----------------|----------|--------|
| `symptoms`  | `string[]`     | **Yes**  | At least one symptom (e.g. `["chest pain", "shortness of breath"]`). Can come from app’s symptom step (e.g. `primarySymptoms` + `freeText` split into list). |
| `vitals`    | `object`       | No       | Key-value map of vital names to numbers. Backend accepts any `dict[str, float]`. Use same keys the AI expects, e.g. `bp` (systolic), `heart_rate`, `spo2`, `temp_c`, `respiratory_rate`, etc. |
| `age_years` | `number` (int) | No       | 0–150. Map from app’s `PatientInfo.age`. |
| `sex`       | `string`       | No       | Map from app’s `PatientInfo.gender`. |

**Example (matches your curl):**

```json
{
  "symptoms": ["chest pain", "shortness of breath"],
  "vitals": { "bp": 180, "heart_rate": 95 }
}
```

**Example with optional fields:**

```json
{
  "symptoms": ["fever", "cough"],
  "vitals": { "bp": 120, "heart_rate": 88, "spo2": 97, "temp_c": 38.5 },
  "age_years": 45,
  "sex": "M"
}
```

**Mobile → API mapping (when you wire real client):**

- **symptoms:** Build from `SymptomInput`: e.g. `primarySymptoms` + split `freeText` by comma/newline into a single list; ensure at least one string.
- **vitals:** From `VitalsInput` → e.g. `heart_rate` ← `heartRateBpm`, `bp` ← `bloodPressureSystolic` (or send both sys/dia if backend adds support), `spo2` ← `spo2Percent`, `temp_c` ← `temperatureCelsius`, `respiratory_rate` ← `respiratoryRatePerMin`.
- **age_years:** `PatientInfo.age`.
- **sex:** `PatientInfo.gender`.

---

## Response (what the mobile app receives)

**Success:** `200` with JSON body matching backend `TriageResult`:

| Field                 | Type      | Notes |
|-----------------------|-----------|--------|
| `severity`            | `string`  | One of: `"critical"`, `"high"`, `"medium"`, `"low"`. |
| `confidence`          | `number`  | 0.0–1.0 (e.g. 0.82). |
| `recommendations`     | `string[]`| List of action items. |
| `force_high_priority` | `boolean` | `true` when confidence < 85%; treat as high priority. |
| `safety_disclaimer`   | `string \| null` | Single disclaimer text. |

**Example (from your curl):**

```json
{
  "severity": "high",
  "confidence": 0.82,
  "recommendations": ["Activate emergency transport immediately — do not delay", "..."],
  "force_high_priority": true,
  "safety_disclaimer": "This is AI-assisted guidance. Seek professional medical care."
}
```

**Mobile model mapping (current app vs API):**

| Backend (API)           | Mobile (TriageResult in TriageModels.kt)     |
|-------------------------|----------------------------------------------|
| `severity`              | `SeverityLevel` (map string → enum)          |
| `confidence`            | `confidencePercent` (× 100, e.g. 0.82 → 82)  |
| `recommendations`       | `recommendedActions`                         |
| `force_high_priority`   | `flaggedForReview`                           |
| `safety_disclaimer`     | `safetyDisclaimers` (single item in list) or one string |
| *(not in API)*          | `emergencyId` (generate client-side or add to backend later) |

---

## Summary

- **Base URL:** `https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev`
- **Endpoint:** `POST /triage` → full URL: `https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev/triage`
- **Input:** `symptoms` (required, ≥1), `vitals` (optional dict), optional `age_years`, `sex`.
- **Output:** `severity`, `confidence`, `recommendations`, `force_high_priority`, `safety_disclaimer`.
- When integrating the real API in the app, map `SymptomInput`/`VitalsInput`/`PatientInfo` → request JSON, and response JSON → `TriageResult` (with `emergencyId` generated or from a future backend field).
