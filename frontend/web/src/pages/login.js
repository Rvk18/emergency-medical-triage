/**
 * Login Page
 */

import { login } from '../utils/auth.js';
import { renderLanguageSelector } from '../components/language-selector.js';
import { t } from '../utils/i18n.js';

export function renderLogin(container) {
  container.innerHTML = `
    <div class="flex items-center justify-center min-h-[80vh]">
      <div class="card max-w-md w-full">
        <h2 class="text-2xl font-bold text-center mb-6" style="color: var(--text-primary);">${t('app_name')}</h2>
        <p class="text-center mb-8" style="color: var(--text-secondary);">Emergency Medical Triage System</p>
        
        <!-- Language Selector -->
        <div id="language-selector-container"></div>
        
        <form id="login-form" class="space-y-4">
          <div class="form-group">
            <label for="email" class="form-label">${t('email_or_phone')}</label>
            <input 
              type="text" 
              id="email" 
              name="email" 
              class="form-input"
              placeholder="${t('email_or_phone')}"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="password" class="form-label">${t('password')}</label>
            <input 
              type="password" 
              id="password" 
              name="password" 
              class="form-input"
              placeholder="${t('password')}"
              required
            />
          </div>
          
          <button type="submit" class="btn btn-primary w-full">
            ${t('login')}
          </button>
        </form>
        
        <div class="mt-6 text-center text-sm" style="color: var(--text-secondary);">
          <p>${t('demo_hint')}</p>
        </div>
      </div>
    </div>
  `;
  
  // Render language selector
  const langContainer = container.querySelector('#language-selector-container');
  renderLanguageSelector(langContainer);
  
  // Attach event listeners
  const form = container.querySelector('#login-form');
  form.addEventListener('submit', handleLogin);
  
  // Listen for language changes to update UI
  window.addEventListener('languagechange', () => {
    renderLogin(container);
  });
}

async function handleLogin(event) {
  event.preventDefault();
  
  const form = event.target;
  const email = form.email.value;
  const password = form.password.value;
  const submitBtn = form.querySelector('button[type="submit"]');
  
  // Disable button and show loading
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="loading"></span> Signing in...';
  
  try {
    await login(email, password);
    console.log('[Login] Success, redirecting to admin dashboard');
    window.location.hash = '/admin';
  } catch (error) {
    console.error('[Login] Failed:', error);
    
    // Show error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-error mt-4';
    errorDiv.textContent = error.message || 'Login failed. Please try again.';
    
    // Remove any existing error messages
    const existingError = form.querySelector('.alert-error');
    if (existingError) {
      existingError.remove();
    }
    
    form.appendChild(errorDiv);
    
    // Re-enable button
    submitBtn.disabled = false;
    submitBtn.innerHTML = t('login');
  }
}
