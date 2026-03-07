/**
 * Admin Hospitals Page
 * View and manage all hospitals in the system
 */

import { getHospitalStatus } from '../services/admin-api.js';

let refreshInterval = null;
let hospitalsData = [];

export function renderAdminHospitals(container) {
  console.log('[AdminHospitals] Rendering');
  
  container.innerHTML = `
    <div class="admin-hospitals">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold" style="color: var(--text-primary);">
          Hospital Management
        </h1>
        <p style="color: var(--text-secondary);">
          Monitor hospital capacity and availability across all facilities
        </p>
      </div>
      
      <!-- Actions -->
      <div class="card mb-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button id="refresh-btn" class="btn btn-secondary">
              🔄 Refresh
            </button>
          </div>
          <div class="text-sm" style="color: var(--text-secondary);">
            Auto-refreshing every 5 seconds
          </div>
        </div>
      </div>
      
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Total Hospitals</div>
          <div class="text-3xl font-bold" style="color: var(--text-primary);">
            <span id="total-hospitals">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Available</div>
          <div class="text-3xl font-bold" style="color: var(--success);">
            <span id="available-count">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Limited Capacity</div>
          <div class="text-3xl font-bold" style="color: var(--warning);">
            <span id="limited-count">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Full/Unavailable</div>
          <div class="text-3xl font-bold" style="color: var(--error);">
            <span id="full-count">-</span>
          </div>
        </div>
      </div>
      
      <!-- Hospitals Grid -->
      <div id="hospitals-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Hospital cards will be rendered here -->
      </div>
    </div>
    
    <!-- Hospital Detail Modal -->
    <div id="hospital-modal" class="modal hidden">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="text-xl font-semibold" style="color: var(--text-primary);">Hospital Details</h3>
          <button id="close-modal" class="text-2xl" style="color: var(--text-secondary);">&times;</button>
        </div>
        <div id="modal-body" class="modal-body">
          <!-- Hospital details will be rendered here -->
        </div>
      </div>
    </div>
  `;
  
  // Initialize
  initHospitals();
  
  // Set up event listeners
  const refreshBtn = container.querySelector('#refresh-btn');
  refreshBtn.addEventListener('click', () => loadHospitalsData());
  
  // Start auto-refresh
  startAutoRefresh();
}

async function initHospitals() {
  await loadHospitalsData();
}

async function loadHospitalsData() {
  console.log('[AdminHospitals] Loading data');
  
  try {
    const response = await getHospitalStatus();
    hospitalsData = response.hospitals || [];
    
    updateStats();
    renderHospitalsGrid();
    
    console.log('[AdminHospitals] Data loaded successfully');
  } catch (error) {
    console.error('[AdminHospitals] Failed to load data:', error);
    showError('Failed to load hospital data');
  }
}

function updateStats() {
  const total = hospitalsData.length;
  const available = hospitalsData.filter(h => h.status === 'available').length;
  const limited = hospitalsData.filter(h => h.status === 'limited').length;
  const full = hospitalsData.filter(h => h.status === 'full' || h.status === 'unavailable').length;
  
  document.getElementById('total-hospitals').textContent = total;
  document.getElementById('available-count').textContent = available;
  document.getElementById('limited-count').textContent = limited;
  document.getElementById('full-count').textContent = full;
}

function renderHospitalsGrid() {
  const container = document.getElementById('hospitals-grid');
  
  if (hospitalsData.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-8" style="color: var(--text-secondary);">
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
    
    const statusText = {
      available: 'Available',
      limited: 'Limited Capacity',
      full: 'Full',
      unavailable: 'Unavailable'
    }[hospital.status];
    
    const totalBeds = hospital.capacity.emergency.available + 
                      hospital.capacity.icu.available + 
                      hospital.capacity.general.available;
    
    const totalCapacity = hospital.capacity.emergency.total + 
                          hospital.capacity.icu.total + 
                          hospital.capacity.general.total;
    
    const occupancyPercent = Math.round(((totalCapacity - totalBeds) / totalCapacity) * 100);
    
    return `
      <div class="card hover:shadow-lg transition-shadow cursor-pointer hospital-card" data-hospital-id="${hospital.id}">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="text-lg font-semibold" style="color: var(--text-primary);">
              ${hospital.name}
            </h3>
            <div class="text-sm mt-1" style="color: var(--text-secondary);">
              ID: ${hospital.id}
            </div>
          </div>
          <div class="text-2xl" style="color: ${statusColor};">●</div>
        </div>
        
        <div class="mb-3">
          <div class="text-sm font-medium mb-1" style="color: ${statusColor};">
            ${statusText}
          </div>
          <div class="text-sm" style="color: var(--text-secondary);">
            ${totalBeds} beds available • ${occupancyPercent}% occupied
          </div>
        </div>
        
        <div class="space-y-2 mb-3">
          <div class="flex justify-between text-sm">
            <span style="color: var(--text-secondary);">Emergency:</span>
            <span style="color: var(--text-primary);">
              ${hospital.capacity.emergency.available}/${hospital.capacity.emergency.total}
            </span>
          </div>
          <div class="flex justify-between text-sm">
            <span style="color: var(--text-secondary);">ICU:</span>
            <span style="color: var(--text-primary);">
              ${hospital.capacity.icu.available}/${hospital.capacity.icu.total}
            </span>
          </div>
          <div class="flex justify-between text-sm">
            <span style="color: var(--text-secondary);">General:</span>
            <span style="color: var(--text-primary);">
              ${hospital.capacity.general.available}/${hospital.capacity.general.total}
            </span>
          </div>
        </div>
        
        <div class="pt-3 border-t" style="border-color: var(--border-color);">
          <div class="flex items-center justify-between text-sm">
            <span style="color: var(--text-secondary);">Incoming Patients:</span>
            <span class="font-semibold" style="color: var(--primary-600);">
              ${hospital.incoming_patients}
            </span>
          </div>
        </div>
      </div>
    `;
  }).join('');
  
  // Add click handlers
  container.querySelectorAll('.hospital-card').forEach(card => {
    card.addEventListener('click', () => {
      const hospitalId = card.dataset.hospitalId;
      showHospitalDetails(hospitalId);
    });
  });
}

