# UI Testing Automation Framework - Architecture & Flow Diagram

## High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           UI TESTING AUTOMATION FRAMEWORK v4.0                           │
│                                  Production-Ready System                                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    EXTERNAL DEPENDENCIES                                 │
├───────────────────┬──────────────────┬──────────────────┬──────────────────────────────┤
│   Web Browser     │   LLM Providers  │  Test Runners    │    Reporting Systems         │
│   (Chromium)      │  - OpenAI GPT-4  │  - Pytest        │    - JSON Reports           │
│   via Playwright  │  - Gemini 2.5    │  - Playwright    │    - HTML Reports           │
│                   │  - Claude 3.5    │                  │    - Markdown Reports        │
└───────────────────┴──────────────────┴──────────────────┴──────────────────────────────┘
                                              ▲
                                              │
                                              │
```

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    LAYER 3: ORCHESTRATION                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         pipeline_integration.py                                  │   │
│  │                                                                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │   Pipeline   │  │   Circuit    │  │    Retry     │  │   Health     │       │   │
│  │  │ Orchestrator │──│   Breaker    │──│   Handler    │──│   Monitor    │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  │                                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐    │   │
│  │  │                    5-Stage Pipeline Execution Flow                       │    │   │
│  │  │  Stage 1 -> Stage 2 -> Stage 3 -> Stage 4 -> Stage 5                   │    │   │
│  │  │ (Extract) (Generate) (Code Gen) (Execute) (Report)                     │    │   │
│  │  └─────────────────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              ▲
                                              │ Orchestrates
                                              │
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    LAYER 2: DOMAIN MODULES                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌──────────────────────────┐  ┌──────────────────────────┐  ┌────────────────────┐    │
│  │ elements_extractor_no_llm│  │elements_extractor_w_llm │  │test_generation_w_llm│    │
│  │                          │  │                          │  │                      │    │
│  │  ┌──────────────────┐   │  │  ┌──────────────────┐   │  │ ┌──────────────────┐│    │
│  │  │ DOM Analysis     │   │  │  │ AI-Enhanced      │   │  │ │ Gherkin Generator││    │
│  │  │ Shadow DOM       │   │  │  │ Semantic Analysis│   │  │ │ 21 Strategies    ││    │
│  │  │ Iframe Traversal │   │  │  │ Context Aware    │   │  │ │ Test Categories  ││    │
│  │  │ Selector Gen     │   │  │  │ Smart Extraction │   │  │ │ Priority Ranking ││    │
│  │  └──────────────────┘   │  │  └──────────────────┘   │  │ └──────────────────┘│    │
│  │         Uses ▼          │  │      Uses ▼             │  │      Uses ▼         │    │
│  │      browser.py         │  │  browser_with_llm.py    │  │    llm.py          │    │
│  └──────────────────────────┘  └──────────────────────────┘  │    prompts.py     │    │
│                                                                └────────────────────┘    │
│                                                                                           │
│  ┌──────────────────────────┐  ┌──────────────────────────┐                            │
│  │ code_generation_with_llm │  │    code_execution.py     │                            │
│  │                          │  │                          │                            │
│  │  ┌──────────────────┐   │  │  ┌──────────────────┐   │                            │
│  │  │ Python Playwright│   │  │  │ Secure Sandbox   │   │                            │
│  │  │ Pytest Generator │   │  │  │ Test Runner      │   │                            │
│  │  │ POM Pattern     │   │  │  │ Coverage Report  │   │                            │
│  │  │ Quantum Gen     │   │  │  │ Result Collector │   │                            │
│  │  └──────────────────┘   │  │  └──────────────────┘   │                            │
│  │      Uses ▼             │  │      Executes ▼          │                            │
│  │    llm.py              │  │   Generated Code         │                            │
│  │    prompts.py          │  └──────────────────────────┘                            │
│  └──────────────────────────┘                                                           │
│                                                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              ▲
                                              │ Built on
                                              │
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              LAYER 1: INTEGRATION MODULE                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           browser_with_llm.py                                    │   │
│  │                                                                                   │   │
│  │  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                   │   │
│  │  │   Browser    │  +  │     LLM      │  +  │   Prompts    │  = Integrated     │   │
│  │  │ Integration  │     │ Integration  │     │ Integration  │    Browser+AI      │   │
│  │  └──────────────┘     └──────────────┘     └──────────────┘                   │   │
│  │                                                                                   │   │
│  │  Combines browser automation with LLM intelligence and prompt strategies         │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              ▲
                                              │ Depends on
                                              │
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               LAYER 0: BASE MODULES                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌──────────────────────────┐  ┌──────────────────────────┐  ┌────────────────────┐    │
│  │       browser.py         │  │         llm.py           │  │    prompts.py      │    │
│  │                          │  │                          │  │                     │    │
│  │  ┌──────────────────┐   │  │  ┌──────────────────┐   │  │ ┌─────────────────┐│    │
│  │  │ Stealth Browser  │   │  │  │ Multi-Provider   │   │  │ │ 21 Strategies:  ││    │
│  │  │ Anti-Detection   │   │  │  │ - OpenAI         │   │  │ │ - Chain of      ││    │
│  │  │ CloudFlare Bypass│   │  │  │ - Gemini         │   │  │ │   Thought       ││    │
│  │  │ Rate Limiting    │   │  │  │ - Anthropic      │   │  │ │ - Tree of       ││    │
│  │  │ Session Mgmt     │   │  │  │                  │   │  │ │   Thought       ││    │
│  │  │ Screenshot       │   │  │  │ Streaming Support│   │  │ │ - ReAct         ││    │
│  │  │ Element Extract  │   │  │  │ Fallback Chain   │   │  │ │ - Self          ││    │
│  │  └──────────────────┘   │  │  │ Config Driven    │   │  │ │   Consistency   ││    │
│  │                          │  │  └──────────────────┘   │  │ │ - Constitutional││    │
│  │  NO LLM Dependencies    │  │                          │  │ │   AI            ││    │
│  └──────────────────────────┘  │  Single Source of Truth │  │ └─────────────────┘│    │
│                                 └──────────────────────────┘  └────────────────────┘    │
│                                                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              COMPLETE DATA FLOW PIPELINE                                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘

     [USER INPUT]
          │
          ▼
    ┌──────────┐
    │   URL    │
    └──────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: ELEMENT EXTRACTION                                                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│    URL ──► browser.py ──► DOM Analysis ──► ExtractedElement[] ──┐                      │
│                │                                                  │                      │
│                ▼                                                  ▼                      │
│         Stealth Mode                                    ┌──────────────────┐            │
│         Anti-Detection                                  │ List of Elements │            │
│         Rate Limiting                                   │ - Buttons        │            │
│                                                         │ - Inputs         │            │
│                                                         │ - Links          │            │
│                                                         └──────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: TEST GENERATION (Gherkin Only)                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│    Elements[] ──► test_generation_with_llm.py ──► LLM Analysis ──► TestScenario[]      │
│                            │                            │                                │
│                            ▼                            ▼                                │
│                   Apply 21 Strategies          ┌──────────────────┐                     │
│                   - Chain of Thought           │ Gherkin Scenarios│                     │
│                   - Self Consistency           │ - Given/When/Then│                     │
│                   - Constitutional AI          │ - Test Data      │                     │
│                                                │ - Priorities     │                     │
│                                                └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: CODE GENERATION (Python Playwright Only)                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│    TestScenario[] ──► code_generation_with_llm.py ──► LLM Synthesis ──► Python Code    │
│                              │                              │                            │
│                              ▼                              ▼                            │
│                     Quantum Generation             ┌──────────────────┐                 │
│                     Pattern: POM                   │ Python Playwright│                 │
│                     Framework: pytest              │ - import pytest  │                 │
│                                                    │ - class TestSuite│                 │
│                                                    │ - def test_*()   │                 │
│                                                    └──────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: CODE EXECUTION                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│    Python Code ──► code_execution.py ──► Secure Sandbox ──► Test Results               │
│                           │                      │                                       │
│                           ▼                      ▼                                       │
│                   Security Checks        ┌──────────────────┐                          │
│                   Dependency Install     │  Execution Report │                          │
│                   Parallel Execution     │  - Pass/Fail     │                          │
│                                          │  - Coverage %    │                          │
│                                          │  - Duration      │                          │
│                                          └──────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 5: REPORTING                                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│    All Results ──► Report Generator ──► Multi-Format Output                             │
│                           │                      │                                       │
│                           ▼                      ▼                                       │
│                   Aggregate Metrics      ┌──────────────────┐                          │
│                   Generate Charts        │  - JSON Report   │                          │
│                   Format Output          │  - HTML Report   │                          │
│                                          │  - MD Report     │                          │
│                                          └──────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Module Relationships & Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            MODULE DEPENDENCY GRAPH                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                              pipeline_integration.py
                                      ╱│╲
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
        test_generation_with_llm  code_generation  code_execution
                    │                 │                 │
                    │                 │                 │ (standalone)
                    ▼                 ▼                 ▼
         ┌──────────┴──────┐  ┌──────┴──────┐         N/A
         │                 │  │              │
         ▼                 ▼  ▼              ▼
    llm.py           prompts.py         llm.py    prompts.py
         │                 │              │           │
         └─────────┬───────┘              └─────┬─────┘
                   │                             │
                   ▼                             ▼
            llm_models.json              llm_models.json
            
    
    elements_extractor_no_llm.py          elements_extractor_with_llm.py
                   │                                    │
                   ▼                                    ▼
             browser.py                        browser_with_llm.py
                                                       ╱│╲
                                          ┌────────────┼────────────┐
                                          ▼            ▼            ▼
                                    browser.py     llm.py     prompts.py


Legend:
  ──► Direct dependency
  ╱│╲ Multiple dependencies
  N/A No external dependencies (standalone)
```

