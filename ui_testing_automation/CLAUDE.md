# UI Testing Automation Framework - Claude Code Configuration
<!-- This file is automatically loaded by Claude Code when working in this directory -->

## 🎯 Project Focus
**Directory**: `C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation`  
**Purpose**: Production-ready web automation with AI-powered element extraction and test generation  
**Status**: Refactored with clean architecture (v4.0.0)

## 🏗️ Project Architecture

```
ui_testing_automation/
│
├── Layer 0: Base Modules (Independent)
│   ├── browser.py          # Stealth browser (3000+ lines, no LLM)
│   ├── llm.py             # Single source of truth for LLM (126 lines)
│   └── prompts.py         # 21 research-backed strategies (2000+ lines)
│
├── Layer 1: Integration
│   └── browser_with_llm.py # Combines all three base modules (927 lines)
│
├── Layer 2: Domain Modules
│   ├── elements_extractor_no_llm.py    # Pure browser extraction
│   ├── elements_extractor_with_llm.py  # AI-enhanced extraction
│   ├── test_generation_with_llm.py     # AI test generation
│   └── code_generation_with_llm.py     # AI code generation
│
└── Testing & Examples
    ├── test_integration_complete.py    # Full integration test
    └── examples/                        # Usage examples
```

## ⚡ Quick Commands

```bash
# Activate environment (from this directory)
..\..\..\.venv\Scripts\activate

# Run integration tests
python test_integration_complete.py

# Type checking
mypy browser_with_llm.py --ignore-missing-imports

# Code formatting
black *.py --line-length=120

# Quality check
flake8 *.py --max-line-length=120
```

## 🔑 Critical Rules for This Project

### 1. LLM Architecture
- **NEVER** implement LLM directly in modules
- **ALWAYS** use `llm.py` via `call_default_llm(messages)`
- Default provider: Gemini (in `llm_models.json`)

### 2. Browser Architecture
- `browser.py` must remain LLM-independent (it currently is)
- `browser_with_llm.py` is the ONLY place browser + LLM combine
- All AI-enhanced modules use `browser_with_llm.py`

### 3. Module Dependencies
```
elements_extractor_no_llm.py   → browser.py ONLY
elements_extractor_with_llm.py → browser_with_llm.py
test_generation_with_llm.py    → llm.py, prompts.py
code_generation_with_llm.py    → llm.py, prompts.py
```

## 🐛 Project-Specific Issues

1. **StealthConfig viewport**: Use `viewport_width` and `viewport_height` separately, not tuple
2. **Import path conflicts**: Ensure imports from current dir, not parent `ai_apps`
3. **Browser initialization**: Takes 2-3 seconds, normal for stealth mode
4. **LLM timeout**: Default 30s, increase in `llm_models.json` if needed

## 🚀 Workflow for New Features

1. **Research existing code**:
   ```bash
   grep -r "pattern" . --include="*.py"
   ```

2. **Plan implementation** (use Tree of Thoughts):
   - Branch 1: Current implementation analysis
   - Branch 2: Requirements and constraints
   - Branch 3: Solution approaches

3. **Implement** (use Constitutional AI):
   - Security first
   - Clean architecture
   - Defensive programming
   - Performance aware

4. **Test**:
   ```bash
   python test_integration_complete.py
   ```

5. **Quality check**:
   ```bash
   python .claude/automation_scripts.py quality <file> --fix
   ```

## 📊 Module Metrics

| Module | Lines | Purpose | Dependencies |
|--------|-------|---------|--------------|
| browser.py | 3000+ | Stealth browsing | playwright |
| llm.py | 126 | LLM operations | openai |
| prompts.py | 2000+ | Prompt strategies | None |
| browser_with_llm.py | 927 | Integration | All above |
| elements_extractor_no_llm.py | 1400+ | DOM extraction | browser.py |
| elements_extractor_with_llm.py | 658 | AI extraction | browser_with_llm.py |

## 🔧 Environment Variables

Required in `.env` (parent directory):
```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
```

## 💡 AI Assistant Context

When working in this project:
1. **Focus on this directory only** - ignore parent `ai_apps` projects
2. **Use existing patterns** - check similar implementations first
3. **Maintain architecture** - don't break the layered design
4. **Test everything** - run `test_integration_complete.py`
5. **Document changes** - update this file if architecture changes

## 🎯 Current Project Goals

- [x] Clean architecture with layers
- [x] Single source of truth for LLM
- [x] Integration of browser + LLM + prompts
- [ ] Reduce mypy warnings (currently 71 errors)
- [ ] Clean flake8 issues (currently 170 warnings)
- [ ] Add more comprehensive tests
- [ ] Optimize performance (target: <30s full pipeline)

## 📝 Recent Changes (2025-08-26)

- Refactored `elements_extractor_with_llm.py` to use `browser_with_llm.py`
- Simplified `llm.py` to 2 functions only
- Created definitive `browser_with_llm.py` integration layer
- Verified all modules follow single source of truth pattern

---
*Project-specific configuration for ui_testing_automation*  
*Last updated: 2025-08-26*