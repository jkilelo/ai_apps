"""
Pydantic v2 Models for Infrastructure Audit System
AI-First Infrastructure Management with Type Safety and Validation
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any, Literal, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
    computed_field,
    field_serializer,
    HttpUrl,
    conint,
    condecimal,
    constr,
)
from pydantic.json_schema import JsonSchemaValue
import json
from pathlib import Path
from uuid import uuid4


# ============================================
# Enums for Type Safety
# ============================================

class CostType(str, Enum):
    """Cost model types for components"""
    FREE = "free"
    FREEMIUM = "freemium"
    PAID = "paid"
    ENTERPRISE = "enterprise"
    USAGE_BASED = "usage_based"
    CUSTOM = "custom"


class ProfileType(str, Enum):
    """Infrastructure profile types"""
    POC = "poc"
    LOCAL = "local"
    OPENSOURCE = "opensource"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"
    HYBRID = "hybrid"


class DependencyType(str, Enum):
    """Component dependency relationship types"""
    REQUIRED = "required"
    OPTIONAL = "optional"
    ALTERNATIVE = "alternative"
    CONFLICTS = "conflicts"
    ENHANCES = "enhances"


class InclusionType(str, Enum):
    """Component inclusion in profiles"""
    REQUIRED = "required"
    OPTIONAL = "optional"
    EXCLUDED = "excluded"
    CONDITIONAL = "conditional"
    ALTERNATIVE = "alternative"


class AuditStatus(str, Enum):
    """Audit check status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    WARNING = "warning"


class Severity(str, Enum):
    """Validation rule severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CRITICAL = "critical"


class LLMProvider(str, Enum):
    """AI-first: Available LLM providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"
    BEDROCK = "bedrock"
    VERTEX_AI = "vertex_ai"
    LOCAL = "local"


class TargetScale(str, Enum):
    """Deployment scale targets"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    EDGE = "edge"
    GLOBAL = "global"


# ============================================
# Base Configuration
# ============================================

class BaseModelWithConfig(BaseModel):
    """Base model with standard configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            Path: lambda v: str(v),
        },
        json_schema_extra={
            "example": {}
        }
    )


# ============================================
# Core Models
# ============================================

class ResourceRequirements(BaseModel):
    """Hardware resource requirements"""
    min_cpu_cores: Optional[conint(ge=1)] = Field(None, description="Minimum CPU cores")
    min_ram_gb: Optional[conint(ge=1)] = Field(None, description="Minimum RAM in GB")
    min_storage_gb: Optional[conint(ge=1)] = Field(None, description="Minimum storage in GB")
    gpu_required: bool = Field(False, description="GPU requirement")
    gpu_vram_gb: Optional[conint(ge=1)] = Field(None, description="GPU VRAM in GB")
    network_bandwidth_mbps: Optional[conint(ge=1)] = Field(None, description="Network bandwidth in Mbps")

    @field_validator("gpu_vram_gb")
    @classmethod
    def validate_gpu_vram(cls, v: Optional[int], info) -> Optional[int]:
        if info.data.get("gpu_required") and v is None:
            raise ValueError("GPU VRAM must be specified if GPU is required")
        return v


class Layer(BaseModelWithConfig):
    """Infrastructure layer hierarchy"""
    id: Optional[int] = None
    code: constr(min_length=1, max_length=50) = Field(..., description="Unique layer code")
    name: constr(min_length=1, max_length=200) = Field(..., description="Layer name")
    order_index: int = Field(..., ge=0, description="Ordering index")
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_critical: bool = Field(False, description="Critical path layer")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    # Computed properties
    children: List[Layer] = Field(default_factory=list, exclude=True)

    @computed_field
    @property
    def level(self) -> int:
        """Compute hierarchy level"""
        return len(self.code.split(".")) if "." in self.code else 0

    @computed_field
    @property
    def is_root(self) -> bool:
        """Check if root layer"""
        return self.parent_id is None


