'use client';
import { getSession } from './auth-client'; // Use the existing session getter

class ApiClient {
  // ✅ FIXED: Ensure environment variable is used properly
  private baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

  request = async (endpoint: string, options: RequestInit = {}) => {
    // Normalize endpoint (ensure it starts with /)
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

    // Ensure baseUrl is properly formatted
    let normalizedBaseUrl = this.baseUrl;
    if (!normalizedBaseUrl.startsWith('http://') && !normalizedBaseUrl.startsWith('https://')) {
      normalizedBaseUrl = `http://${normalizedBaseUrl}`;
    }
    // Ensure baseUrl doesn't end with a slash
    if (normalizedBaseUrl.endsWith('/')) {
      normalizedBaseUrl = normalizedBaseUrl.slice(0, -1);
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>)
    };

    // Get the token directly from localStorage to ensure it's available
    const token = localStorage.getItem('auth_token');

    // Add authentication token to headers if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      console.log('Added authentication token to request'); // Debug log
    } else {
      console.log('No authentication token found'); // Debug log
    }

    // Prepare fetch options with credentials (for cookie-based auth)
    // This is the primary method for better-auth session management
    const fetchOptions: RequestInit = {
      ...options,
      headers,
      credentials: 'include', // Critical: Include cookies for session management
    };

    const fullUrl = `${normalizedBaseUrl}${cleanEndpoint}`;
    console.log(`Making request to: ${fullUrl}`); // Debug log
    console.log('Headers:', headers); // Debug log
    console.log('Credentials:', 'include'); // Debug log
    console.log('Token available:', !!token); // Debug log

    // Validate URL before making request
    try {
      new URL(fullUrl); // This will throw if the URL is invalid
    } catch (urlError) {
      console.error('Invalid URL:', fullUrl, urlError);
      throw new Error(`Invalid API URL: ${fullUrl}`);
    }

    const response = await fetch(fullUrl, fetchOptions);

    if (!response.ok) {
      // Handle Unauthorized specifically
      if (response.status === 401) {
        console.error("🚫 401 Unauthorized: Invalid or expired session");

        // Clear the token since it's invalid
        localStorage.removeItem('auth_token');

        // Attempt to get more details about the error
        let errorDetails = '';
        try {
          const errorResponse = await response.json();
          errorDetails = errorResponse.detail || errorResponse.message || 'Unknown error';
        } catch (e) {
          errorDetails = response.statusText || 'Unable to parse error';
        }

        console.error('Error details:', errorDetails);

        // Don't immediately redirect - let the calling code handle this gracefully
        // The better-auth library should handle session invalidation internally
        const skipRedirect = (options as any)?.skipRedirect; // Type assertion to handle custom property
        if (!skipRedirect) {
          // Since this is synchronous and we can't await getSession() here,
          // we'll let the calling component handle the redirect
          // The calling function should catch the error and decide to redirect
        }

        // Throw an error that can be caught by the calling function
        throw new Error(`Unauthorized: ${errorDetails}`);
      }

      // Try to get error details from response
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        // If response is not JSON, use status text
        errorData = { detail: response.statusText };
      }

      console.error(`API Error ${response.status}:`, errorData);
      throw new Error(errorData.detail || errorData.message || `Error ${response.status}`);
    }

    return response.json();
  };

  get = (endpoint: string) => this.request(endpoint, { method: 'GET' });

  post = (endpoint: string, data: any) => {
    // Transform priority from string to number if present
    const transformedData = { ...data };
    if (transformedData.priority) {
      switch (transformedData.priority) {
        case 'low':
          transformedData.priority = 1;
          break;
        case 'medium':
          transformedData.priority = 2;
          break;
        case 'high':
          transformedData.priority = 3;
          break;
        default:
          // If it's already a number, leave it as is
          if (typeof transformedData.priority === 'number') {
            break;
          }
          // Default to medium if unknown value
          transformedData.priority = 2;
      }
    }
    return this.request(endpoint, { method: 'POST', body: JSON.stringify(transformedData) });
  };

  put = (endpoint: string, data: any) => {
    // Transform priority from string to number if present
    const transformedData = { ...data };
    if (transformedData.priority) {
      switch (transformedData.priority) {
        case 'low':
          transformedData.priority = 1;
          break;
        case 'medium':
          transformedData.priority = 2;
          break;
        case 'high':
          transformedData.priority = 3;
          break;
        default:
          // If it's already a number, leave it as is
          if (typeof transformedData.priority === 'number') {
            break;
          }
          // Default to medium if unknown value
          transformedData.priority = 2;
      }
    }
    return this.request(endpoint, { method: 'PUT', body: JSON.stringify(transformedData) });
  };

  delete = (endpoint: string) =>
    this.request(endpoint, { method: 'DELETE' });

  patch = (endpoint: string, data: any) => {
    // Transform priority from string to number if present
    const transformedData = { ...data };
    if (transformedData.priority) {
      switch (transformedData.priority) {
        case 'low':
          transformedData.priority = 1;
          break;
        case 'medium':
          transformedData.priority = 2;
          break;
        case 'high':
          transformedData.priority = 3;
          break;
        default:
          // If it's already a number, leave it as is
          if (typeof transformedData.priority === 'number') {
            break;
          }
          // Default to medium if unknown value
          transformedData.priority = 2;
      }
    }
    return this.request(endpoint, { method: 'PATCH', body: JSON.stringify(transformedData) });
  };
}

export const apiClient = new ApiClient();