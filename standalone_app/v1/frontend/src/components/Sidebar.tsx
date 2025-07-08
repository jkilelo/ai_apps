import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Brain, 
  Globe, 
  Database, 
  ChevronLeft,
  ChevronRight,
  Sparkles
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/llm-query', icon: Brain, label: 'LLM Query' },
    { path: '/web-automation', icon: Globe, label: 'Web Automation' },
    { path: '/data-profiling', icon: Database, label: 'Data Profiling' },
  ];

  return (
    <aside className={`fixed left-0 top-0 h-full bg-white shadow-xl transition-all duration-300 z-50 ${
      isOpen ? 'w-64' : 'w-20'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className={`flex items-center gap-3 transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0'
        }`}>
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-gray-900">AI Apps</h1>
            <p className="text-xs text-gray-500">Standalone v1</p>
          </div>
        </div>
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          {isOpen ? (
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-600" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `sidebar-item ${isActive ? 'sidebar-item-active' : ''}`
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            <span className={`transition-opacity duration-300 ${
              isOpen ? 'opacity-100' : 'opacity-0 w-0'
            }`}>
              {item.label}
            </span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className={`absolute bottom-0 left-0 right-0 p-4 border-t transition-opacity duration-300 ${
        isOpen ? 'opacity-100' : 'opacity-0'
      }`}>
        <div className="text-xs text-gray-500">
          <p>Version 1.0.0</p>
          <p className="mt-1">© 2024 AI Apps</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;