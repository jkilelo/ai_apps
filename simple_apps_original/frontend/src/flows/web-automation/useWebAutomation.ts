/**
 * Consolidated Web Automation Hook with Integrated API Service
 * Combines state management and API calls in a single hook for better maintainability
 * Clear separation of API endpoints for each step
 */

import { useState, useCallback, useEffect, useMemo } from 'react';

// ============================================================================
// Type Definitions
// ============================================================================
export interface AutomationFormData {
    targetUrl: string;
    testName: string;
    description: string;
    browserType: 'chrome' | 'firefox' | 'safari';
    viewport: {
        width: number;
        height: number;
    };
}

export interface WorkflowStep {
    id: string;
    type: 'click' | 'type' | 'wait' | 'assert' | 'navigate' | 'screenshot';
    selector?: string;
    value?: string;
    description: string;
    timeout?: number;
}

export interface AutomationResults {
    status: 'success' | 'failed' | 'warning';
    executionTime: number;
    steps: Array<{
        step: WorkflowStep;
        status: 'passed' | 'failed' | 'skipped';
        duration: number;
        error?: string;
        screenshot?: string;
    }>;
    screenshots: string[];
    logs: string[];
    metrics: {
        totalSteps: number;
        passedSteps: number;
        failedSteps: number;
        coverage: number;
    };
}

export interface BackendStepResponse {
    success: boolean;
    session_id: string;
    step: number;
    job_id?: string;
    status: string;
    message: string;
    data?: any;
}

export interface WorkflowSession {
    session_id: string;
    status: string;
    created_at: string;
    current_step: number;
    steps_completed: string[];
    target_data?: any;
    elements_data?: any;
    workflow_data?: any;
    execution_data?: any;
    results_data?: any;
}

// Senior Integration Engineer Pattern: Centralized API Configuration
declare const process: any;
const API_BASE_URL = (typeof process !== 'undefined' && process.env?.REACT_APP_WEB_AUTOMATION_API_URL) || 'http://localhost:5175/api/ui';
const API_TIMEOUT = 60000; // 60 seconds - backend can take 20+ seconds with LLM
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // Start with 1 second

