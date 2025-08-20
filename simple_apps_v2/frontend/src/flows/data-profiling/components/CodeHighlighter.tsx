import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface CodeHighlighterProps {
    code: string;
    language?: string;
    title?: string;
    isDark?: boolean;
}

export const CodeHighlighter: React.FC<CodeHighlighterProps> = ({
    code,
    language = 'json',
    title,
    isDark = false
}) => {
    const [copied, setCopied] = React.useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy code:', err);
        }
    };

    const formatCode = (rawCode: string, lang: string) => {
        if (lang === 'json') {
            try {
                const parsed = typeof rawCode === 'string' ? JSON.parse(rawCode) : rawCode;
                return JSON.stringify(parsed, null, 2);
            } catch {
                return typeof rawCode === 'object' ? JSON.stringify(rawCode, null, 2) : rawCode;
            }
        }
        return rawCode;
    };

    const formattedCode = formatCode(code, language);

    return (
        <div className="relative group">
            {/* Header with title and copy button */}
            {title && (
                <div className="flex items-center justify-between bg-slate-800 dark:bg-slate-900 px-4 py-2 rounded-t-2xl border-b border-slate-700">
                    <span className="text-sm font-medium text-slate-300">{title}</span>
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={handleCopy}
                        className="p-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 hover:text-white transition-all"
                        title="Copy to clipboard"
                    >
                        {copied ? (
                            <Check className="h-4 w-4 text-green-400" />
                        ) : (
                            <Copy className="h-4 w-4" />
                        )}
                    </motion.button>
                </div>
            )}

            {/* Code block */}
            <div className="relative overflow-hidden rounded-2xl">
                {!title && (
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={handleCopy}
                        className="absolute top-3 right-3 z-10 p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-all opacity-0 group-hover:opacity-100"
                        title="Copy to clipboard"
                    >
                        {copied ? (
                            <Check className="h-4 w-4 text-green-400" />
                        ) : (
                            <Copy className="h-4 w-4" />
                        )}
                    </motion.button>
                )}

                <SyntaxHighlighter
                    language={language}
                    style={isDark ? vscDarkPlus : vs}
                    customStyle={{
                        margin: 0,
                        borderRadius: title ? '0 0 16px 16px' : '16px',
                        fontSize: '13px',
                        lineHeight: '1.5',
                        padding: '16px',
                        maxHeight: '400px',
                        background: isDark
                            ? 'linear-gradient(145deg, #1e293b 0%, #0f172a 100%)'
                            : 'linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%)',
                    }}
                    showLineNumbers={language !== 'json'}
                    wrapLines={true}
                    wrapLongLines={true}
                >
                    {formattedCode}
                </SyntaxHighlighter>
            </div>
        </div>
    );
};

// Helper function to detect language from content
export const detectLanguage = (content: any): string => {
    if (typeof content === 'object') {
        return 'json';
    }

    const str = String(content).toLowerCase();

    if (str.includes('from pyspark') || str.includes('spark =') || str.includes('spark.sql')) {
        return 'python';
    }

    if (str.includes('select ') || str.includes('from ') || str.includes('where ')) {
        return 'sql';
    }

    if (str.includes('function') || str.includes('const ') || str.includes('let ')) {
        return 'javascript';
    }

    try {
        JSON.parse(str);
        return 'json';
    } catch {
        return 'text';
    }
};

// Specialized component for PySpark code display
export const PySparkCodeDisplay: React.FC<{ stepData: any }> = ({ stepData }) => {
    const pysparkCode = stepData?.step_data?.pyspark_code || stepData?.pyspark_code;

    if (!pysparkCode) {
        return (
            <div className="text-center py-8 text-slate-500">
                No PySpark code available
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="ml-2 text-sm font-medium text-slate-600 dark:text-slate-300">
                    PySpark Code Generator
                </span>
            </div>

            <CodeHighlighter
                code={pysparkCode}
                language="python"
                title="Generated PySpark Code"
                isDark={true}
            />
        </div>
    );
};

export const ExecutionResultsDisplay: React.FC<{ stepData: any }> = ({ stepData }) => {
    const executionResult = stepData?.step_data?.execution_result;
    const details = stepData?.step_data?.details;

    return (
        <div className="space-y-4">
            {executionResult && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4">
                    <div className="flex items-center space-x-2 mb-2">
                        <Check className="h-5 w-5 text-green-600 dark:text-green-400" />
                        <span className="font-medium text-green-800 dark:text-green-200">
                            Execution Status
                        </span>
                    </div>
                    <p className="text-green-700 dark:text-green-300">{executionResult}</p>
                </div>
            )}

            {details && details.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-slate-900 dark:text-white">Execution Details:</h4>
                    {details.map((detail: any, index: number) => (
                        <div key={index} className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                            <div className="flex items-center space-x-2">
                                <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                                    Step {detail.step}:
                                </span>
                                <span className="text-sm text-blue-700 dark:text-blue-300">
                                    {detail.result}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
