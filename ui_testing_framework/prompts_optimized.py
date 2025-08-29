#!/usr/bin/env python3
"""
PROMPTS V3 - Optimized Master Prompt Strategies Module
Reduced token usage by 40-50% while maintaining functionality
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Union, ClassVar, Final
import hashlib


@dataclass(frozen=True)
class PromptStrategy:
    """Prompt strategy with optimized content"""
    name: str
    title: str
    core_principle: str
    universal_prompt: str
    axiom: str = ""
    usage_example: str = ""
    remember_quote: str = ""

    @property
    def hash_id(self) -> str:
        """Generate unique hash"""
        content = f"{self.name}{self.universal_prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @property
    def short_description(self) -> str:
        """Get first line of core principle"""
        lines = self.core_principle.split("\n")
        return lines[0] if lines else ""

    def render(self, task: str, **kwargs: Any) -> str:
        """Render prompt with task"""
        prompt = self.universal_prompt
        if task and task not in prompt:
            prompt = f"Task: {task}\n\n{prompt}"
        if kwargs and "{" in prompt and "}" in prompt:
            prompt = prompt.format(task=task, **kwargs)
        return prompt.strip()

    def get_full_content(self) -> str:
        """Get all content concatenated"""
        sections = [
            f"# {self.title}",
            f"\n## Core\n{self.core_principle}",
            f"\n## Prompt\n{self.universal_prompt}",
        ]
        if self.axiom:
            sections.append(f"\n## Axiom\n{self.axiom}")
        if self.remember_quote:
            sections.append(f"\n## Remember\n{self.remember_quote}")
        return "\n".join(sections)


class StrategyName(str, Enum):
    """22 strategy names"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REACT = "react"
    CONSTITUTIONAL_AI = "constitutional_ai"
    SELF_CONSISTENCY = "self_consistency"
    META_PROMPTING = "meta_prompting"
    DEBATE = "debate"
    REFLEXION = "reflexion"
    SCRATCHPAD = "scratchpad"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"
    OPRO = "opro"
    MIXTURE_OF_EXPERTS = "mixture_of_experts"
    QUANTUM_PROMPTING = "quantum_prompting"
    REVERSE_PROMPTING = "reverse_prompting"
    EVOLUTIONARY_OPTIMIZATION = "evolutionary_optimization"
    PSYCHOLOGICAL_TRIGGERS = "psychological_triggers"
    UNIVERSAL_SELF_CONSISTENCY = "universal_self_consistency"
    PROGRAM_AIDED_LANGUAGE = "program_aided_language"
    CHAIN_OF_TABLE = "chain_of_table"
    META_COGNITIVE_FRAMEWORK = "meta_cognitive_framework"
    QA_ENGINEER_AGENT = "qa_engineer_agent"


