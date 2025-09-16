# GitHub Copilot Instructions for UI Testing Framework V3

## Project Context
This is a production-grade UI Testing Framework using Hexagonal Architecture (Ports & Adapters pattern) with a plugin-first design. The system extracts web elements, formats them for various use cases, and generates comprehensive test cases using LLM integration.

## Critical Architectural Rules

### 1. Core Domain Purity
- **ZERO external dependencies** in `core/` directory
- Use ONLY Python built-ins (dataclasses, enum, typing, functools, etc.)
- All business logic must be in domain models
- Domain models must be immutable (frozen dataclasses)
- No technical logic in domain layer

### 2. Hexagonal Architecture
- **Ports** (`ports/`) define contracts using Python Protocol
- **Adapters** (`adapters/`) implement port interfaces
- **Plugins** (`plugins/`) extend functionality
- Everything must be a plugin except core domain
- Use dependency injection for all dependencies

### 3. QA-First Mindset
- Think like a 30+ year senior QA engineer
- Focus on:
  - What would break the application?
  - What would users interact with?
  - What needs accessibility testing?
  - What has business impact?
- Prioritize interactive elements
- Generate comprehensive test coverage

## Coding Standards

### Python Style
- Use type hints for ALL functions and methods
- Follow PEP 8 with 100-character line limit
- Use descriptive variable names
- Document business rules in docstrings
- Prefer composition over inheritance

### Testing Requirements
- Minimum 95% test coverage
- Test business logic separately from technical logic
- Use pytest for all tests
- Mock external dependencies
- Test error paths and edge cases

### Error Handling
- Raise domain exceptions for business rule violations
- Use graceful degradation for technical failures
- Log errors with context
- Never expose internal implementation details

## Directory Structure
```
ui_testing_framework_v3/
├── core/           # Domain layer - ZERO external deps
├── ports/          # Interface definitions (Protocols)
├── adapters/       # Port implementations
├── plugins/        # External plugins
├── application/    # Use cases & workflows (LangGraph)
├── infrastructure/ # Cross-cutting concerns
├── api/           # External interfaces (CLI, REST)
├── tests/         # Test suite
├── config/        # Configuration files (TOML)
└── docs/          # Documentation
```

## Key Design Patterns

### 1. Immutable Value Objects
```python
@dataclass(frozen=True)
class URL:
    value: str
    
    def __post_init__(self):
        # Validate in constructor
        if not self.value:
            raise ValueError("URL cannot be empty")
```

### 2. Protocol-Based Ports
```python
@runtime_checkable
class IExtractor(Protocol):
    async def extract(self, url: URL) -> List[Element]:
        ...
```

### 3. Plugin Registration
```python
registry.register("extractor", StealthBrowserAdapter, "stealth")
adapter = registry.get("extractor", "stealth")
```

### 4. LangGraph Workflows
```python
workflow = StateGraph(WorkflowState)
workflow.add_node("extract", extract_elements)
workflow.add_edge("extract", "format")
```

## Browser Automation Rules
- **ALWAYS set headless=False** for debugging
- Use stealth mode with anti-bot level "maximum"
- Support shadow DOM extraction
- Handle dynamic content with intelligent waiting
- Cache extraction results for performance

## LLM Integration Guidelines
- Optimize token usage in formatters
- Group elements by interaction type
- Provide test hints based on element analysis
- Generate test scenarios from element patterns
- Validate all generated tests

## Performance Optimization
- Use built-in caching (@lru_cache, @cache)
- Implement connection pooling for browsers
- Use async/await for I/O operations
- Leverage collections (deque, defaultdict)
- Cache with TTL for extraction results

## Security Considerations
- Validate all URLs before processing
- Sanitize CSS selectors
- Never log sensitive data
- Use secrets module for token generation
- Implement rate limiting

## Common Tasks

### Adding a New Adapter
1. Create adapter class in `adapters/`
2. Implement required port interface
3. Register with plugin registry
4. Add configuration in TOML
5. Write comprehensive tests

### Creating a Plugin
1. Create plugin file in `plugins/`
2. Implement `register()` function
3. Call `registry.register()` in register
4. Document plugin capabilities
5. Add integration tests

### Extending Workflows
1. Define new workflow state
2. Create workflow nodes
3. Connect with edges
4. Add error handling
5. Test complete flow

## Debugging Tips
- Check browser headless setting (must be False)
- Verify plugin registration
- Validate port contracts
- Review event bus history
- Check configuration loading

## Production Checklist
- [ ] All tests passing (95%+ coverage)
- [ ] No external deps in core domain
- [ ] All ports have implementations
- [ ] Error handling comprehensive
- [ ] Configuration validated
- [ ] Documentation complete
- [ ] Performance benchmarks met
- [ ] Security review completed

## Contact
For architectural decisions or complex implementations, think like a senior QA engineer with 30+ years of experience focused on production quality and comprehensive testing.