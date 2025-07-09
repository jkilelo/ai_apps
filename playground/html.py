#!/usr/bin/env python3
"""
Dynamic HTML Form Wizard Generator with FastAPI/Pydantic Integration

This module provides a complete solution for creating multi-step form wizards
with dynamic form generation based on previous step inputs, with tight integration
for FastAPI Request/Response models using Pydantic.
"""

import json
from typing import Dict, List, Any, Optional, Union, Callable, Type, get_type_hints, get_args, get_origin
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime, date, time
from decimal import Decimal
import inspect

# Pydantic imports - these are optional but enable the FastAPI integration
try:
    from pydantic import BaseModel, Field, ValidationError
    try:
        # Pydantic v2
        from pydantic.fields import FieldInfo
    except ImportError:
        # Pydantic v1
        from pydantic.fields import ModelField as FieldInfo
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None
    Field = None
    FieldInfo = None


class FieldType(Enum):
    """Enumeration of supported form field types"""
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    TEL = "tel"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime-local"
    TEXTAREA = "textarea"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE = "file"
    HIDDEN = "hidden"
    RANGE = "range"
    COLOR = "color"
    URL = "url"


@dataclass
class ValidationRule:
    """Represents a validation rule for a form field"""
    type: str  # required, min, max, pattern, custom
    value: Any = None
    message: str = ""
    
    def to_html_attrs(self) -> Dict[str, str]:
        """Convert validation rule to HTML attributes"""
        attrs = {}
        if self.type == "required":
            attrs["required"] = "required"
        elif self.type == "min":
            attrs["min"] = str(self.value)
        elif self.type == "max":
            attrs["max"] = str(self.value)
        elif self.type == "minlength":
            attrs["minlength"] = str(self.value)
        elif self.type == "maxlength":
            attrs["maxlength"] = str(self.value)
        elif self.type == "pattern":
            attrs["pattern"] = str(self.value)
        return attrs


@dataclass
class FormField:
    """Represents a single form field"""
    name: str
    type: FieldType
    label: str
    placeholder: str = ""
    default_value: Any = None
    options: List[Dict[str, str]] = field(default_factory=list)  # For select, radio, checkbox
    validation_rules: List[ValidationRule] = field(default_factory=list)
    css_classes: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    help_text: str = ""
    depends_on: Optional[Dict[str, Any]] = None  # Conditional display based on other fields
    
    def render(self, step_index: int, form_data: Dict[str, Any] = None) -> str:
        """Render the form field as HTML"""
        # Check if field should be displayed based on dependencies
        if self.depends_on and form_data:
            for field_name, expected_value in self.depends_on.items():
                if form_data.get(field_name) != expected_value:
                    return ""  # Don't render if dependency not met
        
        # Build validation attributes
        validation_attrs = {}
        for rule in self.validation_rules:
            validation_attrs.update(rule.to_html_attrs())
        
        # Merge all attributes
        all_attrs = {**self.attributes, **validation_attrs}
        attrs_str = " ".join(f'{k}="{v}"' for k, v in all_attrs.items())
        
        # Get current value
        current_value = ""
        if form_data and self.name in form_data:
            current_value = form_data[self.name]
        elif self.default_value is not None:
            current_value = self.default_value
        
        # Base field wrapper
        field_html = f'<div class="form-field {self.css_classes}" data-field-name="{self.name}">'
        
        # Label
        required = any(rule.type == "required" for rule in self.validation_rules)
        required_indicator = '<span class="required">*</span>' if required else ''
        field_html += f'<label for="{self.name}_step{step_index}">{self.label}{required_indicator}</label>'
        
        # Field input
        field_id = f"{self.name}_step{step_index}"
        
        if self.type == FieldType.TEXTAREA:
            field_html += f'<textarea id="{field_id}" name="{self.name}" placeholder="{self.placeholder}" {attrs_str}>{current_value}</textarea>'
        
        elif self.type == FieldType.SELECT:
            field_html += f'<select id="{field_id}" name="{self.name}" {attrs_str}>'
            if self.placeholder:
                field_html += f'<option value="">{self.placeholder}</option>'
            for option in self.options:
                selected = 'selected' if str(option["value"]) == str(current_value) else ''
                field_html += f'<option value="{option["value"]}" {selected}>{option["label"]}</option>'
            field_html += '</select>'
        
        elif self.type == FieldType.RADIO:
            field_html += '<div class="radio-group">'
            for i, option in enumerate(self.options):
                checked = 'checked' if str(option["value"]) == str(current_value) else ''
                field_html += f'''
                    <label class="radio-label">
                        <input type="radio" id="{field_id}_{i}" name="{self.name}" value="{option["value"]}" {checked} {attrs_str}>
                        <span>{option["label"]}</span>
                    </label>
                '''
            field_html += '</div>'
        
        elif self.type == FieldType.CHECKBOX:
            if self.options:  # Multiple checkboxes
                field_html += '<div class="checkbox-group">'
                current_values = current_value if isinstance(current_value, list) else []
                for i, option in enumerate(self.options):
                    checked = 'checked' if option["value"] in current_values else ''
                    field_html += f'''
                        <label class="checkbox-label">
                            <input type="checkbox" id="{field_id}_{i}" name="{self.name}[]" value="{option["value"]}" {checked} {attrs_str}>
                            <span>{option["label"]}</span>
                        </label>
                    '''
                field_html += '</div>'
            else:  # Single checkbox
                checked = 'checked' if current_value else ''
                field_html += f'''
                    <label class="checkbox-label">
                        <input type="checkbox" id="{field_id}" name="{self.name}" value="1" {checked} {attrs_str}>
                        <span>{self.label}</span>
                    </label>
                '''
        
        else:  # Standard input types
            field_html += f'<input type="{self.type.value}" id="{field_id}" name="{self.name}" value="{current_value}" placeholder="{self.placeholder}" {attrs_str}>'
        
        # Help text
        if self.help_text:
            field_html += f'<small class="help-text">{self.help_text}</small>'
        
        # Validation messages
        field_html += '<div class="validation-message"></div>'
        
        field_html += '</div>'
        
        return field_html


