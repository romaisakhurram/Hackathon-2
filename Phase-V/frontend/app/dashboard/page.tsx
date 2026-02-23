'use client'

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { getSession, signOut } from '@/lib/auth-client';
import { toast } from 'sonner';
import { Plus, Check, X, AlertCircle, MoreVertical, Search, Filter, Calendar, User, Edit, MessageCircle, Clock, Repeat, Tag as TagIcon } from 'lucide-react';
import { Task } from '@/types/task';
import ChatInterface from '@/components/chat/chat-interface';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [newTaskDifficultyLevel, setNewTaskDifficultyLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('intermediate');
  const [newTaskDueDate, setNewTaskDueDate] = useState<string>('');
  const [newTaskTags, setNewTaskTags] = useState<string>('');
  const [newTaskRecurrence, setNewTaskRecurrence] = useState<'none' | 'daily' | 'weekly' | 'monthly' | 'yearly'>('none');
  const [newTaskReminder, setNewTaskReminder] = useState<'none' | 'email' | 'push' | 'sms' | 'in-app'>('none');
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTask, setEditingTask] = useState<{id: string, title: string, description: string, priority: 'low' | 'medium' | 'high'} | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterBy, setFilterBy] = useState<'all' | 'pending' | 'completed' | 'in-progress'>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'due_date' | 'priority' | 'title'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showUserMenu && !target.closest('.md\\:hidden')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showUserMenu]);

  // Check if user is authenticated and maintain session
  useEffect(() => {
    let isMounted = true; // Track if component is still mounted

    const checkAuth = async () => {
      try {
        // Ensure we're on the client side before checking authentication
        if (typeof window === 'undefined') {
          return;
        }

        const session = await getSession();

        console.log('Full session object:', session);

        // Our new auth client returns either null (not authenticated) or an object with user info
        const isValidSession = session !== null;

        if (isValidSession) {
          console.log('Authentication verified, loading tasks');
          fetchTasks();
        } else {
          console.log('Authentication failed, redirecting to sign in');
          console.log('Session data:', session);
          if (isMounted) {
            router.push('/signin');
          }
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        // Clear any stored token to ensure clean state
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        if (isMounted) {
          router.push('/signin');
        }
      }
    };

    // Start the authentication check
    checkAuth();

    // Set up periodic session validation (check every 30 seconds)
    const intervalId = setInterval(async () => {
      if (isMounted && typeof window !== 'undefined') {
        try {
          const session = await getSession();

          console.log('Periodic session check:', session);

          // Our new auth client returns either null (not authenticated) or an object with user info
          const isValidSession = session !== null;

          if (!isValidSession) {
            console.log('Session validation failed, redirecting to sign in');
            console.log('Session data:', session);
            // Clear any stored token to ensure clean state
            if (typeof window !== 'undefined') {
              localStorage.removeItem('auth_token');
            }
            if (isMounted) {
              router.push('/signin');
            }
          }
        } catch (error) {
          console.error('Periodic auth check failed:', error);
          // Clear any stored token to ensure clean state and redirect
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
          }
          if (isMounted) {
            router.push('/signin');
          }
        }
      }
    }, 30000); // Check every 30 seconds

    // Add event listener to fetch tasks when the page becomes visible again
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isMounted) {
        console.log('Page became visible, fetching latest tasks');
        fetchTasks();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Cleanup function to prevent memory leaks
    return () => {
      isMounted = false;
      clearInterval(intervalId);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [router]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      
      // Build query parameters based on filters and search
      let endpoint = '/api/tasks/';
      const params = new URLSearchParams();
      
      if (searchQuery) {
        endpoint = '/api/tasks/search';
        params.append('query', searchQuery);
        
        // Add filters to search request
        const filters: any = {};
        if (filterBy !== 'all') {
          filters.status = [filterBy];
        }
        if (params.toString()) {
          params.append('filters', JSON.stringify(filters));
        }
      } else if (filterBy !== 'all') {
        // If not searching but filtering, we need to implement a different approach
        // For now, we'll fetch all and filter client-side
      }
      
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder);
      params.append('page', '1');
      params.append('limit', '100'); // Adjust as needed
      
      const queryString = params.toString();
      const fullEndpoint = endpoint + (queryString ? '?' + queryString : '');
      
      const response = await apiClient.get(fullEndpoint);

      // Convert numeric priorities to string for UI display
      const tasksWithConvertedPriorities = response.map((task: any) => ({
        ...task,
        priority: task.priority === 1 ? 'low' :
                 task.priority === 2 ? 'medium' :
                 task.priority === 3 ? 'high' : 'medium'
      }));

      setTasks(tasksWithConvertedPriorities || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);

      // Check if this is an authentication error
      if (error instanceof Error && error.message.includes('Unauthorized')) {
        // Don't show toast for auth errors, let the session monitoring handle it
        console.log('Authentication error detected, letting session monitoring handle redirect');
        // Clear any stored token to ensure clean state
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        // Redirect to sign in
        router.push('/signin');
      } else {
        toast.error('Failed to load tasks');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newTaskTitle.trim()) {
      toast.error('Task title is required');
      return;
    }

    // Convert priority string to number for backend compatibility
    let priorityValue = 0;
    if (newTaskPriority === 'low') priorityValue = 1;
    else if (newTaskPriority === 'medium') priorityValue = 2;
    else if (newTaskPriority === 'high') priorityValue = 3;

    try {
      const newTaskData: any = {
        title: newTaskTitle,
        description: newTaskDescription,
        priority: priorityValue,
        difficulty_level: newTaskDifficultyLevel,
        status: 'pending',
      };

      // Add due date if provided
      if (newTaskDueDate) {
        newTaskData.due_date = newTaskDueDate;
      }

      // Note: tags, recurrence_rule, and reminders are not supported in basic create
      // They will be added in a future update

      const newTask = await apiClient.post('/api/tasks/', newTaskData);

      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
      setNewTaskDescription('');
      setNewTaskPriority('medium');
      setNewTaskDifficultyLevel('intermediate');
      setNewTaskDueDate('');
      setNewTaskTags('');
      setNewTaskRecurrence('none');
      setNewTaskReminder('none');
      setShowAddForm(false);
      toast.success('Task added successfully');
    } catch (error) {
      console.error('Error adding task:', error);

      // Check if this is an authentication error
      if (error instanceof Error && error.message.includes('Unauthorized')) {
        console.log('Authentication error detected when adding task');
        // Clear any stored token to ensure clean state
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        // Redirect to sign in
        router.push('/signin');
      } else {
        toast.error('Failed to add task');
      }
    }
  };

  const handleToggleComplete = async (id: string, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
      const updatedTask = await apiClient.patch(`/api/tasks/${id}/toggle`, { status: newStatus });

      setTasks(tasks.map(task =>
        task.id === id ? { ...task, status: newStatus } : task
      ));

      toast.success(`Task ${newStatus === 'completed' ? 'completed' : 'marked as pending'}`);
    } catch (error) {
      console.error('Error updating task:', error);

      // Check if this is an authentication error
      if (error instanceof Error && error.message.includes('Unauthorized')) {
        console.log('Authentication error detected when toggling task');
        // Clear any stored token to ensure clean state
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        // Redirect to sign in
        router.push('/signin');
      } else {
        toast.error('Failed to update task');
      }
    }
  };

  const handleDeleteTask = async (id: string) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await apiClient.delete(`/api/tasks/${id}`);
      setTasks(tasks.filter(task => task.id !== id));
      toast.success('Task deleted successfully');
    } catch (error) {
      console.error('Error deleting task:', error);

      // Check if this is an authentication error
      if (error instanceof Error && error.message.includes('Unauthorized')) {
        console.log('Authentication error detected when deleting task');
        // Clear any stored token to ensure clean state
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        // Redirect to sign in
        router.push('/signin');
      } else {
        toast.error('Failed to delete task');
      }
    }
  };

  const startEditingTask = (task: Task) => {
    // Task.priority is already a string ('low' | 'medium' | 'high'), no conversion needed
    setEditingTask({
      id: task.id,
      title: task.title,
      description: task.description || '',
      priority: task.priority
    });
  };

  const handleUpdateTask = async () => {
    if (!editingTask) return;

    try {
      const updatedTask = await apiClient.put(`/api/tasks/${editingTask.id}`, {
        title: editingTask.title,
        description: editingTask.description,
        priority: editingTask.priority, // apiClient will handle the conversion to number
      });

      setTasks(tasks.map(task =>
        task.id === editingTask.id ? updatedTask : task
      ));

      setEditingTask(null);
      toast.success('Task updated successfully');
    } catch (error) {
      console.error('Error updating task:', error);

      // Check if this is an authentication error
      if (error instanceof Error && error.message.includes('Unauthorized')) {
        console.log('Authentication error detected when updating task');
        // Clear any stored token to ensure clean state
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        // Redirect to sign in
        router.push('/signin');
      } else {
        toast.error('Failed to update task');
      }
    }
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
  };

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

  // Apply client-side filtering if not using search
  const filteredAndSortedTasks = tasks.filter(task => {
    if (filterBy === 'all') return true;
    return task.status === filterBy;
  }).sort((a, b) => {
    let aValue, bValue;
    
    switch (sortBy) {
      case 'title':
        aValue = a.title.toLowerCase();
        bValue = b.title.toLowerCase();
        break;
      case 'priority':
        const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
        aValue = priorityOrder[a.priority as keyof typeof priorityOrder];
        bValue = priorityOrder[b.priority as keyof typeof priorityOrder];
        break;
      case 'due_date':
        aValue = a.due_date ? new Date(a.due_date).getTime() : Infinity;
        bValue = b.due_date ? new Date(b.due_date).getTime() : Infinity;
        break;
      case 'created_at':
      default:
        aValue = new Date(a.created_at).getTime();
        bValue = new Date(b.created_at).getTime();
        break;
    }
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header - Responsive */}
      <header className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-40">
        <div className="w-full px-3 sm:px-4 md:px-6 lg:px-8">
          <div className="flex justify-between h-14 sm:h-16 items-center">
            <div className="flex items-center">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center flex-shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 sm:h-6 sm:w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h1 className="text-lg sm:text-xl md:text-2xl font-bold text-slate-900 ml-2 sm:ml-3 truncate">TaskFlow</h1>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-3">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/chat">
                  <MessageCircle className="h-5 w-5" />
                  <span className="ml-2">Chat</span>
                </Link>
              </Button>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/profile">
                  <User className="h-5 w-5" />
                  <span className="ml-2">Profile</span>
                </Link>
              </Button>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/settings">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span className="ml-2">Settings</span>
                </Link>
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout} className="text-sm">
                Logout
              </Button>
            </div>
            
            {/* Mobile Menu Button */}
            <div className="md:hidden relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="p-2 rounded-lg bg-indigo-50 text-indigo-600 active:scale-95 transition-transform"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              
              {/* Mobile Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in zoom-in duration-200">
                  <button
                    onClick={() => { router.push('/dashboard'); setShowUserMenu(false); }}
                    className="w-full px-4 py-3 text-left text-sm text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Dashboard
                  </button>
                  <button
                    onClick={() => { router.push('/profile'); setShowUserMenu(false); }}
                    className="w-full px-4 py-3 text-left text-sm text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center transition-colors"
                  >
                    <User className="h-5 w-5 mr-3" />
                    Profile
                  </button>
                  <button
                    onClick={() => { router.push('/settings'); setShowUserMenu(false); }}
                    className="w-full px-4 py-3 text-left text-sm text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Settings
                  </button>
                  <button
                    onClick={() => { router.push('/chat'); setShowUserMenu(false); }}
                    className="w-full px-4 py-3 text-left text-sm text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center transition-colors"
                  >
                    <MessageCircle className="h-5 w-5 mr-3" />
                    Chat
                  </button>
                  <div className="border-t border-slate-200 my-1"></div>
                  <button
                    onClick={() => { handleLogout(); setShowUserMenu(false); }}
                    className="w-full px-4 py-3 text-left text-sm text-red-600 hover:bg-red-50 flex items-center transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-8">
        <div className="flex flex-col lg:flex-row gap-4 sm:gap-8">
          {/* Tasks Section */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 sm:mb-8 gap-3">
              <div className="w-full sm:w-auto">
                <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Your Tasks</h2>
                <p className="text-sm sm:text-base text-slate-600 mt-1">Manage your personal todo items efficiently</p>
              </div>
              <Button className="w-full sm:w-auto mt-2 sm:mt-0 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white text-sm sm:text-base" onClick={() => setShowAddForm(!showAddForm)}>
                <Plus className="h-4 w-4 mr-1 sm:mr-2" />
                Add Task
              </Button>
            </div>

            {/* Filters and Search */}
            <div className="mb-4 sm:mb-6 flex flex-col gap-3">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search tasks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm sm:text-base"
                />
              </div>
              <div className="grid grid-cols-2 sm:flex sm:flex-wrap gap-2">
                <select
                  value={filterBy}
                  onChange={(e) => setFilterBy(e.target.value as any)}
                  className="px-2 sm:px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-xs sm:text-sm flex-1 min-w-[120px]"
                >
                  <option value="all">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="in-progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-2 sm:px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-xs sm:text-sm flex-1 min-w-[140px]"
                >
                  <option value="created_at">Sort by Date</option>
                  <option value="due_date">Sort by Due Date</option>
                  <option value="priority">Sort by Priority</option>
                  <option value="title">Sort by Title</option>
                </select>
                <select
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value as any)}
                  className="px-2 sm:px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-xs sm:text-sm flex-1 min-w-[120px]"
                >
                  <option value="desc">Descending</option>
                  <option value="asc">Ascending</option>
                </select>
                <Button onClick={fetchTasks} variant="outline" className="text-xs sm:text-sm px-3 sm:px-4">
                  Apply
                </Button>
              </div>
            </div>

            {/* Add Task Form */}
            {showAddForm && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 mb-4 sm:mb-6">
                <h3 className="text-base sm:text-lg font-medium text-slate-900 mb-4">Create New Task</h3>
                <form onSubmit={handleAddTask} className="space-y-4">
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-slate-700 mb-1">
                      Task Title *
                    </label>
                    <input
                      type="text"
                      id="title"
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="What needs to be done?"
                      required
                    />
                  </div>
                  <div>
                    <label htmlFor="description" className="block text-sm font-medium text-slate-700 mb-1">
                      Description
                    </label>
                    <textarea
                      id="description"
                      value={newTaskDescription}
                      onChange={(e) => setNewTaskDescription(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Add details..."
                      rows={3}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="priority" className="block text-sm font-medium text-slate-700 mb-1">
                        Priority
                      </label>
                      <select
                        id="priority"
                        value={newTaskPriority}
                        onChange={(e) => setNewTaskPriority(e.target.value as 'low' | 'medium' | 'high')}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>
                    <div>
                      <label htmlFor="difficulty" className="block text-sm font-medium text-slate-700 mb-1">
                        Difficulty Level
                      </label>
                      <select
                        id="difficulty"
                        value={newTaskDifficultyLevel}
                        onChange={(e) => setNewTaskDifficultyLevel(e.target.value as 'beginner' | 'intermediate' | 'advanced')}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      >
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="dueDate" className="block text-sm font-medium text-slate-700 mb-1">
                        Due Date
                      </label>
                      <input
                        type="date"
                        id="dueDate"
                        value={newTaskDueDate}
                        onChange={(e) => setNewTaskDueDate(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label htmlFor="tags" className="block text-sm font-medium text-slate-700 mb-1">
                        Tags (comma separated)
                      </label>
                      <input
                        type="text"
                        id="tags"
                        value={newTaskTags}
                        onChange={(e) => setNewTaskTags(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="work, personal, urgent"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="recurrence" className="block text-sm font-medium text-slate-700 mb-1">
                        Recurrence
                      </label>
                      <select
                        id="recurrence"
                        value={newTaskRecurrence}
                        onChange={(e) => setNewTaskRecurrence(e.target.value as any)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      >
                        <option value="none">No Recurrence</option>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="yearly">Yearly</option>
                      </select>
                    </div>
                    <div>
                      <label htmlFor="reminder" className="block text-sm font-medium text-slate-700 mb-1">
                        Reminder
                      </label>
                      <select
                        id="reminder"
                        value={newTaskReminder}
                        onChange={(e) => setNewTaskReminder(e.target.value as any)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      >
                        <option value="none">No Reminder</option>
                        <option value="email">Email</option>
                        <option value="push">Push Notification</option>
                        <option value="sms">SMS</option>
                        <option value="in-app">In-App</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex space-x-3 pt-2">
                    <Button type="submit">Add Task</Button>
                    <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                      Cancel
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* Task List */}
            {filteredAndSortedTasks.length === 0 ? (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
                <div className="mx-auto h-24 w-24 rounded-full bg-slate-100 flex items-center justify-center mb-6">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-slate-900 mb-1">No tasks yet</h3>
                <p className="text-slate-500 mb-6">Get started by creating your first task</p>
                <Button onClick={() => setShowAddForm(true)} className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white">
                  <Plus className="h-4 w-4 mr-2" />
                  Create your first task
                </Button>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="divide-y divide-slate-100">
                  {filteredAndSortedTasks.map((task) => (
                    editingTask && editingTask.id === task.id ? (
                      // Edit form for the task
                      <div key={task.id} className="p-6 bg-slate-50 border border-slate-200 rounded-lg m-4">
                        <div className="space-y-4">
                          <div>
                            <label htmlFor={`edit-title-${task.id}`} className="block text-sm font-medium text-slate-700 mb-1">
                              Task Title
                            </label>
                            <input
                              id={`edit-title-${task.id}`}
                              type="text"
                              value={editingTask.title}
                              onChange={(e) => setEditingTask({...editingTask, title: e.target.value})}
                              className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                              placeholder="What needs to be done?"
                            />
                          </div>
                          <div>
                            <label htmlFor={`edit-description-${task.id}`} className="block text-sm font-medium text-slate-700 mb-1">
                              Description
                            </label>
                            <textarea
                              id={`edit-description-${task.id}`}
                              value={editingTask.description}
                              onChange={(e) => setEditingTask({...editingTask, description: e.target.value})}
                              className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                              placeholder="Add details..."
                              rows={2}
                            />
                          </div>
                          <div>
                            <label htmlFor={`edit-priority-${task.id}`} className="block text-sm font-medium text-slate-700 mb-1">
                              Priority
                            </label>
                            <select
                              id={`edit-priority-${task.id}`}
                              value={editingTask.priority}
                              onChange={(e) => setEditingTask({...editingTask, priority: e.target.value as 'low' | 'medium' | 'high'})}
                              className="w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            >
                              <option value="low">Low</option>
                              <option value="medium">Medium</option>
                              <option value="high">High</option>
                            </select>
                          </div>
                          <div className="flex space-x-3 pt-2">
                            <Button onClick={handleUpdateTask}>Save Changes</Button>
                            <Button type="button" variant="outline" onClick={handleCancelEdit}>
                              Cancel
                            </Button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      // Display task normally
                      <div key={task.id} className="p-6 hover:bg-slate-50 transition-colors">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3">
                            <button
                              onClick={() => handleToggleComplete(task.id, task.status)}
                              className={`flex-shrink-0 w-5 h-5 rounded border mt-0.5 flex items-center justify-center ${
                                task.status === 'completed'
                                  ? 'bg-green-500 border-green-500 text-white'
                                  : 'border-slate-300'
                              }`}
                              aria-label={task.status === 'completed' ? 'Mark as incomplete' : 'Mark as complete'}
                            >
                              {task.status === 'completed' && <Check className="h-4 w-4" />}
                            </button>
                            <div className="min-w-0 flex-1">
                              <h3 className={`text-sm font-medium ${
                                task.status === 'completed'
                                  ? 'text-slate-500 line-through'
                                  : 'text-slate-900'
                              }`}>
                                {task.title}
                              </h3>
                              {task.description && (
                                <p className={`text-sm mt-1 ${
                                  task.status === 'completed'
                                    ? 'text-slate-400 line-through'
                                    : 'text-slate-500'
                                }`}>
                                  {task.description}
                                </p>
                              )}
                              <div className="flex flex-wrap items-center gap-2 mt-2">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  task.priority === 'high'
                                    ? 'bg-red-100 text-red-800'
                                    : task.priority === 'medium'
                                      ? 'bg-yellow-100 text-yellow-800'
                                      : 'bg-green-100 text-green-800'
                                }`}>
                                  {task.priority}
                                </span>
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  task.status === 'completed'
                                    ? 'bg-green-100 text-green-800'
                                    : task.status === 'in-progress'
                                      ? 'bg-blue-100 text-blue-800'
                                      : 'bg-slate-100 text-slate-800'
                                }`}>
                                  {task.status}
                                </span>
                                {task.due_date && (
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                                    <Calendar className="h-3 w-3 mr-1" />
                                    {new Date(task.due_date).toLocaleDateString()}
                                  </span>
                                )}
                                {task.tags && task.tags.length > 0 && (
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                    <TagIcon className="h-3 w-3 mr-1" />
                                    {task.tags.join(', ')}
                                  </span>
                                )}
                                {task.recurrence_rule && (
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                                    <Repeat className="h-3 w-3 mr-1" />
                                    {task.recurrence_rule.interval}
                                  </span>
                                )}
                                {task.reminders && task.reminders.length > 0 && (
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
                                    <Clock className="h-3 w-3 mr-1" />
                                    {task.reminders[0].method}
                                  </span>
                                )}
                                <span className="text-xs text-slate-500">
                                  {new Date(task.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => startEditingTask(task)}
                              className="text-slate-400 hover:text-indigo-500 transition-colors p-1 rounded hover:bg-slate-100"
                              aria-label="Edit task"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteTask(task.id)}
                              className="text-slate-400 hover:text-red-500 transition-colors p-1 rounded hover:bg-red-50"
                              aria-label="Delete task"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    )
                  ))}
                </div>
              </div>
            )}
          </div> {/* Close flex-1 div (tasks section) */}
        </div> {/* Close flex container (row layout) */}
      </main>

      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50"></div>
    </div>
  );
}