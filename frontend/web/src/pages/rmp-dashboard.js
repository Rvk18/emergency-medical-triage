/**
 * RMP Dashboard Page
 * Phase 5 implementation
 */

import { t, getCurrentLanguage } from '../utils/i18n.js';
import { getCurrentUser } from '../utils/auth.js';
import { getAllPatients, formatTimestamp, getPatientDisplayName } from '../utils/patient-history.js';

export function renderDashboard(container) {
  console.log('[Dashboard] Rendering with language:', getCurrentLanguage());
  
  const user = getCurrentUser();
  const patients = getAllPatients();
  
  // Calculate stats
  const totalCases = patients.length;
  const criticalCases = patients.filter(p => p.triageResult.severity === 'critical').length;
  const highCases = patients.filter(p => p.triageResult.severity === 'high').length;
  const avgConfidence = patients.length > 0 
    ? Math.round(patients.reduce((sum, p) => sum + p.triageResult.confidence, 0) / patients.length * 100)
    : 0;
  
  // Mock competency data
  const competencyScore = 85;
  const successRate = 94;
  const level = 'Advanced';
  
  container.innerHTML = `
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2" style="color: var(--text-primary);">${t('dashboard')}</h1>
        <p style="color: var(--text-secondary);">${t('welcome_back')}, ${user.name}</p>
      </div>
      
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-semibold" style="color: var(--text-secondary);">${t('total_cases')}</h3>
            <svg class="w-5 h-5" style="color: var(--primary-600);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p class="text-3xl font-bold" style="color: var(--text-primary);">${totalCases}</p>
        </div>
        
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-semibold" style="color: var(--text-secondary);">${t('competency_score')}</h3>
            <svg class="w-5 h-5" style="color: var(--primary-600);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          </div>
          <p class="text-3xl font-bold" style="color: var(--primary-600);">${competencyScore}%</p>
          <p class="text-xs mt-1" style="color: var(--text-secondary);">${t('level')}: ${level}</p>
        </div>
        
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-semibold" style="color: var(--text-secondary);">${t('avg_confidence')}</h3>
            <svg class="w-5 h-5" style="color: var(--success);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <p class="text-3xl font-bold" style="color: var(--success);">${avgConfidence}%</p>
        </div>
        
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-semibold" style="color: var(--text-secondary);">${t('critical_high')}</h3>
            <svg class="w-5 h-5" style="color: var(--error);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p class="text-3xl font-bold" style="color: var(--error);">${criticalCases + highCases}</p>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="card mb-6">
        <h2 class="text-xl font-semibold mb-4" style="color: var(--text-primary);">${t('quick_actions')}</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a href="#/triage" class="btn btn-primary flex items-center justify-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            ${t('new_assessment')}
          </a>
          <a href="#/hospitals" class="btn btn-secondary flex items-center justify-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            ${t('find_hospitals')}
          </a>
          <button class="btn btn-secondary flex items-center justify-center" onclick="alert('${t('learning_coming_soon')}')">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            ${t('learning_modules')}
          </button>
        </div>
      </div>
      
      <!-- Recent Cases -->
      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold" style="color: var(--text-primary);">${t('recent_cases')}</h2>
          ${patients.length > 5 ? `<a href="#/hospitals" class="text-sm" style="color: var(--primary-600);">${t('view_all')}</a>` : ''}
        </div>
        
        ${patients.length === 0 ? `
          <div class="text-center py-8">
            <svg class="w-16 h-16 mx-auto mb-4" style="color: var(--text-secondary);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p style="color: var(--text-secondary);">${t('no_cases_yet')}</p>
            <a href="#/triage" class="btn btn-primary mt-4">${t('start_first_assessment')}</a>
          </div>
        ` : `
          <div class="space-y-3">
            ${patients.slice(0, 5).map(patient => renderCaseCard(patient)).join('')}
          </div>
        `}
      </div>
    </div>
  `;
}

function renderCaseCard(patient) {
  const displayName = getPatientDisplayName(patient.patientInfo);
  const timeAgo = formatTimestamp(patient.timestamp);
  const severity = patient.triageResult.severity;
  const confidence = Math.round(patient.triageResult.confidence * 100);
  
  return `
    <div class="p-4 rounded-md border transition-colors hover:bg-gray-50" style="border-color: var(--border-color);">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-1">
            <span class="font-semibold" style="color: var(--text-primary);">${displayName}</span>
            <span class="badge badge-${severity.toLowerCase()}">${severity.toUpperCase()}</span>
          </div>
          <p class="text-sm" style="color: var(--text-secondary);">
            ${t('confidence')}: ${confidence}% • ${timeAgo}
          </p>
        </div>
        <a href="#/hospitals" class="btn btn-secondary btn-sm">
          ${t('view_details')}
        </a>
      </div>
    </div>
  `;
}
