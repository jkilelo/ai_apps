import React, { useState } from 'react'
import { App, SubApp } from '../types/app'
import { Breadcrumb } from './Breadcrumb'
import { WorkflowProgress } from './WorkflowProgress'
import { StepForm } from './forms/StepForm'
import { StepResultsEnhanced } from './StepResultsEnhanced'
import { useWorkflowWithAPI } from '../hooks/useWorkflowWithAPI'
import { StepFormData } from '../types/workflow'
import { EmptyState } from './ui/EmptyState'
import { SuccessAnimation } from './ui/SuccessAnimation'

interface MainPanelProps {
  selectedApp: App | null
}

export const MainPanel: React.FC<MainPanelProps> = ({ selectedApp }) => {
  const [selectedSubApp, setSelectedSubApp] = useState<SubApp | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [viewResultsStepId, setViewResultsStepId] = useState<number | null>(null)
  const [showSuccess, setShowSuccess] = useState(false)
  
  const currentSteps = selectedSubApp ? selectedSubApp.steps : (selectedApp?.steps || [])
  
  const { workflowState, executeStep, setCurrentStep, resetWorkflow, getAvailableInputs } = useWorkflowWithAPI(
    selectedApp?.id || 0,
    selectedSubApp?.id,
    currentSteps
  )

  const handleStepSubmit = async (stepId: number, formData: StepFormData) => {
    setIsExecuting(true)
    setViewResultsStepId(null)
    try {
      const result = await executeStep(stepId, formData)
      if (result.status === 'success') {
        setShowSuccess(true)
        
        // Auto-advance to next available step
        const nextStep = currentSteps.find(s => 
          s.id > stepId && workflowState.steps[s.id]?.status === 'pending'
        )
        if (nextStep) {
          setTimeout(() => setCurrentStep(nextStep.id), 500)
        }
      } else if (result.status === 'error') {
        console.error('Step execution error:', result.error)
        // Error is already stored in workflow state and will be displayed by StepResultsEnhanced
      }
    } catch (error) {
      console.error('Unexpected error in handleStepSubmit:', error)
    } finally {
      setIsExecuting(false)
    }
  }

  const breadcrumbItems = [
    { label: 'Apps', onClick: () => setSelectedSubApp(null) },
    ...(selectedApp ? [{ label: selectedApp.name.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) }] : []),
    ...(selectedSubApp ? [{ label: selectedSubApp.name.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) }] : [])
  ]

  if (!selectedApp) {
    return (
      <div className="flex-1 flex items-center justify-center ml-80 p-8" style={{ background: 'var(--color-bg-primary)' }}>
        <EmptyState
          title="Select an app to get started"
          description="Choose from the sidebar or use ⌘K to search"
          icon={
            <div className="w-24 h-24 mb-6 rounded-full flex items-center justify-center shadow-xl" style={{ background: 'var(--color-bg-tertiary)' }}>
              <svg className="w-12 h-12" style={{ color: 'var(--color-text-muted)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
              </svg>
            </div>
          }
        />
      </div>
    )
  }

  const currentStep = workflowState.currentStepId 
    ? currentSteps.find(s => s.id === workflowState.currentStepId)
    : null

  return (
    <main className="flex-1 ml-80 min-h-screen" style={{ background: 'var(--color-bg-primary)' }}>
      {showSuccess && <SuccessAnimation onComplete={() => setShowSuccess(false)} />}
      <div className="sticky top-0 z-10 backdrop-blur-sm border-b" style={{ background: 'var(--color-bg-primary)', borderColor: 'var(--color-border-primary)' }}>
        <div className="px-6 py-4">
          <Breadcrumb items={breadcrumbItems} />
          
          <div className="mt-4 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
                {(selectedSubApp ? selectedSubApp.name : selectedApp.name)
                  .replace(/_/g, ' ')
                  .replace(/\b\w/g, l => l.toUpperCase())}
              </h1>
              <p className="mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                {selectedSubApp ? selectedSubApp.Description : selectedApp.Description}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="badge badge-primary">
                v{selectedSubApp ? selectedSubApp.version : selectedApp.version}
              </span>
              {currentSteps.length > 0 && workflowState.overallProgress > 0 && (
                <button
                  onClick={resetWorkflow}
                  className="btn btn-secondary"
                >
                  Reset Workflow
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="p-6">
        {selectedApp.sub_apps && !selectedSubApp ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {selectedApp.sub_apps.map((subApp) => (
              <div
                key={subApp.id}
                onClick={() => setSelectedSubApp(subApp)}
                className="group relative card-elevated p-6 cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-[1.02]"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-primary-500 flex items-center justify-center text-white font-bold shadow-sm">
                    {subApp.name.charAt(0).toUpperCase()}
                  </div>
                  <svg className="w-5 h-5 transition-colors duration-200" style={{ color: 'var(--color-text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                
                <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>
                  {subApp.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </h3>
                <p className="text-sm mb-4 line-clamp-2" style={{ color: 'var(--color-text-secondary)' }}>
                  {subApp.Description}
                </p>
                
                <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    {subApp.steps.length} steps
                  </span>
                  <span>v{subApp.version}</span>
                </div>
              </div>
            ))}
          </div>
        ) : currentSteps.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <WorkflowProgress
                steps={currentSteps}
                workflowSteps={workflowState.steps}
                currentStepId={workflowState.currentStepId}
                onStepClick={setCurrentStep}
                onViewResults={(stepId) => {
                  setCurrentStep(stepId)
                  setViewResultsStepId(stepId)
                }}
              />
            </div>
            
            <div className="lg:col-span-2 space-y-6">
              {currentStep && (
                <>
                  {viewResultsStepId === currentStep.id && workflowState.steps[currentStep.id]?.result ? (
                    <>
                      <div className="card p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h2 className="text-xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                            {currentStep.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} - Results
                          </h2>
                          <button
                            onClick={() => setViewResultsStepId(null)}
                            className="btn btn-secondary"
                          >
                            Edit Step
                          </button>
                        </div>
                        <p style={{ color: 'var(--color-text-secondary)' }}>{currentStep.Description}</p>
                      </div>
                      
                      <StepResultsEnhanced
                        result={workflowState.steps[currentStep.id].result!}
                        outputDefinitions={currentStep.output}
                        stepName={currentStep.name}
                      />
                    </>
                  ) : (
                    <>
                      <div className="card p-6">
                        <h2 className="text-xl font-semibold text-white mb-2">
                          {currentStep.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </h2>
                        <p className="mb-6" style={{ color: 'var(--color-text-secondary)' }}>{currentStep.Description}</p>
                        
                        <StepForm
                          step={currentStep}
                          status={workflowState.steps[currentStep.id]?.status || 'locked'}
                          formData={workflowState.steps[currentStep.id]?.formData || {}}
                          availableInputs={getAvailableInputs(currentStep.id)}
                          onSubmit={(formData) => handleStepSubmit(currentStep.id, formData)}
                          onCancel={() => setCurrentStep(null)}
                          isExecuting={isExecuting}
                        />
                      </div>
                      
                      {workflowState.steps[currentStep.id]?.result && (
                        <StepResultsEnhanced
                          result={workflowState.steps[currentStep.id].result!}
                          outputDefinitions={currentStep.output}
                          stepName={currentStep.name}
                        />
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <p style={{ color: 'var(--color-text-tertiary)' }}>No workflow steps defined for this app.</p>
          </div>
        )}
      </div>
    </main>
  )
}