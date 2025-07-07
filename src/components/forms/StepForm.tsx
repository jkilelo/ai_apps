import React, { useState, useEffect } from 'react'
import { AppStep } from '../../types/app'
import { StepFormData, StepStatus } from '../../types/workflow'
import { FormInput } from './FormInput'
import dummyData from '../../data/dummyData.json'

interface StepFormProps {
  step: AppStep
  status: StepStatus
  formData: StepFormData
  availableInputs?: Record<string, any>
  onSubmit: (data: StepFormData) => void
  onCancel: () => void
  isExecuting?: boolean
}

export const StepForm: React.FC<StepFormProps> = ({
  step,
  status,
  formData: initialData,
  availableInputs = {},
  onSubmit,
  onCancel,
  isExecuting = false
}) => {
  const [formData, setFormData] = useState<StepFormData>(initialData)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  useEffect(() => {
    // Initialize form with default values based on input type
    const defaults: StepFormData = {}
    step.input.forEach(input => {
      // Check if we have a value from previous step outputs
      if (availableInputs[input.name] !== undefined) {
        defaults[input.name] = availableInputs[input.name]
      } else if (initialData[input.name] !== undefined) {
        defaults[input.name] = initialData[input.name]
      } else {
        if (input.type === 'array') {
          defaults[input.name] = []
        } else if (input.type === 'boolean') {
          defaults[input.name] = false
        } else {
          defaults[input.name] = ''
        }
      }
    })
    setFormData(defaults)
  }, [step.id, JSON.stringify(availableInputs), initialData])

  const handleChange = (name: string, value: any) => {
    setFormData(prev => ({ ...prev, [name]: value }))
    setTouched(prev => ({ ...prev, [name]: true }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    step.input.forEach(input => {
      if (input.required && !formData[input.name]) {
        newErrors[input.name] = `${input.name} is required`
      }
      
      // Add specific validations based on type
      if (input.type === 'array' && input.required && (!formData[input.name] || formData[input.name].length === 0)) {
        newErrors[input.name] = `At least one ${input.name} is required`
      }
    })
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validate()) {
      onSubmit(formData)
    }
  }

  const getInputOptions = (inputName: string): Array<{ label: string; value: string }> => {
    // Provide dynamic options based on input name
    if (inputName === 'database_name') {
      return dummyData.databases.map(db => ({
        label: db.display_name,
        value: db.name
      }))
    }
    
    if (inputName === 'table_name' && formData.database_name) {
      const db = dummyData.databases.find(d => d.name === formData.database_name)
      return db?.tables.map(table => ({
        label: table.display_name,
        value: table.name
      })) || []
    }
    
    if (inputName === 'columns' && formData.database_name && formData.table_name) {
      const db = dummyData.databases.find(d => d.name === formData.database_name)
      const table = db?.tables.find(t => t.name === formData.table_name)
      return table?.columns.map(col => ({
        label: `${col.name} (${col.type})`,
        value: col.name
      })) || []
    }
    
    return []
  }

  const getInputType = (input: any): string => {
    if (input.name.includes('database') || input.name.includes('table')) {
      return 'select'
    }
    if (input.type === 'array') {
      return 'array'
    }
    if (input.type === 'list<object>' || input.type === 'object') {
      return input.type
    }
    if (input.type === 'string' && input.description?.toLowerCase().includes('code')) {
      return 'textarea'
    }
    return 'text'
  }

  if (status === 'locked') {
    return (
      <div className="glass-enhanced rounded-xl p-8 text-center border-2 border-gray-700/50 border-dashed">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center shadow-xl">
          <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-300 mb-2">Step Locked</h3>
        <p className="text-sm text-gray-500">Complete the required dependencies first</p>
      </div>
    )
  }

  if (status === 'completed') {
    return (
      <div className="bg-gradient-to-br from-green-900/20 to-green-800/10 border border-green-800/50 rounded-xl p-8 text-center shadow-lg">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-green-700 to-green-800 flex items-center justify-center shadow-xl animate-bounce">
          <svg className="w-8 h-8 text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-green-300 mb-2">Step Completed</h3>
        <p className="text-sm text-gray-400">This step has been successfully executed</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="bg-gray-800/50 rounded-xl p-6 space-y-6">
      <div className="space-y-4">
        {step.input.map((input) => {
          const isFromPreviousStep = availableInputs[input.name] !== undefined
          return (
            <div key={input.name}>
              {isFromPreviousStep && (
                <div className="flex items-center gap-2 text-xs text-primary-400 mb-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  <span>Auto-filled from previous step</span>
                </div>
              )}
              <FormInput
                key={input.name}
                label={input.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                name={input.name}
                type={getInputType(input)}
                value={formData[input.name]}
                onChange={handleChange}
                required={input.required}
                placeholder={input.description}
                error={touched[input.name] ? errors[input.name] : undefined}
                disabled={isExecuting}
                options={getInputOptions(input.name)}
                description={input.description}
              />
            </div>
          )
        })}
      </div>

      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isExecuting}
          className="flex-1 px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isExecuting ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Executing...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Execute Step
            </>
          )}
        </button>
        
        <button
          type="button"
          onClick={onCancel}
          disabled={isExecuting}
          className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-gray-300 font-medium rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}