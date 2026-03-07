/**
 * Patient History Management
 * Stores and manages multiple patient triage assessments
 */

const HISTORY_KEY = 'patient_history';
const CURRENT_PATIENT_KEY = 'current_patient_id';

/**
 * Patient assessment structure
 * @typedef {Object} PatientAssessment
 * @property {string} id - Unique assessment ID
 * @property {string} sessionId - Session ID for API continuity
 * @property {Object} patientInfo - Patient information
 * @property {Object} triageResult - Triage assessment result
 * @property {number} timestamp - Assessment timestamp
 * @property {Object} [hospitalMatch] - Hospital matching result (optional)
 */

/**
 * Get all patient assessments
 * @returns {PatientAssessment[]} Array of patient assessments
 */
export function getAllPatients() {
  try {
    const history = localStorage.getItem(HISTORY_KEY);
    return history ? JSON.parse(history) : [];
  } catch (error) {
    console.error('[PatientHistory] Failed to load history:', error);
    return [];
  }
}

/**
 * Get current patient ID
 * @returns {string|null} Current patient ID
 */
export function getCurrentPatientId() {
  return sessionStorage.getItem(CURRENT_PATIENT_KEY);
}

/**
 * Set current patient ID
 * @param {string} patientId - Patient ID to set as current
 */
export function setCurrentPatientId(patientId) {
  sessionStorage.setItem(CURRENT_PATIENT_KEY, patientId);
  console.log('[PatientHistory] Current patient set:', patientId);
}

/**
 * Get current patient assessment
 * @returns {PatientAssessment|null} Current patient assessment
 */
export function getCurrentPatient() {
  const currentId = getCurrentPatientId();
  if (!currentId) return null;
  
  const patients = getAllPatients();
  return patients.find(p => p.id === currentId) || null;
}

/**
 * Save patient assessment
 * @param {Object} patientInfo - Patient information
 * @param {Object} triageResult - Triage result
 * @param {string} sessionId - Session ID
 * @returns {string} Assessment ID
 */
export function savePatientAssessment(patientInfo, triageResult, sessionId) {
  const patients = getAllPatients();
  
  // Create new assessment
  const assessment = {
    id: crypto.randomUUID(),
    sessionId: sessionId,
    patientInfo: patientInfo,
    triageResult: triageResult,
    timestamp: Date.now(),
  };
  
  // Add to history (keep last 50 assessments)
  patients.unshift(assessment);
  if (patients.length > 50) {
    patients.splice(50);
  }
  
  // Save to localStorage
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(patients));
    setCurrentPatientId(assessment.id);
    console.log('[PatientHistory] Saved assessment:', assessment.id);
    return assessment.id;
  } catch (error) {
    console.error('[PatientHistory] Failed to save assessment:', error);
    throw error;
  }
}

/**
 * Update patient assessment with hospital match
 * @param {string} patientId - Patient ID
 * @param {Object} hospitalMatch - Hospital matching result
 */
export function updatePatientHospitalMatch(patientId, hospitalMatch) {
  const patients = getAllPatients();
  const patient = patients.find(p => p.id === patientId);
  
  if (patient) {
    patient.hospitalMatch = hospitalMatch;
    patient.updatedAt = Date.now();
    
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(patients));
      console.log('[PatientHistory] Updated hospital match for:', patientId);
    } catch (error) {
      console.error('[PatientHistory] Failed to update hospital match:', error);
    }
  }
}

/**
 * Delete patient assessment
 * @param {string} patientId - Patient ID to delete
 */
export function deletePatientAssessment(patientId) {
  const patients = getAllPatients();
  const filtered = patients.filter(p => p.id !== patientId);
  
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered));
    
    // If deleted patient was current, clear current
    if (getCurrentPatientId() === patientId) {
      sessionStorage.removeItem(CURRENT_PATIENT_KEY);
    }
    
    console.log('[PatientHistory] Deleted assessment:', patientId);
  } catch (error) {
    console.error('[PatientHistory] Failed to delete assessment:', error);
  }
}

/**
 * Clear all patient history
 */
export function clearAllPatients() {
  try {
    localStorage.removeItem(HISTORY_KEY);
    sessionStorage.removeItem(CURRENT_PATIENT_KEY);
    console.log('[PatientHistory] Cleared all history');
  } catch (error) {
    console.error('[PatientHistory] Failed to clear history:', error);
  }
}

/**
 * Get patient display name
 * @param {Object} patientInfo - Patient information
 * @returns {string} Display name
 */
export function getPatientDisplayName(patientInfo) {
  if (patientInfo.patient_id) {
    return patientInfo.patient_id;
  }
  
  const parts = [];
  if (patientInfo.age) parts.push(`${patientInfo.age}y`);
  if (patientInfo.sex) parts.push(patientInfo.sex);
  
  return parts.length > 0 ? parts.join(', ') : 'Unknown';
}

/**
 * Format timestamp
 * @param {number} timestamp - Timestamp in milliseconds
 * @returns {string} Formatted time
 */
export function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
}
