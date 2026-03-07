/**
 * Admin Analytics & Reports
 * Data visualization and reporting for emergency medical triage system
 */

import Chart from 'chart.js/auto';

let currentView = 'overview'; // overview, response-time, utilization, severity, peak-hours, heatmap, reports
let dateRange = 'week'; // today, week, month, year, custom
let refreshInterval = null;
let charts = {}; // Store chart instances for cleanup

/**
 * Render admin analytics page
 * @param {HTMLElement} container - Container element
 */
export function renderAdminAnalytics(container) {
  container.innerHTML = render();
  mount();
}

function render() {
  return `
    <div class="page-container">
      <div class="page-header">
        <h1>📈 Analytics & Reports</h1>
        <p>Data-driven insights for emergency medical operations</p>
      </div>

      <!-- Date Range Selector -->
      <div class="analytics-controls">
        <div class="date-range-selector">
          <button class="date-btn ${dateRange === 'today' ? 'active' : ''}" onclick="window.adminAnalytics.setDateRange('today')">Today</button>
          <button class="date-btn ${dateRange === 'week' ? 'active' : ''}" onclick="window.adminAnalytics.setDateRange('week')">This Week</button>
          <button class="date-btn ${dateRange === 'month' ? 'active' : ''}" onclick="window.adminAnalytics.setDateRange('month')">This Month</button>
          <button class="date-btn ${dateRange === 'year' ? 'active' : ''}" onclick="window.adminAnalytics.setDateRange('year')">This Year</button>
          <button class="date-btn ${dateRange === 'custom' ? 'active' : ''}" onclick="window.adminAnalytics.setDateRange('custom')">Custom</button>
        </div>
        <button class="btn-primary" onclick="window.adminAnalytics.exportReport()">
          📥 Export Report
        </button>
      </div>

      <!-- View Tabs -->
      <div class="analytics-tabs">
        <button class="analytics-tab ${currentView === 'overview' ? 'active' : ''}" onclick="window.adminAnalytics.switchView('overview')">
          📊 Overview
        </button>
        <button class="analytics-tab ${currentView === 'response-time' ? 'active' : ''}" onclick="window.adminAnalytics.switchView('response-time')">
          ⏱️ Response Time
        </button>
        <button class="analytics-tab ${currentView === 'utilization' ? 'active' : ''}" onclick="window.adminAnalytics.switchView('utilization')">
          🏥 Hospital Utilization
        </button>
        <button class="analytics-tab ${currentView === 'severity' ? 'active' : ''}" onclick="window.adminAnalytics.switchView('severity')">
          🚨 Severity Distribution
        </button>
        <button class="analytics-tab ${currentView === 'peak-hours' ? 'active' : ''}" onclick="window.adminAnalytics.switchView('peak-hours')">
          📅 Peak Hours
        </button>
        <button class="analytics-tab ${currentView === 'heatmap' ? 'active' : ''}" onclick="window.adminAnalytics.switchView('heatmap')">
          🗺️ Geographic Heatmap
        </button>
        <button class="analytics-tab ${currentView === 'reports' ? 'active' : ''}" onclick="window.adminAnalytics.switchView('reports')">
          📄 Reports
        </button>
      </div>

      <!-- Content Area -->
      <div class="analytics-content">
        ${renderCurrentView()}
      </div>
    </div>
  `;
}

function renderCurrentView() {
  switch (currentView) {
    case 'overview':
      return renderOverview();
    case 'response-time':
      return renderResponseTime();
    case 'utilization':
      return renderUtilization();
    case 'severity':
      return renderSeverity();
    case 'peak-hours':
      return renderPeakHours();
    case 'heatmap':
      return renderHeatmap();
    case 'reports':
      return renderReports();
    default:
      return '';
  }
}

// ============================================================================
// OVERVIEW
// ============================================================================

