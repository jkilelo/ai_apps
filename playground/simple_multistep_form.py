#!/usr/bin/env python3
"""
Simple multi-step form application using FastAPI, Jinja2, and Bootstrap 5.3
"""

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import uvicorn
from pathlib import Path

# Create FastAPI app
app = FastAPI(title="Multi-Step Form Demo")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Store form data (in production, use a database or session)
form_data = {}


# Models for form data
class FormData(BaseModel):
    # Form 1 fields
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    
    # Form 2 fields
    address: Optional[str] = ""
    city: Optional[str] = ""
    zipcode: Optional[str] = ""
    
    # Form 3 fields
    occupation: Optional[str] = ""
    company: Optional[str] = ""
    experience: Optional[str] = ""
    
    # Form 4 fields
    interests: Optional[str] = ""
    skills: Optional[str] = ""
    goals: Optional[str] = ""
    
    # Form 5 fields
    feedback: Optional[str] = ""
    rating: Optional[str] = ""
    recommend: Optional[str] = ""


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Display the home page"""
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "Multi-Step Form Demo"
    })


@app.get("/form/{step}", response_class=HTMLResponse)
async def show_form(request: Request, step: int):
    """Display a specific form step"""
    if step < 1 or step > 5:
        step = 1
    
    # Get existing data
    data = form_data.get("session", FormData())
    
    return templates.TemplateResponse(f"form{step}.html", {
        "request": request,
        "step": step,
        "data": data,
        "title": f"Step {step} of 5"
    })


@app.post("/form/{step}/submit", response_class=HTMLResponse)
async def submit_form(request: Request, step: int):
    """Handle form submission"""
    form = await request.form()
    
    # Get or create session data
    if "session" not in form_data:
        form_data["session"] = FormData()
    
    data = form_data["session"]
    
    # Update data based on step
    if step == 1:
        data.name = form.get("name", "")
        data.email = form.get("email", "")
        data.phone = form.get("phone", "")
    elif step == 2:
        data.address = form.get("address", "")
        data.city = form.get("city", "")
        data.zipcode = form.get("zipcode", "")
    elif step == 3:
        data.occupation = form.get("occupation", "")
        data.company = form.get("company", "")
        data.experience = form.get("experience", "")
    elif step == 4:
        data.interests = form.get("interests", "")
        data.skills = form.get("skills", "")
        data.goals = form.get("goals", "")
    elif step == 5:
        data.feedback = form.get("feedback", "")
        data.rating = form.get("rating", "")
        data.recommend = form.get("recommend", "")
    
    # Save updated data
    form_data["session"] = data
    
    # Determine next step
    next_step = step + 1
    if next_step > 5:
        # Show completion page
        return templates.TemplateResponse("complete.html", {
            "request": request,
            "data": data,
            "title": "Form Complete"
        })
    
    # Show next form with pre-filled data
    return templates.TemplateResponse(f"form{next_step}.html", {
        "request": request,
        "step": next_step,
        "data": data,
        "title": f"Step {next_step} of 5",
        "show_data": True  # Flag to show previous data
    })


@app.get("/reset")
async def reset_form():
    """Reset form data"""
    form_data.clear()
    return {"message": "Form data reset"}


# Create templates directory and files
def create_templates():
    """Create template files"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Multi-Step Form</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .step-indicator {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        .step {
            flex: 1;
            text-align: center;
            padding: 10px;
            background: #e9ecef;
            margin: 0 5px;
            border-radius: 5px;
            position: relative;
        }
        .step.active {
            background: #0d6efd;
            color: white;
        }
        .step.completed {
            background: #198754;
            color: white;
        }
        .data-display {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .data-display h5 {
            color: #495057;
            margin-bottom: 15px;
        }
        .data-item {
            margin-bottom: 8px;
        }
        .data-label {
            font-weight: bold;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Home page
    home_template = '''{% extends "base.html" %}
{% block content %}
<div class="card">
    <div class="card-body text-center">
        <h1 class="card-title">Multi-Step Form Demo</h1>
        <p class="card-text">This demo shows a 5-step form process where you fill in step 1, 
        then just click "Next" for the remaining steps while viewing your submitted data.</p>
        <a href="/form/1" class="btn btn-primary btn-lg">Start Form</a>
        <a href="/reset" class="btn btn-secondary btn-lg">Reset Data</a>
    </div>
</div>
{% endblock %}'''
    
    # Form 1 template
    form1_template = '''{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Personal Information</h2>

<!-- Step indicator -->
<div class="step-indicator">
    <div class="step active">Step 1</div>
    <div class="step">Step 2</div>
    <div class="step">Step 3</div>
    <div class="step">Step 4</div>
    <div class="step">Step 5</div>
</div>

<form method="post" action="/form/1/submit">
    <div class="mb-3">
        <label for="name" class="form-label">Name</label>
        <input type="text" class="form-control" id="name" name="name" value="{{ data.name }}" required>
    </div>
    <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" class="form-control" id="email" name="email" value="{{ data.email }}" required>
    </div>
    <div class="mb-3">
        <label for="phone" class="form-label">Phone</label>
        <input type="tel" class="form-control" id="phone" name="phone" value="{{ data.phone }}" required>
    </div>
    <button type="submit" class="btn btn-primary">Submit & Continue</button>
    <a href="/" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}'''
    
    # Form 2 template
    form2_template = '''{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Address Information</h2>

<!-- Step indicator -->
<div class="step-indicator">
    <div class="step completed">Step 1</div>
    <div class="step active">Step 2</div>
    <div class="step">Step 3</div>
    <div class="step">Step 4</div>
    <div class="step">Step 5</div>
</div>

{% if show_data %}
<div class="data-display">
    <h5>Your Submitted Information:</h5>
    <div class="data-item"><span class="data-label">Name:</span> {{ data.name }}</div>
    <div class="data-item"><span class="data-label">Email:</span> {{ data.email }}</div>
    <div class="data-item"><span class="data-label">Phone:</span> {{ data.phone }}</div>
</div>
{% endif %}

<form method="post" action="/form/2/submit">
    <div class="mb-3">
        <label for="address" class="form-label">Address</label>
        <input type="text" class="form-control" id="address" name="address" value="{{ data.address }}" readonly>
    </div>
    <div class="mb-3">
        <label for="city" class="form-label">City</label>
        <input type="text" class="form-control" id="city" name="city" value="{{ data.city }}" readonly>
    </div>
    <div class="mb-3">
        <label for="zipcode" class="form-label">Zip Code</label>
        <input type="text" class="form-control" id="zipcode" name="zipcode" value="{{ data.zipcode }}" readonly>
    </div>
    <button type="submit" class="btn btn-primary">Next</button>
</form>
{% endblock %}'''
    
    # Form 3 template
    form3_template = '''{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Professional Information</h2>

<!-- Step indicator -->
<div class="step-indicator">
    <div class="step completed">Step 1</div>
    <div class="step completed">Step 2</div>
    <div class="step active">Step 3</div>
    <div class="step">Step 4</div>
    <div class="step">Step 5</div>
</div>

{% if show_data %}
<div class="data-display">
    <h5>Your Submitted Information:</h5>
    <div class="row">
        <div class="col-md-6">
            <div class="data-item"><span class="data-label">Name:</span> {{ data.name }}</div>
            <div class="data-item"><span class="data-label">Email:</span> {{ data.email }}</div>
            <div class="data-item"><span class="data-label">Phone:</span> {{ data.phone }}</div>
        </div>
        <div class="col-md-6">
            <div class="data-item"><span class="data-label">Address:</span> {{ data.address }}</div>
            <div class="data-item"><span class="data-label">City:</span> {{ data.city }}</div>
            <div class="data-item"><span class="data-label">Zip:</span> {{ data.zipcode }}</div>
        </div>
    </div>
</div>
{% endif %}

<form method="post" action="/form/3/submit">
    <div class="mb-3">
        <label for="occupation" class="form-label">Occupation</label>
        <input type="text" class="form-control" id="occupation" name="occupation" value="{{ data.occupation }}" readonly>
    </div>
    <div class="mb-3">
        <label for="company" class="form-label">Company</label>
        <input type="text" class="form-control" id="company" name="company" value="{{ data.company }}" readonly>
    </div>
    <div class="mb-3">
        <label for="experience" class="form-label">Years of Experience</label>
        <input type="text" class="form-control" id="experience" name="experience" value="{{ data.experience }}" readonly>
    </div>
    <button type="submit" class="btn btn-primary">Next</button>
</form>
{% endblock %}'''
    
    # Form 4 template
    form4_template = '''{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Interests & Skills</h2>

<!-- Step indicator -->
<div class="step-indicator">
    <div class="step completed">Step 1</div>
    <div class="step completed">Step 2</div>
    <div class="step completed">Step 3</div>
    <div class="step active">Step 4</div>
    <div class="step">Step 5</div>
</div>

{% if show_data %}
<div class="data-display">
    <h5>Your Submitted Information:</h5>
    <div class="row">
        <div class="col-md-4">
            <div class="data-item"><span class="data-label">Name:</span> {{ data.name }}</div>
            <div class="data-item"><span class="data-label">Email:</span> {{ data.email }}</div>
            <div class="data-item"><span class="data-label">Phone:</span> {{ data.phone }}</div>
        </div>
        <div class="col-md-4">
            <div class="data-item"><span class="data-label">Address:</span> {{ data.address }}</div>
            <div class="data-item"><span class="data-label">City:</span> {{ data.city }}</div>
            <div class="data-item"><span class="data-label">Zip:</span> {{ data.zipcode }}</div>
        </div>
        <div class="col-md-4">
            <div class="data-item"><span class="data-label">Occupation:</span> {{ data.occupation }}</div>
            <div class="data-item"><span class="data-label">Company:</span> {{ data.company }}</div>
            <div class="data-item"><span class="data-label">Experience:</span> {{ data.experience }}</div>
        </div>
    </div>
</div>
{% endif %}

<form method="post" action="/form/4/submit">
    <div class="mb-3">
        <label for="interests" class="form-label">Interests</label>
        <textarea class="form-control" id="interests" name="interests" rows="2" readonly>{{ data.interests }}</textarea>
    </div>
    <div class="mb-3">
        <label for="skills" class="form-label">Skills</label>
        <textarea class="form-control" id="skills" name="skills" rows="2" readonly>{{ data.skills }}</textarea>
    </div>
    <div class="mb-3">
        <label for="goals" class="form-label">Goals</label>
        <textarea class="form-control" id="goals" name="goals" rows="2" readonly>{{ data.goals }}</textarea>
    </div>
    <button type="submit" class="btn btn-primary">Next</button>
</form>
{% endblock %}'''
    
    # Form 5 template
    form5_template = '''{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Feedback</h2>

<!-- Step indicator -->
<div class="step-indicator">
    <div class="step completed">Step 1</div>
    <div class="step completed">Step 2</div>
    <div class="step completed">Step 3</div>
    <div class="step completed">Step 4</div>
    <div class="step active">Step 5</div>
</div>

{% if show_data %}
<div class="data-display">
    <h5>Your Complete Information:</h5>
    <div class="row">
        <div class="col-md-6">
            <h6 class="text-primary">Personal Info</h6>
            <div class="data-item"><span class="data-label">Name:</span> {{ data.name }}</div>
            <div class="data-item"><span class="data-label">Email:</span> {{ data.email }}</div>
            <div class="data-item"><span class="data-label">Phone:</span> {{ data.phone }}</div>
            <div class="data-item"><span class="data-label">Address:</span> {{ data.address }}</div>
            <div class="data-item"><span class="data-label">City:</span> {{ data.city }}</div>
            <div class="data-item"><span class="data-label">Zip:</span> {{ data.zipcode }}</div>
        </div>
        <div class="col-md-6">
            <h6 class="text-primary">Professional Info</h6>
            <div class="data-item"><span class="data-label">Occupation:</span> {{ data.occupation }}</div>
            <div class="data-item"><span class="data-label">Company:</span> {{ data.company }}</div>
            <div class="data-item"><span class="data-label">Experience:</span> {{ data.experience }}</div>
            <div class="data-item"><span class="data-label">Interests:</span> {{ data.interests }}</div>
            <div class="data-item"><span class="data-label">Skills:</span> {{ data.skills }}</div>
            <div class="data-item"><span class="data-label">Goals:</span> {{ data.goals }}</div>
        </div>
    </div>
</div>
{% endif %}

<form method="post" action="/form/5/submit">
    <div class="mb-3">
        <label for="feedback" class="form-label">Your Feedback</label>
        <textarea class="form-control" id="feedback" name="feedback" rows="3" readonly>{{ data.feedback }}</textarea>
    </div>
    <div class="mb-3">
        <label for="rating" class="form-label">Rating</label>
        <select class="form-control" id="rating" name="rating" disabled>
            <option value="">Select rating</option>
            <option value="5" {% if data.rating == "5" %}selected{% endif %}>5 - Excellent</option>
            <option value="4" {% if data.rating == "4" %}selected{% endif %}>4 - Good</option>
            <option value="3" {% if data.rating == "3" %}selected{% endif %}>3 - Average</option>
            <option value="2" {% if data.rating == "2" %}selected{% endif %}>2 - Poor</option>
            <option value="1" {% if data.rating == "1" %}selected{% endif %}>1 - Very Poor</option>
        </select>
    </div>
    <div class="mb-3">
        <label for="recommend" class="form-label">Would you recommend?</label>
        <select class="form-control" id="recommend" name="recommend" disabled>
            <option value="">Select option</option>
            <option value="yes" {% if data.recommend == "yes" %}selected{% endif %}>Yes</option>
            <option value="no" {% if data.recommend == "no" %}selected{% endif %}>No</option>
            <option value="maybe" {% if data.recommend == "maybe" %}selected{% endif %}>Maybe</option>
        </select>
    </div>
    <button type="submit" class="btn btn-success">Complete Form</button>
</form>
{% endblock %}'''
    
    # Completion template
    complete_template = '''{% extends "base.html" %}
{% block content %}
<div class="text-center">
    <h1 class="text-success mb-4">🎉 Form Completed!</h1>
    <p class="lead">Thank you for completing the multi-step form.</p>
</div>

<div class="card mt-4">
    <div class="card-header bg-success text-white">
        <h4 class="mb-0">Your Complete Submission</h4>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <h5 class="text-primary">Personal Information</h5>
                <ul class="list-unstyled">
                    <li><strong>Name:</strong> {{ data.name }}</li>
                    <li><strong>Email:</strong> {{ data.email }}</li>
                    <li><strong>Phone:</strong> {{ data.phone }}</li>
                    <li><strong>Address:</strong> {{ data.address }}</li>
                    <li><strong>City:</strong> {{ data.city }}</li>
                    <li><strong>Zip Code:</strong> {{ data.zipcode }}</li>
                </ul>
            </div>
            <div class="col-md-6">
                <h5 class="text-primary">Professional Information</h5>
                <ul class="list-unstyled">
                    <li><strong>Occupation:</strong> {{ data.occupation }}</li>
                    <li><strong>Company:</strong> {{ data.company }}</li>
                    <li><strong>Experience:</strong> {{ data.experience }}</li>
                    <li><strong>Interests:</strong> {{ data.interests }}</li>
                    <li><strong>Skills:</strong> {{ data.skills }}</li>
                    <li><strong>Goals:</strong> {{ data.goals }}</li>
                </ul>
                <h5 class="text-primary mt-3">Feedback</h5>
                <ul class="list-unstyled">
                    <li><strong>Feedback:</strong> {{ data.feedback }}</li>
                    <li><strong>Rating:</strong> {{ data.rating }}</li>
                    <li><strong>Would Recommend:</strong> {{ data.recommend }}</li>
                </ul>
            </div>
        </div>
    </div>
</div>

<div class="text-center mt-4">
    <a href="/" class="btn btn-primary">Start New Form</a>
    <a href="/reset" class="btn btn-secondary">Reset Data</a>
</div>
{% endblock %}'''
    
    # Write all templates
    (templates_dir / "base.html").write_text(base_template)
    (templates_dir / "home.html").write_text(home_template)
    (templates_dir / "form1.html").write_text(form1_template)
    (templates_dir / "form2.html").write_text(form2_template)
    (templates_dir / "form3.html").write_text(form3_template)
    (templates_dir / "form4.html").write_text(form4_template)
    (templates_dir / "form5.html").write_text(form5_template)
    (templates_dir / "complete.html").write_text(complete_template)


if __name__ == "__main__":
    # Create templates
    create_templates()
    print("Templates created successfully!")
    
    # Run the app
    print("Starting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)