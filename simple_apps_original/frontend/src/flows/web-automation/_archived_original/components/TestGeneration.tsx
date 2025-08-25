import { motion } from 'framer-motion';
import { WorkflowStep } from '../hooks/useWebAutomation';

interface TestGenerationProps {
    workflow: WorkflowStep[];
    onChange: (workflow: WorkflowStep[]) => void;
    targetUrl: string;
    onNext: () => void;
    onBack: () => void;
}

export function TestGeneration({ workflow, onChange, targetUrl, onNext, onBack }: TestGenerationProps) {
    return (
        <div className="h-full w-full">
            <div className="bg-gradient-to-r from-[#004685]/10 to-blue-500/10 border-b border-[#004685]/20 dark:border-[#004685]/20 p-6">
                <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-[#004685] to-blue-600 rounded-2xl flex items-center justify-center">
                        <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-[#004685] dark:text-[#004685]">Workflow Builder</h2>
                        <p className="text-sm text-slate-600 dark:text-slate-400">
                            Target: {targetUrl}
                        </p>
                    </div>
                </div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-6 overflow-y-auto max-h-96"
            >

                <div className="space-y-4 mb-8">
                    {workflow.length === 0 ? (
                        <p className="text-slate-500 text-center py-8">No workflow steps added yet</p>
                    ) : (
                        workflow.map((step, index) => (
                            <div key={step.id} className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                                <div className="flex items-center justify-between">
                                    <span className="font-medium">{index + 1}. {step.description}</span>
                                    <span className="text-sm text-slate-500">{step.type}</span>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                <div className="flex justify-between">
                    <button
                        onClick={onBack}
                        className="px-6 py-2 text-slate-600 hover:text-slate-900 transition-colors"
                    >
                        Back
                    </button>
                    <motion.button
                        onClick={onNext}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="px-8 py-3 bg-gradient-to-r from-[#004685] to-blue-600 text-white rounded-2xl hover:shadow-xl transition-all shadow-lg shadow-[#004685]/25"
                    >
                        Continue to Execution
                    </motion.button>
                </div>
            </motion.div>
        </div>
    );
}
