#!/usr/bin/env python3
"""
10-step employee onboarding form chain with navigation and no validation
Allows easy navigation between steps without losing state
"""

import sys
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum
import asyncio

sys.path.insert(0, '/var/www/ai_apps/playground')

from pydantic import BaseModel, Field, ConfigDict
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

# Step 1: Basic Information - NO VALIDATION
class BasicInfoRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    first_name: Optional[str] = Field(default="", description="First name")
    last_name: Optional[str] = Field(default="", description="Last name") 
    email: Optional[str] = Field(default="", description="Work email address")
    phone: Optional[str] = Field(default="", description="Phone number")
    date_of_birth: Optional[str] = Field(default="", description="Date of birth")

class BasicInfoResponse(BaseModel):
    employee_id: str
    full_name: str
    age: Optional[int] = None
    email_verified: bool = False

# Step 2: Employment Details - NO VALIDATION
class EmploymentDetailsRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="", description="Employee ID")
    employment_type: Optional[str] = Field(default="", description="Type of employment")
    department: Optional[str] = Field(default="", description="Department")
    job_title: Optional[str] = Field(default="", description="Job title")
    start_date: Optional[str] = Field(default="", description="Start date")
    manager_email: Optional[str] = Field(default="", description="Manager's email")
    salary: Optional[str] = Field(default="", description="Annual salary")

class EmploymentDetailsResponse(BaseModel):
    compensation_package_id: str
    requires_equipment: bool = False
    requires_visa: bool = False
    probation_period_days: int = 90

# Step 3: Address Information - NO VALIDATION
class AddressInfoRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="")
    street_address: Optional[str] = Field(default="")
    city: Optional[str] = Field(default="")
    state: Optional[str] = Field(default="")
    zip_code: Optional[str] = Field(default="")
    country: Optional[str] = Field(default="USA")
    work_location: Optional[str] = Field(default="", description="Primary work location")
    
class AddressInfoResponse(BaseModel):
    address_id: str
    tax_jurisdiction: str
    commute_eligible: bool
    remote_setup_required: bool

# Step 4: Emergency Contact - NO VALIDATION
class EmergencyContactRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="")
    contact_name: Optional[str] = Field(default="")
    relationship: Optional[str] = Field(default="")
    contact_phone: Optional[str] = Field(default="")
    contact_email: Optional[str] = Field(default="")
    alternate_phone: Optional[str] = Field(default="")
    
class EmergencyContactResponse(BaseModel):
    contact_id: str
    verified: bool

# Step 5: Education & Experience - NO VALIDATION
class EducationExperienceRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="")
    highest_education: Optional[str] = Field(default="")
    field_of_study: Optional[str] = Field(default="")
    university: Optional[str] = Field(default="")
    graduation_year: Optional[str] = Field(default="")
    years_of_experience: Optional[str] = Field(default="0")
    previous_companies: Optional[List[str]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)

class EducationExperienceResponse(BaseModel):
    profile_id: str
    skill_level: str
    training_recommendations: List[str]

# Step 6: Benefits Selection - NO VALIDATION
class BenefitsSelectionRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="")
    health_plan: Optional[str] = Field(default="")
    dental_plan: Optional[str] = Field(default="")
    vision_plan: Optional[str] = Field(default="")
    retirement_401k_percentage: Optional[str] = Field(default="0")
    life_insurance_multiplier: Optional[str] = Field(default="1")
    dependent_count: Optional[str] = Field(default="0")
    fsa_contribution: Optional[str] = Field(default="0")
    
class BenefitsSelectionResponse(BaseModel):
    benefits_package_id: str
    total_cost: Decimal
    employee_contribution: Decimal
    effective_date: date

# Step 7: IT Equipment (Conditional) - NO VALIDATION
class ITEquipmentRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="")
    laptop_type: Optional[str] = Field(default="", description="Laptop preference")
    needs_monitor: Optional[bool] = Field(default=False)
    monitor_count: Optional[str] = Field(default="1")
    needs_keyboard: Optional[bool] = Field(default=False)
    needs_mouse: Optional[bool] = Field(default=False)
    special_software: Optional[List[str]] = Field(default_factory=list)
    additional_requests: Optional[str] = Field(default="")
    
class ITEquipmentResponse(BaseModel):
    equipment_request_id: str
    estimated_ready_date: date
    total_cost: Decimal

