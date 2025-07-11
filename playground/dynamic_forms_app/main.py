#!/usr/bin/env python3
"""
Dynamic Forms Generator - Real-time FastAPI Application
A beautiful, responsive application that automatically generates modern forms from FastAPI endpoints
"""

import asyncio
import json
import inspect
import re
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union, get_type_hints, get_origin, get_args
from enum import Enum
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, EmailStr
from pydantic.fields import FieldInfo


class UserProfile(BaseModel):
    """Example user profile model"""
    first_name: str = Field(..., description="Your first name", min_length=2, max_length=50)
    last_name: str = Field(..., description="Your last name", min_length=2, max_length=50)
    email: EmailStr = Field(..., description="Your email address")
    age: int = Field(..., description="Your age", ge=13, le=120)
    bio: Optional[str] = Field(None, description="Tell us about yourself", max_length=500)
    newsletter: bool = Field(True, description="Subscribe to newsletter")


class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    SPORTS = "sports"
    HOME = "home"


class Product(BaseModel):
    """Example product model"""
    name: str = Field(..., description="Product name", min_length=3, max_length=100)
    category: ProductCategory = Field(..., description="Product category")
    price: float = Field(..., description="Product price", gt=0, le=10000)
    description: str = Field(..., description="Product description", max_length=1000)
    in_stock: bool = Field(True, description="Is product in stock")
    rating: Optional[float] = Field(None, description="Product rating", ge=0, le=5)


class ContactForm(BaseModel):
    """Example contact form model"""
    name: str = Field(..., description="Your full name", min_length=2)
    email: EmailStr = Field(..., description="Your email address")
    subject: str = Field(..., description="Message subject", max_length=200)
    message: str = Field(..., description="Your message", min_length=10, max_length=2000)
    urgent: bool = Field(False, description="Mark as urgent")


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except:
            self.disconnect(websocket)
            
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


class FormGenerator:
    """Generates beautiful forms from Pydantic models and FastAPI endpoints"""
    
    @staticmethod
    def get_field_type(field_type, field_info: FieldInfo) -> Dict[str, Any]:
        """Determine HTML input type and attributes from Python type"""
        
        # Handle Optional types
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            if len(args) == 2 and type(None) in args:
                field_type = next(arg for arg in args if arg is not type(None))
        
        field_config = {
            "type": "text",
            "attributes": {},
            "validation": {},
            "options": None
        }
        
        # Handle different field types
        if field_type == str:
            field_config["type"] = "text"
            if field_info.description and any(keyword in field_info.description.lower() 
                                            for keyword in ["email", "mail"]):
                field_config["type"] = "email"
            elif field_info.description and any(keyword in field_info.description.lower() 
                                              for keyword in ["password", "pwd"]):
                field_config["type"] = "password"
            elif field_info.description and any(keyword in field_info.description.lower() 
                                              for keyword in ["url", "link", "website"]):
                field_config["type"] = "url"
            elif field_info.description and any(keyword in field_info.description.lower() 
                                              for keyword in ["phone", "tel"]):
                field_config["type"] = "tel"
                
        elif field_type == EmailStr:
            field_config["type"] = "email"
            
        elif field_type == int:
            field_config["type"] = "number"
            field_config["attributes"]["step"] = "1"
            
        elif field_type == float:
            field_config["type"] = "number"
            field_config["attributes"]["step"] = "0.01"
            
        elif field_type == bool:
            field_config["type"] = "checkbox"
            
        elif field_type == date:
            field_config["type"] = "date"
            
        elif field_type == datetime:
            field_config["type"] = "datetime-local"
            
        elif hasattr(field_type, '__bases__') and Enum in field_type.__bases__:
            field_config["type"] = "select"
            field_config["options"] = [{"value": item.value, "label": item.value.title()} 
                                     for item in field_type]
        
        # Handle constraints
        if hasattr(field_info, 'constraints'):
            constraints = field_info.constraints
            
            if hasattr(constraints, 'min_length') and constraints.min_length:
                field_config["attributes"]["minlength"] = constraints.min_length
                field_config["validation"]["minLength"] = constraints.min_length
                
            if hasattr(constraints, 'max_length') and constraints.max_length:
                field_config["attributes"]["maxlength"] = constraints.max_length
                field_config["validation"]["maxLength"] = constraints.max_length
                
            if hasattr(constraints, 'ge') and constraints.ge is not None:
                field_config["attributes"]["min"] = constraints.ge
                field_config["validation"]["min"] = constraints.ge
                
            if hasattr(constraints, 'le') and constraints.le is not None:
                field_config["attributes"]["max"] = constraints.le
                field_config["validation"]["max"] = constraints.le
                
            if hasattr(constraints, 'gt') and constraints.gt is not None:
                field_config["attributes"]["min"] = constraints.gt + (0.01 if field_type == float else 1)
                field_config["validation"]["min"] = constraints.gt + (0.01 if field_type == float else 1)
                
            if hasattr(constraints, 'lt') and constraints.lt is not None:
                field_config["attributes"]["max"] = constraints.lt - (0.01 if field_type == float else 1)
                field_config["validation"]["max"] = constraints.lt - (0.01 if field_type == float else 1)
        
        # Handle long text fields
        if (field_type == str and field_info.description and 
            any(keyword in field_info.description.lower() 
                for keyword in ["message", "description", "bio", "comment", "text", "content"])):
            field_config["type"] = "textarea"
            field_config["attributes"]["rows"] = 4
        
        return field_config
    
    @staticmethod
    def model_to_form_schema(model: BaseModel) -> Dict[str, Any]:
        """Convert a Pydantic model to a form schema"""
        
        schema = {
            "name": model.__name__,
            "title": model.__name__.replace("_", " ").title(),
            "description": model.__doc__ or f"Form for {model.__name__}",
            "fields": []
        }
        
        # Get type hints and model fields
        type_hints = get_type_hints(model)
        
        for field_name, field_info in model.model_fields.items():
            field_type = type_hints.get(field_name, str)
            field_config = FormGenerator.get_field_type(field_type, field_info)
            
            field_schema = {
                "name": field_name,
                "label": field_name.replace("_", " ").title(),
                "description": field_info.description or "",
                "required": field_info.is_required(),
                "default": field_info.default if field_info.default is not ... else None,
                **field_config
            }
            
            schema["fields"].append(field_schema)
        
        return schema


