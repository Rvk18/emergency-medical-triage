# Web Application Code Guide (Vanilla JS + Vite)

**For Developers:** This guide explains how to understand, navigate, and contribute to the web application codebase.

---

## 1. Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn/pnpm
- Git
- Code editor (VS Code recommended)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/Rvk18/emergency-medical-triage.git
cd emergency-medical-triage/frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
# Edit .env with your API URL

# Run development server
npm run dev

# Open http://localhost:5173
```

### Environment Variables

```bash
# .env
VITE_API_URL=https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev
VITE_APP_ENV=development
```

---

## 2. Code Organization Principles

### File Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| **Pages** | kebab-case.js | `triage-wizard.js`, `hospital-match.js` |
| **Components** | kebab-case.js | `severity-badge.js`, `language-selector.js` |
| **Services** | kebab-case.js | `triage.js`, `hospitals.js` |
| **Utils** | kebab-case.js | `session.js`, `validation.js` |
| **Constants** | UPPER_SNAKE_CASE | `API_TIMEOUT`, `MAX_RETRIES` |

### Directory Structure Logic

```
src/
├── main.js           # App entry point
├── style.css         # Import all styles
├── styles/           # CSS modules
│   ├── tokens.css   # Design tokens
│   ├── global.css   # Base styles
│   └── components.css # Component styles
├── pages/            # Route-level pages
├── components/       # Reusable UI components
├── services/         # API calls (one per domain)
├── validators/       # Input validation
├── utils/            # Helper functions
└── data/             # Mock data, translations
```

**Rule of thumb:**
- If it renders UI → `pages/` or `components/`
- If it calls API → `services/`
- If it validates input → `validators/`
- If it's a helper → `utils/`
- If it's mock data → `data/`

---

## 3. Key Concepts & Patterns

### 3.1 Session Management

**Problem:** Backend requires same `session_id` across triage → hospitals → routing for AgentCore memory.

**Solution:** Generate UUID at flow start, store in sessionStorage, send with every API call.

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

export function saveTriageResult(result) {
  sessionStorage.setItem('triage_result', JSON.stringify(result));
}

export function getTriageResult() {
  const data = sessionStorage.getItem('triage_result');
  return data ? JSON.parse(data) : null;
}
```

**Usage in pages:**

```javascript
// pages/triage-wizard.js
import { initSession, getSessionId } from '../utils/session.js';

export function renderTriageWizard(container) {
  initSession(); // Generate UUID on mount
  
  container.innerHTML = `
    <div class="wizard">
      <!-- wizard content -->
    </div>
  `;
  
  attachEventListeners(container);
}

async function handleSubmit(event) {
  event.preventDefault();
  
  const data = collectFormData();
  const sessionId = getSessionId();
  
  try {
    const result = await assessTriage({ ...data, session_id: sessionId });
    saveTriageResult(result);
    navigateTo('/hospitals');
  } catch (error) {
    showError(error.message);
  }
}
```

### 3.2 API Integration Pattern (Minimal Hop)

**Problem:** Need consistent error handling, validation, safety guardrails across all API calls.

**Solution:** One service module per domain, direct Fetch API calls, no nested wrappers.

```javascript
// services/triage.js
const API_URL = import.meta.env.VITE_API_URL;

/**
 * Assess triage for patient symptoms and vitals.
 * Applies safety guardrails before returning.
 * 
 * @param {Object} data - Triage request data
 * @param {string[]} data.symptoms - Patient symptoms
 * @param {Object} data.vitals - Vital signs
 * @param {number} data.age_years - Patient age
 * @param {string} data.sex - Patient sex
 * @param {string} data.session_id - Session ID for AgentCore
 * @returns {Promise<Object>} Triage result
 * @throws {Error} On network or validation failure
 */
export async function assessTriage(data) {
  try {
    const response = await fetch(`${API_URL}/triage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      signal: AbortSignal.timeout(10000) // 10s timeout
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Validate response shape
    if (!result.severity || typeof result.confidence !== 'number') {
      throw new Error('Invalid response shape from API');
    }
    
    // Apply safety guardrails (Antigravity Rule 6)
    return applySafetyGuardrails(result);
    
  } catch (error) {
    console.error('[Triage Service]', error);
    
    // Never silent failures (Antigravity Rule 2.4)
    if (error.name === 'AbortError') {
      throw new Error('Request timeout. Please try again.');
    }
    
    throw error;
  }
}

