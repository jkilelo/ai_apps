import { useState, useCallback } from 'react';
import { apiService } from '../../../services/api.js';

interface ProfileData {
    database: string;
    table: string;
    columns: string[];
}

interface StepResult {
    step: string;
    data: any;
    status: 'pending' | 'loading' | 'success' | 'error';
    error?: string;
}

export const useDataProfiling = () => {
    const [results, setResults] = useState<StepResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const executeFullFlow = useCallback(async (profileData: ProfileData) => {
        setIsLoading(true);
        setError(null);

        const steps = [
            { key: 'metadata', fn: () => apiService.getMetadata(profileData), title: 'Metadata Analysis' },
            { key: 'profiling_suggestions', fn: () => apiService.post('/api/profiling/suggestions', profileData), title: 'Profiling Suggestions' },
            { key: 'profiling_testcases', fn: () => apiService.post('/api/profiling/testcases', profileData), title: 'Profiling Test Cases' },
            { key: 'profiling_code', fn: () => apiService.post('/api/profiling/pyspark_code', profileData), title: 'PySpark Code Generation' },
            { key: 'profiling_execution', fn: () => apiService.post('/api/profiling/code_execution', profileData), title: 'Code Execution' },
            { key: 'dq_suggestions', fn: () => apiService.post('/api/dq/suggestions', profileData), title: 'Data Quality Suggestions' },
            { key: 'dq_testcases', fn: () => apiService.post('/api/dq/testcases', profileData), title: 'DQ Test Cases' },
            { key: 'dq_code', fn: () => apiService.post('/api/dq/pyspark_code', profileData), title: 'DQ Code Generation' },
            { key: 'dq_execution', fn: () => apiService.post('/api/dq/code_execution', profileData), title: 'DQ Execution' }
        ];

        // Initialize all steps as pending
        setResults(steps.map(step => ({
            step: step.key,
            data: null,
            status: 'pending' as const,
            title: step.title
        })));

        try {
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];

                // Mark current step as loading
                setResults(prev => prev.map((result, index) =>
                    index === i ? { ...result, status: 'loading' as const } : result
                ));

                try {
                    const result = await step.fn();

                    // Mark step as success
                    setResults(prev => prev.map((result, index) =>
                        index === i ? {
                            ...result,
                            status: 'success' as const,
                            data: result
                        } : result
                    ));

                    // Add delay between steps for better UX
                    if (i < steps.length - 1) {
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                } catch (stepError) {
                    // Mark step as error
                    setResults(prev => prev.map((result, index) =>
                        index === i ? {
                            ...result,
                            status: 'error' as const,
                            error: stepError instanceof Error ? stepError.message : 'Unknown error'
                        } : result
                    ));

                    console.error(`Error in step ${step.key}:`, stepError);
                    // Continue with next steps even if one fails
                }
            }
        } catch (error) {
            setError(error instanceof Error ? error.message : 'Unknown error occurred');
        } finally {
            setIsLoading(false);
        }
    }, []);

    return {
        results,
        isLoading,
        error,
        executeFullFlow
    };
};
