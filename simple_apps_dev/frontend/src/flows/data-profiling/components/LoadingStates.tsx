import React from 'react';
import { motion } from 'framer-motion';

interface SkeletonLoaderProps {
    lines?: number;
    showCode?: boolean;
    showHeader?: boolean;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
    lines = 4,
    showCode = false,
    showHeader = true
}) => {
    return (
        <div className="space-y-4 animate-pulse">
            {showHeader && (
                <div className="space-y-3">
                    <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded-lg w-1/3"></div>
                    <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-2/3"></div>
                </div>
            )}

            {showCode ? (
                <div className="bg-slate-100 dark:bg-slate-800 rounded-xl p-4 space-y-2">
                    <div className="flex items-center space-x-2 mb-3">
                        <div className="w-3 h-3 bg-red-300 rounded-full"></div>
                        <div className="w-3 h-3 bg-yellow-300 rounded-full"></div>
                        <div className="w-3 h-3 bg-green-300 rounded-full"></div>
                        <div className="h-3 bg-slate-300 dark:bg-slate-600 rounded w-24 ml-2"></div>
                    </div>
                    {Array.from({ length: lines }).map((_, i) => (
                        <div
                            key={i}
                            className={`h-4 bg-slate-200 dark:bg-slate-700 rounded ${i % 3 === 0 ? 'w-full' : i % 3 === 1 ? 'w-5/6' : 'w-4/5'
                                }`}
                        />
                    ))}
                </div>
            ) : (
                <div className="space-y-2">
                    {Array.from({ length: lines }).map((_, i) => (
                        <div
                            key={i}
                            className={`h-4 bg-slate-200 dark:bg-slate-700 rounded ${i === lines - 1 ? 'w-2/3' : 'w-full'
                                }`}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export const CardSkeleton: React.FC = () => (
    <div className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-xl rounded-3xl border border-white/20 dark:border-slate-700/30 shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-slate-100/10 to-slate-200/10 border-b border-slate-200/20 dark:border-slate-700/20 p-6">
            <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-slate-300 dark:bg-slate-600 rounded"></div>
                <div className="h-6 bg-slate-300 dark:bg-slate-600 rounded w-48"></div>
            </div>
        </div>
        <div className="p-6">
            <SkeletonLoader showCode lines={6} />
        </div>
    </div>
);

// Enhanced loading state with pulsing animation
export const StepLoadingIndicator: React.FC<{ stepTitle: string }> = ({ stepTitle }) => (
    <div className="flex items-center justify-center py-20">
        <div className="text-center">
            <motion.div
                className="relative inline-block"
                animate={{
                    scale: [1, 1.1, 1],
                    rotate: [0, 180, 360]
                }}
                transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
            >
                <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full"></div>
                <div className="absolute inset-2 border-2 border-purple-200 border-b-purple-500 rounded-full animate-spin"></div>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-6"
            >
                <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    Processing {stepTitle}
                </h3>
                <div className="flex items-center justify-center space-x-1">
                    <motion.div
                        animate={{ opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                        className="w-2 h-2 bg-indigo-500 rounded-full"
                    />
                    <motion.div
                        animate={{ opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                        className="w-2 h-2 bg-indigo-500 rounded-full"
                    />
                    <motion.div
                        animate={{ opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                        className="w-2 h-2 bg-indigo-500 rounded-full"
                    />
                </div>
            </motion.div>
        </div>
    </div>
);
