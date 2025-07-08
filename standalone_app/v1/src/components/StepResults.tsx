import React from 'react'
import { StepExecutionResult } from '../types/workflow'

interface StepResultsProps {
  result: StepExecutionResult
  outputDefinitions?: Array<{
    name: string
    type: string
    description: string
  }>
}

export const StepResults: React.FC<StepResultsProps> = ({ result, outputDefinitions = [] }) => {
  const formatValue = (value: any): string => {
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2)
    }
    return String(value)
  }

  if (result.status === 'error') {
    return (
      <div className="bg-accent-900/20 border border-accent-800/50 rounded-xl p-6">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-accent-800/30 flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-medium text-accent-400">Execution Failed</h3>
            <p className="text-sm text-gray-400 mt-1">
              {new Date(result.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
        
        <div className="bg-accent-900/20 rounded-lg p-4 font-mono text-sm text-accent-300">
          {result.error || 'An unknown error occurred'}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-green-900/20 border border-green-800/50 rounded-xl p-6">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 rounded-full bg-green-800/30 flex items-center justify-center flex-shrink-0">
          <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-medium text-green-400">Execution Successful</h3>
          <p className="text-sm text-gray-400 mt-1">
            {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      {result.data && (
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-300">Output Data</h4>
          
          {outputDefinitions.length > 0 ? (
            <div className="space-y-3">
              {outputDefinitions.map((output) => {
                const value = result.data[output.name]
                if (value === undefined) return null
                
                return (
                  <div key={output.name} className="bg-gray-800/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="text-sm font-medium text-gray-200">
                        {output.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </h5>
                      <span className="text-xs px-2 py-1 bg-gray-700 text-gray-400 rounded">
                        {output.type}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mb-2">{output.description}</p>
                    
                    <pre className="bg-gray-900 rounded p-3 text-xs text-gray-300 overflow-x-auto">
                      {formatValue(value)}
                    </pre>
                  </div>
                )
              })}
            </div>
          ) : (
            <pre className="bg-gray-900 rounded-lg p-4 text-sm text-gray-300 overflow-x-auto">
              {formatValue(result.data)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}