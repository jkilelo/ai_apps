import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Database, Table, Columns, Play, Loader } from 'lucide-react';

interface ProfileFormData {
    database: string;
    table: string;
    columns: string[];
}

interface ProfileFormProps {
    onSubmit: (data: ProfileFormData) => void;
    isLoading: boolean;
}

export const ProfileForm: React.FC<ProfileFormProps> = ({ onSubmit, isLoading }) => {
    const [formData, setFormData] = useState<ProfileFormData>({
        database: '',
        table: '',
        columns: []
    });
    const [columnsInput, setColumnsInput] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.database.trim() || !formData.table.trim()) return;

        const columns = columnsInput.split(',').map(col => col.trim()).filter(Boolean);
        onSubmit({
            ...formData,
            columns
        });
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto"
        >
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Database className="w-8 h-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                        Configure Data Source
                    </h2>
                    <p className="text-slate-600 dark:text-slate-400">
                        Enter your database details to begin comprehensive analysis
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Database Input */}
                    <div>
                        <label className="flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            <Database className="w-4 h-4 mr-2" />
                            Database Name
                        </label>
                        <input
                            type="text"
                            value={formData.database}
                            onChange={(e) => setFormData(prev => ({ ...prev, database: e.target.value }))}
                            placeholder="e.g., production_db, analytics_db"
                            className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            required
                        />
                    </div>

                    {/* Table Input */}
                    <div>
                        <label className="flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            <Table className="w-4 h-4 mr-2" />
                            Table Name
                        </label>
                        <input
                            type="text"
                            value={formData.table}
                            onChange={(e) => setFormData(prev => ({ ...prev, table: e.target.value }))}
                            placeholder="e.g., users, transactions, orders"
                            className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            required
                        />
                    </div>

                    {/* Columns Input */}
                    <div>
                        <label className="flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            <Columns className="w-4 h-4 mr-2" />
                            Columns (Optional)
                        </label>
                        <input
                            type="text"
                            value={columnsInput}
                            onChange={(e) => setColumnsInput(e.target.value)}
                            placeholder="e.g., id, name, email, created_at (comma-separated)"
                            className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        />
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            Leave empty to analyze all columns
                        </p>
                    </div>

                    {/* Submit Button */}
                    <motion.button
                        type="submit"
                        disabled={isLoading || !formData.database.trim() || !formData.table.trim()}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium py-4 rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                    >
                        {isLoading ? (
                            <>
                                <Loader className="w-5 h-5 animate-spin" />
                                <span>Starting Analysis...</span>
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5" />
                                <span>Start Full Analysis</span>
                            </>
                        )}
                    </motion.button>
                </form>
            </div>
        </motion.div>
    );
};
