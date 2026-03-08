/**
 * Google Maps Utilities
 * Load and initialize Google Maps API
 */

import { getGoogleMapsApiKey } from '../services/config.js';

let isLoaded = false;
let isLoading = false;
let loadCallbacks = [];

/**
 * Load Google Maps API script
 * @returns {Promise<void>}
 */
export async function loadGoogleMaps() {
  return new Promise(async (resolve, reject) => {
    // Already loaded
    if (isLoaded && window.google && window.google.maps) {
      resolve();
      return;
    }
    
    // Currently loading
    if (isLoading) {
      loadCallbacks.push({ resolve, reject });
      return;
    }
    
    isLoading = true;
    loadCallbacks.push({ resolve, reject });
    
    try {
      // Prefer key from backend (GET /config → Secrets Manager); fallback to .env for local override
      let apiKey = await getGoogleMapsApiKey();
      if (!apiKey || apiKey === 'your_google_maps_api_key_here') {
        apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || null;
        if (apiKey) console.log('[GoogleMaps] Using API key from .env');
      } else {
        console.log('[GoogleMaps] Using API key from backend (GET /config)');
      }
      
      if (!apiKey) {
        throw new Error('Google Maps API key not available');
      }
      
      console.log('[GoogleMaps] API key retrieved, loading Maps script');
      
      // Create script element
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
      script.async = true;
      script.defer = true;
      
      script.onload = () => {
        isLoaded = true;
        isLoading = false;
        console.log('[GoogleMaps] API loaded successfully');
        
        // Resolve all pending callbacks
        loadCallbacks.forEach(cb => cb.resolve());
        loadCallbacks = [];
      };
      
      script.onerror = (error) => {
        isLoading = false;
        console.error('[GoogleMaps] Failed to load API script:', error);
        
        // Reject all pending callbacks
        const err = new Error('Failed to load Google Maps script');
        loadCallbacks.forEach(cb => cb.reject(err));
        loadCallbacks = [];
      };
      
      document.head.appendChild(script);
      
    } catch (error) {
      isLoading = false;
      console.error('[GoogleMaps] Failed to fetch API key:', error);
      
      // Reject all pending callbacks
      loadCallbacks.forEach(cb => cb.reject(error));
      loadCallbacks = [];
    }
  });
}

/**
 * Create a map instance
 * @param {HTMLElement} container - Map container element
 * @param {Object} options - Map options
 * @returns {google.maps.Map}
 */
export function createMap(container, options = {}) {
  if (!window.google || !window.google.maps) {
    throw new Error('Google Maps API not loaded');
  }
  
  const defaultOptions = {
    center: { lat: 12.9716, lng: 77.5946 }, // Bangalore
    zoom: 12,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: true,
    zoomControl: true,
  };
  
  return new google.maps.Map(container, { ...defaultOptions, ...options });
}

/**
 * Create a marker
 * @param {google.maps.Map} map - Map instance
 * @param {Object} options - Marker options
 * @returns {google.maps.Marker}
 */
export function createMarker(map, options = {}) {
  if (!window.google || !window.google.maps) {
    throw new Error('Google Maps API not loaded');
  }
  
  return new google.maps.Marker({
    map,
    ...options
  });
}

/**
 * Create a patient marker (color-coded by severity)
 * @param {google.maps.Map} map - Map instance
 * @param {Object} patient - Patient data
 * @returns {google.maps.Marker}
 */
