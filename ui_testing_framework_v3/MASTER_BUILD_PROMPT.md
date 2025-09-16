# Master Build Prompt: UI Testing Framework V3 - Hexagonal Plugin Architecture
## Autonomous System Generation Instructions

---

# SYSTEM CONTEXT AND VISION

You are tasked with building a production-grade UI Testing Framework using Hexagonal Architecture (Ports & Adapters pattern) with a plugin-first design. This system extracts web elements, formats them for various use cases, and generates comprehensive test cases using LLM integration.

## Critical Requirements
1. **ZERO external dependencies in core domain** - Use only Python built-ins for core
2. **Everything is a plugin** - Core only defines contracts
3. **QA-first mindset** - Think like a 30+ year senior QA engineer
4. **Production-ready** - Handle errors, scale, perform
5. **Fully testable** - 95%+ coverage achievable

---

# PHASE 0: PREPARATION AND VALIDATION

## Prerequisites Check
```python
# Verify Python 3.11+ (for tomllib)
import sys
assert sys.version_info >= (3, 11), "Python 3.11+ required"

# Verify directory structure
from pathlib import Path
project_root = Path("ui_testing_framework_v3")
assert not project_root.exists(), "Clean start required"
```

## Create Project Structure
```
ui_testing_framework_v3/
├── core/                 # Domain layer - ZERO external deps
├── ports/                # Interface definitions
├── adapters/             # Port implementations  
├── plugins/              # External plugins
├── application/          # Use cases & workflows
├── infrastructure/       # Cross-cutting concerns
├── api/                  # External interfaces
├── tests/                # Test suite
├── config/               # Configuration files
└── docs/                 # Documentation
```

---

# PHASE 1: CORE DOMAIN (Week 1, Days 1-2)

## Design Principles
1. **Immutability**: All domain models are immutable (frozen dataclasses)
2. **Pure Functions**: No side effects in domain logic
3. **Business Rules**: Encapsulated within domain models
4. **No Dependencies**: Only Python built-ins allowed

## Implementation Steps

### Step 1.1: Create Domain Models
```python
# core/models.py
"""
CRITICAL: This file MUST have ZERO imports except Python built-ins
Every field MUST be justified by business need
Every method MUST contain business logic, not technical logic
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from functools import cached_property
from enum import Enum

class ElementType(Enum):
    """Business classification of elements"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    SELECT = "select"
    TEXTAREA = "textarea"
    IMAGE = "image"
    TEXT = "text"
    CONTAINER = "container"

@dataclass(frozen=True)
class Element:
    """
    Immutable domain model representing a UI element
    
    Business Rules:
    - Element must have a unique selector
    - Interactive elements have higher test priority
    - Elements with ARIA labels are accessibility-compliant
    """
    selector: str
    tag_name: str
    element_type: ElementType
    attributes: Dict[str, Any] = field(default_factory=dict)
    text: Optional[str] = None
    
    def __post_init__(self):
        """Validate business rules on creation"""
        if not self.selector:
            raise ValueError("Element must have selector")
        if not self.tag_name:
            raise ValueError("Element must have tag_name")
    
    @cached_property
    def is_interactive(self) -> bool:
        """Business rule: Determine if element is interactive"""
        return self.element_type in [
            ElementType.BUTTON,
            ElementType.INPUT,
            ElementType.LINK,
            ElementType.SELECT,
            ElementType.TEXTAREA
        ]
    
    @cached_property
    def interaction_score(self) -> float:
        """
        Business logic: Calculate element importance for testing
        Score between 0.0 and 1.0
        """
        score = 0.0
        
        # Base score by type
        if self.element_type == ElementType.BUTTON:
            score += 0.4
        elif self.element_type == ElementType.INPUT:
            score += 0.35
        elif self.element_type == ElementType.LINK:
            score += 0.3
        elif self.element_type in [ElementType.SELECT, ElementType.TEXTAREA]:
            score += 0.25
        
        # Bonus for accessibility
        if self.attributes.get("aria-label"):
            score += 0.2
        if self.attributes.get("aria-describedby"):
            score += 0.1
        
        # Bonus for testability
        if self.attributes.get("id"):
            score += 0.15
        if self.attributes.get("data-testid"):
            score += 0.2
        
        return min(score, 1.0)
    
    @cached_property
    def test_priority(self) -> str:
        """Business rule: Determine test priority"""
        if self.interaction_score >= 0.7:
            return "high"
        elif self.interaction_score >= 0.4:
            return "medium"
        return "low"

@dataclass
class TestCase:
    """
    Domain model for test cases
    
    Business Rules:
    - Every test must have at least one step
    - Every test must have at least one assertion
    - High priority tests run first
    """
    name: str
    description: str
    steps: List[str]
    assertions: List[str]
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        """Business rule validation"""
        if not self.name:
            return False
        if len(self.steps) == 0:
            return False
        if len(self.assertions) == 0:
            return False
        if self.priority not in ["low", "medium", "high", "critical"]:
            return False
        return True
    
    def estimated_duration(self) -> int:
        """Business logic: Estimate test duration in seconds"""
        base_time = len(self.steps) * 2  # 2 seconds per step
        assertion_time = len(self.assertions) * 1  # 1 second per assertion
        
        # Complexity multiplier
        if self.priority == "critical":
            multiplier = 1.5
        elif self.priority == "high":
            multiplier = 1.2
        else:
            multiplier = 1.0
        
        return int((base_time + assertion_time) * multiplier)
```

### Step 1.2: Create Value Objects
```python
# core/value_objects.py
"""
Value objects are immutable and compared by value, not identity
They encapsulate validation and business logic for specific concepts
"""

from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class URL:
    """Value object for URLs with validation"""
    value: str
    
    def __post_init__(self):
        """Validate URL format"""
        if not self.value:
            raise ValueError("URL cannot be empty")
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(self.value):
            raise ValueError(f"Invalid URL format: {self.value}")
    
    @property
    def domain(self) -> str:
        """Extract domain from URL"""
        # Simple extraction without urllib
        parts = self.value.replace("http://", "").replace("https://", "").split("/")[0]
        return parts.split(":")[0]  # Remove port if present

@dataclass(frozen=True)
class CSSSelector:
    """Value object for CSS selectors with validation"""
    value: str
    
    def __post_init__(self):
        """Validate CSS selector"""
        if not self.value:
            raise ValueError("Selector cannot be empty")
        
        # Check for common invalid patterns
        invalid_patterns = ["javascript:", "<script", "onclick="]
        for pattern in invalid_patterns:
            if pattern in self.value.lower():
                raise ValueError(f"Invalid selector pattern: {pattern}")
    
    @property
    def specificity_score(self) -> int:
        """Calculate CSS specificity score"""
        score = 0
        # ID selectors
        score += self.value.count("#") * 100
        # Class selectors
        score += self.value.count(".") * 10
        # Element selectors (simplified)
        score += len([p for p in self.value.split() if not p.startswith(("#", ".", "["))])
        return score
```