// ============================================================================
// Main Hook
// ============================================================================
export function useWebAutomation() {
    // State Management
    const [currentStep, setCurrentStep] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [stepStatus, setStepStatus] = useState<{ [key: number]: string }>({});
    const [sessionId, setSessionId] = useState<string | null>(null);

    const [formData, setFormData] = useState<AutomationFormData>({
        targetUrl: '',
        testName: '',
        description: '',
        browserType: 'chrome',
        viewport: {
            width: 1920,
            height: 1080
        }
    });

    const [workflow, setWorkflow] = useState<WorkflowStep[]>([]);
    const [results, setResults] = useState<AutomationResults | null>(null);

    // ============================================================================
    // API Service Methods (Integrated)
    // ============================================================================
    const baseHeaders = useMemo(() => ({
        'Content-Type': 'application/json',
    }), []);

    /**
     * Senior Integration Engineer Pattern: Retry logic with exponential backoff
     */
    const retryWithBackoff = useCallback(async <T>(
        fn: () => Promise<T>,
        retries: number = MAX_RETRIES,
        delay: number = RETRY_DELAY
    ): Promise<T> => {
        console.log(`🔁 retryWithBackoff called with ${retries} retries`);
        try {
            const result = await fn();
            console.log('🎯 Function succeeded on first try');
            return result;
        } catch (error) {
            console.log('⚠️ Function failed:', error);
            if (retries <= 0) {
                console.error('💔 No retries left, throwing error');
                throw error;
            }
            
            console.warn(`⏰ Retrying after ${delay}ms... (${retries} attempts left)`);
            await new Promise(resolve => setTimeout(resolve, delay));
            
            return retryWithBackoff(fn, retries - 1, delay * 2); // Exponential backoff
        }
    }, []);

    /**
     * Senior Integration Engineer Pattern: API call wrapper with timeout
     */
    const apiCall = useCallback(async (
        endpoint: string,
        options: RequestInit
    ): Promise<any> => {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), API_TIMEOUT);
        
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            clearTimeout(timeout);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const jsonData = await response.json();
            console.log(`📡 API Response from ${endpoint}:`, jsonData);
            return jsonData;
        } catch (error: any) {
            clearTimeout(timeout);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }, []);

    /**
     * Transform backend results to frontend format
     */
    const transformResultsToFrontend = useCallback((backendData: any): AutomationResults => {
        const testExecution = backendData.test_execution || {};
        const testResults = testExecution.test_results || [];

        return {
            status: testExecution.passed_tests === testExecution.total_tests ? 'success' :
                testExecution.failed_tests === 0 ? 'warning' : 'failed',
            executionTime: testExecution.execution_time || 0,
            steps: testResults.map((result: any, index: number) => ({
                step: {
                    id: `step-${index}`,
                    type: result.test_type || 'assert',
                    description: result.test_name || 'Test step',
                    selector: result.selector,
                    value: result.expected_value
                },
                status: result.status === 'passed' ? 'passed' : 'failed',
                duration: result.duration || 0,
                error: result.error_message,
                screenshot: result.screenshot_path
            })),
            screenshots: testExecution.screenshots || [],
            logs: testExecution.logs || [],
            metrics: {
                totalSteps: testExecution.total_tests || 0,
                passedSteps: testExecution.passed_tests || 0,
                failedSteps: testExecution.failed_tests || 0,
                coverage: backendData.metrics?.coverage_score || 0
            }
        };
    }, []);

    // ============================================================================
    // Step 1: Element Extraction API Calls - NEW ENDPOINT
    // ============================================================================
    const setupTargetAPI = useCallback(async (data: AutomationFormData): Promise<any> => {
        const request = {
            url: data.targetUrl,
            headless: true
        };

        console.log('📤 Sending request:', request);
        console.log('🔗 API URL:', `${API_BASE_URL}/element_extraction`);
        
        try {
            const result = await retryWithBackoff(() => {
                console.log('🔄 Making API call...');
                return apiCall('/element_extraction', {
                    method: 'POST',
                    body: JSON.stringify(request)
                });
            });
            console.log('✅ API call successful:', result);
            return result;
        } catch (error) {
            console.error('❌ API call error in setupTargetAPI:', error);
            throw error;
        }
    }, [apiCall, retryWithBackoff]);

    const getTargetSetupStatus = useCallback(async (): Promise<BackendStepResponse> => {
        if (!sessionId) {
            throw new Error('No active session. Please run target setup first.');
        }

        const response = await fetch(`${API_BASE_URL}/workflow/${sessionId}/step1/status`, {
            method: 'GET',
            headers: baseHeaders
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }, [sessionId, baseHeaders]);

    // Step 1 Execution (Called by ElementExtraction component)
    const executeTargetSetup = useCallback(async () => {
        setIsLoading(true);
        setStepStatus(prev => ({ ...prev, 1: 'processing' }));

        try {
            console.log('🚀 Starting element extraction for:', formData.targetUrl);
            const response = await setupTargetAPI(formData).catch(err => {
                console.error('❌ API call failed:', err);
                throw err;
            });
            console.log('📦 Backend response:', response);

            if (response.success && response.data) {
                // Store extraction data for next step
                setSessionId(response.data.url); // Use URL as session identifier
                
                // Store the extraction result for chaining
                (window as any).__extractionData = response.data;
                console.log('✅ Extraction data stored:', response.data);
                
                // Log extracted elements count
                const elementsCount = response.data.elements?.length || 0;
                console.log(`📊 Extracted ${elementsCount} elements`);
                
                setStepStatus(prev => ({ ...prev, 1: 'completed' }));
                
                // Automatically move to step 2
                console.log('➡️ Moving to Step 2: Test Generation');
                setCurrentStep(2);
                
                // Trigger test generation automatically after a short delay
                setTimeout(() => {
                    console.log('🔄 Auto-triggering test generation...');
                }, 1000);
            } else {
                throw new Error(response.error || 'Failed to extract elements');
            }
        } catch (error) {
            console.error('❌ Element extraction failed:', error);
            setStepStatus(prev => ({ ...prev, 1: 'failed' }));
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, [formData, setupTargetAPI]);

    // ============================================================================
    // Step 2: Test Generation API Calls - NEW ENDPOINT
    // ============================================================================
    const buildWorkflowAPI = useCallback(async (): Promise<any> => {
        const extractionData = (window as any).__extractionData;
        
        if (!extractionData) {
            throw new Error('No extraction data available. Please run element extraction first.');
        }

        const request = {
            extraction_data: extractionData,
            test_categories: ['functional', 'validation', 'navigation', 'interaction']
        };

        return await retryWithBackoff(() =>
            apiCall('/test_generation', {
                method: 'POST',
                body: JSON.stringify(request)
            })
        );
    }, [apiCall, retryWithBackoff]);

    const getWorkflowBuildStatus = useCallback(async (): Promise<BackendStepResponse> => {
        if (!sessionId) {
            throw new Error('No active session.');
        }

        const response = await fetch(`${API_BASE_URL}/workflow/${sessionId}/step2/status`, {
            method: 'GET',
            headers: baseHeaders
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }, [sessionId, baseHeaders]);

    // Step 2 Execution (Called by TestGeneration component)
    const executeWorkflowBuild = useCallback(async () => {
        setIsLoading(true);
        setStepStatus(prev => ({ ...prev, 2: 'processing' }));

        try {
            const response = await buildWorkflowAPI();

            if (response.success && response.data) {
                // Store test data for next step
                (window as any).__testData = response.data;
                
                // Update workflow from generated tests
                // Check for both test_scenarios and gherkin_features (v2 backend structure)
                const scenarios = response.data.test_scenarios || response.data.gherkin_features || {};
                const workflowSteps: WorkflowStep[] = [];
                
                // Handle v2 backend structure where features contain scenarios
                let stepIndex = 0;
                Object.entries(scenarios).forEach(([category, feature]: [string, any]) => {
                    if (feature.scenarios && Array.isArray(feature.scenarios)) {
                        feature.scenarios.forEach((scenario: any) => {
                            // Add the scenario as a workflow step
                            workflowSteps.push({
                                id: `step-${stepIndex++}`,
                                type: 'assert',
                                description: scenario.name || scenario.title || `${category}: Test step ${stepIndex}`,
                                timeout: 5000
                            });
                            
                            // If scenario has steps, add them too (for better granularity)
                            if (scenario.steps && Array.isArray(scenario.steps)) {
                                scenario.steps.forEach((step: any) => {
                                    workflowSteps.push({
                                        id: `step-${stepIndex++}`,
                                        type: 'assert',
                                        description: `  → ${step.keyword} ${step.text}`,
                                        timeout: 5000
                                    });
                                });
                            }
                        });
                    }
                });
                
                // Log for debugging
                console.log('Generated workflow steps:', workflowSteps);
                console.log('Test data structure:', response.data);
                
                setWorkflow(workflowSteps);
                setStepStatus(prev => ({ ...prev, 2: 'completed' }));
                setCurrentStep(3);
            } else {
                throw new Error(response.error || 'Failed to generate tests');
            }
        } catch (error) {
            console.error('Test generation failed:', error);
            setStepStatus(prev => ({ ...prev, 2: 'failed' }));
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, [buildWorkflowAPI]);

    // ============================================================================
    // Step 3: Code Generation API Calls - NEW ENDPOINT
    // ============================================================================
    const generateCodeAPI = useCallback(async (): Promise<any> => {
        const testData = (window as any).__testData;
        
        if (!testData) {
            throw new Error('No test data available. Please run test generation first.');
        }

        const request = {
            test_data: testData,
            language: 'python',
            framework: 'playwright'
        };

        return await retryWithBackoff(() =>
            apiCall('/code_generation', {
                method: 'POST',
                body: JSON.stringify(request)
            })
        );
    }, [apiCall, retryWithBackoff]);

    // Step 3 Execution (Called by CodeGeneration component)
    const getResults = useCallback(async () => {
        setIsLoading(true);
        setStepStatus(prev => ({ ...prev, 3: 'processing' }));

        try {
            const response = await generateCodeAPI();

            if (response.success && response.data) {
                // Store code data for next step
                (window as any).__codeData = response.data;
                
                setStepStatus(prev => ({ ...prev, 3: 'completed' }));
                setCurrentStep(4); // Move to code execution step
            } else {
                throw new Error(response.error || 'Failed to generate code');
            }
        } catch (error) {
            console.error('Failed to generate code:', error);
            setStepStatus(prev => ({ ...prev, 3: 'failed' }));
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, [generateCodeAPI]);

    // ============================================================================
    // Step 4: Code Execution API Calls - NEW ENDPOINT
    // ============================================================================
    const executeCodeAPI = useCallback(async (): Promise<any> => {
        const codeData = (window as any).__codeData;
        
        if (!codeData) {
            throw new Error('No code data available. Please run code generation first.');
        }

        const request = {
            code_data: codeData,
            run_tests: true,
            capture_screenshots: true,
            timeout: 60000
        };

        return await retryWithBackoff(() =>
            apiCall('/code_execution', {
                method: 'POST',
                body: JSON.stringify(request)
            })
        );
    }, [apiCall, retryWithBackoff]);

    // Step 4 Execution (Called by CodeExecution component)
    const executeTests = useCallback(async () => {
        setIsLoading(true);
        setStepStatus(prev => ({ ...prev, 4: 'processing' }));

        try {
            const response = await executeCodeAPI();

            if (response.success && response.data) {
                // Store execution results
                const executionResults = response.data;
                
                // Transform backend results to frontend format
                const formattedResults = transformResultsToFrontend(executionResults);
                setResults(formattedResults);
                
                setStepStatus(prev => ({ ...prev, 4: 'completed' }));
                
                // Code execution is the final step
                console.log('Pipeline completed successfully!');
            } else {
                throw new Error(response.error || 'Failed to execute code');
            }
        } catch (error) {
            console.error('Code execution failed:', error);
            setStepStatus(prev => ({ ...prev, 4: 'failed' }));
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, [executeCodeAPI, transformResultsToFrontend]);

    // ============================================================================
    // Utility Methods
    // ============================================================================
    const resetSession = useCallback(async (): Promise<void> => {
        if (sessionId) {
            try {
                await fetch(`${API_BASE_URL}/workflow/${sessionId}`, {
                    method: 'DELETE',
                    headers: baseHeaders
                });
            } catch (error) {
                console.warn('Failed to cleanup session:', error);
            }
        }
        setSessionId(null);
    }, [sessionId, baseHeaders]);

    const resetFlow = useCallback(async () => {
        try {
            await resetSession();
        } catch (error) {
            console.warn('Failed to cleanup session:', error);
        }

        setCurrentStep(1);
        setFormData({
            targetUrl: '',
            testName: '',
            description: '',
            browserType: 'chrome',
            viewport: {
                width: 1920,
                height: 1080
            }
        });
        setWorkflow([]);
        setResults(null);
        setIsLoading(false);
        setStepStatus({});
        setSessionId(null);
    }, [resetSession]);

    // No auto-load needed - results are fetched after code execution in step 4

    // ============================================================================
    // Return Hook Interface
    // ============================================================================
    return {
        // State
        currentStep,
        setCurrentStep,
        formData,
        setFormData,
        workflow,
        setWorkflow,
        results,
        isLoading,
        stepStatus,
        sessionId,
        
        // Step Execution Methods (mapped to new naming)
        executeTargetSetup,     // Step 1: Element Extraction
        executeWorkflowBuild,   // Step 2: Test Generation  
        getResults,             // Step 3: Code Generation
        executeTests,           // Step 4: Code Execution
        
        // Utility
        resetFlow
    };
}