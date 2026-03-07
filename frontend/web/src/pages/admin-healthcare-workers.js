/**
 * Admin Healthcare Workers Page
 * View and manage healthcare workers (RMPs, EMTs, etc.)
 */

// Mock data for healthcare workers (will be replaced with API call)
function getMockHealthcareWorkers() {
  return {
    workers: [
      {
        id: 'rmp-001',
        name: 'Dr. Rajesh Kumar',
        role: 'RMP',
        status: 'active',
        current_patient: 'patient-001',
        location: { lat: 12.9716, lon: 77.5946 },
        cases_today: 5,
        cases_total: 234,
        rating: 4.8,
        phone: '+91 98765 43210',
        last_active: new Date().toISOString()
      },
      {
        id: 'rmp-002',
        name: 'Dr. Priya Sharma',
        role: 'RMP',
        status: 'active',
        current_patient: 'patient-002',
        location: { lat: 12.9352, lon: 77.6245 },
        cases_today: 3,
        cases_total: 189,
        rating: 4.9,
        phone: '+91 98765 43211',
        last_active: new Date().toISOString()
      },
      {
        id: 'emt-001',
        name: 'Amit Patel',
        role: 'EMT',
        status: 'available',
        current_patient: null,
        location: { lat: 12.9141, lon: 77.6411 },
        cases_today: 2,
        cases_total: 156,
        rating: 4.7,
        phone: '+91 98765 43212',
        last_active: new Date(Date.now() - 300000).toISOString()
      },
      {
        id: 'rmp-003',
        name: 'Dr. Sunita Reddy',
        role: 'RMP',
        status: 'offline',
        current_patient: null,
        location: { lat: 12.9279, lon: 77.6271 },
        cases_today: 0,
        cases_total: 312,
        rating: 4.6,
        phone: '+91 98765 43213',
        last_active: new Date(Date.now() - 7200000).toISOString()
      }
    ]
  };
}

let refreshInterval = null;
let workersData = [];
let filterStatus = 'all';

export function renderAdminHealthcareWorkers(container) {
  console.log('[AdminHealthcareWorkers] Rendering');
  
  container.innerHTML = `
    <div class="admin-healthcare-workers">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold" style="color: var(--text-primary);">
          Healthcare Workers
        </h1>
        <p style="color: var(--text-secondary);">
          Monitor and manage RMPs, EMTs, and other healthcare workers
        </p>
      </div>
      
      <!-- Filters and Actions -->
      <div class="card mb-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <div>
              <label class="text-sm font-medium" style="color: var(--text-secondary);">Filter by Status:</label>
              <select id="status-filter" class="form-select ml-2">
                <option value="all">All Workers</option>
                <option value="active">Active (On Duty)</option>
                <option value="available">Available</option>
                <option value="offline">Offline</option>
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
          <div class="text-sm" style="color: var(--text-secondary);">Total Workers</div>
          <div class="text-3xl font-bold" style="color: var(--text-primary);">
            <span id="total-workers">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Active (On Duty)</div>
          <div class="text-3xl font-bold" style="color: var(--success);">
            <span id="active-count">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Available</div>
          <div class="text-3xl font-bold" style="color: var(--primary-600);">
            <span id="available-count">-</span>
          </div>
        </div>
        
        <div class="card">
          <div class="text-sm" style="color: var(--text-secondary);">Cases Today</div>
          <div class="text-3xl font-bold" style="color: var(--text-primary);">
            <span id="cases-today">-</span>
          </div>
        </div>
      </div>
      
      <!-- Workers Grid -->
      <div id="workers-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Worker cards will be rendered here -->
      </div>
    </div>
    
    <!-- Worker Detail Modal -->
    <div id="worker-modal" class="modal hidden">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="text-xl font-semibold" style="color: var(--text-primary);">Worker Details</h3>
          <button id="close-modal" class="text-2xl" style="color: var(--text-secondary);">&times;</button>
        </div>
        <div id="modal-body" class="modal-body">
          <!-- Worker details will be rendered here -->
        </div>
      </div>
    </div>
  `;
  
  // Initialize
  initWorkers();
  
  // Set up event listeners
  const refreshBtn = container.querySelector('#refresh-btn');
  const statusFilter = container.querySelector('#status-filter');
  
  refreshBtn.addEventListener('click', () => loadWorkersData());
  statusFilter.addEventListener('change', (e) => {
    filterStatus = e.target.value;
    renderWorkersGrid();
  });
  
  // Start auto-refresh
  startAutoRefresh();
}

