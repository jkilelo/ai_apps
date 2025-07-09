import React, { useState, useEffect } from 'react'
import { App } from '../types/app'
import { Logo } from './Logo'
import { ThemeToggle } from './ui/ThemeToggle'

interface SidebarProps {
  apps: App[]
  selectedApp: App | null
  onSelectApp: (app: App) => void
  theme?: 'light' | 'dark'
  onToggleTheme?: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ apps, selectedApp, onSelectApp, theme = 'dark', onToggleTheme }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [favorites, setFavorites] = useState<number[]>([])
  const [recentApps, setRecentApps] = useState<number[]>([])
  const [isSearchFocused, setIsSearchFocused] = useState(false)

  useEffect(() => {
    const savedFavorites = localStorage.getItem('appFavorites')
    const savedRecent = localStorage.getItem('recentApps')
    if (savedFavorites) setFavorites(JSON.parse(savedFavorites))
    if (savedRecent) setRecentApps(JSON.parse(savedRecent))
  }, [])

  const filteredApps = apps.filter(app =>
    app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    app.Description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const toggleFavorite = (appId: number) => {
    const newFavorites = favorites.includes(appId)
      ? favorites.filter(id => id !== appId)
      : [...favorites, appId]
    setFavorites(newFavorites)
    localStorage.setItem('appFavorites', JSON.stringify(newFavorites))
  }

  const handleAppSelect = (app: App) => {
    onSelectApp(app)
    const newRecent = [app.id, ...recentApps.filter(id => id !== app.id)].slice(0, 3)
    setRecentApps(newRecent)
    localStorage.setItem('recentApps', JSON.stringify(newRecent))
  }

  const favoriteApps = apps.filter(app => favorites.includes(app.id))
  const recentlyUsedApps = apps.filter(app => recentApps.includes(app.id))

  return (
    <aside className="fixed left-0 top-0 h-full w-80 flex flex-col glass-intense animate-slideInLeft">
      {/* Header */}
      <div className="p-6 border-b" style={{ borderColor: 'var(--border-primary)' }}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3 animate-fadeIn">
            <div className="relative">
              <Logo className="w-10 h-10 animate-float" />
              <div className="absolute inset-0 blur-xl opacity-50">
                <Logo className="w-10 h-10" />
              </div>
            </div>
            <h1 className="text-xl font-bold gradient-text">
              AI Apps Suite
            </h1>
          </div>
          <span className="badge badge-blue animate-pulse">
            Beta
          </span>
        </div>
        
        {/* Search Bar */}
        <div className={`relative transition-all duration-300 ${isSearchFocused ? 'transform scale-[1.02]' : ''}`}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setIsSearchFocused(true)}
            onBlur={() => setIsSearchFocused(false)}
            placeholder="Search apps..."
            className="input input-glass pl-10 pr-12"
          />
          <svg className="absolute left-3 top-3.5 w-4 h-4 pointer-events-none" style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <kbd className="absolute right-3 top-3 text-xs px-2 py-1 glass rounded-md">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Apps List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {/* Favorites Section */}
        {favoriteApps.length > 0 && (
          <div className="p-4 animate-slideUp">
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: 'var(--text-tertiary)' }}>
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              Favorites
            </h3>
            <div className="space-y-2">
              {favoriteApps.map((app, index) => (
                <div key={app.id} style={{ animationDelay: `${index * 50}ms` }} className="animate-slideInLeft">
                  <AppItem
                    app={app}
                    isSelected={selectedApp?.id === app.id}
                    isFavorite={true}
                    onSelect={() => handleAppSelect(app)}
                    onToggleFavorite={() => toggleFavorite(app.id)}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Section */}
        {recentlyUsedApps.length > 0 && filteredApps.length === apps.length && (
          <div className="p-4 animate-slideUp">
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: 'var(--text-tertiary)' }}>
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              Recent
            </h3>
            <div className="space-y-2">
              {recentlyUsedApps.map((app, index) => (
                <div key={app.id} style={{ animationDelay: `${index * 50}ms` }} className="animate-slideInLeft">
                  <AppItem
                    app={app}
                    isSelected={selectedApp?.id === app.id}
                    isFavorite={favorites.includes(app.id)}
                    onSelect={() => handleAppSelect(app)}
                    onToggleFavorite={() => toggleFavorite(app.id)}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* All Apps Section */}
        <div className="p-4 animate-slideUp">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: 'var(--text-tertiary)' }}>
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            All Apps
          </h3>
          <div className="space-y-2">
            {filteredApps.map((app, index) => (
              <div key={app.id} style={{ animationDelay: `${index * 30}ms` }} className="animate-slideInLeft">
                <AppItem
                  app={app}
                  isSelected={selectedApp?.id === app.id}
                  isFavorite={favorites.includes(app.id)}
                  onSelect={() => handleAppSelect(app)}
                  onToggleFavorite={() => toggleFavorite(app.id)}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t glass-subtle" style={{ borderColor: 'var(--border-primary)' }}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
              U
            </div>
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>User</p>
              <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Free Plan</p>
            </div>
          </div>
          <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            <svg className="w-4 h-4" style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
        
        <div className="flex items-center justify-between">
          <button className="btn btn-secondary flex-1 mr-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          {onToggleTheme && <ThemeToggle theme={theme} onToggle={onToggleTheme} />}
        </div>
      </div>
    </aside>
  )
}

interface AppItemProps {
  app: App
  isSelected: boolean
  isFavorite: boolean
  onSelect: () => void
  onToggleFavorite: () => void
}

const AppItem: React.FC<AppItemProps> = ({ app, isSelected, isFavorite, onSelect, onToggleFavorite }) => {
  const [isHovered, setIsHovered] = useState(false)
  
  // Get app color based on name or id
  const getAppColor = () => {
    const colors = [
      { bg: 'from-blue-500 to-blue-600', shadow: 'rgba(59, 130, 246, 0.5)' },
      { bg: 'from-purple-500 to-purple-600', shadow: 'rgba(147, 51, 234, 0.5)' },
      { bg: 'from-green-500 to-green-600', shadow: 'rgba(34, 197, 94, 0.5)' },
      { bg: 'from-orange-500 to-orange-600', shadow: 'rgba(251, 146, 60, 0.5)' },
      { bg: 'from-pink-500 to-pink-600', shadow: 'rgba(236, 72, 153, 0.5)' },
      { bg: 'from-indigo-500 to-indigo-600', shadow: 'rgba(99, 102, 241, 0.5)' },
    ]
    return colors[app.id % colors.length]
  }
  
  const appColor = getAppColor()
  
  return (
    <div
      className={`group relative rounded-xl cursor-pointer transition-all duration-300 ${
        isSelected ? 'card-interactive' : ''
      }`}
      style={{
        background: isSelected ? 'var(--color-blue)' : isHovered ? 'var(--glass-bg)' : 'transparent',
        transform: isSelected ? 'scale(1.02)' : isHovered ? 'scale(1.01)' : 'scale(1)',
        boxShadow: isSelected ? `0 8px 20px ${appColor.shadow}` : 'none'
      }}
      onClick={onSelect}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-center gap-3 p-3">
        {/* App Icon */}
        <div className={`relative w-11 h-11 rounded-xl bg-gradient-to-br ${appColor.bg} flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
          isSelected || isHovered ? 'shadow-lg' : ''
        }`}>
          <span className="text-white font-bold text-lg">
            {app.name.substring(0, 2).toUpperCase()}
          </span>
          {isSelected && (
            <div className="absolute inset-0 rounded-xl bg-white opacity-20 animate-pulse"></div>
          )}
        </div>
        
        {/* App Info */}
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold truncate" style={{ 
            color: isSelected ? 'white' : 'var(--text-primary)' 
          }}>
            {app.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </h4>
          <p className="text-xs truncate flex items-center gap-1" style={{ 
            color: isSelected ? 'rgba(255,255,255,0.8)' : 'var(--text-tertiary)' 
          }}>
            {app.sub_apps ? (
              <>
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                </svg>
                {app.sub_apps.length} modules
              </>
            ) : (
              <>
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                </svg>
                {app.steps?.length || 0} steps
              </>
            )}
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1">
          {isSelected && (
            <div className="w-2 h-2 rounded-full bg-white animate-pulse mr-2"></div>
          )}
          
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggleFavorite()
            }}
            className={`p-1.5 rounded-lg transition-all duration-200 ${
              isFavorite ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
            }`}
            style={{ 
              color: isFavorite ? '#FFCC00' : isSelected ? 'white' : 'var(--text-tertiary)' 
            }}
          >
            <svg className="w-4 h-4" fill={isFavorite ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}