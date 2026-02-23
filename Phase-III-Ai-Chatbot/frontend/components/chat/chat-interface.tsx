/**
 * User-friendly chat interface component with proper styling.
 * Provides a clean, responsive UI for interacting with the AI chatbot.
 */

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Bot, SendHorizontal, User, RotateCcw, Sparkles, MessageCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { LoadingState, ErrorState, SuccessState, ChatStates } from './loading-states';
import { apiClient } from '@/lib/api';
import { getCurrentUserId } from '@/lib/auth-utils';

interface ChatInterfaceProps {
  userId?: string;
  conversationId?: string;
  onConversationChange?: (conversationId: string) => void;
  onTaskCreated?: () => void; // Callback to refresh tasks when created via chat
  className?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tool_calls?: Array<{
    name: string;
    parameters: Record<string, any>;
    result: any;
  }>;
  action?: string;
  result?: any;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  userId,
  conversationId,
  onConversationChange,
  onTaskCreated,
  className
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(conversationId || null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    // Add user message to the conversation
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Call the real chat API
      const response = await callChatAPI(inputValue.trim());

      setMessages(prev => [...prev, response]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');

      // Add error message to the conversation
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an issue: ${err instanceof Error ? err.message : 'Unable to process your request'}`,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Real chat API call
  const callChatAPI = async (message: string): Promise<Message> => {
    try {
      // Get the current user ID
      const userId = await getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Use the correct endpoint format
      const response = await apiClient.post(`/${userId}/chat`, {
        message: message,
        conversation_id: currentConversationId || undefined
      });

      // Update conversation ID if it's a new conversation
      if (!currentConversationId && response.conversation_id) {
        setCurrentConversationId(response.conversation_id);
        onConversationChange?.(response.conversation_id);
      }

      // If a task was created via chat, notify the parent component to refresh tasks
      if (response.action === 'add_task' && response.result && onTaskCreated) {
        onTaskCreated();
      }

      return {
        id: `ai_${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        tool_calls: response.tool_calls || [],
        action: response.action,
        result: response.result
      };
    } catch (error) {
      console.error('Chat API error:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to get response from AI assistant');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any); // Type assertion to treat as form event
    }
  };

  return (
    <Card className={cn('w-full h-[500px] sm:h-[600px] flex flex-col', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageCircle className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
            <CardTitle className="text-base sm:text-lg">Todo AI Assistant</CardTitle>
          </div>

          {currentConversationId && (
            <Badge variant="secondary" className="text-xs hidden sm:inline-flex">
              Conv: {currentConversationId.substring(0, 8)}...
            </Badge>
          )}
        </div>

        <p className="text-xs sm:text-sm text-muted-foreground">
          Natural language task management with AI assistance
        </p>
      </CardHeader>

      <Separator />

      <CardContent className="flex-1 flex flex-col p-4">
        <ChatStates
          loading={isLoading}
          error={error}
          loadingMessage="AI is processing your request..."
        >
          <ScrollArea className="flex-1 w-full pb-4">
            <div className="space-y-6">
              {messages.length === 0 && !isLoading && (
                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                  <div className="bg-primary/10 p-4 rounded-full mb-4">
                    <Bot className="h-10 w-10 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Welcome to Todo AI Chat</h3>
                  <p className="text-muted-foreground max-w-md">
                    I can help you manage your tasks using natural language. Try asking me to add, list, update, or complete tasks.
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 mt-6 w-full max-w-lg">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setInputValue("Add a task to buy groceries")}
                      className="justify-start text-xs sm:text-sm"
                    >
                      <Sparkles className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2 flex-shrink-0" />
                      <span className="truncate">Add a task to buy groceries</span>
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setInputValue("Show me my tasks")}
                      className="justify-start text-xs sm:text-sm"
                    >
                      <Sparkles className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2 flex-shrink-0" />
                      <span className="truncate">Show me my tasks</span>
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setInputValue("Complete task #1")}
                      className="justify-start text-xs sm:text-sm"
                    >
                      <Sparkles className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2 flex-shrink-0" />
                      <span className="truncate">Complete task #1</span>
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setInputValue("Update task #2 priority to high")}
                      className="justify-start text-xs sm:text-sm"
                    >
                      <Sparkles className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2 flex-shrink-0" />
                      <span className="truncate">Update task priority</span>
                    </Button>
                  </div>
                </div>
              )}

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <Avatar className="h-8 w-8 border flex-shrink-0">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        <Bot className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}

                  <div className={`max-w-[85%] sm:max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                    <div
                      className={cn(
                        'p-3 sm:p-4 rounded-lg',
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground rounded-br-none'
                          : 'bg-muted rounded-bl-none'
                      )}
                    >
                      <p className="whitespace-pre-wrap text-sm sm:text-base">{message.content}</p>

                      {message.tool_calls && message.tool_calls.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-t-muted-foreground/20">
                          <p className="text-xs text-muted-foreground mb-2">Used tools:</p>
                          <div className="flex flex-wrap gap-2">
                            {message.tool_calls.map((tool_call, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {typeof tool_call === 'object' && tool_call.name
                                  ? tool_call.name
                                  : 'unknown_tool'}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 ml-2">
                      {new Date(message.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>

                  {message.role === 'user' && (
                    <Avatar className="h-8 w-8 border flex-shrink-0">
                      <AvatarFallback className="bg-secondary text-secondary-foreground">
                        <User className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex items-center gap-3 justify-start">
                  <Avatar className="h-8 w-8 border">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      <Bot className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-muted rounded-lg rounded-bl-none p-4">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="h-2 w-2 bg-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="h-2 w-2 bg-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </ChatStates>
      </CardContent>

      <Separator />

      <CardFooter className="p-3 sm:p-4 pt-0">
        <form onSubmit={handleSubmit} className="flex w-full gap-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me to manage your tasks..."
            className="flex-1 min-h-[50px] sm:min-h-[60px] max-h-32 resize-none border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 rounded-md"
            disabled={isLoading}
            rows={1}
          />

          <Button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="h-[50px] sm:h-[60px] flex-shrink-0 px-2 sm:px-4"
          >
            <SendHorizontal className="h-4 w-4" />
            <span className="sr-only">Send</span>
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
};

export default ChatInterface;