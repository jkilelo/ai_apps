#!/usr/bin/env python3
"""
Infrastructure Users and Multi-Tenancy Models
Implements the hierarchical user structure for infrastructure management
Following 2025 cloud-native and DevOps best practices
"""

from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from pydantic import constr, conint, HttpUrl, EmailStr


# ============================================
# User Tier Enums
# ============================================

class UserTier(str, Enum):
    """User tier levels from individual to enterprise"""
    INDIVIDUAL = "individual"
    TEAM = "team"
    PROJECT = "project"
    ORGANIZATION = "organization"
    MULTI_TENANT = "multi_tenant"


class UserPersona(str, Enum):
    """Specific user personas in infrastructure"""
    # Individual personas
    INDIVIDUAL_DEVELOPER = "individual_developer"
    JUNIOR_DEVELOPER = "junior_developer"
    SENIOR_DEVELOPER = "senior_developer"
    DEVOPS_ENGINEER = "devops_engineer"
    PLATFORM_ENGINEER = "platform_engineer"
    SRE = "site_reliability_engineer"
    SECURITY_ENGINEER = "security_engineer"
    DATA_ENGINEER = "data_engineer"
    AI_ML_ENGINEER = "ai_ml_engineer"

    # Leadership personas
    TEAM_LEAD = "team_lead"
    ENGINEERING_MANAGER = "engineering_manager"
    PLATFORM_LEAD = "platform_lead"
    SECURITY_LEAD = "security_lead"
    CTO = "chief_technology_officer"

    # Specialized personas
    QA_ENGINEER = "qa_engineer"
    FINOPS_PRACTITIONER = "finops_practitioner"
    COMPLIANCE_SPECIALIST = "compliance_specialist"
    ARCHITECT = "architect"

    # Tenant personas
    TENANT_ADMIN = "tenant_admin"
    TENANT_DEVELOPER = "tenant_developer"
    SAAS_PROVIDER_ADMIN = "saas_provider_admin"


class AccessLevel(str, Enum):
    """Access levels for resources"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class EnvironmentType(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    SANDBOX = "sandbox"
    DISASTER_RECOVERY = "disaster_recovery"


class ComplianceFramework(str, Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOC2 = "soc2"
    ISO_27001 = "iso_27001"
    NIST = "nist"
    CIS = "cis"
    CCPA = "ccpa"


# ============================================
# Resource Quota Models
# ============================================

class ResourceQuota(BaseModel):
    """Resource quota definition for users/teams"""
    # Compute resources
    cpu_cores: Optional[int] = Field(None, ge=0)
    memory_gb: Optional[int] = Field(None, ge=0)
    gpu_units: Optional[int] = Field(0, ge=0)

    # Storage resources
    storage_gb: Optional[int] = Field(None, ge=0)
    object_storage_gb: Optional[int] = Field(None, ge=0)

    # Network resources
    bandwidth_mbps: Optional[int] = Field(None, ge=0)
    public_ips: Optional[int] = Field(0, ge=0)

    # API resources
    api_calls_per_minute: Optional[int] = Field(None, ge=0)
    api_calls_per_month: Optional[int] = Field(None, ge=0)

    # AI/ML resources
    llm_tokens_per_month: Optional[int] = Field(None, ge=0)
    training_hours_per_month: Optional[int] = Field(None, ge=0)

    # Cost limits
    max_monthly_spend: Optional[Decimal] = Field(None, ge=0)

    @computed_field
    @property
    def is_unlimited(self) -> bool:
        """Check if quota is unlimited"""
        return all(v is None for v in [
            self.cpu_cores, self.memory_gb, self.storage_gb,
            self.api_calls_per_month, self.max_monthly_spend
        ])


# ============================================
# Permission Models
# ============================================

class Permission(BaseModel):
    """Granular permission definition"""
    resource_type: str = Field(..., description="Type of resource")
    resource_pattern: str = Field(..., description="Resource name pattern (* for wildcard)")
    actions: List[str] = Field(..., description="Allowed actions")
    environments: List[EnvironmentType] = Field(default_factory=list)
    conditions: Optional[Dict[str, Any]] = Field(None, description="Additional conditions")
    expires_at: Optional[datetime] = Field(None, description="Permission expiry")

    @computed_field
    @property
    def is_expired(self) -> bool:
        """Check if permission has expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False


