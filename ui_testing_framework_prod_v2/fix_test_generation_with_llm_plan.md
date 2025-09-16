# Test Generation With LLM - DRY Fix Plan

## DRY Violations Identified:

### 1. Duplicate Element Summary Logic (lines 188-222)
- **Issue:** Manual element summarization that duplicates ElementSerializer functionality
- **Fix:** Use ElementSerializer.element_summary() from data_types.py

### 2. Duplicate Code Extraction Logic (lines 431-449)
- **Issue:** Custom code extraction from LLM responses
- **Fix:** Move to shared utility CodeExtractor in data_types.py

### 3. Duplicate Relevance Checking (lines 398-429)
- **Issue:** Custom element relevance logic for scenarios
- **Fix:** Create shared TestRelevanceAnalyzer in data_types.py

### 4. Manual Scenario Generation for Simple Pages (lines 451-514)
- **Issue:** Hardcoded scenario templates for basic elements
- **Fix:** Create shared ScenarioTemplates in data_types.py

### 5. Redundant Element Type Checking (lines 473-510)
- **Issue:** Multiple if/elif chains checking element types
- **Fix:** Use ElementClassifier.get_functional_purpose() from data_types.py

### 6. Duplicate Priority Assignment Logic
- **Issue:** Hardcoded priority values throughout
- **Fix:** Create shared TestPriorityAssigner in data_types.py

### 7. Multiple Similar Prompt Building Patterns
- **Issue:** Similar prompt structures repeated multiple times
- **Fix:** Standardize with enhanced LLMPromptBuilder

## Refactoring Strategy:

### Step 1: Add Test Generation Utilities to data_types.py
```python
class CodeExtractor:
    @staticmethod
    def extract_code_from_response(response: str) -> str

class TestRelevanceAnalyzer:
    @staticmethod
    def get_relevant_elements(scenario, elements) -> List

class ScenarioTemplates:
    @staticmethod
    def get_basic_scenario(element, url) -> TestScenario

class TestPriorityAssigner:
    @staticmethod
    def assign_priority(element_type, category) -> TestPriority

class TestContextBuilder:
    @staticmethod
    def build_test_context(page_analysis) -> Dict
```

### Step 2: Consolidate Scenario Generation
- Use templates for simple scenarios
- Standardize LLM prompts for complex scenarios

### Step 3: Remove Redundant Logic
- Replace custom code extraction
- Use shared relevance analyzer
- Leverage existing element utilities

### Step 4: Simplify Module Structure
- Focus on orchestration, not implementation
- Delegate to shared utilities

## Expected Outcome:
- Remove ~300+ lines of duplicate code
- Single source of truth for test generation logic
- Consistent scenario generation across all paths
- Cleaner separation of concerns
- Full DRY compliance