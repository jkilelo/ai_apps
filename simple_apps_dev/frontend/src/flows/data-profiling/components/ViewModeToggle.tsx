import React from 'react';
import { motion } from 'framer-motion';
import { Code, Presentation, Eye } from 'lucide-react';
import { useTheme } from '../../../contexts/ThemeContext';

export const ViewModeToggle: React.FC = () => {
    const { viewMode, toggleViewMode } = useTheme();

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="fixed top-6 right-6 z-50"
        >
            <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl rounded-2xl border border-white/20 dark:border-slate-700/30 shadow-2xl p-1 flex items-center space-x-1">
                <motion.button
                    onClick={toggleViewMode}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`
                        flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium text-sm
                        ${viewMode === 'developer'
                            ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/25'
                            : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50'
                        }
                    `}
                >
                    <Code className="h-4 w-4" />
                    <span>Developer</span>
                </motion.button>

                <motion.button
                    onClick={toggleViewMode}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`
                        flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium text-sm
                        ${viewMode === 'executive'
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25'
                            : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50'
                        }
                    `}
                >
                    <Presentation className="h-4 w-4" />
                    <span>Executive</span>
                </motion.button>
            </div>

            {/* View Mode Indicator */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-2 text-center"
            >
                <div className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm rounded-lg px-3 py-1 border border-white/20 dark:border-slate-700/30">
                    <div className="flex items-center justify-center space-x-2 text-xs text-slate-600 dark:text-slate-400">
                        <Eye className="h-3 w-3" />
                        <span>
                            {viewMode === 'developer' ? 'Technical View' : 'Business View'}
                        </span>
                    </div>
                </div>
            </motion.div>
        </motion.div>
    );
};
