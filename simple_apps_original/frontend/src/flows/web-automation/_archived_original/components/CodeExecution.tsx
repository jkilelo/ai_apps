import { motion } from 'framer-motion';
import { PlayIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import { WorkflowStep } from '../hooks/useWebAutomation';

interface CodeExecutionProps {
    workflow: WorkflowStep[];
    onExecute: () => void;
    onBack: () => void;
    isLoading: boolean;
}

export function CodeExecution({ workflow, onExecute, onBack, isLoading }: CodeExecutionProps) {
    return (
        <div className="space-y-6 p-6">
            <div className="bg-gradient-to-r from-[#004685]/10 to-blue-500/10 border-b border-[#004685]/20 dark:border-[#004685]/20 p-6 -m-6 mb-6">
                <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-[#004685] to-blue-600 rounded-2xl flex items-center justify-center">
                        <PlayIcon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-[#004685] dark:text-[#004685]">Test Execution</h2>
                        <p className="text-sm text-slate-600 dark:text-slate-400">Ready to execute {workflow.length} workflow steps</p>
                    </div>
                </div>
            </div>

            <div className="p-6 space-y-6">
                {/* Workflow Preview */}
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Workflow Overview</h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {workflow.map((step, index) => (
                            <div key={index} className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                                <div className="w-6 h-6 bg-[#004685] text-white rounded-full flex items-center justify-center text-xs font-medium">
                                    {index + 1}
                                </div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-slate-900 dark:text-white">{step.description}</p>
                                    <p className="text-xs text-slate-500 dark:text-slate-400">{step.type} {step.selector ? `- ${step.selector}` : ''}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Execution Status */}
                {isLoading ? (
                    <div className="text-center py-8">
                        <div className="w-16 h-16 border-4 border-[#004685]/20 border-t-[#004685] rounded-full animate-spin mx-auto mb-4"></div>
                        <p className="text-slate-600 dark:text-slate-300 font-medium">Executing workflow...</p>
                        <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">This may take a few moments</p>
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <motion.button
                            onClick={onExecute}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="px-8 py-4 bg-gradient-to-r from-[#004685] to-blue-600 text-white font-medium rounded-2xl hover:shadow-xl shadow-[#004685]/25 transition-all flex items-center space-x-2 mx-auto"
                        >
                            <PlayIcon className="h-5 w-5" />
                            <span>Execute Workflow</span>
                        </motion.button>
                    </div>
                )}

                {/* Navigation */}
                <div className="flex justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
                    <motion.button
                        onClick={onBack}
                        disabled={isLoading}
                        whileHover={!isLoading ? { scale: 1.02 } : {}}
                        whileTap={!isLoading ? { scale: 0.98 } : {}}
                        className={`px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all ${isLoading
                            ? 'text-slate-400 dark:text-slate-500 cursor-not-allowed'
                            : 'text-slate-600 dark:text-slate-300 hover:text-[#004685] dark:hover:text-[#004685]'
                            }`}
                    >
                        <ArrowLeftIcon className="h-4 w-4" />
                        <span>Back</span>
                    </motion.button>
                </div>
            </div>
        </div>
    );
}
