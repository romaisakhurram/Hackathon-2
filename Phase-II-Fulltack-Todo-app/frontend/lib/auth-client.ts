import { createAuthClient } from 'better-auth/client';

// Create the auth client with JWT plugin
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000',
  fetchOptions:{
    credentials: 'include',
  },
});

// Export authentication functions
export const { signIn, signUp, signOut, getSession } = authClient;

export { createAuthClient };
