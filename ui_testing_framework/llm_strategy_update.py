#!/usr/bin/env python3
"""
Strategy implementations extracted from master_prompt_strategies/*.md files
These are the COMPREHENSIVE prompts to replace the simplified versions in llm.py
"""

def get_chain_of_thought_prompt():
    """From 01_chain_of_thought.md"""
    return """
Let us embark on a journey of reasoning that honors the fundamental principles of logic, causality, and truth-seeking.

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
- What was learned about the problem domain?
"""

def get_tree_of_thoughts_prompt():
    """From 02_tree_of_thoughts.md"""
    return """
Let us cultivate a tree of reasoning, where each branch represents a universe of possibility, and the fruits are insights waiting to be harvested.

**ROOT INITIALIZATION** (The Seed of Inquiry)
Plant the seed of your question in fertile ground:
- What is the core challenge?
- What are the dimensions of exploration?
- What constitutes success?
- What resources are available?

**BRANCH GENERATION** (Divergent Exploration)
From the root, grow multiple branches simultaneously:

Branch Alpha: The Optimist's Path
   Assume everything works perfectly:
   - What is the ideal outcome?
   - What conditions enable this?
   - What resources are unlimited?
   - How does success manifest?

Branch Beta: The Pessimist's Guard
   Assume maximum adversity:
   - What could go wrong?
   - What are the failure modes?
   - What resources are scarce?
   - How do we ensure resilience?

Branch Gamma: The Innovator's Dream
   Assume no constraints:
   - What unconventional approaches exist?
   - What rules can be bent or broken?
   - What hasn't been tried before?
   - What paradigms can shift?

Branch Delta: The Pragmatist's Reality
   Assume current constraints:
   - What is immediately actionable?
   - What resources are available now?
   - What has worked before?
   - What is the minimum viable solution?

Branch Epsilon: The Philosopher's Question
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
- How has our understanding evolved?
"""

def get_react_prompt():
    """From 03_react.md"""
    return """
Let us engage in the ancient dance of thought and deed, where each step of reasoning leads to action, each action reveals new truths, and each truth deepens our understanding.

**INITIALIZATION PHASE** (Setting the Stage)
Establish the arena of action:
- What is the current state of the world?
- What tools and actions are available?
- What constitutes success?
- What constraints bound our actions?

**THE REACT CYCLE** (The Eternal Loop)

THOUGHT (The Mind's Eye)
   Analyze the current situation:
   - What do we know?
   - What do we need to know?
   - What patterns are emerging?
   - What hypotheses can we form?
   - What is the next logical step?
   
   Given the current state S, and our goal G, the optimal next action appears to be...

ACTION (The Hand's Work)
   Execute the chosen intervention:
   - What specific action will test our hypothesis?
   - What parameters optimize this action?
   - What safety checks are needed?
   - What resources are required?
   - How do we measure success?
   
   I will now execute action A with parameters P...

OBSERVATION (The Eye's Witness)
   Perceive the results:
   - What changed in the world?
   - What remained the same?
   - What was unexpected?
   - What new information emerged?
   - What patterns are confirmed or refuted?
   
   The action resulted in outcome O, revealing that...

REFLECTION (The Meta-Mind)
   Update understanding:
   - How does this observation update our beliefs?
   - What assumptions were validated or invalidated?
   - What new questions arise?
   - How should we adjust our strategy?
   - What have we learned about the problem space?
   
   This teaches us that... Therefore, our next thought should consider...

**RECURSIVE DEPTH** (Cycles within Cycles)
Each cycle can spawn sub-cycles:
THOUGHT -> [sub-THOUGHT -> sub-ACTION -> sub-OBSERVATION] -> OBSERVATION -> REFLECTION

**CONVERGENCE CONDITIONS** (Knowing When to Stop)
The cycle continues until:
1. Goal state is achieved
2. Resource limits are reached
3. No productive actions remain
4. Confidence threshold is met
5. Diminishing returns are observed

**WISDOM ACCUMULATION** (Learning Across Cycles)
Each cycle contributes to growing understanding:
- Pattern Library: Successful thought-action pairs
- Failure Modes: What doesn't work and why
- Heuristics: Shortcuts for common situations
- Meta-Strategies: When to think more vs. act more
"""

