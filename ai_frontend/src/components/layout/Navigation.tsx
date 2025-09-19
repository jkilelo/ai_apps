import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Monitor, BarChart3, Home } from 'lucide-react';

export function Navigation() {
    const location = useLocation();

    const isActive = (path: string) => location.pathname === path;

    return (
        <nav className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-2">
                            <Monitor className="h-8 w-8 text-blue-600" />
                            <span className="text-xl font-bold text-slate-900 dark:text-white">
                                AI Testing Apps
                            </span>
                        </Link>
                    </div>

                    <div className="flex items-center space-x-8">
                        <Link
                            to="/"
                            className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                isActive('/')
                                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100'
                                    : 'text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white'
                            }`}
                        >
                            <Home className="h-4 w-4" />
                            <span>Home</span>
                        </Link>

                        <Link
                            to="/web-automation"
                            className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                isActive('/web-automation')
                                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100'
                                    : 'text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white'
                            }`}
                        >
                            <Monitor className="h-4 w-4" />
                            <span>Web Automation</span>
                        </Link>

                        <Link
                            to="/data-profiling"
                            className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                isActive('/data-profiling')
                                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100'
                                    : 'text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white'
                            }`}
                        >
                            <BarChart3 className="h-4 w-4" />
                            <span>Data Profiling</span>
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
}