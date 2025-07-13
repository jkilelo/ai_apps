import React, { useState } from 'react';
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
import { StepWizard } from '../../components/ui/StepWizard';
import { ProfileForm } from './components/ProfileForm';
import { ResultsDisplay } from './components/ResultsDisplay';
import { useDataProfiling } from './hooks/useDataProfiling';

const steps = [
    { id: 'input', title: 'Data Input', icon: Database, description: 'Configure data source' },
    { id: 'metadata', title: 'Metadata Analysis', icon: Layers, description: 'Analyze data structure' },
    { id: 'profiling', title: 'Data Profiling', icon: BarChart3, description: 'Statistical analysis' },
    { id: 'quality', title: 'Quality Checks', icon: Target, description: 'Data quality assessment' },
    { id: 'code', title: 'Code Generation', icon: Code, description: 'Generate automation code' },
    { id: 'execution', title: 'Execution', icon: Zap, description: 'Run analysis pipeline' }
];

export const DataProfilingFlow: React.FC = () => {
    const [currentStep, setCurrentStep] = useState(0);
    const {
        profileData,
        results,
        isLoading,
        error,
        executeFullFlow
    } = useDataProfiling();

    const handleFormSubmit = async (data: any) => {
        setCurrentStep(1);
        await executeFullFlow(data);
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
                delayChildren: 0.2
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0 }
    };

    return (
        <div className="min-h-screen relative overflow-hidden">
            {/* Animated Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-100 dark:from-slate-900 dark:via-indigo-900 dark:to-slate-800">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%239C92AC" fill-opacity="0.05"%3E%3Ccircle cx="30" cy="30" r="10"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
                
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
                    className="absolute top-20 right-20 w-32 h-32 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-xl"
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
                    className="absolute bottom-20 left-20 w-24 h-24 bg-gradient-to-r from-cyan-400/20 to-blue-400/20 rounded-full blur-xl"
                />
            </div>

            <div className="relative z-10 container mx-auto px-4 py-8">
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    className="max-w-7xl mx-auto"
                >
                    {/* Header */}
                    <motion.div
                        variants={itemVariants}
                        className="mb-12"
                    >
                        <Link
                            to="/"
                            className="inline-flex items-center space-x-2 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors mb-8 group"
                        >
                            <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                            <span>Back to Dashboard</span>
                        </Link>

                        <div className="text-center">
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
                                className="inline-flex items-center justify-center w-20 h-20 mb-6 rounded-3xl bg-gradient-to-r from-indigo-500 to-purple-600 shadow-2xl shadow-indigo-500/25"
                            >
                                <Sparkles className="h-10 w-10 text-white" />
                            </motion.div>
                            
                            <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent mb-4">
                                Data Profiling & Quality Analysis
                            </h1>
                            <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed">
                                Advanced AI-powered data analysis pipeline with comprehensive quality assessment and automated insights generation
                            </p>
                        </div>
                    </motion.div>

                    {/* Step Progress - Glassmorphism Design */}
                    <motion.div
                        variants={itemVariants}
                        className="mb-12"
                    >
                        <div className="backdrop-blur-xl bg-white/30 dark:bg-slate-800/30 rounded-3xl border border-white/20 dark:border-slate-700/30 shadow-2xl shadow-indigo-500/10 p-8">
                            <StepWizard 
                                steps={steps.map((step, index) => ({
                                    id: step.id,
                                    title: step.title,
                                    description: step.description,
                                    icon: step.icon
                                }))} 
                                currentStep={currentStep}
                                onStepClick={setCurrentStep}
                                variant="indigo"
                            />
                        </div>
                    </motion.div>

                    {/* Main Content Area */}
                    <motion.div
                        variants={itemVariants}
                    >
                        <div className="backdrop-blur-xl bg-white/40 dark:bg-slate-800/40 rounded-3xl border border-white/20 dark:border-slate-700/30 shadow-2xl shadow-indigo-500/10 overflow-hidden">
                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={currentStep}
                                    initial={{ opacity: 0, x: 50 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -50 }}
                                    transition={{ duration: 0.3 }}
                                    className="p-8"
                                >
                                    {/* Step Content */}
                                    {currentStep === 0 && (
                                        <div className="space-y-8">
                                            <div className="text-center">
                                                <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
                                                    Configure Data Source
                                                </h2>
                                                <p className="text-slate-600 dark:text-slate-300 mb-8">
                                                    Specify your database and table for comprehensive analysis
                                                </p>
                                            </div>
                                            <ProfileForm onSubmit={handleFormSubmit} />
                                        </div>
                                    )}

                                    {currentStep > 0 && (
                                        <div className="space-y-8">
                                            <div className="text-center">
                                                <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
                                                    {steps[currentStep].title}
                                                </h2>
                                                <p className="text-slate-600 dark:text-slate-300 mb-8">
                                                    {steps[currentStep].description}
                                                </p>
                                            </div>

                                            {/* Loading State */}
                                            {isLoading && (
                                                <div className="text-center py-16">
                                                    <motion.div
                                                        animate={{ rotate: 360 }}
                                                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                                        className="inline-block w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full mb-4"
                                                    />
                                                    <p className="text-slate-600 dark:text-slate-300 text-lg">
                                                        Processing your data analysis...
                                                    </p>
                                                </div>
                                            )}

                                            {/* Results */}
                                            {results && !isLoading && (
                                                <ResultsDisplay results={results} />
                                            )}

                                            {/* Error State */}
                                            {error && (
                                                <motion.div
                                                    initial={{ opacity: 0, scale: 0.9 }}
                                                    animate={{ opacity: 1, scale: 1 }}
                                                    className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl p-6 text-center"
                                                >
                                                    <div className="text-red-600 dark:text-red-400 mb-2">
                                                        <CheckCircle className="h-8 w-8 mx-auto mb-2" />
                                                        <p className="font-semibold">Analysis Error</p>
                                                    </div>
                                                    <p className="text-red-600 dark:text-red-400">{error}</p>
                                                </motion.div>
                                            )}
                                        </div>
                                    )}
                                </motion.div>
                            </AnimatePresence>
                        </div>
                    </motion.div>

                    {/* Navigation Controls */}
                    {currentStep > 0 && (
                        <motion.div
                            variants={itemVariants}
                            className="mt-8 flex justify-center space-x-4"
                        >
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                                className="px-8 py-3 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border border-white/20 dark:border-slate-700/30 rounded-xl text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-800 transition-all shadow-lg"
                            >
                                Previous Step
                            </motion.button>
                            
                            {currentStep < steps.length - 1 && (
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
                                    className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg shadow-indigo-500/25"
                                >
                                    Next Step
                                </motion.button>
                            )}
                        </motion.div>
                    )}
                </motion.div>
            </div>
        </div >
    );
};
<StepWizard steps={steps} currentStep={currentStep} />

{/* Content Area */ }
<motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ delay: 0.2 }}
    className="mt-8"
>
    {currentStep === 0 && (
        <ProfileForm onSubmit={handleFormSubmit} isLoading={isLoading} />
    )}

    {currentStep > 0 && (
        <ResultsDisplay
            results={results}
            currentStep={currentStep}
            isLoading={isLoading}
            error={error}
        />
    )}
</motion.div>
            </div >
        </div >
    );
};
