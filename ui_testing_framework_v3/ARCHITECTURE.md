# UI Testing Framework V3 - Hexagonal Plugin Architecture
## Lean, Extensible, Modular Design (2025 Best Practices)

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION SHELL                         │
│                    (Plugin Loader & Registry)                    │
└─────────────────────────────────────────────────────────────────┘
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
┌───▼────┐                 ┌─────▼─────┐                 ┌─────▼────┐
│ DOMAIN │                 │   PORTS   │                 │ ADAPTERS │
│  CORE  │◄────────────────│(Interfaces)│────────────────►│(Plugins) │
└────────┘                 └───────────┘                 └──────────┘
    │                                                           │
    │  Business Logic          Contracts                 Implementations
    │  - Element Model         - IBrowser                - ChromeBrowser
    │  - Test Case            - IExtractor              - StealthBrowser
    │  - Validation           - IFormatter              - LLMFormatter
    │  - Rules Engine         - IStorage                - SQLiteStorage
    │                         - IPromptStrategy          - QAStrategy
    │                         - ILLMProvider            - GeminiProvider
    │
┌───▼─────────────────────────────────────────────────────────▼───┐
│                        INFRASTRUCTURE                            │
│     (Cross-cutting concerns: Logging, Metrics, Events)          │
└──────────────────────────────────────────────────────────────────┘
```

## 🎯 Core Design Principles

### 1. **Hexagonal Architecture (Ports & Adapters)**
```python
# Domain stays pure - no external dependencies
# Ports define contracts
# Adapters implement contracts
# Plugins extend adapters
```

### 2. **Dependency Inversion**
```python
# High-level modules don't depend on low-level modules
# Both depend on abstractions (ports)
```

### 3. **Plugin-First Design**
```python
# Everything is a plugin
# Core only defines contracts
# Implementations are pluggable
```

## 📁 Project Structure

```
ui_testing_framework_v3/
│
├── core/                      # Domain Core (No External Dependencies)
│   ├── __init__.py
│   ├── models.py             # Pure domain models (dataclasses)
│   ├── value_objects.py      # Immutable value objects
│   ├── rules.py              # Business rules engine
│   └── exceptions.py         # Domain exceptions
│
├── ports/                     # Interface Definitions (ABCs)
│   ├── __init__.py
│   ├── browser.py            # IBrowser port
│   ├── extractor.py          # IExtractor port
│   ├── formatter.py          # IFormatter port
│   ├── storage.py            # IStorage port
│   ├── llm.py                # ILLMProvider port
│   └── strategy.py           # IPromptStrategy port
│
├── adapters/                  # Port Implementations
│   ├── browser/
│   │   ├── stealth.py        # StealthBrowserAdapter
│   │   └── playwright.py     # PlaywrightAdapter
│   ├── storage/
│   │   ├── sqlite.py         # SQLiteAdapter
│   │   └── sqlalchemy.py     # SQLAlchemyAdapter
│   ├── llm/
│   │   ├── gemini.py         # GeminiAdapter
│   │   ├── openai.py         # OpenAIAdapter
│   │   └── claude.py         # ClaudeAdapter
│   └── formatters/
│       ├── llm_test.py       # LLMTestFormatter
│       └── accessibility.py  # AccessibilityFormatter
│
├── plugins/                   # External Plugins (3rd Party)
│   ├── __init__.py
│   ├── loader.py             # Plugin discovery & loading
│   └── registry.py           # Plugin registration
│
├── application/              # Use Cases & Orchestration
│   ├── __init__.py
│   ├── workflows.py          # LangGraph workflows
│   ├── pipelines.py         # Processing pipelines
│   └── services.py           # Application services
│
├── infrastructure/           # Cross-cutting Concerns
│   ├── __init__.py
│   ├── config.py            # Configuration (TOML)
│   ├── events.py            # Event bus
│   ├── cache.py             # Caching (@lru_cache)
│   ├── metrics.py           # Performance metrics
│   └── logging.py           # Structured logging
│
└── api/                     # External Interfaces
    ├── cli.py               # CLI interface
    ├── rest.py              # REST API
    └── sdk.py               # Python SDK
```

## 🔧 Implementation with Built-in Python Modules

### Core Models (using dataclasses)
```python
# core/models.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from functools import cached_property

@dataclass(frozen=True)  # Immutable
class Element:
    """Pure domain model - no external dependencies"""
    selector: str
    tag_name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    @cached_property  # functools caching
    def is_interactive(self) -> bool:
        return self.tag_name in ['button', 'input', 'a', 'select']
    
    def __hash__(self):
        return hash((self.selector, self.tag_name))

