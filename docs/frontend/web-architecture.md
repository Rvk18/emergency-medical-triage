# Web Application Architecture (Vanilla JS + Vite)

**Project:** Emergency Medical Triage - Web Dashboard  
**Last Updated:** March 2026  
**Stack:** Vanilla JavaScript, Vite, Tailwind CSS, Fetch API

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Client)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Vanilla JS Application                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │   Pages/     │  │  Components  │  │ localStorage │ │ │
│  │  │   Router     │  │   (Vanilla)  │  │ sessionStorage│ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │ │
│  │         │                  │                  │         │ │
│  │  ┌──────┴──────────────────┴──────────────────┴──────┐ │ │
│  │  │           Services (API Layer)                     │ │ │
│  │  └──────────────────────┬─────────────────────────────┘ │ │
│  │                         │                                │ │
│  │  ┌──────────────────────┴─────────────────────────────┐ │ │
│  │  │           Fetch API (Native)                       │ │ │
│  │  └──────────────────────┬─────────────────────────────┘ │ │
│  └─────────────────────────┼──────────────────────────────┘ │
└────────────────────────────┼─────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   AWS API Gateway                            │
│         https://vrxlwtzfff.execute-api.us-east-1...         │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Triage     │    │   Hospital   │    │   Routing    │
│   Lambda     │    │   Matcher    │    │   Lambda     │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           │
                           ▼
                ┌──────────────────┐
                │  Bedrock Agent   │
                │     Core         │
                └──────────────────┘
```

**Key Principle:** Minimal hops. UI → API Gateway → Lambda. No middleware chains.

---

## 2. Frontend Architecture Layers

### 2.1 Presentation Layer (DOM Manipulation)

**Responsibility:** UI rendering, user interactions, visual feedback

**Structure:**
- **Pages** (`src/pages/`): Route-level components (pure functions that return HTML strings or DOM elements)
- **Components** (`src/components/`): Reusable UI pieces
- **Styles** (`src/styles/`): CSS modules (tokens, global, components)

**Pattern:**
```javascript
// pages/triage-wizard.js
export function renderTriageWizard(container) {
  const html = `
    <div class="wizard">
      <div class="wizard-steps">...</div>
      <div class="wizard-content">...</div>
    </div>
  `;
  
  container.innerHTML = html;
  attachEventListeners(container);
}

function attachEventListeners(container) {
  const nextBtn = container.querySelector('.btn-next');
  nextBtn.addEventListener('click', handleNext);
}
```

### 2.2 State Management Layer

**Responsibility:** Application state, persistence

**Technologies:**
- **sessionStorage**: Session ID, current flow state (triage data, selected hospital)
- **localStorage**: Theme preference, language, auth token
- **In-memory**: Temporary UI state (current step, loading states)

**No global state library.** Keep it simple.

**State Categories:**

| State Type | Storage | Example |
|------------|---------|---------|
| **Session State** | sessionStorage | session_id, triage_result, selected_hospital |
| **Persistent State** | localStorage | theme, language, auth_token |
| **Temporary State** | In-memory (closures) | current_step, is_loading |

### 2.3 Data Layer (Services)

**Responsibility:** HTTP communication, request/response transformation, error handling

**Structure:**
```
src/services/
├── triage.js          // Triage endpoints
├── hospitals.js       // Hospital endpoints
├── routing.js         // Routing endpoints
├── rmp.js             // RMP endpoints
└── admin.js           // Admin endpoints
```

**Pattern (Minimal Hop):**
```javascript
// services/triage.js
const API_URL = import.meta.env.VITE_API_URL;

