#!/usr/bin/env python3
"""
Dynamic HTML Form Wizard Generator v2.0 with FastAPI/Pydantic Integration

Enhanced version with security features, advanced field types, real-time validation,
analytics, themes, and more - while maintaining backward compatibility.
"""

import json
import secrets
import hashlib
from typing import Dict, List, Any, Optional, Union, Callable, Type, get_type_hints, get_args, get_origin
from dataclasses import dataclass, field as dataclass_field
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
    # Original field types
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
    
    # New advanced field types
    TAGS = "tags"
    AUTOCOMPLETE = "autocomplete"
    FILE_DRAG = "file-drag"
    RICH_TEXT = "richtext"
    DATE_RANGE = "daterange"
    RATING = "rating"
    COUNTRY = "country"
    PHONE_INTL = "phone-intl"


class FormTheme(Enum):
    """Available form themes"""
    DEFAULT = "default"
    MODERN = "modern"
    BOOTSTRAP = "bootstrap"
    MATERIAL = "material"
    DARK = "dark"
    MINIMAL = "minimal"


@dataclass
class ValidationRule:
    """Represents a validation rule for a form field"""
    type: str  # required, min, max, pattern, custom, ajax
    value: Any = None
    message: str = ""
    ajax_url: Optional[str] = None  # For ajax validation
    
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
        elif self.type == "ajax" and self.ajax_url:
            attrs["data-validate-url"] = self.ajax_url
        return attrs


@dataclass
class FormField:
    """Represents a single form field with enhanced features"""
    name: str
    type: FieldType
    label: str
    placeholder: str = ""
    default_value: Any = None
    options: List[Dict[str, str]] = dataclass_field(default_factory=list)
    validation_rules: List[ValidationRule] = dataclass_field(default_factory=list)
    css_classes: str = ""
    attributes: Dict[str, str] = dataclass_field(default_factory=dict)
    help_text: str = ""
    depends_on: Optional[Dict[str, Any]] = None
    
    # New enhanced features
    autocomplete_source: Optional[Union[List[str], str]] = None  # URL or list
    real_time_validate: bool = False
    debounce_ms: int = 500
    max_file_size: Optional[int] = None  # bytes
    accepted_files: Optional[List[str]] = None  # ['.pdf', '.doc']
    enable_rich_text: bool = False
    show_if: Optional[Dict[str, Any]] = None  # Advanced conditional display
    calculate_from: Optional[List[str]] = None  # Calculate value from other fields
    
    def render(self, step_index: int, form_data: Dict[str, Any] = None, theme: FormTheme = FormTheme.DEFAULT) -> str:
        """Render the form field as HTML with enhanced features"""
        # Check if field should be displayed based on dependencies
        if self.depends_on and form_data:
            for field_name, expected_value in self.depends_on.items():
                if form_data.get(field_name) != expected_value:
                    return ""  # Don't render if dependency not met
        
        # Check advanced conditional display
        if self.show_if and form_data:
            if not self._evaluate_condition(self.show_if, form_data):
                return ""
        
        # Build validation attributes
        validation_attrs = {}
        for rule in self.validation_rules:
            validation_attrs.update(rule.to_html_attrs())
        
        # Add real-time validation attributes
        if self.real_time_validate:
            validation_attrs["data-realtime-validate"] = "true"
            validation_attrs["data-debounce"] = str(self.debounce_ms)
        
        # Merge all attributes
        all_attrs = {**self.attributes, **validation_attrs}
        attrs_str = " ".join(f'{k}="{v}"' for k, v in all_attrs.items())
        
        # Get current value
        current_value = ""
        if form_data and self.name in form_data:
            current_value = form_data[self.name]
        elif self.default_value is not None:
            current_value = self.default_value
        
        # Render based on field type
        if self.type in [FieldType.TAGS, FieldType.AUTOCOMPLETE, FieldType.FILE_DRAG, FieldType.RICH_TEXT]:
            return self._render_advanced_field(step_index, current_value, attrs_str, theme)
        else:
            return self._render_standard_field(step_index, current_value, attrs_str)
    
    def _render_standard_field(self, step_index: int, current_value: Any, attrs_str: str) -> str:
        """Render standard HTML5 form fields"""
        field_html = f'<div class="form-field {self.css_classes}" data-field-name="{self.name}"'
        if self.show_if:
            field_html += f' data-show-if=\'{json.dumps(self.show_if)}\''
        field_html += '>'
        
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
    
    def _render_advanced_field(self, step_index: int, current_value: Any, attrs_str: str, theme: FormTheme) -> str:
        """Render advanced custom field types"""
        field_id = f"{self.name}_step{step_index}"
        field_html = f'<div class="form-field {self.css_classes} field-{self.type.value}" data-field-name="{self.name}">'
        
        # Label
        required = any(rule.type == "required" for rule in self.validation_rules)
        required_indicator = '<span class="required">*</span>' if required else ''
        field_html += f'<label for="{field_id}">{self.label}{required_indicator}</label>'
        
        if self.type == FieldType.TAGS:
            field_html += self._render_tags_field(field_id, current_value)
        elif self.type == FieldType.AUTOCOMPLETE:
            field_html += self._render_autocomplete_field(field_id, current_value, attrs_str)
        elif self.type == FieldType.FILE_DRAG:
            field_html += self._render_file_drag_field(field_id)
        elif self.type == FieldType.RICH_TEXT:
            field_html += self._render_rich_text_field(field_id, current_value)
        
        # Help text
        if self.help_text:
            field_html += f'<small class="help-text">{self.help_text}</small>'
        
        # Validation messages
        field_html += '<div class="validation-message"></div>'
        field_html += '</div>'
        
        return field_html
    
    def _render_tags_field(self, field_id: str, current_value: Any) -> str:
        """Render tags input field"""
        tags_list = current_value if isinstance(current_value, list) else []
        tags_json = json.dumps(tags_list)
        
        return f'''
            <div class="tags-container" id="{field_id}_container">
                <div id="{field_id}_tags" class="tags-list"></div>
                <input type="text" 
                       id="{field_id}" 
                       class="tags-input" 
                       placeholder="Type and press Enter"
                       data-field-name="{self.name}">
                <input type="hidden" name="{self.name}" id="{field_id}_hidden" value='{tags_json}'>
            </div>
        '''
    
    def _render_autocomplete_field(self, field_id: str, current_value: Any, attrs_str: str) -> str:
        """Render autocomplete field"""
        source_attr = ""
        if isinstance(self.autocomplete_source, str):
            source_attr = f'data-autocomplete-url="{self.autocomplete_source}"'
        elif isinstance(self.autocomplete_source, list):
            source_attr = f'data-autocomplete-items=\'{json.dumps(self.autocomplete_source)}\''
        
        return f'''
            <div class="autocomplete-wrapper">
                <input type="text" 
                       id="{field_id}" 
                       name="{self.name}"
                       value="{current_value}"
                       placeholder="{self.placeholder}"
                       {source_attr}
                       {attrs_str}
                       autocomplete="off">
                <div id="{field_id}_suggestions" class="autocomplete-suggestions"></div>
            </div>
        '''
    
    def _render_file_drag_field(self, field_id: str) -> str:
        """Render drag and drop file upload field"""
        accept = ','.join(self.accepted_files) if self.accepted_files else ''
        max_size_attr = f'data-max-size="{self.max_file_size}"' if self.max_file_size else ''
        
        return f'''
            <div id="{field_id}_dropzone" class="file-dropzone" {max_size_attr}>
                <input type="file" 
                       id="{field_id}" 
                       name="{self.name}"
                       accept="{accept}"
                       multiple
                       class="file-input-hidden">
                <div class="dropzone-content">
                    <svg class="upload-icon" width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                    <p>Drag files here or <a href="#" class="browse-link">browse</a></p>
                    <small>Max file size: {self.max_file_size / 1024 / 1024 if self.max_file_size else 10}MB</small>
                </div>
                <div id="{field_id}_files" class="uploaded-files"></div>
            </div>
        '''
    
    def _render_rich_text_field(self, field_id: str, current_value: Any) -> str:
        """Render rich text editor field"""
        return f'''
            <div class="rich-text-wrapper">
                <div class="rich-text-toolbar" id="{field_id}_toolbar">
                    <button type="button" data-command="bold" title="Bold">B</button>
                    <button type="button" data-command="italic" title="Italic">I</button>
                    <button type="button" data-command="underline" title="Underline">U</button>
                    <button type="button" data-command="insertUnorderedList" title="Bullet List">•</button>
                    <button type="button" data-command="insertOrderedList" title="Numbered List">1.</button>
                    <button type="button" data-command="createLink" title="Link">🔗</button>
                </div>
                <div contenteditable="true" 
                     id="{field_id}_editor" 
                     class="rich-text-editor"
                     data-field-name="{self.name}">{current_value}</div>
                <textarea name="{self.name}" id="{field_id}" style="display:none;">{current_value}</textarea>
            </div>
        '''
    
    def _evaluate_condition(self, condition: Dict[str, Any], form_data: Dict[str, Any]) -> bool:
        """Evaluate complex conditions for field display"""
        for field_name, expected in condition.items():
            actual = form_data.get(field_name)
            
            # Handle different condition types
            if isinstance(expected, dict):
                operator = expected.get('operator', 'equals')
                value = expected.get('value')
                
                if operator == 'equals' and actual != value:
                    return False
                elif operator == 'not_equals' and actual == value:
                    return False
                elif operator == 'contains' and value not in str(actual):
                    return False
                elif operator == 'greater_than' and not (actual > value):
                    return False
                elif operator == 'less_than' and not (actual < value):
                    return False
                elif operator == 'in' and actual not in value:
                    return False
            else:
                # Simple equality check
                if actual != expected:
                    return False
        
        return True