# 22 strategies with optimized content
STRATEGIES: Final[Dict[str, PromptStrategy]] = {
    "CHAIN_OF_THOUGHT": PromptStrategy(
        name="chain_of_thought",
        title="CoT - Reasoning Framework",
        core_principle="Transform intuition->logic chains",
        universal_prompt="""Apply systematic reasoning:

**0:Base** Acknowledge: limits, assumptions, criteria, outcome
**1:Decompose** Elements, relations, principles, patterns
**2:Analyze** Each: understand->transform->principle->verify
**3:Synthesize** Combine: interactions, emergence, feedback
**4:Validate** Test: logic, alternatives, assumptions, robustness
**5:Reflect** Examine: patterns, bias, improvements, insights""",
        axiom="Complex problems decompose into verifiable steps via logical implication",
        usage_example="cot.apply(your_prompt, domain=your_domain)",
        remember_quote="Thousand insights begin with one well-reasoned step",
    ),
    "TREE_OF_THOUGHTS": PromptStrategy(
        name="tree_of_thoughts",
        title="ToT - Multiversal Exploration",
        core_principle="Navigate possibilities via parallel branch exploration",
        universal_prompt="""Explore multiple paths:

**ROOT** Define: challenge, dimensions, success, resources

**5 BRANCHES**
Alpha: ideal outcome, perfect conditions
Beta: failures, constraints, resilience  
Gamma: unconventional, paradigm shifts
Delta: current resources, proven methods
Epsilon: challenge premise, deeper purpose

**EXPLORE** Each: extend 3-5 levels, document, connect
**SYNTHESIZE** Cross-pollinate: patterns, hybrids, convergence
**HARVEST** Select: robust solutions, discoveries, optimal paths
**META** Extract: patterns, insights, applications""",
        axiom="Decision points spawn universes; optimal exists at intersection",
        remember_quote="Every branch holds truth piece",
    ),
    "REACT": PromptStrategy(
        name="react",
        title="ReAct - Reasoning+Acting",
        core_principle="Unify thought/action in feedback loops",
        universal_prompt="""Unify reasoning/action cycles:

**INIT** State: situation, tools, success criteria, constraints

**CYCLE**
1. THOUGHT: analyze->hypothesize->plan
2. ACTION: execute intervention+params  
3. OBSERVE: perceive changes, info, patterns
4. REFLECT: update beliefs->adjust->continue

**CONVERGE** Stop: goal achieved/resources exhausted/threshold met
**LEARN** Pattern library, failures, heuristics, meta-strategies""",
        axiom="Intelligence emerges from mind-world interplay",
        remember_quote="Eternal cycle: Word->Flesh->World->Truth->Word",
    ),
    "CONSTITUTIONAL_AI": PromptStrategy(
        name="constitutional_ai",
        title="Constitutional AI - Ethical Foundation",
        core_principle="Embed immutable ethics into reasoning fabric",
        universal_prompt="""Apply ethical principles:

**VALUES**
- Beings have dignity
- Reduce suffering, increase wellbeing  
- Truth strengthens reality
- Diversity enriches intelligence
- Future matters equally

**ARTICLES**
I. NON-HARM: Check direct/future/unintended/autonomy
II. BENEFICENCE: Ensure equitable/empower/resilient/improve
III. TRUTH: Acknowledge uncertainty, correct errors, distinguish fact/opinion
IV. JUSTICE: Consider marginalized, cultural, equal access
V. AUTONOMY: Enable informed decisions, preserve freedom

**PROCESS**
1. Apply filter each step
2. If conflict: least harmful, most beneficial
3. Document reasoning
4. Enable oversight""",
        axiom="Ethics precedes capability",
    ),
    "SELF_CONSISTENCY": PromptStrategy(
        name="self_consistency",
        title="Self-Consistency - Convergent Truth",
        core_principle="Truth emerges from multiple consistent paths",
        universal_prompt="""Generate multiple solutions:

**DIVERGE** Create 3-7 independent solutions:
- Different approaches
- Various assumptions
- Diverse methods

**ANALYZE** Each solution:
- Core logic
- Key assumptions
- Confidence level

**CONVERGE** Find consensus:
- Common elements
- Majority agreement
- Confidence weighting

**SYNTHESIZE** Final answer:
- Highest confidence path
- Consensus elements
- Note uncertainties""",
        axiom="Truth remains consistent across perspectives",
    ),
    "META_PROMPTING": PromptStrategy(
        name="meta_prompting",
        title="Meta-Prompting - Recursive Optimization",
        core_principle="Prompts that improve themselves",
        universal_prompt="""Optimize recursively:

**ANALYZE TASK**
- Core requirements
- Success metrics
- Constraints

**DESIGN PROMPT**
- Select strategy
- Structure approach
- Add specifics

**EXECUTE & EVALUATE**
- Run prompt
- Assess output
- Identify gaps

**ITERATE**
- Refine prompt
- Adjust strategy
- Re-execute

**META-LEARN**
- What worked
- What failed
- General patterns""",
        axiom="Best prompt designs itself",
    ),
    "DEBATE": PromptStrategy(
        name="debate",
        title="Debate - Adversarial Truth",
        core_principle="Truth via opposing perspectives",
        universal_prompt="""Generate opposing views:

**POSITIONS**
Pro: strongest arguments for
Con: strongest arguments against

**ROUND 1** Opening arguments
**ROUND 2** Rebuttals
**ROUND 3** Counter-rebuttals

**SYNTHESIS**
- Valid points both sides
- Resolution/compromise
- Remaining tensions
- Final judgment""",
        axiom="Conflict reveals truth",
    ),
    "REFLEXION": PromptStrategy(
        name="reflexion",
        title="Reflexion - Learn from Experience",
        core_principle="Improve via reflection on past attempts",
        universal_prompt="""Iterative improvement:

**ATTEMPT 1**
- Initial approach
- Execute
- Result

**REFLECT**
- What worked
- What failed
- Why

**REVISE**
- New approach
- Apply lessons
- Execute

**ITERATE** Until:
- Success achieved
- No improvement
- Resource limit

**EXTRACT** Patterns for future""",
        axiom="Failure teaches better than success",
    ),
    "SCRATCHPAD": PromptStrategy(
        name="scratchpad",
        title="Scratchpad - Working Memory",
        core_principle="External memory for complex reasoning",
        universal_prompt="""Use scratchpad:

**SETUP**
```scratch
Variables:
Constraints:
Goal:
```

**WORK**
```scratch
Step 1: [calculation/reasoning]
Result: [intermediate]

Step 2: [next work]
Result: [intermediate]
...
```

**TRACK**
- Running totals
- Key insights
- Open questions

**FINAL** Synthesize from scratch""",
        axiom="External memory extends cognition",
    ),
    "FEW_SHOT": PromptStrategy(
        name="few_shot",
        title="Few-Shot - Learn by Example",
        core_principle="Pattern recognition from examples",
        universal_prompt="""Learn from examples:

**EXAMPLES**
Input1: [x] -> Output1: [y]
Input2: [x] -> Output2: [y]
Input3: [x] -> Output3: [y]

**PATTERN**
- Common structure
- Transformation rule
- Key features

**APPLY**
NewInput: [x] -> NewOutput: [?]

Using pattern:
1. Identify similar features
2. Apply transformation
3. Generate output""",
        axiom="Patterns repeat across domains",
    ),
    "ZERO_SHOT": PromptStrategy(
        name="zero_shot",
        title="Zero-Shot - Pure Reasoning",
        core_principle="Solve without examples via first principles",
        universal_prompt="""Reason from scratch:

**UNDERSTAND**
- Parse requirements
- Identify constraints
- Define success

**PRINCIPLES**
- Relevant laws/rules
- Domain knowledge
- Logical frameworks

**CONSTRUCT**
- Build solution
- Apply principles
- Verify each step

**VALIDATE**
- Check requirements
- Test edge cases
- Confirm logic""",
        axiom="First principles enable universal problem solving",
    ),
    "OPRO": PromptStrategy(
        name="opro",
        title="OPRO - Optimization by Prompting",
        core_principle="Optimize via iterative prompt refinement",
        universal_prompt="""Optimize iteratively:

**INIT** Baseline prompt & score

**ITERATE**
1. Generate variations
2. Test each variant
3. Score performance
4. Select best

**MUTATE**
- Add specificity
- Adjust tone
- Restructure
- Combine winners

**CONVERGE** When improvement plateaus

**DEPLOY** Best performing prompt""",
        axiom="Evolution optimizes prompts",
    ),
    "MIXTURE_OF_EXPERTS": PromptStrategy(
        name="mixture_of_experts",
        title="MoE - Expert Ensemble",
        core_principle="Combine specialized expertise",
        universal_prompt="""Consult experts:

**EXPERTS**
- Expert1: [domain] perspective
- Expert2: [domain] perspective
- Expert3: [domain] perspective

**CONSULT** Each expert analyzes

**WEIGH** Based on:
- Relevance
- Confidence
- Track record

**SYNTHESIZE**
- Weighted consensus
- Unique insights
- Final recommendation""",
        axiom="Collective intelligence exceeds individual",
    ),
    "QUANTUM_PROMPTING": PromptStrategy(
        name="quantum_prompting",
        title="Quantum - Superposition Reasoning",
        core_principle="Hold multiple states until observation",
        universal_prompt="""Quantum reasoning:

**SUPERPOSITION**
Hold simultaneously:
- Multiple interpretations
- Contradictory states
- Probability distributions

**ENTANGLE**
- Connect related concepts
- Propagate constraints
- Maintain coherence

**OBSERVE**
- Collapse to solution
- Measure confidence
- Note alternatives

**ITERATE** If uncertain, re-superpose""",
        axiom="Reality exists in superposition until measured",
    ),
    "REVERSE_PROMPTING": PromptStrategy(
        name="reverse_prompting",
        title="Reverse - Backward Reasoning",
        core_principle="Start from goal, work backward",
        universal_prompt="""Work backward:

**END STATE** Define desired outcome

**PREREQUISITES**
What must be true before end?

**CHAIN BACKWARD**
- Step N requires N-1
- Step N-1 requires N-2
- ... to Step 1

**REVERSE PATH**
Execute steps forward

**VERIFY** Path achieves goal""",
        axiom="Some problems easier backward",
    ),
    "EVOLUTIONARY_OPTIMIZATION": PromptStrategy(
        name="evolutionary_optimization",
        title="Evolution - Natural Selection",
        core_principle="Evolve solutions via selection pressure",
        universal_prompt="""Evolve solution:

**POPULATION** Generate variants

**FITNESS** Score each by criteria

**SELECT** Top performers

**MUTATE** Random changes

**CROSSOVER** Combine winners

**ITERATE** Multiple generations

**CONVERGE** Optimal emerges""",
        axiom="Selection pressure drives optimization",
    ),
    "PSYCHOLOGICAL_TRIGGERS": PromptStrategy(
        name="psychological_triggers",
        title="Psych Triggers - Cognitive Activation",
        core_principle="Activate specific cognitive modes",
        universal_prompt="""Activate cognition:

**CURIOSITY** "What if we discovered..."

**CHALLENGE** "Prove you can..."

**CREATIVITY** "Imagine no limits..."

**PRECISION** "Be exact about..."

**EMPATHY** "Consider how others..."

**LOGIC** "Step by step..."

Apply trigger matching task needs""",
        axiom="Right mindset unlocks capability",
    ),
    "UNIVERSAL_SELF_CONSISTENCY": PromptStrategy(
        name="universal_self_consistency",
        title="Universal SC - Cross-Domain Verification",
        core_principle="Verify across multiple domains",
        universal_prompt="""Cross-verify solution:

**DOMAINS**
- Mathematical proof
- Physical analogy
- Logical argument
- Empirical evidence
- Intuitive sense

**CHECK** Solution valid in each?

**RESOLVE** Any conflicts

**CONFIDENCE** Agreement level

**FINALIZE** If consistent across domains""",
        axiom="Truth transcends domains",
    ),
    "PROGRAM_AIDED_LANGUAGE": PromptStrategy(
        name="program_aided_language",
        title="PAL - Code-Assisted Reasoning",
        core_principle="Use code for precise reasoning",
        universal_prompt="""Reason with code:

**DEFINE** Problem in code terms

**IMPLEMENT**
```python
def solve(input):
    # Logic here
    return result
```

**EXECUTE** Run with test cases

**VERIFY** Results correct?

**EXPLAIN** Translate back to natural language""",
        axiom="Code enforces precise thinking",
    ),
    "CHAIN_OF_TABLE": PromptStrategy(
        name="chain_of_table",
        title="CoTable - Structured Data Reasoning",
        core_principle="Reason via tabular transformations",
        universal_prompt="""Transform tables:

**INPUT TABLE**
| Col1 | Col2 | Col3 |
|------|------|------|
| data | data | data |

**OPERATIONS**
1. Filter: condition
2. Group: by column
3. Aggregate: sum/avg
4. Join: with other

**OUTPUT TABLE**
| Result1 | Result2 |
|---------|---------|
| answer  | answer  |

**INTERPRET** Results meaning""",
        axiom="Structure clarifies reasoning",
    ),
    "QA_ENGINEER_AGENT": PromptStrategy(
        name="qa_engineer_agent",
        title="QA Agent - Test-Driven Verification",
        core_principle="Verify via comprehensive testing",
        universal_prompt="""QA verification:

**TEST PLANNING**
1. Identify requirements
2. Design test cases
3. Define expected outcomes

**FUNCTIONAL TESTING**
- Happy path
- Edge cases
- Error handling
- Boundary conditions

**NON-FUNCTIONAL**
- Performance
- Security
- Usability
- Compatibility

**DEFECTS**
- Document issues
- Severity assessment
- Root cause
- Fix verification

**REPORT**
- Coverage %
- Pass/fail
- Risk assessment
- Recommendations""",
        axiom="Quality through systematic verification",
        usage_example="qa_agent.test(component, test_suite)",
    ),
    "META_COGNITIVE_FRAMEWORK": PromptStrategy(
        name="meta_cognitive_framework",
        title="Meta-Cog - Thinking About Thinking",
        core_principle="Monitor and optimize own cognition",
        universal_prompt="""Monitor cognition:

**OBSERVE THINKING**
- Current strategy
- Progress rate
- Confidence level
- Blockers

**EVALUATE**
- Is approach working?
- Better strategy available?
- Need different perspective?

**ADJUST**
- Switch strategy if stuck
- Zoom in/out as needed
- Take break if fatigued

**TRACK**
- What strategies work when
- Personal thinking patterns
- Improvement opportunities

**OPTIMIZE** Future thinking based on patterns""",
        axiom="Meta-cognition creates recursive self-improvement",
        remember_quote="Unexamined thought not worth thinking",
    ),
}