### Step 1.3: Create Domain Exceptions
```python
# core/exceptions.py
"""
Domain-specific exceptions
These represent business rule violations, not technical errors
"""

class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class InvalidElementException(DomainException):
    """Raised when element violates business rules"""
    pass

class InvalidTestCaseException(DomainException):
    """Raised when test case is invalid"""
    pass

class ExtractionException(DomainException):
    """Raised when extraction fails due to business rules"""
    pass
```

## Validation Checkpoint 1
```python
# tests/test_core.py
"""
MUST PASS before proceeding to Phase 2
Tests domain logic without any external dependencies
"""

def test_element_immutability():
    """Elements cannot be modified after creation"""
    element = Element(selector="#test", tag_name="button", element_type=ElementType.BUTTON)
    with pytest.raises(AttributeError):
        element.selector = "#modified"

def test_interaction_score():
    """Business logic for scoring works correctly"""
    button = Element(
        selector="#submit",
        tag_name="button",
        element_type=ElementType.BUTTON,
        attributes={"id": "submit", "aria-label": "Submit form"}
    )
    assert button.interaction_score >= 0.7
    assert button.test_priority == "high"

def test_test_case_validation():
    """Test cases validate business rules"""
    invalid_test = TestCase(name="", steps=[], assertions=[])
    assert invalid_test.validate() == False
    
    valid_test = TestCase(
        name="Test login",
        description="Verify login functionality",
        steps=["Navigate to login", "Enter credentials", "Click submit"],
        assertions=["User is logged in", "Dashboard is visible"]
    )
    assert valid_test.validate() == True
```

---

# PHASE 2: PORTS (CONTRACTS) - Days 3-4

## Design Principles
1. **Protocol-based**: Use Python Protocol for runtime checking
2. **Minimal Interface**: Only essential methods
3. **Clear Contracts**: Explicit input/output types
4. **No Implementation**: Pure interfaces

### Step 2.1: Create Port Interfaces
```python
# ports/extractor.py
"""
Port for element extraction
This is a CONTRACT - implementations can vary but must honor this interface
"""

from typing import Protocol, List, runtime_checkable
from core.models import Element
from core.value_objects import URL

@runtime_checkable
class IExtractor(Protocol):
    """
    Contract for element extraction
    
    Implementers MUST:
    1. Extract elements from web pages
    2. Handle errors gracefully
    3. Support configuration
    """
    
    async def extract(self, url: URL) -> List[Element]:
        """
        Extract elements from URL
        
        Args:
            url: The URL to extract from
            
        Returns:
            List of extracted elements
            
        Raises:
            ExtractionException: On business logic errors
        """
        ...
    
    def supports_shadow_dom(self) -> bool:
        """Check if extractor supports shadow DOM"""
        ...
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get extractor capabilities"""
        ...

# ports/formatter.py
@runtime_checkable
class IFormatter(Protocol):
    """Contract for formatting extracted elements"""
    
    def format(self, elements: List[Element]) -> Dict[str, Any]:
        """
        Format elements for specific use case
        
        Args:
            elements: Elements to format
            
        Returns:
            Formatted data structure
        """
        ...
    
    @property
    def format_type(self) -> str:
        """Get format type identifier"""
        ...
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate formatted output meets requirements"""
        ...

# ports/test_generator.py
@runtime_checkable
class ITestGenerator(Protocol):
    """Contract for test generation"""
    
    async def generate(self, formatted_data: Dict[str, Any]) -> List[TestCase]:
        """
        Generate test cases from formatted data
        
        Args:
            formatted_data: Formatted element data
            
        Returns:
            List of generated test cases
        """
        ...
    
    def get_supported_types(self) -> List[str]:
        """Get supported test types"""
        ...

# ports/storage.py
@runtime_checkable
class IStorage(Protocol):
    """Contract for persistence"""
    
    async def save(self, key: str, data: Any) -> bool:
        """Save data with key"""
        ...
    
    async def load(self, key: str) -> Optional[Any]:
        """Load data by key"""
        ...
    
    async def delete(self, key: str) -> bool:
        """Delete data by key"""
        ...
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        ...
```

## Validation Checkpoint 2
```python
# Verify ports are properly defined
def test_port_contracts():
    """Ensure ports define clear contracts"""
    assert hasattr(IExtractor, 'extract')
    assert hasattr(IFormatter, 'format')
    assert hasattr(ITestGenerator, 'generate')
    
    # Verify runtime checkable
    class FakeExtractor:
        async def extract(self, url): return []
        def supports_shadow_dom(self): return False
        def get_capabilities(self): return {}
    
    assert isinstance(FakeExtractor(), IExtractor)
```

---

# PHASE 3: ADAPTERS (IMPLEMENTATIONS) - Days 5-7

## Design Principles
1. **Single Responsibility**: Each adapter does one thing
2. **Dependency Injection**: Dependencies passed via constructor
3. **Configuration-driven**: Behavior controlled by config
4. **Fail-safe**: Graceful degradation