# Step 8: Access & Security - NO VALIDATION
class AccessSecurityRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="")
    needs_building_access: Optional[bool] = Field(default=False)
    building_locations: Optional[List[str]] = Field(default_factory=list)
    needs_parking: Optional[bool] = Field(default=False)
    vehicle_license: Optional[str] = Field(default="")
    security_clearance_required: Optional[bool] = Field(default=False)
    background_check_consent: Optional[bool] = Field(default=False)
    systems_access: Optional[List[str]] = Field(default_factory=list)
    
class AccessSecurityResponse(BaseModel):
    access_request_id: str
    badge_number: str
    security_training_required: bool

# Step 9: Training & Orientation - NO VALIDATION
class TrainingOrientationRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="")
    preferred_training_track: Optional[str] = Field(default="")
    orientation_date: Optional[str] = Field(default="", description="Preferred orientation date")
    training_schedule_preference: Optional[str] = Field(default="flexible", description="morning/afternoon/flexible")
    mentor_preference: Optional[str] = Field(default="")
    accessibility_needs: Optional[str] = Field(default="")
    dietary_restrictions: Optional[str] = Field(default="")
    
class TrainingOrientationResponse(BaseModel):
    training_plan_id: str
    orientation_confirmed: bool
    mentor_assigned: str
    first_week_schedule: Dict[str, str]

# Step 10: Final Review & Welcome Kit - NO VALIDATION
class FinalReviewRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    employee_id: Optional[str] = Field(default="")
    tshirt_size: Optional[str] = Field(default="")
    welcome_kit_address: Optional[str] = Field(default="same", description="same/different")
    alternate_address: Optional[str] = Field(default="")
    start_date_confirmed: Optional[bool] = Field(default=False, description="Confirm start date")
    information_accurate: Optional[bool] = Field(default=False, description="Confirm all information")
    questions_comments: Optional[str] = Field(default="")
    
class FinalReviewResponse(BaseModel):
    onboarding_complete: bool
    employee_id: str
    start_date: date
    first_day_instructions: str
    welcome_kit_tracking: str


