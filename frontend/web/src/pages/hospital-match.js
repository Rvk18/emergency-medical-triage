/**
 * Hospital Match Page
 * Phase 4 implementation
 */

import { matchHospitals } from '../services/api.js';
import { t, getCurrentLanguage } from '../utils/i18n.js';
import { 
  getCurrentPatient, 
  getAllPatients, 
  setCurrentPatientId,
  getPatientDisplayName,
  formatTimestamp,
  updatePatientHospitalMatch
} from '../utils/patient-history.js';

export function renderHospitalMatch(container) {
  console.log('[HospitalMatch] Rendering with language:', getCurrentLanguage());
  
  // Get current patient from history
  const currentPatient = getCurrentPatient();
  const allPatients = getAllPatients();
  
  if (!currentPatient) {
    renderNoTriageData(container);
    return;
  }
  
  const { patientInfo, triageResult, sessionId, hospitalMatch } = currentPatient;
  
  // Get patient identifier
  const patientId = patientInfo?.patient_id || t('unknown_patient');
  const patientAge = patientInfo?.age ? `${patientInfo.age} ${t('years')}` : '';
  const patientSex = patientInfo?.sex ? t(`sex_${patientInfo.sex.toLowerCase()}`) : '';
  const patientInfoText = [patientAge, patientSex].filter(Boolean).join(', ');
  
  container.innerHTML = `
    <div class="max-w-6xl mx-auto">
      <!-- Header with Patient Selector -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-3xl font-bold" style="color: var(--text-primary);">${t('find_hospitals')}</h1>
          ${allPatients.length > 1 ? `
            <button id="show-patient-list-btn" class="btn btn-secondary">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              ${t('patient_history')} (${allPatients.length})
            </button>
          ` : ''}
        </div>
        <p style="color: var(--text-secondary);">
          ${t('patient')}: <span class="font-semibold">${patientId}</span>
          ${patientInfoText ? `<span class="ml-2">(${patientInfoText})</span>` : ''}
        </p>
      </div>
      
      <!-- Patient List Modal (hidden by default) -->
      <div id="patient-list-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);">
        <div class="card max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold" style="color: var(--text-primary);">${t('patient_history')}</h2>
            <button id="close-patient-list-btn" class="p-2 rounded-md hover:bg-gray-100">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div id="patient-list-content"></div>
        </div>
      </div>
      
      <!-- Triage Summary Card -->
      <div class="card mb-6" style="border-left: 4px solid var(--severity-${triageResult.severity.toLowerCase()});">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold" style="color: var(--text-primary);">${t('triage_summary')}</h2>
          <span class="badge badge-${triageResult.severity.toLowerCase()}">${triageResult.severity.toUpperCase()}</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="text-sm" style="color: var(--text-secondary);">${t('confidence')}</p>
            <p class="text-lg font-semibold" style="color: var(--text-primary);">${Math.round(triageResult.confidence * 100)}%</p>
          </div>
          <div>
            <p class="text-sm" style="color: var(--text-secondary);">${t('recommendations')}</p>
            <p class="text-sm" style="color: var(--text-primary);">${triageResult.recommendations.length} ${t('actions')}</p>
          </div>
        </div>
      </div>
      
      <!-- Hospital Matching Section -->
      <div id="hospital-results">
        ${hospitalMatch ? renderHospitalResults(null, hospitalMatch.hospitals, true) : `
          <div class="flex items-center justify-center py-12">
            <button id="find-hospitals-btn" class="btn btn-primary btn-lg">
              ${t('search_hospitals')}
            </button>
          </div>
        `}
      </div>
    </div>
  `;
  
  // Attach event listeners
  const findBtn = container.querySelector('#find-hospitals-btn');
  if (findBtn) {
    findBtn.addEventListener('click', () => findHospitals(container, currentPatient));
  }
  
  const showListBtn = container.querySelector('#show-patient-list-btn');
  if (showListBtn) {
    showListBtn.addEventListener('click', () => showPatientList(container));
  }
  
  const closeListBtn = container.querySelector('#close-patient-list-btn');
  if (closeListBtn) {
    closeListBtn.addEventListener('click', () => hidePatientList());
  }
  
  // Close modal on background click
  const modal = container.querySelector('#patient-list-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        hidePatientList();
      }
    });
  }
}

