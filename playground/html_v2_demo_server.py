#!/usr/bin/env python3
"""
FastAPI Demo Server for HTML Form Wizard v2 Examples

This server demonstrates all the form examples with working endpoints.
Run with: python html_v2_demo_server.py
Then visit: http://localhost:8036
"""

from fastapi import FastAPI, Response, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
import json
from datetime import datetime
import uvicorn

# Import our examples
from html_v2_examples import (
    create_job_application_form,
    create_customer_survey,
    create_event_registration,
    create_patient_intake_form,
    create_product_feedback_form,
    create_restaurant_reservation,
    create_real_estate_inquiry,
    PYDANTIC_AVAILABLE
)

if PYDANTIC_AVAILABLE:
    from html_v2_examples import create_course_enrollment_form

app = FastAPI(title="HTML Form Wizard v2 Demo")


# Homepage with all available forms
@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Display all available form examples"""
    
    forms = [
        {
            "url": "/job-application",
            "title": "Job Application",
            "description": "Multi-step application with resume upload, skills tags, and conditional fields",
            "features": ["File Upload", "Tags Input", "Rich Text", "Conditional Fields"],
            "steps": 3
        },
        {
            "url": "/customer-survey",
            "title": "Customer Survey",
            "description": "Dynamic survey that adapts questions based on your responses",
            "features": ["Dynamic Questions", "Rating Fields", "Conditional Logic"],
            "steps": 3
        },
        {
            "url": "/event-registration",
            "title": "Event Registration",
            "description": "Conference registration with workshop selection and dietary preferences",
            "features": ["Multi-select", "File Upload", "Conditional Fields"],
            "steps": 3
        },
        {
            "url": "/patient-intake",
            "title": "Medical Patient Intake",
            "description": "Secure medical form with health history and insurance information",
            "features": ["Privacy Features", "Tags Input", "Conditional Sections"],
            "steps": 3
        },
        {
            "url": "/product-feedback",
            "title": "Product Review",
            "description": "Product feedback form with ratings, image upload, and rich text editor",
            "features": ["Rich Text Editor", "Ratings", "Autocomplete", "Image Upload"],
            "steps": 1
        },
        {
            "url": "/restaurant-reservation",
            "title": "Restaurant Reservation",
            "description": "Table booking with date/time selection and special requests",
            "features": ["Date/Time Pickers", "Conditional Fields", "Special Requests"],
            "steps": 1
        },
        {
            "url": "/real-estate-inquiry",
            "title": "Real Estate Inquiry",
            "description": "Property inquiry that adapts based on buying, selling, or renting",
            "features": ["Dynamic Fields", "Tags Input", "Rich Text", "File Upload"],
            "steps": 3
        }
    ]
    
    if PYDANTIC_AVAILABLE:
        forms.append({
            "url": "/course-enrollment",
            "title": "Course Enrollment",
            "description": "Online course registration generated from Pydantic model",
            "features": ["Pydantic Integration", "Auto-generated", "Type Validation"],
            "steps": 1
        })
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HTML Form Wizard v2 - Real-Life Examples</title>
        <style>
            * { box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                background: #f5f5f5;
                margin: 0;
                padding: 0;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 60px 20px;
                text-align: center;
            }
            
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }
            
            .header p {
                margin: 10px 0 0;
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            
            .intro {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 40px;
            }
            
            .intro h2 {
                margin-top: 0;
                color: #4a5568;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            
            .feature {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .feature-icon {
                font-size: 24px;
            }
            
            .forms-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 30px;
            }
            
            .form-card {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .form-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }
            
            .form-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
            }
            
            .form-header h3 {
                margin: 0;
                font-size: 1.4em;
            }
            
            .form-body {
                padding: 20px;
            }
            
            .form-description {
                color: #666;
                margin-bottom: 15px;
            }
            
            .form-features {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 20px;
            }
            
            .feature-tag {
                background: #e2e8f0;
                color: #4a5568;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.85em;
            }
            
            .form-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .steps-badge {
                background: #f7fafc;
                color: #718096;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 0.9em;
            }
            
            .try-button {
                background: #667eea;
                color: white;
                text-decoration: none;
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: 500;
                transition: background 0.3s;
            }
            
            .try-button:hover {
                background: #5a67d8;
            }
            
            .api-section {
                background: #2d3748;
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin-top: 40px;
            }
            
            .api-section h3 {
                margin-top: 0;
            }
            
            .api-section code {
                background: #1a202c;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            
            .endpoint-list {
                background: #1a202c;
                padding: 20px;
                border-radius: 4px;
                margin-top: 15px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                line-height: 1.8;
                overflow-x: auto;
            }
            
            .endpoint-list .method {
                font-weight: bold;
                margin-right: 10px;
            }
            
            .get { color: #48bb78; }
            .post { color: #4299e1; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 HTML Form Wizard v2 Examples</h1>
            <p>Real-world form implementations with advanced features</p>
        </div>
        
        <div class="container">
            <div class="intro">
                <h2>Welcome to the Form Wizard Demo</h2>
                <p>These examples demonstrate real-life scenarios using the enhanced HTML Form Wizard v2. Each form showcases different features and use cases.</p>
                
                <div class="features-grid">
                    <div class="feature">
                        <span class="feature-icon">🔒</span>
                        <span>CSRF Protection</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">📊</span>
                        <span>Form Analytics</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">💾</span>
                        <span>Auto-save Progress</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">🎨</span>
                        <span>Multiple Themes</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">📱</span>
                        <span>Mobile Responsive</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">⚡</span>
                        <span>Real-time Validation</span>
                    </div>
                </div>
            </div>
            
            <div class="forms-grid">
    """
    
    # Add form cards
    for form in forms:
        features_html = "".join(f'<span class="feature-tag">{feat}</span>' for feat in form["features"])
        
        html_content += f"""
                <div class="form-card">
                    <div class="form-header">
                        <h3>{form["title"]}</h3>
                    </div>
                    <div class="form-body">
                        <p class="form-description">{form["description"]}</p>
                        <div class="form-features">
                            {features_html}
                        </div>
                        <div class="form-footer">
                            <span class="steps-badge">{form["steps"]} steps</span>
                            <a href="{form["url"]}" class="try-button">Try it →</a>
                        </div>
                    </div>
                </div>
        """
    
    html_content += """
            </div>
            
            <div class="api-section">
                <h3>API Endpoints</h3>
                <p>All forms submit to working API endpoints that return JSON responses:</p>
                
                <div class="endpoint-list">
                    <div><span class="method get">GET</span> /api/health - Check API status</div>
                    <div><span class="method post">POST</span> /api/job-application - Submit job application</div>
                    <div><span class="method post">POST</span> /api/survey - Submit customer survey</div>
                    <div><span class="method post">POST</span> /api/event-registration - Register for event</div>
                    <div><span class="method post">POST</span> /api/patient-intake - Submit patient form</div>
                    <div><span class="method post">POST</span> /api/product-review - Submit product review</div>
                    <div><span class="method post">POST</span> /api/restaurant-reservation - Make reservation</div>
                    <div><span class="method post">POST</span> /api/real-estate-inquiry - Submit property inquiry</div>
                    <div><span class="method post">POST</span> /api/course-enrollment - Enroll in course</div>
                    <div><span class="method post">POST</span> /api/validate/email - Validate email (Ajax)</div>
                    <div><span class="method post">POST</span> /api/validate/username - Validate username (Ajax)</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


# Form display endpoints
@app.get("/job-application", response_class=HTMLResponse)
async def job_application_form():
    wizard = create_job_application_form()
    return HTMLResponse(content=wizard.generate_html())


@app.get("/customer-survey", response_class=HTMLResponse)
async def customer_survey_form():
    wizard = create_customer_survey()
    return HTMLResponse(content=wizard.generate_html())


@app.get("/event-registration", response_class=HTMLResponse)
async def event_registration_form():
    wizard = create_event_registration()
    return HTMLResponse(content=wizard.generate_html())


@app.get("/patient-intake", response_class=HTMLResponse)
async def patient_intake_form():
    wizard = create_patient_intake_form()
    return HTMLResponse(content=wizard.generate_html())


@app.get("/product-feedback", response_class=HTMLResponse)
async def product_feedback_form():
    wizard = create_product_feedback_form()
    return HTMLResponse(content=wizard.generate_html())


@app.get("/restaurant-reservation", response_class=HTMLResponse)
async def restaurant_reservation_form():
    wizard = create_restaurant_reservation()
    return HTMLResponse(content=wizard.generate_html())


@app.get("/real-estate-inquiry", response_class=HTMLResponse)
async def real_estate_inquiry_form():
    wizard = create_real_estate_inquiry()
    return HTMLResponse(content=wizard.generate_html())


if PYDANTIC_AVAILABLE:
    @app.get("/course-enrollment", response_class=HTMLResponse)
    async def course_enrollment_form():
        wizard = create_course_enrollment_form()
        return HTMLResponse(content=wizard.generate_html())


# API endpoints for form submissions
@app.post("/api/{form_type}")
async def handle_form_submission(form_type: str, request: Request):
    """Generic form submission handler"""
    
    # Get form data
    form_data = await request.form()
    
    # Convert to dict and handle files
    data = {}
    files = []
    
    for key, value in form_data.items():
        if hasattr(value, 'filename'):  # It's a file
            files.append({
                "field": key,
                "filename": value.filename,
                "content_type": value.content_type,
                "size": len(await value.read())
            })
        else:
            # Handle arrays (checkboxes)
            if key in data:
                if not isinstance(data[key], list):
                    data[key] = [data[key]]
                data[key].append(value)
            else:
                data[key] = value
    
    # Create response
    response = {
        "status": "success",
        "message": f"Thank you! Your {form_type.replace('-', ' ')} has been received.",
        "form_type": form_type,
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "files": files if files else None,
        "next_steps": get_next_steps(form_type)
    }
    
    return JSONResponse(content=response)


def get_next_steps(form_type: str) -> str:
    """Return appropriate next steps message based on form type"""
    
    messages = {
        "job-application": "We'll review your application and contact you within 3-5 business days.",
        "survey": "Thank you for your feedback! We value your input and will use it to improve our services.",
        "event-registration": "You're registered! Check your email for confirmation and event details.",
        "patient-intake": "Your information has been saved. Please arrive 15 minutes before your appointment.",
        "product-review": "Thank you for your review! It will be published after moderation.",
        "restaurant-reservation": "Your table is reserved! You'll receive a confirmation text shortly.",
        "real-estate-inquiry": "An agent will contact you within 24 hours to discuss your requirements.",
        "course-enrollment": "Welcome to the course! Check your email for login credentials and course materials."
    }
    
    return messages.get(form_type, "Thank you for your submission!")


# Validation endpoints for Ajax validation
@app.post("/api/validate/email")
async def validate_email(request: Request):
    """Email validation endpoint for real-time validation"""
    data = await request.json()
    email = data.get("value", "")
    
    # Simple validation (in production, check if email already exists, etc.)
    if "@" in email and "." in email.split("@")[1]:
        return {"valid": True}
    else:
        return {"valid": False, "message": "Please enter a valid email address"}


@app.post("/api/validate/username")
async def validate_username(request: Request):
    """Username validation endpoint for real-time validation"""
    data = await request.json()
    username = data.get("value", "")
    
    # Simulate checking if username is taken
    taken_usernames = ["admin", "user", "test", "demo"]
    
    if len(username) < 4:
        return {"valid": False, "message": "Username must be at least 4 characters"}
    elif username.lower() in taken_usernames:
        return {"valid": False, "message": "This username is already taken"}
    else:
        return {"valid": True, "message": "Username is available"}


# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Analytics endpoint
@app.post("/api/analytics")
async def track_analytics(request: Request):
    """Track form analytics events"""
    data = await request.json()
    
    # In a real app, you'd save this to a database
    print(f"Analytics Event: {data.get('event')} for form {data.get('formId')}")
    
    return {"status": "tracked"}


# Autocomplete endpoint for companies
@app.get("/api/companies/search")
async def search_companies(q: str = ""):
    """Autocomplete endpoint for company names"""
    
    companies = [
        "Apple Inc.", "Amazon", "Google", "Microsoft", "Meta",
        "Tesla", "Netflix", "Adobe", "Salesforce", "Oracle",
        "IBM", "Intel", "Cisco", "Dell Technologies", "HP Inc."
    ]
    
    # Filter based on query
    if q:
        filtered = [c for c in companies if q.lower() in c.lower()]
        return filtered[:5]  # Return top 5 matches
    
    return companies[:5]


if __name__ == "__main__":
    print("🚀 Starting HTML Form Wizard v2 Demo Server")
    print("📍 Visit http://localhost:8036 to see all examples")
    print("✨ Features: CSRF, Analytics, Autosave, Rich Text, File Upload, and more!")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8036)