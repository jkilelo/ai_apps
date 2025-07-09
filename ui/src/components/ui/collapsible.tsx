import React, { useState, createContext, useContext } from 'react';

interface CollapsibleContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const CollapsibleContext = createContext<CollapsibleContextType | undefined>(undefined);

export const Collapsible: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className = '' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <CollapsibleContext.Provider value={{ isOpen, setIsOpen }}>
      <div className={className}>
        {children}
      </div>
    </CollapsibleContext.Provider>
  );
};

export const CollapsibleTrigger: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className = '' 
}) => {
  const context = useContext(CollapsibleContext);
  if (!context) throw new Error('CollapsibleTrigger must be used within Collapsible');
  
  return (
    <button
      type="button"
      className={className}
      onClick={() => context.setIsOpen(!context.isOpen)}
    >
      {children}
    </button>
  );
};

export const CollapsibleContent: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className = '' 
}) => {
  const context = useContext(CollapsibleContext);
  if (!context) throw new Error('CollapsibleContent must be used within Collapsible');
  
  if (!context.isOpen) return null;
  
  return (
    <div className={className}>
      {children}
    </div>
  );
};