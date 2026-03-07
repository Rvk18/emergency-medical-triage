# Web Application Implementation Plan

**Project:** Emergency Medical Triage - Admin Dashboard  
**Stack:** Vanilla JavaScript, Vite, Tailwind CSS, Google Maps API  
**Target Users:** System Administrators (monitoring and routing)

**IMPORTANT:** This plan has been updated to reflect the new admin-focused dashboard. See [ADMIN-DASHBOARD-REFACTOR.md](./ADMIN-DASHBOARD-REFACTOR.md) for detailed refactoring guide.

---

## 1. Overview

The web dashboard is an **Admin Monitoring and Routing Dashboard** for emergency medical triage operations. Admins can monitor active patients in real-time, track their locations and ETAs, view hospital capacity, and re-route patients when their assigned hospital becomes unavailable.

### Key Principles
- **Real-time Monitoring**: Live updates of patient locations and status
- **Admin-focused**: Designed for system administrators, not patients
- **Map-centric**: Google Maps integration for visual tracking
- **Quick Actions**: One-click re-routing when hospitals become unavailable
- **System Overview**: Dashboard showing all active patients and hospital capacity
- **Audit Trail**: All admin actions logged for compliance

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Framework** | Vanilla JavaScript + Vite | Fast, minimal, no framework overhead |
| **Styling** | Tailwind CSS 3.x | Utility-first, consistent design system |
| **Maps** | Google Maps JavaScript API | Real-time location tracking, route visualization |
| **Auth** | AWS Cognito (via Amplify) | Secure admin authentication, JWT tokens |
| **API Client** | Fetch API | Native, no extra dependencies |
| **Real-time** | Polling (5s intervals) | Simple, reliable updates (WebSocket later) |
| **State** | sessionStorage + in-memory | Minimal state management |
| **Build** | Vite | Fast dev server, optimized production builds |

---

## 3. Project Structure

```
frontend/web/
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
│   │   ├── auth.js      # Cognito authentication
│   │   ├── router.js    # Hash-based SPA router
│   │   ├── google-maps.js # Maps utilities
│   │   └── polling.js   # Real-time update polling
│   ├── services/
│   │   ├── admin-api.js # Admin API calls
│   │   ├── maps.js      # Google Maps API
│   │   └── reroute.js   # Re-routing logic
│   ├── components/
│   │   ├── admin-layout.js
│   │   ├── top-bar.js
│   │   ├── admin-map.js
│   │   ├── patient-list.js
│   │   ├── patient-card.js
│   │   ├── patient-detail-modal.js
│   │   ├── hospital-status-panel.js
│   │   ├── hospital-card.js
│   │   ├── reroute-modal.js
│   │   ├── dashboard-overview.js
│   │   ├── alert-panel.js
│   │   ├── activity-feed.js
│   │   └── severity-badge.js
│   ├── pages/
│   │   ├── admin-login.js
│   │   └── admin-dashboard.js
│   └── data/
│       └── mock-admin.js
└── .env.example
```


---

## 4. Implementation Phases

### Phase 1: Authentication & Layout (Day 1)

**Goal:** Set up admin authentication and basic dashboard layout

**Tasks:**
1. Implement Cognito authentication (AWS Amplify)
2. Create admin login page
3. Build admin dashboard layout
4. Add top bar with system status
5. Set up hash-based routing

**Deliverables:**
- Working admin login with Cognito
- Protected admin dashboard route
- Basic layout structure

**Exit Criteria:**
- Admin can log in with Cognito credentials
- Dashboard loads after successful login
- Non-authenticated users redirected to login

---

### Phase 2: Google Maps Integration (Day 2)

**Goal:** Integrate Google Maps for real-time patient and hospital tracking

**Tasks:**
1. Set up Google Maps JavaScript API
2. Create map component with initialization
3. Add patient markers (color-coded by severity)
4. Add hospital markers (with capacity indicators)
5. Draw route polylines
6. Implement marker click handlers
7. Add map controls (zoom, pan, center)

**Deliverables:**
- Working Google Maps integration
- Patient and hospital markers on map
- Route visualization

