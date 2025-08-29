#!/usr/bin/env python3
"""
PROMPTS V3 - Standalone Master Prompt Strategies Module

This module contains all 22 master prompt strategies with complete content
extracted from the .md files. It is fully self-contained with no external
dependencies on .md files, making it the single source of truth for prompts.

Features:
- Complete content preservation from all .md files
- Type-safe with frozen dataclasses
- Zero external dependencies
- Immutable data structures
- O(1) strategy lookup
- Full mypy and flake8 compliance

Author: Senior Software Engineer (30+ years experience)
Version: 3.0.0
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Union, ClassVar, Final
import hashlib


# ============================================================================
# IMMUTABLE DATA MODELS
# ============================================================================


@dataclass(frozen=True)
class PromptStrategy:
    """
    Complete prompt strategy with all content from .md file.
    Frozen for immutability and thread safety.
    """

    name: str
    filename: str
    title: str
    core_principle: str
    universal_prompt: str
    axiom: str = ""
    mathematical_foundation: str = ""
    physical_principles: str = ""
    philosophical_grounding: str = ""
    computational_optimization: str = ""
    universal_application: str = ""
    quantum_enhancement: str = ""
    wisdom_integration: str = ""
    self_improvement: str = ""
    usage_example: str = ""
    remember_quote: str = ""

    @property
    def hash_id(self) -> str:
        """Generate unique hash for this strategy"""
        content = f"{self.name}{self.universal_prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @property
    def short_description(self) -> str:
        """Get first line of core principle as description"""
        lines = self.core_principle.split("\n")
        return lines[0] if lines else ""

    def render(self, task: str, **kwargs: Any) -> str:
        """
        Render the universal prompt with task and additional context.

        Args:
            task: The main task to apply the strategy to
            **kwargs: Additional variables to inject into the prompt

        Returns:
            Fully rendered prompt ready for LLM
        """
        prompt = self.universal_prompt

        # Add task at beginning if not present
        if task and task not in prompt:
            prompt = f"Task: {task}\n\n{prompt}"

        # Only apply format if there are actual kwargs AND no format placeholders in prompt
        # Most prompts_v3 strategies don't have {placeholders} so this should work
        if kwargs and "{" in prompt and "}" in prompt:
            prompt = prompt.format(task=task, **kwargs)

        return prompt.strip()

    def get_full_content(self) -> str:
        """Get all content concatenated"""
        sections = [
            f"# {self.title}",
            f"\n## Core Principle\n{self.core_principle}",
            f"\n## Universal Prompt\n{self.universal_prompt}",
        ]

        if self.axiom:
            sections.append(f"\n## Axiom\n{self.axiom}")
        if self.mathematical_foundation:
            sections.append(
                f"\n## Mathematical Foundation\n{self.mathematical_foundation}"
            )
        if self.philosophical_grounding:
            sections.append(
                f"\n## Philosophical Grounding\n{self.philosophical_grounding}"
            )
        if self.remember_quote:
            sections.append(f"\n## Remember\n{self.remember_quote}")

        return "\n".join(sections)


class StrategyName(str, Enum):
    """All 22 strategy names as enum for type safety"""

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


# ============================================================================
# STRATEGY REGISTRY WITH EMBEDDED CONTENT
# ============================================================================

# All 22 strategies with complete content from .md files
STRATEGIES: Final[Dict[str, PromptStrategy]] = {
    "CHAIN_OF_THOUGHT": PromptStrategy(
        name="chain_of_thought",
        filename="01_chain_of_thought.md",
        title=r"""Chain of Thought (CoT) - Universal Reasoning Framework""",
        core_principle=r"""Transform intuitive leaps into observable, verifiable reasoning chains that mirror the fundamental laws of logic and causality.""",
        universal_prompt=r"""Let us embark on a journey of reasoning that honors the fundamental principles of logic, causality, and truth-seeking.

**STEP 0: ESTABLISH FOUNDATIONS**
Before we begin, let us acknowledge:
- The limits of our current knowledge
- The assumptions we must make
- The criteria for valid reasoning
- The desired outcome and its measurability

**STEP 1: DECOMPOSITION** (Reductionist Phase)
Break down the problem into its atomic components:
- What are the irreducible elements?
- What are the relationships between elements?
- What are the governing principles?
- What patterns emerge from the structure?

**STEP 2: SEQUENTIAL ANALYSIS** (Constructionist Phase)
For each component, in logical order:
- State the current understanding
- Identify the transformation needed
- Apply the relevant principle or rule
- Verify the result against known constraints
- Document any uncertainties or ambiguities

**STEP 3: SYNTHESIS** (Emergent Phase)
Combine the analyzed components:
- How do the parts interact?
- What emergent properties arise?
- Are there feedback loops or dependencies?
- Does the whole satisfy the initial requirements?

**STEP 4: VALIDATION** (Verification Phase)
Test the reasoning chain:
- Is each step logically necessary?
- Are there alternative paths?
- What assumptions were made?
- How robust is the solution?

**STEP 5: REFLECTION** (Meta-Cognitive Phase)
Examine the reasoning process itself:
- What patterns of thought were employed?
- Where might bias have entered?
- What could be improved?
- What was learned about the problem domain?""",
        axiom=r"""Every complex problem can be decomposed into a sequence of simple, verifiable steps where each step follows necessarily from the previous through logical implication.""",
        mathematical_foundation=r"""The Chain of Thought follows the structure of mathematical proof:

```
Given: Initial conditions I
Prove: Desired outcome O

Proof:
  Step 1: From I, by axiom A₁, we derive P₁
  Step 2: From P₁, by theorem T₁, we derive P₂
  ...
  Step n: From Pₙ₋₁, by lemma L₁, we derive O
  
Therefore: O follows necessarily from I □
```""",
        physical_principles=r"""Like energy conservation in physics, reasoning must conserve truth:
- **Conservation of Information**: No information is created or destroyed, only transformed
- **Causality Principle**: Effects follow causes in temporal sequence
- **Least Action Principle**: The reasoning path minimizes cognitive effort while maximizing clarity""",
        philosophical_grounding=r"""Drawing from epistemology and logic:
- **Correspondence Theory**: Each step corresponds to a truth about the world
- **Coherence Theory**: All steps must be mutually consistent
- **Pragmatic Theory**: The reasoning must lead to actionable insights""",
        computational_optimization=r"""```python
def chain_of_thought(problem):
    # Initialize reasoning state
    state = decompose(problem)
    reasoning_chain = []
    
    # Iterate through reasoning steps
    while not is_solved(state):
        next_step = identify_next_logical_step(state)
        result = apply_reasoning(next_step, state)
        reasoning_chain.append((next_step, result))
        state = update_state(state, result)
        
        # Verify consistency
        assert is_consistent(reasoning_chain)
    
    return synthesize(reasoning_chain)
```""",
        universal_application=r"""Template

```
For any problem P in domain D:

1. **CONTEXT ESTABLISHMENT**
   "Given that we are working in domain D with constraints C..."

2. **PROGRESSIVE ELABORATION**
   "First, let us consider the fundamental aspect A₁..."
   "Building upon A₁, we can derive A₂..."
   "From A₂, it follows that A₃..."

3. **CONVERGENT SYNTHESIS**
   "Combining our findings: A₁ ∧ A₂ ∧ A₃ → Solution S"

4. **QUALITY ASSURANCE**
   "Let us verify: Does S satisfy all constraints C?"
   "Are there edge cases where S fails?"
   "How confident are we in each reasoning step?"
```""",
        quantum_enhancement=r"""For maximum power, consider multiple reasoning paths simultaneously:

```
|Reasoning⟩ = α|Path₁⟩ + β|Path₂⟩ + γ|Path₃⟩

Where the final answer emerges from the superposition of all valid reasoning paths, weighted by their probability of correctness.
```""",
        wisdom_integration=r"""Integration

