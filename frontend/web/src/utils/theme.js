/**
 * Theme Management - Light/Dark Mode Toggle
 * Persists preference in localStorage
 */

const THEME_KEY = 'medtriage_theme';

/**
 * Initialize theme on page load
 */
export function initTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  const theme = savedTheme || (prefersDark ? 'dark' : 'light');
  setTheme(theme);
  
  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(THEME_KEY)) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });
}

/**
 * Set theme (light or dark)
 * @param {string} theme - 'light' or 'dark'
 */
export function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
  console.log(`[Theme] Set data-theme="${theme}" on <html>`);
  console.log(`[Theme] Current attribute:`, document.documentElement.getAttribute('data-theme'));
}

/**
 * Get current theme
 * @returns {string} Current theme ('light' or 'dark')
 */
export function getTheme() {
  return document.documentElement.getAttribute('data-theme') || 'light';
}

/**
 * Toggle between light and dark theme
 */
export function toggleTheme() {
  const current = getTheme();
  const next = current === 'light' ? 'dark' : 'light';
  console.log(`[Theme] Toggling from ${current} to ${next}`);
  setTheme(next);
  
  // Update icon
  updateThemeIcon(next);
}

/**
 * Update theme toggle icon
 */
function updateThemeIcon(theme) {
  const button = document.getElementById('theme-toggle');
  if (!button) return;
  
  const icon = theme === 'dark' 
    ? `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>`
    : `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>`;
  
  button.innerHTML = icon;
}
