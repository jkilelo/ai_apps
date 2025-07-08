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
          <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )
      case 'in_progress':
        return (
          <div className="spinner"></div>
        )
      case 'failed':
        return (
          <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )
      case 'locked':
        return (
          <svg className="w-5 h-5" style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        )
      default:
        return <span className="text-2xl font-bold" style={{ color: 'var(--text-tertiary)' }}>{status === 'pending' ? '•' : ''}</span>
    }
  }

  const getStatusColor = (status: StepStatus, isActive: boolean) => {
    if (isActive) return 'scale-[1.02] shadow-lg'
    
    switch (status) {
      case 'completed':
        return 'hover:scale-[1.01]'
      case 'in_progress':
        return 'animate-pulse'
      case 'failed':
        return ''
      case 'pending':
        return 'hover:scale-[1.01]'
      case 'locked':
        return 'opacity-50'
      default:
        return ''
    }
  }

  const completedSteps = Object.values(workflowSteps).filter(s => s.status === 'completed').length
  const progressPercentage = (completedSteps / steps.length) * 100

  return (
    <div>
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-medium" style={{ color: 'var(--text-primary)' }}>Workflow Progress</h3>
          <span className="badge badge-blue">
            {completedSteps} of {steps.length}
          </span>
        </div>
        
        <div className="w-full rounded-full h-3 overflow-hidden glass" style={{ background: 'var(--bg-tertiary)' }}>
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-700 ease-out relative"
            style={{ width: `${progressPercentage}%` }}
          >
            <div className="absolute inset-0 bg-white/20 animate-shimmer" />
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
                <div className={`absolute left-6 top-16 w-0.5 h-14 transition-all duration-300`} style={{ 
                  background: status === 'completed' ? 'linear-gradient(to bottom, var(--color-green), transparent)' : 'var(--border-primary)',
                  opacity: status === 'completed' ? 1 : 0.3
                }} />
              )}
              
              <div
                onClick={() => status !== 'locked' && onStepClick(step.id)}
                className={`glass rounded-xl p-4 transition-all duration-300 animate-slideInLeft ${
                  getStatusColor(status, isActive)
                } ${status !== 'locked' ? 'cursor-pointer' : 'cursor-not-allowed'}`}
                style={{ 
                  animationDelay: `${index * 100}ms`,
                  background: isActive ? 'var(--glass-bg)' : '',
                  borderColor: isActive ? 'var(--color-blue)' : ''
                }}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 ${
                    isActive ? 'bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg' : 
                    status === 'completed' ? 'bg-gradient-to-br from-green-500 to-green-600' :
                    status === 'failed' ? 'bg-gradient-to-br from-red-500 to-red-600' :
                    status === 'in_progress' ? 'bg-gradient-to-br from-blue-500 to-blue-600' :
                    'neumorphic'
                  }`}>
                    {getStatusIcon(status)}
                  </div>
                  
                  <div className="flex-1 text-left">
                    <h4 className="font-medium" style={{ color: 'var(--text-primary)' }}>
                      {step.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h4>
                    <p className="text-sm line-clamp-1" style={{ color: 'var(--text-secondary)' }}>{step.Description}</p>
                    
                    {workflowStep?.completedAt && (
                      <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
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
                        className="btn btn-success py-1 px-3 text-xs"
                      >
                        View Results
                      </button>
                    )}
                    
                    <svg className={`w-5 h-5 transition-transform duration-300 ${
                      isActive ? 'rotate-90' : ''
                    }`} style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
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