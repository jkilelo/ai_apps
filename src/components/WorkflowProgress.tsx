import React from 'react'
import { AppStep } from '../types/app'
import { WorkflowStep, StepStatus } from '../types/workflow'

interface WorkflowProgressProps {
  steps: AppStep[]
  workflowSteps: Record<number, WorkflowStep>
  currentStepId: number | null
  onStepClick: (stepId: number) => void
  onViewResults?: (stepId: number) => void
}

export const WorkflowProgress: React.FC<WorkflowProgressProps> = ({
  steps,
  workflowSteps,
  currentStepId,
  onStepClick,
  onViewResults
}) => {
  const getStepStatus = (stepId: number): StepStatus => {
    return workflowSteps[stepId]?.status || 'locked'
  }

  const getStatusIcon = (status: StepStatus) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        )
      case 'in_progress':
        return (
          <svg className="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )
      case 'failed':
        return (
          <svg className="w-5 h-5 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )
      case 'locked':
        return (
          <svg className="w-5 h-5" style={{ color: 'var(--color-text-muted)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        )
      default:
        return <span className="text-2xl font-bold" style={{ color: 'var(--color-text-tertiary)' }}>{status === 'pending' ? '•' : ''}</span>
    }
  }

  const getStatusColor = (status: StepStatus, isActive: boolean) => {
    if (isActive) return 'border-primary-500 bg-primary-500/10'
    
    switch (status) {
      case 'completed':
        return 'border-green-500 bg-green-500/10'
      case 'in_progress':
        return 'border-primary-500 bg-primary-500/10'
      case 'failed':
        return 'border-accent-500 bg-accent-500/10'
      case 'pending':
        return 'hover:border-opacity-70'
      case 'locked':
        return 'opacity-50'
      default:
        return 'border-gray-700'
    }
  }

  const completedSteps = Object.values(workflowSteps).filter(s => s.status === 'completed').length
  const progressPercentage = (completedSteps / steps.length) * 100

  return (
    <div className="card-elevated p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-medium" style={{ color: 'var(--color-text-primary)' }}>Workflow Progress</h3>
          <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            {completedSteps} of {steps.length} steps completed
          </span>
        </div>
        
        <div className="w-full rounded-full h-3 overflow-hidden shadow-inner" style={{ background: 'var(--color-bg-tertiary)' }}>
          <div
            className="h-full bg-primary-500 transition-all duration-700 ease-out shadow-sm relative"
            style={{ width: `${progressPercentage}%` }}
          >
            <div className="absolute inset-0 bg-white/20 animate-pulse" />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {steps.map((step, index) => {
          const status = getStepStatus(step.id)
          const isActive = currentStepId === step.id
          const workflowStep = workflowSteps[step.id]
          
          return (
            <div key={step.id} className="relative">
              {index < steps.length - 1 && (
                <div className={`absolute left-6 top-14 w-0.5 h-16 transition-colors duration-300`} style={{ 
                  background: status === 'completed' ? '#22c55e' : 'var(--color-border-primary)'
                }} />
              )}
              
              <div
                onClick={() => status !== 'locked' && onStepClick(step.id)}
                className={`w-full p-4 rounded-lg border transition-all duration-200 ${
                  getStatusColor(status, isActive)
                } ${status !== 'locked' ? 'cursor-pointer' : 'cursor-not-allowed'}`}
                style={{ 
                  borderColor: isActive ? '' : 'var(--color-border-primary)',
                  background: isActive ? '' : 'var(--color-bg-secondary)'
                }}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                    isActive ? 'border-primary-500 bg-primary-500/10' : 
                    status === 'completed' ? 'border-green-500 bg-green-500/10' :
                    status === 'failed' ? 'border-accent-500 bg-accent-500/10' :
                    ''
                  }`} style={{
                    borderColor: (isActive || status === 'completed' || status === 'failed') ? '' : 'var(--color-border-secondary)',
                    background: (isActive || status === 'completed' || status === 'failed') ? '' : 'var(--color-bg-tertiary)'
                  }}>
                    {getStatusIcon(status)}
                  </div>
                  
                  <div className="flex-1 text-left">
                    <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                      {step.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h4>
                    <p className="text-sm line-clamp-1" style={{ color: 'var(--color-text-secondary)' }}>{step.Description}</p>
                    
                    {workflowStep?.completedAt && (
                      <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                        Completed at {new Date(workflowStep.completedAt).toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {status === 'completed' && onViewResults && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onViewResults(step.id)
                        }}
                        className="px-3 py-1 text-xs bg-green-500/10 hover:bg-green-500/20 text-green-600 rounded-lg transition-colors duration-200 border border-green-500/20"
                      >
                        View Results
                      </button>
                    )}
                    
                    <svg className={`w-5 h-5 transition-transform duration-200 ${
                      isActive ? 'rotate-90' : ''
                    }`} style={{ color: 'var(--color-text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}