### Step 3.1: Create Browser Adapter
```python
# adapters/browser/stealth.py
"""
Stealth browser adapter - implements IExtractor port
Uses the production-proven stealth browser
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import deque
from functools import lru_cache
import sqlite3
import secrets
import json

from core.models import Element, ElementType
from core.value_objects import URL, CSSSelector
from core.exceptions import ExtractionException
from ports.extractor import IExtractor

# Import production browser (copied from ui_testing_framework_prod)
from .browser import UltimateStealthBrowser

class StealthBrowserAdapter:
    """
    Production-grade browser adapter with anti-bot measures
    
    Features:
    - Stealth mode to avoid detection
    - Shadow DOM support
    - Intelligent waiting
    - Caching for performance
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize with configuration
        
        Config options:
        - headless: bool (default False for debugging)
        - timeout: int (milliseconds, default 30000)
        - cache_size: int (default 100)
        - anti_bot_level: str (minimum|medium|maximum)
        """
        self.config = config or {}
        self.browser = None
        self._cache = {}
        self._history = deque(maxlen=self.config.get('cache_size', 100))
        
        # Configuration with defaults
        self.headless = self.config.get('headless', False)  # ALWAYS default False
        self.timeout = self.config.get('timeout', 30000)
        self.anti_bot_level = self.config.get('anti_bot_level', 'maximum')
    
    async def initialize(self):
        """Initialize browser with stealth settings"""
        if not self.browser:
            self.browser = UltimateStealthBrowser(
                headless=self.headless,
                anti_bot_level=self.anti_bot_level
            )
            await self.browser.initialize()
    
    async def extract(self, url: URL) -> List[Element]:
        """
        Extract elements with QA focus
        
        Think like 30+ year senior QA engineer:
        1. What would break the application?
        2. What would users interact with?
        3. What needs accessibility testing?
        4. What has business impact?
        """
        # Check cache first
        cache_key = f"{url.value}:{self.anti_bot_level}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Initialize if needed
        await self.initialize()
        
        try:
            # Navigate with stealth
            await self.browser.navigate(url.value)
            
            # Extract with QA mindset
            elements = await self._extract_qa_focused_elements()
            
            # Cache results
            self._cache[cache_key] = elements
            self._history.append(url.value)
            
            return elements
            
        except Exception as e:
            raise ExtractionException(f"Failed to extract from {url.value}: {e}")
    
    async def _extract_qa_focused_elements(self) -> List[Element]:
        """
        Extract elements that matter for QA testing
        
        Priority order (QA mindset):
        1. Form inputs (data entry points)
        2. Buttons (action triggers)
        3. Links (navigation)
        4. Dropdowns (choices)
        5. Error messages (validation)
        6. Required fields (business rules)
        7. ARIA elements (accessibility)
        """
        elements = []
        
        # QA-critical selectors
        qa_selectors = [
            # Form inputs - highest priority for testing
            ('input[type="text"]', ElementType.INPUT, 0.9),
            ('input[type="email"]', ElementType.INPUT, 0.9),
            ('input[type="password"]', ElementType.INPUT, 0.95),
            ('input[type="submit"]', ElementType.BUTTON, 0.85),
            ('input[type="checkbox"]', ElementType.INPUT, 0.7),
            ('input[type="radio"]', ElementType.INPUT, 0.7),
            
            # Buttons - action triggers
            ('button', ElementType.BUTTON, 0.8),
            ('[role="button"]', ElementType.BUTTON, 0.75),
            ('.btn', ElementType.BUTTON, 0.75),
            
            # Textareas - long form input
            ('textarea', ElementType.TEXTAREA, 0.8),
            
            # Selects - choice validation
            ('select', ElementType.SELECT, 0.75),
            
            # Links - navigation testing
            ('a[href]', ElementType.LINK, 0.6),
            
            # Required fields - business rule validation
            ('[required]', ElementType.INPUT, 0.95),
            ('[aria-required="true"]', ElementType.INPUT, 0.95),
            
            # Error messages - validation testing
            ('.error', ElementType.TEXT, 0.9),
            ('[role="alert"]', ElementType.TEXT, 0.9),
            ('.validation-error', ElementType.TEXT, 0.9),
            
            # Accessibility elements
            ('[aria-label]', None, 0.7),  # Type determined by tag
            ('[aria-describedby]', None, 0.6),
        ]
        
        for selector, default_type, base_score in qa_selectors:
            try:
                raw_elements = await self.browser.query_selector_all(selector)
                
                for raw_elem in raw_elements:
                    # Get element details
                    tag_name = await raw_elem.tag_name()
                    attributes = await raw_elem.attributes()
                    text = await raw_elem.text_content()
                    
                    # Determine element type
                    if default_type:
                        element_type = default_type
                    else:
                        element_type = self._determine_element_type(tag_name)
                    
                    # Create element with QA scoring
                    element = Element(
                        selector=self._generate_selector(raw_elem, attributes),
                        tag_name=tag_name,
                        element_type=element_type,
                        attributes=attributes,
                        text=text[:100] if text else None  # Limit text length
                    )
                    
                    # Only include interactive or important elements
                    if element.interaction_score >= 0.3:
                        elements.append(element)
                        
            except Exception as e:
                # Log but continue - QA principle: gather what we can
                print(f"Warning: Failed to extract {selector}: {e}")
        
        # Deduplicate and sort by importance
        seen = set()
        unique_elements = []
        for elem in sorted(elements, key=lambda e: e.interaction_score, reverse=True):
            if elem.selector not in seen:
                seen.add(elem.selector)
                unique_elements.append(elem)
        
        return unique_elements[:100]  # Limit to top 100 most important
    
    def _generate_selector(self, element, attributes: Dict[str, Any]) -> str:
        """Generate the most reliable selector for an element"""
        # Priority: id > data-testid > aria-label > class > tag
        if attributes.get('id'):
            return f"#{attributes['id']}"
        if attributes.get('data-testid'):
            return f"[data-testid='{attributes['data-testid']}']"
        if attributes.get('aria-label'):
            return f"[aria-label='{attributes['aria-label']}']"
        if attributes.get('class'):
            classes = attributes['class'].split()[0]  # First class
            return f".{classes}"
        return element.tag_name
    
    def _determine_element_type(self, tag_name: str) -> ElementType:
        """Determine element type from tag name"""
        mapping = {
            'button': ElementType.BUTTON,
            'input': ElementType.INPUT,
            'a': ElementType.LINK,
            'select': ElementType.SELECT,
            'textarea': ElementType.TEXTAREA,
            'img': ElementType.IMAGE,
            'div': ElementType.CONTAINER,
            'span': ElementType.TEXT,
            'p': ElementType.TEXT,
        }
        return mapping.get(tag_name, ElementType.TEXT)
    
    def supports_shadow_dom(self) -> bool:
        """Check shadow DOM support"""
        return True
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get adapter capabilities"""
        return {
            'shadow_dom': True,
            'javascript': True,
            'screenshots': True,
            'cookies': True,
            'local_storage': True,
            'anti_bot': True,
            'headless': self.headless,
        }
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.cleanup()
            self.browser = None
```

