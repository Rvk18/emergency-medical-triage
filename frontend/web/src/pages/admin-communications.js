/**
 * Admin Communications Hub
 * Chat, broadcast messages, emergency announcements, patient handoff notes
 */

let currentView = 'chat'; // chat, broadcast, announcements, handoffs, logs
let selectedWorker = null;
let messages = [];
let broadcasts = [];
let announcements = [];
let handoffs = [];
let callLogs = [];
let refreshInterval = null;

/**
 * Render admin communications page
 * @param {HTMLElement} container - Container element
 */
export function renderAdminCommunications(container) {
  container.innerHTML = render();
  mount();
}

function render() {
  return `
    <div class="page-container">
      <div class="page-header">
        <h1>💬 Communication Hub</h1>
        <p>Real-time communication with healthcare workers and hospitals</p>
      </div>

      <!-- View Tabs -->
      <div class="comm-tabs">
        <button 
          class="comm-tab ${currentView === 'chat' ? 'active' : ''}"
          onclick="window.adminComm.switchView('chat')"
        >
          💬 Chat
        </button>
        <button 
          class="comm-tab ${currentView === 'broadcast' ? 'active' : ''}"
          onclick="window.adminComm.switchView('broadcast')"
        >
          📢 Broadcast
        </button>
        <button 
          class="comm-tab ${currentView === 'announcements' ? 'active' : ''}"
          onclick="window.adminComm.switchView('announcements')"
        >
          🚨 Emergency Alerts
        </button>
        <button 
          class="comm-tab ${currentView === 'handoffs' ? 'active' : ''}"
          onclick="window.adminComm.switchView('handoffs')"
        >
          📋 Patient Handoffs
        </button>
        <button 
          class="comm-tab ${currentView === 'logs' ? 'active' : ''}"
          onclick="window.adminComm.switchView('logs')"
        >
          📞 Call Logs
        </button>
      </div>

      <!-- Content Area -->
      <div class="comm-content">
        ${renderCurrentView()}
      </div>
    </div>
  `;
}

function renderCurrentView() {
  switch (currentView) {
    case 'chat':
      return renderChatView();
    case 'broadcast':
      return renderBroadcastView();
    case 'announcements':
      return renderAnnouncementsView();
    case 'handoffs':
      return renderHandoffsView();
    case 'logs':
      return renderCallLogsView();
    default:
      return '';
  }
}

// ============================================================================
// CHAT VIEW
// ============================================================================

function renderChatView() {
  return `
    <div class="chat-container">
      <!-- Workers List -->
      <div class="chat-sidebar">
        <div class="chat-sidebar-header">
          <h3>Healthcare Workers</h3>
          <input 
            type="text" 
            placeholder="Search workers..."
            class="search-input"
            oninput="window.adminComm.filterWorkers(this.value)"
          />
        </div>
        <div class="workers-list" id="workersList">
          ${renderWorkersList()}
        </div>
      </div>

      <!-- Chat Area -->
      <div class="chat-main">
        ${selectedWorker ? renderChatMessages() : renderNoChatSelected()}
      </div>
    </div>
  `;
}

function renderWorkersList() {
  // Mock data - replace with actual API call
  const workers = [
    { id: 'w1', name: 'Dr. Sarah Johnson', role: 'Paramedic', status: 'online', unread: 2 },
    { id: 'w2', name: 'John Smith', role: 'EMT', status: 'online', unread: 0 },
    { id: 'w3', name: 'Dr. Emily Chen', role: 'ER Doctor', status: 'busy', unread: 1 },
    { id: 'w4', name: 'Mike Wilson', role: 'Ambulance Driver', status: 'offline', unread: 0 },
  ];

  return workers.map(worker => `
    <div 
      class="worker-item ${selectedWorker?.id === worker.id ? 'active' : ''}"
      onclick="window.adminComm.selectWorker('${worker.id}')"
    >
      <div class="worker-avatar">
        <span class="status-indicator status-${worker.status}"></span>
        ${worker.name.charAt(0)}
      </div>
      <div class="worker-info">
        <div class="worker-name">${worker.name}</div>
        <div class="worker-role">${worker.role}</div>
      </div>
      ${worker.unread > 0 ? `<span class="unread-badge">${worker.unread}</span>` : ''}
    </div>
  `).join('');
}

function renderNoChatSelected() {
  return `
    <div class="no-chat-selected">
      <div class="empty-state-icon">💬</div>
      <h3>Select a healthcare worker to start chatting</h3>
      <p>Choose from the list on the left to view conversation history and send messages</p>
    </div>
  `;
}

