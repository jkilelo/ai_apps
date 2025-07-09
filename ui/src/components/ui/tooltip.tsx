import React, { useState } from 'react';

interface TooltipProps {
  children: React.ReactNode;
}

interface TooltipContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const TooltipContext = React.createContext<TooltipContextType | undefined>(undefined);

export const TooltipProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};

export const Tooltip: React.FC<TooltipProps> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <TooltipContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="relative inline-block">
        {children}
      </div>
    </TooltipContext.Provider>
  );
};

export const TooltipTrigger: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const context = React.useContext(TooltipContext);
  if (!context) throw new Error('TooltipTrigger must be used within Tooltip');
  
  return (
    <div
      onMouseEnter={() => context.setIsOpen(true)}
      onMouseLeave={() => context.setIsOpen(false)}
    >
      {children}
    </div>
  );
};

export const TooltipContent: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className = '' 
}) => {
  const context = React.useContext(TooltipContext);
  if (!context) throw new Error('TooltipContent must be used within Tooltip');
  
  if (!context.isOpen) return null;
  
  return (
    <div className={`absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs bg-gray-900 text-white rounded whitespace-nowrap ${className}`}>
      {children}
      <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px">
        <div className="border-4 border-transparent border-t-gray-900" />
      </div>
    </div>
  );
};