# Improved Element Extraction Architecture

## Overview
A more intelligent, efficient, and maintainable architecture for web element extraction.

## Core Principles
1. **Data-Driven Configuration** - Profiles defined in YAML, not code
2. **Smart Storage** - SQLite for queryable results, with optional S3/cloud backup
3. **Intelligent Selection** - Auto-detect best profile based on page analysis
4. **Composable Filters** - Mix and match filters like LEGO blocks
5. **Streaming Pipeline** - Process elements as they're found, not all at once
6. **Caching & Deduplication** - Smart caching with content hashing

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Configuration Layer                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ profiles/   │  │ filters/     │  │ rules/       │  │
│  │ *.yaml      │  │ *.yaml       │  │ *.yaml       │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Intelligence Layer                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Profile     │  │ Page         │  │ Learning     │  │
│  │ Selector    │  │ Analyzer     │  │ Engine       │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Extraction Pipeline                    │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐    │
│  │Fetch │→│Parse │→│Filter│→│Score │→│Enrich│    │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Storage Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ SQLite DB   │  │ Cache        │  │ File System  │  │
│  │ (Primary)   │  │ (Redis/Mem)  │  │ (Backup)     │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 1. Configuration-Driven Profiles (YAML)

```yaml
# profiles/qa.yaml
name: qa
description: QA Engineer Profile
version: 1.0.0

filters:
  - interactive_only
  - min_size: 10
  - visible: true
  
scoring:
  weights:
    has_id: 0.2
    has_name: 0.3
    is_form_element: 0.5
    has_validation: 0.4
    
categories:
  - forms
  - navigation
  - actions
  
output:
  format: json
  compress: true
  include_screenshots: false
```

## 2. Composable Filter Pipeline

```python
from typing import Protocol, List, Iterator
from dataclasses import dataclass

class ElementFilter(Protocol):
    """Protocol for all filters"""
    def filter(self, element: Element) -> bool: ...
    def priority(self) -> int: ...

@dataclass
class FilterPipeline:
    """Composable filter pipeline"""
    filters: List[ElementFilter]
    
    def process(self, elements: Iterator[Element]) -> Iterator[Element]:
        """Stream processing with early termination"""
        for element in elements:
            if all(f.filter(element) for f in self.filters):
                yield element

# Usage - Compose filters dynamically
pipeline = FilterPipeline([
    InteractiveFilter(min_score=0.7),
    SizeFilter(min_width=10, min_height=10),
    VisibilityFilter(check_viewport=True),
    AccessibilityFilter(aria_required=True)
])
```

## 3. Intelligent Storage with SQLite

```python
# schema.sql
CREATE TABLE extractions (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    profile TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    content_hash TEXT,  -- For deduplication
    metadata JSON
);

CREATE TABLE elements (
    id INTEGER PRIMARY KEY,
    extraction_id INTEGER REFERENCES extractions(id),
    selector TEXT,
    tag_name TEXT,
    element_type TEXT,
    interaction_score REAL,
    attributes JSON,
    computed_style JSON,
    category TEXT
);

CREATE INDEX idx_url ON extractions(url);
CREATE INDEX idx_content_hash ON extractions(content_hash);
CREATE INDEX idx_element_type ON elements(element_type);
```

## 4. Smart Profile Selection

```python
class ProfileSelector:
    """Automatically select best profile based on page analysis"""
    
    def analyze_page(self, page: Page) -> PageCharacteristics:
        return PageCharacteristics(
            form_count=page.count("form"),
            input_count=page.count("input"),
            button_count=page.count("button"),
            has_aria=page.has_aria_attributes(),
            uses_framework=page.detect_framework(),
            is_spa=page.is_single_page_app()
        )
    
    def select_profile(self, characteristics: PageCharacteristics) -> str:
        scores = {}
        
        # Score each profile based on page characteristics
        if characteristics.form_count > 3:
            scores['qa'] = 0.9
        if characteristics.has_aria:
            scores['accessibility'] = 0.8
        if characteristics.is_spa:
            scores['interactive'] = 0.9
            
        return max(scores, key=scores.get, default='general')
```

