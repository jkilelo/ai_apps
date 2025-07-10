#!/usr/bin/env python3
"""
10-Step Employee Onboarding Form Chain
Demonstrates a comprehensive onboarding process with conditional routing,
field injection, and complex validation using Pydantic v2 and html_v3.py
"""

import sys
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum
import asyncio

sys.path.insert(0, '/var/www/ai_apps/playground')

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from html_v3 import FormChainEngine, FormStep, FormFieldSpec, FieldType
from pydantic import __version__ as pydantic_version

print(f"Using Pydantic version: {pydantic_version}")

# Enums for various options
class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"

class Department(str, Enum):
    ENGINEERING = "engineering"
    SALES = "sales"
    MARKETING = "marketing"
    HR = "hr"
    FINANCE = "finance"
    OPERATIONS = "operations"

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    PHD = "phd"
    OTHER = "other"

class TShirtSize(str, Enum):
    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"
    XXL = "xxl"

class WorkLocation(str, Enum):
    OFFICE = "office"
    REMOTE = "remote"
    HYBRID = "hybrid"

class BenefitPlan(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

class TrainingTrack(str, Enum):
    TECHNICAL = "technical"
    LEADERSHIP = "leadership"
    SALES = "sales"
    GENERAL = "general"

# Step 1: Basic Information
class BasicInfoRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')  # Changed from forbid to ignore
    
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    email: EmailStr = Field(..., description="Work email address")
    phone: str = Field(..., min_length=5, description="Phone number")  # Removed strict pattern
    date_of_birth: date = Field(..., description="Date of birth")
    
    @field_validator('date_of_birth')
    def validate_age(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 16:  # Reduced from 18 to 16 for testing
            raise ValueError('Employee must be at least 16 years old')
        if age > 100:
            raise ValueError('Invalid date of birth')
        return v

class BasicInfoResponse(BaseModel):
    employee_id: str
    full_name: str
    age: int
    email_verified: bool = False

# Step 2: Employment Details
class EmploymentDetailsRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')  # Changed from forbid to ignore
    
    employee_id: str = Field(..., description="Employee ID")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    department: Department = Field(..., description="Department")
    job_title: str = Field(..., min_length=3, max_length=100, description="Job title")
    start_date: date = Field(..., description="Start date")
    manager_email: EmailStr = Field(..., description="Manager's email")
    salary: Decimal = Field(..., gt=0, le=1000000, description="Annual salary")
    
    @field_validator('start_date')
    def validate_start_date(cls, v):
        if v < date.today():
            raise ValueError('Start date cannot be in the past')
        if v > date.today().replace(year=date.today().year + 1):
            raise ValueError('Start date must be within one year')
        return v

class EmploymentDetailsResponse(BaseModel):
    compensation_package_id: str
    requires_equipment: bool
    requires_visa: bool
    probation_period_days: int

# Step 3: Address Information
class AddressInfoRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: str
    street_address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")
    country: str = Field(..., min_length=2, max_length=100)
    work_location: WorkLocation = Field(..., description="Primary work location")
    
class AddressInfoResponse(BaseModel):
    address_id: str
    tax_jurisdiction: str
    commute_eligible: bool
    remote_setup_required: bool

# Step 4: Emergency Contact
class EmergencyContactRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: str
    contact_name: str = Field(..., min_length=2, max_length=100)
    relationship: str = Field(..., min_length=2, max_length=50)
    contact_phone: str = Field(..., pattern=r"^\+?1?\d{10,14}$")
    contact_email: Optional[EmailStr] = Field(None)
    alternate_phone: Optional[str] = Field(None, pattern=r"^\+?1?\d{10,14}$")
    
class EmergencyContactResponse(BaseModel):
    contact_id: str
    verified: bool

# Step 5: Education & Experience
class EducationExperienceRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: str
    highest_education: EducationLevel
    field_of_study: str = Field(..., min_length=2, max_length=100)
    university: str = Field(..., min_length=2, max_length=200)
    graduation_year: int = Field(..., ge=1950, le=date.today().year)
    years_of_experience: int = Field(..., ge=0, le=50)
    previous_companies: List[str] = Field(..., min_items=0, max_items=10)
    certifications: List[str] = Field(default_factory=list, max_items=20)
    skills: List[str] = Field(..., min_items=1, max_items=50)
    
class EducationExperienceResponse(BaseModel):
    profile_id: str
    skill_level: str
    training_recommendations: List[str]

# Step 6: Benefits Selection
class BenefitsSelectionRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: str
    health_plan: BenefitPlan
    dental_plan: BenefitPlan
    vision_plan: BenefitPlan
    retirement_401k_percentage: int = Field(..., ge=0, le=100)
    life_insurance_multiplier: int = Field(..., ge=0, le=10)
    dependent_count: int = Field(..., ge=0, le=20)
    fsa_contribution: Decimal = Field(default=Decimal('0'), ge=0, le=5000)
    
class BenefitsSelectionResponse(BaseModel):
    benefits_package_id: str
    total_cost: Decimal
    employee_contribution: Decimal
    effective_date: date

# Step 7: IT Equipment (Conditional - only if requires_equipment)
class ITEquipmentRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: str
    laptop_type: str = Field(..., description="Laptop preference")
    needs_monitor: bool = Field(default=True)
    monitor_count: int = Field(default=1, ge=0, le=3)
    needs_keyboard: bool = Field(default=True)
    needs_mouse: bool = Field(default=True)
    special_software: List[str] = Field(default_factory=list, max_items=20)
    additional_requests: Optional[str] = Field(None, max_length=500)
    
class ITEquipmentResponse(BaseModel):
    equipment_request_id: str
    estimated_ready_date: date
    total_cost: Decimal

# Step 8: Access & Security
class AccessSecurityRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: str
    needs_building_access: bool
    building_locations: List[str] = Field(default_factory=list, max_items=10)
    needs_parking: bool
    vehicle_license: Optional[str] = Field(None, max_length=20)
    security_clearance_required: bool
    background_check_consent: bool = Field(..., description="Must consent")
    systems_access: List[str] = Field(..., min_items=1, max_items=50)
    
    @field_validator('background_check_consent')
    def must_consent(cls, v):
        if not v:
            raise ValueError('Background check consent is required')
        return v
    
class AccessSecurityResponse(BaseModel):
    access_request_id: str
    badge_number: str
    security_training_required: bool

# Step 9: Training & Orientation
class TrainingOrientationRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: str
    preferred_training_track: TrainingTrack
    orientation_date: date = Field(..., description="Preferred orientation date")
    training_schedule_preference: str = Field(..., description="morning/afternoon/flexible")
    mentor_preference: Optional[str] = Field(None, max_length=100)
    accessibility_needs: Optional[str] = Field(None, max_length=500)
    dietary_restrictions: Optional[str] = Field(None, max_length=200)
    
    @field_validator('orientation_date')
    def validate_orientation_date(cls, v):
        if v < date.today():
            raise ValueError('Orientation date cannot be in the past')
        return v
    
class TrainingOrientationResponse(BaseModel):
    training_plan_id: str
    orientation_confirmed: bool
    mentor_assigned: str
    first_week_schedule: Dict[str, str]

# Step 10: Final Review & Welcome Kit
class FinalReviewRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: str
    tshirt_size: TShirtSize
    welcome_kit_address: str = Field(..., description="same/different")
    alternate_address: Optional[str] = Field(None, max_length=500)
    start_date_confirmed: bool = Field(..., description="Confirm start date")
    information_accurate: bool = Field(..., description="Confirm all information")
    questions_comments: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('start_date_confirmed', 'information_accurate')
    def must_confirm(cls, v):
        if not v:
            raise ValueError('Confirmation required')
        return v
    
class FinalReviewResponse(BaseModel):
    onboarding_complete: bool
    employee_id: str
    start_date: date
    first_day_instructions: str
    welcome_kit_tracking: str


# Create the 10-step onboarding chain
def create_employee_onboarding_chain() -> FormChainEngine:
    """Create the 10-step employee onboarding form chain"""
    
    steps = []
    
    # Step 1: Basic Information
    steps.append(FormStep(
        id="basic_info",
        title="Basic Information",
        description="Let's start with your basic information",
        request_model=BasicInfoRequest,
        response_model=BasicInfoResponse,
        processor=None,  # Would implement processor
        next_step_id="employment_details",
        is_entry_point=True
    ))
    
    # Step 2: Employment Details
    steps.append(FormStep(
        id="employment_details",
        title="Employment Details",
        description="Tell us about your role and compensation",
        request_model=EmploymentDetailsRequest,
        response_model=EmploymentDetailsResponse,
        processor=None,
        # Conditional routing based on requires_equipment
        conditional_next=lambda response: "it_equipment" if response.requires_equipment else "address_info"
    ))
    
    # Step 3: Address Information
    steps.append(FormStep(
        id="address_info",
        title="Address Information",
        description="Where are you located?",
        request_model=AddressInfoRequest,
        response_model=AddressInfoResponse,
        processor=None,
        next_step_id="emergency_contact"
    ))
    
    # Step 4: Emergency Contact
    steps.append(FormStep(
        id="emergency_contact",
        title="Emergency Contact",
        description="Who should we contact in case of emergency?",
        request_model=EmergencyContactRequest,
        response_model=EmergencyContactResponse,
        processor=None,
        next_step_id="education_experience"
    ))
    
    # Step 5: Education & Experience
    steps.append(FormStep(
        id="education_experience",
        title="Education & Experience",
        description="Tell us about your background",
        request_model=EducationExperienceRequest,
        response_model=EducationExperienceResponse,
        processor=None,
        next_step_id="benefits_selection"
    ))
    
    # Step 6: Benefits Selection
    steps.append(FormStep(
        id="benefits_selection",
        title="Benefits Selection",
        description="Choose your benefits package",
        request_model=BenefitsSelectionRequest,
        response_model=BenefitsSelectionResponse,
        processor=None,
        next_step_id="access_security"
    ))
    
    # Step 7: IT Equipment (Conditional)
    steps.append(FormStep(
        id="it_equipment",
        title="IT Equipment Request",
        description="Select your IT equipment needs",
        request_model=ITEquipmentRequest,
        response_model=ITEquipmentResponse,
        processor=None,
        next_step_id="address_info"  # Continue to address after equipment
    ))
    
    # Step 8: Access & Security
    steps.append(FormStep(
        id="access_security",
        title="Access & Security",
        description="Set up your access and security requirements",
        request_model=AccessSecurityRequest,
        response_model=AccessSecurityResponse,
        processor=None,
        next_step_id="training_orientation"
    ))
    
    # Step 9: Training & Orientation
    steps.append(FormStep(
        id="training_orientation",
        title="Training & Orientation",
        description="Schedule your training and orientation",
        request_model=TrainingOrientationRequest,
        response_model=TrainingOrientationResponse,
        processor=None,
        next_step_id="final_review",
        # Inject fields based on previous responses
        inject_fields=lambda response: [
            FormFieldSpec(
                name="buddy_program",
                field_type=FieldType.CHECKBOX,
                label="Would you like to join the buddy program?",
                required=False
            )
        ] if response.get('step_basic_info_response', {}).get('age', 30) < 25 else []
    ))
    
    # Step 10: Final Review
    steps.append(FormStep(
        id="final_review",
        title="Final Review & Welcome Kit",
        description="Review your information and complete onboarding",
        request_model=FinalReviewRequest,
        response_model=FinalReviewResponse,
        processor=None,
        is_exit_point=True
    ))
    
    # Create and return the chain
    chain = FormChainEngine(
        chain_id="employee_onboarding",
        title="New Employee Onboarding",
        description="Complete 10-step onboarding process for new employees",
        steps=steps,
        theme="professional"
    )
    
    return chain


if __name__ == "__main__":
    # Test chain creation
    chain = create_employee_onboarding_chain()
    print(f"Created employee onboarding chain with {len(chain.steps)} steps")
    print(f"Steps: {', '.join(chain.step_order)}")
    
    # Test form generation
    html = chain.generate_form_html("basic_info")
    print(f"\nGenerated HTML form: {len(html)} characters")
    print("Contains email field:", "email" in html)
    print("Contains date field:", 'type="date"' in html)