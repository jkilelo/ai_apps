# Prompts V2 API Documentation

## Overview

`prompts_v2.py` is a production-ready, type-safe implementation of all 21 master prompt strategies that uses `.md` files from `master_prompt_strategies/` as the single source of truth. It provides seamless integration with `llm.py` through a compatibility adapter.

## Key Features

- **21 Research-Backed Strategies**: All strategies from master_prompt_strategies
- **Pydantic V2 Type Enforcement**: Strict type checking and validation
- **Single Source of Truth**: Prompts loaded directly from .md files
- **Caching System**: LRU cache for performance optimization
- **Factory Pattern**: Clean strategy selection and instantiation
- **LLM.py Integration**: Drop-in replacement compatibility
- **Error Handling**: Graceful fallbacks with detailed warnings

## Architecture

```
prompts_v2.py
├── Data Models (Pydantic V2)
│   ├── PromptMetadata
│   ├── PromptTemplate
│   ├── StrategyRequest
│   └── StrategyResponse
├── MD File Parser
│   └── MDFileParser
├── Strategy System
│   ├── IPromptStrategy (Protocol)
│   ├── BasePromptStrategy (Abstract)
│   └── Concrete Strategies (21)
├── Factory
│   └── StrategyFactory
├── Main Engine
│   └── PromptEngineV2
└── Compatibility Layer
    └── LLMCompatibilityAdapter
```

## Quick Start

### Basic Usage

```python
from prompts_v2 import generate_prompt, StrategyType

# Simple usage
prompt = generate_prompt("Explain quantum computing")
print(prompt)

# With specific strategy
prompt = generate_prompt(
    "Design a REST API", 
    strategy="tree_of_thoughts"
)
```

### Advanced Usage

```python
from prompts_v2 import PromptEngineV2, StrategyRequest, TaskCategory, ComplexityLevel

# Initialize engine
engine = PromptEngineV2()

# Create detailed request
request = StrategyRequest(
    task="Create a secure authentication system",
    category=TaskCategory.GENERATION,
    complexity=ComplexityLevel.COMPLEX,
    requirements=[
        "Use JWT tokens",
        "Implement refresh tokens",
        "Add rate limiting"
    ],
    examples=["Auth0 style API", "Firebase Auth pattern"]
)

# Generate prompt
response = engine.generate(request)
print(f"Strategy: {response.strategy_used.value}")
print(f"Confidence: {response.confidence:.2%}")
print(f"Prompt: {response.prompt[:500]}...")
```

## API Reference

### Core Classes

#### `PromptEngineV2`

Main engine for prompt generation.

```python
class PromptEngineV2:
    def __init__(
        self, 
        strategies_dir: Optional[Path] = None,
        cache_enabled: bool = True,
        max_cache_size: int = 1000
    )
    
    def generate(
        self, 
        request: Union[StrategyRequest, Dict, str]
    ) -> StrategyResponse
    
    def generate_batch(
        self, 
        requests: List[Union[StrategyRequest, Dict, str]]
    ) -> List[StrategyResponse]
    
    def get_stats(self) -> Dict[str, Any]
    
    def clear_cache(self) -> None
```

#### `StrategyRequest`

Request model with Pydantic V2 validation.

```python
class StrategyRequest(BaseModel):
    task: str  # Min 10 chars, max 10000
    strategy: Optional[StrategyType] = None
    category: Optional[TaskCategory] = None
    complexity: ComplexityLevel = ComplexityLevel.MODERATE
    context: Dict[str, Any] = {}
    requirements: List[str] = []
    examples: List[str] = []
    max_tokens: int = 4000  # 100-100000
    temperature: float = 0.7  # 0.0-2.0
```

#### `StrategyResponse`

Response model with metadata and metrics.

```python
class StrategyResponse(BaseModel):
    prompt: str  # Min 50 chars
    strategy_used: StrategyType
    confidence: float  # 0.0-1.0
    metadata: PromptMetadata
    rendering_time_ms: float
    cache_hit: bool = False
    warnings: List[str] = []
    
    @property
    def quality_score(self) -> float
```

### Enums

#### `StrategyType`

All 21 available strategies:

- `CHAIN_OF_THOUGHT`
- `TREE_OF_THOUGHTS`
- `REACT`
- `CONSTITUTIONAL_AI`
- `SELF_CONSISTENCY`
- `META_PROMPTING`
- `DEBATE`
- `REFLEXION`
- `SCRATCHPAD`
- `FEW_SHOT`
- `ZERO_SHOT`
- `OPRO`
- `MIXTURE_OF_EXPERTS`
- `QUANTUM_PROMPTING`
- `REVERSE_PROMPTING`
- `EVOLUTIONARY_OPTIMIZATION`
- `PSYCHOLOGICAL_TRIGGERS`
- `UNIVERSAL_SELF_CONSISTENCY`
- `PROGRAM_AIDED_LANGUAGE`
- `CHAIN_OF_TABLE`
- `META_COGNITIVE_FRAMEWORK`

#### `TaskCategory`

Task categorization for automatic strategy selection:

- `REASONING`
- `CREATIVE`
- `ANALYTICAL`
- `EXTRACTION`
- `GENERATION`
- `VALIDATION`
- `OPTIMIZATION`
- `CLASSIFICATION`
- `SUMMARIZATION`
- `TRANSLATION`
- `TESTING`
- `DEBUGGING`
- `PLANNING`
- `EXECUTION`

#### `ComplexityLevel`

Task complexity levels:

