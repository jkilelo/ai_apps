#!/usr/bin/env python
"""
AI Browser Project Initialization Script
Quickly sets up the project structure and configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directory_structure():
    """Create the 5-layer architecture directories"""
    directories = [
        "src/execution",
        "src/perception", 
        "src/cognition",
        "src/memory",
        "src/extensibility",
        "tests/execution",
        "tests/perception",
        "tests/cognition",
        "tests/memory",
        "tests/extensibility",
        "plugins/stealth",
        "plugins/analysis",
        "plugins/optimization",
        "plugins/custom",
        "configs",
        "data/sqlite",
        "data/qdrant",
        "data/falkordb",
        "logs",
        "scripts",
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py for Python packages
        if dir_path.startswith("src/") or dir_path.startswith("tests/"):
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Package initialization"""')
    
    print("✅ Directory structure created")

def create_pyproject_toml():
    """Create pyproject.toml with modern Python configuration"""
    content = '''[project]
name = "ai-browser"
version = "1.0.0"
description = "AI-First Smart Browser with autonomous web agent capabilities"
requires-python = ">=3.11"
dependencies = [
    "playwright>=1.40.0",
    "pydantic>=2.5.0",
    "loguru>=0.7.2",
    "openai>=1.10.0",
    "anthropic>=0.15.0",
    "google-generativeai>=0.3.0",
    "qdrant-client>=1.7.0",
    "falkordb>=1.0.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.25.0",
    "beautifulsoup4>=4.12.0",
    "pillow>=10.0.0",
    "numpy>=1.24.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
    "ipython>=8.15.0",
]

[tool.ruff]
line-length = 120
target-version = "py311"
select = [
    "E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM",
]
ignore = ["E501"]
fix = true

[tool.ruff.isort]
known-first-party = ["src"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
asyncio_mode = "auto"
addopts = "-xvs --tb=short --cov=src --cov-report=html"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__pycache__/*"]
'''
    
    Path("pyproject.toml").write_text(content)
    print("✅ pyproject.toml created")

def create_env_template():
    """Create .env.example template"""
    content = '''# AI Provider API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here

# Memory Services (optional)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
FALKORDB_URL=redis://localhost:6379
FALKORDB_PASSWORD=

# Browser Configuration
BROWSER_TYPE=chromium
HEADLESS=false
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
'''
    
    Path(".env.example").write_text(content)
    print("✅ .env.example created")

def create_docker_compose():
    """Create docker-compose.yml for memory services"""
    content = '''version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: ai-browser-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./data/qdrant:/qdrant/storage:z
    restart: unless-stopped

  falkordb:
    image: falkordb/falkordb:latest
    container_name: ai-browser-falkordb
    ports:
      - "6379:6379"
    volumes:
      - ./data/falkordb:/data
    restart: unless-stopped
'''
    
    Path("docker-compose.yml").write_text(content)
    print("✅ docker-compose.yml created")

def create_gitignore():
    """Create .gitignore file"""
    content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
ENV/
env/

# UV
.uv/
uv.lock

# Environment
.env
*.env
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Logs
logs/
*.log

# Data
data/
*.db
*.sqlite

# Testing
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Browser
screenshots/
downloads/
.cache/

# Build
dist/
build/
*.egg-info/
'''
    
    Path(".gitignore").write_text(content)
    print("✅ .gitignore created")

def create_main_entry():
    """Create main.py entry point"""
    content = '''#!/usr/bin/env python
"""
AI Browser - Main Entry Point
Autonomous web agent with natural language task execution
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add("logs/ai_browser_{time}.log", rotation="100 MB", retention="7 days")


class TaskConfig(BaseModel):
    """Configuration for task execution"""
    task: str
    url: Optional[str] = None
    headless: bool = False
    timeout: int = 30000


async def main(config: TaskConfig) -> None:
    """Main execution function"""
    logger.info(f"Starting AI Browser with task: {config.task}")
    
    try:
        # Import after logging setup
        from src.execution.browser_manager import BrowserManager
        from src.cognition.agent_orchestrator import AgentOrchestrator
        
        # Initialize browser
        browser_manager = BrowserManager()
        await browser_manager.launch(headless=config.headless)
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(browser_manager)
        
        # Execute task
        result = await orchestrator.execute_task(
            task=config.task,
            url=config.url,
            timeout=config.timeout
        )
        
        logger.success(f"Task completed: {result}")
        
    except ImportError as e:
        logger.error(f"Module not implemented yet: {e}")
        logger.info("Run 'python init_project.py' to set up project structure")
    except Exception as e:
        logger.exception(f"Error executing task: {e}")
        raise
    finally:
        if 'browser_manager' in locals():
            await browser_manager.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Browser - Autonomous Web Agent")
    parser.add_argument("--task", required=True, help="Natural language task to execute")
    parser.add_argument("--url", help="Starting URL (optional)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--timeout", type=int, default=30000, help="Task timeout in ms")
    
    args = parser.parse_args()
    
    config = TaskConfig(
        task=args.task,
        url=args.url,
        headless=args.headless,
        timeout=args.timeout
    )
    
    asyncio.run(main(config))
'''
    
    Path("src/main.py").write_text(content)
    print("✅ src/main.py created")

def create_python_version():
    """Create .python-version file"""
    Path(".python-version").write_text("3.11")
    print("✅ .python-version created")

def run_uv_init():
    """Initialize UV project"""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ UV is installed")
        
        # Initialize project if not already done
        if not Path("uv.lock").exists():
            print("Initializing UV project...")
            subprocess.run(["uv", "init", ".", "--python", "3.11"], check=True)
            print("✅ UV project initialized")
        else:
            print("✅ UV project already initialized")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  UV not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False
    
    return True

def install_dependencies():
    """Install project dependencies with UV"""
    try:
        print("Installing dependencies...")
        subprocess.run(["uv", "sync", "--all-extras"], check=True)
        print("✅ Dependencies installed")
        
        print("Installing Playwright browsers...")
        subprocess.run(["uv", "run", "playwright", "install", "chromium"], check=True)
        print("✅ Playwright browsers installed")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error installing dependencies: {e}")

def main():
    """Run all initialization steps"""
    print("""
╔══════════════════════════════════════════════╗
║     AI Browser Project Initialization       ║
║     Setting up 5-layer architecture...      ║
╚══════════════════════════════════════════════╝
    """)
    
    # Create all necessary files and directories
    create_directory_structure()
    create_pyproject_toml()
    create_env_template()
    create_docker_compose()
    create_gitignore()
    create_python_version()
    create_main_entry()
    
    # Initialize UV and install dependencies
    if run_uv_init():
        install_dependencies()
    
    print("""
╔══════════════════════════════════════════════╗
║           ✅ Setup Complete!                ║
╚══════════════════════════════════════════════╝

Next steps:
1. Copy .env.example to .env and add your API keys
2. (Optional) Start memory services: docker-compose up -d
3. Test browser launch: uv run python src/main.py --task "test" --url "https://google.com"
4. Start developing with Claude Code!

Quick commands:
- Run tests: uv run pytest
- Check code: uvx ruff check src/
- Format code: uvx ruff format src/
- Type check: uv run mypy src/
""")

if __name__ == "__main__":
    main()