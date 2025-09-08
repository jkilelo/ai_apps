# 🤖 AI-First Smart Browser v2.0.0

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.40+-green.svg)](https://playwright.dev/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Claude Code Optimized](https://img.shields.io/badge/Claude%20Code-Optimized-purple.svg)](https://claude.ai)

## 🚀 Overview

A production-ready, autonomous web agent built with Python and Playwright that executes natural language tasks through intelligent browser automation. This framework combines military-grade stealth capabilities, multi-modal perception (DOM + visual), LLM-based reasoning, and a plugin architecture optimized for Claude Code development.

## 🏗️ Architecture

The framework follows a **5-layer architecture**:

1. **Execution Layer** - Browser control and stealth operations
2. **Perception Layer** - DOM processing and visual annotation (Set-of-Marks)
3. **Cognition Layer** - LLM integration and ReAct reasoning loop
4. **Memory Layer** - Multi-tier memory systems (planned)
5. **Extensibility Layer** - Plugin system and MCP protocol (planned)

## ✨ Key Features

### Implemented
- ✅ **Stealth Browser Automation** - Advanced bot evasion with plugin-based stealth system
- ✅ **Multi-Modal Perception** - Combines DOM analysis with visual annotation
- ✅ **Set-of-Marks Visual System** - Annotates interactive elements on screenshots
- ✅ **Multi-LLM Support** - OpenAI, Anthropic Claude, Google Gemini
- ✅ **Structured Action Generation** - Type-safe actions using Pydantic models
- ✅ **Intelligent DOM Processing** - Simplifies HTML to LLM-friendly format
- ✅ **Action Dispatcher** - Maps high-level actions to browser primitives
- ✅ **Configurable Architecture** - JSON/YAML based configuration

### In Development
- 🔄 ReAct Agent Loop with self-correction
- 🔄 Hierarchical task planning
- 🔄 Memory systems (SQLite, Qdrant, Knowledge Graphs)
- 🔄 MCP protocol support
- 🔄 Plugin ecosystem

## 📦 Installation

### Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/ai-browser.git
cd ai-browser

# Run automated setup
chmod +x setup.sh
./setup.sh
```

### Manual Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (UV recommended, 10-100x faster)
uv pip install -r requirements.txt
# Or with standard pip:
# pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 🔧 Configuration

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_gemini_key
```

## 🎯 Quick Start

### Basic Usage

```python
import asyncio
from src.main import AIBrowserAgent

async def main():
    # Initialize agent
    agent = AIBrowserAgent()
    
    # Execute a task
    result = await agent.execute_task(
        task="Search for Python tutorials on Google and find the official Python documentation",
        start_url="https://google.com"
    )
    
    print(f"Success: {result['success']}")
    print(f"Summary: {result['summary']}")

asyncio.run(main())
```

### Command Line Interface

```bash
# Execute a task
python src/main.py --task "Find the weather in New York" --url "https://weather.com"

# Test stealth capabilities
python src/main.py --test-stealth

# Run in headless mode
python src/main.py --task "Your task" --headless

# Use custom configuration
python src/main.py --task "Your task" --config config.json
```

## 🏛️ Component Details

### Execution Layer (`src/execution/`)

- **BrowserManager**: Handles browser lifecycle with Playwright
- **StealthManager**: Plugin-based bot evasion system
- **Action Primitives**: Low-level browser interactions (click, type, scroll, etc.)

#### Stealth Plugins
- WebDriver flag masking
- Chrome runtime emulation
- Plugin array spoofing
- WebGL vendor spoofing
- Language consistency
- Permissions API implementation
- User agent data override
- Canvas fingerprint noise

### Perception Layer (`src/perception/`)

- **DOMProcessor**: Extracts and simplifies HTML content
- **VisualAnnotator**: Implements Set-of-Marks annotation system
- **StateObserver**: Orchestrates multi-modal state capture

### Cognition Layer (`src/cognition/`)

- **LLM Providers**: OpenAI, Anthropic, Gemini implementations
- **Structured Actions**: Type-safe action models with Pydantic
- **PromptBuilder**: Sophisticated prompt engineering
- **ActionDispatcher**: Maps structured actions to browser execution

## 🧪 Testing Stealth

Test the stealth capabilities:

```python
import asyncio
from src.main import AIBrowserAgent

async def test_stealth():
    agent = AIBrowserAgent()
    results = await agent.test_stealth()
    
    print(f"Bot detected: {results['is_bot']}")
    print(f"WebDriver flag: {results['details']['webdriver']}")
    print(f"Plugins count: {results['details']['plugins_length']}")
    
asyncio.run(test_stealth())
```

## 📊 Performance Targets

- Browser initialization: <2s
- Page state capture: <5s
- Action execution: <1s
- LLM response: <10s
- Memory retrieval: <100ms (when implemented)

## 🔌 Extending the Framework

### Adding a New LLM Provider

```python
from src.cognition.llm import ILLMProvider

class CustomProvider(ILLMProvider):
    async def generate(self, prompt: str, **kwargs) -> str:
        # Your implementation
        pass
    
    async def generate_structured(self, prompt: str, output_model, **kwargs):
        # Your implementation
        pass
```

### Adding a New Stealth Plugin

```python
from src.execution.stealth_manager import IStealthPlugin

class CustomStealthPlugin(IStealthPlugin):
    def get_name(self) -> str:
        return "custom_plugin"
    
    async def apply_to_context(self, context):
        # Your stealth modifications
        pass
```

## 🛣️ Roadmap

### Phase 1: Foundation ✅
- Browser control
- Stealth system
- Basic perception

### Phase 2: Intelligence ✅
- LLM integration
- Structured actions
- Prompt engineering

### Phase 3: Agency (Current)
- ReAct loop
- Self-correction
- Task planning

### Phase 4: Memory (Next)
- Session memory (SQLite)
- Semantic memory (Qdrant)
- Knowledge graphs (FalkorDB)

### Phase 5: Extensibility
- Plugin system
- MCP protocol
- A2A communication

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Playwright for browser automation
- OpenAI, Anthropic, and Google for LLM capabilities
- The open-source community for inspiration and tools

## 🐳 Container Services (Podman)

| Service | Port | Status | Purpose |
|---------|------|--------|---------|
| **FalkorDB** | 6379 | ✅ Running | Graph database for knowledge patterns |
| **Meilisearch** | 7700 | ✅ Running | Full-text search engine |
| **Qdrant** | 6333 | ⏸️ Optional | Vector database for semantic search |

```bash
# Container management
make container-up    # Start all containers
make container-down  # Stop all containers
make container-health # Check health status

# Deploy Qdrant (optional)
podman run -d --name qdrant -p 6333:6333 docker.io/qdrant/qdrant:latest
```

## 🤖 Claude Code Integration

This project is **fully optimized** for Claude Code with:
- **11 Specialized AI Agents** for different domains
- **7 Custom Commands** for common workflows
- **Advanced Hooks** for automation
- **128K Token Context** support
- **Parallel Tool Execution** enabled

### Custom Commands
- `/test-stealth` - Validate bot detection evasion
- `/run-task` - Execute browser automation task
- `/browser-session` - Launch persistent browser
- `/debug-browser` - Interactive debugging mode

### Specialized Agents
- `stealth-evasion-expert` - Bot detection bypass
- `browser-automation-specialist` - Playwright expertise
- `web-perception-specialist` - DOM and visual analysis
- `react-reasoning-architect` - ReAct loop design
- And 7 more domain experts...

## 🧪 Testing

```bash
# Run all tests
make test

# Test categories
make test-unit        # Unit tests
make test-integration # Integration tests
make test-stealth     # Stealth validation
make test-coverage    # Coverage report
```

## 🛠️ Development

```bash
# Code quality
make lint      # Run linting
make format    # Format code
make typecheck # Type checking
make quality   # All checks

# Development commands
make run          # Run application
make browser-dev  # Browser with DevTools
make shell        # IPython with context
```

## 📚 Documentation

- [Architecture Guide](.claude/CLAUDE.md) - Complete project architecture
- [Container Reference](.claude/CONTAINER_REFERENCE.md) - Podman services guide
- [Agent Matrix](.claude/agent_matrix.yaml) - Agent orchestration rules
- [Development Aliases](.claude/aliases.sh) - Productivity shortcuts

## ⚠️ Disclaimer

This tool is for legitimate automation and testing purposes only. Users are responsible for complying with websites' terms of service and applicable laws.

---

**Status**: 🚧 Active Development  
**Version**: 2.0.0  
**Python**: 3.11+  
**Container Runtime**: Podman  
**Last Updated**: 2025-01-05  
**Claude Code**: Fully Optimized