## Contract & Data Structure Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          PYDANTIC V2 DATA CONTRACTS                                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌────────────────┐         ┌────────────────┐         ┌────────────────┐
    │ExtractedElement│ ──────► │  TestScenario  │ ──────► │ GeneratedCode  │
    ├────────────────┤         ├────────────────┤         ├────────────────┤
    │ selector       │         │ name           │         │ code           │
    │ element_type   │         │ description    │         │ language       │
    │ tag_name       │         │ category       │         │ framework      │
    │ attributes     │         │ priority       │         │ pattern        │
    │ text           │         │ steps[]        │         │ confidence     │
    │ is_clickable   │         │ test_data      │         └────────────────┘
    │ confidence     │         │ expected[]     │                │
    └────────────────┘         │ confidence     │                ▼
            │                  └────────────────┘         ┌────────────────┐
            │                          │                  │ExecutionResult │
            ▼                          ▼                  ├────────────────┤
    ┌────────────────┐         ┌────────────────┐        │ success        │
    │ExtractionResult│         │ TestSuite      │        │ test_results[] │
    ├────────────────┤         ├────────────────┤        │ passed_tests   │
    │ elements[]     │         │ name           │        │ failed_tests   │
    │ success        │         │ framework      │        │ execution_time │
    │ errors[]       │         │ scenarios[]    │        │ coverage_%     │
    │ statistics     │         │ feature_name   │        └────────────────┘
    │ screenshots[]  │         │ description    │                │
    └────────────────┘         └────────────────┘                ▼
                                                          ┌────────────────┐
                                                          │ PipelineResult │
                                                          ├────────────────┤
                                                          │ stages{}       │
                                                          │ success        │
                                                          │ duration       │
                                                          │ metrics{}      │
                                                          └────────────────┘
