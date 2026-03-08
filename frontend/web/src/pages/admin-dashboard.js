/**
 * Admin Dashboard Page
 * Main monitoring and routing interface for administrators
 */

import { getActivePatients, getHospitalStatus } from '../services/admin-api.js';
import { t } from '../utils/i18n.js';
import { 
  loadGoogleMaps, 
  createMap, 
  createPatientMarker, 
  createHospitalMarker,
  fitBoundsToMarkers,
  clearMarkers
} from '../utils/google-maps.js';

let refreshInterval = null;
let patientsData = [];
let hospitalsData = [];
let map = null;
let patientMarkers = [];
let hospitalMarkers = [];
let mapLoaded = false;

export function renderAdminDashboard(container) {
  console.log('[AdminDashboard] Rendering');
  
  container.innerHTML = `
    <div class="admin-dashboard">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold" style="color: var(--text-primary);">
          ${t('admin_dashboard') || 'Admin Dashboard'}
        </h1>
        <p style="color: var(--text-secondary);">
          ${t('monitor_patients_hospitals') || 'Monitor active patients and hospital capacity in real-time'}
        </p>
      </div>
      
      <!-- Dashboard Overview Cards -->
      <div id="overview-cards" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Active Patients</div>
          <div class="text-3xl font-bold" style="color: var(--text-primary);">
            <span id="total-patients">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Critical Cases</div>
          <div class="text-3xl font-bold" style="color: var(--severity-critical);">
            <span id="critical-patients">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Available Hospitals</div>
          <div class="text-3xl font-bold" style="color: var(--success);">
            <span id="available-hospitals">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">System Status</div>
          <div class="text-lg font-semibold" style="color: var(--success);">
            <span id="system-status">● Online</span>
          </div>
        </div>
      </div>
      
      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Map View (Left - 2 columns) -->
        <div class="lg:col-span-2">
          <div class="card">
            <h2 class="text-xl font-semibold mb-4" style="color: var(--text-primary);">
              Live Map
            </h2>
            <div id="admin-map" class="rounded-lg" style="height: 500px; width: 100%; background-color: #E5E7EB;">
              <!-- Google Maps will be rendered here -->
            </div>
          </div>
        </div>
        
        <!-- Patient List (Right - 1 column) -->
        <div class="lg:col-span-1">
          <div class="card">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold" style="color: var(--text-primary);">
                Active Patients
              </h2>
              <button id="refresh-btn" class="btn btn-secondary btn-sm">
                🔄 Refresh
              </button>
            </div>
            
            <div id="patient-list" class="space-y-3" style="max-height: 500px; overflow-y: auto;">
              <!-- Patient cards will be rendered here -->
            </div>
          </div>
        </div>
      </div>
      
      <!-- Hospital Status Panel -->
      <div class="mt-6">
        <div class="card">
          <h2 class="text-xl font-semibold mb-4" style="color: var(--text-primary);">
            Hospital Status
          </h2>
          <div id="hospital-status" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- Hospital cards will be rendered here -->
          </div>
        </div>
      </div>
    </div>
    
    <!-- Patient Detail Modal (hidden by default) -->
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
  initDashboard();
  
  // Set up event listeners
  const refreshBtn = container.querySelector('#refresh-btn');
  refreshBtn.addEventListener('click', () => loadDashboardData());
  
  // Start auto-refresh (every 5 seconds)
  startAutoRefresh();
}

/**
 * Initialize dashboard
 */
async function initDashboard() {
  await loadDashboardData();
  await initMap();
}

/**
 * Initialize Google Maps
 */
async function initMap() {
  const mapContainer = document.getElementById('admin-map');
  if (!mapContainer) return;
  
  try {
    // Load Google Maps API
    await loadGoogleMaps();
    
    // Create map
    map = createMap(mapContainer, {
      center: { lat: 12.9716, lng: 77.5946 }, // Bangalore
      zoom: 12
    });
    
    mapLoaded = true;
    console.log('[AdminDashboard] Google Maps initialized');
    
    // Render markers
    updateMapMarkers();
    
  } catch (error) {
    console.error('[AdminDashboard] Failed to initialize Google Maps:', error);
    mapLoaded = false;
    
    // Show fallback message
    mapContainer.innerHTML = `
      <div style="height: 100%; display: flex; align-items: center; justify-content: center; background-color: #F3F4F6;">
        <div style="text-align: center; color: #6B7280;">
          <p style="font-size: 18px; margin-bottom: 8px;">📍 Map Unavailable</p>
          <p style="font-size: 14px;">Google Maps API key not available.</p>
          <p style="font-size: 12px; margin-top: 8px;">The key is loaded from the backend (GET /config). Ensure <code>google_maps_api_key</code> is set in Terraform and the secret exists. For local dev you can set <code>VITE_GOOGLE_MAPS_API_KEY</code> in .env.</p>
        </div>
      </div>
    `;
  }
}

/**
 * Load all dashboard data
 */
async function loadDashboardData() {
  console.log('[AdminDashboard] Loading data');
  
  try {
    // Fetch data in parallel
    const [patientsResponse, hospitalsResponse] = await Promise.all([
      getActivePatients(),
      getHospitalStatus()
    ]);
    
    patientsData = patientsResponse.patients || [];
    hospitalsData = hospitalsResponse.hospitals || [];
    
    // Update UI
    updateOverviewCards();
    renderPatientList();
    renderHospitalStatus();
    
    // Update map if loaded
    if (mapLoaded && map) {
      updateMapMarkers();
    }
    
    console.log('[AdminDashboard] Data loaded successfully');
  } catch (error) {
    console.error('[AdminDashboard] Failed to load data:', error);
    showError('Failed to load dashboard data');
  }
}

/**
 * Update map markers
 */
function updateMapMarkers() {
  if (!mapLoaded || !map) return;
  
  try {
    // Clear existing markers
    clearMarkers(patientMarkers);
    clearMarkers(hospitalMarkers);
    patientMarkers = [];
    hospitalMarkers = [];
    
    // Add patient markers
    patientsData.forEach(patient => {
      const marker = createPatientMarker(map, patient);
      patientMarkers.push(marker);
    });
    
    // Add hospital markers
    hospitalsData.forEach(hospital => {
      const marker = createHospitalMarker(map, hospital);
      hospitalMarkers.push(marker);
    });
    
    // Fit bounds to show all markers
    const allMarkers = [...patientMarkers, ...hospitalMarkers];
    if (allMarkers.length > 0) {
      fitBoundsToMarkers(map, allMarkers);
    }
    
    console.log('[AdminDashboard] Map markers updated');
  } catch (error) {
    console.error('[AdminDashboard] Failed to update map markers:', error);
  }
}

/**
 * Update overview cards
 */
function updateOverviewCards() {
  const totalPatients = patientsData.length;
  const criticalPatients = patientsData.filter(p => p.severity === 'critical').length;
  const availableHospitals = hospitalsData.filter(h => h.status === 'available').length;
  
  document.getElementById('total-patients').textContent = totalPatients;
  document.getElementById('critical-patients').textContent = criticalPatients;
  document.getElementById('available-hospitals').textContent = availableHospitals;
}

/**
 * Render patient list
 */
function renderPatientList() {
  const container = document.getElementById('patient-list');
  
  if (patientsData.length === 0) {
    container.innerHTML = `
      <div class="text-center py-8" style="color: var(--text-secondary);">
        <p>No active patients</p>
      </div>
    `;
    return;
  }
  
  // Sort by severity (critical first)
  const sortedPatients = [...patientsData].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });
  
  container.innerHTML = sortedPatients.map(patient => `
    <div class="patient-card" data-patient-id="${patient.id}">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <span class="font-semibold" style="color: var(--text-primary);">
              ${patient.patient_name || patient.id}
            </span>
            <span class="badge badge-${patient.severity}">${patient.severity.toUpperCase()}</span>
          </div>
          <div class="text-sm" style="color: var(--text-secondary);">
            → ${patient.destination_hospital_name}
          </div>
          <div class="text-sm mt-1" style="color: var(--text-secondary);">
            ETA: ${patient.eta_minutes} min • ${patient.distance_remaining_km.toFixed(1)} km
          </div>
        </div>
        <button class="btn btn-sm btn-secondary view-details-btn" data-patient-id="${patient.id}">
          View
        </button>
      </div>
    </div>
  `).join('');
  
  // Add click handlers
  container.querySelectorAll('.view-details-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const patientId = btn.dataset.patientId;
      showPatientDetails(patientId);
    });
  });
}

/**
 * Render hospital status
 */
function renderHospitalStatus() {
  const container = document.getElementById('hospital-status');
  
  if (hospitalsData.length === 0) {
    container.innerHTML = `
      <div class="text-center py-8" style="color: var(--text-secondary);">
        <p>No hospital data available</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = hospitalsData.map(hospital => {
    const statusColor = {
      available: 'var(--success)',
      limited: 'var(--warning)',
      full: 'var(--error)',
      unavailable: 'var(--gray-500)'
    }[hospital.status];
    
    const totalBeds = hospital.capacity.emergency.available + 
                      hospital.capacity.icu.available + 
                      hospital.capacity.general.available;
    
    return `
      <div class="hospital-card">
        <div class="flex items-start justify-between mb-2">
          <div class="font-semibold" style="color: var(--text-primary);">
            ${hospital.name}
          </div>
          <div class="text-lg" style="color: ${statusColor};">●</div>
        </div>
        <div class="text-sm mb-2" style="color: var(--text-secondary);">
          ${totalBeds} beds available
        </div>
        <div class="text-xs" style="color: var(--text-secondary);">
          Emergency: ${hospital.capacity.emergency.available}/${hospital.capacity.emergency.total} •
          ICU: ${hospital.capacity.icu.available}/${hospital.capacity.icu.total}
        </div>
        <div class="text-xs mt-1" style="color: var(--text-secondary);">
          ${hospital.incoming_patients} incoming
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Show patient details modal
 */
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
  
  // Show modal
  modal.classList.remove('hidden');
  
  // Add event listeners
  document.getElementById('close-modal').addEventListener('click', () => {
    modal.classList.add('hidden');
  });
  
  document.getElementById('close-modal-btn').addEventListener('click', () => {
    modal.classList.add('hidden');
  });
  
  document.getElementById('reroute-btn').addEventListener('click', () => {
    showRerouteInterface(patient.id);
  });
}

/**
 * Show re-route interface
 */
function showRerouteInterface(patientId) {
  alert('Re-routing interface coming soon!\n\nThis will allow you to:\n- View alternative hospitals\n- Calculate new routes\n- Send notifications to RMP');
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
  // Clear existing interval
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
  
  // Refresh every 5 seconds
  refreshInterval = setInterval(() => {
    console.log('[AdminDashboard] Auto-refreshing data');
    loadDashboardData();
  }, 5000);
  
  console.log('[AdminDashboard] Auto-refresh started (5s interval)');
}

/**
 * Stop auto-refresh (cleanup)
 */
export function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
    console.log('[AdminDashboard] Auto-refresh stopped');
  }
}

/**
 * Show error message
 */
function showError(message) {
  const container = document.getElementById('patient-list');
  if (container) {
    container.innerHTML = `
      <div class="p-4 rounded-md" style="background-color: var(--error); color: white;">
        ${message}
      </div>
    `;
  }
}
