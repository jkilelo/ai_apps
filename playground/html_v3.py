#!/usr/bin/env python3
"""
Dynamic HTML Form Chain Engine v3.0 - Forms as Input-Output Processors

This revolutionary approach treats forms as first-class input-output parameters in a 
processing chain. Each step in the chain has a Pydantic model for its request (input) 
and response (output), with the response of one step becoming part of the input for 
the next step.

Key Features:
- Form chains with entry and exit points
- Automatic form generation from Pydantic models
- Response data flows into next form
- Dynamic field injection based on previous responses
- State management across the chain
- Type-safe form processing pipeline
"""

import json
import secrets
import hashlib
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple, get_type_hints, get_args, get_origin
from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from datetime import datetime, date, time
from decimal import Decimal
import inspect
import base64
from abc import ABC, abstractmethod

# Pydantic is required for v3
try:
    from pydantic import BaseModel, Field, ValidationError, validator
    try:
        # Pydantic v2 - check for v2-specific attribute
        from pydantic import __version__
        PYDANTIC_V2 = int(__version__.split('.')[0]) >= 2
        if PYDANTIC_V2:
            from pydantic_core import PydanticUndefined
    except:
        PYDANTIC_V2 = False
        PydanticUndefined = None
except ImportError:
    raise ImportError("html_v3.py requires Pydantic. Install with: pip install pydantic")