@dataclass
class FormStep:
    """Represents a single step in the form wizard"""
    title: str
    description: str = ""
    fields: List[FormField] = field(default_factory=list)
    validator: Optional[Callable] = None  # Custom validation function
    dynamic_fields_generator: Optional[Callable] = None  # Generate fields based on previous data
    
    def render(self, step_index: int, form_data: Dict[str, Any] = None) -> str:
        """Render the form step as HTML"""
        # Generate dynamic fields if generator provided
        if self.dynamic_fields_generator and form_data:
            dynamic_fields = self.dynamic_fields_generator(form_data)
            all_fields = self.fields + dynamic_fields
        else:
            all_fields = self.fields
        
        step_html = f'''
        <div class="form-step" data-step="{step_index}">
            <h2>{self.title}</h2>
            {f'<p class="step-description">{self.description}</p>' if self.description else ''}
            <div class="form-fields">
        '''
        
        for field in all_fields:
            step_html += field.render(step_index, form_data)
        
        step_html += '''
            </div>
        </div>
        '''
        
        return step_html


class FormWizard:
    """Main class for creating multi-step form wizards"""
    
    def __init__(self, title: str, steps: List[FormStep], submit_url: str = "#", method: str = "POST"):
        self.title = title
        self.steps = steps
        self.submit_url = submit_url
        self.method = method
        self.theme = "default"
        self.save_progress = True
        self.show_progress_bar = True
        self.allow_step_navigation = True
        
    def generate_html(self, include_styles: bool = True, include_scripts: bool = True) -> str:
        """Generate the complete HTML for the form wizard"""
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
'''
        
        if include_styles:
            html += self._generate_styles()
        
        html += '''
</head>
<body>
    <div class="form-wizard-container">
'''
        
        # Progress bar
        if self.show_progress_bar:
            html += self._generate_progress_bar()
        
        # Form
        html += f'''
        <form id="wizardForm" action="{self.submit_url}" method="{self.method}" novalidate>
            <div class="form-steps-container">
'''
        
        # Render each step
        for i, step in enumerate(self.steps):
            html += step.render(i)
        
        html += '''
            </div>
            
            <!-- Navigation buttons -->
            <div class="form-navigation">
                <button type="button" class="btn btn-secondary" id="prevBtn" onclick="changeStep(-1)" style="display: none;">Previous</button>
                <button type="button" class="btn btn-primary" id="nextBtn" onclick="changeStep(1)">Next</button>
                <button type="submit" class="btn btn-success" id="submitBtn" style="display: none;">Submit</button>
            </div>
        </form>
        
        <!-- Summary/Confirmation -->
        <div id="summaryContainer" style="display: none;">
            <h2>Submission Summary</h2>
            <div id="summaryContent"></div>
            <button type="button" class="btn btn-primary" onclick="editForm()">Edit</button>
            <button type="button" class="btn btn-success" onclick="confirmSubmission()">Confirm & Submit</button>
        </div>
    </div>
'''
        
        if include_scripts:
            html += self._generate_scripts()
        
        html += '''
