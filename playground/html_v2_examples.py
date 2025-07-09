#!/usr/bin/env python3
"""
Comprehensive Real-Life Examples for HTML Form Wizard v2

This file contains working examples of various real-world forms using html_v2.py.
All examples are ready to run and demonstrate different features.
"""

import sys
import os
from datetime import datetime, date, timedelta
from typing import List, Optional
from enum import Enum

# Add current directory to path to import html_v2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from html_v2 import (
    FormWizard, FormStep, FormField, FieldType, ValidationRule, 
    FormTheme, FormI18n, PydanticFormConverter
)

# Check if Pydantic is available
try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("Note: Pydantic not installed. Some examples will be skipped.")


# Example 1: Job Application Form
def create_job_application_form():
    """
    Multi-step job application with resume upload, skills tags, and conditional fields
    """
    
    # Step 1: Personal Information
    personal_fields = [
        FormField(
            name="full_name",
            type=FieldType.TEXT,
            label="Full Name",
            placeholder="John Doe",
            validation_rules=[
                ValidationRule("required", message="Full name is required"),
                ValidationRule("minlength", 2, "Name must be at least 2 characters")
            ],
            real_time_validate=True
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email Address",
            placeholder="john@example.com",
            validation_rules=[
                ValidationRule("required", message="Email is required"),
                ValidationRule("pattern", r"[^@]+@[^@]+\.[^@]+", "Please enter a valid email")
            ],
            real_time_validate=True
        ),
        FormField(
            name="phone",
            type=FieldType.TEL,
            label="Phone Number",
            placeholder="(555) 123-4567",
            validation_rules=[
                ValidationRule("required", message="Phone number is required")
            ]
        ),
        FormField(
            name="linkedin_url",
            type=FieldType.URL,
            label="LinkedIn Profile",
            placeholder="https://linkedin.com/in/yourprofile",
            help_text="Optional but recommended"
        ),
        FormField(
            name="location",
            type=FieldType.TEXT,
            label="Current Location",
            placeholder="City, State/Country",
            validation_rules=[
                ValidationRule("required", message="Location is required")
            ]
        ),
        FormField(
            name="willing_to_relocate",
            type=FieldType.RADIO,
            label="Willing to Relocate?",
            options=[
                {"value": "yes", "label": "Yes"},
                {"value": "no", "label": "No"},
                {"value": "maybe", "label": "Open to discussion"}
            ],
            validation_rules=[
                ValidationRule("required", message="Please select an option")
            ]
        )
    ]
    
    # Step 2: Professional Experience
    experience_fields = [
        FormField(
            name="years_experience",
            type=FieldType.NUMBER,
            label="Years of Professional Experience",
            placeholder="5",
            validation_rules=[
                ValidationRule("required", message="Years of experience is required"),
                ValidationRule("min", 0, "Years cannot be negative"),
                ValidationRule("max", 50, "Please enter a valid number of years")
            ]
        ),
        FormField(
            name="current_position",
            type=FieldType.TEXT,
            label="Current/Most Recent Position",
            placeholder="Senior Software Engineer",
            validation_rules=[
                ValidationRule("required", message="Current position is required")
            ]
        ),
        FormField(
            name="current_company",
            type=FieldType.TEXT,
            label="Current/Most Recent Company",
            placeholder="Tech Corp Inc.",
            validation_rules=[
                ValidationRule("required", message="Company name is required")
            ]
        ),
        FormField(
            name="skills",
            type=FieldType.TAGS,
            label="Technical Skills",
            placeholder="Type a skill and press Enter",
            help_text="Add your key technical skills (e.g., Python, JavaScript, AWS)",
            validation_rules=[
                ValidationRule("required", message="Please add at least one skill")
            ]
        ),
        FormField(
            name="resume",
            type=FieldType.FILE_DRAG,
            label="Upload Resume",
            accepted_files=[".pdf", ".doc", ".docx"],
            max_file_size=5 * 1024 * 1024,  # 5MB
            help_text="PDF or Word format, max 5MB",
            validation_rules=[
                ValidationRule("required", message="Resume is required")
            ]
        ),
        FormField(
            name="portfolio_url",
            type=FieldType.URL,
            label="Portfolio/GitHub URL",
            placeholder="https://github.com/yourusername",
            help_text="Optional: Share your work samples"
        )
    ]
    
    # Step 3: Position Details
    position_fields = [
        FormField(
            name="position_applying",
            type=FieldType.SELECT,
            label="Position Applying For",
            placeholder="Select a position",
            options=[
                {"value": "frontend", "label": "Frontend Developer"},
                {"value": "backend", "label": "Backend Developer"},
                {"value": "fullstack", "label": "Full Stack Developer"},
                {"value": "devops", "label": "DevOps Engineer"},
                {"value": "data", "label": "Data Engineer"},
                {"value": "ml", "label": "Machine Learning Engineer"},
                {"value": "other", "label": "Other"}
            ],
            validation_rules=[
                ValidationRule("required", message="Please select a position")
            ]
        ),
        FormField(
            name="other_position",
            type=FieldType.TEXT,
            label="Specify Position",
            placeholder="Enter the position title",
            show_if={"position_applying": "other"},
            validation_rules=[
                ValidationRule("required", message="Please specify the position")
            ]
        ),
        FormField(
            name="employment_type",
            type=FieldType.CHECKBOX,
            label="Employment Type Preference",
            options=[
                {"value": "full_time", "label": "Full-time"},
                {"value": "part_time", "label": "Part-time"},
                {"value": "contract", "label": "Contract"},
                {"value": "remote", "label": "Remote"}
            ],
            help_text="Select all that apply"
        ),
        FormField(
            name="expected_salary",
            type=FieldType.RANGE,
            label="Expected Salary Range (USD)",
            attributes={
                "min": "50000",
                "max": "250000",
                "step": "10000"
            },
            help_text="Drag to set your expected salary range"
        ),
        FormField(
            name="start_date",
            type=FieldType.DATE,
            label="Earliest Start Date",
            validation_rules=[
                ValidationRule("required", message="Start date is required"),
                ValidationRule("min", date.today().isoformat(), "Start date must be in the future")
            ]
        ),
        FormField(
            name="cover_letter",
            type=FieldType.RICH_TEXT,
            label="Cover Letter",
            help_text="Tell us why you're interested in this position",
            enable_rich_text=True,
            validation_rules=[
                ValidationRule("required", message="Cover letter is required")
            ]
        )
    ]
    
    # Create the wizard
    wizard = FormWizard(
        title="Job Application",
        steps=[
            FormStep(
                title="Personal Information",
                description="Let's start with your contact details",
                fields=personal_fields
            ),
            FormStep(
                title="Experience & Skills",
                description="Tell us about your professional background",
                fields=experience_fields
            ),
            FormStep(
                title="Position Details",
                description="What role are you interested in?",
                fields=position_fields
            )
        ],
        submit_url="/api/job-application",
        theme=FormTheme.MODERN,
        enable_analytics=True,
        enable_autosave=True
    )
    
    return wizard