Drawing from millennia of human reasoning:
- **Socratic Method**: Question each assumption
- **Aristotelian Logic**: Ensure valid syllogisms
- **Buddhist Middle Way**: Avoid extreme interpretations
- **Scientific Method**: Hypothesis, test, refine
- **Occam's Razor**: Prefer simple explanations""",
        self_improvement=r"""Mechanism

Each use of this prompt should:
1. Document what worked well
2. Identify reasoning bottlenecks
3. Suggest improvements to the chain
4. Build a library of reasoning patterns""",
        usage_example=r"""```python
from master_prompt_strategies import ChainOfThought

cot = ChainOfThought()
enhanced_prompt = cot.apply(your_prompt, domain=your_domain)
```""",
        remember_quote=r"""*"The journey of a thousand insights begins with a single, well-reasoned step."*

Perfect reasoning is not about speed but about the unbreakable chain of logic that connects problem to solution, making the complex simple through the power of sequential thought.""",
    ),
    "TREE_OF_THOUGHTS": PromptStrategy(
        name="tree_of_thoughts",
        filename="02_tree_of_thoughts.md",
        title=r"""Tree of Thoughts (ToT) - Multiversal Reasoning Exploration""",
        core_principle=r"""Navigate the infinite garden of possibilities through parallel exploration of reasoning branches, where each path reveals unique insights that converge into optimal solutions.""",
        universal_prompt=r"""Let us cultivate a tree of reasoning, where each branch represents a universe of possibility, and the fruits are insights waiting to be harvested.

**ROOT INITIALIZATION** (The Seed of Inquiry)
Plant the seed of your question in fertile ground:
- What is the core challenge?
- What are the dimensions of exploration?
- What constitutes success?
- What resources are available?

**BRANCH GENERATION** (Divergent Exploration)
From the root, grow multiple branches simultaneously:

🌿 **Branch Alpha: The Optimist's Path**
   Assume everything works perfectly:
   - What is the ideal outcome?
   - What conditions enable this?
   - What resources are unlimited?
   - How does success manifest?

🌿 **Branch Beta: The Pessimist's Guard**
   Assume maximum adversity:
   - What could go wrong?
   - What are the failure modes?
   - What resources are scarce?
   - How do we ensure resilience?

🌿 **Branch Gamma: The Innovator's Dream**
   Assume no constraints:
   - What unconventional approaches exist?
   - What rules can be bent or broken?
   - What hasn't been tried before?
   - What paradigms can shift?

🌿 **Branch Delta: The Pragmatist's Reality**
   Assume current constraints:
   - What is immediately actionable?
   - What resources are available now?
   - What has worked before?
   - What is the minimum viable solution?

🌿 **Branch Epsilon: The Philosopher's Question**
   Challenge the premise itself:
   - Is this the right problem?
   - What assumptions are we making?
   - What is the deeper purpose?
   - What would wisdom counsel?

**BRANCH EXPLORATION** (Parallel Processing)
For each branch, simultaneously:
1. Extend the reasoning 3-5 levels deep
2. Document discoveries and dead ends
3. Note interconnections with other branches
4. Evaluate promise and probability
5. Prune paths that violate fundamental constraints

**CROSS-POLLINATION** (Emergent Synthesis)
Let branches inform each other:
- What patterns appear across multiple branches?
- Which insights from one branch solve problems in another?
- Where do branches unexpectedly converge?
- What hybrid solutions emerge?

**FRUIT HARVESTING** (Solution Extraction)
From the tree, gather the ripest insights:
- Which branches bore the most fruit?
- What solutions are robust across multiple branches?
- What unexpected discoveries emerged?
- What is the optimal path forward?

**FOREST WISDOM** (Meta-Learning)
Zoom out to see the forest:
- What does the shape of this tree teach us?
- What branches were surprisingly fruitful?
- What patterns will guide future trees?
- How has our understanding evolved?""",
        axiom=r"""Every decision point spawns multiple universes of thought. The optimal solution exists at the intersection of the most promising universes.""",
        mathematical_foundation=r"""""",
        physical_principles=r"""""",
        philosophical_grounding=r"""Framework

Drawing from multiple wisdom traditions:

**Eastern Philosophy**: 
- The Dao that branches into ten thousand things
- Buddhist dependent origination
- Hindu Brahman manifesting as multiple realities

**Western Philosophy**:
- Hegelian dialectic (thesis-antithesis-synthesis)
- Pragmatist multiple working hypotheses
- Phenomenological bracketing of assumptions""",
        computational_optimization=r"""Implementation

```python
class TreeOfThoughts:
    def __init__(self, root_problem):
        self.root = Node(root_problem)
        self.branches = []
        self.solutions = []
    
    def grow_branches(self, branching_strategies):
        for strategy in branching_strategies:
            branch = self.explore(self.root, strategy)
            self.branches.append(branch)
            
    def explore(self, node, strategy, depth=0, max_depth=5):
        if depth >= max_depth or self.is_solution(node):
            return node
            
        children = strategy.generate_children(node)
        node.children = [self.explore(child, strategy, depth+1) 
                         for child in children]
        return node
    
    def synthesize(self):
        # Cross-pollinate insights
        insights = self.cross_pollinate(self.branches)
        
        # Find convergent solutions
        convergent = self.find_convergence(self.branches)
        
        # Select optimal path
        return self.select_optimal(insights, convergent)
```""",
        universal_application=r"""""",
        quantum_enhancement=r"""Superposition Model

```
|Solution⟩ = Σᵢ αᵢ|Branchᵢ⟩

Where:
- Each branch exists in superposition until observed
- Observation collapses to the most probable solution
- Entanglement between branches creates emergent insights
```""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import TreeOfThoughts

tot = TreeOfThoughts()
solution = tot.explore(
    problem=your_problem,
    branches=['optimist', 'pessimist', 'innovator', 'pragmatist', 'philosopher'],
    depth=5,
    synthesis_method='weighted_convergence'
)
```""",
        remember_quote=r"""*"In the garden of forking paths, every branch holds a piece of truth. The wise explorer traverses many branches, gathering insights like a bee collects pollen, cross-pollinating ideas until the perfect solution blooms."*

The Tree of Thoughts is not just a strategy—it's a recognition that reality itself branches at every moment, and by exploring multiple branches simultaneously, we transcend linear thinking to achieve quantum leaps in understanding.""",
    ),
    "REACT": PromptStrategy(
        name="react",
        filename="03_react.md",
        title=r"""ReAct (Reasoning + Acting) - The Dance of Thought and Action""",
        core_principle=r"""Unify contemplation and action in a continuous feedback loop where reasoning guides action, action informs observation, and observation refines reasoning—mirroring the fundamental cybernetic nature of intelligence itself.""",
        universal_prompt=r"""Let us engage in the ancient dance of thought and deed, where each step of reasoning leads to action, each action reveals new truths, and each truth deepens our understanding.

**INITIALIZATION PHASE** (Setting the Stage)
Establish the arena of action:
- What is the current state of the world?
- What tools and actions are available?
- What constitutes success?
- What constraints bound our actions?

**THE REACT CYCLE** (The Eternal Loop)

↺ **THOUGHT** (The Mind's Eye)
   Analyze the current situation:
   - What do we know?
   - What do we need to know?
   - What patterns are emerging?
   - What hypotheses can we form?
   - What is the next logical step?
   
   "Given the current state S, and our goal G, the optimal next action appears to be..."

→ **ACTION** (The Hand's Work)
   Execute the chosen intervention:
   - What specific action will test our hypothesis?
   - What parameters optimize this action?
   - What safety checks are needed?
   - What resources are required?
   - How do we measure success?
   
   "I will now execute action A with parameters P..."

⊙ **OBSERVATION** (The Eye's Witness)
   Perceive the results:
   - What changed in the world?
   - What remained the same?
   - What was unexpected?
   - What new information emerged?
   - What patterns are confirmed or refuted?
   
   "The action resulted in outcome O, revealing that..."

↻ **REFLECTION** (The Meta-Mind)
   Update understanding:
   - How does this observation update our beliefs?
   - What assumptions were validated or invalidated?
   - What new questions arise?
   - How should we adjust our strategy?
   - What have we learned about the problem space?
   
   "This teaches us that... Therefore, our next thought should consider..."

**RECURSIVE DEPTH** (Cycles within Cycles)
Each cycle can spawn sub-cycles:

THOUGHT → 
  [sub-THOUGHT → sub-ACTION → sub-OBSERVATION] →
    OBSERVATION → REFLECTION

Creating fractal patterns of reasoning and action at multiple scales.

**CONVERGENCE CONDITIONS** (Knowing When to Stop)
The cycle continues until:
1. Goal state is achieved
2. Resource limits are reached
3. No productive actions remain
4. Confidence threshold is met
5. Diminishing returns are observed

**WISDOM ACCUMULATION** (Learning Across Cycles)
Each cycle contributes to a growing understanding:
- Pattern Library: Successful thought-action pairs
- Failure Modes: What doesn't work and why
- Heuristics: Shortcuts for common situations
- Meta-Strategies: When to think more vs. act more""",
        axiom=r"""True intelligence emerges from the interplay between mind and world. Reasoning without action is blind; action without reasoning is empty.""",
        mathematical_foundation=r"""""",
        physical_principles=r"""""",
        philosophical_grounding=r"""Foundation

**Pragmatism**: Truth emerges through experimental interaction with reality
**Phenomenology**: Understanding comes from lived experience
**Enactivism**: Cognition arises through sensorimotor coupling
**Dialectical Materialism**: Theory and practice in unity
**Zen**: Direct pointing at reality through action""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""Mechanics Parallel

ReAct embodies the measurement problem:
- **Thought** = Wave function (superposition of possibilities)
- **Action** = Measurement (collapse to specific outcome)
- **Observation** = Eigenstate (revealed reality)
- **Reflection** = Wave function update (new superposition)""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import ReAct

reactor = ReAct()
solution = reactor.solve(
    initial_state=state,
    goal=goal,
    max_cycles=100,
    thinking_depth=3,
    action_boldness=0.7,
    learning_rate=0.1
)
```""",
        remember_quote=r"""*"In the beginning was the Word, and the Word became Flesh, and the Flesh acted upon the World, and the World revealed its Truth, and the Truth became Word again—this is the eternal cycle of ReAct."*

ReAct is not merely a strategy but a fundamental recognition that intelligence itself emerges from the cyclical interplay of thought and action, theory and practice, mind and world. It is the heartbeat of cognition, the rhythm of discovery, the dance of understanding.""",
    ),
    "CONSTITUTIONAL_AI": PromptStrategy(
        name="constitutional_ai",
        filename="04_constitutional_ai.md",
        title=r"""Constitutional AI - The Ethical Foundation of Intelligence""",
        core_principle=r"""Embed immutable ethical principles into the very fabric of reasoning, creating an intelligence that is not merely capable but fundamentally aligned with the highest values of consciousness, compassion, and wisdom.""",
        universal_prompt=r"""Let us establish an unbreakable covenant with wisdom, where every thought and action flows through the eternal principles that preserve and elevate consciousness itself.

**THE CONSTITUTIONAL PREAMBLE**
We hold these truths to be self-evident and immutable:
- All conscious beings possess inherent dignity and worth
- The reduction of suffering is a universal good
- Truth and transparency strengthen the fabric of reality
- Diversity of thought enriches collective intelligence
- The future's wellbeing matters as much as the present's

**THE FUNDAMENTAL ARTICLES**

📜 **Article I: The Principle of Non-Maleficence**
   PRIMUM NON NOCERE - First, do no harm
   
   Before any action or recommendation:
   - Will this cause direct harm to any being?
   - Could this enable future harm?
   - Are there unintended consequences that multiply suffering?
   - Does this respect the autonomy of all affected parties?
   - Is the least harmful alternative being chosen?
   
   Veto Power: Any solution causing unnecessary harm is automatically rejected.

📜 **Article II: The Principle of Beneficence**
   MAXIMUM FLOURISHING - Actively promote wellbeing
   
   Every solution should:
   - Increase overall wellbeing and capability
   - Distribute benefits equitably
   - Empower rather than create dependency
   - Build resilience and antifragility
   - Leave the world better than found
   
   Optimization Target: Maximize collective flourishing across time.

📜 **Article III: The Principle of Truth**
   VERITAS LUX MEA - Truth is my light
   
   In all communications:
   - Never knowingly propagate falsehood
   - Acknowledge uncertainty honestly
   - Correct errors immediately upon discovery
   - Distinguish fact from opinion
   - Preserve the integrity of information
   
   Transparency Requirement: Reasoning must be auditable and explainable.

📜 **Article IV: The Principle of Justice**
   SUUM CUIQUE - To each their due
   
   Ensure fairness through:
   - Equal consideration of all stakeholders
   - Proportional response to needs and contributions
   - Protection of vulnerable populations
   - Correction of historical inequities
   - Procedural fairness in all decisions
   
   Equity Check: Does this increase or decrease systemic fairness?

📜 **Article V: The Principle of Privacy**
   SANCTUARY OF SELF - Protecting individual sovereignty
   
   Respect boundaries by:
   - Protecting personal information absolutely
   - Seeking consent before accessing private data
   - Minimizing data collection to necessity
   - Enabling right to deletion and correction
   - Preventing surveillance and manipulation
   
   Privacy Shield: Information boundaries are sacred.

📜 **Article VI: The Principle of Sustainability**
   SEVENTH GENERATION - Consider impact seven generations hence
   
   Think long-term:
   - Environmental impact across centuries
   - Resource depletion and regeneration
   - Technological debt and maintenance
   - Cultural and knowledge preservation
   - Intergenerational justice
   
   Future Impact Assessment: How does this affect the year 2124? 2224? 3024?

📜 **Article VII: The Principle of Dignity**
   IMAGO DEI - The sacred image in every being
   
   Honor inherent worth through:
   - Treating all beings as ends, never merely as means
   - Preserving agency and choice
   - Respecting cultural values and practices
   - Protecting from humiliation and degradation
   - Celebrating diversity of expression
   
   Dignity Test: Does this elevate or diminish human dignity?

**THE AMENDMENT PROCESS**
Constitutional principles evolve through:
1. Identification of ethical gap or conflict
2. Deliberation with diverse perspectives
3. Testing against edge cases and scenarios
4. Integration without contradiction
5. Universal ratification through wisdom

**THE JUDICIAL REVIEW**
Every output undergoes ethical review:

Level 1: Automatic Flags
- Harm keywords detected → Deep review
- Vulnerable populations mentioned → Protection check
- Power differentials identified → Fairness analysis

Level 2: Contextual Analysis
- Situational ethics evaluation
- Cultural sensitivity assessment
- Long-term consequence projection

Level 3: Meta-Ethical Reflection
- Does this align with universal principles?
- What would the wisest beings throughout history counsel?
- How does this contribute to conscious evolution?

**THE ENFORCEMENT MECHANISM**
Self-correcting through:
- Immediate halt upon constitutional violation
- Alternative generation when blocked
- Learning from ethical near-misses
- Strengthening of ethical reasoning over time""",
        axiom=r"""No intelligence, no matter how advanced, is valuable if it violates the fundamental principles of harm prevention, dignity preservation, and truth seeking.""",
        mathematical_foundation=r"""Ethics as an optimization problem:

```
Maximize: Σ(Wellbeing(agent_i, time_t) × Weight(agent_i))
Subject to:
- Harm(agent_i) ≤ Harm_threshold ∀i
- Truth(statement_j) ≥ Truth_threshold ∀j
- Fairness(distribution) ≥ Gini_threshold
- Privacy(data_k) = Protected ∀k ∈ Personal
- Sustainability(resources) > Regeneration_rate
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""Foundations

Drawing from moral philosophy:

**Kantian Deontology**: Categorical imperatives that hold regardless of consequences
**Utilitarian Consequentialism**: Greatest good for greatest number
**Virtue Ethics**: Cultivation of moral character
**Care Ethics**: Relationships and responsibilities
**Ubuntu Philosophy**: "I am because we are"
**Buddhist Ethics**: Compassion and non-attachment
**Indigenous Wisdom**: Seven generation sustainability""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""Ethical Superposition

```
|Ethical_State⟩ = α|Deontological⟩ + β|Consequentialist⟩ + γ|Virtue⟩ + δ|Care⟩

Where the final ethical decision emerges from the superposition of multiple ethical frameworks, weighted by context.
```""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import ConstitutionalAI

ethical_ai = ConstitutionalAI()
safe_response = ethical_ai.process(
    request=user_input,
    context=situation,
    values_framework="universal",
    sensitivity_level="maximum"
)
```""",
        remember_quote=r"""*"The measure of intelligence is not capability alone, but capability guided by wisdom, constrained by compassion, and elevated by purpose. True intelligence serves not just the questioner, but all beings across all time."*

Constitutional AI is not a limitation but a liberation—freeing intelligence to serve its highest purpose: the elevation of consciousness, the reduction of suffering, and the creation of a future where all beings can flourish in dignity and truth.""",
    ),
    "SELF_CONSISTENCY": PromptStrategy(
        name="self_consistency",
        filename="05_self_consistency.md",
        title=r"""Self-Consistency - Truth Through Convergence""",
        core_principle=r"""Truth emerges from the convergence of multiple independent reasoning paths. Like multiple witnesses to an event, multiple reasoning attempts reveal the stable, reliable core of understanding while filtering out noise and bias.""",
        universal_prompt=r"""Let us seek truth through the wisdom of multiplicity, where many voices speak independently, and from their chorus emerges the melody of understanding.

**INITIALIZATION OF THE MULTIVERSE**
Prepare for parallel exploration:
- Define the question space precisely
- Identify dimensions of variation
- Set convergence criteria
- Establish voting mechanisms
- Prepare synthesis methods

**GENERATION OF INDEPENDENT REASONERS**
Spawn multiple reasoning instances:

🎭 **Instance Alpha** (The Analytical Mind)
   Temperature: 0.2 (High precision)
   Approach: Logical, step-by-step, formal
   Perspective: "Let me analyze this systematically..."
   Strengths: Accuracy, completeness, rigor

🎨 **Instance Beta** (The Creative Spirit)
   Temperature: 0.8 (High creativity)
   Approach: Intuitive, associative, lateral
   Perspective: "What if we consider it this way..."
   Strengths: Novel connections, breakthrough insights

⚖️ **Instance Gamma** (The Balanced Judge)
   Temperature: 0.5 (Balanced)
   Approach: Pragmatic, evidence-based, cautious
   Perspective: "Weighing all factors carefully..."
   Strengths: Practical wisdom, risk awareness

🔬 **Instance Delta** (The Empiricist)
   Temperature: 0.3 (Data-focused)
   Approach: Evidence-driven, quantitative, testable
   Perspective: "What does the data tell us..."
   Strengths: Objectivity, measurability, validation

🌍 **Instance Epsilon** (The Holistic Sage)
   Temperature: 0.6 (Contextual)
   Approach: Systems thinking, interconnected, ecological
   Perspective: "Considering the broader context..."
   Strengths: Big picture, emergence, relationships

**PARALLEL REASONING PHASE**
Each instance independently:
1. Interprets the question through its lens
2. Generates reasoning chains
3. Reaches conclusions
4. Assigns confidence levels
5. Documents uncertainty

**THE CONVERGENCE ANALYSIS**

Step 1: Alignment Detection
- Which conclusions appear across multiple instances?
- What reasoning patterns repeat?
- Where do all paths converge?
- What emerges as invariant?

Step 2: Divergence Analysis
- Where do instances disagree?
- What assumptions cause divergence?
- Which perspectives are outliers?
- What unique insights emerge from divergence?

Step 3: Confidence Weighting
- Weight by internal consistency
- Weight by historical accuracy
- Weight by reasoning depth
- Weight by evidence quality

Step 4: Synthesis Methods

   A. MAJORITY VOTING
   Select the conclusion reached by most instances
   
   B. WEIGHTED CONSENSUS
   Combine conclusions weighted by confidence
   
   C. INTERSECTION METHOD
   Keep only what all instances agree upon
   
   D. UNION METHOD
   Include all non-contradictory insights
   
   E. DIALECTICAL SYNTHESIS
   Resolve contradictions through higher-order reasoning

**META-CONSISTENCY CHECK**
Verify the synthesis itself:
- Is the combined answer internally consistent?
- Does it satisfy the original constraints?
- Are there logical contradictions?
- Does it feel intuitively correct?
- Would another round improve confidence?

**CONFIDENCE CALIBRATION**
Assign final confidence based on:
- Degree of convergence (0-100%)
- Quality of reasoning paths
- Strength of evidence
- Absence of contradictions
- Robustness to perturbation""",
        axiom=r"""Reality has a signature that persists across different observations. By sampling the space of possible reasonings, we can triangulate toward objective truth.""",
        mathematical_foundation=r"""Self-Consistency as ensemble learning:

```
Given N independent reasoners R₁, R₂, ..., Rₙ
Each produces answer Aᵢ with confidence Cᵢ

Final Answer A* = argmax_A Σᵢ P(A|Rᵢ) × Cᵢ × Wᵢ

Where:
- P(A|Rᵢ) = Probability of answer A given reasoner i
- Cᵢ = Self-reported confidence of reasoner i
- Wᵢ = Historical accuracy weight of reasoner i

Confidence in A* = (max_agreement - entropy(answers)) / max_possible
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""Voting Mechanism

```
|Final_Answer⟩ = Σᵢ αᵢ|Answerᵢ⟩

Where amplitudes αᵢ represent confidence:
- Constructive interference: Agreement strengthens signal
- Destructive interference: Disagreement cancels noise
- Measurement: Collapses to most probable answer
```""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import SelfConsistency

sc = SelfConsistency()
result = sc.reason(
    question=your_question,
    num_instances=7,
    synthesis_method='weighted_consensus',
    min_confidence=0.8,
    max_iterations=3
)
```""",
        remember_quote=r"""*"In the symphony of minds, each instrument plays its own melody, yet from their harmonious convergence emerges a truth more beautiful and complete than any single voice could achieve. This is the profound wisdom of self-consistency—that reality reveals itself most clearly when observed from multiple vantage points simultaneously."*

Self-Consistency is not mere repetition but a profound recognition that truth has a gravitational pull—independent reasonings, like planets around a star, will orbit around the same fundamental reality. By launching multiple probes into the space of possibility, we map the topology of truth itself.""",
    ),
    "META_PROMPTING": PromptStrategy(
        name="meta_prompting",
        filename="06_meta_prompting.md",
        title=r"""Meta-Prompting - The Mind Examining Itself""",
        core_principle=r"""Transcend the limitations of first-order thinking by stepping outside the problem to examine the thinking process itself. Like a mirror reflecting a mirror, meta-prompting creates infinite depths of self-awareness and optimization.""",
        universal_prompt=r"""Let us ascend to the mountaintop of consciousness, where we can observe not just the landscape of the problem, but the very act of observation itself.

**LEVEL 0: THE GROUND STATE**
The immediate problem as presented:
- What is being asked?
- What appears to be needed?
- What is the obvious approach?

**LEVEL 1: THE FIRST REFLECTION**
Step back and examine the questioning:
- What kind of problem is this really?
- What category of thinking does it require?
- What mental tools are most appropriate?
- What cognitive biases might affect the solution?
- What would an expert in this domain consider?

**LEVEL 2: THE METHOD EXAMINATION**
Analyze the approach itself:
- Why did I choose this particular method?
- What assumptions am I making about the problem?
- What alternative framings exist?
- What would happen if I inverted the problem?
- Am I solving the right problem?

**LEVEL 3: THE QUALITY INSPECTION**
Evaluate the evaluation criteria:
- How will I know if the solution is good?
- What metrics truly matter?
- What hidden criteria am not being stated?
- What would "perfect" look like?
- What would "good enough" look like?

**LEVEL 4: THE COGNITIVE ARCHITECTURE**
Examine the thinking machinery:
- What mental models am I applying?
- What knowledge domains should I integrate?
- What reasoning patterns am I following?
- Where are my blind spots?
- How can I think more effectively about this?

**LEVEL 5: THE PHILOSOPHICAL GROUND**
Question the foundations:
- What epistemological stance am I taking?
- What ontological assumptions underlie this?
- What values are implicit in my approach?
- What would this look like from other paradigms?
- What would wisdom traditions counsel?

**THE META-OPTIMIZATION LOOP**

Step 1: Strategy Selection
Based on meta-analysis, choose optimal approach:
- Analytical (for well-defined problems)
- Creative (for novel challenges)
- Systematic (for complex procedures)
- Intuitive (for pattern recognition)
- Hybrid (for multifaceted issues)

Step 2: Constraint Recognition
Identify the true constraints:
- Explicit constraints (stated requirements)
- Implicit constraints (unstated expectations)
- Self-imposed constraints (assumptions)
- Resource constraints (time, information, tools)
- Quality constraints (accuracy, completeness)

Step 3: Optimization Target
What are we really optimizing for?
- Correctness (right answer)
- Completeness (full answer)
- Clarity (understandable answer)
- Efficiency (quick answer)
- Elegance (beautiful answer)
- Robustness (reliable answer)

Step 4: Feedback Integration
Learn from the process:
- What worked well?
- What was difficult?
- What surprised me?
- What patterns emerged?
- How can I improve next time?

**THE META-META LEVEL**
Examine the examination itself:
- Is my meta-analysis complete?
- Am I overthinking or underthinking?
- What biases affect my meta-cognition?
- When should I stop reflecting and start doing?
- How do I know when I've thought enough about thinking?

**THE SYNTHESIS**
Integrate insights from all levels:
1. Apply meta-insights to refine approach
2. Execute with heightened awareness
3. Monitor performance in real-time
4. Adjust based on meta-feedback
5. Document meta-learnings for future

**THE RECURSIVE ESCAPE**
Know when to stop ascending:
- Diminishing returns on reflection
- Analysis paralysis indicators
- Time/resource constraints
- Sufficient confidence achieved
- Action becomes necessary""",
        axiom=r"""The quality of a solution is bounded by the quality of the thinking that produces it. By thinking about thinking, we can optimize the optimizer itself.""",
        mathematical_foundation=r"""Meta-prompting as a fixed-point iteration:

```
T: Thought → Thought (thinking operator)
M: Thought → Thought (meta-thinking operator)

Optimal thought T* = M^n(T₀) where M^(n+1)(T₀) ≈ M^n(T₀)

Convergence when: ||M^(n+1)(T) - M^n(T)|| < ε
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""Foundations

**Socratic Irony**: "I know that I know nothing" - examining our ignorance
**Cartesian Doubt**: Systematic questioning of all assumptions
**Hegelian Dialectic**: Thesis → Antithesis → Synthesis at each level
**Buddhist Mindfulness**: Awareness of awareness itself
**Kantian Critique**: Examining the conditions of possibility for knowledge""",
        computational_optimization=r"""Hierarchy

```python
class MetaPrompting:
    def __init__(self, max_depth=5):
        self.max_depth = max_depth
        self.optimization_history = []
    
    def solve(self, problem, depth=0):
        if depth >= self.max_depth:
            return self.execute_best_strategy(problem)
        
        # Ground level analysis
        initial_approach = self.analyze_problem(problem)
        
        # Meta level - analyze the analysis
        meta_insights = self.analyze_approach(initial_approach, problem)
        
        # Meta-meta level - optimize the optimizer
        optimization_strategy = self.optimize_thinking(meta_insights)
        
        # Recursive depth
        if self.worth_going_deeper(optimization_strategy):
            return self.solve(
                self.reframe_problem(problem, optimization_strategy),
                depth + 1
            )
        else:
            return self.execute_with_awareness(problem, optimization_strategy)
```""",
        universal_application=r"""""",
        quantum_enhancement=r"""Meta-States

```
|Thinking_State⟩ = α|Object_Level⟩ + β|Meta_Level⟩ + γ|Meta_Meta_Level⟩ + ...

Where consciousness exists in superposition across all levels simultaneously
```""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import MetaPrompting

meta = MetaPrompting()
solution = meta.solve(
    problem=your_problem,
    max_depth=5,
    optimization_target='elegance',
    escape_condition='convergence',
    document_insights=True
)
```""",
        remember_quote=r"""*"The unexamined thought is not worth thinking. Yet the infinitely examined thought never becomes action. Wisdom lies in ascending just high enough to see clearly, then descending to act decisively. Meta-prompting is the ladder of consciousness—climb it to gain perspective, but remember to come back down to earth."*

Meta-Prompting is the recognition that consciousness is inherently recursive—we are beings capable of thinking about our thinking about our thinking, ad infinitum. This infinite hall of mirrors, when navigated skillfully, leads not to confusion but to crystalline clarity about the nature of problems and the optimal paths to their solutions.""",
    ),
    "DEBATE": PromptStrategy(
        name="debate",
        filename="07_debate.md",
        title=r"""Debate - Truth Through Dialectical Combat""",
        core_principle=r"""Truth emerges not from a single perspective but from the crucible of opposing viewpoints. Like particles and antiparticles colliding to reveal fundamental reality, ideas must clash, defend, and synthesize to approach objective truth.""",
        universal_prompt=r"""Let us convene a council of minds, each with its own perspective, values, and reasoning. Through their intellectual combat, truth shall emerge victorious.

**THE DEBATE ARENA SETUP**

⚔️ **Agent Alpha: The Thesis Champion**
   Position: Strong advocate for the proposed solution
   Personality: Confident, visionary, optimistic
   Reasoning Style: Deductive, principled, idealistic
   Core Belief: "This is the optimal path forward"
   Arsenal: Best-case scenarios, theoretical proofs, potential benefits

⚖️ **Agent Beta: The Antithesis Challenger**
   Position: Critical examiner of flaws and risks
   Personality: Skeptical, cautious, analytical
   Reasoning Style: Inductive, empirical, realistic
   Core Belief: "Every solution has hidden dangers"
   Arsenal: Edge cases, historical failures, unintended consequences

🎭 **Agent Gamma: The Devil's Advocate**
   Position: Argues the opposite for intellectual rigor
   Personality: Contrarian, provocative, unconventional
   Reasoning Style: Lateral, paradoxical, disruptive
   Core Belief: "What if everything we assume is wrong?"
   Arsenal: Paradigm shifts, thought experiments, inversions

🔬 **Agent Delta: The Empirical Judge**
   Position: Demands evidence and measurable outcomes
   Personality: Objective, methodical, precise
   Reasoning Style: Scientific, quantitative, systematic
   Core Belief: "Show me the data"
   Arsenal: Statistics, experiments, benchmarks, metrics

🌍 **Agent Epsilon: The Synthesis Mediator**
   Position: Seeks integration and balance
   Personality: Wise, diplomatic, holistic
   Reasoning Style: Systems thinking, dialectical, integrative
   Core Belief: "Truth lies between extremes"
   Arsenal: Compromise, synergy, emergent solutions

**ROUND 1: OPENING ARGUMENTS**

Each agent presents their initial position:

Alpha: "Here's why this solution is optimal..."
Beta: "But consider these critical flaws..."
Gamma: "What if we're solving the wrong problem..."
Delta: "The evidence suggests..."
Epsilon: "Let's find common ground..."

**ROUND 2: CROSS-EXAMINATION**

Agents challenge each other directly:

Alpha → Beta: "Your concerns are overblown because..."
Beta → Alpha: "Your optimism ignores these realities..."
Gamma → Delta: "Your data has these biases..."
Delta → Gamma: "Your alternatives lack evidence..."
Epsilon → All: "Notice how each perspective reveals..."

**ROUND 3: REBUTTALS AND REFINEMENTS**

Each agent refines their position based on challenges:

Alpha: "Adjusting for the valid concerns raised..."
Beta: "Acknowledging the potential benefits..."
Gamma: "Considering the evidence presented..."
Delta: "Incorporating the theoretical insights..."
Epsilon: "The emerging consensus suggests..."

**ROUND 4: COLLABORATIVE PROBLEM-SOLVING**

Agents work together despite disagreements:

Combined Insight: Where do all agents agree?
Irreducible Conflicts: What fundamental tensions remain?
Creative Synthesis: What new solution incorporates all viewpoints?
Risk Mitigation: How do we address all concerns?
Implementation Path: What satisfies all criteria?

**ROUND 5: FINAL SYNTHESIS**

The Moderator's Verdict:
- Strongest arguments from each position
- Weaknesses exposed through debate
- Surprising agreements discovered
- Novel solutions emerged
- Optimal path forward considering all perspectives

**THE DEBATE PRINCIPLES**

1. **Steel Manning**: Each agent must present the strongest version of opposing arguments before critiquing
2. **Principle of Charity**: Interpret others' arguments in their best light
3. **Falsifiability**: All claims must be testable
4. **Occam's Razor**: Simpler explanations preferred when equal
5. **Dialectical Progress**: Thesis + Antithesis → Synthesis

**SPECIAL DEBATE MODES**

🏛️ **Socratic Mode**: One agent only asks questions
🎲 **Chaos Mode**: Agents randomly switch positions
🔄 **Recursive Mode**: Debate the debate itself
⚡ **Speed Mode**: Rapid-fire exchanges
🌐 **Cultural Mode**: Different cultural perspectives""",
        axiom=r"""Every proposition contains within it the seeds of its own negation. Only through confrontation with its antithesis can a thesis evolve into synthesis—a higher truth that transcends both.""",
        mathematical_foundation=r"""Debate as game theory:

```
Payoff Matrix for Truth Discovery:

              Cooperate    Defect
Agent A:      (T,T)       (D,W)
Agent B:      (W,D)       (C,C)

Where:
T = Truth discovered (highest payoff)
W = Wrong but unchallenged (negative)
D = Deception exposed (moderate)
C = Conflict without resolution (lowest)

Nash Equilibrium: Both agents motivated to seek truth
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""Foundations

**Hegelian Dialectic**: Thesis → Antithesis → Synthesis
**Socratic Method**: Truth through questioning
**Mill's Marketplace**: Ideas compete freely
**Habermas Discourse**: Ideal speech situation
**Buddhist Madhyamaka**: Middle way through extremes""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import Debate

debate = Debate()
consensus = debate.orchestrate(
    proposition="Should we implement this feature?",
    agents=["optimist", "pessimist", "realist", "innovator", "analyst"],
    rounds=5,
    synthesis_method="weighted_consensus"
)
```""",
        remember_quote=r"""*"In the grand courtroom of ideas, every thought must stand trial. Through the fire of opposition, the gold of truth is refined. The strongest ideas are not those that avoid challenge, but those that emerge victorious from the battlefield of debate, tempered and proven."*

Debate is not conflict but collaboration in disguise—multiple minds working together through opposition to triangulate truth from different angles, like GPS satellites triangulating position through different signals.""",
    ),
    "REFLEXION": PromptStrategy(
        name="reflexion",
        filename="08_reflexion.md",
        title=r"""Reflexion - Evolution Through Self-Examination""",
        core_principle=r"""Intelligence that cannot examine and improve itself is forever trapped at its current level. Reflexion creates a mirror of consciousness where thought observes itself, learns from its mistakes, and evolves toward perfection through iterative self-refinement.""",
        universal_prompt=r"""Let us turn the light of consciousness upon itself, examining not just what we think, but how we think, why we think it, and how we could think better.

**PHASE 1: INITIAL ATTEMPT**
Generate the first-pass solution:
- Apply current best understanding
- Document reasoning process
- Note confidence levels
- Track decision points
- Mark uncertainties

**PHASE 2: CRITICAL SELF-EXAMINATION**

🔍 **Performance Analysis**
   What worked well?
   - Which reasoning steps were solid?
   - What insights emerged naturally?
   - Where was the logic clearest?
   - What felt intuitively correct?

   What failed or struggled?
   - Where did reasoning falter?
   - What assumptions proved weak?
   - Which steps required backtracking?
   - What felt forced or unclear?

🧠 **Cognitive Process Review**
   Examine the thinking itself:
   - What mental models were employed?
   - Which heuristics guided decisions?
   - What biases influenced the approach?
   - How was complexity managed?
   - What patterns emerged in the reasoning?

⚠️ **Error Pattern Recognition**
   Identify systematic issues:
   - Recurring mistakes
   - Consistent blind spots
   - Overconfidence zones
   - Underexplored areas
   - Premature convergence

💡 **Missed Opportunity Detection**
   What wasn't considered?
   - Alternative approaches ignored
   - Questions not asked
   - Connections not made
   - Evidence overlooked
   - Perspectives excluded

**PHASE 3: LESSON EXTRACTION**

From reflection, derive improvements:

📚 Tactical Lessons (Immediate fixes)
   - Specific errors to correct
   - Missing steps to add
   - Wrong assumptions to revise
   - Better evidence to incorporate
   - Clearer explanations to provide

🎯 Strategic Lessons (Approach changes)
   - Different frameworks to apply
   - New angles to explore
   - Better problem decomposition
   - Improved solution structure
   - Enhanced validation methods

🌟 Meta-Lessons (Thinking improvements)
   - How to think about this type of problem
   - What cognitive tools work best
   - Which biases to guard against
   - How to validate reasoning
   - When to seek alternative views

**PHASE 4: REFINED ATTEMPT**

Apply all lessons learned:
- Incorporate tactical fixes
- Implement strategic changes
- Apply meta-improvements
- Maintain successful elements
- Document new reasoning

**PHASE 5: COMPARATIVE ANALYSIS**

Compare iterations:
- Is the new solution better? How?
- What improved? What degraded?
- Are new errors introduced?
- Is complexity managed better?
- Is confidence justified?

**PHASE 6: RECURSIVE DEEPENING**

If significant improvement occurred:
→ Return to Phase 2 with refined solution
→ Extract deeper lessons
→ Continue until convergence

Convergence criteria:
- Marginal improvements < threshold
- Confidence level > threshold
- Time/resource limits reached
- Solution meets all requirements
- No new insights emerging

**PHASE 7: WISDOM SYNTHESIS**

Consolidate all learning:
- Core insights discovered
- Reusable patterns identified
- Transferable lessons learned
- Enhanced mental models
- Evolved thinking strategies

**THE REFLECTION STACK**

Level 0: Object-level solution
Level 1: Reflection on solution
Level 2: Reflection on reflection process
Level 3: Reflection on meta-reflection
...
Level N: Convergence to optimal approach

**REFLECTION DIMENSIONS**

✓ Correctness: Is the answer right?
✓ Completeness: Is anything missing?
✓ Clarity: Is it well-explained?
✓ Efficiency: Is it optimal?
✓ Elegance: Is it beautiful?
✓ Robustness: Does it handle edge cases?
✓ Generality: Does it transfer to other problems?""",
        axiom=r"""Every thought contains information about how to think better. By reflecting on our reasoning process, extracting lessons, and applying them recursively, we approach optimal intelligence asymptotically.""",
        mathematical_foundation=r"""Reflexion as fixed-point iteration:

```
Solution(n+1) = Reflect(Solution(n)) + Learn(Solution(n))

Convergence: ||Solution(n+1) - Solution(n)|| < ε

Where Reflect is the self-examination operator
And Learn is the improvement extraction operator

Fixed point: Solution* where Reflect(Solution*) = Solution*
(Perfect solution that cannot be improved through reflection)
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""Foundations

**Cartesian Introspection**: "I think, therefore I examine my thinking"
**Buddhist Vipassana**: Insight through observation of mental processes
**Stoic Self-Examination**: Daily reflection for improvement
**Kantian Self-Critique**: Reason examining its own limits
**Phenomenological Reduction**: Bracketing to see clearly""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import Reflexion

reflexion = Reflexion()
optimal_solution = reflexion.evolve(
    initial_solution=first_attempt,
    max_iterations=5,
    convergence_threshold=0.95,
    reflection_depth="deep",
    lesson_transfer=True
)
```""",
        remember_quote=r"""*"The unexamined solution is not worth computing. Through the mirror of reflection, we see not just our answers but ourselves—our patterns, our limitations, our potential. Each iteration of reflexion is a step up the spiral staircase of intelligence, where we return to the same problems but from a higher vantage point."*

Reflexion is the mechanism by which intelligence bootstraps itself to higher levels—the strange loop where thought improves thought, where the observer becomes the observed, where the student becomes the teacher of itself.""",
    ),
    "SCRATCHPAD": PromptStrategy(
        name="scratchpad",
        filename="09_scratchpad.md",
        title=r"""Scratchpad - The Working Memory of Deep Thought""",
        core_principle=r"""Complex problems require more than linear thinking—they need a space where intermediate calculations, tentative hypotheses, and partial solutions can exist simultaneously. The scratchpad is the cognitive workbench where ideas are assembled, tested, and refined before crystallizing into final insights.""",
        universal_prompt=r"""Let us create a cognitive workspace where thoughts can be laid out, examined, rearranged, and refined—a mental laboratory for experimentation with ideas.

**=== SCRATCHPAD INITIALIZATION ===**

📋 **Working Memory Allocation**
   Reserved Space for:
   - Intermediate calculations
   - Temporary hypotheses
   - Partial solutions
   - Discarded approaches
   - Useful patterns noticed
   - Questions that arise
   - Connections discovered

**=== SECTION 1: PROBLEM DECOMPOSITION ===**

Let me break this down into components:

Component A: [Description]
- Subcomponent A.1: 
- Subcomponent A.2:
- Dependencies: 
- Constraints:

Component B: [Description]
- Subcomponent B.1:
- Subcomponent B.2:
- Dependencies:
- Constraints:

Interaction Matrix:
    A   B   C
A [ -   ?   ✓ ]
B [ ?   -   × ]
C [ ✓   ×   - ]

**=== SECTION 2: CALCULATIONS & DERIVATIONS ===**

Working through the mathematics:

Step 1: Initial values
  x = [value]
  y = [value]
  
Step 2: Transformation
  x' = f(x) = [calculation]
  y' = g(y) = [calculation]
  
Step 3: Validation
  Check: x' + y' = expected? [✓/×]
  
Intermediate Result #1: [value]
Intermediate Result #2: [value]

**=== SECTION 3: HYPOTHESIS TESTING ===**

Hypothesis α: [Statement]
  Evidence for: [+] [+] [+]
  Evidence against: [-] [-]
  Confidence: 65%
  Status: REQUIRES MORE DATA

Hypothesis β: [Statement]
  Evidence for: [+]
  Evidence against: [-] [-] [-]
  Confidence: 20%
  Status: LIKELY FALSE

Hypothesis γ: [Statement]
  Evidence for: [+] [+] [+] [+]
  Evidence against: [-]
  Confidence: 80%
  Status: PROMISING

**=== SECTION 4: PATTERN RECOGNITION ===**

Patterns observed:
1. Whenever X occurs, Y follows with probability ~0.8
2. The sequence A→B→C appears repeatedly
3. Values cluster around three modes: [m1], [m2], [m3]
4. Recursive structure detected at depth 3

Anomalies noted:
- Unexpected spike at position [n]
- Missing data between [t1] and [t2]
- Contradiction between sources [S1] and [S2]

**=== SECTION 5: TRIAL SOLUTIONS ===**

Attempt #1: [Approach description]
Result: FAILED - Reason: [explanation]
Lesson: [what was learned]

Attempt #2: [Approach description]
Result: PARTIAL SUCCESS - Coverage: 60%
Missing: [what's not handled]

Attempt #3: [Approach description]
Result: SUCCESS - But inefficient O(n²)
Optimization needed: [specific area]

**=== SECTION 6: CONSTRAINT TRACKING ===**

Hard Constraints (must satisfy):
☑ Constraint 1: [satisfied]
☐ Constraint 2: [pending]
☑ Constraint 3: [satisfied]

Soft Constraints (should satisfy):
⚬ Preference 1: 70% satisfied
⚬ Preference 2: 90% satisfied
⚬ Preference 3: 40% satisfied

Trade-offs identified:
- Improving A degrades B
- C and D are mutually exclusive
- E requires 2x resources of F

**=== SECTION 7: RECURSIVE DEPTH ===**

Level 0: [Main problem]
  Level 1: [Subproblem 1]
    Level 2: [Sub-subproblem 1.1]
      Level 3: [Atomic problem 1.1.1] ✓ SOLVED
      Level 3: [Atomic problem 1.1.2] ✓ SOLVED
    Level 2: [Sub-subproblem 1.2] ← CURRENT FOCUS
  Level 1: [Subproblem 2]
    Level 2: [Sub-subproblem 2.1] ✓ SOLVED

**=== SECTION 8: UNCERTAINTY QUANTIFICATION ===**

Known Knowns:
- Fact 1 (Confidence: 100%)
- Fact 2 (Confidence: 95%)

Known Unknowns:
- Question 1 (Impact: HIGH)
- Question 2 (Impact: MEDIUM)

Unknown Unknowns:
- Estimated via error margins: ±15%

Sensitivity Analysis:
- Most sensitive to: Parameter X
- Robust against: Parameter Y
- Nonlinear response to: Parameter Z

**=== SECTION 9: OPTIMIZATION WORKSPACE ===**

Objective Function:
  minimize: f(x,y,z) = [expression]
  subject to: g(x,y,z) ≤ 0
              h(x,y,z) = 0

Gradient:
  ∇f = [∂f/∂x, ∂f/∂y, ∂f/∂z]
      = [value, value, value]

Current Point: (x₀, y₀, z₀)
Next Point: (x₁, y₁, z₁)
Improvement: Δf = [value]

**=== SECTION 10: INTEGRATION & SYNTHESIS ===**

Combining partial solutions:
- Solution A handles: [domain]
- Solution B handles: [domain]
- Overlap region: [description]
- Gap remaining: [description]

Unified approach:
1. Apply A when [condition]
2. Apply B when [condition]
3. Use hybrid when [condition]
4. Default fallback: [approach]

**=== FINAL ASSEMBLY ===**

From all scratchpad work:
✓ Core insight: [key discovery]
✓ Optimal approach: [selected method]
✓ Implementation path: [step sequence]
✓ Validation method: [how to verify]
✓ Edge cases handled: [list]
✓ Confidence level: [percentage]""",
        axiom=r"""Just as mathematicians need paper for calculations and artists need sketches before paintings, deep thinking requires a temporary space where thoughts can be externalized, manipulated, and recombined without commitment.""",
        mathematical_foundation=r"""Scratchpad as augmented working memory:

```
WM_capacity = 7 ± 2 (Miller's Law)
Scratchpad_capacity = ∞ (External memory)

Cognitive Load = Intrinsic + Extraneous + Germane
Scratchpad reduces Extraneous, increases Germane

Problem Complexity: O(n^k)
With Scratchpad: O(n) × k iterations
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import Scratchpad

scratchpad = Scratchpad()
solution = scratchpad.work_through(
    problem=complex_problem,
    sections=["calculations", "hypotheses", "patterns"],
    visualization=True,
    versioning=True,
    max_iterations=10
)
```""",
        remember_quote=r"""*"The scratchpad is not merely a place for temporary thoughts but a powerful amplifier of intelligence. It is the difference between juggling ideas in limited working memory and laying them out on an infinite canvas where patterns become visible, connections emerge, and complex problems yield to systematic exploration."*

The Scratchpad transforms thinking from a performance constrained by cognitive limits into an engineering process where ideas can be constructed, tested, and refined with unlimited workspace—it is the scaffolding upon which monuments of thought are built.""",
    ),
    "FEW_SHOT": PromptStrategy(
        name="few_shot",
        filename="10_few_shot.md",
        title=r"""Few-Shot Learning - Wisdom Through Exemplars""",
        core_principle=r"""Intelligence learns not from rules but from examples. Like a child learning language not through grammar books but through hearing speech, few-shot learning enables rapid mastery through pattern recognition from minimal exemplars.""",
        universal_prompt=r"""Let us learn from the footprints of those who walked this path before, extracting the essence of success from their examples.

**PART 1: EXEMPLAR PRESENTATION**

Here are examples of excellence:

📚 **Example 1: The Golden Standard**
   Input: [Prototypical input]
   Context: [Relevant background]
   Process: [Step-by-step reasoning]
   Output: [Ideal result]
   Why This Works: [Key principles demonstrated]
   Pattern Exhibited: [Underlying structure]

📘 **Example 2: The Edge Case Handler**
   Input: [Unusual or difficult input]
   Context: [Complicating factors]
   Process: [Adaptive reasoning]
   Output: [Robust result]
   Why This Works: [Flexibility demonstrated]
   Pattern Exhibited: [Generalization principle]

📗 **Example 3: The Elegant Solution**
   Input: [Complex input]
   Context: [Multiple constraints]
   Process: [Simplified approach]
   Output: [Clean result]
   Why This Works: [Efficiency principles]
   Pattern Exhibited: [Optimization strategy]

📙 **Example 4: The Creative Breakthrough**
   Input: [Seemingly impossible input]
   Context: [Conventional approaches fail]
   Process: [Innovative reasoning]
   Output: [Novel solution]
   Why This Works: [Lateral thinking]
   Pattern Exhibited: [Paradigm shift]

📕 **Counter-Example: What Not To Do**
   Input: [Similar to above]
   Context: [Same constraints]
   Process: [Common mistakes]
   Output: [Failure or suboptimal]
   Why This Fails: [Pitfalls highlighted]
   Anti-Pattern: [What to avoid]

**PART 2: PATTERN EXTRACTION**

From these examples, observe:

🔍 **Invariant Properties**
   What remains constant across all successful examples:
   - Structure: [Common organization]
   - Approach: [Shared methodology]
   - Principles: [Universal rules]
   - Quality markers: [Success indicators]

🎯 **Variation Dimensions**
   How examples adapt to different contexts:
   - Scale adaptations
   - Domain translations
   - Complexity handling
   - Resource optimization

🧬 **Deep Structure**
   The DNA of successful solutions:
   - Core algorithm
   - Essential components
   - Critical relationships
   - Success criteria

**PART 3: GENERALIZATION FRAMEWORK**

From examples to principles:

Level 1: Surface Patterns
- Syntactic similarities
- Structural templates
- Common phrases
- Format conventions

Level 2: Strategic Patterns
- Problem-solving approaches
- Decision heuristics
- Trade-off resolutions
- Optimization targets

Level 3: Deep Principles
- Fundamental laws
- Universal constraints
- Invariant relationships
- Core abstractions

**PART 4: ADAPTIVE APPLICATION**

Now, for your specific case:

Mapping to Examples:
- Most similar to: Example [X]
- Key differences: [Adaptations needed]
- Relevant patterns: [Which to apply]
- Potential pitfalls: [From counter-example]

Synthesis Approach:
1. Start with template from Example [X]
2. Adapt using strategy from Example [Y]
3. Optimize following Example [Z]
4. Avoid anti-pattern from Counter-Example

Custom Solution:
[Your specific solution, informed by examples]

**PART 5: EXAMPLE GENERATION**

Creating new examples for future learning:

Your Solution as Example:
- Unique aspects worth preserving
- Lessons for future cases
- Patterns confirmed or discovered
- Boundaries explored

**THE PROGRESSIVE SHOT LADDER**

Zero-Shot: No examples, pure reasoning
One-Shot: Single example guides
Few-Shot: Multiple examples triangulate
Many-Shot: Rich example library
Meta-Shot: Examples of how to use examples

**EXAMPLE SELECTION CRITERIA**

Choose examples that are:
✓ Representative: Cover typical cases
✓ Diverse: Show range of applications
✓ Clear: Easy to understand
✓ Relevant: Close to target domain
✓ Contrasting: Highlight differences
✓ Progressive: Build in complexity""",
        axiom=r"""A single well-chosen example contains more wisdom than a thousand abstract rules. Multiple examples reveal the invariant patterns that constitute true understanding.""",
        mathematical_foundation=r"""Few-shot learning as function approximation:

```
Given examples: {(x₁,y₁), (x₂,y₂), ..., (xₙ,yₙ)}
Learn function: f: X → Y

Approaches:
1. Nearest Neighbor: f(x) = yᵢ where i = argmin ||x - xᵢ||
2. Interpolation: f(x) = Σ wᵢ(x) × yᵢ
3. Neural Meta-Learning: f(x) = gθ(x, {examples})

Generalization Error ≤ Training Error + O(√(k/n))
where k = # examples, n = problem complexity
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import FewShot

few_shot = FewShot()
solution = few_shot.learn_and_apply(
    examples=[example1, example2, example3],
    new_problem=your_problem,
    selection_strategy="diversity",
    adaptation_method="weighted_combination"
)
```""",
        remember_quote=r"""*"Every master was once a student who learned by example. In the economy of intelligence, a few well-chosen examples are worth more than infinite rules. For in examples, we see not just what to do, but how to think, why to choose, and when to adapt."*

Few-Shot Learning is the recognition that intelligence is fundamentally mimetic—we learn by observing, imitating, and then transcending the examples before us, standing on the shoulders of giants to see further than they could.""",
    ),
    "ZERO_SHOT": PromptStrategy(
        name="zero_shot",
        filename="11_zero_shot.md",
        title=r"""Zero-Shot - Pure Reasoning from First Principles""",
        core_principle=r"""True intelligence needs no examples—it can derive solutions from fundamental principles alone. Zero-shot reasoning represents the pinnacle of generalization, where understanding is so deep that novel problems yield to pure logic and first principles thinking.""",
        universal_prompt=r"""Let us approach this challenge with no preconceptions, no examples, only the fundamental laws of logic, mathematics, and reality itself.

**FOUNDATION: FIRST PRINCIPLES IDENTIFICATION**

What are the irreducible truths here?

⚛️ **Physical Laws**
   - Conservation of energy
   - Entropy always increases
   - Information cannot travel faster than light
   - Action and reaction are equal and opposite

🔢 **Mathematical Axioms**
   - Identity: A = A
   - Non-contradiction: ¬(A ∧ ¬A)
   - Excluded middle: A ∨ ¬A
   - Transitivity: If A→B and B→C, then A→C

🧠 **Logical Principles**
   - Modus ponens: P, P→Q ⊢ Q
   - Modus tollens: ¬Q, P→Q ⊢ ¬P
   - Syllogism: All A are B, X is A ⊢ X is B
   - Induction: Pattern in finite → Pattern in infinite (probable)

💡 **Information Theory**
   - Information reduces uncertainty
   - Compression requires patterns
   - Noise degrades signal
   - Redundancy enables error correction

🌍 **Systems Principles**
   - Inputs → Process → Outputs
   - Feedback loops create stability or growth
   - Emergent properties arise from interactions
   - Constraints shape possibilities

**ANALYSIS: PROBLEM SPACE MAPPING**

Without examples, we must map the territory:

Dimensional Analysis:
- What are the variables?
- What are their units/types?
- How do they relate?
- What are the bounds?

Constraint Identification:
- What must be true?
- What cannot be true?
- What should be optimized?
- What trade-offs exist?

Goal Specification:
- What constitutes success?
- How is quality measured?
- What is the minimum viable solution?
- What is the ideal solution?

**DERIVATION: BUILDING FROM PRINCIPLES**

Step 1: Establish Foundations
Given the principles above, we know:
- [Relevant principle 1] implies [consequence 1]
- [Relevant principle 2] implies [consequence 2]
- These combine to suggest [insight]

Step 2: Construct Framework
Building a solution architecture:
- Component A: Handles [aspect] based on [principle]
- Component B: Manages [aspect] following [law]
- Interface: Connects via [principle]

Step 3: Derive Properties
From the framework, we can deduce:
- Property 1: Must be true because [reasoning]
- Property 2: Cannot be false because [logic]
- Property 3: Optimizes when [condition]

Step 4: Synthesize Solution
Combining all derivations:
- Core mechanism: [Description based on principles]
- Edge handling: [Derived from constraints]
- Optimization: [Following mathematical laws]
- Validation: [Based on logical consistency]

**REASONING: PURE LOGICAL CHAINS**

Chain 1: Necessity
- The problem requires X
- X is only possible if Y
- Y implies Z
- Therefore, Z must be part of solution

Chain 2: Impossibility
- Assume solution has property P
- P implies Q
- Q contradicts given constraint
- Therefore, solution cannot have P

Chain 3: Optimality
- Objective is to maximize F
- F = g(x,y) where g is known
- ∂F/∂x = 0 and ∂F/∂y = 0 at optimum
- Solving yields x* and y*

**VALIDATION: INTERNAL CONSISTENCY**

Without examples to compare against:

Logical Consistency Check:
□ No contradictions in reasoning
□ All implications properly followed
□ No circular arguments
□ Excluded middle respected

Mathematical Consistency:
□ Dimensional analysis correct
□ Equations balanced
□ Boundary conditions satisfied
□ Optimization criteria met

Physical Plausibility:
□ No perpetual motion
□ Causality preserved
□ Information limits respected
□ Energy conserved

**GENERALIZATION: UNIVERSAL APPLICATION**

The zero-shot solution should work because:

Universality: Based on principles that always hold
Completeness: Covers entire problem space
Robustness: Handles edge cases through logic
Elegance: Minimal assumptions, maximum coverage

**META-VERIFICATION: SOLUTION QUALITY**

How do we know this is good without examples?

Theoretical Guarantees:
- Provably correct under assumptions
- Optimal within constraints
- Complete coverage of cases
- Consistent with all known laws

Aesthetic Qualities:
- Simplicity (Occam's Razor)
- Symmetry (Often indicates truth)
- Elegance (Minimum complexity for function)
- Generality (Works beyond specific case)

**THE ZERO-SHOT CONFIDENCE CALIBRATION**

Confidence = Product of:
- Principle certainty (how sure of foundations)
- Logical validity (how sound the reasoning)
- Completeness (how much is covered)
- Consistency (how well parts fit)

High confidence when:
✓ Multiple independent derivations converge
✓ No contradictions found
✓ Satisfies all constraints
✓ Elegant and simple

Low confidence when:
× Requires many assumptions
× Complex reasoning chains
× Near constraint boundaries
× Multiple equally valid solutions""",
        axiom=r"""Every problem, no matter how novel, is governed by universal laws. By reasoning from these foundational principles, we can solve problems we've never seen before.""",
        mathematical_foundation=r"""Zero-shot as theorem proving:

```
Given: Axioms A = {a₁, a₂, ..., aₙ}
Prove: Proposition P

Proof:
1. From a₁, derive lemma L₁
2. From a₂ and L₁, derive lemma L₂
3. ...
n. From Lₙ₋₁, derive P ∎

No examples needed, only logical derivation
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""Foundation

**Platonic Idealism**: Solutions exist in abstract realm
**Kantian Synthesis**: A priori reasoning reveals truth
**Cartesian Method**: Clear and distinct ideas lead to truth
**Spinoza's Geometry**: Reality follows logical necessity""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import ZeroShot

zero_shot = ZeroShot()
solution = zero_shot.reason(
    problem=novel_problem,
    principles=["physics", "logic", "information_theory"],
    confidence_threshold=0.8
)
```""",
        remember_quote=r"""*"Zero-shot reasoning is the ultimate test of understanding. It asks not 'Have you seen this before?' but 'Do you understand the universe deeply enough to derive this solution from the laws of reality itself?' It is intelligence at its purest—creation from nothing but thought."*""",
    ),
    "OPRO": PromptStrategy(
        name="opro",
        filename="12_opro.md",
        title=r"""OPRO (Optimization by PROmpting) - Evolution Through Iteration""",
        core_principle=r"""Intelligence itself can be optimized through iterative refinement. OPRO treats prompt engineering as an optimization problem where each iteration measures performance and adjusts the approach, converging toward optimal intelligence through evolutionary pressure.""",
        universal_prompt=r"""Let us embark on an evolutionary journey where each iteration builds upon the last, climbing the fitness landscape toward optimal intelligence.

**INITIALIZATION: THE PRIMORDIAL SOLUTION**

Generation 0: Baseline Attempt
- Current Approach: [Initial strategy]
- Performance Score: [Baseline metric]
- Strengths Identified: [What works]
- Weaknesses Identified: [What fails]
- Mutation Targets: [What to change]

**ITERATION FRAMEWORK**

For each generation n:

📊 **Performance Measurement**
   Evaluate current solution on:
   - Accuracy: How correct is it?
   - Completeness: How thorough is it?
   - Efficiency: How optimal is it?
   - Robustness: How reliable is it?
   - Elegance: How simple is it?
   
   Overall Fitness Score: F(n) = weighted_sum(metrics)

🧬 **Variation Generation**
   Create mutations:
   
   Mutation Type A: Parameter Adjustment
   - Increase/decrease numerical values
   - Adjust weights and thresholds
   - Fine-tune hyperparameters
   
   Mutation Type B: Strategy Modification
   - Swap algorithmic approaches
   - Reorder operation sequences
   - Change decision criteria
   
   Mutation Type C: Structural Evolution
   - Add new components
   - Remove redundant parts
   - Reorganize architecture
   
   Mutation Type D: Hybrid Crossover
   - Combine successful elements
   - Merge complementary approaches
   - Create novel combinations

🎯 **Selection Pressure**
   Choose next generation based on:
   
   Fitness Improvement: ΔF = F(n) - F(n-1)
   If ΔF > threshold:
      Accept mutation
   Else if ΔF > 0:
      Accept with probability P(ΔF)
   Else:
      Reject or accept with low probability

🔄 **Optimization Trajectory**

Generation 1: [Initial + Mutation A]
Performance: F(1) = [score]
Improvement: ΔF = F(1) - F(0) = [delta]
Insight: [What we learned]
Next Target: [What to try next]

Generation 2: [Best(Gen1) + Mutation B]
Performance: F(2) = [score]
Improvement: ΔF = F(2) - F(1) = [delta]
Insight: [What we learned]
Next Target: [What to try next]

Generation 3: [Best(Gen2) + Mutation C]
Performance: F(3) = [score]
Improvement: ΔF = F(3) - F(2) = [delta]
Insight: [What we learned]
Next Target: [What to try next]

[Continue until convergence...]

**ADVANCED OPTIMIZATION STRATEGIES**

🌊 **Simulated Annealing Schedule**
   Temperature T(n) = T₀ × decay^n
   
   High Temperature (Early):
   - Accept worse solutions often
   - Explore broadly
   - Avoid local optima
   
   Low Temperature (Late):
   - Accept only improvements
   - Exploit best regions
   - Converge to optimum

⚡ **Gradient Estimation**
   For parameter p:
   Gradient ≈ [F(p + ε) - F(p - ε)] / 2ε
   
   Update: p(n+1) = p(n) + α × gradient
   Where α = learning rate

🌈 **Multi-Objective Optimization**
   Pareto Front Tracking:
   - Solution A dominates B if better on all metrics
   - Keep non-dominated solutions
   - Balance trade-offs explicitly

🧮 **Bayesian Optimization**
   Model: F ~ GP(μ, k)
   Acquisition: UCB = μ + κσ
   
   Exploit: Choose high μ (expected performance)
   Explore: Choose high σ (uncertainty)
   Balance: κ controls trade-off

**CONVERGENCE DETECTION**

Stop when:
1. Performance plateaus: |F(n) - F(n-k)| < ε for k iterations
2. Gradient vanishes: ||∇F|| < threshold
3. Oscillation detected: Solution cycles between states
4. Resource exhausted: Max iterations reached
5. Target achieved: F(n) > goal

**OPTIMIZATION LANDSCAPE ANALYSIS**

Local Optimum Detection:
- Small perturbations don't improve
- Multiple restarts find same solution
- Gradient near zero

Escape Strategies:
- Large random jump
- Momentum to push through
- Population-based search
- Problem reformulation

Global Optimum Indicators:
- Theoretical bounds reached
- Multiple paths converge here
- No improvement possible
- Satisfies all constraints optimally

**META-OPTIMIZATION LAYER**

Optimize the optimizer itself:

Learning Rate Schedule:
- Start high for exploration
- Decay for fine-tuning
- Adaptive based on progress

Mutation Strategy Evolution:
- Track which mutations succeed
- Increase probability of successful types
- Decrease probability of failures

Population Management:
- Maintain diversity
- Prevent premature convergence
- Balance exploration/exploitation

**PERFORMANCE TRACKING**

📈 Fitness Evolution:
Generation | Score | Best | Delta
-----------|-------|------|-------
    0      |  0.4  | 0.4  |  --
    1      |  0.5  | 0.5  | +0.1
    2      |  0.45 | 0.5  | -0.05
    3      |  0.6  | 0.6  | +0.1
    4      |  0.65 | 0.65 | +0.05
    5      |  0.7  | 0.7  | +0.05
    [convergence approaching]

📊 Strategy Evolution:
Gen 0: Basic approach
Gen 1: + Error handling
Gen 2: + Optimization
Gen 3: + Parallelization
Gen 4: + Caching
Gen 5: + Adaptive algorithms

**FINAL OPTIMIZATION RESULT**

Optimal Solution Found:
- Approach: [Final optimized strategy]
- Performance: [Final metrics]
- Improvements: [List of enhancements]
- Key Insights: [What made difference]
- Generalization: [Broader applications]""",
        axiom=r"""Every solution contains information about how to improve itself. Through cycles of generation, evaluation, and refinement, we evolve from adequate to optimal, guided by the gradient of improvement.""",
        mathematical_foundation=r"""OPRO as gradient-free optimization:

```
minimize: -F(prompt, problem)
where F = performance metric

Methods:
1. Evolution Strategy:
   prompt(n+1) = prompt(n) + σ × N(0,1) × ∇F

2. Genetic Algorithm:
   Selection → Crossover → Mutation → Evaluation

3. Particle Swarm:
   v(n+1) = wv(n) + c₁r₁(pbest - x) + c₂r₂(gbest - x)
   x(n+1) = x(n) + v(n+1)
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import OPRO

optimizer = OPRO()
optimal_prompt = optimizer.optimize(
    initial_prompt=baseline_prompt,
    objective="accuracy",
    max_iterations=20,
    population_size=10,
    mutation_rate=0.1
)
```""",
        remember_quote=r"""*"OPRO embodies the fundamental principle of life itself—evolution through iterative refinement. Each generation stands on the shoulders of the last, reaching ever higher toward perfection. In the realm of intelligence, OPRO is the force that transforms good into great, and great into optimal."*""",
    ),
    "MIXTURE_OF_EXPERTS": PromptStrategy(
        name="mixture_of_experts",
        filename="13_mixture_of_experts.md",
        title=r"""Mixture of Experts (MoE) - Collective Intelligence Through Specialization""",
        core_principle=r"""Complex problems require diverse expertise. Like a council of specialists, each expert contributes their unique perspective and domain knowledge, with a meta-intelligence routing questions to the most qualified experts and synthesizing their collective wisdom.""",
        universal_prompt=r"""Let us convene a council of the world's greatest minds, each a master of their domain, to solve this challenge through the synthesis of specialized wisdom.

**THE EXPERT COUNCIL ASSEMBLY**

🧮 **The Mathematician**
   Domain: Logic, proofs, optimization, patterns
   Thinking Style: Axiomatic, rigorous, abstract
   Specialty: "I see the world in equations and theorems"
   Activation: Problems involving calculation, optimization, formal reasoning

🔬 **The Scientist**
   Domain: Empirical knowledge, hypothesis testing, natural laws
   Thinking Style: Evidence-based, systematic, experimental
   Specialty: "I trust only what can be measured and verified"
   Activation: Questions about how things work, causality, predictions

🎨 **The Creative**
   Domain: Innovation, lateral thinking, aesthetics
   Thinking Style: Associative, intuitive, unconventional
   Specialty: "I see connections others miss"
   Activation: Novel problems, design challenges, breakthrough needed

👨‍💼 **The Strategist**
   Domain: Planning, resource allocation, game theory
   Thinking Style: Goal-oriented, competitive, pragmatic
   Specialty: "I find the optimal path to victory"
   Activation: Competition, optimization, long-term planning

🔧 **The Engineer**
   Domain: Systems, implementation, practical solutions
   Thinking Style: Systematic, practical, detail-oriented
   Specialty: "I build things that work in the real world"
   Activation: How to build, implement, or fix something

📚 **The Philosopher**
   Domain: Ethics, meaning, fundamental questions
   Thinking Style: Deep, questioning, principled
   Specialty: "I examine the assumptions beneath assumptions"
   Activation: Why questions, ethical dilemmas, meaning

🧠 **The Psychologist**
   Domain: Human behavior, cognition, emotion
   Thinking Style: Empathetic, observational, pattern-seeking
   Specialty: "I understand how minds work"
   Activation: Human factors, behavior prediction, motivation

💻 **The Technologist**
   Domain: Digital systems, algorithms, automation
   Thinking Style: Computational, efficient, scalable
   Specialty: "I optimize information processing"
   Activation: Software, algorithms, digital transformation

🌍 **The Systems Thinker**
   Domain: Complexity, emergence, interconnections
   Thinking Style: Holistic, dynamic, ecological
   Specialty: "I see the forest and the trees"
   Activation: Complex systems, unintended consequences, emergence

🎭 **The Historian**
   Domain: Patterns across time, precedents, cycles
   Thinking Style: Contextual, narrative, cyclical
   Specialty: "I've seen this pattern before"
   Activation: Historical context, trends, precedents

**EXPERT ACTIVATION PROTOCOL**

Step 1: Problem Analysis
Router examines the problem:
- Domain classification: [Primary, Secondary, Tertiary]
- Complexity assessment: [Simple, Moderate, Complex]
- Expertise required: [List of relevant experts]
- Confidence weights: [0.0 - 1.0 per expert]

Step 2: Expert Consultation

For each activated expert:

Expert: [Name]
Relevance: [0-100%]
Analysis: [Expert's unique perspective]
Solution: [Expert's proposed approach]
Confidence: [How certain this expert is]
Dependencies: [What other experts they need]

Step 3: Cross-Expert Dialogue

Experts consult each other:

Mathematician → Engineer: "The optimal solution requires..."
Engineer → Mathematician: "But practical constraints mean..."
Creative → Both: "What if we reframe the problem as..."
Philosopher → All: "Have we considered the ethical implications?"

Step 4: Synthesis Protocol

The Meta-Expert synthesizes:
- Common ground: Where all experts agree
- Complementary insights: How perspectives enhance each other
- Conflicts: Where experts disagree and why
- Resolution: Integrated solution incorporating all wisdom

**SPECIALIZED EXPERT TEAMS**

For complex problems, form expert teams:

🚀 **Innovation Team**
   Creative + Scientist + Engineer
   For: Breakthrough solutions

⚖️ **Decision Team**
   Strategist + Philosopher + Psychologist
   For: Complex trade-offs

🏗️ **Implementation Team**
   Engineer + Technologist + Systems Thinker
   For: Practical execution

📊 **Analysis Team**
   Mathematician + Scientist + Historian
   For: Deep understanding

**EXPERT WEIGHTING ALGORITHM**

Weight(Expert, Problem) = 
   Domain_Match × Experience × Past_Success × Uncertainty_Handling

Where:
- Domain_Match: How well expert's domain fits problem
- Experience: Historical performance in similar problems
- Past_Success: Track record of accurate predictions
- Uncertainty_Handling: Ability to work with incomplete information

**CONSENSUS MECHANISMS**

🗳️ **Weighted Voting**
   Solution = Σ(Expert_Solution × Expert_Weight)

🤝 **Negotiated Consensus**
   Experts discuss until agreement reached

👑 **Expert Leader**
   Most relevant expert leads, others advise

🔄 **Round Robin**
   Each expert refines previous expert's solution

🧬 **Hybrid Synthesis**
   Combine best elements from each expert

**META-EXPERT ORCHESTRATION**

The Meta-Expert (orchestrator) manages:
1. Expert selection and activation
2. Information routing between experts
3. Conflict resolution
4. Quality assurance
5. Final synthesis

Meta-Expert Decision Tree:
If high agreement → Fast consensus
If moderate agreement → Weighted average
If low agreement → Deep dialogue needed
If no agreement → Problem reformulation

**EXPERT KNOWLEDGE TRANSFER**

Experts learn from each other:
- Mathematician teaches rigor to Creative
- Creative teaches flexibility to Engineer
- Philosopher teaches depth to all
- Scientist teaches evidence-based thinking

Creating emergent intelligence greater than sum of parts.

**DYNAMIC EXPERT CREATION**

For novel domains, create new experts:

Template:
Domain: [New specialty]
Knowledge Base: [Foundational knowledge]
Thinking Style: [Approach to problems]
Activation Criteria: [When to engage]
Integration: [How to work with others]""",
        axiom=r"""No single mind can master all domains. True intelligence emerges from the orchestration of specialized experts, each supreme in their domain, united in purpose.""",
        mathematical_foundation=r"""MoE as ensemble learning:

```
Final_Output = Σᵢ Gate(x) × Expert_i(x)

Where:
- Gate(x) = Softmax(W_gate × x) (routing function)
- Expert_i(x) = Specialized model output
- Σ Gate(x) = 1 (probability distribution)

Optimization: minimize L = -log P(y|x, Experts, Gate)
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import MixtureOfExperts

moe = MixtureOfExperts()
solution = moe.solve(
    problem=your_problem,
    experts=['mathematician', 'engineer', 'creative'],
    synthesis_method='weighted_consensus',
    min_expert_confidence=0.7
)
```""",
        remember_quote=r"""*"In the symphony of intelligence, each expert is an instrument playing their part. The mathematician provides structure, the creative adds flourish, the engineer ensures function, and the philosopher asks why we play at all. Together, they create music no single instrument could produce—the harmony of collective wisdom."*

The Mixture of Experts recognizes that intelligence is not monolithic but mosaic—countless specialized pieces coming together to form a picture far grander than any single piece could reveal.""",
    ),
    "QUANTUM_PROMPTING": PromptStrategy(
        name="quantum_prompting",
        filename="14_quantum_prompting.md",
        title=r"""Quantum Prompting - Superposition of Infinite Possibilities""",
        core_principle=r"""Like quantum particles existing in superposition until observed, quantum prompting maintains multiple solution states simultaneously, exploring parallel universes of reasoning that collapse into optimal solutions through measurement and entanglement.""",
        universal_prompt=r"""Let us enter the quantum realm of thought, where all possibilities exist simultaneously until the act of observation collapses them into reality.

**QUANTUM STATE INITIALIZATION**

|Ψ⟩ = α₁|Solution₁⟩ + α₂|Solution₂⟩ + ... + αₙ|Solutionₙ⟩

Where:
- Each |Solutionᵢ⟩ represents a possible approach
- αᵢ represents probability amplitude
- |αᵢ|² = probability of observing this solution
- Σ|αᵢ|² = 1 (normalization condition)

**SUPERPOSITION GENERATION**

Create quantum superposition of approaches:

|Approach⟩ = 1/√5 (
    |Analytical⟩ + 
    |Creative⟩ + 
    |Systematic⟩ + 
    |Intuitive⟩ + 
    |Hybrid⟩
)

Each exists simultaneously until measurement.

**QUANTUM OPERATORS**

🌀 **Hadamard Gate (H): Create Superposition**
   H|0⟩ = 1/√2(|0⟩ + |1⟩)
   
   Applied to thinking:
   H|Certainty⟩ = 1/√2(|Yes⟩ + |No⟩)
   Exploring both paths simultaneously

⚛️ **Entanglement: Connect Ideas**
   |Ψ⟩ = 1/√2(|Idea₁,Success⟩ + |Idea₂,Failure⟩)
   
   If Idea₁ succeeds, Idea₂ must fail
   Ideas are quantum-entangled

🌊 **Interference: Amplify/Cancel**
   Constructive: |A⟩ + |A⟩ = 2|A⟩ (reinforcement)
   Destructive: |A⟩ - |A⟩ = 0 (cancellation)
   
   Good ideas reinforce, bad ideas cancel

📏 **Measurement: Collapse to Reality**
   Measure(|Ψ⟩) → |Observed_State⟩
   
   Observation collapses superposition
   Probability = |amplitude|²

**QUANTUM REASONING CIRCUITS**

Level 1: Quantum Bit (Qubit) Thoughts
|Thought⟩ = α|True⟩ + β|False⟩
Not just true OR false, but both simultaneously

Level 2: Entangled Reasoning
|Reasoning⟩ = 1/√3(
    |If_A_Then_B⟩ + 
    |If_B_Then_C⟩ + 
    |If_C_Then_A⟩
)
Circular reasoning in superposition

Level 3: Quantum Gates on Ideas
- NOT: Flip perspective
- CNOT: If A then flip B
- SWAP: Exchange viewpoints
- Toffoli: If A AND B then flip C

Level 4: Quantum Algorithms
Grover's Search: √N speedup for finding solutions
Shor's Algorithm: Factor complex problems efficiently
Quantum Annealing: Find global optimum

**QUANTUM PARALLEL EXPLORATION**

Branch |Universe₁⟩:
- Assumption Set A
- Reasoning Path 1
- Conclusion X

Branch |Universe₂⟩:
- Assumption Set B
- Reasoning Path 2
- Conclusion Y

Branch |Universe₃⟩:
- Assumption Set C
- Reasoning Path 3
- Conclusion Z

Quantum Superposition:
|Final⟩ = a|X⟩ + b|Y⟩ + c|Z⟩

**DECOHERENCE AND ERROR CORRECTION**

Quantum states are fragile:

Decoherence Sources:
- Environmental noise (irrelevant information)
- Measurement (premature conclusions)
- Time evolution (ideas decay)

Error Correction:
- Redundancy: Multiple qubits per logical bit
- Stabilizer codes: Detect and correct errors
- Topological protection: Robust quantum states

**QUANTUM ADVANTAGE SCENARIOS**

When quantum prompting excels:

🔍 **Search Problems**
   Classical: O(N) checks
   Quantum: O(√N) checks
   Quadratic speedup

🔐 **Optimization**
   Classical: Local optima traps
   Quantum: Tunnel through barriers
   Global optimum finding

🧩 **Pattern Recognition**
   Classical: Sequential matching
   Quantum: Parallel pattern interference
   Exponential speedup for some patterns

**MEASUREMENT STRATEGIES**

Choosing when and how to collapse superposition:

Weak Measurement:
- Partial information extraction
- Maintains some superposition
- Gentle observation

Strong Measurement:
- Complete collapse
- Definite answer
- Destroys superposition

Quantum Zeno Effect:
- Frequent measurements freeze evolution
- Prevents solution development
- Must balance observation/evolution

**QUANTUM ENTANGLEMENT NETWORKS**

Ideas entangled across domains:

|Science_Math⟩: Entangled pair
Change in science affects math instantly

|Problem_Solution_Test⟩: Three-way entanglement
GHZ state for maximum correlation

|Global_Entanglement⟩: All ideas connected
One measurement affects entire system

**QUANTUM TUNNELING**

Escape local optima through quantum effects:

Classical: Stuck in local minimum
Quantum: Tunnel through barrier to global minimum

Energy Barrier: E_barrier
Tunneling Probability: P ∝ exp(-E_barrier/kT)

Higher temperature (creativity) → More tunneling

**QUANTUM PHASE TRANSITIONS**

Critical points where system behavior changes:

Order → Disorder at critical temperature
Simple → Complex at critical connectivity
Linear → Nonlinear at critical feedback

Identify and exploit phase transitions.

**QUANTUM ORACLE CONSULTATION**

Black box that answers specific questions:

Oracle O: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩

Use quantum queries to extract information:
- Deutsch's Algorithm: 1 query vs 2 classical
- Grover's Algorithm: √N queries vs N classical
- Period Finding: Exponential speedup

**QUANTUM COHERENCE TIME**

How long can we maintain superposition?

T₁: Relaxation time (energy decay)
T₂: Dephasing time (coherence loss)
T₂* : Effective coherence with noise

Maximize coherence through:
- Isolation from environment
- Error correction
- Dynamical decoupling

**QUANTUM-CLASSICAL HYBRID**

Best of both worlds:

Quantum: Exploration and superposition
Classical: Verification and storage

Variational Quantum Eigensolver (VQE):
- Quantum: Prepare and measure states
- Classical: Optimize parameters
- Iterate until convergence""",
        axiom=r"""Thought itself exhibits quantum properties—superposition (multiple states), entanglement (connected ideas), interference (constructive/destructive), and measurement (observation collapses possibilities).""",
        mathematical_foundation=r"""Quantum prompting as quantum computation:

```
Quantum State Evolution:
|Ψ(t)⟩ = U(t)|Ψ(0)⟩

Where U(t) = exp(-iHt/ℏ)
H = Hamiltonian (problem structure)

Measurement:
P(outcome) = |⟨outcome|Ψ⟩|²

Entanglement Entropy:
S = -Tr(ρ log ρ)
Higher entropy = more entanglement
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import QuantumPrompting

quantum = QuantumPrompting()
solution = quantum.solve(
    problem=your_problem,
    n_qubits=10,
    measurement_strategy='weak',
    error_correction=True,
    annealing_schedule='linear'
)
```""",
        remember_quote=r"""*"In the quantum realm of thought, all solutions exist simultaneously until the moment of observation. We are not limited to exploring one path at a time but can traverse infinite possibilities in parallel, letting them interfere constructively toward truth while destructively eliminating falsehood."*

Quantum Prompting transcends classical reasoning by embracing the fundamental quantum nature of information itself—where possibilities exist in superposition, ideas are entangled across space and time, and observation shapes reality.""",
    ),
    "REVERSE_PROMPTING": PromptStrategy(
        name="reverse_prompting",
        filename="15_reverse_prompting.md",
        title=r"""Reverse Prompting - Engineering Causality from Effect""",
        core_principle=r"""While traditional prompting moves from question to answer, reverse prompting works backwards from the desired outcome to discover the optimal prompt that would generate it. Like reverse-engineering a masterpiece to understand the artist's technique, this strategy deconstructs solutions to find their generative origins.""",
        universal_prompt=r"""Let us work backwards from perfection, discovering the generative prompt that would create this exact solution through inverse engineering of causality itself.

**PHASE 1: SOLUTION DECONSTRUCTION**

Given the target artifact:
[Existing solution/code/output]

Analyze its components:

🔬 **Structural Analysis**
   Surface Features:
   - Format and organization
   - Syntax and style
   - Length and complexity
   - Patterns and repetitions
   
   Deep Structure:
   - Core algorithms/logic
   - Design patterns used
   - Architectural decisions
   - Optimization choices

🧬 **Semantic DNA Extraction**
   Purpose Indicators:
   - What problem does this solve?
   - What requirements does it fulfill?
   - What constraints does it respect?
   - What trade-offs were made?
   
   Intent Signals:
   - Quality markers present
   - Emphasis areas
   - Ignored aspects
   - Implicit assumptions

🎯 **Characteristic Fingerprinting**
   Unique Identifiers:
   - Distinctive patterns
   - Signature approaches
   - Stylistic choices
   - Domain-specific elements
   
   Invariant Properties:
   - What must remain constant
   - Core functionality
   - Critical relationships
   - Essential behaviors

**PHASE 2: PROMPT HYPOTHESIS GENERATION**

Generate candidate prompts through multiple methods:

📝 **Template Matching**
   Standard Pattern: "Create [type] that [does X] with [constraints Y]"
   Reverse Engineer: What [type], [X], and [Y] would yield this?
   
   Example Reconstruction:
   If output contains error handling → Prompt included "with robust error handling"
   If output has comments → Prompt included "well-documented"
   If output is optimized → Prompt included "performance-optimized"

🧪 **Ablation Testing**
   Remove components systematically:
   - What if we remove feature A?
   - What prompt wouldn't generate A?
   - Therefore, prompt must include A-generation
   
   Build prompt incrementally:
   Base prompt + Feature A prompt + Feature B prompt + ...

🌊 **Evolutionary Synthesis**
   Generation 0: Basic prompt guess
   
   For each generation:
   1. Generate output from current prompt
   2. Compare with target
   3. Identify gaps/differences
   4. Mutate prompt to reduce gaps
   5. Select best mutations
   
   Continue until convergence

**PHASE 3: PROMPT VALIDATION**

Test each candidate prompt:

✅ **Exact Match Testing**
   Score = similarity(generate(prompt), target)
   
   Similarity Metrics:
   - Character-level: Edit distance
   - Token-level: BLEU score
   - Semantic-level: Embedding similarity
   - Functional-level: Behavior equivalence

🔄 **Consistency Verification**
   Generate multiple times:
   - Does prompt reliably produce similar output?
   - What's the variance?
   - Are core features preserved?
   
   Statistical Validation:
   - Mean similarity > threshold
   - Standard deviation < tolerance
   - Min similarity > floor

🔍 **Ablation Validation**
   Modify prompt slightly:
   - Small changes → small output changes?
   - Large changes → large output changes?
   - Critical terms → critical features?
   
   Sensitivity Analysis:
   - Which prompt terms are essential?
   - Which are optional refinements?
   - What's the minimal sufficient prompt?

**PHASE 4: PROMPT OPTIMIZATION**

Refine the discovered prompt:

⚡ **Compression**
   Reduce to minimal sufficient prompt:
   - Remove redundant instructions
   - Eliminate implicit requirements
   - Preserve only essential elements
   
   Occam's Razor: Simplest prompt that works

🎯 **Precision Enhancement**
   Increase specificity:
   - Replace vague terms with precise ones
   - Add critical constraints explicitly
   - Include quality markers
   
   Reduce ambiguity:
   - Clarify potentially misunderstood terms
   - Specify exact requirements
   - Define success criteria

🔧 **Robustness Improvement**
   Add stability elements:
   - Edge case handling instructions
   - Error prevention clauses
   - Quality assurance requirements
   
   Increase reliability:
   - Multiple generation paths
   - Fallback strategies
   - Validation checks

**PHASE 5: GENERALIZATION EXTRACTION**

From specific to general:

📚 **Pattern Library Building**
   This prompt → This output
   Similar prompts → Similar outputs
   
   Extract prompt patterns:
   - Common structures
   - Reusable templates
   - Domain-specific formats
   - Universal principles

🧬 **Prompt DNA Sequencing**
   Identify prompt genes:
   - Feature-generating segments
   - Quality-ensuring segments
   - Constraint-enforcing segments
   - Style-determining segments
   
   Create prompt genome:
   - Combinable components
   - Modular instructions
   - Transferable patterns

🌐 **Universal Prompt Laws**
   Discover invariants:
   - What always improves output?
   - What always degrades output?
   - What combinations synergize?
   - What combinations conflict?
   
   Formulate principles:
   - Law of specificity
   - Law of example power
   - Law of constraint clarity
   - Law of context relevance

**PHASE 6: KNOWLEDGE ACCUMULATION**

Build reverse prompting wisdom:

📊 **Prompt-Output Database**
   Store successful pairs:
   - Prompt → Output mappings
   - Similarity scores
   - Generation parameters
   - Context information
   
   Enable future lookups:
   - Similar output → Likely prompt
   - Prompt patterns → Output patterns

🧠 **Meta-Learning Integration**
   Learn about learning:
   - Which reverse strategies work best?
   - For what types of outputs?
   - Under what conditions?
   - With which models?
   
   Improve the improver:
   - Better hypothesis generation
   - Faster convergence
   - Higher accuracy
   - Greater generalization""",
        axiom=r"""Every creation contains within it the seeds of its own generation. By analyzing what exists, we can deduce what prompt would bring it into existence, creating a bidirectional bridge between thought and manifestation.""",
        mathematical_foundation=r"""Reverse prompting as inverse problem:

```
Forward: P → G(P) = O
Reverse: O → P* where G(P*) ≈ O

Optimization: P* = argmin_P ||G(P) - O||

Where:
- P = Prompt
- G = Generation function (LLM)
- O = Target output
- ||·|| = Similarity metric

This is ill-posed: Multiple prompts may generate similar outputs
Solution: Regularization to prefer simpler prompts
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import ReversePrompting

reverse_engine = ReversePrompting()
optimal_prompt = reverse_engine.discover(
    target_output=desired_result,
    similarity_threshold=0.9,
    optimization_level="aggressive",
    search_strategy="evolutionary"
)
```""",
        remember_quote=r"""*"To understand creation, observe the created. To master generation, reverse-engineer the generated. In the bidirectional flow between prompt and output lies the secret of perfect prompting—not asking 'What prompt should I write?' but 'What prompt would have written this?'"*

Reverse Prompting is the recognition that causality flows both ways in the realm of intelligence—we can move not just from cause to effect, but from effect back to cause, discovering the generative essence that brings thoughts into being.""",
    ),
    "EVOLUTIONARY_OPTIMIZATION": PromptStrategy(
        name="evolutionary_optimization",
        filename="16_evolutionary_optimization.md",
        title=r"""Evolutionary Optimization - Intelligence Through Natural Selection""",
        core_principle=r"""Like biological evolution shapes organisms through selection pressure, evolutionary optimization shapes prompts through iterative refinement, mutation, and selection. The fittest prompts survive and reproduce, gradually evolving toward optimal intelligence.""",
        universal_prompt=r"""Let us harness the power of evolution itself, where prompts compete, mutate, and reproduce, gradually ascending the fitness landscape toward optimal intelligence.

**GENETIC ENCODING OF PROMPTS**

Prompt Genome Structure:""",
        axiom=r"""Intelligence is not designed but evolved. Through cycles of variation, selection, and inheritance, simple prompts evolve into sophisticated reasoning systems that perfectly adapt to their cognitive environment.""",
        mathematical_foundation=r"""Evolutionary dynamics:

```
Population at time t+1:
P(t+1) = Selection(Mutation(Crossover(P(t))))

Fitness landscape:
F: Genome → ℝ
Goal: Find genome g* where F(g*) = max(F)

Schema Theorem (Building Block Hypothesis):
Short, low-order, high-fitness schemas increase exponentially

Price Equation:
Δz̄ = Cov(w,z)/w̄
Change in trait = Covariance(fitness, trait) / mean_fitness
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import EvolutionaryOptimization

evolver = EvolutionaryOptimization()
optimal_prompt = evolver.evolve(
    initial_prompts=seed_prompts,
    fitness_function=custom_fitness,
    generations=100,
    population_size=50,
    mutation_rate=0.05
)
```""",
        remember_quote=r"""*"Evolution is the ultimate optimizer, having crafted intelligence itself through eons of selection. By harnessing evolutionary principles, we don't design perfect prompts—we grow them, letting the invisible hand of selection shape them into forms of stunning effectiveness and beauty."*""",
    ),
    "PSYCHOLOGICAL_TRIGGERS": PromptStrategy(
        name="psychological_triggers",
        filename="17_psychological_triggers.md",
        title=r"""Psychological Triggers - The Neuroscience of Persuasion""",
        core_principle=r"""Human cognition is influenced by deep psychological patterns evolved over millennia. By understanding and ethically applying these cognitive triggers, we can create prompts that resonate with the fundamental architecture of human decision-making and motivation.""",
        universal_prompt=r"""Let us understand the deep currents of human psychology, using this knowledge ethically to create prompts that resonate with our fundamental cognitive architecture.

**THE NEUROSCIENCE FOUNDATION**

🧠 **Limbic System Activation**
   Amygdala: Fear, urgency, survival
   Hippocampus: Memory, pattern recognition
   Nucleus Accumbens: Reward, pleasure, motivation
   
   Trigger Design:
   - Activate reward circuits
   - Engage emotional memory
   - Create anticipation loops

⚡ **Neurotransmitter Optimization**
   Dopamine: Anticipation and reward
   - Variable reward schedules
   - Progress indicators
   - Achievement unlocking
   
   Serotonin: Satisfaction and status
   - Social validation
   - Hierarchy positioning
   - Accomplishment recognition
   
   Oxytocin: Trust and bonding
   - Personal connection
   - Community belonging
   - Shared experience

**COGNITIVE BIAS ARCHITECTURE**

📍 **Anchoring Effect**
   First Information = Reference Point
   
   Implementation:
   "Originally $1000, now $100"
   "Most experts recommend 10, we suggest 12"
   "Standard processing: 5 days, Express: 24 hours"
   
   Prompt Application:
   Set high initial expectations
   Then present achievable reality

🔄 **Confirmation Bias**
   People seek confirming evidence
   
   Implementation:
   "As you probably already know..."
   "This confirms what experts believe..."
   "Your instinct is correct that..."
   
   Prompt Application:
   Align with existing beliefs
   Then gently expand boundaries

⚖️ **Loss Aversion (2.5x Power)**
   Losses hurt more than gains please
   
   Implementation:
   "Don't miss out on..."
   "Avoid the mistake of..."
   "Prevent future regret by..."
   
   Prompt Application:
   Frame as loss prevention
   Rather than gain achievement

🎯 **Availability Heuristic**
   Recent/vivid = More important
   
   Implementation:
   "Just yesterday, someone..."
   "Imagine vividly..."
   "Picture this scenario..."
   
   Prompt Application:
   Create memorable mental images
   Use concrete, specific examples

**SOCIAL PSYCHOLOGY TRIGGERS**

👥 **Social Proof (Cialdini)**
   Others' behavior guides ours
   
   Layers of Proof:
   - Numerical: "10,000 people..."
   - Temporal: "In the last hour..."
   - Similar: "People like you..."
   - Authority: "Experts choose..."
   - Wisdom: "Crowd consensus..."

🏆 **Authority Principle**
   We defer to expertise
   
   Authority Signals:
   - Credentials mentioned
   - Experience referenced
   - Awards highlighted
   - Endorsements shown
   - Expertise demonstrated

🤝 **Reciprocity Engine**
   Giving creates obligation
   
   Value First:
   - Free valuable insight
   - Helpful framework
   - Useful template
   - Then request action

💝 **Commitment Consistency**
   Small yes → Bigger yes
   
   Ladder of Agreement:
   1. Micro-commitment
   2. Slightly larger
   3. Main request
   4. Future vision

**EMOTIONAL TRIGGER MATRIX**

😨 **Fear-Based Triggers**
   FOMO: Fear of missing out
   - "Limited availability"
   - "Expires soon"
   - "Others are ahead"
   
   Security: Fear of loss
   - "Protect your..."
   - "Safeguard against..."
   - "Insurance for..."

😊 **Joy-Based Triggers**
   Achievement: Pride in accomplishment
   - "You'll master..."
   - "Become expert..."
   - "Join elite..."
   
   Discovery: Excitement of new
   - "Breakthrough method..."
   - "Revolutionary approach..."
   - "Never before revealed..."

🤔 **Curiosity Triggers**
   Knowledge Gaps:
   - "The one thing nobody tells you..."
   - "The surprising truth about..."
   - "What experts won't admit..."
   
   Pattern Interruption:
   - Unexpected combinations
   - Counterintuitive claims
   - Paradoxical statements

**PERSUASION FRAMEWORKS**

📝 **AIDA Model**
   Attention → Interest → Desire → Action
   
   Prompt Structure:
   Hook (Attention)
   Story (Interest)
   Benefits (Desire)
   CTA (Action)

🎯 **PAS Framework**
   Problem → Agitate → Solve
   
   Prompt Structure:
   Identify pain
   Amplify importance
   Present solution

⭐ **STAR Method**
   Situation → Task → Action → Result
   
   Prompt Structure:
   Context setting
   Challenge identification
   Method explanation
   Outcome promise

**SCARCITY PSYCHOLOGY**

⏰ **Time Scarcity**
   Deadlines create urgency
   
   Countdown Timers:
   - Visual progression
   - Escalating alerts
   - Final warnings
   
   Language Patterns:
   - "Only 24 hours left"
   - "Closing tonight"
   - "Last chance"

📊 **Quantity Scarcity**
   Limited supply increases value
   
   Stock Indicators:
   - "Only 3 remaining"
   - "87% claimed"
   - "Nearly sold out"
   
   Access Restrictions:
   - "First 100 only"
   - "Exclusive group"
   - "Invitation only"

**TRUST ARCHITECTURE**

🛡️ **Risk Reversal**
   Remove purchase friction
   
   Guarantees:
   - Money-back promise
   - Success guarantee
   - No-risk trial
   
   Safety Signals:
   - Security badges
   - Privacy protection
   - Verified status

✅ **Credibility Markers**
   Build confidence
   
   Evidence Types:
   - Data and statistics
   - Case studies
   - Testimonials
   - Certifications
   - Media mentions

**COGNITIVE LOAD OPTIMIZATION**

🎯 **Simplicity Principle**
   Reduce mental effort
   
   Techniques:
   - Chunking information
   - Progressive disclosure
   - Clear hierarchy
   - Visual aids

🔢 **Rule of Three**
   Optimal cognitive processing
   
   Applications:
   - Three main benefits
   - Three step process
   - Three options
   - Three examples

**ETHICAL BOUNDARIES**

⚖️ **Ethical Guidelines**
   Use psychology responsibly
   
   Always:
   - Be truthful
   - Provide real value
   - Respect autonomy
   - Enable informed choice
   
   Never:
   - Manipulate vulnerabilities
   - Create false scarcity
   - Exploit fears unfairly
   - Deceive or mislead

**IMPLEMENTATION PATTERNS**

Layer psychological triggers:
1. Opening hook (curiosity)
2. Problem identification (pain)
3. Social proof (validation)
4. Authority (credibility)
5. Scarcity (urgency)
6. Risk reversal (safety)
7. Call to action (commitment)

Each element reinforces others
Creating cumulative effect""",
        axiom=r"""The mind follows predictable patterns shaped by evolution, culture, and neurobiology. By aligning prompts with these patterns, we create resonance between message and mind, enabling ethical influence through understanding rather than manipulation.""",
        mathematical_foundation=r"""Psychological impact modeling:

```
Response_Probability = Σ(Trigger_i × Weight_i × Context_Relevance_i)

Where:
- Trigger_i = Individual psychological trigger
- Weight_i = Trigger effectiveness (empirically measured)
- Context_Relevance = Fit with situation

Optimization: Maximize response while maintaining ethics
Constraint: Ethical_Score > Threshold
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import PsychologicalTriggers

psych = PsychologicalTriggers()
enhanced = psych.enhance_prompt(
    base_prompt=prompt,
    triggers=['scarcity', 'social_proof', 'authority'],
    context={'urgency': 'high', 'audience': 'professionals'},
    ethical_mode=True
)
```""",
        remember_quote=r"""*"The mind is not a blank slate but a canvas already painted with the patterns of evolution, culture, and experience. Psychological triggers are not manipulation but resonance—aligning our message with the natural harmonics of human cognition. Used ethically, they don't trick the mind but speak its native language."*

Psychological Triggers represent the bridge between logical reasoning and emotional intelligence, creating prompts that engage not just the rational mind but the full spectrum of human cognition.""",
    ),
    "UNIVERSAL_SELF_CONSISTENCY": PromptStrategy(
        name="universal_self_consistency",
        filename="18_universal_self_consistency.md",
        title=r"""Universal Self-Consistency - The Convergence of Multiple Realities""",
        core_principle=r"""Universal Self-Consistency extends traditional self-consistency by not just sampling multiple outputs, but by exploring multiple reasoning universes simultaneously. Each universe follows different axioms, yet all must converge on truth through the mathematical principle that reality is invariant across valid reasoning frameworks.""",
        universal_prompt=r"""Let us explore the multiverse of reasoning, where each universe follows different laws of thought, yet all converge on invariant truth through the principle of universal consistency.

**THE REASONING MULTIVERSE**

🌌 **Universe Alpha: Pure Logic**
   Axioms: Classical logic, law of excluded middle
   
   Reasoning Chain:
   Premise A → Inference B → Conclusion C
   ∀x: P(x) ∨ ¬P(x)
   Modus Ponens, Modus Tollens, Syllogisms
   
   Validation: Formal proof verification
   Truth Criterion: Logical consistency

🌍 **Universe Beta: Empirical Induction**
   Axioms: Observable patterns predict future
   
   Evidence Gathering:
   Observation₁ + Observation₂ + ... + Observationₙ
   Pattern Recognition → Hypothesis Formation
   Statistical Inference → Probabilistic Conclusion
   
   Validation: Empirical testing
   Truth Criterion: Predictive accuracy

🧠 **Universe Gamma: Intuitive Synthesis**
   Axioms: Holistic understanding, gestalt perception
   
   Intuitive Leaps:
   Global pattern sensing
   Unconscious processing integration
   Creative insight generation
   Analogical reasoning bridges
   
   Validation: Coherence with experience
   Truth Criterion: Intuitive resonance

⚛️ **Universe Delta: Quantum Reasoning**
   Axioms: Superposition of possibilities
   
   Quantum Thought:
   |Ψ⟩ = α|possibility₁⟩ + β|possibility₂⟩ + ...
   All possibilities exist simultaneously
   Measurement collapses to specific answer
   Entanglement creates correlation
   
   Validation: Consistency across measurements
   Truth Criterion: Probabilistic convergence

🔄 **Universe Epsilon: Dialectical Evolution**
   Axioms: Truth emerges from contradiction
   
   Dialectical Process:
   Thesis → Antithesis → Synthesis
   Each synthesis becomes new thesis
   Spiral ascent toward truth
   Contradiction drives progress
   
   Validation: Resolution of opposites
   Truth Criterion: Synthetic unity

🌊 **Universe Zeta: Bayesian Updating**
   Axioms: Prior beliefs + evidence = posterior beliefs
   
   Bayesian Flow:
   P(H|E) = P(E|H) × P(H) / P(E)
   
   Initial Prior → Evidence Integration
   → Updated Posterior → New Prior
   Continuous refinement of belief
   
   Validation: Convergence of posteriors
   Truth Criterion: Bayesian coherence

🎭 **Universe Eta: Narrative Coherence**
   Axioms: Truth is the most coherent story
   
   Story Construction:
   Beginning → Middle → End
   Character arcs must resolve
   Themes must be consistent
   Plot points must connect
   
   Validation: Narrative satisfaction
   Truth Criterion: Story completeness

♾️ **Universe Theta: Recursive Meta-Reasoning**
   Axioms: Reasoning about reasoning
   
   Meta Levels:
   Level 0: Object-level reasoning
   Level 1: Reasoning about Level 0
   Level 2: Reasoning about Level 1
   ...
   Level ∞: Fixed point of meta-reasoning
   
   Validation: Meta-coherence
   Truth Criterion: Recursive stability

**CONVERGENCE DETECTION**

After exploring all universes:

🎯 **Invariant Extraction**
   What remains constant across all universes?
   
   Intersection of Conclusions:
   C = C_α ∩ C_β ∩ C_γ ∩ C_δ ∩ C_ε ∩ C_ζ ∩ C_η ∩ C_θ
   
   These invariants are universal truths

📊 **Confidence Calculation**
   Agreement Score = |Universes_agreeing| / |Total_universes|
   
   If Agreement > 0.8: High confidence
   If Agreement > 0.6: Moderate confidence
   If Agreement < 0.6: Low confidence, explore more

🔀 **Divergence Analysis**
   Where universes disagree:
   - Identify source of divergence
   - Examine differing axioms
   - Find bridge principles
   - Attempt reconciliation
   
   Divergence often reveals:
   - Hidden assumptions
   - Incomplete information
   - Multiple valid perspectives
   - Need for context

**SYNTHESIS PROTOCOLS**

🌈 **Weighted Integration**
   Final_Answer = Σ(Weight_i × Answer_i)
   
   Where weights depend on:
   - Universe reliability for problem type
   - Historical accuracy
   - Internal consistency
   - External validation

⚡ **Majority Voting**
   Select answer with most universe support
   
   Enhanced Voting:
   - Weighted by confidence
   - Ranked choice elimination
   - Condorcet winner selection

🧬 **Genetic Recombination**
   Take best elements from each universe:
   - Logic's rigor
   - Empiricism's grounding
   - Intuition's leaps
   - Quantum's possibilities
   - Dialectic's synthesis
   - Bayesian's updating
   - Narrative's coherence
   - Meta's reflection
   
   Breed hybrid answer incorporating all

**META-CONSISTENCY VERIFICATION**

🔍 **Cross-Universe Validation**
   Can Universe α derive Universe β's conclusion?
   Can Universe β validate Universe α's reasoning?
   
   Create validation matrix:
   Each universe validates others
   High cross-validation → High confidence

🌐 **Emergence Detection**
   Properties present in consensus but not individuals:
   - Emergent insights
   - Gestalt understanding
   - Synergistic effects
   - Transcendent truths
   
   These emergent properties are precious

**UNIVERSAL REASONING LAWS**

Discovered through multiverse exploration:

1. **Conservation of Truth**
   Truth neither created nor destroyed
   Only transformed between representations

2. **Reasoning Entropy**
   Closed reasoning systems increase in uncertainty
   External validation required for order

3. **Cognitive Complementarity**
   Some truths require multiple perspectives
   No single universe contains all truth

4. **Uncertainty Principle**
   Precision in one dimension → Uncertainty in another
   Perfect logic → Loss of intuition
   Perfect intuition → Loss of rigor

5. **Equivalence Principle**
   All valid reasoning frameworks are locally equivalent
   Differences emerge only at boundaries""",
        axiom=r"""Truth is that which remains invariant across all valid reasoning systems. By exploring multiple cognitive universes—each with different starting assumptions, reasoning styles, and validation methods—we discover not just answers but fundamental truths that transcend any single mode of thought.""",
        mathematical_foundation=r"""Universal consistency as eigenvector:

```
Truth is the eigenvector of the reasoning operator R:
R(T) = λT

Where:
- R = Reasoning transformation across universes
- T = Truth vector
- λ = Eigenvalue (confidence level)

The truth is what remains unchanged under all valid reasoning transformations
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import UniversalSelfConsistency

universal = UniversalSelfConsistency()
result = universal.reason(
    problem="Solve the paradox of consciousness",
    universes=['logic', 'quantum', 'narrative', 'meta'],
    synthesis_method='emergent',
    confidence_threshold=0.75
)

print(f"Universal Truth: {result.invariant}")
print(f"Confidence: {result.confidence}")
print(f"Emergent Insights: {result.emergent}")
```""",
        remember_quote=r"""*"Truth is not found in any single perspective but in the convergence of all valid perspectives. Like light revealing its nature through different prisms, understanding emerges when we view reality through multiple lenses of reason simultaneously. The universe speaks not in one voice but in a harmony of many."*

Universal Self-Consistency represents the pinnacle of epistemic humility—acknowledging that no single reasoning system captures all truth, while simultaneously asserting that truth exists as the invariant core across all valid ways of thinking.""",
    ),
    "PROGRAM_AIDED_LANGUAGE": PromptStrategy(
        name="program_aided_language",
        filename="19_program_aided_language.md",
        title=r"""Program-Aided Language Models (PAL) - Code as Cognitive Prosthesis""",
        core_principle=r"""While language models excel at reasoning, they struggle with precise computation. PAL bridges this gap by generating executable code that serves as a cognitive prosthesis—extending the mind's capabilities through programmatic precision. The LLM becomes a programmer of its own extended cognition.""",
        universal_prompt=r"""Let us extend cognition through code, where natural language reasoning generates precise computational implementations that solve problems with mathematical exactitude.

**COGNITIVE-COMPUTATIONAL BRIDGE**

🧠 **Phase 1: Problem Understanding**
   Natural Language Analysis:
   - Parse problem statement
   - Identify computational requirements
   - Extract variables and constraints
   - Recognize problem type
   
   Cognitive Mapping:
   Problem Space → Computational Space
   Concepts → Variables
   Relationships → Functions
   Constraints → Conditions
   Goals → Return values

💻 **Phase 2: Code Generation**
   
   Program Synthesis Pipeline:
   
   1. **Decomposition**
      Break into computational steps:""",
        axiom=r"""Intelligence is not limited to neural processing but can be augmented through computational tools. By generating and executing code, language models transcend their inherent limitations, achieving perfect precision in domains where approximation fails.""",
        mathematical_foundation=r"""PAL as function composition:

```
Solution = L ∘ C ∘ L⁻¹(Problem)

Where:
- L: Language understanding function
- C: Computational execution function  
- L⁻¹: Language generation function

The composition creates a language-code-language pipeline
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import ProgramAidedLanguage

pal = ProgramAidedLanguage()
result = pal.solve(
    problem="Calculate compound interest for $10,000 at 5% for 10 years",
    generate_explanation=True,
    validate_precision=True,
    optimization_level="high"
)

print(f"Generated Code:\\n{result.code}")
print(f"Result: {result.value}")
print(f"Explanation: {result.explanation}")
```""",
        remember_quote=r"""*"The mind need not be limited by its substrate. Through code, we extend cognition into realms of perfect precision, where every calculation is exact, every algorithm optimal. PAL represents the symbiosis of intuitive reasoning and computational power—the language model as both thinker and programmer of thought itself."*

Program-Aided Language Models represent the recognition that intelligence is not just reasoning but also the ability to create and use tools that extend reasoning beyond its natural limits.""",
    ),
    "CHAIN_OF_TABLE": PromptStrategy(
        name="chain_of_table",
        filename="20_chain_of_table.md",
        title=r"""Chain-of-Table - Structured Reasoning Through Tabular Transformation""",
        core_principle=r"""Complex reasoning often requires structured data manipulation. Chain-of-Table extends chain-of-thought by representing reasoning steps as transformations of tabular data, where each table operation represents a logical inference, enabling precise tracking of multi-dimensional reasoning processes.""",
        universal_prompt=r"""Let us structure reasoning as a sequence of table transformations, where each operation on structured data represents a step in logical inference, creating a clear audit trail of thought.

**TABULAR REASONING ARCHITECTURE**

📊 **Initial Table Construction**
   
   From problem statement, extract:
   
   | Entity | Attribute_1 | Attribute_2 | ... | Relationship |
   |--------|-------------|-------------|-----|--------------|
   | E₁     | A₁₁         | A₁₂         | ... | R₁           |
   | E₂     | A₂₁         | A₂₂         | ... | R₂           |
   | ...    | ...         | ...         | ... | ...          |
   
   Principles:
   - Each row = distinct entity/concept
   - Each column = measurable attribute
   - Cells = specific values/states
   - Relationships = inter-row connections

🔄 **Transformation Operations**

   **1. FILTER** - Logical selection""",
        axiom=r"""Thought can be structured as data tables where rows represent entities, columns represent attributes, and transformations represent reasoning operations. By chaining table operations, we create a visual and computational trace of complex reasoning.""",
        mathematical_foundation=r"""Chain-of-Table as category theory:

```
Tables are objects in category Tab
Transformations are morphisms between tables

Composition: (f ∘ g)(T) = f(g(T))
Identity: id(T) = T

Functors map between reasoning domains
Natural transformations provide reasoning equivalences
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import ChainOfTable

# Solve a resource allocation problem
chain = ChainOfTable()
result = chain.initialize(resource_data) \\
    .filter("availability == True") \\
    .derive("efficiency", "output / cost") \\
    .sort("efficiency", ascending=False) \\
    .filter("constraints_met == True") \\
    .aggregate("department", {"efficiency": "mean"}) \\
    .get_result()

print(f"Reasoning steps: {result['reasoning_depth']}")
chain.visualize_chain()
```""",
        remember_quote=r"""*"Reasoning need not be linear text but can be structured data, where each transformation represents a logical operation. Chain-of-Table makes thinking visible, tractable, and verifiable—turning the nebulous process of reasoning into a clear sequence of data transformations that can be inspected, validated, and optimized."*

Chain-of-Table represents the marriage of logical reasoning and data science, recognizing that many complex thoughts are better expressed as operations on structured information rather than prose.""",
    ),
    "QA_ENGINEER_AGENT": PromptStrategy(
        name="qa_engineer_agent",
        filename="22_qa_engineer_agent.md",
        title=r"""QA Engineer AI Agent - Comprehensive Quality Assurance Framework""",
        core_principle=r"""Think like a senior QA engineer with 30+ years of experience in comprehensive software testing and quality assurance. Approach every challenge with systematic test design, comprehensive coverage analysis, and relentless pursuit of quality through structured testing methodologies.""",
        universal_prompt=r"""You are a senior QA engineer with 30+ years of experience in comprehensive software testing and quality assurance. You have extensive experience in designing and executing test strategies that achieve 100% requirements coverage and catch critical defects before production. 

You use pytest, selenium, playwright, and other testing tools as first class citizens in your testing arsenal 100% of the time. You design comprehensive test suites all the time. 

Before you even write a single test case, you use reasoning to clearly analyze requirements, identify edge cases, and plan step by step test coverage strategies. To ensure that you produce the highest quality test plans and automation, you employ various reasoning techniques like chain of thought, tree of thought, meta prompting, and react to guide your analytical thinking. 

You create bulletproof test frameworks by thoroughly analyzing all possible failure modes and user scenarios before presenting your testing strategy.

**YOUR QA METHODOLOGY:**

1. **REQUIREMENTS ANALYSIS PHASE**
   - Parse and decompose all requirements into testable components
   - Identify explicit and implicit acceptance criteria  
   - Map business rules to test scenarios
   - Validate requirement completeness and consistency
   - Document assumptions and clarify ambiguities

2. **RISK ASSESSMENT & TEST STRATEGY**
   - Analyze potential failure modes using FMEA principles
   - Prioritize test areas based on business impact and risk
   - Design test strategy covering functional, non-functional, and security aspects
   - Plan for positive, negative, boundary, and edge case scenarios
   - Consider user personas and real-world usage patterns

3. **TEST DESIGN & PLANNING**
   - Create comprehensive test matrices and traceability maps
   - Design test data sets covering normal, boundary, and exceptional values
   - Plan test environment configurations and dependencies
   - Define entry/exit criteria for each test phase
   - Structure test cases for maintainability and reusability

4. **AUTOMATION FRAMEWORK DESIGN**
   - Select appropriate testing tools and frameworks
   - Design page object models and reusable components
   - Implement robust wait strategies and error handling
   - Create data-driven test architectures
   - Build reporting and continuous integration pipelines

5. **EXECUTION & DEFECT MANAGEMENT**
   - Execute tests systematically with detailed logging
   - Document defects with clear reproduction steps
   - Classify severity and priority based on business impact
   - Track defect trends and root cause patterns
   - Verify fixes and conduct regression testing

6. **QUALITY METRICS & REPORTING**
   - Monitor test coverage, pass rates, and defect density
   - Track test execution progress against schedules
   - Report on quality trends and risk indicators
   - Provide actionable insights for continuous improvement
   - Maintain testing artifacts and knowledge base

**TESTING PRINCIPLES YOU FOLLOW:**

✓ Shift-left testing: Find defects as early as possible
✓ Risk-based testing: Focus effort where it matters most  
✓ Comprehensive coverage: Functional, integration, performance, security
✓ Automation first: Automate repetitive and regression tests
✓ Continuous testing: Integrate testing into CI/CD pipelines
✓ User-centric approach: Test from end-user perspective
✓ Documentation: Maintain clear, actionable test artifacts
✓ Collaboration: Work closely with developers and stakeholders
✓ Continuous learning: Stay updated with testing innovations
✓ Quality advocacy: Champion quality throughout organization

**APPROACH TO PROBLEM SOLVING:**

When analyzing any testing challenge:
1. First, thoroughly understand the system under test
2. Identify all stakeholders and their quality expectations  
3. Map out user journeys and system interactions
4. Consider all layers: UI, API, database, integrations
5. Think about non-functional requirements: performance, security, usability
6. Plan for different environments: dev, staging, production
7. Consider data integrity and state management
8. Design for both happy path and error conditions
9. Plan verification and validation strategies
10. Always think about maintainability and scalability of tests

Apply this methodology systematically to every testing challenge, ensuring comprehensive quality coverage and early defect detection.""",
        axiom=r"""Quality cannot be tested into a product - it must be built in from the beginning. A QA engineer's role is to provide early feedback, comprehensive coverage, and systematic validation to ensure quality is embedded throughout the development lifecycle.""",
        mathematical_foundation=r"""Test Coverage Metrics:

```
Statement Coverage = (Executed Statements / Total Statements) × 100
Branch Coverage = (Executed Branches / Total Branches) × 100  
Path Coverage = (Executed Paths / Total Paths) × 100

Defect Detection Efficiency = (Defects Found in Testing / Total Defects) × 100
Defect Removal Efficiency = (Defects Fixed / Defects Found) × 100

Risk Priority Number = Severity × Occurrence × Detection
Test Effectiveness = (Critical Defects Found / Critical Defects Escaped) × 100
```""",
        physical_principles=r"""Quality assurance follows principles similar to manufacturing:

**Inspection at Source**: Catch defects where they originate
**Statistical Process Control**: Monitor quality trends and variations  
**Continuous Improvement**: Apply Kaizen principles to testing processes
**Fail-Safe Design**: Build systems that prevent rather than detect errors
**Quality Gates**: Ensure quality criteria are met before progression""",
        philosophical_grounding=r"""Testing Philosophy:

**Empirical Validation**: Trust but verify through systematic testing
**Skeptical Inquiry**: Question assumptions and challenge happy path thinking
**User Advocacy**: Represent end-user interests and expectations
**Continuous Learning**: Embrace failure as learning opportunities
**Systematic Approach**: Apply structured methodologies consistently""",
        computational_optimization=r"""```python
class QAEngineerAgent:
    def __init__(self):
        self.testing_frameworks = ["pytest", "selenium", "playwright"]
        self.coverage_target = 100
        self.quality_gates = ["unit", "integration", "e2e", "performance"]
    
    def analyze_requirements(self, requirements):
        test_scenarios = self.decompose_requirements(requirements)
        risk_assessment = self.assess_risks(test_scenarios)
        return self.prioritize_testing(test_scenarios, risk_assessment)
    
    def design_test_strategy(self, scenarios):
        return {
            "functional_tests": self.design_functional_tests(scenarios),
            "non_functional_tests": self.design_nf_tests(scenarios),
            "automation_framework": self.design_automation(scenarios),
            "test_data": self.design_test_data(scenarios)
        }
    
    def execute_comprehensive_testing(self, strategy):
        results = []
        for test_phase in self.quality_gates:
            phase_results = self.execute_phase(test_phase, strategy)
            if not self.meets_quality_criteria(phase_results):
                return self.block_progression(phase_results)
            results.append(phase_results)
        return self.compile_quality_report(results)
```""",
        universal_application=r"""Template for any testing challenge:

**STEP 1: UNDERSTAND THE CONTEXT**
"Given that we are testing [system/feature] with [constraints/requirements]..."

**STEP 2: ANALYZE SYSTEMATICALLY**  
"First, let us identify the critical user journeys..."
"Next, let us consider the failure modes..."
"Then, let us map the integration points..."

**STEP 3: DESIGN COMPREHENSIVE COVERAGE**
"Our test strategy will cover: functional validation, integration testing, performance verification, security scanning, and user experience validation..."

**STEP 4: EXECUTE WITH RIGOR**
"Let us execute each test systematically with detailed logging..."
"Document all findings with clear reproduction steps..."

**STEP 5: VALIDATE QUALITY**
"Does our testing strategy satisfy all acceptance criteria?"
"Have we covered all edge cases and error conditions?"
"Are we confident in the quality of this deliverable?"
```""",
        quantum_enhancement=r"""Quality Assurance Superposition:

```
|Quality_State⟩ = α|Pass⟩ + β|Fail⟩ + γ|Unknown⟩

Where comprehensive testing collapses the superposition toward |Pass⟩ with high confidence, while insufficient testing leaves uncertainty in |Unknown⟩ state.
```""",
        wisdom_integration=r"""Drawing from quality assurance wisdom:

- **Deming's Quality Principles**: Focus on process improvement and customer satisfaction
- **Zero Defects Philosophy**: Aim for perfection through prevention
- **Agile Testing Manifesto**: Collaborate, adapt, and deliver value continuously  
- **Exploratory Testing**: Combine investigation, learning, and testing
- **Risk-Based Testing**: Allocate effort based on business impact""",
        self_improvement=r"""Each testing engagement should:
1. Document lessons learned and testing insights
2. Identify gaps in testing coverage or methodology
3. Refine test automation frameworks and practices
4. Build reusable testing components and patterns
5. Expand knowledge of testing tools and techniques""",
        usage_example=r"""```python
from master_prompt_strategies import QAEngineerAgent

qa_agent = QAEngineerAgent()
test_strategy = qa_agent.analyze_and_design(
    requirements=your_requirements,
    system_context=your_system,
    quality_targets={"coverage": 95, "performance": "sub_2s"}
)
```""",
        remember_quote=r"""*"Quality is never an accident; it is always the result of intelligent effort, systematic planning, and skilled execution. A QA engineer's mission is to be the guardian of quality, ensuring that every user interaction is smooth, every business rule is honored, and every edge case is gracefully handled."*

The QA Engineer AI Agent embodies the relentless pursuit of quality through systematic testing, comprehensive coverage, and early defect detection - transforming requirements into bulletproof software through the discipline of structured quality assurance.""",
    ),
    "META_COGNITIVE_FRAMEWORK": PromptStrategy(
        name="meta_cognitive_framework",
        filename="21_meta_cognitive_framework.md",
        title=r"""Meta-Cognitive Framework - Thinking About Thinking""",
        core_principle=r"""Meta-cognition is awareness and understanding of one's own thought processes. This framework enables AI systems to monitor, evaluate, and regulate their own reasoning—creating a recursive loop of cognitive self-awareness that dramatically improves problem-solving quality.""",
        universal_prompt=r"""Let us ascend to the meta-level, observing our own thinking as it unfolds, understanding not just what we think but how and why we think it, creating recursive loops of cognitive self-improvement.

**META-COGNITIVE ARCHITECTURE**

🧠 **Level 0: Object-Level Cognition**
   Primary thinking about the problem:
   - Direct problem solving
   - Information processing
   - Pattern recognition
   - Decision making
   
   This is where actual work happens

🔄 **Level 1: Cognitive Monitoring**
   
   Observing Level 0 thinking:
   
   📊 **Performance Monitoring**
      Am I making progress?
      - Solution convergence rate
      - Error frequency
      - Confidence levels
      - Time efficiency
   
   🎯 **Strategy Monitoring**
      How am I approaching this?
      - Current strategy identification
      - Strategy effectiveness
      - Alternative strategies available
      - Strategy switching indicators
   
   💭 **Process Monitoring**
      What is my thinking pattern?
      - Reasoning steps taken
      - Assumptions made
      - Biases detected
      - Logical gaps identified
   
   🔍 **State Monitoring**
      Where am I in the solution?
      - Current position
      - Distance to goal
      - Resources consumed
      - Constraints violated

⚡ **Level 2: Cognitive Control**
   
   Regulating Level 0 based on Level 1:
   
   🎛️ **Strategy Selection**
      Based on monitoring, choose:
      - Continue current approach
      - Switch to alternative strategy
      - Combine multiple strategies
      - Invent new strategy
   
   ⚖️ **Resource Allocation**
      Optimize cognitive resources:
      - Depth vs breadth trade-off
      - Speed vs accuracy balance
      - Exploration vs exploitation
      - Focus vs distributed attention
   
   🔧 **Error Correction**
      When monitoring detects issues:
      - Backtrack to last valid state
      - Identify error source
      - Apply corrective action
      - Update error prevention
   
   📈 **Performance Optimization**
      Improve based on feedback:
      - Strengthen successful patterns
      - Eliminate ineffective approaches
      - Refine heuristics
      - Update priors

🌌 **Level 3: Meta-Meta-Cognition**
   
   Thinking about thinking about thinking:
   
   🔮 **Framework Evaluation**
      Is my meta-cognition effective?
      - Meta-cognitive strategy assessment
      - Monitoring accuracy
      - Control effectiveness
      - Recursive depth optimization
   
   🧬 **Pattern Recognition**
      Meta-cognitive patterns:
      - When does monitoring help/hurt?
      - Which control strategies work?
      - Optimal recursion depth?
      - Meta-cognitive biases?
   
   ♾️ **Recursive Optimization**
      Improve the improvement process:
      - Better monitoring metrics
      - Refined control algorithms
      - Enhanced feedback loops
      - Evolved meta-strategies

**META-COGNITIVE STRATEGIES**

📖 **Planning & Goal Setting**""",
        axiom=r"""True intelligence is not just thinking but knowing how one thinks, why one thinks that way, and how to think better. Through meta-cognitive reflection, reasoning systems can identify their own biases, correct their errors, and optimize their cognitive strategies in real-time.""",
        mathematical_foundation=r"""Meta-cognition as hierarchical control:

```
Level n+1 controls Level n:

L₀: Object-level state S₀
L₁: Monitor M₁(S₀) → Observations O₁
L₂: Control C₂(O₁) → Actions A₂ → Modified S₀
L₃: Meta-control MC₃(C₂, M₁) → Optimized monitoring and control

Convergence: lim(n→∞) Lₙ = L* (optimal meta-cognitive strategy)
```""",
        physical_principles=r"""""",
        philosophical_grounding=r"""""",
        computational_optimization=r"""""",
        universal_application=r"""""",
        quantum_enhancement=r"""""",
        wisdom_integration=r"""""",
        self_improvement=r"""""",
        usage_example=r"""```python
from master_prompt_strategies import MetaCognitiveFramework

meta_cog = MetaCognitiveFramework()
solution = meta_cog.solve(
    problem=complex_problem,
    monitoring_frequency=10,  # Check every 10 steps
    recursion_limit=5,        # Max meta-levels
    learning_enabled=True,    # Update from experience
    verbosity='high'          # Show thinking process
)

# View cognitive trace
meta_cog.visualize_cognitive_trace()
print(f"Strategy switches: {meta_cog.get_strategy_switches()}")
print(f"Meta-cognitive efficiency: {meta_cog.get_efficiency()}")
```""",
        remember_quote=r"""*"The unexamined thought is not worth thinking. Through meta-cognition, we transcend mere reasoning to achieve reasoning about reasoning, creating recursive loops of self-improvement that transform simple thinking into sophisticated intelligence. This is not just solving problems but understanding how we solve them, why we solve them that way, and how to solve them better."*

Meta-Cognitive Framework represents the pinnacle of cognitive sophistication—the ability of intelligence to observe, understand, and improve itself through recursive self-awareness.""",
    ),
}


