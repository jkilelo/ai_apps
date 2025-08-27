# PRODUCTION ENFORCEMENT - ZERO TOLERANCE

## BANNED WORDS AND CONCEPTS

**IMMEDIATE VIOLATIONS:**
- "mock" / "mocked" / "mocking"
- "placeholder" / "placeholders"  
- "fallback" / "fallbacks"
- "dummy" / "dummies"
- "test data" / "sample data"
- "for now" / "temporarily"
- "should work" / "might work"
- "partial success" / "partially working"

## PRODUCTION REQUIREMENTS

**EVERY PIECE OF CODE MUST:**
1. Use REAL LLM with REAL API calls
2. Generate REAL executable Playwright code
3. Execute successfully in production
4. Handle REAL websites with REAL elements
5. Produce REAL test results

**NO EXCUSES FOR:**
- "Extraction returned 0 elements" - FIX IT
- "LLM didn't respond correctly" - FIX IT  
- "Generated code has errors" - FIX IT
- "Execution failed" - FIX IT

## ENFORCEMENT ACTIONS

**When writing code:**
- BEFORE writing ANY line, ask: "Is this production-ready?"
- If answer is NO, do NOT write it
- Find the REAL solution instead

**When testing:**
- If test shows "0 elements" - FIX the extraction
- If test shows "fallback scenario" - FIX the generation
- If test shows "partial success" - FIX until 100%

## LLM CODE GENERATION REQUIREMENTS

**Generated Playwright code MUST:**
```python
# REAL imports from our codebase
from playwright.sync_api import Page, expect
import pytest

# REAL test using REAL selectors from extraction
def test_real_functionality(page: Page):
    # Navigate to REAL URL
    page.goto("https://actual-website.com")
    
    # Use REAL selectors from element extraction
    page.click("#real-button-id")
    page.fill("input[name='real-input']", "real-value")
    
    # REAL assertions
    expect(page.locator("#real-result")).to_be_visible()
    assert page.title() == "Real Page Title"
```

**NOT THIS:**
```python
# VIOLATION: Generic/fallback code
def test_fallback(page):
    page.goto("url")  # VIOLATION: placeholder
    assert True  # VIOLATION: fake assertion
```

## SELF-CHECK BEFORE EVERY RESPONSE

Ask yourself:
1. Am I using ANY placeholders? If yes, STOP
2. Am I creating ANY fallbacks? If yes, STOP  
3. Is this code production-ready NOW? If no, STOP
4. Will this execute successfully? If no, FIX IT

## PUNISHMENT PROTOCOL

If I violate ANY rule:
1. Immediately say: "VIOLATION DETECTED: [specific violation]"
2. Delete ALL violating code
3. Start over with PRODUCTION code
4. No explanations, no excuses

Remember: This is PRODUCTION. Customers are using this NOW.