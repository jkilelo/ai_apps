import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
    Database,
    BarChart3,
    CheckCircle,
    Code,
    Play,
    ArrowLeft,
    Sparkles,
    Layers,
    Target,
    Zap
} from 'lucide-react';
import { ExecutiveResultsDisplay } from './components/ExecutiveResultsDisplay';
import { ViewModeToggle } from './components/ViewModeToggle';
import { CodeHighlighter, detectLanguage, PySparkCodeDisplay, ExecutionResultsDisplay } from './components/CodeHighlighter';
import { ProgressIndicator } from './components/ProgressIndicator';
import { StepLoadingIndicator } from './components/LoadingStates';
import { ToastContainer, useToast } from './components/ToastNotification';
import { Tooltip } from './components/UIComponents';
import { EnhancedProfileForm } from './components/EnhancedProfileForm';
import { useTheme } from '../../contexts/ThemeContext';
import './styles/scrollbar.css';

const steps = [
    { id: 'input', title: 'Data Input', icon: Database, description: 'Configure data source' },
    { id: 'metadata', title: 'Metadata Analysis', icon: Layers, description: 'Analyze data structure' },
    { id: 'profiling_suggestions', title: 'Profiling Suggestions', icon: BarChart3, description: 'Get profiling recommendations' },
    { id: 'profiling_testcases', title: 'Profiling Tests', icon: CheckCircle, description: 'Generate test cases' },
    { id: 'profiling_code', title: 'PySpark Code', icon: Code, description: 'Generate PySpark code' },
    { id: 'profiling_execution', title: 'Code Execution', icon: Play, description: 'Execute profiling code' },
    { id: 'dq_suggestions', title: 'DQ Suggestions', icon: Target, description: 'Data quality recommendations' },
    { id: 'dq_testcases', title: 'DQ Test Cases', icon: CheckCircle, description: 'Quality test cases' },
    { id: 'dq_code', title: 'DQ Code Generation', icon: Code, description: 'Generate DQ PySpark code' },
    { id: 'dq_execution', title: 'DQ Execution', icon: Zap, description: 'Execute quality analysis' }
];

