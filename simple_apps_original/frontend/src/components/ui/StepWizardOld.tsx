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
    variant?: 'blue' | 'emerald';
    className?: string;
}

export const StepWizard: React.FC<StepWizardProps> = ({
    steps,
    currentStep,
    className = ''
}) => {
    return (
        <div className={`flex items-center justify-center space-x-4 ${className}`}>
            {steps.map((step, index) => {
                const isActive = index === currentStep;
                const isCompleted = index < currentStep;
                const isPending = index > currentStep;

                return (
                    <div key={step.id} className="flex items-center">
                        {/* Step Circle */}
                        <motion.div
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ delay: index * 0.1 }}
                            className={`
                relative flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300
                ${isCompleted ? 'bg-emerald-500 border-emerald-500 text-white' : ''}
                ${isActive ? 'bg-blue-500 border-blue-500 text-white scale-110' : ''}
                ${isPending ? 'bg-slate-100 border-slate-300 text-slate-500' : ''}
              `}
                        >
                            {isCompleted ? (
                                <Check className="w-6 h-6" />
                            ) : isActive ? (
                                <Clock className="w-6 h-6 animate-pulse" />
                            ) : (
                                <step.icon className="w-6 h-6" />
                            )}

                            {/* Active indicator */}
                            {isActive && (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="absolute -inset-1 bg-blue-500 rounded-full opacity-25"
                                />
                            )}
                        </motion.div>

                        {/* Step Label */}
                        <div className="ml-3 hidden sm:block">
                            <p className={`
                text-sm font-medium transition-colors
                ${isCompleted ? 'text-emerald-600' : ''}
                ${isActive ? 'text-blue-600' : ''}
                ${isPending ? 'text-slate-500' : ''}
              `}>
                                {step.title}
                            </p>
                        </div>

                        {/* Connector Line */}
                        {index < steps.length - 1 && (
                            <div className={`
                w-8 h-0.5 mx-4 transition-colors duration-300
                ${index < currentStep ? 'bg-emerald-500' : 'bg-slate-300'}
              `} />
                        )}
                    </div>
                );
            })}
        </div>
    );
};
