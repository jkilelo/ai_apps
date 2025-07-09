import { useState, useEffect, useCallback } from 'react'
import { AppStep } from '../types/app'
import { WorkflowState, WorkflowStep, StepStatus, StepFormData, StepExecutionResult } from '../types/workflow'

export const useWorkflow = (appId: number, subAppId: number | undefined, steps: AppStep[]) => {
  const [workflowState, setWorkflowState] = useState<WorkflowState>({
    appId,
    subAppId,
    steps: {},
    currentStepId: null,
    overallProgress: 0
  })

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

  // Execute step
  const executeStep = useCallback(async (stepId: number, formData: StepFormData) => {
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

    // Simulate API call with delay
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 2000))

    // Simulate success/failure (90% success rate)
    const isSuccess = Math.random() > 0.1
    
    const result: StepExecutionResult = isSuccess ? {
      status: 'success',
      data: generateMockResult(stepId, formData),
      timestamp: new Date().toISOString()
    } : {
      status: 'error',
      error: 'Simulated execution error: Connection timeout',
      timestamp: new Date().toISOString()
    }

    // Update step with result
    setWorkflowState(prev => ({
      ...prev,
      steps: {
        ...prev.steps,
        [stepId]: {
          ...prev.steps[stepId],
          status: isSuccess ? 'completed' : 'failed' as StepStatus,
          result,
          completedAt: new Date().toISOString()
        }
      }
    }))

    // Update dependencies after completion
    if (isSuccess) {
      setTimeout(updateStepDependencies, 100)
    }

    return result
  }, [updateStepDependencies])

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
  }, [appId, subAppId, steps])

  return {
    workflowState,
    executeStep,
    setCurrentStep,
    resetWorkflow,
    getAvailableInputs
  }
}

// Generate mock results based on step
const generateMockResult = (stepId: number, formData: StepFormData): any => {
  // Mock different results based on step type
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
      },
      {
        id: 2,
        type: 'range_check',
        description: 'Validate amount is within expected range',
        severity: 'medium',
        columns: ['amount']
      }
    ],
    test_cases: [
      {
        id: 1,
        name: 'test_null_values',
        description: 'Test for null values in critical columns',
        expected_result: 'No null values found'
      },
      {
        id: 2,
        name: 'test_data_ranges',
        description: 'Test data ranges are within bounds',
        expected_result: 'All values within expected ranges'
      }
    ],
    pyspark_code: `# Auto-generated PySpark code
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when

# Initialize Spark session
spark = SparkSession.builder.appName("DataQualityCheck").getOrCreate()

# Load data
df = spark.table("${formData.database_name}.${formData.table_name}")

# Perform quality checks
null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns])
print("Null value counts:")
null_counts.show()
`,
    execution_results: [
      {
        check: 'null_values',
        status: 'passed',
        details: 'No critical null values found'
      },
      {
        check: 'data_ranges',
        status: 'passed',
        details: 'All values within expected ranges'
      }
    ]
  }

  // Return appropriate mock result based on step
  const resultKeys = Object.keys(mockResults)
  return mockResults[resultKeys[stepId % resultKeys.length]]
}