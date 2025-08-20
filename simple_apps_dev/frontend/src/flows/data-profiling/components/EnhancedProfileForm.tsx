import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Database,
    Table,
    Columns,
    Play,
    Loader,
    CheckCircle,
    AlertCircle,
    Eye,
    EyeOff,
    ChevronDown
} from 'lucide-react';
import { HelpTooltip, FocusRing } from './UIComponents';

interface ProfileFormData {
    database: string;
    table: string;
    columns: string[];
    connectionString?: string;
    username?: string;
    password?: string;
}

interface ValidationError {
    field: string;
    message: string;
}

interface EnhancedProfileFormProps {
    onSubmit: (data: ProfileFormData) => void;
    isLoading: boolean;
}

export const EnhancedProfileForm: React.FC<EnhancedProfileFormProps> = ({ onSubmit, isLoading }) => {
    const [formData, setFormData] = useState<ProfileFormData>({
        database: '',
        table: '',
        columns: [],
        connectionString: '',
        username: '',
        password: ''
    });

    const [columnsInput, setColumnsInput] = useState('');
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
    const [fieldFocus, setFieldFocus] = useState<string | null>(null);

    // Real-time validation
    const validateField = (field: string, value: string): string | null => {
        switch (field) {
            case 'database':
                if (!value.trim()) return 'Database name is required';
                if (value.length < 2) return 'Database name must be at least 2 characters';
                if (!/^[a-zA-Z0-9_-]+$/.test(value)) return 'Only letters, numbers, hyphens, and underscores allowed';
                return null;
            case 'table':
                if (!value.trim()) return 'Table name is required';
                if (value.length < 2) return 'Table name must be at least 2 characters';
                if (!/^[a-zA-Z0-9_-]+$/.test(value)) return 'Only letters, numbers, hyphens, and underscores allowed';
                return null;
            case 'connectionString':
                if (showAdvanced && value && !value.includes('://')) {
                    return 'Please provide a valid connection string format';
                }
                return null;
            default:
                return null;
        }
    };

    const updateValidationErrors = (field: string, value: string) => {
        const error = validateField(field, value);
        setValidationErrors(prev => {
            const filtered = prev.filter(e => e.field !== field);
            return error ? [...filtered, { field, message: error }] : filtered;
        });
    };

    const handleInputChange = (field: keyof ProfileFormData, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        updateValidationErrors(field, value);
    };

    const getFieldError = (field: string) =>
        validationErrors.find(e => e.field === field)?.message;

    const isFieldValid = (field: string) =>
        formData[field as keyof ProfileFormData] && !getFieldError(field);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Validate all required fields
        const requiredFields = ['database', 'table'];
        const errors: ValidationError[] = [];

        requiredFields.forEach(field => {
            const error = validateField(field, formData[field as keyof ProfileFormData] as string);
            if (error) errors.push({ field, message: error });
        });

        if (errors.length > 0) {
            setValidationErrors(errors);
            return;
        }

        const columns = columnsInput.split(',').map(col => col.trim()).filter(Boolean);
        onSubmit({ ...formData, columns });
    };

    // Suggested databases and tables for better UX
    const suggestedDatabases = ['postgres', 'mysql', 'sqlite', 'mongodb', 'oracle'];
    const suggestedTables = ['users', 'orders', 'products', 'transactions', 'customers'];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto"
        >
            <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 dark:border-slate-700/30 overflow-hidden">
                {/* Enhanced Header */}
                <div className="bg-gradient-to-r from-blue-500/10 via-indigo-500/10 to-purple-500/10 border-b border-white/20 dark:border-slate-700/30 p-8">
                    <div className="text-center">
                        <motion.div
                            className="w-20 h-20 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg"
                            whileHover={{ scale: 1.05, rotate: 5 }}
                            transition={{ type: "spring", stiffness: 300 }}
                        >
                            <Database className="w-10 h-10 text-white" />
                        </motion.div>

                        <h2 className="text-3xl font-bold bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 dark:from-white dark:via-blue-100 dark:to-indigo-100 bg-clip-text text-transparent mb-3">
                            Configure Data Source
                        </h2>

                        <p className="text-slate-600 dark:text-slate-300 text-lg">
                            Connect your database to begin comprehensive analysis
                        </p>

                        <div className="flex items-center justify-center space-x-6 mt-4 text-sm text-slate-500 dark:text-slate-400">
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                                <span>Secure Connection</span>
                            </div>
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span>Real-time Analysis</span>
                            </div>
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                                <span>Smart Insights</span>
                            </div>
                        </div>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                    {/* Database Input with enhanced validation */}
                    <div>
                        <label className="flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                            <Database className="w-4 h-4 mr-2 text-blue-500" />
                            Database Name
                            <HelpTooltip
                                content="The name of your database (e.g., myapp_production, analytics_db)"
                                className="ml-2"
                            />
                        </label>

                        <FocusRing>
                            <div className="relative">
                                <input
                                    type="text"
                                    value={formData.database}
                                    onChange={(e) => handleInputChange('database', e.target.value)}
                                    onFocus={() => setFieldFocus('database')}
                                    onBlur={() => setFieldFocus(null)}
                                    placeholder="Enter database name..."
                                    className={`
                                        w-full px-4 py-3 pr-10 bg-slate-50 dark:bg-slate-700/50 border rounded-xl 
                                        transition-all duration-200 placeholder-slate-400 dark:placeholder-slate-500
                                        ${getFieldError('database')
                                            ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                                            : isFieldValid('database')
                                                ? 'border-emerald-300 focus:border-emerald-500 focus:ring-emerald-500/20'
                                                : 'border-slate-200 dark:border-slate-600 focus:border-blue-500 focus:ring-blue-500/20'
                                        }
                                        focus:ring-4
                                    `}
                                    required
                                />

                                {/* Validation indicator */}
                                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                                    {getFieldError('database') ? (
                                        <AlertCircle className="w-5 h-5 text-red-500" />
                                    ) : isFieldValid('database') ? (
                                        <CheckCircle className="w-5 h-5 text-emerald-500" />
                                    ) : null}
                                </div>
                            </div>
                        </FocusRing>

                        {/* Error message */}
                        <AnimatePresence>
                            {getFieldError('database') && (
                                <motion.p
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="text-sm text-red-600 dark:text-red-400 mt-2 flex items-center space-x-1"
                                >
                                    <AlertCircle className="w-4 h-4" />
                                    <span>{getFieldError('database')}</span>
                                </motion.p>
                            )}
                        </AnimatePresence>

                        {/* Suggestions */}
                        {fieldFocus === 'database' && !formData.database && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-2"
                            >
                                <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">Popular databases:</p>
                                <div className="flex flex-wrap gap-2">
                                    {suggestedDatabases.map(db => (
                                        <button
                                            key={db}
                                            type="button"
                                            onClick={() => handleInputChange('database', db)}
                                            className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-md hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                                        >
                                            {db}
                                        </button>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </div>

                    {/* Table Input with enhanced validation */}
                    <div>
                        <label className="flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                            <Table className="w-4 h-4 mr-2 text-indigo-500" />
                            Table Name
                            <HelpTooltip
                                content="The specific table you want to analyze (e.g., user_profiles, order_history)"
                                className="ml-2"
                            />
                        </label>

                        <FocusRing>
                            <div className="relative">
                                <input
                                    type="text"
                                    value={formData.table}
                                    onChange={(e) => handleInputChange('table', e.target.value)}
                                    onFocus={() => setFieldFocus('table')}
                                    onBlur={() => setFieldFocus(null)}
                                    placeholder="Enter table name..."
                                    className={`
                                        w-full px-4 py-3 pr-10 bg-slate-50 dark:bg-slate-700/50 border rounded-xl 
                                        transition-all duration-200 placeholder-slate-400 dark:placeholder-slate-500
                                        ${getFieldError('table')
                                            ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                                            : isFieldValid('table')
                                                ? 'border-emerald-300 focus:border-emerald-500 focus:ring-emerald-500/20'
                                                : 'border-slate-200 dark:border-slate-600 focus:border-blue-500 focus:ring-blue-500/20'
                                        }
                                        focus:ring-4
                                    `}
                                    required
                                />

                                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                                    {getFieldError('table') ? (
                                        <AlertCircle className="w-5 h-5 text-red-500" />
                                    ) : isFieldValid('table') ? (
                                        <CheckCircle className="w-5 h-5 text-emerald-500" />
                                    ) : null}
                                </div>
                            </div>
                        </FocusRing>

                        <AnimatePresence>
                            {getFieldError('table') && (
                                <motion.p
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="text-sm text-red-600 dark:text-red-400 mt-2 flex items-center space-x-1"
                                >
                                    <AlertCircle className="w-4 h-4" />
                                    <span>{getFieldError('table')}</span>
                                </motion.p>
                            )}
                        </AnimatePresence>

                        {fieldFocus === 'table' && !formData.table && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-2"
                            >
                                <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">Common table names:</p>
                                <div className="flex flex-wrap gap-2">
                                    {suggestedTables.map(table => (
                                        <button
                                            key={table}
                                            type="button"
                                            onClick={() => handleInputChange('table', table)}
                                            className="px-2 py-1 text-xs bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-md hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors"
                                        >
                                            {table}
                                        </button>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </div>

                    {/* Columns Input */}
                    <div>
                        <label className="flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                            <Columns className="w-4 h-4 mr-2 text-purple-500" />
                            Columns (Optional)
                            <HelpTooltip
                                content="Specify columns to analyze, or leave empty to analyze all columns. Use comma-separated values."
                                className="ml-2"
                            />
                        </label>

                        <FocusRing>
                            <textarea
                                value={columnsInput}
                                onChange={(e) => setColumnsInput(e.target.value)}
                                placeholder="id, name, email, created_at, status..."
                                rows={3}
                                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 transition-all resize-none placeholder-slate-400 dark:placeholder-slate-500"
                            />
                        </FocusRing>

                        <div className="flex items-center justify-between mt-2">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                Leave empty to analyze all columns automatically
                            </p>
                            {columnsInput && (
                                <span className="text-xs text-purple-600 dark:text-purple-400">
                                    {columnsInput.split(',').filter(c => c.trim()).length} columns specified
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Advanced Options Toggle */}
                    <div className="border-t border-slate-200 dark:border-slate-700 pt-6">
                        <button
                            type="button"
                            onClick={() => setShowAdvanced(!showAdvanced)}
                            className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
                        >
                            <motion.div
                                animate={{ rotate: showAdvanced ? 90 : 0 }}
                                transition={{ duration: 0.2 }}
                            >
                                <ChevronDown className="w-4 h-4" />
                            </motion.div>
                            <span>Advanced Connection Options</span>
                        </button>

                        <AnimatePresence>
                            {showAdvanced && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="mt-4 space-y-4 overflow-hidden"
                                >
                                    {/* Connection String */}
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                            Connection String (Optional)
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.connectionString}
                                            onChange={(e) => handleInputChange('connectionString', e.target.value)}
                                            placeholder="postgresql://user:password@localhost:5432/dbname"
                                            className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                                        />
                                    </div>

                                    {/* Username and Password */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                                Username
                                            </label>
                                            <input
                                                type="text"
                                                value={formData.username}
                                                onChange={(e) => handleInputChange('username', e.target.value)}
                                                placeholder="database_user"
                                                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                                Password
                                            </label>
                                            <div className="relative">
                                                <input
                                                    type={showPassword ? 'text' : 'password'}
                                                    value={formData.password}
                                                    onChange={(e) => handleInputChange('password', e.target.value)}
                                                    placeholder="••••••••"
                                                    className="w-full px-4 py-3 pr-10 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => setShowPassword(!showPassword)}
                                                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                                                >
                                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Enhanced Submit Button */}
                    <motion.button
                        type="submit"
                        disabled={isLoading || validationErrors.length > 0 || !formData.database.trim() || !formData.table.trim()}
                        whileHover={{ scale: isLoading ? 1 : 1.02 }}
                        whileTap={{ scale: isLoading ? 1 : 0.98 }}
                        className="w-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 text-white font-semibold py-4 rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3 text-lg"
                    >
                        {isLoading ? (
                            <>
                                <Loader className="w-6 h-6 animate-spin" />
                                <span>Connecting & Analyzing...</span>
                            </>
                        ) : (
                            <>
                                <Play className="w-6 h-6" />
                                <span>Start Comprehensive Analysis</span>
                            </>
                        )}
                    </motion.button>

                    {/* Form hints */}
                    <div className="text-center pt-4 border-t border-slate-200 dark:border-slate-700">
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            🔒 All connections are secure and data is processed in real-time
                        </p>
                    </div>
                </form>
            </div>
        </motion.div>
    );
};
