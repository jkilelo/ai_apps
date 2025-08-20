import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Circle, Clock } from 'lucide-react';

interface ProgressIndicatorProps {
    currentStep: number;
    totalSteps: number;
    completedSteps: string[];
    estimatedTimeRemaining?: number;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
    currentStep,
    totalSteps,
    completedSteps,
    estimatedTimeRemaining
}) => {
    const progressPercentage = (currentStep / (totalSteps - 1)) * 100;

    return (
        <div className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-xl border-b border-white/20 dark:border-slate-700/30 p-4">
            {/* Progress Bar */}
            <div className="relative">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        Progress
                    </span>
                    <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                        <span>{currentStep + 1} of {totalSteps}</span>
                        {estimatedTimeRemaining && (
                            <>
                                <span>•</span>
                                <div className="flex items-center space-x-1">
                                    <Clock className="h-3 w-3" />
                                    <span>~{estimatedTimeRemaining}min</span>
                                </div>
                            </>
                        )}
                    </div>
                </div>

                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                    <motion.div
                        className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${progressPercentage}%` }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                    />
                </div>

                <div className="flex justify-between mt-2">
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                        {Math.round(progressPercentage)}% Complete
                    </span>
                    <span className="text-xs text-emerald-600 dark:text-emerald-400">
                        {completedSteps.length} steps completed
                    </span>
                </div>
            </div>
        </div>
    );
};

// Enhanced Step Indicator with mini progress
export const StepProgressDots: React.FC<{
    steps: any[];
    currentStep: number;
    completedSteps: string[];
}> = ({ steps, currentStep, completedSteps }) => {
    return (
        <div className="flex items-center space-x-2 py-2">
            {steps.map((step, index) => {
                const isCompleted = completedSteps.includes(step.id);
                const isCurrent = currentStep === index;
                const isUpcoming = index > currentStep;

                return (
                    <motion.div
                        key={step.id}
                        className="relative"
                        whileHover={{ scale: 1.1 }}
                        title={step.title}
                    >
                        <div className={`
                            w-3 h-3 rounded-full border-2 transition-all duration-300
                            ${isCompleted
                                ? 'bg-emerald-500 border-emerald-500'
                                : isCurrent
                                    ? 'bg-blue-500 border-blue-500 animate-pulse'
                                    : isUpcoming
                                        ? 'bg-slate-200 border-slate-300 dark:bg-slate-600 dark:border-slate-500'
                                        : 'bg-slate-400 border-slate-400'
                            }
                        `}>
                            {isCompleted && (
                                <CheckCircle className="w-2 h-2 text-white absolute -top-0.5 -left-0.5" />
                            )}
                        </div>
                        {index < steps.length - 1 && (
                            <div className={`
                                absolute top-1.5 left-3 w-8 h-0.5 transition-all duration-300
                                ${isCompleted ? 'bg-emerald-300' : 'bg-slate-200 dark:bg-slate-600'}
                            `} />
                        )}
                    </motion.div>
                );
            })}
        </div>
    );
};
