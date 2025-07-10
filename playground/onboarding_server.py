#!/usr/bin/env python3
"""
FastAPI server for the 10-step employee onboarding form
"""

import sys
import json
import base64
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional
from uuid import uuid4
import asyncio

sys.path.insert(0, '/var/www/ai_apps/playground')

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import ValidationError

from employee_onboarding_10steps import (
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
    description="10-step employee onboarding process",
    version="1.0.0"
)

# Store active onboarding sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

# Create the onboarding chain
onboarding_chain = create_employee_onboarding_chain()


# Mock processors for each step
async def process_basic_info(data: dict, context: dict) -> BasicInfoResponse:
    """Process basic information and create employee ID"""
    employee_id = f"EMP-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"
    
    dob = data.get('date_of_birth')
    if isinstance(dob, str):
        dob = date.fromisoformat(dob)
    
    age = date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day))
    
    return BasicInfoResponse(
        employee_id=employee_id,
        full_name=f"{data['first_name']} {data['last_name']}",
        age=age,
        email_verified=True
    )


async def process_employment_details(data: dict, context: dict) -> EmploymentDetailsResponse:
    """Process employment details"""
    requires_equipment = data['department'] == 'engineering'  # Only engineering needs equipment
    requires_visa = False  # Simplified
    
    probation_days = {
        'full_time': 90,
        'part_time': 60,
        'contract': 0,
        'intern': 30
    }
    
    return EmploymentDetailsResponse(
        compensation_package_id=f"COMP-{str(uuid4())[:8]}",
        requires_equipment=requires_equipment,
        requires_visa=requires_visa,
        probation_period_days=probation_days.get(data['employment_type'], 90)
    )


async def process_address_info(data: dict, context: dict) -> AddressInfoResponse:
    """Process address information"""
    return AddressInfoResponse(
        address_id=f"ADDR-{str(uuid4())[:8]}",
        tax_jurisdiction=data['state'],
        commute_eligible=data['work_location'] in ['office', 'hybrid'],
        remote_setup_required=data['work_location'] in ['remote', 'hybrid']
    )


async def process_emergency_contact(data: dict, context: dict) -> EmergencyContactResponse:
    """Process emergency contact"""
    return EmergencyContactResponse(
        contact_id=f"EMRG-{str(uuid4())[:8]}",
        verified=True
    )


async def process_education_experience(data: dict, context: dict) -> EducationExperienceResponse:
    """Process education and experience"""
    skill_level = "senior" if int(data['years_of_experience']) >= 5 else "junior"
    
    training_recs = []
    if skill_level == "junior":
        training_recs.extend(["Mentorship Program", "Technical Foundations"])
    if 'python' in [s.lower() for s in data.get('skills', [])]:
        training_recs.append("Advanced Python Workshop")
        
    return EducationExperienceResponse(
        profile_id=f"PROF-{str(uuid4())[:8]}",
        skill_level=skill_level,
        training_recommendations=training_recs
    )


async def process_benefits_selection(data: dict, context: dict) -> BenefitsSelectionResponse:
    """Process benefits selection"""
    # Simple cost calculation
    base_costs = {
        'basic': 100,
        'standard': 200,
        'premium': 400
    }
    
    total = base_costs.get(data['health_plan'], 200)
    total += base_costs.get(data['dental_plan'], 200) * 0.3
    total += base_costs.get(data['vision_plan'], 200) * 0.2
    total += float(data.get('fsa_contribution', 0)) * 0.1
    
    return BenefitsSelectionResponse(
        benefits_package_id=f"BEN-{str(uuid4())[:8]}",
        total_cost=Decimal(str(total)),
        employee_contribution=Decimal(str(total * 0.3)),
        effective_date=date.today().replace(day=1)
    )


