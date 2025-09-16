#!/usr/bin/env python3
"""
Setup script for optimal Claude Code environment.
Implements all recommendations from the best practices analysis.
"""

import subprocess
import sys
import os
from pathlib import Path
import json


def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        if result.stdout:
            print(f"   SUCCESS: {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"   ERROR: {e.stderr.strip() if e.stderr else str(e)}")
        return False


def create_project_structure():
    """Create the complete project directory structure."""
    print("Creating project structure...")

    directories = [
        "core",
        "agents",
        "stealth",
        "mcp",
        "utils",
        "tests/test_core",
        "tests/test_agents",
        "tests/test_stealth",
        "tests/test_integration",
        "docs",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        (Path(directory) / "__init__.py").touch(exist_ok=True)

    print("   SUCCESS: Project structure created")


def create_requirements_file():
    """Create requirements.txt with all necessary dependencies."""
    print("Creating requirements.txt...")

    requirements = [
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
        "pytest>=7.0.0",
        "pytest-asyncio",
        "pytest-cov",
        "black",
        "isort",
        "mypy",
        "flake8",
        "pre-commit",
    ]

    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))

    print("   SUCCESS: requirements.txt created")


def create_pyproject_toml():
    """Create pyproject.toml for project configuration."""
    print("Creating pyproject.toml...")

    pyproject_content = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ai-stealth-browser"
version = "1.0.0"
description = "The most advanced AI-first stealth browser automation system"
authors = [{name = "AI Stealth Browser Team"}]
license = {text = "MIT"}
requires-python = ">=3.11"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
asyncio_mode = "auto"
addopts = "--cov=. --cov-report=term-missing"
"""

    with open("pyproject.toml", "w") as f:
        f.write(pyproject_content)

 print( " SUCCESS: pyproject.toml created " ) 

def install_dependencies():
    """Install all project dependencies."""
 print( " Installing dependencies... " ) 
    # Install core dependencies
    if run_command("pip install -r requirements.txt", check=False):
 print( " SUCCESS: Core dependencies installed " )     else:
 print( " WARNING: Some dependencies may have failed to install " ) 
    # Install Playwright browsers
    if run_command("playwright install chromium", check=False):
 print( " SUCCESS: Playwright browsers installed " ) 

def setup_git_hooks():
    """Set up git hooks for code quality."""
 print( " Setting up git hooks... " ) 
    # Initialize git if not already done
    if not Path(".git").exists():
        run_command("git init", check=False)

    # Create pre-commit hook
    hooks_dir = Path(".git/hooks")
    hooks_dir.mkdir(exist_ok=True)

    pre_commit_hook = hooks_dir / "pre-commit"
    pre_commit_content = """#!/bin/sh
# Pre-commit hook for code quality checks
echo " Running pre-commit checks... " 
# Run the Claude Code git guard
python .claude/hooks/git_commit_guard.py
exit_code=$?

if [ $exit_code -ne 0 ]; then
 echo " ERROR: Pre-commit checks failed "     exit 1
fi

echo " SUCCESS: Pre-commit checks passed " exit 0
"""

    with open(pre_commit_hook, "w") as f:
        f.write(pre_commit_content)

    # Make hook executable (Windows compatible)
    if os.name != "nt":
        os.chmod(pre_commit_hook, 0o755)

 print( " SUCCESS: Git hooks configured " ) 

def create_documentation():
    """Create basic documentation files."""
 print( " Creating documentation... " ) 
    # Create README.md
    readme_content = """# AI-First Stealth Browser

The most sophisticated, stealth, AI-first smart browser ever known to humans.

## Features

- **AI-First Architecture**: Powered by specialized AI agents - **Advanced Stealth**: Undetectable automation with human-like behavior - **High Performance**: Optimized for speed and efficiency - **Security Focused**: Privacy-first design with zero tracking - **Intelligent Automation**: Context-aware task completion 
## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run the stealth browser
python stealth_browser.py
```

## Architecture

This project follows a modular architecture with specialized AI agents:

- **StealthAgent**: Monitors and adapts anti-detection strategies
- **NavigationAgent**: Handles intelligent browsing patterns
- **SecurityAgent**: Manages security protocols
- **PerformanceAgent**: Optimizes speed and resources
- **LearningAgent**: Analyzes patterns for improvement

## Development

The project uses Claude Code environment with automated hooks for code quality.

See `.CLAUDE.md` for the complete project constitution and guidelines.
"""

    with open("README.md", "w") as f:
        f.write(readme_content)

 print( " SUCCESS: Documentation created " ) 

def validate_setup():
    """Validate that the setup was successful."""
 print( " SUCCESS: Validating setup... " ) 
    checks = [
        ("Claude settings", Path(".claude/settings.json").exists()),
        ("Project constitution", Path(".CLAUDE.md").exists()),
        ("Stealth agent", Path(".claude/agents/stealth_agent.py").exists()),
        ("Navigation agent", Path(".claude/agents/navigation_agent.py").exists()),
        ("Auto formatter hook", Path(".claude/hooks/auto_formatter.py").exists()),
        ("Git commit guard", Path(".claude/hooks/git_commit_guard.py").exists()),
        ("Requirements file", Path("requirements.txt").exists()),
        ("Project config", Path("pyproject.toml").exists()),
    ]

    all_passed = True
    for check_name, check_result in checks:
 status = " SUCCESS: " if check_result else " ERROR: "         print(f"   {status} {check_name}")
        if not check_result:
            all_passed = False

    return all_passed


def main():
    """Main setup function."""
 print( " Setting up optimal Claude Code environment for AI-First Stealth Browser " )     print("=" * 80)

    try:
        # Run setup steps
        create_project_structure()
        create_requirements_file()
        create_pyproject_toml()
        install_dependencies()
        setup_git_hooks()
        create_documentation()

        # Validate setup
        if validate_setup():
 print( " \n Claude Code environment setup completed successfully! " )             print("\nNext steps:")
            print("1. Review the project constitution in .CLAUDE.md")
            print("2. Examine the specialized agents in .claude/agents/")
            print("3. Start developing with enhanced stealth capabilities")
            print("4. Use 'git commit' to see automated quality checks in action")
        else:
            print(
 " \n WARNING: Setup completed with some issues. Please check the validation results above. "             )

    except Exception as e:
 print(f " \n ERROR: Setup failed with error: {e} " )         return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