### Step 3.2: Create Formatter Adapters
```python
# adapters/formatters/llm_test.py
"""
Formatter optimized for LLM test generation
Reduces tokens while preserving information
"""

from typing import List, Dict, Any
from collections import defaultdict
from ports.formatter import IFormatter
from core.models import Element

class LLMTestFormatter:
    """
    Format elements for efficient LLM consumption
    
    Optimizations:
    - Group by interaction type
    - Prioritize testable elements
    - Include test hints
    - Minimize token usage
    """
    
    @property
    def format_type(self) -> str:
        return "llm_test"
    
    def format(self, elements: List[Element]) -> Dict[str, Any]:
        """
        Format for LLM test generation
        
        Output structure optimized for prompting:
        - Grouped by test scenario
        - Includes interaction patterns
        - Provides test hints
        """
        # Group elements by interaction type
        grouped = defaultdict(list)
        for elem in elements:
            if elem.test_priority in ['high', 'critical']:
                grouped['critical_paths'].append(self._element_to_dict(elem))
            elif elem.element_type.value in ['input', 'textarea']:
                grouped['data_inputs'].append(self._element_to_dict(elem))
            elif elem.element_type.value == 'button':
                grouped['actions'].append(self._element_to_dict(elem))
            elif elem.element_type.value == 'link':
                grouped['navigation'].append(self._element_to_dict(elem))
            else:
                grouped['other'].append(self._element_to_dict(elem))
        
        # Generate test hints based on elements
        test_hints = self._generate_test_hints(elements)
        
        # Create optimized output
        return {
            'summary': {
                'total_elements': len(elements),
                'interactive_count': len([e for e in elements if e.is_interactive]),
                'high_priority_count': len([e for e in elements if e.test_priority in ['high', 'critical']]),
            },
            'test_targets': {
                'critical_paths': grouped['critical_paths'][:10],  # Top 10
                'data_inputs': grouped['data_inputs'][:15],
                'actions': grouped['actions'][:10],
                'navigation': grouped['navigation'][:5],
            },
            'test_hints': test_hints,
            'test_scenarios': self._generate_test_scenarios(grouped),
        }
    
    def _element_to_dict(self, element: Element) -> Dict[str, Any]:
        """Convert element to minimal dict for LLM"""
        return {
            'selector': element.selector,
            'type': element.element_type.value,
            'priority': element.test_priority,
            'attributes': {
                k: v for k, v in element.attributes.items()
                if k in ['id', 'name', 'aria-label', 'required', 'data-testid']
            },
            'text': element.text[:50] if element.text else None,
        }
    
    def _generate_test_hints(self, elements: List[Element]) -> List[str]:
        """Generate testing hints based on elements"""
        hints = []
        
        # Check for forms
        if any(e.element_type.value in ['input', 'button'] for e in elements):
            hints.append("Test form validation and submission")
        
        # Check for required fields
        if any(e.attributes.get('required') for e in elements):
            hints.append("Test required field validation")
        
        # Check for passwords
        if any(e.attributes.get('type') == 'password' for e in elements):
            hints.append("Test authentication flow and security")
        
        # Check for accessibility
        if any(e.attributes.get('aria-label') for e in elements):
            hints.append("Verify accessibility compliance")
        
        # Check for navigation
        if any(e.element_type.value == 'link' for e in elements):
            hints.append("Test navigation paths and broken links")
        
        return hints
    
    def _generate_test_scenarios(self, grouped: Dict[str, List]) -> List[Dict[str, str]]:
        """Generate test scenarios based on element groups"""
        scenarios = []
        
        if grouped['data_inputs'] and grouped['actions']:
            scenarios.append({
                'name': 'Form Submission Flow',
                'description': 'Test data input validation and form submission',
                'priority': 'high',
            })
        
        if grouped['navigation']:
            scenarios.append({
                'name': 'Navigation Testing',
                'description': 'Verify all navigation links work correctly',
                'priority': 'medium',
            })
        
        if grouped['critical_paths']:
            scenarios.append({
                'name': 'Critical Path Testing',
                'description': 'Test high-priority user journeys',
                'priority': 'critical',
            })
        
        return scenarios
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate formatted output"""
        required_keys = ['summary', 'test_targets', 'test_hints', 'test_scenarios']
        return all(key in output for key in required_keys)
```

### Step 3.3: Create Storage Adapter
```python
# adapters/storage/sqlite.py
"""
SQLite storage adapter - zero external dependencies
"""

import sqlite3
import json
import secrets
from typing import Optional, Any
from pathlib import Path
from datetime import datetime
from ports.storage import IStorage

class SQLiteAdapter:
    """
    SQLite storage using built-in sqlite3
    
    Features:
    - JSON serialization for complex data
    - Automatic cleanup of old data
    - Query capabilities
    """
    
    def __init__(self, db_path: str = "data/storage.db"):
        """Initialize with database path"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON storage(created_at)
            """)
    
    async def save(self, key: str, data: Any) -> bool:
        """Save data with key"""
        try:
            json_data = json.dumps(data)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO storage (key, data, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, json_data))
            
            return True
        except Exception as e:
            print(f"Storage save error: {e}")
            return False
    
    async def load(self, key: str) -> Optional[Any]:
        """Load data by key"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM storage WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return None
        except Exception as e:
            print(f"Storage load error: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete data by key"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM storage WHERE key = ?", (key,))
            return True
        except Exception as e:
            print(f"Storage delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM storage WHERE key = ? LIMIT 1",
                    (key,)
                )
                return cursor.fetchone() is not None
        except Exception:
            return False
```

## Validation Checkpoint 3
```python
# Verify adapters implement ports correctly
def test_adapter_contracts():
    """Ensure adapters fulfill port contracts"""
    
    # Test browser adapter
    browser = StealthBrowserAdapter()
    assert isinstance(browser, IExtractor)
    assert hasattr(browser, 'extract')
    assert hasattr(browser, 'supports_shadow_dom')
    
    # Test formatter adapter
    formatter = LLMTestFormatter()
    assert isinstance(formatter, IFormatter)
    assert formatter.format_type == "llm_test"
    
    # Test storage adapter
    storage = SQLiteAdapter()
    assert isinstance(storage, IStorage)
```

---

# PHASE 4: PLUGIN SYSTEM - Week 2, Days 1-2

### Step 4.1: Create Plugin Registry
```python
# plugins/registry.py
"""
Central plugin registry - the heart of extensibility
"""

from typing import Dict, Type, Any, Optional
from pathlib import Path
from collections import defaultdict
import tomllib
from functools import singledispatch, cache

class PluginRegistry:
    """
    Plugin registry with discovery and lifecycle management
    
    Features:
    - Auto-discovery of plugins
    - Singleton pattern for instances
    - Configuration injection
    - Hot-swapping support
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize registry with optional config"""
        self._registry: Dict[str, Dict[str, Type]] = defaultdict(dict)
        self._instances: Dict[str, Any] = {}
        self._config = self._load_config(config_path) if config_path else {}
    
    @cache
    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load TOML configuration"""
        with open(path, 'rb') as f:
            return tomllib.load(f)
    
    def register(self, port: str, adapter_class: Type, name: Optional[str] = None):
        """
        Register adapter for a port
        
        Args:
            port: Port name (e.g., 'extractor', 'formatter')
            adapter_class: Adapter class to register
            name: Optional name, defaults to class name
        """
        adapter_name = name or adapter_class.__name__
        self._registry[port][adapter_name] = adapter_class
        
        # Clear cached instance if exists (for hot-swapping)
        cache_key = f"{port}:{adapter_name}"
        if cache_key in self._instances:
            del self._instances[cache_key]
    
    def get(self, port: str, name: Optional[str] = None) -> Any:
        """
        Get adapter instance (singleton)
        
        Args:
            port: Port name
            name: Adapter name, uses default if not specified
            
        Returns:
            Adapter instance
        """
        # Determine adapter name
        if not name:
            # Use configured default
            name = self._config.get(port, {}).get('default')
            
            # Or first registered adapter
            if not name and port in self._registry:
                name = list(self._registry[port].keys())[0]
        
        if not name:
            raise ValueError(f"No adapter registered for port '{port}'")
        
        # Check cache
        cache_key = f"{port}:{name}"
        if cache_key in self._instances:
            return self._instances[cache_key]
        
        # Create new instance
        adapter_class = self._registry[port].get(name)
        if not adapter_class:
            available = list(self._registry[port].keys())
            raise ValueError(
                f"Adapter '{name}' not found for port '{port}'. "
                f"Available: {available}"
            )
        
        # Create with config
        port_config = self._config.get(port, {})
        instance = adapter_class(port_config)
        
        # Cache instance
        self._instances[cache_key] = instance
        
        return instance
    
    def list_adapters(self, port: str) -> List[str]:
        """List all registered adapters for a port"""
        return list(self._registry.get(port, {}).keys())
    
    def discover_plugins(self, plugin_dir: Path):
        """
        Auto-discover and register plugins from directory
        
        Plugins must:
        1. Be in plugin_dir
        2. Have a register() function
        3. Call registry.register() in register()
        """
        import importlib.util
        
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.stem.startswith("_"):
                continue
            
            # Load module
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem,
                plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Register if has register function
            if hasattr(module, 'register'):
                module.register(self)

# Global registry instance
registry = PluginRegistry()
```