class Role(BaseModel):
    """Role definition with permissions"""
    name: constr(min_length=1, max_length=100) = Field(..., description="Role name")
    description: Optional[str] = None
    permissions: List[Permission] = Field(default_factory=list)
    inherits_from: Optional[List[str]] = Field(None, description="Parent roles")
    is_system_role: bool = Field(False, description="System-defined role")
    is_custom_role: bool = Field(False, description="Custom user-defined role")

    @field_validator("name")
    @classmethod
    def validate_role_name(cls, v: str) -> str:
        """Validate role name format"""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Role name must be alphanumeric with _ or -")
        return v.lower()


# ============================================
# User Models
# ============================================

class BaseUser(BaseModel):
    """Base user model"""
    id: Optional[str] = Field(None, description="User ID")
    email: Optional[str] = Field(None, description="User email")
    username: constr(min_length=3, max_length=50) = Field(..., description="Username")
    full_name: Optional[str] = None

    # Authentication
    auth_provider: str = Field("internal", description="Authentication provider")
    mfa_enabled: bool = Field(False, description="MFA enabled")
    last_login: Optional[datetime] = None

    # Status
    is_active: bool = Field(True)
    is_verified: bool = Field(False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IndividualUser(BaseUser):
    """Individual user with personal workspace"""
    persona: UserPersona = Field(..., description="User persona type")
    tier: UserTier = Field(UserTier.INDIVIDUAL)

    # Access control
    roles: List[str] = Field(default_factory=list)
    permissions: List[Permission] = Field(default_factory=list)

    # Resource quotas
    resource_quota: ResourceQuota = Field(default_factory=ResourceQuota)

    # Team membership
    teams: List[str] = Field(default_factory=list, description="Team IDs")
    primary_team: Optional[str] = None

    # Training & compliance
    completed_trainings: List[str] = Field(default_factory=list)
    compliance_certifications: List[ComplianceFramework] = Field(default_factory=list)
    next_training_due: Optional[datetime] = None

    # Development access
    git_username: Optional[str] = None
    ssh_keys: List[str] = Field(default_factory=list, description="SSH public keys")
    api_keys: List[Dict[str, Any]] = Field(default_factory=list)

    @computed_field
    @property
    def requires_training(self) -> bool:
        """Check if user needs training"""
        if self.next_training_due:
            return datetime.now() > self.next_training_due
        return len(self.completed_trainings) == 0

    @computed_field
    @property
    def access_level(self) -> str:
        """Determine overall access level"""
        if "admin" in self.roles or "owner" in self.roles:
            return "admin"
        elif "developer" in self.roles or "engineer" in self.roles:
            return "write"
        elif "viewer" in self.roles or "auditor" in self.roles:
            return "read"
        return "none"


# ============================================
# Team Models
# ============================================

class Team(BaseModel):
    """Team of users working together"""
    id: Optional[str] = None
    name: constr(min_length=1, max_length=100) = Field(..., description="Team name")
    description: Optional[str] = None
    tier: UserTier = Field(UserTier.TEAM)

    # Team composition
    lead_id: str = Field(..., description="Team lead user ID")
    member_ids: List[str] = Field(default_factory=list, description="Team member IDs")

    # Team type and focus
    team_type: str = Field(..., description="development, platform, security, data")
    primary_language: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)

    # Access and resources
    shared_roles: List[str] = Field(default_factory=list)
    team_quota: ResourceQuota = Field(default_factory=ResourceQuota)

    # Team workspace
    namespaces: List[str] = Field(default_factory=list)
    repositories: List[str] = Field(default_factory=list)
    shared_secrets: List[str] = Field(default_factory=list)

    # Communication
    slack_channel: Optional[str] = None
    email_list: Optional[str] = None
    on_call_rotation: Optional[List[str]] = None

    # Performance
    velocity_points: Optional[int] = Field(None, ge=0)
    sprint_duration_days: int = Field(14, ge=1, le=30)

    @computed_field
    @property
    def team_size(self) -> int:
        """Calculate team size"""
        return len(self.member_ids) + 1  # +1 for lead

    @model_validator(mode="after")
    def validate_team_size(self) -> "Team":
        """Validate team size constraints"""
        if self.team_size > 15:
            raise ValueError("Team size should not exceed 15 members (two-pizza rule)")
        return self


