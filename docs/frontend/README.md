# Frontend Documentation

Comprehensive documentation for Emergency Medical Triage frontend applications.

---

## 📱 Platforms

| Platform | Status | Quick Start |
|----------|--------|-------------|
| **Web Dashboard** | 📝 Planning | [Web Overview](./WEB-OVERVIEW.md) |
| **Android Mobile** | 🚧 In Progress | [Mobile README](../../frontend/mobile-android/README.md) |

---

## 🗂️ Documentation Index

### Web Application (Admin Dashboard)
| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[ADMIN-DASHBOARD-REFACTOR.md](./ADMIN-DASHBOARD-REFACTOR.md)** | 🆕 Complete refactoring guide for admin dashboard | 20 min |
| **[ADMIN-QUICK-START.md](./ADMIN-QUICK-START.md)** | 🆕 Get admin dashboard running quickly | 10 min |
| **[web-implementation-plan.md](./web-implementation-plan.md)** | Updated 6-day build plan for admin features | 15 min |
| **[RMP-AUTH.md](./RMP-AUTH.md)** | 🆕 Cognito authentication integration guide | 15 min |
| **[API-Integration-Guide.md](./API-Integration-Guide.md)** | 🆕 Complete API reference with auth | 10 min |
| **[web-architecture.md](./web-architecture.md)** | System design and patterns (reference) | 20 min |
| **[web-code-guide.md](./web-code-guide.md)** | Developer guide with examples | 30 min |
| **[WEB-OVERVIEW.md](./WEB-OVERVIEW.md)** | Original overview (legacy reference) | 5 min |

### Mobile Application
| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[android-mobile-plan.md](./android-mobile-plan.md)** | Android implementation plan | 10 min |
| **[mobile-mock-design-checklist.md](./mobile-mock-design-checklist.md)** | Design requirements | 5 min |

### Shared Documentation
| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[frontend_workflow.md](./frontend_workflow.md)** | User flows, screen maps, role matrix | 15 min |
| **[triage-api-contract.md](./triage-api-contract.md)** | Backend API reference | 10 min |
| **[implementation_plan.md](./implementation_plan.md)** | Original frontend plan (legacy) | 10 min |

---

## 🚀 Quick Start by Role

### I'm a Web Developer
1. **CRITICAL:** Read [rules_anitgravity_frontend.md](./rules_anitgravity_frontend.md) (15 min)
2. Read [WEB-OVERVIEW.md](./WEB-OVERVIEW.md) (5 min)
3. Review [web-architecture.md](./web-architecture.md) (20 min)
4. Follow [implementation_plan.md](./implementation_plan.md) and [task.md](./task.md)
5. Reference [web-code-guide.md](./web-code-guide.md) while coding

### I'm a Mobile Developer
1. Read [android-mobile-plan.md](./android-mobile-plan.md) (10 min)
2. Review [mobile-mock-design-checklist.md](./mobile-mock-design-checklist.md)
3. Check [../../frontend/mobile-android/README.md](../../frontend/mobile-android/README.md)
4. Start with Phase 1 (Foundation)

### I'm a Product Manager
1. Read [frontend_workflow.md](./frontend_workflow.md) (15 min)
2. Review [implementation_plan.md](./implementation_plan.md) for timeline
3. Check [mobile-mock-design-checklist.md](./mobile-mock-design-checklist.md) for design status
4. Understand [rules_anitgravity_frontend.md](./rules_anitgravity_frontend.md) constraints

### I'm a Designer
1. Read [frontend_workflow.md](./frontend_workflow.md) (15 min)
2. Review [mobile-mock-design-checklist.md](./mobile-mock-design-checklist.md)
3. Check design system in [implementation_plan.md](./implementation_plan.md) section on design tokens
4. Understand severity colors (NEVER CHANGE): Critical #DC2626, High #EA580C, Medium #D97706, Low #16A34A

### I'm a Backend Developer
1. Read [triage-api-contract.md](./triage-api-contract.md) (10 min)
2. Review API endpoints in [frontend_workflow.md](./frontend_workflow.md) section 9
3. Understand session tracking requirements

---

## 🎯 Key Concepts

### Session Continuity (Critical!)
Both web and mobile must send the same `session_id` (UUID, ≥33 chars) across:
- POST /triage
- POST /hospitals/match
- POST /routing/calculate

This enables AgentCore memory continuity across the flow.

### Safety Guardrails
Medical safety rules enforced in UI:
- Confidence < 85% → auto-escalate to HIGH priority
- Always display safety disclaimers
- Critical symptoms → CRITICAL severity

### Multi-language Support
7 languages: English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati

### Design Consistency
Severity colors must match across platforms:
- Critical: `#DC2626` (Red)
- High: `#EA580C` (Orange)
- Medium: `#D97706` (Amber)
- Low: `#16A34A` (Green)

---

## 📊 Implementation Status

### Web Dashboard
- [x] Documentation complete
- [ ] Project setup
- [ ] Phase 1: Foundation
- [ ] Phase 2: Auth & Language
- [ ] Phase 3: Triage Flow
- [ ] Phase 4: Hospitals & Routing
- [ ] Phase 5: RMP Features
- [ ] Phase 6: Admin & Hospital Staff

### Mobile Android
- [x] Phase 1: Foundation (Complete)
- [x] Phase 2: Auth & Language (Complete)
- [ ] Phase 3: Triage Flow (In Progress)
- [ ] Phase 4: Hospitals & Routing
- [ ] Phase 5: RMP Features

---

## 🔗 External Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Query Documentation](https://tanstack.com/query/latest)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)
- [Material 3 Guidelines](https://m3.material.io/)

---

## 📝 Contributing

1. Choose your platform (web or mobile)
2. Read the platform-specific documentation
3. Follow the implementation plan
4. Ensure design consistency
5. Test thoroughly
6. Submit PR with platform prefix: `[web]` or `[mobile]`

---

## 🆘 Need Help?

- **Web questions:** Check [WEB-OVERVIEW.md](./WEB-OVERVIEW.md) or [web-code-guide.md](./web-code-guide.md)
- **Mobile questions:** Check [android-mobile-plan.md](./android-mobile-plan.md)
- **API questions:** Check [triage-api-contract.md](./triage-api-contract.md)
- **Workflow questions:** Check [frontend_workflow.md](./frontend_workflow.md)
- **General questions:** Ask in team Slack channel

---

**Last Updated:** March 2026
