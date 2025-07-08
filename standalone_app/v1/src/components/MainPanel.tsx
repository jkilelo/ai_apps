import React, { useState, useEffect } from 'react'
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
      <div className="flex-1 flex items-center justify-center ml-80 p-8" style={{ background: 'var(--bg-primary)' }}>
        <div className="glass rounded-3xl p-12 max-w-md mx-auto text-center animate-scaleIn">
          <div className="relative inline-block mb-6">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center animate-pulse">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
          </div>
          <h3 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
            Select an app to get started
          </h3>
          <p className="text-base mb-6" style={{ color: 'var(--text-secondary)' }}>
            Choose from the sidebar or press <kbd className="px-2 py-1 mx-1 glass rounded text-xs">⌘K</kbd> to search
          </p>
          <button className="btn btn-primary">
            Browse Apps
          </button>
        </div>
      </div>
    )
  }

  const currentStep = workflowState.currentStepId 
    ? currentSteps.find(s => s.id === workflowState.currentStepId)
    : null

  return (
    <main className="flex-1 ml-80 min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      {showSuccess && <SuccessAnimation onComplete={() => setShowSuccess(false)} />}
      
      {/* Modern Header */}
      <div className="sticky top-0 z-10 glass-subtle border-b animate-slideDown" style={{ borderColor: 'var(--border-primary)' }}>
        <div className="px-8 py-6">
          <Breadcrumb items={breadcrumbItems} />
          
          <div className="mt-4 flex items-center justify-between">
            <div className="animate-slideInLeft">
              <h1 className="text-3xl font-bold gradient-text">
                {(selectedSubApp ? selectedSubApp.name : selectedApp.name)
                  .replace(/_/g, ' ')
                  .replace(/\b\w/g, l => l.toUpperCase())}
              </h1>
              <p className="mt-2 text-lg" style={{ color: 'var(--text-secondary)' }}>
                {selectedSubApp ? selectedSubApp.Description : selectedApp.Description}
              </p>
            </div>
            
            <div className="flex items-center gap-3 animate-slideInRight">
              <span className="badge badge-purple">
                v{selectedSubApp ? selectedSubApp.version : selectedApp.version}
              </span>
              {currentSteps.length > 0 && workflowState.overallProgress > 0 && (
                <button
                  onClick={resetWorkflow}
                  className="btn btn-secondary"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Reset
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="p-8">
        {selectedApp.sub_apps && !selectedSubApp ? (
          // Sub Apps Grid
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {selectedApp.sub_apps.map((subApp, index) => (
              <div
                key={subApp.id}
                onClick={() => setSelectedSubApp(subApp)}
                className="card-interactive group animate-slideUp"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                      <span className="text-white font-bold text-xl">
                        {subApp.name.substring(0, 2).toUpperCase()}
                      </span>
                    </div>
                    <svg className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                  
                  <h3 className="text-lg font-semibold mb-2 group-hover:text-blue-600 transition-colors" style={{ color: 'var(--text-primary)' }}>
                    {subApp.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </h3>
                  <p className="text-sm mb-4 line-clamp-2" style={{ color: 'var(--text-secondary)' }}>
                    {subApp.Description}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs" style={{ color: 'var(--text-tertiary)' }}>
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      {subApp.steps.length} steps
                    </span>
                    <span className="badge badge-blue">
                      v{subApp.version}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : currentSteps.length > 0 ? (
          // Workflow View
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Progress Panel */}
            <div className="lg:col-span-1">
              <div className="glass rounded-2xl p-6 animate-slideInLeft">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 1.414L10.586 9.5H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
                  </svg>
                  Workflow Progress
                </h2>
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
            </div>
            
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {currentStep && (
                <>
                  {viewResultsStepId === currentStep.id && workflowState.steps[currentStep.id]?.result ? (
                    // Results View
                    <>
                      <div className="glass rounded-2xl p-6 animate-slideUp">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h2 className="text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                              {currentStep.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h2>
                            <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                              Step Results
                            </p>
                          </div>
                          <button
                            onClick={() => setViewResultsStepId(null)}
                            className="btn btn-secondary"
                          >
                            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            Edit Step
                          </button>
                        </div>
                        <p style={{ color: 'var(--text-secondary)' }}>{currentStep.Description}</p>
                      </div>
                      
                      <div className="animate-slideUp" style={{ animationDelay: '100ms' }}>
                        <StepResultsEnhanced
                          result={workflowState.steps[currentStep.id].result!}
                          outputDefinitions={currentStep.output}
                          stepName={currentStep.name}
                        />
                      </div>
                    </>
                  ) : (
                    // Form View
                    <>
                      <div className="glass rounded-2xl p-6 animate-slideUp">
                        <div className="flex items-start gap-4 mb-6">
                          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                            <span className="text-white font-bold">
                              {currentStep.id}
                            </span>
                          </div>
                          <div>
                            <h2 className="text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                              {currentStep.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h2>
                            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
                              {currentStep.Description}
                            </p>
                          </div>
                        </div>
                        
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
                        <div className="animate-slideUp" style={{ animationDelay: '100ms' }}>
                          <StepResultsEnhanced
                            result={workflowState.steps[currentStep.id].result!}
                            outputDefinitions={currentStep.output}
                            stepName={currentStep.name}
                          />
                        </div>
                      )}
                    </>
                  )}
                </>
              )}
              
              {!currentStep && (
                <div className="glass rounded-2xl p-12 text-center animate-scaleIn">
                  <svg className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                    Select a step to begin
                  </h3>
                  <p style={{ color: 'var(--text-secondary)' }}>
                    Click on any step in the workflow to get started
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          // No Steps
          <div className="glass rounded-2xl p-12 text-center animate-scaleIn">
            <svg className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p style={{ color: 'var(--text-secondary)' }}>
              No workflow steps defined for this app.
            </p>
          </div>
        )}
      </div>
    </main>
  )
}