# ============================================
# Project Models
# ============================================

class Project(BaseModel):
    """Project scope for delivery"""
    id: Optional[str] = None
    name: constr(min_length=1, max_length=100) = Field(..., description="Project name")
    code: constr(min_length=1, max_length=50) = Field(..., description="Project code")
    description: Optional[str] = None
    tier: UserTier = Field(UserTier.PROJECT)

    # Project ownership
    owner_team_id: str = Field(..., description="Owning team ID")
    contributing_team_ids: List[str] = Field(default_factory=list)

    # Project type
    project_type: str = Field(..., description="microservice, monolith, data_platform, ml_model")
    architecture_pattern: Optional[str] = None

    # Resources
    environments: List[EnvironmentType] = Field(default_factory=list)
    project_quota: ResourceQuota = Field(default_factory=ResourceQuota)

    # Deployment
    deployment_strategy: str = Field("rolling", description="rolling, blue_green, canary")
    ci_cd_pipeline: Optional[str] = None
    deployment_frequency: Optional[str] = None  # daily, weekly, monthly

    # Monitoring
    slo_targets: Dict[str, float] = Field(default_factory=dict)
    alert_channels: List[str] = Field(default_factory=list)

    # Compliance
    compliance_frameworks: List[ComplianceFramework] = Field(default_factory=list)
    data_classification: Optional[str] = None  # public, internal, confidential, restricted

    # Status
    status: str = Field("active", description="planning, active, maintenance, archived")
    created_at: datetime = Field(default_factory=datetime.now)
    go_live_date: Optional[datetime] = None
    sunset_date: Optional[datetime] = None

    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if project has production environment"""
        return EnvironmentType.PRODUCTION in self.environments

    @computed_field
    @property
    def requires_compliance_audit(self) -> bool:
        """Check if project requires compliance audit"""
        return len(self.compliance_frameworks) > 0


# ============================================
# Organization Models
# ============================================

class Organization(BaseModel):
    """Organization containing multiple teams and projects"""
    id: Optional[str] = None
    name: constr(min_length=1, max_length=200) = Field(..., description="Organization name")
    domain: Optional[str] = Field(None, description="Organization domain")
    tier: UserTier = Field(UserTier.ORGANIZATION)

    # Organization structure
    org_type: str = Field(..., description="startup, smb, enterprise")
    industry: Optional[str] = None
    employee_count: Optional[int] = Field(None, ge=1)

    # Hierarchy
    divisions: List[str] = Field(default_factory=list)
    departments: List[str] = Field(default_factory=list)
    teams: List[str] = Field(default_factory=list, description="Team IDs")
    projects: List[str] = Field(default_factory=list, description="Project IDs")

    # Leadership
    cto_user_id: Optional[str] = None
    security_officer_id: Optional[str] = None
    platform_owner_id: Optional[str] = None

    # Infrastructure
    cloud_providers: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    availability_zones: List[str] = Field(default_factory=list)

    # Budget and costs
    annual_it_budget: Optional[Decimal] = Field(None, ge=0)
    monthly_cloud_spend: Optional[Decimal] = Field(None, ge=0)
    cost_center: Optional[str] = None

    # Compliance
    compliance_frameworks: List[ComplianceFramework] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    audit_frequency: Optional[str] = None  # monthly, quarterly, annually

    # Policies
    password_policy: Dict[str, Any] = Field(default_factory=dict)
    retention_policy_days: int = Field(90, ge=1)
    backup_policy: Dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def organization_size(self) -> str:
        """Categorize organization size"""
        if not self.employee_count:
            return "unknown"
        elif self.employee_count < 50:
            return "startup"
        elif self.employee_count < 500:
            return "smb"
        else:
            return "enterprise"

    @computed_field
    @property
    def is_multi_cloud(self) -> bool:
        """Check if using multiple cloud providers"""
        return len(self.cloud_providers) > 1


# ============================================
# Multi-Tenant Models
# ============================================

class Tenant(BaseModel):
    """Tenant in a multi-tenant system"""
    id: Optional[str] = None
    name: constr(min_length=1, max_length=200) = Field(..., description="Tenant name")
    code: constr(min_length=1, max_length=50) = Field(..., description="Tenant code")
    tier: UserTier = Field(UserTier.MULTI_TENANT)

    # Tenant details
    organization_id: Optional[str] = Field(None, description="Parent organization")
    tenant_type: str = Field("standard", description="trial, standard, premium, enterprise")

    # Subscription
    subscription_tier: str = Field(..., description="free, basic, professional, enterprise")
    subscription_start: datetime = Field(default_factory=datetime.now)
    subscription_end: Optional[datetime] = None
    trial_ends: Optional[datetime] = None

    # Isolation
    isolation_model: str = Field("shared", description="shared, dedicated, isolated")
    data_residency: Optional[str] = Field(None, description="Region for data storage")

    # Resources
    tenant_quota: ResourceQuota = Field(default_factory=ResourceQuota)
    dedicated_resources: Dict[str, Any] = Field(default_factory=dict)

    # Customization
    custom_domain: Optional[str] = None
    white_label: bool = Field(False)
    custom_branding: Dict[str, Any] = Field(default_factory=dict)
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

    # Users
    admin_users: List[str] = Field(default_factory=list)
    max_users: Optional[int] = Field(None, ge=1)
    active_users: int = Field(0, ge=0)

    # Compliance
    compliance_requirements: List[ComplianceFramework] = Field(default_factory=list)
    data_processing_agreement: bool = Field(False)

    # Status
    is_active: bool = Field(True)
    is_suspended: bool = Field(False)
    created_at: datetime = Field(default_factory=datetime.now)

    @computed_field
    @property
    def is_trial(self) -> bool:
        """Check if tenant is in trial"""
        if self.trial_ends:
            return datetime.now() < self.trial_ends
        return False

    @computed_field
    @property
    def days_until_renewal(self) -> Optional[int]:
        """Calculate days until subscription renewal"""
        if self.subscription_end:
            delta = self.subscription_end - datetime.now()
            return delta.days
        return None

    @model_validator(mode="after")
    def validate_user_limits(self) -> "Tenant":
        """Validate user count against limits"""
        if self.max_users and self.active_users > self.max_users:
            raise ValueError(f"Active users ({self.active_users}) exceeds limit ({self.max_users})")
        return self


# ============================================
# Access Control Models
# ============================================

class AccessRequest(BaseModel):
    """Request for elevated access"""
    id: Optional[str] = None
    requester_id: str = Field(..., description="User requesting access")

    # Request details
    resource_type: str = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="Specific resource ID")
    requested_permissions: List[str] = Field(..., description="Requested permissions")

    # Justification
    reason: str = Field(..., description="Reason for request")
    ticket_reference: Optional[str] = Field(None, description="Ticket/issue reference")

    # Time bounds
    requested_at: datetime = Field(default_factory=datetime.now)
    start_time: datetime = Field(..., description="When access should start")
    end_time: datetime = Field(..., description="When access should end")

    # Approval
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_status: str = Field("pending", description="pending, approved, denied, expired")
    denial_reason: Optional[str] = None

    # Audit
    access_logs: List[Dict[str, Any]] = Field(default_factory=list)

    @computed_field
    @property
    def duration_hours(self) -> float:
        """Calculate access duration in hours"""
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600

    @field_validator("end_time")
    @classmethod
    def validate_time_limit(cls, v: datetime, info) -> datetime:
        """Validate access duration doesn't exceed 30 days"""
        start_time = info.data.get("start_time")
        if start_time:
            max_duration = timedelta(days=30)
            if v - start_time > max_duration:
                raise ValueError("Access duration cannot exceed 30 days")
        return v


