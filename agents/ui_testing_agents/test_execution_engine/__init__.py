"""
Nexus Executor - Cutting-Edge Python Execution Environment
===========================================================

A comprehensive, secure, and high-performance code execution system that combines
the best features from multiple execution modules with advanced capabilities.

Features:
- Advanced security sandboxing with multiple isolation levels
- Multi-language support (Python, JavaScript, TypeScript, and more)
- Intelligent code analysis and optimization
- LLM-powered code generation and testing
- Real-time monitoring and comprehensive reporting
- Distributed execution capabilities
- Resource management and throttling
- Caching and performance optimization
"""

__version__ = "1.0.0"
__author__ = "Nexus Team"

from .core.models import (
    ExecutionMode,
    ExecutionStatus,
    CodeLanguage,
    SecurityLevel,
    ReportFormat,
    ResourceType,
    MetricType,
    
    ResourceLimits,
    SecurityConfig,
    ExecutionConfig,
    
    CodeArtifact,
    ExecutionRequest,
    ExecutionResult,
    
    PerformanceMetrics,
    ExecutionReport,
    CodeAnalysis,
    OptimizationSuggestion,
    TestCase,
)

from .core.sandbox import (
    NexusSandbox,
    SandboxFactory,
    SecurityRules,
    ASTSecurityAnalyzer,
)

from .core.executor import (
    NexusExecutor,
    ExecutorFactory,
    PythonExecutor,
    JavaScriptExecutor,
)

from .core.analyzer import (
    NexusCodeAnalyzer,
    ComplexityCalculator,
    PatternDetector,
    DependencyAnalyzer,
    OptimizationSuggester,
)

# Convenience functions
def create_executor(config: ExecutionConfig = None) -> NexusExecutor:
    """Create a new executor instance"""
    return ExecutorFactory.create(config)

def get_default_executor() -> NexusExecutor:
    """Get the default executor instance"""
    return ExecutorFactory.get_default()

def analyze_code(code: str, language: CodeLanguage = CodeLanguage.PYTHON) -> CodeAnalysis:
    """Analyze code and return analysis results"""
    artifact = CodeArtifact(content=code, language=language)
    analyzer = NexusCodeAnalyzer()
    return analyzer.analyze(artifact)

async def execute_code(
    code: str,
    language: CodeLanguage = CodeLanguage.PYTHON,
    security_level: SecurityLevel = SecurityLevel.STANDARD
) -> ExecutionResult:
    """Execute code with default settings"""
    # For NONE level, also clear blocked patterns
    security_config = SecurityConfig(level=security_level)
    if security_level == SecurityLevel.NONE:
        security_config.blocked_imports = []
        security_config.blocked_builtins = []
    
    config = ExecutionConfig(
        language=language,
        security=security_config
    )
    artifact = CodeArtifact(content=code, language=language)
    request = ExecutionRequest(artifact=artifact, config=config)
    
    # Create executor with our specific config instead of using default
    executor = NexusExecutor(config)
    return await executor.execute(request)

__all__ = [
    # Version
    "__version__",
    
    # Models
    "ExecutionMode",
    "ExecutionStatus",
    "CodeLanguage",
    "SecurityLevel",
    "ReportFormat",
    "ResourceType",
    "MetricType",
    "ResourceLimits",
    "SecurityConfig",
    "ExecutionConfig",
    "CodeArtifact",
    "ExecutionRequest",
    "ExecutionResult",
    "PerformanceMetrics",
    "ExecutionReport",
    "CodeAnalysis",
    "OptimizationSuggestion",
    "TestCase",
    
    # Sandbox
    "NexusSandbox",
    "SandboxFactory",
    "SecurityRules",
    "ASTSecurityAnalyzer",
    
    # Executor
    "NexusExecutor",
    "ExecutorFactory",
    "PythonExecutor",
    "JavaScriptExecutor",
    
    # Analyzer
    "NexusCodeAnalyzer",
    "ComplexityCalculator",
    "PatternDetector",
    "DependencyAnalyzer",
    "OptimizationSuggester",
    
    # Convenience functions
    "create_executor",
    "get_default_executor",
    "analyze_code",
    "execute_code",
]