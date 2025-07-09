import React from 'react';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning';
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ 
  variant = 'default', 
  className = '', 
  children, 
  ...props 
}) => {
  const variantClasses = {
    default: 'bg-gray-900 text-white dark:bg-gray-50 dark:text-gray-900',
    secondary: 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100',
    destructive: 'bg-red-500 text-white',
    outline: 'border border-gray-300 dark:border-gray-700',
    success: 'bg-green-500 text-white',
    warning: 'bg-yellow-500 text-white'
  };
  
  return (
    <div
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};