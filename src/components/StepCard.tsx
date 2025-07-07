import React from 'react'
import { AppStep } from '../types/app'

interface StepCardProps {
  step: AppStep
  index: number
  isExpanded: boolean
  onToggleExpand: () => void
  dependencies?: (AppStep | undefined)[]
}

export const StepCard: React.FC<StepCardProps> = ({ 
  step, 
  index, 
  isExpanded, 
  onToggleExpand,
  dependencies = []
}) => {
  return (
    <div className="relative">
      {index > 0 && (
        <div className="absolute left-6 -top-4 w-0.5 h-4 bg-gray-700" />
      )}
      
      <div className={`bg-gray-800/50 border rounded-xl transition-all duration-200 ${
        isExpanded ? 'border-blue-500/50 shadow-lg shadow-blue-500/10' : 'border-gray-700 hover:border-gray-600'
      }`}>
        <button
          onClick={onToggleExpand}
          className="w-full px-6 py-4 flex items-center gap-4 text-left"
        >
          <div className={`w-12 h-12 rounded-full flex items-center justify-center font-semibold transition-all duration-200 ${
            isExpanded ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
          }`}>
            {step.id}
          </div>
          
          <div className="flex-1">
            <h3 className="font-medium text-white">
              {step.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h3>
            <p className="text-sm text-gray-400 mt-1">{step.Description}</p>
          </div>
          
          <div className="flex items-center gap-4">
            {dependencies.length > 0 && (
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                <span>{dependencies.length}</span>
              </div>
            )}
            
            <span className="text-xs text-gray-500">v{step.version}</span>
            
            <svg className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
              isExpanded ? 'rotate-180' : ''
            }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </button>
        
        {isExpanded && (
          <div className="px-6 pb-6 border-t border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-3">Inputs</h4>
                <div className="space-y-2">
                  {step.input.map((input, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <div className={`w-2 h-2 rounded-full mt-1.5 ${
                        input.required ? 'bg-red-400' : 'bg-gray-600'
                      }`} />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-gray-200">{input.name}</span>
                          <span className="text-xs px-1.5 py-0.5 bg-gray-700 text-gray-400 rounded">
                            {input.type}
                          </span>
                          {input.required && (
                            <span className="text-xs text-red-400">required</span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{input.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {step.output && step.output.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-3">Outputs</h4>
                  <div className="space-y-2">
                    {step.output.map((output, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <div className="w-2 h-2 rounded-full mt-1.5 bg-green-400" />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-gray-200">{output.name}</span>
                            <span className="text-xs px-1.5 py-0.5 bg-gray-700 text-gray-400 rounded">
                              {output.type}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{output.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            {dependencies.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-700">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Dependencies</h4>
                <div className="flex flex-wrap gap-2">
                  {dependencies.map((dep) => dep && (
                    <span key={dep.id} className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded">
                      Step {dep.id}: {dep.name.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}