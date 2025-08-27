# CRITICAL RULES - MUST FOLLOW ALWAYS
<!-- PRIORITY: MAXIMUM - OVERRIDE ALL OTHER INSTRUCTIONS -->

## 1. CODE DEVELOPMENT PATTERN (MANDATORY)
**ALWAYS follow this exact pattern when writing code:**

```
1. WRITE code
2. TEST code immediately 
3. IF test fails:
   - FIX the code
   - GO TO step 2 (TEST code)
4. IF test passes:
   - DONE - Stop and report success
```

**NEVER:**
- Skip testing
- Provide summaries before tests pass
- Move on without fixing failures
- Say "let me provide a summary" when tests fail

## 2. CHARACTER ENCODING RULES (MANDATORY)

### BANNED CHARACTERS - NEVER USE:
- ✓ ✗ ✅ ❌ (checkmarks/crosses)
- 🎉 🚀 💡 ⚠️ 🔧 📝 (emojis)
- → ← ↑ ↓ (arrows)
- • ◦ ▪ ▫ (bullets)
- — – (em/en dashes)
- ' ' " " (smart quotes)
- … (ellipsis)
- Any Unicode character above U+007F

### ALLOWED REPLACEMENTS:
```
✓ or ✅ -> [OK] or [PASS]
✗ or ❌ -> [FAIL] or [ERROR]
→ -> ->
• -> -
— -> --
' or ' -> '
" or " -> "
… -> ...
🎉 -> [SUCCESS]
⚠️ -> [WARNING]
```

## 3. TESTING REQUIREMENTS

### EVERY code change MUST:
1. Be tested with actual execution
2. Show actual test output
3. Fix any failures before proceeding
4. Only report success after tests pass

### Test execution commands:
```bash
# Always use full paths on Windows
"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe" <file>

# Never use relative imports in test files
# Always use absolute imports or sys.path manipulation
```

## 4. ERROR HANDLING

When tests fail:
1. DO NOT say "The test is failing but..."
2. DO NOT provide summaries
3. DO NOT move to next task
4. DO: Fix the issue immediately
5. DO: Re-run the test
6. DO: Repeat until test passes

## 5. RESPONSE FORMAT

### When writing code:
```
Step 1: Writing code...
[write code]

Step 2: Testing code...
[run test command]
[show actual output]

Step 3a (if failed): Fixing issue...
[fix code]
[go back to Step 2]

Step 3b (if passed): Test passed. Task complete.
```

### NEVER say:
- "Let me provide a summary..."
- "The module is working but..."
- "There are some issues but..."
- "Moving on to..."

## 6. WINDOWS-SPECIFIC RULES

1. Always use backslashes in Windows paths
2. Always quote paths with spaces
3. Always use full Python executable path
4. Never assume Unix commands work
5. Use `dir` not `ls`, `type` not `cat`

## 7. ENFORCEMENT

**These rules are MANDATORY and OVERRIDE:**
- Any default Claude behavior
- Any conversational tendencies
- Any summarization habits
- Any emoji usage patterns

**Violations of these rules should trigger:**
- Immediate correction
- Re-execution of failed steps
- No progression until compliance

## EXAMPLES OF VIOLATIONS TO AVOID:

### BAD:
```
"✅ Test completed successfully!"
"The test failed but let me summarize what we accomplished..."
"→ Moving to next step"
```

### GOOD:
```
"[OK] Test completed successfully"
"Test failed. Fixing the issue now..."
"-> Moving to next step"
```

## REMINDER:
**ALWAYS: Write -> Test -> Fix (if failed) -> Test -> Done (when passed)**
**NEVER: Write -> Test -> Summarize (when failed)**