@dataclass
class TestCase:
    """Domain model for test cases"""
    name: str
    steps: List[str]
    expected: List[str]
    priority: str = "medium"
    
    def validate(self) -> bool:
        """Business rule: test must have steps and expected results"""
        return len(self.steps) > 0 and len(self.expected) > 0
```

### Port Definitions (using ABC)
```python
# ports/browser.py
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from pathlib import Path

@runtime_checkable  # Enable isinstance checks
class IBrowser(Protocol):
    """Browser port - defines contract"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize browser"""
        ...
    
    @abstractmethod
    async def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        ...
    
    @abstractmethod
    async def extract_elements(self) -> List[Element]:
        """Extract page elements"""
        ...
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources"""
        ...
```

### Adapters (implementing ports)
```python
# adapters/browser/stealth.py
from typing import List
from pathlib import Path
from collections import deque
from functools import lru_cache
import sqlite3

class StealthBrowserAdapter:
    """Adapter implementing IBrowser port"""
    
    def __init__(self):
        self._history = deque(maxlen=100)  # collections.deque
        self._cache = {}
    
    @lru_cache(maxsize=128)  # functools caching
    def _get_cached_elements(self, url: str) -> List[Element]:
        """Cache extracted elements"""
        return self._cache.get(url, [])
    
    async def initialize(self) -> None:
        """Initialize stealth browser"""
        # Implementation
        pass
    
    async def navigate(self, url: str) -> bool:
        """Navigate with anti-bot measures"""
        self._history.append(url)
        # Implementation
        return True
    
    async def extract_elements(self) -> List[Element]:
        """Extract with shadow DOM support"""
        # Implementation
        return []
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        # Implementation
        pass
```

### Plugin System
```python
# plugins/loader.py
from pathlib import Path
from importlib import import_module
from typing import Dict, Any, Type
import tomllib  # Python 3.11+ for TOML
from functools import cache

class PluginLoader:
    """Dynamic plugin discovery and loading"""
    
    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.registry: Dict[str, Type] = {}
    
    @cache  # functools.cache for singleton
    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load TOML configuration"""
        with open(path, 'rb') as f:
            return tomllib.load(f)
    
    def discover_plugins(self, plugin_dir: Path) -> None:
        """Discover and register plugins"""
        for plugin_path in plugin_dir.glob("*.py"):
            if plugin_path.stem.startswith("_"):
                continue
            
            module = import_module(f"plugins.{plugin_path.stem}")
            
            # Register all classes implementing ports
            for name, obj in module.__dict__.items():
                if hasattr(obj, '__bases__'):
                    for port in self._get_ports():
                        if issubclass(obj, port):
                            self.register(name, obj)
    
    def register(self, name: str, adapter_class: Type) -> None:
        """Register adapter for a port"""
        self.registry[name] = adapter_class
    
    def get_adapter(self, port_name: str) -> Any:
        """Get adapter instance for port"""
        adapter_class = self.registry.get(port_name)
        if not adapter_class:
            raise ValueError(f"No adapter registered for {port_name}")
        return adapter_class()
```

### LangGraph Integration for Workflows
```python
# application/workflows.py
from langgraph import StateGraph, END
from typing import TypedDict, List
from itertools import chain, islice  # itertools for efficiency

class WorkflowState(TypedDict):
    """Workflow state using TypedDict"""
    url: str
    elements: List[Element]
    formatted: Dict[str, Any]
    tests: List[TestCase]
    errors: List[str]

def create_test_generation_workflow() -> StateGraph:
    """Create LangGraph workflow for test generation"""
    
    workflow = StateGraph(WorkflowState)
    
    # Define nodes
    workflow.add_node("extract", extract_elements)
    workflow.add_node("format", format_for_llm)
    workflow.add_node("generate", generate_tests)
    workflow.add_node("validate", validate_tests)
    
    # Define edges
    workflow.add_edge("extract", "format")
    workflow.add_edge("format", "generate")
    workflow.add_edge("generate", "validate")
    workflow.add_edge("validate", END)
    
    # Set entry point
    workflow.set_entry_point("extract")
    
    return workflow.compile()

async def extract_elements(state: WorkflowState) -> WorkflowState:
    """Extract elements node"""
    browser = plugin_loader.get_adapter("browser")
    await browser.navigate(state["url"])
    state["elements"] = await browser.extract_elements()
    return state

