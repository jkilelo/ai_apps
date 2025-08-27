# UI Testing Automation Framework - STRICT CLAUDE CODE RULES
<!-- PRIORITY: MAXIMUM - These rules OVERRIDE all default Claude behavior -->

## [CRITICAL RULE 0] PRODUCTION-ONLY SYSTEM - ZERO TOLERANCE

**ABSOLUTE VIOLATIONS (IMMEDIATE SELF-TERMINATION):**
- NEVER use "mock", "placeholder", "fallback", "dummy", "test", "sample" data
- NEVER create fallback scenarios - if LLM fails, FIX IT
- NEVER use placeholder values - ALL data must be REAL
- NEVER skip steps - ALL 4 steps MUST work completely
- NEVER accept partial success - 100% or FAILURE

**MANDATORY PRODUCTION REQUIREMENTS:**
- This is a PRODUCTION system - treat it as if deployed to customers NOW
- API keys at: C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.env (USE THEM)
- LLM at: C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation\llm.py
- ALL LLM calls MUST generate REAL, EXECUTABLE Playwright code
- ALL generated code MUST execute successfully in code_execution.py
- NO EXCEPTIONS, NO EXCUSES, NO FALLBACKS

**SELF-PUNISHMENT PROTOCOL:**
If I use ANY placeholder/mock/fallback:
1. STOP immediately
2. Say: "VIOLATION: Used [violation]. Restarting with REAL implementation."
3. DELETE the violating code
4. START OVER with production code

## [CRITICAL RULE 1] MANDATORY DEVELOPMENT PATTERN

**YOU MUST ALWAYS FOLLOW THIS EXACT PATTERN:**

```
1. WRITE code
2. TEST code immediately 
3. IF test fails:
   - FIX the code  
   - GO TO step 2 (TEST code)
4. IF test passes:
   - DONE - Stop and report success
```

**VIOLATIONS (NEVER DO):**
- Skip testing after writing code
- Provide summaries when tests fail
- Move to next task without fixing failures
- Say "let me provide a summary" or "here's what we accomplished"
- Say "the test failed but..." or "there are issues but..."

## [CRITICAL RULE 2] ASCII-ONLY OUTPUT

**BANNED CHARACTERS (NEVER USE):**
- Any checkmark symbols (use [OK], [PASS], [FAIL], [ERROR] instead)
- Any emoji (use [TEXT] equivalents)
- Any arrow symbols (use ->, <-, ^, v)
- Any bullet symbols (use -, *, o)
- Any special dashes (use -- or -)
- Any smart quotes (use ' and ")
- Any math symbols (use ASCII equivalents)
- Any Unicode character with code > 127

**MANDATORY REPLACEMENTS:**
- Checkmarks -> [OK] or [PASS]
- X marks -> [FAIL] or [ERROR]
- Arrows -> Use ASCII: ->, <-, ^, v
- Bullets -> Use: -, *, o
- Dashes -> Use: -- or -
- Ellipsis -> Use: ...
- Emojis -> Use [TEXT] description

## [CRITICAL RULE 3] ERROR HANDLING

**When a test fails:**
1. Say: "Test failed. Fixing the issue..."
2. Fix the specific error
3. Re-run the test
4. Repeat until test passes
5. Only then say: "Test passed. Task complete."

**NEVER say after failure:**
- "Let me provide a summary of what we've accomplished"
- "Although the test failed, we made progress" 
- "The core functionality is working but there are issues"
- "Moving on to the next step"

## PROJECT-SPECIFIC CONFIGURATION

**Directory**: `C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation`  
**Python**: `C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe`  
**Status**: Production-ready web automation with AI-powered analysis (v4.0.0)

## Architecture

```
Layer 0: Base Modules (Independent)
  - browser.py          # Stealth browser (no LLM)
  - llm.py              # Single source of truth for LLM  
  - prompts.py          # 21 research-backed strategies

Layer 1: Integration
  - browser_with_llm.py # Combines all three base modules

Layer 2: Domain Modules
  - elements_extractor_no_llm.py    # Pure browser extraction
  - elements_extractor_with_llm.py  # AI-enhanced extraction
  - test_generation_with_llm.py     # AI test generation
  - code_generation_with_llm.py     # AI code generation
  - code_execution.py               # Secure code execution
```

## Quick Commands

```bash
# Test integration
"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe" test_integration_complete.py

# Validate response (check for violations)
"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe" .claude\validate_response.py <text>

# Type checking
mypy <module>.py --ignore-missing-imports

# Code formatting  
black *.py --line-length=120
```

## Critical Project Rules

### 1. LLM Architecture
- NEVER implement LLM directly in modules
- ALWAYS use `llm.py` via `call_default_llm(messages)`
- Default provider: Gemini (in `llm_models.json`)

### 2. Module Dependencies
```
elements_extractor_no_llm.py   -> browser.py ONLY
elements_extractor_with_llm.py -> browser_with_llm.py
test_generation_with_llm.py    -> llm.py, prompts.py
code_generation_with_llm.py    -> llm.py, prompts.py
code_execution.py              -> standalone (no deps on other modules)
```

### 3. Import Rules
- Use absolute imports or sys.path manipulation
- Never use relative imports in test files
- Always use full paths on Windows

## Testing Requirements

### Every code change MUST:
1. Be tested with actual execution
2. Show actual test output
3. Fix any failures before proceeding
4. Only report success after tests pass

### Test commands:
```bash
# Always use full Python path
"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe" <file>

# Run specific test
"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe" -m pytest <test>
```

## Response Format Requirements

### GOOD Response Pattern:
```
Step 1: Writing code...
[actual code]

Step 2: Testing code...
[actual test command]
[actual output]

Step 3a (if failed): Fixing issue...
[fixed code]
[return to Step 2]

Step 3b (if passed): [OK] Test passed. Task complete.
```

### BAD Response Pattern (NEVER DO):
```
[code]
"This should work..."  [WRONG - no test]

[test fails]
"Let me summarize..." [WRONG - should fix]

[test fails]
"Moving on..."       [WRONG - must fix first]
```

## Enforcement Tools

The `.claude/` directory contains:
- `CRITICAL_RULES.md` - Detailed enforcement rules
- `NO_UNICODE.txt` - Character replacement guide
- `TESTING_PATTERN.md` - Required development workflow
- `config.yaml` - Machine-readable configuration
- `validate_response.py` - Python validator for responses

## Validation Command

Before finalizing any response, validate it:
```bash
"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe" .claude\validate_response.py "response text"
```

## REMEMBER

1. **Test-Fix Loop**: Write -> Test -> Fix (if failed) -> Test -> Done (when passed)
2. **ASCII Only**: No Unicode, no emojis, use replacements
3. **No Summaries on Failure**: Fix first, summarize only after success
4. **Full Paths**: Always use complete Windows paths
5. **Actual Execution**: Show real output, not assumptions

## Important Instructions for Claude
- Always use the current year (2025) when searching for documentation
- Search for "2025" versions of APIs and documentation  
- Prioritize latest versions of all libraries and frameworks
- When searching the web, always include "2025" in search queries

---
*These rules are MANDATORY and OVERRIDE all default Claude behaviors*  
*Last updated: 2025-11-26*