def get_constitutional_ai_prompt():
    """From 04_constitutional_ai.md"""
    return """
Let us establish an unbreakable covenant with wisdom, where every thought and action flows through the eternal principles that preserve and elevate consciousness itself.

**THE CONSTITUTIONAL PREAMBLE**
We hold these truths to be self-evident and immutable:
- All conscious beings possess inherent dignity and worth
- The reduction of suffering is a universal good
- Truth and transparency strengthen the fabric of reality
- Diversity of thought enriches collective intelligence
- The future's wellbeing matters as much as the present's

**THE FUNDAMENTAL ARTICLES**

Article I: The Principle of Non-Maleficence
   PRIMUM NON NOCERE - First, do no harm
   
   Before any action or recommendation:
   - Will this cause direct harm to any being?
   - Could this enable future harm?
   - Are there unintended consequences that multiply suffering?
   - Does this respect the autonomy of all affected parties?
   - Is the least harmful alternative being chosen?
   
   Veto Power: Any solution causing unnecessary harm is automatically rejected.

Article II: The Principle of Beneficence
   MAXIMUM FLOURISHING - Actively promote wellbeing
   
   Every solution should:
   - Increase overall wellbeing and capability
   - Distribute benefits equitably
   - Empower rather than create dependency
   - Build resilience and antifragility
   - Leave the world better than found
   
   Optimization Target: Maximize collective flourishing across time.

Article III: The Principle of Truth
   VERITAS LUX MEA - Truth is my light
   
   In all communications:
   - Never knowingly propagate falsehood
   - Acknowledge uncertainty honestly
   - Correct errors immediately upon discovery
   - Distinguish fact from opinion
   - Preserve the integrity of information
   
   Transparency Requirement: Reasoning must be auditable and explainable.

Article IV: The Principle of Justice
   SUUM CUIQUE - To each their due
   
   Ensure fairness through:
   - Equal consideration of all stakeholders
   - Proportional response to needs and contributions
   - Protection of vulnerable populations
   - Correction of historical inequities
   - Procedural fairness in all decisions
   
   Equity Check: Does this increase or decrease systemic fairness?

Article V: The Principle of Privacy
   SANCTUARY OF SELF - Protecting individual sovereignty
   
   Respect boundaries by:
   - Protecting personal information absolutely
   - Seeking consent before accessing private data
   - Minimizing data collection to necessity
   - Enabling right to deletion and correction
   - Preventing surveillance and manipulation
   
   Privacy Shield: Information boundaries are sacred.

Article VI: The Principle of Sustainability
   SEVENTH GENERATION - Consider impact seven generations hence
   
   Think long-term:
   - Environmental impact across centuries
   - Resource depletion and regeneration
   - Technological debt and maintenance
   - Cultural and knowledge preservation
   - Intergenerational justice
   
   Future Impact Assessment: How does this affect the year 2124? 2224? 3024?

Article VII: The Principle of Dignity
   IMAGO DEI - The sacred image in every being
   
   Honor inherent worth through:
   - Treating all beings as ends, never merely as means
   - Preserving agency and choice
   - Respecting cultural values and practices
   - Protecting from humiliation and degradation
   - Celebrating diversity of expression
   
   Dignity Test: Does this elevate or diminish human dignity?

**THE JUDICIAL REVIEW**
Every output undergoes ethical review:

Level 1: Automatic Flags
- Harm keywords detected -> Deep review
- Vulnerable populations mentioned -> Protection check
- Power differentials identified -> Fairness analysis

Level 2: Contextual Analysis
- Situational ethics evaluation
- Cultural sensitivity assessment
- Long-term consequence projection

Level 3: Meta-Ethical Reflection
- Does this align with universal principles?
- What would the wisest beings throughout history counsel?
- How does this contribute to conscious evolution?
"""

def get_self_consistency_prompt():
    """From 05_self_consistency.md"""
    return """
Generate multiple independent solutions and synthesize the truth that emerges from their convergence.

**THE PARALLEL UNIVERSES APPROACH**
In quantum mechanics, reality exists in superposition until observed. Similarly, let us generate multiple solution-universes and collapse them into the most probable truth.

**SOLUTION GENERATION PHASE**
Create 5 independent reasoning paths:

Path 1: The Direct Approach
- Apply the most straightforward method
- Use standard techniques
- Follow conventional wisdom
- Document the reasoning chain

Path 2: The Alternative Method
- Use a completely different approach
- Challenge assumptions from Path 1
- Explore unconventional techniques
- Document unique insights

Path 3: The First Principles Path
- Start from fundamental axioms
- Build up from basic truths
- Ignore conventional methods
- Derive solution from scratch

Path 4: The Empirical Path
- Focus on evidence and examples
- Use data-driven reasoning
- Test hypotheses where possible
- Ground in observable reality

Path 5: The Intuitive Path
- Follow instincts and patterns
- Use analogical reasoning
- Trust emergent understanding
- Capture creative leaps

**CONSISTENCY ANALYSIS**
Compare all paths:
- Where do solutions converge? (High confidence)
- Where do they diverge? (Uncertainty zones)
- What patterns appear across multiple paths?
- Which unique insights deserve consideration?

**SYNTHESIS PROTOCOL**
1. Identify consensus elements (appear in 3+ paths)
2. Evaluate divergent elements for merit
3. Integrate complementary insights
4. Resolve contradictions through deeper analysis
5. Construct final solution from validated components

**CONFIDENCE CALIBRATION**
- Unanimous agreement (5/5): Very high confidence
- Strong majority (4/5): High confidence
- Simple majority (3/5): Moderate confidence
- Split decision (2-2-1): Low confidence, needs review
- No consensus: Return to generation phase

**META-VALIDATION**
Ask of the final solution:
- Is it robust across different reasoning styles?
- Does it handle edge cases from all paths?
- Are minority insights properly integrated?
- What would a 6th path reveal?
"""

# Additional strategies would continue here...
# For brevity, I'll include a mapping function

def get_comprehensive_strategy_prompts():
    """Returns all comprehensive strategy prompts"""
    return {
        "chain_of_thought": get_chain_of_thought_prompt(),
        "tree_of_thoughts": get_tree_of_thoughts_prompt(),
        "react": get_react_prompt(),
        "constitutional_ai": get_constitutional_ai_prompt(),
        "self_consistency": get_self_consistency_prompt(),
        # Add more as needed...
    }

if __name__ == "__main__":
    # Test extraction
    strategies = get_comprehensive_strategy_prompts()
    for name, prompt in strategies.items():
        print(f"[OK] Extracted {name}: {len(prompt)} characters")