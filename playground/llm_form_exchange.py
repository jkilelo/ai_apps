#!/usr/bin/env python3
"""
LLM Form Exchange System - Backend
A simple request-response system where user and LLM exchange forms
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import random
import uvicorn
from pathlib import Path

# Create FastAPI app
app = FastAPI(title="LLM Form Exchange", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for requests and responses
class UserFormData(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    form_type: str = Field(description="Type of form submitted")
    fields: Dict[str, Any] = Field(description="Form field values")
    session_id: str = Field(description="Session identifier")
    step: int = Field(description="Current step in the conversation")

class LLMFormResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    form_type: str = Field(description="Type of form to display")
    title: str = Field(description="Form title")
    description: str = Field(description="Form description")
    fields: List[Dict[str, Any]] = Field(description="Form fields to render")
    session_id: str = Field(description="Session identifier")
    step: int = Field(description="Current step")
    is_final: bool = Field(default=False, description="Is this the final form?")

# Session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}

# Form templates for different steps
FORM_TEMPLATES = {
    "initial": {
        "title": "Tell me about yourself",
        "description": "Let's start with some basic information",
        "fields": [
            {"name": "name", "type": "text", "label": "Your Name", "required": True},
            {"name": "interest", "type": "select", "label": "What interests you?", "options": ["Technology", "Art", "Science", "Sports", "Music"], "required": True},
            {"name": "experience", "type": "textarea", "label": "Tell us about your experience", "required": False}
        ]
    },
    "follow_up_tech": {
        "title": "Technology Interests",
        "description": "Great! Let's dive deeper into your tech interests",
        "fields": [
            {"name": "languages", "type": "checkbox", "label": "Programming languages you know", "options": ["Python", "JavaScript", "Java", "C++", "Go", "Rust"], "required": False},
            {"name": "field", "type": "radio", "label": "Preferred field", "options": ["Web Development", "Data Science", "DevOps", "Mobile", "AI/ML"], "required": True},
            {"name": "project", "type": "text", "label": "Describe a project you're proud of", "required": False}
        ]
    },
    "follow_up_art": {
        "title": "Artistic Interests",
        "description": "Wonderful! Tell me more about your artistic side",
        "fields": [
            {"name": "medium", "type": "checkbox", "label": "Art forms you enjoy", "options": ["Painting", "Drawing", "Sculpture", "Photography", "Digital Art"], "required": False},
            {"name": "style", "type": "text", "label": "Your favorite art style", "required": False},
            {"name": "inspiration", "type": "textarea", "label": "What inspires your creativity?", "required": False}
        ]
    },
    "recommendation": {
        "title": "Personalized Recommendations",
        "description": "Based on our conversation, here are some suggestions",
        "fields": [
            {"name": "feedback", "type": "radio", "label": "Was this helpful?", "options": ["Very helpful", "Somewhat helpful", "Not helpful"], "required": True},
            {"name": "email", "type": "email", "label": "Email for more resources (optional)", "required": False},
            {"name": "comments", "type": "textarea", "label": "Any additional comments?", "required": False}
        ]
    }
}

def generate_llm_response(user_data: UserFormData) -> LLMFormResponse:
    """Generate LLM form response based on user input"""
    session = sessions.get(user_data.session_id, {})
    
    # Store user response
    session[f"step_{user_data.step}"] = user_data.fields
    sessions[user_data.session_id] = session
    
    # Determine next form based on conversation flow
    if user_data.step == 0:
        # First response - choose follow-up based on interest
        interest = user_data.fields.get("interest", "").lower()
        if interest == "technology":
            template = FORM_TEMPLATES["follow_up_tech"]
            form_type = "follow_up_tech"
        elif interest == "art":
            template = FORM_TEMPLATES["follow_up_art"]
            form_type = "follow_up_art"
        else:
            # Generic follow-up for other interests
            template = FORM_TEMPLATES["recommendation"]
            form_type = "recommendation"
    elif user_data.step == 1:
        # Second response - show recommendations
        template = FORM_TEMPLATES["recommendation"]
        form_type = "recommendation"
    else:
        # Final step
        return LLMFormResponse(
            form_type="complete",
            title="Thank You!",
            description=f"Thanks for chatting, {session.get('step_0', {}).get('name', 'friend')}! Your responses have been recorded.",
            fields=[],
            session_id=user_data.session_id,
            step=user_data.step + 1,
            is_final=True
        )
    
    # Add dynamic content based on previous responses
    if form_type == "recommendation":
        name = session.get('step_0', {}).get('name', 'there')
        template["description"] = f"Based on our conversation, {name}, here are some personalized suggestions for you"
    
    return LLMFormResponse(
        form_type=form_type,
        title=template["title"],
        description=template["description"],
        fields=template["fields"],
        session_id=user_data.session_id,
        step=user_data.step + 1,
        is_final=False
    )

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main HTML page"""
    html_path = Path(__file__).parent / "llm_form_exchange.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    else:
        return HTMLResponse(content="<h1>Please create llm_form_exchange.html</h1>")

@app.post("/api/start")
async def start_conversation() -> LLMFormResponse:
    """Start a new conversation"""
    session_id = f"session_{datetime.now().timestamp()}_{random.randint(1000, 9999)}"
    sessions[session_id] = {"started_at": datetime.now().isoformat()}
    
    template = FORM_TEMPLATES["initial"]
    return LLMFormResponse(
        form_type="initial",
        title=template["title"],
        description=template["description"],
        fields=template["fields"],
        session_id=session_id,
        step=0,
        is_final=False
    )

@app.post("/api/submit", response_model=LLMFormResponse)
async def submit_form(user_data: UserFormData) -> LLMFormResponse:
    """Process user form submission and return LLM response"""
    return generate_llm_response(user_data)

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session data for debugging"""
    return sessions.get(session_id, {"error": "Session not found"})

if __name__ == "__main__":
    print("🚀 Starting LLM Form Exchange Server")
    print("📍 Visit http://localhost:8000 to start")
    uvicorn.run(app, host="0.0.0.0", port=8000)