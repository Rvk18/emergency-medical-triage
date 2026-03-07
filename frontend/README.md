# Frontend

All client applications for Emergency Medical Triage live here, segregated by platform:

| Folder | Platform | Tech Stack | Status |
|--------|----------|------------|--------|
| **web/** | Web dashboard | Vanilla JS, Vite, Tailwind CSS | 📝 Planning |
| **mobile-android/** | Android app | Kotlin, Jetpack Compose, Material 3 | 🚧 In Progress |

---

## Quick Links

### Web Dashboard
- [README](./web/README.md) - Setup and quick start
- [WEB-OVERVIEW](../docs/frontend/WEB-OVERVIEW.md) - Quick reference
- [Implementation Plan](../docs/frontend/implementation_plan.md) - Build phases (vanilla JS)
- [Architecture](../docs/frontend/web-architecture.md) - System design
- [Code Guide](../docs/frontend/web-code-guide.md) - Developer guide
- [Antigravity Rules](../docs/frontend/rules_anitgravity_frontend.md) - **MANDATORY READING**
- [Task Checklist](../docs/frontend/task.md) - Phase-by-phase tasks

### Mobile Android
- [README](./mobile-android/README.md) - Setup and quick start
- [Implementation Plan](../docs/frontend/android-mobile-plan.md) - Build phases
- [Mock Design Checklist](../docs/frontend/mobile-mock-design-checklist.md) - Design requirements

### Shared Documentation
- [Frontend Workflow](../docs/frontend/frontend_workflow.md) - User flows and screen maps
- [API Contract](../docs/frontend/triage-api-contract.md) - Backend API reference

---

## Development Guidelines

### Separation of Concerns
- **Do not** mix web and mobile code across folders
- **Do not** edit backend code (`../src/`, `../infrastructure/`) from frontend
- **Do not** share components between web and mobile (different frameworks)

### Shared Resources
- Design tokens (colors, spacing, typography) should match across platforms
- API contracts are shared (same backend endpoints)
- User flows and business logic should be consistent
- Translation files can be shared (JSON format)

---

## Getting Started

### Web Dashboard
```bash
cd web
npm install
cp .env.example .env
npm run dev
# Open http://localhost:5173
```

### Mobile Android
```bash
cd mobile-android
./gradlew assembleDebug
# Or open in Android Studio
```

---

## Tech Stack Comparison

| Aspect | Web | Mobile Android |
|--------|-----|----------------|
| **Language** | Vanilla JavaScript | Kotlin |
| **Framework** | None (Vite build tool) | Jetpack Compose |
| **Styling** | Tailwind CSS | Material 3 |
| **State** | sessionStorage + localStorage | Hilt + Room |
| **Navigation** | Hash-based SPA router | Compose Navigation |
| **API Client** | Fetch API (native) | Retrofit + OkHttp |
| **Forms** | Vanilla JS | Compose Forms |
| **i18n** | Custom translation object | Android Resources |

---

## Common Features

Both platforms implement:
- ✅ Triage assessment (4-step wizard)
- ✅ Hospital matching and routing
- ✅ RMP dashboard and training
- ✅ Multi-language support (7 languages)
- ✅ Offline mode
- ✅ Session tracking (UUID-based)
- ✅ Safety guardrails (confidence < 85% → high priority)
- ✅ Role-based access (Healthcare Worker, Hospital Staff, Admin)

---

## Design Consistency

### Severity Colors (Must Match)
- Critical: `#DC2626` (Red 600)
- High: `#EA580C` (Orange 600)
- Medium: `#D97706` (Amber 600)
- Low: `#16A34A` (Green 600)

### Typography
- Font: Inter (web) / Roboto (Android)
- Scale: 12px, 14px, 16px, 18px, 20px, 24px, 30px, 36px

### Spacing (8pt Grid)
- 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px

---

## Antigravity Rules (Web Only)

The web application follows strict safety-critical frontend standards:

- **Minimal Hop Rule:** UI → API Gateway → Lambda (no middleware chains)
- **No Silent Failures:** All errors logged and shown
- **No Hardcoding:** Use environment variables
- **Safety Guardrails:** Confidence < 85% → HIGH priority
- **Conservative Defaults:** On failure, treat as HIGH priority

See [Antigravity Rules](../docs/frontend/rules_anitgravity_frontend.md) for complete list.

---

## Contributing

1. Choose your platform (web or mobile)
2. **Web developers:** Read [Antigravity Rules](../docs/frontend/rules_anitgravity_frontend.md) first (MANDATORY)
3. Read the platform-specific README and docs
4. Follow the implementation plan for your platform
5. Ensure design consistency with the other platform
6. Test on multiple screen sizes
7. Submit PR with platform prefix: `[web]` or `[mobile]`

---

## Questions?

- **Web:** Check [web/README.md](./web/README.md), [WEB-OVERVIEW](../docs/frontend/WEB-OVERVIEW.md), and [Antigravity Rules](../docs/frontend/rules_anitgravity_frontend.md)
- **Mobile:** Check [mobile-android/README.md](./mobile-android/README.md) and [android-mobile-plan.md](../docs/frontend/android-mobile-plan.md)
- **API:** Check [triage-api-contract.md](../docs/frontend/triage-api-contract.md)
- **Workflows:** Check [frontend_workflow.md](../docs/frontend/frontend_workflow.md)