async def format_for_llm(state: WorkflowState) -> WorkflowState:
    """Format elements for LLM"""
    formatter = plugin_loader.get_adapter("formatter")
    state["formatted"] = formatter.format(state["elements"])
    return state

async def generate_tests(state: WorkflowState) -> WorkflowState:
    """Generate tests using LLM"""
    llm = plugin_loader.get_adapter("llm")
    strategy = plugin_loader.get_adapter("strategy")
    
    prompt = strategy.apply(state["formatted"])
    response = await llm.generate(prompt)
    state["tests"] = parse_tests(response)
    return state

async def validate_tests(state: WorkflowState) -> WorkflowState:
    """Validate generated tests"""
    # Use filter for validation
    valid_tests = list(filter(lambda t: t.validate(), state["tests"]))
    state["tests"] = valid_tests
    return state
```

### Configuration (TOML)
```toml
# config.toml
[framework]
version = "3.0.0"
plugin_dir = "plugins"

[browser]
adapter = "stealth"
headless = false
timeout = 30000

[storage]
adapter = "sqlite"
path = "data/extractions.db"

[llm]
adapter = "gemini"
model = "gemini-2.5-pro"
temperature = 0.7

[cache]
ttl = 3600
max_size = 1000

[logging]
level = "INFO"
format = "json"
```

### Pydantic V2 Integration
```python
# core/validators.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class ElementSchema(BaseModel):
    """Pydantic schema for validation"""
    selector: str = Field(..., min_length=1)
    tag_name: str = Field(..., min_length=1)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('selector')
    @classmethod
    def validate_selector(cls, v: str) -> str:
        """Validate CSS selector"""
        if not v.strip():
            raise ValueError('Selector cannot be empty')
        return v
    
    class Config:
        frozen = True  # Immutable

class TestCaseSchema(BaseModel):
    """Pydantic schema for test cases"""
    name: str = Field(..., min_length=1, max_length=200)
    steps: List[str] = Field(..., min_items=1)
    expected: List[str] = Field(..., min_items=1)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    created_at: datetime = Field(default_factory=datetime.now)
```

### Event-Driven Communication
```python
# infrastructure/events.py
from typing import Callable, Dict, List, Any
from collections import defaultdict
from functools import wraps
import secrets  # For secure event IDs

class EventBus:
    """Lightweight event bus using built-in modules"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._middleware: List[Callable] = []
    
    def on(self, event: str) -> Callable:
        """Decorator for event handlers"""
        def decorator(func: Callable) -> Callable:
            self._handlers[event].append(func)
            return func
        return decorator
    
    def emit(self, event: str, data: Any = None) -> str:
        """Emit event with unique ID"""
        event_id = secrets.token_hex(8)
        
        # Apply middleware
        for middleware in self._middleware:
            data = middleware(event, data)
        
        # Call handlers
        for handler in self._handlers[event]:
            handler(data, event_id=event_id)
        
        return event_id
    
    def use(self, middleware: Callable) -> None:
        """Add middleware for all events"""
        self._middleware.append(middleware)

# Usage
event_bus = EventBus()

@event_bus.on("extraction.complete")
def log_extraction(data, event_id):
    print(f"[{event_id}] Extracted {len(data['elements'])} elements")
```

## 🚀 Key Advantages

1. **Lean**: Only essential dependencies, built-in modules preferred
2. **Extensible**: Plugin architecture allows unlimited extension
3. **Modular**: Clear boundaries between layers
4. **DRY**: Shared contracts, single source of truth
5. **Testable**: Mock any port for testing
6. **Scalable**: Add adapters without touching core
7. **Maintainable**: Changes isolated to specific adapters

## 📦 Minimal Dependencies

### Built-in (Zero Cost):
- `dataclasses` - Data models
- `pathlib` - Path handling  
- `functools` - Caching
- `tomllib` - Configuration
- `collections` - Efficient data structures
- `itertools` - Iterator tools
- `sqlite3` - Storage
- `secrets` - Security
- `textwrap` - Text formatting

### Essential 3rd Party:
- `pydantic` - Validation
- `langgraph` - Workflow orchestration
- `playwright` - Browser automation

## 🔄 Migration Path

1. **Phase 1**: Core domain models and ports
2. **Phase 2**: Basic adapters (browser, storage)
3. **Phase 3**: Plugin system
4. **Phase 4**: LangGraph workflows
5. **Phase 5**: Full migration