function renderOverview() {
  return `
    <div class="analytics-overview">
      <!-- Key Metrics -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">⏱️</div>
          <div class="metric-value">12.5 min</div>
          <div class="metric-label">Avg Response Time</div>
          <div class="metric-change positive">↓ 8% from last week</div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">🚑</div>
          <div class="metric-value">247</div>
          <div class="metric-label">Total Patients</div>
          <div class="metric-change positive">↑ 12% from last week</div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">🏥</div>
          <div class="metric-value">78%</div>
          <div class="metric-label">Hospital Utilization</div>
          <div class="metric-change neutral">→ Same as last week</div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">🚨</div>
          <div class="metric-value">23</div>
          <div class="metric-label">Critical Cases</div>
          <div class="metric-change negative">↑ 15% from last week</div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <div class="chart-card">
          <h3>Response Time Trend</h3>
          <div class="chart-placeholder">
            <canvas id="responseTimeChart" width="400" height="200"></canvas>
          </div>
        </div>
        
        <div class="chart-card">
          <h3>Patient Severity Distribution</h3>
          <div class="chart-placeholder">
            <canvas id="severityChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="activity-card">
        <h3>Recent Activity Highlights</h3>
        <div class="activity-list">
          <div class="activity-item">
            <span class="activity-time">2 min ago</span>
            <span class="activity-text">Peak hour detected: 45 patients in last hour</span>
          </div>
          <div class="activity-item">
            <span class="activity-time">15 min ago</span>
            <span class="activity-text">City General Hospital reached 90% capacity</span>
          </div>
          <div class="activity-item">
            <span class="activity-time">1 hour ago</span>
            <span class="activity-text">Average response time improved by 2 minutes</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

// ============================================================================
// RESPONSE TIME METRICS
// ============================================================================

function renderResponseTime() {
  return `
    <div class="response-time-view">
      <div class="view-header">
        <h2>⏱️ Response Time Analysis</h2>
        <p>Average time from triage to hospital arrival</p>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-label">Average Response Time</div>
          <div class="stat-value">12.5 min</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Fastest Response</div>
          <div class="stat-value">4.2 min</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Slowest Response</div>
          <div class="stat-value">28.7 min</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Median Response</div>
          <div class="stat-value">11.3 min</div>
        </div>
      </div>

      <!-- Detailed Chart -->
      <div class="chart-card large">
        <h3>Response Time Breakdown</h3>
        <div class="chart-placeholder large">
          <canvas id="responseTimeDetailChart"></canvas>
        </div>
      </div>

      <!-- By Severity -->
      <div class="chart-card">
        <h3>Response Time by Severity</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Avg Time</th>
              <th>Cases</th>
              <th>Target</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="severity-badge severity-critical">Critical</span></td>
              <td>8.2 min</td>
              <td>23</td>
              <td>&lt; 10 min</td>
              <td><span class="status-badge status-success">✓ On Target</span></td>
            </tr>
            <tr>
              <td><span class="severity-badge severity-high">High</span></td>
              <td>11.5 min</td>
              <td>45</td>
              <td>&lt; 15 min</td>
              <td><span class="status-badge status-success">✓ On Target</span></td>
            </tr>
            <tr>
              <td><span class="severity-badge severity-medium">Medium</span></td>
              <td>14.8 min</td>
              <td>89</td>
              <td>&lt; 20 min</td>
              <td><span class="status-badge status-success">✓ On Target</span></td>
            </tr>
            <tr>
              <td><span class="severity-badge severity-low">Low</span></td>
              <td>18.3 min</td>
              <td>90</td>
              <td>&lt; 30 min</td>
              <td><span class="status-badge status-success">✓ On Target</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ============================================================================
// HOSPITAL UTILIZATION
// ============================================================================

function renderUtilization() {
  return `
    <div class="utilization-view">
      <div class="view-header">
        <h2>🏥 Hospital Utilization Trends</h2>
        <p>Capacity and usage patterns over time</p>
      </div>

      <!-- Utilization Chart -->
      <div class="chart-card large">
        <h3>Utilization Over Time</h3>
        <div class="chart-placeholder large">
          <canvas id="utilizationChart"></canvas>
        </div>
      </div>

      <!-- By Hospital -->
      <div class="hospitals-grid">
        ${renderHospitalUtilization()}
      </div>

      <!-- Department Breakdown -->
      <div class="chart-card">
        <h3>Department Utilization</h3>
        <div class="department-bars">
          <div class="dept-bar">
            <div class="dept-label">Emergency</div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 85%">85%</div>
            </div>
          </div>
          <div class="dept-bar">
            <div class="dept-label">ICU</div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 72%">72%</div>
            </div>
          </div>
          <div class="dept-bar">
            <div class="dept-label">General</div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 68%">68%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderHospitalUtilization() {
  const hospitals = [
    { name: 'City General Hospital', utilization: 92, beds: 45, available: 4, trend: 'up' },
    { name: 'Regional Medical Center', utilization: 78, beds: 60, available: 13, trend: 'stable' },
    { name: 'St. Mary\'s Hospital', utilization: 65, beds: 35, available: 12, trend: 'down' },
  ];

  return hospitals.map(h => `
    <div class="hospital-util-card">
      <h4>${h.name}</h4>
      <div class="util-percentage ${h.utilization > 85 ? 'high' : h.utilization > 70 ? 'medium' : 'low'}">
        ${h.utilization}%
      </div>
      <div class="util-details">
        <div>${h.beds - h.available}/${h.beds} beds occupied</div>
        <div>${h.available} available</div>
      </div>
      <div class="util-trend trend-${h.trend}">
        ${h.trend === 'up' ? '↑' : h.trend === 'down' ? '↓' : '→'} ${h.trend}
      </div>
    </div>
  `).join('');
}

// ============================================================================
// SEVERITY DISTRIBUTION
// ============================================================================

function renderSeverity() {
  return `
    <div class="severity-view">
      <div class="view-header">
        <h2>🚨 Patient Severity Distribution</h2>
        <p>Breakdown of patient cases by severity level</p>
      </div>

      <div class="charts-row">
        <!-- Pie Chart -->
        <div class="chart-card">
          <h3>Current Distribution</h3>
          <div class="chart-placeholder">
            <canvas id="severityPieChart"></canvas>
          </div>
          <div class="severity-legend">
            <div class="legend-item"><span class="dot critical"></span> Critical: 23 (9%)</div>
            <div class="legend-item"><span class="dot high"></span> High: 45 (18%)</div>
            <div class="legend-item"><span class="dot medium"></span> Medium: 89 (36%)</div>
            <div class="legend-item"><span class="dot low"></span> Low: 90 (37%)</div>
          </div>
        </div>

        <!-- Trend Chart -->
        <div class="chart-card">
          <h3>Severity Trend</h3>
          <div class="chart-placeholder">
            <canvas id="severityTrendChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Detailed Table -->
      <div class="chart-card">
        <h3>Severity Metrics</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Count</th>
              <th>Percentage</th>
              <th>Avg Response Time</th>
              <th>Outcomes</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="severity-badge severity-critical">Critical</span></td>
              <td>23</td>
              <td>9%</td>
              <td>8.2 min</td>
              <td><span class="outcome-badge success">95% Stable</span></td>
            </tr>
            <tr>
              <td><span class="severity-badge severity-high">High</span></td>
              <td>45</td>
              <td>18%</td>
              <td>11.5 min</td>
              <td><span class="outcome-badge success">98% Stable</span></td>
            </tr>
            <tr>
              <td><span class="severity-badge severity-medium">Medium</span></td>
              <td>89</td>
              <td>36%</td>
              <td>14.8 min</td>
              <td><span class="outcome-badge success">99% Stable</span></td>
            </tr>
            <tr>
              <td><span class="severity-badge severity-low">Low</span></td>
              <td>90</td>
              <td>37%</td>
              <td>18.3 min</td>
              <td><span class="outcome-badge success">100% Stable</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ============================================================================
// PEAK HOURS ANALYSIS
// ============================================================================

function renderPeakHours() {
  return `
    <div class="peak-hours-view">
      <div class="view-header">
        <h2>📅 Peak Hours Analysis</h2>
        <p>Identify high-demand periods for resource planning</p>
      </div>

      <!-- Heatmap by Hour and Day -->
      <div class="chart-card large">
        <h3>Weekly Pattern</h3>
        <div class="heatmap-grid">
          ${renderHourlyHeatmap()}
        </div>
      </div>

      <!-- Hourly Distribution -->
      <div class="chart-card">
        <h3>Average Patients by Hour</h3>
        <div class="chart-placeholder">
          <canvas id="hourlyChart"></canvas>
        </div>
      </div>

      <!-- Peak Insights -->
      <div class="insights-grid">
        <div class="insight-card">
          <div class="insight-icon">🔥</div>
          <div class="insight-title">Busiest Hour</div>
          <div class="insight-value">2:00 PM - 3:00 PM</div>
          <div class="insight-detail">Avg 18 patients/hour</div>
        </div>
        <div class="insight-card">
          <div class="insight-icon">😌</div>
          <div class="insight-title">Quietest Hour</div>
          <div class="insight-value">4:00 AM - 5:00 AM</div>
          <div class="insight-detail">Avg 3 patients/hour</div>
        </div>
        <div class="insight-card">
          <div class="insight-icon">📆</div>
          <div class="insight-title">Busiest Day</div>
          <div class="insight-value">Friday</div>
          <div class="insight-detail">Avg 42 patients/day</div>
        </div>
        <div class="insight-card">
          <div class="insight-icon">🌙</div>
          <div class="insight-title">Weekend Pattern</div>
          <div class="insight-value">15% Higher</div>
          <div class="insight-detail">vs weekday average</div>
        </div>
      </div>
    </div>
  `;
}

function renderHourlyHeatmap() {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const hours = Array.from({length: 24}, (_, i) => i);
  
  // Mock data - intensity from 0-100
  const getIntensity = (day, hour) => {
    // Simulate peak hours (9am-5pm) and weekend patterns
    const isWeekend = day >= 5;
    const isPeakHour = hour >= 9 && hour <= 17;
    const base = Math.random() * 30;
    const peak = isPeakHour ? 40 : 0;
    const weekend = isWeekend ? 20 : 0;
    return Math.min(100, base + peak + weekend);
  };

  let html = '<div class="heatmap-labels-y">';
  days.forEach(day => {
    html += `<div class="heatmap-label">${day}</div>`;
  });
  html += '</div><div class="heatmap-cells">';
  
  days.forEach((day, dayIdx) => {
    html += '<div class="heatmap-row">';
    hours.forEach(hour => {
      const intensity = getIntensity(dayIdx, hour);
      const level = intensity > 75 ? 'high' : intensity > 50 ? 'medium' : intensity > 25 ? 'low' : 'minimal';
      html += `<div class="heatmap-cell ${level}" title="${day} ${hour}:00 - ${Math.round(intensity)}% capacity"></div>`;
    });
    html += '</div>';
  });
  
  html += '</div><div class="heatmap-labels-x">';
  for (let i = 0; i < 24; i += 3) {
    html += `<div class="heatmap-label">${i}:00</div>`;
  }
  html += '</div>';
  
  return html;
}

// ============================================================================
// GEOGRAPHIC HEATMAP
// ============================================================================

function renderHeatmap() {
  return `
    <div class="heatmap-view">
      <div class="view-header">
        <h2>🗺️ Geographic Heatmap</h2>
        <p>Emergency call distribution across the region</p>
      </div>

      <!-- Map Container -->
      <div class="map-card large">
        <div class="map-controls">
          <select class="form-select" onchange="window.adminAnalytics.changeHeatmapMetric(this.value)">
            <option value="calls">Emergency Calls</option>
            <option value="response-time">Avg Response Time</option>
            <option value="severity">Critical Cases</option>
          </select>
        </div>
        <div class="map-placeholder">
          <div class="map-mock">
            🗺️ Google Maps with heatmap overlay showing emergency call density
            <br><br>
            <div style="text-align: left; max-width: 400px; margin: 20px auto;">
              <strong>Hotspots:</strong><br>
              🔴 Downtown Area: 45 calls<br>
              🟠 East District: 32 calls<br>
              🟡 North Suburbs: 28 calls<br>
              🟢 West Side: 18 calls<br>
              🔵 South Region: 12 calls
            </div>
          </div>
        </div>
      </div>

      <!-- Regional Stats -->
      <div class="regions-grid">
        <div class="region-card">
          <h4>Downtown</h4>
          <div class="region-stat">45 calls</div>
          <div class="region-detail">Avg response: 9.2 min</div>
          <div class="region-hospitals">3 hospitals nearby</div>
        </div>
        <div class="region-card">
          <h4>East District</h4>
          <div class="region-stat">32 calls</div>
          <div class="region-detail">Avg response: 11.5 min</div>
          <div class="region-hospitals">2 hospitals nearby</div>
        </div>
        <div class="region-card">
          <h4>North Suburbs</h4>
          <div class="region-stat">28 calls</div>
          <div class="region-detail">Avg response: 14.8 min</div>
          <div class="region-hospitals">2 hospitals nearby</div>
        </div>
        <div class="region-card">
          <h4>West Side</h4>
          <div class="region-stat">18 calls</div>
          <div class="region-detail">Avg response: 13.2 min</div>
          <div class="region-hospitals">1 hospital nearby</div>
        </div>
      </div>
    </div>
  `;
}

// ============================================================================
// REPORTS
// ============================================================================

function renderReports() {
  return `
    <div class="reports-view">
      <div class="view-header">
        <h2>📄 Reports & Exports</h2>
        <p>Generate and download comprehensive reports</p>
      </div>

      <!-- Quick Reports -->
      <div class="reports-grid">
        <div class="report-card">
          <div class="report-icon">📊</div>
          <h3>Daily Summary</h3>
          <p>Complete overview of today's operations</p>
          <div class="report-actions">
            <button class="btn-secondary" onclick="window.adminAnalytics.generateReport('daily', 'pdf')">PDF</button>
            <button class="btn-secondary" onclick="window.adminAnalytics.generateReport('daily', 'csv')">CSV</button>
          </div>
        </div>

        <div class="report-card">
          <div class="report-icon">📅</div>
          <h3>Weekly Report</h3>
          <p>7-day performance and trends</p>
          <div class="report-actions">
            <button class="btn-secondary" onclick="window.adminAnalytics.generateReport('weekly', 'pdf')">PDF</button>
            <button class="btn-secondary" onclick="window.adminAnalytics.generateReport('weekly', 'csv')">CSV</button>
          </div>
        </div>

        <div class="report-card">
          <div class="report-icon">📆</div>
          <h3>Monthly Report</h3>
          <p>Comprehensive monthly analysis</p>
          <div class="report-actions">
            <button class="btn-secondary" onclick="window.adminAnalytics.generateReport('monthly', 'pdf')">PDF</button>
            <button class="btn-secondary" onclick="window.adminAnalytics.generateReport('monthly', 'csv')">CSV</button>
          </div>
        </div>

        <div class="report-card">
          <div class="report-icon">🎯</div>
          <h3>Custom Report</h3>
          <p>Build your own report</p>
          <div class="report-actions">
            <button class="btn-primary" onclick="window.adminAnalytics.openCustomReport()">Configure</button>
          </div>
        </div>
      </div>

      <!-- Recent Reports -->
      <div class="recent-reports">
        <h3>Recent Reports</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Report Name</th>
              <th>Type</th>
              <th>Date Range</th>
              <th>Generated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Weekly Summary - Week 10</td>
              <td>Weekly</td>
              <td>Mar 1 - Mar 7, 2026</td>
              <td>2 hours ago</td>
              <td>
                <button class="btn-sm" onclick="window.adminAnalytics.downloadReport('report1')">Download</button>
              </td>
            </tr>
            <tr>
              <td>February Monthly Report</td>
              <td>Monthly</td>
              <td>Feb 1 - Feb 28, 2026</td>
              <td>1 week ago</td>
              <td>
                <button class="btn-sm" onclick="window.adminAnalytics.downloadReport('report2')">Download</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Export Options -->
      <div class="export-options card">
        <h3>Bulk Data Export</h3>
        <p>Export raw data for external analysis</p>
        <div class="export-form">
          <div class="form-group">
            <label>Data Type</label>
            <select class="form-select" id="exportDataType">
              <option value="patients">Patient Records</option>
              <option value="hospitals">Hospital Data</option>
              <option value="response-times">Response Times</option>
              <option value="all">All Data</option>
            </select>
          </div>
          <div class="form-group">
            <label>Date Range</label>
            <div class="date-inputs">
              <input type="date" class="form-input" id="exportStartDate" />
              <span>to</span>
              <input type="date" class="form-input" id="exportEndDate" />
            </div>
          </div>
          <div class="form-group">
            <label>Format</label>
            <select class="form-select" id="exportFormat">
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
              <option value="excel">Excel (XLSX)</option>
            </select>
          </div>
          <button class="btn-primary" onclick="window.adminAnalytics.exportData()">
            📥 Export Data
          </button>
        </div>
      </div>
    </div>
  `;
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

export function mount() {
  // Set up global handlers
  window.adminAnalytics = {
    switchView: (view) => {
      currentView = view;
      destroyCharts(); // Clean up old charts
      const container = document.getElementById('app-content');
      if (container) {
        container.innerHTML = render();
        // Re-initialize charts for new view
        setTimeout(() => initializeCharts(), 100);
      }
    },
    
    setDateRange: (range) => {
      dateRange = range;
      destroyCharts();
      const container = document.getElementById('app-content');
      if (container) {
        container.innerHTML = render();
        setTimeout(() => initializeCharts(), 100);
      }
      console.log('[Analytics] Date range changed to:', range);
    },
    
    exportReport: () => {
      console.log('[Analytics] Exporting report for:', currentView, dateRange);
      alert(`Exporting ${currentView} report for ${dateRange}...`);
    },
    
    generateReport: (type, format) => {
      console.log('[Analytics] Generating report:', type, format);
      alert(`Generating ${type} report in ${format.toUpperCase()} format...`);
    },
    
    downloadReport: (reportId) => {
      console.log('[Analytics] Downloading report:', reportId);
    },
    
    openCustomReport: () => {
      console.log('[Analytics] Opening custom report builder');
      alert('Custom report builder coming soon!');
    },
    
    exportData: () => {
      const dataType = document.getElementById('exportDataType')?.value;
      const startDate = document.getElementById('exportStartDate')?.value;
      const endDate = document.getElementById('exportEndDate')?.value;
      const format = document.getElementById('exportFormat')?.value;
      
      console.log('[Analytics] Exporting data:', { dataType, startDate, endDate, format });
      alert(`Exporting ${dataType} from ${startDate} to ${endDate} as ${format.toUpperCase()}...`);
    },
    
    changeHeatmapMetric: (metric) => {
      console.log('[Analytics] Changing heatmap metric to:', metric);
    }
  };

  // Initialize charts after a short delay to ensure DOM is ready
  setTimeout(() => initializeCharts(), 100);
  
  // Start auto-refresh
  startAutoRefresh();
}

export function unmount() {
  stopAutoRefresh();
  destroyCharts();
  delete window.adminAnalytics;
}

function destroyCharts() {
  Object.values(charts).forEach(chart => {
    if (chart) chart.destroy();
  });
  charts = {};
}

function initializeCharts() {
  console.log('[Analytics] Initializing charts for view:', currentView);
  
  switch (currentView) {
    case 'overview':
      createResponseTimeChart();
      createSeverityPieChart();
      break;
    case 'response-time':
      createResponseTimeDetailChart();
      break;
    case 'utilization':
      createUtilizationChart();
      break;
    case 'severity':
      createSeverityPieChart();
      createSeverityTrendChart();
      break;
    case 'peak-hours':
      createHourlyChart();
      break;
  }
}

// Chart creation functions
function createResponseTimeChart() {
  const canvas = document.getElementById('responseTimeChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  charts.responseTime = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Response Time (minutes)',
        data: [13.2, 11.8, 12.5, 10.9, 12.1, 14.3, 13.7],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Minutes'
          }
        }
      }
    }
  });
}

