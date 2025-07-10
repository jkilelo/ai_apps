#!/usr/bin/env python3
"""
FastAPI server for the 10-step employee onboarding form with navigation support
Allows users to navigate between steps and view previous step results
"""

import sys
import json
import base64
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional, List
from uuid import uuid4
import asyncio

sys.path.insert(0, '/var/www/ai_apps/playground')

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import ValidationError

from html_v3_employee_onboarding_10steps_simple import (
    create_employee_onboarding_chain,
    BasicInfoResponse, EmploymentDetailsResponse, AddressInfoResponse,
    EmergencyContactResponse, EducationExperienceResponse, BenefitsSelectionResponse,
    ITEquipmentResponse, AccessSecurityResponse, TrainingOrientationResponse,
    FinalReviewResponse
)
from port_finder import find_free_port

# Find available port
PORT = find_free_port(8100, 8200)

# Create FastAPI app
app = FastAPI(
    title="Employee Onboarding System",
    description="10-step employee onboarding process with navigation",
    version="2.0.0"
)

# Store active onboarding sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

# Create the onboarding chain
onboarding_chain = create_employee_onboarding_chain()

# Step order for navigation
STEP_ORDER = [
    "basic_info",
    "employment_details", 
    "it_equipment",
    "address_info",
    "emergency_contact",
    "education_experience",
    "benefits_selection",
    "access_security",
    "training_orientation",
    "final_review"
]

# Step titles for display
STEP_TITLES = {
    "basic_info": "Basic Information",
    "employment_details": "Employment Details",
    "it_equipment": "IT Equipment",
    "address_info": "Address Information",
    "emergency_contact": "Emergency Contact",
    "education_experience": "Education & Experience",
    "benefits_selection": "Benefits Selection",
    "access_security": "Access & Security",
    "training_orientation": "Training & Orientation",
    "final_review": "Final Review"
}


# Mock processors for each step (NO VALIDATION - just process data)
async def process_basic_info(data: dict, context: dict) -> BasicInfoResponse:
    """Process basic information and create employee ID"""
    employee_id = f"EMP-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"
    
    # Handle empty or invalid date
    age = None
    if data.get('date_of_birth'):
        try:
            dob = date.fromisoformat(data['date_of_birth']) if isinstance(data['date_of_birth'], str) else data['date_of_birth']
            age = date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day))
        except:
            age = None
    
    return BasicInfoResponse(
        employee_id=employee_id,
        full_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or "Unknown",
        age=age,
        email_verified=True
    )


async def process_employment_details(data: dict, context: dict) -> EmploymentDetailsResponse:
    """Process employment details"""
    requires_equipment = data.get('department') == 'engineering'
    
    probation_days = {
        'full_time': 90,
        'part_time': 60,
        'contract': 0,
        'intern': 30
    }
    
    return EmploymentDetailsResponse(
        compensation_package_id=f"COMP-{str(uuid4())[:8]}",
        requires_equipment=requires_equipment,
        requires_visa=False,
        probation_period_days=probation_days.get(data.get('employment_type', ''), 90)
    )


async def process_address_info(data: dict, context: dict) -> AddressInfoResponse:
    """Process address information"""
    return AddressInfoResponse(
        address_id=f"ADDR-{str(uuid4())[:8]}",
        tax_jurisdiction=data.get('state', 'Unknown'),
        commute_eligible=data.get('work_location') in ['office', 'hybrid'],
        remote_setup_required=data.get('work_location') in ['remote', 'hybrid']
    )


async def process_emergency_contact(data: dict, context: dict) -> EmergencyContactResponse:
    """Process emergency contact"""
    return EmergencyContactResponse(
        contact_id=f"EMRG-{str(uuid4())[:8]}",
        verified=True
    )


