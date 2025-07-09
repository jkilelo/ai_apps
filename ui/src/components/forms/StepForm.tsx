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
      <div className="glass rounded-2xl p-8 text-center animate-fadeIn">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full neumorphic flex items-center justify-center">
          <svg className="w-8 h-8" style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Step Locked</h3>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Complete the required dependencies first</p>
      </div>
    )
  }

  if (status === 'completed') {
    return (
      <div className="glass rounded-2xl p-8 text-center animate-fadeIn" style={{
        background: 'linear-gradient(135deg, rgba(52, 199, 89, 0.1) 0%, rgba(52, 199, 89, 0.05) 100%)',
        borderColor: 'rgba(52, 199, 89, 0.3)'
      }}>
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center animate-bounce">
          <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Step Completed</h3>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>This step has been successfully executed</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 animate-fadeIn">
      <div className="space-y-4">
        {step.input.map((input, index) => {
          const isFromPreviousStep = availableInputs[input.name] !== undefined
          return (
            <div key={input.name} className="animate-slideUp" style={{ animationDelay: `${index * 50}ms` }}>
              {isFromPreviousStep && (
                <div className="flex items-center gap-2 text-xs mb-2 animate-fadeIn" style={{ color: 'var(--color-blue)' }}>
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
          className="flex-1 btn btn-primary flex items-center justify-center gap-2"
        >
          {isExecuting ? (
            <>
              <div className="spinner"></div>
              <span>Executing...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Execute Step</span>
            </>
          )}
        </button>
        
        <button
          type="button"
          onClick={onCancel}
          disabled={isExecuting}
          className="btn btn-secondary"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}