# ============================================
# Audit Models
# ============================================

class UserAuditLog(BaseModel):
    """Audit log for user actions"""
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    # User information
    user_id: str = Field(..., description="User who performed action")
    user_email: Optional[str] = None
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None

    # Action details
    action_type: str = Field(..., description="Type of action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="Specific resource ID")

    # Change details
    previous_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None

    # Result
    success: bool = Field(True)
    error_message: Optional[str] = None

    # Compliance
    compliance_relevant: bool = Field(False)
    compliance_frameworks: List[ComplianceFramework] = Field(default_factory=list)

    # Risk assessment
    risk_level: str = Field("low", description="low, medium, high, critical")
    suspicious_activity: bool = Field(False)

    @computed_field
    @property
    def requires_investigation(self) -> bool:
        """Check if audit log requires investigation"""
        return (
            self.risk_level in ["high", "critical"] or
            self.suspicious_activity or
            not self.success
        )


# ============================================
# User Management Service
# ============================================

class UserManagementService:
    """Service for managing users across all tiers"""

    def __init__(self):
        self.users: Dict[str, IndividualUser] = {}
        self.teams: Dict[str, Team] = {}
        self.projects: Dict[str, Project] = {}
        self.organizations: Dict[str, Organization] = {}
        self.tenants: Dict[str, Tenant] = {}
        self.audit_logs: List[UserAuditLog] = []

    def create_user(self, user: IndividualUser) -> str:
        """Create a new user"""
        user_id = f"user_{len(self.users) + 1}"
        user.id = user_id
        self.users[user_id] = user

        # Log the action
        self._log_action(
            user_id=user_id,
            action_type="user_created",
            resource_type="user",
            resource_id=user_id
        )

        return user_id

    def assign_user_to_team(self, user_id: str, team_id: str) -> bool:
        """Assign user to a team"""
        if user_id in self.users and team_id in self.teams:
            user = self.users[user_id]
            team = self.teams[team_id]

            if user_id not in team.member_ids:
                team.member_ids.append(user_id)

            if team_id not in user.teams:
                user.teams.append(team_id)

            self._log_action(
                user_id=user_id,
                action_type="team_assignment",
                resource_type="team",
                resource_id=team_id
            )

            return True
        return False

    def grant_permission(self, user_id: str, permission: Permission) -> bool:
        """Grant permission to a user"""
        if user_id in self.users:
            user = self.users[user_id]
            user.permissions.append(permission)

            self._log_action(
                user_id=user_id,
                action_type="permission_granted",
                resource_type="permission",
                new_value=permission.model_dump()
            )

            return True
        return False

    def check_access(self, user_id: str, resource: str, action: str, environment: EnvironmentType) -> bool:
        """Check if user has access to perform action on resource"""
        if user_id not in self.users:
            return False

        user = self.users[user_id]

        # Check direct permissions
        for permission in user.permissions:
            if permission.is_expired:
                continue

            if (resource.startswith(permission.resource_pattern.replace("*", "")) and
                action in permission.actions and
                (not permission.environments or environment in permission.environments)):
                return True

        # Check role-based permissions (would need role resolution)
        # This is simplified - in practice, would resolve role permissions
        if "admin" in user.roles:
            return True

        return False

    def get_user_quota(self, user_id: str) -> Optional[ResourceQuota]:
        """Get effective resource quota for a user"""
        if user_id not in self.users:
            return None

        user = self.users[user_id]
        effective_quota = user.resource_quota

        # Aggregate team quotas if user is part of teams
        # This is simplified - in practice, would have more complex logic
        for team_id in user.teams:
            if team_id in self.teams:
                team = self.teams[team_id]
                # Would merge quotas based on policy

        return effective_quota

    def audit_inactive_users(self, days: int = 30) -> List[str]:
        """Find users who haven't logged in for specified days"""
        inactive_users = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for user_id, user in self.users.items():
            if user.last_login and user.last_login < cutoff_date:
                inactive_users.append(user_id)

        return inactive_users

    def _log_action(self, user_id: str, action_type: str, resource_type: str,
                    resource_id: Optional[str] = None, **kwargs) -> None:
        """Log an action to audit trail"""
        log = UserAuditLog(
            user_id=user_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            **kwargs
        )
        self.audit_logs.append(log)

    def get_compliance_report(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Generate compliance report for a specific framework"""
        report = {
            "framework": framework.value,
            "timestamp": datetime.now().isoformat(),
            "users": {
                "total": len(self.users),
                "with_mfa": sum(1 for u in self.users.values() if u.mfa_enabled),
                "with_training": sum(1 for u in self.users.values() if not u.requires_training),
            },
            "organizations": {
                "compliant": sum(
                    1 for org in self.organizations.values()
                    if framework in org.compliance_frameworks
                )
            },
            "audit_logs": {
                "compliance_relevant": sum(
                    1 for log in self.audit_logs
                    if framework in log.compliance_frameworks
                )
            }
        }

        return report


# ============================================
# Usage Examples
# ============================================

def create_example_hierarchy():
    """Create an example user hierarchy"""
    service = UserManagementService()

    # Create individual users
    dev_user = IndividualUser(
        username="john.doe",
        email="john@example.com",
        persona=UserPersona.SENIOR_DEVELOPER,
        roles=["developer", "reviewer"],
        mfa_enabled=True,
        resource_quota=ResourceQuota(
            cpu_cores=4,
            memory_gb=16,
            storage_gb=100,
            api_calls_per_month=100000
        )
    )

    devops_user = IndividualUser(
        username="jane.smith",
        email="jane@example.com",
        persona=UserPersona.DEVOPS_ENGINEER,
        roles=["devops", "admin"],
        mfa_enabled=True,
        resource_quota=ResourceQuota(
            cpu_cores=8,
            memory_gb=32,
            storage_gb=500,
            max_monthly_spend=Decimal("1000")
        )
    )

    # Create users
    dev_id = service.create_user(dev_user)
    devops_id = service.create_user(devops_user)

    # Create a team
    platform_team = Team(
        name="Platform Team",
        description="Internal developer platform team",
        lead_id=devops_id,
        member_ids=[dev_id],
        team_type="platform",
        tech_stack=["kubernetes", "terraform", "python"],
        team_quota=ResourceQuota(
            cpu_cores=100,
            memory_gb=256,
            storage_gb=5000
        )
    )

    # Create a project
    idp_project = Project(
        name="Internal Developer Platform",
        code="IDP",
        owner_team_id="team_1",
        project_type="platform",
        environments=[EnvironmentType.DEVELOPMENT, EnvironmentType.PRODUCTION],
        compliance_frameworks=[ComplianceFramework.SOC2],
        project_quota=ResourceQuota(
            cpu_cores=50,
            memory_gb=128,
            storage_gb=2000
        )
    )

    # Create an organization
    tech_org = Organization(
        name="TechCorp",
        domain="techcorp.com",
        org_type="smb",
        employee_count=200,
        cloud_providers=["aws", "gcp"],
        compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.GDPR],
        annual_it_budget=Decimal("2000000")
    )

    # Create a tenant (for SaaS)
    customer_tenant = Tenant(
        name="Customer A",
        code="CUST_A",
        organization_id="org_1",
        subscription_tier="professional",
        isolation_model="dedicated",
        tenant_quota=ResourceQuota(
            cpu_cores=20,
            memory_gb=64,
            storage_gb=1000,
            api_calls_per_month=1000000
        ),
        max_users=50,
        active_users=35
    )

    return service


if __name__ == "__main__":
    # Demo the user hierarchy
    service = create_example_hierarchy()

    print("Infrastructure User Hierarchy System")
    print("=====================================")
    print(f"Total users: {len(service.users)}")
    print(f"Total audit logs: {len(service.audit_logs)}")

    # Check access
    user_id = list(service.users.keys())[0]
    has_access = service.check_access(
        user_id=user_id,
        resource="project/idp",
        action="read",
        environment=EnvironmentType.DEVELOPMENT
    )
    print(f"User {user_id} has access: {has_access}")

    # Find inactive users
    inactive = service.audit_inactive_users(days=30)
    print(f"Inactive users: {len(inactive)}")

    # Generate compliance report
    report = service.get_compliance_report(ComplianceFramework.SOC2)
    print(f"SOC2 Compliance: {report['users']['with_mfa']}/{report['users']['total']} users with MFA")