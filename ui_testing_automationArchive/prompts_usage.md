# PROMPTS Module Usage Guide (Real-World Examples)

Comprehensive, role-aware examples for using `prompts.py` across UI Testing, QA, DevOps, Product, and Advanced AI Engineering workflows.

---

## 1. Quick Overview

The `PromptEngine` unifies 21 prompt strategies + a template system + performance tracking + A/B testing + optimization.

Core objects:

- `PromptEngine` – main orchestrator (strategy selection, templates, metrics, cache)
- `PromptRequest` / `PromptResponse` – IO contracts
- `PromptStrategy` / `TaskType` / `ComplexityLevel` – enums guiding selection
- `TemplateManager` – reusable parameterized prompt blueprints
- `PerformanceTracker` – success/time/confidence & A/B test registry

When to use:

- Need a *structured* prompt for LLM tasks (debugging, test generation, extraction, optimization)
- Want *repeatability* + *metrics* for strategy effectiveness
- Need *safe fallback + alternative strategies* for experimentation

---

## 2. Minimal Quick Start

```python
from ui_testing_automation.prompts import PromptEngine, PromptRequest, TaskType

engine = PromptEngine()
req = PromptRequest(
    task="Summarize why visual regression testing matters (<=60 words)",
    task_type=TaskType.ANALYTICAL
)
resp = engine.generate_prompt(req)
print(resp.strategy_used, resp.confidence)
print(resp.enhanced_prompt[:400])  # feed to LLM afterward
```

---

## 3. Strategy Auto-Selection vs Forced Strategy

```python
# Auto (let engine pick best based on TaskType + Complexity)
req_auto = PromptRequest(task="Generate login edge test cases", task_type=TaskType.GENERATION)
resp_auto = engine.generate_prompt(req_auto)

# Force a specific strategy (e.g., Tree of Thoughts)
from ui_testing_automation.prompts import PromptStrategy
req_forced = PromptRequest(
    task="Design a migration approach from Selenium to Playwright",
    task_type=TaskType.REASONING,
    preferred_strategies=[PromptStrategy.TREE_OF_THOUGHTS]
)
resp_forced = engine.generate_prompt(req_forced)
```

---

## 4. Using Built-In Templates

```python
# Element extraction
resp_template = engine.generate_with_template(
    template_name="element_extraction",
    task_type=TaskType.EXTRACTION,
    html_content="""
    <form id='signup'>
      <input name='email' type='email' required>
      <input name='pwd' type='password' minlength='8' required>
      <button type='submit'>Create Account</button>
    </form>
    """
)
print(resp_template.strategy_used, resp_template.templates_used)
```

```python
# Test generation template
resp_tests = engine.generate_with_template(
    template_name="test_generation",
    task_type=TaskType.GENERATION,
    feature_name="Checkout Flow",
    feature_description="User purchases items with shipping + payment",
    requirements="Cart, address validation, payment gateway retry, order id uniqueness",
    min_scenarios=12,
)
```

---

## 5. Real-World Scenario Gallery

### 5.1 QA Engineer – Generate Negative & Edge Tests

```python
req = PromptRequest(
    task="Generate edge + invalid input scenarios for password reset email field (RFC 5322 awareness)",
    task_type=TaskType.GENERATION,
    complexity=ComplexityLevel.COMPLEX,
    preferred_strategies=[PromptStrategy.SELF_CONSISTENCY]
)
resp = engine.generate_prompt(req)
```

### 5.2 Security Review – Constitutional AI Safeguards

```python
req = PromptRequest(
    task="Assess potential security risks in a feature allowing file uploads (pdf, png, svg)",
    task_type=TaskType.VALIDATION,
    preferred_strategies=[PromptStrategy.CONSTITUTIONAL_AI]
)
resp = engine.generate_prompt(req)
```

### 5.3 Debugging Flaky Test – ReAct + Scratchpad

```python
failing_context = {
    "recent_changes": "Parallelization enabled",
    "intermittent_stack": "ElementNotInteractableException on #submit",
}
req = PromptRequest(
    task="Investigate flaky Playwright test failing intermittently when clicking #submit after network idle",
    task_type=TaskType.DEBUGGING,
    preferred_strategies=[PromptStrategy.REACT, PromptStrategy.SCRATCHPAD]
)
resp = engine.generate_prompt(req)
```

### 5.4 Product Manager – High-Level Feature Risks (Tree of Thoughts)

