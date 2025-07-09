export type StepStatus = 'locked' | 'pending' | 'in_progress' | 'completed' | 'failed'

export interface StepFormData {
  [key: string]: any
}

export interface StepExecutionResult {
  status: 'success' | 'error'
  data?: any
  error?: string
  timestamp: string
}

export interface WorkflowStep {
  id: number
  status: StepStatus
  formData: StepFormData
  result?: StepExecutionResult
  startedAt?: string
  completedAt?: string
}

export interface WorkflowState {
  appId: number
  subAppId?: number
  steps: Record<number, WorkflowStep>
  currentStepId: number | null
  overallProgress: number
}