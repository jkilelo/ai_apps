import { useState, useRef } from 'react';
import { Database, Play, Download, RefreshCw, AlertCircle } from 'lucide-react';
import { apiService, WebSocketService } from '../services/api.js';
import { GetMetadataRequest, GetMetadataResponse } from '../types/api.js';
import FormInput from './FormInput.js';
import LoadingSpinner from './LoadingSpinner.js';

interface DataProfilerProps {
    wsService: WebSocketService;
    onFormStart: (formName: string) => void;
}

const DataProfiler = ({ onFormStart }: DataProfilerProps) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<GetMetadataResponse | null>(null);
    const [formData, setFormData] = useState<GetMetadataRequest>({
        database: '',
        table: '',
        columns: [],
    });
    const [columnsInput, setColumnsInput] = useState('');

    const columnsInputRef = useRef<HTMLInputElement>(null);

    const handleInputChange = (field: keyof GetMetadataRequest, value: string | string[]) => {
        setFormData(prev => ({
            ...prev,
            [field]: value,
        }));
        setError(null);
    };

    const handleColumnsInputChange = (value: string) => {
        setColumnsInput(value);
        setError(null);
    };

    const validateForm = (): boolean => {
        if (!formData.database.trim()) {
            setError('Database name is required');
            return false;
        }
        if (!formData.table.trim()) {
            setError('Table name is required');
            return false;
        }
        if (formData.database.length < 2) {
            setError('Database name must be at least 2 characters');
            return false;
        }
        if (formData.table.length < 2) {
            setError('Table name must be at least 2 characters');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            // Notify WebSocket about form start
            onFormStart('Data Profiling');

            // Convert columnsInput string to array for the API call
            const columns = columnsInput.split(',').map(col => col.trim()).filter(Boolean);
            const requestData = {
                ...formData,
                columns: columns.length > 0 ? columns : []
            };

            const response = await apiService.getMetadata(requestData);
            setResult(response);
        } catch (err) {
            console.error('Error getting metadata:', err);
            setError(err instanceof Error ? err.message : 'Failed to get metadata');
        } finally {
            setIsLoading(false);
        }
    };

    const handleReset = () => {
        setFormData({
            database: '',
            table: '',
            columns: [],
        });
        setColumnsInput('');
        setResult(null);
        setError(null);
        if (columnsInputRef.current) {
            columnsInputRef.current.value = '';
        }
    };

    const handleExport = () => {
        if (!result) return;

        const dataStr = JSON.stringify(result, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `metadata_${result.database}_${result.table}.json`;
        link.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="space-y-6">
            {/* Main Form Card */}
            <div className="card">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                            <Database className="h-6 w-6 mr-2 text-primary-600" />
                            Data Profiling
                        </h2>
                        <p className="text-gray-600 mt-1">
                            Analyze database tables and retrieve metadata information
                        </p>
                    </div>

                    {result && (
                        <button
                            onClick={handleExport}
                            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                            <Download className="h-4 w-4" />
                            <span>Export</span>
                        </button>
                    )}
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-6">
                        <FormInput
                            label="Database Name"
                            type="text"
                            value={formData.database}
                            onChange={(value: string) => handleInputChange('database', value)}
                            placeholder="e.g., test_db, production_db"
                            required
                            maxLength={50}
                        />

                        <FormInput
                            label="Table Name"
                            type="text"
                            value={formData.table}
                            onChange={(value: string) => handleInputChange('table', value)}
                            placeholder="e.g., users, orders"
                            required
                            maxLength={100}
                        />
                    </div>

                    <FormInput
                        ref={columnsInputRef}
                        label="Columns (Optional)"
                        type="text"
                        value={columnsInput}
                        onChange={handleColumnsInputChange}
                        placeholder="e.g., id, name, email (comma-separated)"
                        description="Leave empty to retrieve all columns"
                    />

                    {error && (
                        <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                            <span className="text-red-700">{error}</span>
                        </div>
                    )}

                    <div className="flex space-x-4">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="flex items-center space-x-2 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <LoadingSpinner size="sm" />
                            ) : (
                                <Play className="h-4 w-4" />
                            )}
                            <span>{isLoading ? 'Analyzing...' : 'Analyze'}</span>
                        </button>

                        <button
                            type="button"
                            onClick={handleReset}
                            className="flex items-center space-x-2 btn-secondary"
                        >
                            <RefreshCw className="h-4 w-4" />
                            <span>Reset</span>
                        </button>
                    </div>
                </form>
            </div>

            {/* Results Card */}
            {result && (
                <div className="card animate-fade-in">
                    <h3 className="text-xl font-semibold mb-4 text-gray-900">
                        Metadata Results
                    </h3>

                    <div className="space-y-4">
                        <div className="grid md:grid-cols-2 gap-4">
                            <div className="p-4 bg-blue-50 rounded-lg">
                                <h4 className="font-medium text-blue-900 mb-2">Database</h4>
                                <p className="text-blue-700 font-mono">{result.database}</p>
                            </div>

                            <div className="p-4 bg-green-50 rounded-lg">
                                <h4 className="font-medium text-green-900 mb-2">Table</h4>
                                <p className="text-green-700 font-mono">{result.table}</p>
                            </div>
                        </div>

                        <div className="p-4 bg-purple-50 rounded-lg">
                            <h4 className="font-medium text-purple-900 mb-2">Columns</h4>
                            {result.columns && result.columns.length > 0 ? (
                                <div className="flex flex-wrap gap-2">
                                    {result.columns.map((column, index) => (
                                        <span
                                            key={index}
                                            className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-mono"
                                        >
                                            {column}
                                        </span>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-purple-700 italic">All columns (none specified)</p>
                            )}
                        </div>

                        <div className="p-4 bg-gray-50 rounded-lg">
                            <h4 className="font-medium text-gray-900 mb-2">Raw Response</h4>
                            <pre className="text-sm text-gray-700 bg-white p-3 rounded border overflow-x-auto">
                                {JSON.stringify(result, null, 2)}
                            </pre>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DataProfiler;
