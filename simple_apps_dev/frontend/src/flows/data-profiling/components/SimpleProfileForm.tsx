import React, { useState } from 'react';
import { Database, Table, Columns, Play } from 'lucide-react';

interface ProfileFormData {
    database: string;
    table: string;
    columns: string;
}

interface SimpleProfileFormProps {
    onSubmit: (data: any) => void;
}

export const SimpleProfileForm: React.FC<SimpleProfileFormProps> = ({ onSubmit }) => {
    const [formData, setFormData] = useState<ProfileFormData>({
        database: '',
        table: '',
        columns: ''
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (formData.database && formData.table) {
            const columnsArray = formData.columns
                .split(',')
                .map(col => col.trim())
                .filter(col => col);
            
            onSubmit({
                ...formData,
                columns: columnsArray.length > 0 ? columnsArray : ['*']
            });
        }
    };

    const handleInputChange = (field: keyof ProfileFormData, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-3">
            {/* Database Name */}
            <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-slate-700 mb-1">
                    <Database className="h-3.5 w-3.5" />
                    <span>Database Name</span>
                </label>
                <input
                    type="text"
                    value={formData.database}
                    onChange={(e) => handleInputChange('database', e.target.value)}
                    placeholder="e.g., sales_db"
                    className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    required
                />
            </div>

            {/* Table Name */}
            <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-slate-700 mb-1">
                    <Table className="h-3.5 w-3.5" />
                    <span>Table Name</span>
                </label>
                <input
                    type="text"
                    value={formData.table}
                    onChange={(e) => handleInputChange('table', e.target.value)}
                    placeholder="e.g., transactions"
                    className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    required
                />
            </div>

            {/* Columns (Optional) */}
            <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-slate-700 mb-1">
                    <Columns className="h-3.5 w-3.5" />
                    <span>Columns (Optional)</span>
                </label>
                <input
                    type="text"
                    value={formData.columns}
                    onChange={(e) => handleInputChange('columns', e.target.value)}
                    placeholder="e.g., id, name, amount (or leave empty for all)"
                    className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <p className="text-xs text-slate-500 mt-1">Comma-separated column names</p>
            </div>

            {/* Submit Button */}
            <button
                type="submit"
                disabled={!formData.database || !formData.table}
                className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors text-sm font-medium"
            >
                <Play className="h-4 w-4" />
                <span>Start Analysis</span>
            </button>
        </form>
    );
};