- `TRIVIAL` (1)
- `SIMPLE` (2)
- `MODERATE` (3)
- `COMPLEX` (4)
- `VERY_COMPLEX` (5)
- `PARADOXICAL` (6)

### Convenience Functions

```python
# Get or create global engine
def get_engine() -> PromptEngineV2

# Generate prompt with simple interface
def generate_prompt(
    task: str,
    strategy: Optional[str] = None,
    **kwargs: Any
) -> str

# List all available strategies
def list_strategies() -> List[str]
```

## Integration with llm.py

### Using the Compatibility Adapter

```python
from prompts_v2 import LLMCompatibilityAdapter

# Initialize adapter
adapter = LLMCompatibilityAdapter()

# Enhance messages (compatible with llm.py)
messages = [
    {"role": "user", "content": "Explain machine learning"}
]

enhanced = adapter.enhance_messages(
    messages, 
    strategy="chain_of_thought"
)

# Use with llm.py
from llm import call_default_llm
response = call_default_llm(enhanced)
```

### Direct Replacement in llm.py

To replace the existing prompt system in `llm.py`:

```python
# In llm.py, replace existing strategy methods with:
from prompts_v2 import LLMCompatibilityAdapter

class LLMProvider:
    def __init__(self):
        self.prompt_adapter = LLMCompatibilityAdapter()
    
    def query_llm(self, messages, strategy=None, **kwargs):
        # Enhance messages with prompts_v2
        if strategy:
            messages = self.prompt_adapter.enhance_messages(
                messages, strategy=strategy
            )
        # Continue with LLM call...
```

## Automatic Strategy Selection

The engine automatically selects the best strategy based on task characteristics:

```python
# Auto-detection based on task content
request = StrategyRequest(
    task="Generate unit tests for a login function"
)
# Will auto-select: SELF_CONSISTENCY (for testing tasks)

# Auto-detection with complexity
request = StrategyRequest(
    task="Solve this paradox: Can an omnipotent being create a stone it cannot lift?",
    complexity=ComplexityLevel.PARADOXICAL
)
# Will auto-select: META_PROMPTING (for complex reasoning)
```

## Caching System

The engine includes an LRU cache for performance:

```python
engine = PromptEngineV2(cache_enabled=True, max_cache_size=500)

# First call - generates prompt
response1 = engine.generate("Task description")
print(response1.cache_hit)  # False

# Second identical call - uses cache
response2 = engine.generate("Task description")
print(response2.cache_hit)  # True

# Check cache statistics
stats = engine.get_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")

# Clear cache if needed
engine.clear_cache()
```

## Error Handling

The engine provides graceful fallbacks:

```python
try:
    response = engine.generate(request)
except Exception as e:
    # Engine automatically falls back to ZERO_SHOT strategy
    # Response will include warnings about the error
    print(response.warnings)
```

## Performance Metrics

Each response includes performance metrics:

```python
response = engine.generate("Complex task description")

print(f"Rendering time: {response.rendering_time_ms:.2f}ms")
print(f"Quality score: {response.quality_score:.2%}")
print(f"Confidence: {response.confidence:.2%}")
print(f"Cache hit: {response.cache_hit}")
```

## Best Practices

1. **Strategy Selection**:
   - Let the engine auto-select for most cases
   - Specify strategy for domain-specific needs
   - Use complexity levels to guide selection

2. **Performance**:
   - Enable caching for repeated queries
   - Use batch generation for multiple prompts
   - Monitor cache hit rates

3. **Type Safety**:
   - Use StrategyRequest for complex queries
   - Leverage Pydantic validation
   - Handle ValidationErrors appropriately

4. **Integration**:
   - Use LLMCompatibilityAdapter for llm.py
   - Implement custom strategies by extending BasePromptStrategy
   - Monitor warnings in responses

## Testing

Run the integration test suite:

```bash
python test_prompts_v2_integration.py
```

Run type checking:

```bash
mypy prompts_v2.py --ignore-missing-imports --strict
```

Run style checks:

```bash
flake8 prompts_v2.py --max-line-length=120
black prompts_v2.py --line-length=120
```

## Migration from prompts.py

To migrate from the old `prompts.py`:

1. Replace imports:
   ```python
   # Old
   from prompts import PromptEngine, PromptStrategy
   
   # New
   from prompts_v2 import PromptEngineV2, StrategyType
   ```

2. Update strategy references:
   ```python
   # Old
   strategy = PromptStrategy.CHAIN_OF_THOUGHT
   
   # New
   strategy = StrategyType.CHAIN_OF_THOUGHT
   ```

3. Use new request model:
   ```python
   # Old
   prompt = engine.generate(task, strategy)
   
   # New
   request = StrategyRequest(task=task, strategy=strategy)
   response = engine.generate(request)
   prompt = response.prompt
   ```

## Troubleshooting

### Common Issues

1. **Strategy not loading**: Check if .md file exists in master_prompt_strategies/
2. **Validation errors**: Ensure task is at least 10 characters
3. **Cache issues**: Clear cache with `engine.clear_cache()`
4. **Import errors**: Ensure pydantic>=2.0 is installed

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now engine will log detailed information
engine = PromptEngineV2()
```

## License and Attribution

This module uses prompt strategies from the master_prompt_strategies collection, which includes research from:
- Chain of Thought (Wei et al., 2022)
- Tree of Thoughts (Yao et al., 2023)
- ReAct (Yao et al., 2022)
- Constitutional AI (Anthropic, 2022)
- And 17 other cutting-edge strategies

---

**Version**: 2.0.0  
**Author**: Senior Software Engineer (30+ years experience)  
**Last Updated**: 2025-08-28  
**Status**: Production Ready