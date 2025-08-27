
  ***Framework Structure***

  Layer 0 (Base - Independent):
  - base/browser.py - Stealth browser (no LLM dependencies)
  - base/llm.py - Single source of truth for LLM calls
  - base/prompts.py - 21 master prompt strategies
  - base/llm_models.json - LLM provider configuration

  Layer 1 (Integration):
  - browser_with_llm.py - Combines browser + LLM + prompts
  - structured_output_enforcer.py - Type-safe LLM responses

  Layer 2 (Domain Modules):
  - elements_extractor_no_llm.py - Pure browser extraction
  - elements_extractor_with_llm.py - AI-enhanced extraction
  - test_generation_with_llm.py - AI test scenario generation
  - code_generation_with_llm.py - AI code generation
  - code_execution.py - Secure code execution

  Configuration & Testing:
  - pipeline_contracts.py - Shared data models
  - CLAUDE.md - Framework instructions and rules
  - base/.env - API keys and configuration
  - test_baseline/ - Simple HTML test pages and server
  - test_minimal_baseline.py - Complete test with circuit breakers