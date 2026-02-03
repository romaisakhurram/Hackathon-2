'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getSession } from '@/lib/auth-client';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const session = await getSession();
        if (session) {
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
          router.push('/signin');
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        // If authentication check fails, redirect to sign in
        setIsAuthenticated(false);
        router.push('/signin');
      }
    };

    checkAuth();
  }, [router]);

  if (isAuthenticated === null) {
    // Loading state while checking authentication
    return fallback || (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (isAuthenticated === false) {
    // Redirect already handled in useEffect, but returning null to prevent rendering
    return null;
  }

  return <>{children}</>;
}