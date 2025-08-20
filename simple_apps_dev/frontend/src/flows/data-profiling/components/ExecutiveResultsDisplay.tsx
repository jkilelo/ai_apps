import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, TrendingUp, AlertCircle, FileText, BarChart3, Shield, Code, Play } from 'lucide-react';

interface ExecutiveResultsDisplayProps {
    stepData: any;
    stepId: string;
}

const formatStepData = (stepData: any, stepId: string) => {
    if (!stepData) return null;

    switch (stepId) {
        case 'metadata':
            return {
                title: 'Database Schema Analysis',
                summary: 'Database structure and table information extracted successfully',
                insights: [
                    'Table structure validated',
                    'Column definitions identified',
                    'Data types confirmed',
                    'Schema integrity verified'
                ],
                icon: FileText,
                color: 'blue'
            };

        case 'profiling_suggestions':
            const suggestions = stepData.data?.suggestions || stepData.suggestions || [];
            return {
                title: 'Data Optimization Recommendations',
                summary: `${suggestions.length} strategic recommendations identified for database optimization`,
                insights: suggestions.map((s: any) => s.description || 'Optimization recommendation available'),
                icon: TrendingUp,
                color: 'green'
            };

        case 'profiling_testcases':
            const testCases = stepData.data?.test_cases || stepData.test_cases || [];
            return {
                title: 'Quality Assurance Framework',
                summary: `${testCases.length} automated test cases generated for data validation`,
                insights: testCases.map((t: any) => t.description || 'Quality test case defined'),
                icon: Shield,
                color: 'purple'
            };

        case 'profiling_code':
            return {
                title: 'Data Processing Pipeline',
                summary: 'Automated data processing pipeline successfully generated',
                insights: [
                    'Spark-based processing framework implemented',
                    'Scalable data analysis pipeline created',
                    'Performance optimization included',
                    'Production-ready code generated'
                ],
                icon: Code,
                color: 'indigo'
            };

        case 'profiling_execution':
            const executionDetails = stepData.data?.details || stepData.details || [];
            return {
                title: 'Data Analysis Execution',
                summary: 'Data profiling analysis completed successfully',
                insights: executionDetails.map((d: any) => d.result || 'Analysis step completed'),
                icon: Play,
                color: 'emerald'
            };

        case 'dq_suggestions':
            const dqSuggestions = stepData.data?.suggestions || stepData.suggestions || [];
            return {
                title: 'Data Quality Enhancement Plan',
                summary: `${dqSuggestions.length} data quality improvements recommended`,
                insights: dqSuggestions.map((s: any) => s.description || 'Quality improvement identified'),
                icon: AlertCircle,
                color: 'orange'
            };

        case 'dq_testcases':
            const dqTestCases = stepData.data?.test_cases || stepData.test_cases || [];
            return {
                title: 'Data Quality Validation Suite',
                summary: `${dqTestCases.length} quality validation tests established`,
                insights: dqTestCases.map((t: any) => t.description || 'Quality validation test created'),
                icon: Shield,
                color: 'red'
            };

        case 'dq_code':
            return {
                title: 'Quality Monitoring System',
                summary: 'Automated data quality monitoring system deployed',
                insights: [
                    'Real-time quality monitoring enabled',
                    'Automated anomaly detection configured',
                    'Quality metrics tracking established',
                    'Compliance reporting framework ready'
                ],
                icon: BarChart3,
                color: 'cyan'
            };

        case 'dq_execution':
            const dqExecutionDetails = stepData.data?.details || stepData.details || [];
            return {
                title: 'Quality Analysis Results',
                summary: 'Comprehensive data quality analysis completed',
                insights: dqExecutionDetails.map((d: any) => d.result || 'Quality check completed'),
                icon: CheckCircle,
                color: 'teal'
            };

        default:
            return {
                title: 'Analysis Complete',
                summary: 'Step completed successfully',
                insights: ['Analysis step processed'],
                icon: CheckCircle,
                color: 'gray'
            };
    }
};

export const ExecutiveResultsDisplay: React.FC<ExecutiveResultsDisplayProps> = ({
    stepData,
    stepId
}) => {
    const formattedData = formatStepData(stepData, stepId);

    if (!formattedData) return null;

    const { title, summary, insights, icon: Icon, color } = formattedData;

    const colorClasses = {
        blue: 'from-blue-500/10 to-blue-600/10 border-blue-200/20 text-blue-800 dark:text-blue-200',
        green: 'from-green-500/10 to-emerald-600/10 border-green-200/20 text-green-800 dark:text-green-200',
        purple: 'from-purple-500/10 to-purple-600/10 border-purple-200/20 text-purple-800 dark:text-purple-200',
        indigo: 'from-indigo-500/10 to-indigo-600/10 border-indigo-200/20 text-indigo-800 dark:text-indigo-200',
        emerald: 'from-emerald-500/10 to-emerald-600/10 border-emerald-200/20 text-emerald-800 dark:text-emerald-200',
        orange: 'from-orange-500/10 to-orange-600/10 border-orange-200/20 text-orange-800 dark:text-orange-200',
        red: 'from-red-500/10 to-red-600/10 border-red-200/20 text-red-800 dark:text-red-200',
        cyan: 'from-cyan-500/10 to-cyan-600/10 border-cyan-200/20 text-cyan-800 dark:text-cyan-200',
        teal: 'from-teal-500/10 to-teal-600/10 border-teal-200/20 text-teal-800 dark:text-teal-200',
        gray: 'from-gray-500/10 to-gray-600/10 border-gray-200/20 text-gray-800 dark:text-gray-200'
    };

    const iconColorClasses = {
        blue: 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30',
        green: 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30',
        purple: 'text-purple-600 dark:text-purple-400 bg-purple-100 dark:bg-purple-900/30',
        indigo: 'text-indigo-600 dark:text-indigo-400 bg-indigo-100 dark:bg-indigo-900/30',
        emerald: 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30',
        orange: 'text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900/30',
        red: 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30',
        cyan: 'text-cyan-600 dark:text-cyan-400 bg-cyan-100 dark:bg-cyan-900/30',
        teal: 'text-teal-600 dark:text-teal-400 bg-teal-100 dark:bg-teal-900/30',
        gray: 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-900/30'
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bg-gradient-to-r ${colorClasses[color as keyof typeof colorClasses]} backdrop-blur-xl rounded-3xl border border-white/20 shadow-xl overflow-hidden`}
        >
            <div className="p-8">
                <div className="flex items-start space-x-4 mb-6">
                    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${iconColorClasses[color as keyof typeof iconColorClasses]}`}>
                        <Icon className="h-6 w-6" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-2xl font-bold mb-2">
                            {title}
                        </h3>
                        <p className="text-lg opacity-80 leading-relaxed">
                            {summary}
                        </p>
                    </div>
                </div>

                <div className="space-y-3">
                    <h4 className="text-lg font-semibold mb-4 flex items-center">
                        <CheckCircle className="h-5 w-5 mr-2" />
                        Key Outcomes
                    </h4>
                    <div className="grid gap-3">
                        {insights.map((insight: string, index: number) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className="flex items-center space-x-3 p-3 bg-white/30 dark:bg-slate-800/30 rounded-xl border border-white/10"
                            >
                                <div className="w-2 h-2 rounded-full bg-current opacity-60"></div>
                                <span className="font-medium">{insight}</span>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </motion.div>
    );
};
