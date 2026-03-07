/**
 * Triage Wizard Page (4-step wizard)
 * Phase 3 implementation
 */

import { performTriage } from '../services/api.js';
import { getCurrentUser } from '../utils/auth.js';
import { t, getCurrentLanguage } from '../utils/i18n.js';
import { savePatientAssessment } from '../utils/patient-history.js';

const STORAGE_KEY = 'triage_wizard_data';

// Load form data from sessionStorage or initialize
let currentStep = parseInt(sessionStorage.getItem('triage_wizard_step') || '1');
let formData = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '{"patientInfo":{},"symptoms":[],"vitals":{}}');

const STEPS = [
  { id: 1, nameKey: 'patient_info', icon: '👤' },
  { id: 2, nameKey: 'symptoms', icon: '🩺' },
  { id: 3, nameKey: 'vital_signs', icon: '❤️' },
  { id: 4, nameKey: 'results', icon: '📊' },
];

// Save form data to sessionStorage
function saveFormData() {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(formData));
  sessionStorage.setItem('triage_wizard_step', currentStep.toString());
}

// Clear form data
function clearFormData() {
  sessionStorage.removeItem(STORAGE_KEY);
  sessionStorage.removeItem('triage_wizard_step');
  currentStep = 1;
  formData = { patientInfo: {}, symptoms: [], vitals: {} };
}

export function renderTriageWizard(container) {
  console.log('[TriageWizard] Rendering with language:', getCurrentLanguage());
  
  container.innerHTML = `
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-6" style="color: var(--text-primary);">${t('triage_assessment')}</h1>
      
      <!-- Progress Steps -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          ${STEPS.map((step, index) => `
            <div class="flex items-center ${index < STEPS.length - 1 ? 'flex-1' : ''}">
              <div class="flex flex-col items-center">
                <div class="step-indicator ${currentStep >= step.id ? 'active' : ''} ${currentStep > step.id ? 'completed' : ''}">
                  <span class="text-2xl">${step.icon}</span>
                </div>
                <span class="text-sm mt-2" style="color: var(--text-secondary);">${t(step.nameKey)}</span>
              </div>
              ${index < STEPS.length - 1 ? '<div class="step-line flex-1 mx-4"></div>' : ''}
            </div>
          `).join('')}
        </div>
      </div>
      
      <!-- Step Content -->
      <div id="step-content" class="card">
        <!-- Content will be rendered here -->
      </div>
    </div>
  `;
  
  renderStep(container);
}

function renderStep(container) {
  const stepContent = container.querySelector('#step-content');
  
  switch (currentStep) {
    case 1:
      renderPatientInfoStep(stepContent);
      break;
    case 2:
      renderSymptomsStep(stepContent);
      break;
    case 3:
      renderVitalsStep(stepContent);
      break;
    case 4:
      renderResultsStep(stepContent);
      break;
  }
}

function renderPatientInfoStep(container) {
  container.innerHTML = `
    <h2 class="text-xl font-semibold mb-4" style="color: var(--text-primary);">${t('patient_information')}</h2>
    <p class="mb-6" style="color: var(--text-secondary);">${t('basic_patient_details')}</p>
    
    <form id="patient-form" class="space-y-4">
      <div class="form-group">
        <label for="age" class="form-label">${t('age_years')}</label>
        <input 
          type="number" 
          id="age" 
          name="age" 
          class="form-input"
          placeholder="${t('enter_age')}"
          min="0"
          max="150"
          value="${formData.patientInfo.age || ''}"
        />
      </div>
      
      <div class="form-group">
        <label for="sex" class="form-label">${t('sex')}</label>
        <select id="sex" name="sex" class="form-select">
          <option value="">${t('select')}</option>
          <option value="M" ${formData.patientInfo.sex === 'M' ? 'selected' : ''}>${t('male')}</option>
          <option value="F" ${formData.patientInfo.sex === 'F' ? 'selected' : ''}>${t('female')}</option>
          <option value="O" ${formData.patientInfo.sex === 'O' ? 'selected' : ''}>${t('other')}</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="patient_id" class="form-label">${t('patient_id')}</label>
        <input 
          type="text" 
          id="patient_id" 
          name="patient_id" 
          class="form-input"
          placeholder="${t('enter_patient_id')}"
          value="${formData.patientInfo.patient_id || ''}"
        />
      </div>
      
      <div class="flex justify-end gap-4 mt-6">
        <button type="submit" class="btn btn-primary">
          ${t('next_symptoms')}
        </button>
      </div>
    </form>
  `;
  
  const form = container.querySelector('#patient-form');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    formData.patientInfo = {
      age: form.age.value ? parseInt(form.age.value) : null,
      sex: form.sex.value || null,
      patient_id: form.patient_id.value || null,
    };
    currentStep = 2;
    saveFormData();
    renderTriageWizard(document.getElementById('app-content'));
  });
}

