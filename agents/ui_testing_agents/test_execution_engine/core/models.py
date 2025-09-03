"""
Unified Data Models for Nexus Executor
Combines and enhances models from all existing modules
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import hashlib
import json


# ============================================================================
# ENUMERATIONS
# ============================================================================

class ExecutionMode(Enum):
    """Execution modes for code"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    CONTAINERIZED = "containerized"
    ISOLATED = "isolated"
    BATCH = "batch"
    STREAM = "stream"
    INTERACTIVE = "interactive"


class ExecutionStatus(Enum):
    """Unified execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    PREPARING = "preparing"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    SECURITY_VIOLATION = "security_violation"
    RESOURCE_LIMIT = "resource_limit"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"


class CodeLanguage(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    C = "c"
    RUST = "rust"
    GO = "go"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    R = "r"
    JULIA = "julia"
    SHELL = "shell"
    SQL = "sql"


class SecurityLevel(Enum):
    """Security levels for execution"""
    NONE = 0  # No restrictions (dangerous!)
    MINIMAL = 1  # Basic restrictions
    STANDARD = 2  # Standard sandbox
    STRICT = 3  # Maximum security
    PARANOID = 4  # Ultra-restrictive


class ReportFormat(Enum):
    """Report format options"""
    HTML = "html"
    JSON = "json"
    XML = "xml"
    JUNIT = "junit"
    MARKDOWN = "markdown"
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    DASHBOARD = "dashboard"


class ResourceType(Enum):
    """System resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    THREADS = "threads"
    PROCESSES = "processes"
    FILE_DESCRIPTORS = "file_descriptors"


class MetricType(Enum):
    """Performance metric types"""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CACHE_HITS = "cache_hits"
    QUEUE_DEPTH = "queue_depth"
    THROUGHPUT = "throughput"
    LATENCY = "latency"


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================

@dataclass
class ResourceLimits:
    """Resource limits for execution"""
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    max_disk_mb: int = 100
    max_network_kb: int = 1024
    max_threads: int = 10
    max_processes: int = 5
    max_file_descriptors: int = 100
    max_execution_time: int = 30
    max_output_size_kb: int = 1024
    gpu_memory_mb: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items() 
            if v is not None
        }


@dataclass
class SecurityConfig:
    """Security configuration"""
    level: SecurityLevel = SecurityLevel.STANDARD
    allowed_imports: List[str] = field(default_factory=list)
    blocked_imports: List[str] = field(default_factory=lambda: [
        "os", "subprocess", "sys", "eval", "exec", "__import__"
    ])
    allowed_builtins: List[str] = field(default_factory=list)
    blocked_builtins: List[str] = field(default_factory=lambda: [
        "eval", "exec", "compile", "open", "__import__"
    ])
    allowed_file_paths: List[Path] = field(default_factory=list)
    network_allowed: bool = False
    filesystem_allowed: bool = False
    enable_audit_log: bool = True
    encryption_enabled: bool = False
    
    def is_import_allowed(self, module: str) -> bool:
        """Check if an import is allowed"""
        if self.level == SecurityLevel.NONE:
            return True
        if module in self.blocked_imports:
            return False
        if self.allowed_imports and module not in self.allowed_imports:
            return False
        return True


@dataclass
class ExecutionConfig:
    """Complete execution configuration"""
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    security: SecurityConfig = field(default_factory=SecurityConfig)
    resources: ResourceLimits = field(default_factory=ResourceLimits)
    language: CodeLanguage = CodeLanguage.PYTHON
    parallel_workers: int = 4
    retry_attempts: int = 3
    retry_delay: float = 1.0
    fail_fast: bool = False
    capture_output: bool = True
    capture_metrics: bool = True
    enable_profiling: bool = False
    enable_tracing: bool = False
    cache_results: bool = True
    verbose: bool = False
    debug: bool = False
    environment_variables: Dict[str, str] = field(default_factory=dict)
    working_directory: Optional[Path] = None
    output_directory: Path = field(default_factory=lambda: Path("./output"))
    temp_directory: Optional[Path] = None
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        data = {
            "mode": self.mode.value,
            "security_level": self.security.level.value,
            "language": self.language.value,
            "resources": self.resources.to_dict(),
            "parallel_workers": self.parallel_workers,
            "retry_attempts": self.retry_attempts,
            "cache_results": self.cache_results,
        }
        return json.dumps(data, indent=2)


