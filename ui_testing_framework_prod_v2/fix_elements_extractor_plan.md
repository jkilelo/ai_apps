# Elements Extractor No LLM - DRY Fix Plan

## Issues to Fix:

### 1. Duplicate Constants (lines 174-241)
- **CONFIDENCE_BASE, CONFIDENCE_INCREMENT** - Move to data_types.py
- **SELECTOR_SCORE_*** constants - Move to data_types.py
- **TAG_TO_ELEMENT_TYPE** mapping - DELETE, use ElementSelectorUtils
- **ROLE_TO_ELEMENT_TYPE** mapping - DELETE, use ElementSelectorUtils
- **ELEMENT_INTERACTIONS** mapping - Move to data_types.py

### 2. Duplicate Utility Functions (lines 102-166)
- **retry_with_backoff** decorator - Move to data_types.py
- **ThreadSafeCache** class - Move to data_types.py
- **memory_cleanup** function - Move to data_types.py

### 3. Duplicate Methods to Replace
- **_map_element_type()** (lines 439-504) - Replace with ElementSelectorUtils.determine_element_type()
- **_convert_browser_elements()** (lines 360-437) - DELETE, use browser results directly
- **_hash_element()** (lines 544-553) - Standardize with browser's deduplication

### 4. Refactoring Strategy
1. Move all shared utilities to data_types.py
2. Import ElementSelectorUtils and use its methods
3. Remove all duplicate mappings
4. Simplify to use browser.extract_elements() results directly
5. Remove unnecessary conversion logic

## Expected Outcome:
- Remove ~250+ lines of duplicate code
- Module becomes a thin wrapper around browser.py
- All types and utilities from data_types.py
- Full DRY compliance