export async function assessTriage(data) {
  const sessionId = sessionStorage.getItem('session_id');
  
  try {
    const response = await fetch(`${API_URL}/triage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, session_id: sessionId })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Validate response shape
    if (!result.severity || typeof result.confidence !== 'number') {
      throw new Error('Invalid response shape');
    }
    
    // Apply safety guardrails
    if (result.confidence < 0.85) {
      result.force_high_priority = true;
      result.severity = 'high';
    }
    
    return result;
  } catch (error) {
    console.error('[Triage Service]', error);
    throw error; // Never silent failures
  }
}
```

---

## 3. Data Flow Patterns

### 3.1 Triage Assessment Flow

```
User Input → Validation → API Request → Loading State → 
Response Processing → Safety Guardrails → DOM Update → Session Storage
```

**Detailed Steps:**

1. **User fills triage wizard** (4 steps)
   ```javascript
   // Collect data from form
   const patientData = {
     age: parseInt(form.age.value),
     gender: form.gender.value,
     symptoms: getSelectedSymptoms(),
     vitals: getVitals()
   };
   ```

2. **Validate input**
   ```javascript
   // validators/triage.js
   export function validateTriageInput(data) {
     if (!data.symptoms || data.symptoms.length === 0) {
       throw new Error('At least one symptom required');
     }
     if (data.age && (data.age < 0 || data.age > 150)) {
       throw new Error('Invalid age');
     }
     return true;
   }
   ```

3. **Generate session ID** (on wizard start)
   ```javascript
   let sessionId = sessionStorage.getItem('session_id');
   if (!sessionId) {
     sessionId = crypto.randomUUID();
     sessionStorage.setItem('session_id', sessionId);
   }
   ```

4. **Submit to API**
   ```javascript
   showLoading();
   try {
     const result = await assessTriage(patientData);
     sessionStorage.setItem('triage_result', JSON.stringify(result));
     renderResults(result);
   } catch (error) {
     showError('Triage assessment failed. Treating as HIGH priority.');
     renderFallbackResults();
   } finally {
     hideLoading();
   }
   ```

5. **Display results**
   - Severity badge with animation
   - Confidence percentage
   - Recommendations list
   - Safety disclaimers (always visible, never collapsible)
   - Override button (if needed)

### 3.2 Session Continuity Pattern

**Goal:** Maintain same AgentCore session across triage → hospitals → routing

**Implementation:**

```javascript
// utils/session.js
export function initSession() {
  let sessionId = sessionStorage.getItem('session_id');
  if (!sessionId || sessionId.length < 33) {
    sessionId = crypto.randomUUID(); // 36 chars
    sessionStorage.setItem('session_id', sessionId);
  }
  return sessionId;
}

export function getSessionId() {
  return sessionStorage.getItem('session_id');
}

export function clearSession() {
  sessionStorage.removeItem('session_id');
  sessionStorage.removeItem('triage_result');
  sessionStorage.removeItem('selected_hospital');
}
```

**Usage:**

```javascript
// pages/triage-wizard.js
import { initSession, getSessionId } from '../utils/session.js';

export function renderTriageWizard(container) {
  initSession(); // Generate UUID on mount
  // ... render wizard
}

// services/hospitals.js
import { getSessionId } from '../utils/session.js';

export async function matchHospitals(severity, recommendations) {
  const sessionId = getSessionId();
  
  const response = await fetch(`${API_URL}/hospitals/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      severity,
      recommendations,
      session_id: sessionId // Reuse same session
    })
  });
  
  return response.json();
}
```

### 3.3 Offline Data Flow

```
Online Request → Success → Cache in localStorage
                ↓ Failure (offline)
         Show cached data + offline banner
```

**Implementation:**

```javascript
// utils/offline.js
export function isOnline() {
  return navigator.onLine;
}

export function showOfflineBanner() {
  const banner = document.getElementById('offline-banner');
  if (banner) {
    banner.classList.remove('hidden');
  }
}

export function hideOfflineBanner() {
  const banner = document.getElementById('offline-banner');
  if (banner) {
    banner.classList.add('hidden');
  }
}

// Listen for online/offline events
window.addEventListener('online', () => {
  hideOfflineBanner();
  syncQueuedRequests();
});

window.addEventListener('offline', () => {
  showOfflineBanner();
});
```

---

## 4. Component Architecture

### 4.1 Component Pattern (Vanilla JS)

**No framework. Pure functions that manipulate DOM.**

```javascript
// components/severity-badge.js
export function createSeverityBadge(severity) {
  const colors = {
    critical: 'bg-red-600',
    high: 'bg-orange-600',
    medium: 'bg-amber-600',
    low: 'bg-green-600'
  };
  
  const badge = document.createElement('span');
  badge.className = `badge ${colors[severity]} text-white px-4 py-2 rounded-full`;
  badge.textContent = severity.toUpperCase();
  
  return badge;
}

// Usage
const badge = createSeverityBadge('high');
container.appendChild(badge);
```

### 4.2 Page Pattern

```javascript
// pages/triage-wizard.js
let currentStep = 1;
const totalSteps = 4;

export function renderTriageWizard(container) {
  container.innerHTML = `
    <div class="wizard">
      <div class="wizard-progress">
        ${renderProgressBar()}
      </div>
      <div class="wizard-content" id="wizard-content">
        ${renderStep(currentStep)}
      </div>
      <div class="wizard-nav">
        ${renderNavigation()}
      </div>
    </div>
  `;
  
  attachEventListeners(container);
}

