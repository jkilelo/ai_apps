#!/usr/bin/env python3
"""
Practical Implementation of Key Enhancements for html.py

This shows how to integrate the most valuable improvements into your existing code.
"""

import secrets
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import re

# Import the original classes (you would merge this into html.py)
# from html import FormField, FormStep, FormWizard, FieldType

# Enhancement 1: Add Security to FormWizard
class SecureFormWizard:
    """FormWizard with built-in security features"""
    
    def __init__(self, title: str, steps: List[Any], submit_url: str = "#", method: str = "POST"):
        # Original init code...
        self.title = title
        self.steps = steps
        self.submit_url = submit_url
        self.method = method
        
        # New security features
        self.csrf_token = secrets.token_urlsafe(32)
        self.enable_csrf = True
        self.sanitize_inputs = True
        self.max_file_size = 5 * 1024 * 1024  # 5MB default
    
    def _generate_security_js(self) -> str:
        """Generate JavaScript for security features"""
        return f"""
        // Security Features
        const securityConfig = {{
            csrfToken: '{self.csrf_token}',
            maxFileSize: {self.max_file_size},
            
            // XSS Protection
            sanitizeInput: function(value) {{
                const div = document.createElement('div');
                div.textContent = value;
                return div.innerHTML;
            }},
            
            // CSRF Protection
            addCsrfToken: function(formData) {{
                formData.append('csrf_token', this.csrfToken);
                return formData;
            }},
            
            // File validation
            validateFile: function(file) {{
                if (file.size > this.maxFileSize) {{
                    alert('File too large. Maximum size: ' + (this.maxFileSize / 1024 / 1024) + 'MB');
                    return false;
                }}
                return true;
            }}
        }};
        """


