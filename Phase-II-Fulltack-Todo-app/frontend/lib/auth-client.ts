// Simple auth client that works with the backend's authentication system
class SimpleAuthClient {
  private baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

  constructor() {
    // Ensure baseUrl is properly initialized
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';
  }

  async signIn(credentials: { email: string; password: string }) {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/sign-in/email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Sign in failed');
      }

      const data = await response.json();

      // Store token in localStorage for persistence
      if (data.access_token) {
        localStorage.setItem('auth_token', data.access_token);
      }
      return data;
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  }

  async signUp(userData: { name: string; email: string; password: string }) {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/sign-up/email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Sign up failed');
      }

      const data = await response.json();

      // Store token in localStorage for persistence
      if (data.access_token) {
        localStorage.setItem('auth_token', data.access_token);
      }
      return data;
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  }

  async signOut() {
    try {
      // Clear the stored token
      localStorage.removeItem('auth_token');
      return { message: 'Successfully signed out' };
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  }

  async getSession() {
    // Get token from localStorage
    const token = localStorage.getItem('auth_token');

    if (token) {
      // Verify the token is still valid by calling the session endpoint
      try {
        const response = await fetch(`${this.baseUrl}/api/auth/get-session`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        const data = await response.json();

        if (response.ok && data.authenticated) {
          return {
            user: { id: data.user_id }, // Return user info if authenticated
            token: token,
          };
        } else {
          // If session is not valid, remove the token
          localStorage.removeItem('auth_token');
          return null;
        }
      } catch (error) {
        console.error('Session verification error:', error);
        // If session verification fails, clear the token
        localStorage.removeItem('auth_token');
        return null;
      }
    }

    // Return null if not authenticated
    return null;
  }
}

// Create a singleton instance
const authClient = new SimpleAuthClient();

// Export authentication functions bound to the instance to preserve 'this' context
export const signIn = authClient.signIn.bind(authClient);
export const signUp = authClient.signUp.bind(authClient);
export const signOut = authClient.signOut.bind(authClient);
export const getSession = authClient.getSession.bind(authClient);
export { authClient };
