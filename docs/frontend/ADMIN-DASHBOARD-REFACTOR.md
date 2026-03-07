# Admin Dashboard Refactor Plan

**Date:** March 7, 2026  
**Purpose:** Refactor the web application from patient-facing triage to admin-focused monitoring and routing dashboard

---

## Overview

The web application is being refactored to serve as an **Admin Dashboard** for monitoring and managing emergency medical triage operations. The admin can see real-time patient movements, hospital assignments, ETAs, and re-route patients when necessary.

### Key Changes

**Before:** Patient-facing triage wizard (symptoms → assessment → hospital match → navigation)  
**After:** Admin monitoring dashboard (view all active patients → track locations → monitor ETAs → re-route if needed)

---

## Admin Responsibilities

The admin user can:

1. **Monitor Active Patients**
   - View all patients currently in transit
   - See patient severity levels (Critical, High, Medium, Low)
   - Track patient locations in real-time on map

2. **Track Hospital Assignments**
   - See which hospital each patient is heading to
   - View hospital capacity and availability status
   - Monitor bed availability by specialty

3. **Monitor ETAs**
   - View estimated time of arrival for each patient
   - See distance remaining to destination
   - Track route progress

4. **Re-route Patients**
   - Identify when assigned hospital becomes unavailable
   - Select alternative hospital from recommendations
   - Recalculate route and update ETA
   - Notify ambulance/RMP of route change

5. **View Patient Details**
   - Access triage assessment results
   - Review symptoms and vitals
   - See medical history and allergies
   - View handoff reports

6. **System Monitoring**
   - View system health and API status
   - Monitor alert notifications
   - Access audit logs
   - Generate reports

---

## New Architecture

### Data Flow

```
Mobile App (RMP) → Backend API → Admin Dashboard
                                      ↓
                              Real-time Updates
                                      ↓
                              Map View + Patient List
                                      ↓
                              Admin Actions (Re-route)
                                      ↓
                              Backend API → Mobile App
```

### Key Components

1. **Dashboard Overview**
   - Active patients count by severity
   - Hospital capacity summary
   - System alerts
   - Recent activity feed

2. **Live Map View**
   - Google Maps integration
   - Patient markers (color-coded by severity)
   - Hospital markers with capacity indicators
   - Route polylines showing patient paths
   - Real-time position updates

3. **Patient List Panel**
   - Sortable/filterable table
   - Patient ID, name, severity, ETA
   - Current location and destination
   - Status indicators (en route, arrived, etc.)
   - Quick actions (view details, re-route)

4. **Patient Detail Modal**
   - Full triage assessment
   - Symptoms and vitals
   - Medical history
   - Current route information
   - Re-routing interface

5. **Hospital Status Panel**
   - List of all hospitals
   - Bed availability by department
   - Incoming patient count
   - Capacity alerts

6. **Re-routing Interface**
   - Triggered when hospital unavailable
   - Shows alternative hospital recommendations
   - Distance and ETA comparison
   - One-click re-route with confirmation
   - Automatic notification to RMP

---

## API Integration Updates

### New Endpoints Needed

```javascript
// Get all active patients (admin view)
GET /admin/patients/active
Response: {
  patients: [
    {
      id: "uuid",
      session_id: "uuid",
      patient_name: "string",
      severity: "critical" | "high" | "medium" | "low",
      current_location: { lat: number, lon: number },
      destination_hospital_id: "string",
      destination_hospital_name: "string",
      eta_minutes: number,
      distance_remaining_km: number,
      status: "en_route" | "arrived" | "cancelled",
      triage_summary: { ... },
      last_updated: "ISO timestamp"
    }
  ]
}

// Get hospital status (admin view)
GET /admin/hospitals/status
Response: {
  hospitals: [
    {
      id: "string",
      name: "string",
      location: { lat: number, lon: number },
      capacity: {
        emergency: { available: number, total: number },
        icu: { available: number, total: number },
        general: { available: number, total: number }
      },
      incoming_patients: number,
      status: "available" | "limited" | "full" | "unavailable"
    }
  ]
}

// Re-route patient
POST /admin/patients/{patient_id}/reroute
Body: {
  new_hospital_id: "string",
  reason: "string"
}
Response: {
  success: boolean,
  new_route: {
    distance_km: number,
    duration_minutes: number,
    directions_url: "string"
  },
  notification_sent: boolean
}

// Get patient details
GET /admin/patients/{patient_id}
Response: {
  patient: { ... full triage data ... },
  route: { ... current route info ... },
  history: [ ... previous actions ... ]
}
```