export const DataProfilingFlow: React.FC = () => {
    const { viewMode } = useTheme();
    const toast = useToast();
    const [currentStep, setCurrentStep] = useState(0);
    const [profileData, setProfileData] = useState<any>(null);
    const [stepResults, setStepResults] = useState<{ [key: string]: any }>({});
    const [isLoadingStep, setIsLoadingStep] = useState(false);
    const [stepError, setStepError] = useState<string | null>(null);

    // Calculate completed steps for progress tracking
    const completedSteps = Object.keys(stepResults);
    const estimatedTimeRemaining = Math.max(0, (steps.length - currentStep - 1) * 0.5); // 30 seconds per step estimate

    const handleFormSubmit = async (data: any) => {
        setProfileData(data);
        setCurrentStep(1);
    };

    const executeStep = async (stepIndex: number) => {
        if (stepIndex === 0 || !profileData) return; // Skip input step

        const step = steps[stepIndex];
        setIsLoadingStep(true);
        setStepError(null);

        try {
            let response;
            switch (step.id) {
                case 'metadata':
                    response = await fetch('/api/metadata', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                case 'profiling_suggestions':
                    response = await fetch('/api/profiling/suggestions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                case 'profiling_testcases':
                    response = await fetch('/api/profiling/testcases', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                case 'profiling_code':
                    response = await fetch('/api/profiling/pyspark_code', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                case 'profiling_execution':
                    response = await fetch('/api/profiling/code_execution', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                case 'dq_suggestions':
                    response = await fetch('/api/dq/suggestions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                case 'dq_testcases':
                    response = await fetch('/api/dq/testcases', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                case 'dq_code':
                    response = await fetch('/api/dq/pyspark_code', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                case 'dq_execution':
                    response = await fetch('/api/dq/code_execution', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profileData)
                    });
                    break;
                default:
                    throw new Error(`Unknown step: ${step.id}`);
            }

            const result = await response.json();
            setStepResults(prev => ({ ...prev, [step.id]: result }));

            // Show success toast
            toast.success(step.title, 'Step executed successfully');
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
            setStepError(errorMessage);

            // Show error toast
            toast.error('Step Failed', errorMessage);
        } finally {
            setIsLoadingStep(false);
        }
    };

    const handleNextStep = () => {
        if (currentStep < steps.length - 1) {
            const nextStep = currentStep + 1;
            setCurrentStep(nextStep);
            if (nextStep > 0) {
                executeStep(nextStep);
            }
        }
    };

    const handlePreviousStep = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    // Auto-execute step when entering it (except input step)
    useEffect(() => {
        if (currentStep > 0 && profileData && !stepResults[steps[currentStep].id]) {
            executeStep(currentStep);
        }
    }, [currentStep, profileData, stepResults]);

    return (
        <div className="h-screen w-screen flex relative overflow-hidden fixed inset-0">
            {/* View Mode Toggle */}
            <div className="absolute top-4 right-4 z-[150]">
                <ViewModeToggle />
            </div>

            {/* Animated Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-slate-50 to-blue-100 dark:from-slate-900 dark:via-blue-900 dark:to-slate-800">
                <div className="absolute inset-0 opacity-40">
                    <div className="w-full h-full bg-repeat" style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23004685' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='10'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
                    }}></div>
                </div>

                {/* Floating Elements */}
                <motion.div
                    animate={{
                        rotate: [0, 360],
                        scale: [1, 1.2, 1],
                    }}
                    transition={{
                        duration: 20,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                    className="absolute top-20 right-20 w-32 h-32 bg-gradient-to-r from-[#004685]/20 to-blue-400/20 rounded-full blur-xl"
                />
                <motion.div
                    animate={{
                        rotate: [360, 0],
                        scale: [1, 0.8, 1],
                    }}
                    transition={{
                        duration: 15,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                    className="absolute bottom-20 left-20 w-24 h-24 bg-gradient-to-r from-blue-400/20 to-[#004685]/20 rounded-full blur-xl"
                />
            </div>

            {/* Left Sidebar - Steps */}
            <motion.div
                initial={{ x: -100, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="relative z-10 w-80 flex-shrink-0 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-r border-white/20 dark:border-slate-700/30 shadow-2xl flex flex-col h-full overflow-hidden"
            >
                <div className="h-full flex flex-col overflow-hidden">
                    {/* Header */}
                    <div className="flex-shrink-0 p-6 border-b border-white/20 dark:border-slate-700/30 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl">
                        <Link
                            to="/"
                            className="inline-flex items-center space-x-2 text-slate-600 dark:text-slate-300 hover:text-[#004685] dark:hover:text-[#004685] transition-colors mb-4 group"
                        >
                            <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                            <span>Back to Dashboard</span>
                        </Link>

                        <div className="flex items-center space-x-3 mb-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-[#004685] to-blue-600 rounded-2xl flex items-center justify-center">
                                <Sparkles className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold bg-gradient-to-r from-[#004685] via-blue-600 to-[#004685] bg-clip-text text-transparent">
                                    Data Profiling & Quality
                                </h1>
                                <p className="text-sm text-slate-600 dark:text-slate-400">
                                    10-step analysis pipeline
                                </p>
                            </div>
                        </div>

                        {/* Progress Indicator */}
                        <div className="relative z-10">
                            <ProgressIndicator
                                totalSteps={steps.length}
                                completedSteps={completedSteps}
                                currentStep={currentStep}
                                estimatedTimeRemaining={estimatedTimeRemaining}
                            />
                        </div>
                    </div>

                    {/* Steps List */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-2 custom-scrollbar min-h-0">
                        {/* ...existing code... */}
                        {steps.map((step, index) => {
                            const StepIcon = step.icon;
                            const isActive = currentStep === index;
                            const isCompleted = stepResults[step.id] || (index === 0 && profileData);
                            const isDisabled = index === 0 ? false : !profileData;

                            // Check if we need to render a section separator
                            const showProfilingSeparator = index === 2; // Before "Profiling Suggestions"
                            const showDQSeparator = index === 6; // Before "DQ Suggestions"

                            return (
                                <React.Fragment key={step.id}>
                                    {/* Profiling Flow Section Header */}
                                    {showProfilingSeparator && (
                                        <div className="relative my-6">
                                            <div className="absolute inset-0 flex items-center">
                                                <div className="w-full border-t border-gradient-to-r from-blue-200 via-indigo-300 to-purple-200 dark:from-blue-800 dark:via-indigo-700 dark:to-purple-800"></div>
                                            </div>
                                            <div className="relative flex justify-center">
                                                <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm px-4 py-2 rounded-full border border-[#004685]/30 dark:border-[#004685] shadow-sm">
                                                    <div className="flex items-center space-x-2">
                                                        <BarChart3 className="h-4 w-4 text-[#004685] dark:text-[#004685]" />
                                                        <span className="text-sm font-medium text-[#004685] dark:text-[#004685]">
                                                            Data Profiling Flow
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Data Quality Flow Section Header */}
                                    {showDQSeparator && (
                                        <div className="relative my-6">
                                            <div className="absolute inset-0 flex items-center">
                                                <div className="w-full border-t border-gradient-to-r from-blue-200 via-[#004685]/30 to-blue-200 dark:from-blue-800 dark:via-[#004685] dark:to-blue-800"></div>
                                            </div>
                                            <div className="relative flex justify-center">
                                                <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm px-4 py-2 rounded-full border border-[#004685]/30 dark:border-[#004685] shadow-sm">
                                                    <div className="flex items-center space-x-2">
                                                        <Target className="h-4 w-4 text-[#004685] dark:text-[#004685]" />
                                                        <span className="text-sm font-medium text-[#004685] dark:text-[#004685]">
                                                            Data Quality Flow
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Step Item */}
                                    <Tooltip content={step.description}>
                                        <motion.div
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                            onClick={() => {
                                                if (!isDisabled) {
                                                    setCurrentStep(index);
                                                }
                                            }}
                                            className={`
                                                relative p-4 rounded-xl border transition-all duration-300 cursor-pointer
                                                ${isActive
                                                    ? index >= 6
                                                        ? 'bg-gradient-to-r from-[#004685] to-blue-700 border-[#004685] shadow-lg shadow-blue-500/25 text-white'
                                                        : index >= 2
                                                            ? 'bg-gradient-to-r from-[#004685] to-blue-600 border-[#004685] shadow-lg shadow-blue-500/25 text-white'
                                                            : 'bg-gradient-to-r from-[#004685] to-blue-600 border-[#004685] shadow-lg shadow-blue-500/25 text-white'
                                                    : isCompleted
                                                        ? index >= 6
                                                            ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700 hover:shadow-md'
                                                            : index >= 2
                                                                ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700 hover:shadow-md'
                                                                : 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700 hover:shadow-md'
                                                        : isDisabled
                                                            ? 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 opacity-50 cursor-not-allowed'
                                                            : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:shadow-md hover:border-[#004685] dark:hover:border-[#004685]'
                                                }
                                            `}
                                        >
                                            {/* Flow Type Indicator */}
                                            {index >= 2 && (
                                                <div className={`
                                                absolute -left-1 top-1/2 transform -translate-y-1/2 w-1 h-8 rounded-full
                                                ${index >= 6
                                                        ? 'bg-gradient-to-b from-[#004685] to-blue-600'
                                                        : 'bg-gradient-to-b from-[#004685] to-blue-500'
                                                    }
                                            `}></div>
                                            )}

                                            <div className="flex items-center space-x-3">
                                                <div className={`
                                                w-8 h-8 rounded-lg flex items-center justify-center transition-colors
                                                ${isActive
                                                        ? 'bg-white/20 text-white'
                                                        : isCompleted
                                                            ? index >= 6
                                                                ? 'bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-400'
                                                                : index >= 2
                                                                    ? 'bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-400'
                                                                    : 'bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-400'
                                                            : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                                                    }
                                            `}>
                                                    {isCompleted && index > 0 ? (
                                                        <CheckCircle className="h-5 w-5" />
                                                    ) : (
                                                        <StepIcon className="h-5 w-5" />
                                                    )}
                                                </div>
                                                <div className="flex-1">
                                                    <h3 className={`font-medium text-sm ${isActive ? 'text-white' : 'text-slate-900 dark:text-white'}`}>
                                                        {step.title}
                                                    </h3>
                                                    <p className={`text-xs ${isActive ? 'text-white/80' : 'text-slate-500 dark:text-slate-400'}`}>
                                                        {step.description}
                                                    </p>
                                                </div>
                                                {isLoadingStep && isActive && (
                                                    <motion.div
                                                        animate={{ rotate: 360 }}
                                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                                        className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                                                    />
                                                )}
                                            </div>
                                        </motion.div>
                                    </Tooltip>
                                </React.Fragment>
                            );
                        })}
                    </div>

                    {/* Navigation Controls */}
                    {currentStep > 0 && (
                        <div className="flex-shrink-0 p-4 border-t border-white/20 dark:border-slate-700/30 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl">
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={handlePreviousStep}
                                className="w-full px-4 py-2 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border border-white/20 dark:border-slate-700/30 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-800 transition-all text-sm"
                            >
                                Previous Step
                            </motion.button>
                        </div>
                    )}
                </div>
            </motion.div>

            {/* Right Canvas - Content */}
            <motion.div
                initial={{ x: 100, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="relative z-10 flex-1 flex flex-col h-full overflow-hidden min-w-0"
            >
                {/* Canvas Header */}
                <div className="flex-shrink-0 bg-white/40 dark:bg-slate-800/40 backdrop-blur-xl border-b border-white/20 dark:border-slate-700/30 p-6">
                    {/* Flow Section Badge */}
                    {currentStep >= 2 && (
                        <div className="flex items-center space-x-2 mb-3">
                            <div className={`
                                inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium
                                ${currentStep >= 6
                                    ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border border-blue-200 dark:border-blue-800'
                                    : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border border-blue-200 dark:border-blue-800'
                                }
                            `}>
                                {currentStep >= 6 ? (
                                    <>
                                        <Target className="h-3 w-3" />
                                        <span>Data Quality Flow</span>
                                    </>
                                ) : (
                                    <>
                                        <BarChart3 className="h-3 w-3" />
                                        <span>Data Profiling Flow</span>
                                    </>
                                )}
                            </div>
                            <div className="text-xs text-slate-500 dark:text-slate-400">
                                Step {currentStep + 1} of {steps.length}
                            </div>
                        </div>
                    )}

                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                        {steps[currentStep].title}
                    </h2>
                    <p className="text-slate-600 dark:text-slate-300">
                        {steps[currentStep].description}
                    </p>
                </div>

                {/* Canvas Content */}
                <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 min-h-0">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentStep}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.3 }}
                            className="h-full w-full"
                        >
                            {/* Step Content */}
                            {currentStep === 0 && (
                                <div className="h-full flex items-center justify-center overflow-y-auto">
                                    <div className="w-full max-w-xl space-y-8 py-8 px-4">
                                        <EnhancedProfileForm onSubmit={handleFormSubmit} isLoading={isLoadingStep} />
                                    </div>
                                </div>
                            )}

                            {currentStep > 0 && (
                                <div className="space-y-6 h-full overflow-y-auto overflow-x-hidden w-full">
                                    {/* Loading State */}
                                    {isLoadingStep && (
                                        <div className="flex items-center justify-center py-20">
                                            <StepLoadingIndicator
                                                stepTitle={steps[currentStep].title}
                                            />
                                        </div>
                                    )}

                                    {/* Current Step Results */}
                                    {stepResults[steps[currentStep].id] && !isLoadingStep && (
                                        <div className="space-y-6">
                                            {viewMode === 'executive' ? (
                                                <ExecutiveResultsDisplay
                                                    stepData={stepResults[steps[currentStep].id]}
                                                    stepId={steps[currentStep].id}
                                                />
                                            ) : (
                                                <motion.div
                                                    initial={{ opacity: 0, y: 20 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                    className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-xl rounded-3xl border border-white/20 dark:border-slate-700/30 shadow-xl overflow-hidden w-full"
                                                >
                                                    <div className="bg-gradient-to-r from-[#004685]/10 to-blue-500/10 border-b border-[#004685]/20 dark:border-[#004685]/20 p-6">
                                                        <div className="flex items-center space-x-3">
                                                            <CheckCircle className="h-6 w-6 text-[#004685] dark:text-[#004685]" />
                                                            <h3 className="text-xl font-semibold text-[#004685] dark:text-[#004685]">
                                                                {steps[currentStep].title} Complete
                                                            </h3>
                                                        </div>
                                                    </div>
                                                    <div className="p-6 max-h-96 overflow-y-auto overflow-x-hidden">
                                                        {/* Render different components based on step type */}
                                                        {steps[currentStep].id.includes('code') ? (
                                                            <PySparkCodeDisplay stepData={stepResults[steps[currentStep].id]} />
                                                        ) : steps[currentStep].id.includes('execution') ? (
                                                            <ExecutionResultsDisplay stepData={stepResults[steps[currentStep].id]} />
                                                        ) : (
                                                            <CodeHighlighter
                                                                code={stepResults[steps[currentStep].id]}
                                                                language={detectLanguage(stepResults[steps[currentStep].id])}
                                                                title={`${steps[currentStep].title} Results`}
                                                                isDark={true}
                                                            />
                                                        )}
                                                    </div>
                                                </motion.div>
                                            )}

                                            {/* Next Step Button */}
                                            {currentStep < steps.length - 1 && (
                                                <div className="flex justify-center">
                                                    <motion.button
                                                        whileHover={{ scale: 1.05 }}
                                                        whileTap={{ scale: 0.95 }}
                                                        onClick={handleNextStep}
                                                        className="px-8 py-4 bg-gradient-to-r from-[#004685] to-blue-600 text-white font-medium rounded-2xl hover:from-[#003668] hover:to-blue-700 transition-all shadow-lg shadow-[#004685]/25 flex items-center space-x-2"
                                                    >
                                                        <span>Continue to {steps[currentStep + 1].title}</span>
                                                        <ArrowLeft className="h-5 w-5 rotate-180" />
                                                    </motion.button>
                                                </div>
                                            )}

                                            {/* Completion Message */}
                                            {currentStep === steps.length - 1 && (
                                                <motion.div
                                                    initial={{ opacity: 0, scale: 0.9 }}
                                                    animate={{ opacity: 1, scale: 1 }}
                                                    className="text-center py-8"
                                                >
                                                    <div className="w-20 h-20 bg-gradient-to-r from-[#004685] to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                                        <CheckCircle className="h-10 w-10 text-white" />
                                                    </div>
                                                    <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                                                        Analysis Complete!
                                                    </h3>
                                                    <p className="text-slate-600 dark:text-slate-300">
                                                        All 10 steps of your data profiling and quality analysis have been completed successfully.
                                                    </p>
                                                </motion.div>
                                            )}
                                        </div>
                                    )}

                                    {/* Error State */}
                                    {stepError && (
                                        <motion.div
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            className="bg-red-50/80 dark:bg-red-900/20 backdrop-blur-xl border border-red-200 dark:border-red-800 rounded-2xl p-6"
                                        >
                                            <div className="text-center">
                                                <div className="text-red-600 dark:text-red-400 mb-4">
                                                    <CheckCircle className="h-8 w-8 mx-auto mb-2" />
                                                    <p className="font-semibold">Step Error</p>
                                                </div>
                                                <p className="text-red-600 dark:text-red-400 mb-4">{stepError}</p>
                                                <motion.button
                                                    whileHover={{ scale: 1.05 }}
                                                    whileTap={{ scale: 0.95 }}
                                                    onClick={() => executeStep(currentStep)}
                                                    className="px-6 py-2 bg-[#EE1C25] text-white rounded-lg hover:bg-red-700 transition-colors"
                                                >
                                                    Retry Step
                                                </motion.button>
                                            </div>
                                        </motion.div>
                                    )}
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>
                </div>
            </motion.div>

            {/* Toast Notifications */}
            <div className="fixed top-4 right-4 z-[200] max-w-sm">
                <ToastContainer toasts={toast.toasts} onRemove={toast.removeToast} />
            </div>
        </div>
    );
};