async function initWorkers() {
  await loadWorkersData();
}

async function loadWorkersData() {
  console.log('[AdminHealthcareWorkers] Loading data');
  
  try {
    // TODO: Replace with actual API call
    const response = getMockHealthcareWorkers();
    workersData = response.workers || [];
    
    updateStats();
    renderWorkersGrid();
    
    console.log('[AdminHealthcareWorkers] Data loaded successfully');
  } catch (error) {
    console.error('[AdminHealthcareWorkers] Failed to load data:', error);
    showError('Failed to load healthcare worker data');
  }
}

function updateStats() {
  const total = workersData.length;
  const active = workersData.filter(w => w.status === 'active').length;
  const available = workersData.filter(w => w.status === 'available').length;
  const casesToday = workersData.reduce((sum, w) => sum + w.cases_today, 0);
  
  document.getElementById('total-workers').textContent = total;
  document.getElementById('active-count').textContent = active;
  document.getElementById('available-count').textContent = available;
  document.getElementById('cases-today').textContent = casesToday;
}

function renderWorkersGrid() {
  const container = document.getElementById('workers-grid');
  
  // Filter workers
  let filtered = workersData;
  if (filterStatus !== 'all') {
    filtered = workersData.filter(w => w.status === filterStatus);
  }
  
  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-8" style="color: var(--text-secondary);">
        <p>No healthcare workers found</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = filtered.map(worker => {
    const statusColor = {
      active: 'var(--success)',
      available: 'var(--primary-600)',
      offline: 'var(--gray-500)'
    }[worker.status];
    
    const statusText = {
      active: 'Active (On Duty)',
      available: 'Available',
      offline: 'Offline'
    }[worker.status];
    
    const timeSinceActive = getTimeSince(worker.last_active);
    
    return `
      <div class="card hover:shadow-lg transition-shadow cursor-pointer worker-card" data-worker-id="${worker.id}">
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-3">
            <div class="profile-avatar-large">
              ${worker.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div>
              <h3 class="text-lg font-semibold" style="color: var(--text-primary);">
                ${worker.name}
              </h3>
              <div class="text-sm" style="color: var(--text-secondary);">
                ${worker.role} • ${worker.id}
              </div>
            </div>
          </div>
          <div class="text-2xl" style="color: ${statusColor};">●</div>
        </div>
        
        <div class="mb-3">
          <div class="text-sm font-medium mb-1" style="color: ${statusColor};">
            ${statusText}
          </div>
          ${worker.current_patient ? `
            <div class="text-sm" style="color: var(--text-secondary);">
              Currently with: ${worker.current_patient}
            </div>
          ` : `
            <div class="text-sm" style="color: var(--text-secondary);">
              No active patient
            </div>
          `}
        </div>
        
        <div class="space-y-2 mb-3">
          <div class="flex justify-between text-sm">
            <span style="color: var(--text-secondary);">Cases Today:</span>
            <span style="color: var(--text-primary);">${worker.cases_today}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span style="color: var(--text-secondary);">Total Cases:</span>
            <span style="color: var(--text-primary);">${worker.cases_total}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span style="color: var(--text-secondary);">Rating:</span>
            <span style="color: var(--text-primary);">⭐ ${worker.rating}/5.0</span>
          </div>
        </div>
        
        <div class="pt-3 border-t" style="border-color: var(--border-color);">
          <div class="text-xs" style="color: var(--text-secondary);">
            Last active: ${timeSinceActive}
          </div>
        </div>
      </div>
    `;
  }).join('');
  
  // Add click handlers
  container.querySelectorAll('.worker-card').forEach(card => {
    card.addEventListener('click', () => {
      const workerId = card.dataset.workerId;
      showWorkerDetails(workerId);
    });
  });
}

