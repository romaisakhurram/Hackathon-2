/**
 * Loading states and error handling components for the chat interface.
 * Provides visual feedback during API requests and error scenarios.
 */

import React from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, CheckCircle2, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingStateProps {
  message?: string;
  className?: string;
}

interface ErrorStateProps {
  error: string | Error;
  onRetry?: () => void;
  className?: string;
}

interface SuccessStateProps {
  message: string;
  className?: string;
}

/**
 * Loading state component with spinner animation
 */
const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Processing your request...',
  className
}) => {
  return (
    <div className={cn('flex items-center justify-center p-4', className)}>
      <div className="flex flex-col items-center gap-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
    </div>
  );
};

/**
 * Error state component with retry option
 */
const ErrorState: React.FC<ErrorStateProps> = ({
  error,
  onRetry,
  className
}) => {
  const errorMessage = error instanceof Error ? error.message : String(error);

  return (
    <Alert variant="destructive" className={cn('mb-4', className)}>
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>
        {errorMessage}

        {onRetry && (
          <div className="mt-3">
            <button
              onClick={onRetry}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded hover:bg-destructive/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-destructive"
            >
              Retry
            </button>
          </div>
        )}
      </AlertDescription>
    </Alert>
  );
};

/**
 * Success state component with checkmark icon
 */
const SuccessState: React.FC<SuccessStateProps> = ({
  message,
  className
}) => {
  return (
    <Alert className={cn('mb-4', className)}>
      <CheckCircle2 className="h-4 w-4 text-green-600" />
      <AlertTitle>Success</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
};

/**
 * Informational state component
 */
const InfoState: React.FC<{ message: string; className?: string }> = ({
  message,
  className
}) => {
  return (
    <Alert className={cn('mb-4', className)}>
      <Info className="h-4 w-4 text-blue-600" />
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
};

/**
 * Combined loading/error/success states for chat operations
 */
interface ChatStatesProps {
  loading?: boolean;
  loadingMessage?: string;
  error?: string | Error | null;
  successMessage?: string;
  onRetry?: () => void;
  children?: React.ReactNode;
}

const ChatStates: React.FC<ChatStatesProps> = ({
  loading,
  loadingMessage,
  error,
  successMessage,
  onRetry,
  children
}) => {
  if (loading) {
    return <LoadingState message={loadingMessage} />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={onRetry} />;
  }

  if (successMessage) {
    return <SuccessState message={successMessage} />;
  }

  return <>{children}</>;
};

export { LoadingState, ErrorState, SuccessState, InfoState, ChatStates };