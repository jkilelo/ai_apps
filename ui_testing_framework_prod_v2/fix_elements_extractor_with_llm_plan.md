# Elements Extractor With LLM - DRY Fix Plan

## DRY Violations Identified:

### 1. Duplicate Imports (lines 22-47)
- **Issue:** Importing from both `ui_testing_framework_prod_v2.data_types` AND `data_types`
- **Fix:** Use single consistent import path

### 2. Local Interactive Element Definitions (lines 281-285)
- **Issue:** Defining `interactive_tags`, `interactive_roles`, `interactive_types` locally
- **Fix:** Move to data_types.py as shared constants or use ELEMENT_INTERACTIONS

### 3. Element Filtering Logic (lines 377-419)
- **Issue:** Complex duplicate logic for determining if element is interactive
- **Fix:** Create shared utility `ElementClassifier.is_interactive()` in data_types.py

### 4. Element Conversion Methods (lines 174-187, 252-259)
- **Issue:** Multiple methods converting Element to dict format
- **Fix:** Add standardized `to_dict()` method to Element class or use existing serialization

### 5. Element Prioritization Logic (lines 421-476)
- **Issue:** Complex prioritization logic that could be shared
- **Fix:** Move to shared utility `ElementPrioritizer` in data_types.py

### 6. Browser Cleanup Issues (lines 309-310)
- **Issue:** Manual browser cleanup instead of using context manager
- **Fix:** Use proper async context manager or ensure cleanup in finally block

### 7. Basic Enrichment Creation (lines 478-530)
- **Issue:** Manual element type to purpose mapping
- **Fix:** Use shared mapping from data_types.py

## Refactoring Strategy:

### Step 1: Add Shared Utilities to data_types.py
```python
class ElementClassifier:
    @staticmethod
    def is_interactive(element) -> bool

class ElementPrioritizer:
    @staticmethod
    def prioritize_elements(elements, max_count) -> List

# Interactive element constants
INTERACTIVE_TAGS = {...}
INTERACTIVE_ROLES = {...}
INTERACTIVE_ELEMENT_TYPES = {...}
```

### Step 2: Fix Imports
- Use consistent import path throughout
- Remove duplicate imports

### Step 3: Replace Local Logic
- Use ElementClassifier.is_interactive()
- Use ElementPrioritizer.prioritize_elements()
- Use shared constants

### Step 4: Standardize Element Serialization
- Use consistent method for converting Element to dict

### Step 5: Fix Browser Integration
- Ensure proper cleanup using async context manager

## Expected Outcome:
- Remove ~200+ lines of duplicate code
- Single source of truth for element classification
- Consistent element handling across modules
- Proper resource cleanup
- Full DRY compliance