```python
req = PromptRequest(
    task="Evaluate rollout risks for beta releasing new in-app notification center",
    task_type=TaskType.REASONING,
    preferred_strategies=[PromptStrategy.TREE_OF_THOUGHTS]
)
resp = engine.generate_prompt(req)
```

### 5.5 Performance Optimization – OPRO

```python
initial_prompt = "Generate optimization ideas to reduce DOM interaction time in automated tests" 
optimized = engine.optimize_prompt(initial_prompt, task_type=TaskType.OPTIMIZATION, iterations=4)
```

### 5.6 Strategy Experiment – A/B Testing

```python
ab = engine.run_ab_test(
    task="Produce test scenarios for multi-currency pricing engine",
    task_type=TaskType.GENERATION,
    strategy_a=PromptStrategy.SELF_CONSISTENCY,
    strategy_b=PromptStrategy.META_PROMPTING,
    test_name="pricing_engine_tests_v1"
)
print(ab)
```

### 5.7 Extraction + Few-Shot Examples

```python
examples = [
  {"input": "<button id='pay'>Pay Now</button>", "output": "button#pay", "reasoning": "Clickable action"},
  {"input": "<input type='email' id='e'>", "output": "input#e[type=email]", "reasoning": "User email field"}
]
req = PromptRequest(
    task="Extract actionable selectors with semantics from given modal HTML",
    task_type=TaskType.EXTRACTION,
    context={"examples": examples},
    preferred_strategies=[PromptStrategy.FEW_SHOT]
)
resp = engine.generate_prompt(req)
```

### 5.8 Regression Risk Analysis – Debate Strategy

```python
req = PromptRequest(
    task="Assess risk of refactoring auth session cache to Redis",
    task_type=TaskType.VALIDATION,
    preferred_strategies=[PromptStrategy.DEBATE]
)
resp = engine.generate_prompt(req)
```

### 5.9 Cross-Paradigm Confidence – Universal Self Consistency

```python
req = PromptRequest(
    task="Formulate a robust rollout plan for test data anonymization service",
    task_type=TaskType.REASONING,
    preferred_strategies=[PromptStrategy.UNIVERSAL_SELF_CONSISTENCY]
)
resp = engine.generate_prompt(req)
```

### 5.10 AI Prompt Architect – Meta-Prompting

```python
req = PromptRequest(
    task="Design the optimal prompt specification template for internal LLM assisted coding tool",
    task_type=TaskType.GENERATION,
    preferred_strategies=[PromptStrategy.META_PROMPTING]
)
resp = engine.generate_prompt(req)
```

---

## 6. Metrics & Performance Reporting

```python
report = engine.get_performance_report()
for strat, perf in report["strategy_performance"].items():
    print(strat, perf["usage_count"], perf["success_rate"], perf["avg_response_time"])
print(report.get("recommendations"))
```

---

## 7. Leveraging Cache

The engine caches identical `PromptRequest` signatures (task + task_type + complexity + strategy prefs). To ensure a cache hit:

- Keep `task` text identical (whitespace matters)
- Same `preferred_strategies` ordering will be normalized via sorting
- Note: `temperature`, `max_tokens`, etc. are NOT in the key (current limitation)

```python
req = PromptRequest(task="Briefly define contract testing", task_type=TaskType.ANALYTICAL)
first = engine.generate_prompt(req)
second = engine.generate_prompt(req)  # likely cache hit
print(second.metrics["cache_hit"], second.processing_time)
```

---

## 8. Extending Templates

```python
engine.template_manager.add_template(
    name="accessibility_audit",
    strategy=PromptStrategy.CHAIN_OF_TABLE,
    template="""
Audit UI component for accessibility:
Name: {component_name}
HTML:
{html_snippet}
Report issues by severity with remediation guidance.
""",
    variables=["component_name", "html_snippet"],
)
resp = engine.generate_with_template(
    template_name="accessibility_audit",
    task_type=TaskType.VALIDATION,
    component_name="Primary Nav",
    html_snippet="""<nav role='navigation'><ul><li><a>Home</a></li></ul></nav>"""
)
```

---

## 9. Adding a Custom Strategy (Lightweight Example)

You can subclass `BasePromptStrategy` externally (without editing original file) and inject it.

