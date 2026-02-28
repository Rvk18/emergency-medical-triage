# MedTriage AI — Android Mobile App

Emergency Medical Triage Android app (Kotlin, Jetpack Compose, Material 3). RMP/Healthcare Worker focus.

## Scope

- **Work only in:** this `frontend/mobile-android/` directory.
- **Do not edit:** `../web/` (web app), `../../src/` (backend), `../../infrastructure/`, or voice interface.
- **Design reference:** See `../../docs/frontend/mobile-mock-design-checklist.md` and `../../docs/frontend/android-mobile-plan.md`.

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