function showHospitalDetails(hospitalId) {
  const hospital = hospitalsData.find(h => h.id === hospitalId);
  if (!hospital) return;
  
  const modal = document.getElementById('hospital-modal');
  const modalBody = document.getElementById('modal-body');
  
  const statusColor = {
    available: 'var(--success)',
    limited: 'var(--warning)',
    full: 'var(--error)',
    unavailable: 'var(--gray-500)'
  }[hospital.status];
  
  modalBody.innerHTML = `
    <div class="space-y-4">
      <!-- Hospital Info -->
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Hospital Information</h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div style="color: var(--text-secondary);">Name:</div>
          <div style="color: var(--text-primary);">${hospital.name}</div>
          
          <div style="color: var(--text-secondary);">ID:</div>
          <div style="color: var(--text-primary);">${hospital.id}</div>
          
          <div style="color: var(--text-secondary);">Status:</div>
          <div>
            <span class="text-sm px-2 py-1 rounded" style="background-color: ${statusColor}20; color: ${statusColor};">
              ${hospital.status.toUpperCase()}
            </span>
          </div>
          
          <div style="color: var(--text-secondary);">Location:</div>
          <div style="color: var(--text-primary);">
            ${hospital.location.lat.toFixed(4)}, ${hospital.location.lon.toFixed(4)}
          </div>
        </div>
      </div>
      
      <!-- Capacity Details -->
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Capacity Details</h4>
        
        <div class="space-y-3">
          <div>
            <div class="flex justify-between mb-1">
              <span class="text-sm font-medium" style="color: var(--text-secondary);">Emergency Department</span>
              <span class="text-sm" style="color: var(--text-primary);">
                ${hospital.capacity.emergency.available}/${hospital.capacity.emergency.total}
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-green-600 h-2 rounded-full" style="width: ${(hospital.capacity.emergency.available / hospital.capacity.emergency.total) * 100}%"></div>
            </div>
          </div>
          
          <div>
            <div class="flex justify-between mb-1">
              <span class="text-sm font-medium" style="color: var(--text-secondary);">ICU</span>
              <span class="text-sm" style="color: var(--text-primary);">
                ${hospital.capacity.icu.available}/${hospital.capacity.icu.total}
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-blue-600 h-2 rounded-full" style="width: ${(hospital.capacity.icu.available / hospital.capacity.icu.total) * 100}%"></div>
            </div>
          </div>
          
          <div>
            <div class="flex justify-between mb-1">
              <span class="text-sm font-medium" style="color: var(--text-secondary);">General Ward</span>
              <span class="text-sm" style="color: var(--text-primary);">
                ${hospital.capacity.general.available}/${hospital.capacity.general.total}
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-purple-600 h-2 rounded-full" style="width: ${(hospital.capacity.general.available / hospital.capacity.general.total) * 100}%"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Incoming Patients -->
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Incoming Patients</h4>
        <div class="text-2xl font-bold" style="color: var(--primary-600);">
          ${hospital.incoming_patients}
        </div>
        <div class="text-sm" style="color: var(--text-secondary);">
          patients currently en route to this facility
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex gap-2 pt-4">
        <button id="view-map-btn" class="btn btn-primary">
          📍 View on Map
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
  
  document.getElementById('view-map-btn').addEventListener('click', () => {
    alert('Map view coming soon!');
  });
}

function startAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
  
  refreshInterval = setInterval(() => {
    console.log('[AdminHospitals] Auto-refreshing data');
    loadHospitalsData();
  }, 5000);
  
  console.log('[AdminHospitals] Auto-refresh started (5s interval)');
}

export function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}

function showError(message) {
  const container = document.getElementById('hospitals-grid');
  if (container) {
    container.innerHTML = `
      <div class="col-span-full p-4 rounded-md" style="background-color: var(--error); color: white;">
        ${message}
      </div>
    `;
  }
}
