/**
 * Authentication & Authorization with AWS Cognito
 */

import { Amplify } from 'aws-amplify';
import { signIn as amplifySignIn, signOut as amplifySignOut, getCurrentUser as amplifyGetCurrentUser, fetchAuthSession } from 'aws-amplify/auth';
import { getCurrentLanguage } from './i18n.js';

const AUTH_KEY = 'medtriage_auth';

// Configure Amplify with Cognito
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
      userPoolClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
      loginWith: {
        email: true,
      },
    },
  },
});

/**
 * User roles
 */
export const ROLES = {
  RMP: 'rmp',
  HEALTHCARE_WORKER: 'healthcare_worker',
  HOSPITAL_STAFF: 'hospital_staff',
  ADMIN: 'admin',
};

/**
 * Login with Cognito
 * @param {string} email - Email
 * @param {string} password - Password
 * @returns {Promise<Object>} User object
 */
export async function login(email, password) {
  try {
    console.log('[Auth] Attempting Cognito sign-in for:', email);
    
    // Sign in with Cognito
    const { isSignedIn, nextStep } = await amplifySignIn({
      username: email,
      password: password,
    });
    
    if (!isSignedIn) {
      console.warn('[Auth] Sign-in incomplete, next step:', nextStep);
      throw new Error('Sign-in incomplete. Please complete the required steps.');
    }
    
    // Get user details and tokens
    const cognitoUser = await amplifyGetCurrentUser();
    const session = await fetchAuthSession();
    
    // Extract tokens
    const idToken = session.tokens?.idToken?.toString();
    const accessToken = session.tokens?.accessToken?.toString();
    
    if (!idToken) {
      throw new Error('Failed to get ID token');
    }
    
    // Store tokens in session storage for API calls
    sessionStorage.setItem('idToken', idToken);
    sessionStorage.setItem('accessToken', accessToken);
    
    // Create user object
    const user = {
      id: cognitoUser.userId,
      email: email,
      username: cognitoUser.username,
      name: email.split('@')[0] || 'User',
      role: ROLES.ADMIN, // Default to admin for now
      language: getCurrentLanguage(),
      cognitoSub: cognitoUser.userId,
    };
    
    // Store user in localStorage
    localStorage.setItem(AUTH_KEY, JSON.stringify(user));
    
    console.log('[Auth] Cognito login successful:', user);
    return user;
    
  } catch (error) {
    console.error('[Auth] Cognito login failed:', error);
    
    // Provide user-friendly error messages
    if (error.name === 'UserNotFoundException') {
      throw new Error('User not found. Please check your email.');
    } else if (error.name === 'NotAuthorizedException') {
      throw new Error('Incorrect password. Please try again.');
    } else if (error.name === 'UserNotConfirmedException') {
      throw new Error('Please verify your email before signing in.');
    } else {
      throw new Error(error.message || 'Login failed. Please try again.');
    }
  }
}

/**
 * Logout
 */
export async function logout() {
  try {
    // Sign out from Cognito
    await amplifySignOut();
    console.log('[Auth] Cognito sign-out successful');
  } catch (error) {
    console.error('[Auth] Cognito sign-out error:', error);
  }
  
  // Clear local storage
  localStorage.removeItem(AUTH_KEY);
  sessionStorage.removeItem('idToken');
  sessionStorage.removeItem('accessToken');
  
  console.log('[Auth] Logged out');
}

/**
 * Get current user
 * @returns {Object|null} User object or null
 */
export function getCurrentUser() {
  const stored = localStorage.getItem(AUTH_KEY);
  if (!stored) return null;
  
  try {
    const user = JSON.parse(stored);
    
    // Validate that we have a Cognito user (has cognitoSub)
    // If not, it's old mock data - clear it
    if (!user.cognitoSub) {
      console.log('[Auth] Detected old mock user data, clearing...');
      localStorage.removeItem(AUTH_KEY);
      sessionStorage.removeItem('idToken');
      sessionStorage.removeItem('accessToken');
      return null;
    }
    
    return user;
  } catch (e) {
    console.error('[Auth] Failed to parse user:', e);
    return null;
  }
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export function isAuthenticated() {
  return getCurrentUser() !== null && sessionStorage.getItem('idToken') !== null;
}

/**
 * Get ID token for API calls
 * @returns {string|null} ID token or null
 */
export function getIdToken() {
  return sessionStorage.getItem('idToken');
}

/**
 * Get access token
 * @returns {string|null} Access token or null
 */
export function getAccessToken() {
  return sessionStorage.getItem('accessToken');
}

/**
 * Refresh auth session and get new tokens
 * @returns {Promise<Object>} New tokens
 */
export async function refreshSession() {
  try {
    const session = await fetchAuthSession({ forceRefresh: true });
    
    const idToken = session.tokens?.idToken?.toString();
    const accessToken = session.tokens?.accessToken?.toString();
    
    if (idToken) {
      sessionStorage.setItem('idToken', idToken);
    }
    if (accessToken) {
      sessionStorage.setItem('accessToken', accessToken);
    }
    
    console.log('[Auth] Session refreshed');
    return { idToken, accessToken };
  } catch (error) {
    console.error('[Auth] Failed to refresh session:', error);
    throw error;
  }
}

/**
 * Check if user has role
 * @param {string} role - Role to check
 * @returns {boolean}
 */
export function hasRole(role) {
  const user = getCurrentUser();
  return user && user.role === role;
}

/**
 * Update user language
 * @param {string} language - Language code
 */
export function updateLanguage(language) {
  const user = getCurrentUser();
  if (!user) return;
  
  user.language = language;
  localStorage.setItem(AUTH_KEY, JSON.stringify(user));
  console.log('[Auth] Language updated:', language);
}
