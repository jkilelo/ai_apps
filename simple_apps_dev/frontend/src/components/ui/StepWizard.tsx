import React from 'react';
import { motion } from 'framer-motion';
import { Check, Clock, AlertCircle } from 'lucide-react';

interface Step {
    id: string | number;
    title?: string;
    name?: string;
    description?: string;
    icon?: React.ComponentType<any>;
}

interface StepWizardProps {
    steps: Step[];
    currentStep: number;
    onStepClick?: (step: number) => void;
    variant?: 'blue' | 'emerald' | 'indigo';
    className?: string;
}

export const StepWizard: React.FC<StepWizardProps> = ({
    steps,
    currentStep,
    onStepClick,
    variant = 'blue',
    className = ''
}) => {
    const colors = {
        blue: {
            active: 'bg-blue-600 text-white border-blue-600',
            completed: 'bg-green-600 text-white border-green-600',
            pending: 'bg-gray-200 text-gray-400 border-gray-300',
            line: 'bg-blue-600',
            lineInactive: 'bg-gray-200'
        },
        emerald: {
            active: 'bg-emerald-600 text-white border-emerald-600',
            completed: 'bg-green-600 text-white border-green-600',
            pending: 'bg-gray-200 text-gray-400 border-gray-300',
            line: 'bg-emerald-600',
            lineInactive: 'bg-gray-200'
        },
        indigo: {
            active: 'bg-indigo-600 text-white border-indigo-600',
            completed: 'bg-green-600 text-white border-green-600',
            pending: 'bg-gray-200 text-gray-400 border-gray-300',
            line: 'bg-indigo-600',
            lineInactive: 'bg-gray-200'
        }
    };

    const theme = colors[variant];

    return (
        <div className={`flex items-center justify-center space-x-4 ${className}`}>
            {steps.map((step, index) => {
                const stepNumber = typeof step.id === 'number' ? step.id : index + 1;
                const isActive = stepNumber === currentStep;
                const isCompleted = stepNumber < currentStep;
                const isPending = stepNumber > currentStep;
                const stepTitle = step.title || step.name || `Step ${stepNumber}`;

                return (
                    <div key={step.id} className="flex items-center">
                        {/* Step Circle */}
                        <motion.div
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: isActive ? 1.1 : 1, opacity: 1 }}
                            transition={{ delay: index * 0.1 }}
                            className={`relative flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300 ${onStepClick ? 'cursor-pointer hover:scale-105' : ''
                                } ${isCompleted
                                    ? theme.completed
                                    : isActive
                                        ? theme.active
                                        : theme.pending
                                }`}
                            onClick={() => onStepClick && onStepClick(stepNumber)}
                        >
                            {isCompleted ? (
                                <Check className="w-6 h-6" />
                            ) : isActive ? (
                                step.icon ? (
                                    <step.icon className="w-6 h-6 animate-pulse" />
                                ) : (
                                    <Clock className="w-6 h-6 animate-pulse" />
                                )
                            ) : (
                                step.icon ? (
                                    <step.icon className="w-6 h-6" />
                                ) : (
                                    <AlertCircle className="w-6 h-6" />
                                )
                            )}

                            {/* Active indicator */}
                            {isActive && (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className={`absolute -inset-1 ${variant === 'emerald' ? 'bg-emerald-500' : 'bg-blue-500'} rounded-full opacity-25`}
                                />
                            )}
                        </motion.div>

                        {/* Step Label */}
                        <div className="ml-3 hidden sm:block">
                            <p className={`text-sm font-medium transition-colors ${isCompleted
                                ? 'text-green-600 dark:text-green-400'
                                : isActive
                                    ? `${variant === 'emerald' ? 'text-emerald-600 dark:text-emerald-400' : 'text-blue-600 dark:text-blue-400'}`
                                    : 'text-gray-500 dark:text-gray-400'
                                }`}>
                                {stepTitle}
                            </p>
                            {step.description && (
                                <p className="text-xs text-gray-400 dark:text-gray-500">
                                    {step.description}
                                </p>
                            )}
                        </div>

                        {/* Connector Line */}
                        {index < steps.length - 1 && (
                            <div className={`w-8 h-0.5 mx-4 transition-colors duration-300 ${stepNumber < currentStep ? theme.line : theme.lineInactive
                                }`} />
                        )}
                    </div>
                );
            })}
        </div>
    );
};