function renderChatMessages() {
  // Mock messages - replace with actual API call
  const mockMessages = [
    { id: 1, sender: 'admin', text: 'Patient ETA update?', timestamp: '10:30 AM', read: true },
    { id: 2, sender: 'worker', text: '5 minutes out, preparing for handoff', timestamp: '10:31 AM', read: true },
    { id: 3, sender: 'admin', text: 'Hospital confirmed ready', timestamp: '10:32 AM', read: true },
  ];

  return `
    <div class="chat-header">
      <div class="chat-header-info">
        <h3>${selectedWorker?.name || 'Healthcare Worker'}</h3>
        <span class="status-text">Online</span>
      </div>
      <button class="btn-icon" onclick="window.adminComm.clearChat()">🗑️ Clear</button>
    </div>

    <div class="chat-messages" id="chatMessages">
      ${mockMessages.map(msg => `
        <div class="message ${msg.sender === 'admin' ? 'message-sent' : 'message-received'}">
          <div class="message-content">${msg.text}</div>
          <div class="message-time">${msg.timestamp}</div>
        </div>
      `).join('')}
    </div>

    <div class="chat-input-container">
      <input 
        type="text" 
        id="chatInput"
        placeholder="Type a message..."
        class="chat-input"
        onkeypress="if(event.key==='Enter') window.adminComm.sendMessage()"
      />
      <button class="btn-primary" onclick="window.adminComm.sendMessage()">
        Send
      </button>
    </div>
  `;
}

// ============================================================================
// BROADCAST VIEW
// ============================================================================

function renderBroadcastView() {
  return `
    <div class="broadcast-container">
      <div class="broadcast-form card">
        <h3>📢 Send Broadcast Message</h3>
        <p>Send a message to all healthcare workers or specific groups</p>
        
        <div class="form-group">
          <label>Recipients</label>
          <select id="broadcastRecipients" class="form-select">
            <option value="all">All Healthcare Workers</option>
            <option value="paramedics">Paramedics Only</option>
            <option value="doctors">Doctors Only</option>
            <option value="drivers">Ambulance Drivers Only</option>
            <option value="hospitals">Hospital Staff</option>
          </select>
        </div>

        <div class="form-group">
          <label>Priority</label>
          <select id="broadcastPriority" class="form-select">
            <option value="normal">Normal</option>
            <option value="high">High Priority</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <div class="form-group">
          <label>Message</label>
          <textarea 
            id="broadcastMessage"
            class="form-textarea"
            rows="4"
            placeholder="Enter your broadcast message..."
          ></textarea>
        </div>

        <button class="btn-primary" onclick="window.adminComm.sendBroadcast()">
          📢 Send Broadcast
        </button>
      </div>

      <div class="broadcast-history">
        <h3>Recent Broadcasts</h3>
        ${renderBroadcastHistory()}
      </div>
    </div>
  `;
}

