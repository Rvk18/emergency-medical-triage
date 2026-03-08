# MedTriage AI — Android Mobile App

Emergency Medical Triage Android app (Kotlin, Jetpack Compose, Material 3). RMP/Healthcare Worker focus.

## Scope

- **Work only in:** this `frontend/mobile-android/` directory.
- **Do not edit:** `../web/` (web app), `../../src/` (backend), `../../infrastructure/`, or voice interface.
- **Design reference:** See `../../docs/frontend/mobile-mock-design-checklist.md` and `../../docs/frontend/android-mobile-plan.md`.

## Auth and API (Cognito + backend)

**Use Cognito for sign-in and send the Id Token on every protected API request.** See:

- **[MOBILE-COGNITO-API-AUTH.md](../../docs/frontend/MOBILE-COGNITO-API-AUTH.md)** – How to get User Pool ID / Client ID / API URL from Terraform, sign in with Cognito InitiateAuth, get the **Id Token** (not Access Token), and send **`Authorization: Bearer <IdToken>`** on all protected endpoints (triage, hospitals, route, rmp/learning). Includes public vs protected endpoints and token refresh.

The app implements **end-to-end Cognito auth**: sign-in with email/password via InitiateAuth, store **Id Token** and **Refresh Token**, and send **`Authorization: Bearer <IdToken>`** on every request to /triage, /hospitals, /route (via `AuthInterceptor`). See `AuthRepository.kt` and `MOBILE-COGNITO-API-AUTH.md`.

**Config:** Set `ApiConfig.COGNITO_CLIENT_ID` and `ApiConfig.BASE_URL` (and optionally `COGNITO_REGION`) to match your backend. From project root after `terraform apply`:  
`terraform -chdir=infrastructure output -raw cognito_app_client_id` and `terraform -chdir=infrastructure output -raw api_gateway_url`.

## Requirements

- Android Studio Ladybug (2024.2.1) or later, or CLI: JDK 17+, Android SDK 34.
- Run `./gradlew assembleDebug` to build.

## Phase 1 (current)

- Design system: theme (light/dark), severity colors, typography, spacing.
- App shell: top bar (title + role badge), bottom nav (Triage, Hospitals, Dashboard, More), offline banner.
- Placeholder screens per tab.

## Next phases

- Phase 2: Auth and language (login, session, 7-language selector).
- Phase 3: Core triage (4-step wizard, result, report, offline).
- Phase 4: Hospital match and routing.
- Phase 5: RMP dashboard, guidance, learning.