/**
 * Apply medical safety guardrails to triage result.
 * Conservative defaults on low confidence.
 */
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

/**
 * Get triage report by ID.
 */
export async function getTriageReport(id) {
  const response = await fetch(`${API_URL}/triage/report/${id}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch report: ${response.status}`);
  }
  
  return response.json();
}
```

**Usage in pages:**

```javascript
// pages/triage-wizard.js
import { assessTriage } from '../services/triage.js';
import { showLoading, hideLoading, showError } from '../utils/ui.js';

async function handleAssess() {
  const data = collectFormData();
  
  showLoading();
  
  try {
    const result = await assessTriage(data);
    renderResults(result);
  } catch (error) {
    showError(error.message);
    renderFallbackResults(); // Conservative default
  } finally {
    hideLoading();
  }
}
```

### 3.3 Form Handling Pattern

**Problem:** Complex multi-step forms with validation, error handling.

**Solution:** Vanilla JS form handling with explicit validation.

```javascript
// pages/triage-wizard.js
function renderPatientInfoForm() {
  return `
    <form id="patient-info-form" class="form">
      <div class="form-group">
        <label for="age">Age</label>
        <input 
          type="number" 
          id="age" 
          name="age" 
          min="0" 
          max="150"
          class="form-input"
        />
        <span class="form-error" id="age-error"></span>
      </div>
      
      <div class="form-group">
        <label for="gender">Gender</label>
        <select id="gender" name="gender" class="form-select">
          <option value="">Select...</option>
          <option value="M">Male</option>
          <option value="F">Female</option>
          <option value="Other">Other</option>
        </select>
        <span class="form-error" id="gender-error"></span>
      </div>
      
      <button type="submit" class="btn btn-primary">Next</button>
    </form>
  `;
}

function attachPatientInfoListeners(container) {
  const form = container.querySelector('#patient-info-form');
  
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    
    const data = {
      age: parseInt(form.age.value) || null,
      gender: form.gender.value || null
    };
    
    // Validate
    const errors = validatePatientInfo(data);
    if (Object.keys(errors).length > 0) {
      showFormErrors(errors);
      return;
    }
    
    // Save and proceed
    savePatientInfo(data);
    goToNextStep();
  });
}

function validatePatientInfo(data) {
  const errors = {};
  
  if (data.age !== null && (data.age < 0 || data.age > 150)) {
    errors.age = 'Age must be between 0 and 150';
  }
  
  return errors;
}

function showFormErrors(errors) {
  // Clear previous errors
  document.querySelectorAll('.form-error').forEach(el => el.textContent = '');
  
  // Show new errors
  Object.entries(errors).forEach(([field, message]) => {
    const errorEl = document.getElementById(`${field}-error`);
    if (errorEl) {
      errorEl.textContent = message;
    }
  });
}
```

### 3.4 Component Pattern

**Problem:** Reusable UI elements (badges, cards, etc.)

**Solution:** Pure functions that return DOM elements or HTML strings.

```javascript
// components/severity-badge.js

/**
 * Create a severity badge element.
 * 
 * @param {string} severity - One of: critical, high, medium, low
 * @returns {HTMLElement} Badge element
 */
export function createSeverityBadge(severity) {
  const colors = {
    critical: 'bg-red-600',
    high: 'bg-orange-600',
    medium: 'bg-amber-600',
    low: 'bg-green-600'
  };
  
  const badge = document.createElement('span');
  badge.className = `badge ${colors[severity]} text-white px-4 py-2 rounded-full uppercase font-semibold`;
  badge.textContent = severity;
  badge.setAttribute('role', 'status');
  badge.setAttribute('aria-label', `Severity: ${severity}`);
  
  // Add pulsing animation for critical
  if (severity === 'critical') {
    badge.classList.add('animate-pulse');
  }
  
  return badge;
}

