# Emergency Medical Triage - Admin Dashboard

AI-powered emergency medical triage monitoring and routing system for administrators.

**Stack:** Vanilla JavaScript, Vite, Tailwind CSS, Google Maps API

**NEW:** This web application has been refactored to serve as an **Admin Dashboard** for monitoring active patients and managing hospital routing. See [ADMIN-DASHBOARD-REFACTOR.md](../../docs/frontend/ADMIN-DASHBOARD-REFACTOR.md) for details.

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API URL

# Run development server
npm run dev

# Open http://localhost:5173
```

---

## 📋 Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Git
- Code editor (VS Code recommended)

---

## 🏗️ Tech Stack

- **Language:** Vanilla JavaScript (ES6+)
- **Build Tool:** Vite 5.x
- **Styling:** Tailwind CSS 3.x
- **API Client:** Fetch API (native)
- **Router:** Hash-based SPA router (custom)
- **State:** sessionStorage + localStorage (no state library)

**Why Vanilla JS?** Safety-critical healthcare application. Minimal complexity, deterministic behavior, explicit over clever. See [Antigravity Rules](../../docs/frontend/rules_anitgravity_frontend.md).

---

## 📁 Project Structure

```
src/
├── main.js              # App entry point
├── style.css            # Import all styles
├── styles/
│   ├── tokens.css      # Design tokens
│   ├── global.css      # Base styles
│   └── components.css  # Component styles
├── pages/               # Route-level pages
│   ├── login.js
│   ├── triage-wizard.js
│   ├── hospital-match.js
│   └── ...
├── components/          # Reusable UI components
│   ├── severity-badge.js
│   ├── language-selector.js
│   └── ...
├── services/            # API calls (one per domain)
│   ├── triage.js
│   ├── hospitals.js
│   └── routing.js
├── validators/          # Input validation
│   └── triage.js
├── utils/               # Helper functions
│   ├── session.js
│   ├── router.js
│   ├── theme.js
│   └── auth.js
└── data/                # Mock data, translations
    ├── mock-triage.js
    ├── mock-hospitals.js
    └── translations.js
```

---

## 🔑 Key Features

### Admin Dashboard (Primary Interface)
- **Real-time Patient Monitoring:** View all active patients in transit with live updates
- **Hospital Status:** Monitor hospital capacity and availability across all facilities
- **Patient Tracking:** Track patient locations, ETAs, and routes on Google Maps
- **Re-routing:** Re-assign patients to alternative hospitals when needed
- **Dashboard Overview:** System-wide statistics and alerts
- **Patient Details:** View complete triage assessments and medical information

### Legacy Features (For Reference)
- **Triage Assessment:** 4-step wizard (patient info, symptoms, vitals, results)
- **Hospital Matching:** Top 3 hospital recommendations with match scores
- **Navigation:** Turn-by-turn directions to selected hospital
- **RMP Dashboard:** Competency tracking, learning modules, guidance
- **Multi-language:** Support for 7 Indian languages
- **Offline Mode:** Cached triage scenarios and hospital data

---

## 🔐 Environment Variables

```bash
# .env
VITE_API_URL=https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev
VITE_APP_ENV=development

# AWS Cognito (for admin authentication)
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_COGNITO_REGION=us-east-1

# Google Maps (for location tracking)
VITE_GOOGLE_MAPS_API_KEY=AIza...your_key_here

# Mock mode (for testing without backend)
VITE_USE_MOCK_API=true
```

**CRITICAL:** Never hardcode API URLs or secrets. Always use environment variables.

See [ADMIN-QUICK-START.md](../../docs/frontend/ADMIN-QUICK-START.md) for setup instructions.

---

## 📜 Available Scripts

```bash
# Development
npm run dev              # Start dev server (http://localhost:5173)
npm run build            # Production build
npm run preview          # Preview production build
```

---

## 🎨 Design System

### Severity Colors (NEVER CHANGE)
- **Critical:** `#DC2626` (Red 600)
- **High:** `#EA580C` (Orange 600)
- **Medium:** `#D97706` (Amber 600)
- **Low:** `#16A34A` (Green 600)

### Typography
- Font: Inter (Google Fonts)
- Sizes: 12px, 14px, 16px, 18px, 20px, 24px, 30px, 36px

### Spacing (8pt Grid)
- 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px

---

## 🔄 Session Management

The app uses UUID-based session tracking for AgentCore memory continuity:

