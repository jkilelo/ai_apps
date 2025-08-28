# LLM Module Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Provider System](#provider-system)
5. [Prompt Strategies](#prompt-strategies)
6. [Configuration System](#configuration-system)
7. [API Reference](#api-reference)
8. [Integration Examples](#integration-examples)
9. [Advanced Features](#advanced-features)
10. [Best Practices](#best-practices)

## Overview

The `llm.py` module serves as the **single source of truth** for all LLM operations in the UI Testing Framework. It provides a unified interface to multiple LLM providers (OpenAI, Google Gemini, Anthropic Claude) with advanced features including:

- **21 Research-backed prompt strategies**
- **Streaming responses**
- **Vision/multimodal support**
- **Structured output with Pydantic models**
- **Async/sync operations**
- **Automatic fallback mechanisms**
- **Type-safe contracts with Pydantic v2**

## Architecture

### Module Structure

```
llm.py (1600+ lines)
├── Pydantic V2 Contracts (lines 98-210)
│   ├── Provider enum
│   ├── Role enum  
│   ├── Message model
│   ├── ImageContent model
│   ├── StreamChunk model
│   ├── LLMResponse model
│   └── LLMConfig model
├── Strategy Engine (lines 216-590)
│   └── 21 prompt strategy implementations
├── Provider Implementations (lines 640-1336)
│   ├── GeminiProvider
│   ├── OpenAIProvider
│   └── AnthropicProvider
├── Unified Gateway (lines 1344-1550)
│   └── UnifiedLLMGateway class
└── Public API Functions (lines 1550+)
    ├── query_llm()
    ├── call_default_llm()
    └── stream_llm()
```

### Design Principles

1. **Single Source of Truth**: All LLM operations go through this module
2. **Provider Abstraction**: Unified interface regardless of provider
3. **Type Safety**: Full Pydantic v2 validation and type hints
4. **Lazy Loading**: Providers loaded only when needed
5. **Strategy Pattern**: Pluggable prompt enhancement strategies
6. **Configuration-Driven**: External JSON config for models

## Core Components

### 1. Message System

```python
class Message(BaseModel):
    role: Role  # system, user, or assistant
    content: str
    images: Optional[List[ImageContent]] = None
    metadata: Dict[str, Any] = {}
```

Messages are the fundamental unit of LLM communication. Each message has:
- **role**: Who is speaking (system/user/assistant)
- **content**: The text content
- **images**: Optional images for vision models
- **metadata**: Additional context

### 2. LLMResponse

```python
class LLMResponse(BaseModel):
    content: str  # The actual response text
    provider: Provider  # Which provider was used
    model: str  # Which model was used
    strategy_used: Optional[StrategyType]  # Strategy applied
    images_processed: int  # Number of images processed
    streaming: bool  # Was this streamed
    structured: bool  # Structured output used
    latency_ms: Optional[int]  # Response time
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    timestamp: datetime
    processing_time: Optional[float]
```

Every LLM query returns a comprehensive response object with metadata about the operation.

### 3. LLMConfig

```python
class LLMConfig(BaseModel):
    provider: Provider = Provider.GEMINI
    model: str = "gemini-2.0-flash"
    temperature: float = 0.0
    max_tokens: int = 8192
    top_p: float = 1.0
    strategy: Optional[StrategyType] = None
    timeout: int = 60
    retry_attempts: int = 3
    stream: bool = False
```

Configuration object that controls LLM behavior.

## Provider System

### Supported Providers

1. **Google Gemini** (Default)
   - Models: gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.0-flash-thinking-exp
   - Features: 1M token context, vision, thinking mode, streaming
   - API Key: `GOOGLE_API_KEY` or `GEMINI_API_KEY`

2. **OpenAI**
   - Models: gpt-5, gpt-5-mini, gpt-4o, o3, o4-mini
   - Features: Vision, streaming, function calling, structured output
   - API Key: `OPENAI_API_KEY`

3. **Anthropic Claude**
   - Models: claude-sonnet-4, claude-3.5-sonnet, claude-3.5-haiku
   - Features: 200K context, vision, computer use, prompt caching
   - API Key: `ANTHROPIC_API_KEY`

### Provider Implementation Pattern

Each provider implements the `LLMProvider` abstract base class:

```python
class LLMProvider(ABC):
    @abstractmethod
    def query(messages, config, images, output_model) -> LLMResponse
    
    @abstractmethod
    def stream(messages, config, images) -> Iterator[StreamChunk]
    
    @abstractmethod
    async def aquery(messages, config, images, output_model) -> LLMResponse
    
    @abstractmethod  
    async def astream(messages, config, images) -> AsyncIterator[StreamChunk]
```

### Lazy Loading

Providers are instantiated only when first used:

```python
def _get_provider(self, provider: Provider) -> LLMProvider:
    if provider not in self.providers:
        if provider == Provider.OPENAI:
            self.providers[provider] = OpenAIProvider()
        elif provider in (Provider.GEMINI, Provider.GOOGLE):
            self.providers[provider] = GeminiProvider()
        elif provider == Provider.ANTHROPIC:
            self.providers[provider] = AnthropicProvider()
    return self.providers[provider]
```

## Prompt Strategies

### 21 Master Strategies

The module implements 21 research-backed prompt engineering strategies:

#### Core Reasoning (lines 254-293)
1. **Chain of Thought (CoT)**: Step-by-step reasoning
2. **Tree of Thoughts (ToT)**: Explore multiple reasoning paths
3. **Graph of Thoughts (GoT)**: Non-linear reasoning with connections

#### Problem Decomposition (lines 295-333)
4. **Least to Most**: Build from simple to complex
5. **Step Back**: Abstract to higher-level principles
6. **Decomposed**: Break into sub-problems

#### Knowledge Enhancement (lines 335-380)
7. **Retrieval Augmented (RAG)**: Augment with external knowledge
8. **Generated Knowledge**: Generate relevant knowledge first
9. **Knowledge Graph**: Structure knowledge as graph

#### Self-Improvement (lines 382-430)
10. **Self Consistency**: Generate multiple solutions
11. **Self Refine**: Iteratively improve response
12. **Self Verification**: Verify own outputs

#### Reasoning Frameworks (lines 432-480)
13. **ReAct**: Reason + Act framework
14. **Reflexion**: Learn from feedback
15. **Chain of Verification**: Multi-step verification

#### Advanced Reasoning (lines 482-530)
16. **Hypothetical Document**: Generate hypothetical examples
17. **Analogical Reasoning**: Use analogies
18. **Socratic Method**: Question-driven exploration

#### Meta Strategies (lines 532-590)
19. **Meta Prompting**: Generate optimal prompts
20. **Prompt Optimization**: Optimize existing prompts
21. **Constitutional AI**: Apply ethical principles

### Strategy Application

Strategies modify the user's prompt to enhance LLM reasoning:

```python
def apply_strategy(messages, strategy, context):
    if strategy == StrategyType.CHAIN_OF_THOUGHT:
        messages[-1].content += """
        Let's think through this step by step:
        1. First, identify the key components
        2. Then, analyze each component  
        3. Finally, synthesize the solution
        Show your reasoning for each step.
        """
    return messages
```

### How Prompts Connect to LLM Calls

1. **User provides initial messages**
2. **Strategy Engine enhances messages** (if strategy specified)
3. **Enhanced messages sent to provider**
4. **Provider formats for specific API**
5. **Response returned with strategy metadata**

## Configuration System

### llm_models.json Structure

The external configuration file controls model selection and fallbacks:

```json
{
    "default": {
        "provider": "gemini",
        "model": "gemini-2.5-flash-lite",
        "supports_streaming": true,
        "max_tokens": 1000000,
        "context_window": 1000000
    },
    "providers": {
        "gemini": {...},
        "openai": {...},
        "anthropic": {...}
    },
    "fallback_order": [
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "openai", "model": "gpt-5-mini"},
        {"provider": "anthropic", "model": "claude-3.5-haiku-20241022"}
    ]
}
```

### Configuration Loading

The configuration is loaded on module initialization and used for:
- Default provider/model selection
- Model capability checking
- Fallback chain determination
- Token limit enforcement

## API Reference

### Primary Functions

#### 1. query_llm()
```python
def query_llm(
    messages: List[Dict[str, Any]],
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List] = None,
    output_model: Optional[Type[BaseModel]] = None
) -> Union[LLMResponse, BaseModel]
```

Main function for querying any LLM provider.

**Parameters:**
- `messages`: List of message dicts with 'role' and 'content'
- `provider`: "openai", "gemini", or "anthropic"
- `model`: Specific model name
- `temperature`: Creativity (0.0 = deterministic)
- `max_tokens`: Maximum response length
- `strategy`: One of 21 prompt strategies
- `images`: Images for vision models
- `output_model`: Pydantic model for structured output

**Returns:** LLMResponse or structured model instance

#### 2. call_default_llm()
```python
def call_default_llm(
    messages: List[Dict[str, Any]],
    strategy: Optional[str] = None,
    **kwargs
) -> LLMResponse
```

Simplified interface using default provider (Gemini).

**Usage:**
```python
response = call_default_llm([
    {"role": "user", "content": "Explain quantum computing"}
], strategy="chain_of_thought")
```

#### 3. stream_llm()
```python
def stream_llm(
    messages: List[Dict[str, Any]],
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> Iterator[StreamChunk]
```

Stream responses for real-time output.

**Usage:**
```python
for chunk in stream_llm(messages):
    print(chunk.content, end="")
    if chunk.is_final:
        break
```

### Async Functions

#### 4. aquery_llm()
```python
async def aquery_llm(
    messages: List[Dict[str, Any]],
    **kwargs
) -> Union[LLMResponse, BaseModel]
```

Async version of query_llm for concurrent operations.

#### 5. astream_llm()
```python
async def astream_llm(
    messages: List[Dict[str, Any]],
    **kwargs
) -> AsyncIterator[StreamChunk]
```

Async streaming for non-blocking I/O.

## Integration Examples

### Basic Usage

```python
from llm import call_default_llm

# Simple query
response = call_default_llm([
    {"role": "user", "content": "What is the capital of France?"}
])
print(response.content)  # "Paris"
```

### With Strategy

```python
from llm import query_llm

# Use Chain of Thought for complex reasoning
response = query_llm(
    messages=[
        {"role": "user", "content": "Calculate 15% of 247"}
    ],
    strategy="chain_of_thought",
    temperature=0
)
print(response.content)
# Shows step-by-step calculation
```

### Vision/Multimodal

```python
from llm import query_llm
from pathlib import Path

# Analyze an image
response = query_llm(
    messages=[
        {"role": "user", "content": "What's in this image?"}
    ],
    images=[Path("screenshot.png")],
    provider="gemini",
    model="gemini-2.5-flash"
)
```

### Structured Output

```python
from llm import query_llm
from pydantic import BaseModel

class ExtractedInfo(BaseModel):
    name: str
    age: int
    occupation: str

response = query_llm(
    messages=[
        {"role": "user", "content": "Extract info from: John Doe, 30, Engineer"}
    ],
    output_model=ExtractedInfo
)
# response is ExtractedInfo instance
print(response.name)  # "John Doe"
```

### Streaming

```python
from llm import stream_llm

for chunk in stream_llm([
    {"role": "user", "content": "Write a short story"}
]):
    print(chunk.content, end="", flush=True)
```

### With Context from Other Modules

```python
from llm import query_llm
from prompts import PromptEngine

# Use prompt engine to optimize prompt
engine = PromptEngine()
optimized = engine.optimize("Extract all buttons from webpage")

response = query_llm(
    messages=[{"role": "user", "content": optimized}],
    strategy="decomposed"
)
```

## Advanced Features

### 1. Image Processing

The module includes `ImageProcessor` class for handling images:

```python
class ImageProcessor:
    def encode_image(path: Path) -> ImageContent
    def encode_bytes(data: bytes) -> ImageContent  
    def encode_pil(image: PIL.Image) -> ImageContent
```

Automatically handles:
- File path to base64 conversion
- Image format detection
- Size optimization
- MIME type detection

### 2. Fallback Mechanism

Automatic fallback when primary provider fails:

```json
"fallback_order": [
    {"provider": "gemini", "model": "gemini-2.5-flash"},
    {"provider": "openai", "model": "gpt-5-mini"},
    {"provider": "anthropic", "model": "claude-3.5-haiku"}
]
```

### 3. Token Management

Each provider enforces token limits:

```python
# Anthropic limits
max_tokens = min(config.max_tokens, 4096)

# OpenAI limits
if "gpt-5" in model:
    max_tokens = min(max_tokens, 128000)
```

### 4. Error Handling

Comprehensive error handling with logging:

```python
try:
    response = provider.query(messages, config)
except Exception as e:
    logger.error(f"{provider} query failed: {e}")
    # Try fallback provider
    return self._try_fallback(messages, config)
```

### 5. Performance Metrics

Every response includes performance data:

```python
response.latency_ms  # Response time
response.prompt_tokens  # Input tokens
response.completion_tokens  # Output tokens
response.processing_time  # Total processing
```

## Best Practices

### 1. Always Use Default Functions

For consistency across the codebase:

```python
# GOOD - uses single source of truth
from llm import call_default_llm
response = call_default_llm(messages)

# BAD - direct provider usage
client = OpenAI()
response = client.chat.completions.create(...)
```

### 2. Apply Appropriate Strategies

Match strategy to task type:

```python
# Reasoning tasks -> Chain of Thought
query_llm(messages, strategy="chain_of_thought")

# Complex problems -> Tree of Thoughts
query_llm(messages, strategy="tree_of_thoughts")

# Verification -> Self Verification
query_llm(messages, strategy="self_verification")
```

### 3. Use Structured Output

For parsing responses:

```python
class TestCase(BaseModel):
    name: str
    steps: List[str]
    expected: str

# Returns validated TestCase instance
test = query_llm(messages, output_model=TestCase)
```

### 4. Handle Streaming Properly

For long responses:

```python
full_response = ""
for chunk in stream_llm(messages):
    full_response += chunk.content
    # Update UI with chunk
    if chunk.is_final:
        break
```

### 5. Configure Temperature

- `0.0`: Deterministic, best for code/analysis
- `0.3-0.7`: Balanced creativity
- `0.8-1.0`: Creative tasks

### 6. Use Vision When Needed

```python
# Analyze UI screenshot
response = query_llm(
    messages=[{"role": "user", "content": "Find all buttons"}],
    images=[screenshot_path],
    provider="gemini"  # Best vision support
)
```

## Integration with Other Modules

### 1. browser_with_llm.py

```python
from llm import call_default_llm

class BrowserWithLLM:
    def analyze_page(self, html):
        response = call_default_llm([
            {"role": "user", "content": f"Analyze: {html}"}
        ], strategy="decomposed")
        return response.content
```

### 2. test_generation_with_llm.py

```python
from llm import query_llm

def generate_tests(elements):
    response = query_llm(
        messages=[{"role": "user", "content": f"Generate tests for: {elements}"}],
        strategy="self_consistency",
        output_model=TestSuite
    )
    return response  # TestSuite instance
```

### 3. code_generation_with_llm.py

```python
from llm import call_default_llm

def generate_code(spec):
    response = call_default_llm(
        messages=[{"role": "user", "content": f"Generate code: {spec}"}],
        strategy="constitutional_ai"  # Ensures safe code
    )
    return response.content
```

## Error Messages and Troubleshooting

### Common Errors

1. **API Key Not Found**
   ```
   ValueError: Gemini API key not found
   ```
   Solution: Set `GOOGLE_API_KEY` in .env file

2. **Import Error**
   ```
   ImportError: google-genai not installed
   ```
   Solution: `pip install google-genai`

3. **Token Limit Exceeded**
   ```
   Error: Maximum context length exceeded
   ```
   Solution: Reduce input size or use model with larger context

4. **Invalid Strategy**
   ```
   ValueError: Invalid strategy: unknown_strategy
   ```
   Solution: Use one of 21 valid strategies

5. **Structured Output Parse Error**
   ```
   ValidationError: Invalid JSON for model
   ```
   Solution: Ensure prompt requests exact format

## Performance Considerations

### 1. Provider Selection

- **Gemini**: Best for cost/performance, 1M context
- **OpenAI**: Best for reasoning tasks (o3/o4 models)
- **Anthropic**: Best for long context (200K)

### 2. Caching

Consider implementing caching for repeated queries:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(prompt_hash):
    return call_default_llm(messages)
```

### 3. Batch Processing

For multiple queries, use async:

```python
async def batch_process(prompts):
    tasks = [aquery_llm(p) for p in prompts]
    return await asyncio.gather(*tasks)
```

### 4. Token Optimization

Minimize tokens for cost:

```python
# Remove unnecessary whitespace
content = " ".join(content.split())

# Use concise system prompts
{"role": "system", "content": "Be concise"}
```

## Summary

The `llm.py` module is the cornerstone of AI operations in the UI Testing Framework. It provides:

1. **Unified Interface**: Single API for all LLM providers
2. **Advanced Strategies**: 21 research-backed prompt techniques
3. **Type Safety**: Full Pydantic v2 validation
4. **Rich Features**: Vision, streaming, structured output
5. **Production Ready**: Error handling, fallbacks, metrics

By centralizing all LLM operations, the module ensures consistency, maintainability, and optimal performance across the entire framework. Always use this module instead of direct provider APIs to maintain the single source of truth principle.

---
*Documentation Version: 1.0.0*  
*Module Version: 4.0.0*  
*Last Updated: 2025-01-28*