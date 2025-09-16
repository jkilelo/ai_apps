# Browser.py Fix Plan - DRY Compliance & Architecture Fix

## Issues to Fix:

### 1. Type System Violations
- **Exception Classes** (lines 498-519): Move to data_types.py
  - BrowserError
  - NavigationError
  - ExtractionError
  - TimeoutError
- **BrowserStealthConfig** (line 207): Remove, use StealthConfig from data_types.py

### 2. DRY Violations - Duplicate Methods
- **_determine_element_type()** - 66 lines duplicated in:
  - DOMExtractionStrategy (lines 1531+)
  - ShadowDOMExtractionStrategy (lines 1776+)
- **_generate_xpath()** - 18 lines duplicated
- **_generate_css_selector()** - 13 lines duplicated

### 3. Page Crash Issue
- Stealth injection too aggressive
- Need to make stealth features optional/configurable
- Disable problematic features by default

## Fix Strategy (Top-Down):

### Phase 1: Move Types to data_types.py
1. Add exception classes to data_types.py
2. Remove BrowserStealthConfig class
3. Update all references

### Phase 2: Create Shared Utilities
1. Create ElementSelectorUtils class in data_types.py
2. Move duplicate methods to utils
3. Update strategies to use shared utils

### Phase 3: Fix Stealth Issues
1. Make stealth injection conditional
2. Add safety checks
3. Disable problematic features by default

### Phase 4: Testing & Certification
1. Test standalone execution
2. Test integration
3. Verify DRY compliance
4. Sign contract

## Expected Outcome:
- Zero duplicate code
- All types in data_types.py
- Browser working without crashes
- Full DRY compliance