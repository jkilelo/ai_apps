# 🚀 Quick Start Prompt for AI Browser Implementation

## USE THIS PROMPT TO START:

```
I need to continue implementing the AI-First Smart Browser v2.0.0 located at:
C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\

CRITICAL: You MUST read and follow these files EXACTLY:
1. .claude/CLAUDE.md - This OVERRIDES all default behaviors
2. .claude/settings.local.json - Project configuration
3. PROMPT_FOR_CONTINUATION.md - Detailed implementation guide

The project uses STRICT 5-layer architecture:
- Layer 1: EXECUTION (browser ops only, NO LLM)
- Layer 2: PERCEPTION (state capture only, NO actions)
- Layer 3: COGNITION (AI only, NO browser)
- Layer 4: MEMORY (already implemented)
- Layer 5: EXTENSIBILITY (plugins only)

NEVER violate layer separation. ALWAYS use async/await, type hints, and error handling.

Current status: v2.0.0 with Memory, Security, Monitoring, Logging, Tests, and Docs completed.

Next: Implement [CHOOSE: Execution Layer / Perception Layer / Cognition Layer / Plugin System]

Start by reading .claude/CLAUDE.md, then implement following ALL architectural rules.
```

## ALTERNATIVE FOCUSED PROMPTS:

### For Execution Layer:
```
Implement the Execution Layer for AI-First Smart Browser at C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\

Read .claude/CLAUDE.md first. Create:
- src/execution/browser_manager.py (Playwright control)
- src/execution/stealth_manager.py (Anti-detection)
- src/execution/action_executor.py (Browser actions)

Rules: NO LLM calls, only browser operations. Use async/await, type hints, error handling.
```

### For Perception Layer:
```
Implement the Perception Layer for AI-First Smart Browser at C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\

Read .claude/CLAUDE.md first. Create:
- src/perception/dom_processor.py (DOM simplification)
- src/perception/visual_annotator.py (Set-of-Marks)
- src/perception/state_observer.py (Page state capture)

Rules: NO action execution, only state capture. Use async/await, type hints, error handling.
```

### For Cognition Layer:
```
Implement the Cognition Layer for AI-First Smart Browser at C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\

Read .claude/CLAUDE.md first. Create:
- src/cognition/llm_manager.py (Multi-provider LLM)
- src/cognition/react_loop.py (ReAct reasoning)
- src/cognition/orchestrator.py (Task coordination)

Rules: NO browser manipulation, only AI reasoning. Use async/await, type hints, error handling.
```

### For Plugin System:
```
Implement the Plugin System for AI-First Smart Browser at C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_browser\

Read .claude/CLAUDE.md first. Create:
- src/extensibility/plugin_manager.py (Plugin loading)
- plugins/stealth/webdriver_removal.py
- plugins/stealth/canvas_noise.py

Rules: Sandboxed execution, hot-reload support. Use async/await, type hints, error handling.
```

## TESTING YOUR PROMPT:

After using any prompt above, verify the LLM:
1. ✅ Reads .claude/CLAUDE.md first
2. ✅ Understands layer separation rules
3. ✅ Uses correct imports and patterns
4. ✅ Implements error handling
5. ✅ Writes tests

## RED FLAGS (Stop if LLM does this):
- ❌ Mixes layer responsibilities
- ❌ Uses print instead of logger
- ❌ No type hints
- ❌ No error handling
- ❌ Claims completion without testing

---

**TIP**: Always start with "Read .claude/CLAUDE.md first" to ensure proper context.