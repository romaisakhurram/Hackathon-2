// Frontend authentication service for Todo Chatbot System
// Handles authentication-related API calls and token management

class AuthService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || '/api';
    this.tokenKey = 'todo-chatbot-token';
  }

  // Get token from localStorage
  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  // Set token in localStorage
  setToken(token) {
    localStorage.setItem(this.tokenKey, token);
  }

  // Remove token from localStorage
  removeToken() {
    localStorage.removeItem(this.tokenKey);
  }

  // Check if user is authenticated
  isAuthenticated() {
    const token = this.getToken();
    if (!token) {
      return false;
    }

    // Check if token is expired
    try {
      const tokenPayload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return tokenPayload.exp > currentTime;
    } catch (error) {
      console.error('Error decoding token:', error);
      return false;
    }
  }

  // Get user info from token
  getUserInfo() {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      const tokenPayload = JSON.parse(atob(token.split('.')[1]));
      return {
        id: tokenPayload.user_id,
        email: tokenPayload.sub,
        name: tokenPayload.name || null
      };
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }

  // Login user
  async login(email, password) {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      this.setToken(data.access_token);
      return { success: true, user: this.getUserInfo() };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message };
    }
  }

  // Signup user
  async signup(name, email, password) {
    try {
      const response = await fetch(`${this.baseURL}/auth/sign-up/email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }

      this.setToken(data.access_token);
      return { success: true, user: this.getUserInfo() };
    } catch (error) {
      console.error('Signup error:', error);
      return { success: false, error: error.message };
    }
  }

  // Logout user
  logout() {
    this.removeToken();
  }

  // Refresh token (if refresh tokens are implemented)
  async refreshToken() {
    // In a real implementation, you would call an endpoint to refresh the token
    // For now, we'll just return the current token status
    return this.isAuthenticated();
  }

  // Make authenticated API request
  async makeAuthenticatedRequest(url, options = {}) {
    const token = this.getToken();

    if (!token) {
      throw new Error('No authentication token found');
    }

    const authenticatedOptions = {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    };

    const response = await fetch(url, authenticatedOptions);

    if (response.status === 401) {
      // Token might be expired, redirect to login
      this.logout();
      window.location.href = '/login';
      throw new Error('Authentication required');
    }

    return response;
  }
}

// Export singleton instance
export default new AuthService();