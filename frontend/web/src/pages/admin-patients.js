/**
 * Admin Patients Page
 * View and manage all patients in the system
 */

import { getActivePatients } from '../services/admin-api.js';

let refreshInterval = null;
let patientsData = [];
let filterSeverity = 'all';
let sortBy = 'severity'; // severity, eta, name

export function renderAdminPatients(container) {
  console.log('[AdminPatients] Rendering');
  
  container.innerHTML = `
    <div class="admin-patients">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold" style="color: var(--text-primary);">
          Patient Management
        </h1>
        <p style="color: var(--text-secondary);">
          Monitor and manage all active patients in the system
        </p>
      </div>
      
      <!-- Filters and Actions -->
      <div class="card mb-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <div>
              <label class="text-sm font-medium" style="color: var(--text-secondary);">Filter by Severity:</label>
              <select id="severity-filter" class="form-select ml-2">
                <option value="all">All Patients</option>
                <option value="critical">Critical Only</option>
                <option value="high">High Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="low">Low Priority</option>
              </select>
            </div>
            
            <div>
              <label class="text-sm font-medium" style="color: var(--text-secondary);">Sort by:</label>
              <select id="sort-by" class="form-select ml-2">
                <option value="severity">Severity</option>
                <option value="eta">ETA (Shortest First)</option>
                <option value="name">Patient Name</option>
              </select>
            </div>
          </div>
          
          <button id="refresh-btn" class="btn btn-secondary">
            🔄 Refresh
          </button>
        </div>
      </div>
      
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Total Active</div>
          <div class="text-3xl font-bold" style="color: var(--text-primary);">
            <span id="total-patients">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Critical</div>
          <div class="text-3xl font-bold" style="color: var(--severity-critical);">
            <span id="critical-count">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">High Priority</div>
          <div class="text-3xl font-bold" style="color: var(--severity-high);">
            <span id="high-count">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">En Route</div>
          <div class="text-3xl font-bold" style="color: var(--primary-600);">
            <span id="enroute-count">-</span>
          </div>
        </div>
      </div>
      
      <!-- Patients Table -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-4" style="color: var(--text-primary);">
          Active Patients
        </h2>
        <div id="patients-table" class="overflow-x-auto">
          <!-- Table will be rendered here -->
        </div>
      </div>
    </div>
    
    <!-- Patient Detail Modal -->
    <div id="patient-modal" class="modal hidden">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="text-xl font-semibold" style="color: var(--text-primary);">Patient Details</h3>
          <button id="close-modal" class="text-2xl" style="color: var(--text-secondary);">&times;</button>
        </div>
        <div id="modal-body" class="modal-body">
          <!-- Patient details will be rendered here -->
        </div>
      </div>
    </div>
  `;
  
  // Initialize
  initPatients();
  
  // Set up event listeners
  const refreshBtn = container.querySelector('#refresh-btn');
  const severityFilter = container.querySelector('#severity-filter');
  const sortBySelect = container.querySelector('#sort-by');
  
  refreshBtn.addEventListener('click', () => loadPatientsData());
  severityFilter.addEventListener('change', (e) => {
    filterSeverity = e.target.value;
    renderPatientsTable();
  });
  sortBySelect.addEventListener('change', (e) => {
    sortBy = e.target.value;
    renderPatientsTable();
  });
  
  // Start auto-refresh
  startAutoRefresh();
}

async function initPatients() {
  await loadPatientsData();
}

async function loadPatientsData() {
  console.log('[AdminPatients] Loading data');
  
  try {
    const response = await getActivePatients();
    patientsData = response.patients || [];
    
    updateStats();
    renderPatientsTable();
    
    console.log('[AdminPatients] Data loaded successfully');
  } catch (error) {
    console.error('[AdminPatients] Failed to load data:', error);
    showError('Failed to load patient data');
  }
}

function updateStats() {
  const total = patientsData.length;
  const critical = patientsData.filter(p => p.severity === 'critical').length;
  const high = patientsData.filter(p => p.severity === 'high').length;
  const enroute = patientsData.filter(p => p.status === 'en_route').length;
  
  document.getElementById('total-patients').textContent = total;
  document.getElementById('critical-count').textContent = critical;
  document.getElementById('high-count').textContent = high;
  document.getElementById('enroute-count').textContent = enroute;
}