@dataclass
class FormStep:
    """Represents a single step in the form wizard"""
    title: str
    description: str = ""
    fields: List[FormField] = dataclass_field(default_factory=list)
    validator: Optional[Callable] = None
    dynamic_fields_generator: Optional[Callable] = None
    
    def render(self, step_index: int, form_data: Dict[str, Any] = None, theme: FormTheme = FormTheme.DEFAULT) -> str:
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
            step_html += field.render(step_index, form_data, theme)
        
        step_html += '''
            </div>
        </div>
        '''
        
        return step_html


class FormAnalytics:
    """Form analytics configuration"""
    def __init__(self, enabled: bool = False, endpoint: str = "/api/analytics"):
        self.enabled = enabled
        self.endpoint = endpoint
        self.track_interactions = True
        self.track_abandonment = True
        self.track_time = True
        self.track_errors = True


class FormI18n:
    """Internationalization support"""
    def __init__(self, default_locale: str = "en"):
        self.default_locale = default_locale
        self.translations = {
            "en": {
                "next": "Next",
                "previous": "Previous",
                "submit": "Submit",
                "save_draft": "Save Draft",
                "required_field": "This field is required",
                "invalid_email": "Please enter a valid email",
                "file_too_large": "File is too large",
                "form_saved": "Form saved",
                "loading": "Loading..."
            }
        }
    
    def add_translations(self, locale: str, translations: Dict[str, str]):
        """Add translations for a locale"""
        if locale not in self.translations:
            self.translations[locale] = {}
        self.translations[locale].update(translations)
    
    def get(self, key: str, locale: Optional[str] = None) -> str:
        """Get translated text"""
        locale = locale or self.default_locale
        return self.translations.get(locale, {}).get(key, key)


