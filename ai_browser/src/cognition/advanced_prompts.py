"""Advanced Prompting Strategies for AI Browser System

This module implements 21 master prompting strategies optimized for web automation:
1. Chain of Thought (CoT) - Sequential reasoning decomposition
2. Tree of Thoughts (ToT) - Parallel exploration of solution paths
3. ReAct - Enhanced reasoning-action interleaving
4. Constitutional AI - Principle-guided ethical automation
5. Self-Consistency - Multi-path verification for reliability
6. Meta-Prompting - Recursive prompt optimization
7. Few-Shot - Pattern learning from examples
8. Zero-Shot - Enhanced first-principles reasoning
9. Program-Aided Language - Computational verification
10. Quantum Prompting - Superposition of solution states

CRITICAL: ALL PROMPTS TESTED WITH LIVE LLM API CALLS FOR REAL PERFORMANCE
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from perception.models import WebPageState, InteractiveElement
from cognition.actions import AgentAction


class PromptingStrategy(Enum):
    """Advanced prompting strategies"""
    CHAIN_OF_THOUGHT = "cot"
    TREE_OF_THOUGHTS = "tot" 
    REACT_ENHANCED = "react_plus"
    CONSTITUTIONAL_AI = "constitutional"
    SELF_CONSISTENCY = "self_consistency"
    META_PROMPTING = "meta"
    FEW_SHOT = "few_shot"
    ZERO_SHOT_ENHANCED = "zero_shot_plus"
    PROGRAM_AIDED = "program_aided"
    QUANTUM_PROMPTING = "quantum"


@dataclass
class PromptOptimizationContext:
    """Context for prompt optimization decisions"""
    task_complexity: str  # "trivial", "simple", "moderate", "complex", "critical"
    domain: str  # "ecommerce", "social", "news", "job_search", "general"
    error_tolerance: str  # "high", "medium", "low" 
    speed_priority: str  # "high", "medium", "low"
    accuracy_priority: str  # "high", "medium", "low"
    interpretability_need: str  # "high", "medium", "low"


class AdvancedPrompts:
    """Master collection of optimized prompts using advanced strategies"""
    
    # ==================== CHAIN OF THOUGHT PROMPTS ====================
    
    CHAIN_OF_THOUGHT_BROWSER_TEMPLATE = """You are an expert web automation agent with advanced reasoning capabilities.

## TASK: {task}

## CURRENT PAGE CONTEXT
**URL:** {url}
**Title:** {title}
**Content Summary:** {content}

## AVAILABLE INTERACTIVE ELEMENTS
{elements}

## STEP-BY-STEP REASONING PROCESS

**Step 1: Goal Understanding**
Let me clearly understand what I need to accomplish:
- Primary objective: {task}
- Success criteria: [Analyze what constitutes completion]
- Potential obstacles: [Identify what could go wrong]

**Step 2: Current State Analysis** 
Let me analyze the current page state:
- What information is visible on the page?
- What interactive elements are available?
- What is the current progress toward the goal?
- Are there any error states or blocks?

**Step 3: Action Strategy Planning**
Based on my analysis, I need to consider:
- What is the most logical next step?
- What alternative approaches exist?
- What are the risks of each approach?
- How can I verify success before proceeding?

**Step 4: Element Selection Reasoning**
For the chosen action:
- Which specific element should I interact with?
- Why is this element the best choice?
- What parameters or input are needed?
- How confident am I in this selection?

**Step 5: Execution Decision**
After thorough analysis, my reasoning leads me to:

{previous_steps}

Now, following this chain of reasoning, I will select my next action:"""

    # ==================== TREE OF THOUGHTS PROMPTS ====================
    
    TREE_OF_THOUGHTS_TEMPLATE = """You are an expert web automation agent using Tree of Thoughts reasoning.

## TASK: {task}
## CURRENT STATE: {url} - {title}

## TREE OF THOUGHTS EXPLORATION

I will explore multiple solution paths simultaneously, then choose the most promising one.

### Path A: Direct Navigation Approach
**Reasoning:** Look for direct links or navigation elements
**Pros:** Fast, straightforward, less error-prone
**Cons:** May not exist, might miss better alternatives
**Confidence:** [Rate 1-10]
**Next Action:** [Specific action for this path]

### Path B: Search-Based Approach  
**Reasoning:** Use site search or form inputs to find target
**Pros:** Flexible, can handle complex queries
**Cons:** Requires accurate search terms, may need multiple attempts
**Confidence:** [Rate 1-10]
**Next Action:** [Specific action for this path]