# Create the 10-step onboarding chain with navigation support
def create_employee_onboarding_chain() -> FormChainEngine:
    """Create the 10-step employee onboarding form chain with navigation support"""
    
    steps = []
    
    # Step 1: Basic Information
    steps.append(FormStep(
        id="basic_info",
        title="Step 1 of 10: Basic Information",
        description="Let's start with your basic information",
        request_model=BasicInfoRequest,
        response_model=BasicInfoResponse,
        processor=None,  # Would implement processor
        next_step_id="employment_details",
        is_entry_point=True,
        # Add field specifications for proper rendering
        fields=[
            FormFieldSpec(name="first_name", field_type=FieldType.TEXT, label="First Name", required=False),
            FormFieldSpec(name="last_name", field_type=FieldType.TEXT, label="Last Name", required=False),
            FormFieldSpec(name="email", field_type=FieldType.EMAIL, label="Email Address", required=False),
            FormFieldSpec(name="phone", field_type=FieldType.TEL, label="Phone Number", required=False),
            FormFieldSpec(name="date_of_birth", field_type=FieldType.DATE, label="Date of Birth", required=False),
        ]
    ))
    
    # Step 2: Employment Details
    steps.append(FormStep(
        id="employment_details",
        title="Step 2 of 10: Employment Details",
        description="Tell us about your role and compensation",
        request_model=EmploymentDetailsRequest,
        response_model=EmploymentDetailsResponse,
        processor=None,
        # Conditional routing based on requires_equipment
        conditional_next=lambda response: "it_equipment" if response.requires_equipment else "address_info",
        fields=[
            FormFieldSpec(
                name="employee_id", 
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(
                name="employment_type",
                field_type=FieldType.SELECT,
                label="Employment Type",
                options=[
                    {"value": t.value, "label": t.value.replace("_", " ").title()}
                    for t in EmploymentType
                ],
                required=False
            ),
            FormFieldSpec(
                name="department",
                field_type=FieldType.SELECT,
                label="Department",
                options=[
                    {"value": d.value, "label": d.value.title()}
                    for d in Department
                ],
                required=False
            ),
            FormFieldSpec(name="job_title", field_type=FieldType.TEXT, label="Job Title", required=False),
            FormFieldSpec(name="start_date", field_type=FieldType.DATE, label="Start Date", required=False),
            FormFieldSpec(name="manager_email", field_type=FieldType.EMAIL, label="Manager's Email", required=False),
            FormFieldSpec(name="salary", field_type=FieldType.NUMBER, label="Annual Salary", required=False),
        ]
    ))
    
    # Step 3: Address Information
    steps.append(FormStep(
        id="address_info",
        title="Step 3 of 10: Address Information",
        description="Where are you located?",
        request_model=AddressInfoRequest,
        response_model=AddressInfoResponse,
        processor=None,
        next_step_id="emergency_contact",
        fields=[
            FormFieldSpec(
                name="employee_id",
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(name="street_address", field_type=FieldType.TEXT, label="Street Address", required=False),
            FormFieldSpec(name="city", field_type=FieldType.TEXT, label="City", required=False),
            FormFieldSpec(name="state", field_type=FieldType.TEXT, label="State/Province", required=False),
            FormFieldSpec(name="zip_code", field_type=FieldType.TEXT, label="ZIP/Postal Code", required=False),
            FormFieldSpec(name="country", field_type=FieldType.TEXT, label="Country", default="USA", required=False),
            FormFieldSpec(
                name="work_location",
                field_type=FieldType.SELECT,
                label="Work Location Preference",
                options=[
                    {"value": loc.value, "label": loc.value.title()}
                    for loc in WorkLocation
                ],
                required=False
            ),
        ]
    ))
    
    # Step 4: Emergency Contact
    steps.append(FormStep(
        id="emergency_contact",
        title="Step 4 of 10: Emergency Contact",
        description="Who should we contact in case of emergency?",
        request_model=EmergencyContactRequest,
        response_model=EmergencyContactResponse,
        processor=None,
        next_step_id="education_experience",
        fields=[
            FormFieldSpec(
                name="employee_id",
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(name="contact_name", field_type=FieldType.TEXT, label="Contact Name", required=False),
            FormFieldSpec(name="relationship", field_type=FieldType.TEXT, label="Relationship", required=False),
            FormFieldSpec(name="contact_phone", field_type=FieldType.TEL, label="Contact Phone", required=False),
            FormFieldSpec(name="contact_email", field_type=FieldType.EMAIL, label="Contact Email", required=False),
            FormFieldSpec(name="alternate_phone", field_type=FieldType.TEL, label="Alternate Phone (Optional)", required=False),
        ]
    ))
    
    # Step 5: Education & Experience
    steps.append(FormStep(
        id="education_experience",
        title="Step 5 of 10: Education & Experience",
        description="Tell us about your background",
        request_model=EducationExperienceRequest,
        response_model=EducationExperienceResponse,
        processor=None,
        next_step_id="benefits_selection",
        fields=[
            FormFieldSpec(
                name="employee_id",
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(
                name="highest_education",
                field_type=FieldType.SELECT,
                label="Highest Education Level",
                options=[
                    {"value": edu.value, "label": edu.value.replace("_", " ").title()}
                    for edu in EducationLevel
                ],
                required=False
            ),
            FormFieldSpec(name="field_of_study", field_type=FieldType.TEXT, label="Field of Study", required=False),
            FormFieldSpec(name="university", field_type=FieldType.TEXT, label="University/College", required=False),
            FormFieldSpec(name="graduation_year", field_type=FieldType.NUMBER, label="Graduation Year", required=False),
            FormFieldSpec(name="years_of_experience", field_type=FieldType.NUMBER, label="Years of Experience", default="0", required=False),
            FormFieldSpec(
                name="previous_companies",
                field_type=FieldType.ARRAY,
                label="Previous Companies",
                required=False
            ),
            FormFieldSpec(
                name="certifications",
                field_type=FieldType.ARRAY,
                label="Professional Certifications",
                required=False
            ),
            FormFieldSpec(
                name="skills",
                field_type=FieldType.ARRAY,
                label="Key Skills",
                required=False
            ),
        ]
    ))
    
    # Step 6: Benefits Selection
    steps.append(FormStep(
        id="benefits_selection",
        title="Step 6 of 10: Benefits Selection",
        description="Choose your benefits package",
        request_model=BenefitsSelectionRequest,
        response_model=BenefitsSelectionResponse,
        processor=None,
        next_step_id="access_security",
        fields=[
            FormFieldSpec(
                name="employee_id",
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(
                name="health_plan",
                field_type=FieldType.SELECT,
                label="Health Insurance Plan",
                options=[
                    {"value": plan.value, "label": f"{plan.value.title()} Plan"}
                    for plan in BenefitPlan
                ],
                required=False
            ),
            FormFieldSpec(
                name="dental_plan",
                field_type=FieldType.SELECT,
                label="Dental Insurance Plan",
                options=[
                    {"value": plan.value, "label": f"{plan.value.title()} Plan"}
                    for plan in BenefitPlan
                ],
                required=False
            ),
            FormFieldSpec(
                name="vision_plan",
                field_type=FieldType.SELECT,
                label="Vision Insurance Plan",
                options=[
                    {"value": plan.value, "label": f"{plan.value.title()} Plan"}
                    for plan in BenefitPlan
                ],
                required=False
            ),
            FormFieldSpec(
                name="retirement_401k_percentage",
                field_type=FieldType.NUMBER,
                label="401(k) Contribution %",
                default="0",
                required=False
            ),
            FormFieldSpec(
                name="life_insurance_multiplier",
                field_type=FieldType.NUMBER,
                label="Life Insurance (Salary Multiplier)",
                default="1",
                required=False
            ),
            FormFieldSpec(
                name="dependent_count",
                field_type=FieldType.NUMBER,
                label="Number of Dependents",
                default="0",
                required=False
            ),
            FormFieldSpec(
                name="fsa_contribution",
                field_type=FieldType.NUMBER,
                label="FSA Annual Contribution",
                default="0",
                required=False
            ),
        ]
    ))
    
    # Step 7: IT Equipment (Conditional)
    steps.append(FormStep(
        id="it_equipment",
        title="Step 7 of 10: IT Equipment Request",
        description="Select your IT equipment needs",
        request_model=ITEquipmentRequest,
        response_model=ITEquipmentResponse,
        processor=None,
        next_step_id="address_info",  # Continue to address after equipment
        fields=[
            FormFieldSpec(
                name="employee_id",
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(
                name="laptop_type",
                field_type=FieldType.SELECT,
                label="Laptop Type",
                options=[
                    {"value": "MacBook Pro 16", "label": "MacBook Pro 16-inch"},
                    {"value": "MacBook Pro 14", "label": "MacBook Pro 14-inch"},
                    {"value": "Dell XPS 15", "label": "Dell XPS 15"},
                    {"value": "ThinkPad X1", "label": "ThinkPad X1 Carbon"},
                ],
                required=False
            ),
            FormFieldSpec(name="needs_monitor", field_type=FieldType.CHECKBOX, label="Need External Monitor?"),
            FormFieldSpec(
                name="monitor_count",
                field_type=FieldType.NUMBER,
                label="Number of Monitors",
                show_if="needs_monitor",
                default="1",
                required=False
            ),
            FormFieldSpec(name="needs_keyboard", field_type=FieldType.CHECKBOX, label="Need External Keyboard?"),
            FormFieldSpec(name="needs_mouse", field_type=FieldType.CHECKBOX, label="Need External Mouse?"),
            FormFieldSpec(
                name="special_software",
                field_type=FieldType.ARRAY,
                label="Special Software Requirements",
                placeholder="Enter software names",
                required=False
            ),
            FormFieldSpec(
                name="additional_requests",
                field_type=FieldType.TEXTAREA,
                label="Additional Equipment Requests",
                required=False
            ),
        ]
    ))
    
    # Step 8: Access & Security
    steps.append(FormStep(
        id="access_security",
        title="Step 8 of 10: Access & Security",
        description="Set up your access and security requirements",
        request_model=AccessSecurityRequest,
        response_model=AccessSecurityResponse,
        processor=None,
        next_step_id="training_orientation",
        fields=[
            FormFieldSpec(
                name="employee_id",
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(name="needs_building_access", field_type=FieldType.CHECKBOX, label="Need Building Access?"),
            FormFieldSpec(
                name="building_locations",
                field_type=FieldType.ARRAY,
                label="Building Locations",
                show_if="needs_building_access",
                required=False
            ),
            FormFieldSpec(name="needs_parking", field_type=FieldType.CHECKBOX, label="Need Parking?"),
            FormFieldSpec(
                name="vehicle_license",
                field_type=FieldType.TEXT,
                label="Vehicle License Plate",
                show_if="needs_parking",
                required=False
            ),
            FormFieldSpec(
                name="security_clearance_required",
                field_type=FieldType.CHECKBOX,
                label="Security Clearance Required?"
            ),
            FormFieldSpec(
                name="background_check_consent",
                field_type=FieldType.CHECKBOX,
                label="Background Check Consent"
            ),
            FormFieldSpec(
                name="systems_access",
                field_type=FieldType.ARRAY,
                label="System Access Requirements",
                required=False
            ),
        ]
    ))
    
    # Step 9: Training & Orientation
    steps.append(FormStep(
        id="training_orientation",
        title="Step 9 of 10: Training & Orientation",
        description="Schedule your training and orientation",
        request_model=TrainingOrientationRequest,
        response_model=TrainingOrientationResponse,
        processor=None,
        next_step_id="final_review",
        fields=[
            FormFieldSpec(
                name="employee_id",
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(
                name="preferred_training_track",
                field_type=FieldType.SELECT,
                label="Preferred Training Track",
                options=[
                    {"value": track.value, "label": track.value.title()}
                    for track in TrainingTrack
                ],
                required=False
            ),
            FormFieldSpec(
                name="orientation_date",
                field_type=FieldType.DATE,
                label="Preferred Orientation Date",
                required=False
            ),
            FormFieldSpec(
                name="training_schedule_preference",
                field_type=FieldType.SELECT,
                label="Training Schedule Preference",
                options=[
                    {"value": "morning", "label": "Morning (9 AM - 12 PM)"},
                    {"value": "afternoon", "label": "Afternoon (1 PM - 5 PM)"},
                    {"value": "flexible", "label": "Flexible"},
                ],
                default="flexible",
                required=False
            ),
            FormFieldSpec(
                name="mentor_preference",
                field_type=FieldType.TEXT,
                label="Mentor Preference (Optional)",
                required=False
            ),
            FormFieldSpec(
                name="accessibility_needs",
                field_type=FieldType.TEXTAREA,
                label="Accessibility Requirements",
                required=False
            ),
            FormFieldSpec(
                name="dietary_restrictions",
                field_type=FieldType.TEXT,
                label="Dietary Restrictions",
                required=False
            ),
        ]
    ))
    
    # Step 10: Final Review
    steps.append(FormStep(
        id="final_review",
        title="Step 10 of 10: Final Review & Welcome Kit",
        description="Review your information and complete onboarding",
        request_model=FinalReviewRequest,
        response_model=FinalReviewResponse,
        processor=None,
        is_exit_point=True,
        fields=[
            FormFieldSpec(
                name="employee_id",
                field_type=FieldType.HIDDEN,
                inject_from="step_basic_info_response.employee_id"
            ),
            FormFieldSpec(
                name="tshirt_size",
                field_type=FieldType.SELECT,
                label="T-Shirt Size",
                options=[
                    {"value": size.value, "label": size.value.upper()}
                    for size in TShirtSize
                ],
                required=False
            ),
            FormFieldSpec(
                name="welcome_kit_address",
                field_type=FieldType.SELECT,
                label="Welcome Kit Delivery Address",
                options=[
                    {"value": "same", "label": "Same as home address"},
                    {"value": "different", "label": "Different address"},
                ],
                default="same",
                required=False
            ),
            FormFieldSpec(
                name="alternate_address",
                field_type=FieldType.TEXTAREA,
                label="Alternate Address",
                show_if="welcome_kit_address == 'different'",
                required=False
            ),
            FormFieldSpec(
                name="start_date_confirmed",
                field_type=FieldType.CHECKBOX,
                label="I confirm my start date"
            ),
            FormFieldSpec(
                name="information_accurate",
                field_type=FieldType.CHECKBOX,
                label="All information provided is accurate"
            ),
            FormFieldSpec(
                name="questions_comments",
                field_type=FieldType.TEXTAREA,
                label="Questions or Comments",
                required=False
            ),
        ]
    ))
    
    # Create and return the chain
    chain = FormChainEngine(
        chain_id="employee_onboarding",
        title="New Employee Onboarding",
        description="Complete 10-step onboarding process for new employees",
        steps=steps,
        theme="professional",
        allow_navigation=True  # Enable navigation between steps
    )
    
    return chain


if __name__ == "__main__":
    # Test chain creation
    chain = create_employee_onboarding_chain()
    print(f"Created employee onboarding chain with {len(chain.steps)} steps")
    print(f"Steps: {', '.join(chain.step_order)}")
    print(f"Navigation enabled: {getattr(chain, 'allow_navigation', False)}")
    
    # Test form generation
    html = chain.generate_form_html("basic_info")
    print(f"\nGenerated HTML form: {len(html)} characters")
    print("Contains email field:", "email" in html)
    print("Contains date field:", 'type="date"' in html)