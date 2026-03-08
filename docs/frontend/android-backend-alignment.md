# Android Frontend – Backend API Alignment

**Purpose:** List backend APIs/features and what was missing in the Android app before alignment; what was added.

---

## Backend API Summary (from API-Integration-Guide.md)

| Endpoint      | Method | Auth | Purpose |
|---------------|--------|------|---------|
| **/health**   | GET    | No   | Liveness check |
| **/triage**   | POST   | Yes  | Submit symptoms/vitals → severity, recommendations, session_id |
| **/hospitals**| POST   | Yes  | Get hospital list by severity + recommendations; optional patient lat/lon |
| **/route**    | POST   | Yes  | Real directions: origin + destination → distance_km, duration_minutes, directions_url |

Auth: `Authorization: Bearer <IdToken>` (Cognito) for all POST endpoints.

---

## What Was Missing (Before Alignment)

1. **GET /health**
   - No API method, no call from app, no UI to check API status.

2. **POST /triage**
   - **Implemented** but missing: `session_id` in request and response (needed for /hospitals and /route).
   - No `Authorization: Bearer` header (401 on protected backend).

3. **POST /hospitals**
   - **Not implemented.** App used mock data only (`HospitalRepository` with hardcoded list).
   - No use of triage result (severity, recommendations, session_id) when loading hospitals.

4. **POST /route**
   - **Not implemented.** App used mock route steps only.
   - Backend returns `distance_km`, `duration_minutes`, `directions_url`; app did not call API or open Google Maps.

5. **Auth**
   - Login is mock (no Cognito). No Bearer token attached to Retrofit calls.

6. **Flow**
   - Triage result was not passed to the Hospitals tab; hospitals loaded mock data with no triage context.

---

## What Was Added (Alignment)

- **GET /health:** `HealthApi`, `HealthRepository`, "Check API status" row in More screen; shows API OK or error message.
- **session_id:** In `TriageRequestDto` / `TriageResponseDto` and `TriageResult`; generated at flow start (UUID) in `TriageViewModel`; passed to POST /triage and (via `TriageSessionHolder`) to POST /hospitals.
- **POST /hospitals:** `HospitalsApi`, `HospitalsRequestDto`/`HospitalsResponseDto`, `HospitalRepository.getMatches()` calls backend when `TriageSessionHolder` has severity/recommendations (set when user taps "Proceed to hospital matching"); fallback to mock when no triage context.
- **POST /route:** `RouteApi`, `RouteRequestDto`/`RouteResponseDto`, `HospitalRepository.getRoute(origin, dest)`; `HospitalsViewModel.selectHospital()` fetches route when hospital has lat/lon; Navigation screen shows distance, duration, and **"Open in Google Maps"** button using `directions_url` (Intent.ACTION_VIEW).
- **Auth interceptor:** `AuthInterceptor` adds `Authorization: Bearer <token>` from `UserPreferences.authToken` for all requests (works with mock token; replace with Cognito Id Token when integrating real auth).
- **Buttons:** "Check API status" (More), "Proceed to hospital matching" saves triage to session holder and navigates to Hospitals, "Navigate" on a hospital loads route and shows "Open in Google Maps" when API returns directions_url.
