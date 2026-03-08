# Web Application Overview

**Quick Reference:** Everything you need to know about the web dashboard in one place.

---

## 📚 Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| [Implementation Plan](./implementation_plan.md) | Build phases, timeline, deliverables | Project managers, developers |
| [Architecture](./web-architecture.md) | System design, patterns, data flow | Architects, senior developers |
| [Code Guide](./web-code-guide.md) | How to write and understand code | All developers |
| [API Contract](./triage-api-contract.md) | Backend API reference | Frontend & backend developers |
| [Frontend Workflow](./frontend_workflow.md) | User flows, screen maps | Designers, product managers |
| [Antigravity Rules](./rules_anitgravity_frontend.md) | Safety-critical frontend standards | All developers |
| [Task Checklist](./task.md) | Phase-by-phase implementation tasks | Developers |

---

## 🎯 Project Summary

**What:** Web dashboard for AI-powered emergency medical triage  
**Who:** Healthcare Workers (RMP), Hospital Staff, Administrators  
**Tech:** Vanilla JavaScript, Vite, Tailwind CSS, Fetch API  
**Status:** Planning phase (not yet implemented)  
**Priority:** Safety > Correctness > Clarity > Reliability > Performance > Aesthetics

---

## 🏗️ Architecture at a Glance

```
Browser → Fetch API → AWS API Gateway → Lambda → Bedrock AgentCore
            ↓
    localStorage (session, theme, language)
            ↓
    Vanilla JS (DOM manipulation)
            ↓
    CSS (Tailwind + Custom)
```

**Key Principle:** Minimal hops, single abstraction layer per domain.

---

## 📋 Implementation Phases

| Phase | Duration | Focus | Key Deliverables |
|-------|----------|-------|------------------|
| **1** | 2-3 days | Foundation | Design system, theme, router, app shell |
| **2** | 1-2 days | Auth & Language | Login, mock auth, 7-language selector |
| **3** | 3-4 days | Triage Flow | 4-step wizard, results, session tracking |
| **4** | 2-3 days | Hospitals & Routing | Hospital cards, map placeholder, navigation |
| **5** | 2-3 days | RMP Features | Dashboard, guidance, learning |
| **6** | 2-3 days | Admin & Hospital Staff | Analytics, capacity management |

**Total:** ~2-3 weeks for complete implementation

---

## 🔑 Key Concepts

### Session Continuity
- Generate UUID at flow start: `crypto.randomUUID()`
- Store in `sessionStorage`
- Send same `session_id` on every API call (triage → hospitals → routing)
- Enables AgentCore memory across the flow

### Safety Guardrails (Antigravity Rules)
- Confidence < 85% → auto-escalate to HIGH priority
- Always display safety disclaimers (never collapsible)
- Critical symptoms → CRITICAL severity
- No silent failures - all errors logged and shown
- Conservative defaults on any failure

### Minimal Hop Rule
```
UI → API Gateway → Lambda → Response
```
No middleware chains, no nested wrappers, ONE service abstraction per domain.

### Multi-language
- 7 languages: English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati
- Translation object in `data/translations.js`
- Simple key lookup, no heavy i18n library

---

## 🎨 Design System

### Colors
```css
Critical: #DC2626  (Red)
High:     #EA580C  (Orange)
Medium:   #D97706  (Amber)
Low:      #16A34A  (Green)
Primary:  #2563EB  (Blue)
```

### Typography
- Font: Inter (Google Fonts)
- Sizes: 12px, 14px, 16px, 18px, 20px, 24px, 30px, 36px

### Spacing (8pt Grid)
- 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px

---

## 🔌 API Integration

### Base URL
```javascript
const API_URL = import.meta.env.VITE_API_URL;
// Never hardcode!
```

### Key Endpoints
```
POST /triage                    # Triage assessment
POST /hospitals/match           # Hospital matching
POST /routing/calculate         # Route calculation
GET  /rmp/profile/:id           # RMP dashboard
GET  /rmp/learning/modules      # Learning modules
```

