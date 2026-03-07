/**
 * Admin API Service
 * Handles admin-specific API calls for monitoring and routing
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev';
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === 'true' || true; // Default to mock for now

/**
 * Get auth token from session storage
 */
function getAuthToken() {
  const token = sessionStorage.getItem('idToken');
  return token;
}

/**
 * Mock active patients data
 */
function getMockActivePatients() {
  return {
    patients: [
      {
        id: "patient-001",
        session_id: "session-001",
        patient_name: "Patient A",
        severity: "critical",
        current_location: { lat: 12.9716, lon: 77.5946 },
        destination_hospital_id: "hosp-001",
        destination_hospital_name: "Apollo Hospital",
        eta_minutes: 12,
        distance_remaining_km: 8.5,
        status: "en_route",
        triage_summary: {
          symptoms: ["chest pain", "shortness of breath"],
          vitals: { bp: 180, heart_rate: 120, spo2: 88 }
        },
        last_updated: new Date().toISOString()
      },
      {
        id: "patient-002",
        session_id: "session-002",
        patient_name: "Patient B",
        severity: "high",
        current_location: { lat: 12.9352, lon: 77.6245 },
        destination_hospital_id: "hosp-002",
        destination_hospital_name: "Manipal Hospital",
        eta_minutes: 8,
        distance_remaining_km: 5.2,
        status: "en_route",
        triage_summary: {
          symptoms: ["severe headache", "vomiting"],
          vitals: { bp: 160, heart_rate: 95, temp_c: 39.5 }
        },
        last_updated: new Date().toISOString()
      },
      {
        id: "patient-003",
        session_id: "session-003",
        patient_name: "Patient C",
        severity: "medium",
        current_location: { lat: 12.9141, lon: 77.6411 },
        destination_hospital_id: "hosp-003",
        destination_hospital_name: "Fortis Hospital",
        eta_minutes: 15,
        distance_remaining_km: 10.3,
        status: "en_route",
        triage_summary: {
          symptoms: ["fever", "cough"],
          vitals: { temp_c: 38.5, spo2: 95 }
        },
        last_updated: new Date().toISOString()
      }
    ]
  };
}

/**
 * Mock hospital status data
 */
function getMockHospitalStatus() {
  return {
    hospitals: [
      {
        id: "hosp-001",
        name: "Apollo Hospital",
        location: { lat: 12.9698, lon: 77.7499 },
        capacity: {
          emergency: { available: 5, total: 10 },
          icu: { available: 2, total: 8 },
          general: { available: 12, total: 50 }
        },
        incoming_patients: 2,
        status: "available"
      },
      {
        id: "hosp-002",
        name: "Manipal Hospital",
        location: { lat: 12.9899, lon: 77.7066 },
        capacity: {
          emergency: { available: 1, total: 8 },
          icu: { available: 0, total: 6 },
          general: { available: 5, total: 40 }
        },
        incoming_patients: 1,
        status: "limited"
      },
      {
        id: "hosp-003",
        name: "Fortis Hospital",
        location: { lat: 12.9116, lon: 77.6493 },
        capacity: {
          emergency: { available: 0, total: 6 },
          icu: { available: 0, total: 4 },
          general: { available: 0, total: 30 }
        },
        incoming_patients: 0,
        status: "full"
      },
      {
        id: "hosp-004",
        name: "Columbia Asia Hospital",
        location: { lat: 12.9279, lon: 77.6271 },
        capacity: {
          emergency: { available: 8, total: 12 },
          icu: { available: 4, total: 10 },
          general: { available: 20, total: 60 }
        },
        incoming_patients: 0,
        status: "available"
      }
    ]
  };
}

/**
 * Get all active patients
 * @returns {Promise<Object>} Active patients data
 */
export async function getActivePatients() {
  console.log('[AdminAPI] GET /admin/patients/active');
  
  if (USE_MOCK) {
    console.log('[AdminAPI] Using mock data');
    await new Promise(resolve => setTimeout(resolve, 500));
    return getMockActivePatients();
  }
  
  try {
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/admin/patients/active`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[AdminAPI] Failed to fetch active patients:', error);
    // Fallback to mock
    return getMockActivePatients();
  }
}

/**
 * Get hospital status
 * @returns {Promise<Object>} Hospital status data
 */
export async function getHospitalStatus() {
  console.log('[AdminAPI] GET /admin/hospitals/status');
  
  if (USE_MOCK) {
    console.log('[AdminAPI] Using mock data');
    await new Promise(resolve => setTimeout(resolve, 500));
    return getMockHospitalStatus();
  }
  
  try {
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/admin/hospitals/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[AdminAPI] Failed to fetch hospital status:', error);
    // Fallback to mock
    return getMockHospitalStatus();
  }
}

/**
 * Get patient details
 * @param {string} patientId - Patient ID
 * @returns {Promise<Object>} Patient details
 */
export async function getPatientDetails(patientId) {
  console.log('[AdminAPI] GET /admin/patients/' + patientId);
  
  if (USE_MOCK) {
    const mockData = getMockActivePatients();
    const patient = mockData.patients.find(p => p.id === patientId);
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      patient: patient || null,
      route: {
        distance_km: patient?.distance_remaining_km || 0,
        duration_minutes: patient?.eta_minutes || 0,
        directions_url: `https://maps.google.com/`
      },
      history: [
        { timestamp: new Date().toISOString(), action: "Triage completed", user: "RMP-001" },
        { timestamp: new Date().toISOString(), action: "Hospital assigned", user: "System" }
      ]
    };
  }
  
  try {
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/admin/patients/${patientId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[AdminAPI] Failed to fetch patient details:', error);
    throw error;
  }
}

/**
 * Re-route patient to new hospital
 * @param {string} patientId - Patient ID
 * @param {string} newHospitalId - New hospital ID
 * @param {string} reason - Reason for re-routing
 * @returns {Promise<Object>} Re-route result
 */
export async function reroutePatient(patientId, newHospitalId, reason) {
  console.log('[AdminAPI] POST /admin/patients/' + patientId + '/reroute');
  
  if (USE_MOCK) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      success: true,
      new_route: {
        distance_km: 6.5,
        duration_minutes: 10,
        directions_url: `https://maps.google.com/`
      },
      notification_sent: true
    };
  }
  
  try {
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/admin/patients/${patientId}/reroute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        new_hospital_id: newHospitalId,
        reason: reason
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[AdminAPI] Failed to re-route patient:', error);
    throw error;
  }
}