class Category(BaseModelWithConfig):
    """Component categories within layers"""
    id: Optional[int] = None
    code: constr(min_length=1, max_length=50) = Field(..., description="Unique category code")
    name: constr(min_length=1, max_length=200) = Field(..., description="Category name")
    layer_id: int = Field(..., description="Parent layer ID")
    icon: Optional[str] = Field(None, max_length=50, description="Icon identifier")
    color: Optional[constr(pattern=r"^#[0-9A-Fa-f]{6}$")] = Field(None, description="Hex color")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)


class Component(BaseModelWithConfig):
    """Infrastructure component definition"""
    id: Optional[int] = None
    code: constr(min_length=1, max_length=100) = Field(..., description="Unique component code")
    name: constr(min_length=1, max_length=500) = Field(..., description="Component name")
    category_id: int = Field(..., description="Category ID")
    layer_id: int = Field(..., description="Layer ID")
    description: Optional[str] = None

    # Version information
    version_min: Optional[str] = Field(None, description="Minimum version")
    version_recommended: Optional[str] = Field(None, description="Recommended version")
    version_latest: Optional[str] = Field(None, description="Latest available version")

    # Component properties
    is_required: bool = Field(True, description="Required component")
    is_ai_component: bool = Field(False, description="AI/ML component")
    is_opensource: bool = Field(True, description="Open source component")
    license_type: Optional[str] = Field(None, description="License type")

    # Documentation
    documentation_url: Optional[HttpUrl] = None
    repository_url: Optional[HttpUrl] = None

    # Cost information
    cost_type: CostType = Field(CostType.FREE, description="Cost model")
    estimated_monthly_cost_min: condecimal(ge=0, decimal_places=2) = Field(Decimal("0.00"))
    estimated_monthly_cost_max: condecimal(ge=0, decimal_places=2) = Field(Decimal("0.00"))

    # Setup information
    setup_complexity: conint(ge=1, le=5) = Field(3, description="Setup complexity (1-5)")
    setup_time_minutes: conint(ge=0) = Field(60, description="Setup time in minutes")

    # Flexible fields
    resource_requirements: Optional[ResourceRequirements] = None
    tags: List[str] = Field(default_factory=list, description="Component tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def validate_cost_consistency(self) -> "Component":
        if self.cost_type != CostType.FREE:
            if self.estimated_monthly_cost_max <= 0:
                raise ValueError(f"Non-free components must have cost estimates")
        return self

    @computed_field
    @property
    def is_free(self) -> bool:
        """Check if component is free"""
        return self.cost_type == CostType.FREE

    @computed_field
    @property
    def average_monthly_cost(self) -> Decimal:
        """Calculate average monthly cost"""
        return (self.estimated_monthly_cost_min + self.estimated_monthly_cost_max) / 2

    @computed_field
    @property
    def setup_time_hours(self) -> float:
        """Setup time in hours"""
        return self.setup_time_minutes / 60.0


class ComponentDependency(BaseModelWithConfig):
    """Component dependency relationships"""
    id: Optional[int] = None
    component_id: int = Field(..., description="Component ID")
    depends_on_id: int = Field(..., description="Dependency component ID")
    dependency_type: DependencyType = Field(DependencyType.REQUIRED)
    condition: Optional[Dict[str, Any]] = Field(None, description="Conditional rules")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def validate_no_self_dependency(self) -> ComponentDependency:
        if self.component_id == self.depends_on_id:
            raise ValueError("Component cannot depend on itself")
        return self


class Alternative(BaseModelWithConfig):
    """Alternative component options"""
    id: Optional[int] = None
    primary_component_id: int = Field(..., description="Primary component ID")
    alternative_component_id: int = Field(..., description="Alternative component ID")
    preference_order: conint(ge=1) = Field(1, description="Preference order")
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)


# ============================================
# Profile Models
# ============================================

