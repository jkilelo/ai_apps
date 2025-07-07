import React, { useState } from 'react'
import { StepExecutionResult } from '../types/workflow'

interface StepResultsEnhancedProps {
  result: StepExecutionResult
  outputDefinitions?: Array<{
    name: string
    type: string
    description: string
  }>
  stepName?: string
}

export const StepResultsEnhanced: React.FC<StepResultsEnhancedProps> = ({ 
  result, 
  outputDefinitions = [],
  stepName 
}) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  
  // Debug logging
  console.log('StepResultsEnhanced - stepName:', stepName)
  console.log('StepResultsEnhanced - result:', result)
  console.log('StepResultsEnhanced - result.data:', result.data)

  const toggleExpanded = (key: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(key)) {
        newSet.delete(key)
      } else {
        newSet.add(key)
      }
      return newSet
    })
  }

  const formatValue = (value: any): string => {
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2)
    }
    return String(value)
  }

  if (result.status === 'error') {
    return (
      <div className="glass rounded-2xl p-6 animate-slideUp" style={{ 
        background: 'linear-gradient(135deg, rgba(255, 59, 48, 0.1) 0%, rgba(255, 59, 48, 0.05) 100%)',
        borderColor: 'rgba(255, 59, 48, 0.3)' 
      }}>
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center flex-shrink-0 animate-bounce">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-medium" style={{ color: 'var(--color-red)' }}>Execution Failed</h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              {new Date(result.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
        
        <div className="glass rounded-xl p-4 font-mono text-sm" style={{ 
          background: 'var(--bg-tertiary)', 
          color: 'var(--text-primary)' 
        }}>
          {result.error || 'An unknown error occurred'}
        </div>
      </div>
    )
  }

  // Render different UI based on step type
  if (stepName === 'element_extraction_using_python_playwright' && result.data?.extracted_elements) {
    return <ElementExtractionResults result={result} />
  }

  if (stepName === 'generate_test_cases_using_llm' && result.data?.test_cases) {
    return <TestGenerationResults result={result} />
  }

  if (stepName === 'execute_test_cases' && result.data?.test_results) {
    return <TestExecutionResults result={result} />
  }

  // Default result view - try to detect if this is element extraction data
  if (result.data?.extracted_elements && Array.isArray(result.data.extracted_elements)) {
    return <ElementExtractionResults result={result} />
  }
  
  // Try to detect if this is test generation data
  if (result.data?.test_cases && Array.isArray(result.data.test_cases)) {
    return <TestGenerationResults result={result} />
  }
  
  // Try to detect if this is test execution data
  if (result.data?.test_results && Array.isArray(result.data.test_results)) {
    return <TestExecutionResults result={result} />
  }
  
  // Generic successful result view
  return (
    <div className="glass rounded-2xl p-6 animate-slideUp" style={{ 
      background: 'linear-gradient(135deg, rgba(52, 199, 89, 0.1) 0%, rgba(52, 199, 89, 0.05) 100%)',
      borderColor: 'rgba(52, 199, 89, 0.3)' 
    }}>
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center flex-shrink-0 animate-bounce">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium" style={{ color: 'var(--color-green)' }}>Execution Successful</h3>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      {result.data && (
        <pre className="glass rounded-xl p-4 text-sm overflow-x-auto font-mono" style={{ 
          background: 'var(--bg-tertiary)', 
          color: 'var(--text-primary)' 
        }}>
          {formatValue(result.data)}
        </pre>
      )}
    </div>
  )
}

// Component for Element Extraction Results
const ElementExtractionResults: React.FC<{ result: StepExecutionResult }> = ({ result }) => {
  const elements = result.data?.extracted_elements || []
  const metadata = result.data?.metadata || {}
  
  return (
    <div className="glass rounded-2xl p-6 animate-slideUp" style={{ 
      background: 'linear-gradient(135deg, rgba(52, 199, 89, 0.1) 0%, rgba(52, 199, 89, 0.05) 100%)',
      borderColor: 'rgba(52, 199, 89, 0.3)' 
    }}>
      <div className="flex items-start gap-3 mb-6">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center flex-shrink-0 animate-bounce">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium" style={{ color: 'var(--color-green)' }}>Element Extraction Complete</h3>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Found {elements.length} elements across {metadata.pages_crawled || 1} page(s)
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {['button', 'input', 'link', 'form'].map((type, index) => {
            const count = elements.filter(e => e.type === type).length
            const colors = [
              { bg: 'from-blue-500 to-blue-600' },
              { bg: 'from-purple-500 to-purple-600' },
              { bg: 'from-orange-500 to-orange-600' },
              { bg: 'from-pink-500 to-pink-600' }
            ]
            return (
              <div key={type} className="glass rounded-xl p-4 text-center animate-scaleIn" style={{ animationDelay: `${index * 100}ms` }}>
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors[index].bg} flex items-center justify-center mx-auto mb-2`}>
                  <span className="text-white font-bold text-lg">{count}</span>
                </div>
                <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{type}s</p>
              </div>
            )
          })}
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
          {elements.map((element, index) => (
            <div key={element.id || index} className="glass rounded-xl p-4 hover:scale-[1.02] transition-all duration-200 animate-slideInLeft" style={{ animationDelay: `${index * 30}ms` }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="badge badge-blue">{element.type}</span>
                  <code className="text-xs px-2 py-1 glass rounded" style={{ color: 'var(--text-tertiary)' }}>{element.tag}</code>
                  {element.text && (
                    <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{element.text}</span>
                  )}
                </div>
                {element.is_interactive && (
                  <span className="badge badge-green">Interactive</span>
                )}
              </div>
              {element.selector && (
                <p className="text-xs mt-2 font-mono" style={{ color: 'var(--text-tertiary)' }}>{element.selector}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Component for Test Generation Results
const TestGenerationResults: React.FC<{ result: StepExecutionResult }> = ({ result }) => {
  const testCases = result.data?.test_cases || []
  const metadata = result.data?.metadata || {}
  const [selectedTest, setSelectedTest] = useState<any>(null)
  
  return (
    <div className="glass rounded-2xl p-6 animate-slideUp" style={{ 
      background: 'linear-gradient(135deg, rgba(52, 199, 89, 0.1) 0%, rgba(52, 199, 89, 0.05) 100%)',
      borderColor: 'rgba(52, 199, 89, 0.3)' 
    }}>
      <div className="flex items-start gap-3 mb-6">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center flex-shrink-0 animate-bounce">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium" style={{ color: 'var(--color-green)' }}>Test Generation Complete</h3>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Generated {testCases.length} test cases for {metadata.total_elements || 0} elements
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
          {testCases.map((test, index) => (
            <div
              key={test.id || index}
              onClick={() => setSelectedTest(test)}
              className={`glass rounded-xl p-4 cursor-pointer transition-all duration-200 animate-slideInLeft ${
                selectedTest?.id === test.id ? 'ring-2 ring-blue-500 scale-[1.02]' : 'hover:scale-[1.01]'
              }`}
              style={{ animationDelay: `${index * 30}ms` }}
            >
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  {test.name}
                </h4>
                <span className={`badge ${test.type === 'negative' ? 'badge-red' : 'badge-blue'}`}>
                  {test.type}
                </span>
              </div>
              <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                {test.expected_result}
              </p>
            </div>
          ))}
        </div>

        {selectedTest && (
          <div className="glass rounded-xl p-6 animate-slideInRight">
            <h4 className="font-medium mb-4" style={{ color: 'var(--text-primary)' }}>
              Test Details: {selectedTest.name}
            </h4>
            <div className="space-y-4">
              <div>
                <p className="text-xs font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>Steps:</p>
                <ol className="list-decimal list-inside space-y-2">
                  {selectedTest.steps.map((step: string, i: number) => (
                    <li key={i} className="text-sm glass rounded-lg p-3 animate-fadeIn" style={{ 
                      color: 'var(--text-primary)',
                      animationDelay: `${i * 100}ms`
                    }}>
                      {step}
                    </li>
                  ))}
                </ol>
              </div>
              {selectedTest.selector && (
                <div>
                  <p className="text-xs font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>Selector:</p>
                  <code className="text-xs block glass rounded-lg p-4 font-mono" style={{ 
                    color: 'var(--text-primary)' 
                  }}>
                    {selectedTest.selector}
                  </code>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Component for Test Execution Results
const TestExecutionResults: React.FC<{ result: StepExecutionResult }> = ({ result }) => {
  const testResults = result.data?.test_results || []
  const summary = result.data?.summary || {}
  
  return (
    <div className="glass rounded-2xl p-6 animate-slideUp" style={{ 
      background: 'linear-gradient(135deg, rgba(52, 199, 89, 0.1) 0%, rgba(52, 199, 89, 0.05) 100%)',
      borderColor: 'rgba(52, 199, 89, 0.3)' 
    }}>
      <div className="flex items-start gap-3 mb-6">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center flex-shrink-0 animate-bounce">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium" style={{ color: 'var(--color-green)' }}>Test Execution Complete</h3>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Pass rate: {summary.pass_rate?.toFixed(1) || 0}% ({summary.passed || 0}/{summary.total || 0} tests)
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="glass rounded-xl p-4 text-center animate-scaleIn">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center mx-auto mb-2">
              <span className="text-white font-bold text-lg">{summary.passed || 0}</span>
            </div>
            <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Passed</p>
          </div>
          <div className="glass rounded-xl p-4 text-center animate-scaleIn" style={{ animationDelay: '100ms' }}>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center mx-auto mb-2">
              <span className="text-white font-bold text-lg">{summary.failed || 0}</span>
            </div>
            <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Failed</p>
          </div>
          <div className="glass rounded-xl p-4 text-center animate-scaleIn" style={{ animationDelay: '200ms' }}>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500 to-yellow-600 flex items-center justify-center mx-auto mb-2">
              <span className="text-white font-bold text-lg">{summary.skipped || 0}</span>
            </div>
            <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Skipped</p>
          </div>
          <div className="glass rounded-xl p-4 text-center animate-scaleIn" style={{ animationDelay: '300ms' }}>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mx-auto mb-2">
              <span className="text-white font-bold text-lg">{summary.total || 0}</span>
            </div>
            <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Total</p>
          </div>
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
          {testResults.map((test, index) => (
            <div key={test.test_id || index} className="glass rounded-xl p-4 animate-slideInLeft" style={{ animationDelay: `${index * 30}ms` }}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                    {test.test_name}
                  </h4>
                  {test.error && (
                    <p className="text-xs mt-1" style={{ color: 'var(--color-red)' }}>{test.error}</p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                    {test.duration?.toFixed(2)}s
                  </span>
                  <span className={`badge ${
                    test.status === 'passed' ? 'badge-green' : 
                    test.status === 'failed' ? 'badge-red' : 
                    'badge-purple'
                  }`}>
                    {test.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}