# Enhancement 2: Advanced Field Types with Practical Implementation
@dataclass
class EnhancedFormField:
    """Form field with advanced features that are easy to implement"""
    
    # Original fields
    name: str
    type: str  # Now supports advanced types
    label: str
    placeholder: str = ""
    default_value: Any = None
    options: List[Dict[str, str]] = field(default_factory=list)
    validation_rules: List[Any] = field(default_factory=list)
    
    # New practical features
    autocomplete_url: Optional[str] = None  # API endpoint for autocomplete
    real_time_validate: bool = False  # Enable real-time validation
    debounce_ms: int = 500  # Delay for real-time validation
    max_file_size: Optional[int] = None  # For file uploads
    accepted_files: Optional[List[str]] = None  # ['.pdf', '.doc']
    
    def render_advanced(self, step_index: int) -> str:
        """Render field with advanced features"""
        field_id = f"{self.name}_step{step_index}"
        
        # Special rendering for advanced types
        if self.type == "tags":
            return self._render_tags_input(field_id)
        elif self.type == "autocomplete":
            return self._render_autocomplete(field_id)
        elif self.type == "file-drag":
            return self._render_drag_drop(field_id)
        else:
            # Fallback to original render method
            return self.render(step_index)
    
    def _render_tags_input(self, field_id: str) -> str:
        """Render a tags input field"""
        return f"""
        <div class="form-field tags-field" data-field-name="{self.name}">
            <label for="{field_id}">{self.label}</label>
            <div class="tags-container" id="{field_id}_container">
                <input type="text" 
                       id="{field_id}" 
                       class="tags-input" 
                       placeholder="Type and press Enter"
                       data-name="{self.name}">
            </div>
            <div class="validation-message"></div>
            <script>
                // Simple tags implementation
                (function() {{
                    const input = document.getElementById('{field_id}');
                    const container = document.getElementById('{field_id}_container');
                    const tags = [];
                    
                    input.addEventListener('keydown', function(e) {{
                        if (e.key === 'Enter' && this.value) {{
                            e.preventDefault();
                            const tag = document.createElement('span');
                            tag.className = 'tag';
                            tag.innerHTML = `${{this.value}} <button onclick="this.parentElement.remove()">×</button>`;
                            container.insertBefore(tag, input);
                            tags.push(this.value);
                            this.value = '';
                            
                            // Store in form data
                            formData['{self.name}'] = tags;
                        }}
                    }});
                }})();
            </script>
        </div>
        """
    
    def _render_autocomplete(self, field_id: str) -> str:
        """Render autocomplete field"""
        return f"""
        <div class="form-field autocomplete-field" data-field-name="{self.name}">
            <label for="{field_id}">{self.label}</label>
            <input type="text" 
                   id="{field_id}" 
                   name="{self.name}"
                   placeholder="{self.placeholder}"
                   autocomplete="off">
            <div id="{field_id}_suggestions" class="autocomplete-suggestions"></div>
            <div class="validation-message"></div>
            <script>
                // Autocomplete implementation
                (function() {{
                    const input = document.getElementById('{field_id}');
                    const suggestions = document.getElementById('{field_id}_suggestions');
                    let timeout;
                    
                    input.addEventListener('input', function() {{
                        clearTimeout(timeout);
                        const value = this.value;
                        
                        if (value.length < 2) {{
                            suggestions.style.display = 'none';
                            return;
                        }}
                        
                        timeout = setTimeout(async () => {{
                            const response = await fetch('{self.autocomplete_url}?q=' + value);
                            const data = await response.json();
                            
                            suggestions.innerHTML = '';
                            data.forEach(item => {{
                                const div = document.createElement('div');
                                div.className = 'suggestion-item';
                                div.textContent = item;
                                div.onclick = function() {{
                                    input.value = item;
                                    suggestions.style.display = 'none';
                                    formData['{self.name}'] = item;
                                }};
                                suggestions.appendChild(div);
                            }});
                            suggestions.style.display = 'block';
                        }}, {self.debounce_ms});
                    }});
                }})();
            </script>
        </div>
        """
    
    def _render_drag_drop(self, field_id: str) -> str:
        """Render drag and drop file upload"""
        accept = ','.join(self.accepted_files) if self.accepted_files else ''
        return f"""
        <div class="form-field file-drop-field" data-field-name="{self.name}">
            <label>{self.label}</label>
            <div id="{field_id}_dropzone" class="dropzone">
                <div class="dropzone-content">
                    <svg class="upload-icon" width="50" height="50" fill="currentColor">
                        <path d="M25 5 L25 35 M15 25 L25 15 L35 25"/>
                    </svg>
                    <p>Drag files here or click to browse</p>
                    <input type="file" 
                           id="{field_id}" 
                           name="{self.name}"
                           accept="{accept}"
                           multiple
                           style="display: none;">
                </div>
                <div id="{field_id}_files" class="uploaded-files"></div>
            </div>
            <div class="validation-message"></div>
            <script>
                // Drag and drop implementation
                (function() {{
                    const dropzone = document.getElementById('{field_id}_dropzone');
                    const input = document.getElementById('{field_id}');
                    const filesList = document.getElementById('{field_id}_files');
                    const uploadedFiles = [];
                    
                    dropzone.onclick = () => input.click();
                    
                    dropzone.ondragover = (e) => {{
                        e.preventDefault();
                        dropzone.classList.add('dragover');
                    }};
                    
                    dropzone.ondragleave = () => {{
                        dropzone.classList.remove('dragover');
                    }};
                    
                    dropzone.ondrop = (e) => {{
                        e.preventDefault();
                        dropzone.classList.remove('dragover');
                        handleFiles(e.dataTransfer.files);
                    }};
                    
                    input.onchange = (e) => {{
                        handleFiles(e.target.files);
                    }};
                    
                    function handleFiles(files) {{
                        Array.from(files).forEach(file => {{
                            if (securityConfig.validateFile(file)) {{
                                uploadedFiles.push(file);
                                displayFile(file);
                            }}
                        }});
                        formData['{self.name}'] = uploadedFiles;
                    }}
                    
                    function displayFile(file) {{
                        const div = document.createElement('div');
                        div.className = 'file-item';
                        div.innerHTML = `
                            <span>${{file.name}} (${{(file.size / 1024).toFixed(1)}}KB)</span>
                            <button onclick="removeFile(this, '${{file.name}}')">×</button>
                        `;
                        filesList.appendChild(div);
                    }}
                }})();
            </script>
        </div>
        """


