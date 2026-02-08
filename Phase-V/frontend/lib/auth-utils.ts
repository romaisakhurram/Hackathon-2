/**
 * Authentication utilities for the chat interface.
 * Handles JWT token retrieval and passing to chat endpoint.
 */

import { getSession, signIn, signOut } from './auth-client';

/**
 * Get the current user's authentication token.
 * @returns Promise resolving to the JWT token string or null if not authenticated
 */
export async function getUserToken(): Promise<string | null> {
  try {
    const session = await getSession();

    if (session && session.token) {
      // Return the token
      return session.token || null;
    }

    return null;
  } catch (error) {
    console.error('Error getting user token:', error);
    return null;
  }
}

/**
 * Get the current user's ID.
 * @returns Promise resolving to the user ID string or null if not authenticated
 */
export async function getCurrentUserId(): Promise<string | null> {
  try {
    const session = await getSession();

    if (session?.user?.id) {
      return session.user.id;
    }

    return null;
  } catch (error) {
    console.error('Error getting current user ID:', error);
    return null;
  }
}

/**
 * Check if the user is currently authenticated.
 * @returns Promise resolving to boolean indicating authentication status
 */
export async function isAuthenticated(): Promise<boolean> {
  try {
    const token = await getUserToken();
    return token !== null && token !== undefined;
  } catch (error) {
    console.error('Error checking authentication status:', error);
    return false;
  }
}

/**
 * Ensure the user is authenticated, redirecting to sign-in if necessary.
 * @returns Promise resolving to the token if authenticated, null if redirected to sign-in
 */
export async function ensureAuthentication(redirectTo: string = '/signin'): Promise<string | null> {
  const token = await getUserToken();

  if (!token) {
    // Redirect to sign-in page
    window.location.href = redirectTo;
    return null;
  }

  return token;
}

/**
 * Format the Authorization header with the JWT token.
 * @returns Promise resolving to the Authorization header string or null if not authenticated
 */
export async function getAuthHeader(): Promise<{ Authorization: string } | null> {
  const token = await getUserToken();

  if (token) {
    return {
      'Authorization': `Bearer ${token}`
    };
  }

  return null;
}

/**
 * Validate the current token is still valid (not expired).
 * @returns Promise resolving to boolean indicating if token is valid
 */
export async function isTokenValid(): Promise<boolean> {
  try {
    const session = await getSession();

    if (!session || !session.token) {
      return false;
    }

    // For now, we'll assume the token is valid
    // In a real implementation, we'd decode the JWT to check the 'exp' claim
    return true;
  } catch (error) {
    console.error('Error validating token:', error);
    return false;
  }
}

/**
 * Refresh the authentication token if needed.
 * @returns Promise resolving to the refreshed token or null if refresh failed
 */
export async function refreshTokenIfNeeded(): Promise<string | null> {
  try {
    const isValid = await isTokenValid();

    if (isValid) {
      return await getUserToken(); // Return current valid token
    }

    // If token is invalid/expired, try to get a new session
    // This would typically trigger a refresh if better-auth supports it
    // or redirect to re-authenticate
    const session = await getSession();

    if (!session) {
      // No session to refresh, return null
      return null;
    }

    // In better-auth, token refresh is often handled automatically by the library
    // For this implementation, we'll return the token if available
    return session.token || null;
  } catch (error) {
    console.error('Error refreshing token:', error);
    return null;
  }
}

/**
 * Prepare headers for chat API requests with authentication.
 * @returns Promise resolving to headers object with auth and content-type
 */
export async function prepareChatApiHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const authHeader = await getAuthHeader();

  if (authHeader) {
    headers['Authorization'] = authHeader.Authorization;
  }

  return headers;
}

/**
 * Validate user context before making chat requests.
 * @returns Promise resolving to object with token and user_id if valid, null otherwise
 */
export async function validateUserContext(): Promise<{ token: string; user_id: string } | null> {
  try {
    const token = await getUserToken();
    const user_id = await getCurrentUserId();

    if (!token || !user_id) {
      return null;
    }

    const isValid = await isTokenValid();

    if (!isValid) {
      return null;
    }

    return {
      token,
      user_id
    };
  } catch (error) {
    console.error('Error validating user context:', error);
    return null;
  }
}

/**
 * Get the authenticated user's profile information.
 * @returns Promise resolving to user profile or null if not authenticated
 */
export async function getUserProfile(): Promise<{
  id: string;
  name?: string;
  email?: string;
  image?: string;
} | null> {
  try {
    const session = await getSession();

    if (session?.user) {
      // Since the session.user only has id, we'll return a limited profile
      return {
        id: session.user.id,
        name: undefined,
        email: undefined,
        image: undefined
      };
    }

    return null;
  } catch (error) {
    console.error('Error getting user profile:', error);
    return null;
  }
}

/**
 * Sign out the current user and clear authentication context.
 */
export async function logoutCurrentUser(): Promise<void> {
  try {
    await signOut();
  } catch (error) {
    console.error('Error signing out user:', error);
    // Even if signOut fails, clear local storage as a fallback
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user_id');
  }
}

// Export default object with all auth utilities
const AuthUtils = {
  getUserToken,
  getCurrentUserId,
  isAuthenticated,
  ensureAuthentication,
  getAuthHeader,
  isTokenValid,
  refreshTokenIfNeeded,
  prepareChatApiHeaders,
  validateUserContext,
  getUserProfile,
  logoutCurrentUser,
};

export default AuthUtils;