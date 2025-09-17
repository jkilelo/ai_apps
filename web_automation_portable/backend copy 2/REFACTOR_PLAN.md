# DRY Violation Fix Plan

## Current Problems (My Failures)
1. **Duplicate Functions**: extract_from_url() in BOTH modules
2. **Double Navigation**: elements_extractor calls navigate(), then browser.extract_elements(url) navigates AGAIN
3. **Unclear Separation**: browser.py has high-level business logic
4. **Confusing API**: Users don't know which module to use

## Root Cause
I fixed modules incrementally without maintaining architectural integrity. I added "main entry points" to both modules when you requested them, not realizing this violated DRY.

## Permanent Fix Architecture

### browser.py (LOW-LEVEL ONLY)
```python
class UltimateStealthBrowser:
    # Core browser operations
    async def initialize()
    async def navigate(url: str) -> bool
    async def get_dom_elements() -> List[Dict]  # Works on CURRENT page, no URL param
    async def cleanup()

# NO module-level functions like extract_from_url()
# NO high-level extraction logic
# NO ExtractionResult return type
```

### elements_extractor_no_llm.py (HIGH-LEVEL API)
```python
# ONLY module with user-facing API
async def extract_from_url(url) -> ExtractionResult
def extract_from_url_sync(url) -> ExtractionResult

class NoLLMExtractor:
    # Orchestrates browser operations
    async def extract_from_url(url):
        browser = UltimateStealthBrowser()
        await browser.initialize()
        await browser.navigate(url)  # Navigate ONCE
        dom_elements = await browser.get_dom_elements()  # Get from current page
        # Process, enrich, filter
        return ExtractionResult(...)
```

## Fix Steps
1. Remove ALL module-level functions from browser.py
2. Rename browser.extract_elements() to get_dom_elements() (no URL param)
3. Update elements_extractor to call navigate() then get_dom_elements()
4. Remove duplicate entry points
5. Test thoroughly

## Result
- **NO duplication**
- **Single navigation**
- **Clear separation**
- **DRY compliant**