async def process_it_equipment(data: dict, context: dict) -> ITEquipmentResponse:
    """Process IT equipment request"""
    # Calculate cost
    base_cost = 2000  # Laptop
    if data.get('needs_monitor'):
        base_cost += 400 * int(data.get('monitor_count', 1))
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
        security_training_required=data.get('security_clearance_required', False)
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
    emp_details = context.get('step_employment_details_response', {})
    
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Employee Onboarding System</h1>
            <p>Welcome to our comprehensive 10-step employee onboarding process.</p>
            
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
            
            <p>This onboarding process features:</p>
            <ul>
                <li>Conditional routing based on your role</li>
                <li>Dynamic field injection</li>
                <li>State persistence across all steps</li>
                <li>Comprehensive validation</li>
                <li>Real-time processing</li>
            </ul>
            
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
        "started_at": datetime.now()
    }
    
    # Generate first form
    html = onboarding_chain.generate_form_html("basic_info")
    
    # Update form action to include session ID
    html = html.replace(
        'action="/api/chain/employee_onboarding/process/',
        f'action="/api/onboarding/{session_id}/process/'
    )
    
    return HTMLResponse(content=html)


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
    
    # Debug: Log form data
    print(f"Processing {step_id} for session {session_id}")
    print(f"Form data keys: {list(form_data.keys())}")
    
    # Convert form data to dict
    for key, value in form_data.items():
        if key == "chain_state":
            # Decode chain state
            if value:
                try:
                    decoded = base64.b64decode(value).decode('utf-8')
                    session["state"] = json.loads(decoded)
                except:
                    pass
        elif key == "csrf_token":
            # Skip CSRF token - it's not part of the model
            continue
        else:
            # Handle multiple values (for checkboxes/multi-select)
            values = form_data.getlist(key)
            if len(values) > 1:
                data[key] = values
            else:
                # Try to parse JSON for array fields
                if value.startswith('[') and value.endswith(']'):
                    try:
                        data[key] = json.loads(value)
                    except:
                        data[key] = value
                else:
                    data[key] = value
    
    # Get the processor
    processor = PROCESSORS.get(step_id)
    if not processor:
        # No processor, return error
        return JSONResponse(
            content={
                "error": True,
                "message": f"No processor for step {step_id}"
            },
            status_code=400
        )
    
    try:
        # First validate the data using the step's request model
        step = chain.steps[step_id]
        request_model = step.request_model
        
        # Try to create the request model to validate
        try:
            validated_data = request_model(**data)
        except ValidationError as e:
            print(f"Validation error for {step_id}:")
            print(f"Data submitted: {data}")
            print(f"Validation errors: {e.errors()}")
            
            # Convert errors to serializable format
            errors = []
            for err in e.errors():
                error_dict = {
                    "field": ".".join(str(x) for x in err.get("loc", [])),
                    "message": err.get("msg", ""),
                    "type": err.get("type", "")
                }
                errors.append(error_dict)
            
            return JSONResponse(
                content={
                    "error": True,
                    "errors": errors,
                    "message": "Validation failed"
                },
                status_code=400
            )
        
        # Process the step
        response = await processor(data, session["state"])
        
        # Convert response to dict with JSON serialization
        response_dict = response.model_dump(mode='json')
        
        # Update state
        session["state"][f"step_{step_id}_request"] = data
        session["state"][f"step_{step_id}_response"] = response_dict
        
        # Get step from chain
        step = chain.steps[step_id]
        
        # Determine next step
        if step.is_exit_point:
            # Chain complete
            del active_sessions[session_id]
            return JSONResponse(content={
                "completed": True,
                "message": "Onboarding completed successfully!",
                "final_data": session["state"]
            })
        
        # Get next step ID
        if step.conditional_next:
            next_step_id = step.conditional_next(response)
        else:
            next_step_id = step.next_step_id
        
        if not next_step_id:
            # No next step, complete
            del active_sessions[session_id]
            return JSONResponse(content={
                "completed": True,
                "message": "Process completed!",
                "final_data": session["state"]
            })
        
        # Generate next form
        next_html = chain.generate_form_html(next_step_id, session["state"])
        
        # Update form action
        next_html = next_html.replace(
            'action="/api/chain/employee_onboarding/process/',
            f'action="/api/onboarding/{session_id}/process/'
        )
        
        # Encode updated state
        encoded_state = base64.b64encode(
            json.dumps(session["state"]).encode()
        ).decode()
        
        # Update hidden state field
        next_html = next_html.replace(
            'name="chain_state" value=""',
            f'name="chain_state" value="{encoded_state}"'
        )
        
        return JSONResponse(content={
            "next_step_id": next_step_id,
            "next_form_html": next_html,
            "chain_state": session["state"]
        })
        
    except ValidationError as e:
        # Convert errors to serializable format
        errors = []
        for err in e.errors():
            error_dict = {
                "field": ".".join(str(x) for x in err.get("loc", [])),
                "message": err.get("msg", ""),
                "type": err.get("type", "")
            }
            errors.append(error_dict)
        
        return JSONResponse(
            content={
                "error": True,
                "errors": errors,
                "message": "Validation failed"
            },
            status_code=400
        )
    except Exception as e:
        import traceback
        print(f"Error processing step {step_id}: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            content={
                "error": True,
                "message": str(e)
            },
            status_code=500
        )


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
    
    print(f"🚀 Starting Employee Onboarding Server on port {PORT}")
    print(f"📍 Visit http://localhost:{PORT} to start onboarding")
    print(f"🔧 10-step process with conditional routing and validation")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)