import { motion } from 'framer-motion';
import { ChartBarIcon, ArrowLeftIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import type { AutomationResults } from '../hooks/useWebAutomation';

interface AutomationResultsProps {
    results: AutomationResults | null;
    onReset: () => void;
    onBack: () => void;
}

export function AutomationResults({ results, onReset, onBack }: AutomationResultsProps) {
    if (!results) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center py-8">
                    <p className="text-slate-600 dark:text-slate-300">No results available</p>
                </div>
            </div>
        );
    }

    const successRate = Math.round((results.metrics.passedSteps / (results.metrics.passedSteps + results.metrics.failedSteps)) * 100);

    return (
        <div className="space-y-6 p-6">
            <div className="bg-gradient-to-r from-[#004685]/10 to-blue-500/10 border-b border-[#004685]/20 dark:border-[#004685]/20 p-6 -m-6 mb-6">
                <div className="bg-gradient-to-r from-[#004685]/10 to-blue-500/10 border-b border-[#004685]/20 dark:border-[#004685]/20 p-6">
                    <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-r from-[#004685] to-blue-600 rounded-2xl flex items-center justify-center">
                            <ChartBarIcon className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-[#004685] dark:text-[#004685]">Automation Results</h2>
                            <p className="text-sm text-slate-600 dark:text-slate-400">Test execution completed with {successRate}% success rate</p>
                        </div>
                    </div>
                </div>

                <div className="p-6 space-y-6">
                    {/* Metrics Summary */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="text-center p-4 bg-green-50 dark:bg-green-900/30 rounded-xl border border-green-200 dark:border-green-800">
                            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{results.metrics.passedSteps}</div>
                            <div className="text-sm text-slate-600 dark:text-slate-300">Passed</div>
                        </div>
                        <div className="text-center p-4 bg-red-50 dark:bg-red-900/30 rounded-xl border border-red-200 dark:border-red-800">
                            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{results.metrics.failedSteps}</div>
                            <div className="text-sm text-slate-600 dark:text-slate-300">Failed</div>
                        </div>
                        <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/30 rounded-xl border border-blue-200 dark:border-blue-800">
                            <div className="text-2xl font-bold text-[#004685] dark:text-[#004685]">{results.executionTime}ms</div>
                            <div className="text-sm text-slate-600 dark:text-slate-300">Duration</div>
                        </div>
                    </div>

                    {/* Step Results */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Step Results</h3>
                        <div className="space-y-2 max-h-64 overflow-y-auto">
                            {results.steps.map((stepResult, index) => (
                                <div key={index} className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${stepResult.status === 'passed'
                                                ? 'bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-200'
                                                : 'bg-red-100 text-red-700 dark:bg-red-800 dark:text-red-200'
                                                }`}>
                                                {index + 1}
                                            </div>
                                            <span className="font-medium text-slate-900 dark:text-white">{stepResult.step.description}</span>
                                        </div>
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${stepResult.status === 'passed'
                                            ? 'bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-200'
                                            : 'bg-red-100 text-red-700 dark:bg-red-800 dark:text-red-200'
                                            }`}>
                                            {stepResult.status}
                                        </span>
                                    </div>
                                    {stepResult.error && (
                                        <p className="text-red-600 dark:text-red-400 text-sm mt-2 ml-9">{stepResult.error}</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Navigation */}
                    <div className="flex justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
                        <motion.button
                            onClick={onBack}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="px-6 py-2 rounded-lg font-medium flex items-center space-x-2 text-slate-600 dark:text-slate-300 hover:text-[#004685] dark:hover:text-[#004685] transition-all"
                        >
                            <ArrowLeftIcon className="h-4 w-4" />
                            <span>Back</span>
                        </motion.button>
                        <motion.button
                            onClick={onReset}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="px-6 py-2 bg-gradient-to-r from-[#004685] to-blue-600 text-white font-medium rounded-lg hover:shadow-lg shadow-[#004685]/25 transition-all flex items-center space-x-2"
                        >
                            <ArrowPathIcon className="h-4 w-4" />
                            <span>Start New Test</span>
                        </motion.button>
                    </div>
                </div>
            </div>
        </div>
    );
}