function createSeverityPieChart() {
  const canvas = document.getElementById('severityChart') || document.getElementById('severityPieChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  charts.severity = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [{
        data: [23, 45, 89, 90],
        backgroundColor: [
          'rgb(220, 38, 38)',
          'rgb(234, 88, 12)',
          'rgb(217, 119, 6)',
          'rgb(22, 163, 74)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

function createResponseTimeDetailChart() {
  const canvas = document.getElementById('responseTimeDetailChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  charts.responseTimeDetail = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Triage', 'Dispatch', 'Travel', 'Handoff'],
      datasets: [{
        label: 'Average Time (minutes)',
        data: [2.5, 1.2, 7.8, 1.0],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(139, 92, 246, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Minutes'
          }
        }
      }
    }
  });
}

function createUtilizationChart() {
  const canvas = document.getElementById('utilizationChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  charts.utilization = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          label: 'Emergency',
          data: [82, 85, 88, 84, 87, 90, 85],
          borderColor: 'rgb(220, 38, 38)',
          backgroundColor: 'rgba(220, 38, 38, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'ICU',
          data: [68, 72, 70, 75, 73, 78, 72],
          borderColor: 'rgb(245, 158, 11)',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'General',
          data: [65, 68, 66, 70, 67, 72, 68],
          borderColor: 'rgb(16, 185, 129)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Utilization %'
          }
        }
      }
    }
  });
}