async def process_education_experience(data: dict, context: dict) -> EducationExperienceResponse:
    """Process education and experience"""
    try:
        years = int(data.get('years_of_experience', 0))
    except:
        years = 0
    
    skill_level = "senior" if years >= 5 else "junior"
    
    training_recs = []
    if skill_level == "junior":
        training_recs.extend(["Mentorship Program", "Technical Foundations"])
    
    skills = data.get('skills', [])
    if isinstance(skills, list) and any('python' in s.lower() for s in skills):
        training_recs.append("Advanced Python Workshop")
        
    return EducationExperienceResponse(
        profile_id=f"PROF-{str(uuid4())[:8]}",
        skill_level=skill_level,
        training_recommendations=training_recs
    )


async def process_benefits_selection(data: dict, context: dict) -> BenefitsSelectionResponse:
    """Process benefits selection"""
    base_costs = {
        'basic': 100,
        'standard': 200,
        'premium': 400
    }
    
    total = base_costs.get(data.get('health_plan', 'basic'), 100)
    total += base_costs.get(data.get('dental_plan', 'basic'), 100) * 0.3
    total += base_costs.get(data.get('vision_plan', 'basic'), 100) * 0.2
    
    try:
        fsa = float(data.get('fsa_contribution', 0))
    except:
        fsa = 0
    total += fsa * 0.1
    
    return BenefitsSelectionResponse(
        benefits_package_id=f"BEN-{str(uuid4())[:8]}",
        total_cost=Decimal(str(total)),
        employee_contribution=Decimal(str(total * 0.3)),
        effective_date=date.today().replace(day=1)
    )


async def process_it_equipment(data: dict, context: dict) -> ITEquipmentResponse:
    """Process IT equipment request"""
    base_cost = 2000  # Laptop
    
    if data.get('needs_monitor'):
        try:
            monitors = int(data.get('monitor_count', 1))
        except:
            monitors = 1
        base_cost += 400 * monitors
    
    if data.get('needs_keyboard'):
        base_cost += 100
    if data.get('needs_mouse'):
        base_cost += 50
        
    return ITEquipmentResponse(
        equipment_request_id=f"EQIP-{str(uuid4())[:8]}",
        estimated_ready_date=date.today().replace(day=date.today().day + 3),
        total_cost=Decimal(str(base_cost))
    )


async def process_access_security(data: dict, context: dict) -> AccessSecurityResponse:
    """Process access and security"""
    return AccessSecurityResponse(
        access_request_id=f"ACC-{str(uuid4())[:8]}",
        badge_number=f"BADGE-{str(uuid4())[:6].upper()}",
        security_training_required=bool(data.get('security_clearance_required', False))
    )


async def process_training_orientation(data: dict, context: dict) -> TrainingOrientationResponse:
    """Process training and orientation"""
    schedule = {
        "Monday": "9:00 AM - Orientation",
        "Tuesday": "10:00 AM - Department Introduction",
        "Wednesday": "2:00 PM - Systems Training",
        "Thursday": "10:00 AM - Security Training",
        "Friday": "3:00 PM - Week 1 Review"
    }
    
    return TrainingOrientationResponse(
        training_plan_id=f"TRAIN-{str(uuid4())[:8]}",
        orientation_confirmed=True,
        mentor_assigned="John Mentor",
        first_week_schedule=schedule
    )


async def process_final_review(data: dict, context: dict) -> FinalReviewResponse:
    """Process final review"""
    emp_response = context.get('step_basic_info_response', {})
    
    return FinalReviewResponse(
        onboarding_complete=True,
        employee_id=emp_response.get('employee_id', 'UNKNOWN'),
        start_date=date.today().replace(day=date.today().day + 7),
        first_day_instructions="Report to reception at 9:00 AM. Ask for HR.",
        welcome_kit_tracking=f"TRACK-{str(uuid4())[:12].upper()}"
    )


# Map processors
PROCESSORS = {
    'basic_info': process_basic_info,
    'employment_details': process_employment_details,
    'address_info': process_address_info,
    'emergency_contact': process_emergency_contact,
    'education_experience': process_education_experience,
    'benefits_selection': process_benefits_selection,
    'it_equipment': process_it_equipment,
    'access_security': process_access_security,
    'training_orientation': process_training_orientation,
    'final_review': process_final_review
}