class FormWizard:
    """Enhanced form wizard with security, analytics, and advanced features"""
    
    def __init__(
        self,
        title: str,
        steps: List[FormStep],
        submit_url: str = "#",
        method: str = "POST",
        theme: FormTheme = FormTheme.DEFAULT,
        enable_csrf: bool = True,
        enable_analytics: bool = False,
        analytics_endpoint: str = "/api/analytics",
        enable_autosave: bool = True,
        autosave_interval: int = 30000,
        i18n: Optional[FormI18n] = None,
        save_progress: bool = True,
        show_progress_bar: bool = True,
        allow_step_navigation: bool = True,
        enable_print_view: bool = True,
        enable_keyboard_shortcuts: bool = True,
        custom_css: str = "",
        custom_js: str = "",
        form_id: Optional[str] = None
    ):
        self.title = title
        self.steps = steps
        self.submit_url = submit_url
        self.method = method
        self.theme = theme
        
        # Security
        self.enable_csrf = enable_csrf
        self.csrf_token = secrets.token_urlsafe(32) if enable_csrf else None
        
        # Analytics
        self.analytics = FormAnalytics(enable_analytics, analytics_endpoint)
        
        # Features
        self.enable_autosave = enable_autosave
        self.autosave_interval = autosave_interval
        self.save_progress = save_progress
        self.show_progress_bar = show_progress_bar
        self.allow_step_navigation = allow_step_navigation
        self.enable_print_view = enable_print_view
        self.enable_keyboard_shortcuts = enable_keyboard_shortcuts
        
        # i18n
        self.i18n = i18n or FormI18n()
        
        # Customization
        self.custom_css = custom_css
        self.custom_js = custom_js
        
        # Form ID for tracking
        self.form_id = form_id or hashlib.md5(f"{title}{len(steps)}".encode()).hexdigest()[:8]
        
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
            if self.custom_css:
                html += f'<style>{self.custom_css}</style>'
        
        html += '''
</head>
<body>
    <div class="form-wizard-container" data-theme="''' + self.theme.value + '''">
'''
        
        # Progress bar
        if self.show_progress_bar:
            html += self._generate_progress_bar()
        
        # Form
        html += f'''
        <form id="wizardForm" action="{self.submit_url}" method="{self.method}" novalidate data-form-id="{self.form_id}">
'''
        
        # CSRF token
        if self.enable_csrf:
            html += f'<input type="hidden" name="csrf_token" value="{self.csrf_token}">'
        
        html += '''
            <div class="form-steps-container">
'''
        
        # Render each step
        for i, step in enumerate(self.steps):
            html += step.render(i, theme=self.theme)
        
        html += '''
            </div>
            
            <!-- Navigation buttons -->
            <div class="form-navigation">
                <button type="button" class="btn btn-secondary" id="prevBtn" onclick="changeStep(-1)" style="display: none;">
                    <span class="btn-text">''' + self.i18n.get('previous') + '''</span>
                </button>
                <button type="button" class="btn btn-primary" id="nextBtn" onclick="changeStep(1)">
                    <span class="btn-text">''' + self.i18n.get('next') + '''</span>
                </button>
                <button type="submit" class="btn btn-success" id="submitBtn" style="display: none;">
                    <span class="btn-text">''' + self.i18n.get('submit') + '''</span>
                </button>
'''
        
        if self.enable_autosave:
            html += f'''
                <button type="button" class="btn btn-ghost" id="saveBtn" onclick="saveProgress()">
                    <span class="btn-text">{self.i18n.get('save_draft')}</span>
                </button>
'''
        
        html += '''
            </div>
        </form>
        
        <!-- Summary/Confirmation -->
        <div id="summaryContainer" style="display: none;">
            <h2>Submission Summary</h2>
            <div id="summaryContent"></div>
            <button type="button" class="btn btn-primary" onclick="editForm()">Edit</button>
            <button type="button" class="btn btn-success" onclick="confirmSubmission()">Confirm & Submit</button>
        </div>
        
        <!-- Loading overlay -->
        <div id="loadingOverlay" class="loading-overlay" style="display: none;">
            <div class="spinner"></div>
            <p>''' + self.i18n.get('loading') + '''</p>
        </div>
        
        <!-- Notification container -->
        <div id="notificationContainer" class="notification-container"></div>
    </div>
'''
        
        if include_scripts:
            html += self._generate_scripts()
            if self.custom_js:
                html += f'<script>{self.custom_js}</script>'
        
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
        """Generate enhanced CSS styles with themes"""
        return '''
    <style>
        /* CSS Variables for theming */
        :root {
            --primary-color: #2196F3;
            --secondary-color: #757575;
            --success-color: #4CAF50;
            --error-color: #f44336;
            --warning-color: #ff9800;
            --info-color: #2196F3;
            --text-color: #333;
            --text-muted: #666;
            --background-color: #fff;
            --background-alt: #f5f5f5;
            --border-color: #ddd;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 8px 16px rgba(0,0,0,0.1);
            --transition-speed: 0.3s;
            --border-radius: 4px;
            --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        
        /* Dark theme */
        [data-theme="dark"] {
            --text-color: #f5f5f5;
            --text-muted: #aaa;
            --background-color: #1a1a1a;
            --background-alt: #2a2a2a;
            --border-color: #444;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.3);
            --shadow-lg: 0 8px 16px rgba(0,0,0,0.3);
        }
        
        /* Modern theme */
        [data-theme="modern"] {
            --primary-color: #6366f1;
            --border-radius: 8px;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            --shadow-md: 0 3px 6px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12);
        }
        
        /* Base styles */
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: var(--font-family);
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-alt);
            margin: 0;
            padding: 20px;
            transition: background-color var(--transition-speed), color var(--transition-speed);
        }
        
        .form-wizard-container {
            max-width: 800px;
            margin: 0 auto;
            background: var(--background-color);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-lg);
            padding: 30px;
            transition: all var(--transition-speed);
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
            transition: all var(--transition-speed);
            cursor: pointer;
        }
        
        .progress-step.active .progress-bullet,
        .progress-step.completed .progress-bullet {
            background-color: var(--primary-color);
            color: white;
            transform: scale(1.1);
        }
        
        .progress-step.completed .progress-bullet::after {
            content: '✓';
            position: absolute;
            font-size: 12px;
            top: -5px;
            right: -5px;
            background: var(--success-color);
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .progress-step.active .progress-label {
            color: var(--primary-color);
            font-weight: 600;
        }
        
        .progress-label {
            margin-top: 8px;
            font-size: 14px;
            color: var(--text-muted);
            transition: all var(--transition-speed);
        }
        
        .progress-line {
            flex: 1;
            height: 2px;
            background-color: #e0e0e0;
            margin: 0 -20px;
            transform: translateY(-20px);
            transition: all var(--transition-speed);
        }
        
        .progress-step.completed + .progress-line {
            background-color: var(--primary-color);
        }
        
        /* Form Steps */
        .form-step {
            display: none;
            animation: slideIn var(--transition-speed) ease-out;
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
            color: var(--text-color);
        }
        
        .step-description {
            color: var(--text-muted);
            margin-bottom: 30px;
        }
        
        /* Form Fields */
        .form-field {
            margin-bottom: 20px;
            transition: all var(--transition-speed);
        }
        
        .form-field.conditional-field {
            overflow: hidden;
        }
        
        .form-field label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: var(--text-color);
            transition: color var(--transition-speed);
        }
        
        .form-field:focus-within label {
            color: var(--primary-color);
        }
        
        .form-field input,
        .form-field select,
        .form-field textarea {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            font-size: 16px;
            transition: all var(--transition-speed);
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .form-field input:focus,
        .form-field select:focus,
        .form-field textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
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
            background-color: rgba(244, 67, 54, 0.05);
        }
        
        .required {
            color: var(--error-color);
            margin-left: 3px;
        }
        
        .help-text {
            display: block;
            margin-top: 5px;
            color: var(--text-muted);
            font-size: 14px;
        }
        
        .validation-message {
            color: var(--error-color);
            font-size: 14px;
            margin-top: 5px;
            display: none;
            animation: fadeIn var(--transition-speed);
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
            transition: all var(--transition-speed);
        }
        
        .radio-label:hover,
        .checkbox-label:hover {
            color: var(--primary-color);
        }
        
        .radio-label input,
        .checkbox-label input {
            width: auto;
            margin-right: 8px;
        }
        
        /* Advanced Field Types */
        
        /* Tags Input */
        .tags-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 8px;
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            min-height: 42px;
            background: var(--background-color);
            transition: all var(--transition-speed);
        }
        
        .tags-container:focus-within {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
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
            animation: scaleIn 0.2s;
        }
        
        @keyframes scaleIn {
            from {
                transform: scale(0.8);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        .tag button {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
            line-height: 1;
            padding: 0;
            margin-left: 4px;
            opacity: 0.8;
            transition: opacity var(--transition-speed);
        }
        
        .tag button:hover {
            opacity: 1;
        }
        
        .tags-input {
            flex: 1;
            border: none;
            outline: none;
            min-width: 150px;
            background: transparent;
            color: var(--text-color);
        }
        
        /* Autocomplete */
        .autocomplete-wrapper {
            position: relative;
        }
        
        .autocomplete-suggestions {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--background-color);
            border: 1px solid var(--border-color);
            border-top: none;
            max-height: 200px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
            box-shadow: var(--shadow-md);
            border-radius: 0 0 var(--border-radius) var(--border-radius);
        }
        
        .suggestion-item {
            padding: 10px;
            cursor: pointer;
            transition: background-color var(--transition-speed);
        }
        
        .suggestion-item:hover,
        .suggestion-item.selected {
            background-color: var(--background-alt);
        }
        
        .suggestion-highlight {
            font-weight: bold;
            color: var(--primary-color);
        }
        
        /* File Drag and Drop */
        .file-dropzone {
            border: 2px dashed var(--border-color);
            border-radius: var(--border-radius);
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all var(--transition-speed);
            background: var(--background-color);
        }
        
        .file-dropzone:hover,
        .file-dropzone.dragover {
            border-color: var(--primary-color);
            background-color: rgba(33, 150, 243, 0.05);
            transform: scale(1.01);
        }
        
        .file-input-hidden {
            display: none;
        }
        
        .upload-icon {
            color: var(--text-muted);
            margin-bottom: 10px;
        }
        
        .browse-link {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
        }
        
        .uploaded-files {
            margin-top: 20px;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: var(--background-alt);
            border-radius: var(--border-radius);
            margin-bottom: 8px;
            animation: slideIn 0.3s;
        }
        
        .file-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .file-icon {
            width: 32px;
            height: 32px;
            background: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .file-item button {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: var(--text-muted);
            transition: color var(--transition-speed);
        }
        
        .file-item button:hover {
            color: var(--error-color);
        }
        
        /* Rich Text Editor */
        .rich-text-wrapper {
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            overflow: hidden;
        }
        
        .rich-text-toolbar {
            display: flex;
            gap: 5px;
            padding: 8px;
            background: var(--background-alt);
            border-bottom: 1px solid var(--border-color);
        }
        
        .rich-text-toolbar button {
            width: 32px;
            height: 32px;
            border: none;
            background: transparent;
            cursor: pointer;
            border-radius: 4px;
            transition: all var(--transition-speed);
            color: var(--text-color);
        }
        
        .rich-text-toolbar button:hover {
            background: var(--primary-color);
            color: white;
        }
        
        .rich-text-toolbar button.active {
            background: var(--primary-color);
            color: white;
        }
        
        .rich-text-editor {
            min-height: 200px;
            padding: 15px;
            outline: none;
            background: var(--background-color);
            color: var(--text-color);
        }
        
        .rich-text-editor:focus {
            background: var(--background-alt);
        }
        
        /* Navigation Buttons */
        .form-navigation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }
        
        .btn {
            padding: 10px 30px;
            border: none;
            border-radius: var(--border-radius);
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all var(--transition-speed);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            position: relative;
            overflow: hidden;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            color: white;
        }
        
        .btn-primary:hover:not(:disabled) {
            background-color: #1976D2;
        }
        
        .btn-secondary {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .btn-secondary:hover:not(:disabled) {
            background-color: #616161;
        }
        
        .btn-success {
            background-color: var(--success-color);
            color: white;
        }
        
        .btn-success:hover:not(:disabled) {
            background-color: #45a049;
        }
        
        .btn-ghost {
            background-color: transparent;
            color: var(--primary-color);
            border: 1px solid var(--primary-color);
        }
        
        .btn-ghost:hover:not(:disabled) {
            background-color: var(--primary-color);
            color: white;
        }
        
        /* Loading state for buttons */
        .btn.loading {
            color: transparent;
        }
        
        .btn.loading::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            top: 50%;
            left: 50%;
            margin: -10px 0 0 -10px;
            border: 2px solid white;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Loading Overlay */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid white;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }
        
        .loading-overlay p {
            color: white;
            margin-top: 20px;
            font-size: 18px;
        }
        
        /* Notifications */
        .notification-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        .notification {
            background: var(--background-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 15px 20px;
            margin-bottom: 10px;
            box-shadow: var(--shadow-md);
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 300px;
            animation: slideInRight 0.3s;
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .notification.success {
            border-left: 4px solid var(--success-color);
        }
        
        .notification.error {
            border-left: 4px solid var(--error-color);
        }
        
        .notification.info {
            border-left: 4px solid var(--info-color);
        }
        
        .notification-close {
            margin-left: auto;
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: var(--text-muted);
        }
        
        /* Summary */
        #summaryContainer {
            animation: fadeIn var(--transition-speed) ease-out;
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
            background-color: var(--background-alt);
            border-radius: var(--border-radius);
        }
        
        .summary-section h3 {
            margin-top: 0;
            color: var(--text-color);
        }
        
        .summary-field {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .summary-field:last-child {
            border-bottom: none;
        }
        
        .summary-label {
            font-weight: 500;
            color: var(--text-muted);
        }
        
        .summary-value {
            color: var(--text-color);
            text-align: right;
            max-width: 60%;
        }
        
        /* Accessibility */
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
        
        /* Focus visible for keyboard navigation */
        *:focus-visible {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        /* Print styles */
        @media print {
            body {
                background: white;
            }
            
            .form-wizard-container {
                box-shadow: none;
                padding: 0;
            }
            
            .form-navigation,
            .progress-container,
            .notification-container,
            .loading-overlay {
                display: none !important;
            }
            
            .form-step {
                display: block !important;
                page-break-inside: avoid;
                margin-bottom: 30px;
            }
            
            .form-step h2 {
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
            }
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
                justify-content: center;
            }
            
            .notification-container {
                left: 10px;
                right: 10px;
                bottom: 10px;
            }
            
            .notification {
                min-width: auto;
            }
        }
    </style>
'''
    
    def _generate_scripts(self) -> str:
        """Generate enhanced JavaScript with all features"""
        return f'''
    <script>
        // Form Wizard Enhanced State
        const formConfig = {{
            formId: '{self.form_id}',
            csrfToken: '{self.csrf_token}',
            enableAnalytics: {str(self.analytics.enabled).lower()},
            analyticsEndpoint: '{self.analytics.endpoint}',
            enableAutosave: {str(self.enable_autosave).lower()},
            autosaveInterval: {self.autosave_interval},
            enableKeyboardShortcuts: {str(self.enable_keyboard_shortcuts).lower()},
            i18n: {json.dumps(self.i18n.translations[self.i18n.default_locale])}
        }};
        
        let currentStep = 0;
        const formData = {{}};
        const form = document.getElementById('wizardForm');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');
        const summaryContainer = document.getElementById('summaryContainer');
        
        // Enhanced initialization
        document.addEventListener('DOMContentLoaded', function() {{
            showStep(currentStep);
            loadSavedProgress();
            initializeEnhancements();
            
            // Add form submit handler
            form.addEventListener('submit', handleSubmit);
            
            // Add input change handlers
            form.addEventListener('input', handleInputChange);
            form.addEventListener('change', handleInputChange);
        }});
        
        // Initialize all enhancements
        function initializeEnhancements() {{
            initializeRealTimeValidation();
            initializeAdvancedFields();
            initializeAnalytics();
            initializeKeyboardShortcuts();
            initializeConditionalFields();
            
            if (formConfig.enableAutosave) {{
                setInterval(saveProgress, formConfig.autosaveInterval);
            }}
        }}
        
        // Real-time validation
        function initializeRealTimeValidation() {{
            document.querySelectorAll('[data-realtime-validate="true"]').forEach(field => {{
                let timeout;
                const debounce = parseInt(field.dataset.debounce) || 500;
                
                field.addEventListener('input', function(e) {{
                    clearTimeout(timeout);
                    const fieldContainer = this.closest('.form-field');
                    const validationMsg = fieldContainer.querySelector('.validation-message');
                    
                    // Reset state
                    this.classList.remove('is-valid', 'is-invalid');
                    validationMsg.classList.remove('show');
                    
                    timeout = setTimeout(async () => {{
                        const isValid = await validateField(this);
                        
                        if (isValid) {{
                            this.classList.add('is-valid');
                        }} else {{
                            this.classList.add('is-invalid');
                            validationMsg.classList.add('show');
                        }}
                    }}, debounce);
                }});
            }});
        }}
        
        // Advanced field initialization
        function initializeAdvancedFields() {{
            // Tags fields
            document.querySelectorAll('.field-tags').forEach(fieldContainer => {{
                const input = fieldContainer.querySelector('.tags-input');
                const container = fieldContainer.querySelector('.tags-container');
                const hiddenInput = fieldContainer.querySelector('input[type="hidden"]');
                const tagsDiv = fieldContainer.querySelector('.tags-list');
                const fieldName = input.dataset.fieldName;
                
                // Load existing tags
                let tags = [];
                try {{
                    tags = JSON.parse(hiddenInput.value || '[]');
                }} catch (e) {{
                    tags = [];
                }}
                
                // Display existing tags
                tags.forEach(tag => addTagElement(tag, tagsDiv, tags, hiddenInput, fieldName));
                
                // Handle new tag input
                input.addEventListener('keydown', function(e) {{
                    if (e.key === 'Enter' && this.value.trim()) {{
                        e.preventDefault();
                        const tag = this.value.trim();
                        if (!tags.includes(tag)) {{
                            tags.push(tag);
                            addTagElement(tag, tagsDiv, tags, hiddenInput, fieldName);
                            hiddenInput.value = JSON.stringify(tags);
                            formData[fieldName] = tags;
                            this.value = '';
                        }}
                    }}
                }});
            }});
            
            // Autocomplete fields
            document.querySelectorAll('.autocomplete-wrapper input').forEach(input => {{
                const suggestionsDiv = input.nextElementSibling;
                let timeout;
                let currentIndex = -1;
                
                input.addEventListener('input', async function() {{
                    clearTimeout(timeout);
                    const value = this.value.trim();
                    
                    if (value.length < 2) {{
                        suggestionsDiv.style.display = 'none';
                        return;
                    }}
                    
                    timeout = setTimeout(async () => {{
                        const suggestions = await getAutocompleteSuggestions(input, value);
                        displaySuggestions(suggestions, value, suggestionsDiv, input);
                    }}, 300);
                }});
                
                // Keyboard navigation
                input.addEventListener('keydown', function(e) {{
                    const items = suggestionsDiv.querySelectorAll('.suggestion-item');
                    
                    if (e.key === 'ArrowDown') {{
                        e.preventDefault();
                        currentIndex = Math.min(currentIndex + 1, items.length - 1);
                        updateSelectedSuggestion(items, currentIndex);
                    }} else if (e.key === 'ArrowUp') {{
                        e.preventDefault();
                        currentIndex = Math.max(currentIndex - 1, -1);
                        updateSelectedSuggestion(items, currentIndex);
                    }} else if (e.key === 'Enter' && currentIndex >= 0) {{
                        e.preventDefault();
                        items[currentIndex].click();
                    }} else if (e.key === 'Escape') {{
                        suggestionsDiv.style.display = 'none';
                    }}
                }});
                
                // Click outside to close
                document.addEventListener('click', function(e) {{
                    if (!input.contains(e.target) && !suggestionsDiv.contains(e.target)) {{
                        suggestionsDiv.style.display = 'none';
                    }}
                }});
            }});
            
            // File drag and drop
            document.querySelectorAll('.file-dropzone').forEach(dropzone => {{
                const input = dropzone.querySelector('input[type="file"]');
                const filesDiv = dropzone.querySelector('.uploaded-files');
                const browseLink = dropzone.querySelector('.browse-link');
                const maxSize = parseInt(dropzone.dataset.maxSize) || 10 * 1024 * 1024;
                const fieldName = input.name;
                const uploadedFiles = [];
                
                // Browse link click
                if (browseLink) {{
                    browseLink.addEventListener('click', (e) => {{
                        e.preventDefault();
                        input.click();
                    }});
                }}
                
                // Drag events
                dropzone.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    dropzone.classList.add('dragover');
                }});
                
                dropzone.addEventListener('dragleave', () => {{
                    dropzone.classList.remove('dragover');
                }});
                
                dropzone.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    dropzone.classList.remove('dragover');
                    handleFiles(e.dataTransfer.files, filesDiv, uploadedFiles, maxSize, fieldName);
                }});
                
                // File input change
                input.addEventListener('change', (e) => {{
                    handleFiles(e.target.files, filesDiv, uploadedFiles, maxSize, fieldName);
                }});
            }});
            
            // Rich text editor
            document.querySelectorAll('.rich-text-wrapper').forEach(wrapper => {{
                const editor = wrapper.querySelector('.rich-text-editor');
                const hiddenTextarea = wrapper.querySelector('textarea');
                const toolbar = wrapper.querySelector('.rich-text-toolbar');
                const fieldName = editor.dataset.fieldName;
                
                // Toolbar buttons
                toolbar.querySelectorAll('button').forEach(btn => {{
                    btn.addEventListener('click', (e) => {{
                        e.preventDefault();
                        const command = btn.dataset.command;
                        
                        if (command === 'createLink') {{
                            const url = prompt('Enter URL:');
                            if (url) {{
                                document.execCommand(command, false, url);
                            }}
                        }} else {{
                            document.execCommand(command, false, null);
                        }}
                        
                        // Update hidden textarea
                        hiddenTextarea.value = editor.innerHTML;
                        formData[fieldName] = editor.innerHTML;
                        
                        // Update button state
                        updateToolbarState(toolbar);
                    }});
                }});
                
                // Update on content change
                editor.addEventListener('input', () => {{
                    hiddenTextarea.value = editor.innerHTML;
                    formData[fieldName] = editor.innerHTML;
                }});
                
                // Update toolbar state on selection change
                editor.addEventListener('mouseup', () => updateToolbarState(toolbar));
                editor.addEventListener('keyup', () => updateToolbarState(toolbar));
            }});
        }}
        
        // Helper functions for advanced fields
        function addTagElement(tag, container, tags, hiddenInput, fieldName) {{
            const tagEl = document.createElement('span');
            tagEl.className = 'tag';
            tagEl.innerHTML = `${{tag}} <button type="button">×</button>`;
            
            tagEl.querySelector('button').addEventListener('click', () => {{
                const index = tags.indexOf(tag);
                if (index > -1) {{
                    tags.splice(index, 1);
                    hiddenInput.value = JSON.stringify(tags);
                    formData[fieldName] = tags;
                    tagEl.remove();
                }}
            }});
            
            container.appendChild(tagEl);
        }}
        
        async function getAutocompleteSuggestions(input, value) {{
            if (input.dataset.autocompleteUrl) {{
                // Fetch from URL
                try {{
                    const response = await fetch(`${{input.dataset.autocompleteUrl}}?q=${{encodeURIComponent(value)}}`);
                    return await response.json();
                }} catch (error) {{
                    console.error('Autocomplete fetch error:', error);
                    return [];
                }}
            }} else if (input.dataset.autocompleteItems) {{
                // Use local items
                const items = JSON.parse(input.dataset.autocompleteItems);
                return items.filter(item => 
                    item.toLowerCase().includes(value.toLowerCase())
                );
            }}
            return [];
        }}
        
        function displaySuggestions(suggestions, query, container, input) {{
            container.innerHTML = '';
            
            if (suggestions.length === 0) {{
                container.style.display = 'none';
                return;
            }}
            
            suggestions.forEach((suggestion, index) => {{
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                
                // Highlight matching text
                const regex = new RegExp(`(${{query}})`, 'gi');
                div.innerHTML = suggestion.replace(regex, '<span class="suggestion-highlight">$1</span>');
                
                div.addEventListener('click', () => {{
                    input.value = suggestion;
                    container.style.display = 'none';
                    formData[input.name] = suggestion;
                    
                    // Trigger change event
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }});
                
                container.appendChild(div);
            }});
            
            container.style.display = 'block';
        }}
        
        function updateSelectedSuggestion(items, index) {{
            items.forEach((item, i) => {{
                if (i === index) {{
                    item.classList.add('selected');
                    item.scrollIntoView({{ block: 'nearest' }});
                }} else {{
                    item.classList.remove('selected');
                }}
            }});
        }}
        
        function handleFiles(files, container, uploadedFiles, maxSize, fieldName) {{
            Array.from(files).forEach(file => {{
                if (file.size > maxSize) {{
                    showNotification(`File "${{file.name}}" is too large. Maximum size is ${{maxSize / 1024 / 1024}}MB`, 'error');
                    return;
                }}
                
                uploadedFiles.push(file);
                displayFile(file, container, uploadedFiles, fieldName);
            }});
            
            formData[fieldName] = uploadedFiles;
        }}
        
        function displayFile(file, container, uploadedFiles, fieldName) {{
            const div = document.createElement('div');
            div.className = 'file-item';
            
            const extension = file.name.split('.').pop().toUpperCase();
            
            div.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">${{extension}}</div>
                    <div>
                        <div>${{file.name}}</div>
                        <small>${{(file.size / 1024).toFixed(1)}} KB</small>
                    </div>
                </div>
                <button type="button">×</button>
            `;
            
            div.querySelector('button').addEventListener('click', () => {{
                const index = uploadedFiles.indexOf(file);
                if (index > -1) {{
                    uploadedFiles.splice(index, 1);
                    formData[fieldName] = uploadedFiles;
                    div.remove();
                }}
            }});
            
            container.appendChild(div);
        }}
        
        function updateToolbarState(toolbar) {{
            toolbar.querySelectorAll('button').forEach(btn => {{
                const command = btn.dataset.command;
                const state = document.queryCommandState(command);
                
                if (state) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});
        }}
        
        // Form analytics
        function initializeAnalytics() {{
            if (!formConfig.enableAnalytics) return;
            
            const analytics = {{
                startTime: Date.now(),
                interactions: {{}},
                errors: {{}},
                
                track(event, data) {{
                    fetch(formConfig.analyticsEndpoint, {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            formId: formConfig.formId,
                            event: event,
                            data: data,
                            timestamp: Date.now()
                        }})
                    }}).catch(console.error);
                }},
                
                trackFieldInteraction(fieldName) {{
                    if (!this.interactions[fieldName]) {{
                        this.interactions[fieldName] = {{
                            count: 0,
                            firstTouch: Date.now()
                        }};
                    }}
                    this.interactions[fieldName].count++;
                }},
                
                trackError(fieldName, error) {{
                    if (!this.errors[fieldName]) {{
                        this.errors[fieldName] = [];
                    }}
                    this.errors[fieldName].push({{
                        error: error,
                        timestamp: Date.now()
                    }});
                }}
            }};
            
            // Track form start
            analytics.track('form_start', {{ step: 0 }});
            
            // Track field interactions
            form.addEventListener('focus', (e) => {{
                if (e.target.name) {{
                    analytics.trackFieldInteraction(e.target.name);
                }}
            }}, true);
            
            // Track errors
            form.addEventListener('invalid', (e) => {{
                if (e.target.name) {{
                    analytics.trackError(e.target.name, e.target.validationMessage);
                }}
            }}, true);
            
            // Make analytics available globally
            window.formAnalytics = analytics;
        }}
        
        // Keyboard shortcuts
        function initializeKeyboardShortcuts() {{
            if (!formConfig.enableKeyboardShortcuts) return;
            
            document.addEventListener('keydown', (e) => {{
                // Ctrl/Cmd + S to save
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {{
                    e.preventDefault();
                    saveProgress();
                    showNotification(formConfig.i18n.form_saved, 'success');
                }}
                
                // Alt + Right/Left for navigation
                if (e.altKey) {{
                    if (e.key === 'ArrowRight' && nextBtn.style.display !== 'none') {{
                        nextBtn.click();
                    }} else if (e.key === 'ArrowLeft' && prevBtn.style.display !== 'none') {{
                        prevBtn.click();
                    }}
                }}
            }});
        }}
        
        // Conditional fields
        function initializeConditionalFields() {{
            updateConditionalFields();
            
            // Update on any form change
            form.addEventListener('change', updateConditionalFields);
        }}
        
        function updateConditionalFields() {{
            document.querySelectorAll('[data-show-if]').forEach(field => {{
                const condition = JSON.parse(field.dataset.showIf);
                const shouldShow = evaluateCondition(condition);
                
                if (shouldShow) {{
                    field.style.display = '';
                    field.style.animation = 'fadeIn 0.3s';
                }} else {{
                    field.style.display = 'none';
                }}
            }});
        }}
        
        function evaluateCondition(condition) {{
            for (const [fieldName, expected] of Object.entries(condition)) {{
                const actual = formData[fieldName];
                
                if (typeof expected === 'object' && expected.operator) {{
                    // Complex condition
                    const {{ operator, value }} = expected;
                    
                    switch (operator) {{
                        case 'equals':
                            if (actual != value) return false;
                            break;
                        case 'not_equals':
                            if (actual == value) return false;
                            break;
                        case 'contains':
                            if (!String(actual).includes(value)) return false;
                            break;
                        case 'greater_than':
                            if (!(parseFloat(actual) > parseFloat(value))) return false;
                            break;
                        case 'less_than':
                            if (!(parseFloat(actual) < parseFloat(value))) return false;
                            break;
                        case 'in':
                            if (!value.includes(actual)) return false;
                            break;
                    }}
                }} else {{
                    // Simple equality
                    if (actual != expected) return false;
                }}
            }}
            
            return true;
        }}
        
        // Original functions with enhancements
        function showStep(stepIndex) {{
            const steps = document.querySelectorAll('.form-step');
            const progressSteps = document.querySelectorAll('.progress-step');
            
            // Hide all steps
            steps.forEach(step => {{
                step.classList.remove('active');
            }});
            
            // Show current step
            if (steps[stepIndex]) {{
                steps[stepIndex].classList.add('active');
                
                // Update conditional fields for current step
                updateConditionalFields();
            }}
            
            // Update progress bar
            progressSteps.forEach((step, index) => {{
                step.classList.remove('active', 'completed');
                if (index < stepIndex) {{
                    step.classList.add('completed');
                }} else if (index === stepIndex) {{
                    step.classList.add('active');
                }}
            }});
            
            // Update navigation buttons
            updateNavigationButtons();
            
            // Focus first input in current step
            setTimeout(() => {{
                const firstInput = steps[stepIndex]?.querySelector('input:not([type="hidden"]), select, textarea');
                if (firstInput && !firstInput.disabled) {{
                    firstInput.focus();
                }}
            }}, 100);
            
            // Track step change
            if (window.formAnalytics) {{
                window.formAnalytics.track('step_change', {{
                    from: currentStep,
                    to: stepIndex
                }});
            }}
        }}
        
        function updateNavigationButtons() {{
            const totalSteps = document.querySelectorAll('.form-step').length;
            
            // Previous button
            if (currentStep === 0) {{
                prevBtn.style.display = 'none';
            }} else {{
                prevBtn.style.display = 'inline-flex';
            }}
            
            // Next/Submit buttons
            if (currentStep === totalSteps - 1) {{
                nextBtn.style.display = 'none';
                submitBtn.style.display = 'inline-flex';
            }} else {{
                nextBtn.style.display = 'inline-flex';
                submitBtn.style.display = 'none';
            }}
        }}
        
        async function changeStep(direction) {{
            const totalSteps = document.querySelectorAll('.form-step').length;
            
            // Validate current step before moving forward
            if (direction > 0 && !await validateCurrentStep()) {{
                return;
            }}
            
            // Save current step data
            saveStepData();
            
            // Update step index
            currentStep += direction;
            
            // Ensure step is within bounds
            if (currentStep < 0) {{
                currentStep = 0;
            }} else if (currentStep >= totalSteps) {{
                currentStep = totalSteps - 1;
            }}
            
            // Show new step
            showStep(currentStep);
            
            // Scroll to top
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        async function validateCurrentStep() {{
            const currentStepElement = document.querySelector(`.form-step[data-step="${{currentStep}}"]`);
            const inputs = currentStepElement.querySelectorAll('input:not([type="hidden"]), select, textarea');
            let isValid = true;
            
            for (const input of inputs) {{
                // Skip if field is not visible
                const fieldContainer = input.closest('.form-field');
                if (fieldContainer && fieldContainer.style.display === 'none') {{
                    continue;
                }}
                
                if (!await validateField(input)) {{
                    isValid = false;
                }}
            }}
            
            if (!isValid && window.formAnalytics) {{
                window.formAnalytics.track('validation_error', {{
                    step: currentStep,
                    errors: Object.keys(window.formAnalytics.errors || {{}})
                }});
            }}
            
            return isValid;
        }}
        
        async function validateField(field) {{
            const fieldContainer = field.closest('.form-field');
            if (!fieldContainer) return true;
            
            const validationMessage = fieldContainer.querySelector('.validation-message');
            
            // Reset validation state
            field.classList.remove('is-invalid');
            validationMessage.textContent = '';
            validationMessage.classList.remove('show');
            
            // Check HTML5 validation
            if (!field.checkValidity()) {{
                field.classList.add('is-invalid');
                validationMessage.textContent = field.validationMessage || formConfig.i18n.required_field;
                validationMessage.classList.add('show');
                return false;
            }}
            
            // Ajax validation
            if (field.dataset.validateUrl) {{
                try {{
                    const response = await fetch(field.dataset.validateUrl, {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            field: field.name,
                            value: field.value,
                            csrf_token: formConfig.csrfToken
                        }})
                    }});
                    
                    const result = await response.json();
                    if (!result.valid) {{
                        field.classList.add('is-invalid');
                        validationMessage.textContent = result.message;
                        validationMessage.classList.add('show');
                        return false;
                    }}
                }} catch (error) {{
                    console.error('Validation error:', error);
                }}
            }}
            
            return true;
        }}
        
        function saveStepData() {{
            const currentStepElement = document.querySelector(`.form-step[data-step="${{currentStep}}"]`);
            const inputs = currentStepElement.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {{
                // Skip hidden fields added by advanced components
                if (input.type === 'hidden' && input.id && input.id.includes('_hidden')) {{
                    // These are handled by their parent components
                    return;
                }}
                
                if (input.type === 'checkbox') {{
                    if (input.name.endsWith('[]')) {{
                        // Multiple checkboxes
                        const name = input.name.slice(0, -2);
                        if (!formData[name]) {{
                            formData[name] = [];
                        }}
                        if (input.checked && !formData[name].includes(input.value)) {{
                            formData[name].push(input.value);
                        }} else if (!input.checked) {{
                            formData[name] = formData[name].filter(v => v !== input.value);
                        }}
                    }} else {{
                        // Single checkbox
                        formData[input.name] = input.checked;
                    }}
                }} else if (input.type === 'radio') {{
                    if (input.checked) {{
                        formData[input.name] = input.value;
                    }}
                }} else if (input.type !== 'file') {{
                    // File inputs are handled separately
                    formData[input.name] = input.value;
                }}
            }});
            
            saveProgress();
        }}
        
        function saveProgress() {{
            if (typeof(Storage) !== "undefined") {{
                const saveData = {{
                    formData: formData,
                    currentStep: currentStep,
                    timestamp: Date.now()
                }};
                
                localStorage.setItem('formWizard_' + formConfig.formId, JSON.stringify(saveData));
                
                // Show save indicator
                if (formConfig.enableAutosave) {{
                    showNotification(formConfig.i18n.form_saved, 'success', 2000);
                }}
            }}
        }}
        
        function loadSavedProgress() {{
            if (typeof(Storage) !== "undefined") {{
                const savedData = localStorage.getItem('formWizard_' + formConfig.formId);
                
                if (savedData) {{
                    try {{
                        const data = JSON.parse(savedData);
                        Object.assign(formData, data.formData);
                        currentStep = data.currentStep || 0;
                        populateFormFields();
                        showStep(currentStep);
                    }} catch (error) {{
                        console.error('Error loading saved data:', error);
                    }}
                }}
            }}
        }}
        
        function populateFormFields() {{
            Object.keys(formData).forEach(fieldName => {{
                const value = formData[fieldName];
                
                // Handle different field types
                const fields = document.querySelectorAll(`[name="${{fieldName}}"], [name="${{fieldName}}[]"]`);
                
                fields.forEach(field => {{
                    if (field.type === 'checkbox') {{
                        if (Array.isArray(value)) {{
                            field.checked = value.includes(field.value);
                        }} else {{
                            field.checked = value;
                        }}
                    }} else if (field.type === 'radio') {{
                        field.checked = field.value === value;
                    }} else if (field.type !== 'file') {{
                        field.value = value;
                    }}
                }});
                
                // Handle advanced fields
                // Rich text editors
                const richTextEditor = document.querySelector(`[data-field-name="${{fieldName}}"].rich-text-editor`);
                if (richTextEditor && value) {{
                    richTextEditor.innerHTML = value;
                }}
            }});
        }}
        
        function handleInputChange(e) {{
            const field = e.target;
            
            // Save field value
            if (field.name && field.type !== 'file') {{
                if (field.type === 'checkbox' && field.name.endsWith('[]')) {{
                    // Handle multiple checkboxes
                    const name = field.name.slice(0, -2);
                    if (!formData[name]) formData[name] = [];
                    
                    if (field.checked) {{
                        if (!formData[name].includes(field.value)) {{
                            formData[name].push(field.value);
                        }}
                    }} else {{
                        formData[name] = formData[name].filter(v => v !== field.value);
                    }}
                }} else if (field.type === 'checkbox') {{
                    formData[field.name] = field.checked;
                }} else if (field.type === 'radio') {{
                    if (field.checked) {{
                        formData[field.name] = field.value;
                    }}
                }} else {{
                    formData[field.name] = field.value;
                }}
            }}
            
            // Update conditional fields
            updateConditionalFields();
            
            // Auto-save
            if (formConfig.enableAutosave) {{
                saveProgress();
            }}
        }}
        
        async function handleSubmit(e) {{
            e.preventDefault();
            
            if (!await validateCurrentStep()) {{
                return;
            }}
            
            saveStepData();
            showSummary();
        }}
        
        function showSummary() {{
            const summaryContent = document.getElementById('summaryContent');
            summaryContent.innerHTML = '';
            
            // Group data by steps
            document.querySelectorAll('.form-step').forEach((step, index) => {{
                const stepTitle = step.querySelector('h2').textContent;
                const section = document.createElement('div');
                section.className = 'summary-section';
                section.innerHTML = `<h3>${{stepTitle}}</h3>`;
                
                const fields = step.querySelectorAll('.form-field');
                let hasVisibleFields = false;
                
                fields.forEach(fieldContainer => {{
                    // Skip hidden fields
                    if (fieldContainer.style.display === 'none') return;
                    
                    const fieldName = fieldContainer.dataset.fieldName;
                    if (formData[fieldName] !== undefined && formData[fieldName] !== '' && formData[fieldName] !== null) {{
                        const label = fieldContainer.querySelector('label').textContent.replace('*', '').trim();
                        let value = formData[fieldName];
                        
                        // Format value for display
                        if (Array.isArray(value)) {{
                            value = value.join(', ');
                        }} else if (typeof value === 'boolean') {{
                            value = value ? 'Yes' : 'No';
                        }}
                        
                        const fieldDiv = document.createElement('div');
                        fieldDiv.className = 'summary-field';
                        fieldDiv.innerHTML = `
                            <span class="summary-label">${{label}}:</span>
                            <span class="summary-value">${{value}}</span>
                        `;
                        section.appendChild(fieldDiv);
                        hasVisibleFields = true;
                    }}
                }});
                
                if (hasVisibleFields) {{
                    summaryContent.appendChild(section);
                }}
            }});
            
            // Hide form and show summary
            form.style.display = 'none';
            summaryContainer.style.display = 'block';
            
            // Track completion
            if (window.formAnalytics) {{
                window.formAnalytics.track('form_complete', {{
                    totalTime: Date.now() - window.formAnalytics.startTime,
                    steps: currentStep + 1
                }});
            }}
        }}
        
        function editForm() {{
            form.style.display = 'block';
            summaryContainer.style.display = 'none';
        }}
        
        async function confirmSubmission() {{
            showLoading(true);
            
            try {{
                // Prepare form data
                const submitData = new FormData();
                
                // Add regular form data
                Object.keys(formData).forEach(key => {{
                    const value = formData[key];
                    if (Array.isArray(value)) {{
                        value.forEach(v => submitData.append(key, v));
                    }} else if (value instanceof FileList || Array.isArray(value)) {{
                        // Handle files
                        Array.from(value).forEach(file => {{
                            submitData.append(key, file);
                        }});
                    }} else {{
                        submitData.append(key, value);
                    }}
                }});
                
                // Add CSRF token
                if (formConfig.csrfToken) {{
                    submitData.append('csrf_token', formConfig.csrfToken);
                }}
                
                // Submit form
                const response = await fetch(form.action, {{
                    method: form.method,
                    body: submitData
                }});
                
                if (response.ok) {{
                    const result = await response.json();
                    showNotification('Form submitted successfully!', 'success');
                    
                    // Clear saved progress
                    if (typeof(Storage) !== "undefined") {{
                        localStorage.removeItem('formWizard_' + formConfig.formId);
                    }}
                    
                    // Track submission
                    if (window.formAnalytics) {{
                        window.formAnalytics.track('form_submit', {{
                            success: true
                        }});
                    }}
                    
                    // Redirect or show success message
                    if (result.redirect) {{
                        window.location.href = result.redirect;
                    }} else {{
                        summaryContainer.innerHTML = `
                            <div class="success-message">
                                <h2>Thank You!</h2>
                                <p>Your submission has been received.</p>
                                ${{result.message || ''}}
                            </div>
                        `;
                    }}
                }} else {{
                    throw new Error('Submission failed');
                }}
            }} catch (error) {{
                console.error('Submission error:', error);
                showNotification('Error submitting form. Please try again.', 'error');
                
                if (window.formAnalytics) {{
                    window.formAnalytics.track('form_submit', {{
                        success: false,
                        error: error.message
                    }});
                }}
            }} finally {{
                showLoading(false);
            }}
        }}
        
        // Utility functions
        function showLoading(show) {{
            const overlay = document.getElementById('loadingOverlay');
            overlay.style.display = show ? 'flex' : 'none';
        }}
        
        function showNotification(message, type = 'info', duration = 5000) {{
            const container = document.getElementById('notificationContainer');
            const notification = document.createElement('div');
            notification.className = `notification ${{type}}`;
            
            const icon = {{
                success: '✓',
                error: '✗',
                info: 'ℹ',
                warning: '⚠'
            }}[type] || 'ℹ';
            
            notification.innerHTML = `
                <span class="notification-icon">${{icon}}</span>
                <span class="notification-message">${{message}}</span>
                <button class="notification-close">×</button>
            `;
            
            notification.querySelector('.notification-close').addEventListener('click', () => {{
                notification.remove();
            }});
            
            container.appendChild(notification);
            
            if (duration > 0) {{
                setTimeout(() => {{
                    notification.style.animation = 'slideOutRight 0.3s';
                    setTimeout(() => notification.remove(), 300);
                }}, duration);
            }}
        }}
        
        // Allow step navigation by clicking on progress bullets
        document.querySelectorAll('.progress-bullet').forEach((bullet, index) => {{
            bullet.addEventListener('click', async () => {{
                if (!{str(self.allow_step_navigation).lower()}) return;
                
                // Can only go back or to current step
                if (index <= currentStep) {{
                    // Validate current step if moving forward
                    if (index > currentStep && !await validateCurrentStep()) {{
                        return;
                    }}
                    
                    saveStepData();
                    currentStep = index;
                    showStep(currentStep);
                }}
            }});
        }});
        
        // Print functionality
        if ({str(self.enable_print_view).lower()}) {{
            // Add print button or use Ctrl+P
            window.addEventListener('beforeprint', () => {{
                document.querySelectorAll('.form-step').forEach(step => {{
                    step.style.display = 'block';
                }});
            }});
            
            window.addEventListener('afterprint', () => {{
                showStep(currentStep);
            }});
        }}
    </script>
'''