```javascript
// Generate session ID at flow start
const sessionId = crypto.randomUUID(); // 36 chars
sessionStorage.setItem('session_id', sessionId);

// Send with every API call
POST /triage { symptoms, vitals, session_id: sessionId }
POST /hospitals/match { severity, recommendations, session_id: sessionId }
POST /routing/calculate { hospital_id, session_id: sessionId }
```

---

## 🛡️ Safety Guardrails (Antigravity Rules)

Medical safety rules enforced in the UI:

1. **Low Confidence:** If confidence < 85%, auto-escalate to HIGH priority
2. **Critical Symptoms:** Chest pain, difficulty breathing → CRITICAL severity
3. **Disclaimers:** Always display safety disclaimers (never collapsible)
4. **No Silent Failures:** All errors logged and shown to user
5. **Conservative Defaults:** On any failure, treat as HIGH priority

See [Antigravity Rules](../../docs/frontend/rules_anitgravity_frontend.md) for complete list.

---

## 🌍 Multi-language Support

Supported languages:
- English (en)
- Hindi (hi)
- Tamil (ta)
- Telugu (te)
- Bengali (bn)
- Marathi (mr)
- Gujarati (gu)

Translation object: `src/data/translations.js`

```javascript
import { t, setLanguage } from './utils/i18n.js';

const title = t('triage.title'); // "Triage Assessment"
setLanguage('hi'); // Switch to Hindi
```

---

## 📚 Documentation

### Admin Dashboard
- [ADMIN-DASHBOARD-REFACTOR.md](../../docs/frontend/ADMIN-DASHBOARD-REFACTOR.md) - **START HERE** - Complete refactoring plan
- [ADMIN-QUICK-START.md](../../docs/frontend/ADMIN-QUICK-START.md) - Quick setup guide
- [IMPLEMENTATION-STATUS.md](./IMPLEMENTATION-STATUS.md) - Current implementation status
- [API-Integration-Guide.md](../../docs/frontend/API-Integration-Guide.md) - API endpoints
- [RMP-AUTH.md](../../docs/frontend/RMP-AUTH.md) - Cognito authentication

### Legacy Documentation
- [WEB-OVERVIEW.md](../../docs/frontend/WEB-OVERVIEW.md) - Quick reference
- [Implementation Plan](../../docs/frontend/implementation_plan.md) - Build phases
- [Architecture](../../docs/frontend/web-architecture.md) - System design
- [Code Guide](../../docs/frontend/web-code-guide.md) - Developer guide
- [API Contract](../../docs/frontend/triage-api-contract.md) - Backend API
- [Antigravity Rules](../../docs/frontend/rules_anitgravity_frontend.md) - **MANDATORY READING**

---

## 🚢 Deployment

```bash
# Build for production
npm run build

# Output in dist/ directory
# Deploy to any static hosting (Vercel, Netlify, S3, etc.)
```

---

## 🐛 Debugging

### Browser DevTools
- Open DevTools (F12)
- Check Console for errors
- Check Network tab for API calls
- Check Application tab for sessionStorage/localStorage

### Common Issues

**API calls failing?**
- Check VITE_API_URL in .env
- Check network connectivity
- Check browser console for errors

**Session not persisting?**
- Check sessionStorage in DevTools
- Ensure session_id is being generated
- Check that session_id is sent with API calls

**Styles not loading?**
- Run `npm run dev` again
- Clear browser cache
- Check that style.css imports all CSS files

---

## 🤝 Contributing

1. Read [Antigravity Rules](../../docs/frontend/rules_anitgravity_frontend.md) (MANDATORY)
2. Review [Code Guide](../../docs/frontend/web-code-guide.md)
3. Follow [Task Checklist](../../docs/frontend/task.md)
4. Create feature branch: `git checkout -b feature/my-feature`
5. Make changes and test
6. Commit: `git commit -m "feat: add my feature"`
7. Push and create PR

---

## 📝 Code Review Checklist

Before submitting PR:
- [ ] No hardcoded values
- [ ] No console.log statements
- [ ] Error states handled
- [ ] Loading states handled
- [ ] session_id included in API calls
- [ ] Safety guardrails applied
- [ ] Translations added
- [ ] Mobile responsive
- [ ] Accessibility tested
- [ ] Follows Antigravity Rules

---

## 🆘 Getting Help

- Check [Antigravity Rules](../../docs/frontend/rules_anitgravity_frontend.md) first
- Review [Code Guide](../../docs/frontend/web-code-guide.md)
- Search GitHub issues
- Ask in team Slack channel

---

## 📄 License

See repository license file.

---

**Priority:** Safety > Correctness > Clarity > Reliability > Performance > Aesthetics

**Built with ❤️ for rural healthcare in India**