export function createPatientMarker(map, patient) {
  const severityColors = {
    critical: '#DC2626',
    high: '#EA580C',
    medium: '#D97706',
    low: '#16A34A'
  };
  
  const color = severityColors[patient.severity] || '#3B82F6';
  
  // Create custom icon
  const icon = {
    path: google.maps.SymbolPath.CIRCLE,
    scale: 10,
    fillColor: color,
    fillOpacity: 1,
    strokeColor: '#FFFFFF',
    strokeWeight: 2
  };
  
  const marker = new google.maps.Marker({
    map,
    position: { lat: patient.current_location.lat, lng: patient.current_location.lon },
    icon,
    title: patient.patient_name || patient.id,
    animation: patient.severity === 'critical' ? google.maps.Animation.BOUNCE : null
  });
  
  // Add info window
  const infoWindow = new google.maps.InfoWindow({
    content: `
      <div style="padding: 8px;">
        <h3 style="margin: 0 0 8px 0; font-weight: 600;">${patient.patient_name || patient.id}</h3>
        <div style="margin-bottom: 4px;">
          <span style="background-color: ${color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">
            ${patient.severity.toUpperCase()}
          </span>
        </div>
        <div style="font-size: 14px; color: #666;">
          <div>→ ${patient.destination_hospital_name}</div>
          <div>ETA: ${patient.eta_minutes} min • ${patient.distance_remaining_km.toFixed(1)} km</div>
        </div>
      </div>
    `
  });
  
  marker.addListener('click', () => {
    infoWindow.open(map, marker);
  });
  
  return marker;
}

/**
 * Create a hospital marker
 * @param {google.maps.Map} map - Map instance
 * @param {Object} hospital - Hospital data
 * @returns {google.maps.Marker}
 */
export function createHospitalMarker(map, hospital) {
  const statusColors = {
    available: '#10B981',
    limited: '#F59E0B',
    full: '#EF4444',
    unavailable: '#6B7280'
  };
  
  const color = statusColors[hospital.status] || '#3B82F6';
  
  // Create custom icon (square for hospitals)
  const icon = {
    path: 'M -8,-8 L 8,-8 L 8,8 L -8,8 Z',
    fillColor: color,
    fillOpacity: 1,
    strokeColor: '#FFFFFF',
    strokeWeight: 2,
    scale: 1
  };
  
  const marker = new google.maps.Marker({
    map,
    position: { lat: hospital.location.lat, lng: hospital.location.lon },
    icon,
    title: hospital.name
  });
  
  const totalBeds = hospital.capacity.emergency.available + 
                    hospital.capacity.icu.available + 
                    hospital.capacity.general.available;
  
  // Add info window
  const infoWindow = new google.maps.InfoWindow({
    content: `
      <div style="padding: 8px;">
        <h3 style="margin: 0 0 8px 0; font-weight: 600;">${hospital.name}</h3>
        <div style="margin-bottom: 4px;">
          <span style="background-color: ${color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">
            ${hospital.status.toUpperCase()}
          </span>
        </div>
        <div style="font-size: 14px; color: #666;">
          <div>${totalBeds} beds available</div>
          <div style="margin-top: 4px;">
            <div>Emergency: ${hospital.capacity.emergency.available}/${hospital.capacity.emergency.total}</div>
            <div>ICU: ${hospital.capacity.icu.available}/${hospital.capacity.icu.total}</div>
            <div>General: ${hospital.capacity.general.available}/${hospital.capacity.general.total}</div>
          </div>
          <div style="margin-top: 4px; font-weight: 600; color: #3B82F6;">
            ${hospital.incoming_patients} incoming
          </div>
        </div>
      </div>
    `
  });
  
  marker.addListener('click', () => {
    infoWindow.open(map, marker);
  });
  
  return marker;
}

/**
 * Fit map bounds to show all markers
 * @param {google.maps.Map} map - Map instance
 * @param {google.maps.Marker[]} markers - Array of markers
 */
export function fitBoundsToMarkers(map, markers) {
  if (!markers || markers.length === 0) return;
  
  const bounds = new google.maps.LatLngBounds();
  markers.forEach(marker => {
    bounds.extend(marker.getPosition());
  });
  
  map.fitBounds(bounds);
  
  // Don't zoom in too much if there's only one marker
  if (markers.length === 1) {
    map.setZoom(14);
  }
}

/**
 * Clear all markers from map
 * @param {google.maps.Marker[]} markers - Array of markers
 */
export function clearMarkers(markers) {
  markers.forEach(marker => marker.setMap(null));
}
