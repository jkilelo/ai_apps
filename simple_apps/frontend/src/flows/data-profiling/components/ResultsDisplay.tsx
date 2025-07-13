import React from 'react';
import { motion } from 'framer-motion';
import {
    CheckCircle,
    Clock,
    XCircle,
    Database,
    BarChart3,
    Code,
    Play,
    Copy,
    Download
} from 'lucide-react';

interface StepResult {
    step: string;
    data: any;
    status: 'pending' | 'loading' | 'success' | 'error';
    error?: string;
    title?: string;
}

interface ResultsDisplayProps {
    results: StepResult[];
    currentStep: number;
    isLoading: boolean;
    error: string | null;
}

const getStepIcon = (step: string) => {
    if (step.includes('metadata')) return Database;
    if (step.includes('suggestions')) return BarChart3;
    if (step.includes('testcases')) return CheckCircle;
    if (step.includes('code')) return Code;
    if (step.includes('execution')) return Play;
    return CheckCircle;
};

const getStatusIcon = (status: string) => {
    switch (status) {
        case 'success': return CheckCircle;
        case 'loading': return Clock;
        case 'error': return XCircle;
        default: return Clock;
    }
};

const getStatusColor = (status: string) => {
    switch (status) {
        case 'success': return 'text-emerald-500 bg-emerald-50 border-emerald-200';
        case 'loading': return 'text-blue-500 bg-blue-50 border-blue-200';
        case 'error': return 'text-red-500 bg-red-50 border-red-200';
        default: return 'text-slate-400 bg-slate-50 border-slate-200';
    }
};

const ResultCard: React.FC<{ result: StepResult; index: number }> = ({ result, index }) => {
    const StepIcon = getStepIcon(result.step);
    const StatusIcon = getStatusIcon(result.status);

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`
        bg-white dark:bg-slate-800 rounded-xl border-2 transition-all duration-300 overflow-hidden
        ${getStatusColor(result.status)}
      `}
        >
            {/* Header */}
            <div className="p-6 border-b border-inherit">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className={`
              p-2 rounded-lg 
              ${result.status === 'success' ? 'bg-emerald-100 text-emerald-600' : ''}
              ${result.status === 'loading' ? 'bg-blue-100 text-blue-600' : ''}
              ${result.status === 'error' ? 'bg-red-100 text-red-600' : ''}
              ${result.status === 'pending' ? 'bg-slate-100 text-slate-400' : ''}
            `}>
                            <StepIcon className="w-5 h-5" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-slate-900 dark:text-white">
                                {result.title || result.step}
                            </h3>
                            <div className="flex items-center space-x-2 mt-1">
                                <StatusIcon className={`w-4 h-4 ${result.status === 'loading' ? 'animate-spin' : ''
                                    }`} />
                                <span className="text-sm capitalize">
                                    {result.status === 'loading' ? 'Processing...' : result.status}
                                </span>
                            </div>
                        </div>
                    </div>

                    {result.data && (
                        <div className="flex space-x-2">
                            <button
                                onClick={() => copyToClipboard(JSON.stringify(result.data, null, 2))}
                                className="p-2 text-slate-400 hover:text-slate-600 transition-colors"
                                title="Copy data"
                            >
                                <Copy className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => {
                                    const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' });
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = `${result.step}_result.json`;
                                    a.click();
                                }}
                                className="p-2 text-slate-400 hover:text-slate-600 transition-colors"
                                title="Download data"
                            >
                                <Download className="w-4 h-4" />
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Content */}
            {result.data && (
                <div className="p-6">
                    {/* Special handling for different data types */}
                    {result.step.includes('code') && result.data.pyspark_code ? (
                        <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
                            <pre className="text-green-400 text-sm">
                                <code>{result.data.pyspark_code}</code>
                            </pre>
                        </div>
                    ) : result.data.suggestions ? (
                        <div className="space-y-3">
                            {result.data.suggestions.map((suggestion: any, idx: number) => (
                                <div key={idx} className="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                                        {suggestion.suggestion_id || idx + 1}
                                    </div>
                                    <p className="text-slate-700 dark:text-slate-300">{suggestion.description}</p>
                                </div>
                            ))}
                        </div>
                    ) : result.data.test_cases ? (
                        <div className="space-y-3">
                            {result.data.test_cases.map((testCase: any, idx: number) => (
                                <div key={idx} className="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                                    <div className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-medium">
                                        {testCase.case_id || idx + 1}
                                    </div>
                                    <p className="text-slate-700 dark:text-slate-300">{testCase.description}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-4">
                            <pre className="text-sm text-slate-700 dark:text-slate-300 overflow-x-auto">
                                {JSON.stringify(result.data, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            )}

            {/* Error Display */}
            {result.error && (
                <div className="p-6 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
                    <p className="text-red-700 dark:text-red-400 text-sm">{result.error}</p>
                </div>
            )}
        </motion.div>
    );
};

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
    results,
    currentStep,
    isLoading,
    error
}) => {
    if (error) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
            >
                <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    Analysis Failed
                </h3>
                <p className="text-slate-600 dark:text-slate-400">{error}</p>
            </motion.div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Progress Summary */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                        Analysis Progress
                    </h2>
                    <div className="text-sm text-slate-600 dark:text-slate-400">
                        {results.filter(r => r.status === 'success').length} / {results.length} completed
                    </div>
                </div>

                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{
                            width: `${(results.filter(r => r.status === 'success').length / results.length) * 100}%`
                        }}
                        transition={{ duration: 0.5 }}
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                    />
                </div>
            </div>

            {/* Results Grid */}
            <div className="grid gap-6">
                {results.map((result, index) => (
                    <ResultCard key={result.step} result={result} index={index} />
                ))}
            </div>
        </div>
    );
};