---

# PHASE 5: APPLICATION LAYER - Days 3-4

### Step 5.1: Create Workflows with LangGraph
```python
# application/workflows.py
"""
LangGraph workflow orchestration
Complex workflows as directed graphs
"""

from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum
from langgraph import StateGraph, END
from itertools import chain

from core.models import Element, TestCase
from core.value_objects import URL
from plugins.registry import registry

class WorkflowState(TypedDict):
    """State passed through workflow"""
    url: str
    profile: str
    elements: List[Element]
    formatted: Dict[str, Any]
    tests: List[TestCase]
    errors: List[str]
    metadata: Dict[str, Any]

class TestGenerationWorkflow:
    """
    Complete test generation workflow
    
    Steps:
    1. Extract elements from URL
    2. Format for LLM consumption
    3. Generate test cases
    4. Validate tests
    5. Store results
    """
    
    def __init__(self):
        """Initialize workflow"""
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the workflow graph"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("extract", self._extract_elements)
        workflow.add_node("format", self._format_elements)
        workflow.add_node("generate", self._generate_tests)
        workflow.add_node("validate", self._validate_tests)
        workflow.add_node("store", self._store_results)
        
        # Add edges
        workflow.add_edge("extract", "format")
        workflow.add_edge("format", "generate")
        workflow.add_edge("generate", "validate")
        workflow.add_edge("validate", "store")
        workflow.add_edge("store", END)
        
        # Set entry point
        workflow.set_entry_point("extract")
        
        return workflow.compile()
    
    async def _extract_elements(self, state: WorkflowState) -> WorkflowState:
        """Extract elements using configured extractor"""
        try:
            # Get extractor based on profile
            extractor = registry.get("extractor", state['profile'])
            
            # Extract elements
            url = URL(state['url'])
            elements = await extractor.extract(url)
            
            state['elements'] = elements
            state['metadata']['extraction_count'] = len(elements)
            
        except Exception as e:
            state['errors'].append(f"Extraction failed: {e}")
        
        return state
    
    async def _format_elements(self, state: WorkflowState) -> WorkflowState:
        """Format elements for test generation"""
        try:
            # Get formatter
            formatter = registry.get("formatter", "llm_test")
            
            # Format elements
            formatted = formatter.format(
                state['elements'],
                {'url': state['url'], 'profile': state['profile']}
            )
            
            state['formatted'] = formatted
            
        except Exception as e:
            state['errors'].append(f"Formatting failed: {e}")
        
        return state
    
    async def _generate_tests(self, state: WorkflowState) -> WorkflowState:
        """Generate test cases"""
        try:
            # Get test generator
            generator = registry.get("test_generator")
            
            # Generate tests
            tests = await generator.generate(state['formatted'])
            
            state['tests'] = tests
            state['metadata']['test_count'] = len(tests)
            
        except Exception as e:
            state['errors'].append(f"Test generation failed: {e}")
        
        return state
    
    async def _validate_tests(self, state: WorkflowState) -> WorkflowState:
        """Validate generated tests"""
        # Filter valid tests
        valid_tests = [t for t in state['tests'] if t.validate()]
        invalid_count = len(state['tests']) - len(valid_tests)
        
        if invalid_count > 0:
            state['errors'].append(f"{invalid_count} invalid tests removed")
        
        state['tests'] = valid_tests
        state['metadata']['valid_test_count'] = len(valid_tests)
        
        return state
    
    async def _store_results(self, state: WorkflowState) -> WorkflowState:
        """Store results in configured storage"""
        try:
            # Get storage
            storage = registry.get("storage")
            
            # Create storage key
            key = f"test_generation:{state['url']}:{state['profile']}"
            
            # Store results
            await storage.save(key, {
                'url': state['url'],
                'profile': state['profile'],
                'tests': [self._test_to_dict(t) for t in state['tests']],
                'metadata': state['metadata'],
                'errors': state['errors'],
            })
            
        except Exception as e:
            state['errors'].append(f"Storage failed: {e}")
        
        return state
    
    def _test_to_dict(self, test: TestCase) -> Dict[str, Any]:
        """Convert test case to dictionary"""
        return {
            'name': test.name,
            'description': test.description,
            'steps': test.steps,
            'assertions': test.assertions,
            'priority': test.priority,
            'tags': test.tags,
            'estimated_duration': test.estimated_duration(),
        }
    
    async def run(self, url: str, profile: str = "qa") -> WorkflowState:
        """
        Run the complete workflow
        
        Args:
            url: URL to test
            profile: Extraction profile
            
        Returns:
            Final workflow state
        """
        initial_state = WorkflowState(
            url=url,
            profile=profile,
            elements=[],
            formatted={},
            tests=[],
            errors=[],
            metadata={}
        )
        
        final_state = await self.workflow.ainvoke(initial_state)
        return final_state
```

### Step 5.2: Create Pipeline for Simple Workflows
```python
# application/pipeline.py
"""
Simple pipeline for linear workflows
Alternative to LangGraph for simpler cases
"""

from typing import List, Tuple, Callable, Any, Dict
from plugins.registry import registry

class Pipeline:
    """
    Linear pipeline execution
    
    Simpler than LangGraph for straightforward workflows
    """
    
    def __init__(self, registry: PluginRegistry):
        """Initialize with registry"""
        self.registry = registry
        self.steps: List[Tuple[str, str, Optional[str]]] = []
    
    def add_step(
        self, 
        name: str, 
        port: str, 
        adapter: Optional[str] = None
    ) -> 'Pipeline':
        """
        Add step to pipeline
        
        Args:
            name: Step name for logging
            port: Port to use
            adapter: Specific adapter, or use default
            
        Returns:
            Self for chaining
        """
        self.steps.append((name, port, adapter))
        return self
    
    async def run(self, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run pipeline with initial data
        
        Args:
            initial_data: Starting data
            
        Returns:
            Final data after all steps
        """
        data = initial_data.copy()
        
        for step_name, port, adapter in self.steps:
            print(f"[Pipeline] Executing: {step_name}")
            
            try:
                # Get adapter
                adapter_instance = self.registry.get(port, adapter)
                
                # Execute based on port type
                if port == "extractor":
                    data['elements'] = await adapter_instance.extract(
                        URL(data['url'])
                    )
                
                elif port == "formatter":
                    data['formatted'] = adapter_instance.format(
                        data['elements']
                    )
                
                elif port == "test_generator":
                    data['tests'] = await adapter_instance.generate(
                        data['formatted']
                    )
                
                print(f"  [OK] {step_name} completed")
                
            except Exception as e:
                print(f"  [ERROR] {step_name} failed: {e}")
                data.setdefault('errors', []).append(str(e))
        
        return data
```