function renderSymptomsStep(container) {
  container.innerHTML = `
    <h2 class="text-xl font-semibold mb-4" style="color: var(--text-primary);">${t('symptoms')}</h2>
    <p class="mb-6" style="color: var(--text-secondary);">${t('describe_symptoms')}</p>
    
    <form id="symptoms-form" class="space-y-4">
      <div class="form-group">
        <label for="symptoms" class="form-label">${t('symptoms')} *</label>
        <textarea 
          id="symptoms" 
          name="symptoms" 
          class="form-textarea"
          rows="6"
          placeholder="${t('symptoms_placeholder')}"
          required
        >${formData.symptoms.join('\n')}</textarea>
        <small style="color: var(--text-secondary);">${t('symptoms_help')}</small>
      </div>
      
      <div class="flex justify-between gap-4 mt-6">
        <button type="button" id="back-btn" class="btn btn-secondary">
          ${t('back')}
        </button>
        <button type="submit" class="btn btn-primary">
          ${t('next_vitals')}
        </button>
      </div>
    </form>
  `;
  
  const form = container.querySelector('#symptoms-form');
  const backBtn = container.querySelector('#back-btn');
  
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const symptomsText = form.symptoms.value.trim();
    
    // Split by newlines or commas
    formData.symptoms = symptomsText
      .split(/[\n,]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0);
    
    if (formData.symptoms.length === 0) {
      alert(t('at_least_one_symptom'));
      return;
    }
    
    currentStep = 3;
    saveFormData();
    renderTriageWizard(document.getElementById('app-content'));
  });
  
  backBtn.addEventListener('click', () => {
    currentStep = 1;
    saveFormData();
    renderTriageWizard(document.getElementById('app-content'));
  });
}

function renderVitalsStep(container) {
  container.innerHTML = `
    <h2 class="text-xl font-semibold mb-4" style="color: var(--text-primary);">${t('vital_signs')}</h2>
    <p class="mb-6" style="color: var(--text-secondary);">${t('enter_vitals')}</p>
    
    <form id="vitals-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="form-group">
          <label for="bp" class="form-label">${t('bp_systolic')}</label>
          <input 
            type="number" 
            id="bp" 
            name="bp" 
            class="form-input"
            placeholder="e.g. 120"
            min="0"
            value="${formData.vitals.bp || ''}"
          />
        </div>
        
        <div class="form-group">
          <label for="heart_rate" class="form-label">${t('heart_rate')}</label>
          <input 
            type="number" 
            id="heart_rate" 
            name="heart_rate" 
            class="form-input"
            placeholder="e.g. 80"
            min="0"
            value="${formData.vitals.heart_rate || ''}"
          />
        </div>
        
        <div class="form-group">
          <label for="spo2" class="form-label">${t('spo2')}</label>
          <input 
            type="number" 
            id="spo2" 
            name="spo2" 
            class="form-input"
            placeholder="e.g. 98"
            min="0"
            max="100"
            value="${formData.vitals.spo2 || ''}"
          />
        </div>
        
        <div class="form-group">
          <label for="temp_c" class="form-label">${t('temperature')}</label>
          <input 
            type="number" 
            id="temp_c" 
            name="temp_c" 
            class="form-input"
            placeholder="e.g. 37.5"
            step="0.1"
            min="0"
            value="${formData.vitals.temp_c || ''}"
          />
        </div>
        
        <div class="form-group">
          <label for="respiratory_rate" class="form-label">${t('respiratory_rate')}</label>
          <input 
            type="number" 
            id="respiratory_rate" 
            name="respiratory_rate" 
            class="form-input"
            placeholder="e.g. 16"
            min="0"
            value="${formData.vitals.respiratory_rate || ''}"
          />
        </div>
      </div>
      
      <div class="flex justify-between gap-4 mt-6">
        <button type="button" id="back-btn" class="btn btn-secondary">
          ${t('back')}
        </button>
        <button type="submit" class="btn btn-primary">
          ${t('submit_assessment')}
        </button>
      </div>
    </form>
  `;
  
  const form = container.querySelector('#vitals-form');
  const backBtn = container.querySelector('#back-btn');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Collect vitals (only non-empty values)
    formData.vitals = {};
    ['bp', 'heart_rate', 'spo2', 'temp_c', 'respiratory_rate'].forEach(field => {
      const value = form[field].value;
      if (value) {
        formData.vitals[field] = parseFloat(value);
      }
    });
    
    // Submit to API
    await submitTriage(container);
  });
  
  backBtn.addEventListener('click', () => {
    currentStep = 2;
    saveFormData();
    renderTriageWizard(document.getElementById('app-content'));
  });
}

