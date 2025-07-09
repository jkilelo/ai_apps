import { useEffect } from 'react'

interface ShortcutHandlers {
  onSearch?: () => void
  onNavigateUp?: () => void
  onNavigateDown?: () => void
  onSelect?: () => void
  onBack?: () => void
}

export const useKeyboardShortcuts = ({
  onSearch,
  onNavigateUp,
  onNavigateDown,
  onSelect,
  onBack
}: ShortcutHandlers) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K for search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        onSearch?.()
      }
      
      // Arrow navigation
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        onNavigateUp?.()
      }
      
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        onNavigateDown?.()
      }
      
      // Enter to select
      if (e.key === 'Enter') {
        onSelect?.()
      }
      
      // Escape to go back
      if (e.key === 'Escape') {
        onBack?.()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onSearch, onNavigateUp, onNavigateDown, onSelect, onBack])
}