class Profile(BaseModelWithConfig):
    """Infrastructure profile definition"""
    id: Optional[int] = None
    code: constr(min_length=1, max_length=50) = Field(..., description="Unique profile code")
    name: constr(min_length=1, max_length=200) = Field(..., description="Profile name")
    description: Optional[str] = None
    profile_type: ProfileType = Field(..., description="Profile type")
    parent_profile_id: Optional[int] = Field(None, description="Parent profile for inheritance")

    # AI-first configuration
    is_ai_first: bool = Field(True, description="AI-first profile")
    default_llm_provider: LLMProvider = Field(LLMProvider.GEMINI, description="Default LLM provider")

    # Scale and capacity
    target_users: conint(ge=1) = Field(1, description="Target number of users")
    target_scale: TargetScale = Field(TargetScale.DEVELOPMENT, description="Target scale")

    # Budget constraints
    max_monthly_budget: Optional[condecimal(ge=0, decimal_places=2)] = None

    # Requirements
    requires_internet: bool = Field(True, description="Internet requirement")
    requires_gpu: bool = Field(False, description="GPU requirement")
    min_ram_gb: conint(ge=1) = Field(16, description="Minimum RAM in GB")
    min_storage_gb: conint(ge=1) = Field(100, description="Minimum storage in GB")
    min_cpu_cores: conint(ge=1) = Field(4, description="Minimum CPU cores")

    # Compliance and metadata
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Status
    is_active: bool = Field(True, description="Active profile")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    @field_validator("default_llm_provider")
    @classmethod
    def validate_ai_first(cls, v: LLMProvider, info) -> LLMProvider:
        if info.data.get("is_ai_first") and v == LLMProvider.LOCAL:
            # Ensure local LLM is properly configured
            metadata = info.data.get("metadata", {})
            if not metadata.get("local_llm_config"):
                raise ValueError("Local LLM requires configuration in metadata")
        return v

    @computed_field
    @property
    def is_opensource_only(self) -> bool:
        """Check if profile uses only open source components"""
        return self.profile_type == ProfileType.OPENSOURCE

    @computed_field
    @property
    def is_production_ready(self) -> bool:
        """Check if profile is production ready"""
        return self.target_scale in [TargetScale.PRODUCTION, TargetScale.GLOBAL]


class ProfileComponent(BaseModelWithConfig):
    """Component inclusion in profiles"""
    id: Optional[int] = None
    profile_id: int = Field(..., description="Profile ID")
    component_id: int = Field(..., description="Component ID")
    inclusion_type: InclusionType = Field(InclusionType.REQUIRED, description="Inclusion type")
    priority: conint(ge=1) = Field(1, description="Installation priority")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Profile-specific config")
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    @computed_field
    @property
    def is_mandatory(self) -> bool:
        """Check if component is mandatory"""
        return self.inclusion_type == InclusionType.REQUIRED


class ProfileRule(BaseModelWithConfig):
    """Profile business logic rules"""
    id: Optional[int] = None
    profile_id: int = Field(..., description="Profile ID")
    rule_type: Literal["inclusion", "exclusion", "validation", "constraint"] = Field(...)
    rule_name: constr(min_length=1, max_length=200) = Field(..., description="Rule name")
    rule_condition: Dict[str, Any] = Field(..., description="Rule condition logic")
    rule_action: Dict[str, Any] = Field(..., description="Rule action logic")
    priority: conint(ge=1) = Field(1, description="Rule priority")
    is_active: bool = Field(True, description="Active rule")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)


# ============================================
# Validation Models
# ============================================

class ValidationRule(BaseModelWithConfig):
    """Validation rule definition"""
    id: Optional[int] = None
    code: constr(min_length=1, max_length=100) = Field(..., description="Unique rule code")
    name: constr(min_length=1, max_length=200) = Field(..., description="Rule name")
    description: Optional[str] = None
    rule_type: Literal["dependency", "compatibility", "security", "performance", "compliance"] = Field(...)
    severity: Severity = Field(Severity.WARNING, description="Rule severity")
    expression: Dict[str, Any] = Field(..., description="Validation logic")
    error_message: Optional[str] = None
    is_active: bool = Field(True, description="Active rule")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    @computed_field
    @property
    def is_critical(self) -> bool:
        """Check if rule is critical"""
        return self.severity in [Severity.ERROR, Severity.CRITICAL]


