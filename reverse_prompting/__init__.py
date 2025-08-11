"""
Reverse Prompting Engine

A revolutionary system for generating high-quality prompts by working backwards
from finished code, applying cutting-edge prompt strategies, and automatically
evaluating and evolving the results.

This package provides a comprehensive framework for:
- Analyzing existing code to understand its structure and functionality
- Generating prompts using multiple advanced strategies
- Creating new code using LLMs based on generated prompts
- Evaluating similarity and functionality between original and generated code
- Iteratively improving prompts through evolutionary algorithms
- Managing sessions and tracking performance metrics

Key Components:
- Core data models and configuration
- Advanced prompt strategies (Chain of Thought, Self-Consistency, etc.)
- Comprehensive evaluation system with multiple similarity metrics
- Multi-backend storage system (SQLite, Redis, MongoDB)
- LLM integration for multiple providers (OpenAI, Anthropic, Google)
- Safe code execution environment
- Performance monitoring and metrics collection
- Command-line interface and examples

Usage:
    from reverse_prompting import ReversePromptingEngine, CodeArtifact, CodeLanguage
    
    # Create a code artifact
    code = CodeArtifact(
        name="example",
        language=CodeLanguage.PYTHON,
        content="def hello_world():\n    print('Hello, World!')"
    )
    
    # Run reverse prompting
    engine = ReversePromptingEngine()
    session = await engine.run_reverse_prompting(
        target_code=code,
        session_name="my_session"
    )
    
    print(f"Generated {len(session.generated_prompts)} prompts")
    print(f"Best score: {session.best_result.overall_score}")

CLI Usage:
    # Run reverse prompting on a Python file
    python -m reverse_prompting run my_script.py
    
    # Use specific strategies with evolution enabled
    python -m reverse_prompting run my_script.py \\
        --strategies chain_of_thought few_shot \\
        --enable-evolution \\
        --enable-monitoring
    
    # List existing sessions
    python -m reverse_prompting list
"""

from .core.models import (
    CodeArtifact,
    CodeLanguage,
    PromptStrategy,
    PromptGeneration,
    EvaluationResult,
    ReversePromptingSession,
    EngineConfig,
    ExecutionStatus,
    VersionInfo,
)

from .engines.reverse_engine import ReversePromptingEngine

from .strategies.prompt_strategies import (
    get_strategy,
    list_available_strategies,
    ZeroShotStrategy,
    FewShotStrategy,
    ChainOfThoughtStrategy,
    SelfConsistencyStrategy,
    TreeOfThoughtsStrategy,
    MixtureOfExpertsStrategy,
    MetaPromptingStrategy,
)

from .evaluation.evaluators import (
    ComprehensiveEvaluator,
    ExactMatchEvaluator,
    SemanticEvaluator,
    StructuralEvaluator,
    FunctionalEvaluator,
    EditDistanceEvaluator,
)

from .storage.session_storage import (
    SessionStorage,
    SQLiteStorage,
    RedisStorage,
    MongoDBStorage,
)

from .utils.llm_interface import LLMInterface, LLMProvider, LLMResponse

from .utils.code_executor import CodeExecutor, ExecutionResult, SecuritySandbox

from .utils.monitoring import (
    PerformanceMonitor,
    get_global_monitor,
    start_global_monitoring,
    stop_global_monitoring,
)

# Version information
__version__ = "1.0.0"
__author__ = "Reverse Prompting Team"
__email__ = "contact@reverseprompting.dev"
__description__ = "Revolutionary reverse prompting system for generating high-quality prompts from code"
__url__ = "https://github.com/reverseprompting/reverse-prompting-engine"