---

# PHASE 6: INFRASTRUCTURE - Days 5-6

### Step 6.1: Configuration Management
```python
# infrastructure/config.py
"""
Configuration management using TOML
"""

import tomllib
from pathlib import Path
from typing import Dict, Any, Optional
from functools import cache

class ConfigManager:
    """
    Centralized configuration management
    
    Features:
    - TOML-based configuration
    - Environment override support
    - Validation
    - Caching
    """
    
    def __init__(self, config_path: Path = Path("config/config.toml")):
        """Initialize with config path"""
        self.config_path = config_path
        self._config = self._load_config()
    
    @cache
    def _load_config(self) -> Dict[str, Any]:
        """Load and validate configuration"""
        if not self.config_path.exists():
            # Return defaults if no config
            return self._get_defaults()
        
        with open(self.config_path, 'rb') as f:
            config = tomllib.load(f)
        
        # Validate configuration
        self._validate_config(config)
        
        return config
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'browser': {
                'headless': False,  # ALWAYS False for debugging
                'timeout': 30000,
                'max_instances': 3,
                'anti_bot_level': 'maximum',
            },
            'extraction': {
                'default_profile': 'qa',
                'cache_size': 100,
                'max_elements': 100,
            },
            'storage': {
                'type': 'sqlite',
                'path': 'data/storage.db',
                'cleanup_days': 30,
            },
            'logging': {
                'level': 'INFO',
                'format': 'json',
            },
        }
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration"""
        # Ensure headless is False
        if config.get('browser', {}).get('headless', False):
            print("WARNING: headless=True detected, overriding to False")
            config['browser']['headless'] = False
        
        # Validate required sections
        required = ['browser', 'extraction', 'storage']
        for section in required:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get config value by dot notation
        
        Example: config.get('browser.timeout', 30000)
        """
        keys = path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
```

### Step 6.2: Event Bus
```python
# infrastructure/events.py
"""
Event-driven communication between components
"""

from typing import Callable, Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime
import secrets

class EventBus:
    """
    Lightweight event bus for decoupled communication
    
    Features:
    - Publish/subscribe pattern
    - Event middleware
    - Event history
    - Type-safe events
    """
    
    def __init__(self):
        """Initialize event bus"""
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._middleware: List[Callable] = []
        self._history: List[Dict[str, Any]] = []
    
    def on(self, event_type: str) -> Callable:
        """
        Decorator to register event handler
        
        Usage:
            @event_bus.on('extraction.complete')
            def handle_extraction(data):
                print(f"Extracted {data['count']} elements")
        """
        def decorator(handler: Callable) -> Callable:
            self._handlers[event_type].append(handler)
            return handler
        return decorator
    
    def emit(self, event_type: str, data: Any = None) -> str:
        """
        Emit an event
        
        Args:
            event_type: Event type
            data: Event data
            
        Returns:
            Event ID for tracking
        """
        # Generate event ID
        event_id = secrets.token_hex(8)
        
        # Create event record
        event = {
            'id': event_id,
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Apply middleware
        for middleware in self._middleware:
            data = middleware(event_type, data)
        
        # Store in history
        self._history.append(event)
        
        # Call handlers
        for handler in self._handlers[event_type]:
            try:
                handler(data, event_id=event_id)
            except Exception as e:
                print(f"Event handler error: {e}")
        
        return event_id
    
    def use(self, middleware: Callable):
        """Add middleware for all events"""
        self._middleware.append(middleware)
    
    def get_history(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get event history"""
        if event_type:
            return [e for e in self._history if e['type'] == event_type]
        return self._history.copy()

# Global event bus
event_bus = EventBus()
```

---

# PHASE 7: EXTERNAL API - Days 7

