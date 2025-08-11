#!/usr/bin/env python3
"""
Base Contracts for CODER Agent - Following CODER v3.1 Principles
Every function has Pydantic v2 input/output contracts
"""

from typing import List, Dict, Any, Optional, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
import uuid


class StrictContract(BaseModel):
    """Base contract with strict validation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=False,
        extra='forbid'  # No extra fields allowed
    )


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ToolType(str, Enum):
    """Available tool types"""
    READ = "read"
    WRITE = "write"
    EDIT = "edit"
    BASH = "bash"
    GREP = "grep"
    SEARCH = "search"
    TEST = "test"
    VALIDATE = "validate"
    CODE_GENERATE = "code_generate"  # Uses real LLM for code generation


# Request/Response Contracts

class AgentRequest(StrictContract):
    """Input contract for agent requests"""
    task: str = Field(..., min_length=1, description="Task description")
    project_path: Optional[str] = Field(None, description="Project root path")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    constraints: Optional[List[str]] = Field(default_factory=list, description="Task constraints")
    timeout_seconds: int = Field(3600, ge=60, le=86400, description="Task timeout")
    require_tests: bool = Field(True, description="Require tests for code changes")
    platform: Literal["windows", "linux", "mac", "any"] = Field("any", description="Target platform")


class AgentResponse(StrictContract):
    """Output contract for agent responses"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    success: bool = Field(..., description="Whether task completed successfully")
    result: Optional[Any] = Field(None, description="Task result")
    changes: List[Dict[str, Any]] = Field(default_factory=list, description="Files changed")
    tests_run: List[Dict[str, Any]] = Field(default_factory=list, description="Tests executed")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Warnings generated")
    duration_seconds: float = Field(..., ge=0, description="Execution duration")
    tokens_used: int = Field(0, ge=0, description="Total tokens consumed")


# Task Planning Contracts (B.R.E.A.K. Methodology)

class TodoItem(StrictContract):
    """Individual TODO item following B.R.E.A.K."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., min_length=1, description="Task description")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current status")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    dependencies: List[str] = Field(default_factory=list, description="Dependent task IDs")
    estimated_tokens: int = Field(0, ge=0, description="Estimated token usage")
    actual_tokens: Optional[int] = Field(None, ge=0, description="Actual tokens used")
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    error: Optional[str] = Field(None, description="Error if failed")
    
    @field_validator('dependencies')
    def validate_dependencies(cls, v):
        """Ensure no circular dependencies"""
        if len(v) != len(set(v)):
            raise ValueError("Duplicate dependencies found")
        return v


class TaskPlan(StrictContract):
    """Complete task plan using B.R.E.A.K. methodology"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    objective: str = Field(..., min_length=1, description="Overall objective")
    tasks: List[TodoItem] = Field(..., min_length=1, description="Planned tasks")
    total_estimated_tokens: int = Field(0, ge=0, description="Total estimated tokens")
    max_parallel_tasks: int = Field(1, ge=1, le=10, description="Max parallel execution")
    
    def get_next_tasks(self) -> List[TodoItem]:
        """Get next executable tasks"""
        pending = [t for t in self.tasks if t.status == TaskStatus.PENDING]
        executable = []
        for task in pending:
            deps_complete = all(
                any(t.id == dep_id and t.status == TaskStatus.COMPLETED 
                    for t in self.tasks)
                for dep_id in task.dependencies
            )
            if deps_complete:
                executable.append(task)
        return executable[:self.max_parallel_tasks]


# Tool Execution Contracts

class ToolCall(StrictContract):
    """Contract for tool invocation"""
    tool: ToolType = Field(..., description="Tool to invoke")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    timeout: int = Field(120, ge=1, le=600, description="Timeout in seconds")
    retry_on_failure: bool = Field(True, description="Retry if fails")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    estimated_tokens: int = Field(100, ge=0, description="Estimated tokens for operation")