# Export main classes and functions
__all__ = [
    # Core models
    "CodeArtifact",
    "CodeLanguage",
    "PromptStrategy",
    "PromptGeneration",
    "EvaluationResult",
    "ReversePromptingSession",
    "EngineConfig",
    "ExecutionStatus",
    "VersionInfo",
    # Main engine
    "ReversePromptingEngine",
    # Strategies
    "get_strategy",
    "list_available_strategies",
    "ZeroShotStrategy",
    "FewShotStrategy",
    "ChainOfThoughtStrategy",
    "SelfConsistencyStrategy",
    "TreeOfThoughtsStrategy",
    "MixtureOfExpertsStrategy",
    "MetaPromptingStrategy",
    # Evaluation
    "ComprehensiveEvaluator",
    "ExactMatchEvaluator",
    "SemanticEvaluator",
    "StructuralEvaluator",
    "FunctionalEvaluator",
    "EditDistanceEvaluator",
    # Storage
    "SessionStorage",
    "SQLiteStorage",
    "RedisStorage",
    "MongoDBStorage",
    # LLM Interface
    "LLMInterface",
    "LLMProvider",
    "LLMResponse",
    # Code Execution
    "CodeExecutor",
    "ExecutionResult",
    "SecuritySandbox",
    # Monitoring
    "PerformanceMonitor",
    "get_global_monitor",
    "start_global_monitoring",
    "stop_global_monitoring",
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__url__",
]


def create_default_engine(**kwargs) -> ReversePromptingEngine:
    """
    Create a ReversePromptingEngine with default configuration.

    Args:
        **kwargs: Additional configuration parameters to override defaults

    Returns:
        Configured ReversePromptingEngine instance

    Example:
        engine = create_default_engine(
            max_iterations=5,
            enable_evolution=True,
            enable_monitoring=True
        )
    """
    config = EngineConfig(**kwargs)
    return ReversePromptingEngine(config=config)


def quick_reverse_prompt(
    code_content: str,
    language: CodeLanguage = CodeLanguage.PYTHON,
    session_name: str = "quick_session",
    **engine_kwargs,
) -> ReversePromptingSession:
    """
    Quick utility function for reverse prompting a code snippet.

    Args:
        code_content: The code content to reverse prompt
        language: Programming language of the code
        session_name: Name for the session
        **engine_kwargs: Additional engine configuration

    Returns:
        Completed reverse prompting session

    Example:
        code = '''
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        '''

        session = quick_reverse_prompt(code, CodeLanguage.PYTHON)
        print(f"Best score: {session.best_result.overall_score}")
    """
    import asyncio

    # Create code artifact
    artifact = CodeArtifact(
        name="quick_code",
        language=language,
        content=code_content,
        description="Quick reverse prompting code",
    )

    # Create engine and run
    engine = create_default_engine(**engine_kwargs)

    # Run in async context
    async def _run():
        return await engine.run_reverse_prompting(
            target_code=artifact, session_name=session_name
        )

    return asyncio.run(_run())


# Package-level configuration
def configure_logging(level: str = "INFO", format_string: str = None):
    """
    Configure package-wide logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string: Custom format string for log messages
    """
    import logging

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set package loggers
    logging.getLogger("reverse_prompting").setLevel(getattr(logging, level.upper()))


def get_package_info() -> dict:
    """
    Get comprehensive package information.

    Returns:
        Dictionary containing package metadata and component status
    """
    import sys
    from pathlib import Path

    # Check optional dependencies
    optional_deps = {
        "redis": False,
        "motor": False,
        "openai": False,
        "anthropic": False,
        "google-generativeai": False,
        "psutil": False,
    }

    for dep in optional_deps:
        try:
            __import__(dep.replace("-", "."))
            optional_deps[dep] = True
        except ImportError:
            pass

    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "url": __url__,
        "python_version": sys.version,
        "install_path": str(Path(__file__).parent),
        "optional_dependencies": optional_deps,
        "available_strategies": [s.value for s in list_available_strategies()],
        "supported_languages": [lang.value for lang in CodeLanguage],
        "storage_backends": ["sqlite", "redis", "mongodb"],
        "llm_providers": ["openai", "anthropic", "google"],
    }


# Initialize logging with default configuration
configure_logging()


# Welcome message for interactive usage
def _print_welcome():
    """Print welcome message in interactive environments."""
    try:
        import sys

        if hasattr(sys, "ps1"):  # Interactive session
            print(
                f"""
Welcome to Reverse Prompting Engine v{__version__}!

Quick start:
  from reverse_prompting import quick_reverse_prompt, CodeLanguage
  
  code = "def hello(): print('Hello, World!')"
  session = quick_reverse_prompt(code, CodeLanguage.PYTHON)

For more examples, check the documentation or run:
  python -m reverse_prompting --help
            """
            )
    except:
        pass  # Ignore any errors in welcome message


# Print welcome message if imported interactively
_print_welcome()