### Existing Endpoints to Use

- `POST /triage` - View triage results (read-only for admin)
- `POST /hospitals` - Get hospital recommendations for re-routing
- `POST /route` - Calculate new routes when re-routing
- `GET /health` - System health check

---

## UI/UX Design

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Top Bar: Logo | System Status | Alerts (3) | Admin Profile │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────┐  ┌─────────────────────┐  │
│  │                             │  │  Active Patients    │  │
│  │                             │  │  ┌───────────────┐  │  │
│  │      Google Maps            │  │  │ Patient 1     │  │  │
│  │                             │  │  │ Critical      │  │  │
│  │  • Patient markers          │  │  │ ETA: 12 min   │  │  │
│  │  • Hospital markers         │  │  └───────────────┘  │  │
│  │  • Route polylines          │  │  ┌───────────────┐  │  │
│  │                             │  │  │ Patient 2     │  │  │
│  │                             │  │  │ High          │  │  │
│  │                             │  │  │ ETA: 8 min    │  │  │
│  │                             │  │  └───────────────┘  │  │
│  │                             │  │                     │  │
│  │                             │  │  [View All]         │  │
│  └─────────────────────────────┘  └─────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Hospital Status                                         ││
│  │  Hospital A: 🟢 Available (5 beds) | 2 incoming         ││
│  │  Hospital B: 🟡 Limited (1 bed)    | 1 incoming         ││
│  │  Hospital C: 🔴 Full               | 0 incoming         ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Color Coding

