// Frontend API client for Todo Chatbot System
// Handles all communication with the backend API

class ApiClient {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || '/api';
  }

  // Generic request method with authentication
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('todo-chatbot-token');
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // AUTHENTICATION METHODS
  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async signup(userData) {
    return this.request('/auth/sign-up/email', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout() {
    // In a real implementation, you might call a logout endpoint
    // For now, just remove the token
    localStorage.removeItem('todo-chatbot-token');
    return { message: 'Logged out successfully' };
  }

  // TASK METHODS
  async getTasks() {
    return this.request('/tasks/');
  }

  async createTask(taskData) {
    return this.request('/tasks/', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(taskId, taskData) {
    return this.request(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(taskId) {
    return this.request(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(taskId) {
    return this.request(`/tasks/${taskId}/toggle`, {
      method: 'PATCH',
    });
  }

  async searchTasks(filters) {
    return this.request('/tasks/search', {
      method: 'POST',
      body: JSON.stringify(filters),
    });
  }

  // CHAT METHODS
  async createConversation(userId) {
    return this.request(`/${userId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message: "New conversation started", conversation_id: null }),
    });
  }

  async sendMessage(userId, message, conversationId = null) {
    return this.request(`/${userId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ 
        message: message,
        conversation_id: conversationId
      }),
    });
  }

  async getConversations(userId) {
    return this.request(`/${userId}/conversations`);
  }

  async getConversationMessages(userId, conversationId) {
    return this.request(`/${userId}/conversations/${conversationId}/messages`);
  }

  async deleteConversation(userId, conversationId) {
    return this.request(`/${userId}/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  // REMINDER METHODS
  async getReminders() {
    return this.request('/reminders/');
  }

  async createReminder(reminderData) {
    return this.request('/reminders/', {
      method: 'POST',
      body: JSON.stringify(reminderData),
    });
  }

  async updateReminder(reminderId, reminderData) {
    return this.request(`/reminders/${reminderId}`, {
      method: 'PUT',
      body: JSON.stringify(reminderData),
    });
  }

  async deleteReminder(reminderId) {
    return this.request(`/reminders/${reminderId}`, {
      method: 'DELETE',
    });
  }

  // TAG METHODS
  async getTags() {
    return this.request('/tags/');
  }

  async createTag(tagData) {
    return this.request('/tags/', {
      method: 'POST',
      body: JSON.stringify(tagData),
    });
  }

  async updateTag(tagId, tagData) {
    return this.request(`/tags/${tagId}`, {
      method: 'PUT',
      body: JSON.stringify(tagData),
    });
  }

  async deleteTag(tagId) {
    return this.request(`/tags/${tagId}`, {
      method: 'DELETE',
    });
  }

  // HEALTH CHECK
  async healthCheck() {
    return this.request('/chat/health');
  }
}

// Export singleton instance
export default new ApiClient();