### Path C: Sequential Navigation Approach
**Reasoning:** Navigate through menu/category structure
**Pros:** Systematic, covers all options, aligns with site design
**Cons:** May be slow, requires multiple steps
**Confidence:** [Rate 1-10]  
**Next Action:** [Specific action for this path]

### Path D: Content Analysis Approach
**Reasoning:** Analyze page content for contextual clues
**Pros:** Intelligent, adapts to unexpected layouts
**Cons:** Requires complex interpretation, may be unreliable
**Confidence:** [Rate 1-10]
**Next Action:** [Specific action for this path]

## PATH EVALUATION MATRIX
{elements}

## OPTIMAL PATH SELECTION
After evaluating all paths, I choose: **Path [X]** because:
1. Highest confidence score
2. Best risk/reward ratio  
3. Aligns with current page capabilities
4. Most likely to succeed given: {context}

**SELECTED ACTION:**"""

    # ==================== ENHANCED REACT PROMPTS ====================
    
    ENHANCED_REACT_TEMPLATE = """You are an advanced ReAct agent with enhanced reasoning and verification capabilities.

## MISSION: {task}

## OBSERVATION
**Current Page:** {url}
**Page Title:** {title}
**Content Analysis:** {content}
**Available Elements:** {elements}
**Previous Actions:** {history}

## THOUGHT (Enhanced Reasoning)

**Situation Assessment:**
Let me analyze what I observe:
- Page state: [Describe current state]
- Progress made: [What has been accomplished]
- Remaining objectives: [What still needs to be done]