# Example 2: Customer Satisfaction Survey
def create_customer_survey():
    """
    Dynamic survey with conditional questions based on responses
    """
    
    # Step 1: General Information
    general_fields = [
        FormField(
            name="customer_type",
            type=FieldType.RADIO,
            label="How long have you been our customer?",
            options=[
                {"value": "new", "label": "Less than 6 months"},
                {"value": "regular", "label": "6 months - 2 years"},
                {"value": "loyal", "label": "More than 2 years"}
            ],
            validation_rules=[
                ValidationRule("required")
            ]
        ),
        FormField(
            name="product_category",
            type=FieldType.SELECT,
            label="Which product category do you use most?",
            options=[
                {"value": "software", "label": "Software Solutions"},
                {"value": "hardware", "label": "Hardware Products"},
                {"value": "services", "label": "Professional Services"},
                {"value": "support", "label": "Support & Maintenance"}
            ],
            validation_rules=[
                ValidationRule("required")
            ]
        ),
        FormField(
            name="usage_frequency",
            type=FieldType.RADIO,
            label="How often do you use our products/services?",
            options=[
                {"value": "daily", "label": "Daily"},
                {"value": "weekly", "label": "Weekly"},
                {"value": "monthly", "label": "Monthly"},
                {"value": "rarely", "label": "Rarely"}
            ],
            validation_rules=[
                ValidationRule("required")
            ]
        )
    ]
    
    # Step 2: Satisfaction Ratings
    rating_fields = [
        FormField(
            name="overall_satisfaction",
            type=FieldType.RATING,
            label="Overall Satisfaction",
            attributes={"max": "5"},
            help_text="Rate from 1 (Very Dissatisfied) to 5 (Very Satisfied)",
            validation_rules=[
                ValidationRule("required")
            ]
        ),
        FormField(
            name="product_quality",
            type=FieldType.RATING,
            label="Product Quality",
            attributes={"max": "5"},
            validation_rules=[
                ValidationRule("required")
            ]
        ),
        FormField(
            name="customer_support",
            type=FieldType.RATING,
            label="Customer Support",
            attributes={"max": "5"},
            validation_rules=[
                ValidationRule("required")
            ]
        ),
        FormField(
            name="value_for_money",
            type=FieldType.RATING,
            label="Value for Money",
            attributes={"max": "5"},
            validation_rules=[
                ValidationRule("required")
            ]
        ),
        FormField(
            name="recommend_likelihood",
            type=FieldType.RANGE,
            label="How likely are you to recommend us? (0-10)",
            attributes={
                "min": "0",
                "max": "10",
                "step": "1"
            },
            help_text="0 = Not at all likely, 10 = Extremely likely",
            validation_rules=[
                ValidationRule("required")
            ]
        )
    ]
    
    # Step 3: Detailed Feedback
    feedback_fields = [
        FormField(
            name="improvement_areas",
            type=FieldType.CHECKBOX,
            label="Which areas need improvement?",
            options=[
                {"value": "quality", "label": "Product Quality"},
                {"value": "features", "label": "Product Features"},
                {"value": "pricing", "label": "Pricing"},
                {"value": "support", "label": "Customer Support"},
                {"value": "documentation", "label": "Documentation"},
                {"value": "delivery", "label": "Delivery/Installation"}
            ],
            help_text="Select all that apply"
        ),
        FormField(
            name="specific_issue",
            type=FieldType.TEXTAREA,
            label="Did you face any specific issues?",
            placeholder="Please describe any problems you encountered...",
            show_if={"overall_satisfaction": {"operator": "less_than", "value": "4"}},
            attributes={"rows": "4"}
        ),
        FormField(
            name="positive_feedback",
            type=FieldType.TEXTAREA,
            label="What do you like most about our products/services?",
            placeholder="Share what you appreciate...",
            show_if={"overall_satisfaction": {"operator": "greater_than", "value": "3"}},
            attributes={"rows": "4"}
        ),
        FormField(
            name="additional_comments",
            type=FieldType.RICH_TEXT,
            label="Additional Comments",
            help_text="Any other feedback you'd like to share?",
            enable_rich_text=True
        ),
        FormField(
            name="contact_me",
            type=FieldType.CHECKBOX,
            label="May we contact you regarding your feedback?",
            default_value=False
        ),
        FormField(
            name="contact_email",
            type=FieldType.EMAIL,
            label="Contact Email",
            placeholder="your@email.com",
            show_if={"contact_me": True},
            validation_rules=[
                ValidationRule("required", message="Email is required if you want to be contacted")
            ]
        )
    ]
    
    # Create dynamic field generator for step 2
    def generate_specific_questions(form_data):
        """Generate product-specific questions based on selection"""
        fields = []
        
        if form_data.get("product_category") == "software":
            fields.extend([
                FormField(
                    name="software_performance",
                    type=FieldType.RATING,
                    label="Software Performance",
                    attributes={"max": "5"},
                    validation_rules=[ValidationRule("required")]
                ),
                FormField(
                    name="ui_experience",
                    type=FieldType.RATING,
                    label="User Interface Experience",
                    attributes={"max": "5"},
                    validation_rules=[ValidationRule("required")]
                )
            ])
        elif form_data.get("product_category") == "hardware":
            fields.extend([
                FormField(
                    name="build_quality",
                    type=FieldType.RATING,
                    label="Build Quality",
                    attributes={"max": "5"},
                    validation_rules=[ValidationRule("required")]
                ),
                FormField(
                    name="durability",
                    type=FieldType.RATING,
                    label="Durability",
                    attributes={"max": "5"},
                    validation_rules=[ValidationRule("required")]
                )
            ])
        
        return fields
    
    # Create the wizard
    wizard = FormWizard(
        title="Customer Satisfaction Survey",
        steps=[
            FormStep(
                title="About You",
                description="Help us understand your experience better",
                fields=general_fields
            ),
            FormStep(
                title="Rate Our Service",
                description="How satisfied are you with different aspects?",
                fields=rating_fields,
                dynamic_fields_generator=generate_specific_questions
            ),
            FormStep(
                title="Your Feedback",
                description="Share your thoughts and suggestions",
                fields=feedback_fields
            )
        ],
        submit_url="/api/survey",
        theme=FormTheme.DEFAULT
    )
    
    return wizard