```

## Production Features & Patterns

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          PRODUCTION-GRADE FEATURES                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │                     FAULT TOLERANCE                               │
    ├──────────────────────────────────────────────────────────────────┤
    │                                                                  │
    │  Circuit Breaker ────► Prevents cascade failures                │
    │       │                                                          │
    │       ▼                                                          │
    │  [Closed] ──fail──► [Open] ──timeout──► [Half-Open]            │
    │                                              │                   │
    │                                              ▼                   │
    │                                         Test & Reset             │
    │                                                                  │
    │  Retry Logic ────► Exponential backoff with jitter              │
    │       │                                                          │
    │       ▼                                                          │
    │  Attempt 1 (1s) ► Attempt 2 (2s) ► Attempt 3 (4s) ► Fail       │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │                      MONITORING & OBSERVABILITY                   │
    ├──────────────────────────────────────────────────────────────────┤
    │                                                                  │
    │  Health Monitor ────► Real-time system health                   │
    │       │                                                          │
    │       ├──► CPU Usage                                            │
    │       ├──► Memory Usage                                         │
    │       ├──► Response Times                                       │
    │       └──► Error Rates                                          │
    │                                                                  │
    │  Logging ────► Structured logging with levels                   │
    │       │                                                          │
    │       ├──► INFO:  Normal operations                             │
    │       ├──► WARN:  Degraded performance                          │
    │       ├──► ERROR: Failures & exceptions                         │
    │       └──► DEBUG: Detailed diagnostics                          │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │                         SECURITY FEATURES                         │
    ├──────────────────────────────────────────────────────────────────┤
    │                                                                  │
    │  Code Execution Sandbox                                         │
    │       │                                                          │
    │       ├──► Isolated environment                                 │
    │       ├──► Resource limits                                      │
    │       ├──► No network access                                    │
    │       └──► Timeout protection                                   │
    │                                                                  │
    │  API Key Management                                             │
    │       │                                                          │
    │       ├──► Environment variables only                           │
    │       ├──► Never in logs                                        │
    │       └──► Rotation support                                     │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘
```

## Configuration Files

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION HIERARCHY                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    .env (API Keys & Secrets)
         │
         ▼
    llm_models.json (LLM Configuration)
         │
         ├──► Default Provider & Model
         ├──► Provider Configurations
         ├──► Model Capabilities
         └──► Fallback Chain
    
    CLAUDE.md (Development Guidelines)
         │
         ├──► Architecture Rules
         ├──► Module Dependencies
         ├──► Error Handling
         └──► Performance Targets
```

## Summary Statistics

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              FRAMEWORK STATISTICS                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  Total Modules:           11 production modules                                          │
│  Lines of Code:           ~15,000+ lines                                                 │
│  Test Coverage:           Production-tested with real websites                           │
│  LLM Providers:           3 (OpenAI, Gemini, Anthropic)                                 │
│  Prompt Strategies:       21 research-backed strategies                                  │
│  Architecture Layers:     4 (Base, Integration, Domain, Orchestration)                   │
│  Design Patterns:         Circuit Breaker, Retry, Factory, Strategy, Observer            │
│  Data Contracts:          15+ Pydantic v2 models                                        │
│  Output Formats:          JSON, HTML, Markdown                                          │
│  Browser Features:        Stealth mode, Anti-detection, CloudFlare bypass               │
│  Security Features:       Sandboxed execution, API key protection                       │
│  Production Ready:        100% - Tested with GitHub, LinkedIn, Amazon                   │
│                                                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---
*Architecture Version: 4.0.0*
*Last Updated: 2025-08-27*
*Status: Production Ready*