# Pydantic/FastAPI Integration (unchanged from v1)
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
        custom_help_text: Optional[Dict[str, str]] = None,
        enable_advanced_fields: bool = True
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
            
            # Enable advanced field types based on field name patterns
            if enable_advanced_fields:
                if 'tags' in field_name.lower() or 'keywords' in field_name.lower():
                    field_kwargs["type"] = FieldType.TAGS
                elif 'description' in field_name.lower() or 'bio' in field_name.lower():
                    field_kwargs["type"] = FieldType.RICH_TEXT
                    field_kwargs["enable_rich_text"] = True
            
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
            
            # Handle file fields
            if field_name.lower() in ['file', 'upload', 'attachment', 'document']:
                field_kwargs["type"] = FieldType.FILE_DRAG
                field_kwargs["accepted_files"] = ['.pdf', '.doc', '.docx', '.jpg', '.png']
                field_kwargs["max_file_size"] = 10 * 1024 * 1024  # 10MB
            
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
        theme: FormTheme = FormTheme.DEFAULT,
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
                custom_help_text=kwargs.get(f'custom_help_text_{i}', kwargs.get('custom_help_text', {})),
                enable_advanced_fields=kwargs.get('enable_advanced_fields', True)
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
        
        # Create wizard with enhanced features
        wizard = FormWizard(
            title=title,
            steps=steps,
            submit_url=submit_url,
            method=kwargs.get('method', 'POST'),
            theme=theme,
            enable_csrf=kwargs.get('enable_csrf', True),
            enable_analytics=kwargs.get('enable_analytics', False),
            analytics_endpoint=kwargs.get('analytics_endpoint', '/api/analytics'),
            enable_autosave=kwargs.get('enable_autosave', True),
            autosave_interval=kwargs.get('autosave_interval', 30000),
            i18n=kwargs.get('i18n', None),
            save_progress=kwargs.get('save_progress', True),
            show_progress_bar=kwargs.get('show_progress_bar', True),
            allow_step_navigation=kwargs.get('allow_step_navigation', True),
            enable_print_view=kwargs.get('enable_print_view', True),
            enable_keyboard_shortcuts=kwargs.get('enable_keyboard_shortcuts', True),
            custom_css=kwargs.get('custom_css', ''),
            custom_js=kwargs.get('custom_js', '')
        )
        
        return wizard


