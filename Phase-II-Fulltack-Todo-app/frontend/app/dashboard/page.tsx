'use client'

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api';
import { getSession, signOut } from '@/lib/auth-client';
import { toast } from 'sonner';
import { Plus, Check, X, AlertCircle, MoreVertical, Search, Filter, Calendar, User, Edit } from 'lucide-react';
import { Task } from '@/types/task';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTask, setEditingTask] = useState<{id: string, title: string, description: string, priority: 'low' | 'medium' | 'high'} | null>(null);
  const router = useRouter();

  // Check if user is authenticated and maintain session
  useEffect(() => {
    let isMounted = true; // Track if component is still mounted

    const checkAuth = async () => {
      try {
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
        localStorage.removeItem('auth_token');
        if (isMounted) {
          router.push('/signin');
        }
      }
    };

    // Start the authentication check
    checkAuth();

    // Set up periodic session validation (check every 30 seconds)
    const intervalId = setInterval(async () => {
      if (isMounted) {
        try {
          const session = await getSession();

          console.log('Periodic session check:', session);

          // Our new auth client returns either null (not authenticated) or an object with user info
          const isValidSession = session !== null;

          if (!isValidSession) {
            console.log('Session validation failed, redirecting to sign in');
            console.log('Session data:', session);
            // Clear any stored token to ensure clean state
            localStorage.removeItem('auth_token');
            if (isMounted) {
              router.push('/signin');
            }
          }
        } catch (error) {
          console.error('Periodic auth check failed:', error);
          // Clear any stored token to ensure clean state and redirect
          localStorage.removeItem('auth_token');
          if (isMounted) {
            router.push('/signin');
          }
        }
      }
    }, 30000); // Check every 30 seconds

    // Cleanup function to prevent memory leaks
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [router]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/tasks/');

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
        localStorage.removeItem('auth_token');
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
      const newTask = await apiClient.post('/api/tasks/', {
        title: newTaskTitle,
        description: newTaskDescription,
        priority: priorityValue,
      });

      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
      setNewTaskDescription('');
      setNewTaskPriority('medium');
      setShowAddForm(false);
      toast.success('Task added successfully');
    } catch (error) {
      console.error('Error adding task:', error);

      // Check if this is an authentication error
      if (error instanceof Error && error.message.includes('Unauthorized')) {
        console.log('Authentication error detected when adding task');
        // Clear any stored token to ensure clean state
        localStorage.removeItem('auth_token');
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
        localStorage.removeItem('auth_token');
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
        localStorage.removeItem('auth_token');
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
        localStorage.removeItem('auth_token');
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h1 className="text-xl font-semibold text-slate-900">TaskFlow Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-slate-600">
                <User className="h-4 w-4" />
                <span className="text-sm">Welcome back!</span>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Your Tasks</h2>
            <p className="text-slate-600 mt-1">Manage your personal todo items efficiently</p>
          </div>
          <Button className="mt-4 sm:mt-0 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white" onClick={() => setShowAddForm(!showAddForm)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Task
          </Button>
        </div>

        {/* Add Task Form */}
        {showAddForm && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
            <h3 className="text-lg font-medium text-slate-900 mb-4">Create New Task</h3>
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
        {tasks.length === 0 ? (
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
              {tasks.map((task) => (
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
                          <div className="flex items-center mt-2 space-x-2">
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
      </main>

      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50"></div>
    </div>
  );
}