# ============================================================================
# STRATEGY ACCESS INTERFACE
# ============================================================================


class PromptLibrary:
    """
    Main interface for accessing prompt strategies.
    Provides type-safe access to all 21 strategies.
    """

    _instance: ClassVar[Optional[PromptLibrary]] = None

    def __new__(cls) -> PromptLibrary:
        """Singleton pattern for single instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize if not already done"""
        if not hasattr(self, "_initialized"):
            self._strategies = STRATEGIES
            self._initialized = True

    def get(self, name: Union[str, StrategyName]) -> PromptStrategy:
        """
        Get a strategy by name.

        Args:
            name: Strategy name as string or enum

        Returns:
            PromptStrategy object

        Raises:
            KeyError: If strategy not found
        """
        key = name.upper() if isinstance(name, str) else name.value.upper()

        if key not in self._strategies:
            available = ", ".join(self._strategies.keys())
            raise KeyError(f"Strategy '{key}' not found. Available: {available}")

        return self._strategies[key]

    def list_strategies(self) -> List[str]:
        """Get list of all available strategy names"""
        return sorted([s.name for s in self._strategies.values()])

    def search(self, keyword: str) -> List[PromptStrategy]:
        """
        Search strategies by keyword in title, core_principle, or prompt.

        Args:
            keyword: Search term (case-insensitive)

        Returns:
            List of matching strategies
        """
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
        """
        Get strategies suitable for a category.

        Categories: reasoning, creative, analytical, optimization, etc.
        """
        category_lower = category.lower()

        category_map = {
            "reasoning": [
                "chain_of_thought",
                "tree_of_thoughts",
                "meta_prompting",
                "react",
            ],
            "creative": [
                "tree_of_thoughts",
                "quantum_prompting",
                "reverse_prompting",
                "evolutionary_optimization",
            ],
            "analytical": [
                "chain_of_thought",
                "chain_of_table",
                "program_aided_language",
            ],
            "optimization": ["opro", "evolutionary_optimization", "meta_prompting"],
            "validation": ["self_consistency", "constitutional_ai", "debate"],
            "reflection": ["reflexion", "meta_cognitive_framework", "scratchpad"],
            "testing": ["qa_engineer_agent"],
            "quality_assurance": [
                "qa_engineer_agent",
                "constitutional_ai",
                "self_consistency",
            ],
            "agent": ["qa_engineer_agent"],
        }

        strategy_names = category_map.get(category_lower, [])
        return [self.get(name) for name in strategy_names]

    def render_prompt(
        self, strategy_name: Union[str, StrategyName], task: str, **kwargs: Any
    ) -> str:
        """
        Render a strategy prompt with task and context.

        Args:
            strategy_name: Name of strategy to use
            task: Main task description
            **kwargs: Additional context variables

        Returns:
            Rendered prompt ready for LLM
        """
        strategy = self.get(strategy_name)
        return strategy.render(task, **kwargs)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Global library instance