### Step 7.1: CLI Interface
```python
# api/cli.py
"""
Command-line interface for the framework
"""

import asyncio
from pathlib import Path
from typing import Optional
import json

from plugins.registry import registry
from application.workflows import TestGenerationWorkflow
from infrastructure.config import ConfigManager
from infrastructure.events import event_bus

class CLI:
    """
    Command-line interface
    
    Commands:
    - extract: Extract elements from URL
    - generate: Generate test cases
    - list: List available plugins
    """
    
    def __init__(self):
        """Initialize CLI"""
        self.config = ConfigManager()
        self._setup_registry()
        self._setup_events()
    
    def _setup_registry(self):
        """Setup plugin registry"""
        # Register built-in adapters
        from adapters.browser.stealth import StealthBrowserAdapter
        from adapters.formatters.llm_test import LLMTestFormatter
        from adapters.storage.sqlite import SQLiteAdapter
        
        registry.register("extractor", StealthBrowserAdapter, "stealth")
        registry.register("formatter", LLMTestFormatter, "llm_test")
        registry.register("storage", SQLiteAdapter, "sqlite")
        
        # Discover external plugins
        plugin_dir = Path("plugins")
        if plugin_dir.exists():
            registry.discover_plugins(plugin_dir)
    
    def _setup_events(self):
        """Setup event handlers"""
        @event_bus.on('extraction.complete')
        def log_extraction(data, event_id):
            print(f"[{event_id}] Extraction complete: {data['count']} elements")
        
        @event_bus.on('test.generated')
        def log_test_generation(data, event_id):
            print(f"[{event_id}] Generated {data['count']} tests")
    
    async def extract(self, url: str, profile: str = "qa") -> List[Element]:
        """Extract elements from URL"""
        extractor = registry.get("extractor", profile)
        elements = await extractor.extract(URL(url))
        
        # Emit event
        event_bus.emit('extraction.complete', {'count': len(elements), 'url': url})
        
        return elements
    
    async def generate_tests(self, url: str, profile: str = "qa") -> Dict[str, Any]:
        """Generate test cases for URL"""
        workflow = TestGenerationWorkflow()
        result = await workflow.run(url, profile)
        
        # Emit event
        event_bus.emit('test.generated', {
            'count': len(result['tests']),
            'url': url,
            'profile': profile
        })
        
        return result
    
    def list_plugins(self) -> Dict[str, List[str]]:
        """List available plugins"""
        ports = ["extractor", "formatter", "test_generator", "storage"]
        plugins = {}
        
        for port in ports:
            plugins[port] = registry.list_adapters(port)
        
        return plugins
    
    async def run(self, command: str, **kwargs):
        """Run CLI command"""
        commands = {
            'extract': self.extract,
            'generate': self.generate_tests,
            'list': lambda: self.list_plugins(),
        }
        
        if command not in commands:
            print(f"Unknown command: {command}")
            print(f"Available: {list(commands.keys())}")
            return
        
        result = await commands[command](**kwargs)
        
        # Output result
        if isinstance(result, (list, dict)):
            print(json.dumps(result, indent=2, default=str))
        else:
            print(result)

# Main entry point
async def main():
    """CLI main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m ui_testing_framework_v3 <command> [options]")
        return
    
    command = sys.argv[1]
    cli = CLI()
    
    if command == "extract":
        if len(sys.argv) < 3:
            print("Usage: extract <url> [profile]")
            return
        url = sys.argv[2]
        profile = sys.argv[3] if len(sys.argv) > 3 else "qa"
        await cli.run("extract", url=url, profile=profile)
    
    elif command == "generate":
        if len(sys.argv) < 3:
            print("Usage: generate <url> [profile]")
            return
        url = sys.argv[2]
        profile = sys.argv[3] if len(sys.argv) > 3 else "qa"
        await cli.run("generate", url=url, profile=profile)
    
    elif command == "list":
        await cli.run("list")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

# PHASE 8: TESTING SUITE - Days 8-9

### Step 8.1: Unit Tests
```python
# tests/test_unit.py
"""
Unit tests for all components
Target: 95% coverage
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

# Test core domain
def test_element_creation():
    """Test element creation and validation"""
    from core.models import Element, ElementType
    
    element = Element(
        selector="#test",
        tag_name="button",
        element_type=ElementType.BUTTON,
        attributes={"id": "test", "aria-label": "Test Button"}
    )
    
    assert element.selector == "#test"
    assert element.is_interactive == True
    assert element.interaction_score > 0.5
    assert element.test_priority == "high"

def test_element_immutability():
    """Test that elements are immutable"""
    from core.models import Element, ElementType
    
    element = Element(
        selector="#test",
        tag_name="button",
        element_type=ElementType.BUTTON
    )
    
    with pytest.raises(AttributeError):
        element.selector = "#modified"

def test_test_case_validation():
    """Test case validation rules"""
    from core.models import TestCase
    
    # Invalid test case
    invalid = TestCase(
        name="",
        description="",
        steps=[],
        assertions=[]
    )
    assert invalid.validate() == False
    
    # Valid test case
    valid = TestCase(
        name="Test Login",
        description="Verify login works",
        steps=["Navigate to login", "Enter credentials", "Submit"],
        assertions=["User is logged in", "Dashboard visible"],
        priority="high"
    )
    assert valid.validate() == True
    assert valid.estimated_duration() > 0

# Test ports
def test_port_contracts():
    """Test that ports are properly defined"""
    from ports.extractor import IExtractor
    from ports.formatter import IFormatter
    from ports.test_generator import ITestGenerator
    from ports.storage import IStorage
    
    # Verify protocols are runtime checkable
    assert hasattr(IExtractor, '__subclasshook__')
    assert hasattr(IFormatter, '__subclasshook__')
    assert hasattr(ITestGenerator, '__subclasshook__')
    assert hasattr(IStorage, '__subclasshook__')

# Test adapters
@pytest.mark.asyncio
async def test_stealth_browser_adapter():
    """Test browser adapter"""
    from adapters.browser.stealth import StealthBrowserAdapter
    from core.value_objects import URL
    
    # Mock browser
    with patch('adapters.browser.stealth.UltimateStealthBrowser') as MockBrowser:
        mock_browser = AsyncMock()
        MockBrowser.return_value = mock_browser
        
        adapter = StealthBrowserAdapter({'headless': False})
        
        # Test initialization
        assert adapter.headless == False
        assert adapter.supports_shadow_dom() == True
        
        # Test capabilities
        caps = adapter.get_capabilities()
        assert caps['anti_bot'] == True
        assert caps['headless'] == False

def test_llm_formatter():
    """Test LLM formatter"""
    from adapters.formatters.llm_test import LLMTestFormatter
    from core.models import Element, ElementType
    
    formatter = LLMTestFormatter()
    
    elements = [
        Element(
            selector="#username",
            tag_name="input",
            element_type=ElementType.INPUT,
            attributes={"id": "username", "required": "true"}
        ),
        Element(
            selector="#submit",
            tag_name="button",
            element_type=ElementType.BUTTON,
            attributes={"id": "submit"}
        )
    ]
    
    result = formatter.format(elements)
    
    assert 'summary' in result
    assert 'test_targets' in result
    assert 'test_hints' in result
    assert result['summary']['total_elements'] == 2
    assert result['summary']['interactive_count'] == 2

# Test plugin registry
def test_plugin_registry():
    """Test plugin registration and retrieval"""
    from plugins.registry import PluginRegistry
    
    registry = PluginRegistry()
    
    # Register adapter
    class TestAdapter:
        def __init__(self, config):
            self.config = config
    
    registry.register("test_port", TestAdapter, "test_adapter")
    
    # Retrieve adapter
    adapter = registry.get("test_port", "test_adapter")
    assert isinstance(adapter, TestAdapter)
    
    # List adapters
    adapters = registry.list_adapters("test_port")
    assert "test_adapter" in adapters
    
    # Test singleton pattern
    adapter2 = registry.get("test_port", "test_adapter")
    assert adapter is adapter2  # Same instance

# Test workflows
@pytest.mark.asyncio
async def test_workflow_execution():
    """Test workflow execution"""
    from application.workflows import TestGenerationWorkflow, WorkflowState
    
    workflow = TestGenerationWorkflow()
    
    # Mock registry
    with patch('application.workflows.registry') as mock_registry:
        # Setup mocks
        mock_extractor = AsyncMock()
        mock_extractor.extract.return_value = []
        
        mock_formatter = Mock()
        mock_formatter.format.return_value = {}
        
        mock_generator = AsyncMock()
        mock_generator.generate.return_value = []
        
        mock_storage = AsyncMock()
        mock_storage.save.return_value = True
        
        mock_registry.get.side_effect = lambda port, name=None: {
            'extractor': mock_extractor,
            'formatter': mock_formatter,
            'test_generator': mock_generator,
            'storage': mock_storage,
        }.get(port)
        
        # Run workflow
        result = await workflow.run("https://example.com", "qa")
        
        assert result['url'] == "https://example.com"
        assert result['profile'] == "qa"
        assert 'elements' in result
        assert 'tests' in result

# Test infrastructure
def test_config_manager():
    """Test configuration management"""
    from infrastructure.config import ConfigManager
    
    # Test with defaults (no config file)
    config = ConfigManager(Path("nonexistent.toml"))
    
    # Check defaults
    assert config.get('browser.headless') == False
    assert config.get('browser.timeout') == 30000
    assert config.get('extraction.default_profile') == 'qa'
    
    # Test dot notation
    assert config.get('browser.anti_bot_level', 'default') == 'maximum'

def test_event_bus():
    """Test event bus"""
    from infrastructure.events import EventBus
    
    bus = EventBus()
    
    # Track events
    received = []
    
    @bus.on('test.event')
    def handler(data, event_id):
        received.append((data, event_id))
    
    # Emit event
    event_id = bus.emit('test.event', {'value': 42})
    
    assert len(received) == 1
    assert received[0][0] == {'value': 42}
    assert received[0][1] == event_id
    
    # Check history
    history = bus.get_history('test.event')
    assert len(history) == 1
    assert history[0]['data'] == {'value': 42}
```

### Step 8.2: Integration Tests
```python
# tests/test_integration.py
"""
Integration tests for complete workflows
"""

import pytest
import asyncio
from pathlib import Path

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_extraction_pipeline():
    """Test complete extraction pipeline"""
    from api.cli import CLI
    
    cli = CLI()
    
    # Test extraction
    elements = await cli.extract("https://example.com", "qa")
    assert isinstance(elements, list)
    
    # Test plugin listing
    plugins = cli.list_plugins()
    assert 'extractor' in plugins
    assert 'formatter' in plugins

@pytest.mark.integration
@pytest.mark.asyncio
async def test_test_generation_workflow():
    """Test complete test generation workflow"""
    from application.workflows import TestGenerationWorkflow
    
    workflow = TestGenerationWorkflow()
    
    # Run workflow
    result = await workflow.run("https://example.com", "qa")
    
    assert 'tests' in result
    assert 'errors' in result
    assert 'metadata' in result

@pytest.mark.integration
def test_plugin_discovery():
    """Test plugin auto-discovery"""
    from plugins.registry import PluginRegistry
    
    # Create test plugin
    plugin_dir = Path("test_plugins")
    plugin_dir.mkdir(exist_ok=True)
    
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text("""
def register(registry):
    class TestPlugin:
        def __init__(self, config):
            pass
    
    registry.register("test_port", TestPlugin, "discovered")
    """)
    
    try:
        # Discover plugins
        registry = PluginRegistry()
        registry.discover_plugins(plugin_dir)
        
        # Verify discovered
        adapters = registry.list_adapters("test_port")
        assert "discovered" in adapters
        
    finally:
        # Cleanup
        plugin_file.unlink()
        plugin_dir.rmdir()
```

---

# PHASE 9: CONFIGURATION FILES

### Step 9.1: Main Configuration
```toml
# config/config.toml
# UI Testing Framework V3 Configuration

[framework]
version = "3.0.0"
name = "UI Testing Framework V3"

[browser]
default = "stealth"
headless = false  # ALWAYS false for debugging
timeout = 30000
max_instances = 3
anti_bot_level = "maximum"
shadow_dom_enabled = true
shadow_dom_max_depth = 5

[extraction]
default_profile = "qa"  # QA-first mindset
cache_size = 100
max_elements = 100
cache_ttl = 3600

[formatter]
default = "llm_test"
token_optimization = true
max_tokens = 4000

[test_generator]
default = "llm"
provider = "gemini"
model = "gemini-2.5-pro"
temperature = 0.7
max_tests_per_page = 20

[storage]
default = "sqlite"
type = "sqlite"
path = "data/storage.db"
cleanup_days = 30
deduplication = true

[logging]
level = "INFO"
format = "json"
file = "logs/framework.log"
max_size = "10MB"
max_files = 5

[events]
history_size = 1000
emit_metrics = true

[performance]
enable_profiling = false
cache_strategy = "lru"
async_timeout = 60
```

### Step 9.2: Docker Support
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Playwright
RUN npx playwright install-deps chromium

WORKDIR /app

# Copy framework
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    playwright \
    langgraph \
    pydantic

# Initialize Playwright
RUN playwright install chromium

# Create data directories
RUN mkdir -p data logs

# Run
CMD ["python", "-m", "ui_testing_framework_v3"]
```

---

# FINAL VALIDATION CHECKLIST

## Architecture Requirements ✓
- [ ] Zero dependencies in core domain
- [ ] All components are plugins
- [ ] Ports define clear contracts
- [ ] Adapters implement ports correctly
- [ ] Plugin registry works with hot-swapping
- [ ] LangGraph workflows execute properly
- [ ] Event bus enables decoupled communication
- [ ] Configuration is centralized

## Quality Requirements ✓
- [ ] 95%+ test coverage achievable
- [ ] All business logic in domain
- [ ] No technical logic in domain
- [ ] Clear separation of concerns
- [ ] Single responsibility per component
- [ ] Dependency injection used
- [ ] Immutable domain models
- [ ] Pure functions where possible

## Performance Requirements ✓
- [ ] Built-in modules used (functools, itertools, collections)
- [ ] Caching implemented (@lru_cache, @cache)
- [ ] Async/await for I/O operations
- [ ] Connection pooling for browsers
- [ ] Efficient data structures (deque, defaultdict)

## Production Requirements ✓
- [ ] Error handling at every level
- [ ] Graceful degradation
- [ ] Comprehensive logging
- [ ] Metrics and monitoring
- [ ] Configuration validation
- [ ] Resource cleanup
- [ ] Security considerations
- [ ] Docker support

---

# EXECUTION INSTRUCTIONS FOR LLM AGENT

1. **Create directory structure EXACTLY as specified**
2. **Implement in EXACT phase order - no skipping**
3. **Run validation checkpoint after EACH phase**
4. **Use ONLY built-in modules in core domain**
5. **Ensure headless=False ALWAYS**
6. **Think like 30+ year senior QA engineer**
7. **Test everything - no assumptions**
8. **Document all decisions**
9. **Handle all errors gracefully**
10. **Optimize for production use**

## Critical Success Factors
1. **Domain purity** - Zero external dependencies in core
2. **Plugin architecture** - Everything pluggable
3. **QA mindset** - Extract what matters for testing
4. **Production ready** - Handle scale and errors
5. **Fully tested** - 95% coverage minimum

## Expected Deliverables
1. Complete working system
2. All tests passing
3. Documentation complete
4. Configuration files
5. CLI interface working
6. Plugin examples
7. Integration tests
8. Performance benchmarks

---

# START BUILDING NOW

Begin with Phase 1, Step 1.1. Create the directory structure first, then implement core/models.py EXACTLY as specified. Proceed step by step, validating each phase before moving to the next.

Remember: You are building a PRODUCTION system that will be used by QA engineers with 30+ years of experience. Quality, reliability, and extensibility are non-negotiable.