# UI Testing Framework Architecture - Single Responsibility & DRY

## Core Principles

1. **Single Source of Truth**: ALL types defined in `types.py` only
2. **Single Responsibility**: Each module does ONE thing only
3. **DRY (Don't Repeat Yourself)**: No duplicate code or functionality
4. **Clear Dependencies**: One-way dependency flow

## Module Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         types.py                             │
│           Single Source of Truth for ALL Types               │
│  (Enums, Models, Configs, Exceptions, Type Aliases)         │
└──────────────────┬──────────────────────────────────────────┘
                   │ Imported by ALL modules
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     CORE SERVICES                            │
├───────────────────────────────────────────────────────────────
│ browser.py          │ The ONLY module for browser automation │
│ llm.py             │ The ONLY module for LLM calls          │
│ llm_utils.py       │ The ONLY module for LLM utilities      │
│ prompts.py         │ The ONLY module for prompt strategies  │
└───────────────────┴──────────────────────────────────────────┘
                   │ Used by extraction/generation layers
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTRACTION LAYER                          │
├───────────────────────────────────────────────────────────────
│ elements_extractor_no_llm.py  │ ONLY DOM extraction         │
│ elements_extractor_with_llm.py│ ONLY element enrichment     │
└───────────────────┴──────────────────────────────────────────┘
                   │ Provides enriched elements to
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    GENERATION LAYER                          │
├───────────────────────────────────────────────────────────────
│ test_generation_with_llm.py │ ONLY test generation          │
└──────────────────────────────────────────────────────────────┘
```

## Module Responsibilities (STRICT)

### 1. **types.py**
- **SOLE RESPONSIBILITY**: Define ALL data types for the entire framework
- **CONTAINS**: 
  - 13 Enum definitions (ElementType, TestCategory, etc.)
  - 31 BaseModel/dataclass definitions
  - 4 Exception classes
  - Type aliases and unions
  - Helper functions for type operations
- **USED BY**: Every other module
- **IMPORTS**: Nothing from framework (only standard library)

### 2. **browser.py**
- **SOLE RESPONSIBILITY**: Browser automation and control
- **DOES**: 
  - Launch browsers
  - Navigate to URLs
  - Execute JavaScript
  - Take screenshots
  - Handle browser lifecycle
- **DOES NOT**: 
  - Extract elements (that's elements_extractor_no_llm.py)
  - Call LLMs (that's llm.py)
  - Generate tests
- **IMPORTS FROM**: types.py ONLY
- **EXPORTS**: Browser class, navigation functions

### 3. **llm.py**
- **SOLE RESPONSIBILITY**: Make LLM API calls
- **DOES**: 
  - Call OpenAI/Anthropic/other LLM APIs
  - Handle API authentication
  - Manage rate limiting
  - Return raw LLM responses
- **DOES NOT**: 
  - Parse responses (that's llm_utils.py)
  - Select strategies (that's llm_utils.py)
  - Format prompts (that's llm_utils.py)
- **IMPORTS FROM**: types.py ONLY
- **EXPORTS**: call_default_llm(), call_specific_llm()

### 4. **llm_utils.py**
- **SOLE RESPONSIBILITY**: LLM response processing and prompt utilities
- **DOES**: 
  - Parse JSON from LLM responses
  - Select appropriate strategies
  - Build consistent prompts
  - Clean/fix malformed responses
- **DOES NOT**: 
  - Make API calls (that's llm.py)
  - Define strategies (that's prompts.py)
- **IMPORTS FROM**: types.py, prompts.py
- **EXPORTS**: LLMResponseParser, StrategySelector, LLMPromptBuilder

### 5. **prompts.py**
- **SOLE RESPONSIBILITY**: Define and manage prompt strategies
- **DOES**: 
  - Define all prompt strategies
  - Render prompts with tasks
  - Manage strategy library
- **DOES NOT**: 
  - Call LLMs (that's llm.py)
  - Parse responses (that's llm_utils.py)
- **IMPORTS FROM**: types.py ONLY
- **EXPORTS**: PromptLibrary, get_strategy(), enhance_with_strategy()

### 6. **elements_extractor_no_llm.py**
- **SOLE RESPONSIBILITY**: Extract raw elements from DOM
- **DOES**: 
  - Parse HTML/DOM
  - Extract element properties
  - Find selectors/XPaths
  - Detect element states
- **DOES NOT**: 
  - Launch browsers (uses browser.py)
  - Enrich with LLM (that's elements_extractor_with_llm.py)
  - Generate tests
- **IMPORTS FROM**: types.py, browser.py
- **EXPORTS**: ElementsExtractorNoLLM, extract_from_url()

### 7. **elements_extractor_with_llm.py**
- **SOLE RESPONSIBILITY**: Enrich elements with LLM analysis
- **DOES**: 
  - Add semantic understanding to elements
  - Classify element purposes
  - Analyze page characteristics
- **DOES NOT**: 
  - Extract raw elements (uses elements_extractor_no_llm.py)
  - Generate tests (that's test_generation_with_llm.py)
  - Generate QA plans (that's test_generation_with_llm.py)
- **IMPORTS FROM**: types.py, elements_extractor_no_llm.py, llm.py, llm_utils.py
- **EXPORTS**: ElementsExtractorWithLLM, extract_and_analyze()

### 8. **test_generation_with_llm.py**
- **SOLE RESPONSIBILITY**: Generate tests from enriched elements
- **DOES**: 
  - Generate test scenarios
  - Create QA test plans
  - Generate Gherkin features
  - Generate test code
- **DOES NOT**: 
  - Extract elements (uses elements_extractor_with_llm.py)
  - Enrich elements (that's elements_extractor_with_llm.py)
- **IMPORTS FROM**: types.py, elements_extractor_with_llm.py, llm.py, llm_utils.py
- **EXPORTS**: TestGenerationEngine, generate_tests_for_url()

## Data Flow (One Direction)

```
1. User provides URL
   ↓
2. browser.py navigates to URL
   ↓
3. elements_extractor_no_llm.py extracts raw elements
   ↓
4. elements_extractor_with_llm.py enriches with LLM
   ↓
5. test_generation_with_llm.py generates tests
   ↓
6. Output: Test scenarios, Gherkin, code
```

## Import Rules (STRICT)

1. **types.py**: Imports NOTHING from the framework
2. **Core Services**: Import ONLY from types.py
3. **Extraction Layer**: Import from types.py and core services
4. **Generation Layer**: Import from types.py, core services, and extraction layer
5. **NO CIRCULAR IMPORTS**: Dependencies flow in one direction only

## Type Usage Examples

### WRONG (Creates own types):
```python
# elements_extractor_no_llm.py
class ElementType(Enum):  # NO! Duplicate type definition
    BUTTON = "button"
    ...

class ExtractionResult:  # NO! Duplicate model
    def __init__(self):
        ...
```

### CORRECT (Imports from types.py):
```python
# elements_extractor_no_llm.py
from types import (
    ElementType,
    ExtractedElement,
    DOMExtractionResult,
    DOMExtractionConfig
)
# Use imported types only
```

## Migration Checklist

### Phase 1: Types Migration
- [x] Create comprehensive types.py with ALL types
- [x] Document all duplicate types
- [ ] Update browser.py to import from types.py
- [ ] Update elements_extractor_no_llm.py to import from types.py
- [ ] Update elements_extractor_with_llm.py to import from types.py
- [ ] Update test_generation_with_llm.py to import from types.py
- [ ] Update llm_utils.py to import from types.py
- [ ] Update prompts.py to import from types.py

### Phase 2: Functionality Separation
- [ ] Remove test generation from elements_extractor_with_llm.py
- [ ] Move QA plan generation to test_generation_with_llm.py
- [ ] Remove duplicate JSON parsing (use llm_utils.py)
- [ ] Remove duplicate strategy selection (use llm_utils.py)

### Phase 3: Cleanup
- [ ] Remove models.py (replaced by types.py)
- [ ] Remove all local type definitions
- [ ] Remove all duplicate functionality
- [ ] Verify no circular imports

## Benefits of This Architecture

1. **Maintainability**: Change types in ONE place only
2. **Clarity**: Each module has ONE clear purpose
3. **Testability**: Mock any layer independently
4. **Scalability**: Add new modules without affecting others
5. **Reliability**: No duplicate code means fewer bugs
6. **Performance**: No redundant operations

## Enforcement Rules

1. **Code Review**: Reject any PR that defines its own types
2. **Testing**: Test each module in isolation
3. **Documentation**: Each module must declare its single responsibility
4. **Imports**: Lint rules to prevent circular imports
5. **Coverage**: Each module must have >80% test coverage

## Anti-Patterns to Avoid

1. **Creating local enums/models** → Use types.py
2. **Duplicating parsing logic** → Use llm_utils.py
3. **Module doing multiple things** → Split into separate modules
4. **Circular dependencies** → Refactor to one-way flow
5. **Copy-paste code** → Extract to shared utility

## Success Metrics

- **Zero duplicate type definitions**
- **Zero circular imports**
- **Each module has exactly ONE responsibility**
- **All types imported from types.py**
- **No module exceeds 500 lines** (except types.py)