import { useState, useEffect, useCallback } from 'react'
import { AppStep } from '../types/app'
import { WorkflowState, WorkflowStep, StepStatus, StepFormData, StepExecutionResult } from '../types/workflow'
import { apiClient } from '../services/api'

export const useWorkflowWithAPI = (appId: number, subAppId: number | undefined, steps: AppStep[]) => {
  const [workflowState, setWorkflowState] = useState<WorkflowState>({
    appId,
    subAppId,
    steps: {},
    currentStepId: null,
    overallProgress: 0
  })

  const [activeJobs, setActiveJobs] = useState<Record<number, string>>({})

  // Initialize workflow steps
  useEffect(() => {
    const initialSteps: Record<number, WorkflowStep> = {}
    
    steps.forEach((step) => {
      const status = step.depends_on.length === 0 ? 'pending' : 'locked'
      initialSteps[step.id] = {
        id: step.id,
        status,
        formData: {}
      }
    })
    
    setWorkflowState({
      appId,
      subAppId,
      steps: initialSteps,
      currentStepId: steps.length > 0 ? steps[0].id : null,
      overallProgress: 0
    })
  }, [appId, subAppId, JSON.stringify(steps.map(s => s.id))])

  // Check and update step dependencies
  const updateStepDependencies = useCallback(() => {
    setWorkflowState(prev => {
      const updatedSteps = { ...prev.steps }
      
      steps.forEach(step => {
        const currentStatus = updatedSteps[step.id]?.status
        
        // Don't update if already completed or in progress
        if (currentStatus === 'completed' || currentStatus === 'in_progress') {
          return
        }
        
        // Check if all dependencies are completed
        const allDependenciesCompleted = step.depends_on.every(
          depId => updatedSteps[depId]?.status === 'completed'
        )
        
        if (allDependenciesCompleted && currentStatus === 'locked') {
          updatedSteps[step.id] = {
            ...updatedSteps[step.id],
            status: 'pending'
          }
        }
      })
      
      // Calculate overall progress
      const completedCount = Object.values(updatedSteps).filter(s => s.status === 'completed').length
      const overallProgress = (completedCount / steps.length) * 100
      
      return {
        ...prev,
        steps: updatedSteps,
        overallProgress
      }
    })
  }, [steps])

  // Get available inputs from previous step outputs
  const getAvailableInputs = useCallback((stepId: number): Record<string, any> => {
    const step = steps.find(s => s.id === stepId)
    if (!step) return {}
    
    const availableInputs: Record<string, any> = {}
    
    // Collect outputs from all dependency steps
    step.depends_on.forEach(depId => {
      const depStep = workflowState.steps[depId]
      if (depStep?.status === 'completed' && depStep.result?.data) {
        // Map output data to available inputs
        Object.entries(depStep.result.data).forEach(([key, value]) => {
          availableInputs[key] = value
        })
      }
    })
    
    return availableInputs
  }, [steps, workflowState.steps])

  // Execute step for UI Web Testing app
  const executeUIWebTestingStep = useCallback(async (step: AppStep, formData: StepFormData) => {
    let jobId: string | null = null
    
    try {
      switch (step.name) {
        case 'element_extraction_using_python_playwright': {
          console.log('Element Extraction - Form data:', formData)
          
          const requestData = {
            web_page_url: formData.web_page_url as string,
            profile: formData.profile as string || 'qa_manual_tester',
            include_screenshots: formData.include_screenshots as boolean || false,
            max_depth: formData.max_depth as number || 1
          }
          
          console.log('Element Extraction - Request data:', requestData)
          
          // Start element extraction
          const response = await apiClient.startElementExtraction(requestData)
          
          jobId = response.job_id
          setActiveJobs(prev => ({ ...prev, [step.id]: jobId! }))
          
          // Poll for results
          const result = await apiClient.pollJobStatus(
            jobId,
            (id) => apiClient.getElementExtractionStatus(id),
            (status) => {
              console.log(`Element extraction ${status.status}...`)
            }
          )
          
          return {
            status: 'success' as const,
            data: {
              extracted_elements: result.extracted_elements,
              metadata: result.metadata
            },
            timestamp: new Date().toISOString()
          }
        }
        
        case 'generate_test_cases_using_llm': {
          // Get extracted elements from previous step
          const prevStepData = getAvailableInputs(step.id)
          console.log('Test Generation - Previous step data:', prevStepData)
          const extractedElements = prevStepData.extracted_elements || formData.extracted_elements
          
          console.log('Test Generation - Extracted elements:', extractedElements)
          
          if (!extractedElements) {
            throw new Error('No extracted elements found from previous step')
          }
          
          const requestData = {
            extracted_elements: extractedElements,
            test_type: formData.test_type as string || 'functional',
            framework: formData.framework as string || 'playwright_pytest',
            include_negative_tests: formData.include_negative_tests as boolean !== false
          }
          
          console.log('Test Generation - Request data:', requestData)
          
          // Start test generation
          const response = await apiClient.startTestGeneration(requestData)
          
          jobId = response.job_id
          setActiveJobs(prev => ({ ...prev, [step.id]: jobId! }))
          
          // Poll for results
          const result = await apiClient.pollJobStatus(
            jobId,
            (id) => apiClient.getTestGenerationStatus(id),
            (status) => {
              console.log(`Test generation ${status.status}...`)
            }
          )
          
          return {
            status: 'success' as const,
            data: {
              test_cases: result.test_cases,
              test_files: result.test_files,
              metadata: result.metadata
            },
            timestamp: new Date().toISOString()
          }
        }
        
        case 'execute_test_cases': {
          // Get test cases from previous step
          const prevStepData = getAvailableInputs(step.id)
          console.log('Previous step data:', prevStepData)
          const testCases = prevStepData.test_cases || formData.test_cases
          const testFiles = prevStepData.test_files || formData.test_files
          
          console.log('Test cases to execute:', testCases)
          
          if (!testCases) {
            throw new Error('No test cases found from previous step')
          }
          
          // Start test execution
          const response = await apiClient.startTestExecution({
            test_cases: testCases,
            test_files: testFiles,
            execution_mode: formData.execution_mode as string || 'sequential',
            timeout: formData.timeout as number || 300,
            browser: formData.browser as string || 'chromium'
          })
          
          jobId = response.job_id
          setActiveJobs(prev => ({ ...prev, [step.id]: jobId! }))
          
          // Poll for results
          const result = await apiClient.pollJobStatus(
            jobId,
            (id) => apiClient.getTestExecutionStatus(id),
            (status) => {
              console.log(`Test execution ${status.status}...`)
            }
          )
          
          return {
            status: 'success' as const,
            data: {
              test_results: result.test_results,
              summary: result.summary,
              metadata: result.metadata
            },
            timestamp: new Date().toISOString()
          }
        }
        
        default:
          throw new Error(`Unknown step: ${step.name}`)
      }
    } catch (error) {
      console.error(`Step execution failed:`, error)
      
      // Clean up job tracking
      if (jobId) {
        setActiveJobs(prev => {
          const newJobs = { ...prev }
          delete newJobs[step.id]
          return newJobs
        })
      }
      
      console.error('Full error details:', error)
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        timestamp: new Date().toISOString()
      }
    }
  }, [getAvailableInputs])

  // Execute step (with API integration for UI Web Testing)
  const executeStep = useCallback(async (stepId: number, formData: StepFormData) => {
    const step = steps.find(s => s.id === stepId)
    if (!step) {
      throw new Error(`Step ${stepId} not found`)
    }

    // Update step to in_progress
    setWorkflowState(prev => ({
      ...prev,
      steps: {
        ...prev.steps,
        [stepId]: {
          ...prev.steps[stepId],
          status: 'in_progress' as StepStatus,
          formData,
          startedAt: new Date().toISOString()
        }
      }
    }))

    let result: StepExecutionResult

    // Check if this is UI Web Testing app
    if (appId === 2 && !subAppId) {
      // Use API integration for UI Web Testing
      result = await executeUIWebTestingStep(step, formData)
    } else {
      // Use mock execution for other apps
      await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 2000))
      
      const isSuccess = Math.random() > 0.1
      result = isSuccess ? {
        status: 'success',
        data: generateMockResult(stepId, formData),
        timestamp: new Date().toISOString()
      } : {
        status: 'error',
        error: 'Simulated execution error: Connection timeout',
        timestamp: new Date().toISOString()
      }
    }

    // Update step with result
    setWorkflowState(prev => ({
      ...prev,
      steps: {
        ...prev.steps,
        [stepId]: {
          ...prev.steps[stepId],
          status: result.status === 'success' ? 'completed' : 'failed' as StepStatus,
          result,
          completedAt: new Date().toISOString()
        }
      }
    }))

    // Update dependencies after completion
    if (result.status === 'success') {
      setTimeout(updateStepDependencies, 100)
    }

    return result
  }, [appId, subAppId, steps, executeUIWebTestingStep, updateStepDependencies])

  // Set current step
  const setCurrentStep = useCallback((stepId: number | null) => {
    setWorkflowState(prev => ({
      ...prev,
      currentStepId: stepId
    }))
  }, [])

  // Reset workflow
  const resetWorkflow = useCallback(() => {
    const initialSteps: Record<number, WorkflowStep> = {}
    
    steps.forEach((step) => {
      const status = step.depends_on.length === 0 ? 'pending' : 'locked'
      initialSteps[step.id] = {
        id: step.id,
        status,
        formData: {}
      }
    })
    
    setWorkflowState({
      appId,
      subAppId,
      steps: initialSteps,
      currentStepId: steps.length > 0 ? steps[0].id : null,
      overallProgress: 0
    })
    
    setActiveJobs({})
  }, [appId, subAppId, steps])

  return {
    workflowState,
    executeStep,
    setCurrentStep,
    resetWorkflow,
    getAvailableInputs,
    activeJobs
  }
}

// Generate mock results for other apps
const generateMockResult = (stepId: number, formData: StepFormData): any => {
  const mockResults: Record<string, any> = {
    metadata: {
      table: formData.table_name,
      database: formData.database_name,
      columns: formData.columns || [],
      row_count: Math.floor(Math.random() * 1000000),
      last_updated: new Date().toISOString()
    },
    suggestions: [
      {
        id: 1,
        type: 'null_check',
        description: 'Check for null values in required columns',
        severity: 'high',
        columns: ['customer_id', 'transaction_date']
      }
    ],
    test_cases: [
      {
        id: 1,
        name: 'test_null_values',
        description: 'Test for null values in critical columns',
        expected_result: 'No null values found'
      }
    ],
    pyspark_code: `# Auto-generated PySpark code`,
    execution_results: [
      {
        check: 'null_values',
        status: 'passed',
        details: 'No critical null values found'
      }
    ]
  }

  const resultKeys = Object.keys(mockResults)
  return mockResults[resultKeys[stepId % resultKeys.length]]
}