class ToolResult(StrictContract):
    """Contract for tool execution result"""
    tool: ToolType = Field(..., description="Tool that was invoked")
    success: bool = Field(..., description="Execution success")
    output: Optional[Any] = Field(None, description="Tool output")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: int = Field(..., ge=0, description="Execution duration in ms")
    retries: int = Field(0, ge=0, description="Number of retries")
    tokens_used: int = Field(0, ge=0, description="Tokens consumed")


# Context Management Contracts

class ContextWindow(StrictContract):
    """Contract for context window management"""
    total_tokens: int = Field(200000, ge=1000, description="Total available tokens")
    used_tokens: int = Field(0, ge=0, description="Currently used tokens")
    reserved_tokens: int = Field(10000, ge=0, description="Reserved for response")
    
    @property
    def available_tokens(self) -> int:
        return self.total_tokens - self.used_tokens - self.reserved_tokens
    
    @property
    def usage_percentage(self) -> float:
        return (self.used_tokens / self.total_tokens) * 100
    
    def can_add(self, tokens: int) -> bool:
        return (self.used_tokens + tokens) < (self.total_tokens - self.reserved_tokens)


class ContextItem(StrictContract):
    """Individual context item"""
    content: str = Field(..., description="Content")
    content_type: str = Field(..., description="Type of content")
    tokens: int = Field(..., ge=0, description="Token count")
    priority: int = Field(5, ge=1, le=10, description="Priority (1=highest)")
    can_summarize: bool = Field(True, description="Can be summarized")
    summary: Optional[str] = Field(None, description="Summarized version")


# Validation Contracts

class ValidationRule(StrictContract):
    """Contract for validation rules"""
    name: str = Field(..., min_length=1, description="Rule name")
    description: str = Field(..., description="What this validates")
    validator: str = Field(..., description="Validation function name")
    severity: Literal["error", "warning", "info"] = Field("error", description="Severity")
    active: bool = Field(True, description="Whether rule is active")


class ValidationResult(StrictContract):
    """Contract for validation results"""
    passed: bool = Field(..., description="Overall validation passed")
    rules_checked: int = Field(..., ge=0, description="Number of rules checked")
    failures: List[Dict[str, Any]] = Field(default_factory=list, description="Failed validations")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    duration_ms: int = Field(..., ge=0, description="Validation duration")


# Pre-flight Contracts

class EnvironmentCheck(StrictContract):
    """Contract for environment checks"""
    check_name: str = Field(..., description="Check name")
    passed: bool = Field(..., description="Check passed")
    message: str = Field(..., description="Check result message")
    severity: Literal["critical", "warning", "info"] = Field(..., description="Severity")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class PreflightResult(StrictContract):
    """Contract for pre-flight check results"""
    all_passed: bool = Field(..., description="All checks passed")
    checks: List[EnvironmentCheck] = Field(..., description="Individual checks")
    can_proceed: bool = Field(..., description="Safe to proceed")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    errors: List[str] = Field(default_factory=list, description="Errors")


# LLM Contracts

class LLMConfig(StrictContract):
    """Contract for LLM configuration"""
    provider: Literal["openai", "anthropic", "local"] = Field(..., description="LLM provider")
    model: str = Field(..., description="Model identifier")
    api_key: Optional[str] = Field(None, description="API key")
    base_url: Optional[str] = Field(None, description="API base URL")
    temperature: float = Field(0.7, ge=0, le=2, description="Temperature")
    max_tokens: int = Field(4000, ge=1, description="Max tokens per request")
    timeout: int = Field(60, ge=1, description="Request timeout")


class LLMRequest(StrictContract):
    """Contract for LLM requests"""
    prompt: str = Field(..., min_length=1, description="Prompt text")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Override temperature")
    max_tokens: Optional[int] = Field(None, ge=1, description="Override max tokens")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Available tools")


class LLMResponse(StrictContract):
    """Contract for LLM responses"""
    content: str = Field(..., description="Response content")
    tokens_used: int = Field(..., ge=0, description="Tokens consumed")
    model: str = Field(..., description="Model used")
    duration_ms: int = Field(..., ge=0, description="Response time")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls requested")