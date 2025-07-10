from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Optional
import uvicorn

app = FastAPI(title="Beautiful Forms App")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage with navigation to all forms"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request, response_data: Optional[dict] = None):
    """Contact form page"""
    return templates.TemplateResponse("contact.html", {
        "request": request, 
        "response_data": response_data
    })

@app.post("/contact", response_class=HTMLResponse)
async def submit_contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    """Handle contact form submission"""
    response_data = {
        "name": name.upper(),
        "email": email.upper(),
        "subject": subject.upper(),
        "message": message.upper()
    }
    return templates.TemplateResponse("contact.html", {
        "request": request, 
        "response_data": response_data
    })

@app.get("/registration", response_class=HTMLResponse)
async def registration_form(request: Request, response_data: Optional[dict] = None):
    """Registration form page"""
    return templates.TemplateResponse("registration.html", {
        "request": request, 
        "response_data": response_data
    })

@app.post("/registration", response_class=HTMLResponse)
async def submit_registration(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    phone: str = Form(...),
    country: str = Form(...),
    terms: Optional[str] = Form(None)
):
    """Handle registration form submission"""
    response_data = {
        "first_name": first_name.upper(),
        "last_name": last_name.upper(),
        "email": email.upper(),
        "password": "***HIDDEN***",
        "confirm_password": "***HIDDEN***",
        "phone": phone.upper(),
        "country": country.upper(),
        "terms": "ACCEPTED" if terms else "NOT ACCEPTED"
    }
    return templates.TemplateResponse("registration.html", {
        "request": request, 
        "response_data": response_data
    })

@app.get("/survey", response_class=HTMLResponse)
async def survey_form(request: Request, response_data: Optional[dict] = None):
    """Survey form page"""
    return templates.TemplateResponse("survey.html", {
        "request": request, 
        "response_data": response_data
    })

@app.post("/survey", response_class=HTMLResponse)
async def submit_survey(
    request: Request,
    name: str = Form(...),
    age: str = Form(...),
    occupation: str = Form(...),
    experience: str = Form(...),
    satisfaction: str = Form(...),
    feedback: str = Form(...),
    recommend: Optional[str] = Form(None)
):
    """Handle survey form submission"""
    response_data = {
        "name": name.upper(),
        "age": age.upper(),
        "occupation": occupation.upper(),
        "experience": experience.upper(),
        "satisfaction": satisfaction.upper(),
        "feedback": feedback.upper(),
        "recommend": "YES" if recommend else "NO"
    }
    return templates.TemplateResponse("survey.html", {
        "request": request, 
        "response_data": response_data
    })

@app.get("/job-application", response_class=HTMLResponse)
async def job_application_form(request: Request, response_data: Optional[dict] = None):
    """Job application form page"""
    return templates.TemplateResponse("job_application.html", {
        "request": request, 
        "response_data": response_data
    })

@app.post("/job-application", response_class=HTMLResponse)
async def submit_job_application(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    experience_years: str = Form(...),
    salary_expectation: str = Form(...),
    cover_letter: str = Form(...),
    availability: str = Form(...)
):
    """Handle job application form submission"""
    response_data = {
        "full_name": full_name.upper(),
        "email": email.upper(),
        "phone": phone.upper(),
        "position": position.upper(),
        "experience_years": experience_years.upper(),
        "salary_expectation": salary_expectation.upper(),
        "cover_letter": cover_letter.upper(),
        "availability": availability.upper()
    }
    return templates.TemplateResponse("job_application.html", {
        "request": request, 
        "response_data": response_data
    })

@app.get("/feedback", response_class=HTMLResponse)
async def feedback_form(request: Request, response_data: Optional[dict] = None):
    """Feedback form page"""
    return templates.TemplateResponse("feedback.html", {
        "request": request, 
        "response_data": response_data
    })

@app.post("/feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    customer_name: str = Form(...),
    email: str = Form(...),
    product_service: str = Form(...),
    rating: str = Form(...),
    improvement_areas: str = Form(...),
    additional_comments: str = Form(...),
    contact_back: Optional[str] = Form(None)
):
    """Handle feedback form submission"""
    response_data = {
        "customer_name": customer_name.upper(),
        "email": email.upper(),
        "product_service": product_service.upper(),
        "rating": rating.upper(),
        "improvement_areas": improvement_areas.upper(),
        "additional_comments": additional_comments.upper(),
        "contact_back": "YES" if contact_back else "NO"
    }
    return templates.TemplateResponse("feedback.html", {
        "request": request, 
        "response_data": response_data
    })

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