function showWorkerDetails(workerId) {
  const worker = workersData.find(w => w.id === workerId);
  if (!worker) return;
  
  const modal = document.getElementById('worker-modal');
  const modalBody = document.getElementById('modal-body');
  
  const statusColor = {
    active: 'var(--success)',
    available: 'var(--primary-600)',
    offline: 'var(--gray-500)'
  }[worker.status];
  
  modalBody.innerHTML = `
    <div class="space-y-4">
      <!-- Worker Info -->
      <div class="flex items-center gap-4 mb-4">
        <div class="profile-avatar-large">
          ${worker.name.split(' ').map(n => n[0]).join('')}
        </div>
        <div>
          <h4 class="text-xl font-semibold" style="color: var(--text-primary);">${worker.name}</h4>
          <div style="color: var(--text-secondary);">${worker.role} • ${worker.id}</div>
        </div>
      </div>
      
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Status</h4>
        <div class="flex items-center gap-2">
          <span class="text-2xl" style="color: ${statusColor};">●</span>
          <span style="color: ${statusColor}; font-weight: 600;">
            ${worker.status.toUpperCase()}
          </span>
        </div>
      </div>
      
      <!-- Contact Info -->
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Contact Information</h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div style="color: var(--text-secondary);">Phone:</div>
          <div style="color: var(--text-primary);">${worker.phone}</div>
          
          <div style="color: var(--text-secondary);">Location:</div>
          <div style="color: var(--text-primary);">
            ${worker.location.lat.toFixed(4)}, ${worker.location.lon.toFixed(4)}
          </div>
        </div>
      </div>
      
      <!-- Performance Stats -->
      <div>
        <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Performance</h4>
        <div class="grid grid-cols-2 gap-4">
          <div class="text-center p-3 rounded" style="background-color: var(--gray-100);">
            <div class="text-2xl font-bold" style="color: var(--primary-600);">
              ${worker.cases_today}
            </div>
            <div class="text-sm" style="color: var(--text-secondary);">Cases Today</div>
          </div>
          <div class="text-center p-3 rounded" style="background-color: var(--gray-100);">
            <div class="text-2xl font-bold" style="color: var(--primary-600);">
              ${worker.cases_total}
            </div>
            <div class="text-sm" style="color: var(--text-secondary);">Total Cases</div>
          </div>
        </div>
        <div class="mt-3 text-center">
          <div class="text-3xl font-bold" style="color: var(--text-primary);">
            ⭐ ${worker.rating}/5.0
          </div>
          <div class="text-sm" style="color: var(--text-secondary);">Average Rating</div>
        </div>
      </div>
      
      <!-- Current Assignment -->
      ${worker.current_patient ? `
        <div>
          <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Current Assignment</h4>
          <div class="p-3 rounded" style="background-color: var(--primary-100);">
            <div class="font-medium" style="color: var(--primary-700);">
              Patient: ${worker.current_patient}
            </div>
            <div class="text-sm mt-1" style="color: var(--primary-600);">
              Currently en route to hospital
            </div>
          </div>
        </div>
      ` : `
        <div>
          <h4 class="font-semibold mb-2" style="color: var(--text-primary);">Current Assignment</h4>
          <div class="p-3 rounded" style="background-color: var(--gray-100);">
            <div style="color: var(--text-secondary);">
              No active patient assignment
            </div>
          </div>
        </div>
      `}
      
      <!-- Actions -->
      <div class="flex gap-2 pt-4">
        <button id="view-location-btn" class="btn btn-primary">
          📍 View Location
        </button>
        <button id="contact-btn" class="btn btn-secondary">
          📞 Contact
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
  
  document.getElementById('view-location-btn').addEventListener('click', () => {
    alert('Map view coming soon!');
  });
  
  document.getElementById('contact-btn').addEventListener('click', () => {
    window.location.href = `tel:${worker.phone}`;
  });
}

function getTimeSince(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const seconds = Math.floor((now - then) / 1000);
  
  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
  return `${Math.floor(seconds / 86400)} days ago`;
}

function startAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
  
  refreshInterval = setInterval(() => {
    console.log('[AdminHealthcareWorkers] Auto-refreshing data');
    loadWorkersData();
  }, 5000);
  
  console.log('[AdminHealthcareWorkers] Auto-refresh started (5s interval)');
}

export function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}

function showError(message) {
  const container = document.getElementById('workers-grid');
  if (container) {
    container.innerHTML = `
      <div class="col-span-full p-4 rounded-md" style="background-color: var(--error); color: white;">
        ${message}
      </div>
    `;
  }
}