```python
from ui_testing_automation.prompts import BasePromptStrategy, PromptStrategy

class RiskMatrixStrategy(BasePromptStrategy):
    def __init__(self):
        super().__init__(PromptStrategy.META_COGNITIVE_FRAMEWORK)  # reuse enum slot or extend enum if refactoring
    def generate(self, task, context):
        return f"""Risk Matrix Analysis\nTask: {task}\n| Risk | Impact | Likelihood | Mitigation |\n|------|--------|------------|-----------|\n"""
    def get_complexity_score(self): return 2

engine.orchestrator.strategies[PromptStrategy.META_COGNITIVE_FRAMEWORK] = RiskMatrixStrategy()
resp = engine.generate_prompt(PromptRequest(task="Assess rollout risks for feature flags", task_type=TaskType.REASONING))
```

(For a production-safe addition, introduce a new enum value + registration path.)

---

## 10. Multi-Strategy Benchmark Harness

```python
candidates = [
  PromptStrategy.CHAIN_OF_THOUGHT,
  PromptStrategy.REACT,
  PromptStrategy.REFLEXION,
  PromptStrategy.SCRATCHPAD,
]
results = []
for strat in candidates:
    r = engine.generate_prompt(PromptRequest(
        task="Diagnose intermittent 500 errors in order service after deployment",
        task_type=TaskType.DEBUGGING,
        preferred_strategies=[strat],
        require_explanation=False,
    ), use_cache=False)
    score = r.confidence / max(r.processing_time, 0.001)
    results.append((strat.value, score))
print(sorted(results, key=lambda x: x[1], reverse=True))
```

---

## 11. Role-Based Cheat Sheet

| Role                 | Typical Task                      | Recommended Strategies                     |
| -------------------- | --------------------------------- | ------------------------------------------ |
| QA Engineer          | Generate test suites / edge cases | Self Consistency, Chain of Thought, Debate |
| SDET                 | Debug flakiness                   | ReAct, Scratchpad, Reflexion               |
| Product Manager      | Risk / scenario exploration       | Tree of Thoughts, Debate, Meta-Prompting   |
| Security Analyst     | Threat modeling                   | Constitutional AI, Debate, Chain of Table  |
| Performance Engineer | Optimization ideas                | OPRO, Evolutionary Optimization, Reflexion |
| Prompt Architect     | Designing templates               | Meta-Prompting, Meta-Cognitive Framework   |
| Data Engineer        | Extraction specs                  | Few-Shot, Chain of Thought, Scratchpad     |

---

## 12. Best Practices & Pitfalls

### Do

- Start with auto-selection; only force strategy when you have evidence
- Use A/B runs to gather empirical validation
- Wrap generation + actual LLM call (this module outputs a *prompt*, not model answer)
- Track drift: regularly inspect performance report
- Layer security-sensitive tasks with `CONSTITUTIONAL_AI`

### Avoid

- Passing huge raw HTML (trim to relevant fragments)
- Relying solely on word-count metrics (true tokens differ)
- Letting `session_history` grow unbounded (periodically prune)
- Using naive template variable names that appear multiple times unintentionally

### Improvement Opportunities (Current Limitations)

| Area             | Limitation                     | Suggested Enhancement                     |
| ---------------- | ------------------------------ | ----------------------------------------- |
| Cache key        | Ignores temperature/max_tokens | Add to `_get_cache_key` parts             |
| Confidence       | Heuristic only                 | Incorporate downstream LLM eval feedback  |
| Token Estimation | Uses `split()`                 | Integrate tokenizer (tiktoken) adapter    |
| A/B Criteria     | Length/time heuristic          | Add semantic scoring hook                 |
| Thread Safety    | Not synchronized               | Introduce locks or thread-safe structures |
| Template Fill    | Simple replace                 | Use `str.format` with escaping safeguards |

---

## 13. Feeding the Generated Prompt to an LLM

Pseudo-integration (actual `query_llm` depends on your `llm.py`):

```python
from ui_testing_automation.prompts import PromptRequest, TaskType
from ui_testing_automation.llm import query_llm  # assuming it exists

req = PromptRequest(
    task="Explain how to stabilize flaky UI tests caused by dynamic loaders",
    task_type=TaskType.ANALYTICAL,
)
prep = engine.generate_prompt(req)
raw_answer = query_llm(prompt=prep.enhanced_prompt, model="gpt-4o", temperature=0.4)
```

---

## 14. Chaining: Prompt Optimization then Generation