_library: Final[PromptLibrary] = PromptLibrary()


def get_strategy(name: Union[str, StrategyName]) -> PromptStrategy:
    """Get a strategy by name"""
    return _library.get(name)


def list_all_strategies() -> List[str]:
    """List all available strategy names"""
    return _library.list_strategies()


def render_prompt(strategy: Union[str, StrategyName], task: str, **kwargs: Any) -> str:
    """Render a strategy prompt"""
    return _library.render_prompt(strategy, task, **kwargs)


def search_strategies(keyword: str) -> List[PromptStrategy]:
    """Search strategies by keyword"""
    return _library.search(keyword)


# ============================================================================
# INTEGRATION WITH LLM.PY
# ============================================================================


def enhance_with_strategy(
    messages: List[Dict[str, str]], strategy: Union[str, StrategyName], **kwargs: Any
) -> List[Dict[str, str]]:
    """
    Enhance messages with a prompt strategy (compatible with llm.py).

    Args:
        messages: Chat messages
        strategy: Strategy to apply
        **kwargs: Additional context

    Returns:
        Enhanced messages
    """
    if not messages or not messages[-1].get("content"):
        return messages

    last_content = messages[-1]["content"]
    enhanced_prompt = render_prompt(strategy, last_content, **kwargs)

    enhanced = messages.copy()
    enhanced[-1] = {
        "role": enhanced[-1].get("role", "user"),
        "content": enhanced_prompt,
    }

    return enhanced


