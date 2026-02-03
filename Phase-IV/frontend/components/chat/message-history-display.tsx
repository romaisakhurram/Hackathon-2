/**
 * Message history display component for the chat interface.
 * Displays conversation messages in chronological order with proper styling.
 */

import React from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { Bot, User } from 'lucide-react';

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
}

interface MessageHistoryDisplayProps {
  messages: Message[];
  isLoading?: boolean;
}

const MessageHistoryDisplay: React.FC<MessageHistoryDisplayProps> = ({
  messages,
  isLoading = false
}) => {
  return (
    <ScrollArea className="flex-1 mb-4 h-full">
      <div className="space-y-4">
        {messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <Bot className="h-12 w-12 mb-3" />
            <h3 className="text-lg font-medium">Welcome to the Todo AI Chat</h3>
            <p className="text-sm">
              Ask me to add, list, update, or manage your tasks using natural language.
            </p>
            <p className="text-xs mt-2">
              Try: "Add a task to buy groceries", "Show my tasks", "Complete task #1"
            </p>
          </div>
        ) : (
          messages.map((message) => (
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

              <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                <div
                  className={cn(
                    'p-4 rounded-lg',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-br-none'
                      : 'bg-muted rounded-bl-none'
                  )}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>

                  {message.tool_calls && message.tool_calls.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-t-muted-foreground/20">
                      <p className="text-xs text-muted-foreground mb-1">Used tools:</p>
                      <div className="flex flex-wrap gap-1">
                        {message.tool_calls.map((tool_call, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-secondary text-secondary-foreground"
                          >
                            {typeof tool_call === 'object' && tool_call.name
                              ? tool_call.name
                              : 'unknown_tool'}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-1 ml-2">
                  {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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
          ))
        )}

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
      </div>
    </ScrollArea>
  );
};

export default MessageHistoryDisplay;