```python
seed = "Generate thorough security regression test ideas for upload service"
optimized_prompt = engine.optimize_prompt(seed, TaskType.OPTIMIZATION, iterations=3).enhanced_prompt
final_req = PromptRequest(task=optimized_prompt, task_type=TaskType.GENERATION)
final_resp = engine.generate_prompt(final_req)
```

---

## 15. Selecting Alternatives Programmatically

```python
req = PromptRequest(task="Classify UI defects by risk", task_type=TaskType.CLASSIFICATION)
resp = engine.generate_prompt(req)
print("Primary:", resp.strategy_used, "Alternatives:", resp.alternative_strategies)
```

(You can rerun using an alternative if desired.)

---

## 16. Quality Review of `prompts.py` (Summary)

Key strengths:

- Clear separation of strategy implementations
- Unified interface (`PromptEngine`)
- Extendable template system
- Inclusion of performance + A/B harness
- Rich domain-specific prompt structures

Notable improvement areas:

1. Caching: Key omits parameters (`temperature`, `context` nuances) → risk of stale reuse
2. Confidence Scoring: Currently heuristic; can integrate empirical post-run evaluation
3. Memory Growth: `session_history` & `cache` unbounded → add max size + eviction (LRU)
4. Thread/Async Safety: Shared dicts mutated without locks → wrap or document single-thread assumption
5. A/B Test Quality Metric: Uses length/time heuristics; consider semantic similarity, factuality, or evaluator model
6. Template Filling: Using naive `str.replace` – collisions if substring overlaps; prefer `str.format` or `Template` with safe substitution
7. Strategy Effectiveness Matrix: Missing entries for some TaskTypes (e.g., CLASSIFICATION, SUMMARIZATION) → falls back generically; add coverage
8. PerformanceTracker `success` flag always `True` in `generate_prompt` → allow caller to feed real success outcome
9. Token Estimation: `len(prompt.split())` underestimates cost; integrate tokenizer per provider
10. Logging: `basicConfig` in library code can override host app logging; recommend guarding or removing
11. Generic Strategy Fallback: Currently all 21 implemented; if more added, ensure detection remains robust
12. Complexity Score: Static per strategy; could adapt dynamically (context size, branching depth)
13. Security/Governance: No redaction of sensitive context before caching; sanitize configurable
14. Enum Extensions: Adding new strategies requires editing enum; consider plugin registry pattern for external extension
15. DRY Opportunities: Many multi-line strategy prompt templates share structural patterns → partial templates or Jinja2 could reduce duplication

Potential quick wins:

- Introduce `MAX_CACHE_ITEMS` + LRU
- Replace `.replace()` with `template.format(**kwargs)` after auditing braces
- Add `cache_hit` true flag inside cached response (currently manually set metrics only)
- Parameterize `StrategyOrchestrator.STRATEGY_EFFECTIVENESS` externally (e.g., JSON override)

---

## 17. Safe Production Integration Checklist

- [ ] Add environment-based logging level switch
- [ ] Introduce token accounting (pre-call guard)
- [ ] Add input validation / size limits
- [ ] Provide hook to evaluate LLM outputs and feed success metrics back (`record_performance`) retroactively
- [ ] Implement metrics exporter (Prometheus / JSON endpoint)
- [ ] Add unit tests per strategy (sanity + deterministic parts)

---

## 18. Strategy Selection Heuristic (Quick Mental Model)

| Goal                            | Try First                  | Why                              |
| ------------------------------- | -------------------------- | -------------------------------- |
| Stepwise logic                  | Chain of Thought           | Deterministic decomposition      |
| Broad exploration               | Tree of Thoughts           | Parallel branch evaluation       |
| Debug / Investigate             | ReAct                      | Thought-action-observation loop  |
| Confidence via diversity        | Self Consistency           | Consensus reduces hallucination  |
| Meta design / template crafting | Meta-Prompting             | Recursive improvement            |
| Ethical / policy aware          | Constitutional AI          | Built-in principle checks        |
| Optimization loops              | OPRO                       | Iterative measurable improvement |
| Creative breakthrough           | Quantum Prompting          | Parallel imaginative states      |
| Cross-discipline validation     | Universal Self Consistency | Multiple paradigms converge      |

---

## 19. Final Notes

- The module outputs *prompts*, not answers. Always separate generation from execution.
- Treat strategies as *exploration tools*; log outcomes to refine selection heuristics.
- Start simple (Chain of Thought) and introduce complex strategies only when needed.

---

## End of Guide
