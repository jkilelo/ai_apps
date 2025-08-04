import { useState, useCallback, useEffect } from 'react';
import { webAutomationAPI } from '../services/webAutomationAPI';

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

export function useWebAutomation() {
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

    // Auto-load results when reaching step 4
    useEffect(() => {
        if (currentStep === 4 && !results && sessionId && stepStatus[3] === 'completed') {
            getResults();
        }
    }, [currentStep, results, sessionId, stepStatus]);

    // Step 1: Target Setup
    const executeTargetSetup = useCallback(async () => {
        setIsLoading(true);
        setStepStatus(prev => ({ ...prev, 1: 'processing' }));

        try {
            // Start target setup
            const response = await webAutomationAPI.setupTarget(formData);

            if (response.success) {
                setSessionId(response.session_id);

                // Poll for completion
                const finalStatus = await webAutomationAPI.pollUntilComplete(
                    () => webAutomationAPI.getTargetSetupStatus(),
                    30, // max attempts
                    2000 // 2 second intervals
                );

                if (finalStatus.status === 'completed') {
                    setStepStatus(prev => ({ ...prev, 1: 'completed' }));
                    setCurrentStep(2);
                } else {
                    throw new Error(finalStatus.message || 'Target setup failed');
                }
            } else {
                throw new Error(response.message || 'Failed to start target setup');
            }
        } catch (error) {
            console.error('Target setup failed:', error);
            setStepStatus(prev => ({ ...prev, 1: 'failed' }));
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, [formData]);

    // Step 2: Workflow Building
    const executeWorkflowBuild = useCallback(async () => {
        setIsLoading(true);
        setStepStatus(prev => ({ ...prev, 2: 'processing' }));

        try {
            // Start workflow building
            const response = await webAutomationAPI.buildWorkflow(workflow);

            if (response.success) {
                // Poll for completion
                const finalStatus = await webAutomationAPI.pollUntilComplete(
                    () => webAutomationAPI.getWorkflowBuildStatus(),
                    30, // max attempts
                    2000 // 2 second intervals
                );

                if (finalStatus.status === 'completed') {
                    setStepStatus(prev => ({ ...prev, 2: 'completed' }));
                    setCurrentStep(3);
                } else {
                    throw new Error(finalStatus.message || 'Workflow building failed');
                }
            } else {
                throw new Error(response.message || 'Failed to start workflow building');
            }
        } catch (error) {
            console.error('Workflow building failed:', error);
            setStepStatus(prev => ({ ...prev, 2: 'failed' }));
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, [workflow]);

    // Step 3: Test Execution
    const executeTests = useCallback(async () => {
        setIsLoading(true);
        setStepStatus(prev => ({ ...prev, 3: 'processing' }));

        try {
            // Start test execution
            const response = await webAutomationAPI.executeTests('sequential');

            if (response.success) {
                // Poll for completion
                const finalStatus = await webAutomationAPI.pollUntilComplete(
                    () => webAutomationAPI.getTestExecutionStatus(),
                    60, // max attempts (longer for test execution)
                    3000 // 3 second intervals
                );

                if (finalStatus.status === 'completed') {
                    setStepStatus(prev => ({ ...prev, 3: 'completed' }));
                    setCurrentStep(4);
                } else {
                    throw new Error(finalStatus.message || 'Test execution failed');
                }
            } else {
                throw new Error(response.message || 'Failed to start test execution');
            }
        } catch (error) {
            console.error('Test execution failed:', error);
            setStepStatus(prev => ({ ...prev, 3: 'failed' }));
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Step 4: Get Results
    const getResults = useCallback(async () => {
        setIsLoading(true);
        setStepStatus(prev => ({ ...prev, 4: 'processing' }));

        try {
            const response = await webAutomationAPI.getResults();

            if (response.success && response.data) {
                const transformedResults = webAutomationAPI.transformResultsToFrontend(response.data);
                setResults(transformedResults);
                setStepStatus(prev => ({ ...prev, 4: 'completed' }));
            } else {
                throw new Error(response.message || 'Failed to get results');
            }
        } catch (error) {
            console.error('Failed to get results:', error);
            setStepStatus(prev => ({ ...prev, 4: 'failed' }));
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Combined workflow execution (for backward compatibility)
    const executeWorkflow = useCallback(async () => {
        try {
            if (currentStep === 1) {
                await executeTargetSetup();
            } else if (currentStep === 2) {
                await executeWorkflowBuild();
            } else if (currentStep === 3) {
                await executeTests();
            } else if (currentStep === 4) {
                await getResults();
            }
        } catch (error) {
            console.error('Workflow step failed:', error);
            // Error handling is done in individual step functions
        }
    }, [currentStep, executeTargetSetup, executeWorkflowBuild, executeTests, getResults]);

    const resetFlow = useCallback(async () => {
        try {
            await webAutomationAPI.resetSession();
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
    }, []);

    return {
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
        executeWorkflow,
        executeTargetSetup,
        executeWorkflowBuild,
        executeTests,
        getResults,
        resetFlow
    };
}