// Usage
const badge = createSeverityBadge('high');
container.appendChild(badge);
```

```javascript
// components/confidence-ring.js

/**
 * Create a confidence ring (circular progress indicator).
 * 
 * @param {number} confidence - Confidence value 0-1
 * @returns {HTMLElement} SVG element
 */
export function createConfidenceRing(confidence) {
  const percentage = Math.round(confidence * 100);
  const circumference = 2 * Math.PI * 45; // radius = 45
  const offset = circumference - (percentage / 100) * circumference;
  
  const color = confidence >= 0.85 ? '#10B981' : '#F59E0B';
  
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('width', '120');
  svg.setAttribute('height', '120');
  svg.setAttribute('viewBox', '0 0 120 120');
  svg.innerHTML = `
    <circle
      cx="60"
      cy="60"
      r="45"
      fill="none"
      stroke="#E5E7EB"
      stroke-width="10"
    />
    <circle
      cx="60"
      cy="60"
      r="45"
      fill="none"
      stroke="${color}"
      stroke-width="10"
      stroke-dasharray="${circumference}"
      stroke-dashoffset="${offset}"
      stroke-linecap="round"
      transform="rotate(-90 60 60)"
    />
    <text
      x="60"
      y="60"
      text-anchor="middle"
      dominant-baseline="middle"
      font-size="24"
      font-weight="bold"
      fill="${color}"
    >
      ${percentage}%
    </text>
  `;
  
  return svg;
}
```

### 3.5 Safety Guardrails Pattern

**Problem:** Must enforce medical safety rules (confidence < 85% → high priority).

**Solution:** Centralized guardrail function applied to all triage results.

```javascript
// utils/safety-guardrails.js

/**
 * Apply medical safety guardrails to triage result.
 * CRITICAL: This function enforces safety rules. Do not bypass.
 * 
 * @param {Object} result - Raw triage result from API
 * @returns {Object} Result with safety guardrails applied
 */
export function applySafetyGuardrails(result) {
  const safeResult = { ...result };
  
  // Rule 1: Low confidence → force high priority (Antigravity 6.2)
  if (safeResult.confidence < 0.85) {
    safeResult.force_high_priority = true;
    safeResult.severity = 'high';
    safeResult.recommendations = [
      'Low confidence assessment. Treating as HIGH priority.',
      ...safeResult.recommendations
    ];
  }
  
  // Rule 2: Critical symptoms → always critical
  const criticalSymptoms = [
    'chest pain',
    'difficulty breathing',
    'unconscious',
    'severe bleeding'
  ];
  
  const hasCriticalSymptom = result.symptoms?.some(symptom =>
    criticalSymptoms.some(critical =>
      symptom.toLowerCase().includes(critical)
    )
  );
  
  if (hasCriticalSymptom) {
    safeResult.severity = 'critical';
  }
  
  // Rule 3: Always include disclaimer (Antigravity 6.1)
  if (!safeResult.safety_disclaimer) {
    safeResult.safety_disclaimer =
      'This system does not provide medical diagnosis. If symptoms are severe, seek emergency care immediately.';
  }
  
  return safeResult;
}

/**
 * Get conservative fallback result when API fails.
 * CRITICAL: Always treat as high priority on failure.
 */
export function getFallbackResult(reason) {
  return {
    severity: 'high',
    confidence: 0.0,
    recommendations: [
      `Unable to complete assessment: ${reason}`,
      'Treating as HIGH priority for safety.',
      'Seek immediate medical attention.'
    ],
    force_high_priority: true,
    safety_disclaimer:
      'This system does not provide medical diagnosis. If symptoms are severe, seek emergency care immediately.'
  };
}
```

---

## 4. Common Tasks & How-Tos

### 4.1 Adding a New Page

```bash
# 1. Create page file
touch src/pages/new-feature.js
```

```javascript
// src/pages/new-feature.js
export function renderNewFeature(container) {
  container.innerHTML = `
    <div class="page">
      <h1>New Feature</h1>
      <p>Content goes here</p>
    </div>
  `;
  
  attachEventListeners(container);
}