# Enhancement 3: Real-time Validation
class RealTimeValidation:
    """Add real-time validation to forms"""
    
    @staticmethod
    def generate_validation_script() -> str:
        """Generate comprehensive validation JavaScript"""
        return """
        // Real-time Validation System
        class FormValidator {
            constructor() {
                this.errors = {};
                this.validationRules = {
                    email: /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/,
                    phone: /^[\\+]?[(]?[0-9]{3}[)]?[-\\s\\.]?[0-9]{3}[-\\s\\.]?[0-9]{4,6}$/,
                    url: /^(https?:\\/\\/)?([\\da-z\\.-]+)\\.([a-z\\.]{2,6})([\\/\\w \\.-]*)*\\/?$/,
                    zipcode: /^\\d{5}(-\\d{4})?$/
                };
                
                this.initializeValidation();
            }
            
            initializeValidation() {
                document.querySelectorAll('input, select, textarea').forEach(field => {
                    // Debounced validation
                    let timeout;
                    field.addEventListener('input', (e) => {
                        clearTimeout(timeout);
                        timeout = setTimeout(() => this.validateField(e.target), 500);
                    });
                    
                    // Immediate validation on blur
                    field.addEventListener('blur', (e) => {
                        this.validateField(e.target);
                    });
                });
            }
            
            async validateField(field) {
                const fieldContainer = field.closest('.form-field');
                const errorDiv = fieldContainer.querySelector('.validation-message');
                
                // Reset state
                field.classList.remove('is-valid', 'is-invalid');
                errorDiv.textContent = '';
                errorDiv.classList.remove('show');
                
                // Check if empty and required
                if (field.hasAttribute('required') && !field.value.trim()) {
                    this.showError(field, 'This field is required');
                    return false;
                }
                
                // Type-specific validation
                if (field.type === 'email' && field.value) {
                    if (!this.validationRules.email.test(field.value)) {
                        this.showError(field, 'Please enter a valid email address');
                        return false;
                    }
                }
                
                // Custom async validation
                if (field.dataset.validateUrl) {
                    try {
                        const response = await fetch(field.dataset.validateUrl, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                field: field.name,
                                value: field.value
                            })
                        });
                        
                        const result = await response.json();
                        if (!result.valid) {
                            this.showError(field, result.message);
                            return false;
                        }
                    } catch (error) {
                        console.error('Validation error:', error);
                    }
                }
                
                // All good
                this.showSuccess(field);
                return true;
            }
            
            showError(field, message) {
                field.classList.add('is-invalid');
                const errorDiv = field.closest('.form-field').querySelector('.validation-message');
                errorDiv.textContent = message;
                errorDiv.classList.add('show');
                this.errors[field.name] = message;
            }
            
            showSuccess(field) {
                field.classList.add('is-valid');
                delete this.errors[field.name];
            }
            
            hasErrors() {
                return Object.keys(this.errors).length > 0;
            }
        }
        
        // Initialize validator
        const formValidator = new FormValidator();
        """


