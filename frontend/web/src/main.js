/**
 * Main Entry Point - Emergency Medical Triage Web App
 */

import './style.css';
import { initTheme, toggleTheme } from './utils/theme.js';
import { initRouter } from './utils/router.js';
import { initSession } from './utils/session.js';
import { getCurrentUser } from './utils/auth.js';
import { t } from './utils/i18n.js';
import { renderProfileDropdown } from './components/profile-dropdown.js';

/**
 * Initialize application
 */
function initApp() {
  // Initialize theme
  initTheme();
  
  // Initialize session
  initSession();
  
  // Render app shell
  renderAppShell();
  
  // Initialize router
  initRouter();
  
  // Setup offline detection
  setupOfflineDetection();
  
  // Listen for language changes globally
  window.addEventListener('languagechange', (e) => {
    console.log('[App] Language changed event received, detail:', e.detail);
    
    // Re-render app shell (header, nav)
    renderAppShell();
    
    // Force re-render current page
    const container = document.getElementById('app-content');
    if (container && container._currentRenderFn) {
      console.log('[App] Re-rendering current page with stored function');
      container._currentRenderFn(container);
    } else {
      console.warn('[App] No render function stored on container');
    }
  });
  
  console.log('[App] Initialized successfully');
}

/**
 * Render app shell (sidebar, topbar, content area)
 */
function renderAppShell() {
  const appShell = document.getElementById('app-shell');
  const user = getCurrentUser();
  
  // Check if we're doing a full render or just updating
  const existingContent = document.getElementById('app-content');
  const preserveContent = existingContent && existingContent._currentRenderFn;
  
  if (preserveContent) {
    console.log('[App] Updating app shell while preserving content');
    // Just update header and nav, preserve content
    const header = appShell.querySelector('header');
    const nav = appShell.querySelector('nav');
    
    if (header) {
      header.innerHTML = `
        <div class="container mx-auto px-4 py-3 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <h1 class="text-xl font-bold text-primary-600">${t('app_name')}</h1>
          </div>
          
          <div class="flex items-center gap-4">
            <button 
              id="theme-toggle" 
              class="p-2 rounded-md transition-colors"
              style="color: var(--text-primary);"
              aria-label="Toggle theme"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            </button>
            ${user ? '<div id="profile-dropdown-container"></div>' : ''}
          </div>
        </div>
      `;
    }
    
    if (nav && user) {
      nav.innerHTML = `
        <div class="container mx-auto px-4">
          <div class="flex gap-2 py-2">
            <a href="#/admin" class="nav-link">📊 Dashboard</a>
            <a href="#/admin/patients" class="nav-link">🚑 Patients</a>
            <a href="#/admin/hospitals" class="nav-link">🏥 Hospitals</a>
            <a href="#/admin/healthcare-workers" class="nav-link">👨‍⚕️ Healthcare Workers</a>
            <a href="#/admin/communications" class="nav-link">💬 Communications</a>
            <a href="#/admin/analytics" class="nav-link">📈 Analytics</a>
          </div>
        </div>
      `;
    }
  } else {
    console.log('[App] Full app shell render');
    // Full render
    appShell.innerHTML = `
      <div class="min-h-screen" style="background-color: var(--bg-secondary);">
        <!-- Top Bar -->
        <header class="sticky top-0 z-50" style="background-color: var(--bg-primary); border-bottom: 1px solid var(--border-color);">
          <div class="container mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-4">
              <h1 class="text-xl font-bold text-primary-600">${t('app_name')}</h1>
            </div>
            
            <div class="flex items-center gap-4">
              <button 
                id="theme-toggle" 
                class="p-2 rounded-md transition-colors"
                style="color: var(--text-primary);"
                aria-label="Toggle theme"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              </button>
              ${user ? '<div id="profile-dropdown-container"></div>' : ''}
            </div>
          </div>
        </header>
        
        <!-- Navigation -->
        ${user ? `
          <nav style="background-color: var(--bg-primary); border-bottom: 1px solid var(--border-color);">
            <div class="container mx-auto px-4">
              <div class="flex gap-2 py-2">
                <a href="#/admin" class="nav-link">📊 Dashboard</a>
                <a href="#/admin/patients" class="nav-link">🚑 Patients</a>
                <a href="#/admin/hospitals" class="nav-link">🏥 Hospitals</a>
                <a href="#/admin/healthcare-workers" class="nav-link">👨‍⚕️ Healthcare Workers</a>
                <a href="#/admin/communications" class="nav-link">💬 Communications</a>
                <a href="#/admin/analytics" class="nav-link">📈 Analytics</a>
              </div>
            </div>
          </nav>
        ` : ''}
        
        <!-- Main Content -->
        <main id="app-content" class="container mx-auto px-4 py-6">
          <!-- Content will be rendered here by router -->
        </main>
      </div>
    `;
  }
  
  // Attach event listeners
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      console.log('[Theme] Toggle clicked');
      toggleTheme();
    });
    console.log('[Theme] Toggle button attached');
  } else {
    console.error('[Theme] Toggle button not found');
  }
  
  // Render profile dropdown
  if (user) {
    const profileContainer = document.getElementById('profile-dropdown-container');
    if (profileContainer) {
      renderProfileDropdown(profileContainer);
    }
  }
  
  // Update active nav link
  updateActiveNavLink();
  window.addEventListener('hashchange', updateActiveNavLink);
}

// Expose globally for language selector
window._renderAppShell = renderAppShell;

/**
 * Update active navigation link
 */
function updateActiveNavLink() {
  const hash = window.location.hash || '#/';
  const links = document.querySelectorAll('.nav-link');
  
  links.forEach(link => {
    if (link.getAttribute('href') === hash) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

/**
 * Setup offline detection
 */
function setupOfflineDetection() {
  const banner = document.getElementById('offline-banner');
  
  function updateOnlineStatus() {
    if (!navigator.onLine) {
      banner.className = 'offline-banner';
      banner.textContent = 'OFFLINE MODE — LIMITED FUNCTIONALITY';
    } else {
      banner.className = 'hidden';
    }
  }
  
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  
  updateOnlineStatus();
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