class ChainState(Enum):
    """States of the form chain execution"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


class FieldType(Enum):
    """Supported HTML form field types"""
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
    TAGS = "tags"
    AUTOCOMPLETE = "autocomplete"
    JSON = "json"
    ARRAY = "array"


@dataclass
class FormFieldSpec:
    """Specification for a form field"""
    name: str
    field_type: FieldType
    label: str
    required: bool = False
    default: Any = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    validators: List[Dict[str, Any]] = dataclass_field(default_factory=list)
    options: Optional[List[Dict[str, str]]] = None
    attributes: Dict[str, Any] = dataclass_field(default_factory=dict)
    

class FormStepProcessor(ABC):
    """Abstract base class for processing form steps"""
    
    @abstractmethod
    async def process(self, input_data: BaseModel, chain_context: Dict[str, Any]) -> BaseModel:
        """Process the input and return the response"""
        pass


@dataclass
class FormStep:
    """Represents a single step in the form chain"""
    id: str
    title: str
    description: str
    request_model: Type[BaseModel]
    response_model: Type[BaseModel]
    processor: Optional[FormStepProcessor] = None
    is_entry_point: bool = False
    is_exit_point: bool = False
    next_step_id: Optional[str] = None
    conditional_next: Optional[Callable[[BaseModel], str]] = None
    inject_fields: Optional[Callable[[BaseModel], List[FormFieldSpec]]] = None


class FormChainEngine:
    """The main engine that manages form chains"""
    
    def __init__(
        self,
        chain_id: str,
        title: str,
        description: str,
        steps: List[FormStep],
        theme: str = "modern",
        enable_state_persistence: bool = True,
        state_storage_key: Optional[str] = None
    ):
        self.chain_id = chain_id
        self.title = title
        self.description = description
        self.steps = {step.id: step for step in steps}
        self.step_order = [step.id for step in steps]
        self.theme = theme
        self.enable_state_persistence = enable_state_persistence
        self.state_storage_key = state_storage_key or f"form_chain_{chain_id}"
        
        # Validate chain structure
        self._validate_chain()
        
        # Generate CSRF token
        # self.csrf_token = secrets.token_urlsafe(32)  # Disabled CSRF for now
        
    def _validate_chain(self):
        """Validate the form chain structure"""
        entry_points = [s for s in self.steps.values() if s.is_entry_point]
        exit_points = [s for s in self.steps.values() if s.is_exit_point]
        
        if len(entry_points) != 1:
            raise ValueError(f"Chain must have exactly 1 entry point, found {len(entry_points)}")
        
        if len(exit_points) < 1:
            raise ValueError("Chain must have at least 1 exit point")
        
        # Validate step connections
        for step in self.steps.values():
            if not step.is_exit_point and not step.next_step_id and not step.conditional_next:
                raise ValueError(f"Step {step.id} must have next_step_id or conditional_next")
    
    def get_entry_point(self) -> FormStep:
        """Get the entry point step"""
        return next(s for s in self.steps.values() if s.is_entry_point)
    
    def model_to_field_specs(
        self, 
        model: Type[BaseModel], 
        prefix: str = "",
        defaults: Optional[Dict[str, Any]] = None
    ) -> List[FormFieldSpec]:
        """Convert a Pydantic model to form field specifications"""
        fields = []
        defaults = defaults or {}
        
        if PYDANTIC_V2:
            model_fields = model.model_fields
        else:
            model_fields = model.__fields__
        
        for field_name, field_info in model_fields.items():
            full_name = f"{prefix}{field_name}" if prefix else field_name
            
            # Get field type and metadata
            if PYDANTIC_V2:
                field_type = field_info.annotation
                is_required = field_info.is_required()
                default_value = field_info.default
                # Handle PydanticUndefined
                if PydanticUndefined and default_value is PydanticUndefined:
                    default_value = None
                field_description = field_info.description
            else:
                # Pydantic v1 - field_info is a ModelField
                field_type = field_info.outer_type_ if hasattr(field_info, 'outer_type_') else field_info.type_
                is_required = field_info.required
                default_value = field_info.default
                field_description = field_info.field_info.description if hasattr(field_info, 'field_info') else None
            
            # Handle optional types
            origin = get_origin(field_type)
            if origin is Union:
                args = get_args(field_type)
                if type(None) in args:
                    field_type = next(arg for arg in args if arg is not type(None))
                    is_required = False
            
            # Determine HTML field type
            html_field_type = self._python_type_to_field_type(field_type)
            
            # Special handling for string fields that should be textareas
            if html_field_type == FieldType.TEXT and field_name.lower() in [
                'message', 'description', 'content', 'body', 'text', 'notes', 
                'comments', 'details', 'summary', 'bio', 'about'
            ]:
                html_field_type = FieldType.TEXTAREA
            
            # Get options for enum fields
            options = None
            if inspect.isclass(field_type) and issubclass(field_type, Enum):
                options = [{"value": e.value, "label": e.name} for e in field_type]
            
            # Create field spec
            field_spec = FormFieldSpec(
                name=full_name,
                field_type=html_field_type,
                label=field_name.replace("_", " ").title(),
                required=is_required,
                default=defaults.get(full_name, default_value if default_value is not None else None),
                help_text=field_description,
                options=options
            )
            
            fields.append(field_spec)
        
        return fields
    
    def _python_type_to_field_type(self, python_type: Type) -> FieldType:
        """Convert Python type to HTML field type"""
        type_mapping = {
            str: FieldType.TEXT,
            int: FieldType.NUMBER,
            float: FieldType.NUMBER,
            bool: FieldType.CHECKBOX,
            date: FieldType.DATE,
            time: FieldType.TIME,
            datetime: FieldType.DATETIME,
            list: FieldType.ARRAY,
            dict: FieldType.JSON,
        }
        
        # Check for specific string patterns
        if python_type == str:
            return FieldType.TEXT
        
        # Check for generic types
        origin = get_origin(python_type)
        if origin is list:
            return FieldType.ARRAY
        elif origin is dict:
            return FieldType.JSON
        
        # Check enum
        if inspect.isclass(python_type) and issubclass(python_type, Enum):
            return FieldType.SELECT
        
        return type_mapping.get(python_type, FieldType.TEXT)
    
    def generate_form_html(
        self,
        step_id: str,
        chain_state: Optional[Dict[str, Any]] = None,
        previous_response: Optional[BaseModel] = None
    ) -> str:
        """Generate HTML for a specific step in the chain"""
        step = self.steps.get(step_id)
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        # Get base fields from request model
        fields = self.model_to_field_specs(step.request_model)
        
        # If there's a previous response, use it to populate defaults
        defaults = {}
        if previous_response:
            if PYDANTIC_V2:
                prev_data = previous_response.model_dump()
            else:
                prev_data = previous_response.dict()
            defaults.update(prev_data)
        
        # Apply defaults to fields
        for field in fields:
            if field.name in defaults:
                field.default = defaults[field.name]
        
        # Inject additional fields if specified
        if step.inject_fields and previous_response:
            injected_fields = step.inject_fields(previous_response)
            fields.extend(injected_fields)
        
        # Generate HTML
        return self._render_form_html(step, fields, chain_state)
    
    def _render_form_html(
        self,
        step: FormStep,
        fields: List[FormFieldSpec],
        chain_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render the HTML for a form step"""
        
        # Generate form fields HTML
        fields_html = ""
        for field in fields:
            fields_html += self._render_field(field)
        
        # Calculate progress
        current_index = self.step_order.index(step.id)
        progress = (current_index / len(self.step_order)) * 100
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title} - {step.title}</title>
    {self._get_styles()}
