/**
 * Hash-based SPA Router
 * Simple router without dependencies
 */

import { isAuthenticated } from './auth.js';

const routes = {};
let currentRoute = null;

// Routes that don't require authentication
const PUBLIC_ROUTES = ['/', '/login'];

/**
 * Register a route
 * @param {string} path - Route path (e.g., '/', '/triage')
 * @param {Function} handler - Async function that returns render function
 */
export function registerRoute(path, handler) {
  routes[path] = handler;
}

/**
 * Initialize router
 */
export function initRouter() {
  // Register default routes
  registerRoute('/', () => import('../pages/login.js').then(m => m.renderLogin));
  registerRoute('/admin', () => import('../pages/admin-dashboard.js').then(m => m.renderAdminDashboard));
  registerRoute('/admin/patients', () => import('../pages/admin-patients.js').then(m => m.renderAdminPatients));
  registerRoute('/admin/hospitals', () => import('../pages/admin-hospitals.js').then(m => m.renderAdminHospitals));
  registerRoute('/admin/healthcare-workers', () => import('../pages/admin-healthcare-workers.js').then(m => m.renderAdminHealthcareWorkers));
  registerRoute('/admin/communications', () => import('../pages/admin-communications.js').then(m => m.renderAdminCommunications));
  registerRoute('/admin/analytics', () => import('../pages/admin-analytics.js').then(m => m.renderAdminAnalytics));
  
  // Listen for hash changes
  window.addEventListener('hashchange', handleRoute);
  
  // Handle initial route
  handleRoute();
}

/**
 * Handle route change
 */
async function handleRoute() {
  const hash = window.location.hash.slice(1) || '/';
  
  // Check authentication
  if (!PUBLIC_ROUTES.includes(hash) && !isAuthenticated()) {
    console.log('[Router] Redirecting to login - not authenticated');
    window.location.hash = '/';
    return;
  }
  
  // If authenticated and on login page, redirect to admin dashboard
  if (hash === '/' && isAuthenticated()) {
    console.log('[Router] Already authenticated, redirecting to admin dashboard');
    window.location.hash = '/admin';
    return;
  }
  
  const routeHandler = routes[hash];
  
  if (!routeHandler) {
    console.error('[Router] Route not found:', hash);
    window.location.hash = '/';
    return;
  }
  
  const container = document.getElementById('app-content');
  if (!container) {
    console.error('[Router] Container #app-content not found');
    return;
  }
  
  // Show loading
  container.innerHTML = '<div class="flex items-center justify-center min-h-screen"><div class="loading"></div></div>';
  
  try {
    const renderFn = await routeHandler();
    currentRoute = hash;
    
    // Store render function for language changes
    container._currentRenderFn = renderFn;
    console.log('[Router] Stored render function on container for route:', hash);
    
    renderFn(container);
  } catch (error) {
    console.error('[Router] Route loading failed:', error);
    container.innerHTML = `
      <div class="flex items-center justify-center min-h-screen">
        <div class="text-center">
          <p class="text-error text-lg font-semibold mb-2">Page failed to load</p>
          <p style="color: var(--text-secondary);">${error.message}</p>
          <button onclick="window.location.reload()" class="btn btn-primary mt-4">Reload</button>
        </div>
      </div>
    `;
  }
}

/**
 * Re-render current route (used for language changes)
 */
export function reRenderCurrentRoute() {
  const container = document.getElementById('app-content');
  if (container && container._currentRenderFn) {
    console.log('[Router] Re-rendering current route');
    container._currentRenderFn(container);
  } else {
    console.warn('[Router] Cannot re-render - no render function stored');
  }
}

/**
 * Navigate to a route
 * @param {string} path - Route path
 */
export function navigateTo(path) {
  window.location.hash = path;
}

/**
 * Get current route
 * @returns {string} Current route path
 */
export function getCurrentRoute() {
  return currentRoute;
}