async function submitTriage(container) {
  const submitBtn = container.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<span class="loading"></span> ${t('analyzing')}`;
  
  try {
    const user = getCurrentUser();
    
    // Get or generate session ID
    let sessionId = sessionStorage.getItem('triage_wizard_session_id');
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      sessionStorage.setItem('triage_wizard_session_id', sessionId);
      console.log('[Triage] Generated new session ID:', sessionId);
    } else {
      console.log('[Triage] Using existing session ID:', sessionId);
    }
    
    // Build API request
    const request = {
      symptoms: formData.symptoms,
      session_id: sessionId,
    };
    
    // Add optional fields
    if (Object.keys(formData.vitals).length > 0) {
      request.vitals = formData.vitals;
    }
    if (formData.patientInfo.age) {
      request.age_years = formData.patientInfo.age;
    }
    if (formData.patientInfo.sex) {
      request.sex = formData.patientInfo.sex;
    }
    if (formData.patientInfo.patient_id) {
      request.patient_id = formData.patientInfo.patient_id;
    }
    if (user) {
      request.submitted_by = user.email;
    }
    
    console.log('[Triage] Submitting:', request);
    
    // Call API
    const result = await performTriage(request);
    
    // Store session_id from response (in case backend generated it)
    if (result.session_id) {
      sessionStorage.setItem('triage_wizard_session_id', result.session_id);
    }
    
    // Store result
    formData.result = result;
    
    // Save to patient history
    try {
      const assessmentId = savePatientAssessment(formData.patientInfo, result, sessionId);
      console.log('[Triage] Saved to patient history:', assessmentId);
    } catch (historyError) {
      console.error('[Triage] Failed to save to history:', historyError);
      // Continue anyway - don't block the flow
    }
    
    // Move to results step
    currentStep = 4;
    renderTriageWizard(document.getElementById('app-content'));
    
  } catch (error) {
    console.error('[Triage] Submission failed:', error);
    alert(`${t('assessment_failed')}: ${error.message}`);
    submitBtn.disabled = false;
    submitBtn.innerHTML = t('submit_assessment');
  }
}

function renderResultsStep(container) {
  const result = formData.result;
  
  if (!result) {
    container.innerHTML = '<p>No results available</p>';
    return;
  }
  
  const severityClass = `badge-${result.severity.toLowerCase()}`;
  const confidencePercent = Math.round(result.confidence * 100);
  
  container.innerHTML = `
    <h2 class="text-xl font-semibold mb-4" style="color: var(--text-primary);">${t('assessment_results')}</h2>
    
    <!-- Severity Badge -->
    <div class="mb-6">
      <div class="flex items-center gap-4 mb-2">
        <span class="badge ${severityClass} text-lg">${result.severity.toUpperCase()}</span>
        <span style="color: var(--text-secondary);">${t('confidence')}: ${confidencePercent}%</span>
      </div>
      ${result.force_high_priority ? `
        <div class="mt-2 p-3 rounded-md" style="background-color: var(--severity-high); color: white;">
          ⚠️ ${t('low_confidence_warning')}
        </div>
      ` : ''}
    </div>
    
    <!-- Recommendations -->
    <div class="mb-6">
      <h3 class="font-semibold mb-3" style="color: var(--text-primary);">${t('recommended_actions')}</h3>
      <ul class="space-y-2">
        ${result.recommendations.map(rec => `
          <li class="flex items-start gap-2">
            <span style="color: var(--primary-600);">•</span>
            <span style="color: var(--text-primary);">${rec}</span>
          </li>
        `).join('')}
      </ul>
    </div>
    
    <!-- Safety Disclaimer -->
    ${result.safety_disclaimer ? `
      <div class="p-4 rounded-md mb-6" style="background-color: var(--gray-100); border-left: 4px solid var(--primary-600);">
        <p style="color: var(--text-primary);">${result.safety_disclaimer}</p>
      </div>
    ` : ''}
    
    <!-- Actions -->
    <div class="flex gap-4 mt-6">
      <button id="new-assessment-btn" class="btn btn-secondary">
        ${t('new_assessment')}
      </button>
      <button id="find-hospitals-btn" class="btn btn-primary">
        ${t('find_hospitals')}
      </button>
    </div>
  `;
  
  const newBtn = container.querySelector('#new-assessment-btn');
  const hospitalsBtn = container.querySelector('#find-hospitals-btn');
  
  newBtn.addEventListener('click', () => {
    clearFormData();
    renderTriageWizard(document.getElementById('app-content'));
  });
  
  hospitalsBtn.addEventListener('click', () => {
    // Store result for hospital matching
    sessionStorage.setItem('triageResult', JSON.stringify(result));
    clearFormData(); // Clear wizard data when moving to hospitals
    window.location.hash = '/hospitals';
  });
}
