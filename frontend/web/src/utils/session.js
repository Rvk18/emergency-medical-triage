/**
 * Session Management
 * Handles session_id for AgentCore memory continuity
 */

const SESSION_KEY = 'session_id';
const TRIAGE_RESULT_KEY = 'triage_result';
const SELECTED_HOSPITAL_KEY = 'selected_hospital';

/**
 * Initialize session - generate UUID if not exists
 * @returns {string} Session ID
 */
export function initSession() {
  let sessionId = sessionStorage.getItem(SESSION_KEY);
  
  // AgentCore requires session_id >= 33 chars
  if (!sessionId || sessionId.length < 33) {
    sessionId = crypto.randomUUID(); // 36 chars
    sessionStorage.setItem(SESSION_KEY, sessionId);
  }
  
  return sessionId;
}

/**
 * Get current session ID
 * @returns {string|null} Session ID or null
 */
export function getSessionId() {
  return sessionStorage.getItem(SESSION_KEY);
}

/**
 * Clear session data
 */
export function clearSession() {
  sessionStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(TRIAGE_RESULT_KEY);
  sessionStorage.removeItem(SELECTED_HOSPITAL_KEY);
}

/**
 * Save triage result to session
 * @param {Object} result - Triage result
 */
export function saveTriageResult(result) {
  sessionStorage.setItem(TRIAGE_RESULT_KEY, JSON.stringify(result));
}

/**
 * Get triage result from session
 * @returns {Object|null} Triage result or null
 */
export function getTriageResult() {
  const data = sessionStorage.getItem(TRIAGE_RESULT_KEY);
  return data ? JSON.parse(data) : null;
}

/**
 * Save selected hospital to session
 * @param {Object} hospital - Hospital data
 */
export function saveSelectedHospital(hospital) {
  sessionStorage.setItem(SELECTED_HOSPITAL_KEY, JSON.stringify(hospital));
}

/**
 * Get selected hospital from session
 * @returns {Object|null} Hospital data or null
 */
export function getSelectedHospital() {
  const data = sessionStorage.getItem(SELECTED_HOSPITAL_KEY);
  return data ? JSON.parse(data) : null;
}
