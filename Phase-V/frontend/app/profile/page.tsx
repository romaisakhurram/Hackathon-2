'use client'

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { getSession } from '@/lib/auth-client';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';

interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
  is_active: boolean;
  consent_granted_at: string | null;
  consent_version: string | null;
}

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const router = useRouter();

  useEffect(() => {
    const checkAuthAndFetchUser = async () => {
      try {
        const session = await getSession();
        if (!session) {
          router.push('/signin');
          return;
        }
        // Fetch user profile from backend
        try {
          const userProfile = await apiClient.get('/api/user/profile');
          setUser(userProfile);
          setName(userProfile.name || '');
        } catch (error) {
          console.error('Error fetching profile:', error);
          // Fallback to session data
          setUser({
            id: session.user?.id || '',
            email: (session.user as any)?.email || '',
            name: (session.user as any)?.name || null,
            created_at: new Date().toISOString(),
            is_active: true,
            consent_granted_at: null,
            consent_version: null
          });
          setName((session.user as any)?.name || '');
        }
      } catch (error) {
        console.error('Error fetching user:', error);
        toast.error('Failed to load user profile');
        router.push('/signin');
      } finally {
        setLoading(false);
      }
    };

    checkAuthAndFetchUser();
  }, [router]);

  const handleSaveProfile = async () => {
    try {
      const updatedUser = await apiClient.put('/api/user/profile', { name });
      setUser(updatedUser);
      setEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-6 py-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {user?.name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">{user?.name || 'User'}</h1>
                <p className="text-slate-600">{user?.email}</p>
                <p className="text-sm text-slate-500">Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'today'}</p>
              </div>
            </div>
            <Button variant="outline" onClick={() => setEditing(!editing)}>
              {editing ? 'Cancel' : 'Edit Profile'}
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-lg font-medium text-slate-900 mb-4">Personal Information</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                  {editing ? (
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="Enter your name"
                    />
                  ) : (
                    <p className="text-slate-900">{user?.name || 'Not provided'}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                  <p className="text-slate-900">{user?.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Account Type</label>
                  <p className="text-slate-900">Free</p>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-lg font-medium text-slate-900 mb-4">Security</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                  <p className="text-slate-900">********</p>
                  <Button variant="outline" size="sm" className="mt-2">
                    Change Password
                  </Button>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Two-Factor Authentication</label>
                  <p className="text-slate-900">Disabled</p>
                  <Button variant="outline" size="sm" className="mt-2">
                    Enable 2FA
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {editing && (
            <div className="mt-8 flex justify-end space-x-4">
              <Button variant="outline" onClick={() => setEditing(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveProfile}>
                Save Changes
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}