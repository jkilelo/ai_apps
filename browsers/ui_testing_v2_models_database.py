"""
Database models for UI Testing Framework v2
SQLModel-based models for async database operations
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Any
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON, Relationship, Index
from sqlalchemy import DateTime, func, Text, Boolean, Integer, String


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExtractionStrategy(str, Enum):
    """Element extraction strategies"""
    AUTO = "auto"
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    VISUAL = "visual"
    AI_ASSISTED = "ai_assisted"


class TestType(str, Enum):
    """Test case types"""
    FUNCTIONAL = "functional"
    UI = "ui"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    VISUAL = "visual"


# Base model with common fields
class TimestampMixin(SQLModel):
    """Mixin for timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))


# Project and Session Models
class Project(SQLModel, table=True):
    """Project model for organizing test sessions"""
    
    __tablename__ = "projects"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))
    created_by: Optional[str] = Field(default=None, max_length=100)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    name: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(default=True)
    settings: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Relationships
    sessions: list["TestSession"] = Relationship(back_populates="project")
    
    __table_args__ = (
        Index("ix_projects_name_active", "name", "is_active"),
        {"extend_existing": True}
    )


class TestSession(SQLModel, table=True):
    """Test session model for tracking extraction and testing workflows"""
    
    __tablename__ = "test_sessions"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))
    created_by: Optional[str] = Field(default=None, max_length=100)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    name: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    url: str = Field(max_length=2048, index=True)
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    
    # Session configuration
    extraction_config: Optional[str] = Field(default=None, sa_column=Column(JSON))
    test_config: Optional[str] = Field(default=None, sa_column=Column(JSON))
    ai_config: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Progress tracking
    progress_percentage: int = Field(default=0, ge=0, le=100)
    current_step: Optional[str] = Field(default=None, max_length=100)
    
    # Results summary
    total_elements: int = Field(default=0, ge=0)
    total_test_cases: int = Field(default=0, ge=0)
    passed_tests: int = Field(default=0, ge=0)
    failed_tests: int = Field(default=0, ge=0)
    
    # Execution times
    started_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    completed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    execution_duration: Optional[int] = Field(default=None, description="Duration in seconds")
    
    # Error tracking
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    error_details: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Foreign keys
    project_id: Optional[UUID] = Field(default=None, foreign_key="projects.id", index=True)
    
    # Relationships
    project: Optional[Project] = Relationship(back_populates="sessions")
    extracted_elements: list["ExtractedElement"] = Relationship(back_populates="session")
    test_cases: list["TestCase"] = Relationship(back_populates="session")
    execution_results: list["ExecutionResult"] = Relationship(back_populates="session")
    
    __table_args__ = (
        Index("ix_sessions_url_status", "url", "status"),
        Index("ix_sessions_created_status", "created_at", "status"),
    )


# Element Extraction Models
class ExtractedElement(SQLModel, table=True):
    """Extracted UI elements from web pages"""
    
    __tablename__ = "extracted_elements"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))
    created_by: Optional[str] = Field(default=None, max_length=100)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Element identification
    tag_name: str = Field(max_length=50, index=True)
    element_type: str = Field(max_length=100, index=True)
    element_id: Optional[str] = Field(default=None, max_length=200)
    class_names: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Selectors
    css_selector: Optional[str] = Field(default=None, sa_column=Column(Text))
    xpath_selector: Optional[str] = Field(default=None, sa_column=Column(Text))
    playwright_selector: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Element properties
    text_content: Optional[str] = Field(default=None, sa_column=Column(Text))
    inner_html: Optional[str] = Field(default=None, sa_column=Column(Text))
    attributes: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Visual properties
    position: Optional[str] = Field(default=None, sa_column=Column(JSON))
    dimensions: Optional[str] = Field(default=None, sa_column=Column(JSON))
    is_visible: bool = Field(default=True)
    is_enabled: bool = Field(default=True)
    
    # Interaction properties
    is_clickable: bool = Field(default=False)
    is_form_field: bool = Field(default=False)
    is_link: bool = Field(default=False)
    is_button: bool = Field(default=False)
    
    # AI analysis results
    ai_description: Optional[str] = Field(default=None, sa_column=Column(Text))
    ai_purpose: Optional[str] = Field(default=None, sa_column=Column(Text))
    ai_test_suggestions: Optional[str] = Field(default=None, sa_column=Column(JSON))
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Extraction metadata
    extraction_strategy: ExtractionStrategy = Field(default=ExtractionStrategy.AUTO, index=True)
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    validation_status: Optional[str] = Field(default=None, max_length=50)
    
    # Foreign keys
    session_id: UUID = Field(foreign_key="test_sessions.id", index=True)
    
    # Relationships
    session: TestSession = Relationship(back_populates="extracted_elements")
    test_cases: list["TestCase"] = Relationship(back_populates="target_element")
    
    __table_args__ = (
        Index("ix_elements_session_type", "session_id", "element_type"),
        Index("ix_elements_clickable", "is_clickable", "session_id"),
    )


