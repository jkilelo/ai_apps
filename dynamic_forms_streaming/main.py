"""
Dynamic Forms FastAPI Application
A modern, real-time form generation system with WebSocket streaming
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Any, Optional, Union
import json
import asyncio
from datetime import datetime, date
from enum import Enum
import uuid

app = FastAPI(
    title="Dynamic Forms API",
    description="A beautiful, responsive form generation system with real-time streaming",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic Models for different forms
class UserProfile(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50, description="First Name")
    last_name: str = Field(..., min_length=2, max_length=50, description="Last Name")
    email: EmailStr = Field(..., description="Email Address")
    age: int = Field(..., ge=18, le=120, description="Age")
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$', description="Phone Number")
    bio: Optional[str] = Field(None, max_length=500, description="Biography")
    website: Optional[str] = Field(None, description="Website URL")
    birth_date: Optional[date] = Field(None, description="Birth Date")

class ProductCategory(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    books = "books"
    home = "home"
    sports = "sports"

class Product(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Product Name")
    description: str = Field(..., min_length=10, max_length=1000, description="Product Description")
    price: float = Field(..., gt=0, description="Price")
    category: ProductCategory = Field(..., description="Product Category")
    in_stock: bool = Field(True, description="In Stock")
    tags: List[str] = Field(default=[], description="Product Tags")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating (0-5)")

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full Name")
    email: EmailStr = Field(..., description="Email Address")
    subject: str = Field(..., min_length=5, max_length=200, description="Subject")
    message: str = Field(..., min_length=10, max_length=2000, description="Message")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$", description="Priority Level")

class FeedbackRating(BaseModel):
    overall_rating: int = Field(..., ge=1, le=5, description="Overall Rating (1-5)")
    ease_of_use: int = Field(..., ge=1, le=5, description="Ease of Use (1-5)")
    features: int = Field(..., ge=1, le=5, description="Features (1-5)")
    support: int = Field(..., ge=1, le=5, description="Support Quality (1-5)")
    recommendation: bool = Field(..., description="Would you recommend this?")
    comments: Optional[str] = Field(None, max_length=1000, description="Additional Comments")

class NewsletterSubscription(BaseModel):
    email: EmailStr = Field(..., description="Email Address")
    interests: List[str] = Field(..., description="Areas of Interest")
    frequency: str = Field("weekly", pattern="^(daily|weekly|monthly)$", description="Email Frequency")
    marketing_consent: bool = Field(..., description="Marketing Consent")

# Form Schema Generator
class FormGenerator:
    @staticmethod
    def pydantic_to_form_schema(model: BaseModel) -> Dict[str, Any]:
        """Convert Pydantic model to form schema"""
        schema = model.model_json_schema()
        form_fields = []
        
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        for field_name, field_info in properties.items():
            field_type = field_info.get('type', 'string')
            field_format = field_info.get('format')
            enum_values = field_info.get('enum')
            
            form_field = {
                'name': field_name,
                'label': field_info.get('description', field_name.replace('_', ' ').title()),
                'required': field_name in required_fields,
                'type': FormGenerator._get_input_type(field_type, field_format, enum_values),
                'placeholder': field_info.get('description', ''),
                'validation': FormGenerator._get_validation_rules(field_info)
            }
            
            # Handle special cases
            if enum_values:
                form_field['options'] = enum_values
            elif field_type == 'array':
                form_field['type'] = 'tags'
                form_field['multiple'] = True
            elif field_name == 'birth_date':
                form_field['type'] = 'date'
            elif 'email' in field_name.lower():
                form_field['type'] = 'email'
            elif 'phone' in field_name.lower():
                form_field['type'] = 'tel'
            elif 'url' in field_name.lower() or 'website' in field_name.lower():
                form_field['type'] = 'url'
            elif field_name in ['bio', 'description', 'message', 'comments']:
                form_field['type'] = 'textarea'
            elif field_name.endswith('_rating') or field_name == 'rating':
                form_field['type'] = 'range'
                form_field['min'] = field_info.get('minimum', 1)
                form_field['max'] = field_info.get('maximum', 5)
            
            form_fields.append(form_field)
        
        return {
            'title': schema.get('title', model.__name__),
            'fields': form_fields
        }
    
    @staticmethod
    def _get_input_type(field_type: str, field_format: str = None, enum_values: List = None) -> str:
        if enum_values:
            return 'select'
        elif field_type == 'boolean':
            return 'checkbox'
        elif field_type == 'integer':
            return 'number'
        elif field_type == 'number':
            return 'number'
        elif field_format == 'email':
            return 'email'
        elif field_format == 'date':
            return 'date'
        elif field_format == 'date-time':
            return 'datetime-local'
        else:
            return 'text'
    
    @staticmethod
    def _get_validation_rules(field_info: Dict) -> Dict:
        rules = {}
        if 'minLength' in field_info:
            rules['minLength'] = field_info['minLength']
        if 'maxLength' in field_info:
            rules['maxLength'] = field_info['maxLength']
        if 'minimum' in field_info:
            rules['min'] = field_info['minimum']
        if 'maximum' in field_info:
            rules['max'] = field_info['maximum']
        if 'pattern' in field_info:
            rules['pattern'] = field_info['pattern']
        return rules

# In-memory storage for demo purposes
stored_data = {
    'user_profiles': [],
    'products': [],
    'contact_messages': [],
    'feedback': [],
    'newsletter_subscriptions': []
}

# Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/endpoints")
async def get_endpoints():
    """Get available API endpoints with their schemas"""
    endpoints = {
        '/api/user-profile': {
            'method': 'POST',
            'title': 'User Profile',
            'description': 'Create or update user profile information',
            'icon': 'user',
            'schema': FormGenerator.pydantic_to_form_schema(UserProfile)
        },
        '/api/product': {
            'method': 'POST',
            'title': 'Product',
            'description': 'Add a new product to the catalog',
            'icon': 'box',
            'schema': FormGenerator.pydantic_to_form_schema(Product)
        },
        '/api/contact': {
            'method': 'POST',
            'title': 'Contact Message',
            'description': 'Send a contact message or inquiry',
            'icon': 'message-circle',
            'schema': FormGenerator.pydantic_to_form_schema(ContactMessage)
        },
        '/api/feedback': {
            'method': 'POST',
            'title': 'Feedback & Rating',
            'description': 'Provide feedback and ratings',
            'icon': 'star',
            'schema': FormGenerator.pydantic_to_form_schema(FeedbackRating)
        },
        '/api/newsletter': {
            'method': 'POST',
            'title': 'Newsletter Subscription',
            'description': 'Subscribe to our newsletter',
            'icon': 'mail',
            'schema': FormGenerator.pydantic_to_form_schema(NewsletterSubscription)
        }
    }
    return endpoints

@app.post("/api/user-profile")
async def create_user_profile(profile: UserProfile):
    """Create user profile"""
    profile_data = profile.model_dump()
    profile_data['id'] = str(uuid.uuid4())
    profile_data['created_at'] = datetime.now().isoformat()
    
    stored_data['user_profiles'].append(profile_data)
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        'type': 'submission',
        'endpoint': '/api/user-profile',
        'data': profile_data,
        'message': f"New user profile created for {profile.first_name} {profile.last_name}"
    }))
    
    return {
        "success": True, 
        "message": f"User profile created successfully for {profile.first_name} {profile.last_name}", 
        "id": profile_data['id'],
        "created_at": profile_data['created_at'],
        "profile_summary": f"{profile.first_name} {profile.last_name}, {profile.age} years old",
        "total_profiles": len(stored_data['user_profiles'])
    }

@app.post("/api/product")
async def create_product(product: Product):
    """Create product"""
    product_data = product.model_dump()
    product_data['id'] = str(uuid.uuid4())
    product_data['created_at'] = datetime.now().isoformat()
    
    stored_data['products'].append(product_data)
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        'type': 'submission',
        'endpoint': '/api/product',
        'data': product_data,
        'message': f"New product '{product.name}' added to catalog"
    }))
    
    return {
        "success": True, 
        "message": f"Product '{product.name}' created successfully", 
        "id": product_data['id'],
        "created_at": product_data['created_at'],
        "product_summary": f"{product.name} - ${product.price} ({product.category})",
        "total_products": len(stored_data['products']),
        "stock_status": "In Stock" if product.in_stock else "Out of Stock"
    }

@app.post("/api/contact")
async def create_contact_message(contact: ContactMessage):
    """Create contact message"""
    contact_data = contact.model_dump()
    contact_data['id'] = str(uuid.uuid4())
    contact_data['created_at'] = datetime.now().isoformat()
    contact_data['ticket_number'] = f"TICKET-{len(stored_data['contact_messages']) + 1:04d}"
    
    stored_data['contact_messages'].append(contact_data)
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        'type': 'submission',
        'endpoint': '/api/contact',
        'data': contact_data,
        'message': f"New contact message from {contact.name}: {contact.subject}"
    }))
    
    return {
        "success": True, 
        "message": f"Contact message received successfully from {contact.name}", 
        "id": contact_data['id'],
        "created_at": contact_data['created_at'],
        "ticket_number": contact_data['ticket_number'],
        "priority_level": contact.priority,
        "estimated_response": "Within 24 hours" if contact.priority in ['normal', 'low'] else "Within 2 hours",
        "total_messages": len(stored_data['contact_messages'])
    }

@app.post("/api/feedback")
async def create_feedback(feedback: FeedbackRating):
    """Create feedback"""
    feedback_data = feedback.model_dump()
    feedback_data['id'] = str(uuid.uuid4())
    feedback_data['created_at'] = datetime.now().isoformat()
    
    stored_data['feedback'].append(feedback_data)
    
    # Calculate average rating
    avg_rating = (feedback.overall_rating + feedback.ease_of_use + feedback.features + feedback.support) / 4
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        'type': 'submission',
        'endpoint': '/api/feedback',
        'data': feedback_data,
        'message': f"New feedback received with overall rating: {feedback.overall_rating}/5"
    }))
    
    return {
        "success": True, 
        "message": f"Thank you for your feedback! Your overall rating: {feedback.overall_rating}/5", 
        "id": feedback_data['id'],
        "created_at": feedback_data['created_at'],
        "average_rating": round(avg_rating, 1),
        "recommendation_status": "Would recommend" if feedback.recommendation else "Would not recommend",
        "feedback_summary": f"Overall: {feedback.overall_rating}/5, Ease: {feedback.ease_of_use}/5, Features: {feedback.features}/5, Support: {feedback.support}/5",
        "total_feedback": len(stored_data['feedback'])
    }

@app.post("/api/newsletter")
async def create_newsletter_subscription(subscription: NewsletterSubscription):
    """Create newsletter subscription"""
    subscription_data = subscription.model_dump()
    subscription_data['id'] = str(uuid.uuid4())
    subscription_data['created_at'] = datetime.now().isoformat()
    subscription_data['status'] = 'active'
    
    stored_data['newsletter_subscriptions'].append(subscription_data)
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        'type': 'submission',
        'endpoint': '/api/newsletter',
        'data': subscription_data,
        'message': f"New newsletter subscription: {subscription.email}"
    }))
    
    return {
        "success": True, 
        "message": f"Successfully subscribed {subscription.email} to our newsletter!", 
        "id": subscription_data['id'],
        "created_at": subscription_data['created_at'],
        "subscription_status": "Active",
        "email_frequency": subscription.frequency,
        "interests_count": len(subscription.interests),
        "interests_summary": ", ".join(subscription.interests[:3]) + ("..." if len(subscription.interests) > 3 else ""),
        "total_subscribers": len(stored_data['newsletter_subscriptions'])
    }

@app.get("/api/data/{data_type}")
async def get_stored_data(data_type: str):
    """Get stored data for a specific type"""
    if data_type in stored_data:
        return stored_data[data_type]
    raise HTTPException(status_code=404, detail="Data type not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send welcome message
        await manager.send_personal_message(json.dumps({
            'type': 'connection',
            'message': 'Connected to real-time updates',
            'timestamp': datetime.now().isoformat()
        }), websocket)
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get('type') == 'ping':
                await manager.send_personal_message(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }), websocket)
            elif message_data.get('type') == 'form_start':
                await manager.broadcast(json.dumps({
                    'type': 'form_activity',
                    'message': f"User started filling {message_data.get('form_name', 'a form')}",
                    'timestamp': datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
