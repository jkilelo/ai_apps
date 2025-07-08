import React from 'react'

interface BreadcrumbItem {
  label: string
  onClick?: () => void
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  return (
    <nav className="flex items-center gap-2 text-sm">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <svg className="w-4 h-4 animate-fadeIn" style={{ color: 'var(--text-tertiary)', animationDelay: `${index * 50}ms` }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
          {item.onClick ? (
            <button
              onClick={item.onClick}
              className="px-3 py-1 rounded-lg transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 animate-fadeIn"
              style={{ 
                color: 'var(--text-secondary)',
                animationDelay: `${index * 50}ms`
              }}
            >
              {item.label}
            </button>
          ) : (
            <span className="font-semibold animate-fadeIn" style={{ 
              color: 'var(--text-primary)',
              animationDelay: `${index * 50}ms`
            }}>{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  )
}