function renderBroadcastHistory() {
  // Mock data
  const mockBroadcasts = [
    { id: 1, message: 'System maintenance scheduled for tonight 11 PM', recipients: 'All', priority: 'normal', time: '2 hours ago', delivered: 45 },
    { id: 2, message: 'New protocol for COVID patients effective immediately', recipients: 'Paramedics', priority: 'high', time: '5 hours ago', delivered: 23 },
  ];

  if (mockBroadcasts.length === 0) {
    return `<div class="empty-state">No broadcasts sent yet</div>`;
  }

  return `
    <div class="broadcast-list">
      ${mockBroadcasts.map(broadcast => `
        <div class="broadcast-item card">
          <div class="broadcast-header">
            <span class="priority-badge priority-${broadcast.priority}">${broadcast.priority}</span>
            <span class="broadcast-time">${broadcast.time}</span>
          </div>
          <div class="broadcast-message">${broadcast.message}</div>
          <div class="broadcast-footer">
            <span>To: ${broadcast.recipients}</span>
            <span>✓ ${broadcast.delivered} delivered</span>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

// ============================================================================
// EMERGENCY ANNOUNCEMENTS VIEW
// ============================================================================

function renderAnnouncementsView() {
  return `
    <div class="announcements-container">
      <div class="announcement-form card alert-danger">
        <h3>🚨 Create Emergency Announcement</h3>
        <p>High-priority alerts for critical situations</p>
        
        <div class="form-group">
          <label>Alert Type</label>
          <select id="alertType" class="form-select">
            <option value="mass-casualty">Mass Casualty Event</option>
            <option value="hospital-divert">Hospital Diversion</option>
            <option value="weather">Severe Weather</option>
            <option value="system">System Emergency</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div class="form-group">
          <label>Announcement Title</label>
          <input 
            type="text" 
            id="alertTitle"
            class="form-input"
            placeholder="Brief title for the alert"
          />
        </div>

        <div class="form-group">
          <label>Details</label>
          <textarea 
            id="alertDetails"
            class="form-textarea"
            rows="4"
            placeholder="Detailed information about the emergency..."
          ></textarea>
        </div>

        <button class="btn-danger" onclick="window.adminComm.sendAlert()">
          🚨 Send Emergency Alert
        </button>
      </div>

      <div class="announcements-list">
        <h3>Active Announcements</h3>
        ${renderActiveAnnouncements()}
      </div>
    </div>
  `;
}

function renderActiveAnnouncements() {
  // Mock data
  const mockAlerts = [
    { id: 1, type: 'hospital-divert', title: 'City General Hospital at Capacity', details: 'Divert all non-critical patients to Regional Medical Center', time: '15 min ago', active: true },
  ];

  if (mockAlerts.length === 0) {
    return `<div class="empty-state">No active announcements</div>`;
  }

  return `
    <div class="alerts-list">
      ${mockAlerts.map(alert => `
        <div class="alert-item card alert-danger">
          <div class="alert-header">
            <span class="alert-type">${alert.type.replace('-', ' ').toUpperCase()}</span>
            <span class="alert-time">${alert.time}</span>
          </div>
          <h4>${alert.title}</h4>
          <p>${alert.details}</p>
          <div class="alert-actions">
            <button class="btn-secondary" onclick="window.adminComm.resolveAlert('${alert.id}')">
              ✓ Resolve
            </button>
            <button class="btn-secondary" onclick="window.adminComm.editAlert('${alert.id}')">
              ✏️ Edit
            </button>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

// ============================================================================
// PATIENT HANDOFFS VIEW
// ============================================================================

function renderHandoffsView() {
  return `
    <div class="handoffs-container">
      <div class="handoffs-header">
        <h3>📋 Patient Handoff Notes</h3>
        <button class="btn-primary" onclick="window.adminComm.createHandoff()">
          + New Handoff Note
        </button>
      </div>

      <div class="handoffs-list">
        ${renderHandoffsList()}
      </div>
    </div>
  `;
}

function renderHandoffsList() {
  // Mock data
  const mockHandoffs = [
    { 
      id: 1, 
      patientId: 'P-2024-001', 
      patientName: 'John Doe',
      from: 'Ambulance A-12',
      to: 'City General ER',
      severity: 'critical',
      notes: 'Cardiac arrest, CPR in progress, ETA 3 minutes',
      time: '5 min ago',
      status: 'pending'
    },
    { 
      id: 2, 
      patientId: 'P-2024-002', 
      patientName: 'Jane Smith',
      from: 'Ambulance A-08',
      to: 'Regional Medical ICU',
      severity: 'high',
      notes: 'Severe trauma, stable vitals, prepared for surgery',
      time: '20 min ago',
      status: 'completed'
    },
  ];

  if (mockHandoffs.length === 0) {
    return `<div class="empty-state">No handoff notes</div>`;
  }

  return mockHandoffs.map(handoff => `
    <div class="handoff-item card">
      <div class="handoff-header">
        <div>
          <h4>${handoff.patientName} (${handoff.patientId})</h4>
          <span class="severity-badge severity-${handoff.severity}">${handoff.severity}</span>
        </div>
        <span class="handoff-time">${handoff.time}</span>
      </div>
      
      <div class="handoff-route">
        <span class="handoff-from">📍 ${handoff.from}</span>
        <span class="handoff-arrow">→</span>
        <span class="handoff-to">🏥 ${handoff.to}</span>
      </div>

      <div class="handoff-notes">${handoff.notes}</div>

      <div class="handoff-footer">
        <span class="status-badge status-${handoff.status}">${handoff.status}</span>
        <div class="handoff-actions">
          <button class="btn-sm" onclick="window.adminComm.viewHandoff('${handoff.id}')">View</button>
          <button class="btn-sm" onclick="window.adminComm.editHandoff('${handoff.id}')">Edit</button>
        </div>
      </div>
    </div>
  `).join('');
}

// ============================================================================
// CALL LOGS VIEW
// ============================================================================

function renderCallLogsView() {
  return `
    <div class="call-logs-container">
      <div class="call-logs-header">
        <h3>📞 Call Logs</h3>
        <div class="call-logs-filters">
          <select class="form-select" onchange="window.adminComm.filterCallLogs(this.value)">
            <option value="all">All Calls</option>
            <option value="incoming">Incoming</option>
            <option value="outgoing">Outgoing</option>
            <option value="missed">Missed</option>
          </select>
          <input 
            type="date" 
            class="form-input"
            onchange="window.adminComm.filterByDate(this.value)"
          />
        </div>
      </div>

      <div class="call-logs-list">
        ${renderCallLogsList()}
      </div>
    </div>
  `;
}

function renderCallLogsList() {
  // Mock data
  const mockLogs = [
    { id: 1, type: 'incoming', from: 'Dr. Sarah Johnson', to: 'Admin', duration: '3:45', time: '10:30 AM', status: 'completed' },
    { id: 2, type: 'outgoing', from: 'Admin', to: 'City General Hospital', duration: '1:20', time: '10:15 AM', status: 'completed' },
    { id: 3, type: 'missed', from: 'Ambulance A-12', to: 'Admin', duration: '0:00', time: '09:45 AM', status: 'missed' },
    { id: 4, type: 'incoming', from: 'Regional Medical Center', to: 'Admin', duration: '5:12', time: '09:30 AM', status: 'completed' },
  ];

  if (mockLogs.length === 0) {
    return `<div class="empty-state">No call logs</div>`;
  }

  return `
    <table class="data-table">
      <thead>
        <tr>
          <th>Type</th>
          <th>From</th>
          <th>To</th>
          <th>Duration</th>
          <th>Time</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        ${mockLogs.map(log => `
          <tr>
            <td>
              <span class="call-type call-${log.type}">
                ${log.type === 'incoming' ? '📞' : log.type === 'outgoing' ? '📱' : '❌'}
                ${log.type}
              </span>
            </td>
            <td>${log.from}</td>
            <td>${log.to}</td>
            <td>${log.duration}</td>
            <td>${log.time}</td>
            <td><span class="status-badge status-${log.status}">${log.status}</span></td>
            <td>
              <button class="btn-sm" onclick="window.adminComm.viewCallDetails('${log.id}')">
                Details
              </button>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

export function mount() {
  // Set up global handlers
  window.adminComm = {
    switchView: (view) => {
      currentView = view;
      const container = document.getElementById('app-content');
      if (container) {
        container.innerHTML = render();
      }
    },
    
    selectWorker: (workerId) => {
      selectedWorker = { id: workerId, name: 'Healthcare Worker' };
      const container = document.getElementById('app-content');
      if (container) {
        container.innerHTML = render();
      }
    },
    
    sendMessage: () => {
      const input = document.getElementById('chatInput');
      if (input && input.value.trim()) {
        console.log('Sending message:', input.value);
        // TODO: Call API to send message
        input.value = '';
      }
    },
    
    sendBroadcast: () => {
      const recipients = document.getElementById('broadcastRecipients')?.value;
      const priority = document.getElementById('broadcastPriority')?.value;
      const message = document.getElementById('broadcastMessage')?.value;
      
      if (message?.trim()) {
        console.log('Sending broadcast:', { recipients, priority, message });
        // TODO: Call API to send broadcast
        alert('Broadcast sent successfully!');
      }
    },
    
    sendAlert: () => {
      const type = document.getElementById('alertType')?.value;
      const title = document.getElementById('alertTitle')?.value;
      const details = document.getElementById('alertDetails')?.value;
      
      if (title?.trim() && details?.trim()) {
        console.log('Sending alert:', { type, title, details });
        // TODO: Call API to send alert
        alert('Emergency alert sent!');
      }
    },
    
    resolveAlert: (alertId) => {
      console.log('Resolving alert:', alertId);
      // TODO: Call API to resolve alert
    },
    
    createHandoff: () => {
      console.log('Creating handoff note');
      // TODO: Show modal to create handoff
    },
    
    viewHandoff: (handoffId) => {
      console.log('Viewing handoff:', handoffId);
      // TODO: Show handoff details
    },
    
    filterCallLogs: (filter) => {
      console.log('Filtering call logs:', filter);
      // TODO: Filter call logs
    },
    
    clearChat: () => {
      if (confirm('Clear chat history?')) {
        console.log('Clearing chat');
        // TODO: Call API to clear chat
      }
    }
  };

  // Start auto-refresh
  startAutoRefresh();
}

export function unmount() {
  stopAutoRefresh();
  delete window.adminComm;
}

function startAutoRefresh() {
  // Refresh data every 5 seconds
  refreshInterval = setInterval(() => {
    // TODO: Fetch latest messages, broadcasts, etc.
    console.log('[Communications] Auto-refresh');
  }, 5000);
}

function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}