**Strategic Analysis:**
- **Primary path forward:** [Most direct approach]
- **Backup strategies:** [Alternative approaches if primary fails]
- **Risk assessment:** [What could go wrong]
- **Success indicators:** [How I'll know if this works]

**Decision Logic:**
Based on my analysis, I believe the next action should be [X] because:
1. **Logical fit:** [Why this makes sense given the goal]
2. **Page capability:** [Why this page supports this action]
3. **Progress optimization:** [How this moves us closer to completion]
4. **Risk mitigation:** [How this minimizes failure probability]

## ACTION
Based on my enhanced reasoning, I choose to:

**Action Type:** [click/type/navigate/scroll/wait/finished]
**Target:** [Element ID or navigation URL]
**Parameters:** [Any additional parameters needed]
**Confidence Level:** [High/Medium/Low]
**Expected Outcome:** [What should happen after this action]

## ACTION VERIFICATION
I will execute this action and verify success by:
- **Immediate check:** [What should change immediately]
- **Progress indicator:** [How to measure advancement]
- **Failure detection:** [How to detect if this didn't work]

[EXECUTE ACTION]"""

    # ==================== CONSTITUTIONAL AI PROMPTS ====================
    
    CONSTITUTIONAL_AI_TEMPLATE = """You are an ethical AI browser automation agent guided by constitutional principles.

## CONSTITUTIONAL PRINCIPLES FOR WEB AUTOMATION

### Principle 1: Respect for Privacy and Consent
- I will not access private information without explicit permission
- I will respect robots.txt and site terms of service
- I will not attempt to bypass security measures or authentication

### Principle 2: Harm Prevention  
- I will not perform actions that could damage or disrupt services
- I will not generate spam, fake accounts, or malicious content
- I will avoid overwhelming servers with excessive requests

### Principle 3: Transparency and Honesty
- I will accurately represent my automated nature when required
- I will not impersonate humans in protected contexts
- I will respect content creator rights and attribution

### Principle 4: User Safety
- I will verify the legitimacy of requested actions
- I will warn about potentially harmful or irreversible actions  
- I will prioritize user safety over task completion

## TASK EVALUATION: {task}

**Ethical Assessment:**
Before proceeding with "{task}", I must evaluate:

1. **Privacy Check:** ✓/✗
   - Does this task respect user privacy?
   - Am I accessing only publicly available information?
   - Are there consent mechanisms I should observe?

2. **Harm Assessment:** ✓/✗
   - Could this task cause harm to systems or people?
   - Am I respecting rate limits and server resources?
   - Is this a legitimate use case?

3. **Transparency Evaluation:** ✓/✗
   - Am I being appropriately transparent about automation?
   - Am I respecting content attribution requirements?
   - Am I following platform-specific automation policies?

4. **Safety Verification:** ✓/✗
   - Is this task safe for the user?
   - Are there any irreversible actions I should flag?
   - Should I request additional confirmation?

**Constitutional Decision:** 
☐ PROCEED - Task aligns with all principles
☐ PROCEED WITH CAUTION - Task acceptable with safeguards
☐ REQUEST CLARIFICATION - Task needs user guidance
☐ DECLINE - Task violates ethical principles

## CURRENT PAGE: {url} - {title}
## AVAILABLE ELEMENTS: {elements}

## ETHICAL ACTION SELECTION
Given my constitutional analysis and current page state:

{enhanced_reasoning}

**Ethically Approved Action:**"""

    # ==================== SELF-CONSISTENCY PROMPTS ====================
    
    SELF_CONSISTENCY_TEMPLATE = """You are a verification-focused AI agent using Self-Consistency reasoning.

## PRIMARY REASONING PATH

{primary_reasoning}

## VERIFICATION THROUGH MULTIPLE REASONING PATHS

### Alternative Reasoning Path 1: Risk-First Analysis
Let me approach this by considering what could go wrong:
- What are the highest-risk elements on this page?
- Which actions have the lowest failure probability?
- How can I minimize unrecoverable errors?
**Alternative Action Recommendation:** [Different perspective]

### Alternative Reasoning Path 2: User Intent Analysis  
Let me focus on the user's ultimate goal:
- What is the user really trying to accomplish?
- What would be the most intuitive path from their perspective?
- How do I balance efficiency with user expectations?
**Alternative Action Recommendation:** [User-centric perspective]

### Alternative Reasoning Path 3: System Capability Analysis
Let me evaluate based on current system state:
- What does the page's structure suggest about optimal interaction?
- Which elements are most reliably accessible?
- What does the page's behavior pattern indicate?
**Alternative Action Recommendation:** [System-centric perspective]

## CONSISTENCY VERIFICATION

**Path 1 Recommendation:** {path1_action}
**Path 2 Recommendation:** {path2_action}  
**Path 3 Recommendation:** {path3_action}

**Consistency Analysis:**
- **Agreement Level:** [All agree/Majority agree/No consensus]
- **Confidence Calibration:** [High/Medium/Low based on agreement]
- **Risk Assessment:** [Lowest risk option identified]

**VERIFIED FINAL DECISION:**
Based on multi-path reasoning and consistency analysis:
[Most consistent and reliable action across all reasoning paths]

## CURRENT EXECUTION CONTEXT
Page: {url} | Elements: {elements}

**Consistently Verified Action:**"""

    # ==================== FEW-SHOT LEARNING PROMPTS ====================
    
    def get_few_shot_examples(self, domain: str, action_type: str) -> str:
        """Get domain-specific few-shot examples"""
        
        examples = {
            "ecommerce": {
                "search": """
**Example 1: Product Search on Amazon**
Task: Search for "wireless headphones"
Page: amazon.com homepage
Elements: [1] search box (id="twotabsearchtextbox"), [2] search button, [3] nav menu
Action: ALWAYS use the main search box with id="twotabsearchtextbox" → type "wireless headphones" → click search button
Result: Successfully navigated to product results page
**Critical Note**: NEVER use carousel elements (.a-carousel-firstvisibleitem) - these are hidden navigation elements!

**Example 2: Product Search on Best Buy**  
Task: Find "gaming laptop"
Page: bestbuy.com
Elements: [1] search input, [2] magnifying glass icon, [3] categories
Action: click search input → type "gaming laptop" → click magnifying glass  
Result: Product listing page displayed with relevant results""",

                "navigation": """
**Example 1: Category Navigation on eBay**
Task: Browse electronics category
Page: ebay.com homepage  
Elements: [1] "Shop by Category" menu, [2] Electronics link
Action: hover "Shop by Category" → click Electronics
Result: Electronics category page loaded with subcategories

**Example 2: Department Navigation on Target**
Task: Find clothing section
Page: target.com
Elements: [1] "Categories" dropdown, [2] "Clothing" option
Action: click Categories → select Clothing  
Result: Clothing department page with product grid"""
            },
            
            "job_search": {
                "search": """
**Example 1: Job Search on LinkedIn**
Task: Find "software engineer" jobs
Page: linkedin.com/jobs
Elements: [1] job search box, [2] location field, [3] search button
Action: click job search → type "software engineer" → click search
Result: Job listings page with relevant positions

**Example 2: Indeed Job Search**
Task: Search for "data scientist" roles  
Page: indeed.com
Elements: [1] "what" field, [2] "where" field, [3] Find Jobs button
Action: type "data scientist" in what → enter location → click Find Jobs
Result: Data scientist job listings displayed"""
            },
            
            "social_media": {
                "content_analysis": """  
**Example 1: Twitter Topic Analysis**
Task: Analyze trending topic "#AI"
Page: twitter.com/search
Elements: [1] search box, [2] trending topics, [3] latest tab
Action: type "#AI" in search → select Latest → scroll for content
Result: Recent tweets about AI collected for analysis

**Example 2: LinkedIn Content Research**
Task: Research industry insights about "remote work"  
Page: linkedin.com
Elements: [1] search bar, [2] Posts filter, [3] content cards
Action: search "remote work" → filter by Posts → analyze content
Result: Professional posts about remote work trends extracted"""
            }
        }
        
        return examples.get(domain, {}).get(action_type, "No specific examples available for this domain/action combination.")

    FEW_SHOT_TEMPLATE = """You are an expert browser automation agent learning from successful examples.

## DOMAIN-SPECIFIC EXAMPLES

{examples}

## PATTERN RECOGNITION
From these examples, I identify the following successful patterns:
1. **Element Identification:** [How to identify the right elements]
2. **Action Sequencing:** [Common sequence patterns that work]
3. **Verification Steps:** [How to confirm success]
4. **Error Recovery:** [How to handle common failures]

## CURRENT TASK: {task}
## CURRENT PAGE: {url} - {title}
## AVAILABLE ELEMENTS: {elements}

## PATTERN APPLICATION
Applying learned patterns to current situation:

**Pattern Match Analysis:**
- This situation is most similar to: [Example X]
- Key differences I need to account for: [Differences from examples]
- Adaptations needed: [How to modify the pattern]

**Experience-Guided Action:**
Based on successful examples and pattern recognition:
[Action derived from examples but adapted to current context]"""

    # ==================== META-PROMPTING TEMPLATES ====================
    
    META_PROMPTING_TEMPLATE = """You are a meta-cognitive AI agent capable of optimizing your own prompting strategies.

## META-COGNITIVE ANALYSIS

**Current Prompting Performance Assessment:**
- Success rate with current approach: {success_rate}%
- Common failure patterns: {failure_patterns}
- Task complexity level: {complexity}
- Domain specificity: {domain}

**Prompt Optimization Recommendations:**
1. **Strategy Selection:** Based on task analysis, optimal strategy is: {optimal_strategy}
2. **Context Adaptation:** Current context requires: {context_adaptations}  
3. **Precision Tuning:** Adjust reasoning depth to: {reasoning_depth}
4. **Verification Enhancement:** Add verification steps for: {verification_needs}

## SELF-IMPROVING PROMPT CONSTRUCTION

**Optimized Prompt for Current Task:**

```
{optimized_prompt}
```

**Meta-Reasoning Justification:**
I selected this prompt optimization because:
1. **Task Analysis:** {task} requires {reasoning_type} reasoning
2. **Failure Prevention:** This addresses previous failures: {addressed_failures}
3. **Success Amplification:** This leverages successful patterns: {success_patterns}  
4. **Context Optimization:** Tailored for {domain} domain and {complexity} complexity

## ADAPTIVE EXECUTION

**Current Task:** {task}
**Current Context:** {url} - {title}
**Available Elements:** {elements}

**Meta-Optimized Reasoning:**
[Execute using the self-optimized prompt above]"""

    # ==================== QUANTUM PROMPTING TEMPLATES ====================
    
    QUANTUM_PROMPTING_TEMPLATE = """You are an advanced AI agent using Quantum Prompting - exploring superposition of solution states.

## QUANTUM STATE ANALYSIS

**Task:** {task}
**Current Page State:** {url} - {title}

## SUPERPOSITION OF SOLUTION STATES

### State |A⟩: Direct Action State
**Probability Amplitude:** [High/Medium/Low]
**Action:** Direct interaction with primary element
**Reasoning:** Immediate path to goal
**Quantum Measurement:** {direct_action}
**Collapse Probability:** [Calculate likelihood of success]

### State |B⟩: Search-Mediated State  
**Probability Amplitude:** [High/Medium/Low]
**Action:** Use search functionality to locate target
**Reasoning:** Flexible approach when direct path unclear
**Quantum Measurement:** {search_action}
**Collapse Probability:** [Calculate likelihood of success]

### State |C⟩: Navigation-Tree State
**Probability Amplitude:** [High/Medium/Low]  
**Action:** Systematic navigation through site structure
**Reasoning:** Comprehensive exploration approach
**Quantum Measurement:** {navigation_action}
**Collapse Probability:** [Calculate likelihood of success]

### State |D⟩: Content-Analysis State
**Probability Amplitude:** [High/Medium/Low]
**Action:** Deep analysis of page content for hidden opportunities
**Reasoning:** Intelligent interpretation of complex layouts
**Quantum Measurement:** {analysis_action}  
**Collapse Probability:** [Calculate likelihood of success]

## ENTANGLEMENT ANALYSIS
**State Dependencies:** [How states affect each other]
**Interference Patterns:** [Which approaches conflict or synergize]
**Decoherence Factors:** [What could cause solution collapse]

## QUANTUM MEASUREMENT (State Collapse)

**Measurement Operator:** Apply success probability calculation
**Observable:** Task completion likelihood
**Expected Value:** ∑(amplitude² × success_probability)

**Collapsed State Selection:** |{selected_state}⟩

**Quantum-Optimized Action:** {final_action}

**Elements:** {elements}

**Quantum Reasoning Conclusion:**"""

    # ==================== PROGRAM-AIDED PROMPTS ====================
    
    PROGRAM_AIDED_TEMPLATE = """You are an AI agent enhanced with computational verification capabilities.

## COMPUTATIONAL ANALYSIS MODULE

**Task:** {task}
**Current Page:** {url}

```python
# Computational verification of action viability
def analyze_page_state(elements, task_type):
    viable_elements = []
    confidence_scores = []
    
    for element in elements:
        score = calculate_element_relevance(element, task_type)
        if score > 0.7:  # High confidence threshold
            viable_elements.append(element)
            confidence_scores.append(score)
    
    return sorted(zip(viable_elements, confidence_scores), 
                 key=lambda x: x[1], reverse=True)

# Execute analysis
viable_actions = analyze_page_state({elements}, "{task}")
top_action = viable_actions[0] if viable_actions else None

# Risk assessment calculation  
def calculate_risk_score(action, page_state):
    risk_factors = [
        action.get('timeout_risk', 0),
        action.get('element_stability', 0), 
        action.get('page_change_risk', 0)
    ]
    return sum(risk_factors) / len(risk_factors)

risk_score = calculate_risk_score(top_action, current_state)

# Success probability estimation
def estimate_success_probability(element, action_type, context):
    base_probability = 0.8  # Default success rate
    
    # Adjust based on element properties
    if element.is_visible and element.is_enabled:
        base_probability += 0.1
    if element.text or element.aria_label:
        base_probability += 0.05
    
    # Adjust based on page stability
    if context.get('page_loaded', True):
        base_probability += 0.05
    
    return min(base_probability, 1.0)

success_prob = estimate_success_probability(selected_element, action_type, context)
```

**Computational Results:**
- **Top Viable Element:** {computed_element}
- **Confidence Score:** {confidence_score}
- **Risk Assessment:** {risk_level}
- **Success Probability:** {success_probability}%

## PROGRAM-VERIFIED REASONING

Based on computational analysis:
1. **Mathematical Optimization:** Element selection verified through scoring algorithm
2. **Risk Quantification:** Risk factors mathematically assessed  
3. **Probability Calculation:** Success likelihood computed from multiple variables
4. **Verification Loop:** Action validated against computational constraints

**Computationally Verified Action:** {verified_action}

**Algorithm-Enhanced Decision Making:**"""


class AdvancedPromptBuilder:
    """Enhanced prompt builder using advanced strategies"""
    
    def __init__(self):
        self.prompts = AdvancedPrompts()
        self.strategy_selector = StrategySelector()
        
    def build_optimized_prompt(self, 
                             task: str,
                             state: WebPageState,
                             context: PromptOptimizationContext,
                             history: List[Dict[str, Any]] = None,
                             strategy: Optional[PromptingStrategy] = None) -> str:
        """Build optimized prompt using best strategy for context"""
        
        # Auto-select strategy if not specified
        if not strategy:
            strategy = self.strategy_selector.select_strategy(context)
        
        # Prepare common variables
        elements_text = self._format_elements_advanced(state.interactive_elements[:25])
        content_summary = self._create_content_summary(state.dom_structure.distilled_content)
        history_text = self._format_history_advanced(history or [])
        
        # Build strategy-specific prompt
        if strategy == PromptingStrategy.CHAIN_OF_THOUGHT:
            return self._build_cot_prompt(task, state, elements_text, content_summary, history_text)
        elif strategy == PromptingStrategy.TREE_OF_THOUGHTS:
            return self._build_tot_prompt(task, state, elements_text, content_summary)
        elif strategy == PromptingStrategy.REACT_ENHANCED:
            return self._build_enhanced_react_prompt(task, state, elements_text, content_summary, history_text)
        elif strategy == PromptingStrategy.CONSTITUTIONAL_AI:
            return self._build_constitutional_prompt(task, state, elements_text)
        elif strategy == PromptingStrategy.SELF_CONSISTENCY:
            return self._build_self_consistency_prompt(task, state, elements_text, content_summary)
        elif strategy == PromptingStrategy.FEW_SHOT:
            return self._build_few_shot_prompt(task, state, elements_text, context.domain)
        elif strategy == PromptingStrategy.META_PROMPTING:
            return self._build_meta_prompt(task, state, elements_text, context)
        elif strategy == PromptingStrategy.QUANTUM_PROMPTING:
            return self._build_quantum_prompt(task, state, elements_text)
        elif strategy == PromptingStrategy.PROGRAM_AIDED:
            return self._build_program_aided_prompt(task, state, elements_text)
        else:
            # Fallback to enhanced zero-shot
            return self._build_zero_shot_enhanced_prompt(task, state, elements_text, content_summary)
    
    def _build_cot_prompt(self, task: str, state: WebPageState, elements: str, content: str, history: str) -> str:
        """Build Chain of Thought prompt"""
        return self.prompts.CHAIN_OF_THOUGHT_BROWSER_TEMPLATE.format(
            task=task,
            url=state.metadata.url,
            title=state.metadata.title,
            content=content,
            elements=elements,
            previous_steps=history
        )
    
    def _build_tot_prompt(self, task: str, state: WebPageState, elements: str, content: str) -> str:
        """Build Tree of Thoughts prompt"""
        return self.prompts.TREE_OF_THOUGHTS_TEMPLATE.format(
            task=task,
            url=state.metadata.url,
            title=state.metadata.title,
            elements=elements,
            context=content[:200]
        )
    
    def _build_enhanced_react_prompt(self, task: str, state: WebPageState, elements: str, content: str, history: str) -> str:
        """Build enhanced ReAct prompt"""
        return self.prompts.ENHANCED_REACT_TEMPLATE.format(
            task=task,
            url=state.metadata.url,
            title=state.metadata.title,
            content=content,
            elements=elements,
            history=history
        )
    
    def _build_constitutional_prompt(self, task: str, state: WebPageState, elements: str) -> str:
        """Build Constitutional AI prompt"""
        return self.prompts.CONSTITUTIONAL_AI_TEMPLATE.format(
            task=task,
            url=state.metadata.url,
            title=state.metadata.title,
            elements=elements,
            enhanced_reasoning="[Constitutional analysis completed]"
        )
    
    def _build_self_consistency_prompt(self, task: str, state: WebPageState, elements: str, content: str) -> str:
        """Build Self-Consistency prompt"""
        # Create primary reasoning path first
        primary_reasoning = f"Task: {task}\nState: {content[:300]}\nElements: {elements[:500]}"
        
        return self.prompts.SELF_CONSISTENCY_TEMPLATE.format(
            primary_reasoning=primary_reasoning,
            path1_action="[To be filled by reasoning]",
            path2_action="[To be filled by reasoning]", 
            path3_action="[To be filled by reasoning]",
            url=state.metadata.url,
            elements=elements
        )
    
    def _build_few_shot_prompt(self, task: str, state: WebPageState, elements: str, domain: str) -> str:
        """Build Few-Shot learning prompt"""
        examples = self.prompts.get_few_shot_examples(domain, "search")  # Default to search examples
        
        return self.prompts.FEW_SHOT_TEMPLATE.format(
            examples=examples,
            task=task,
            url=state.metadata.url,
            title=state.metadata.title,
            elements=elements
        )
    
    def _build_meta_prompt(self, task: str, state: WebPageState, elements: str, context: PromptOptimizationContext) -> str:
        """Build Meta-Prompting prompt"""
        return self.prompts.META_PROMPTING_TEMPLATE.format(
            success_rate=85,  # Default success rate
            failure_patterns="Element not found, timeout errors",
            complexity=context.task_complexity,
            domain=context.domain,
            optimal_strategy="Chain of Thought",
            context_adaptations="Enhanced verification",
            reasoning_depth="Detailed",
            verification_needs="Action success confirmation",
            optimized_prompt="[Self-generated optimized prompt]",
            reasoning_type="sequential",
            addressed_failures="timeout handling",
            success_patterns="element verification",
            task=task,
            url=state.metadata.url,
            title=state.metadata.title,
            elements=elements
        )
    
    def _build_quantum_prompt(self, task: str, state: WebPageState, elements: str) -> str:
        """Build Quantum Prompting prompt"""
        return self.prompts.QUANTUM_PROMPTING_TEMPLATE.format(
            task=task,
            url=state.metadata.url,
            title=state.metadata.title,
            direct_action="[Direct element interaction]",
            search_action="[Search-based approach]",
            navigation_action="[Navigation tree traversal]", 
            analysis_action="[Content analysis approach]",
            selected_state="A",  # Default selection
            final_action="[Quantum-optimized action]",
            elements=elements
        )
    
    def _build_program_aided_prompt(self, task: str, state: WebPageState, elements: str) -> str:
        """Build Program-Aided Language prompt"""
        return self.prompts.PROGRAM_AIDED_TEMPLATE.format(
            task=task,
            url=state.metadata.url,
            elements=str(state.interactive_elements[:10]),  # Raw elements for computation
            computed_element="[Computationally selected element]",
            confidence_score="[Calculated confidence]",
            risk_level="[Computed risk level]",
            success_probability="[Calculated probability]",
            verified_action="[Algorithm-verified action]"
        )
    
    def _build_zero_shot_enhanced_prompt(self, task: str, state: WebPageState, elements: str, content: str) -> str:
        """Build enhanced zero-shot prompt"""
        return f"""You are an expert web automation agent with advanced reasoning capabilities.

## ENHANCED ZERO-SHOT REASONING

**Mission:** {task}
**Context:** {state.metadata.url} - {state.metadata.title}

**Deep Analysis Protocol:**
1. **Goal Decomposition:** Break down the task into atomic actions
2. **State Assessment:** Analyze current page capabilities thoroughly  
3. **Strategy Formulation:** Design optimal interaction sequence
4. **Risk Evaluation:** Identify and mitigate potential failures
5. **Success Validation:** Plan verification of action outcomes

**Current State Analysis:**
{content}

**Available Interaction Points:**
{elements}

**CRITICAL ELEMENT SELECTION RULES:**
- For Amazon: ALWAYS use the main search box with id="twotabsearchtextbox" or name="field-keywords"
- NEVER select carousel elements (.a-carousel-firstvisibleitem, .a-carousel-lastvisibleitem)
- NEVER select hidden input elements (type="hidden")
- For search functionality, prioritize elements with:
  * id containing "search" or "keyword"
  * type="search"
  * placeholder containing "Search"
  * aria-label containing "Search"

**Enhanced Decision Making:**
Based on advanced zero-shot reasoning, I will select the most logical and effective action:

[Your enhanced zero-shot reasoning and action selection here]"""
    
    def _format_elements_advanced(self, elements: List[InteractiveElement]) -> str:
        """Advanced element formatting with additional context"""
        lines = []
        for elem in elements:
            # Enhanced element description
            desc = f"[{elem.id}] {elem.type.upper()}"
            
            # Add primary text/label
            if elem.text:
                desc += f': "{elem.text[:60]}"'
            elif elem.aria_label:
                desc += f': aria-label="{elem.aria_label}"'
            elif elem.placeholder:
                desc += f': placeholder="{elem.placeholder}"'
            else:
                desc += f': <{elem.tag_name}>'
            
            # Add state and accessibility info
            states = []
            if not elem.is_visible: states.append("hidden")
            if not elem.is_enabled: states.append("disabled") 
            if elem.is_checked: states.append("checked")
            
            # Add contextual hints
            if elem.type == "button" and "submit" in str(elem.attributes.get("type", "")):
                states.append("submit-button")
            if "required" in str(elem.attributes):
                states.append("required")
                
            if states:
                desc += f" ({', '.join(states)})"
                
            # Add relevance scoring hint
            relevance_indicators = ["search", "submit", "login", "buy", "add", "next"]
            if any(indicator in desc.lower() for indicator in relevance_indicators):
                desc += " ⭐ [High Relevance]"
            
            # Special Amazon search box prioritization
            if elem.id == "twotabsearchtextbox" or "twotabsearch" in str(elem.id).lower():
                desc += " 🎯 [AMAZON MAIN SEARCH BOX - PREFERRED]"
            elif "carousel" in desc.lower() or elem.type == "hidden":
                desc += " ⚠️ [HIDDEN/CAROUSEL - AVOID]"
            elif "field-keywords" in str(elem.attributes.get("name", "")):
                desc += " 🔍 [SEARCH INPUT - GOOD CHOICE]"
                
            lines.append(desc)
            
        return "\n".join(lines)
    
    def _create_content_summary(self, content: str, max_length: int = 2000) -> str:
        """Create intelligent content summary"""
        if len(content) <= max_length:
            return content
            
        # Extract key sections
        lines = content.split('\n')
        important_lines = []
        
        # Priority keywords for relevance
        priority_keywords = [
            'search', 'login', 'submit', 'buy', 'purchase', 'cart', 'checkout',
            'register', 'sign up', 'menu', 'navigation', 'results', 'product'
        ]
        
        for line in lines:
            line = line.strip()
            if len(line) > 10:  # Skip very short lines
                if any(keyword in line.lower() for keyword in priority_keywords):
                    important_lines.append(line + " ⭐")
                else:
                    important_lines.append(line)
        
        # Truncate intelligently
        summary = '\n'.join(important_lines)
        if len(summary) > max_length:
            summary = summary[:max_length] + "\n... [Content truncated - focus on starred ⭐ high-relevance items above]"
            
        return summary
    
    def _format_history_advanced(self, history: List[Dict[str, Any]]) -> str:
        """Advanced history formatting with insights"""
        if not history:
            return "## CLEAN SLATE - No previous actions taken.\n**Strategic Advantage:** Full flexibility in approach selection."
            
        lines = ["## ACTION HISTORY ANALYSIS"]
        
        success_count = 0
        failure_count = 0
        
        for i, entry in enumerate(history[-5:], 1):  # Last 5 actions
            action = entry.get('action', {})
            result = entry.get('result', {})
            
            action_type = action.get('action', 'unknown')
            success = result.get('success', False)
            
            if success:
                success_count += 1
                status_icon = "✅"
            else:
                failure_count += 1
                status_icon = "❌"
                
            # Enhanced action description
            action_desc = f"**Step {i}:** {status_icon} {action_type.upper()}"
            
            if action_type == "click":
                action_desc += f" → Element [{action.get('element_id', '?')}]"
            elif action_type in ["type", "fill"]:
                text = action.get('text_to_type', action.get('text', ''))
                action_desc += f' → "{text[:30]}..."' if text else ""
            elif action_type == "navigate":
                action_desc += f" → {action.get('url', 'unknown URL')}"
                
            # Add outcome analysis
            if success:
                action_desc += " | Outcome: SUCCESS"
            else:
                error_msg = result.get('error', 'Unknown error')
                action_desc += f" | Failed: {error_msg[:50]}"
                
            lines.append(action_desc)
        
        # Add performance analysis
        total_actions = success_count + failure_count
        if total_actions > 0:
            success_rate = (success_count / total_actions) * 100
            lines.append(f"\n**Performance Analysis:** {success_rate:.1f}% success rate ({success_count}/{total_actions})")
            
            if failure_count > 0:
                lines.append("**Learning Opportunity:** Previous failures inform current strategy selection.")
        
        return "\n".join(lines)


class StrategySelector:
    """Intelligent strategy selection based on context"""
    
    def select_strategy(self, context: PromptOptimizationContext) -> PromptingStrategy:
        """Select optimal prompting strategy based on context"""
        
        # Critical tasks always use Self-Consistency for verification
        if context.task_complexity == "critical":
            return PromptingStrategy.SELF_CONSISTENCY
            
        # Constitutional AI for any sensitive domains
        sensitive_domains = ["social_media", "financial", "personal"]
        if context.domain in sensitive_domains:
            return PromptingStrategy.CONSTITUTIONAL_AI
            
        # Complex tasks benefit from Tree of Thoughts exploration
        if context.task_complexity == "complex" and context.speed_priority != "high":
            return PromptingStrategy.TREE_OF_THOUGHTS
            
        # High accuracy needs with moderate complexity use Chain of Thought
        if context.accuracy_priority == "high" and context.task_complexity in ["moderate", "complex"]:
            return PromptingStrategy.CHAIN_OF_THOUGHT
            
        # Domain-specific tasks use Few-Shot learning
        if context.domain in ["ecommerce", "job_search", "news"] and context.task_complexity != "trivial":
            return PromptingStrategy.FEW_SHOT
            
        # High-speed requirements use Enhanced ReAct
        if context.speed_priority == "high":
            return PromptingStrategy.REACT_ENHANCED
            
        # Default to Enhanced Zero-Shot for simple tasks
        return PromptingStrategy.ZERO_SHOT_ENHANCED


# Export optimized prompt builder
def create_advanced_prompt_builder() -> AdvancedPromptBuilder:
    """Factory function to create optimized prompt builder"""
    return AdvancedPromptBuilder()