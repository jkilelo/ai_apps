import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChartBarIcon, ComputerDesktopIcon, Bars3Icon, XMarkIcon, HomeIcon } from '@heroicons/react/24/outline';

export function Navigation() {
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();

    const navigation = [
        { name: 'Home', href: '/', icon: HomeIcon },
        { name: 'Data Profiling', href: '/data-profiling', icon: ChartBarIcon },
        { name: 'Web Automation', href: '/web-automation', icon: ComputerDesktopIcon },
    ];

    const isActive = (href: string) => location.pathname === href;

    return (
        <nav className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-[100]">
            <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6">
                <div className="flex justify-between h-12 sm:h-14">
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-2">
                            <div className="h-7 w-7 sm:h-8 sm:w-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-md flex items-center justify-center">
                                <ChartBarIcon className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
                            </div>
                            <span className="text-base sm:text-lg font-semibold text-slate-900 hidden sm:block">
                                AI Platform
                            </span>
                        </Link>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-1">
                        {navigation.map((item) => {
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${
                                        isActive(item.href)
                                            ? 'text-white bg-blue-600'
                                            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                                    }`}
                                >
                                    <Icon className="h-4 w-4" />
                                    <span>{item.name}</span>
                                </Link>
                            );
                        })}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="text-slate-600 hover:text-slate-900 p-2"
                            aria-label="Toggle menu"
                        >
                            {isOpen ? (
                                <XMarkIcon className="h-5 w-5" />
                            ) : (
                                <Bars3Icon className="h-5 w-5" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile menu */}
            {isOpen && (
                <div className="md:hidden border-t border-slate-200">
                    <div className="px-2 py-2 space-y-1 bg-white">
                        {navigation.map((item) => {
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    onClick={() => setIsOpen(false)}
                                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                        isActive(item.href)
                                            ? 'text-white bg-blue-600'
                                            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                                    }`}
                                >
                                    <Icon className="h-4 w-4" />
                                    <span>{item.name}</span>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            )}
        </nav>
    );
}