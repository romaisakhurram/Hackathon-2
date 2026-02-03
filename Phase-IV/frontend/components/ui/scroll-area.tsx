import * as React from 'react';

import { cn } from '@/lib/utils';

interface ScrollAreaProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'vertical' | 'horizontal';
}

const ScrollArea = React.forwardRef<HTMLDivElement, ScrollAreaProps>(
  ({ className, children, orientation = 'vertical', ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'relative overflow-hidden',
        className
      )}
      {...props}
    >
      <div className="h-full w-full overflow-auto">
        {children}
      </div>
      <ScrollBar orientation={orientation} />
    </div>
  )
);
ScrollArea.displayName = 'ScrollArea';

interface ScrollBarProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'vertical' | 'horizontal';
}

const ScrollBar = React.forwardRef<HTMLDivElement, ScrollBarProps>(
  ({ orientation = 'vertical', className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'absolute right-0 top-0 z-10 h-full w-2.5 touch-none select-none transition-colors',
        orientation === 'horizontal' && 'left-0 h-2.5 w-full',
        className
      )}
      {...props}
    >
      <div className="h-20 w-full min-h-10 bg-border rounded-full" />
    </div>
  )
);
ScrollBar.displayName = 'ScrollBar';

export { ScrollArea, ScrollBar };