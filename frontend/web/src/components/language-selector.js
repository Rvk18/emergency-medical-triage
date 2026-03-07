/**
 * Language Selector Component
 * Pill-style selector for 7 languages
 */

import { LANGUAGES, getCurrentLanguage, setLanguage } from '../utils/i18n.js';
import { updateLanguage } from '../utils/auth.js';
import { reRenderCurrentRoute } from '../utils/router.js';

/**
 * Render language selector
 * @param {HTMLElement} container - Container element
 */
export function renderLanguageSelector(container) {
  const currentLang = getCurrentLanguage();
  
  const html = `
    <div class="language-selector">
      <label class="form-label mb-2" style="color: var(--text-primary);">Language / भाषा</label>
      <div class="language-pills">
        ${Object.values(LANGUAGES).map(lang => `
          <button 
            class="language-pill ${lang.code === currentLang ? 'active' : ''}"
            data-lang="${lang.code}"
            aria-label="Select ${lang.name}"
          >
            ${lang.nativeName}
          </button>
        `).join('')}
      </div>
    </div>
  `;
  
  container.innerHTML = html;
  
  // Attach event listeners
  const pills = container.querySelectorAll('.language-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      const langCode = pill.getAttribute('data-lang');
      handleLanguageChange(langCode, pills);
    });
  });
}

/**
 * Handle language change
 * @param {string} langCode - Language code
 * @param {NodeList} pills - All pill elements
 */
function handleLanguageChange(langCode, pills) {
  // Update active state
  pills.forEach(p => p.classList.remove('active'));
  const selectedPill = Array.from(pills).find(p => p.getAttribute('data-lang') === langCode);
  if (selectedPill) {
    selectedPill.classList.add('active');
  }
  
  // Update language
  setLanguage(langCode);
  updateLanguage(langCode);
  
  console.log('[LanguageSelector] Language changed:', langCode);
  
  // Force immediate re-render of the entire app
  setTimeout(() => {
    console.log('[LanguageSelector] Forcing app re-render');
    
    // Store the current render function before re-rendering shell
    const container = document.getElementById('app-content');
    const currentRenderFn = container ? container._currentRenderFn : null;
    console.log('[LanguageSelector] Current render function exists:', !!currentRenderFn);
    
    // Re-render app shell
    const renderAppShell = window._renderAppShell;
    if (renderAppShell) {
      renderAppShell();
    }
    
    // Restore and call the render function
    if (currentRenderFn) {
      const newContainer = document.getElementById('app-content');
      if (newContainer) {
        newContainer._currentRenderFn = currentRenderFn;
        console.log('[LanguageSelector] Restored render function, calling it now');
        currentRenderFn(newContainer);
      }
    } else {
      console.error('[LanguageSelector] No render function to restore!');
    }
  }, 50);
}
