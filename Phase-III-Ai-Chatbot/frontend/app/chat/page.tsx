'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { getUserToken, getCurrentUserId } from '@/lib/auth-utils';
import { Send, Bot, User, Loader2, Sparkles, Lightbulb, CheckCircle, XCircle, AlertTriangle, Check } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tool_calls?: any[];
  action?: string;
  result?: any;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    // Add user message to the conversation
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get current user ID from auth context first
      const userId = await getCurrentUserId();

      // Check if user is authenticated
      if (!userId) {
        throw new Error('User not authenticated. Please sign in to continue.');
      }

      // Get user token for authentication
      const token = await getUserToken();
      if (!token) {
        throw new Error('Authentication token missing. Please sign in again.');
      }

      // Send the message to the backend chat endpoint
      // Use the API base URL from environment with proper protocol
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

      // Ensure the URL has the proper protocol
      let fullApiUrl = apiUrl;
      if (!fullApiUrl.startsWith('http://') && !fullApiUrl.startsWith('https://')) {
        fullApiUrl = `https://${fullApiUrl}`;
      }

      const endpoint = `${fullApiUrl}/api/${userId}/chat`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: inputValue.trim(),
          conversation_id: conversationId || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update conversation ID if this is a new conversation
      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      // Add AI response to the conversation
      const aiMessage: Message = {
        id: `ai_${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        tool_calls: data.tool_calls || [],
        action: data.action,
        result: data.result,
      };

      setMessages(prev => [...prev, aiMessage]);

      // Show success toast for successful operations
      if (data.action && data.result && !data.response.toLowerCase().includes('error')) {
        if (data.action === 'complete_task') {
          toast.success('Task marked as completed!', {
            icon: <CheckCircle className="h-4 w-4" />,
          });
        } else if (data.action === 'add_task') {
          toast.success('Task added successfully!', {
            icon: <CheckCircle className="h-4 w-4" />,
          });
        } else if (data.action === 'delete_task') {
          toast.success('Task deleted successfully!', {
            icon: <CheckCircle className="h-4 w-4" />,
          });
        } else if (data.action === 'update_task') {
          toast.success('Task updated successfully!', {
            icon: <CheckCircle className="h-4 w-4" />,
          });
        }
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      toast.error(error.message || 'Failed to send message. Please try again.', {
        icon: <AlertTriangle className="h-4 w-4" />,
      });

      // Add error message to the conversation
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an issue: ${error.message || 'Unable to process your request'}`,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    switch(action) {
      case 'add':
        setInputValue('Add a task to buy groceries');
        break;
      case 'list':
        setInputValue('Show my tasks');
        break;
      case 'complete':
        setInputValue('Complete task #1');
        break;
      case 'update':
        setInputValue('Update task #2 priority to high');
        break;
      default:
        break;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto py-6 px-4 max-w-4xl">
        <div className="h-[calc(100vh-8rem)] flex flex-col">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-xl p-6">
            <div className="flex items-center gap-3">
              <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
                <Bot className="h-6 w-6" />
              </div>
              <div>
                <h3 className="flex items-center gap-2 text-xl font-semibold">
                  Todo AI Assistant
                </h3>
                <p className="text-blue-100 text-sm mt-1">
                  {conversationId
                    ? `Conversation: ${conversationId.substring(0, 8)}...`
                    : 'Natural language task management'}
                </p>
              </div>
            </div>
          </div>

          <div className="flex-1 flex flex-col bg-blue-50">
            <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
              <div className="space-y-6 max-w-full">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center py-12">
                    <div className="bg-gradient-to-r from-blue-100 to-blue-200 p-5 rounded-full mb-6">
                      <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-3 rounded-full">
                        <Bot className="h-10 w-10 text-white" />
                      </div>
                    </div>
                    <h3 className="text-2xl font-bold text-blue-800 mb-2">Welcome to Todo AI Chat</h3>
                    <p className="text-blue-600 max-w-md mb-8">
                      I can help you manage your tasks using natural language. Try asking me to add, list, update, or complete tasks.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-lg">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickAction('add')}
                        className="justify-start border-blue-200 hover:bg-blue-50 hover:border-blue-300 text-blue-700"
                      >
                        <Sparkles className="h-4 w-4 mr-2 text-blue-600" />
                        Add a task to buy groceries
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickAction('list')}
                        className="justify-start border-blue-200 hover:bg-blue-50 hover:border-blue-300 text-blue-700"
                      >
                        <ListIcon className="h-4 w-4 mr-2 text-blue-600" />
                        Show me my tasks
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickAction('complete')}
                        className="justify-start border-blue-200 hover:bg-blue-50 hover:border-blue-300 text-blue-700"
                      >
                        <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
                        Complete task #1
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickAction('update')}
                        className="justify-start border-blue-200 hover:bg-blue-50 hover:border-blue-300 text-blue-700"
                      >
                        <Lightbulb className="h-4 w-4 mr-2 text-blue-600" />
                        Update task priority
                      </Button>
                    </div>

                    <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100 max-w-lg">
                      <div className="flex items-start">
                        <Lightbulb className="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                        <div>
                          <h4 className="font-medium text-blue-800">Tip: For complete task</h4>
                          <p className="text-blue-600 text-sm mt-1">
                            When saying "Complete task #1", make sure to refer to an existing task number from your list.
                            You can say "Show my tasks" first to see the available tasks and their numbers.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col gap-6">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        {message.role === 'assistant' && (
                          <Avatar className="h-9 w-9 border border-blue-200 flex-shrink-0">
                            <AvatarFallback className="bg-gradient-to-r from-blue-100 to-blue-200 text-blue-600">
                              <Bot className="h-4 w-4" />
                            </AvatarFallback>
                          </Avatar>
                        )}

                        <div className={`max-w-[75%] flex flex-col ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                          <div
                            className={`p-4 rounded-2xl break-words ${
                              message.role === 'user'
                                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-br-none shadow-md'
                                : 'bg-blue-100 rounded-bl-none shadow-sm'
                            }`}
                          >
                            <p className="whitespace-pre-wrap break-words">{message.content}</p>

                            {/* Display tasks if action is list_tasks and result contains tasks */}
                            {message.action === 'list_tasks' && message.result?.tasks && message.result.tasks.length > 0 && (
                              <div className="mt-4 pt-4 border-t border-blue-200">
                                <p className="text-xs font-semibold text-blue-500 mb-3">Your Tasks:</p>
                                <div className="space-y-3">
                                  {message.result.tasks.map((task: any, index: number) => (
                                    <div
                                      key={task.id || index}
                                      className={`p-3 bg-blue-50 rounded-lg border ${
                                        task.status === 'completed'
                                          ? 'border-blue-300 bg-blue-100'
                                          : 'border-blue-200'
                                      }`}
                                    >
                                      <div className="flex items-start gap-3">
                                        <div className={`flex-shrink-0 w-5 h-5 rounded-full border flex items-center justify-center mt-0.5 ${
                                          task.status === 'completed'
                                            ? 'bg-blue-500 border-blue-500 text-white'
                                            : 'border-blue-300'
                                        }`}>
                                          {task.status === 'completed' && (
                                            <Check className="h-3 w-3" />
                                          )}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                          <div className="flex items-center gap-2">
                                            <span className="font-medium text-blue-800">{task.title}</span>
                                            {task.priority && (
                                              <Badge
                                                variant="secondary"
                                                className={`text-xs capitalize ${
                                                  task.priority === 'high' ? 'bg-red-100 text-red-800' :
                                                  task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                                  'bg-green-100 text-green-800'
                                                }`}
                                              >
                                                {task.priority}
                                              </Badge>
                                            )}
                                            {task.status === 'completed' && (
                                              <Badge variant="outline" className="text-xs border-blue-300 text-blue-700">
                                                Completed
                                              </Badge>
                                            )}
                                          </div>
                                          {task.description && (
                                            <p className="text-xs text-blue-600 mt-1">{task.description}</p>
                                          )}
                                          <p className="text-xs text-blue-500 mt-2">
                                            ID: {task.id?.substring(0, 8)}...
                                          </p>
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {message.action === 'complete_task' && message.result && (
                              <div className="mt-3 pt-3 border-t border-blue-200">
                                <div className="flex items-center text-blue-600">
                                  <CheckCircle className="h-4 w-4 mr-2" />
                                  <span className="text-sm font-medium">Task completed successfully!</span>
                                </div>
                                {message.result.title && (
                                  <p className="text-sm text-blue-600 mt-1">Completed: {message.result.title}</p>
                                )}
                              </div>
                            )}

                            {message.tool_calls && message.tool_calls.length > 0 && (
                              <div className="mt-3 pt-3 border-t border-blue-200">
                                <p className="text-xs text-blue-500 mb-2">Used tools:</p>
                                <div className="flex flex-wrap gap-1">
                                  {message.tool_calls.map((tool_call, index) => (
                                    <Badge
                                      key={index}
                                      variant="outline"
                                      className="text-xs capitalize"
                                    >
                                      {typeof tool_call === 'object' && tool_call.name
                                        ? tool_call.name.replace('_', ' ')
                                        : 'unknown tool'}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                          <p className="text-xs text-blue-500 mt-2 ml-2 self-end">
                            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>

                        {message.role === 'user' && (
                          <Avatar className="h-9 w-9 border border-blue-200 flex-shrink-0">
                            <AvatarFallback className="bg-blue-100 text-blue-600">
                              <User className="h-4 w-4" />
                            </AvatarFallback>
                          </Avatar>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </ScrollArea>

            <div className="p-6 pt-0">
              <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask me to manage your tasks (e.g., 'Add a task to buy groceries')..."
                  disabled={isLoading}
                  className="flex-1 h-12 rounded-xl border-blue-300 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:border-blue-500 shadow-sm"
                />
                <Button
                  type="submit"
                  disabled={isLoading || !inputValue.trim()}
                  className="h-12 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-md"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="mr-2 h-4 w-4" />
                      Send
                    </>
                  )}
                </Button>
              </form>

              <p className="text-xs text-blue-500 mt-3 text-center">
                Tip: Use task IDs when completing tasks (e.g., "Complete task with ID: abc123...")
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper component for the list icon since it's not in lucide-react
function ListIcon(props: any) {
  return (
    <svg
      {...props}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 6h16M4 10h16M4 14h16M4 18h16"
      />
    </svg>
  );
}