**Severity Colors (same as mobile):**
- Critical: Red (#DC2626)
- High: Orange (#EA580C)
- Medium: Amber (#D97706)
- Low: Green (#16A34A)

**Hospital Status Colors:**
- Available: Green (#10B981)
- Limited: Yellow (#F59E0B)
- Full: Red (#EF4444)
- Unavailable: Gray (#6B7280)

**Map Markers:**
- Patient markers: Colored by severity with pulse animation
- Hospital markers: Colored by status with bed count badge
- Selected patient: Larger marker with highlight

---

## Implementation Phases

### Phase 1: Authentication & Layout (Day 1)

**Tasks:**
1. Update login page for admin role
2. Implement Cognito authentication (use RMP-AUTH.md guide)
3. Create admin dashboard layout
4. Add top bar with system status
5. Set up routing for admin pages

**Files to Create/Update:**
- `src/pages/admin-login.js`
- `src/pages/admin-dashboard.js`
- `src/components/admin-layout.js`
- `src/components/top-bar.js`
- `src/utils/auth.js` (update for Cognito)

### Phase 2: Google Maps Integration (Day 2)

**Tasks:**
1. Set up Google Maps JavaScript API
2. Create map component with markers
3. Implement patient markers (color-coded)
4. Add hospital markers
5. Draw route polylines
6. Add marker click handlers

**Files to Create:**
- `src/components/admin-map.js`
- `src/utils/google-maps.js`
- `src/services/maps.js`

**Environment Variables:**
```
VITE_GOOGLE_MAPS_API_KEY=your_key_here
```

### Phase 3: Patient Monitoring (Day 3)

**Tasks:**
1. Create patient list component
2. Implement active patients API call
3. Add real-time updates (polling or WebSocket)
4. Create patient detail modal
5. Add filtering and sorting
6. Implement status indicators

**Files to Create:**
- `src/components/patient-list.js`
- `src/components/patient-card.js`
- `src/components/patient-detail-modal.js`
- `src/services/admin-api.js`

### Phase 4: Hospital Status (Day 4)

**Tasks:**
1. Create hospital status panel
2. Implement hospital status API call
3. Add capacity indicators
4. Show incoming patient counts
5. Add hospital detail view

**Files to Create:**
- `src/components/hospital-status-panel.js`
- `src/components/hospital-card.js`

### Phase 5: Re-routing Feature (Day 5)

**Tasks:**
1. Create re-routing interface
2. Implement hospital unavailable detection
3. Add alternative hospital selection
4. Calculate new routes
5. Send re-route notifications
6. Update map and patient list

**Files to Create:**
- `src/components/reroute-modal.js`
- `src/services/reroute.js`

### Phase 6: Dashboard Overview & Polish (Day 6)

**Tasks:**
1. Create dashboard overview cards
2. Add system alerts
3. Implement activity feed
4. Add error handling
5. Optimize performance
6. Add loading states
7. Test all features

**Files to Create:**
- `src/components/dashboard-overview.js`
- `src/components/alert-panel.js`
- `src/components/activity-feed.js`

---

## Files to Remove/Refactor

### Remove (Patient-facing features):
- `src/pages/triage-wizard.js` → Keep for reference, but not used
- Patient symptom input components
- Patient vitals input components

### Refactor (Reuse for admin view):
- `src/services/api.js` → Add admin endpoints
- `src/components/severity-badge.js` → Reuse as-is
- `src/utils/router.js` → Update routes for admin pages
- `src/styles/*` → Keep design tokens, update components

### Keep (Still needed):
- Authentication utilities
- API client base
- Design system components
- Theme utilities

---

## Real-time Updates Strategy

### Option 1: Polling (Simpler, recommended for MVP)

```javascript
// Poll every 5 seconds for active patients
useEffect(() => {
  const interval = setInterval(async () => {
    const patients = await fetchActivePatients();
    updatePatientMarkers(patients);
  }, 5000);
  
  return () => clearInterval(interval);
}, []);
```

### Option 2: WebSocket (Better for production)

```javascript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('wss://api.example.com/admin/stream');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  
  switch (update.type) {
    case 'patient_location':
      updatePatientLocation(update.patient_id, update.location);
      break;
    case 'hospital_status':
      updateHospitalStatus(update.hospital_id, update.status);
      break;
    case 'patient_arrived':
      removePatientFromMap(update.patient_id);
      break;
  }
};
```

**Recommendation:** Start with polling for MVP, migrate to WebSocket later.

---

## Security Considerations

1. **Admin-only Access**
   - Require admin role in Cognito token
   - Validate role on every API call
   - Redirect non-admins to login

2. **Data Privacy**
   - Mask patient PII in list view
   - Full details only in modal (with audit log)
   - No patient data in URL parameters

3. **Action Audit**
   - Log all re-routing actions
   - Track admin user for each action
   - Store reason for re-routing

---

## Testing Checklist

- [ ] Admin can log in with Cognito
- [ ] Dashboard loads with active patients
- [ ] Map displays patient and hospital markers
- [ ] Patient markers are color-coded by severity
- [ ] Clicking patient marker shows details
- [ ] Patient list updates in real-time
- [ ] Hospital status panel shows correct data
- [ ] Re-routing flow works end-to-end
- [ ] New route is calculated correctly
- [ ] Map updates after re-routing
- [ ] Error states display properly
- [ ] Loading states work correctly
- [ ] Mobile responsive (tablet view)

---

## Next Steps

1. Read the new authentication documentation (RMP-AUTH.md)
2. Review Google Maps integration guide (GOOGLE-MAPS-ACCOUNT-SETUP.md)
3. Start with Phase 1: Authentication & Layout
4. Set up Google Maps API key
5. Implement core monitoring features
6. Add re-routing capability
7. Test with real backend APIs

---

## References

- [RMP-AUTH.md](./RMP-AUTH.md) - Cognito authentication guide
- [API-Integration-Guide.md](./API-Integration-Guide.md) - API endpoints and contracts
- [GOOGLE-MAPS-ACCOUNT-SETUP.md](../infrastructure/GOOGLE-MAPS-ACCOUNT-SETUP.md) - Maps setup
- [AC4-Product-Decisions.md](../backend/AC4-Product-Decisions.md) - Product requirements
- [web-architecture.md](./web-architecture.md) - Original architecture (for reference)
