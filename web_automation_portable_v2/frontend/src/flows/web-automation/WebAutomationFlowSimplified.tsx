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
    Loader2,
    CheckSquare,
    Square,
    MousePointer,
    Eye,
    Hash,
    Type,
    Sparkles,
    Brain,
    Shield,
    Search,
    ChevronDown,
    ChevronUp,
    ChevronLeft,
    Code,
    Info,
    AlertCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

// API Configuration - Using unified API with real extraction
const API_BASE = 'http://localhost:8210/api/ui';

// Configure axios with longer timeout for element extraction
const axiosConfig = {
    timeout: 120000, // 2 minutes timeout for element extraction
    headers: {
        'Content-Type': 'application/json',
    }
};

// Step definitions
const steps = [
    { id: 1, title: 'Element Extraction', icon: Settings, description: 'Extract page elements' },
    { id: 2, title: 'Analyze Elements with AI', icon: Target, description: 'Enrich elements with AI' },
    { id: 3, title: 'Test Generation', icon: Code2, description: 'Generate test cases' },
    { id: 4, title: 'Code Generation', icon: Play, description: 'Generate automation code' },
    { id: 5, title: 'Code Execution', icon: FileText, description: 'Execute generated code' }
];

export function WebAutomationFlowSimplified() {
    // === CONSOLIDATED STATE ===
    const [currentStep, setCurrentStep] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Step 1: Element Extraction State
    const [url, setUrl] = useState('');
    const [elements, setElements] = useState<any[]>([]);

    // Step 2: AI Analysis State
    const [analyzedElements, setAnalyzedElements] = useState<any[]>([]);
    const [selectedElements, setSelectedElements] = useState<string[]>([]);

    // Step 3: Test Generation State - Enhanced UI state
    const [tests, setTests] = useState<any[]>([]);
    const [expandedElements, setExpandedElements] = useState<Set<number>>(new Set());
    const [searchTerm, setSearchTerm] = useState('');
    const [filterCategory, setFilterCategory] = useState<string>('all');

    // Step 4: Code Generation State
    const [code, setCode] = useState('');
    const [language, setLanguage] = useState<'python' | 'javascript'>('python');

    // Step 5: Execution State
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
            const response = await axios.post(`${API_BASE}/extract_elements`, { url }, axiosConfig);
            const extractedElements = response.data.elements || [];
            setElements(extractedElements);
            // Select all elements by default
            setSelectedElements(extractedElements.map((_, index) => String(index)));
            setCurrentStep(2);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to extract elements');
        } finally {
            setIsLoading(false);
        }
    };

    const analyzeWithAI = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const selectedElems = selectedElements.length > 0
                ? elements.filter((_, i) => selectedElements.includes(String(i)))
                : elements;

            const response = await axios.post(`${API_BASE}/analyze-elements`, {
                url,
                elements: selectedElems
            }, axiosConfig);
            // PageAnalysis returns enriched_elements array
            setAnalyzedElements(response.data.enriched_elements || []);
            setCurrentStep(3);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to analyze elements with AI');
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
                elements: analyzedElements.length > 0 ? analyzedElements : elements
            }, axiosConfig);
            setTests(response.data.tests || []);
            setCurrentStep(4);
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
            }, axiosConfig);
            setCode(response.data.code || '');
            setCurrentStep(5);
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
            }, axiosConfig);
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
        setAnalyzedElements([]);
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

            case 2: // Analyze Elements with AI
                return (
                    <div className="p-8">
                        <div className="space-y-6">
                            {/* Header with stats */}
                            <div>
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <h3 className="text-lg font-medium text-slate-900 dark:text-white flex items-center space-x-2">
                                            <Sparkles className="h-5 w-5 text-blue-500" />
                                            <span>Select Elements for AI Analysis</span>
                                        </h3>
                                        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                                            {elements.length} elements extracted • {selectedElements.length} selected
                                        </p>
                                    </div>

                                    {/* Selection controls */}
                                    <div className="flex items-center space-x-2">
                                        <button
                                            onClick={() => setSelectedElements(elements.map((_, i) => String(i)))}
                                            className="px-3 py-1.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors flex items-center space-x-1"
                                        >
                                            <CheckSquare className="h-3 w-3" />
                                            <span>Select All</span>
                                        </button>
                                        <button
                                            onClick={() => setSelectedElements([])}
                                            className="px-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors flex items-center space-x-1"
                                        >
                                            <Square className="h-3 w-3" />
                                            <span>Deselect All</span>
                                        </button>
                                    </div>
                                </div>

                                {/* Elements Grid */}
                                <div className="max-h-[400px] overflow-y-auto space-y-3 border border-slate-200 dark:border-slate-700 rounded-xl p-4 bg-gradient-to-br from-slate-50/50 to-blue-50/30 dark:from-slate-900/50 dark:to-blue-900/20 custom-scrollbar">
                                    {elements.length > 0 ? (
                                        <div className="grid gap-3">
                                            {elements.map((element, index) => {
                                                const isSelected = selectedElements.includes(String(index));
                                                const elementType = element.type || 'unknown';
                                                const isInteractive = element.is_interactive || elementType === 'button' || elementType === 'link' || elementType === 'input';

                                                return (
                                                    <motion.div
                                                        key={index}
                                                        initial={{ opacity: 0, y: 10 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        transition={{ duration: 0.2, delay: index * 0.02 }}
                                                        onClick={() => {
                                                            if (isSelected) {
                                                                setSelectedElements(selectedElements.filter(i => i !== String(index)));
                                                            } else {
                                                                setSelectedElements([...selectedElements, String(index)]);
                                                            }
                                                        }}
                                                        className={`
                                                            relative group cursor-pointer rounded-lg border-2 transition-all duration-200 p-4
                                                            ${isSelected
                                                                ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-blue-100/50 dark:from-blue-900/20 dark:to-blue-800/20 shadow-lg shadow-blue-500/20'
                                                                : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md'
                                                            }
                                                        `}
                                                    >
                                                        {/* Checkbox indicator */}
                                                        <div className="absolute top-3 right-3">
                                                            {isSelected ? (
                                                                <CheckCircle className="h-5 w-5 text-blue-500" />
                                                            ) : (
                                                                <div className="h-5 w-5 rounded-full border-2 border-slate-300 dark:border-slate-600 group-hover:border-blue-400 dark:group-hover:border-blue-500 transition-colors" />
                                                            )}
                                                        </div>

                                                        {/* Element content */}
                                                        <div className="pr-8">
                                                            {/* Element header */}
                                                            <div className="flex items-start space-x-3 mb-2">
                                                                {/* Element type icon */}
                                                                <div className={`
                                                                    p-2 rounded-lg flex-shrink-0
                                                                    ${isInteractive
                                                                        ? 'bg-green-100 dark:bg-green-900/30'
                                                                        : 'bg-slate-100 dark:bg-slate-700'
                                                                    }
                                                                `}>
                                                                    {elementType === 'button' || elementType === 'link' ? (
                                                                        <MousePointer className={`h-4 w-4 ${isInteractive ? 'text-green-600 dark:text-green-400' : 'text-slate-500'}`} />
                                                                    ) : elementType === 'input' || elementType === 'text_input' ? (
                                                                        <Type className={`h-4 w-4 ${isInteractive ? 'text-green-600 dark:text-green-400' : 'text-slate-500'}`} />
                                                                    ) : (
                                                                        <Hash className="h-4 w-4 text-slate-500" />
                                                                    )}
                                                                </div>

                                                                {/* Element info */}
                                                                <div className="flex-1 min-w-0">
                                                                    <div className="flex items-center space-x-2 mb-1">
                                                                        <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                                                                            {element.tag || 'Element'} #{index + 1}
                                                                        </span>
                                                                        {isInteractive && (
                                                                            <span className="px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                                                                                Interactive
                                                                            </span>
                                                                        )}
                                                                        {element.confidence && (
                                                                            <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">
                                                                                {(element.confidence * 100).toFixed(0)}%
                                                                            </span>
                                                                        )}
                                                                    </div>

                                                                    {/* Selector */}
                                                                    {element.selector && (
                                                                        <div className="flex items-center space-x-1 mb-1">
                                                                            <Code2 className="h-3 w-3 text-slate-400" />
                                                                            <code className="text-xs font-mono text-slate-600 dark:text-slate-400 truncate block">
                                                                                {element.selector}
                                                                            </code>
                                                                        </div>
                                                                    )}

                                                                    {/* Text content */}
                                                                    {element.text && (
                                                                        <div className="flex items-start space-x-1 mt-2">
                                                                            <Eye className="h-3 w-3 text-slate-400 mt-0.5 flex-shrink-0" />
                                                                            <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2">
                                                                                {element.text}
                                                                            </p>
                                                                        </div>
                                                                    )}

                                                                    {/* Classes */}
                                                                    {element.classes && element.classes.length > 0 && (
                                                                        <div className="flex flex-wrap gap-1 mt-2">
                                                                            {element.classes.slice(0, 3).map((cls, idx) => (
                                                                                <span key={idx} className="px-1.5 py-0.5 text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded">
                                                                                    .{cls}
                                                                                </span>
                                                                            ))}
                                                                            {element.classes.length > 3 && (
                                                                                <span className="px-1.5 py-0.5 text-xs text-slate-500">
                                                                                    +{element.classes.length - 3} more
                                                                                </span>
                                                                            )}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </motion.div>
                                                );
                                            })}
                                        </div>
                                    ) : (
                                        <div className="text-center py-12">
                                            <Settings className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
                                            <p className="text-slate-500 dark:text-slate-400">No elements extracted yet</p>
                                            <p className="text-sm text-slate-400 dark:text-slate-500 mt-1">Go back and extract elements from a URL</p>
                                        </div>
                                    )}
                                </div>

                                {/* Selection summary */}
                                {elements.length > 0 && (
                                    <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                        <div className="flex items-center justify-between">
                                            <p className="text-sm text-blue-700 dark:text-blue-300">
                                                {selectedElements.length === 0 ? (
                                                    <span>⚠️ Please select at least one element to analyze with AI</span>
                                                ) : selectedElements.length === 1 ? (
                                                    <span>✅ 1 element selected for AI analysis</span>
                                                ) : (
                                                    <span>✅ {selectedElements.length} elements selected for AI analysis</span>
                                                )}
                                            </p>
                                            {selectedElements.length > 10 && (
                                                <p className="text-xs text-blue-600 dark:text-blue-400">
                                                    ℹ️ Only first 10 will be analyzed
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {error && (
                                <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
                                    {error}
                                </div>
                            )}

                            {/* Action buttons */}
                            <div className="flex space-x-3">
                                <button
                                    onClick={() => setCurrentStep(1)}
                                    className="px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
                                >
                                    Back
                                </button>
                                <button
                                    onClick={analyzeWithAI}
                                    disabled={isLoading || selectedElements.length === 0}
                                    className={`
                                        flex-1 px-6 py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2
                                        ${selectedElements.length === 0
                                            ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 dark:text-slate-500 cursor-not-allowed'
                                            : 'bg-gradient-to-r from-[#004685] to-blue-600 text-white hover:from-[#003567] hover:to-blue-700 shadow-lg shadow-blue-500/25'
                                        }
                                        ${isLoading ? 'opacity-75' : ''}
                                    `}
                                    title={selectedElements.length === 0 ? 'Please select at least one element' : ''}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="h-5 w-5 animate-spin" />
                                            <span>Analyzing with AI...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="h-5 w-5" />
                                            <span>Analyze {selectedElements.length > 0 ? selectedElements.length : ''} Element{selectedElements.length !== 1 ? 's' : ''} with AI</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                );

            case 3: // Test Generation - Enhanced AI Analysis Display
                // Toggle element expansion
                const toggleElementExpand = (index: number) => {
                    const newExpanded = new Set(expandedElements);
                    if (newExpanded.has(index)) {
                        newExpanded.delete(index);
                    } else {
                        newExpanded.add(index);
                    }
                    setExpandedElements(newExpanded);
                };

                // Filter elements based on search and category
                const filteredAnalyzedElements = analyzedElements.filter((element) => {
                    const matchesSearch = searchTerm === '' ||
                        JSON.stringify(element).toLowerCase().includes(searchTerm.toLowerCase());
                    const matchesCategory = filterCategory === 'all' ||
                        (element.test_categories && element.test_categories.some((cat: any) =>
                            (typeof cat === 'string' ? cat : cat.value || cat).toLowerCase() === filterCategory.toLowerCase()
                        ));
                    return matchesSearch && matchesCategory;
                });

                // Extract unique categories from all elements
                const allCategories = Array.from(new Set(
                    analyzedElements.flatMap(el =>
                        el.test_categories?.map((cat: any) =>
                            typeof cat === 'string' ? cat : cat.value || cat
                        ) || []
                    )
                ));

                // Calculate statistics
                const stats = {
                    totalElements: analyzedElements.length,
                    highConfidence: analyzedElements.filter(e => e.confidence_score && e.confidence_score > 0.8).length,
                    withValidation: analyzedElements.filter(e => e.llm_analysis?.validation_rules?.length > 0).length,
                    interactive: analyzedElements.filter(e => e.llm_analysis?.interaction_type).length,
                    withTests: analyzedElements.filter(e => e.test_scenarios?.length > 0).length,
                };

                return (
                    <div className="p-8">
                        <div className="space-y-6">
                            {/* Enhanced Header with Statistics Dashboard */}
                            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center space-x-2">
                                            <Brain className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                                            <span>AI Analysis Results</span>
                                        </h3>
                                        <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
                                            {analyzedElements.length > 0
                                                ? `Successfully enriched ${analyzedElements.length} elements with AI insights`
                                                : `${elements.length} elements ready for test generation`
                                            }
                                        </p>
                                    </div>
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-full shadow-lg"
                                    >
                                        <span className="text-sm font-semibold">AI Powered</span>
                                    </motion.div>
                                </div>

                                {/* Statistics Cards */}
                                {analyzedElements.length > 0 && (
                                    <div className="grid grid-cols-5 gap-3 mt-4">
                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.1 }}
                                            className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700"
                                        >
                                            <div className="flex items-center space-x-2">
                                                <Eye className="h-4 w-4 text-blue-500" />
                                                <div>
                                                    <p className="text-xs text-slate-500 dark:text-slate-400">Total</p>
                                                    <p className="text-lg font-bold text-slate-900 dark:text-white">{stats.totalElements}</p>
                                                </div>
                                            </div>
                                        </motion.div>

                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.2 }}
                                            className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700"
                                        >
                                            <div className="flex items-center space-x-2">
                                                <Shield className="h-4 w-4 text-green-500" />
                                                <div>
                                                    <p className="text-xs text-slate-500 dark:text-slate-400">High Conf.</p>
                                                    <p className="text-lg font-bold text-slate-900 dark:text-white">{stats.highConfidence}</p>
                                                </div>
                                            </div>
                                        </motion.div>

                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.3 }}
                                            className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700"
                                        >
                                            <div className="flex items-center space-x-2">
                                                <CheckCircle className="h-4 w-4 text-purple-500" />
                                                <div>
                                                    <p className="text-xs text-slate-500 dark:text-slate-400">Validated</p>
                                                    <p className="text-lg font-bold text-slate-900 dark:text-white">{stats.withValidation}</p>
                                                </div>
                                            </div>
                                        </motion.div>

                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.4 }}
                                            className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700"
                                        >
                                            <div className="flex items-center space-x-2">
                                                <MousePointer className="h-4 w-4 text-orange-500" />
                                                <div>
                                                    <p className="text-xs text-slate-500 dark:text-slate-400">Interactive</p>
                                                    <p className="text-lg font-bold text-slate-900 dark:text-white">{stats.interactive}</p>
                                                </div>
                                            </div>
                                        </motion.div>

                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.5 }}
                                            className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700"
                                        >
                                            <div className="flex items-center space-x-2">
                                                <FileText className="h-4 w-4 text-indigo-500" />
                                                <div>
                                                    <p className="text-xs text-slate-500 dark:text-slate-400">With Tests</p>
                                                    <p className="text-lg font-bold text-slate-900 dark:text-white">{stats.withTests}</p>
                                                </div>
                                            </div>
                                        </motion.div>
                                    </div>
                                )}
                            </div>

                            {/* Search and Filter Controls */}
                            {analyzedElements.length > 0 && (
                                <div className="flex space-x-4">
                                    <div className="flex-1 relative">
                                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                                        <input
                                            type="text"
                                            placeholder="Search elements..."
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                            className="w-full pl-10 pr-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <select
                                        value={filterCategory}
                                        onChange={(e) => setFilterCategory(e.target.value)}
                                        className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="all">All Categories</option>
                                        {allCategories.map(cat => (
                                            <option key={cat} value={cat.toLowerCase()}>{cat}</option>
                                        ))}
                                    </select>
                                    <button
                                        onClick={() => setExpandedElements(new Set(filteredAnalyzedElements.map((_, i) => i)))}
                                        className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                                    >
                                        <ChevronDown className="h-4 w-4" />
                                        <span className="ml-2">Expand All</span>
                                    </button>
                                    <button
                                        onClick={() => setExpandedElements(new Set())}
                                        className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                                    >
                                        <ChevronUp className="h-4 w-4" />
                                        <span className="ml-2">Collapse All</span>
                                    </button>
                                </div>
                            )}

                            {/* Enhanced AI-Enriched Elements Display */}
                            <div className="max-h-[500px] overflow-y-auto space-y-4 custom-scrollbar">
                                {filteredAnalyzedElements.length > 0 ? (
                                    filteredAnalyzedElements.map((element, index) => (
                                        <motion.div
                                            key={index}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.05 }}
                                            className={`group relative overflow-hidden rounded-xl border transition-all ${
                                                expandedElements.has(index)
                                                    ? 'border-blue-400 dark:border-blue-600 shadow-lg'
                                                    : 'border-slate-200 dark:border-slate-700 hover:shadow-md'
                                            }`}
                                        >
                                            {/* Gradient Background */}
                                            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-white to-purple-50/50 dark:from-blue-900/10 dark:via-slate-900 dark:to-purple-900/10" />

                                            {/* Content */}
                                            <div className="relative p-5">
                                                {/* Header */}
                                                <div
                                                    onClick={() => toggleElementExpand(index)}
                                                    className="flex justify-between items-start cursor-pointer"
                                                >
                                                    <div className="flex-1">
                                                        <div className="flex items-center space-x-3">
                                                            {/* Element Type Icon */}
                                                            <div className={`p-2 rounded-lg ${
                                                                element.llm_analysis?.interaction_type === 'click'
                                                                    ? 'bg-blue-100 dark:bg-blue-900/30'
                                                                    : element.llm_analysis?.interaction_type === 'input'
                                                                    ? 'bg-purple-100 dark:bg-purple-900/30'
                                                                    : 'bg-slate-100 dark:bg-slate-800'
                                                            }`}>
                                                                {element.llm_analysis?.interaction_type === 'click' ? (
                                                                    <MousePointer className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                                                ) : element.llm_analysis?.interaction_type === 'input' ? (
                                                                    <Type className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                                                                ) : (
                                                                    <Code className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                                                                )}
                                                            </div>

                                                            <div>
                                                                <p className="text-base font-semibold text-slate-900 dark:text-white flex items-center space-x-2">
                                                                    <span>{element.base_element?.tag_name || element.tag || 'Element'}</span>
                                                                    <span className="text-slate-400">#{index + 1}</span>
                                                                </p>
                                                                <p className="text-xs font-mono text-slate-500 dark:text-slate-400 mt-1">
                                                                    {element.base_element?.css_selector || element.selector || 'No selector'}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Badges and Expand Icon */}
                                                    <div className="flex items-center space-x-2">
                                                        {element.confidence_score && (
                                                            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                                                element.confidence_score > 0.8
                                                                    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                                                                    : element.confidence_score > 0.5
                                                                    ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
                                                                    : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                                                            }`}>
                                                                {(element.confidence_score * 100).toFixed(0)}%
                                                            </div>
                                                        )}
                                                        <ChevronDown className={`h-5 w-5 text-slate-400 transition-transform ${
                                                            expandedElements.has(index) ? 'rotate-180' : ''
                                                        }`} />
                                                    </div>
                                                </div>

                                                {/* Quick Info Bar */}
                                                <div className="mt-3 flex flex-wrap items-center gap-2">
                                                    {element.llm_analysis?.purpose && (
                                                        <div className="flex items-center space-x-1 px-2 py-1 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                                            <Target className="h-3 w-3 text-blue-600 dark:text-blue-400" />
                                                            <span className="text-xs text-blue-700 dark:text-blue-300">{element.llm_analysis.purpose}</span>
                                                        </div>
                                                    )}
                                                    {element.test_categories && element.test_categories.length > 0 && (
                                                        element.test_categories.slice(0, 3).map((cat: any, idx: number) => (
                                                            <span key={idx} className="px-2 py-1 text-xs bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 text-green-700 dark:text-green-400 rounded-lg font-medium">
                                                                {typeof cat === 'string' ? cat : cat.value || cat}
                                                            </span>
                                                        ))
                                                    )}
                                                </div>

                                                {/* Expanded Content */}
                                                {expandedElements.has(index) && (
                                                    <motion.div
                                                        initial={{ opacity: 0, height: 0 }}
                                                        animate={{ opacity: 1, height: 'auto' }}
                                                        exit={{ opacity: 0, height: 0 }}
                                                        className="mt-4 space-y-4 border-t border-slate-200 dark:border-slate-700 pt-4"
                                                    >
                                                        {/* AI Analysis Section */}
                                                        {element.llm_analysis && Object.keys(element.llm_analysis).length > 0 && (
                                                            <div className="bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 rounded-lg p-4">
                                                                <h4 className="text-sm font-semibold text-indigo-900 dark:text-indigo-300 mb-3 flex items-center">
                                                                    <Brain className="h-4 w-4 mr-2" />
                                                                    AI Analysis Insights
                                                                </h4>
                                                                <div className="space-y-2">
                                                                    {element.llm_analysis.interaction_type && (
                                                                        <div className="flex items-start space-x-2">
                                                                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400 min-w-[100px]">Interaction:</span>
                                                                            <span className="text-xs text-slate-700 dark:text-slate-300 font-mono bg-white/50 dark:bg-slate-800/50 px-2 py-1 rounded">
                                                                                {element.llm_analysis.interaction_type}
                                                                            </span>
                                                                        </div>
                                                                    )}
                                                                    {element.llm_analysis.validation_rules && element.llm_analysis.validation_rules.length > 0 && (
                                                                        <div className="flex items-start space-x-2">
                                                                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400 min-w-[100px]">Validations:</span>
                                                                            <div className="flex flex-wrap gap-1">
                                                                                {element.llm_analysis.validation_rules.map((rule: string, idx: number) => (
                                                                                    <span key={idx} className="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 px-2 py-1 rounded">
                                                                                        {rule}
                                                                                    </span>
                                                                                ))}
                                                                            </div>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        )}

                                                        {/* Test Scenarios Section */}
                                                        {element.test_scenarios && element.test_scenarios.length > 0 && (
                                                            <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-4">
                                                                <h4 className="text-sm font-semibold text-green-900 dark:text-green-300 mb-3 flex items-center">
                                                                    <FileText className="h-4 w-4 mr-2" />
                                                                    Test Scenarios ({element.test_scenarios.length})
                                                                </h4>
                                                                <ul className="space-y-2">
                                                                    {element.test_scenarios.map((scenario: string, idx: number) => (
                                                                        <li key={idx} className="flex items-start space-x-2">
                                                                            <CheckCircle className="h-3 w-3 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
                                                                            <span className="text-xs text-slate-700 dark:text-slate-300">{scenario}</span>
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        )}

                                                        {/* Context Information */}
                                                        {element.context && (
                                                            <div className="bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20 rounded-lg p-4">
                                                                <h4 className="text-sm font-semibold text-orange-900 dark:text-orange-300 mb-3 flex items-center">
                                                                    <Info className="h-4 w-4 mr-2" />
                                                                    Context Information
                                                                </h4>
                                                                <div className="grid grid-cols-2 gap-3">
                                                                    {element.context.semantic_role && (
                                                                        <div>
                                                                            <p className="text-xs text-slate-500 dark:text-slate-400">Semantic Role</p>
                                                                            <p className="text-sm font-medium text-slate-700 dark:text-slate-300">{element.context.semantic_role}</p>
                                                                        </div>
                                                                    )}
                                                                    {element.context.interaction_likelihood !== undefined && (
                                                                        <div>
                                                                            <p className="text-xs text-slate-500 dark:text-slate-400">Interaction Likelihood</p>
                                                                            <div className="flex items-center space-x-2">
                                                                                <div className="flex-1 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                                                                    <div
                                                                                        className="h-full bg-gradient-to-r from-orange-400 to-yellow-400"
                                                                                        style={{ width: `${element.context.interaction_likelihood * 100}%` }}
                                                                                    />
                                                                                </div>
                                                                                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                                                                    {(element.context.interaction_likelihood * 100).toFixed(0)}%
                                                                                </span>
                                                                            </div>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </motion.div>
                                                )}
                                            </div>
                                        </motion.div>
                                    ))
                                ) : analyzedElements.length === 0 && elements.length > 0 ? (
                                    /* Fallback display for non-analyzed elements */
                                    <div className="text-center py-12">
                                        <Brain className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
                                        <p className="text-slate-500 dark:text-slate-400">
                                            {elements.length} elements extracted and ready for AI analysis
                                        </p>
                                        <p className="text-sm text-slate-400 dark:text-slate-500 mt-2">
                                            Go back to Step 2 to analyze elements with AI
                                        </p>
                                    </div>
                                ) : (
                                    <div className="text-center py-12">
                                        <Eye className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
                                        <p className="text-slate-500 dark:text-slate-400">
                                            No elements to display
                                        </p>
                                    </div>
                                )}
                            </div>

                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg"
                                >
                                    <div className="flex items-center space-x-2">
                                        <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
                                        <p className="text-red-600 dark:text-red-400">{error}</p>
                                    </div>
                                </motion.div>
                            )}

                            <div className="flex space-x-3">
                                <button
                                    onClick={() => setCurrentStep(2)}
                                    className="px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-all flex items-center space-x-2"
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                    <span>Back</span>
                                </button>
                                <button
                                    onClick={generateTests}
                                    disabled={isLoading || (analyzedElements.length === 0 && elements.length === 0)}
                                    className="flex-1 px-6 py-3 bg-gradient-to-r from-[#004685] to-blue-600 text-white rounded-lg font-medium hover:from-[#003567] hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="h-5 w-5 animate-spin" />
                                            <span>Generating Tests...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="h-5 w-5" />
                                            <span>Generate Test Scenarios</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                );

            case 4: // Code Generation
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
                                    onClick={() => setCurrentStep(3)}
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

            case 5: // Code Execution
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
                                    onClick={() => setCurrentStep(4)}
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