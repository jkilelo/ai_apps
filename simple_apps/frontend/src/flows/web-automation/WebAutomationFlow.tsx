import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowLeft,
    Monitor,
    Settings,
    Play,
    FileText,
    CheckCircle,
    Target,
    Code2
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useWebAutomation } from './hooks/useWebAutomation';
import { AutomationForm } from './components/AutomationForm';
import { WorkflowBuilder } from './components/WorkflowBuilder';
import { TestExecution } from './components/TestExecution';
import { AutomationResults } from './components/AutomationResults';
import './styles/scrollbar.css';

const steps = [
    { id: 1, title: 'Target Setup', icon: Settings, description: 'Define automation target' },
    { id: 2, title: 'Workflow Builder', icon: Code2, description: 'Create automation steps' },
    { id: 3, title: 'Test Execution', icon: Play, description: 'Run automation tests' },
    { id: 4, title: 'Results & Report', icon: FileText, description: 'View results and reports' }
];

export function WebAutomationFlow() {
    const {
        currentStep,
        setCurrentStep,
        formData,
        setFormData,
        workflow,
        setWorkflow,
        results,
        isLoading,
        stepStatus,
        sessionId,
        executeTargetSetup,
        executeWorkflowBuild,
        executeTests,
        getResults,
        resetFlow
    } = useWebAutomation();

    const handleNext = () => {
        if (currentStep < steps.length) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handleBack = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
        }
    };

    // Step-specific execution handlers
    const handleStep1Execute = async () => {
        try {
            await executeTargetSetup();
        } catch (error) {
            console.error('Step 1 failed:', error);
        }
    };

    const handleStep2Execute = async () => {
        try {
            await executeWorkflowBuild();
        } catch (error) {
            console.error('Step 2 failed:', error);
        }
    };

    const handleStep3Execute = async () => {
        try {
            await executeTests();
        } catch (error) {
            console.error('Step 3 failed:', error);
        }
    };

    const handleStep4Execute = async () => {
        try {
            await getResults();
        } catch (error) {
            console.error('Step 4 failed:', error);
        }
    };

    const renderStepContent = () => {
        switch (currentStep) {
            case 1:
                return (
                    <AutomationForm
                        data={formData}
                        onChange={setFormData}
                        onNext={handleStep1Execute}
                    />
                );
            case 2:
                return (
                    <WorkflowBuilder
                        workflow={workflow}
                        onChange={setWorkflow}
                        targetUrl={formData.targetUrl}
                        onNext={handleStep2Execute}
                        onBack={handleBack}
                    />
                );
            case 3:
                return (
                    <TestExecution
                        workflow={workflow}
                        onExecute={handleStep3Execute}
                        onBack={handleBack}
                        isLoading={isLoading}
                    />
                );
            case 4:
                return (
                    <AutomationResults
                        results={results}
                        onReset={resetFlow}
                        onBack={handleBack}
                    />
                );
            default:
                return null;
        }
    };

    return (
        <div className="h-screen w-screen flex relative overflow-hidden fixed inset-0">
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
                                <Monitor className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold bg-gradient-to-r from-[#004685] via-blue-600 to-[#004685] bg-clip-text text-transparent">
                                    Web Automation
                                </h1>
                                <p className="text-sm text-slate-600 dark:text-slate-400">
                                    {steps.length}-step automation pipeline
                                </p>
                            </div>
                        </div>

                        {/* Progress Indicator */}
                        <div className="relative z-10">
                            <div className="bg-slate-100 dark:bg-slate-700 rounded-full h-2 mb-3">
                                <motion.div
                                    className="bg-gradient-to-r from-[#004685] to-blue-600 h-2 rounded-full"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${(currentStep / steps.length) * 100}%` }}
                                    transition={{ duration: 0.5 }}
                                />
                            </div>
                            <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400">
                                <span>Step {currentStep} of {steps.length}</span>
                                <span>{Math.round((currentStep / steps.length) * 100)}% Complete</span>
                            </div>
                        </div>
                    </div>

                    {/* Steps List */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-2 min-h-0 custom-scrollbar">
                        {steps.map((step, index) => {
                            const StepIcon = step.icon;
                            const isActive = currentStep === step.id;
                            const isCompleted = currentStep > step.id;
                            const isAccessible = step.id <= currentStep || step.id === currentStep + 1;

                            return (
                                <motion.div
                                    key={step.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    onClick={() => {
                                        if (isAccessible) {
                                            setCurrentStep(step.id);
                                        }
                                    }}
                                    className={`
                                        relative p-4 rounded-xl border transition-all duration-300 cursor-pointer
                                        ${isActive
                                            ? 'bg-gradient-to-r from-[#004685] to-blue-600 border-[#004685] shadow-lg shadow-blue-500/25 text-white'
                                            : isCompleted
                                                ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700 hover:shadow-md'
                                                : isAccessible
                                                    ? 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:shadow-md hover:border-[#004685] dark:hover:border-[#004685]'
                                                    : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 opacity-50 cursor-not-allowed'
                                        }
                                    `}
                                >
                                    <div className="flex items-center space-x-3">
                                        <div className={`
                                            w-8 h-8 rounded-lg flex items-center justify-center transition-colors
                                            ${isActive
                                                ? 'bg-white/20 text-white'
                                                : isCompleted
                                                    ? 'bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-400'
                                                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                                            }
                                        `}>
                                            {isCompleted ? (
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
                                        {isLoading && isActive && (
                                            <motion.div
                                                animate={{ rotate: 360 }}
                                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                                            />
                                        )}
                                    </div>
                                </motion.div>
                            );
                        })}
                    </div>

                    {/* Navigation Controls */}
                    {currentStep > 1 && (
                        <div className="flex-shrink-0 p-4 border-t border-white/20 dark:border-slate-700/30 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl">
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={handleBack}
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
                    <div className="flex items-center space-x-2 mb-3">
                        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border border-blue-200 dark:border-blue-800">
                            <Target className="h-3 w-3" />
                            <span>Web Automation Flow</span>
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">
                            Step {currentStep} of {steps.length}
                        </div>
                    </div>

                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                        {steps[currentStep - 1]?.title}
                    </h2>
                    <p className="text-slate-600 dark:text-slate-300">
                        {steps[currentStep - 1]?.description}
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
                            <div className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-xl rounded-3xl border border-white/20 dark:border-slate-700/30 shadow-xl overflow-hidden w-full">
                                {renderStepContent()}
                            </div>
                        </motion.div>
                    </AnimatePresence>
                </div>
            </motion.div>
        </div>
    );
}
