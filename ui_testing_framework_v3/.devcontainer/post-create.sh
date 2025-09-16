#!/bin/bash
# Post-create script for development container

echo "🔧 Setting up UI Testing Framework V3 development environment..."

# Create project structure if not exists
echo "📁 Creating project structure..."
mkdir -p core ports adapters plugins application infrastructure api tests config docs
mkdir -p data logs
mkdir -p .vscode .github/copilot/prompts

# Create Python __init__ files
touch core/__init__.py
touch ports/__init__.py
touch adapters/__init__.py
touch plugins/__init__.py
touch application/__init__.py
touch infrastructure/__init__.py
touch api/__init__.py
touch tests/__init__.py

# Set up git if not initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git config --global user.email "dev@ui-testing-framework.local"
    git config --global user.name "UI Testing Framework Developer"
fi

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "🔐 Creating .env file..."
    cat > .env << EOF
# Environment variables for UI Testing Framework V3
HEADLESS=false
ANTI_BOT_LEVEL=maximum
LOG_LEVEL=INFO
PYTHONPATH=/workspace
EOF
fi

# Create pytest.ini if not exists
if [ ! -f pytest.ini ]; then
    echo "🧪 Creating pytest configuration..."
    cat > pytest.ini << EOF
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=.
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=95
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    smoke: Smoke tests
EOF
fi

# Create pyproject.toml if not exists
if [ ! -f pyproject.toml ]; then
    echo "📋 Creating pyproject.toml..."
    cat > pyproject.toml << EOF
[project]
name = "ui-testing-framework-v3"
version = "3.0.0"
description = "Production-grade UI Testing Framework with Hexagonal Architecture"
requires-python = ">=3.11"
dependencies = [
    "playwright>=1.40.0",
    "langgraph>=0.0.20",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.12.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "UP", "S", "B", "A", "C4", "DTZ", "T10", "ISC", "ICN", "PIE", "PYI", "PT", "RET", "SIM", "TID", "TCH", "ARG", "PGH", "PL", "TRY", "PERF", "RUF"]
ignore = ["E501", "S101"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
no_implicit_reexport = true

[tool.coverage.run]
source = ["."]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
EOF
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --user -e . 2>/dev/null || true
pip install --user -r requirements-dev.txt 2>/dev/null || true

# Set up Playwright
echo "🎭 Setting up Playwright browsers..."
playwright install chromium 2>/dev/null || true

# Create sample configuration if not exists
if [ ! -f config/config.toml ]; then
    echo "⚙️ Creating sample configuration..."
    mkdir -p config
    cat > config/config.toml << EOF
# UI Testing Framework V3 Configuration

[framework]
version = "3.0.0"
name = "UI Testing Framework V3"

[browser]
headless = false
timeout = 30000
anti_bot_level = "maximum"

[extraction]
default_profile = "qa"
cache_size = 100
max_elements = 100

[storage]
type = "sqlite"
path = "data/storage.db"

[logging]
level = "INFO"
format = "json"
EOF
fi

# Set correct permissions
echo "🔒 Setting permissions..."
chmod +x .devcontainer/post-create.sh 2>/dev/null || true
chmod 755 data logs 2>/dev/null || true

# Display welcome message
echo "
╔══════════════════════════════════════════════════════════════╗
║     🚀 UI Testing Framework V3 - Development Ready! 🚀      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Architecture: Hexagonal (Ports & Adapters)                 ║
║  Pattern: Plugin-First Design                               ║
║  Testing: 95%+ Coverage Required                            ║
║  Browser: Headless=False (Always)                           ║
║                                                              ║
║  Quick Start:                                                ║
║  1. Review MASTER_BUILD_PROMPT.md for requirements          ║
║  2. Follow phase-based implementation                       ║
║  3. Run tests: pytest                                       ║
║  4. Check coverage: pytest --cov                            ║
║                                                              ║
║  VSCode Agent Mode: Enabled ✓                               ║
║  MCP Servers: Configured ✓                                  ║
║  GitHub Copilot: Optimized ✓                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"

echo "✅ Development environment setup complete!"