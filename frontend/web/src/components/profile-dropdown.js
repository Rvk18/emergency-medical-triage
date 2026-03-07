/**
 * Profile Dropdown Component
 * Shows user info, language selector, and logout
 */

import { getCurrentUser, logout } from '../utils/auth.js';
import { renderLanguageSelector } from './language-selector.js';
import { t } from '../utils/i18n.js';

let isOpen = false;

/**
 * Render profile dropdown button
 * @param {HTMLElement} container - Container element
 */
export function renderProfileDropdown(container) {
  const user = getCurrentUser();
  if (!user) return;
  
  const html = `
    <div class="profile-dropdown-container">
      <button 
        id="profile-btn" 
        class="profile-btn"
        aria-label="Profile menu"
      >
        <div class="profile-avatar">
          ${user.name.charAt(0).toUpperCase()}
        </div>
        <span class="profile-name">${user.name}</span>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      <div id="profile-dropdown" class="profile-dropdown hidden">
        <div class="profile-dropdown-header">
          <div class="profile-avatar-large">
            ${user.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <p class="font-semibold" style="color: var(--text-primary);">${user.name}</p>
            <p class="text-sm" style="color: var(--text-secondary);">${user.email}</p>
            <p class="text-xs mt-1" style="color: var(--text-secondary);">
              ${user.role.replace('_', ' ').toUpperCase()}
            </p>
          </div>
        </div>
        
        <div class="profile-dropdown-divider"></div>
        
        <div class="profile-dropdown-section">
          <div id="profile-language-selector"></div>
        </div>
        
        <div class="profile-dropdown-divider"></div>
        
        <button id="profile-logout-btn" class="profile-dropdown-item">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          ${t('logout')}
        </button>
      </div>
    </div>
  `;
  
  container.innerHTML = html;
  
  // Render language selector inside dropdown
  const langContainer = container.querySelector('#profile-language-selector');
  renderLanguageSelector(langContainer);
  
  // Attach event listeners
  const profileBtn = container.querySelector('#profile-btn');
  const dropdown = container.querySelector('#profile-dropdown');
  const logoutBtn = container.querySelector('#profile-logout-btn');
  
  profileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleDropdown(dropdown);
  });
  
  logoutBtn.addEventListener('click', handleLogout);
  
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!container.contains(e.target)) {
      closeDropdown(dropdown);
    }
  });
}

/**
 * Toggle dropdown visibility
 */
function toggleDropdown(dropdown) {
  isOpen = !isOpen;
  if (isOpen) {
    dropdown.classList.remove('hidden');
  } else {
    dropdown.classList.add('hidden');
  }
}

/**
 * Close dropdown
 */
function closeDropdown(dropdown) {
  isOpen = false;
  dropdown.classList.add('hidden');
}

/**
 * Handle logout
 */
function handleLogout() {
  logout();
  window.location.hash = '/';
  window.location.reload();
}