**Exit Criteria:**
- Map loads and displays correctly
- Markers appear at correct locations
- Clicking markers shows info windows
- Routes display as polylines

---

### Phase 3: Patient Monitoring (Day 3)

**Goal:** Display active patients and their real-time status

**Tasks:**
1. Create patient list component
2. Implement GET /admin/patients/active API call
3. Add real-time polling (5-second intervals)
4. Build patient card component
5. Create patient detail modal
6. Add filtering by severity
7. Add sorting by ETA
8. Implement status indicators

**Deliverables:**
- Patient list panel with real-time updates
- Patient detail modal
- Filtering and sorting

**Exit Criteria:**
- Patient list updates every 5 seconds
- Patient cards show correct data
- Detail modal displays full triage info
- Filters and sorting work correctly

---

### Phase 4: Hospital Status Panel (Day 4)

**Goal:** Monitor hospital capacity and availability

**Tasks:**
1. Create hospital status panel component
2. Implement GET /admin/hospitals/status API call
3. Build hospital card with capacity indicators
4. Add incoming patient counts
5. Show availability status (available/limited/full)
6. Add hospital detail view

**Deliverables:**
- Hospital status panel
- Capacity indicators
- Real-time status updates

**Exit Criteria:**
- Hospital panel shows all hospitals
- Capacity displays correctly
- Status colors match availability
- Incoming patient counts accurate

---

### Phase 5: Re-routing Feature (Day 5)

**Goal:** Enable admins to re-route patients to alternative hospitals

**Tasks:**
1. Create re-routing modal component
2. Detect when hospital becomes unavailable
3. Fetch alternative hospital recommendations
4. Calculate new routes using POST /route
5. Implement POST /admin/patients/{id}/reroute
6. Update map with new route
7. Show confirmation and notifications
8. Log re-routing actions

**Deliverables:**
- Re-routing interface
- Alternative hospital selection
- Route recalculation
- Audit logging

**Exit Criteria:**
- Admin can trigger re-route from patient detail
- Alternative hospitals display with ETAs
- New route calculates correctly
- Map updates after re-routing
- RMP receives notification (backend)

---

### Phase 6: Dashboard Overview & Polish (Day 6)

**Goal:** Add dashboard overview and finalize features

**Tasks:**
1. Create dashboard overview cards
   - Active patients count by severity
   - Hospital capacity summary
   - System alerts
2. Build activity feed component
3. Add system health indicators
4. Implement error handling
5. Add loading states
6. Optimize polling performance
7. Test all features end-to-end
8. Add responsive design (tablet support)

**Deliverables:**
- Dashboard overview section
- Activity feed
- Error handling
- Performance optimization

**Exit Criteria:**
- Overview cards show correct stats
- Activity feed displays recent actions
- Errors display user-friendly messages
- Loading states work smoothly
- Dashboard works on tablet screens

---

## 5. Design System

### Color Palette

```css
/* Severity Colors */
--severity-critical: #DC2626;    /* Red 600 */
--severity-high: #EA580C;        /* Orange 600 */
--severity-medium: #D97706;      /* Amber 600 */
--severity-low: #16A34A;         /* Green 600 */

/* Primary Colors (Medical Blue) */
--primary-50: #EFF6FF;
--primary-100: #DBEAFE;
--primary-500: #3B82F6;
--primary-600: #2563EB;
--primary-700: #1D4ED8;

/* Neutral Colors */
--gray-50: #F8FAFC;
--gray-100: #F1F5F9;
--gray-500: #64748B;
--gray-700: #334155;
--gray-900: #0F172A;

/* Semantic Colors */
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
--info: #3B82F6;
```

### Typography

```css
/* Font Family */
--font-sans: 'Inter', system-ui, sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing

```css
/* 8pt Grid System */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### Border Radius

```css
--radius-sm: 0.25rem;   /* 4px */
--radius-md: 0.5rem;    /* 8px */
--radius-lg: 0.75rem;   /* 12px */
--radius-xl: 1rem;      /* 16px */
--radius-full: 9999px;  /* Pill shape */
```

