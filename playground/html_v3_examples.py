#!/usr/bin/env python3
"""
Real-World Examples for HTML Form Chain Engine v3.0

These examples demonstrate the power of treating forms as input-output processors
in a chain, where each step's response feeds into the next step's form.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
import asyncio
import random
import json

from html_v3 import (
    FormChainEngine, FormStep, FormStepProcessor, FormFieldSpec,
    FieldType, create_form_chain
)


# ==============================================================================
# Example 1: Data Quality Check Process
# ==============================================================================

class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


# Step 1: Select Database and Table
class DataSourceRequest(BaseModel):
    database_type: DatabaseType = Field(..., description="Type of database")
    connection_string: str = Field(..., description="Database connection string")
    table_name: str = Field(..., description="Table or collection name to analyze")
    sample_size: int = Field(1000, ge=100, le=10000, description="Number of rows to sample")


class DataSourceResponse(BaseModel):
    database_type: DatabaseType
    table_name: str
    total_rows: int
    columns: List[Dict[str, str]]  # name, type, nullable
    sample_data: List[Dict[str, Any]]


# Step 2: Select Columns and Quality Checks
class QualityCheckRequest(BaseModel):
    # These will be populated from previous response
    database_type: DatabaseType
    table_name: str
    
    # User selects columns to check
    columns_to_check: List[str] = Field(..., description="Select columns to perform quality checks on")
    
    # Quality check options
    check_nulls: bool = Field(True, description="Check for null values")
    check_duplicates: bool = Field(True, description="Check for duplicate values")
    check_patterns: bool = Field(False, description="Check data patterns and formats")
    check_outliers: bool = Field(False, description="Check for statistical outliers")
    custom_rules: Optional[str] = Field(None, description="Custom SQL/query rules (JSON format)")


class QualityCheckResponse(BaseModel):
    columns_checked: List[str]
    quality_issues: List[Dict[str, Any]]  # column, issue_type, count, examples
    quality_score: float
    recommendations: List[str]


# Step 3: Configure Actions
class QualityActionRequest(BaseModel):
    # Previous context
    table_name: str
    quality_score: float
    
    # Actions to take
    generate_report: bool = Field(True, description="Generate detailed quality report")
    create_cleaned_table: bool = Field(False, description="Create a cleaned version of the table")
    add_constraints: bool = Field(False, description="Add database constraints based on findings")
    schedule_monitoring: bool = Field(False, description="Schedule regular quality checks")
    
    # If creating cleaned table
    cleaned_table_name: Optional[str] = Field(None, description="Name for the cleaned table")
    
    # If scheduling
    monitoring_frequency: Optional[str] = Field(None, description="How often to run checks (daily, weekly, monthly)")


class QualityActionResponse(BaseModel):
    actions_completed: List[str]
    report_url: Optional[str]
    cleaned_table_name: Optional[str]
    monitoring_job_id: Optional[str]
    completion_time: datetime


# Processors
class DataSourceProcessor(FormStepProcessor):
    async def process(self, input_data: DataSourceRequest, chain_context: Dict[str, Any]) -> DataSourceResponse:
        # Simulate database connection and metadata retrieval
        
        # Fake column data
        columns = [
            {"name": "id", "type": "integer", "nullable": "false"},
            {"name": "customer_name", "type": "varchar(255)", "nullable": "false"},
            {"name": "email", "type": "varchar(255)", "nullable": "true"},
            {"name": "order_date", "type": "date", "nullable": "false"},
            {"name": "order_amount", "type": "decimal(10,2)", "nullable": "false"},
            {"name": "status", "type": "varchar(50)", "nullable": "false"},
            {"name": "phone", "type": "varchar(20)", "nullable": "true"},
            {"name": "address", "type": "text", "nullable": "true"}
        ]
        
        # Fake sample data
        sample_data = []
        for i in range(5):
            sample_data.append({
                "id": i + 1,
                "customer_name": f"Customer {i+1}",
                "email": f"customer{i+1}@example.com" if i % 2 == 0 else None,
                "order_date": "2024-01-15",
                "order_amount": round(random.uniform(10, 500), 2),
                "status": random.choice(["pending", "completed", "cancelled"]),
                "phone": f"555-{random.randint(1000, 9999)}" if i % 3 == 0 else None,
                "address": f"{random.randint(100, 999)} Main St" if i % 2 == 0 else None
            })
        
        return DataSourceResponse(
            database_type=input_data.database_type,
            table_name=input_data.table_name,
            total_rows=random.randint(10000, 100000),
            columns=columns,
            sample_data=sample_data
        )


class QualityCheckProcessor(FormStepProcessor):
    async def process(self, input_data: QualityCheckRequest, chain_context: Dict[str, Any]) -> QualityCheckResponse:
        # Simulate quality checks
        issues = []
        
        if input_data.check_nulls:
            for col in input_data.columns_to_check:
                if random.random() > 0.7:  # 30% chance of null issues
                    issues.append({
                        "column": col,
                        "issue_type": "null_values",
                        "count": random.randint(100, 1000),
                        "percentage": round(random.uniform(1, 15), 2),
                        "examples": ["NULL", "NULL", "NULL"]
                    })
        
        if input_data.check_duplicates:
            if "email" in input_data.columns_to_check:
                issues.append({
                    "column": "email",
                    "issue_type": "duplicates",
                    "count": random.randint(50, 200),
                    "percentage": round(random.uniform(0.5, 5), 2),
                    "examples": ["user@example.com", "test@test.com"]
                })
        
        if input_data.check_patterns:
            if "email" in input_data.columns_to_check:
                issues.append({
                    "column": "email",
                    "issue_type": "invalid_format",
                    "count": random.randint(10, 50),
                    "percentage": round(random.uniform(0.1, 1), 2),
                    "examples": ["not-an-email", "missing@", "@nodomain"]
                })
        
        # Calculate quality score
        total_issues = sum(issue["count"] for issue in issues)
        quality_score = max(0, 100 - (total_issues / 100))
        
        # Generate recommendations
        recommendations = []
        if any(i["issue_type"] == "null_values" for i in issues):
            recommendations.append("Consider adding NOT NULL constraints to critical columns")
        if any(i["issue_type"] == "duplicates" for i in issues):
            recommendations.append("Add unique constraints to prevent duplicate entries")
        if any(i["issue_type"] == "invalid_format" for i in issues):
            recommendations.append("Implement data validation at the application level")
        
        return QualityCheckResponse(
            columns_checked=input_data.columns_to_check,
            quality_issues=issues,
            quality_score=round(quality_score, 2),
            recommendations=recommendations
        )


class QualityActionProcessor(FormStepProcessor):
    async def process(self, input_data: QualityActionRequest, chain_context: Dict[str, Any]) -> QualityActionResponse:
        actions_completed = []
        
        report_url = None
        if input_data.generate_report:
            report_url = f"/reports/quality_{input_data.table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            actions_completed.append("Generated quality report")
        
        cleaned_table = None
        if input_data.create_cleaned_table and input_data.cleaned_table_name:
            cleaned_table = input_data.cleaned_table_name
            actions_completed.append(f"Created cleaned table: {cleaned_table}")
        
        monitoring_job_id = None
        if input_data.schedule_monitoring:
            monitoring_job_id = f"QC_{input_data.table_name}_{random.randint(1000, 9999)}"
            actions_completed.append(f"Scheduled {input_data.monitoring_frequency} quality checks")
        
        return QualityActionResponse(
            actions_completed=actions_completed,
            report_url=report_url,
            cleaned_table_name=cleaned_table,
            monitoring_job_id=monitoring_job_id,
            completion_time=datetime.now()
        )


def create_data_quality_chain() -> FormChainEngine:
    """Create the data quality check form chain"""
    
    # Define custom field injection for step 2
    def inject_column_selection(response: DataSourceResponse) -> List[FormFieldSpec]:
        # Don't inject individual checkboxes - the columns_to_check field handles this
        # Instead, we could inject other fields based on the response
        fields = []
        
        # Add a hidden field with available columns for JavaScript to use
        fields.append(
            FormFieldSpec(
                name="available_columns",
                field_type=FieldType.HIDDEN,
                label="Available Columns",
                default=json.dumps([col['name'] for col in response.columns])
            )
        )
        
        return fields
    
    # Define conditional next step (could route based on quality score)
    def determine_next_step(response: QualityCheckResponse) -> str:
        # Always go to step 3 in this example, but could branch based on score
        return "step_3"
    
    steps = [
        FormStep(
            id="step_1",
            title="Select Data Source",
            description="Connect to your database and select a table to analyze",
            request_model=DataSourceRequest,
            response_model=DataSourceResponse,
            processor=DataSourceProcessor(),
            is_entry_point=True,
            next_step_id="step_2"
        ),
        FormStep(
            id="step_2",
            title="Configure Quality Checks",
            description="Select columns and quality checks to perform",
            request_model=QualityCheckRequest,
            response_model=QualityCheckResponse,
            processor=QualityCheckProcessor(),
            next_step_id="step_3",
            conditional_next=determine_next_step,
            inject_fields=inject_column_selection
        ),
        FormStep(
            id="step_3",
            title="Take Action",
            description="Review results and choose actions to take",
            request_model=QualityActionRequest,
            response_model=QualityActionResponse,
            processor=QualityActionProcessor(),
            is_exit_point=True
        )
    ]
    
    return FormChainEngine(
        chain_id="data_quality_check",
        title="Data Quality Check Process",
        description="Analyze your data quality and take corrective actions",
        steps=steps,
        theme="modern"
    )


# ==============================================================================
# Example 2: Multi-stage Job Application with Dynamic Paths
# ==============================================================================

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"


class Department(str, Enum):
    ENGINEERING = "engineering"
    SALES = "sales"
    MARKETING = "marketing"
    OPERATIONS = "operations"


# Step 1: Basic Information
class ApplicantBasicRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    phone: str = Field(...)
    experience_level: ExperienceLevel
    department: Department
    years_experience: int = Field(..., ge=0, le=50)
    resume_text: str = Field(..., description="Paste your resume or key highlights")


class ApplicantBasicResponse(BaseModel):
    applicant_id: str
    experience_level: ExperienceLevel
    department: Department
    screening_score: float
    next_assessments: List[str]


# Step 2: Dynamic Technical Assessment (for Engineering)
class TechnicalAssessmentRequest(BaseModel):
    applicant_id: str
    programming_languages: List[str] = Field(..., description="Select all that apply")
    
    # Dynamic fields based on experience level
    system_design_approach: Optional[str] = Field(None, description="How would you design a distributed cache?")
    code_sample: Optional[str] = Field(None, description="Provide a code sample showcasing your best work")
    
    # For senior/lead only
    architecture_experience: Optional[str] = Field(None, description="Describe your experience with system architecture")
    team_size_managed: Optional[int] = Field(None, ge=0, description="Largest team you've managed")


class TechnicalAssessmentResponse(BaseModel):
    technical_score: float
    strengths: List[str]
    areas_for_discussion: List[str]
    recommended_interviewers: List[str]


# Step 2 Alternative: Sales Assessment
class SalesAssessmentRequest(BaseModel):
    applicant_id: str
    sales_methodology: str = Field(..., description="Your preferred sales methodology")
    largest_deal_size: float = Field(..., description="Largest deal closed (in USD)")
    sales_cycle_experience: str = Field(..., description="Describe your experience with enterprise sales cycles")
    crm_tools: List[str] = Field(..., description="CRM tools you're proficient with")


class SalesAssessmentResponse(BaseModel):
    sales_readiness_score: float
    industry_fit: str
    recommended_territory: Optional[str]


# Step 3: Interview Scheduling
class InterviewSchedulingRequest(BaseModel):
    applicant_id: str
    availability_dates: List[date] = Field(..., description="Select your available dates")
    timezone: str = Field(..., description="Your timezone")
    preferred_times: List[str] = Field(..., description="Preferred time slots")
    interview_format_preference: str = Field(..., description="Video, Phone, or In-person")
    accommodation_needs: Optional[str] = Field(None, description="Any accommodations needed?")


class InterviewSchedulingResponse(BaseModel):
    interview_scheduled: bool
    interview_date: Optional[datetime]
    interview_format: str
    interviewers: List[str]
    next_steps: str


# Processors
class ApplicantScreeningProcessor(FormStepProcessor):
    async def process(self, input_data: ApplicantBasicRequest, chain_context: Dict[str, Any]) -> ApplicantBasicResponse:
        # Generate applicant ID
        applicant_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Calculate screening score based on experience
        base_score = 60
        if input_data.years_experience >= 5:
            base_score += 20
        if input_data.experience_level in [ExperienceLevel.SENIOR, ExperienceLevel.LEAD]:
            base_score += 15
        
        # Determine assessments based on department
        assessments = []
        if input_data.department == Department.ENGINEERING:
            assessments = ["Technical Assessment", "Coding Challenge", "System Design"]
        elif input_data.department == Department.SALES:
            assessments = ["Sales Methodology", "Role Play", "Territory Planning"]
        
        return ApplicantBasicResponse(
            applicant_id=applicant_id,
            experience_level=input_data.experience_level,
            department=input_data.department,
            screening_score=min(base_score + random.randint(-10, 10), 100),
            next_assessments=assessments
        )


def create_job_application_chain() -> FormChainEngine:
    """Create a dynamic job application chain"""
    
    # Determine next step based on department
    def route_by_department(response: ApplicantBasicResponse) -> str:
        if response.department == Department.ENGINEERING:
            return "tech_assessment"
        elif response.department == Department.SALES:
            return "sales_assessment"
        else:
            return "scheduling"  # Skip to scheduling for other departments
    
    # Inject fields based on experience level
    def inject_senior_fields(response: ApplicantBasicResponse) -> List[FormFieldSpec]:
        fields = []
        if response.experience_level in [ExperienceLevel.SENIOR, ExperienceLevel.LEAD]:
            fields.extend([
                FormFieldSpec(
                    name="leadership_experience",
                    field_type=FieldType.TEXTAREA,
                    label="Leadership Experience",
                    help_text="Describe your experience leading teams or projects",
                    required=True
                ),
                FormFieldSpec(
                    name="mentoring_approach",
                    field_type=FieldType.TEXTAREA,
                    label="Mentoring Philosophy",
                    help_text="How do you approach mentoring junior team members?",
                    required=False
                )
            ])
        return fields
    
    steps = [
        FormStep(
            id="basic_info",
            title="Basic Information",
            description="Tell us about yourself and your experience",
            request_model=ApplicantBasicRequest,
            response_model=ApplicantBasicResponse,
            processor=ApplicantScreeningProcessor(),
            is_entry_point=True,
            conditional_next=route_by_department
        ),
        FormStep(
            id="tech_assessment",
            title="Technical Assessment",
            description="Complete technical evaluation based on your experience level",
            request_model=TechnicalAssessmentRequest,
            response_model=TechnicalAssessmentResponse,
            processor=None,  # Would implement actual processor
            next_step_id="scheduling",
            inject_fields=inject_senior_fields
        ),
        FormStep(
            id="sales_assessment",
            title="Sales Assessment",
            description="Tell us about your sales experience and approach",
            request_model=SalesAssessmentRequest,
            response_model=SalesAssessmentResponse,
            processor=None,  # Would implement actual processor
            next_step_id="scheduling"
        ),
        FormStep(
            id="scheduling",
            title="Schedule Your Interview",
            description="Select your availability for the interview process",
            request_model=InterviewSchedulingRequest,
            response_model=InterviewSchedulingResponse,
            processor=None,  # Would implement actual processor
            is_exit_point=True
        )
    ]
    
    return FormChainEngine(
        chain_id="job_application",
        title="Join Our Team - Application Process",
        description="Complete our multi-stage application process",
        steps=steps,
        theme="modern"
    )


# ==============================================================================
# Example 3: Insurance Claim Process with Document Upload
# ==============================================================================

class ClaimType(str, Enum):
    AUTO = "auto"
    HOME = "home"
    HEALTH = "health"
    TRAVEL = "travel"


# Step 1: Claim Type Selection
class ClaimInitiationRequest(BaseModel):
    policy_number: str = Field(..., description="Your insurance policy number")
    claim_type: ClaimType = Field(..., description="Type of claim")
    incident_date: date = Field(..., description="When did the incident occur?")
    incident_description: str = Field(..., description="Brief description of what happened")
    estimated_loss: float = Field(..., ge=0, description="Estimated loss amount in USD")


class ClaimInitiationResponse(BaseModel):
    claim_id: str
    claim_type: ClaimType
    coverage_verified: bool
    deductible_amount: float
    required_documents: List[str]


# Step 2A: Auto Claim Details
class AutoClaimRequest(BaseModel):
    claim_id: str
    vehicle_vin: str = Field(..., description="Vehicle Identification Number")
    accident_location: str = Field(..., description="Where did the accident occur?")
    other_party_involved: bool = Field(..., description="Was another party involved?")
    
    # Conditional fields
    other_driver_info: Optional[str] = Field(None, description="Other driver's information")
    police_report_number: Optional[str] = Field(None, description="Police report number if available")
    
    injuries_reported: bool = Field(..., description="Were there any injuries?")
    vehicle_driveable: bool = Field(..., description="Is the vehicle still driveable?")
    
    photos_description: str = Field(..., description="Describe the photos you'll upload")


# Step 2B: Home Claim Details  
class HomeClaimRequest(BaseModel):
    claim_id: str
    property_address: str = Field(..., description="Address of the affected property")
    damage_type: str = Field(..., description="Type of damage (fire, water, theft, etc.)")
    affected_areas: List[str] = Field(..., description="Which areas of the home were affected?")
    temporary_repairs_made: bool = Field(..., description="Have you made temporary repairs?")
    property_vacant: bool = Field(..., description="Is the property currently vacant?")
    contractor_estimate: Optional[float] = Field(None, description="Contractor estimate if available")


# Common response for claim details
class ClaimDetailsResponse(BaseModel):
    claim_id: str
    details_recorded: bool
    adjuster_assigned: bool
    adjuster_name: Optional[str]
    inspection_scheduled: Optional[datetime]
    next_action_required: str


# Step 3: Document Upload
class DocumentUploadRequest(BaseModel):
    claim_id: str
    documents_ready: bool = Field(..., description="I have all required documents ready to upload")
    
    # Document checklist (dynamic based on claim type)
    photos_uploaded: bool = Field(False, description="Damage photos")
    receipts_uploaded: bool = Field(False, description="Receipts for damaged items")
    police_report_uploaded: Optional[bool] = Field(None, description="Police report (if applicable)")
    medical_records_uploaded: Optional[bool] = Field(None, description="Medical records (if injuries)")
    
    additional_notes: Optional[str] = Field(None, description="Any additional information")


class DocumentUploadResponse(BaseModel):
    claim_id: str
    documents_received: List[str]
    documents_missing: List[str]
    claim_status: str
    estimated_processing_time: str
    next_steps: List[str]


def create_insurance_claim_chain() -> FormChainEngine:
    """Create an insurance claim processing chain"""
    
    # Route based on claim type
    def route_by_claim_type(response: ClaimInitiationResponse) -> str:
        if response.claim_type == ClaimType.AUTO:
            return "auto_details"
        elif response.claim_type == ClaimType.HOME:
            return "home_details"
        else:
            return "document_upload"  # Skip to documents for other types
    
    # Inject document fields based on claim type and previous responses
    def inject_document_fields(response: Any) -> List[FormFieldSpec]:
        fields = []
        
        # Get claim type from chain context
        if hasattr(response, 'claim_type'):
            if response.claim_type == ClaimType.AUTO:
                fields.append(
                    FormFieldSpec(
                        name="vehicle_photos",
                        field_type=FieldType.FILE,
                        label="Vehicle Damage Photos",
                        required=True,
                        help_text="Upload photos showing all damage to your vehicle",
                        attributes={"accept": "image/*", "multiple": True}
                    )
                )
        
        return fields
    
    steps = [
        FormStep(
            id="claim_initiation",
            title="Start Your Claim",
            description="Begin your insurance claim process",
            request_model=ClaimInitiationRequest,
            response_model=ClaimInitiationResponse,
            processor=None,
            is_entry_point=True,
            conditional_next=route_by_claim_type
        ),
        FormStep(
            id="auto_details",
            title="Auto Claim Details",
            description="Provide specific details about your auto claim",
            request_model=AutoClaimRequest,
            response_model=ClaimDetailsResponse,
            processor=None,
            next_step_id="document_upload"
        ),
        FormStep(
            id="home_details",
            title="Property Claim Details",
            description="Provide specific details about your property claim",
            request_model=HomeClaimRequest,
            response_model=ClaimDetailsResponse,
            processor=None,
            next_step_id="document_upload"
        ),
        FormStep(
            id="document_upload",
            title="Upload Supporting Documents",
            description="Upload all required documentation for your claim",
            request_model=DocumentUploadRequest,
            response_model=DocumentUploadResponse,
            processor=None,
            is_exit_point=True,
            inject_fields=inject_document_fields
        )
    ]
    
    return FormChainEngine(
        chain_id="insurance_claim",
        title="File an Insurance Claim",
        description="Submit and track your insurance claim online",
        steps=steps,
        theme="modern"
    )


# ==============================================================================
# Example 4: Customer Support Ticket with AI-Driven Routing
# ==============================================================================

class IssueCategory(str, Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature"
    OTHER = "other"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Step 1: Issue Description
class SupportTicketRequest(BaseModel):
    customer_email: str = Field(..., description="Your email address")
    issue_category: IssueCategory = Field(..., description="What type of issue are you experiencing?")
    issue_summary: str = Field(..., max_length=200, description="Brief summary of your issue")
    issue_description: str = Field(..., description="Detailed description of the problem")
    affected_services: List[str] = Field(..., description="Which services are affected?")
    impact_level: Priority = Field(..., description="How is this impacting your work?")


class SupportTicketResponse(BaseModel):
    ticket_id: str
    issue_category: IssueCategory
    suggested_solutions: List[Dict[str, str]]  # title, description, link
    requires_human_support: bool
    ai_confidence_score: float


# Step 2: Diagnostic Information (Technical Issues)
class TechnicalDiagnosticsRequest(BaseModel):
    ticket_id: str
    operating_system: str = Field(..., description="Your operating system")
    browser_version: str = Field(..., description="Browser and version")
    error_messages: Optional[str] = Field(None, description="Any error messages you see")
    steps_to_reproduce: str = Field(..., description="Steps to reproduce the issue")
    tried_solutions: List[str] = Field(default_factory=list, description="Solutions you've already tried")
    can_share_screen: bool = Field(..., description="Can you share your screen for debugging?")


# Step 2: Billing Information (Billing Issues)
class BillingDetailsRequest(BaseModel):
    ticket_id: str
    account_id: str = Field(..., description="Your account ID")
    invoice_number: Optional[str] = Field(None, description="Invoice number if applicable")
    payment_method: str = Field(..., description="Payment method used")
    dispute_amount: Optional[float] = Field(None, description="Amount in dispute if any")
    billing_period: str = Field(..., description="Billing period in question")


# Common response for diagnostics
class DiagnosticsResponse(BaseModel):
    ticket_id: str
    automated_fix_attempted: bool
    fix_successful: Optional[bool]
    human_agent_required: bool
    estimated_wait_time: Optional[int]  # minutes
    knowledge_base_articles: List[str]


# Step 3: Resolution or Escalation
class ResolutionRequest(BaseModel):
    ticket_id: str
    solution_helpful: bool = Field(..., description="Did the suggested solutions help?")
    issue_resolved: bool = Field(..., description="Is your issue now resolved?")
    
    # If not resolved
    request_callback: Optional[bool] = Field(None, description="Request a callback from support?")
    preferred_contact_time: Optional[str] = Field(None, description="Best time to contact you")
    additional_comments: Optional[str] = Field(None, description="Any additional information")
    
    # Feedback
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5, description="Rate your experience (1-5)")


class ResolutionResponse(BaseModel):
    ticket_id: str
    ticket_status: str
    resolution_summary: str
    callback_scheduled: Optional[datetime]
    agent_assigned: Optional[str]
    reference_number: str
    follow_up_actions: List[str]


def create_support_ticket_chain() -> FormChainEngine:
    """Create a customer support ticket chain with intelligent routing"""
    
    # Route based on issue category and AI analysis
    def route_support_ticket(response: SupportTicketResponse) -> str:
        if not response.requires_human_support and response.ai_confidence_score > 0.8:
            return "resolution"  # Skip to resolution if AI solved it
        
        if response.issue_category == IssueCategory.TECHNICAL:
            return "tech_diagnostics"
        elif response.issue_category == IssueCategory.BILLING:
            return "billing_details"
        else:
            return "resolution"
    
    # Inject fields based on previous responses
    def inject_resolution_fields(response: Any) -> List[FormFieldSpec]:
        fields = []
        
        if hasattr(response, 'human_agent_required') and response.human_agent_required:
            fields.extend([
                FormFieldSpec(
                    name="urgency_reason",
                    field_type=FieldType.TEXTAREA,
                    label="Why is this urgent?",
                    help_text="Help us prioritize your request",
                    required=True
                ),
                FormFieldSpec(
                    name="business_impact",
                    field_type=FieldType.SELECT,
                    label="Business Impact",
                    options=[
                        {"value": "none", "label": "No impact"},
                        {"value": "minor", "label": "Minor inconvenience"},
                        {"value": "moderate", "label": "Affecting productivity"},
                        {"value": "severe", "label": "Business operations blocked"}
                    ],
                    required=True
                )
            ])
        
        return fields
    
    steps = [
        FormStep(
            id="ticket_creation",
            title="Create Support Ticket",
            description="Describe your issue and we'll help you resolve it",
            request_model=SupportTicketRequest,
            response_model=SupportTicketResponse,
            processor=None,
            is_entry_point=True,
            conditional_next=route_support_ticket
        ),
        FormStep(
            id="tech_diagnostics",
            title="Technical Diagnostics",
            description="Help us understand your technical environment",
            request_model=TechnicalDiagnosticsRequest,
            response_model=DiagnosticsResponse,
            processor=None,
            next_step_id="resolution"
        ),
        FormStep(
            id="billing_details",
            title="Billing Information",
            description="Provide details about your billing issue",
            request_model=BillingDetailsRequest,
            response_model=DiagnosticsResponse,
            processor=None,
            next_step_id="resolution"
        ),
        FormStep(
            id="resolution",
            title="Resolution & Feedback",
            description="Let us know if we've resolved your issue",
            request_model=ResolutionRequest,
            response_model=ResolutionResponse,
            processor=None,
            is_exit_point=True,
            inject_fields=inject_resolution_fields
        )
    ]
    
    return FormChainEngine(
        chain_id="support_ticket",
        title="Customer Support Center",
        description="Get help with our AI-powered support system",
        steps=steps,
        theme="modern"
    )


# ==============================================================================
# Main function to demonstrate all examples
# ==============================================================================

async def main():
    """Demonstrate all form chain examples"""
    
    print("Form Chain Engine v3.0 - Examples")
    print("=" * 50)
    
    # Create all chains
    chains = {
        "1": ("Data Quality Check", create_data_quality_chain()),
        "2": ("Job Application", create_job_application_chain()),
        "3": ("Insurance Claim", create_insurance_claim_chain()),
        "4": ("Support Ticket", create_support_ticket_chain())
    }
    
    print("\nAvailable Form Chains:")
    for key, (name, _) in chains.items():
        print(f"{key}. {name}")
    
    # In a real application, you would integrate these with a web framework
    # For demonstration, we'll just show that they can be created
    
    # Example: Generate the entry form for data quality chain
    dq_chain = chains["1"][1]
    entry_form_html = dq_chain.generate_form_html("step_1")
    
    # Save to file for viewing
    with open("/var/www/ai_apps/playground/form_chain_example.html", "w") as f:
        f.write(entry_form_html)
    
    print("\nExample form saved to form_chain_example.html")
    print("Each chain demonstrates different features:")
    print("- Data Quality: Database analysis with dynamic field injection")
    print("- Job Application: Conditional routing based on department/experience")
    print("- Insurance Claim: Document upload and claim-type specific forms")
    print("- Support Ticket: AI-driven routing and diagnostic collection")


if __name__ == "__main__":
    asyncio.run(main())