## 5. Caching Strategy

```python
class ExtractionCache:
    """Smart caching with content-based invalidation"""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}  # Use Redis in production
        self.ttl = ttl
    
    def get_or_extract(self, url: str, profile: str) -> ExtractionResult:
        # Generate cache key from URL + profile + page content hash
        page_hash = self.get_page_hash(url)
        cache_key = f"{url}:{profile}:{page_hash}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Extract and cache
        result = self.extract(url, profile)
        self.cache[cache_key] = result
        return result
```

## 6. Incremental Extraction

```python
class IncrementalExtractor:
    """Only extract what changed since last run"""
    
    def extract_diff(self, url: str, profile: str) -> DiffResult:
        current = self.extract(url, profile)
        previous = self.storage.get_latest(url, profile)
        
        if not previous:
            return DiffResult(added=current.elements, removed=[], changed=[])
        
        # Compute diff
        added = current - previous
        removed = previous - current
        changed = self.detect_changes(current, previous)
        
        return DiffResult(added, removed, changed)
```

## 7. Profile Composition

```python
class CompositeProfile:
    """Combine multiple profiles"""
    
    def __init__(self, profiles: List[str]):
        self.profiles = profiles
    
    def extract(self, page: Page) -> ExtractionResult:
        results = {}
        
        # Run all profiles in parallel
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.run_profile, page, p): p 
                for p in self.profiles
            }
            
            for future in as_completed(futures):
                profile = futures[future]
                results[profile] = future.result()
        
        # Merge results intelligently
        return self.merge_results(results)
```

## 8. Event-Driven Architecture

```python
from typing import Callable
from enum import Enum

class ExtractionEvent(Enum):
    STARTED = "started"
    ELEMENT_FOUND = "element_found"
    ELEMENT_FILTERED = "element_filtered"
    COMPLETED = "completed"
    ERROR = "error"

class EventDrivenExtractor:
    """Reactive extraction with event hooks"""
    
    def __init__(self):
        self.listeners = defaultdict(list)
    
    def on(self, event: ExtractionEvent, callback: Callable):
        self.listeners[event].append(callback)
    
    def extract(self, url: str, profile: str):
        self.emit(ExtractionEvent.STARTED, {"url": url, "profile": profile})
        
        try:
            for element in self.stream_elements(url):
                self.emit(ExtractionEvent.ELEMENT_FOUND, element)
                
                if self.filter(element, profile):
                    self.emit(ExtractionEvent.ELEMENT_FILTERED, element)
                    yield element
                    
            self.emit(ExtractionEvent.COMPLETED)
        except Exception as e:
            self.emit(ExtractionEvent.ERROR, e)
```

## 9. Simple API for Common Use Cases

```python
# Simple one-liner for basic use
elements = extract("https://example.com")  # Auto-detects profile

# With options
elements = extract(
    "https://example.com",
    profile="qa",  # Or auto-detect
    cache=True,
    diff_only=True,
    stream=True
)

# Batch processing
results = extract_batch([
    "https://example1.com",
    "https://example2.com"
], parallel=True)

# Query historical data
history = query_extractions(
    url="https://example.com",
    date_range=("2024-01-01", "2024-12-31"),
    profile="qa"
)
```

## Benefits of This Architecture

1. **Simpler Configuration** - YAML files instead of Python classes
2. **Better Performance** - Streaming, caching, incremental extraction
3. **Smarter** - Auto-profile selection, learning from history
4. **More Flexible** - Compose profiles, event hooks, plugin system
5. **Better Storage** - Queryable SQLite, deduplication, compression
6. **Easier to Use** - Simple API for common cases, complex API for advanced
7. **Production Ready** - Monitoring, metrics, error recovery built-in

## Migration Path

1. Keep existing code as "v1"
2. Implement new architecture as "v2" in parallel
3. Provide compatibility layer
4. Gradually migrate profiles to YAML
5. Switch storage to SQLite with JSON export option