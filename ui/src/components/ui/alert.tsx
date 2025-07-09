import React from 'react';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive';
  children: React.ReactNode;
}

export const Alert: React.FC<AlertProps> = ({ 
  variant = 'default', 
  className = '', 
  children, 
  ...props 
}) => {
  const variantClasses = {
    default: 'bg-gray-100 border-gray-300 dark:bg-gray-800 dark:border-gray-700',
    destructive: 'bg-red-50 border-red-500 text-red-900 dark:bg-red-900/10 dark:border-red-900 dark:text-red-50'
  };
  
  return (
    <div
      className={`relative w-full rounded-lg border p-4 ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const AlertTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className = '' 
}) => {
  return (
    <h5 className={`mb-1 font-medium leading-none tracking-tight ${className}`}>
      {children}
    </h5>
  );
};

export const AlertDescription: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className = '' 
}) => {
  return (
    <div className={`text-sm ${className}`}>
      {children}
    </div>
  );
};