function attachEventListeners(container) {
  // Add event listeners
}
```

```javascript
// 2. Add to router (utils/router.js)
const routes = {
  // ... existing routes
  '/new-feature': () => import('../pages/new-feature.js').then(m => m.renderNewFeature)
};
```

```javascript
// 3. Add navigation link (main.js or sidebar)
<a href="#/new-feature">New Feature</a>
```

### 4.2 Adding a New API Endpoint

```javascript
// 1. Add to service module
// src/services/newFeature.js
const API_URL = import.meta.env.VITE_API_URL;

export async function doSomething(data) {
  try {
    const response = await fetch(`${API_URL}/new-feature`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('[NewFeature Service]', error);
    throw error;
  }
}
```

```javascript
// 2. Use in page
import { doSomething } from '../services/newFeature.js';

async function handleSubmit() {
  try {
    const result = await doSomething({ field: 'value' });
    console.log('Success:', result);
  } catch (error) {
    showError(error.message);
  }
}
```

### 4.3 Adding a New Component

```javascript
// src/components/NewComponent.js

/**
 * Create a new component.
 * 
 * @param {Object} props - Component properties
 * @returns {HTMLElement} Component element
 */
export function createNewComponent(props) {
  const element = document.createElement('div');
  element.className = 'new-component';
  element.innerHTML = `
    <h3>${props.title}</h3>
    <p>${props.description}</p>
  `;
  
  return element;
}

// Usage
import { createNewComponent } from '../components/NewComponent.js';

const component = createNewComponent({
  title: 'Hello',
  description: 'World'
});

container.appendChild(component);
```

### 4.4 Adding Translations

```javascript
// src/data/translations.js
export const translations = {
  en: {
    triage: {
      title: 'Triage Assessment',
      steps: {
        patient_info: 'Patient Information',
        symptoms: 'Symptoms',
        vitals: 'Vital Signs',
        results: 'Results'
      }
    }
  },
  hi: {
    triage: {
      title: 'ट्राइएज मूल्यांकन',
      steps: {
        patient_info: 'रोगी की जानकारी',
        symptoms: 'लक्षण',
        vitals: 'महत्वपूर्ण संकेत',
        results: 'परिणाम'
      }
    }
  }
  // ... other languages
};

// utils/i18n.js
import { translations } from '../data/translations.js';

let currentLanguage = localStorage.getItem('language') || 'en';

export function t(key) {
  const keys = key.split('.');
  let value = translations[currentLanguage];
  
  for (const k of keys) {
    value = value?.[k];
  }
  
  return value || key;
}

export function setLanguage(lang) {
  currentLanguage = lang;
  localStorage.setItem('language', lang);
  // Trigger re-render
  window.dispatchEvent(new Event('languagechange'));
}

// Usage
import { t } from '../utils/i18n.js';

const title = t('triage.title'); // "Triage Assessment" or "ट्राइएज मूल्यांकन"
```

---

## 5. Antigravity Rules Compliance

### 5.1 Minimal Hop Rule ✅

```javascript
// ✅ Good: Direct API call
export async function assessTriage(data) {
  const response = await fetch(`${API_URL}/triage`, {
    method: 'POST',
    body: JSON.stringify(data)
  });
  return response.json();
}

// ❌ Bad: Multiple abstraction layers
class ApiWrapper {
  async request() { /* ... */ }
}
class TriageService extends ApiWrapper {
  async assess() { /* ... */ }
}
class TriageAdapter {
  constructor(service) { /* ... */ }
}
```

### 5.2 No Silent Failures ✅

```javascript
// ✅ Good: Log and show error
try {
  const result = await assessTriage(data);
  return result;
} catch (error) {
  console.error('[Triage]', error);
  showError('Assessment failed');
  return getFallbackResult();
}

// ❌ Bad: Silent catch
try {
  const result = await assessTriage(data);
  return result;
} catch (e) {
  // Silent failure
}
```

### 5.3 No Hardcoding ✅

```javascript
// ✅ Good: Environment variable
const API_URL = import.meta.env.VITE_API_URL;

// ❌ Bad: Hardcoded
const API_URL = 'https://prod-api.com';
```

### 5.4 Validate All External Data ✅

```javascript
// ✅ Good: Validate response
const result = await response.json();

if (!result.severity || typeof result.confidence !== 'number') {
  throw new Error('Invalid response shape');
}

// ❌ Bad: Blindly use response
const result = await response.json();
renderResults(result.severity); // Could be undefined!
```

---

## 6. Common Pitfalls & Solutions

### 6.1 Pitfall: Forgetting to Send session_id

**Problem:** Hospital matching fails because session_id is missing.

**Solution:** Always use `getSessionId()` utility.

```javascript
// ❌ Wrong
const response = await fetch(`${API_URL}/hospitals/match`, {
  method: 'POST',
  body: JSON.stringify({ severity, recommendations })
});

// ✅ Correct
import { getSessionId } from '../utils/session.js';

const response = await fetch(`${API_URL}/hospitals/match`, {
  method: 'POST',
  body: JSON.stringify({
    severity,
    recommendations,
    session_id: getSessionId()
  })
});
```

### 6.2 Pitfall: Not Applying Safety Guardrails

**Problem:** Displaying raw API response without safety checks.

**Solution:** Always use `applySafetyGuardrails()`.

```javascript
// ❌ Wrong
const result = await assessTriage(data);
renderResults(result);

// ✅ Correct
import { applySafetyGuardrails } from '../utils/safety-guardrails.js';

const rawResult = await assessTriage(data);
const result = applySafetyGuardrails(rawResult);
renderResults(result);
```

### 6.3 Pitfall: Hardcoding API URLs

**Problem:** API URL changes between environments.

**Solution:** Use environment variables.

```javascript
// ❌ Wrong
const API_URL = 'https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev';

// ✅ Correct
const API_URL = import.meta.env.VITE_API_URL;
```

### 6.4 Pitfall: Not Handling Loading/Error States

**Problem:** UI freezes or shows nothing during API calls.

**Solution:** Always handle loading and error states.

```javascript
// ❌ Wrong
const result = await fetchData();
renderData(result);

// ✅ Correct
showLoading();
try {
  const result = await fetchData();
  renderData(result);
} catch (error) {
  showError(error.message);
} finally {
  hideLoading();
}
```

---

## 7. Code Review Checklist

Before submitting a PR, ensure:

- [ ] No hardcoded values (use environment variables or constants)
- [ ] No console.log statements (use proper logging)
- [ ] Error states handled (try/catch, show errors)
- [ ] Loading states handled (show/hide loading)
- [ ] session_id included in API calls (if applicable)
- [ ] Safety guardrails applied (for triage results)
- [ ] Translations added for all user-facing text
- [ ] Accessibility: keyboard navigation works, ARIA labels present
- [ ] Mobile responsive (test at 375px, 768px, 1024px)
- [ ] Follows Antigravity Rules (minimal hops, no silent failures)
- [ ] No unnecessary abstractions or helper functions
- [ ] Input validation on all forms
- [ ] Disclaimers visible and never collapsible

---

## 8. Useful Commands

```bash
# Development
npm run dev              # Start dev server (http://localhost:5173)
npm run build            # Production build
npm run preview          # Preview production build

# No linting/testing in initial setup (keep it minimal)
```

---

## 9. Resources & References

### Documentation
- [Vite Documentation](https://vitejs.dev/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### Internal Docs
- [Implementation Plan](./implementation_plan.md)
- [Architecture](./web-architecture.md)
- [API Contract](./triage-api-contract.md)
- [Frontend Workflow](./frontend_workflow.md)
- [Antigravity Rules](./rules_anitgravity_frontend.md) (MANDATORY)
- [Task Checklist](./task.md)

### Getting Help
- Check Antigravity Rules first
- Review existing code in codebase
- Search GitHub issues
- Ask in team Slack channel

---

**Remember: Safety > Correctness > Clarity > Reliability > Performance > Aesthetics**

**Follow the Antigravity Rules. Keep it simple. No over-engineering.**