# Enhancement 4: Form Analytics Integration
def generate_analytics_script(form_id: str) -> str:
    """Generate analytics tracking script"""
    return f"""
    // Form Analytics
    class FormAnalytics {{
        constructor(formId) {{
            this.formId = formId;
            this.startTime = Date.now();
            this.interactions = {{}};
            this.abandonments = [];
            
            this.trackFormStart();
            this.setupTracking();
        }}
        
        trackFormStart() {{
            this.send('form_start', {{
                formId: this.formId,
                timestamp: this.startTime,
                referrer: document.referrer
            }});
        }}
        
        setupTracking() {{
            // Track field interactions
            document.querySelectorAll('.form-field input, .form-field select, .form-field textarea').forEach(field => {{
                field.addEventListener('focus', () => {{
                    if (!this.interactions[field.name]) {{
                        this.interactions[field.name] = {{
                            firstInteraction: Date.now(),
                            interactionCount: 0,
                            timeSpent: 0
                        }};
                    }}
                    this.interactions[field.name].lastFocus = Date.now();
                }});
                
                field.addEventListener('blur', () => {{
                    if (this.interactions[field.name] && this.interactions[field.name].lastFocus) {{
                        const timeSpent = Date.now() - this.interactions[field.name].lastFocus;
                        this.interactions[field.name].timeSpent += timeSpent;
                        this.interactions[field.name].interactionCount++;
                    }}
                }});
            }});
            
            // Track form abandonment
            window.addEventListener('beforeunload', () => {{
                if (!this.formCompleted) {{
                    this.send('form_abandoned', {{
                        formId: this.formId,
                        currentStep: currentStep,
                        timeSpent: Date.now() - this.startTime,
                        interactions: this.interactions
                    }});
                }}
            }});
        }}
        
        trackStepChange(fromStep, toStep) {{
            this.send('step_change', {{
                formId: this.formId,
                fromStep: fromStep,
                toStep: toStep,
                timestamp: Date.now()
            }});
        }}
        
        trackFormComplete() {{
            this.formCompleted = true;
            this.send('form_complete', {{
                formId: this.formId,
                totalTime: Date.now() - this.startTime,
                interactions: this.interactions
            }});
        }}
        
        send(event, data) {{
            // Send to your analytics endpoint
            if (window.analyticsEndpoint) {{
                fetch(window.analyticsEndpoint, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{event, data}})
                }}).catch(console.error);
            }}
            
            // Also send to Google Analytics if available
            if (typeof gtag !== 'undefined') {{
                gtag('event', event, data);
            }}
        }}
    }}
    
    // Initialize analytics
    const formAnalytics = new FormAnalytics('{form_id}');
    """


# Enhancement 5: Enhanced CSS with Modern Styling
def generate_enhanced_styles() -> str:
    """Generate enhanced CSS with modern features"""
    return """
    <style>
        /* Enhanced styles with CSS variables for theming */
        :root {
            --primary-color: #2196F3;
            --success-color: #4CAF50;
            --error-color: #f44336;
            --warning-color: #ff9800;
            --text-color: #333;
            --border-color: #ddd;
            --background-color: #fff;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 8px 16px rgba(0,0,0,0.1);
            --transition-speed: 0.3s;
        }
        
        /* Dark theme */
        [data-theme="dark"] {
            --text-color: #fff;
            --background-color: #1a1a1a;
            --border-color: #444;
        }
        
        /* Validation states */
        .form-field input.is-valid,
        .form-field select.is-valid,
        .form-field textarea.is-valid {
            border-color: var(--success-color);
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%234CAF50'%3E%3Cpath d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 20px;
            padding-right: 40px;
        }
        
        .form-field input.is-invalid,
        .form-field select.is-invalid,
        .form-field textarea.is-invalid {
            border-color: var(--error-color);
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23f44336'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 20px;
            padding-right: 40px;
        }
        
        /* Tags input */
        .tags-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 8px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            min-height: 42px;
        }
        
        .tag {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;
            background: var(--primary-color);
            color: white;
            border-radius: 16px;
            font-size: 14px;
        }
        
        .tag button {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
            line-height: 1;
            padding: 0;
        }
        
        .tags-input {
            flex: 1;
            border: none;
            outline: none;
            min-width: 150px;
        }
        
        /* Autocomplete */
        .autocomplete-field {
            position: relative;
        }
        
        .autocomplete-suggestions {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid var(--border-color);
            border-top: none;
            max-height: 200px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
            box-shadow: var(--shadow-md);
        }
        
        .suggestion-item {
            padding: 10px;
            cursor: pointer;
            transition: background-color var(--transition-speed);
        }
        
        .suggestion-item:hover {
            background-color: #f5f5f5;
        }
        
        /* Drag and drop */
        .dropzone {
            border: 2px dashed var(--border-color);
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all var(--transition-speed);
        }
        
        .dropzone:hover,
        .dropzone.dragover {
            border-color: var(--primary-color);
            background-color: rgba(33, 150, 243, 0.05);
        }
        
        .upload-icon {
            color: #999;
            margin-bottom: 10px;
        }
        
        .uploaded-files {
            margin-top: 20px;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        
        .file-item button {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: #999;
        }
        
        /* Loading states */
        .loading {
            position: relative;
            pointer-events: none;
            opacity: 0.6;
        }
        
        .loading::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            margin: -10px 0 0 -10px;
            border: 2px solid var(--primary-color);
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Accessibility improvements */
        .form-field:focus-within label {
            color: var(--primary-color);
        }
        
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0,0,0,0);
            white-space: nowrap;
            border: 0;
        }
        
        /* Print styles */
        @media print {
            .form-navigation,
            .progress-container {
                display: none;
            }
            
            .form-step {
                display: block !important;
                page-break-inside: avoid;
            }
        }
    </style>
    """