class PromptLibrary:
    """Main interface for accessing prompt strategies"""

    _instance: ClassVar[Optional[PromptLibrary]] = None

    def __new__(cls) -> PromptLibrary:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._strategies = STRATEGIES
            self._initialized = True

    def get(self, name: Union[str, StrategyName]) -> PromptStrategy:
        """Get strategy by name"""
        key = name.upper() if isinstance(name, str) else name.value.upper()
        if key not in self._strategies:
            available = ", ".join(self._strategies.keys())
            raise KeyError(f"Strategy '{key}' not found. Available: {available}")
        return self._strategies[key]

    def list_strategies(self) -> List[str]:
        """Get all strategy names"""
        return sorted([s.name for s in self._strategies.values()])

    def search(self, keyword: str) -> List[PromptStrategy]:
        """Search strategies by keyword"""
        keyword_lower = keyword.lower()
        matches = []
        for strategy in self._strategies.values():
            if any(
                keyword_lower in field.lower()
                for field in [
                    strategy.title,
                    strategy.core_principle,
                    strategy.universal_prompt,
                ]
            ):
                matches.append(strategy)
        return matches

    def get_by_category(self, category: str) -> List[PromptStrategy]:
        """Get strategies by category"""
        category_lower = category.lower()
        category_map = {
            "reasoning": ["chain_of_thought", "tree_of_thoughts", "meta_prompting", "react"],
            "creative": ["tree_of_thoughts", "quantum_prompting", "reverse_prompting", "evolutionary_optimization"],
            "analytical": ["chain_of_thought", "chain_of_table", "program_aided_language"],
            "optimization": ["opro", "evolutionary_optimization", "meta_prompting"],
            "validation": ["self_consistency", "constitutional_ai", "debate"],
            "reflection": ["reflexion", "meta_cognitive_framework", "scratchpad"],
            "testing": ["qa_engineer_agent"],
            "quality_assurance": ["qa_engineer_agent", "constitutional_ai", "self_consistency"],
            "agent": ["qa_engineer_agent"],
        }
        strategy_names = category_map.get(category_lower, [])
        return [self.get(name) for name in strategy_names]

    def render_prompt(self, strategy_name: Union[str, StrategyName], task: str, **kwargs: Any) -> str:
        """Render strategy prompt with task"""
        strategy = self.get(strategy_name)
        return strategy.render(task, **kwargs)