### Request Pattern (Minimal Hop)
```javascript
// services/triage.js
export async function assessTriage(data) {
  const sessionId = sessionStorage.getItem('session_id');
  
  const response = await fetch(`${API_URL}/triage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...data, session_id: sessionId })
  });
  
  if (!response.ok) {
    throw new Error(`Triage failed: ${response.status}`);
  }
  
  const result = await response.json();
  
  // Apply safety guardrails
  if (result.confidence < 0.85) {
    result.force_high_priority = true;
    result.severity = 'high';
  }
  
  return result;
}
```

---

## � Project Structure

```
frontend/
├── index.html           # Entry point
├── package.json
├── vite.config.js
├── public/
│   └── favicon.svg
├── src/
│   ├── main.js          # App bootstrap
│   ├── style.css        # Import all styles
│   ├── styles/
│   │   ├── tokens.css   # Design tokens
│   │   ├── global.css   # Base styles
│   │   └── components.css # Component styles
│   ├── utils/
│   │   ├── theme.js     # Light/dark toggle
│   │   ├── router.js    # Hash-based SPA router
│   │   └── auth.js      # Mock auth
│   ├── services/
│   │   ├── triage.js    # Triage API calls
│   │   ├── hospitals.js # Hospital API calls
│   │   └── routing.js   # Routing API calls
│   ├── validators/
│   │   └── triage.js    # Input validation
│   ├── components/
│   │   ├── language-selector.js
│   │   └── guidance-overlay.js
│   ├── pages/
│   │   ├── login.js
│   │   ├── triage-wizard.js
│   │   ├── triage-report.js
│   │   ├── hospital-match.js
│   │   ├── navigation.js
│   │   ├── rmp-dashboard.js
│   │   ├── learning.js
│   │   ├── admin-dashboard.js
│   │   └── hospital-portal.js
│   └── data/
│       ├── mock-triage.js
│       ├── mock-hospitals.js
│       ├── mock-admin.js
│       └── translations.js
└── .env.example
```

---

## 🚀 Quick Commands

```bash
# Setup
npm install
cp .env.example .env
npm run dev

# Development
npm run dev              # Start dev server (http://localhost:5173)
npm run build            # Production build
npm run preview          # Preview production build

# No linting/testing in initial setup (keep it minimal)
```

---

## ✅ Pre-Implementation Checklist

Before starting development:

- [ ] Read [Antigravity Rules](./rules_anitgravity_frontend.md) (MANDATORY)
- [ ] Review [Implementation Plan](./implementation_plan.md)
- [ ] Understand [API Contract](./triage-api-contract.md)
- [ ] Study [Frontend Workflow](./frontend_workflow.md)
- [ ] Review [Task Checklist](./task.md)
- [ ] Set up development environment (Node.js 18+, Vite)
- [ ] Get API URL and test backend connectivity
- [ ] Confirm design tokens with mobile team

---

## 🎓 Learning Path

**New to the project?** Follow this order:

1. **Start here:** Read this overview
2. **CRITICAL:** Read [Antigravity Rules](./rules_anitgravity_frontend.md)
3. **Understand users:** Review [Frontend Workflow](./frontend_workflow.md)
4. **Learn architecture:** Read [Architecture](./web-architecture.md)
5. **Plan work:** Review [Implementation Plan](./implementation_plan.md) and [Task Checklist](./task.md)
6. **Start coding:** Follow [Code Guide](./web-code-guide.md)
7. **Integrate API:** Reference [API Contract](./triage-api-contract.md)

---

## 🆘 Common Questions

**Q: Why Vanilla JS instead of React/Vue?**  
A: Safety-critical healthcare app. Minimal complexity, deterministic behavior, explicit over clever. See Antigravity Rules.

**Q: Where do I start coding?**  
A: Follow Phase 1 in [Task Checklist](./task.md)

**Q: How do I call the backend API?**  
A: See [API Contract](./triage-api-contract.md) and [Code Guide](./web-code-guide.md) - use Fetch API directly, one service per domain

**Q: How does session tracking work?**  
A: Generate UUID with `crypto.randomUUID()`, store in `sessionStorage`, send with every API call

**Q: What are safety guardrails?**  
A: See [Antigravity Rules](./rules_anitgravity_frontend.md) section 6 - confidence < 85% → HIGH priority, always show disclaimers

**Q: Can I use a library for X?**  
A: Only if absolutely necessary. Check Antigravity Rules first. Prefer vanilla JS.

---

## 📞 Getting Help

1. Check [Antigravity Rules](./rules_anitgravity_frontend.md) first
2. Review relevant documentation above
3. Search existing GitHub issues
4. Ask in team Slack channel
5. Consult with senior developers

---

**Ready to build? Start with [Task Checklist](./task.md) Phase 1!**