# Example: Putting it all together
def create_enhanced_form_example():
    """Example of creating a form with all enhancements"""
    
    # Import the enhanced classes
    from html import FormStep
    
    # Create enhanced fields
    fields = [
        EnhancedFormField(
            name="email",
            type="email",
            label="Email Address",
            placeholder="your@email.com",
            real_time_validate=True,
            validation_rules=[
                {"type": "required", "message": "Email is required"},
                {"type": "email", "message": "Enter a valid email"}
            ]
        ),
        EnhancedFormField(
            name="skills",
            type="tags",
            label="Your Skills",
            placeholder="Add your skills"
        ),
        EnhancedFormField(
            name="company",
            type="autocomplete",
            label="Company",
            placeholder="Start typing to search...",
            autocomplete_url="/api/companies/search"
        ),
        EnhancedFormField(
            name="resume",
            type="file-drag",
            label="Upload Resume",
            accepted_files=[".pdf", ".doc", ".docx"],
            max_file_size=5 * 1024 * 1024  # 5MB
        )
    ]
    
    # Create form step
    step = FormStep(
        title="Enhanced Application Form",
        description="Experience the power of enhanced form fields",
        fields=fields
    )
    
    # Create secure wizard with analytics
    wizard = SecureFormWizard(
        title="Job Application",
        steps=[step],
        submit_url="/api/apply"
    )
    
    # Generate complete HTML with all enhancements
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{wizard.title}</title>
        {generate_enhanced_styles()}
    </head>
    <body>
        <div class="form-wizard-container">
            <form id="wizardForm" data-form-id="{wizard.csrf_token[:8]}">
                <input type="hidden" name="csrf_token" value="{wizard.csrf_token}">
                <!-- Form content here -->
            </form>
        </div>
        
        <script>
            {wizard._generate_security_js()}
            {RealTimeValidation.generate_validation_script()}
            {generate_analytics_script(wizard.csrf_token[:8])}
        </script>
    </body>
    </html>
    """
    
    return html


if __name__ == "__main__":
    print("Enhanced Form Implementation Guide")
    print("=================================")
    print("\nKey enhancements implemented:")
    print("1. ✅ CSRF protection with secure tokens")
    print("2. ✅ Advanced field types (tags, autocomplete, drag-drop)")
    print("3. ✅ Real-time validation with debouncing")
    print("4. ✅ Form analytics tracking")
    print("5. ✅ Modern CSS with validation states")
    print("6. ✅ Accessibility improvements")
    print("7. ✅ File upload with validation")
    print("8. ✅ Print-friendly styles")
    print("\nThese enhancements can be easily integrated into your existing html.py!")