def generate_navigation_html(current_step: str, session_id: str, state: dict) -> str:
    """Generate navigation and progress summary HTML"""
    completed_steps = [step for step in STEP_ORDER if f"step_{step}_response" in state]
    
    nav_html = """
    <div class="navigation-container">
        <style>
            .navigation-container {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .step-nav {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 20px;
            }
            .step-nav-item {
                padding: 8px 16px;
                border-radius: 4px;
                text-decoration: none;
                font-size: 14px;
                transition: all 0.2s;
            }
            .step-nav-item.completed {
                background: #28a745;
                color: white;
                cursor: pointer;
            }
            .step-nav-item.current {
                background: #007bff;
                color: white;
            }
            .step-nav-item.pending {
                background: #e9ecef;
                color: #6c757d;
                cursor: not-allowed;
            }
            .step-nav-item.completed:hover {
                background: #218838;
            }
            .progress-summary {
                margin-top: 20px;
                padding: 15px;
                background: white;
                border-radius: 4px;
                border: 1px solid #dee2e6;
            }
            .summary-item {
                margin-bottom: 10px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 4px;
            }
            .summary-item strong {
                color: #495057;
            }
        </style>
        
        <h3>Progress: Step """ + str(STEP_ORDER.index(current_step) + 1) + """ of 10</h3>
        
        <div class="step-nav">
    """
    
    # Add navigation items
    for i, step in enumerate(STEP_ORDER):
        if step == current_step:
            nav_html += f'<div class="step-nav-item current">{i+1}. {STEP_TITLES[step]}</div>'
        elif step in completed_steps:
            nav_html += f'<a href="/onboarding/{session_id}/navigate/{step}" class="step-nav-item completed">{i+1}. {STEP_TITLES[step]} ✓</a>'
        else:
            nav_html += f'<div class="step-nav-item pending">{i+1}. {STEP_TITLES[step]}</div>'
    
    nav_html += """
        </div>
        
        <div class="progress-summary">
            <h4>Information Collected So Far:</h4>
    """
    
    # Add summary of collected data
    if 'step_basic_info_response' in state:
        resp = state['step_basic_info_response']
        nav_html += f"""
            <div class="summary-item">
                <strong>Employee ID:</strong> {resp.get('employee_id', 'N/A')}<br>
                <strong>Name:</strong> {resp.get('full_name', 'N/A')}<br>
                <strong>Email:</strong> {state.get('step_basic_info_request', {}).get('email', 'N/A')}
            </div>
        """
    
    if 'step_employment_details_response' in state:
        req = state.get('step_employment_details_request', {})
        nav_html += f"""
            <div class="summary-item">
                <strong>Department:</strong> {req.get('department', 'N/A')}<br>
                <strong>Job Title:</strong> {req.get('job_title', 'N/A')}<br>
                <strong>Start Date:</strong> {req.get('start_date', 'N/A')}
            </div>
        """
    
    if 'step_address_info_response' in state:
        req = state.get('step_address_info_request', {})
        nav_html += f"""
            <div class="summary-item">
                <strong>Location:</strong> {req.get('city', 'N/A')}, {req.get('state', 'N/A')}<br>
                <strong>Work Location:</strong> {req.get('work_location', 'N/A')}
            </div>
        """
    
    nav_html += """
        </div>
    </div>
    """
    
    return nav_html