function renderStep(step) {
  switch (step) {
    case 1: return renderPatientInfo();
    case 2: return renderSymptoms();
    case 3: return renderVitals();
    case 4: return renderResults();
    default: return '';
  }
}

function attachEventListeners(container) {
  const nextBtn = container.querySelector('.btn-next');
  const prevBtn = container.querySelector('.btn-prev');
  
  if (nextBtn) {
    nextBtn.addEventListener('click', handleNext);
  }
  if (prevBtn) {
    prevBtn.addEventListener('click', handlePrev);
  }
}

function handleNext() {
  if (currentStep < totalSteps) {
    currentStep++;
    const content = document.getElementById('wizard-content');
    content.innerHTML = renderStep(currentStep);
  }
}
```

---

## 5. Routing Architecture

### 5.1 Hash-based SPA Router

```javascript
// utils/router.js
const routes = {
  '/': () => import('../pages/login.js').then(m => m.renderLogin),
  '/triage': () => import('../pages/triage-wizard.js').then(m => m.renderTriageWizard),
  '/hospitals': () => import('../pages/hospital-match.js').then(m => m.renderHospitalMatch),
  '/dashboard': () => import('../pages/rmp-dashboard.js').then(m => m.renderDashboard),
  '/admin': () => import('../pages/admin-dashboard.js').then(m => m.renderAdminDashboard)
};

export function initRouter() {
  window.addEventListener('hashchange', handleRoute);
  handleRoute(); // Initial route
}

async function handleRoute() {
  const hash = window.location.hash.slice(1) || '/';
  const routeLoader = routes[hash];
  
  if (!routeLoader) {
    console.error('Route not found:', hash);
    window.location.hash = '/';
    return;
  }
  
  const container = document.getElementById('app-content');
  container.innerHTML = '<div class="loading">Loading...</div>';
  
  try {
    const renderFn = await routeLoader();
    renderFn(container);
  } catch (error) {
    console.error('Route loading failed:', error);
    container.innerHTML = '<div class="error">Page failed to load</div>';
  }
}

export function navigateTo(path) {
  window.location.hash = path;
}
```

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
1. User submits credentials → POST /auth/login
2. Backend validates → returns JWT token
3. Frontend stores token in localStorage (or httpOnly cookie if backend sets it)
4. All API requests include token in Authorization header
5. Token expires after 24 hours → redirect to login
```

### 6.2 Security Measures

| Layer | Measure | Implementation |
|-------|---------|----------------|
| **Transport** | HTTPS only | Enforced by API Gateway |
| **Auth** | JWT tokens | localStorage, short expiry |
| **XSS** | Content sanitization | DOMPurify for user input |
| **Secrets** | Environment variables | `.env`, never committed |
| **API** | Rate limiting | Backend enforced |
| **Validation** | Input validation | Client + server |

### 6.3 No Secrets in Frontend

```javascript
// ❌ NEVER do this
const API_KEY = 'sk-1234567890abcdef';

// ✅ Use environment variables
const API_URL = import.meta.env.VITE_API_URL;

// ✅ Auth tokens from backend
const token = localStorage.getItem('auth_token');
```

---

## 7. Antigravity Compliance

### 7.1 Minimal Hop Rule ✅

```
UI → Fetch → API Gateway → Lambda
```

No middleware chains, no nested wrappers.

### 7.2 No Silent Failures ✅

```javascript
try {
  const result = await assessTriage(data);
  return result;
} catch (error) {
  console.error('[Triage]', error); // Always log
  showErrorMessage('Assessment failed'); // Always show
  return getFallbackResult(); // Conservative default
}
```

### 7.3 Safety Guardrails ✅

```javascript
function applySafetyGuardrails(result) {
  // Rule 1: Low confidence → force high priority
  if (result.confidence < 0.85) {
    result.force_high_priority = true;
    result.severity = 'high';
  }
  
  // Rule 2: Always include disclaimer
  if (!result.safety_disclaimer) {
    result.safety_disclaimer = 
      'This is AI-assisted guidance. Seek professional medical care.';
  }
  
  return result;
}
```

### 7.4 No Hardcoding ✅

```javascript
// ❌ Bad
const API_URL = 'https://prod-api.com';

// ✅ Good
const API_URL = import.meta.env.VITE_API_URL;
```

---

## 8. Performance Considerations

- **Code splitting**: Dynamic imports for routes
- **Minimal dependencies**: No heavy libraries
- **Debounced input**: 300-500ms for search/autocomplete
- **API timeout**: 10s max (configurable)
- **No polling**: Use WebSockets if real-time needed

---

**This architecture prioritizes safety, simplicity, and maintainability over clever abstractions.**
