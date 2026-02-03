'use client'

import { ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { signOut } from '@/lib/auth-client';
import { toast } from 'sonner';
import { LayoutDashboard, Plus, User, LogOut, Settings } from 'lucide-react';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await signOut();
      router.push('/signin');
      toast.success('Signed out successfully');
    } catch (error) {
      console.error('Error signing out:', error);
      toast.error('Failed to sign out');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-10 w-64 bg-white border-r border-slate-200">
        <div className="flex items-center justify-center h-16 px-4 border-b border-slate-200">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span className="text-xl font-bold text-slate-900">TaskFlow</span>
          </div>
        </div>
        <nav className="mt-6">
          <div className="px-3 space-y-1">
            <Button
              variant="ghost"
              className="w-full justify-start px-3 py-2 text-slate-700 hover:bg-slate-100"
              onClick={() => router.push('/dashboard')}
            >
              <LayoutDashboard className="h-4 w-4 mr-3" />
              Dashboard
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start px-3 py-2 text-slate-700 hover:bg-slate-100"
              onClick={() => router.push('/profile')}
            >
              <User className="h-4 w-4 mr-3" />
              Profile
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start px-3 py-2 text-slate-700 hover:bg-slate-100"
              onClick={() => router.push('/settings')}
            >
              <Settings className="h-4 w-4 mr-3" />
              Settings
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start px-3 py-2 mt-4"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4 mr-3" />
              Logout
            </Button>
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="ml-64">
        {/* Top navigation bar */}
        <header className="bg-white border-b border-slate-200">
          <div className="flex items-center justify-between h-16 px-6">
            <div>
              <h1 className="text-xl font-semibold text-slate-900">Dashboard</h1>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}