# ============================================================================
# EXECUTION MODELS
# ============================================================================

@dataclass
class CodeArtifact:
    """Represents a piece of code to execute"""
    id: str = field(default_factory=lambda: hashlib.md5(
        str(datetime.now()).encode()).hexdigest()[:8])
    content: str = ""
    language: CodeLanguage = CodeLanguage.PYTHON
    filename: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    hash: Optional[str] = None
    
    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.sha256(self.content.encode()).hexdigest()
    
    def get_lines(self) -> List[str]:
        """Get code lines"""
        return self.content.splitlines()
    
    def get_size(self) -> int:
        """Get code size in bytes"""
        return len(self.content.encode())


@dataclass
class ExecutionRequest:
    """Request to execute code"""
    artifact: CodeArtifact
    config: ExecutionConfig = field(default_factory=ExecutionConfig)
    priority: int = 5  # 1-10, higher is more priority
    tags: List[str] = field(default_factory=list)
    callback_url: Optional[str] = None
    timeout_override: Optional[int] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    parent_job_id: Optional[str] = None
    
    def get_cache_key(self) -> str:
        """Generate cache key for this request"""
        key_parts = [
            self.artifact.hash,
            self.config.mode.value,
            self.config.language.value,
            str(self.config.security.level.value)
        ]
        return hashlib.md5("_".join(key_parts).encode()).hexdigest()


@dataclass
class ExecutionResult:
    """Result of code execution"""
    request_id: str
    status: ExecutionStatus
    artifact_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    return_value: Any = None
    
    # Metrics
    metrics: Dict[MetricType, float] = field(default_factory=dict)
    resource_usage: Dict[ResourceType, float] = field(default_factory=dict)
    
    # Additional data
    logs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    artifacts: List[Path] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        """Check if execution was successful"""
        return self.status == ExecutionStatus.SUCCESS
    
    @property
    def is_complete(self) -> bool:
        """Check if execution is complete"""
        return self.status in [
            ExecutionStatus.SUCCESS,
            ExecutionStatus.FAILED,
            ExecutionStatus.ERROR,
            ExecutionStatus.TIMEOUT,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.SECURITY_VIOLATION
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "artifact_id": self.artifact_id,
            "duration_ms": self.duration_ms,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "error_message": self.error_message,
            "metrics": {k.value: v for k, v in self.metrics.items()},
            "resource_usage": {k.value: v for k, v in self.resource_usage.items()},
            "is_success": self.is_success,
        }