# Example 3: Event Registration Form
def create_event_registration():
    """
    Conference/Event registration with payment and dietary preferences
    """
    
    # Step 1: Attendee Information
    attendee_fields = [
        FormField(
            name="first_name",
            type=FieldType.TEXT,
            label="First Name",
            validation_rules=[ValidationRule("required")],
            real_time_validate=True
        ),
        FormField(
            name="last_name",
            type=FieldType.TEXT,
            label="Last Name",
            validation_rules=[ValidationRule("required")],
            real_time_validate=True
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email Address",
            validation_rules=[ValidationRule("required")],
            real_time_validate=True
        ),
        FormField(
            name="phone",
            type=FieldType.TEL,
            label="Phone Number",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="organization",
            type=FieldType.TEXT,
            label="Organization/Company",
            placeholder="Your company name"
        ),
        FormField(
            name="job_title",
            type=FieldType.TEXT,
            label="Job Title",
            placeholder="Your position"
        ),
        FormField(
            name="badge_name",
            type=FieldType.TEXT,
            label="Name for Badge",
            placeholder="How should your name appear on the badge?",
            help_text="Leave blank to use your full name"
        )
    ]
    
    # Step 2: Registration Options
    registration_fields = [
        FormField(
            name="ticket_type",
            type=FieldType.RADIO,
            label="Registration Type",
            options=[
                {"value": "early_bird", "label": "Early Bird - $299 (until Dec 31)"},
                {"value": "regular", "label": "Regular - $399"},
                {"value": "vip", "label": "VIP All-Access - $599"},
                {"value": "student", "label": "Student - $99 (ID required)"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="student_id",
            type=FieldType.FILE_DRAG,
            label="Upload Student ID",
            accepted_files=[".jpg", ".jpeg", ".png", ".pdf"],
            max_file_size=2 * 1024 * 1024,
            show_if={"ticket_type": "student"},
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="workshop_sessions",
            type=FieldType.CHECKBOX,
            label="Workshop Sessions (Select all you plan to attend)",
            options=[
                {"value": "ai_basics", "label": "Introduction to AI - Morning"},
                {"value": "ml_advanced", "label": "Advanced Machine Learning - Morning"},
                {"value": "nlp_workshop", "label": "NLP Hands-on Workshop - Afternoon"},
                {"value": "cv_tutorial", "label": "Computer Vision Tutorial - Afternoon"},
                {"value": "ethics_panel", "label": "AI Ethics Panel Discussion - Evening"}
            ],
            help_text="Included with VIP ticket, $50 each for other tickets"
        ),
        FormField(
            name="needs_accommodation",
            type=FieldType.CHECKBOX,
            label="Do you require any special accommodations?",
            default_value=False
        ),
        FormField(
            name="accommodation_details",
            type=FieldType.TEXTAREA,
            label="Please describe your accommodation needs",
            show_if={"needs_accommodation": True},
            attributes={"rows": "3"}
        )
    ]
    
    # Step 3: Additional Information
    additional_fields = [
        FormField(
            name="dietary_restrictions",
            type=FieldType.CHECKBOX,
            label="Dietary Restrictions",
            options=[
                {"value": "vegetarian", "label": "Vegetarian"},
                {"value": "vegan", "label": "Vegan"},
                {"value": "gluten_free", "label": "Gluten-Free"},
                {"value": "halal", "label": "Halal"},
                {"value": "kosher", "label": "Kosher"},
                {"value": "other", "label": "Other"}
            ],
            help_text="Select all that apply"
        ),
        FormField(
            name="dietary_other",
            type=FieldType.TEXT,
            label="Please specify other dietary restrictions",
            show_if={"dietary_restrictions": {"operator": "contains", "value": "other"}}
        ),
        FormField(
            name="t_shirt_size",
            type=FieldType.SELECT,
            label="T-Shirt Size",
            options=[
                {"value": "xs", "label": "XS"},
                {"value": "s", "label": "S"},
                {"value": "m", "label": "M"},
                {"value": "l", "label": "L"},
                {"value": "xl", "label": "XL"},
                {"value": "xxl", "label": "XXL"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="how_heard",
            type=FieldType.SELECT,
            label="How did you hear about this event?",
            options=[
                {"value": "email", "label": "Email"},
                {"value": "social", "label": "Social Media"},
                {"value": "colleague", "label": "Colleague/Friend"},
                {"value": "website", "label": "Our Website"},
                {"value": "other", "label": "Other"}
            ]
        ),
        FormField(
            name="newsletter",
            type=FieldType.CHECKBOX,
            label="Subscribe to our newsletter for future events",
            default_value=True
        ),
        FormField(
            name="photo_consent",
            type=FieldType.CHECKBOX,
            label="I consent to being photographed/filmed during the event",
            default_value=True
        )
    ]
    
    # Create the wizard
    wizard = FormWizard(
        title="Tech Conference 2024 Registration",
        steps=[
            FormStep(
                title="Attendee Information",
                description="Tell us about yourself",
                fields=attendee_fields
            ),
            FormStep(
                title="Registration Options",
                description="Choose your ticket and sessions",
                fields=registration_fields
            ),
            FormStep(
                title="Additional Information",
                description="Help us make your experience better",
                fields=additional_fields
            )
        ],
        submit_url="/api/event-registration",
        theme=FormTheme.MODERN,
        enable_autosave=True
    )
    
    return wizard


# Example 4: Medical Patient Intake Form
def create_patient_intake_form():
    """
    Medical form with privacy considerations and conditional health questions
    """
    
    # Step 1: Patient Information
    patient_fields = [
        FormField(
            name="patient_id",
            type=FieldType.TEXT,
            label="Patient ID (if returning patient)",
            placeholder="Leave blank if new patient"
        ),
        FormField(
            name="first_name",
            type=FieldType.TEXT,
            label="First Name",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="last_name",
            type=FieldType.TEXT,
            label="Last Name",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="date_of_birth",
            type=FieldType.DATE,
            label="Date of Birth",
            validation_rules=[
                ValidationRule("required"),
                ValidationRule("max", date.today().isoformat())
            ]
        ),
        FormField(
            name="gender",
            type=FieldType.SELECT,
            label="Gender",
            options=[
                {"value": "male", "label": "Male"},
                {"value": "female", "label": "Female"},
                {"value": "other", "label": "Other"},
                {"value": "prefer_not_say", "label": "Prefer not to say"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="ssn_last_four",
            type=FieldType.TEXT,
            label="Last 4 digits of SSN",
            attributes={"maxlength": "4", "pattern": "[0-9]{4}"},
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="primary_phone",
            type=FieldType.TEL,
            label="Primary Phone",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email Address",
            help_text="For appointment reminders and secure communications"
        ),
        FormField(
            name="emergency_contact",
            type=FieldType.TEXT,
            label="Emergency Contact Name",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="emergency_phone",
            type=FieldType.TEL,
            label="Emergency Contact Phone",
            validation_rules=[ValidationRule("required")]
        )
    ]
    
    # Step 2: Medical History
    medical_fields = [
        FormField(
            name="visit_reason",
            type=FieldType.TEXTAREA,
            label="Reason for Visit",
            placeholder="Please describe your symptoms or reason for visit",
            validation_rules=[ValidationRule("required")],
            attributes={"rows": "3"}
        ),
        FormField(
            name="current_medications",
            type=FieldType.TAGS,
            label="Current Medications",
            placeholder="Type medication name and press Enter",
            help_text="Include dosage if known"
        ),
        FormField(
            name="allergies",
            type=FieldType.TAGS,
            label="Allergies (medications, foods, etc.)",
            placeholder="Type allergy and press Enter"
        ),
        FormField(
            name="chronic_conditions",
            type=FieldType.CHECKBOX,
            label="Do you have any of these conditions?",
            options=[
                {"value": "diabetes", "label": "Diabetes"},
                {"value": "hypertension", "label": "High Blood Pressure"},
                {"value": "heart_disease", "label": "Heart Disease"},
                {"value": "asthma", "label": "Asthma"},
                {"value": "arthritis", "label": "Arthritis"},
                {"value": "cancer", "label": "Cancer"},
                {"value": "mental_health", "label": "Mental Health Condition"},
                {"value": "other", "label": "Other"}
            ]
        ),
        FormField(
            name="other_conditions",
            type=FieldType.TEXTAREA,
            label="Please specify other conditions",
            show_if={"chronic_conditions": {"operator": "contains", "value": "other"}},
            attributes={"rows": "2"}
        ),
        FormField(
            name="surgeries",
            type=FieldType.TEXTAREA,
            label="Previous Surgeries (with approximate dates)",
            placeholder="e.g., Appendectomy - 2019",
            attributes={"rows": "3"}
        ),
        FormField(
            name="family_history",
            type=FieldType.CHECKBOX,
            label="Family History of:",
            options=[
                {"value": "heart_disease", "label": "Heart Disease"},
                {"value": "cancer", "label": "Cancer"},
                {"value": "diabetes", "label": "Diabetes"},
                {"value": "mental_illness", "label": "Mental Illness"},
                {"value": "stroke", "label": "Stroke"}
            ]
        )
    ]
    
    # Step 3: Lifestyle & Insurance
    lifestyle_fields = [
        FormField(
            name="smoking",
            type=FieldType.RADIO,
            label="Do you smoke?",
            options=[
                {"value": "never", "label": "Never"},
                {"value": "former", "label": "Former smoker"},
                {"value": "current", "label": "Current smoker"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="alcohol",
            type=FieldType.RADIO,
            label="Alcohol consumption",
            options=[
                {"value": "none", "label": "None"},
                {"value": "occasional", "label": "Occasional (1-2 drinks/week)"},
                {"value": "moderate", "label": "Moderate (3-7 drinks/week)"},
                {"value": "heavy", "label": "Heavy (>7 drinks/week)"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="exercise",
            type=FieldType.RADIO,
            label="Exercise frequency",
            options=[
                {"value": "none", "label": "No regular exercise"},
                {"value": "light", "label": "1-2 times/week"},
                {"value": "moderate", "label": "3-4 times/week"},
                {"value": "active", "label": "5+ times/week"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="insurance_provider",
            type=FieldType.TEXT,
            label="Insurance Provider",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="insurance_id",
            type=FieldType.TEXT,
            label="Insurance ID Number",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="insurance_group",
            type=FieldType.TEXT,
            label="Group Number"
        ),
        FormField(
            name="pharmacy_preference",
            type=FieldType.TEXT,
            label="Preferred Pharmacy",
            placeholder="Name and location"
        ),
        FormField(
            name="consent",
            type=FieldType.CHECKBOX,
            label="I consent to treatment and acknowledge the privacy policy",
            validation_rules=[ValidationRule("required", message="Consent is required")]
        )
    ]
    
    # Create the wizard
    wizard = FormWizard(
        title="Patient Intake Form",
        steps=[
            FormStep(
                title="Patient Information",
                description="Please provide your personal information",
                fields=patient_fields
            ),
            FormStep(
                title="Medical History",
                description="Help us understand your health background",
                fields=medical_fields
            ),
            FormStep(
                title="Lifestyle & Insurance",
                description="Additional information for your care",
                fields=lifestyle_fields
            )
        ],
        submit_url="/api/patient-intake",
        theme=FormTheme.DEFAULT,
        enable_autosave=True,
        # Add custom privacy notice
        custom_css="""
        .form-wizard-container::before {
            content: "🔒 Your information is protected by HIPAA and our privacy policy";
            display: block;
            background: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            color: #1976d2;
        }
        """
    )
    
    return wizard


# Example 5: Product Feedback Form
def create_product_feedback_form():
    """
    Product review form with ratings, image upload, and rich text
    """
    
    fields = [
        FormField(
            name="product_name",
            type=FieldType.AUTOCOMPLETE,
            label="Product Name",
            placeholder="Start typing to search...",
            autocomplete_source=[
                "iPhone 15 Pro",
                "Samsung Galaxy S24",
                "MacBook Pro M3",
                "Dell XPS 15",
                "Sony WH-1000XM5",
                "iPad Pro 12.9",
                "Google Pixel 8",
                "Microsoft Surface Pro"
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="purchase_date",
            type=FieldType.DATE,
            label="Purchase Date",
            validation_rules=[
                ValidationRule("required"),
                ValidationRule("max", date.today().isoformat())
            ]
        ),
        FormField(
            name="overall_rating",
            type=FieldType.RATING,
            label="Overall Rating",
            attributes={"max": "5"},
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="title",
            type=FieldType.TEXT,
            label="Review Title",
            placeholder="Summarize your experience",
            validation_rules=[
                ValidationRule("required"),
                ValidationRule("maxlength", 100)
            ]
        ),
        FormField(
            name="pros",
            type=FieldType.TAGS,
            label="Pros",
            placeholder="Add positive aspects",
            help_text="What did you like? Press Enter after each item"
        ),
        FormField(
            name="cons",
            type=FieldType.TAGS,
            label="Cons",
            placeholder="Add negative aspects",
            help_text="What could be improved? Press Enter after each item"
        ),
        FormField(
            name="detailed_review",
            type=FieldType.RICH_TEXT,
            label="Detailed Review",
            help_text="Share your full experience with this product",
            enable_rich_text=True,
            validation_rules=[
                ValidationRule("required"),
                ValidationRule("minlength", 50, "Please write at least 50 characters")
            ]
        ),
        FormField(
            name="product_images",
            type=FieldType.FILE_DRAG,
            label="Product Photos (Optional)",
            accepted_files=[".jpg", ".jpeg", ".png", ".webp"],
            max_file_size=10 * 1024 * 1024,  # 10MB
            help_text="Share photos of the product in use"
        ),
        FormField(
            name="recommend",
            type=FieldType.RADIO,
            label="Would you recommend this product?",
            options=[
                {"value": "yes", "label": "Yes, definitely"},
                {"value": "maybe", "label": "Yes, with reservations"},
                {"value": "no", "label": "No"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="verified_purchase",
            type=FieldType.CHECKBOX,
            label="I purchased this product and this is my honest review",
            validation_rules=[ValidationRule("required", message="Please confirm this is your honest review")]
        ),
        FormField(
            name="reviewer_name",
            type=FieldType.TEXT,
            label="Your Name (as it should appear)",
            placeholder="John D. or Anonymous",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email (not displayed publicly)",
            help_text="For verification purposes only",
            validation_rules=[ValidationRule("required")]
        )
    ]
    
    wizard = FormWizard(
        title="Product Review",
        steps=[
            FormStep(
                title="Share Your Experience",
                description="Help others make informed decisions",
                fields=fields
            )
        ],
        submit_url="/api/product-review",
        theme=FormTheme.MODERN
    )
    
    return wizard


# Example 6: Online Course Enrollment (using Pydantic)
if PYDANTIC_AVAILABLE:
    class StudentLevel(str, Enum):
        BEGINNER = "beginner"
        INTERMEDIATE = "intermediate"
        ADVANCED = "advanced"
    
    class CourseCategory(str, Enum):
        PROGRAMMING = "programming"
        DATA_SCIENCE = "data_science"
        WEB_DEV = "web_development"
        MOBILE = "mobile_development"
        DEVOPS = "devops"
        AI_ML = "ai_machine_learning"
    
    class CourseEnrollment(BaseModel):
        # Student Information
        full_name: str = Field(..., min_length=2, description="Your full name")
        email: str = Field(..., description="Email for course access")
        phone: Optional[str] = Field(None, description="Contact number")
        
        # Course Selection
        course_category: CourseCategory = Field(..., description="Select course category")
        experience_level: StudentLevel = Field(..., description="Your current level")
        
        # Background
        current_role: str = Field(..., description="Your current job/role")
        years_experience: int = Field(0, ge=0, le=50, description="Years in tech")
        primary_goal: str = Field(..., max_length=200, description="What do you hope to achieve?")
        
        # Learning Preferences
        preferred_schedule: List[str] = Field(..., description="Preferred class times")
        time_commitment: int = Field(..., ge=5, le=40, description="Hours per week you can dedicate")
        
        # Technical Setup
        has_computer: bool = Field(..., description="Do you have a computer?")
        operating_system: Optional[str] = Field(None, description="Your OS")
        
        # Payment
        payment_plan: str = Field(..., description="Payment option")
        promo_code: Optional[str] = Field(None, description="Discount code if any")
        
        # Agreement
        terms_accepted: bool = Field(..., description="I accept the terms and conditions")
        refund_policy_acknowledged: bool = Field(..., description="I understand the refund policy")
    
    def create_course_enrollment_form():
        """Create course enrollment form from Pydantic model"""
        
        # Custom labels for better UX
        custom_labels = {
            "full_name": "Full Name",
            "email": "Email Address",
            "course_category": "Course Category",
            "experience_level": "Experience Level",
            "current_role": "Current Job/Role",
            "years_experience": "Years of Experience",
            "primary_goal": "Primary Learning Goal",
            "preferred_schedule": "Preferred Schedule",
            "time_commitment": "Weekly Time Commitment (hours)",
            "has_computer": "I have access to a computer",
            "operating_system": "Operating System",
            "payment_plan": "Payment Plan",
            "promo_code": "Promo Code",
            "terms_accepted": "I accept the terms and conditions",
            "refund_policy_acknowledged": "I understand the refund policy"
        }
        
        # Custom help text
        custom_help = {
            "primary_goal": "What specific skills or outcomes are you looking for?",
            "time_commitment": "Be realistic about your availability",
            "promo_code": "Enter if you have a discount code"
        }
        
        # Create wizard from Pydantic model
        wizard = PydanticFormConverter.create_wizard_from_models(
            [CourseEnrollment],
            title="Online Course Enrollment",
            submit_url="/api/course-enrollment",
            step_titles=["Course Registration"],
            step_descriptions=["Join our learning community"],
            theme=FormTheme.MODERN,
            custom_labels=custom_labels,
            custom_help_text=custom_help,
            enable_analytics=True,
            enable_autosave=True
        )
        
        # Add custom field modifications after generation
        for step in wizard.steps:
            for field in step.fields:
                # Make schedule field checkboxes
                if field.name == "preferred_schedule":
                    field.type = FieldType.CHECKBOX
                    field.options = [
                        {"value": "morning", "label": "Morning (9 AM - 12 PM)"},
                        {"value": "afternoon", "label": "Afternoon (1 PM - 5 PM)"},
                        {"value": "evening", "label": "Evening (6 PM - 9 PM)"},
                        {"value": "weekend", "label": "Weekends"}
                    ]
                
                # Make payment plan radio buttons
                elif field.name == "payment_plan":
                    field.type = FieldType.RADIO
                    field.options = [
                        {"value": "full", "label": "Full Payment - $999 (Save $200)"},
                        {"value": "installments", "label": "3 Monthly Installments - $399/month"},
                        {"value": "subscription", "label": "Monthly Subscription - $149/month"}
                    ]
                
                # Make OS a select field
                elif field.name == "operating_system":
                    field.type = FieldType.SELECT
                    field.options = [
                        {"value": "windows", "label": "Windows"},
                        {"value": "macos", "label": "macOS"},
                        {"value": "linux", "label": "Linux"},
                        {"value": "other", "label": "Other"}
                    ]
                    field.show_if = {"has_computer": True}
        
        return wizard


# Example 7: Real Estate Inquiry Form
def create_real_estate_inquiry():
    """
    Property inquiry form with dynamic fields based on property type
    """
    
    # Step 1: Contact Information
    contact_fields = [
        FormField(
            name="full_name",
            type=FieldType.TEXT,
            label="Full Name",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="phone",
            type=FieldType.TEL,
            label="Phone",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="preferred_contact",
            type=FieldType.RADIO,
            label="Preferred Contact Method",
            options=[
                {"value": "email", "label": "Email"},
                {"value": "phone", "label": "Phone"},
                {"value": "text", "label": "Text Message"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="best_time",
            type=FieldType.SELECT,
            label="Best Time to Contact",
            options=[
                {"value": "morning", "label": "Morning (9 AM - 12 PM)"},
                {"value": "afternoon", "label": "Afternoon (12 PM - 5 PM)"},
                {"value": "evening", "label": "Evening (5 PM - 8 PM)"}
            ]
        )
    ]
    
    # Step 2: Property Preferences
    def generate_property_fields(form_data):
        """Generate fields based on property interest type"""
        base_fields = [
            FormField(
                name="interest_type",
                type=FieldType.RADIO,
                label="Are you looking to:",
                options=[
                    {"value": "buy", "label": "Buy"},
                    {"value": "rent", "label": "Rent"},
                    {"value": "sell", "label": "Sell"}
                ],
                validation_rules=[ValidationRule("required")]
            ),
            FormField(
                name="property_type",
                type=FieldType.SELECT,
                label="Property Type",
                options=[
                    {"value": "house", "label": "Single Family House"},
                    {"value": "condo", "label": "Condo/Townhouse"},
                    {"value": "apartment", "label": "Apartment"},
                    {"value": "land", "label": "Land/Lot"},
                    {"value": "commercial", "label": "Commercial"}
                ],
                validation_rules=[ValidationRule("required")]
            )
        ]
        
        # Add fields based on interest type
        if form_data.get("interest_type") in ["buy", "rent"]:
            base_fields.extend([
                FormField(
                    name="location_preference",
                    type=FieldType.TAGS,
                    label="Preferred Areas/Neighborhoods",
                    placeholder="Add neighborhood names",
                    help_text="Type and press Enter to add multiple areas"
                ),
                FormField(
                    name="bedrooms",
                    type=FieldType.SELECT,
                    label="Bedrooms",
                    options=[
                        {"value": "studio", "label": "Studio"},
                        {"value": "1", "label": "1"},
                        {"value": "2", "label": "2"},
                        {"value": "3", "label": "3"},
                        {"value": "4", "label": "4"},
                        {"value": "5+", "label": "5+"}
                    ],
                    validation_rules=[ValidationRule("required")]
                ),
                FormField(
                    name="bathrooms",
                    type=FieldType.SELECT,
                    label="Bathrooms",
                    options=[
                        {"value": "1", "label": "1"},
                        {"value": "1.5", "label": "1.5"},
                        {"value": "2", "label": "2"},
                        {"value": "2.5", "label": "2.5"},
                        {"value": "3+", "label": "3+"}
                    ],
                    validation_rules=[ValidationRule("required")]
                ),
                FormField(
                    name="price_range",
                    type=FieldType.TEXT,
                    label="Budget Range",
                    placeholder="e.g., $200,000 - $300,000",
                    validation_rules=[ValidationRule("required")]
                ),
                FormField(
                    name="move_timeline",
                    type=FieldType.SELECT,
                    label="When do you need to move?",
                    options=[
                        {"value": "asap", "label": "ASAP"},
                        {"value": "1month", "label": "Within 1 month"},
                        {"value": "3months", "label": "Within 3 months"},
                        {"value": "6months", "label": "Within 6 months"},
                        {"value": "flexible", "label": "Flexible"}
                    ],
                    validation_rules=[ValidationRule("required")]
                )
            ])
        
        elif form_data.get("interest_type") == "sell":
            base_fields.extend([
                FormField(
                    name="property_address",
                    type=FieldType.TEXT,
                    label="Property Address",
                    validation_rules=[ValidationRule("required")]
                ),
                FormField(
                    name="property_condition",
                    type=FieldType.RADIO,
                    label="Property Condition",
                    options=[
                        {"value": "excellent", "label": "Excellent"},
                        {"value": "good", "label": "Good"},
                        {"value": "fair", "label": "Fair"},
                        {"value": "needs_work", "label": "Needs Work"}
                    ],
                    validation_rules=[ValidationRule("required")]
                ),
                FormField(
                    name="reason_selling",
                    type=FieldType.SELECT,
                    label="Reason for Selling",
                    options=[
                        {"value": "upgrading", "label": "Upgrading"},
                        {"value": "downsizing", "label": "Downsizing"},
                        {"value": "relocating", "label": "Relocating"},
                        {"value": "financial", "label": "Financial Reasons"},
                        {"value": "other", "label": "Other"}
                    ]
                ),
                FormField(
                    name="asking_price",
                    type=FieldType.TEXT,
                    label="Desired Selling Price",
                    placeholder="e.g., $350,000"
                )
            ])
        
        return base_fields
    
    # Step 3: Additional Information
    additional_fields = [
        FormField(
            name="pre_approved",
            type=FieldType.RADIO,
            label="Are you pre-approved for a mortgage?",
            options=[
                {"value": "yes", "label": "Yes"},
                {"value": "no", "label": "No"},
                {"value": "na", "label": "Not applicable"}
            ],
            show_if={"interest_type": "buy"}
        ),
        FormField(
            name="amenities",
            type=FieldType.CHECKBOX,
            label="Important Amenities",
            options=[
                {"value": "garage", "label": "Garage/Parking"},
                {"value": "yard", "label": "Yard/Outdoor Space"},
                {"value": "pool", "label": "Pool"},
                {"value": "gym", "label": "Gym/Fitness Center"},
                {"value": "pets", "label": "Pet Friendly"},
                {"value": "storage", "label": "Storage Space"},
                {"value": "laundry", "label": "In-unit Laundry"}
            ],
            show_if={"interest_type": {"operator": "in", "value": ["buy", "rent"]}}
        ),
        FormField(
            name="additional_notes",
            type=FieldType.RICH_TEXT,
            label="Additional Requirements or Questions",
            help_text="Tell us more about what you're looking for",
            enable_rich_text=True
        ),
        FormField(
            name="property_photos",
            type=FieldType.FILE_DRAG,
            label="Property Photos",
            accepted_files=[".jpg", ".jpeg", ".png"],
            max_file_size=5 * 1024 * 1024,
            help_text="Upload photos of your property",
            show_if={"interest_type": "sell"}
        ),
        FormField(
            name="newsletter",
            type=FieldType.CHECKBOX,
            label="Send me new listings that match my criteria",
            default_value=True
        )
    ]
    
    # Create the wizard
    wizard = FormWizard(
        title="Real Estate Inquiry",
        steps=[
            FormStep(
                title="Contact Information",
                description="How can we reach you?",
                fields=contact_fields
            ),
            FormStep(
                title="Property Preferences",
                description="Tell us what you're looking for",
                fields=[],  # Will be populated dynamically
                dynamic_fields_generator=generate_property_fields
            ),
            FormStep(
                title="Additional Information",
                description="Any other details we should know?",
                fields=additional_fields
            )
        ],
        submit_url="/api/real-estate-inquiry",
        theme=FormTheme.MODERN,
        enable_autosave=True
    )
    
    return wizard


# Example 8: Restaurant Reservation
def create_restaurant_reservation():
    """
    Restaurant booking form with date/time selection and special requests
    """
    
    # Calculate available dates (next 30 days)
    today = date.today()
    max_date = today + timedelta(days=30)
    
    fields = [
        FormField(
            name="reservation_date",
            type=FieldType.DATE,
            label="Reservation Date",
            validation_rules=[
                ValidationRule("required"),
                ValidationRule("min", today.isoformat(), "Please select a future date"),
                ValidationRule("max", max_date.isoformat(), "Reservations only available for next 30 days")
            ]
        ),
        FormField(
            name="reservation_time",
            type=FieldType.SELECT,
            label="Preferred Time",
            options=[
                {"value": "17:00", "label": "5:00 PM"},
                {"value": "17:30", "label": "5:30 PM"},
                {"value": "18:00", "label": "6:00 PM"},
                {"value": "18:30", "label": "6:30 PM"},
                {"value": "19:00", "label": "7:00 PM"},
                {"value": "19:30", "label": "7:30 PM"},
                {"value": "20:00", "label": "8:00 PM"},
                {"value": "20:30", "label": "8:30 PM"},
                {"value": "21:00", "label": "9:00 PM"}
            ],
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="party_size",
            type=FieldType.NUMBER,
            label="Number of Guests",
            validation_rules=[
                ValidationRule("required"),
                ValidationRule("min", 1, "Minimum 1 guest"),
                ValidationRule("max", 12, "For parties larger than 12, please call us")
            ],
            attributes={"min": "1", "max": "12"}
        ),
        FormField(
            name="seating_preference",
            type=FieldType.RADIO,
            label="Seating Preference",
            options=[
                {"value": "any", "label": "No preference"},
                {"value": "indoor", "label": "Indoor"},
                {"value": "outdoor", "label": "Outdoor/Patio"},
                {"value": "bar", "label": "Bar seating"},
                {"value": "private", "label": "Private dining room"}
            ],
            default_value="any"
        ),
        FormField(
            name="occasion",
            type=FieldType.SELECT,
            label="Special Occasion?",
            options=[
                {"value": "none", "label": "Just dining out"},
                {"value": "birthday", "label": "Birthday"},
                {"value": "anniversary", "label": "Anniversary"},
                {"value": "business", "label": "Business dinner"},
                {"value": "date", "label": "Date night"},
                {"value": "other", "label": "Other celebration"}
            ],
            default_value="none"
        ),
        FormField(
            name="occasion_details",
            type=FieldType.TEXT,
            label="Tell us more about the occasion",
            placeholder="e.g., 50th birthday, 10th anniversary",
            show_if={"occasion": {"operator": "not_equals", "value": "none"}}
        ),
        FormField(
            name="dietary_restrictions",
            type=FieldType.CHECKBOX,
            label="Dietary Restrictions",
            options=[
                {"value": "vegetarian", "label": "Vegetarian"},
                {"value": "vegan", "label": "Vegan"},
                {"value": "gluten_free", "label": "Gluten-free"},
                {"value": "nut_allergy", "label": "Nut allergy"},
                {"value": "shellfish", "label": "Shellfish allergy"},
                {"value": "dairy_free", "label": "Dairy-free"},
                {"value": "other", "label": "Other"}
            ],
            help_text="Check all that apply to your party"
        ),
        FormField(
            name="dietary_notes",
            type=FieldType.TEXTAREA,
            label="Additional dietary notes",
            show_if={"dietary_restrictions": {"operator": "contains", "value": "other"}},
            attributes={"rows": "2"}
        ),
        FormField(
            name="special_requests",
            type=FieldType.TEXTAREA,
            label="Special Requests",
            placeholder="High chair needed, wheelchair accessible, etc.",
            attributes={"rows": "3"}
        ),
        FormField(
            name="guest_name",
            type=FieldType.TEXT,
            label="Name for Reservation",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="phone",
            type=FieldType.TEL,
            label="Phone Number",
            validation_rules=[ValidationRule("required")],
            help_text="We'll text you a confirmation"
        ),
        FormField(
            name="email",
            type=FieldType.EMAIL,
            label="Email Address",
            validation_rules=[ValidationRule("required")]
        ),
        FormField(
            name="marketing_consent",
            type=FieldType.CHECKBOX,
            label="Send me special offers and event invitations",
            default_value=True
        )
    ]
    
    wizard = FormWizard(
        title="Reserve Your Table",
        steps=[
            FormStep(
                title="Make a Reservation",
                description="Book your dining experience",
                fields=fields
            )
        ],
        submit_url="/api/restaurant-reservation",
        theme=FormTheme.DEFAULT,
        custom_css="""
        .form-wizard-container {
            background-image: linear-gradient(rgba(255,255,255,0.9), rgba(255,255,255,0.9)), 
                            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" font-size="50">🍽️</text></svg>');
            background-position: top right;
            background-repeat: no-repeat;
            background-size: 100px;
        }
        """
    )
    
    return wizard


# Main execution function
def generate_all_examples():
    """Generate all example forms"""
    
    examples = [
        ("job_application", create_job_application_form(), "Multi-step job application with file upload"),
        ("customer_survey", create_customer_survey(), "Dynamic survey with conditional questions"),
        ("event_registration", create_event_registration(), "Conference registration with sessions"),
        ("patient_intake", create_patient_intake_form(), "Medical form with privacy features"),
        ("product_feedback", create_product_feedback_form(), "Product review with rich text and ratings"),
        ("restaurant_reservation", create_restaurant_reservation(), "Restaurant booking with special requests"),
        ("real_estate_inquiry", create_real_estate_inquiry(), "Property inquiry with dynamic fields")
    ]
    
    if PYDANTIC_AVAILABLE:
        examples.append(
            ("course_enrollment", create_course_enrollment_form(), "Online course registration from Pydantic model")
        )
    
    print("🚀 Generating Real-Life Form Examples\n")
    print("=" * 60)
    
    for filename, wizard, description in examples:
        output_file = f"{filename}_form.html"
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(wizard.generate_html())
            
            print(f"✅ {output_file}")
            print(f"   {description}")
            print(f"   Theme: {wizard.theme.value}")
            print(f"   Steps: {len(wizard.steps)}")
            print(f"   Features: {'CSRF' if wizard.enable_csrf else ''} "
                  f"{'Analytics' if wizard.analytics.enabled else ''} "
                  f"{'Autosave' if wizard.enable_autosave else ''}")
            print()
        
        except Exception as e:
            print(f"❌ Error generating {filename}: {str(e)}")
            print()
    
    print("=" * 60)
    print("\n📄 Forms generated successfully!")
    print("\nTo test the forms:")
    print("1. Open any HTML file in your browser")
    print("2. Fill out the form fields")
    print("3. Watch the real-time validation")
    print("4. See conditional fields appear/disappear")
    print("5. Try the autosave feature (check localStorage)")
    print("\nFor production use, update the submit_url to your actual API endpoints.")


if __name__ == "__main__":
    generate_all_examples()