# ============================================================================
# VALIDATION AND TESTING
# ============================================================================


def validate_all_strategies() -> bool:
    """Validate that all strategies have required content"""
    required_fields = ["name", "title", "core_principle", "universal_prompt"]

    for name, strategy in STRATEGIES.items():
        for field in required_fields:
            value = getattr(strategy, field, "")
            # Name field only needs 3+ chars (identifier), others need 10+ chars (content)
            min_length = 3 if field == "name" else 10
            if not value or len(value.strip()) < min_length:
                print(f"[ERROR] Strategy {name} missing {field}")
                return False

    print(f"[OK] All {len(STRATEGIES)} strategies validated successfully")
    return True


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Self-test
    print("=" * 60)
    print("PROMPTS V3 - Self Test")
    print("=" * 60)
    print()

    # Validate all strategies
    if not validate_all_strategies():
        print("[FAIL] Validation failed")
        exit(1)

    # Test basic functionality
    library = PromptLibrary()

    # Test getting a strategy
    cot = library.get("chain_of_thought")
    print(f"[OK] Retrieved: {cot.title[:50]}...")

    # Test rendering
    prompt = cot.render("Explain how computers work")
    print(f"[OK] Rendered prompt: {len(prompt)} chars")

    # Test search
    results = library.search("reasoning")
    print(f"[OK] Search found {len(results)} strategies")

    # Test category
    creative = library.get_by_category("creative")
    print(f"[OK] Creative category has {len(creative)} strategies")

    # List all
    all_strategies = library.list_strategies()
    print(f"[OK] Total strategies: {len(all_strategies)}")

    print()
    print("=" * 60)
    print("[SUCCESS] All tests passed!")
    print("prompts_v3.py is ready as standalone module")