# Test Case Models
class TestCase(SQLModel, table=True):
    """Generated test cases"""
    
    __tablename__ = "test_cases"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))
    created_by: Optional[str] = Field(default=None, max_length=100)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Test identification
    name: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    test_type: TestType = Field(default=TestType.FUNCTIONAL, index=True)
    priority: int = Field(default=5, ge=1, le=10)  # 1=highest, 10=lowest
    
    # Test steps
    steps: Optional[str] = Field(default=None, sa_column=Column(JSON))
    expected_results: Optional[str] = Field(default=None, sa_column=Column(JSON))
    test_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Prerequisites and conditions
    preconditions: Optional[str] = Field(default=None, sa_column=Column(JSON))
    postconditions: Optional[str] = Field(default=None, sa_column=Column(JSON))
    tags: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Generated code
    generated_code: Optional[str] = Field(default=None, sa_column=Column(Text))
    framework: Optional[str] = Field(default=None, max_length=50)
    language: Optional[str] = Field(default=None, max_length=50)
    
    # AI generation metadata
    ai_prompt_used: Optional[str] = Field(default=None, sa_column=Column(Text))
    ai_provider: Optional[str] = Field(default=None, max_length=50)
    ai_model: Optional[str] = Field(default=None, max_length=100)
    generation_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Execution tracking
    is_executable: bool = Field(default=False)
    execution_count: int = Field(default=0, ge=0)
    last_execution_status: Optional[str] = Field(default=None, max_length=50)
    
    # Foreign keys
    session_id: UUID = Field(foreign_key="test_sessions.id", index=True)
    target_element_id: Optional[UUID] = Field(default=None, foreign_key="extracted_elements.id", index=True)
    
    # Relationships
    session: TestSession = Relationship(back_populates="test_cases")
    target_element: Optional[ExtractedElement] = Relationship(back_populates="test_cases")
    execution_results: list["ExecutionResult"] = Relationship(back_populates="test_case")
    
    __table_args__ = (
        Index("ix_testcases_session_type", "session_id", "test_type"),
        Index("ix_testcases_priority", "priority", "session_id"),
    )


# Execution Models
class ExecutionResult(SQLModel, table=True):
    """Test execution results"""
    
    __tablename__ = "execution_results"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))
    created_by: Optional[str] = Field(default=None, max_length=100)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Execution identification
    execution_id: str = Field(max_length=100, index=True)
    execution_name: Optional[str] = Field(default=None, max_length=200)
    
    # Execution configuration
    browser: str = Field(max_length=50, index=True)
    framework: str = Field(max_length=50)
    language: str = Field(max_length=50)
    parallel_execution: bool = Field(default=False)
    
    # Execution status
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    completed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    duration_seconds: Optional[float] = Field(default=None, ge=0)
    
    # Results summary
    total_tests: int = Field(default=0, ge=0)
    passed_tests: int = Field(default=0, ge=0)
    failed_tests: int = Field(default=0, ge=0)
    skipped_tests: int = Field(default=0, ge=0)
    
    # Execution details
    test_results: Optional[str] = Field(default=None, sa_column=Column(JSON))
    console_output: Optional[str] = Field(default=None, sa_column=Column(Text))
    error_output: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Screenshots and artifacts
    screenshots: Optional[str] = Field(default=None, sa_column=Column(JSON))  # File paths as JSON
    video_path: Optional[str] = Field(default=None, max_length=500)
    trace_path: Optional[str] = Field(default=None, max_length=500)
    
    # Performance metrics
    page_load_time: Optional[float] = Field(default=None, ge=0)
    network_requests: int = Field(default=0, ge=0)
    resource_usage: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Error tracking
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    error_traceback: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Foreign keys
    session_id: UUID = Field(foreign_key="test_sessions.id", index=True)
    test_case_id: Optional[UUID] = Field(default=None, foreign_key="test_cases.id", index=True)
    
    # Relationships
    session: TestSession = Relationship(back_populates="execution_results")
    test_case: Optional[TestCase] = Relationship(back_populates="execution_results")
    
    __table_args__ = (
        Index("ix_execution_session_status", "session_id", "status"),
        Index("ix_execution_started", "started_at", "status"),
    )