</body>
</html>
'''
        
        return html
    
    def _generate_progress_bar(self) -> str:
        """Generate progress bar HTML"""
        progress_html = '<div class="progress-container">'
        
        for i, step in enumerate(self.steps):
            active_class = 'active' if i == 0 else ''
            progress_html += f'''
                <div class="progress-step {active_class}" data-step="{i}">
                    <div class="progress-bullet">{i + 1}</div>
                    <div class="progress-label">{step.title}</div>
                </div>
            '''
            
            if i < len(self.steps) - 1:
                progress_html += '<div class="progress-line"></div>'
        
        progress_html += '</div>'
        return progress_html
    
    def _generate_styles(self) -> str:
        """Generate CSS styles for the form wizard"""
        return '''
    <style>
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        
        .form-wizard-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        
        /* Progress Bar */
        .progress-container {
            display: flex;
            align-items: center;
            margin-bottom: 40px;
            padding: 20px 0;
        }
        
        .progress-step {
            flex: 1;
            text-align: center;
            position: relative;
        }
        
        .progress-bullet {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: #e0e0e0;
            color: #999;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .progress-step.active .progress-bullet,
        .progress-step.completed .progress-bullet {
            background-color: #4CAF50;
            color: white;
        }
        
        .progress-step.active .progress-label {
            color: #4CAF50;
            font-weight: 600;
        }
        
        .progress-label {
            margin-top: 8px;
            font-size: 14px;
            color: #666;
        }
        
        .progress-line {
            flex: 1;
            height: 2px;
            background-color: #e0e0e0;
            margin: 0 -20px;
            transform: translateY(-20px);
        }
        
        .progress-step.completed + .progress-line {
            background-color: #4CAF50;
        }
        
        /* Form Steps */
        .form-step {
            display: none;
            animation: slideIn 0.3s ease-out;
        }
        
        .form-step.active {
            display: block;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .form-step h2 {
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .step-description {
            color: #666;
            margin-bottom: 30px;
        }
        
        /* Form Fields */
        .form-field {
            margin-bottom: 20px;
        }
        
        .form-field label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #555;
        }
        
        .form-field input,
        .form-field select,
        .form-field textarea {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        
        .form-field input:focus,
        .form-field select:focus,
        .form-field textarea:focus {
            outline: none;
            border-color: #4CAF50;
            box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
        }
        
        .form-field input.error,
        .form-field select.error,
        .form-field textarea.error {
            border-color: #f44336;
        }
        
        .required {
            color: #f44336;
            margin-left: 3px;
        }
        
        .help-text {
            display: block;
            margin-top: 5px;
            color: #666;
            font-size: 14px;
        }
        
        .validation-message {
            color: #f44336;
            font-size: 14px;
            margin-top: 5px;
            display: none;
        }
        
        .validation-message.show {
            display: block;
        }
        
        /* Radio and Checkbox Groups */
        .radio-group,
        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .radio-label,
        .checkbox-label {
            display: flex;
            align-items: center;
            cursor: pointer;
        }
        
        .radio-label input,
        .checkbox-label input {
            width: auto;
            margin-right: 8px;
        }
        
        /* Navigation Buttons */
        .form-navigation {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        
        .btn {
            padding: 10px 30px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-primary {
            background-color: #2196F3;
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #1976D2;
        }
        
        .btn-secondary {
            background-color: #757575;
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: #616161;
        }
        
        .btn-success {
            background-color: #4CAF50;
            color: white;
        }
        
        .btn-success:hover {
            background-color: #45a049;
        }
        
        /* Summary */
        #summaryContainer {
            animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        .summary-section {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }
        
        .summary-section h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        
        .summary-field {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .summary-label {
            font-weight: 500;
            color: #555;
        }
        
        .summary-value {
            color: #333;
        }
        
        /* Responsive */
        @media (max-width: 600px) {
            .form-wizard-container {
                padding: 20px;
            }
            
            .progress-label {
                font-size: 12px;
            }
            
            .progress-bullet {
                width: 30px;
                height: 30px;
                font-size: 14px;
            }
            
            .form-navigation {
                flex-direction: column;
                gap: 10px;
            }
            
            .btn {
                width: 100%;
            }
        }
    </style>
'''
    
    def _generate_scripts(self) -> str:
        """Generate JavaScript for form wizard functionality"""
        return '''
    <script>
        // Form Wizard State
        let currentStep = 0;
        const formData = {};
        const form = document.getElementById('wizardForm');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');
        const summaryContainer = document.getElementById('summaryContainer');
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            showStep(currentStep);
            loadSavedProgress();
            
            // Add form submit handler
            form.addEventListener('submit', handleSubmit);
            
            // Add input change handlers for saving progress
            form.addEventListener('input', saveProgress);
            form.addEventListener('change', saveProgress);
        });
        
        function showStep(stepIndex) {
            const steps = document.querySelectorAll('.form-step');
            const progressSteps = document.querySelectorAll('.progress-step');
            
            // Hide all steps
            steps.forEach(step => {
                step.classList.remove('active');
            });
            
            // Show current step
            if (steps[stepIndex]) {
                steps[stepIndex].classList.add('active');
            }
            
            // Update progress bar
            progressSteps.forEach((step, index) => {
                step.classList.remove('active', 'completed');
                if (index < stepIndex) {
                    step.classList.add('completed');
                } else if (index === stepIndex) {
                    step.classList.add('active');
                }
            });
            
            // Update navigation buttons
            updateNavigationButtons();
            
            // Focus first input in current step
            const firstInput = steps[stepIndex]?.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        }
        
        function updateNavigationButtons() {
            const totalSteps = document.querySelectorAll('.form-step').length;
            
            // Previous button
            if (currentStep === 0) {
                prevBtn.style.display = 'none';
            } else {
                prevBtn.style.display = 'inline-block';
            }
            
            // Next/Submit buttons
            if (currentStep === totalSteps - 1) {
                nextBtn.style.display = 'none';
                submitBtn.style.display = 'inline-block';
            } else {
                nextBtn.style.display = 'inline-block';
                submitBtn.style.display = 'none';
            }
        }
        
        function changeStep(direction) {
            const totalSteps = document.querySelectorAll('.form-step').length;
            
            // Validate current step before moving forward
            if (direction > 0 && !validateCurrentStep()) {
                return;
            }
            
            // Save current step data
            saveStepData();
            
            // Update step index
            currentStep += direction;
            
            // Ensure step is within bounds
            if (currentStep < 0) {
                currentStep = 0;
            } else if (currentStep >= totalSteps) {
                currentStep = totalSteps - 1;
            }
            
            // Show new step
            showStep(currentStep);
            
            // Generate dynamic fields for next step if needed
            if (direction > 0) {
                generateDynamicFields();
            }
        }
        
        function validateCurrentStep() {
            const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
            const inputs = currentStepElement.querySelectorAll('input, select, textarea');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            return isValid;
        }
        
        function validateField(field) {
            const fieldContainer = field.closest('.form-field');
            const validationMessage = fieldContainer.querySelector('.validation-message');
            
            // Reset validation state
            field.classList.remove('error');
            validationMessage.textContent = '';
            validationMessage.classList.remove('show');
            
            // Check HTML5 validation
            if (!field.checkValidity()) {
                field.classList.add('error');
                validationMessage.textContent = field.validationMessage;
                validationMessage.classList.add('show');
                return false;
            }
            
            // Custom validation can be added here
            
            return true;
        }
        
        function saveStepData() {
            const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
            const inputs = currentStepElement.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                if (input.type === 'checkbox') {
                    if (input.name.endsWith('[]')) {
                        // Multiple checkboxes
                        const name = input.name.slice(0, -2);
                        if (!formData[name]) {
                            formData[name] = [];
                        }
                        if (input.checked && !formData[name].includes(input.value)) {
                            formData[name].push(input.value);
                        } else if (!input.checked) {
                            formData[name] = formData[name].filter(v => v !== input.value);
                        }
                    } else {
                        // Single checkbox
                        formData[input.name] = input.checked;
                    }
                } else if (input.type === 'radio') {
                    if (input.checked) {
                        formData[input.name] = input.value;
                    }
                } else {
                    formData[input.name] = input.value;
                }
            });
            
            saveProgress();
        }
        
        function saveProgress() {
            if (typeof(Storage) !== "undefined") {
                localStorage.setItem('formWizardData', JSON.stringify(formData));
                localStorage.setItem('formWizardStep', currentStep);
            }
        }
        
        function loadSavedProgress() {
            if (typeof(Storage) !== "undefined") {
                const savedData = localStorage.getItem('formWizardData');
                const savedStep = localStorage.getItem('formWizardStep');
                
                if (savedData) {
                    Object.assign(formData, JSON.parse(savedData));
                    populateFormFields();
                }
                
                if (savedStep) {
                    currentStep = parseInt(savedStep);
                    showStep(currentStep);
                }
            }
        }
        
        function populateFormFields() {
            Object.keys(formData).forEach(fieldName => {
                const value = formData[fieldName];
                const fields = document.querySelectorAll(`[name="${fieldName}"], [name="${fieldName}[]"]`);
                
                fields.forEach(field => {
                    if (field.type === 'checkbox') {
                        if (Array.isArray(value)) {
                            field.checked = value.includes(field.value);
                        } else {
                            field.checked = value;
                        }
                    } else if (field.type === 'radio') {
                        field.checked = field.value === value;
                    } else {
                        field.value = value;
                    }
                });
            });
        }
        
        function generateDynamicFields() {
            // This function would be customized based on your specific needs
            // It can modify the DOM to add/remove fields based on formData
        }
        
        function handleSubmit(e) {
            e.preventDefault();
            
            if (!validateCurrentStep()) {
                return;
            }
            
            saveStepData();
            showSummary();
        }
        
        function showSummary() {
            const summaryContent = document.getElementById('summaryContent');
            summaryContent.innerHTML = '';
            
            // Group data by steps
            document.querySelectorAll('.form-step').forEach((step, index) => {
                const stepTitle = step.querySelector('h2').textContent;
                const section = document.createElement('div');
                section.className = 'summary-section';
                section.innerHTML = `<h3>${stepTitle}</h3>`;
                
                const fields = step.querySelectorAll('.form-field');
                fields.forEach(fieldContainer => {
                    const fieldName = fieldContainer.dataset.fieldName;
                    if (formData[fieldName] !== undefined && formData[fieldName] !== '') {
                        const label = fieldContainer.querySelector('label').textContent.replace('*', '').trim();
                        const value = Array.isArray(formData[fieldName]) 
                            ? formData[fieldName].join(', ') 
                            : formData[fieldName];
                        
                        const fieldDiv = document.createElement('div');
                        fieldDiv.className = 'summary-field';
                        fieldDiv.innerHTML = `
                            <span class="summary-label">${label}:</span>
                            <span class="summary-value">${value}</span>
                        `;
                        section.appendChild(fieldDiv);
                    }
                });
                
                if (section.querySelector('.summary-field')) {
                    summaryContent.appendChild(section);
                }
            });
            
            // Hide form and show summary
            form.style.display = 'none';
            summaryContainer.style.display = 'block';
        }
        
        function editForm() {
            form.style.display = 'block';
            summaryContainer.style.display = 'none';
        }
        
        function confirmSubmission() {
            // Create form data object
            const formDataObj = new FormData();
            Object.keys(formData).forEach(key => {
                if (Array.isArray(formData[key])) {
                    formData[key].forEach(value => {
                        formDataObj.append(key, value);
                    });
                } else {
                    formDataObj.append(key, formData[key]);
                }
            });
            
            // Submit form via AJAX
            fetch(form.action, {
                method: form.method,
                body: formDataObj
            })
            .then(response => response.json())
            .then(data => {
                alert('Form submitted successfully!');
                clearProgress();
            })
            .catch(error => {
                alert('Error submitting form: ' + error.message);
            });
        }
        
        function clearProgress() {
            if (typeof(Storage) !== "undefined") {
                localStorage.removeItem('formWizardData');
                localStorage.removeItem('formWizardStep');
            }
        }
    </script>
'''


# Pydantic/FastAPI Integration
class PydanticFormConverter:
    """Converts Pydantic models to form fields and wizards"""
    
    @staticmethod
    def get_field_type_from_annotation(annotation: Any) -> FieldType:
        """Map Python type annotations to HTML field types"""
        # Handle Optional types
        origin = get_origin(annotation)
        if origin is Union:
            args = get_args(annotation)
            # Filter out None type for Optional fields
            non_none_args = [arg for arg in args if arg is not type(None)]
            if non_none_args:
                annotation = non_none_args[0]
        
        # Direct type mappings
        type_map = {
            str: FieldType.TEXT,
            int: FieldType.NUMBER,
            float: FieldType.NUMBER,
            Decimal: FieldType.NUMBER,
            bool: FieldType.CHECKBOX,
            date: FieldType.DATE,
            time: FieldType.TIME,
            datetime: FieldType.DATETIME,
        }
        
        # Check for direct type match
        if annotation in type_map:
            return type_map[annotation]
        
        # Check for List types (multiple checkbox)
        if origin is list:
            return FieldType.CHECKBOX
        
        # Check for Enum types (select dropdown)
        if inspect.isclass(annotation) and issubclass(annotation, Enum):
            return FieldType.SELECT
        
        # Default to text
        return FieldType.TEXT
    
    @staticmethod
    def extract_validation_rules(field_info: Any, field_name: str) -> List[ValidationRule]:
        """Extract validation rules from Pydantic field info"""
        rules = []
        
        if not PYDANTIC_AVAILABLE:
            return rules
        
        # Check if field is required
        if hasattr(field_info, 'is_required') and field_info.is_required():
            rules.append(ValidationRule("required", message=f"{field_name} is required"))
        elif hasattr(field_info, 'required') and field_info.required:
            rules.append(ValidationRule("required", message=f"{field_name} is required"))
        
        # Extract constraints from field_info
        if hasattr(field_info, 'constraints'):
            constraints = field_info.constraints
        elif hasattr(field_info, 'metadata'):
            # For Pydantic v2
            constraints = {}
            for item in field_info.metadata:
                if hasattr(item, '__dict__'):
                    constraints.update(item.__dict__)
        else:
            constraints = {}
        
        # Map Pydantic constraints to HTML validation
        if constraints:
            if 'min_length' in constraints:
                rules.append(ValidationRule("minlength", constraints['min_length']))
            if 'max_length' in constraints:
                rules.append(ValidationRule("maxlength", constraints['max_length']))
            if 'ge' in constraints:  # greater than or equal
                rules.append(ValidationRule("min", constraints['ge']))
            if 'le' in constraints:  # less than or equal
                rules.append(ValidationRule("max", constraints['le']))
            if 'gt' in constraints:  # greater than
                rules.append(ValidationRule("min", constraints['gt']))
            if 'lt' in constraints:  # less than
                rules.append(ValidationRule("max", constraints['lt']))
            if 'regex' in constraints:
                rules.append(ValidationRule("pattern", constraints['regex']))
        
        return rules
    
    @staticmethod
    def get_field_options_from_enum(enum_class: Type[Enum]) -> List[Dict[str, str]]:
        """Convert Enum to select options"""
        return [
            {"value": item.value, "label": item.name.replace('_', ' ').title()}
            for item in enum_class
        ]
    
    @staticmethod
    def model_to_form_fields(
        model: Type[BaseModel],
        exclude_fields: Optional[List[str]] = None,
        custom_labels: Optional[Dict[str, str]] = None,
        custom_help_text: Optional[Dict[str, str]] = None
    ) -> List[FormField]:
        """Convert a Pydantic model to a list of form fields"""
        if not PYDANTIC_AVAILABLE:
            raise RuntimeError("Pydantic is not installed. Install it with: pip install pydantic")
        
        fields = []
        exclude_fields = exclude_fields or []
        custom_labels = custom_labels or {}
        custom_help_text = custom_help_text or {}
        
        # Get model fields
        model_fields = model.model_fields if hasattr(model, 'model_fields') else model.__fields__
        
        for field_name, field_info in model_fields.items():
            if field_name in exclude_fields:
                continue
            
            # Get field type
            if hasattr(field_info, 'annotation'):
                field_type = field_info.annotation
            else:
                field_type = field_info.type_
            
            # Determine HTML field type
            html_field_type = PydanticFormConverter.get_field_type_from_annotation(field_type)
            
            # Create label
            label = custom_labels.get(field_name, field_name.replace('_', ' ').title())
            
            # Get field description/help text
            help_text = custom_help_text.get(field_name, "")
            if hasattr(field_info, 'description') and field_info.description:
                help_text = help_text or field_info.description
            
            # Get validation rules
            validation_rules = PydanticFormConverter.extract_validation_rules(field_info, field_name)
            
            # Handle special field types
            field_kwargs = {
                "name": field_name,
                "type": html_field_type,
                "label": label,
                "help_text": help_text,
                "validation_rules": validation_rules
            }
            
            # Add placeholder from field info if available
            if hasattr(field_info, 'metadata'):
                for meta in field_info.metadata:
                    if hasattr(meta, 'placeholder'):
                        field_kwargs["placeholder"] = meta.placeholder
            
            # Handle enum fields
            origin = get_origin(field_type)
            if origin is Union:
                args = get_args(field_type)
                non_none_args = [arg for arg in args if arg is not type(None)]
                if non_none_args and inspect.isclass(non_none_args[0]) and issubclass(non_none_args[0], Enum):
                    field_type = non_none_args[0]
            
            if inspect.isclass(field_type) and issubclass(field_type, Enum):
                field_kwargs["options"] = PydanticFormConverter.get_field_options_from_enum(field_type)
            
            # Handle List fields for multiple selection
            if origin is list:
                args = get_args(field_type)
                if args and inspect.isclass(args[0]) and issubclass(args[0], Enum):
                    field_kwargs["options"] = PydanticFormConverter.get_field_options_from_enum(args[0])
            
            # Handle email fields
            if field_name.lower() in ['email', 'email_address']:
                field_kwargs["type"] = FieldType.EMAIL
            
            # Handle password fields
            if 'password' in field_name.lower():
                field_kwargs["type"] = FieldType.PASSWORD
            
            # Handle URL fields
            if field_name.lower() in ['url', 'website', 'link']:
                field_kwargs["type"] = FieldType.URL
            
            # Handle phone fields
            if field_name.lower() in ['phone', 'telephone', 'mobile']:
                field_kwargs["type"] = FieldType.TEL
            
            # Create form field
            form_field = FormField(**field_kwargs)
            fields.append(form_field)
        
        return fields
    
    @staticmethod
    def create_wizard_from_models(
        models: Union[Type[BaseModel], List[Type[BaseModel]]],
        title: str,
        submit_url: str = "/api/submit",
        step_titles: Optional[List[str]] = None,
        step_descriptions: Optional[List[str]] = None,
        **kwargs
    ) -> FormWizard:
        """Create a form wizard from one or more Pydantic models"""
        if not isinstance(models, list):
            models = [models]
        
        steps = []
        for i, model in enumerate(models):
            # Generate form fields from model
            fields = PydanticFormConverter.model_to_form_fields(
                model,
                exclude_fields=kwargs.get(f'exclude_fields_{i}', kwargs.get('exclude_fields', [])),
                custom_labels=kwargs.get(f'custom_labels_{i}', kwargs.get('custom_labels', {})),
                custom_help_text=kwargs.get(f'custom_help_text_{i}', kwargs.get('custom_help_text', {}))
            )
            
            # Create step
            step_title = step_titles[i] if step_titles and i < len(step_titles) else f"Step {i + 1}"
            step_description = step_descriptions[i] if step_descriptions and i < len(step_descriptions) else ""
            
            step = FormStep(
                title=step_title,
                description=step_description,
                fields=fields
            )
            steps.append(step)
        
        # Create wizard
        wizard = FormWizard(
            title=title,
            steps=steps,
            submit_url=submit_url,
            method=kwargs.get('method', 'POST')
        )
        
        return wizard


# FastAPI Integration Helpers
def generate_form_endpoint(router, model: Type[BaseModel], path: str = "/form"):
    """
    Generate a FastAPI endpoint that returns the HTML form for a Pydantic model
    
    Usage:
        from fastapi import APIRouter
        router = APIRouter()
        
        class UserRequest(BaseModel):
            name: str
            email: str
            age: int
        
        generate_form_endpoint(router, UserRequest, "/user-form")
    """
    if not PYDANTIC_AVAILABLE:
        raise RuntimeError("Pydantic is required for FastAPI integration")
    
    from fastapi import Response
    
    @router.get(path, response_class=Response)
    async def get_form():
        wizard = PydanticFormConverter.create_wizard_from_models(
            model,
            title=f"{model.__name__} Form",
            submit_url=f"/api{path}",
            step_titles=[model.__name__]
        )
        html_content = wizard.generate_html()
        return Response(content=html_content, media_type="text/html")
    
    @router.post(f"/api{path}")
    async def submit_form(data: model):
        # Process the form data
        return {"status": "success", "data": data.model_dump()}
    
    return router


# Example Usage and Helper Functions

def create_user_registration_wizard():
    """Example: Create a user registration wizard"""
    
    # Step 1: Personal Information
    personal_fields = [
        FormField(
            name="first_name",
            type=FieldType.TEXT,
            label="First Name",
            placeholder="Enter your first name",
            validation_rules=[
                ValidationRule("required", message="First name is required"),
                ValidationRule("minlength", 2, "First name must be at least 2 characters")
            ]
        ),
        FormField(
            name="last_name",
            type=FieldType.TEXT,
            label="Last Name",
            placeholder="Enter your last name",
            validation_rules=[
                ValidationRule("required", message="Last name is required")
            ]
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email Address",
            placeholder="your@email.com",
            validation_rules=[
                ValidationRule("required", message="Email is required"),
                ValidationRule("pattern", r"[^@]+@[^@]+\.[^@]+", "Please enter a valid email")
            ]
        ),
        FormField(
            name="phone",
            type=FieldType.TEL,
            label="Phone Number",
            placeholder="+1 (555) 123-4567",
            help_text="We'll only use this for important account notifications"
        ),
        FormField(
            name="birth_date",
            type=FieldType.DATE,
            label="Date of Birth",
            validation_rules=[
                ValidationRule("required", message="Birth date is required")
            ]
        )
    ]
    
    # Step 2: Account Details
    account_fields = [
        FormField(
            name="username",
            type=FieldType.TEXT,
            label="Username",
            placeholder="Choose a username",
            validation_rules=[
                ValidationRule("required", message="Username is required"),
                ValidationRule("minlength", 4, "Username must be at least 4 characters"),
                ValidationRule("pattern", "^[a-zA-Z0-9_]+$", "Username can only contain letters, numbers, and underscores")
            ]
        ),
        FormField(
            name="password",
            type=FieldType.PASSWORD,
            label="Password",
            placeholder="Create a strong password",
            validation_rules=[
                ValidationRule("required", message="Password is required"),
                ValidationRule("minlength", 8, "Password must be at least 8 characters")
            ],
            help_text="Use at least 8 characters with a mix of letters, numbers, and symbols"
        ),
        FormField(
            name="confirm_password",
            type=FieldType.PASSWORD,
            label="Confirm Password",
            placeholder="Re-enter your password",
            validation_rules=[
                ValidationRule("required", message="Please confirm your password")
            ]
        )
    ]
    
    # Step 3: Preferences (with conditional fields)
    preferences_fields = [
        FormField(
            name="account_type",
            type=FieldType.RADIO,
            label="Account Type",
            options=[
                {"value": "personal", "label": "Personal Account"},
                {"value": "business", "label": "Business Account"},
                {"value": "developer", "label": "Developer Account"}
            ],
            validation_rules=[
                ValidationRule("required", message="Please select an account type")
            ]
        ),
        FormField(
            name="interests",
            type=FieldType.CHECKBOX,
            label="Areas of Interest",
            options=[
                {"value": "technology", "label": "Technology"},
                {"value": "design", "label": "Design"},
                {"value": "marketing", "label": "Marketing"},
                {"value": "data", "label": "Data Science"},
                {"value": "other", "label": "Other"}
            ]
        ),
        FormField(
            name="newsletter",
            type=FieldType.CHECKBOX,
            label="Subscribe to our newsletter",
            default_value=True
        ),
        FormField(
            name="notifications",
            type=FieldType.SELECT,
            label="Email Notification Preferences",
            placeholder="Select frequency",
            options=[
                {"value": "all", "label": "All notifications"},
                {"value": "important", "label": "Important only"},
                {"value": "weekly", "label": "Weekly digest"},
                {"value": "none", "label": "No emails"}
            ],
            default_value="important"
        )
    ]
    
    # Dynamic field generator for business accounts
    def generate_business_fields(form_data):
        if form_data.get("account_type") == "business":
            return [
                FormField(
                    name="company_name",
                    type=FieldType.TEXT,
                    label="Company Name",
                    placeholder="Enter your company name",
                    validation_rules=[
                        ValidationRule("required", message="Company name is required for business accounts")
                    ]
                ),
                FormField(
                    name="company_size",
                    type=FieldType.SELECT,
                    label="Company Size",
                    options=[
                        {"value": "1-10", "label": "1-10 employees"},
                        {"value": "11-50", "label": "11-50 employees"},
                        {"value": "51-200", "label": "51-200 employees"},
                        {"value": "201-500", "label": "201-500 employees"},
                        {"value": "500+", "label": "500+ employees"}
                    ]
                )
            ]
        return []
    
    # Create steps
    steps = [
        FormStep(
            title="Personal Information",
            description="Let's start with your basic information",
            fields=personal_fields
        ),
        FormStep(
            title="Account Setup",
            description="Create your account credentials",
            fields=account_fields
        ),
        FormStep(
            title="Preferences",
            description="Customize your experience",
            fields=preferences_fields,
            dynamic_fields_generator=generate_business_fields
        )
    ]
    
    # Create wizard
    wizard = FormWizard(
        title="User Registration",
        steps=steps,
        submit_url="/api/register",
        method="POST"
    )
    
    return wizard


def create_product_order_wizard():
    """Example: Create a product order wizard with dynamic pricing"""
    
    # Step 1: Product Selection
    product_fields = [
        FormField(
            name="product_category",
            type=FieldType.SELECT,
            label="Product Category",
            placeholder="Choose a category",
            options=[
                {"value": "electronics", "label": "Electronics"},
                {"value": "clothing", "label": "Clothing"},
                {"value": "books", "label": "Books"},
                {"value": "home", "label": "Home & Garden"}
            ],
            validation_rules=[
                ValidationRule("required", message="Please select a category")
            ]
        )
    ]
    
    # Dynamic product generator based on category
    def generate_product_fields(form_data):
        category = form_data.get("product_category")
        if category == "electronics":
            return [
                FormField(
                    name="product",
                    type=FieldType.RADIO,
                    label="Select Product",
                    options=[
                        {"value": "laptop", "label": "Laptop - $999"},
                        {"value": "phone", "label": "Smartphone - $599"},
                        {"value": "tablet", "label": "Tablet - $399"}
                    ],
                    validation_rules=[
                        ValidationRule("required", message="Please select a product")
                    ]
                )
            ]
        elif category == "clothing":
            return [
                FormField(
                    name="product",
                    type=FieldType.RADIO,
                    label="Select Product",
                    options=[
                        {"value": "shirt", "label": "T-Shirt - $29"},
                        {"value": "jeans", "label": "Jeans - $79"},
                        {"value": "jacket", "label": "Jacket - $149"}
                    ],
                    validation_rules=[
                        ValidationRule("required", message="Please select a product")
                    ]
                ),
                FormField(
                    name="size",
                    type=FieldType.SELECT,
                    label="Size",
                    options=[
                        {"value": "xs", "label": "XS"},
                        {"value": "s", "label": "S"},
                        {"value": "m", "label": "M"},
                        {"value": "l", "label": "L"},
                        {"value": "xl", "label": "XL"}
                    ],
                    validation_rules=[
                        ValidationRule("required", message="Please select a size")
                    ]
                )
            ]
        return []
    
    # Step 2: Customer Information
    customer_fields = [
        FormField(
            name="full_name",
            type=FieldType.TEXT,
            label="Full Name",
            validation_rules=[
                ValidationRule("required", message="Name is required")
            ]
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email",
            validation_rules=[
                ValidationRule("required", message="Email is required")
            ]
        ),
        FormField(
            name="shipping_address",
            type=FieldType.TEXTAREA,
            label="Shipping Address",
            placeholder="Enter your full address",
            validation_rules=[
                ValidationRule("required", message="Shipping address is required")
            ]
        )
    ]
    
    # Step 3: Payment
    payment_fields = [
        FormField(
            name="payment_method",
            type=FieldType.RADIO,
            label="Payment Method",
            options=[
                {"value": "credit", "label": "Credit Card"},
                {"value": "debit", "label": "Debit Card"},
                {"value": "paypal", "label": "PayPal"}
            ],
            validation_rules=[
                ValidationRule("required", message="Please select a payment method")
            ]
        )
    ]
    
    # Create steps
    steps = [
        FormStep(
            title="Product Selection",
            description="Choose your product",
            fields=product_fields,
            dynamic_fields_generator=generate_product_fields
        ),
        FormStep(
            title="Customer Information",
            description="Where should we send your order?",
            fields=customer_fields
        ),
        FormStep(
            title="Payment",
            description="Complete your purchase",
            fields=payment_fields
        )
    ]
    
    # Create wizard
    wizard = FormWizard(
        title="Product Order",
        steps=steps,
        submit_url="/api/order",
        method="POST"
    )
    
    return wizard


# FastAPI/Pydantic Integration Examples
def fastapi_examples():
    """Examples of using the Pydantic integration with FastAPI"""
    
    if not PYDANTIC_AVAILABLE:
        print("Please install pydantic to use FastAPI integration: pip install pydantic fastapi")
        return
    
    # Example 1: Simple Account Registration
    from pydantic import BaseModel, Field, EmailStr
    from typing import Optional
    from enum import Enum as PyEnum
    
    class AccountType(PyEnum):
        PERSONAL = "personal"
        BUSINESS = "business"
        ENTERPRISE = "enterprise"
    
    class AccountRequest(BaseModel):
        """Account registration request model"""
        username: str = Field(..., min_length=3, max_length=20, description="Unique username")
        email: EmailStr = Field(..., description="Valid email address")
        password: str = Field(..., min_length=8, description="Strong password")
        first_name: str = Field(..., description="Your first name")
        last_name: str = Field(..., description="Your last name")
        account_type: AccountType = Field(..., description="Type of account")
        age: int = Field(..., ge=18, le=120, description="Must be 18 or older")
        bio: Optional[str] = Field(None, max_length=500, description="Tell us about yourself")
        newsletter: bool = Field(True, description="Subscribe to newsletter")
    
    # Generate form from model
    print("=== Example 1: Simple Form from Pydantic Model ===")
    wizard = PydanticFormConverter.create_wizard_from_models(
        AccountRequest,
        title="Create Your Account",
        submit_url="/api/account/register",
        step_titles=["Account Information"],
        custom_labels={
            "email": "Email Address",
            "bio": "About You"
        }
    )
    
    # Save the form
    with open("account_form.html", "w") as f:
        f.write(wizard.generate_html())
    print("Account form saved to account_form.html")
    
    # Example 2: Multi-step Form with Multiple Models
    class PersonalInfo(BaseModel):
        first_name: str = Field(..., min_length=2)
        last_name: str = Field(..., min_length=2)
        date_of_birth: date = Field(...)
        phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    
    class AddressInfo(BaseModel):
        street_address: str = Field(...)
        city: str = Field(...)
        state: str = Field(..., max_length=2)
        zip_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$')
        country: str = Field(default="USA")
    
    class PaymentInfo(BaseModel):
        card_type: str = Field(..., description="Credit or Debit")
        card_number: str = Field(..., min_length=16, max_length=16)
        expiry_month: int = Field(..., ge=1, le=12)
        expiry_year: int = Field(..., ge=2024, le=2034)
        cvv: str = Field(..., min_length=3, max_length=4)
    
    print("\n=== Example 2: Multi-step Wizard from Multiple Models ===")
    multi_step_wizard = PydanticFormConverter.create_wizard_from_models(
        [PersonalInfo, AddressInfo, PaymentInfo],
        title="Complete Registration",
        submit_url="/api/complete-registration",
        step_titles=["Personal Information", "Address", "Payment Method"],
        step_descriptions=[
            "Let's start with your basic information",
            "Where should we send your order?",
            "Secure payment information"
        ]
    )
    
    with open("multi_step_form.html", "w") as f:
        f.write(multi_step_wizard.generate_html())
    print("Multi-step form saved to multi_step_form.html")
    
    # Example 3: FastAPI Router Integration
    print("\n=== Example 3: FastAPI Router Integration ===")
    print("""
    # In your FastAPI app:
    from fastapi import FastAPI, APIRouter
    from html import generate_form_endpoint, AccountRequest
    
    app = FastAPI()
    router = APIRouter()
    
    # This automatically creates both GET (form) and POST (submit) endpoints
    generate_form_endpoint(router, AccountRequest, "/account-form")
    
    app.include_router(router)
    
    # Now you can:
    # GET  /account-form     -> Returns the HTML form
    # POST /api/account-form -> Handles form submission
    """)
    
    # Example 4: Dynamic form based on user choices
    print("\n=== Example 4: Custom Dynamic Form Generation ===")
    
    class BaseProduct(BaseModel):
        product_type: str = Field(..., description="Type of product")
        quantity: int = Field(..., ge=1, le=100)
    
    class ElectronicsDetails(BaseModel):
        warranty_years: int = Field(1, ge=0, le=5)
        color: str = Field(...)
        model: str = Field(...)
    
    class ClothingDetails(BaseModel):
        size: str = Field(...)
        material: str = Field(...)
        care_instructions: Optional[str] = Field(None)
    
    # Create a dynamic form that changes based on product type
    def create_dynamic_product_form():
        # Base step
        base_fields = PydanticFormConverter.model_to_form_fields(BaseProduct)
        
        # Modify product_type to be a select field
        for field in base_fields:
            if field.name == "product_type":
                field.type = FieldType.SELECT
                field.options = [
                    {"value": "electronics", "label": "Electronics"},
                    {"value": "clothing", "label": "Clothing"},
                    {"value": "books", "label": "Books"}
                ]
        
        # Dynamic field generator
        def generate_product_details(form_data):
            product_type = form_data.get("product_type")
            if product_type == "electronics":
                return PydanticFormConverter.model_to_form_fields(ElectronicsDetails)
            elif product_type == "clothing":
                return PydanticFormConverter.model_to_form_fields(ClothingDetails)
            return []
        
        steps = [
            FormStep(
                title="Select Product",
                description="Choose your product type and quantity",
                fields=base_fields
            ),
            FormStep(
                title="Product Details",
                description="Provide specific details for your product",
                fields=[],  # Will be populated dynamically
                dynamic_fields_generator=generate_product_details
            )
        ]
        
        wizard = FormWizard(
            title="Product Order Form",
            steps=steps,
            submit_url="/api/product/order"
        )
        
        return wizard
    
    dynamic_wizard = create_dynamic_product_form()
    with open("dynamic_product_form.html", "w") as f:
        f.write(dynamic_wizard.generate_html())
    print("Dynamic product form saved to dynamic_product_form.html")


# Main execution
if __name__ == "__main__":
    # Run original examples
    print("=== Original Examples ===")
    
    # Example 1: User Registration Wizard
    registration_wizard = create_user_registration_wizard()
    with open("registration_form.html", "w") as f:
        f.write(registration_wizard.generate_html())
    print("Registration form saved to registration_form.html")
    
    # Example 2: Product Order Wizard
    order_wizard = create_product_order_wizard()
    with open("order_form.html", "w") as f:
        f.write(order_wizard.generate_html())
    print("Order form saved to order_form.html")
    
    # Run FastAPI/Pydantic examples
    print("\n" + "="*50 + "\n")
    fastapi_examples()
    
    print("\n=== Summary ===")
    print("The html.py module now supports:")
    print("1. Manual form creation (original functionality)")
    print("2. Automatic form generation from Pydantic models")
    print("3. FastAPI endpoint generation")
    print("4. Dynamic forms based on user input")
    print("5. Multi-step wizards from multiple models")
    print("\nAll forms include validation, progress tracking, and local storage!")