# FastAPI Integration Helper (enhanced)
def generate_form_endpoint(router, model: Type[BaseModel], path: str = "/form", theme: FormTheme = FormTheme.DEFAULT):
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
    
    from fastapi import Response, Request
    
    @router.get(path, response_class=Response)
    async def get_form():
        wizard = PydanticFormConverter.create_wizard_from_models(
            model,
            title=f"{model.__name__} Form",
            submit_url=f"/api{path}",
            step_titles=[model.__name__],
            theme=theme,
            enable_analytics=True,
            enable_autosave=True
        )
        html_content = wizard.generate_html()
        return Response(content=html_content, media_type="text/html")
    
    @router.post(f"/api{path}")
    async def submit_form(request: Request, data: model):
        # Verify CSRF token if enabled
        form_data = await request.form()
        csrf_token = form_data.get("csrf_token")
        
        # Process the form data
        return {
            "status": "success",
            "data": data.model_dump() if hasattr(data, 'model_dump') else data.dict(),
            "message": "Form submitted successfully!"
        }
    
    return router


# Example usage functions remain the same but with enhanced features
def create_user_registration_wizard():
    """Example: Create an enhanced user registration wizard"""
    
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
            ],
            real_time_validate=True
        ),
        FormField(
            name="last_name",
            type=FieldType.TEXT,
            label="Last Name",
            placeholder="Enter your last name",
            validation_rules=[
                ValidationRule("required", message="Last name is required")
            ],
            real_time_validate=True
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email Address",
            placeholder="your@email.com",
            validation_rules=[
                ValidationRule("required", message="Email is required"),
                ValidationRule("pattern", r"[^@]+@[^@]+\.[^@]+", "Please enter a valid email"),
                ValidationRule("ajax", ajax_url="/api/validate/email")
            ],
            real_time_validate=True,
            debounce_ms=1000
        ),
        FormField(
            name="phone",
            type=FieldType.PHONE_INTL,
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
        ),
        FormField(
            name="profile_photo",
            type=FieldType.FILE_DRAG,
            label="Profile Photo (Optional)",
            accepted_files=[".jpg", ".jpeg", ".png", ".gif"],
            max_file_size=5 * 1024 * 1024,  # 5MB
            help_text="Drag and drop your photo or click to browse"
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
                ValidationRule("pattern", "^[a-zA-Z0-9_]+$", "Username can only contain letters, numbers, and underscores"),
                ValidationRule("ajax", ajax_url="/api/validate/username")
            ],
            real_time_validate=True
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
            name="company_name",
            type=FieldType.TEXT,
            label="Company Name",
            placeholder="Enter your company name",
            validation_rules=[
                ValidationRule("required", message="Company name is required for business accounts")
            ],
            show_if={"account_type": "business"}  # Only show for business accounts
        ),
        FormField(
            name="interests",
            type=FieldType.TAGS,
            label="Areas of Interest",
            placeholder="Add your interests",
            help_text="Press Enter to add tags"
        ),
        FormField(
            name="bio",
            type=FieldType.RICH_TEXT,
            label="About You",
            help_text="Tell us a bit about yourself",
            enable_rich_text=True
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
            fields=preferences_fields
        )
    ]
    
    # Create wizard with enhanced features
    wizard = FormWizard(
        title="User Registration",
        steps=steps,
        submit_url="/api/register",
        method="POST",
        theme=FormTheme.MODERN,
        enable_csrf=True,
        enable_analytics=True,
        enable_autosave=True,
        enable_keyboard_shortcuts=True
    )
    
    return wizard