# ============================================================================
# MONITORING MODELS
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Performance metrics for execution"""
    execution_time_ms: float = 0.0
    queue_time_ms: float = 0.0
    preparation_time_ms: float = 0.0
    
    cpu_time_ms: float = 0.0
    cpu_percent_avg: float = 0.0
    cpu_percent_max: float = 0.0
    
    memory_mb_avg: float = 0.0
    memory_mb_max: float = 0.0
    memory_allocations: int = 0
    
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    disk_operations: int = 0
    
    network_sent_bytes: int = 0
    network_recv_bytes: int = 0
    network_connections: int = 0
    
    cache_hits: int = 0
    cache_misses: int = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "total_time_ms": self.execution_time_ms + self.queue_time_ms + self.preparation_time_ms,
            "cpu_efficiency": self.cpu_time_ms / max(self.execution_time_ms, 1) * 100,
            "memory_efficiency": (self.memory_mb_avg / max(self.memory_mb_max, 1)) * 100,
            "cache_hit_rate": (self.cache_hits / max(self.cache_hits + self.cache_misses, 1)) * 100,
        }


@dataclass
class SecurityAuditLog:
    """Security audit log entry"""
    timestamp: datetime
    event_type: str
    severity: str  # INFO, WARNING, ERROR, CRITICAL
    description: str
    artifact_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    blocked_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionReport:
    """Comprehensive execution report"""
    summary: Dict[str, Any]
    results: List[ExecutionResult]
    metrics: PerformanceMetrics
    security_logs: List[SecurityAuditLog]
    generated_at: datetime = field(default_factory=datetime.now)
    format: ReportFormat = ReportFormat.JSON
    
    def to_format(self, format: ReportFormat) -> Union[str, bytes]:
        """Convert report to specified format"""
        if format == ReportFormat.JSON:
            return json.dumps({
                "summary": self.summary,
                "results": [r.to_dict() for r in self.results],
                "metrics": self.metrics.__dict__,
                "generated_at": self.generated_at.isoformat()
            }, indent=2)
        # Other formats would be implemented here
        return str(self.summary)


# ============================================================================
# INTELLIGENT FEATURES MODELS
# ============================================================================

@dataclass
class CodeAnalysis:
    """Code analysis results"""
    artifact_id: str
    language: CodeLanguage
    lines_of_code: int
    complexity: Dict[str, float]  # cyclomatic, cognitive, etc.
    imports: List[str]
    functions: List[str]
    classes: List[str]
    potential_issues: List[Dict[str, Any]]
    security_risks: List[Dict[str, Any]]
    performance_hints: List[str]
    test_coverage: Optional[float] = None
    dependencies_graph: Optional[Dict[str, List[str]]] = None


@dataclass
class OptimizationSuggestion:
    """Code optimization suggestion"""
    type: str  # performance, memory, readability, security
    severity: str  # low, medium, high, critical
    line_range: tuple[int, int]
    description: str
    suggested_code: Optional[str] = None
    estimated_improvement: Optional[float] = None
    references: List[str] = field(default_factory=list)


@dataclass
class TestCase:
    """Generated test case"""
    name: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Any
    test_type: str  # unit, integration, property, fuzz
    code: str
    coverage_target: Optional[str] = None
    priority: int = 5


# ============================================================================
# ORCHESTRATION MODELS
# ============================================================================

@dataclass 
class ExecutionJob:
    """Job for execution queue"""
    request: ExecutionRequest
    id: str = field(default_factory=lambda: hashlib.md5(
        str(datetime.now()).encode()).hexdigest())
    status: ExecutionStatus = ExecutionStatus.PENDING
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    assigned_worker: Optional[str] = None
    result: Optional[ExecutionResult] = None
    
    def __lt__(self, other):
        """For priority queue ordering"""
        return self.priority > other.priority


@dataclass
class WorkerStatus:
    """Status of an execution worker"""
    id: str
    status: str  # idle, busy, offline
    current_job: Optional[str] = None
    jobs_completed: int = 0
    jobs_failed: int = 0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    resources: ResourceLimits = field(default_factory=ResourceLimits)
    capabilities: List[CodeLanguage] = field(default_factory=list)


@dataclass
class ClusterStatus:
    """Status of execution cluster"""
    workers: List[WorkerStatus]
    queue_depth: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    avg_execution_time_ms: float
    avg_queue_time_ms: float
    resource_utilization: Dict[ResourceType, float]
    
    def get_available_workers(self) -> List[WorkerStatus]:
        """Get available workers"""
        return [w for w in self.workers if w.status == "idle"]
    
    def get_health_score(self) -> float:
        """Calculate cluster health score (0-100)"""
        factors = []
        
        # Worker availability
        if self.workers:
            available_ratio = len(self.get_available_workers()) / len(self.workers)
            factors.append(available_ratio * 30)
        
        # Success rate
        total_jobs = self.completed_jobs + self.failed_jobs
        if total_jobs > 0:
            success_rate = self.completed_jobs / total_jobs
            factors.append(success_rate * 40)
        
        # Resource utilization (optimal is 60-80%)
        avg_utilization = sum(self.resource_utilization.values()) / len(self.resource_utilization)
        if 60 <= avg_utilization <= 80:
            factors.append(30)
        elif avg_utilization < 60:
            factors.append((avg_utilization / 60) * 30)
        else:
            factors.append(((100 - avg_utilization) / 20) * 30)
        
        return sum(factors)


# ============================================================================
# CACHE MODELS
# ============================================================================

@dataclass
class CacheEntry:
    """Cache entry for execution results"""
    key: str
    result: ExecutionResult
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: int = 3600
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def touch(self):
        """Update access time and count"""
        self.accessed_at = datetime.now()
        self.access_count += 1