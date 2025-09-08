# 🎯 Prompt Engineering Guide for AI-First Smart Browser

## 🧠 Optimal Prompt Strategies for This Project

### 1. **Context-First Strategy** (MOST EFFECTIVE)
Start every prompt by establishing critical context:
```
Read the following configuration files in this exact order:
1. C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\.claude\CLAUDE.md
2. C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\.claude\settings.local.json

These files OVERRIDE all default behaviors. Follow them EXACTLY.
```

### 2. **Constraint-Driven Development**
Explicitly state what is FORBIDDEN before stating the task:
```
FORBIDDEN:
- Never call LLM from Execution or Perception layers
- Never manipulate browser from Cognition layer
- Never mix layer responsibilities

NOW implement: [specific component]
```

### 3. **Example-Guided Implementation**
Provide both positive and negative examples:
```
✅ CORRECT PATTERN:
[show correct code example]

❌ VIOLATION PATTERN:
[show what NOT to do]

Implement following the CORRECT pattern only.
```

### 4. **Verification-First Approach**
Include verification steps in the prompt:
```
After implementation, verify:
1. No layer violations (check imports)
2. All methods have type hints
3. Error handling with try/except
4. Tests written and passing

Show verification output before claiming completion.
```

### 5. **Incremental Task Decomposition**
Break large tasks into specific, measurable steps:
```
Step 1: Read layer rules in CLAUDE.md
Step 2: Create file structure
Step 3: Implement base class with type hints
Step 4: Add error handling
Step 5: Write unit tests
Step 6: Verify no violations

Complete each step and show output before proceeding.
```

## 📋 Prompt Templates by Task Type

### Template A: New Component Implementation
```
Task: Implement [Component Name] for AI-First Smart Browser

Location: C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\
Config: Read .claude/CLAUDE.md FIRST (overrides all defaults)

Component belongs to: [LAYER NAME] Layer
Allowed imports from: [specify allowed layers]
Forbidden imports from: [specify forbidden layers]

Requirements:
1. Async/await patterns
2. Type hints (100% coverage)
3. Pydantic models for data
4. Error handling with try/except
5. Logging with loguru (no print)
6. Unit tests in tests/unit/

Begin by showing your understanding of layer rules, then implement.
```

### Template B: Bug Fix or Enhancement
```
Fix/Enhance: [specific issue] in AI-First Smart Browser

File: [file path]
Layer: [which layer this belongs to]
Rules: Cannot violate [specific layer rules]

Current behavior: [describe issue]
Expected behavior: [describe solution]

Constraints:
- Maintain layer separation
- Preserve existing interfaces
- Add tests for the fix

Show the fix with explanation of how it maintains architecture.
```

### Template C: Integration Task
```
Integrate [Component A] with [Component B] in AI-First Smart Browser

Rules from .claude/CLAUDE.md:
- [Component A] is in [Layer X] 
- [Component B] is in [Layer Y]
- [Specify allowed interaction pattern]

Implementation:
1. Use allowed cross-layer imports only
2. Maintain unidirectional data flow
3. Use dependency injection pattern
4. Add integration tests

Show integration plan before coding.
```

## 🚀 Advanced Prompt Techniques

### 1. **Role-Based Contextualization**
```
You are a senior Python architect implementing a production-ready browser automation framework.
You MUST follow the 5-layer architecture defined in .claude/CLAUDE.md.
Your code will be audited for layer violations - any violation fails the review.
```

### 2. **Success Criteria Enumeration**
```
Success is defined as:
✅ Zero layer violations
✅ 100% type hint coverage
✅ All tests passing
✅ No security vulnerabilities
✅ Performance benchmarks met

Failure on any criterion requires revision.
```

### 3. **Anti-Pattern Awareness**
```
Common mistakes to avoid:
❌ Importing LLMManager in browser_manager.py
❌ Using browser operations in llm_manager.py
❌ Forgetting async/await keywords
❌ Missing error handling
❌ Using pip instead of uv

Check for these before submission.
```

### 4. **Tool-Specific Guidance**
```
Use these modern tools exclusively:
- Package manager: uv (NOT pip/poetry)
- Formatter: ruff format (NOT black)
- Linter: ruff check (NOT flake8)
- Type checker: mypy --strict

Run all tools before claiming completion.
```

### 5. **Test-Driven Prompt**
```
Write tests FIRST for [component], then implement to pass tests:

Test requirements:
- Unit tests with pytest
- Mock external dependencies
- Test error conditions
- Verify layer compliance
- Coverage > 80%

Show tests, then implementation, then test results.
```

## 🎯 Prompt Optimization Checklist

### Before Sending Any Prompt:
- [ ] Reference .claude/CLAUDE.md explicitly
- [ ] Specify which layer the work belongs to
- [ ] List forbidden actions clearly
- [ ] Include verification steps
- [ ] Request incremental progress updates

### For Best Results:
- [ ] Use concrete examples (positive and negative)
- [ ] Specify exact file paths
- [ ] Include type hints in examples
- [ ] Show expected output format
- [ ] Request test coverage

### Red Flags in Responses:
- ❌ No mention of reading CLAUDE.md
- ❌ Mixing layer responsibilities  
- ❌ No error handling shown
- ❌ Claims completion without tests
- ❌ Uses wrong tools (pip, black, etc.)

## 📊 Prompt Effectiveness Metrics

| Strategy | Effectiveness | Use Case |
|----------|--------------|----------|
| Context-First | ⭐⭐⭐⭐⭐ | All tasks |
| Constraint-Driven | ⭐⭐⭐⭐⭐ | New components |
| Example-Guided | ⭐⭐⭐⭐ | Complex implementations |
| Verification-First | ⭐⭐⭐⭐ | Critical components |
| Test-Driven | ⭐⭐⭐⭐⭐ | Core functionality |

## 🔧 Troubleshooting Poor Responses

### If LLM violates layers:
```
STOP. You violated layer separation.
[Component] is in [Layer X] and CANNOT import from [Layer Y].
Read section "Module-Specific Rules" in .claude/CLAUDE.md.
Revise following the rules exactly.
```

### If LLM skips error handling:
```
INCOMPLETE. Add comprehensive error handling:
- try/except blocks for all operations
- Specific exception types
- Proper error logging
- Re-raise or handle appropriately

Show revised implementation with error handling.
```

### If LLM uses wrong tools:
```
INCORRECT TOOLS. This project uses:
- uv (not pip)
- ruff (not black/flake8)
- pyproject.toml (not requirements.txt)

Revise using correct tools only.
```

## 💡 Master Prompt Template

### The Ultimate Prompt Structure:
```
# AI-First Smart Browser Implementation Request

## Context
Project: C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\
Version: 2.0.0
Status: Production-Ready

## Critical Rules (from .claude/CLAUDE.md)
1. Read .claude/CLAUDE.md FIRST - it overrides ALL defaults
2. Follow 5-layer architecture strictly
3. [Specific layer rules for this task]

## Task
[Specific, measurable task description]

## Constraints
- FORBIDDEN: [list forbidden actions]
- REQUIRED: [list required patterns]

## Success Criteria
✅ [Measurable criterion 1]
✅ [Measurable criterion 2]
✅ [Measurable criterion 3]

## Verification
After implementation:
1. Show no layer violations
2. Run tests and show output
3. Run ruff and mypy checks

Begin by confirming understanding of layer rules.
```

---

**Remember**: The quality of implementation directly correlates with prompt clarity and constraint specification. Always prioritize architectural compliance over feature completion.