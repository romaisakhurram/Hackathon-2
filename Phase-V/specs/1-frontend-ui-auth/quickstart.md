# Quickstart Guide: Professional SaaS Todo Frontend

## Prerequisites
- Node.js 18+ installed
- Access to backend API with the defined contracts
- Better Auth configured on the backend

## Setup Instructions

### 1. Initialize Next.js Project
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint
cd frontend
```

### 2. Install Dependencies
```bash
npm install lucide-react sonner clsx tailwind-merge
npm install better-auth
```

### 3. Configure Tailwind CSS
Update `tailwind.config.ts` with professional color palette:
```typescript
import type { Config } from 'tailwindcss'

export default {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        indigo: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        zinc: {
          50: '#fafafa',
          100: '#f4f4f5',
          200: '#e4e4e7',
          300: '#d4d4d8',
          400: '#a1a1aa',
          500: '#71717a',
          600: '#52525b',
          700: '#3f3f46',
          800: '#27272a',
          900: '#18181b',
        }
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
```

### 4. Set up Better Auth Client
Create `lib/auth-client.ts`:
```typescript
import { betterAuth } from 'better-auth/client';
import { jwtPlugin } from 'better-auth/client/plugins';

export const authClient = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  plugins: [
    jwtPlugin({
      secret: process.env.BETTER_AUTH_SECRET || 'your-secret-key'
    })
  ]
});
```

### 5. Create Centralized API Client
Create `lib/api.ts`:
```typescript
import { authClient } from './auth-client';

class ApiClient {
  private baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

  async request(endpoint: string, options: RequestInit = {}) {
    const token = await authClient.getSession();

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  get = (endpoint: string) => this.request(endpoint, { method: 'GET' });
  post = (endpoint: string, data: any) =>
    this.request(endpoint, { method: 'POST', body: JSON.stringify(data) });
  put = (endpoint: string, data: any) =>
    this.request(endpoint, { method: 'PUT', body: JSON.stringify(data) });
  delete = (endpoint: string) => this.request(endpoint, { method: 'DELETE' });
  patch = (endpoint: string, data: any) =>
    this.request(endpoint, { method: 'PATCH', body: JSON.stringify(data) });
}

export const apiClient = new ApiClient();
```

### 6. Implement Protected Route Middleware
Create a higher-order component or hook for protected routes that checks for valid session before allowing access to dashboard.

### 7. Development Workflow
- Run `npm run dev` to start the development server
- Access the application at `http://localhost:3000`
- Authentication pages will be available at `/signin` and `/signup`
- Dashboard will be available at `/dashboard` for authenticated users