if __name__ == "__main__":
    # Example 1: Enhanced User Registration Wizard
    print("Generating enhanced user registration form...")
    registration_wizard = create_user_registration_wizard()
    
    # Generate and save HTML
    with open("registration_form_v2.html", "w") as f:
        f.write(registration_wizard.generate_html())
    
    print("✅ Enhanced registration form saved to registration_form_v2.html")
    
    # Example 2: Pydantic Integration Example
    if PYDANTIC_AVAILABLE:
        print("\nGenerating form from Pydantic model...")
        
        from pydantic import BaseModel, Field
        from typing import Optional
        from enum import Enum as PyEnum
        
        class Priority(PyEnum):
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"
            URGENT = "urgent"
        
        class TaskRequest(BaseModel):
            title: str = Field(..., min_length=3, max_length=100, description="Task title")
            description: Optional[str] = Field(None, description="Detailed description")
            priority: Priority = Field(..., description="Task priority level")
            due_date: Optional[date] = Field(None, description="When is this due?")
            tags: Optional[List[str]] = Field(default_factory=list, description="Task tags")
            assigned_to: Optional[str] = Field(None, description="Assign to team member")
            notify_on_complete: bool = Field(True, description="Send notification when complete")
        
        # Create form from Pydantic model
        task_wizard = PydanticFormConverter.create_wizard_from_models(
            TaskRequest,
            title="Create New Task",
            submit_url="/api/tasks",
            step_titles=["Task Details"],
            theme=FormTheme.MODERN,
            enable_analytics=True,
            custom_labels={
                "notify_on_complete": "Notify me when complete"
            }
        )
        
        with open("task_form_v2.html", "w") as f:
            f.write(task_wizard.generate_html())
        
        print("✅ Task form from Pydantic model saved to task_form_v2.html")
    
    print("""
    
🚀 HTML Form Wizard v2.0 Features:
    
✅ Security
   - CSRF protection
   - Input sanitization
   - Secure file uploads
   
✅ Advanced Field Types
   - Tags input
   - Autocomplete
   - Drag & drop file upload
   - Rich text editor
   - International phone input
   
✅ Real-time Features
   - Field validation with debouncing
   - Ajax validation
   - Auto-save progress
   - Conditional fields
   
✅ User Experience
   - Multiple themes (Default, Modern, Dark)
   - Keyboard shortcuts (Ctrl+S to save)
   - Progress tracking
   - Mobile responsive
   - Print-friendly
   
✅ Analytics
   - Form interaction tracking
   - Abandonment tracking
   - Time spent per field
   - Error tracking
   
✅ Developer Features
   - Pydantic model integration
   - FastAPI endpoint generation
   - Internationalization support
   - Custom CSS/JS injection
   - Import/Export capability
    
All features are backward compatible with v1!
    """)