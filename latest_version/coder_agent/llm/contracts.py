#!/usr/bin/env python3
"""
LLM Integration Contracts - CODER v3.1 Compliant
Following STRICT Pydantic v2 contracts for ALL functions
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  
    GOOGLE = "google"


class LLMMessage(BaseModel):
    """Single message in conversation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    role: Literal["system", "user", "assistant"] = Field(
        ..., 
        description="Message role"
    )
    content: str = Field(
        ..., 
        min_length=1, 
        max_length=100000,
        description="Message content"
    )
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class LLMRequestInput(BaseModel):
    """Input contract for LLM requests"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM provider to use"
    )
    model: Optional[str] = Field(
        default=None,
        description="Specific model to use"
    )
    messages: List[LLMMessage] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Conversation messages"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=4000,
        ge=1,
        le=32000,
        description="Maximum response tokens"
    )
    timeout_seconds: int = Field(
        default=60,
        ge=1,
        le=300,
        description="Request timeout"
    )
    
    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v: List[LLMMessage]) -> List[LLMMessage]:
        # Must have at least one user message
        if not any(msg.role == "user" for msg in v):
            raise ValueError("At least one user message required")
        return v


class LLMResponseOutput(BaseModel):
    """Output contract for LLM responses"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    success: bool = Field(
        ...,
        description="Request success status"
    )
    content: Optional[str] = Field(
        default=None,
        description="Response content"
    )
    provider: LLMProvider = Field(
        ...,
        description="Provider used"
    )
    model: str = Field(
        ...,
        description="Model used"
    )
    tokens_used: int = Field(
        default=0,
        ge=0,
        description="Tokens consumed"
    )
    execution_time_ms: float = Field(
        ...,
        ge=0,
        description="Request duration in milliseconds"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response timestamp"
    )


class CodeGenerationInput(BaseModel):
    """Input contract for code generation requests"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    task_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="What code to generate"
    )
    language: str = Field(
        default="python",
        description="Programming language"
    )
    context: Optional[str] = Field(
        default=None,
        max_length=10000,
        description="Additional context or existing code"
    )
    requirements: List[str] = Field(
        default_factory=list,
        max_length=20,
        description="Specific requirements"
    )
    follow_coder_v3: bool = Field(
        default=True,
        description="Follow CODER v3.1 protocol"
    )
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        supported = ["python", "javascript", "typescript", "java", "go", "rust"]
        if v.lower() not in supported:
            raise ValueError(f"Language must be one of {supported}")
        return v.lower()


class CodeGenerationOutput(BaseModel):
    """Output contract for code generation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    success: bool = Field(
        ...,
        description="Generation success"
    )
    code: Optional[str] = Field(
        default=None,
        description="Generated code"
    )
    tests: Optional[str] = Field(
        default=None,
        description="Generated tests"
    )
    contracts: Optional[str] = Field(
        default=None,
        description="Pydantic contracts"
    )
    documentation: Optional[str] = Field(
        default=None,
        description="Generated documentation"
    )
    language: str = Field(
        ...,
        description="Language used"
    )
    tokens_used: int = Field(
        default=0,
        ge=0,
        description="Total tokens used"
    )
    execution_time_ms: float = Field(
        ...,
        ge=0,
        description="Generation time"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error if failed"
    )
    coder_v3_compliant: bool = Field(
        default=False,
        description="Whether output follows CODER v3.1"
    )