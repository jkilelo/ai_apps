import React from 'react'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export const EmptyState: React.FC<EmptyStateProps> = ({ 
  icon, 
  title, 
  description, 
  action 
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 animate-fade-in">
      {icon || (
        <div className="w-24 h-24 mb-6 rounded-full bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center">
          <svg className="w-12 h-12" style={{ color: 'var(--color-text-muted)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        </div>
      )}
      
      <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>{title}</h3>
      
      {description && (
        <p className="text-center max-w-sm mb-6" style={{ color: 'var(--color-text-secondary)' }}>{description}</p>
      )}
      
      {action && (
        <button
          onClick={action.onClick}
          className="btn btn-primary transform hover:scale-105 hover:shadow-lg hover:shadow-primary-500/20"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}