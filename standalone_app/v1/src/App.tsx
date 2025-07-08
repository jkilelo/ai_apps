import React, { useState, useEffect, useRef } from 'react'
import { Sidebar } from './components/Sidebar'
import { MainPanel } from './components/MainPanel'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import { useTheme } from './hooks/useTheme'
import { App as AppType } from './types/app'
import appsData from '../apps/apps_map.json'

function App() {
  const [apps, setApps] = useState<AppType[]>([])
  const [selectedApp, setSelectedApp] = useState<AppType | null>(null)
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    setApps(appsData as AppType[])
  }, [])

  useKeyboardShortcuts({
    onSearch: () => {
      setIsSearchOpen(true)
      setTimeout(() => searchInputRef.current?.focus(), 100)
    },
    onBack: () => {
      if (isSearchOpen) {
        setIsSearchOpen(false)
      }
    }
  })

  return (
    <div className="h-screen overflow-hidden" style={{ background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}>
      <Sidebar
        apps={apps}
        selectedApp={selectedApp}
        onSelectApp={setSelectedApp}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
      
      <MainPanel selectedApp={selectedApp} />
      
      {/* Command Palette */}
      {isSearchOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-32">
          <div 
            className="absolute inset-0 backdrop-blur-sm" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
            onClick={() => setIsSearchOpen(false)}
          />
          <div className="relative w-full max-w-2xl rounded-xl shadow-2xl overflow-hidden animate-scale-in card-elevated">
            <div className="flex items-center px-4 py-3 border-b" style={{ borderColor: 'var(--color-border-primary)' }}>
              <svg className="w-5 h-5 text-primary-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search apps, commands, or actions..."
                className="flex-1 bg-transparent focus:outline-none" style={{ color: 'var(--color-text-primary)' }}
              />
              <kbd className="text-xs px-1.5 py-0.5 rounded" style={{ color: 'var(--color-text-muted)', background: 'var(--color-bg-tertiary)' }}>
                ESC
              </kbd>
            </div>
            <div className="p-2 max-h-96 overflow-y-auto">
              <div className="text-xs px-3 py-2" style={{ color: 'var(--color-text-tertiary)' }}>Quick Actions</div>
              {apps.map(app => (
                <button
                  key={app.id}
                  onClick={() => {
                    setSelectedApp(app)
                    setIsSearchOpen(false)
                  }}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors duration-150 hover:bg-opacity-50"
                  style={{ 
                    ':hover': { backgroundColor: 'var(--color-bg-tertiary)' }
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-medium" style={{ background: 'var(--color-bg-tertiary)' }}>
                    {app.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 text-left">
                    <div className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                      {app.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </div>
                    <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{app.Description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App