# FastAPI app initialization
app = FastAPI(
    title="Dynamic Forms Generator",
    description="Automatically generate beautiful forms from FastAPI endpoints",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Connection manager
manager = ConnectionManager()

# Form generator
form_generator = FormGenerator()


@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/endpoints")
async def get_endpoints():
    """Get all available API endpoints with their schemas"""
    endpoints = []
    
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'endpoint'):
            if 'POST' in route.methods and route.path.startswith('/api/'):
                # Get function signature
                func = route.endpoint
                signature = inspect.signature(func)
                
                endpoint_info = {
                    "path": route.path,
                    "name": route.name or func.__name__,
                    "description": func.__doc__ or f"API endpoint for {route.path}",
                    "method": "POST",
                    "parameters": []
                }
                
                # Analyze parameters
                for param_name, param in signature.parameters.items():
                    if param_name in ['request', 'websocket']:
                        continue
                        
                    param_info = {
                        "name": param_name,
                        "type": str(param.annotation) if param.annotation != param.empty else "str",
                        "required": param.default == param.empty,
                        "default": param.default if param.default != param.empty else None
                    }
                    endpoint_info["parameters"].append(param_info)
                
                endpoints.append(endpoint_info)
    
    return {"endpoints": endpoints}


@app.get("/api/form-schema/{model_name}")
async def get_form_schema(model_name: str):
    """Get form schema for a specific model"""
    models = {
        "UserProfile": UserProfile,
        "Product": Product,
        "ContactForm": ContactForm
    }
    
    if model_name not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models[model_name]
    schema = form_generator.model_to_form_schema(model)
    return schema


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time form updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "form_update":
                # Broadcast form updates to all connected clients
                await manager.broadcast({
                    "type": "form_update",
                    "data": message["data"],
                    "timestamp": datetime.now().isoformat()
                })
            elif message["type"] == "form_submit":
                # Handle form submission
                await handle_form_submission(message["data"], websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def handle_form_submission(form_data: dict, websocket: WebSocket):
    """Handle form submission and send response"""
    try:
        # Process the form data
        response = {
            "type": "form_response",
            "status": "success",
            "message": "Form submitted successfully!",
            "data": form_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.send_personal_message(response, websocket)
        
        # Broadcast submission to all clients (for demo purposes)
        await manager.broadcast({
            "type": "form_submitted",
            "form_name": form_data.get("form_name", "Unknown"),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "form_response",
            "status": "error",
            "message": f"Error processing form: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, websocket)


# Example API endpoints that will have forms generated for them

@app.post("/api/user-profile")
async def create_user_profile(profile: UserProfile):
    """Create a new user profile"""
    # Simulate processing
    await asyncio.sleep(0.5)
    
    return {
        "status": "success",
        "message": "User profile created successfully!",
        "data": profile.model_dump(),
        "id": f"user_{datetime.now().timestamp()}"
    }


@app.post("/api/product")
async def create_product(product: Product):
    """Create a new product"""
    # Simulate processing
    await asyncio.sleep(0.3)
    
    return {
        "status": "success",
        "message": "Product created successfully!",
        "data": product.model_dump(),
        "id": f"product_{datetime.now().timestamp()}"
    }


@app.post("/api/contact")
async def submit_contact_form(contact: ContactForm):
    """Submit a contact form"""
    # Simulate processing
    await asyncio.sleep(0.2)
    
    return {
        "status": "success",
        "message": "Contact form submitted successfully! We'll get back to you soon.",
        "data": contact.model_dump(),
        "reference": f"ticket_{datetime.now().timestamp()}"
    }


@app.post("/api/feedback")
async def submit_feedback(
    name: str = Form(..., description="Your name"),
    email: EmailStr = Form(..., description="Your email"),
    rating: int = Form(..., description="Rating (1-5)", ge=1, le=5),
    feedback: str = Form(..., description="Your feedback", min_length=10),
    recommend: bool = Form(False, description="Would you recommend us?")
):
    """Submit feedback form"""
    await asyncio.sleep(0.4)
    
    return {
        "status": "success",
        "message": "Thank you for your feedback!",
        "data": {
            "name": name,
            "email": email,
            "rating": rating,
            "feedback": feedback,
            "recommend": recommend
        }
    }


@app.get("/api/stats")
async def get_app_stats():
    """Get application statistics"""
    return {
        "active_connections": len(manager.active_connections),
        "available_forms": 4,
        "total_endpoints": len([r for r in app.routes if hasattr(r, 'methods')]),
        "uptime": "Running",
        "last_updated": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🚀 Starting Dynamic Forms Generator...")
    print("📍 Dashboard: http://localhost:8992")
    print("🔧 Press Ctrl+C to stop")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8992,
        reload=True,
        log_level="info"
    )