</head>
<body>
    <div class="form-chain-container">
        <div class="chain-header">
            <h1>{self.title}</h1>
            <p class="chain-description">{self.description}</p>
            
            <div class="progress-container">
                <div class="progress-bar" style="width: {progress}%"></div>
                <div class="progress-text">Step {current_index + 1} of {len(self.step_order)}</div>
            </div>
        </div>
        
        <div class="step-container">
            <h2>{step.title}</h2>
            <p class="step-description">{step.description}</p>
            
            <form id="chainForm" method="POST" action="/api/chain/{self.chain_id}/process/{step.id}">
                <!-- <input type="hidden" name="csrf_token" value=""> --> <!-- CSRF disabled -->
                <input type="hidden" name="chain_state" value="{self._encode_state(chain_state)}">
                
                <div class="form-fields">
                    {fields_html}
                </div>
                
                <div class="form-actions">
                    {"" if step.is_entry_point else '<button type="button" class="btn-secondary" onclick="history.back()">Previous</button>'}
                    <button type="submit" class="btn-primary">
                        {"Complete" if step.is_exit_point else "Next"}
                    </button>
                </div>
            </form>
        </div>
        
        {self._get_chain_visualization(step.id)}
    </div>
    
    {self._get_scripts()}
</body>
</html>
"""
        return html
    
    def _safe_default(self, value: Any) -> Any:
        """Safely handle default values, converting PydanticUndefined to None"""
        if PYDANTIC_V2 and PydanticUndefined and value is PydanticUndefined:
            return None
        return value
    
    def _render_field(self, field: FormFieldSpec) -> str:
        """Render a single form field"""
        field_id = f"field_{field.name}"
        required_attr = "required" if field.required else ""
        
        # Safely get default value
        safe_default = self._safe_default(field.default)
        
        # Base attributes
        attrs = {
            "id": field_id,
            "name": field.name,
            "class": "form-control"
        }
        
        if field.placeholder:
            attrs["placeholder"] = field.placeholder
        
        # Merge with custom attributes
        attrs.update(field.attributes)
        
        # Convert to string
        attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        
        # Field HTML based on type
        field_html = ""
        
        if field.field_type == FieldType.SELECT and field.options:
            options_html = ""
            for opt in field.options:
                selected = "selected" if opt["value"] == safe_default else ""
                options_html += f'<option value="{opt["value"]}" {selected}>{opt["label"]}</option>'
            
            field_html = f'<select {attrs_str} {required_attr}>{options_html}</select>'
            
        elif field.field_type == FieldType.TEXTAREA:
            field_html = f'<textarea {attrs_str} rows="4" {required_attr}>{safe_default or ""}</textarea>'
            
        elif field.field_type == FieldType.CHECKBOX:
            checked = "checked" if safe_default else ""
            field_html = f'<input type="checkbox" {attrs_str} {checked}>'
            
        elif field.field_type == FieldType.ARRAY:
            field_html = f"""
                <div class="array-field" data-field-name="{field.name}">
                    <div class="array-items"></div>
                    <button type="button" class="btn-add-item" onclick="addArrayItem('{field.name}')">Add Item</button>
                </div>
                <input type="hidden" name="{field.name}" id="{field_id}" value='{json.dumps(safe_default or [])}'>
            """
            
        elif field.field_type == FieldType.JSON:
            field_html = f"""
                <textarea {attrs_str} rows="6" {required_attr} class="json-editor">{json.dumps(safe_default or {}, indent=2)}</textarea>
            """
            
        else:
            input_type = field.field_type.value
            value_attr = f'value="{safe_default}"' if safe_default is not None else ""
            field_html = f'<input type="{input_type}" {attrs_str} {value_attr} {required_attr}>'
        
        # Wrap in field container
        return f"""
        <div class="form-field">
            <label for="{field_id}" class="{"required" if field.required else ""}">
                {field.label}
            </label>
            {field_html}
            {f'<small class="help-text">{field.help_text}</small>' if field.help_text else ''}
        </div>
        """
    
    def _get_chain_visualization(self, current_step_id: str) -> str:
        """Generate a visualization of the form chain"""
        nodes = []
        
        for step_id in self.step_order:
            step = self.steps[step_id]
            status = "completed" if self.step_order.index(step_id) < self.step_order.index(current_step_id) else \
                     "current" if step_id == current_step_id else "pending"
            
            nodes.append(f"""
                <div class="chain-node {status}">
                    <div class="node-icon">{"✓" if status == "completed" else self.step_order.index(step_id) + 1}</div>
                    <div class="node-title">{step.title}</div>
                </div>
            """)
        
        return f"""
        <div class="chain-visualization">
            <h3>Process Flow</h3>
            <div class="chain-nodes">
                {"".join(nodes)}
            </div>
        </div>
        """
    
    def _encode_state(self, state: Optional[Dict[str, Any]]) -> str:
        """Encode chain state for transmission"""
        if not state:
            return ""
        
        # Convert to JSON and base64 encode
        json_str = json.dumps(state)
        return base64.b64encode(json_str.encode()).decode()
    
    def _decode_state(self, encoded_state: str) -> Dict[str, Any]:
        """Decode chain state"""
        if not encoded_state:
            return {}
        
        try:
            json_str = base64.b64decode(encoded_state.encode()).decode()
            return json.loads(json_str)
        except:
            return {}
    
    def _get_styles(self) -> str:
        """Get CSS styles for the form chain"""
        return """
    <style>
        * { box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f6fa;
            margin: 0;
            padding: 0;
        }
        
        .form-chain-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .chain-header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .chain-header h1 {
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 2em;
        }
        
        .chain-description {
            color: #7f8c8d;
            margin: 0 0 20px 0;
        }
        
        .progress-container {
            background: #ecf0f1;
            border-radius: 20px;
            height: 40px;
            position: relative;
            overflow: hidden;
        }
        
        .progress-bar {
            background: linear-gradient(135deg, #3498db, #2980b9);
            height: 100%;
            border-radius: 20px;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #2c3e50;
            font-weight: 500;
        }
        
        .step-container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .step-container h2 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        
        .step-description {
            color: #7f8c8d;
            margin: 0 0 30px 0;
        }
        
        .form-fields {
            margin-bottom: 30px;
        }
        
        .form-field {
            margin-bottom: 25px;
        }
        
        .form-field label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 500;
        }
        
        .form-field label.required::after {
            content: " *";
            color: #e74c3c;
        }
        
        .form-control {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        
        .help-text {
            display: block;
            margin-top: 5px;
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .form-actions {
            display: flex;
            gap: 15px;
            justify-content: flex-end;
        }
        
        .btn-primary, .btn-secondary {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #3498db;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        }
        
        .btn-secondary {
            background: #ecf0f1;
            color: #2c3e50;
        }
        
        .btn-secondary:hover {
            background: #bdc3c7;
        }
        
        /* Chain Visualization */
        .chain-visualization {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 12px;
            margin-top: 30px;
        }
        
        .chain-visualization h3 {
            margin: 0 0 20px 0;
            color: #2c3e50;
        }
        
        .chain-nodes {
            display: flex;
            gap: 20px;
            overflow-x: auto;
            padding: 10px 0;
        }
        
        .chain-node {
            flex-shrink: 0;
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
            min-width: 120px;
        }
        
        .chain-node::after {
            content: "→";
            position: absolute;
            right: -25px;
            top: 50%;
            transform: translateY(-50%);
            color: #bdc3c7;
            font-size: 20px;
        }
        
        .chain-node:last-child::after {
            display: none;
        }
        
        .chain-node.completed {
            background: #d4edda;
            color: #155724;
        }
        
        .chain-node.current {
            background: #cce5ff;
            color: #004085;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
        }
        
        .chain-node.pending {
            opacity: 0.6;
        }
        
        .node-icon {
            font-size: 24px;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .node-title {
            font-size: 14px;
        }
        
        /* Array fields */
        .array-field {
            border: 2px dashed #ecf0f1;
            padding: 15px;
            border-radius: 8px;
        }
        
        .array-items {
            margin-bottom: 10px;
        }
        
        .array-item {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .array-item input {
            flex: 1;
        }
        
        .btn-remove-item {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .btn-add-item {
            background: #27ae60;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        
        /* JSON editor */
        .json-editor {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            background: #f8f9fa;
        }
        
        /* Loading states */
        .loading {
            opacity: 0.6;
            pointer-events: none;
            position: relative;
        }
        
        .loading::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            margin: -10px;
            border: 2px solid #3498db;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .form-chain-container {
                padding: 10px;
            }
            
            .chain-header, .step-container {
                padding: 20px;
            }
            
            .chain-nodes {
                flex-direction: column;
                gap: 10px;
            }
            
            .chain-node::after {
                display: none;
            }
        }
    </style>
        """
    
    def _get_scripts(self) -> str:
        """Get JavaScript for the form chain"""
        return """
    <script>
        // Array field handling
        function addArrayItem(fieldName) {
            const container = document.querySelector(`[data-field-name="${fieldName}"] .array-items`);
            const itemDiv = document.createElement('div');
            itemDiv.className = 'array-item';
            itemDiv.innerHTML = `
                <input type="text" class="form-control" placeholder="Item value">
                <button type="button" class="btn-remove-item" onclick="removeArrayItem(this)">Remove</button>
            `;
            container.appendChild(itemDiv);
            updateArrayField(fieldName);
        }
        
        function removeArrayItem(button) {
            const fieldName = button.closest('.array-field').dataset.fieldName;
            button.parentElement.remove();
            updateArrayField(fieldName);
        }
        
        function updateArrayField(fieldName) {
            const container = document.querySelector(`[data-field-name="${fieldName}"]`);
            const inputs = container.querySelectorAll('.array-items input');
            const values = Array.from(inputs).map(input => input.value).filter(v => v);
            document.getElementById(`field_${fieldName}`).value = JSON.stringify(values);
        }
        
        // Form submission handling
        document.getElementById('chainForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const form = e.target;
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.classList.add('loading');
            
            try {
                // Validate JSON fields
                form.querySelectorAll('.json-editor').forEach(textarea => {
                    try {
                        JSON.parse(textarea.value);
                    } catch (err) {
                        throw new Error(`Invalid JSON in field: ${textarea.name}`);
                    }
                });
                
                // Submit form
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    
                    if (result.next_form_html) {
                        // Replace the entire page with the next form
                        document.open();
                        document.write(result.next_form_html);
                        document.close();
                    } else if (result.redirect_url) {
                        window.location.href = result.redirect_url;
                    } else if (result.completed) {
                        // Show completion message
                        document.body.innerHTML = `
                            <div class="form-chain-container">
                                <div class="step-container" style="text-align: center;">
                                    <h2>✅ Process Completed!</h2>
                                    <p>${result.message || 'The form chain has been completed successfully.'}</p>
                                    <pre style="text-align: left; background: #f8f9fa; padding: 20px; border-radius: 8px;">
${JSON.stringify(result.final_data, null, 2)}
                                    </pre>
                                </div>
                            </div>
                        `;
                    }
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.detail || 'Form submission failed'}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            } finally {
                submitBtn.classList.remove('loading');
            }
        });
        
        // Auto-save form state
        function saveFormState() {
            const formData = new FormData(document.getElementById('chainForm'));
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            localStorage.setItem('""" + self.state_storage_key + """', JSON.stringify(data));
        }
        
        // Restore form state
        function restoreFormState() {
            const saved = localStorage.getItem('""" + self.state_storage_key + """');
            if (saved) {
                try {
                    const data = JSON.parse(saved);
                    const form = document.getElementById('chainForm');
                    
                    for (let [key, value] of Object.entries(data)) {
                        const field = form.elements[key];
                        if (field && field.name !== 'csrf_token' && field.name !== 'chain_state') {
                            field.value = value;
                        }
                    }
                } catch (err) {
                    console.error('Failed to restore form state:', err);
                }
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            restoreFormState();
            
            // Auto-save on input
            document.getElementById('chainForm').addEventListener('input', saveFormState);
            
            // Initialize array fields
            document.querySelectorAll('input[type="hidden"][value^="["]').forEach(input => {
                try {
                    const values = JSON.parse(input.value);
                    const fieldName = input.name;
                    values.forEach(value => {
                        addArrayItem(fieldName);
                        const container = document.querySelector(`[data-field-name="${fieldName}"]`);
                        const lastInput = container.querySelector('.array-items .array-item:last-child input');
                        if (lastInput) lastInput.value = value;
                    });
                } catch (err) {
                    console.error('Failed to initialize array field:', err);
                }
            });
        });
    </script>
        """
    
    async def process_step(
        self,
        step_id: str,
        form_data: Dict[str, Any],
        chain_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a form step and determine the next action"""
        
        step = self.steps.get(step_id)
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        # Validate and parse input data
        try:
            input_model = step.request_model(**form_data)
        except ValidationError as e:
            return {
                "error": True,
                "errors": e.errors(),
                "message": "Validation failed"
            }
        
        # Process the step
        try:
            if step.processor:
                response_model = await step.processor.process(input_model, chain_state)
            else:
                # Default processing - just pass through
                response_model = step.response_model(**form_data)
        except Exception as e:
            return {
                "error": True,
                "errors": [{"msg": str(e)}],
                "message": f"Processing error: {str(e)}"
            }
        
        # Update chain state
        chain_state[f"step_{step_id}_request"] = form_data
        if PYDANTIC_V2:
            response_dict = response_model.model_dump()
        else:
            response_dict = response_model.dict()
        
        # Convert Decimal and date types to string for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(v) for v in obj]
            elif isinstance(obj, Decimal):
                return str(obj)
            elif isinstance(obj, (date, datetime)):
                return obj.isoformat()
            return obj
        
        chain_state[f"step_{step_id}_response"] = convert_for_json(response_dict)
        
        # Determine next step
        if step.is_exit_point:
            return {
                "completed": True,
                "final_data": chain_state,
                "message": "Form chain completed successfully!"
            }
        
        # Get next step ID
        if step.conditional_next:
            next_step_id = step.conditional_next(response_model)
        else:
            next_step_id = step.next_step_id
        
        if not next_step_id:
            raise ValueError(f"No next step defined for {step_id}")
        
        # Generate next form
        next_form_html = self.generate_form_html(next_step_id, chain_state, response_model)
        
        return {
            "next_step_id": next_step_id,
            "next_form_html": next_form_html,
            "chain_state": chain_state
        }


# Helper function for creating form chains from models
def create_form_chain(
    chain_id: str,
    title: str,
    description: str,
    models: List[Tuple[Type[BaseModel], Type[BaseModel], Optional[FormStepProcessor]]],
    step_titles: Optional[List[str]] = None,
    step_descriptions: Optional[List[str]] = None
) -> FormChainEngine:
    """
    Create a form chain from a list of request/response model pairs
    
    Args:
        chain_id: Unique identifier for the chain
        title: Title of the form chain
        description: Description of the form chain
        models: List of tuples (request_model, response_model, processor)
        step_titles: Optional list of step titles
        step_descriptions: Optional list of step descriptions
    """
    
    steps = []
    
    for i, (request_model, response_model, processor) in enumerate(models):
        step = FormStep(
            id=f"step_{i+1}",
            title=step_titles[i] if step_titles else f"Step {i+1}",
            description=step_descriptions[i] if step_descriptions else f"Complete step {i+1}",
            request_model=request_model,
            response_model=response_model,
            processor=processor,
            is_entry_point=(i == 0),
            is_exit_point=(i == len(models) - 1),
            next_step_id=f"step_{i+2}" if i < len(models) - 1 else None
        )
        steps.append(step)
    
    return FormChainEngine(
        chain_id=chain_id,
        title=title,
        description=description,
        steps=steps
    )


# Example processor for demonstration
class EchoProcessor(FormStepProcessor):
    """Simple processor that echoes input with a timestamp"""
    
    async def process(self, input_data: BaseModel, chain_context: Dict[str, Any]) -> BaseModel:
        # Get the response model class from the type hints
        response_model = self.__class__.__annotations__.get('response_model', BaseModel)
        
        # Create response with input data plus timestamp
        if PYDANTIC_V2:
            data = input_data.model_dump()
        else:
            data = input_data.dict()
            
        data['processed_at'] = datetime.now().isoformat()
        
        return response_model(**data)


# Export main classes and functions
__all__ = [
    'FormChainEngine',
    'FormStep',
    'FormStepProcessor',
    'FormFieldSpec',
    'ChainState',
    'FieldType',
    'create_form_chain',
    'EchoProcessor'
]