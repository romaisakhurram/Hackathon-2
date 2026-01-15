'use client';
import { getSession } from './auth-client'; // Use the existing session getter

class ApiClient {
  // ✅ FIXED: Ensure environment variable is used properly
  private baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

  request = async (endpoint: string, options: RequestInit = {}) => {
    // Normalize endpoint (ensure it starts with /)
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>)
    };

    // Get session from the existing auth client to check if user is authenticated
    let token: string | undefined;
    let isAuthenticated = false;

    try {
      const sessionResponse = await getSession();

      // Check if user is authenticated
      if (sessionResponse && typeof sessionResponse === 'object' && 'user' in sessionResponse) {
        // Check for authentication status - user exists means authenticated
          isAuthenticated = !!sessionResponse.user;
  
          // Extract token if available - better-auth uses cookie-based auth primarily
          if ('token' in sessionResponse && typeof sessionResponse.token === 'string') {
            token = sessionResponse.token;
          }
      }
    } catch (error) {
      console.error('❌ Auth Session Fetch Error:', error);
      isAuthenticated = false;
    }

    // Add token to headers if available, but rely primarily on cookie-based auth
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Prepare fetch options with credentials (for cookie-based auth)
    // This is the primary method for better-auth session management
    const fetchOptions: RequestInit = {
      ...options,
      headers,
      credentials: 'include', // Critical: Include cookies for session management
    };

    const response = await fetch(`${this.baseUrl}${cleanEndpoint}`, fetchOptions);

    if (!response.ok) {
      // Handle Unauthorized specifically
      if (response.status === 401) {
        console.error("🚫 401 Unauthorized: Invalid or expired session");

        // Don't immediately redirect - let the calling code handle this gracefully
        // The better-auth library should handle session invalidation internally
        if (!options?.skipRedirect) {
          // Since this is synchronous and we can't await getSession() here,
          // we'll let the calling component handle the redirect
          // The calling function should catch the error and decide to redirect
        }

        // Throw an error that can be caught by the calling function
        throw new Error('Unauthorized: Session may have expired');
      }

      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || `Error ${response.status}`);
    }

    return response.json();
  };

  get = (endpoint: string) => this.request(endpoint, { method: 'GET' });
  
  post = (endpoint: string, data: any) => 
    this.request(endpoint, { method: 'POST', body: JSON.stringify(data) });

  put = (endpoint: string, data: any) => 
    this.request(endpoint, { method: 'PUT', body: JSON.stringify(data) });

  delete = (endpoint: string) => 
    this.request(endpoint, { method: 'DELETE' });

  patch = (endpoint: string, data: any) => 
    this.request(endpoint, { method: 'PATCH', body: JSON.stringify(data) });
}

export const apiClient = new ApiClient();