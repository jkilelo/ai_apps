/**
 * Web Automation API Service
 * Integrates with the new 4-step backend workflow
 */

import { AutomationFormData, WorkflowStep, AutomationResults } from '../hooks/useWebAutomation';

// Environment variable with fallback
declare const process: any;
const API_BASE_URL = (typeof process !== 'undefined' && process.env?.REACT_APP_WEB_AUTOMATION_API_URL) || 'http://localhost:8002/api/v1/web-automation';

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

class WebAutomationAPIService {
    private sessionId: string | null = null;
    private baseHeaders = {
        'Content-Type': 'application/json',
    };

    /**
     * Step 1: Target Setup
     */
    async setupTarget(formData: AutomationFormData): Promise<BackendStepResponse> {
        try {
            const request = {
                target_url: formData.targetUrl,
                test_name: formData.testName,
                description: formData.description,
                browser_type: formData.browserType,
                viewport: formData.viewport,
                user_profile: 'qa_tester'
            };

            const response = await fetch(`${API_BASE_URL}/workflow/step1/target-setup`, {
                method: 'POST',
                headers: this.baseHeaders,
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result: BackendStepResponse = await response.json();

            if (result.success) {
                this.sessionId = result.session_id;
            }

            return result;
        } catch (error) {
            console.error('Target setup failed:', error);
            throw error;
        }
    }

    /**
     * Monitor Step 1 progress
     */
    async getTargetSetupStatus(): Promise<BackendStepResponse> {
        if (!this.sessionId) {
            throw new Error('No active session. Please run target setup first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/workflow/${this.sessionId}/step1/status`, {
                method: 'GET',
                headers: this.baseHeaders
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get target setup status:', error);
            throw error;
        }
    }

    /**
     * Step 2: Workflow Builder
     */
    async buildWorkflow(workflowSteps: WorkflowStep[]): Promise<BackendStepResponse> {
        if (!this.sessionId) {
            throw new Error('No active session. Please run target setup first.');
        }

        try {
            const request = {
                session_id: this.sessionId,
                workflow_steps: workflowSteps.map(step => ({
                    type: step.type,
                    selector: step.selector,
                    value: step.value,
                    description: step.description,
                    timeout: step.timeout
                })),
                test_types: ['functional', 'accessibility'],
                include_accessibility: true
            };

            const response = await fetch(`${API_BASE_URL}/workflow/${this.sessionId}/step2/build-workflow`, {
                method: 'POST',
                headers: this.baseHeaders,
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Workflow building failed:', error);
            throw error;
        }
    }

    /**
     * Monitor Step 2 progress
     */
    async getWorkflowBuildStatus(): Promise<BackendStepResponse> {
        if (!this.sessionId) {
            throw new Error('No active session. Please run target setup first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/workflow/${this.sessionId}/step2/status`, {
                method: 'GET',
                headers: this.baseHeaders
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get workflow build status:', error);
            throw error;
        }
    }

    /**
     * Step 3: Test Execution
     */
    async executeTests(executionMode: 'sequential' | 'parallel' = 'sequential'): Promise<BackendStepResponse> {
        if (!this.sessionId) {
            throw new Error('No active session. Please run target setup first.');
        }

        try {
            const request = {
                session_id: this.sessionId,
                execution_mode: executionMode,
                capture_screenshots: true,
                max_retries: 3
            };

            const response = await fetch(`${API_BASE_URL}/workflow/${this.sessionId}/step3/execute-tests`, {
                method: 'POST',
                headers: this.baseHeaders,
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Test execution failed:', error);
            throw error;
        }
    }

    /**
     * Monitor Step 3 progress
     */
    async getTestExecutionStatus(): Promise<BackendStepResponse> {
        if (!this.sessionId) {
            throw new Error('No active session. Please run target setup first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/workflow/${this.sessionId}/step3/status`, {
                method: 'GET',
                headers: this.baseHeaders
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get test execution status:', error);
            throw error;
        }
    }

    /**
     * Step 4: Results & Report
     */
    async getResults(): Promise<BackendStepResponse> {
        if (!this.sessionId) {
            throw new Error('No active session. Please run target setup first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/workflow/${this.sessionId}/step4/results?format=json`, {
                method: 'GET',
                headers: this.baseHeaders
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get results:', error);
            throw error;
        }
    }

    /**
     * Get overall workflow status
     */
    async getWorkflowStatus(): Promise<WorkflowSession> {
        if (!this.sessionId) {
            throw new Error('No active session. Please run target setup first.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/workflow/${this.sessionId}/status`, {
                method: 'GET',
                headers: this.baseHeaders
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get workflow status:', error);
            throw error;
        }
    }

    /**
     * Convert backend results to frontend format
     */
    transformResultsToFrontend(backendData: any): AutomationResults {
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
    }

    /**
     * Reset session
     */
    async resetSession(): Promise<void> {
        if (this.sessionId) {
            try {
                await fetch(`${API_BASE_URL}/workflow/${this.sessionId}`, {
                    method: 'DELETE',
                    headers: this.baseHeaders
                });
            } catch (error) {
                console.warn('Failed to cleanup session:', error);
            }
        }
        this.sessionId = null;
    }

    /**
     * Get current session ID
     */
    getCurrentSessionId(): string | null {
        return this.sessionId;
    }

    /**
     * Set session ID (for resuming workflows)
     */
    setSessionId(sessionId: string): void {
        this.sessionId = sessionId;
    }

    /**
     * Utility: Poll status until completion
     */
    async pollUntilComplete(
        statusFn: () => Promise<BackendStepResponse>,
        maxAttempts: number = 30,
        intervalMs: number = 2000
    ): Promise<BackendStepResponse> {
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            const status = await statusFn();

            if (status.status === 'completed' || status.status === 'failed') {
                return status;
            }

            // Wait before next poll
            await new Promise(resolve => setTimeout(resolve, intervalMs));
        }

        throw new Error('Polling timeout: Operation did not complete in time');
    }
}

// Export singleton instance
export const webAutomationAPI = new WebAutomationAPIService();

export default webAutomationAPI;
