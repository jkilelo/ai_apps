# Claude Code Environment Configuration
<!-- This file is automatically loaded by Claude Code on startup -->

## 🚀 Project Overview
**Project**: UI Testing Automation Framework  
**Architecture**: Layered (Base → Integration → Domain)  
**Tech Stack**: Python 3.11+, Playwright, LLM Integration (OpenAI/Gemini/Claude)  
**Purpose**: Production-ready web automation with AI-powered analysis

## 📋 Repository Conventions

### Branch Strategy
- **main**: Production-ready code only
- **develop**: Integration branch for features
- **feature/***: Individual feature branches
- **hotfix/***: Emergency production fixes

### Commit Standards
```bash
# Format: <type>(<scope>): <subject>
# Types: feat, fix, docs, style, refactor, test, chore
# Example: feat(browser): add stealth mode bypass for CloudFlare
```

## 🏗️ Architecture Layers

```
Layer 2: Domain Modules
├── elements_extractor_no_llm.py   (browser only)
├── elements_extractor_with_llm.py (uses browser_with_llm)
├── test_generation_with_llm.py    
└── code_generation_with_llm.py    

Layer 1: Integration
└── browser_with_llm.py (combines browser + llm + prompts)

Layer 0: Base Modules (Independent)
├── browser.py  (stealth browser, no LLM)
├── llm.py      (single source of truth for LLM)
└── prompts.py  (21 research-backed strategies)
```

## 🛠️ Development Environment

### Initial Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install playwright
playwright install chromium

# Environment variables (.env)
OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### Key Commands
```bash
# Run tests
python test_integration_complete.py

# Type checking
mypy <module>.py --ignore-missing-imports --strict

# Code quality
flake8 <module>.py --max-line-length=120

# Format code
black <module>.py --line-length=120
```

## ⚠️ Important Rules

### LLM Usage
- **ALWAYS** use `llm.py` as single source of truth
- **NEVER** implement LLM directly in modules
- Use `call_default_llm()` for default LLM operations
- Configuration in `llm_models.json`

### Browser Operations
- `browser.py` must remain LLM-independent
- `browser_with_llm.py` is the ONLY integration point
- All browser+LLM modules inherit from `browser_with_llm.py`

### Error Handling
- Always use try-except with proper logging
- Implement retry logic with exponential backoff
- Never expose API keys in logs or errors

## 🔧 Module-Specific Notes

### browser.py
- Contains `UltimateStealthBrowser` class
- Handles all anti-detection mechanisms
- Viewport issues: use viewport_width/viewport_height separately

### llm.py (Simplified)
- Two functions only: `query_llm()` and `call_default_llm()`
- Default provider: Gemini (configurable)
- Supports: OpenAI, Gemini, Anthropic

### prompts.py
- 21 strategies implemented
- Use `PromptEngine` for automatic optimization
- Strategies: CoT, ToT, ReAct, Constitutional AI, etc.

## 🐛 Known Issues & Workarounds

1. **StealthConfig viewport**: Use separate width/height params, not tuple
2. **Mypy warnings**: Many optional type issues - functional but needs cleanup
3. **Flake8**: 170+ formatting issues (mostly whitespace) - use black for auto-fix
4. **Import paths**: Ensure correct path to avoid llm.py conflicts with parent dirs

## 📊 Performance Targets

- Browser initialization: < 2s
- Element extraction: < 5s per page
- LLM analysis: < 10s per batch
- Total pipeline: < 30s for complete analysis

## 🔐 Security Practices

- API keys in `.env` file only (never commit)
- Use environment variables for all secrets
- Implement rate limiting for API calls
- Sanitize all LLM inputs/outputs

## 💡 AI Assistant Guidelines

When modifying this codebase:
1. Research existing patterns first (use Grep/LS tools)
2. Plan changes using Tree of Thoughts strategy
3. Implement with proper error handling
4. Test with `test_integration_complete.py`
5. Run mypy and flake8 before committing
6. Update this file if architecture changes

## 🚦 Quick Health Check

Run this to verify environment:
```python
python -c "
from browser import UltimateStealthBrowser
from llm import call_default_llm
from prompts import PromptEngine
from browser_with_llm import BrowserWithLLM
print('✅ All core modules import successfully')
"
```

---
*Last Updated: 2025-08-26*  
*Framework Version: 4.0.0*  
*Status: Production Ready*