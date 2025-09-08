# 🎯 AI-First Smart Browser Implementation Prompt

## CRITICAL CONTEXT
You are implementing the **AI-First Smart Browser v2.0.0**, a production-ready web automation framework. The project has **STRICT ARCHITECTURAL RULES** that MUST be followed.

## 🔴 MANDATORY CONFIGURATION TO FOLLOW

### Primary Configuration Files (READ THESE FIRST)
1. **`.claude/CLAUDE.md`** - OVERRIDES ALL DEFAULT BEHAVIORS
2. **`.claude/settings.local.json`** - Project-specific settings
3. **`.claude/custom-commands.json`** - Available commands
4. **`.claude/CAPABILITIES.md`** - Current implementation status

## ⚠️ ABSOLUTE RULES (NEVER VIOLATE)

### 5-Layer Architecture (STRICT SEPARATION)
```
Layer 1: EXECUTION     → Browser control ONLY (NO LLM calls)
Layer 2: PERCEPTION    → State capture ONLY (NO actions)  
Layer 3: COGNITION     → AI reasoning ONLY (NO browser ops)
Layer 4: MEMORY        → Storage ONLY (Already implemented)
Layer 5: EXTENSIBILITY → Plugins ONLY
```

### FORBIDDEN Actions
- ❌ **NEVER** call LLMs from Execution or Perception layers
- ❌ **NEVER** manipulate browser from Cognition layer
- ❌ **NEVER** mix layer responsibilities
- ❌ **NEVER** create files outside designated directories
- ❌ **NEVER** remove stealth capabilities

### REQUIRED Practices
- ✅ **ALWAYS** use type hints and Pydantic models
- ✅ **ALWAYS** implement async/await patterns
- ✅ **ALWAYS** handle errors with try/except
- ✅ **ALWAYS** use the logger (not print)
- ✅ **ALWAYS** test before claiming completion

## 📋 CURRENT STATUS

### ✅ COMPLETED Components (v2.0.0)
- Memory Layer (SQLite, Qdrant, FalkorDB)
- Security (Encryption, Rate Limiting, Auditing)  
- Monitoring (Metrics, Alerts, Health Checks)
- Logging System (Structured, Specialized Loggers)
- Test Suite (Unit, Integration, Stealth)
- CI/CD Pipeline (GitHub Actions)
- Documentation (MkDocs)
- Examples (Basic, Advanced, Security)

### 🔧 PENDING Implementation
Choose ONE of these to implement next:

#### Option 1: Complete Execution Layer
```python
# src/execution/browser_manager.py
# src/execution/stealth_manager.py  
# src/execution/action_executor.py
```
- Implement BrowserManager with Playwright
- Add StealthManager with plugin system
- Create ActionExecutor for browser operations

#### Option 2: Complete Perception Layer
```python
# src/perception/dom_processor.py
# src/perception/visual_annotator.py
# src/perception/state_observer.py
```
- Implement DOM simplification
- Add Set-of-Marks visual annotation
- Create comprehensive state capture

#### Option 3: Complete Cognition Layer
```python
# src/cognition/llm_manager.py
# src/cognition/react_loop.py
# src/cognition/orchestrator.py
```
- Implement multi-provider LLM support
- Add ReAct reasoning pattern
- Create task orchestration

#### Option 4: Implement Plugin System
```python
# src/extensibility/plugin_manager.py
# plugins/stealth/*.py
```
- Create plugin loading mechanism
- Implement stealth plugins
- Add hot-reload support

## 🛠️ IMPLEMENTATION GUIDELINES

### When Implementing ANY Component:

1. **Check Architecture Rules**
   - Which layer does this belong to?
   - What can this layer access?
   - What is forbidden?

2. **Follow Code Standards**
   ```python
   # ALWAYS use this pattern:
   from typing import Dict, List, Optional, Any
   from pydantic import BaseModel
   import asyncio
   from loguru import logger
   
   class ComponentName:
       """Docstring required"""
       
       async def method_name(self, param: Type) -> ReturnType:
           """Docstring required"""
           try:
               # Implementation
               logger.info("Operation completed")
               return result
           except Exception as e:
               logger.error(f"Operation failed: {e}")
               raise
   ```

3. **Test Your Implementation**
   - Write unit tests in `tests/unit/`
   - Verify no layer violations
   - Check error handling

4. **Use Modern Tools**
   - Package manager: `uv` (NOT pip)
   - Formatter/Linter: `ruff` (NOT black/flake8)
   - Config: `pyproject.toml` (NOT requirements.txt)

## 📍 SPECIFIC TASK INSTRUCTIONS

### Your Task:
[CHOOSE ONE OF THE PENDING OPTIONS ABOVE]

### Implementation Steps:
1. Read relevant sections in `.claude/CLAUDE.md`
2. Check existing code structure
3. Implement following the layer rules
4. Add comprehensive error handling
5. Write tests
6. Update documentation

### Success Criteria:
- ✅ No layer violations
- ✅ All methods have type hints
- ✅ Error handling implemented
- ✅ Logging added
- ✅ Tests written
- ✅ Documentation updated

## 🎯 EXAMPLE CORRECT IMPLEMENTATION

```python
# src/execution/browser_manager.py
# ✅ CORRECT - Execution layer only handles browser operations

from typing import Optional, Dict, Any
from playwright.async_api import Browser, BrowserContext, Page
from pydantic import BaseModel
from loguru import logger

class BrowserConfig(BaseModel):
    """Browser configuration model"""
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    stealth_mode: bool = True

class BrowserManager:
    """Manages browser lifecycle and operations"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        logger.info("BrowserManager initialized")
    
    async def launch(self, config: BrowserConfig) -> Browser:
        """Launch browser with configuration"""
        try:
            # Implementation here
            # NO LLM CALLS - this is execution layer!
            logger.info("Browser launched successfully")
            return self.browser
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            raise
```

## ❌ EXAMPLE VIOLATION

```python
# ❌ WRONG - Execution layer calling LLM
class BrowserManager:
    async def smart_click(self, prompt: str):
        # ❌ VIOLATION - Execution layer cannot call LLM!
        response = await self.llm.generate(prompt)  # FORBIDDEN!
        await page.click(response.selector)
```

## 🚦 CHECKLIST BEFORE COMPLETION

Before claiming any task is complete, verify:

- [ ] Layer separation maintained
- [ ] Type hints on all methods
- [ ] Error handling with try/except
- [ ] Logging instead of print
- [ ] Tests written and passing
- [ ] No forbidden imports
- [ ] Documentation updated
- [ ] Code formatted with ruff

## 📚 REFERENCE COMMANDS

Use these commands to verify your work:

```bash
# Test your implementation
pytest tests/unit/test_your_component.py -v

# Check code quality
ruff check src/
ruff format src/

# Type checking
mypy src/ --strict

# Run security audit
python -c "from src.security.audit import run_security_audit; print(run_security_audit())"
```

---

## 🎬 START IMPLEMENTATION

**NOW**: Choose ONE pending component and implement it following ALL rules above. Start by:

1. State which component you're implementing
2. Confirm you understand the layer rules
3. Show your implementation plan
4. Begin coding with proper structure

Remember: **QUALITY > SPEED**. One correctly implemented component is better than three with violations.

---
*This prompt ensures strict adherence to the AI-First Smart Browser architecture v2.0.0*