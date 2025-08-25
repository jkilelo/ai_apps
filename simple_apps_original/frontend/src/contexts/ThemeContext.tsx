import React, { createContext, useContext, useState } from 'react';

export type ViewMode = 'developer' | 'executive';

interface ThemeContextType {
    viewMode: ViewMode;
    setViewMode: (mode: ViewMode) => void;
    toggleViewMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [viewMode, setViewMode] = useState<ViewMode>('developer');

    const toggleViewMode = () => {
        setViewMode(prev => prev === 'developer' ? 'executive' : 'developer');
    };

    return (
        <ThemeContext.Provider value={{ viewMode, setViewMode, toggleViewMode }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};
