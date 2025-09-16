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
    Code2,
    Globe,
    ArrowRight,
    RefreshCw,
    Loader2
} from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

// API Configuration - Using unified API with real extraction
const API_BASE = 'http://localhost:8001/api/web-automation';

// Step definitions
const steps = [
    { id: 1, title: 'Element Extraction', icon: Settings, description: 'Extract page elements' },
    { id: 2, title: 'Test Generation', icon: Code2, description: 'Generate test cases' },
    { id: 3, title: 'Code Generation', icon: Play, description: 'Generate automation code' },
    { id: 4, title: 'Code Execution', icon: FileText, description: 'Execute generated code' }
];

export function WebAutomationFlowSimplified() {
    // === CONSOLIDATED STATE ===
    const [currentStep, setCurrentStep] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Step 1: Element Extraction State
    const [url, setUrl] = useState('');
    const [elements, setElements] = useState<any[]>([]);

    // Step 2: Test Generation State
    const [tests, setTests] = useState<any[]>([]);
    const [selectedElements, setSelectedElements] = useState<string[]>([]);

    // Step 3: Code Generation State
    const [code, setCode] = useState('');
    const [language, setLanguage] = useState<'python' | 'javascript'>('python');

    // Step 4: Execution State
    const [results, setResults] = useState<any>(null);

    // === API FUNCTIONS ===
    const extractElements = async () => {
        if (!url) {
            setError('Please enter a URL');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_BASE}/extract`, { url });
            setElements(response.data.elements || []);
            setCurrentStep(2);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to extract elements');
        } finally {
            setIsLoading(false);
        }
    };

    const generateTests = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_BASE}/generate-tests`, {
                url,
                elements: selectedElements.length > 0
                    ? elements.filter((_, i) => selectedElements.includes(String(i)))
                    : elements
            });
            setTests(response.data.tests || []);
            setCurrentStep(3);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to generate tests');
        } finally {
            setIsLoading(false);
        }
    };

    const generateCode = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_BASE}/generate-code`, {
                tests,
                language,
                url
            });
            setCode(response.data.code || '');
            setCurrentStep(4);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to generate code');
        } finally {
            setIsLoading(false);
        }
    };

    const executeCode = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_BASE}/execute`, {
                code,
                language
            });
            setResults(response.data.results);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to execute code');
        } finally {
            setIsLoading(false);
        }
    };

    const resetFlow = () => {
        setCurrentStep(1);
        setUrl('');
        setElements([]);
        setTests([]);
        setCode('');
        setResults(null);
        setSelectedElements([]);
        setError(null);
    };

    // === INLINE STEP COMPONENTS ===
    const renderStepContent = () => {
        switch (currentStep) {
            case 1: // Element Extraction
                return (
                    <div className="p-8">
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Target URL
                                </label>
                                <div className="flex space-x-2">
                                    <div className="relative flex-1">
                                        <Globe className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                                        <input
                                            type="url"
                                            value={url}
                                            onChange={(e) => setUrl(e.target.value)}
                                            placeholder="https://example.com"
                                            className="w-full pl-10 pr-3 py-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        />
                                    </div>
                                </div>
                            </div>

                            {error && (
                                <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
                                    {error}
                                </div>
                            )}

                            <button
                                onClick={extractElements}
                                disabled={isLoading || !url}
                                className="w-full px-6 py-3 bg-gradient-to-r from-[#004685] to-blue-600 text-white rounded-lg font-medium hover:from-[#003567] hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="h-5 w-5 animate-spin" />
                                        <span>Extracting Elements...</span>
                                    </>
                                ) : (
                                    <>
                                        <ArrowRight className="h-5 w-5" />
                                        <span>Extract Elements</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                );

            case 2: // Test Generation
                return (
                    <div className="p-8">
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4">
                                    Extracted Elements ({elements.length})
                                </h3>
                                <div className="max-h-64 overflow-y-auto space-y-2 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
                                    {elements.length > 0 ? (
                                        elements.map((element, index) => (
                                            <label key={index} className="flex items-center space-x-3 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 p-2 rounded">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedElements.includes(String(index))}
                                                    onChange={(e) => {
                                                        if (e.target.checked) {
                                                            setSelectedElements([...selectedElements, String(index)]);
                                                        } else {
                                                            setSelectedElements(selectedElements.filter(i => i !== String(index)));
                                                        }
                                                    }}
                                                    className="h-4 w-4 text-blue-600 rounded border-slate-300"
                                                />
                                                <div className="flex-1">
                                                    <span className="text-sm font-mono text-slate-600 dark:text-slate-400">
                                                        {element.selector || element.type || `Element ${index + 1}`}
                                                    </span>
                                                    {element.text && (
                                                        <p className="text-xs text-slate-500 dark:text-slate-500 truncate">
                                                            {element.text}
                                                        </p>
                                                    )}
                                                </div>
                                            </label>
                                        ))
                                    ) : (
                                        <p className="text-slate-500 dark:text-slate-400">No elements extracted</p>
                                    )}
                                </div>
                            </div>

                            {error && (
                                <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
                                    {error}
                                </div>
                            )}

                            <div className="flex space-x-3">
                                <button
                                    onClick={() => setCurrentStep(1)}
                                    className="px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
                                >
                                    Back
                                </button>
                                <button
                                    onClick={generateTests}
                                    disabled={isLoading || elements.length === 0}
                                    className="flex-1 px-6 py-3 bg-gradient-to-r from-[#004685] to-blue-600 text-white rounded-lg font-medium hover:from-[#003567] hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="h-5 w-5 animate-spin" />
                                            <span>Generating Tests...</span>
                                        </>
                                    ) : (
                                        <>
                                            <ArrowRight className="h-5 w-5" />
                                            <span>Generate Tests</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                );

            case 3: // Code Generation
                return (
                    <div className="p-8">
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4">
                                    Generated Tests ({tests.length})
                                </h3>
                                <div className="max-h-48 overflow-y-auto space-y-2 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
                                    {tests.length > 0 ? (
                                        tests.map((test, index) => (
                                            <div key={index} className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                                                <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                                    {test.name || `Test ${index + 1}`}
                                                </p>
                                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                                    {test.description || 'No description'}
                                                </p>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="text-slate-500 dark:text-slate-400">No tests generated</p>
                                    )}
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Target Language
                                </label>
                                <select
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value as 'python' | 'javascript')}
                                    className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                                >
                                    <option value="python">Python (Selenium)</option>
                                    <option value="javascript">JavaScript (Playwright)</option>
                                </select>
                            </div>

                            {error && (
                                <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
                                    {error}
                                </div>
                            )}

                            <div className="flex space-x-3">
                                <button
                                    onClick={() => setCurrentStep(2)}
                                    className="px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
                                >
                                    Back
                                </button>
                                <button
                                    onClick={generateCode}
                                    disabled={isLoading || tests.length === 0}
                                    className="flex-1 px-6 py-3 bg-gradient-to-r from-[#004685] to-blue-600 text-white rounded-lg font-medium hover:from-[#003567] hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="h-5 w-5 animate-spin" />
                                            <span>Generating Code...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Code2 className="h-5 w-5" />
                                            <span>Generate Code</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                );

            case 4: // Code Execution
                return (
                    <div className="p-8">
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4">
                                    Generated Code
                                </h3>
                                <div className="relative">
                                    <pre className="p-4 bg-slate-900 text-green-400 rounded-lg overflow-x-auto max-h-64 text-sm font-mono">
                                        {code || '# No code generated'}
                                    </pre>
                                    <button
                                        onClick={() => navigator.clipboard.writeText(code)}
                                        className="absolute top-2 right-2 px-3 py-1 bg-slate-800 text-slate-300 rounded text-xs hover:bg-slate-700"
                                    >
                                        Copy
                                    </button>
                                </div>
                            </div>

                            {results && (
                                <div className="p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg">
                                    <h4 className="text-sm font-medium text-green-800 dark:text-green-200 mb-2">
                                        Execution Results
                                    </h4>
                                    <pre className="text-xs text-green-700 dark:text-green-300 font-mono whitespace-pre-wrap">
                                        {JSON.stringify(results, null, 2)}
                                    </pre>
                                </div>
                            )}

                            {error && (
                                <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
                                    {error}
                                </div>
                            )}

                            <div className="flex space-x-3">
                                <button
                                    onClick={() => setCurrentStep(3)}
                                    className="px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
                                >
                                    Back
                                </button>
                                <button
                                    onClick={executeCode}
                                    disabled={isLoading || !code}
                                    className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="h-5 w-5 animate-spin" />
                                            <span>Executing...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Play className="h-5 w-5" />
                                            <span>Execute Code</span>
                                        </>
                                    )}
                                </button>
                                <button
                                    onClick={resetFlow}
                                    className="px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-all flex items-center space-x-2"
                                >
                                    <RefreshCw className="h-4 w-4" />
                                    <span>Reset</span>
                                </button>
                            </div>
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    // === MAIN RENDER (preserving original layout) ===
    return (
        <>
            {/* Inline scrollbar CSS */}
            <style>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 6px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: rgba(0,0,0,0.1);
                    border-radius: 3px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(0,70,133,0.5);
                    border-radius: 3px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: rgba(0,70,133,0.7);
                }
            `}</style>

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
        </>
    );
}