@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Serve the homepage"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Employee Onboarding System</title>
        <style>
            body {{
                font-family: -apple-system, system-ui, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .button {{
                display: inline-block;
                background: #007bff;
                color: white;
                padding: 0.75rem 1.5rem;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 1rem;
            }}
            .button:hover {{
                background: #0056b3;
            }}
            .info {{
                background: #e3f2fd;
                padding: 1rem;
                border-radius: 4px;
                margin: 1rem 0;
            }}
            .features {{
                background: #e8f5e9;
                padding: 1rem;
                border-radius: 4px;
                margin: 1rem 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Employee Onboarding System v2.0</h1>
            <p>Welcome to our enhanced 10-step employee onboarding process with navigation support.</p>
            
            <div class="info">
                <h3>Process Overview:</h3>
                <ol>
                    <li>Basic Information</li>
                    <li>Employment Details</li>
                    <li>IT Equipment (conditional)</li>
                    <li>Address Information</li>
                    <li>Emergency Contact</li>
                    <li>Education & Experience</li>
                    <li>Benefits Selection</li>
                    <li>Access & Security</li>
                    <li>Training & Orientation</li>
                    <li>Final Review & Welcome Kit</li>
                </ol>
            </div>
            
            <div class="features">
                <h3>New Features:</h3>
                <ul>
                    <li>✅ Navigate between completed steps</li>
                    <li>✅ View summary of previously entered information</li>
                    <li>✅ No validation - all fields are optional</li>
                    <li>✅ Change values in any completed step</li>
                    <li>✅ Visual progress indicator</li>
                    <li>✅ State persistence across navigation</li>
                </ul>
            </div>
            
            <a href="/onboarding/start" class="button">Start Onboarding Process</a>
            
            <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #ddd;">
                <p><small>Server running on port {PORT}</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


@app.get("/onboarding/start", response_class=HTMLResponse)
async def start_onboarding():
    """Start the onboarding process"""
    session_id = f"session_{str(uuid4())}"
    active_sessions[session_id] = {
        "chain": onboarding_chain,
        "state": {},
        "current_step": "basic_info",
        "started_at": datetime.now()
    }
    
    return RedirectResponse(url=f"/onboarding/{session_id}/step/basic_info")


@app.get("/onboarding/{session_id}/step/{step_id}", response_class=HTMLResponse)
async def show_step(session_id: str, step_id: str):
    """Show a specific step form with navigation"""
    if session_id not in active_sessions:
        return RedirectResponse(url="/")
    
    session = active_sessions[session_id]
    chain = session["chain"]
    state = session["state"]
    
    # Update current step
    session["current_step"] = step_id
    
    # Generate navigation
    nav_html = generate_navigation_html(step_id, session_id, state)
    
    # Generate form for the step
    form_html = chain.generate_form_html(step_id, state)
    
    # Update form action
    form_html = form_html.replace(
        'action="/api/chain/employee_onboarding/process/',
        f'action="/api/onboarding/{session_id}/process/'
    )
    
    # Encode state
    encoded_state = base64.b64encode(json.dumps(state).encode()).decode()
    form_html = form_html.replace(
        'name="chain_state" value=""',
        f'name="chain_state" value="{encoded_state}"'
    )
    
    # Insert navigation before form
    form_html = form_html.replace(
        '<div class="step-container">',
        nav_html + '<div class="step-container">'
    )
    
    return HTMLResponse(content=form_html)


@app.get("/onboarding/{session_id}/navigate/{step_id}")
async def navigate_to_step(session_id: str, step_id: str):
    """Navigate to a specific step"""
    if session_id not in active_sessions:
        return RedirectResponse(url="/")
    
    # Check if step is completed
    session = active_sessions[session_id]
    if f"step_{step_id}_response" in session["state"]:
        return RedirectResponse(url=f"/onboarding/{session_id}/step/{step_id}", status_code=303)
    else:
        # Can't navigate to uncompleted step
        current = session.get("current_step", "basic_info")
        return RedirectResponse(url=f"/onboarding/{session_id}/step/{current}", status_code=303)


@app.post("/api/onboarding/{session_id}/process/{step_id}")
async def process_onboarding_step(session_id: str, step_id: str, request: Request):
    """Process a form submission"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    chain = session["chain"]
    
    # Get form data
    form_data = await request.form()
    data = {}
    
    # Convert form data to dict
    for key, value in form_data.items():
        if key == "chain_state":
            if value:
                try:
                    decoded = base64.b64decode(value).decode('utf-8')
                    session["state"] = json.loads(decoded)
                except:
                    pass
        elif key in ["csrf_token", "_navigation"]:
            continue
        else:
            values = form_data.getlist(key)
            if len(values) > 1:
                data[key] = values
            else:
                if value.startswith('[') and value.endswith(']'):
                    try:
                        data[key] = json.loads(value)
                    except:
                        data[key] = value
                else:
                    data[key] = value
    
    # Check if this is navigation
    if "_navigation" in form_data:
        nav_step = form_data["_navigation"]
        return RedirectResponse(url=f"/onboarding/{session_id}/step/{nav_step}", status_code=303)
    
    # Get processor
    processor = PROCESSORS.get(step_id)
    if not processor:
        raise HTTPException(status_code=400, detail=f"No processor for step {step_id}")
    
    try:
        # Process the step (NO VALIDATION)
        response = await processor(data, session["state"])
        response_dict = response.model_dump(mode='json')
        
        # Update state
        session["state"][f"step_{step_id}_request"] = data
        session["state"][f"step_{step_id}_response"] = response_dict
        
        # Get step from chain
        step = chain.steps[step_id]
        
        # Determine next step
        if step.is_exit_point:
            # Show completion page
            return HTMLResponse(content=generate_completion_page(session_id, session["state"]))
        
        # Get next step ID
        if step.conditional_next:
            next_step_id = step.conditional_next(response)
        else:
            next_step_id = step.next_step_id
        
        # If IT equipment step should be skipped, remove it from navigation
        if step_id == "employment_details" and not response.requires_equipment and next_step_id == "address_info":
            # Mark IT equipment as skipped
            session["state"]["step_it_equipment_skipped"] = True
        
        # Redirect to next step (must use 303 for POST->GET redirect)
        return RedirectResponse(url=f"/onboarding/{session_id}/step/{next_step_id}", status_code=303)
        
    except Exception as e:
        import traceback
        print(f"Error processing step {step_id}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


def generate_completion_page(session_id: str, state: dict) -> str:
    """Generate completion page with summary"""
    emp_data = state.get('step_basic_info_response', {})
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Onboarding Complete</title>
        <style>
            body {{
                font-family: -apple-system, system-ui, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .success {{
                background: #d4edda;
                color: #155724;
                padding: 1rem;
                border-radius: 4px;
                margin-bottom: 2rem;
            }}
            .summary {{
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 4px;
                margin: 1rem 0;
            }}
            .button {{
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 0.75rem 1.5rem;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 1rem;
            }}
            .nav-button {{
                display: inline-block;
                background: #007bff;
                color: white;
                padding: 0.5rem 1rem;
                text-decoration: none;
                border-radius: 4px;
                margin-right: 0.5rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">
                <h1>🎉 Onboarding Complete!</h1>
                <p>Congratulations! You have successfully completed the employee onboarding process.</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Employee ID:</strong> {emp_data.get('employee_id', 'N/A')}</p>
                <p><strong>Name:</strong> {emp_data.get('full_name', 'N/A')}</p>
                <p><strong>Start Date:</strong> {state.get('step_final_review_response', {}).get('start_date', 'TBD')}</p>
                <p><strong>Welcome Kit Tracking:</strong> {state.get('step_final_review_response', {}).get('welcome_kit_tracking', 'N/A')}</p>
                
                <h3>First Day Instructions:</h3>
                <p>{state.get('step_final_review_response', {}).get('first_day_instructions', 'Details will be sent via email.')}</p>
            </div>
            
            <div style="margin-top: 2rem;">
                <p>You can still review and update your information:</p>
    """
    
    # Add navigation to all completed steps
    for step in STEP_ORDER:
        if f"step_{step}_response" in state:
            html += f'<a href="/onboarding/{session_id}/step/{step}" class="nav-button">Review {STEP_TITLES[step]}</a>'
    
    html += """
            </div>
            
            <a href="/" class="button" style="margin-top: 2rem;">Start New Onboarding</a>
        </div>
    </body>
    </html>
    """
    
    return html


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions),
        "port": PORT,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 Starting Employee Onboarding Server v2.0 on port {PORT}")
    print(f"📍 Visit http://localhost:{PORT} to start onboarding")
    print(f"✨ Features: Navigation, No Validation, Step Summary")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)