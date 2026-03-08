/**
 * Config Service
 * Fetches frontend configuration from backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev';

let configCache = null;

/**
 * Fetch frontend configuration from backend
 * @returns {Promise<Object>} Configuration object
 */
export async function fetchConfig() {
  // Return cached config if available
  if (configCache) {
    return configCache;
  }
  
  try {
    console.log('[Config] Fetching configuration from backend');
    
    const response = await fetch(`${API_BASE_URL}/config`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const config = await response.json();
    
    // Cache the config
    configCache = config;
    
    console.log('[Config] Configuration loaded successfully');
    return config;
    
  } catch (error) {
    console.error('[Config] Failed to fetch configuration:', error);
    
    // Return fallback config
    return {
      google_maps_api_key: null,
      environment: 'dev'
    };
  }
}

/**
 * Get Google Maps API key
 * @returns {Promise<string|null>} API key or null
 */
export async function getGoogleMapsApiKey() {
  const config = await fetchConfig();
  return config.google_maps_api_key || null;
}

/**
 * Clear config cache (useful for testing)
 */
export function clearConfigCache() {
  configCache = null;
}
