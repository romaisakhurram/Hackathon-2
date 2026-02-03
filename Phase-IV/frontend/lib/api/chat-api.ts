/**
 * API client for chat endpoint communication.
 * Provides methods to interact with the backend chat API.
 */

import { getSession } from '../auth-client';
import { apiClient } from '../api';

interface ChatRequest {
  message: string;
  conversation_id?: string;
}

interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: Array<{
    name: string;
    parameters: Record<string, any>;
    result: any;
  }>;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  conversation_id: string;
}

/**
 * Send a chat message to the backend and receive AI response.
 * @param message - The user's message to send
 * @param conversationId - Optional conversation ID to continue existing conversation
 * @returns ChatResponse with conversation ID, AI response, and tool calls
 */
export async function sendChatMessage(message: string, conversationId?: string): Promise<ChatResponse> {
  try {
    // Get the current user's session/token
    const session = await getSession();
    if (!session?.user?.id) {
      throw new Error('User not authenticated');
    }

    const userId = session.user.id;

    // Prepare the request body
    const requestBody: ChatRequest = {
      message,
      conversation_id: conversationId
    };

    // Use the configured API client to make the request to the backend
    const data = await apiClient.post(`/api/${userId}/chat`, requestBody);
    return data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

/**
 * Get conversation history for a specific conversation.
 * @param conversationId - ID of the conversation to retrieve messages for
 * @returns Array of messages in the conversation
 */
export async function getConversationHistory(conversationId: string): Promise<Message[]> {
  try {
    // Get the current user's session/token
    const session = await getSession();
    if (!session?.user?.id) {
      throw new Error('User not authenticated');
    }

    const userId = session.user.id;

    // Use the configured API client to get conversation messages
    const data = await apiClient.get(`/api/${userId}/conversations/${conversationId}/messages`);
    return data.messages || [];
  } catch (error) {
    console.error('Error getting conversation history:', error);
    throw error;
  }
}

/**
 * Get all conversations for the current user.
 * @returns Array of conversation metadata
 */
export async function getUserConversations(): Promise<Array<{
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}>> {
  try {
    // Get the current user's session/token
    const session = await getSession();
    if (!session?.user?.id) {
      throw new Error('User not authenticated');
    }

    const userId = session.user.id;

    // Use the configured API client to get user's conversations
    const data = await apiClient.get(`/api/${userId}/conversations`);
    return data.conversations || [];
  } catch (error) {
    console.error('Error getting user conversations:', error);
    throw error;
  }
}

/**
 * Create a new conversation.
 * @returns New conversation with ID
 */
export async function createNewConversation(): Promise<ChatResponse> {
  try {
    // Get the current user's session/token
    const session = await getSession();
    if (!session?.user?.id) {
      throw new Error('User not authenticated');
    }

    const userId = session.user.id;

    // Send an empty message to create a new conversation
    const data = await apiClient.post(`/api/${userId}/chat`, { message: "" }); // Empty message to just create conversation
    return data;
  } catch (error) {
    console.error('Error creating new conversation:', error);
    throw error;
  }
}