import React from 'react'
import { Tooltip } from './Tooltip'

interface ThemeToggleProps {
  theme: 'light' | 'dark'
  onToggle: () => void
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ theme, onToggle }) => {
  return (
    <Tooltip content={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
      <button
        onClick={onToggle}
        className="relative w-14 h-8 rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        style={{ 
          background: theme === 'dark' ? 'var(--color-bg-tertiary)' : '#255BE3'
        }}
        aria-label="Toggle theme"
      >
        <div
          className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transform transition-transform duration-300 ${
            theme === 'dark' ? 'translate-x-1' : 'translate-x-7'
          }`}
        >
          <div className="flex items-center justify-center h-full">
            {theme === 'dark' ? (
              <svg className="w-4 h-4 text-neutral-800" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            ) : (
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            )}
          </div>
        </div>
      </button>
    </Tooltip>
  )
}