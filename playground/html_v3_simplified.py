#!/usr/bin/env python3
"""
HTML Form Chain Engine v3 - SIMPLIFIED VERSION

Core improvements:
1. Server-side session storage (no JSON in hidden fields)
2. Pure HTML forms with POST-Redirect-GET pattern
3. No JavaScript required for basic functionality
4. Type-safe form handling
5. Clean error handling
"""

from typing import Dict, List, Any, Optional, Type, Union, Callable, Tuple
from pydantic import BaseModel, Field, ValidationError
from abc import ABC, abstractmethod
from enum import Enum
import uuid
from datetime import datetime
import inspect
from dataclasses import dataclass
from urllib.parse import urlencode


# In-memory session storage (use Redis in production)
SESSIONS: Dict[str, Dict[str, Any]] = {}


class FieldType(Enum):
    """Supported HTML field types"""
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    PASSWORD = "password"
    DATE = "date"
    DATETIME = "datetime-local"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    HIDDEN = "hidden"
    FILE = "file"
    ARRAY = "array"  # Special handling for lists
    BOOLEAN = "checkbox"  # Maps to checkbox


@dataclass
class FormFieldSpec:
    """Specification for a form field"""
    name: str
    field_type: FieldType
    label: str
    required: bool = True
    default: Any = None
    help_text: Optional[str] = None
    options: Optional[List[Union[str, Dict[str, str]]]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    placeholder: Optional[str] = None


class FormStepProcessor(ABC):
    """Abstract processor for form steps"""
    
    @abstractmethod
    async def process(self, input_data: BaseModel, session_data: Dict[str, Any]) -> BaseModel:
        """Process form input and return response model"""
        pass


@dataclass
class FormStep:
    """Definition of a single step in the form chain"""
    id: str
    title: str
    description: str
    request_model: Type[BaseModel]
    response_model: Type[BaseModel]
    processor: Optional[FormStepProcessor] = None
    is_entry_point: bool = False
    is_exit_point: bool = False
    next_step_id: Optional[str] = None
    
    def get_field_specs(self) -> List[FormFieldSpec]:
        """Extract field specifications from the request model"""
        fields = []
        
        model_fields = self.request_model.__fields__ if hasattr(self.request_model, '__fields__') else self.request_model.model_fields
        
        for field_name, field_info in model_fields.items():
            # Get field type
            field_type = field_info.annotation if hasattr(field_info, 'annotation') else field_info.type_
            
            # Map Python type to HTML field type
            html_type = self._get_html_type(field_type)
            
            # Extract field properties
            if hasattr(field_info, 'field_info'):
                # Pydantic v1
                fi = field_info.field_info
                required = field_info.required
            else:
                # Pydantic v2
                fi = field_info
                required = field_info.is_required()
            
            default = fi.default if fi.default is not None else None
            # Handle PydanticUndefined
            if default is not None and str(default) == "PydanticUndefined":
                default = None
            
            # Get options for enum fields
            options = None
            if inspect.isclass(field_type) and issubclass(field_type, Enum):
                options = [{"value": e.value, "label": e.name} for e in field_type]
            
            fields.append(FormFieldSpec(
                name=field_name,
                field_type=html_type,
                label=field_name.replace('_', ' ').title(),
                required=required,
                default=default,
                help_text=fi.description if hasattr(fi, 'description') else None,
                options=options
            ))
        
        return fields
    
    def _get_html_type(self, python_type: Type) -> FieldType:
        """Map Python type to HTML field type"""
        # Handle Optional types
        if hasattr(python_type, '__origin__'):
            if python_type.__origin__ is Union:
                # Get the non-None type
                args = [t for t in python_type.__args__ if t is not type(None)]
                if args:
                    python_type = args[0]
        
        # Basic type mapping
        type_map = {
            str: FieldType.TEXT,
            int: FieldType.NUMBER,
            float: FieldType.NUMBER,
            bool: FieldType.BOOLEAN,
            datetime: FieldType.DATETIME,
        }
        
        # Check if it's a list
        if hasattr(python_type, '__origin__') and python_type.__origin__ is list:
            return FieldType.ARRAY
        
        # Check if it's an enum
        if inspect.isclass(python_type) and issubclass(python_type, Enum):
            return FieldType.SELECT
        
        return type_map.get(python_type, FieldType.TEXT)


class SimplifiedFormChain:
    """Simplified form chain engine using server-side sessions"""
    
    def __init__(self, steps: List[FormStep]):
        self.steps = {step.id: step for step in steps}
        self.step_order = [step.id for step in steps]
        
        # Validate chain
        entry_points = [s for s in steps if s.is_entry_point]
        if len(entry_points) != 1:
            raise ValueError("Chain must have exactly one entry point")
    
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {
            "created_at": datetime.now().isoformat(),
            "current_step": None,
            "data": {}
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return SESSIONS.get(session_id)
    
    def render_step(self, step_id: str, session_id: str, errors: Optional[List[str]] = None) -> str:
        """Render a form step as pure HTML"""
        step = self.steps.get(step_id)
        if not step:
            return self._render_error("Step not found")
        
        session = self.get_session(session_id)
        if not session:
            return self._render_error("Session expired")
        
        # Get fields from model
        fields = step.get_field_specs()
        
        # Get previous step data for pre-population
        # Look for defaults from the previous step
        prev_data = session["data"].get(f"{step_id}_defaults", {})
        # Also check if this step has stored request data (e.g., on error)
        if f"step_{step_id}_request" in session["data"]:
            prev_data.update(session["data"][f"step_{step_id}_request"])
        
        # Build form HTML
        fields_html = ""
        for field in fields:
            # Get value, handling PydanticUndefined
            default_value = field.default
            if default_value is not None and str(default_value) == "PydanticUndefined":
                default_value = ""
            value = prev_data.get(field.name, default_value if default_value is not None else "")
            fields_html += self._render_field(field, value)
        
        # Calculate progress
        current_index = self.step_order.index(step_id) if step_id in self.step_order else 0
        progress = int((current_index / len(self.step_order)) * 100)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{step.title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: system-ui, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .progress {{
            height: 4px;
            background: #e0e0e0;
            margin-bottom: 30px;
            border-radius: 2px;
            overflow: hidden;
        }}
        .progress-bar {{
            height: 100%;
            background: #4CAF50;
            width: {progress}%;
            transition: width 0.3s;
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .description {{
            color: #666;
            margin-bottom: 30px;
        }}
        .field {{
            margin-bottom: 20px;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #333;
        }}
        input, select, textarea {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }}
        input:focus, select:focus, textarea:focus {{
            outline: none;
            border-color: #4CAF50;
        }}
        .help-text {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .error {{
            background: #fee;
            border: 1px solid #fcc;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            color: #c00;
        }}
        .actions {{
            margin-top: 30px;
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }}
        button {{
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .btn-primary {{
            background: #4CAF50;
            color: white;
        }}
        .btn-primary:hover {{
            background: #45a049;
        }}
        .btn-secondary {{
            background: #f0f0f0;
            color: #333;
        }}
        .array-field {{
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 4px;
            background: #fafafa;
        }}
        .array-item {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .array-item input {{
            flex: 1;
        }}
        .array-item button {{
            padding: 5px 10px;
            background: #f44336;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        .btn-add {{
            padding: 5px 15px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="progress">
            <div class="progress-bar"></div>
        </div>
        
        <h1>{step.title}</h1>
        <p class="description">{step.description}</p>
        
        {self._render_errors(errors)}
        
        <form method="POST" action="/process/{session_id}/{step_id}">
            {fields_html}
            
            <div class="actions">
                {'' if step.is_entry_point else '<button type="button" class="btn-secondary" onclick="history.back()">Back</button>'}
                <button type="submit" class="btn-primary">
                    {('Finish' if step.is_exit_point else 'Next')}
                </button>
            </div>
        </form>
    </div>
    
    <script>
        // Minimal JavaScript for array fields only
        function addArrayItem(fieldName) {{
            const container = document.getElementById(fieldName + '_items');
            const item = document.createElement('div');
            item.className = 'array-item';
            item.innerHTML = `
                <input type="text" name="${{fieldName}}[]" required>
                <button type="button" onclick="this.parentElement.remove()">Remove</button>
            `;
            container.appendChild(item);
        }}
    </script>
</body>
</html>
"""
        return html
    
    def _render_field(self, field: FormFieldSpec, value: Any) -> str:
        """Render a single form field"""
        required = "required" if field.required else ""
        
        if field.field_type == FieldType.ARRAY:
            # Special handling for arrays
            items_html = ""
            if isinstance(value, list):
                for item in value:
                    items_html += f'''
                    <div class="array-item">
                        <input type="text" name="{field.name}[]" value="{item}" {required}>
                        <button type="button" onclick="this.parentElement.remove()">Remove</button>
                    </div>
                    '''
            
            return f"""
            <div class="field">
                <label>{field.label}</label>
                <div class="array-field">
                    <div id="{field.name}_items">
                        {items_html}
                    </div>
                    <button type="button" class="btn-add" onclick="addArrayItem('{field.name}')">Add Item</button>
                </div>
                {f'<div class="help-text">{field.help_text}</div>' if field.help_text else ''}
            </div>
            """
        
        elif field.field_type == FieldType.SELECT:
            options_html = ""
            if field.options:
                # Handle enum values
                compare_value = value
                if hasattr(value, 'value'):
                    # It's an enum, get its value
                    compare_value = value.value
                    
                for opt in field.options:
                    if isinstance(opt, dict):
                        selected = "selected" if opt["value"] == compare_value else ""
                        options_html += f'<option value="{opt["value"]}" {selected}>{opt["label"]}</option>'
                    else:
                        selected = "selected" if opt == compare_value else ""
                        options_html += f'<option value="{opt}" {selected}>{opt}</option>'
            
            return f"""
            <div class="field">
                <label for="{field.name}">{field.label}</label>
                <select id="{field.name}" name="{field.name}" {required}>
                    <option value="">Select...</option>
                    {options_html}
                </select>
                {f'<div class="help-text">{field.help_text}</div>' if field.help_text else ''}
            </div>
            """
        
        elif field.field_type == FieldType.TEXTAREA:
            return f"""
            <div class="field">
                <label for="{field.name}">{field.label}</label>
                <textarea id="{field.name}" name="{field.name}" rows="4" {required}>{value}</textarea>
                {f'<div class="help-text">{field.help_text}</div>' if field.help_text else ''}
            </div>
            """
        
        elif field.field_type == FieldType.BOOLEAN:
            checked = "checked" if value else ""
            return f"""
            <div class="field">
                <label>
                    <input type="checkbox" name="{field.name}" value="true" {checked}>
                    {field.label}
                </label>
                {f'<div class="help-text">{field.help_text}</div>' if field.help_text else ''}
            </div>
            """
        
        else:
            # Standard input fields
            input_type = field.field_type.value
            return f"""
            <div class="field">
                <label for="{field.name}">{field.label}</label>
                <input type="{input_type}" id="{field.name}" name="{field.name}" 
                       value="{value}" {required}
                       {f'min="{field.min_value}"' if field.min_value else ''}
                       {f'max="{field.max_value}"' if field.max_value else ''}
                       {f'pattern="{field.pattern}"' if field.pattern else ''}
                       {f'placeholder="{field.placeholder}"' if field.placeholder else ''}>
                {f'<div class="help-text">{field.help_text}</div>' if field.help_text else ''}
            </div>
            """
    
    def _render_errors(self, errors: Optional[List[str]]) -> str:
        """Render error messages"""
        if not errors:
            return ""
        
        error_html = '<div class="error"><strong>Please fix the following errors:</strong><ul>'
        for error in errors:
            error_html += f'<li>{error}</li>'
        error_html += '</ul></div>'
        return error_html
    
    def _render_error(self, message: str) -> str:
        """Render error page"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <div style="max-width: 600px; margin: 50px auto; padding: 20px; background: #fee; border: 1px solid #fcc; border-radius: 4px;">
                <h2>Error</h2>
                <p>{message}</p>
                <a href="/">Start Over</a>
            </div>
        </body>
        </html>
        """
    
    async def process_step(self, session_id: str, step_id: str, form_data: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """
        Process a step submission and return (next_step_id, error_message)
        """
        session = self.get_session(session_id)
        if not session:
            return "", "Session expired"
        
        step = self.steps.get(step_id)
        if not step:
            return "", "Invalid step"
        
        # Clean form data (handle arrays, checkboxes, etc.)
        cleaned_data = self._clean_form_data(form_data, step.request_model)
        
        # Validate with Pydantic
        try:
            input_model = step.request_model(**cleaned_data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = error["loc"][0]
                msg = error["msg"]
                errors.append(f"{field}: {msg}")
            return step_id, "\n".join(errors)
        
        # Store request data
        session["data"][f"step_{step_id}_request"] = cleaned_data
        
        # Process with processor if available
        if step.processor:
            try:
                response = await step.processor.process(input_model, session["data"])
                # Store response data
                if hasattr(response, 'dict'):
                    session["data"][f"step_{step_id}_response"] = response.dict()
                else:
                    session["data"][f"step_{step_id}_response"] = response.model_dump()
            except Exception as e:
                return step_id, f"Processing error: {str(e)}"
        
        # Determine next step
        if step.is_exit_point:
            return "completed", None
        elif step.next_step_id:
            # Pre-populate next step with response data
            if f"step_{step_id}_response" in session["data"]:
                response_data = session["data"][f"step_{step_id}_response"]
                # Store for next step's pre-population
                session["data"][f"{step.next_step_id}_defaults"] = response_data
            return step.next_step_id, None
        else:
            return "", "No next step configured"
    
    def _clean_form_data(self, form_data: Dict[str, Any], model: Type[BaseModel]) -> Dict[str, Any]:
        """Clean and convert form data to match model expectations"""
        cleaned = {}
        
        model_fields = model.__fields__ if hasattr(model, '__fields__') else model.model_fields
        
        for field_name, field_info in model_fields.items():
            if field_name in form_data:
                value = form_data[field_name]
                
                # Get field type
                field_type = field_info.annotation if hasattr(field_info, 'annotation') else field_info.type_
                
                # Handle different types
                if field_type == bool:
                    # Checkboxes send "true" or nothing
                    cleaned[field_name] = value == "true"
                elif hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                    # Arrays come as lists already from form
                    if isinstance(value, list):
                        cleaned[field_name] = value
                    else:
                        cleaned[field_name] = [value] if value else []
                elif field_type in [int, float]:
                    # Convert numeric strings
                    try:
                        cleaned[field_name] = field_type(value) if value else None
                    except (ValueError, TypeError):
                        cleaned[field_name] = None
                else:
                    # Everything else as-is
                    cleaned[field_name] = value
            else:
                # Check for array fields (they come as fieldname[] in form data)
                array_key = f"{field_name}[]"
                if array_key in form_data:
                    cleaned[field_name] = form_data[array_key]
                    if not isinstance(cleaned[field_name], list):
                        cleaned[field_name] = [cleaned[field_name]]
        
        return cleaned
    
    def render_completion(self, session_id: str) -> str:
        """Render completion page"""
        session = self.get_session(session_id)
        if not session:
            return self._render_error("Session not found")
        
        # Get all collected data
        data = session["data"]
        
        # Format data nicely
        summary_html = ""
        for key, value in data.items():
            if key.endswith("_request"):
                step_name = key.replace("step_", "").replace("_request", "")
                summary_html += f"<h3>{step_name.replace('_', ' ').title()}</h3><pre>{self._format_data(value)}</pre>"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Process Complete</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: system-ui, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .success {{
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 30px;
                }}
                h1 {{
                    color: #333;
                    margin: 0 0 10px 0;
                }}
                h3 {{
                    color: #666;
                    margin-top: 30px;
                }}
                pre {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 4px;
                    overflow-x: auto;
                }}
                .actions {{
                    margin-top: 30px;
                    text-align: center;
                }}
                .btn {{
                    display: inline-block;
                    padding: 10px 20px;
                    background: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }}
                .btn:hover {{
                    background: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">
                    <h1>✅ Process Completed Successfully!</h1>
                    <p>All steps have been completed. Here's a summary of your submission:</p>
                </div>
                
                {summary_html}
                
                <div class="actions">
                    <a href="/" class="btn">Start New Process</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_data(self, data: Dict[str, Any]) -> str:
        """Format data for display"""
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


# Example usage for FastAPI
"""
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# Initialize form chain
chain = SimplifiedFormChain(steps=[...])

@app.get("/", response_class=HTMLResponse)
async def start():
    # Create new session
    session_id = chain.create_session()
    # Redirect to first step
    return RedirectResponse(f"/form/{session_id}/step_1")

@app.get("/form/{session_id}/{step_id}", response_class=HTMLResponse)
async def show_form(session_id: str, step_id: str):
    return chain.render_step(step_id, session_id)

@app.post("/process/{session_id}/{step_id}")
async def process_form(session_id: str, step_id: str, request: Request):
    form_data = await request.form()
    form_dict = dict(form_data)
    
    next_step, error = await chain.process_step(session_id, step_id, form_dict)
    
    if error:
        # Show form again with errors
        return HTMLResponse(chain.render_step(step_id, session_id, [error]))
    elif next_step == "completed":
        # Show completion page
        return HTMLResponse(chain.render_completion(session_id))
    else:
        # Redirect to next step (PRG pattern)
        return RedirectResponse(f"/form/{session_id}/{next_step}", status_code=303)
"""