# ============================================
# Audit Models
# ============================================

class AuditSession(BaseModelWithConfig):
    """Audit session tracking"""
    id: Optional[int] = None
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique session ID")
    profile_id: int = Field(..., description="Profile ID")
    user_email: Optional[str] = None
    environment: TargetScale = Field(TargetScale.DEVELOPMENT, description="Environment")

    # Timing
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    # Statistics
    total_components: int = Field(0, ge=0)
    passed_components: int = Field(0, ge=0)
    failed_components: int = Field(0, ge=0)
    skipped_components: int = Field(0, ge=0)

    # Status and results
    overall_status: Literal["pending", "running", "completed", "failed", "cancelled"] = Field("pending")
    report: Dict[str, Any] = Field(default_factory=dict, description="Audit report")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @computed_field
    @property
    def duration_seconds(self) -> Optional[int]:
        """Calculate audit duration"""
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return None

    @computed_field
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_components > 0:
            return (self.passed_components / self.total_components) * 100
        return 0.0

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if audit is complete"""
        return self.overall_status in ["completed", "failed", "cancelled"]


class AuditResult(BaseModelWithConfig):
    """Individual audit check result"""
    id: Optional[int] = None
    session_id: int = Field(..., description="Audit session ID")
    component_id: int = Field(..., description="Component ID")
    status: AuditStatus = Field(..., description="Check status")
    check_type: Optional[Literal["installation", "version", "configuration", "connectivity", "permission"]] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[conint(ge=0)] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    checked_at: datetime = Field(default_factory=datetime.now)

    @computed_field
    @property
    def is_success(self) -> bool:
        """Check if result is success"""
        return self.status == AuditStatus.PASSED


# ============================================
# Cost & Resource Models
# ============================================

class CostEstimate(BaseModelWithConfig):
    """Cost estimation for profiles and components"""
    id: Optional[int] = None
    profile_id: int = Field(..., description="Profile ID")
    component_id: Optional[int] = None
    cost_category: Literal["infrastructure", "api", "license", "support", "bandwidth"] = Field(...)
    provider: Optional[str] = None
    pricing_model: Literal["per_user", "per_request", "flat", "tiered", "usage"] = Field("flat")

    # Cost details
    base_cost: condecimal(ge=0, decimal_places=2) = Field(Decimal("0.00"))
    unit_cost: Optional[condecimal(ge=0, decimal_places=4)] = None
    unit_type: Optional[Literal["request", "gb", "hour", "month", "user"]] = None
    estimated_units: Optional[conint(ge=0)] = None
    total_monthly_cost: condecimal(ge=0, decimal_places=2) = Field(Decimal("0.00"))
    currency: constr(min_length=3, max_length=3) = Field("USD", description="Currency code")

    # Validity
    notes: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def calculate_total_cost(self) -> CostEstimate:
        """Calculate total monthly cost"""
        if self.unit_cost and self.estimated_units:
            self.total_monthly_cost = self.base_cost + (self.unit_cost * self.estimated_units)
        elif not self.total_monthly_cost:
            self.total_monthly_cost = self.base_cost
        return self


# ============================================
# Compatibility Models
# ============================================

class CompatibilityMatrix(BaseModelWithConfig):
    """Component compatibility tracking"""
    id: Optional[int] = None
    component_a_id: int = Field(..., description="First component ID")
    component_b_id: int = Field(..., description="Second component ID")
    compatibility_status: Literal["compatible", "incompatible", "conditional", "unknown"] = Field(...)

    # Version constraints
    min_version_a: Optional[str] = None
    max_version_a: Optional[str] = None
    min_version_b: Optional[str] = None
    max_version_b: Optional[str] = None

    # Additional information
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Compatibility conditions")
    notes: Optional[str] = None
    verified_date: Optional[date] = None

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    @computed_field
    @property
    def is_verified(self) -> bool:
        """Check if compatibility is verified"""
        return self.verified_date is not None


# ============================================
# Aggregation Models
# ============================================

class ProfileSummary(BaseModel):
    """Profile summary with statistics"""
    profile: Profile
    total_components: int = 0
    required_components: int = 0
    optional_components: int = 0

    # Cost breakdown
    free_components: int = 0
    paid_components: int = 0
    min_monthly_cost: Decimal = Decimal("0.00")
    max_monthly_cost: Decimal = Decimal("0.00")
    average_monthly_cost: Decimal = Decimal("0.00")

    # Complexity metrics
    total_setup_hours: float = 0.0
    average_complexity: float = 0.0

    # Requirements
    total_min_ram_gb: int = 0
    total_min_storage_gb: int = 0
    requires_gpu: bool = False

    # Compliance
    compliance_coverage: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)

    @computed_field
    @property
    def is_budget_friendly(self) -> bool:
        """Check if profile is within budget"""
        if self.profile.max_monthly_budget:
            return self.max_monthly_cost <= self.profile.max_monthly_budget
        return True

    @computed_field
    @property
    def readiness_score(self) -> float:
        """Calculate profile readiness score (0-100)"""
        score = 100.0

        # Deduct for missing requirements
        if self.missing_requirements:
            score -= len(self.missing_requirements) * 5

        # Deduct for high complexity
        if self.average_complexity > 4:
            score -= 10

        # Deduct for excessive setup time
        if self.total_setup_hours > 40:
            score -= 15

        return max(0.0, score)


class DependencyGraph(BaseModel):
    """Component dependency graph"""
    nodes: List[Component] = Field(default_factory=list)
    edges: List[ComponentDependency] = Field(default_factory=list)

    @computed_field
    @property
    def node_count(self) -> int:
        """Total number of nodes"""
        return len(self.nodes)

    @computed_field
    @property
    def edge_count(self) -> int:
        """Total number of edges"""
        return len(self.edges)

    def get_dependencies(self, component_id: int) -> List[int]:
        """Get direct dependencies of a component"""
        return [e.depends_on_id for e in self.edges if e.component_id == component_id]

    def get_dependents(self, component_id: int) -> List[int]:
        """Get components that depend on this one"""
        return [e.component_id for e in self.edges if e.depends_on_id == component_id]

    def topological_sort(self) -> List[int]:
        """Return components in installation order"""
        from collections import defaultdict, deque

        # Build adjacency list and in-degree count
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        for edge in self.edges:
            graph[edge.depends_on_id].append(edge.component_id)
            in_degree[edge.component_id] += 1

        # Find all nodes with no dependencies
        queue = deque([n.id for n in self.nodes if n.id and in_degree[n.id] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # Remove edge and update in-degrees
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != self.node_count:
            raise ValueError("Circular dependency detected")

        return result


# ============================================
# Export Configuration
# ============================================

__all__ = [
    # Enums
    "CostType",
    "ProfileType",
    "DependencyType",
    "InclusionType",
    "AuditStatus",
    "Severity",
    "LLMProvider",
    "TargetScale",

    # Core Models
    "ResourceRequirements",
    "Layer",
    "Category",
    "Component",
    "ComponentDependency",
    "Alternative",

    # Profile Models
    "Profile",
    "ProfileComponent",
    "ProfileRule",

    # Validation Models
    "ValidationRule",

    # Audit Models
    "AuditSession",
    "AuditResult",

    # Cost Models
    "CostEstimate",

    # Compatibility Models
    "CompatibilityMatrix",

    # Aggregation Models
    "ProfileSummary",
    "DependencyGraph",
]