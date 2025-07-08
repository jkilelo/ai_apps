import React from 'react'
import { Tooltip } from '../ui/Tooltip'

interface FormInputProps {
  label: string
  name: string
  type?: string
  value: any
  onChange: (name: string, value: any) => void
  required?: boolean
  placeholder?: string
  error?: string
  disabled?: boolean
  options?: Array<{ label: string; value: string }>
  description?: string
}

export const FormInput: React.FC<FormInputProps> = ({
  label,
  name,
  type = 'text',
  value,
  onChange,
  required = false,
  placeholder,
  error,
  disabled = false,
  options = [],
  description
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const newValue = type === 'number' ? Number(e.target.value) : e.target.value
    onChange(name, newValue)
  }

  const handleArrayChange = (index: number, newValue: string) => {
    const newArray = [...(value || [])]
    newArray[index] = newValue
    onChange(name, newArray)
  }

  const addArrayItem = () => {
    onChange(name, [...(value || []), ''])
  }

  const removeArrayItem = (index: number) => {
    const newArray = (value || []).filter((_: any, i: number) => i !== index)
    onChange(name, newArray)
  }

  const baseInputClasses = `
    w-full px-4 py-3 bg-gray-800/50 border rounded-xl text-gray-100 
    placeholder-gray-500 transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500
    focus:bg-gray-800/70 focus:shadow-lg focus:shadow-primary-500/10
    disabled:opacity-50 disabled:cursor-not-allowed
    ${error ? 'border-accent-500 bg-accent-900/10' : 'border-gray-700/50 hover:border-gray-600/50'}
  `

  return (
    <div className="space-y-2">
      <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
        {label}
        {required && (
          <Tooltip content="This field is required">
            <span className="text-accent-400 cursor-help">*</span>
          </Tooltip>
        )}
      </label>
      
      {description && (
        <p className="text-xs text-gray-500">{description}</p>
      )}

      {type === 'select' ? (
        <select
          name={name}
          value={value || ''}
          onChange={handleChange}
          disabled={disabled}
          className={baseInputClasses}
        >
          <option value="">Select {label.toLowerCase()}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : type === 'array' ? (
        <div className="space-y-2">
          {(value || []).map((item: string, index: number) => (
            <div key={index} className="flex gap-2">
              <input
                type="text"
                value={item}
                onChange={(e) => handleArrayChange(index, e.target.value)}
                disabled={disabled}
                placeholder={`Item ${index + 1}`}
                className={baseInputClasses}
              />
              <button
                type="button"
                onClick={() => removeArrayItem(index)}
                disabled={disabled}
                className="px-3 py-2 bg-accent-600/20 hover:bg-accent-600/30 text-accent-400 rounded-lg transition-all duration-200 disabled:opacity-50 hover:shadow-lg hover:shadow-accent-500/20 hover:scale-105"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addArrayItem}
            disabled={disabled}
            className="w-full px-4 py-2 bg-primary-600/20 hover:bg-primary-600/30 text-primary-400 rounded-lg transition-all duration-200 disabled:opacity-50 hover:shadow-lg hover:shadow-primary-500/20 border border-primary-600/30 hover:border-primary-600/50"
          >
            Add Item
          </button>
        </div>
      ) : type === 'textarea' ? (
        <textarea
          name={name}
          value={value || ''}
          onChange={handleChange}
          disabled={disabled}
          placeholder={placeholder}
          rows={4}
          className={baseInputClasses}
        />
      ) : type === 'object' || type === 'list<object>' ? (
        <div className="space-y-2">
          <textarea
            name={name}
            value={typeof value === 'object' ? JSON.stringify(value, null, 2) : value || ''}
            onChange={handleChange}
            disabled={true}
            placeholder={placeholder}
            rows={8}
            className={`${baseInputClasses} font-mono text-xs`}
          />
          <p className="text-xs text-gray-500">
            This field contains structured data from the previous step
          </p>
        </div>
      ) : (
        <input
          type={type}
          name={name}
          value={typeof value === 'object' ? JSON.stringify(value) : value || ''}
          onChange={handleChange}
          disabled={disabled}
          placeholder={placeholder}
          className={baseInputClasses}
        />
      )}

      {error && (
        <p className="text-xs text-accent-400 flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </p>
      )}
    </div>
  )
}