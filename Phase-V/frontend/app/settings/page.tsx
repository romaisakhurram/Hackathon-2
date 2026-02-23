'use client'

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { getSession } from '@/lib/auth-client';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';

interface UserSettings {
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
    in_app: boolean;
  };
  theme: string;
  language: string;
  timezone: string;
}

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState<UserSettings>({
    notifications: {
      email: true,
      push: true,
      sms: false,
      in_app: true,
    },
    theme: 'system',
    language: 'en',
    timezone: 'UTC',
  });
  const router = useRouter();

  useEffect(() => {
    const checkAuthAndFetchUser = async () => {
      try {
        const session = await getSession();
        if (!session) {
          router.push('/signin');
          return;
        }
        setUser(session.user);
        
        // Fetch user settings from backend
        try {
          const userSettings = await apiClient.get('/api/user/settings');
          setSettings(userSettings);
        } catch (error) {
          console.error('Error fetching settings:', error);
          // Use default settings if fetch fails
        }
      } catch (error) {
        console.error('Error fetching user:', error);
        toast.error('Failed to load settings');
        router.push('/signin');
      } finally {
        setLoading(false);
      }
    };

    checkAuthAndFetchUser();
  }, [router]);

  const handleNotificationChange = (type: string) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [type]: !prev.notifications[type as keyof typeof prev.notifications]
      }
    }));
  };

  const handleSaveSettings = async () => {
    try {
      await apiClient.put('/api/user/settings', settings);
      toast.success('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    }
  };

  const handleExportData = async () => {
    try {
      const result = await apiClient.post('/api/user/export-data', {});
      toast.success(result.message || 'Data export initiated! You will receive an email when ready.');
    } catch (error) {
      console.error('Error exporting data:', error);
      toast.error('Failed to export data');
    }
  };

  const handleDeleteAccount = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }
    
    try {
      await apiClient.delete('/api/user/account');
      toast.success('Account deletion requested. You will receive a confirmation email.');
      // Clear local storage and redirect
      localStorage.removeItem('auth_token');
      router.push('/signin');
    } catch (error) {
      console.error('Error deleting account:', error);
      toast.error('Failed to delete account');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-6 py-8">
          <h1 className="text-2xl font-bold text-slate-900 mb-8">Settings</h1>

          <div className="space-y-8">
            {/* Account Settings */}
            <div>
              <h2 className="text-lg font-medium text-slate-900 mb-4">Account Settings</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-slate-900">Email Notifications</h3>
                    <p className="text-sm text-slate-500">Receive emails about important account events</p>
                  </div>
                  <button
                    onClick={() => handleNotificationChange('email')}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                      settings.notifications.email ? 'bg-indigo-600' : 'bg-slate-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        settings.notifications.email ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-slate-900">Push Notifications</h3>
                    <p className="text-sm text-slate-500">Receive push notifications on your devices</p>
                  </div>
                  <button
                    onClick={() => handleNotificationChange('push')}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                      settings.notifications.push ? 'bg-indigo-600' : 'bg-slate-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        settings.notifications.push ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-slate-900">SMS Notifications</h3>
                    <p className="text-sm text-slate-500">Receive SMS notifications for urgent updates</p>
                  </div>
                  <button
                    onClick={() => handleNotificationChange('sms')}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                      settings.notifications.sms ? 'bg-indigo-600' : 'bg-slate-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        settings.notifications.sms ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Theme Settings */}
            <div>
              <h2 className="text-lg font-medium text-slate-900 mb-4">Theme Settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Appearance</label>
                  <div className="flex space-x-4">
                    <div className="flex items-center">
                      <input
                        id="system-theme"
                        name="theme"
                        type="radio"
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-slate-300"
                        checked={settings.theme === 'system'}
                        onChange={() => setSettings({...settings, theme: 'system'})}
                      />
                      <label htmlFor="system-theme" className="ml-2 block text-sm text-slate-900">
                        System
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="light-theme"
                        name="theme"
                        type="radio"
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-slate-300"
                        checked={settings.theme === 'light'}
                        onChange={() => setSettings({...settings, theme: 'light'})}
                      />
                      <label htmlFor="light-theme" className="ml-2 block text-sm text-slate-900">
                        Light
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="dark-theme"
                        name="theme"
                        type="radio"
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-slate-300"
                        checked={settings.theme === 'dark'}
                        onChange={() => setSettings({...settings, theme: 'dark'})}
                      />
                      <label htmlFor="dark-theme" className="ml-2 block text-sm text-slate-900">
                        Dark
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Data Settings */}
            <div>
              <h2 className="text-lg font-medium text-slate-900 mb-4">Data Settings</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-slate-900 mb-1">Export Data</h3>
                  <p className="text-sm text-slate-500 mb-3">Download a copy of your data</p>
                  <Button variant="outline" onClick={handleExportData}>Export Data</Button>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-900 mb-1">Delete Account</h3>
                  <p className="text-sm text-slate-500 mb-3">Permanently delete your account and all data</p>
                  <Button variant="destructive" onClick={handleDeleteAccount}>Delete Account</Button>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 flex justify-end">
            <Button onClick={handleSaveSettings}>Save Settings</Button>
          </div>
        </div>
      </div>
    </div>
  );
}