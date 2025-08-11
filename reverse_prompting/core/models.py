"""
Core Data Models for the Reverse Prompting Engine

This module defines the foundational data structures used throughout the
reverse prompting system, including prompts, code artifacts, evaluation
results, and state management.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator, ConfigDict
import json
import hashlib


class PromptStrategy(str, Enum):
    """Enumeration of available prompting strategies."""

    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    SELF_CONSISTENCY = "self_consistency"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    MIXTURE_OF_EXPERTS = "mixture_of_experts"
    CHAIN_OF_PROMPTS = "chain_of_prompts"
    REFLEXION = "reflexion"
    REACT = "react"
    DECOMPOSITION = "decomposition"
    PROGRESSIVE_HINT = "progressive_hint"
    STRUCTURED_OUTPUT = "structured_output"
    META_PROMPTING = "meta_prompting"
    CONSTITUTIONAL_AI = "constitutional_ai"
    PROMPT_CHAINING = "prompt_chaining"
    ROLE_PLAYING = "role_playing"
    PERSPECTIVE_TAKING = "perspective_taking"
    ANALOGICAL_REASONING = "analogical_reasoning"


class CodeLanguage(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    SHELL = "shell"
    R = "r"
    MATLAB = "matlab"


class ExecutionStatus(str, Enum):
    """Execution status of code."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    PERMISSION_ERROR = "permission_error"
    UNKNOWN = "unknown"


class SimilarityMetric(str, Enum):
    """Types of similarity metrics."""

    EXACT_MATCH = "exact_match"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    FUNCTIONAL = "functional"
    BEHAVIORAL = "behavioral"
    LEXICAL = "lexical"
    SYNTACTIC = "syntactic"
    EDIT_DISTANCE = "edit_distance"
    COSINE_SIMILARITY = "cosine_similarity"
    JACCARD = "jaccard"
    BLEU = "bleu"
    ROUGE = "rouge"


class VersionInfo(BaseModel):
    """Version information for tracking changes."""

    major: int = 1
    minor: int = 0
    patch: int = 0
    build: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.build:
            version += f"-{self.build}"
        return version

    def increment_patch(self) -> VersionInfo:
        """Create a new version with incremented patch number."""
        return VersionInfo(
            major=self.major,
            minor=self.minor,
            patch=self.patch + 1,
            build=self.build,
            timestamp=datetime.now(),
        )


class CodeArtifact(BaseModel):
    """Represents a piece of code with metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    language: CodeLanguage
    content: str
    description: Optional[str] = None
    file_path: Optional[Path] = None
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: VersionInfo = Field(default_factory=VersionInfo)
    created_at: datetime = Field(default_factory=datetime.now)
    hash: Optional[str] = None

    def __post_init__(self):
        """Generate hash after initialization."""
        if not self.hash:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the code content."""
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    @validator("content")
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Code content cannot be empty")
        return v

    def save_to_file(self, directory: Path) -> Path:
        """Save the code artifact to a file."""
        if not self.file_path:
            extension = self._get_file_extension()
            filename = f"{self.name}_{self.id.hex[:8]}.{extension}"
            self.file_path = directory / filename

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(self.content, encoding="utf-8")
        return self.file_path

    def _get_file_extension(self) -> str:
        """Get file extension based on language."""
        extensions = {
            CodeLanguage.PYTHON: "py",
            CodeLanguage.JAVASCRIPT: "js",
            CodeLanguage.TYPESCRIPT: "ts",
            CodeLanguage.JAVA: "java",
            CodeLanguage.CSHARP: "cs",
            CodeLanguage.CPP: "cpp",
            CodeLanguage.GO: "go",
            CodeLanguage.RUST: "rs",
            CodeLanguage.PHP: "php",
            CodeLanguage.RUBY: "rb",
            CodeLanguage.SWIFT: "swift",
            CodeLanguage.KOTLIN: "kt",
            CodeLanguage.SQL: "sql",
            CodeLanguage.HTML: "html",
            CodeLanguage.CSS: "css",
            CodeLanguage.SHELL: "sh",
            CodeLanguage.R: "r",
            CodeLanguage.MATLAB: "m",
        }
        return extensions.get(self.language, "txt")