function renderNoTriageData(container) {
  container.innerHTML = `
    <div class="max-w-4xl mx-auto">
      <div class="card text-center py-12">
        <svg class="w-16 h-16 mx-auto mb-4" style="color: var(--text-secondary);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h2 class="text-xl font-semibold mb-2" style="color: var(--text-primary);">${t('no_triage_data')}</h2>
        <p class="mb-6" style="color: var(--text-secondary);">${t('complete_triage_first')}</p>
        <a href="#/triage" class="btn btn-primary">${t('start_triage')}</a>
      </div>
    </div>
  `;
}

function showPatientList(container) {
  const modal = container.querySelector('#patient-list-modal');
  const content = container.querySelector('#patient-list-content');
  
  if (!modal || !content) return;
  
  const allPatients = getAllPatients();
  const currentPatient = getCurrentPatient();
  
  content.innerHTML = `
    <div class="space-y-2">
      ${allPatients.map(patient => {
        const isActive = currentPatient && patient.id === currentPatient.id;
        const displayName = getPatientDisplayName(patient.patientInfo);
        const timeAgo = formatTimestamp(patient.timestamp);
        
        return `
          <button 
            class="w-full text-left p-4 rounded-md transition-colors ${isActive ? 'bg-primary-50 border-2 border-primary-600' : 'hover:bg-gray-50 border-2 border-transparent'}"
            data-patient-id="${patient.id}"
            onclick="window.switchPatient('${patient.id}')"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-semibold" style="color: var(--text-primary);">${displayName}</span>
                  <span class="badge badge-${patient.triageResult.severity.toLowerCase()}">${patient.triageResult.severity}</span>
                </div>
                <p class="text-sm" style="color: var(--text-secondary);">
                  ${t('confidence')}: ${Math.round(patient.triageResult.confidence * 100)}% • ${timeAgo}
                </p>
              </div>
              ${isActive ? `
                <svg class="w-5 h-5" style="color: var(--primary-600);" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              ` : ''}
            </div>
          </button>
        `;
      }).join('')}
    </div>
  `;
  
  modal.classList.remove('hidden');
}

