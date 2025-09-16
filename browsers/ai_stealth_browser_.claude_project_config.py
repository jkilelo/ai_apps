"""
Project configuration and structure definition for AI-First Stealth Browser.

This module defines the project structure, dependencies, and configuration
for the optimal Claude Code development environment.
"""

from pathlib import Path
from typing import Dict, List, Any

class ProjectConfig:
    """Configuration class for the AI-First Stealth Browser project."""
    
    # Project metadata
    PROJECT_NAME = "AI-First Stealth Browser"
    PROJECT_VERSION = "1.0.0"
    PYTHON_VERSION = "3.11+"
    
    # Core dependencies
    CORE_DEPENDENCIES = [
        "playwright>=1.40.0",
        "pydantic>=2.5.0",
        "pydantic-ai>=0.0.13",
        "asyncio",
        "aiofiles",
        "httpx",
        "beautifulsoup4",
        "lxml",
        "fake-useragent",
        "undetected-chromedriver",
    ]
    
    # Development dependencies
    DEV_DEPENDENCIES = [
        "pytest>=7.0.0",
        "pytest-asyncio",
        "pytest-cov",
        "black",
        "isort",
        "mypy",
        "flake8",
        "pre-commit",
    ]
    
    # MCP Server dependencies
    MCP_DEPENDENCIES = [
        "mcp-server-filesystem",
        "mcp-server-playwright", 
        "mcp-server-memory",
        "mcp-server-github",
    ]
    
    # Project structure
    PROJECT_STRUCTURE = {
        "core/": {
            "__init__.py": "Core module initialization",
            "browser_engine.py": "Main browser engine with Playwright integration",
            "stealth_engine.py": "Advanced stealth and anti-detection system",
            "ai_coordinator.py": "AI agent coordination and management",
        },
        "agents/": {
            "__init__.py": "Agents module initialization", 
            "stealth_agent.py": "Stealth monitoring and adaptation agent",
            "navigation_agent.py": "Intelligent navigation and interaction agent",
            "security_agent.py": "Security monitoring and threat detection agent",
            "performance_agent.py": "Performance optimization agent",
            "learning_agent.py": "Pattern learning and behavior adaptation agent",
        },
        "stealth/": {
            "__init__.py": "Stealth module initialization",
            "detection_evasion.py": "Detection system evasion techniques",
            "fingerprint_spoofing.py": "Browser fingerprint spoofing",
            "human_simulation.py": "Human behavior simulation",
            "anti_detection.py": "Anti-detection countermeasures",
        },
        "mcp/": {
            "__init__.py": "MCP module initialization",
            "server_manager.py": "MCP server management and coordination",
            "protocol_handler.py": "MCP protocol implementation",
            "tool_registry.py": "Available tools and capabilities registry",
        },
        "utils/": {
            "__init__.py": "Utils module initialization",
            "helpers.py": "Utility functions and helpers",
            "config.py": "Configuration management",
            "logging.py": "Logging configuration and utilities",
            "validators.py": "Data validation utilities",
        },
        "tests/": {
            "__init__.py": "Tests module initialization",
            "test_core/": "Core functionality tests",
            "test_agents/": "Agent functionality tests", 
            "test_stealth/": "Stealth capability tests",
            "test_integration/": "Integration tests",
            "conftest.py": "Pytest configuration",
        },
        "docs/": {
            "README.md": "Project documentation",
            "ARCHITECTURE.md": "System architecture documentation",
            "API.md": "API documentation",
            "DEPLOYMENT.md": "Deployment instructions",
        },
        ".claude/": {
            "settings.json": "Claude Code environment settings",
            ".CLAUDE.md": "Project constitution and guidelines",
            "hooks/": "Automation hooks and scripts",
            "agents/": "Claude Code specialized agents",
        }
    }
    
    @classmethod
    def get_project_root(cls) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent
        
    @classmethod
    def create_structure(cls) -> None:
        """Create the complete project structure."""
        root = cls.get_project_root()
        
        def create_directory_structure(structure: Dict[str, Any], base_path: Path):
            for name, content in structure.items():
                path = base_path / name
                
                if name.endswith("/"):
                    # It's a directory
                    path.mkdir(exist_ok=True)
                    if isinstance(content, dict):
                        create_directory_structure(content, path)
                else:
                    # It's a file
                    if not path.exists():
                        path.touch()
                        if isinstance(content, str):
                            path.write_text(f'"""{content}"""\n')
                            
        create_directory_structure(cls.PROJECT_STRUCTURE, root)
        
    @classmethod
    def get_requirements_txt(cls) -> str:
        """Generate requirements.txt content."""
        all_deps = cls.CORE_DEPENDENCIES + cls.DEV_DEPENDENCIES
        return "\n".join(all_deps)
        
    @classmethod
    def get_pyproject_toml(cls) -> str:
        """Generate pyproject.toml content."""
        return f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{cls.PROJECT_NAME.lower().replace(' ', '-')}"
version = "{cls.PROJECT_VERSION}"
description = "The most advanced AI-first stealth browser automation system"
authors = [{{name = "AI Stealth Browser Team"}}]
license = {{text = "MIT"}}
requires-python = ">={cls.PYTHON_VERSION.rstrip('+')}"
dependencies = {cls.CORE_DEPENDENCIES}

[project.optional-dependencies]
dev = {cls.DEV_DEPENDENCIES}
mcp = {cls.MCP_DEPENDENCIES}

[tool.black]
line-length = 100
target-version = ['py311']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.pytest_cache
  | \\.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "--cov=. --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
source = ["."]
omit = [
    "tests/*",
    "setup.py",
    "*/site-packages/*",
    ".venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
'''

# Configuration instance
config = ProjectConfig()
