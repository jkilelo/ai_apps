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
      <div className="card p-6" style={{ background: 'rgba(255, 60, 40, 0.05)', borderColor: 'rgba(255, 60, 40, 0.2)' }}>
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(255, 60, 40, 0.1)' }}>
            <svg className="w-6 h-6 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-medium text-accent-500">Execution Failed</h3>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              {new Date(result.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
        
        <div className="rounded-lg p-4 font-mono text-sm" style={{ 
          background: 'var(--color-bg-tertiary)', 
          color: 'var(--color-text-primary)' 
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
    <div className="card p-6" style={{ background: 'rgba(34, 197, 94, 0.05)', borderColor: 'rgba(34, 197, 94, 0.2)' }}>
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(34, 197, 94, 0.1)' }}>
          <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium text-green-500">Execution Successful</h3>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      {result.data && (
        <pre className="rounded-lg p-4 text-sm overflow-x-auto" style={{ 
          background: 'var(--color-bg-tertiary)', 
          color: 'var(--color-text-primary)' 
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
    <div className="card p-6" style={{ background: 'rgba(34, 197, 94, 0.05)', borderColor: 'rgba(34, 197, 94, 0.2)' }}>
      <div className="flex items-start gap-3 mb-6">
        <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(34, 197, 94, 0.1)' }}>
          <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium text-green-500">Element Extraction Complete</h3>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            Found {elements.length} elements across {metadata.pages_crawled || 1} page(s)
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {['button', 'input', 'link', 'form'].map((type) => {
            const count = elements.filter(e => e.type === type).length
            return (
              <div key={type} className="card p-3 text-center">
                <p className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>{count}</p>
                <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{type}s</p>
              </div>
            )
          })}
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {elements.map((element, index) => (
            <div key={element.id || index} className="card p-3 hover:shadow-sm transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="badge badge-primary">{element.type}</span>
                  <code className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{element.tag}</code>
                  {element.text && (
                    <span className="text-sm" style={{ color: 'var(--color-text-primary)' }}>{element.text}</span>
                  )}
                </div>
                {element.is_interactive && (
                  <span className="text-xs text-green-500">Interactive</span>
                )}
              </div>
              {element.selector && (
                <p className="text-xs mt-2 font-mono" style={{ color: 'var(--color-text-muted)' }}>{element.selector}</p>
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
    <div className="card p-6" style={{ background: 'rgba(34, 197, 94, 0.05)', borderColor: 'rgba(34, 197, 94, 0.2)' }}>
      <div className="flex items-start gap-3 mb-6">
        <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(34, 197, 94, 0.1)' }}>
          <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium text-green-500">Test Generation Complete</h3>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            Generated {testCases.length} test cases for {metadata.total_elements || 0} elements
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {testCases.map((test, index) => (
            <div
              key={test.id || index}
              onClick={() => setSelectedTest(test)}
              className={`card p-3 cursor-pointer transition-all ${
                selectedTest?.id === test.id ? 'ring-2 ring-primary-500' : 'hover:shadow-sm'
              }`}
            >
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                  {test.name}
                </h4>
                <span className={`badge ${test.type === 'negative' ? 'badge-accent' : 'badge-primary'}`}>
                  {test.type}
                </span>
              </div>
              <p className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                {test.expected_result}
              </p>
            </div>
          ))}
        </div>

        {selectedTest && (
          <div className="card p-4">
            <h4 className="font-medium mb-3" style={{ color: 'var(--color-text-primary)' }}>
              Test Details: {selectedTest.name}
            </h4>
            <div className="space-y-3">
              <div>
                <p className="text-xs font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Steps:</p>
                <ol className="list-decimal list-inside space-y-1">
                  {selectedTest.steps.map((step: string, i: number) => (
                    <li key={i} className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                      {step}
                    </li>
                  ))}
                </ol>
              </div>
              {selectedTest.selector && (
                <div>
                  <p className="text-xs font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Selector:</p>
                  <code className="text-xs block p-2 rounded" style={{ 
                    background: 'var(--color-bg-tertiary)', 
                    color: 'var(--color-text-primary)' 
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
    <div className="card p-6" style={{ background: 'rgba(34, 197, 94, 0.05)', borderColor: 'rgba(34, 197, 94, 0.2)' }}>
      <div className="flex items-start gap-3 mb-6">
        <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(34, 197, 94, 0.1)' }}>
          <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium text-green-500">Test Execution Complete</h3>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            Pass rate: {summary.pass_rate?.toFixed(1) || 0}% ({summary.passed || 0}/{summary.total || 0} tests)
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="card p-3 text-center">
            <p className="text-2xl font-bold text-green-500">{summary.passed || 0}</p>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Passed</p>
          </div>
          <div className="card p-3 text-center">
            <p className="text-2xl font-bold text-accent-500">{summary.failed || 0}</p>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Failed</p>
          </div>
          <div className="card p-3 text-center">
            <p className="text-2xl font-bold text-yellow-500">{summary.skipped || 0}</p>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Skipped</p>
          </div>
          <div className="card p-3 text-center">
            <p className="text-2xl font-bold text-primary-500">{summary.total || 0}</p>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Total</p>
          </div>
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {testResults.map((test, index) => (
            <div key={test.test_id || index} className="card p-3">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                    {test.test_name}
                  </h4>
                  {test.error && (
                    <p className="text-xs mt-1 text-accent-500">{test.error}</p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                    {test.duration?.toFixed(2)}s
                  </span>
                  <span className={`badge ${
                    test.status === 'passed' ? 'badge-primary' : 
                    test.status === 'failed' ? 'badge-accent' : 
                    'badge-neutral'
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