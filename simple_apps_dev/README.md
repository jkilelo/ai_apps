# Simple Apps v2 - Modern Web Automation Testing

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, clean web automation testing application with comprehensive element extraction, test generation, and execution capabilities. Built with FastAPI, React, Playwright, and LLM integration.

## ✨ Features

- 🔍 **Intelligent Element Extraction** - Advanced web element detection using Playwright
- 🧠 **LLM-Powered Analysis** - Smart element categorization and test scenario generation
- 🎯 **Automated Test Generation** - Generate complete pytest test suites
- ⚡ **Real-time Execution** - Execute generated tests with live results
- 🏗️ **Modern Architecture** - Clean src-layout structure with type safety
- 🛠️ **Developer Experience** - Rich CLI, comprehensive logging, and dev tools integration

## 🏗️ Project Structure

```
simple_apps_v2/
├── src/simple_apps_v2/        # Main application package
│   ├── api/                   # FastAPI application and routes
│   ├── core/                  # Configuration, logging, models
│   ├── services/              # Business logic services
│   └── utils/                 # Utility functions
├── frontend/                  # React TypeScript frontend
├── tests/                     # Comprehensive test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── pyproject.toml            # Modern Python project configuration
└── Makefile                  # Development commands
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Git**

### Installation

```bash
# Clone and navigate to project
git clone <repository-url>
cd simple_apps_v2

# Install Python dependencies with development tools
pip install -e ".[all]"

# Install Playwright browsers
playwright install chromium

# Install frontend dependencies
cd frontend && npm install && cd ..

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Install pre-commit hooks (recommended)
pre-commit install
```

### Running the Application

```bash
# Start API server
make serve
# Or: python -m simple_apps_v2 serve

# Start frontend (in another terminal)
cd frontend && npm run dev

# Access the application
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:5175
# - API Docs: http://localhost:5175/docs
```

## 📖 Usage

### Command Line Interface

```bash
# Extract elements from a website
simple-apps extract https://example.com --output results.json

# Start API server with custom settings
simple-apps serve --host 127.0.0.1 --port 8000 --log-level debug

# Check system health
simple-apps health

# View configuration
simple-apps config

# Initialize new project
simple-apps init my-project
```

### Python API

```python
import asyncio
from simple_apps_v2.services.extractor import ElementExtractor

async def extract_elements():
    extractor = ElementExtractor()
    result = await extractor.extract_elements_from_url(
        url="https://example.com",
        analyze_with_llm=True
    )
    return result

# Run extraction
result = asyncio.run(extract_elements())
print(f"Found {result['total_elements']} elements")
```

### REST API

```bash
# Extract elements
curl -X POST "http://localhost:5175/api/extract-elements" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "analyze_with_llm": true}'

# Generate tests
curl -X POST "http://localhost:5175/api/generate-tests" \
  -H "Content-Type: application/json" \
  -d '{"extraction_data": {...}}'

# Generate code
curl -X POST "http://localhost:5175/api/generate-code" \
  -H "Content-Type: application/json" \
  -d '{"extraction_data": {...}, "test_data": {...}}'

# Execute tests
curl -X POST "http://localhost:5175/api/execute-tests" \
  -H "Content-Type: application/json" \
  -d '{"generated_files": [...], "url": "https://example.com"}'
```

## 🔧 Configuration

Configuration is managed through environment variables and `.env` files:

```env
# Application
APP_NAME="Simple Apps v2"
DEBUG=false
API_PORT=5175

# LLM Integration (at least one required)
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-google-api-key
ANTHROPIC_API_KEY=your-anthropic-key

# Browser Settings
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30000

# Logging
LOG_LEVEL=INFO
```

See `.env.example` for complete configuration options.

## 🧪 Development

### Development Commands

```bash
# Install all dependencies
make install-all

# Run linting and formatting
make lint
make format

# Run tests
make test           # All tests
make test-unit      # Unit tests only
make test-integration  # Integration tests
make test-coverage  # With coverage report

# Start development server
make serve-dev      # With reload and debug logging

# Code quality checks
make mypy           # Type checking
make pre-commit-run # All pre-commit hooks

# Clean build artifacts
make clean
```

### Testing

The project includes comprehensive test coverage:

- **Unit Tests** - Test individual components in isolation
- **Integration Tests** - Test service interactions  
- **End-to-End Tests** - Test complete workflows
- **Browser Tests** - Test browser automation functionality
- **LLM Tests** - Test AI integration (requires API keys)

```bash
# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m browser      # Browser automation tests
pytest -m "not llm"    # Skip LLM tests (no API keys needed)
```

### Code Quality

The project enforces high code quality standards:

- **Ruff** - Fast linting and formatting
- **MyPy** - Static type checking
- **Pre-commit hooks** - Automated checks before commits
- **Test coverage** - Minimum 80% coverage required
- **Type hints** - Full type annotation coverage

## 🏛️ Architecture

### Core Principles

- **Clean Architecture** - Clear separation of concerns
- **Type Safety** - Comprehensive type hints and validation
- **Async/Await** - Full async support for better performance
- **Configuration Management** - Environment-based configuration
- **Dependency Injection** - Loosely coupled services
- **Error Handling** - Comprehensive error management
- **Logging** - Structured logging with rich formatting

### Services

- **BrowserService** - Manages Playwright browser automation
- **ElementExtractor** - Extracts and categorizes web elements
- **LLMService** - Handles multiple LLM provider integrations
- **APIRouter** - RESTful API endpoints with validation

### Models

All data models use Pydantic for validation and serialization:

- **ExtractionRequest/Response** - Element extraction API models
- **GenerateTestsRequest/Response** - Test generation models
- **CodeGenerationRequest/Response** - Code generation models
- **ExecuteTestsRequest/Response** - Test execution models

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Install** development dependencies: `make install-dev`
4. **Make** your changes with tests
5. **Run** quality checks: `make lint test`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to the branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

### Development Guidelines

- Write comprehensive tests for all new features
- Follow the existing code style (enforced by pre-commit hooks)
- Add type hints to all functions and classes
- Update documentation for API changes
- Ensure all tests pass and coverage remains above 80%

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [API Docs](http://localhost:5175/docs) (when server is running)
- **Issues**: [GitHub Issues](https://github.com/ai-apps/simple-apps-v2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ai-apps/simple-apps-v2/discussions)

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **Playwright** - Reliable browser automation
- **Pydantic** - Data validation using Python type hints
- **Ruff** - An extremely fast Python linter and code formatter
- **Rich** - Rich text and beautiful formatting in the terminal