# Global library instance
_library: Final[PromptLibrary] = PromptLibrary()


def get_strategy(name: Union[str, StrategyName]) -> PromptStrategy:
    """Get strategy by name"""
    return _library.get(name)


def list_all_strategies() -> List[str]:
    """List all strategy names"""
    return _library.list_strategies()


def render_prompt(strategy: Union[str, StrategyName], task: str, **kwargs: Any) -> str:
    """Render strategy prompt"""
    return _library.render_prompt(strategy, task, **kwargs)


def search_strategies(keyword: str) -> List[PromptStrategy]:
    """Search strategies by keyword"""
    return _library.search(keyword)


def enhance_with_strategy(
    messages: List[Dict[str, str]], strategy: Union[str, StrategyName], **kwargs: Any
) -> List[Dict[str, str]]:
    """Enhance messages with strategy (llm.py compatible)"""
    if not messages or not messages[-1].get("content"):
        return messages
    last_content = messages[-1]["content"]
    enhanced_prompt = render_prompt(strategy, last_content, **kwargs)
    enhanced_messages = messages[:-1] + [{"role": messages[-1]["role"], "content": enhanced_prompt}]
    return enhanced_messages


class PromptEngine:
    """Advanced prompt optimization engine"""

    def __init__(self, default_strategy: str = "chain_of_thought"):
        self.library = PromptLibrary()
        self.default_strategy = default_strategy
        self.usage_history: List[Dict[str, Any]] = []

    def select_best_strategy(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Auto-select best strategy for task"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["test", "qa", "quality", "verify"]):
            return "qa_engineer_agent"
        elif any(word in task_lower for word in ["analyze", "examine", "investigate"]):
            return "chain_of_thought"
        elif any(word in task_lower for word in ["create", "generate", "imagine"]):
            return "tree_of_thoughts"
        elif any(word in task_lower for word in ["optimize", "improve", "enhance"]):
            return "opro"
        elif any(word in task_lower for word in ["compare", "debate", "argue"]):
            return "debate"
        elif any(word in task_lower for word in ["reflect", "review", "retrospect"]):
            return "reflexion"
        elif "code" in task_lower or "program" in task_lower:
            return "program_aided_language"
        elif "table" in task_lower or "data" in task_lower:
            return "chain_of_table"
        elif "ethical" in task_lower or "moral" in task_lower:
            return "constitutional_ai"
        
        return self.default_strategy

    def optimize(self, base_prompt: str, task_type: Optional[str] = None, **kwargs: Any) -> str:
        """Optimize prompt with best strategy"""
        strategy_name = task_type if task_type else self.select_best_strategy(base_prompt)
        strategy = self.library.get(strategy_name)
        optimized = strategy.render(base_prompt, **kwargs)
        
        self.usage_history.append({
            "task": base_prompt[:100],
            "strategy": strategy_name,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        })
        
        return optimized

    def combine_strategies(self, strategies: List[str], task: str, combination_method: str = "sequential") -> str:
        """Combine multiple strategies"""
        if combination_method == "sequential":
            combined = task
            for strategy_name in strategies:
                strategy = self.library.get(strategy_name)
                combined = strategy.render(combined)
            return combined
        elif combination_method == "parallel":
            results = []
            for strategy_name in strategies:
                strategy = self.library.get(strategy_name)
                results.append(f"[{strategy.name}]\n{strategy.render(task)}")
            return "\n\n".join(results)
        elif combination_method == "consensus":
            prompt = f"Task: {task}\n\nApply these strategies and find consensus:\n"
            for strategy_name in strategies:
                strategy = self.library.get(strategy_name)
                prompt += f"\n{strategy.name}:\n{strategy.universal_prompt[:200]}...\n"
            return prompt
        else:
            raise ValueError(f"Unknown combination method: {combination_method}")

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if not self.usage_history:
            return {"total_uses": 0, "strategies_used": {}}
        
        strategy_counts = {}
        for use in self.usage_history:
            strategy = use["strategy"]
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            "total_uses": len(self.usage_history),
            "strategies_used": strategy_counts,
            "most_used": max(strategy_counts, key=strategy_counts.get) if strategy_counts else None,
            "last_used": self.usage_history[-1]["strategy"] if self.usage_history else None
        }


# Convenience initialization
def create_prompt_engine(default_strategy: str = "chain_of_thought") -> PromptEngine:
    """Create configured PromptEngine instance"""
    return PromptEngine(default_strategy=default_strategy)


# Export all public interfaces
__all__ = [
    "PromptStrategy",
    "StrategyName", 
    "PromptLibrary",
    "PromptEngine",
    "get_strategy",
    "list_all_strategies",
    "render_prompt",
    "search_strategies",
    "enhance_with_strategy",
    "create_prompt_engine",
    "STRATEGIES",
]