function hidePatientList() {
  const modal = document.querySelector('#patient-list-modal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

// Global function to switch patients
window.switchPatient = function(patientId) {
  setCurrentPatientId(patientId);
  hidePatientList();
  
  // Re-render the page
  const container = document.getElementById('app-content');
  if (container) {
    renderHospitalMatch(container);
  }
};

async function findHospitals(container, currentPatient) {
  const resultsDiv = container.querySelector('#hospital-results');
  const { triageResult, sessionId, id: patientId } = currentPatient;
  
  // Show loading
  resultsDiv.innerHTML = `
    <div class="flex flex-col items-center justify-center py-12">
      <div class="loading mb-4"></div>
      <p style="color: var(--text-secondary);">${t('searching_hospitals')}</p>
    </div>
  `;
  
  try {
    const request = {
      severity: triageResult.severity,
      recommendations: triageResult.recommendations,
      session_id: sessionId,
      limit: 5,
    };
    
    console.log('[HospitalMatch] Searching hospitals:', request);
    
    const result = await matchHospitals(request);
    
    console.log('[HospitalMatch] Found hospitals:', result);
    
    // Save hospital match to patient history
    updatePatientHospitalMatch(patientId, result);
    
    renderHospitalResults(resultsDiv, result.hospitals);
    
  } catch (error) {
    console.error('[HospitalMatch] Search failed:', error);
    resultsDiv.innerHTML = `
      <div class="card text-center py-8" style="border-left: 4px solid var(--error);">
        <p class="text-lg font-semibold mb-2" style="color: var(--error);">${t('hospital_search_failed')}</p>
        <p class="mb-4" style="color: var(--text-secondary);">${error.message}</p>
        <button id="retry-btn" class="btn btn-secondary">${t('try_again')}</button>
      </div>
    `;
    
    const retryBtn = resultsDiv.querySelector('#retry-btn');
    if (retryBtn) {
      retryBtn.addEventListener('click', () => findHospitals(container, currentPatient));
    }
  }
}

function renderHospitalResults(container, hospitals, skipContainer = false) {
  if (!hospitals || hospitals.length === 0) {
    const html = `
      <div class="card text-center py-8">
        <p class="text-lg font-semibold mb-2" style="color: var(--text-primary);">${t('no_hospitals_found')}</p>
        <p style="color: var(--text-secondary);">${t('no_hospitals_message')}</p>
      </div>
    `;
    
    if (skipContainer) {
      return html;
    } else {
      container.innerHTML = html;
      return;
    }
  }
  
  const html = `
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-xl font-semibold" style="color: var(--text-primary);">${t('recommended_hospitals')}</h2>
      <span style="color: var(--text-secondary);">${hospitals.length} ${t('hospitals_found')}</span>
    </div>
    
    <div class="space-y-4">
      ${hospitals.map((hospital, index) => renderHospitalCard(hospital, index)).join('')}
    </div>
    
    <div class="mt-6 flex gap-4">
      <a href="#/triage" class="btn btn-secondary">${t('new_assessment')}</a>
    </div>
  `;
  
  if (skipContainer) {
    return html;
  } else {
    container.innerHTML = html;
  }
}

function renderHospitalCard(hospital, index) {
  const matchScore = hospital.match_score || hospital.matchScore || 0;
  const matchPercent = Math.round(matchScore * 100);
  const distance = hospital.distance_km || hospital.distanceKm || 0;
  const beds = hospital.available_beds || hospital.availableBeds || 0;
  const specialist = hospital.specialist_available || hospital.specialistAvailable || false;
  
  // Get translated reason - use reason_key if available, otherwise use reason directly
  const reasonKey = hospital.reason_key || hospital.reasonKey;
  const reason = reasonKey ? t(reasonKey) : (hospital.reason || '');
  
  return `
    <div class="card hover:shadow-lg transition-shadow">
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-2">
            <span class="flex items-center justify-center w-8 h-8 rounded-full" style="background-color: var(--primary-100); color: var(--primary-600); font-weight: 600;">
              ${index + 1}
            </span>
            <h3 class="text-lg font-semibold" style="color: var(--text-primary);">${hospital.name}</h3>
          </div>
          <p class="text-sm mb-2" style="color: var(--text-secondary);">${hospital.address || t('address_not_available')}</p>
        </div>
        <div class="text-right">
          <div class="text-2xl font-bold" style="color: var(--primary-600);">${matchPercent}%</div>
          <div class="text-xs" style="color: var(--text-secondary);">${t('match')}</div>
        </div>
      </div>
      
      <div class="grid grid-cols-3 gap-4 mb-4">
        <div class="text-center p-3 rounded-md" style="background-color: var(--gray-50);">
          <div class="text-lg font-semibold" style="color: var(--text-primary);">${distance.toFixed(1)} km</div>
          <div class="text-xs" style="color: var(--text-secondary);">${t('distance')}</div>
        </div>
        <div class="text-center p-3 rounded-md" style="background-color: var(--gray-50);">
          <div class="text-lg font-semibold" style="color: var(--text-primary);">${beds}</div>
          <div class="text-xs" style="color: var(--text-secondary);">${t('beds_available')}</div>
        </div>
        <div class="text-center p-3 rounded-md" style="background-color: var(--gray-50);">
          <div class="text-lg font-semibold" style="color: ${specialist ? 'var(--success)' : 'var(--text-secondary)'};">
            ${specialist ? '✓' : '—'}
          </div>
          <div class="text-xs" style="color: var(--text-secondary);">${t('specialist')}</div>
        </div>
      </div>
      
      ${reason ? `
        <div class="p-3 rounded-md mb-4" style="background-color: var(--primary-50); border-left: 3px solid var(--primary-600);">
          <p class="text-sm" style="color: var(--text-primary);">${reason}</p>
        </div>
      ` : ''}
      
      <div class="flex gap-2">
        <button class="btn btn-primary flex-1" onclick="alert('${t('navigation_coming_soon')}')">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          ${t('get_directions')}
        </button>
        <button class="btn btn-secondary" onclick="alert('${t('call_coming_soon')}')">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
          </svg>
        </button>
      </div>
    </div>
  `;
}
