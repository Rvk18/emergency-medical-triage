/**
 * API Service
 * Handles all API calls to the backend
 */

import { getIdToken } from '../utils/auth.js';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev';
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === 'true' || false;

/**
 * Build headers for API requests (includes Cognito Id Token when logged in)
 * @returns {Record<string, string>}
 */
function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = getIdToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Mock triage response
 */
function getMockTriageResponse(data) {
  // Determine severity based on symptoms
  const symptoms = data.symptoms.join(' ').toLowerCase();
  let severity = 'medium';
  let confidence = 0.85;
  
  if (symptoms.includes('chest pain') || symptoms.includes('heart') || symptoms.includes('breathing')) {
    severity = 'high';
    confidence = 0.82;
  } else if (symptoms.includes('fever') || symptoms.includes('cough')) {
    severity = 'medium';
    confidence = 0.88;
  } else if (symptoms.includes('headache') || symptoms.includes('cold')) {
    severity = 'low';
    confidence = 0.90;
  }
  
  // Check vitals for critical conditions
  if (data.vitals) {
    if (data.vitals.bp > 180 || data.vitals.heart_rate > 120 || data.vitals.spo2 < 90) {
      severity = 'critical';
      confidence = 0.95;
    }
  }
  
  const recommendations = {
    critical: [
      'Call emergency services immediately (108)',
      'Do not attempt to transport patient yourself',
      'Keep patient calm and monitor vital signs',
      'Prepare medical history and current medications'
    ],
    high: [
      'Seek immediate medical attention at nearest hospital',
      'Monitor vital signs closely',
      'Keep patient comfortable and calm',
      'Prepare list of current medications'
    ],
    medium: [
      'Schedule appointment with doctor within 24 hours',
      'Monitor symptoms for any worsening',
      'Rest and stay hydrated',
      'Take over-the-counter medication if needed'
    ],
    low: [
      'Monitor symptoms over next few days',
      'Rest and maintain good hydration',
      'Consult doctor if symptoms persist or worsen',
      'Continue regular activities with caution'
    ]
  };
  
  return {
    severity,
    confidence,
    recommendations: recommendations[severity],
    force_high_priority: confidence < 0.85,
    safety_disclaimer: 'This is AI-assisted guidance based on mock data. Always seek professional medical care for accurate diagnosis and treatment.',
    session_id: data.session_id,
    id: crypto.randomUUID()
  };
}

/**
 * Perform triage assessment
 * @param {Object} data - Triage request data
 * @returns {Promise<Object>} Triage result
 */