function createSeverityTrendChart() {
  const canvas = document.getElementById('severityTrendChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  charts.severityTrend = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          label: 'Critical',
          data: [3, 4, 2, 5, 3, 4, 2],
          borderColor: 'rgb(220, 38, 38)',
          backgroundColor: 'rgba(220, 38, 38, 0.5)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'High',
          data: [6, 7, 5, 8, 6, 7, 6],
          borderColor: 'rgb(234, 88, 12)',
          backgroundColor: 'rgba(234, 88, 12, 0.5)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Medium',
          data: [12, 14, 11, 15, 13, 14, 10],
          borderColor: 'rgb(217, 119, 6)',
          backgroundColor: 'rgba(217, 119, 6, 0.5)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Low',
          data: [15, 16, 14, 17, 15, 16, 13],
          borderColor: 'rgb(22, 163, 74)',
          backgroundColor: 'rgba(22, 163, 74, 0.5)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          stacked: true,
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Patients'
          }
        },
        x: {
          stacked: true
        }
      }
    }
  });
}

function createHourlyChart() {
  const canvas = document.getElementById('hourlyChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  
  // Generate mock data for 24 hours
  const hourlyData = [
    3, 2, 2, 1, 3, 5, 8, 12, 15, 16, 17, 18,
    18, 17, 16, 15, 14, 13, 12, 10, 8, 6, 5, 4
  ];
  
  charts.hourly = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Array.from({length: 24}, (_, i) => `${i}:00`),
      datasets: [{
        label: 'Patients per Hour',
        data: hourlyData,
        backgroundColor: hourlyData.map(val => 
          val > 15 ? 'rgba(220, 38, 38, 0.8)' :
          val > 10 ? 'rgba(245, 158, 11, 0.8)' :
          'rgba(59, 130, 246, 0.8)'
        )
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Patients'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Hour of Day'
          }
        }
      }
    }
  });
}

function startAutoRefresh() {
  // Refresh data every 30 seconds (less frequent than real-time views)
  refreshInterval = setInterval(() => {
    console.log('[Analytics] Auto-refresh');
    // TODO: Fetch latest analytics data
  }, 30000);
}

function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}
