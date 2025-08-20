import { forwardRef } from 'react';

interface FormInputProps {
    label: string;
    type: string;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    description?: string;
    required?: boolean;
    maxLength?: number;
}

const FormInput = forwardRef<HTMLInputElement, FormInputProps>(
    ({ label, type, value, onChange, placeholder, description, required, maxLength }, ref) => {
        return (
            <div>
                <label className="label">
                    {label}
                    {required && <span className="text-red-500 ml-1">*</span>}
                </label>
                <input
                    ref={ref}
                    type={type}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder}
                    required={required}
                    maxLength={maxLength}
                    className="input-field"
                />
                {description && (
                    <p className="mt-1 text-sm text-gray-500">{description}</p>
                )}
            </div>
        );
    }
);

FormInput.displayName = 'FormInput';

export default FormInput;