export async function performTriage(data) {
  console.log('[API] POST /triage', data);
  
  // Use mock API if enabled or if real API fails
  if (USE_MOCK) {
    console.log('[API] Using mock API');
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay
    return getMockTriageResponse(data);
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/triage`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    
    console.log('[API] Response status:', response.status);
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.message || error.error || errorMessage;
        console.error('[API] Error response:', error);
      } catch (e) {
        const text = await response.text();
        console.error('[API] Error text:', text);
        errorMessage = text || errorMessage;
      }
      
      // Fall back to mock if API fails
      console.warn('[API] Real API failed, falling back to mock');
      await new Promise(resolve => setTimeout(resolve, 500));
      return getMockTriageResponse(data);
    }
    
    const result = await response.json();
    console.log('[API] Triage result:', result);
    
    // Validate response
    if (!result.severity || result.confidence === undefined) {
      throw new Error('Invalid response from server');
    }
    
    return result;
  } catch (error) {
    console.error('[API] Triage failed:', error);
    
    // Fall back to mock on any error
    console.warn('[API] Falling back to mock due to error');
    await new Promise(resolve => setTimeout(resolve, 500));
    return getMockTriageResponse(data);
  }
}

/**
 * Mock hospital response
 */
function getMockHospitalResponse(data) {
  const hospitals = [
    {
      name: 'City General Hospital',
      address: '123 Main Street, Medical District',
      distance_km: 2.5,
      available_beds: 12,
      specialist_available: true,
      match_score: 0.95,
      reason_key: 'hospital_reason_1'
    },
    {
      name: 'Regional Medical Center',
      address: '456 Health Avenue, Downtown',
      distance_km: 4.2,
      available_beds: 8,
      specialist_available: true,
      match_score: 0.88,
      reason_key: 'hospital_reason_2'
    },
    {
      name: 'Community Health Clinic',
      address: '789 Care Road, Suburb',
      distance_km: 6.1,
      available_beds: 5,
      specialist_available: false,
      match_score: 0.72,
      reason_key: 'hospital_reason_3'
    },
    {
      name: 'University Hospital',
      address: '321 Academic Way, University District',
      distance_km: 8.5,
      available_beds: 15,
      specialist_available: true,
      match_score: 0.85,
      reason_key: 'hospital_reason_4'
    },
    {
      name: 'St. Mary\'s Medical Center',
      address: '654 Chapel Street, Old Town',
      distance_km: 5.8,
      available_beds: 10,
      specialist_available: true,
      match_score: 0.80,
      reason_key: 'hospital_reason_5'
    }
  ];
  
  return {
    hospitals: hospitals.slice(0, data.limit || 5),
    session_id: data.session_id,
    id: crypto.randomUUID()
  };
}

/**
 * Match hospitals based on triage result
 * @param {Object} data - Hospital match request data
 * @returns {Promise<Object>} Hospital recommendations
 */
export async function matchHospitals(data) {
  console.log('[API] POST /hospitals', data);
  
  // Use mock API if enabled or if real API fails
  if (USE_MOCK) {
    console.log('[API] Using mock API for hospitals');
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay
    return getMockHospitalResponse(data);
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/hospitals`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    
    console.log('[API] Response status:', response.status);
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.message || error.error || errorMessage;
        console.error('[API] Error response:', error);
      } catch (e) {
        const text = await response.text();
        console.error('[API] Error text:', text);
        errorMessage = text || errorMessage;
      }
      
      // Fall back to mock if API fails
      console.warn('[API] Real API failed, falling back to mock');
      await new Promise(resolve => setTimeout(resolve, 500));
      return getMockHospitalResponse(data);
    }
    
    const result = await response.json();
    console.log('[API] Hospital match result:', result);
    
    // Validate response
    if (!result.hospitals || !Array.isArray(result.hospitals)) {
      throw new Error('Invalid response from server');
    }
    
    return result;
  } catch (error) {
    console.error('[API] Hospital matching failed:', error);
    
    // Fall back to mock on any error
    console.warn('[API] Falling back to mock due to error');
    await new Promise(resolve => setTimeout(resolve, 500));
    return getMockHospitalResponse(data);
  }
}

/**
 * Get hospital recommendations (legacy name, use matchHospitals instead)
 * @param {Object} data - Hospital match request data
 * @returns {Promise<Object>} Hospital recommendations
 */
export async function getHospitalRecommendations(data) {
  return matchHospitals(data);
}

/**
 * Mock route response
 */
function getMockRouteResponse(data) {
  return {
    distance_km: 5.2,
    duration_minutes: 14,
    directions_url: 'https://www.google.com/maps/dir/?api=1',
    session_id: data.session_id
  };
}

/**
 * Get driving directions (POST /route)
 * @param {Object} data - { origin: { lat, lon } | { address }, destination: { lat, lon } | { address }, session_id?: string }
 * @returns {Promise<Object>} { distance_km, duration_minutes, directions_url }
 */
export async function getRoute(data) {
  console.log('[API] POST /route', data);

  if (USE_MOCK) {
    console.log('[API] Using mock API for route');
    await new Promise(resolve => setTimeout(resolve, 800));
    return getMockRouteResponse(data);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/route`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    console.log('[API] Route response status:', response.status);

    if (!response.ok) {
      const text = await response.text();
      let errorMessage = `HTTP ${response.status}`;
      try {
        const error = JSON.parse(text);
        errorMessage = error.message || error.error || errorMessage;
      } catch (_) {
        errorMessage = text || errorMessage;
      }
      console.warn('[API] Real route API failed, falling back to mock');
      await new Promise(resolve => setTimeout(resolve, 300));
      return getMockRouteResponse(data);
    }

    const result = await response.json();
    if (result.directions_url === undefined && result.distance_km === undefined) {
      throw new Error('Invalid route response');
    }
    return result;
  } catch (error) {
    console.error('[API] Route failed:', error);
    console.warn('[API] Falling back to mock');
    await new Promise(resolve => setTimeout(resolve, 300));
    return getMockRouteResponse(data);
  }
}

/**
 * Health check
 * @returns {Promise<Object>} Health status
 */
export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  } catch (error) {
    console.error('[API] Health check failed:', error);
    throw error;
  }
}