class PromptTemplate(BaseModel):
    """Template for generating prompts using specific strategies."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    strategy: PromptStrategy
    template: str
    variables: List[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    examples: List[Dict[str, str]] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    output_format: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: VersionInfo = Field(default_factory=VersionInfo)
    created_at: datetime = Field(default_factory=datetime.now)

    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        rendered = self.template
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered

    def validate_variables(self, **kwargs) -> bool:
        """Validate that all required variables are provided."""
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        return True


class ExecutionResult(BaseModel):
    """Result of code execution."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    artifact_id: UUID
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    memory_usage: Optional[float] = None
    error_message: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

    @property
    def is_successful(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS and self.return_code == 0


class SimilarityScore(BaseModel):
    """Similarity score between two code artifacts."""

    metric: SimilarityMetric
    score: float = Field(ge=0.0, le=1.0)
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

    @validator("score")
    def score_range(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class EvaluationResult(BaseModel):
    """Comprehensive evaluation result comparing original and generated code."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    original_artifact_id: UUID
    generated_artifact_id: UUID
    prompt_id: UUID
    similarity_scores: List[SimilarityScore] = Field(default_factory=list)
    execution_comparison: Optional[Dict[str, Any]] = None
    functional_equivalence: bool = False
    performance_comparison: Dict[str, float] = Field(default_factory=dict)
    overall_score: float = Field(ge=0.0, le=1.0, default=0.0)
    success: bool = False
    notes: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)

    def add_similarity_score(self, metric: SimilarityMetric, score: float, **details):
        """Add a similarity score to the evaluation."""
        similarity_score = SimilarityScore(metric=metric, score=score, details=details)
        self.similarity_scores.append(similarity_score)

    def calculate_overall_score(
        self, weights: Optional[Dict[SimilarityMetric, float]] = None
    ) -> float:
        """Calculate overall score based on weighted similarity scores."""
        if not self.similarity_scores:
            return 0.0

        if weights is None:
            # Default equal weights
            weights = {score.metric: 1.0 for score in self.similarity_scores}

        total_weight = 0.0
        weighted_sum = 0.0

        for sim_score in self.similarity_scores:
            weight = weights.get(sim_score.metric, 1.0)
            weighted_sum += sim_score.score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        self.overall_score = weighted_sum / total_weight
        return self.overall_score


class PromptGeneration(BaseModel):
    """A generated prompt for creating code."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    template_id: UUID
    strategy: PromptStrategy
    content: str
    system_prompt: Optional[str] = None
    target_artifact_id: UUID
    variables: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: VersionInfo = Field(default_factory=VersionInfo)
    timestamp: datetime = Field(default_factory=datetime.now)


class ReversePromptingSession(BaseModel):
    """A complete reverse prompting session."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    original_artifact: CodeArtifact
    target_description: str
    strategies_used: List[PromptStrategy] = Field(default_factory=list)
    generated_prompts: List[PromptGeneration] = Field(default_factory=list)
    generated_artifacts: List[CodeArtifact] = Field(default_factory=list)
    evaluations: List[EvaluationResult] = Field(default_factory=list)
    best_result: Optional[EvaluationResult] = None
    session_config: Dict[str, Any] = Field(default_factory=dict)
    version: VersionInfo = Field(default_factory=VersionInfo)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_evaluation(self, evaluation: EvaluationResult):
        """Add an evaluation result and update best result if necessary."""
        self.evaluations.append(evaluation)

        if (
            self.best_result is None
            or evaluation.overall_score > self.best_result.overall_score
        ):
            self.best_result = evaluation

        self.updated_at = datetime.now()

    def get_success_rate(self) -> float:
        """Calculate the success rate of evaluations."""
        if not self.evaluations:
            return 0.0

        successful = sum(1 for eval_result in self.evaluations if eval_result.success)
        return successful / len(self.evaluations)


class StateSnapshot(BaseModel):
    """Snapshot of the system state at a particular point in time."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    state_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    checksum: str
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def create(
        cls, session_id: UUID, state_type: str, data: Dict[str, Any]
    ) -> StateSnapshot:
        """Create a state snapshot with automatic checksum."""
        checksum = hashlib.sha256(
            json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

        return cls(
            session_id=session_id, state_type=state_type, data=data, checksum=checksum
        )


# Type aliases for commonly used types
T = TypeVar("T")
PromptFunction = Callable[[CodeArtifact], str]
EvaluationFunction = Callable[[CodeArtifact, CodeArtifact], EvaluationResult]
StrategyFunction = Callable[[CodeArtifact, Dict[str, Any]], PromptGeneration]


@dataclass
class EngineConfig:
    """Configuration for the reverse prompting engine."""

    max_iterations: int = 10
    timeout_seconds: int = 300
    parallel_strategies: int = 3
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    auto_save_interval: int = 60
    similarity_threshold: float = 0.8
    success_threshold: float = 0.9
    max_prompt_length: int = 8192
    enable_evolution: bool = True
    evolution_generations: int = 5
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    population_size: int = 20
    enable_monitoring: bool = True
    log_level: str = "INFO"
    storage_backend: str = "sqlite"
    storage_path: str = "./sessions"
    storage_config: Dict[str, Any] = field(default_factory=dict)
    llm_providers: List[str] = field(default_factory=lambda: ["openai", "anthropic"])
    default_provider: str = "openai"
    llm_rate_limit: int = 100  # Added llm_rate_limit field
    retry_attempts: int = 3
    retry_delay: float = 1.0


# Export all models
__all__ = [
    "PromptStrategy",
    "CodeLanguage",
    "ExecutionStatus",
    "SimilarityMetric",
    "VersionInfo",
    "CodeArtifact",
    "PromptTemplate",
    "ExecutionResult",
    "SimilarityScore",
    "EvaluationResult",
    "PromptGeneration",
    "ReversePromptingSession",
    "StateSnapshot",
    "EngineConfig",
    "PromptFunction",
    "EvaluationFunction",
    "StrategyFunction",
]
