import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Monitor, Settings, Play, Menu, X, CheckCircle, Globe, Code, Zap, Copy, Eye, AlertCircle, ChevronRight, FileJson, FileSpreadsheet, RefreshCw, Shield, Terminal, Download, Database, ArrowLeft } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import testUrlsData from './testUrls.json';

const steps = [
    { id: 1, title: 'Extract Elements', icon: Globe },
    { id: 2, title: 'Generate Tests', icon: Zap },
    { id: 3, title: 'Generate Code', icon: Code },
    { id: 4, title: 'Execute Tests', icon: Play }
];

export function WebAutomationFlowVertical() {
    const [currentStep, setCurrentStep] = useState(1);
    const [formData, setFormData] = useState({ url: 'https://www.example.com' });
    // const [isExecuting, setIsExecuting] = useState(false);  // Unused - commented for future use
    const [isExtracting, setIsExtracting] = useState(false);
    const [extractedElements, setExtractedElements] = useState<any>(null);
    // const [results, setResults] = useState<any>(null);  // Unused - commented for future use
    const [completedSteps, setCompletedSteps] = useState<number[]>([]);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [viewMode, setViewMode] = useState<'executive' | 'developer'>('executive');
    const [copiedJson, setCopiedJson] = useState(false);
    const [copiedTestsJson, setCopiedTestsJson] = useState(false);
    const [extractionPhase, setExtractionPhase] = useState<'idle' | 'connecting' | 'navigating' | 'extracting' | 'analyzing' | 'complete' | 'error'>('idle');
    const [extractionProgress, setExtractionProgress] = useState(0);
    const [extractionError, setExtractionError] = useState<string | null>(null);
    const [retryCount, setRetryCount] = useState(0);
    const [generatedTests, setGeneratedTests] = useState<any>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationPhase, setGenerationPhase] = useState<'idle' | 'preparing' | 'functional' | 'validation' | 'edge_cases' | 'security' | 'finalizing' | 'complete' | 'error'>('idle');
    const [generationProgress, setGenerationProgress] = useState(0);
    const [selectedCategories, setSelectedCategories] = useState<string[]>(['functional', 'validation', 'edge_cases']);
    const [autoGeneratingTests, setAutoGeneratingTests] = useState(false);
    const [generatedCode, setGeneratedCode] = useState<any>(null);
    const [isGeneratingCode, setIsGeneratingCode] = useState(false);
    const [codeGenerationPhase, setCodeGenerationPhase] = useState<'idle' | 'preparing' | 'page_objects' | 'test_files' | 'configuration' | 'finalizing' | 'complete' | 'error'>('idle');
    const [codeGenerationProgress, setCodeGenerationProgress] = useState(0);
    const [copiedCodeJson, setCopiedCodeJson] = useState(false);
    const [autoGeneratingCode, setAutoGeneratingCode] = useState(false);
    const [selectedFile, setSelectedFile] = useState<{ filename: string; content: string } | null>(null);
    const [testResults, setTestResults] = useState<any>(null);
    const [isExecutingTests, setIsExecutingTests] = useState(false);
    const [executionPhase, setExecutionPhase] = useState<'idle' | 'preparing' | 'installing' | 'running' | 'collecting' | 'complete' | 'error'>('idle');
    const [executionProgress, setExecutionProgress] = useState(0);
    const [executionLogs, setExecutionLogs] = useState<string[]>([]);
    const [showLogs, setShowLogs] = useState(false);
    const [autoExecutingTests, setAutoExecutingTests] = useState(false);

    // Auto-trigger test generation when reaching step 2
    useEffect(() => {
        if (currentStep === 2 && extractedElements && !generatedTests && !isGenerating && !autoGeneratingTests) {
            setAutoGeneratingTests(true);
            // Use default categories
            setSelectedCategories(['functional', 'validation', 'edge_cases']);
            // Start generation automatically
            handleGenerateTests();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentStep, extractedElements, generatedTests, isGenerating, autoGeneratingTests]);

    // Auto-trigger code generation when reaching step 3
    useEffect(() => {
        if (currentStep === 3 && extractedElements && generatedTests && !generatedCode && !isGeneratingCode && !autoGeneratingCode) {
            setAutoGeneratingCode(true);
            // Start code generation automatically
            handleGenerateCode();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentStep, extractedElements, generatedTests, generatedCode, isGeneratingCode, autoGeneratingCode]);

    // Auto-trigger test execution when reaching step 4
    useEffect(() => {
        if (currentStep === 4 && generatedCode && !testResults && !isExecutingTests && !autoExecutingTests) {
            setAutoExecutingTests(true);
            // Start test execution automatically
            handleExecuteTests();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentStep, generatedCode, testResults, isExecutingTests, autoExecutingTests]);

    const handleCopyJson = () => {
        if (extractedElements) {
            navigator.clipboard.writeText(JSON.stringify(extractedElements, null, 2));
            setCopiedJson(true);
            setTimeout(() => setCopiedJson(false), 2000);
        }
    };

    const handleCopyTestsJson = () => {
        if (generatedTests) {
            navigator.clipboard.writeText(JSON.stringify(generatedTests, null, 2));
            setCopiedTestsJson(true);
            setTimeout(() => setCopiedTestsJson(false), 2000);
        }
    };

    const handleExportTestsJson = () => {
        if (generatedTests) {
            const dataStr = JSON.stringify(generatedTests, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `tests_${new URL(formData.url).hostname}_${Date.now()}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
    };

    const handleExportTestsCsv = () => {
        if (generatedTests && generatedTests.features) {
            // Create CSV header
            const headers = ['Feature', 'Category', 'Scenario', 'Type', 'Steps Count', 'Tags'];
            const rows: string[][] = [];
            
            Object.entries(generatedTests.features).forEach(([category, feature]: [string, any]) => {
                if (feature.scenarios) {
                    feature.scenarios.forEach((scenario: any, idx: number) => {
                        rows.push([
                            feature.title || `${category} Tests`,
                            category.replace('_', ' '),
                            scenario.title || scenario.name || `Scenario ${idx + 1}`,
                            scenario.type || 'Test',
                            (scenario.steps?.length || 0).toString(),
                            (scenario.tags || []).join('; ')
                        ]);
                    });
                }
            });
            
            // Convert to CSV format
            const csvContent = [
                headers.join(','),
                ...rows.map(row => row.map(field => `"${field.replace(/"/g, '""')}"`).join(','))
            ].join('\n');
            
            // Create and download file
            const dataBlob = new Blob([csvContent], { type: 'text/csv' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `tests_${new URL(formData.url).hostname}_${Date.now()}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
    };

    const handleCopyCodeJson = () => {
        if (generatedCode) {
            navigator.clipboard.writeText(JSON.stringify(generatedCode, null, 2));
            setCopiedCodeJson(true);
            setTimeout(() => setCopiedCodeJson(false), 2000);
        }
    };

    const handleExecuteTests = async () => {
        if (!generatedCode || !generatedCode.generated_files) return;
        
        setIsExecutingTests(true);
        setExecutionPhase('preparing');
        setExecutionProgress(10);
        setExecutionLogs(['Starting test execution...']);
        
        try {
            // Phase 1: Preparing
            await new Promise(resolve => setTimeout(resolve, 500));
            setExecutionPhase('installing');
            setExecutionProgress(25);
            setExecutionLogs(prev => [...prev, 'Installing test dependencies...']);
            
            // Phase 2: Installing
            await new Promise(resolve => setTimeout(resolve, 500));
            setExecutionPhase('running');
            setExecutionProgress(50);
            setExecutionLogs(prev => [...prev, 'Running tests...']);
            
            // Make API call to execute tests
            const response = await fetch('http://localhost:5175/api/execute-tests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    generated_files: generatedCode.generated_files,
                    url: formData.url,
                    test_type: 'pytest'
                }),
            });
            
            const data = await response.json();
            
            // Phase 3: Collecting results
            setExecutionPhase('collecting');
            setExecutionProgress(75);
            setExecutionLogs(prev => [...prev, ...data.logs]);
            
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Phase 4: Complete
            setExecutionPhase('complete');
            setExecutionProgress(100);
            setTestResults(data);
            
            // Mark step as completed
            if (!completedSteps.includes(5)) {
                setCompletedSteps([...completedSteps, 5]);
            }
            
        } catch (error: any) {
            console.error('Error executing tests:', error);
            setExecutionPhase('error');
            setExecutionLogs(prev => [...prev, `Error: ${error.message}`]);
        } finally {
            setTimeout(() => {
                setIsExecutingTests(false);
                setExecutionPhase('idle');
                setExecutionProgress(0);
            }, 1000);
        }
    };

    const handleGenerateCode = async () => {
        setIsGeneratingCode(true);
        setCodeGenerationPhase('preparing');
        setCodeGenerationProgress(10);
        
        try {
            // Simulate preparation phase
            await new Promise(resolve => setTimeout(resolve, 500));
            setCodeGenerationPhase('page_objects');
            setCodeGenerationProgress(20);
            
            // Call backend to generate code
            const response = await fetch('http://localhost:5175/api/generate-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    extraction_data: extractedElements,
                    test_data: generatedTests,
                    code_type: 'pytest',
                    language: 'python'
                })
            });
            
            // Update progress during generation
            setTimeout(() => {
                if (isGeneratingCode) {
                    setCodeGenerationPhase('test_files');
                    setCodeGenerationProgress(50);
                }
            }, 2000);
            
            setTimeout(() => {
                if (isGeneratingCode) {
                    setCodeGenerationPhase('configuration');
                    setCodeGenerationProgress(75);
                }
            }, 4000);
            
            setTimeout(() => {
                if (isGeneratingCode) {
                    setCodeGenerationPhase('finalizing');
                    setCodeGenerationProgress(90);
                }
            }, 6000);
            
            if (!response.ok) {
                throw new Error('Failed to generate code');
            }
            
            const data = await response.json();
            setCodeGenerationPhase('complete');
            setCodeGenerationProgress(100);
            
            await new Promise(resolve => setTimeout(resolve, 500));
            
            setGeneratedCode(data);
            setCompletedSteps([...completedSteps, currentStep]);
            if (currentStep < 4) {
                setCurrentStep(currentStep + 1);
            }
            
        } catch (error: any) {
            console.error('Error generating code:', error);
            setCodeGenerationPhase('error');
            // Don't reset state to allow retry
        } finally {
            if (codeGenerationPhase !== 'error') {
                setIsGeneratingCode(false);
                setCodeGenerationPhase('idle');
                setCodeGenerationProgress(0);
            }
        }
    };

    const handleExportJson = () => {
        if (extractedElements) {
            const dataStr = JSON.stringify(extractedElements, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `extraction_${new URL(formData.url).hostname}_${Date.now()}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
    };

    const handleRetryExtraction = () => {
        setExtractionError(null);
        setExtractionPhase('idle');
        setIsExtracting(false);
        setExtractionProgress(0);
        // Retry the extraction
        setTimeout(() => handleStepComplete(), 100);
    };

    const handleExportCsv = () => {
        if (extractedElements && extractedElements.elements) {
            // Create CSV header
            const headers = ['Element ID', 'Tag Name', 'Category', 'Description', 'Test Priority', 'Selector'];
            const rows = extractedElements.elements.map((elem: any, idx: number) => [
                idx + 1,
                elem.tag_name || '',
                elem.category || '',
                elem.description || elem.text || '',
                elem.test_priority || 'Normal',
                elem.selector || elem.id || ''
            ]);
            
            // Convert to CSV format
            const csvContent = [
                headers.join(','),
                ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
            ].join('\n');
            
            const dataBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `extraction_${new URL(formData.url).hostname}_${Date.now()}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
    };

    const handleGenerateTests = async () => {
        setIsGenerating(true);
        setGenerationPhase('preparing');
        setGenerationProgress(10);
        
        try {
            // Simulate preparation phase
            await new Promise(resolve => setTimeout(resolve, 500));
            setGenerationPhase('functional');
            setGenerationProgress(20);
            
            // Call backend to generate tests
            const response = await fetch('http://localhost:5175/api/generate-tests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    extraction_data: extractedElements,
                    test_categories: selectedCategories
                })
            });
            
            // Update progress during generation
            setTimeout(() => {
                if (isGenerating) {
                    setGenerationPhase('validation');
                    setGenerationProgress(40);
                }
            }, 2000);
            
            setTimeout(() => {
                if (isGenerating) {
                    setGenerationPhase('edge_cases');
                    setGenerationProgress(60);
                }
            }, 4000);
            
            setTimeout(() => {
                if (isGenerating) {
                    setGenerationPhase('finalizing');
                    setGenerationProgress(80);
                }
            }, 6000);
            
            if (!response.ok) {
                throw new Error('Failed to generate tests');
            }
            
            const data = await response.json();
            setGenerationPhase('complete');
            setGenerationProgress(100);
            
            await new Promise(resolve => setTimeout(resolve, 500));
            
            setGeneratedTests(data);
            setCompletedSteps([...completedSteps, currentStep]);
            if (currentStep < 4) {
                setCurrentStep(currentStep + 1);
            }
        } catch (error: any) {
            console.error('Error generating tests:', error);
            setGenerationPhase('error');
            alert('Failed to generate tests. Please try again.');
        } finally {
            setIsGenerating(false);
            setGenerationPhase('idle');
            setGenerationProgress(0);
        }
    };

    // Unused function - replaced by handleExecuteTests
    // const handleExecute = () => {
    //     setIsExecuting(true);
    //     setTimeout(() => {
    //         setIsExecuting(false);
    //         setResults({ success: true, tests: 10, passed: 10 });
    //         setCompletedSteps([...completedSteps, currentStep]);
    //         if (currentStep < 4) {
    //             setCurrentStep(currentStep + 1);
    //         }
    //     }, 2000);
    // };

    const handleStepComplete = async () => {
        // For step 1 (Extract Elements), call the backend to extract elements
        if (currentStep === 1) {
            setIsExtracting(true);
            setExtractionPhase('connecting');
            setExtractionProgress(0);
            
            try {
                // Simulate connection phase
                await new Promise(resolve => setTimeout(resolve, 500));
                setExtractionPhase('navigating');
                setExtractionProgress(20);
                
                // Start the actual extraction
                const extractionPromise = fetch('http://localhost:5175/api/extract-elements', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: formData.url,
                        headless: true,
                        analyze_with_llm: true
                    })
                });
                
                // Update phases while waiting
                setTimeout(() => {
                    if (isExtracting) {
                        setExtractionPhase('extracting');
                        setExtractionProgress(40);
                    }
                }, 2000);
                
                setTimeout(() => {
                    if (isExtracting) {
                        setExtractionPhase('analyzing');
                        setExtractionProgress(70);
                    }
                }, 5000);
                
                const response = await extractionPromise;
                
                if (!response.ok) {
                    throw new Error('Failed to extract elements');
                }
                
                setExtractionProgress(90);
                const data = await response.json();
                
                setExtractionPhase('complete');
                setExtractionProgress(100);
                
                // Small delay to show completion
                await new Promise(resolve => setTimeout(resolve, 500));
                
                setExtractedElements(data);
                // Don't auto-progress to next step, stay in step 1 to show results
                // User will manually proceed via the Continue button
            } catch (error: any) {
                console.error('Error extracting elements:', error);
                setExtractionPhase('error');
                setExtractionError(error.message || 'Failed to extract elements');
                setRetryCount(retryCount + 1);
                // Don't reset isExtracting here to allow retry
            } finally {
                if (extractionPhase !== 'error') {
                    setIsExtracting(false);
                    setExtractionPhase('idle');
                    setExtractionProgress(0);
                }
            }
        } else {
            // For other steps, use the original logic (but with updated step count)
            setCompletedSteps([...completedSteps, currentStep]);
            if (currentStep < 4) {
                setCurrentStep(currentStep + 1);
            }
        }
        
        // Auto-close sidebar on mobile after action
        if (window.innerWidth < 768) {
            setSidebarOpen(false);
        }
    };

    const renderStepContent = () => {
        switch (currentStep) {
            case 1:
                return (
                    <div className="space-y-8">
                        {/* URL Input Section */}
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-xl font-bold text-slate-900 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                    Extract Elements
                                </h3>
                                <p className="text-sm text-slate-600 mt-2">
                                    Enter the URL of the web application you want to test and extract its elements
                                </p>
                            </div>
                            
                            {/* URL Input - Enhanced */}
                            <div className="space-y-3">
                                <label className="text-sm font-semibold text-slate-700">Target URL</label>
                                <div className="relative">
                                    <input
                                        type="url"
                                        placeholder="https://www.example.com"
                                        className="w-full px-4 py-4 pr-12 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 bg-white/70 backdrop-blur-sm shadow-sm hover:shadow-md"
                                        value={formData.url}
                                        onChange={(e) => setFormData({ url: e.target.value })}
                                    />
                                    <Globe className="absolute right-4 top-4 h-5 w-5 text-slate-400" />
                                </div>
                            </div>
                            
                            {/* Quick Select - Enhanced */}
                            <div className="space-y-3">
                                <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Popular test sites:</p>
                                <div className="flex flex-wrap gap-2">
                                    {testUrlsData.testUrls.map((site) => (
                                        <button
                                            key={site.id}
                                            onClick={() => setFormData({ url: site.url })}
                                            className={`px-4 py-2 text-xs font-medium rounded-full transition-all duration-300 border ${
                                                formData.url === site.url
                                                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white border-blue-400 shadow-lg scale-105'
                                                    : 'bg-white/80 text-slate-700 border-slate-200 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 hover:border-blue-300 hover:scale-105 hover:shadow-md backdrop-blur-sm'
                                            }`}
                                        >
                                            {site.name}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            
                            {/* Selected URL Display - Enhanced */}
                            {formData.url && formData.url !== 'https://www.example.com' && (
                                <div className="bg-gradient-to-r from-slate-50 to-blue-50 border border-slate-200 rounded-xl p-4 backdrop-blur-sm">
                                    <div className="flex items-center space-x-3">
                                        <div className="bg-blue-100 rounded-full p-2">
                                            <Globe className="h-4 w-4 text-blue-600" />
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-xs font-medium text-slate-500">Selected URL</p>
                                            <p className="text-sm text-slate-700 break-all font-mono">{formData.url}</p>
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {/* Extraction Button or Progress */}
                            {isExtracting ? (
                                <div className="space-y-4">
                                    {extractionPhase === 'error' ? (
                                        /* Error State with Enhanced Styling */
                                        <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl p-6 backdrop-blur-sm">
                                            <div className="flex items-start space-x-4 mb-4">
                                                <div className="bg-red-100 rounded-full p-2">
                                                    <AlertCircle className="h-5 w-5 text-red-600" />
                                                </div>
                                                <div className="flex-1">
                                                    <p className="text-sm font-semibold text-red-900">Extraction Failed</p>
                                                    <p className="text-xs text-red-700 mt-1">{extractionError}</p>
                                                    {retryCount > 0 && (
                                                        <p className="text-xs text-red-600 mt-1">Attempt {retryCount} failed</p>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="flex space-x-3">
                                                <button
                                                    onClick={handleRetryExtraction}
                                                    className="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white py-3 px-4 rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 text-sm font-semibold flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-105"
                                                >
                                                    <RefreshCw className="h-4 w-4 mr-2" />
                                                    Retry Extraction
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        setIsExtracting(false);
                                                        setExtractionPhase('idle');
                                                        setExtractionError(null);
                                                        setExtractionProgress(0);
                                                    }}
                                                    className="flex-1 bg-white border border-slate-300 text-slate-700 py-3 px-4 rounded-xl hover:bg-slate-50 transition-all duration-300 text-sm font-semibold backdrop-blur-sm"
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        /* Enhanced Progress Display */
                                        <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6 backdrop-blur-sm">
                                            <div className="flex items-center justify-between mb-4">
                                                <div className="flex items-center space-x-4">
                                                    <div className="relative">
                                                        <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent"></div>
                                                        <div className="absolute inset-0 rounded-full bg-blue-100/30"></div>
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-semibold text-blue-900">
                                                            {extractionPhase === 'connecting' && 'Connecting to browser...'}
                                                            {extractionPhase === 'navigating' && `Navigating to ${new URL(formData.url).hostname}...`}
                                                            {extractionPhase === 'extracting' && 'Extracting page elements...'}
                                                            {extractionPhase === 'analyzing' && 'Analyzing with AI...'}
                                                            {extractionPhase === 'complete' && 'Processing complete!'}
                                                        </p>
                                                        <p className="text-xs text-blue-600 mt-1 font-medium">
                                                            {extractionPhase === 'connecting' && 'Initializing headless browser'}
                                                            {extractionPhase === 'navigating' && 'Loading page content'}
                                                            {extractionPhase === 'extracting' && 'Identifying testable elements'}
                                                            {extractionPhase === 'analyzing' && 'Generating test scenarios'}
                                                            {extractionPhase === 'complete' && 'Finalizing results'}
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                                        {extractionProgress}%
                                                    </span>
                                                </div>
                                            </div>
                                            
                                            {/* Enhanced Progress Bar */}
                                            <div className="w-full bg-white/50 rounded-full h-3 overflow-hidden backdrop-blur-sm">
                                                <div 
                                                    className="bg-gradient-to-r from-blue-500 via-purple-500 to-blue-600 h-full rounded-full transition-all duration-500 ease-out shadow-sm"
                                                    style={{ width: `${extractionProgress}%` }}
                                                />
                                            </div>
                                            
                                            {/* Enhanced Phase Indicators */}
                                            <div className="flex justify-between mt-4 px-1">
                                                <div className={`flex flex-col items-center transition-all duration-300 ${extractionProgress >= 0 ? 'text-blue-600' : 'text-slate-400'}`}>
                                                    <div className={`w-3 h-3 rounded-full transition-all duration-300 ${extractionProgress >= 0 ? 'bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg' : 'bg-slate-300'}`} />
                                                    <span className="text-xs mt-1 font-medium">Connect</span>
                                                </div>
                                                <div className={`flex flex-col items-center transition-all duration-300 ${extractionProgress >= 20 ? 'text-blue-600' : 'text-slate-400'}`}>
                                                    <div className={`w-3 h-3 rounded-full transition-all duration-300 ${extractionProgress >= 20 ? 'bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg' : 'bg-slate-300'}`} />
                                                    <span className="text-xs mt-1 font-medium">Navigate</span>
                                                </div>
                                                <div className={`flex flex-col items-center transition-all duration-300 ${extractionProgress >= 40 ? 'text-blue-600' : 'text-slate-400'}`}>
                                                    <div className={`w-3 h-3 rounded-full transition-all duration-300 ${extractionProgress >= 40 ? 'bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg' : 'bg-slate-300'}`} />
                                                    <span className="text-xs mt-1 font-medium">Extract</span>
                                                </div>
                                                <div className={`flex flex-col items-center transition-all duration-300 ${extractionProgress >= 70 ? 'text-blue-600' : 'text-slate-400'}`}>
                                                    <div className={`w-3 h-3 rounded-full transition-all duration-300 ${extractionProgress >= 70 ? 'bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg' : 'bg-slate-300'}`} />
                                                    <span className="text-xs mt-1 font-medium">Analyze</span>
                                                </div>
                                                <div className={`flex flex-col items-center transition-all duration-300 ${extractionProgress >= 100 ? 'text-emerald-600' : 'text-slate-400'}`}>
                                                    <div className={`w-3 h-3 rounded-full transition-all duration-300 ${extractionProgress >= 100 ? 'bg-gradient-to-r from-emerald-500 to-teal-500 shadow-lg' : 'bg-slate-300'}`} />
                                                    <span className="text-xs mt-1 font-medium">Done</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <button
                                    onClick={() => {
                                        setIsExtracting(true);
                                        setExtractionPhase('connecting');
                                        setExtractionProgress(0);
                                        handleStepComplete();
                                    }}
                                    disabled={!formData.url}
                                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-6 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 text-sm font-semibold disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-105 disabled:hover:scale-100 disabled:hover:shadow-lg backdrop-blur-sm"
                                >
                                    <Globe className="h-5 w-5 mr-3" />
                                    Extract Elements
                                </button>
                            )}
                        </div>

                        {/* Extraction Results Section */}
                        {extractedElements && (
                            <div className="space-y-6 border-t border-slate-200 pt-8">
                                {/* Header with View Mode Toggle and Export Options */}
                                <div className="flex items-center justify-between">
                                    <h4 className="text-lg font-semibold text-slate-900">Extraction Results</h4>
                                    <div className="flex items-center space-x-3">
                                        {/* Export Buttons */}
                                        <div className="flex items-center space-x-1 bg-white/80 backdrop-blur-sm rounded-xl p-1 border border-slate-200 shadow-sm">
                                            <button
                                                onClick={handleExportJson}
                                                className="px-3 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-white rounded-lg transition-all duration-300"
                                                title="Export as JSON"
                                            >
                                                <div className="flex items-center space-x-2">
                                                    <FileJson className="h-3 w-3" />
                                                    <span>JSON</span>
                                                </div>
                                            </button>
                                            <button
                                                onClick={handleExportCsv}
                                                className="px-3 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-white rounded-lg transition-all duration-300"
                                                title="Export as CSV"
                                            >
                                                <div className="flex items-center space-x-2">
                                                    <FileSpreadsheet className="h-3 w-3" />
                                                    <span>CSV</span>
                                                </div>
                                            </button>
                                        </div>
                                        
                                        {/* View Mode Toggle */}
                                        <div className="flex items-center bg-white/80 backdrop-blur-sm rounded-xl p-1 border border-slate-200 shadow-sm">
                                            <button
                                                onClick={() => setViewMode('executive')}
                                                className={`px-4 py-2 text-xs font-medium rounded-lg transition-all duration-300 ${
                                                    viewMode === 'executive'
                                                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-md'
                                                        : 'text-slate-600 hover:text-slate-900 hover:bg-white'
                                                }`}
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <Eye className="h-3 w-3" />
                                                    <span>Executive</span>
                                                </div>
                                            </button>
                                            <button
                                                onClick={() => setViewMode('developer')}
                                                className={`px-4 py-2 text-xs font-medium rounded-lg transition-all duration-300 ${
                                                    viewMode === 'developer'
                                                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-md'
                                                        : 'text-slate-600 hover:text-slate-900 hover:bg-white'
                                                }`}
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <Code className="h-3 w-3" />
                                                    <span>Developer</span>
                                                </div>
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {viewMode === 'executive' ? (
                                    /* Executive View - Enhanced */
                                    <div className="space-y-6">
                                        {/* Enhanced Success Banner */}
                                        <div className="bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 text-white rounded-xl p-6 shadow-xl backdrop-blur-sm">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-4">
                                                    <div className="bg-white/20 rounded-full p-2">
                                                        <CheckCircle className="h-6 w-6" />
                                                    </div>
                                                    <div>
                                                        <h4 className="text-lg font-bold">Analysis Complete</h4>
                                                        <p className="text-emerald-100 text-sm">{new URL(formData.url).hostname}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center space-x-8">
                                                    <div className="text-center">
                                                        <div className="text-3xl font-bold">{extractedElements.total_elements || 0}</div>
                                                        <div className="text-emerald-100 text-sm">Elements</div>
                                                    </div>
                                                    <div className="text-center border-l border-emerald-400 pl-8">
                                                        <div className="text-3xl font-bold">{Object.keys(extractedElements.elements_by_category || {}).length}</div>
                                                        <div className="text-emerald-100 text-sm">Categories</div>
                                                    </div>
                                                    <div className="text-center border-l border-emerald-400 pl-8">
                                                        <div className="text-3xl font-bold">{extractedElements.llm_analysis ? 'High' : 'Med'}</div>
                                                        <div className="text-emerald-100 text-sm">Quality</div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Rest of the executive view content from case 2 */}
                                        {(extractedElements.llm_analysis || extractedElements.elements_by_category) && (
                                            <div className="space-y-4">
                                                <div className="flex items-center justify-between">
                                                    <h4 className="text-sm font-semibold text-slate-800">Critical Test Scenarios</h4>
                                                    <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                                                        {extractedElements.llm_analysis?.critical_flows?.length || Object.keys(extractedElements.elements_by_category || {}).length} flows identified
                                                    </span>
                                                </div>
                                                
                                                <div className="grid gap-3">
                                                    {(() => {
                                                        // Use critical_flows if available, otherwise generate from categories
                                                        let flows = extractedElements.llm_analysis?.critical_flows;
                                                        
                                                        // Fallback: Generate flows from element categories if critical_flows not available
                                                        if (!flows || flows.length === 0) {
                                                            flows = [];
                                                            const categories = extractedElements.elements_by_category || {};
                                                            
                                                            // Generate flows based on available categories
                                                            if (categories.navigation) {
                                                                flows.push({
                                                                    flow_name: "Navigation Flow Test",
                                                                    description: "Validate all navigation elements and menu interactions",
                                                                    priority: "P1",
                                                                    elements_involved: [`${categories.navigation.length} navigation elements`],
                                                                    steps: [
                                                                        "Click main navigation menu",
                                                                        "Verify all links are accessible",
                                                                        "Test responsive navigation on mobile"
                                                                    ]
                                                                });
                                                            }
                                                            
                                                            if (categories.action || categories.button) {
                                                                const actionCount = (categories.action?.length || 0) + (categories.button?.length || 0);
                                                                flows.push({
                                                                    flow_name: "User Action Flow",
                                                                    description: "Test all interactive buttons and action elements",
                                                                    priority: "P1",
                                                                    elements_involved: [`${actionCount} action elements`],
                                                                    steps: [
                                                                        "Identify all clickable buttons",
                                                                        "Verify button states (enabled/disabled)",
                                                                        "Test click handlers and responses"
                                                                    ]
                                                                });
                                                            }
                                                            
                                                            if (categories.form_input || categories.input) {
                                                                const inputCount = (categories.form_input?.length || 0) + (categories.input?.length || 0);
                                                                flows.push({
                                                                    flow_name: "Form Submission Flow",
                                                                    description: "Validate form inputs and submission process",
                                                                    priority: "P2",
                                                                    elements_involved: [`${inputCount} input fields`],
                                                                    steps: [
                                                                        "Fill all required fields",
                                                                        "Validate input constraints",
                                                                        "Submit form and verify response"
                                                                    ]
                                                                });
                                                            }
                                                            
                                                            if (categories.authentication) {
                                                                flows.push({
                                                                    flow_name: "Authentication Flow",
                                                                    description: "Test login/logout and authentication states",
                                                                    priority: "P1",
                                                                    elements_involved: [`${categories.authentication.length} auth elements`],
                                                                    steps: [
                                                                        "Navigate to login page",
                                                                        "Enter credentials",
                                                                        "Verify successful authentication",
                                                                        "Test logout functionality"
                                                                    ]
                                                                });
                                                            }
                                                            
                                                            if (categories.search) {
                                                                flows.push({
                                                                    flow_name: "Search Functionality",
                                                                    description: "Test search feature and result display",
                                                                    priority: "P2",
                                                                    elements_involved: [`${categories.search.length} search elements`],
                                                                    steps: [
                                                                        "Enter search query",
                                                                        "Submit search",
                                                                        "Verify results display",
                                                                        "Test search filters if available"
                                                                    ]
                                                                });
                                                            }
                                                        }
                                                        
                                                        return flows.slice(0, 5).map((flow: any, idx: number) => {
                                                        const priorityColors = [
                                                            'from-red-50 to-orange-50 border-red-200',
                                                            'from-orange-50 to-yellow-50 border-orange-200', 
                                                            'from-yellow-50 to-green-50 border-yellow-200',
                                                            'from-green-50 to-blue-50 border-green-200',
                                                            'from-blue-50 to-indigo-50 border-blue-200'
                                                        ];
                                                        const priorityIcons = ['🔴', '🟠', '🟡', '🟢', '🔵'];
                                                        
                                                        return (
                                                            <div key={idx} className={`bg-gradient-to-r ${priorityColors[idx] || priorityColors[4]} border rounded-xl p-4 hover:shadow-md transition-all backdrop-blur-sm`}>
                                                                <div className="flex items-start justify-between">
                                                                    <div className="flex-1">
                                                                        <div className="flex items-center space-x-2 mb-2">
                                                                            <span className="text-lg">{priorityIcons[idx] || '🔵'}</span>
                                                                            <h5 className="text-sm font-semibold text-slate-900">
                                                                                {flow.flow_name || `Test Flow ${idx + 1}`}
                                                                            </h5>
                                                                            {idx === 0 && (
                                                                                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-medium">
                                                                                    Critical
                                                                                </span>
                                                                            )}
                                                                        </div>
                                                                        
                                                                        {flow.description && (
                                                                            <p className="text-xs text-slate-600 mb-2">{flow.description}</p>
                                                                        )}
                                                                        
                                                                        {flow.steps && flow.steps.length > 0 && (
                                                                            <div className="mt-2 space-y-1">
                                                                                <p className="text-xs font-medium text-slate-500">Test Steps:</p>
                                                                                <div className="pl-4">
                                                                                    {flow.steps.slice(0, 3).map((step: string, stepIdx: number) => (
                                                                                        <div key={stepIdx} className="flex items-start space-x-1 text-xs text-slate-600">
                                                                                            <span className="text-slate-400">{stepIdx + 1}.</span>
                                                                                            <span>{step}</span>
                                                                                        </div>
                                                                                    ))}
                                                                                    {flow.steps.length > 3 && (
                                                                                        <span className="text-xs text-slate-400 italic">+{flow.steps.length - 3} more steps</span>
                                                                                    )}
                                                                                </div>
                                                                            </div>
                                                                        )}
                                                                        
                                                                        {flow.elements_involved && (
                                                                            <div className="mt-2 flex flex-wrap gap-1">
                                                                                {flow.elements_involved.slice(0, 3).map((elem: string, elemIdx: number) => (
                                                                                    <span key={elemIdx} className="text-xs bg-white/70 text-slate-600 px-2 py-0.5 rounded">
                                                                                        {elem}
                                                                                    </span>
                                                                                ))}
                                                                                {flow.elements_involved.length > 3 && (
                                                                                    <span className="text-xs text-slate-500">+{flow.elements_involved.length - 3}</span>
                                                                                )}
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                    
                                                                    <div className="text-right ml-4">
                                                                        <div className="text-xs text-slate-500">Priority</div>
                                                                        <div className="text-lg font-bold text-slate-900">
                                                                            {flow.priority || `P${idx + 1}`}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        );
                                                    });
                                                    })()}
                                                </div>
                                            </div>
                                        )}

                                        {/* Enhanced Element Distribution */}
                                        {extractedElements.elements_by_category && (
                                            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200 p-6 shadow-lg">
                                                <h4 className="text-sm font-bold text-slate-700 uppercase tracking-wide mb-4">Element Distribution</h4>
                                                <div className="grid grid-cols-2 gap-3">
                                                    {Object.entries(extractedElements.elements_by_category).slice(0, 6).map(([category, items]: [string, any]) => {
                                                        const categoryColors: any = {
                                                            'navigation': 'from-blue-400 to-blue-600',
                                                            'action': 'from-green-400 to-green-600',
                                                            'form_input': 'from-purple-400 to-purple-600',
                                                            'authentication': 'from-orange-400 to-orange-600',
                                                            'search': 'from-pink-400 to-pink-600',
                                                            'interactive': 'from-indigo-400 to-indigo-600'
                                                        };
                                                        const gradientColor = categoryColors[category.toLowerCase()] || 'from-slate-400 to-slate-600';
                                                        
                                                        return (
                                                            <div key={category} className="flex items-center justify-between p-3 bg-gradient-to-r from-slate-50 to-white rounded-lg border border-slate-100 hover:shadow-md transition-all duration-300">
                                                                <div className="flex items-center space-x-3 flex-1">
                                                                    <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${gradientColor} shadow-sm`} />
                                                                    <span className="text-sm text-slate-700 capitalize font-medium">
                                                                        {category.replace(/_/g, ' ')}
                                                                    </span>
                                                                </div>
                                                                <span className="text-sm font-bold text-slate-900 bg-slate-100 px-2 py-1 rounded-full">
                                                                    {items.length}
                                                                </span>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )}
                                        
                                        {/* Enhanced AI Recommendations */}
                                        {extractedElements.llm_analysis && extractedElements.llm_analysis.recommendations && (
                                            <div className="bg-gradient-to-r from-purple-50 via-pink-50 to-purple-50 rounded-xl border border-purple-200 p-6 backdrop-blur-sm shadow-lg">
                                                <div className="flex items-start space-x-4">
                                                    <div className="bg-purple-100 rounded-full p-3">
                                                        <Shield className="h-6 w-6 text-purple-600" />
                                                    </div>
                                                    <div className="flex-1">
                                                        <h4 className="text-lg font-bold text-purple-900 mb-4">Testing Recommendations</h4>
                                                        <div className="space-y-3">
                                                            {extractedElements.llm_analysis.recommendations.slice(0, 3).map((rec: string, idx: number) => (
                                                                <div key={idx} className="flex items-start space-x-3">
                                                                    <CheckCircle className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                                                                    <p className="text-sm text-purple-700 leading-relaxed">{rec}</p>
                                                                </div>
                                                            ))}
                                                        </div>
                                                        
                                                        {extractedElements.llm_analysis.test_coverage && (
                                                            <div className="mt-5 pt-4 border-t border-purple-200">
                                                                <div className="flex items-center justify-between mb-2">
                                                                    <span className="text-sm text-purple-600 font-medium">Estimated Coverage</span>
                                                                    <span className="text-lg font-bold text-purple-900">
                                                                        {extractedElements.llm_analysis.test_coverage}%
                                                                    </span>
                                                                </div>
                                                                <div className="w-full bg-purple-100 rounded-full h-3">
                                                                    <div 
                                                                        className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full shadow-sm transition-all duration-1000"
                                                                        style={{ width: `${extractedElements.llm_analysis.test_coverage || 75}%` }}
                                                                    />
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    /* Enhanced Developer View */
                                    <div className="space-y-6">
                                        {/* Enhanced Developer Header */}
                                        <div className="bg-gradient-to-r from-slate-800 via-slate-900 to-slate-800 text-white rounded-xl p-4 shadow-xl">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-3">
                                                    <Terminal className="h-5 w-5 text-emerald-400" />
                                                    <span className="text-sm font-mono">response.json</span>
                                                    <span className="text-xs text-slate-400 bg-slate-700 px-2 py-1 rounded">
                                                        {JSON.stringify(extractedElements).length} bytes
                                                    </span>
                                                </div>
                                                <button
                                                    onClick={handleCopyJson}
                                                    className="flex items-center space-x-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-all duration-300"
                                                >
                                                    {copiedJson ? (
                                                        <>
                                                            <CheckCircle className="h-4 w-4 text-green-400" />
                                                            <span className="text-sm text-green-400">Copied!</span>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Copy className="h-4 w-4" />
                                                            <span className="text-sm">Copy JSON</span>
                                                        </>
                                                    )}
                                                </button>
                                            </div>
                                        </div>
                                        
                                        {/* Enhanced Syntax Highlighted JSON */}
                                        <div className="rounded-xl overflow-hidden border border-slate-300 shadow-lg">
                                            <SyntaxHighlighter
                                                language="json"
                                                style={vscDarkPlus}
                                                customStyle={{
                                                    margin: 0,
                                                    borderRadius: '0.75rem',
                                                    fontSize: '0.75rem',
                                                    maxHeight: '400px',
                                                    overflow: 'auto'
                                                }}
                                                showLineNumbers={true}
                                                lineNumberStyle={{ color: '#6B7280', fontSize: '0.625rem' }}
                                            >
                                                {JSON.stringify(extractedElements, null, 2)}
                                            </SyntaxHighlighter>
                                        </div>
                                        
                                        {/* Enhanced Developer Stats */}
                                        <div className="grid grid-cols-3 gap-4">
                                            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 text-center shadow-lg">
                                                <div className="text-xs text-slate-400 mb-1">Properties</div>
                                                <div className="text-lg font-mono text-slate-200 font-bold">
                                                    {Object.keys(extractedElements).length}
                                                </div>
                                            </div>
                                            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 text-center shadow-lg">
                                                <div className="text-xs text-slate-400 mb-1">Elements</div>
                                                <div className="text-lg font-mono text-slate-200 font-bold">
                                                    {extractedElements.total_elements || 0}
                                                </div>
                                            </div>
                                            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 text-center shadow-lg">
                                                <div className="text-xs text-slate-400 mb-1">Categories</div>
                                                <div className="text-lg font-mono text-slate-200 font-bold">
                                                    {Object.keys(extractedElements.elements_by_category || {}).length}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                
                                {/* Enhanced Continue Button */}
                                <button
                                    onClick={() => {
                                        setCompletedSteps([...completedSteps, currentStep]);
                                        setCurrentStep(2);
                                    }}
                                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-6 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 text-sm font-semibold flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-105 backdrop-blur-sm"
                                >
                                    <ChevronRight className="h-5 w-5 mr-2" />
                                    Continue to Test Generation
                                </button>
                            </div>
                        )}
                    </div>
                );
            
            case 2:
                return (
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-900">Generate Test Cases</h3>
                        
                        {!generatedTests ? (
                            /* Auto-Generation Progress */
                            <div className="space-y-4">
                                {/* Info about automatic generation */}
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                    <div className="flex items-start space-x-3">
                                        <Zap className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                        <div>
                                            <p className="text-sm font-medium text-blue-900">Automatic Test Generation</p>
                                            <p className="text-xs text-blue-700 mt-1">
                                                Generating comprehensive test cases from extracted elements using AI
                                            </p>
                                            <div className="mt-2 flex items-center space-x-1 text-xs text-blue-600">
                                                <span>Categories:</span>
                                                <span className="font-medium">Functional, Validation, Edge Cases</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Generation Progress */}
                                {isGenerating && (
                                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center space-x-3">
                                                <div className="animate-spin rounded-full h-5 w-5 border-2 border-purple-600 border-t-transparent"></div>
                                                <div>
                                                    <p className="text-sm font-medium text-purple-900">
                                                        {generationPhase === 'preparing' && 'Preparing test generation...'}
                                                        {generationPhase === 'functional' && 'Generating functional tests...'}
                                                        {generationPhase === 'validation' && 'Creating validation tests...'}
                                                        {generationPhase === 'edge_cases' && 'Adding edge case scenarios...'}
                                                        {generationPhase === 'security' && 'Including security tests...'}
                                                        {generationPhase === 'finalizing' && 'Finalizing test suite...'}
                                                        {generationPhase === 'complete' && 'Test generation complete!'}
                                                    </p>
                                                    <p className="text-xs text-purple-600 mt-0.5">
                                                        Using AI to create comprehensive Gherkin scenarios
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <span className="text-lg font-bold text-purple-900">{generationProgress}%</span>
                                            </div>
                                        </div>
                                        
                                        {/* Progress Bar */}
                                        <div className="w-full bg-purple-100 rounded-full h-2 overflow-hidden">
                                            <div 
                                                className="bg-gradient-to-r from-purple-500 to-purple-600 h-full rounded-full transition-all duration-500 ease-out"
                                                style={{ width: `${generationProgress}%` }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            /* Display Generated Tests with View Modes */
                            <div className="space-y-4">
                                {/* Header with Export and View Mode Toggle */}
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                        <CheckCircle className="h-5 w-5 text-green-600" />
                                        <div>
                                            <h4 className="text-sm font-semibold text-green-900">Test Cases Generated</h4>
                                            <p className="text-xs text-green-700">
                                                {Object.keys(generatedTests.features || {}).length} test features created
                                            </p>
                                        </div>
                                    </div>
                                    
                                    <div className="flex items-center space-x-3">
                                        {/* Export Buttons */}
                                        <div className="flex items-center bg-slate-50 rounded-lg p-1">
                                            <button
                                                onClick={handleExportTestsJson}
                                                className="px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-white rounded transition-all"
                                                title="Export as JSON"
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <FileJson className="h-3 w-3" />
                                                    <span>JSON</span>
                                                </div>
                                            </button>
                                            <button
                                                onClick={handleExportTestsCsv}
                                                className="px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-white rounded transition-all"
                                                title="Export as CSV"
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <FileSpreadsheet className="h-3 w-3" />
                                                    <span>CSV</span>
                                                </div>
                                            </button>
                                        </div>
                                        
                                        {/* View Mode Toggle */}
                                        <div className="flex items-center bg-slate-100 rounded-lg p-1">
                                            <button
                                                onClick={() => setViewMode('executive')}
                                                className={`px-3 py-1.5 text-xs font-medium rounded transition-all ${
                                                    viewMode === 'executive'
                                                        ? 'bg-white text-slate-900 shadow-sm'
                                                        : 'text-slate-600 hover:text-slate-900'
                                                }`}
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <Eye className="h-3 w-3" />
                                                    <span>Executive</span>
                                                </div>
                                            </button>
                                            <button
                                                onClick={() => setViewMode('developer')}
                                                className={`px-3 py-1.5 text-xs font-medium rounded transition-all ${
                                                    viewMode === 'developer'
                                                        ? 'bg-white text-slate-900 shadow-sm'
                                                        : 'text-slate-600 hover:text-slate-900'
                                                }`}
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <Code className="h-3 w-3" />
                                                    <span>Developer</span>
                                                </div>
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {viewMode === 'executive' ? (
                                    /* Executive View - Visual and Simple */
                                    <div className="space-y-4">
                                        {/* Success Banner */}
                                        <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg p-4 shadow-lg">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-3">
                                                    <Zap className="h-5 w-5" />
                                                    <div>
                                                        <h4 className="text-sm font-semibold">Test Generation Complete</h4>
                                                        <p className="text-green-100 text-xs">AI-powered test scenarios ready for execution</p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-lg font-bold">{Object.keys(generatedTests.features || {}).length}</div>
                                                    <div className="text-xs text-green-100">Features</div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Test Categories Overview */}
                                        <div className="grid grid-cols-1 gap-3">
                                            {generatedTests.features && Object.entries(generatedTests.features).map(([category, feature]: [string, any]) => {
                                                const categoryColors: any = {
                                                    'functional': 'from-blue-500 to-blue-600',
                                                    'validation': 'from-purple-500 to-purple-600', 
                                                    'edge_cases': 'from-orange-500 to-orange-600',
                                                    'security': 'from-red-500 to-red-600',
                                                    'accessibility': 'from-indigo-500 to-indigo-600',
                                                    'performance': 'from-yellow-500 to-yellow-600'
                                                };
                                                const gradient = categoryColors[category] || 'from-slate-500 to-slate-600';
                                                
                                                return (
                                                    <div key={category} className="bg-white rounded-lg border border-slate-200 p-4 hover:border-slate-300 transition-colors">
                                                        <div className="flex items-start space-x-3">
                                                            <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${gradient} mt-1 flex-shrink-0`}></div>
                                                            <div className="flex-1">
                                                                <h5 className="text-sm font-semibold text-slate-800 capitalize mb-2">
                                                                    {category.replace('_', ' ')} Tests
                                                                </h5>
                                                                <div className="space-y-1">
                                                                    {feature.scenarios?.slice(0, 3).map((scenario: any, idx: number) => (
                                                                        <div key={idx} className="flex items-start space-x-2">
                                                                            <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                                                                            <span className="text-xs text-slate-600">
                                                                                {scenario.title || scenario.name || (typeof scenario === 'string' ? scenario : 'Test scenario')}
                                                                            </span>
                                                                        </div>
                                                                    ))}
                                                                    {feature.scenarios && feature.scenarios.length > 3 && (
                                                                        <div className="text-xs text-slate-500 ml-5">
                                                                            +{feature.scenarios.length - 3} more scenarios
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                            <div className="text-right">
                                                                <div className="text-sm font-bold text-slate-700">{feature.scenarios?.length || 0}</div>
                                                                <div className="text-xs text-slate-500">scenarios</div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>

                                        {/* Continue Button */}
                                        <button
                                            onClick={handleStepComplete}
                                            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-all text-sm font-medium flex items-center justify-center shadow-sm hover:shadow-md"
                                        >
                                            <ChevronRight className="h-4 w-4 mr-2" />
                                            Continue to Code Generation
                                        </button>
                                    </div>
                                ) : (
                                    /* Developer View - JSON with Syntax Highlighting */
                                    <div className="space-y-4">
                                        {/* Developer Header */}
                                        <div className="bg-gradient-to-r from-slate-800 to-slate-900 text-white rounded-lg p-3">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-2">
                                                    <Terminal className="h-4 w-4 text-emerald-400" />
                                                    <span className="text-sm font-mono">generated_tests.json</span>
                                                    <span className="text-xs text-slate-400">({JSON.stringify(generatedTests).length} bytes)</span>
                                                </div>
                                                <button
                                                    onClick={handleCopyTestsJson}
                                                    className="flex items-center space-x-1 px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
                                                >
                                                    {copiedTestsJson ? (
                                                        <>
                                                            <CheckCircle className="h-3 w-3 text-green-400" />
                                                            <span className="text-xs text-green-400">Copied!</span>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Copy className="h-3 w-3" />
                                                            <span className="text-xs">Copy JSON</span>
                                                        </>
                                                    )}
                                                </button>
                                            </div>
                                        </div>
                                        
                                        {/* Syntax Highlighted JSON */}
                                        <div className="rounded-xl overflow-hidden border border-slate-700">
                                            <SyntaxHighlighter
                                                language="json"
                                                style={vscDarkPlus}
                                                customStyle={{
                                                    margin: 0,
                                                    borderRadius: '0.75rem',
                                                    fontSize: '0.75rem',
                                                    maxHeight: '400px',
                                                    overflow: 'auto'
                                                }}
                                                showLineNumbers={true}
                                                lineNumberStyle={{ color: '#6B7280', fontSize: '0.625rem' }}
                                            >
                                                {JSON.stringify(generatedTests, null, 2)}
                                            </SyntaxHighlighter>
                                        </div>
                                        
                                        {/* Quick Stats for Developers */}
                                        <div className="grid grid-cols-3 gap-2">
                                            <div className="bg-slate-800 rounded-lg p-2 text-center">
                                                <div className="text-xs text-slate-400">Features</div>
                                                <div className="text-sm font-mono text-slate-200">
                                                    {Object.keys(generatedTests.features || {}).length}
                                                </div>
                                            </div>
                                            <div className="bg-slate-800 rounded-lg p-2 text-center">
                                                <div className="text-xs text-slate-400">Scenarios</div>
                                                <div className="text-sm font-mono text-slate-200">
                                                    {Object.values(generatedTests.features || {}).reduce((total: number, feature: any) => 
                                                        total + (feature.scenarios?.length || 0), 0)}
                                                </div>
                                            </div>
                                            <div className="bg-slate-800 rounded-lg p-2 text-center">
                                                <div className="text-xs text-slate-400">Size</div>
                                                <div className="text-sm font-mono text-slate-200">
                                                    {(JSON.stringify(generatedTests).length / 1024).toFixed(1)}kb
                                                </div>
                                            </div>
                                        </div>

                                        {/* Continue Button */}
                                        <button
                                            onClick={handleStepComplete}
                                            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-all text-sm font-medium flex items-center justify-center shadow-sm hover:shadow-md"
                                        >
                                            <ChevronRight className="h-4 w-4 mr-2" />
                                            Continue to Code Generation
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            
            case 3:
                return (
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-900">Generate Code</h3>
                        
                        {!generatedCode ? (
                            /* Auto-Generation Progress */
                            <div className="space-y-4">
                                {/* Info about automatic generation */}
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                    <div className="flex items-start space-x-3">
                                        <Code className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                        <div>
                                            <p className="text-sm font-medium text-blue-900">Automatic Code Generation</p>
                                            <p className="text-xs text-blue-700 mt-1">
                                                Generating executable test code from test scenarios using AI
                                            </p>
                                            <div className="mt-2 flex items-center space-x-1 text-xs text-blue-600">
                                                <span>Includes:</span>
                                                <span className="font-medium">Page Objects, Test Files, Configuration</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Generation Progress */}
                                {isGeneratingCode && (
                                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center space-x-3">
                                                <div className="animate-spin rounded-full h-5 w-5 border-2 border-purple-600 border-t-transparent"></div>
                                                <div>
                                                    <p className="text-sm font-medium text-purple-900">
                                                        {codeGenerationPhase === 'preparing' && 'Preparing code generation...'}
                                                        {codeGenerationPhase === 'page_objects' && 'Generating page objects...'}
                                                        {codeGenerationPhase === 'test_files' && 'Creating test files...'}
                                                        {codeGenerationPhase === 'configuration' && 'Setting up configuration...'}
                                                        {codeGenerationPhase === 'finalizing' && 'Finalizing code structure...'}
                                                        {codeGenerationPhase === 'complete' && 'Code generation complete!'}
                                                    </p>
                                                    <p className="text-xs text-purple-600 mt-0.5">
                                                        Using AI to create production-ready test automation code
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <span className="text-lg font-bold text-purple-900">{codeGenerationProgress}%</span>
                                            </div>
                                        </div>
                                        
                                        {/* Progress Bar */}
                                        <div className="w-full bg-purple-100 rounded-full h-2 overflow-hidden">
                                            <div 
                                                className="bg-gradient-to-r from-purple-500 to-purple-600 h-full rounded-full transition-all duration-500 ease-out"
                                                style={{ width: `${codeGenerationProgress}%` }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            /* Display Generated Code with View Modes */
                            <div className="space-y-4">
                                {/* Header with Export and View Mode Toggle */}
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                        <CheckCircle className="h-5 w-5 text-green-600" />
                                        <div>
                                            <h4 className="text-sm font-semibold text-green-900">Code Generated</h4>
                                            <p className="text-xs text-green-700">
                                                {Object.keys(generatedCode.generated_files || {}).length} files created
                                            </p>
                                        </div>
                                    </div>
                                    
                                    <div className="flex items-center space-x-3">
                                        {/* Export Buttons */}
                                        <div className="flex items-center bg-slate-50 rounded-lg p-1">
                                            <button
                                                onClick={() => {
                                                    // Create a ZIP file with all generated files
                                                    if (generatedCode && generatedCode.generated_files) {
                                                        // Create download content
                                                        const files = generatedCode.generated_files;
                                                        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
                                                        const zipName = `test_automation_code_${timestamp}.zip`;
                                                        
                                                        // For now, download as JSON (could integrate JSZip library for actual ZIP)
                                                        const content = JSON.stringify(files, null, 2);
                                                        const blob = new Blob([content], { type: 'application/json' });
                                                        const url = URL.createObjectURL(blob);
                                                        const a = document.createElement('a');
                                                        a.href = url;
                                                        a.download = zipName.replace('.zip', '.json');
                                                        document.body.appendChild(a);
                                                        a.click();
                                                        document.body.removeChild(a);
                                                        URL.revokeObjectURL(url);
                                                    }
                                                }}
                                                className="px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-white rounded transition-all"
                                                title="Download all files"
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <Download className="h-3 w-3" />
                                                    <span>Export</span>
                                                </div>
                                            </button>
                                        </div>
                                        
                                        {/* View Mode Toggle */}
                                        <div className="flex items-center bg-slate-100 rounded-lg p-1">
                                            <button
                                                onClick={() => setViewMode('executive')}
                                                className={`px-3 py-1.5 text-xs font-medium rounded transition-all ${
                                                    viewMode === 'executive'
                                                        ? 'bg-white text-slate-900 shadow-sm'
                                                        : 'text-slate-600 hover:text-slate-900'
                                                }`}
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <Eye className="h-3 w-3" />
                                                    <span>Executive</span>
                                                </div>
                                            </button>
                                            <button
                                                onClick={() => setViewMode('developer')}
                                                className={`px-3 py-1.5 text-xs font-medium rounded transition-all ${
                                                    viewMode === 'developer'
                                                        ? 'bg-white text-slate-900 shadow-sm'
                                                        : 'text-slate-600 hover:text-slate-900'
                                                }`}
                                            >
                                                <div className="flex items-center space-x-1">
                                                    <Code className="h-3 w-3" />
                                                    <span>Developer</span>
                                                </div>
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {viewMode === 'executive' ? (
                                    /* Executive View - Visual File Structure */
                                    <div className="space-y-4">
                                        {/* Success Banner with Quality Indicators */}
                                        <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg p-4 shadow-lg">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-3">
                                                    <Code className="h-5 w-5" />
                                                    <div>
                                                        <h4 className="text-sm font-semibold">Code Generation Complete</h4>
                                                        <p className="text-green-100 text-xs">Production-ready test automation code</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center space-x-4">
                                                    <div className="text-center">
                                                        <div className="text-lg font-bold">{Object.keys(generatedCode.generated_files || {}).length}</div>
                                                        <div className="text-xs text-green-100">Files</div>
                                                    </div>
                                                    <div className="text-center border-l border-green-400 pl-4">
                                                        <div className="text-lg font-bold">{generatedCode.statistics?.total_lines || 0}</div>
                                                        <div className="text-xs text-green-100">Lines</div>
                                                    </div>
                                                    <div className="text-center border-l border-green-400 pl-4">
                                                        <div className="flex items-center space-x-1">
                                                            <Shield className="h-4 w-4 text-green-200" />
                                                            <span className="text-sm font-bold">Ready</span>
                                                        </div>
                                                        <div className="text-xs text-green-100">Status</div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* File Structure Overview */}
                                        {generatedCode.file_structure && (
                                            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-3">
                                                <div className="flex items-center space-x-2 mb-3">
                                                    <Database className="h-4 w-4 text-slate-600" />
                                                    <h5 className="text-sm font-semibold text-slate-800">Project Structure</h5>
                                                </div>
                                                <div className="space-y-1 font-mono text-xs text-slate-600">
                                                    {Object.entries(generatedCode.file_structure).map(([dir, files]: [string, any]) => (
                                                        <div key={dir}>
                                                            {dir && <div className="flex items-center space-x-1">
                                                                <span className="text-slate-400">📁</span>
                                                                <span>{dir || '/'}</span>
                                                            </div>}
                                                            {Array.isArray(files) && files.map((file: string) => (
                                                                <div key={file} className="ml-4 flex items-center space-x-1">
                                                                    <span className="text-slate-400">📄</span>
                                                                    <span>{file}</span>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                        
                                        {/* Instruction to click cards */}
                                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                                            <div className="flex items-center space-x-2">
                                                <Eye className="h-4 w-4 text-blue-600" />
                                                <p className="text-xs text-blue-700">
                                                    Click any file card to view code • Hover for quick copy
                                                </p>
                                            </div>
                                        </div>
                                        
                                        {/* File Structure Overview */}
                                        <div className="grid grid-cols-1 gap-3">
                                            {generatedCode.generated_files && Object.entries(generatedCode.generated_files).map(([filename, content]: [string, any]) => {
                                                // const fileType = filename.endsWith('.py') ? 'python' : 'config';  // Unused variable
                                                const isTest = filename.startsWith('test_');
                                                const isPage = filename.includes('page');
                                                // const isConfig = filename === 'conftest.py';  // Unused variable
                                                
                                                const fileColors = {
                                                    'test': 'from-blue-500 to-blue-600',
                                                    'page': 'from-purple-500 to-purple-600',
                                                    'config': 'from-orange-500 to-orange-600'
                                                };
                                                
                                                const fileType2 = isTest ? 'test' : (isPage ? 'page' : 'config');
                                                const gradient = fileColors[fileType2] || 'from-slate-500 to-slate-600';
                                                
                                                return (
                                                    <div 
                                                        key={filename} 
                                                        className="bg-white rounded-lg border border-slate-200 p-4 hover:border-slate-300 hover:shadow-md transition-all cursor-pointer group"
                                                        onClick={() => setSelectedFile({ filename, content: typeof content === 'string' ? content : '' })}
                                                    >
                                                        <div className="flex items-start space-x-3">
                                                            <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${gradient} mt-1 flex-shrink-0`}></div>
                                                            <div className="flex-1">
                                                                <h5 className="text-sm font-semibold text-slate-800 mb-1 group-hover:text-blue-600 transition-colors">
                                                                    {filename}
                                                                </h5>
                                                                <p className="text-xs text-slate-600 mb-2">
                                                                    {isTest ? 'Test automation file' : 
                                                                     isPage ? 'Page object class' : 
                                                                     'Configuration file'}
                                                                </p>
                                                                <div className="text-xs text-slate-500">
                                                                    {typeof content === 'string' ? content.split('\n').length : 0} lines
                                                                </div>
                                                            </div>
                                                            <div className="text-right">
                                                                <div className="text-xs text-slate-500 capitalize">{fileType2}</div>
                                                                <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-2">
                                                                    <button
                                                                        onClick={(e) => {
                                                                            e.stopPropagation();
                                                                            const cleanContent = typeof content === 'string' 
                                                                                ? content.replace(/^```python\n/, '').replace(/\n```$/, '').replace(/^```\n/, '')
                                                                                : '';
                                                                            navigator.clipboard.writeText(cleanContent);
                                                                        }}
                                                                        className="p-1 hover:bg-slate-100 rounded transition-colors"
                                                                        title="Copy code"
                                                                    >
                                                                        <Copy className="h-3 w-3 text-slate-400" />
                                                                    </button>
                                                                    <Eye className="h-4 w-4 text-slate-400" />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>

                                        {/* Action Buttons */}
                                        <div className="flex space-x-3">
                                            <button
                                                onClick={() => {
                                                    // Reset and regenerate
                                                    setGeneratedCode(null);
                                                    setIsGeneratingCode(false);
                                                    setCodeGenerationPhase('idle');
                                                    setCodeGenerationProgress(0);
                                                    setAutoGeneratingCode(false);
                                                    // Trigger regeneration
                                                    setTimeout(() => handleGenerateCode(), 100);
                                                }}
                                                className="flex-1 bg-slate-100 text-slate-700 py-3 px-4 rounded-lg hover:bg-slate-200 transition-all text-sm font-medium flex items-center justify-center"
                                            >
                                                <RefreshCw className="h-4 w-4 mr-2" />
                                                Regenerate
                                            </button>
                                            <button
                                                onClick={handleStepComplete}
                                                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-all text-sm font-medium flex items-center justify-center shadow-sm hover:shadow-md"
                                            >
                                                <ChevronRight className="h-4 w-4 mr-2" />
                                                Continue
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    /* Developer View - Code with Syntax Highlighting */
                                    <div className="space-y-4">
                                        {/* Developer Header */}
                                        <div className="bg-gradient-to-r from-slate-800 to-slate-900 text-white rounded-lg p-3">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-2">
                                                    <Terminal className="h-4 w-4 text-emerald-400" />
                                                    <span className="text-sm font-mono">generated_code.json</span>
                                                    <span className="text-xs text-slate-400">({JSON.stringify(generatedCode).length} bytes)</span>
                                                </div>
                                                <button
                                                    onClick={handleCopyCodeJson}
                                                    className="flex items-center space-x-1 px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
                                                >
                                                    {copiedCodeJson ? (
                                                        <>
                                                            <CheckCircle className="h-3 w-3 text-green-400" />
                                                            <span className="text-xs text-green-400">Copied!</span>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Copy className="h-3 w-3" />
                                                            <span className="text-xs">Copy JSON</span>
                                                        </>
                                                    )}
                                                </button>
                                            </div>
                                        </div>
                                        
                                        {/* Syntax Highlighted JSON */}
                                        <div className="rounded-xl overflow-hidden border border-slate-700">
                                            <SyntaxHighlighter
                                                language="json"
                                                style={vscDarkPlus}
                                                customStyle={{
                                                    margin: 0,
                                                    borderRadius: '0.75rem',
                                                    fontSize: '0.75rem',
                                                    maxHeight: '400px',
                                                    overflow: 'auto'
                                                }}
                                                showLineNumbers={true}
                                                lineNumberStyle={{ color: '#6B7280', fontSize: '0.625rem' }}
                                            >
                                                {JSON.stringify(generatedCode, null, 2)}
                                            </SyntaxHighlighter>
                                        </div>
                                        
                                        {/* Quick Stats for Developers */}
                                        <div className="grid grid-cols-3 gap-2">
                                            <div className="bg-slate-800 rounded-lg p-2 text-center">
                                                <div className="text-xs text-slate-400">Files</div>
                                                <div className="text-sm font-mono text-slate-200">
                                                    {Object.keys(generatedCode.generated_files || {}).length}
                                                </div>
                                            </div>
                                            <div className="bg-slate-800 rounded-lg p-2 text-center">
                                                <div className="text-xs text-slate-400">Lines</div>
                                                <div className="text-sm font-mono text-slate-200">
                                                    {generatedCode.statistics?.total_lines || 0}
                                                </div>
                                            </div>
                                            <div className="bg-slate-800 rounded-lg p-2 text-center">
                                                <div className="text-xs text-slate-400">Size</div>
                                                <div className="text-sm font-mono text-slate-200">
                                                    {(JSON.stringify(generatedCode).length / 1024).toFixed(1)}kb
                                                </div>
                                            </div>
                                        </div>

                                        {/* Action Buttons */}
                                        <div className="flex space-x-3">
                                            <button
                                                onClick={() => {
                                                    // Reset and regenerate
                                                    setGeneratedCode(null);
                                                    setIsGeneratingCode(false);
                                                    setCodeGenerationPhase('idle');
                                                    setCodeGenerationProgress(0);
                                                    setAutoGeneratingCode(false);
                                                    // Trigger regeneration
                                                    setTimeout(() => handleGenerateCode(), 100);
                                                }}
                                                className="flex-1 bg-slate-100 text-slate-700 py-3 px-4 rounded-lg hover:bg-slate-200 transition-all text-sm font-medium flex items-center justify-center"
                                            >
                                                <RefreshCw className="h-4 w-4 mr-2" />
                                                Regenerate
                                            </button>
                                            <button
                                                onClick={handleStepComplete}
                                                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-all text-sm font-medium flex items-center justify-center shadow-sm hover:shadow-md"
                                            >
                                                <ChevronRight className="h-4 w-4 mr-2" />
                                                Continue
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            
            case 4:
                return (
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-900">Execute Tests</h3>
                        
                        {!testResults ? (
                            /* Auto-Execution Progress */
                            <div className="space-y-4">
                                {/* Info about automatic execution */}
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                    <div className="flex items-start space-x-3">
                                        <Play className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                        <div>
                                            <p className="text-sm font-medium text-blue-900">Automatic Test Execution</p>
                                            <p className="text-xs text-blue-700 mt-1">
                                                Running generated tests against {new URL(formData.url).hostname}
                                            </p>
                                            <div className="mt-2 flex items-center space-x-1 text-xs text-blue-600">
                                                <span>Framework:</span>
                                                <span className="font-medium">Pytest + Playwright</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Execution Progress */}
                                {isExecutingTests && (
                                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center space-x-3">
                                                <div className="animate-spin rounded-full h-5 w-5 border-2 border-purple-600 border-t-transparent"></div>
                                                <div>
                                                    <p className="text-sm font-medium text-purple-900">
                                                        {executionPhase === 'preparing' && 'Preparing test environment...'}
                                                        {executionPhase === 'installing' && 'Installing dependencies...'}
                                                        {executionPhase === 'running' && 'Running test suite...'}
                                                        {executionPhase === 'collecting' && 'Collecting results...'}
                                                        {executionPhase === 'complete' && 'Tests completed!'}
                                                        {executionPhase === 'error' && 'Execution error occurred'}
                                                    </p>
                                                    <p className="text-xs text-purple-600 mt-0.5">
                                                        {executionPhase === 'running' && 'Executing test scenarios...'}
                                                        {executionPhase === 'installing' && 'Setting up Playwright and pytest...'}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <span className="text-lg font-bold text-purple-900">{executionProgress}%</span>
                                            </div>
                                        </div>
                                        
                                        {/* Progress Bar */}
                                        <div className="w-full bg-purple-100 rounded-full h-2 overflow-hidden">
                                            <div 
                                                className="bg-gradient-to-r from-purple-500 to-purple-600 h-full rounded-full transition-all duration-500 ease-out"
                                                style={{ width: `${executionProgress}%` }}
                                            />
                                        </div>
                                        
                                        {/* Show logs toggle */}
                                        {executionLogs.length > 0 && (
                                            <button
                                                onClick={() => setShowLogs(!showLogs)}
                                                className="mt-3 text-xs text-purple-700 hover:text-purple-900 font-medium"
                                            >
                                                {showLogs ? 'Hide' : 'Show'} Execution Logs ({executionLogs.length})
                                            </button>
                                        )}
                                        
                                        {/* Logs display */}
                                        {showLogs && (
                                            <div className="mt-2 bg-slate-900 text-green-400 p-3 rounded font-mono text-xs max-h-32 overflow-y-auto">
                                                {executionLogs.map((log, idx) => (
                                                    <div key={idx}>$ {log}</div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ) : (
                            /* Display Test Results */
                            <div className="space-y-4">
                                {/* Results Summary */}
                                <div className={`bg-gradient-to-r ${testResults.failed > 0 ? 'from-orange-500 to-red-600' : 'from-green-500 to-emerald-600'} text-white rounded-lg p-4 shadow-lg`}>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            {testResults.failed > 0 ? (
                                                <AlertCircle className="h-5 w-5" />
                                            ) : (
                                                <CheckCircle className="h-5 w-5" />
                                            )}
                                            <div>
                                                <h4 className="text-sm font-semibold">Test Execution Complete</h4>
                                                <p className="text-xs text-white/90">
                                                    {testResults.duration.toFixed(1)}s execution time
                                                </p>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-3 gap-4">
                                            <div className="text-center">
                                                <div className="text-2xl font-bold">{testResults.total_tests}</div>
                                                <div className="text-xs text-white/80">Total</div>
                                            </div>
                                            <div className="text-center border-l border-white/30 pl-4">
                                                <div className="text-2xl font-bold">{testResults.passed}</div>
                                                <div className="text-xs text-white/80">Passed</div>
                                            </div>
                                            <div className="text-center border-l border-white/30 pl-4">
                                                <div className="text-2xl font-bold">{testResults.failed}</div>
                                                <div className="text-xs text-white/80">Failed</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Pass Rate Chart */}
                                <div className="bg-white border border-slate-200 rounded-lg p-4">
                                    <h5 className="text-sm font-semibold text-slate-800 mb-3">Test Results</h5>
                                    <div className="relative h-8 bg-slate-100 rounded-full overflow-hidden">
                                        <div 
                                            className="absolute left-0 top-0 h-full bg-green-500 transition-all duration-500"
                                            style={{ width: `${(testResults.passed / testResults.total_tests) * 100}%` }}
                                        />
                                        {testResults.failed > 0 && (
                                            <div 
                                                className="absolute right-0 top-0 h-full bg-red-500 transition-all duration-500"
                                                style={{ width: `${(testResults.failed / testResults.total_tests) * 100}%` }}
                                            />
                                        )}
                                    </div>
                                    <div className="flex justify-between mt-2 text-xs text-slate-600">
                                        <span>{((testResults.passed / testResults.total_tests) * 100).toFixed(0)}% Pass Rate</span>
                                        <span>{testResults.total_tests} Total Tests</span>
                                    </div>
                                </div>
                                
                                {/* Individual Test Results */}
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between mb-2">
                                        <h5 className="text-sm font-semibold text-slate-800">Test Details</h5>
                                        <button
                                            onClick={() => setShowLogs(!showLogs)}
                                            className="text-xs text-slate-600 hover:text-slate-900"
                                        >
                                            {showLogs ? 'Hide' : 'Show'} Details
                                        </button>
                                    </div>
                                    
                                    {(showLogs ? testResults.test_results : testResults.test_results.slice(0, 3)).map((test: any, idx: number) => (
                                        <div key={idx} className="bg-white border border-slate-200 rounded-lg p-3">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-2">
                                                    {test.status === 'passed' ? (
                                                        <CheckCircle className="h-4 w-4 text-green-600" />
                                                    ) : test.status === 'failed' ? (
                                                        <X className="h-4 w-4 text-red-600" />
                                                    ) : (
                                                        <AlertCircle className="h-4 w-4 text-yellow-600" />
                                                    )}
                                                    <span className="text-xs font-mono text-slate-700">{test.name}</span>
                                                </div>
                                                <span className="text-xs text-slate-500">{test.duration.toFixed(2)}s</span>
                                            </div>
                                            {test.message && (
                                                <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                                                    {test.message}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                    
                                    {!showLogs && testResults.test_results.length > 3 && (
                                        <button
                                            onClick={() => setShowLogs(true)}
                                            className="text-xs text-blue-600 hover:text-blue-700"
                                        >
                                            +{testResults.test_results.length - 3} more tests
                                        </button>
                                    )}
                                </div>
                                
                                {/* Execution Logs */}
                                {executionLogs.length > 0 && (
                                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                                        <h5 className="text-sm font-semibold text-slate-800 mb-2">Execution Logs</h5>
                                        <div className="bg-slate-900 text-green-400 p-3 rounded font-mono text-xs max-h-40 overflow-y-auto">
                                            {executionLogs.map((log, idx) => (
                                                <div key={idx}>$ {log}</div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                
                                {/* Action Buttons */}
                                <div className="flex space-x-3">
                                    <button
                                        onClick={() => {
                                            // Re-run tests
                                            setTestResults(null);
                                            setIsExecutingTests(false);
                                            setExecutionPhase('idle');
                                            setExecutionProgress(0);
                                            setExecutionLogs([]);
                                            setAutoExecutingTests(false);
                                            setTimeout(() => handleExecuteTests(), 100);
                                        }}
                                        className="flex-1 bg-slate-100 text-slate-700 py-3 px-4 rounded-lg hover:bg-slate-200 transition-all text-sm font-medium flex items-center justify-center"
                                    >
                                        <RefreshCw className="h-4 w-4 mr-2" />
                                        Re-run Tests
                                    </button>
                                    <button
                                        onClick={() => {
                                            // Start new test
                                            setCurrentStep(1);
                                            // setResults(null);  // Commented - results not currently used
                                            setTestResults(null);
                                            setGeneratedCode(null);
                                            setGeneratedTests(null);
                                            setExtractedElements(null);
                                            setCompletedSteps([]);
                                            setFormData({ url: 'https://www.example.com' });
                                        }}
                                        className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-all text-sm font-medium flex items-center justify-center shadow-sm hover:shadow-md"
                                    >
                                        <Play className="h-4 w-4 mr-2" />
                                        Start New Test
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                );
            
            default:
                return null;
        }
    };

    return (
        <div className="h-[calc(100vh-49px)] sm:h-[calc(100vh-57px)] flex relative bg-slate-50">
            {/* Mobile Menu Button */}
            <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden absolute top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md border border-slate-200"
            >
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            {/* Sidebar - Vertical Navigation */}
            <div className={`
                ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
                md:translate-x-0 transition-transform duration-300
                fixed md:relative w-64 md:w-72 h-full bg-white border-r border-slate-200 z-40
                flex flex-col
            `}>
                {/* Header */}
                <div className="p-4 border-b border-slate-200">
                    <Link to="/" className="flex items-center space-x-2 text-sm text-slate-600 hover:text-slate-900 mb-3">
                        <ArrowLeft className="h-4 w-4" />
                        <span>Back</span>
                    </Link>
                    <h1 className="text-lg font-semibold text-slate-900">Web Automation</h1>
                    <div className="mt-2 text-xs text-slate-500">
                        Step {currentStep} of {steps.length}
                    </div>
                </div>

                {/* Steps List - Vertical */}
                <div className="flex-1 overflow-y-auto p-3">
                    {steps.map((step) => {
                        const StepIcon = step.icon;
                        const isActive = currentStep === step.id;
                        const isCompleted = completedSteps.includes(step.id);
                        
                        return (
                            <button
                                key={step.id}
                                onClick={() => {
                                    setCurrentStep(step.id);
                                    if (window.innerWidth < 768) {
                                        setSidebarOpen(false);
                                    }
                                }}
                                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg mb-1 transition-all text-sm ${
                                    isActive
                                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                                        : isCompleted
                                        ? 'bg-green-50 text-green-700 hover:bg-green-100'
                                        : 'hover:bg-slate-50 text-slate-600'
                                }`}
                            >
                                <StepIcon className="h-4 w-4 flex-shrink-0" />
                                <span className="text-left flex-1">{step.title}</span>
                                {isCompleted && <CheckCircle className="h-3 w-3 text-green-600" />}
                            </button>
                        );
                    })}
                </div>

                {/* Progress Summary */}
                <div className="p-3 border-t border-slate-200">
                    <div className="text-xs text-slate-500">Progress</div>
                    <div className="mt-1 w-full bg-slate-200 rounded-full h-2">
                        <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(completedSteps.length / steps.length) * 100}%` }}
                        />
                    </div>
                    <div className="mt-1 text-xs text-slate-600">
                        {completedSteps.length} of {steps.length} completed
                    </div>
                </div>
            </div>

            {/* Overlay for mobile */}
            {sidebarOpen && (
                <div
                    className="md:hidden fixed inset-0 bg-black bg-opacity-25 z-30"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                {/* Content */}
                <div className="flex-1 bg-white m-4 rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                    <div className="h-full overflow-auto p-4">
                        {renderStepContent()}
                    </div>
                </div>
            </div>
            
            {/* Code Viewer Modal */}
            {selectedFile && (
                <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] flex flex-col">
                        {/* Modal Header */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
                            <div className="flex items-center space-x-3">
                                <Code className="h-5 w-5 text-blue-600" />
                                <div>
                                    <h3 className="text-lg font-semibold text-slate-900">{selectedFile.filename}</h3>
                                    <p className="text-xs text-slate-500">
                                        {selectedFile.content.split('\n').length} lines of Python code
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-2">
                                {/* Copy Button */}
                                <button
                                    onClick={() => {
                                        navigator.clipboard.writeText(selectedFile.content);
                                        // You could add a toast notification here
                                    }}
                                    className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                                    title="Copy code"
                                >
                                    <Copy className="h-4 w-4" />
                                </button>
                                {/* Download Button */}
                                <button
                                    onClick={() => {
                                        const blob = new Blob([selectedFile.content], { type: 'text/plain' });
                                        const url = URL.createObjectURL(blob);
                                        const a = document.createElement('a');
                                        a.href = url;
                                        a.download = selectedFile.filename;
                                        document.body.appendChild(a);
                                        a.click();
                                        document.body.removeChild(a);
                                        URL.revokeObjectURL(url);
                                    }}
                                    className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                                    title="Download file"
                                >
                                    <Download className="h-4 w-4" />
                                </button>
                                {/* Close Button */}
                                <button
                                    onClick={() => setSelectedFile(null)}
                                    className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                                    title="Close"
                                >
                                    <X className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                        
                        {/* Code Content with Syntax Highlighting */}
                        <div className="flex-1 overflow-auto">
                            <div className="relative">
                                {/* Clean the code content - remove markdown code blocks if present */}
                                <SyntaxHighlighter
                                    language="python"
                                    style={vscDarkPlus}
                                    showLineNumbers={true}
                                    customStyle={{
                                        margin: 0,
                                        padding: '1.5rem',
                                        fontSize: '0.875rem',
                                        lineHeight: '1.5',
                                    }}
                                    lineNumberStyle={{
                                        color: '#6b7280',
                                        paddingRight: '1.5rem',
                                        userSelect: 'none',
                                    }}
                                >
                                    {selectedFile.content.replace(/^```python\n/, '').replace(/\n```$/, '').replace(/^```\n/, '')}
                                </SyntaxHighlighter>
                            </div>
                        </div>
                        
                        {/* Modal Footer */}
                        <div className="flex items-center justify-between px-6 py-3 border-t border-slate-200 bg-slate-50">
                            <div className="text-xs text-slate-500">
                                {selectedFile.filename.endsWith('test_') || selectedFile.filename.startsWith('test_') 
                                    ? 'Test File' 
                                    : selectedFile.filename.includes('page') 
                                    ? 'Page Object' 
                                    : 'Configuration'}
                            </div>
                            <button
                                onClick={() => setSelectedFile(null)}
                                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}