# Workflow State Models
class WorkflowState(SQLModel, table=True):
    """Workflow state tracking for complex operations"""
    
    __tablename__ = "workflow_states"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))
    created_by: Optional[str] = Field(default=None, max_length=100)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Workflow identification
    workflow_id: str = Field(max_length=100, index=True, unique=True)
    workflow_type: str = Field(max_length=50, index=True)
    workflow_name: str = Field(max_length=200)
    
    # State tracking
    current_step: str = Field(max_length=100, index=True)
    total_steps: int = Field(default=0, ge=0)
    completed_steps: int = Field(default=0, ge=0)
    
    # Status and progress
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    progress_percentage: int = Field(default=0, ge=0, le=100)
    
    # State data
    state_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    step_history: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    last_activity_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    completed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    
    # Error handling
    error_count: int = Field(default=0, ge=0)
    last_error: Optional[str] = Field(default=None, sa_column=Column(Text))
    retry_count: int = Field(default=0, ge=0)
    
    # Configuration
    config: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    __table_args__ = (
        Index("ix_workflow_type_status", "workflow_type", "status"),
        Index("ix_workflow_activity", "last_activity_at", "status"),
    )


# User Session Models (for UI state management)
class UserSession(SQLModel, table=True):
    """User session state for UI interactions"""
    
    __tablename__ = "user_sessions"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))
    created_by: Optional[str] = Field(default=None, max_length=100)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Session identification
    session_token: str = Field(max_length=255, index=True, unique=True)
    user_id: Optional[str] = Field(default=None, max_length=100, index=True)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Session data
    session_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    preferences: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Activity tracking
    last_activity_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    activity_count: int = Field(default=0, ge=0)
    
    # Session lifecycle
    expires_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    is_active: bool = Field(default=True, index=True)
    
    __table_args__ = (
        Index("ix_user_sessions_user_active", "user_id", "is_active"),
        Index("ix_user_sessions_expires", "expires_at", "is_active"),
    )


# Cache Models (for persistent caching)
class CacheEntry(SQLModel, table=True):
    """Persistent cache entries"""
    
    __tablename__ = "cache_entries"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))
    created_by: Optional[str] = Field(default=None, max_length=100)
    extra_data: Optional[str] = Field(default=None, sa_column=Column(JSON))
    
    # Cache key and namespace
    cache_key: str = Field(max_length=255, index=True)
    namespace: str = Field(max_length=100, index=True)
    
    # Cache data
    cache_value: Optional[str] = Field(default=None, sa_column=Column(JSON))
    value_type: str = Field(max_length=50)  # Type hint for deserialization
    
    # Expiration
    expires_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), index=True))
    ttl_seconds: Optional[int] = Field(default=None, ge=0)
    
    # Access tracking
    access_count: int = Field(default=0, ge=0)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    
    # Size tracking
    size_bytes: Optional[int] = Field(default=None, ge=0)
    
    __table_args__ = (
        Index("ix_cache_key_namespace", "cache_key", "namespace", unique=True),
        Index("ix_cache_expires", "expires_at"),
    )