function renderPatientsTable() {
  const container = document.getElementById('patients-table');
  
  // Filter patients
  let filtered = patientsData;
  if (filterSeverity !== 'all') {
    filtered = patientsData.filter(p => p.severity === filterSeverity);
  }
  
  // Sort patients
  filtered = [...filtered].sort((a, b) => {
    if (sortBy === 'severity') {
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      return severityOrder[a.severity] - severityOrder[b.severity];
    } else if (sortBy === 'eta') {
      return a.eta_minutes - b.eta_minutes;
    } else if (sortBy === 'name') {
      return (a.patient_name || a.id).localeCompare(b.patient_name || b.id);
    }
    return 0;
  });
  
  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="text-center py-8" style="color: var(--text-secondary);">
        <p>No patients found</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = `
    <table class="w-full">
      <thead>
        <tr style="border-bottom: 2px solid var(--border-color);">
          <th class="text-left py-3 px-4" style="color: var(--text-secondary);">Patient</th>
          <th class="text-left py-3 px-4" style="color: var(--text-secondary);">Severity</th>
          <th class="text-left py-3 px-4" style="color: var(--text-secondary);">Destination</th>
          <th class="text-left py-3 px-4" style="color: var(--text-secondary);">ETA</th>
          <th class="text-left py-3 px-4" style="color: var(--text-secondary);">Distance</th>
          <th class="text-left py-3 px-4" style="color: var(--text-secondary);">Status</th>
          <th class="text-left py-3 px-4" style="color: var(--text-secondary);">Actions</th>
        </tr>
      </thead>
      <tbody>
        ${filtered.map(patient => `
          <tr style="border-bottom: 1px solid var(--border-color);" class="hover:bg-gray-50">
            <td class="py-3 px-4">
              <div class="font-semibold" style="color: var(--text-primary);">
                ${patient.patient_name || patient.id}
              </div>
              <div class="text-sm" style="color: var(--text-secondary);">
                ID: ${patient.id}
              </div>
            </td>
            <td class="py-3 px-4">
              <span class="badge badge-${patient.severity}">${patient.severity.toUpperCase()}</span>
            </td>
            <td class="py-3 px-4" style="color: var(--text-primary);">
              ${patient.destination_hospital_name}
            </td>
            <td class="py-3 px-4" style="color: var(--text-primary);">
              ${patient.eta_minutes} min
            </td>
            <td class="py-3 px-4" style="color: var(--text-primary);">
              ${patient.distance_remaining_km.toFixed(1)} km
            </td>
            <td class="py-3 px-4">
              <span class="text-sm px-2 py-1 rounded" style="background-color: var(--primary-100); color: var(--primary-700);">
                ${patient.status.replace('_', ' ')}
              </span>
            </td>
            <td class="py-3 px-4">
              <button class="btn btn-sm btn-secondary view-details-btn" data-patient-id="${patient.id}">
                View Details
              </button>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
  
  // Add click handlers
  container.querySelectorAll('.view-details-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const patientId = btn.dataset.patientId;
      showPatientDetails(patientId);
    });
  });
}

function showPatientDetails(patientId) {
  const patient = patientsData.find(p => p.id === patientId);
  if (!patient) return;
  
  const modal = document.getElementById('patient-modal');
  const modalBody = document.getElementById('modal-body');
  
  modalBody.innerHTML = `
    <div class="space-y-4">
      <!-- Patient Info -->
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Patient Information</h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div style="color: var(--text-secondary);">ID:</div>
          <div style="color: var(--text-primary);">${patient.id}</div>
          
          <div style="color: var(--text-secondary);">Name:</div>
          <div style="color: var(--text-primary);">${patient.patient_name || 'N/A'}</div>
          
          <div style="color: var(--text-secondary);">Severity:</div>
          <div><span class="badge badge-${patient.severity}">${patient.severity.toUpperCase()}</span></div>
          
          <div style="color: var(--text-secondary);">Status:</div>
          <div style="color: var(--text-primary);">${patient.status}</div>
        </div>
      </div>
      
      <!-- Triage Summary -->
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Triage Summary</h4>
        <div class="text-sm">
          <div style="color: var(--text-secondary);" class="mb-1">Symptoms:</div>
          <ul class="list-disc list-inside" style="color: var(--text-primary);">
            ${patient.triage_summary.symptoms.map(s => `<li>${s}</li>`).join('')}
          </ul>
          
          ${patient.triage_summary.vitals ? `
            <div class="mt-2" style="color: var(--text-secondary);">Vitals:</div>
            <div style="color: var(--text-primary);">
              ${Object.entries(patient.triage_summary.vitals).map(([key, value]) => 
                `${key}: ${value}`
              ).join(' • ')}
            </div>
          ` : ''}
        </div>
      </div>
      
      <!-- Route Info -->
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Route Information</h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div style="color: var(--text-secondary);">Destination:</div>
          <div style="color: var(--text-primary);">${patient.destination_hospital_name}</div>
          
          <div style="color: var(--text-secondary);">ETA:</div>
          <div style="color: var(--text-primary);">${patient.eta_minutes} minutes</div>
          
          <div style="color: var(--text-secondary);">Distance:</div>
          <div style="color: var(--text-primary);">${patient.distance_remaining_km.toFixed(1)} km</div>
          
          <div style="color: var(--text-secondary);">Last Updated:</div>
          <div style="color: var(--text-primary);">${new Date(patient.last_updated).toLocaleTimeString()}</div>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex gap-2 pt-4">
        <button id="reroute-btn" class="btn btn-primary" data-patient-id="${patient.id}">
          Re-route Patient
        </button>
        <button id="close-modal-btn" class="btn btn-secondary">
          Close
        </button>
      </div>
    </div>
  `;
  
  modal.classList.remove('hidden');
  
  document.getElementById('close-modal').addEventListener('click', () => {
    modal.classList.add('hidden');
  });
  
  document.getElementById('close-modal-btn').addEventListener('click', () => {
    modal.classList.add('hidden');
  });
  
  document.getElementById('reroute-btn').addEventListener('click', () => {
    alert('Re-routing interface coming soon!');
  });
}

function startAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
  
  refreshInterval = setInterval(() => {
    console.log('[AdminPatients] Auto-refreshing data');
    loadPatientsData();
  }, 5000);
  
  console.log('[AdminPatients] Auto-refresh started (5s interval)');
}

export function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}

function showError(message) {
  const container = document.getElementById('patients-table');
  if (container) {
    container.innerHTML = `
      <div class="p-4 rounded-md" style="background-color: var(--error); color: white;">
        ${message}
      </div>
    `;
  }
}
