import { motion } from 'framer-motion';
import { ArrowRightIcon, GlobeAltIcon } from '@heroicons/react/24/outline';
import { AutomationFormData } from '../hooks/useWebAutomation';

interface AutomationFormProps {
    data: AutomationFormData;
    onChange: (data: AutomationFormData) => void;
    onNext: () => void;
}

export function AutomationForm({ data, onChange, onNext }: AutomationFormProps) {
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (data.targetUrl && data.testName) {
            onNext();
        }
    };

    const isValid = data.targetUrl && data.testName;

    return (
        <div className="h-full flex items-center justify-center overflow-y-auto">
            <div className="w-full max-w-xl space-y-8 py-8 px-4">
                <div className="text-center space-y-4 mb-8">
                    <div className="w-16 h-16 bg-gradient-to-r from-[#004685] to-blue-600 rounded-2xl flex items-center justify-center mx-auto">
                        <GlobeAltIcon className="h-8 w-8 text-white" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-[#004685] dark:text-white">Target Setup</h2>
                        <p className="text-slate-600 dark:text-slate-400">Configure your automation target and preferences</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-xl rounded-3xl border border-white/20 dark:border-slate-700/30 shadow-xl p-8 space-y-6">
                    {/* Basic Information */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center space-x-2">
                            <GlobeAltIcon className="h-5 w-5 text-[#004685]" />
                            <span>Basic Information</span>
                        </h3>

                        <div className="grid grid-cols-1 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Target URL *
                                </label>
                                <input
                                    type="url"
                                    value={data.targetUrl}
                                    onChange={(e) => onChange({ ...data, targetUrl: e.target.value })}
                                    placeholder="https://example.com"
                                    className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-[#004685] focus:border-transparent transition-all"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Test Name *
                                </label>
                                <input
                                    type="text"
                                    value={data.testName}
                                    onChange={(e) => onChange({ ...data, testName: e.target.value })}
                                    placeholder="My Website Test"
                                    className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-[#004685] focus:border-transparent transition-all"
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    {/* Description */}
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                Description (Optional)
                            </label>
                            <textarea
                                value={data.description}
                                onChange={(e) => onChange({ ...data, description: e.target.value })}
                                placeholder="Describe what this automation will test..."
                                rows={3}
                                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-[#004685] focus:border-transparent transition-all resize-none"
                            />
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="flex justify-center pt-4 border-t border-slate-200 dark:border-slate-700">
                        <motion.button
                            type="submit"
                            disabled={!isValid}
                            whileHover={isValid ? { scale: 1.02 } : {}}
                            whileTap={isValid ? { scale: 0.98 } : {}}
                            className={`px-8 py-4 rounded-2xl font-medium flex items-center space-x-2 transition-all shadow-lg ${isValid
                                ? 'bg-gradient-to-r from-[#004685] to-blue-600 text-white hover:shadow-xl shadow-[#004685]/25'
                                : 'bg-slate-300 dark:bg-slate-600 text-slate-500 dark:text-slate-400 cursor-not-allowed'
                                }`}
                        >
                            <span>Continue to Workflow Builder</span>
                            <ArrowRightIcon className="h-4 w-4" />
                        </motion.button>
                    </div>
                </form>
            </div>
        </div>
    );
}
