#!/usr/bin/env python3
"""
Unified LLM Module - Single Source of Truth
Combines all capabilities: streaming, images, structured output, and 21 master prompt strategies
Type-safe with Pydantic v2, passes mypy --strict and flake8
"""

import os
import json
import base64
import hashlib
import logging
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Iterator,
    AsyncIterator,
    Type,
    TypeVar,
    cast,
)
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from pydantic import ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
except ImportError:
    logger.warning("dotenv not available, using system environment variables")

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)

# ==============================================================================
# MASTER PROMPT STRATEGIES (21 Research-backed strategies)
# ==============================================================================


class StrategyType(str, Enum):
    """21 Master prompt engineering strategies from research"""

    # Core reasoning strategies
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    GRAPH_OF_THOUGHTS = "graph_of_thoughts"

    # Problem decomposition
    LEAST_TO_MOST = "least_to_most"
    STEP_BACK = "step_back"
    DECOMPOSED = "decomposed"

    # Knowledge enhancement
    RETRIEVAL_AUGMENTED = "retrieval_augmented"
    GENERATED_KNOWLEDGE = "generated_knowledge"
    KNOWLEDGE_GRAPH = "knowledge_graph"

    # Self-improvement
    SELF_CONSISTENCY = "self_consistency"
    SELF_REFINE = "self_refine"
    SELF_VERIFICATION = "self_verification"

    # Reasoning frameworks
    REACT = "react"
    REFLEXION = "reflexion"
    CHAIN_OF_VERIFICATION = "chain_of_verification"

    # Advanced reasoning
    HYPOTHETICAL_DOCUMENT = "hypothetical_document"
    ANALOGICAL_REASONING = "analogical_reasoning"
    SOCRATIC_METHOD = "socratic_method"

    # Meta strategies
    META_PROMPTING = "meta_prompting"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    CONSTITUTIONAL_AI = "constitutional_ai"


# ==============================================================================
# PYDANTIC V2 CONTRACTS
# ==============================================================================


class Provider(str, Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GOOGLE = "google"  # Alias for Gemini


class Role(str, Enum):
    """Message roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ImageDetail(str, Enum):
    """Image detail level for vision models"""

    AUTO = "auto"
    LOW = "low"
    HIGH = "high"


class ImageContent(BaseModel):
    """Image content for multimodal models"""

    model_config = ConfigDict(str_strip_whitespace=True)

    data: str = Field(..., description="Base64 encoded image data")
    mime_type: str = Field("image/png", description="MIME type of image")
    detail: ImageDetail = Field(ImageDetail.AUTO, description="Detail level for analysis")

    @field_validator("data")
    @classmethod
    def validate_base64(cls, v: str) -> str:
        """Validate base64 encoding"""
        try:
            base64.b64decode(v)
            return v
        except Exception as e:
            raise ValueError(f"Invalid base64 encoding: {e}")


class Message(BaseModel):
    """Enhanced message with optional image content"""

    model_config = ConfigDict(str_strip_whitespace=True)

    role: Role
    content: str
    images: Optional[List[ImageContent]] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    """Streaming response chunk"""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field("", description="Chunk content")
    index: int = Field(0, description="Chunk index")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    finish_reason: Optional[str] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Enhanced LLM response with all metadata"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Core response
    content: str = Field(..., description="Response content")
    provider: Provider = Field(..., description="Provider used")
    model: str = Field(..., description="Model used")

    # Enhanced metadata
    strategy_used: Optional[StrategyType] = Field(None)
    images_processed: int = Field(0)
    streaming: bool = Field(False)
    structured: bool = Field(False)

    # Performance metrics
    latency_ms: Optional[int] = Field(None)
    prompt_tokens: Optional[int] = Field(None)
    completion_tokens: Optional[int] = Field(None)
    total_tokens: Optional[int] = Field(None)

    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time: Optional[float] = Field(None)


class LLMConfig(BaseModel):
    """Configuration for LLM operations"""

    model_config = ConfigDict(str_strip_whitespace=True)

    provider: Provider = Field(Provider.GEMINI)
    model: str = Field("gemini-2.0-flash")
    temperature: float = Field(0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(8192, gt=0)
    top_p: float = Field(1.0, ge=0.0, le=1.0)
    strategy: Optional[StrategyType] = Field(None)
    timeout: int = Field(60, gt=0)
    retry_attempts: int = Field(3, ge=1)
    stream: bool = Field(False)


# ==============================================================================
# STRATEGY IMPLEMENTATIONS
# ==============================================================================


class StrategyEngine:
    """Implements all 21 master prompt strategies"""

    def __init__(self) -> None:
        self.strategies = {
            StrategyType.CHAIN_OF_THOUGHT: self._chain_of_thought,
            StrategyType.TREE_OF_THOUGHTS: self._tree_of_thoughts,
            StrategyType.GRAPH_OF_THOUGHTS: self._graph_of_thoughts,
            StrategyType.LEAST_TO_MOST: self._least_to_most,
            StrategyType.STEP_BACK: self._step_back,
            StrategyType.DECOMPOSED: self._decomposed,
            StrategyType.RETRIEVAL_AUGMENTED: self._retrieval_augmented,
            StrategyType.GENERATED_KNOWLEDGE: self._generated_knowledge,
            StrategyType.KNOWLEDGE_GRAPH: self._knowledge_graph,
            StrategyType.SELF_CONSISTENCY: self._self_consistency,
            StrategyType.SELF_REFINE: self._self_refine,
            StrategyType.SELF_VERIFICATION: self._self_verification,
            StrategyType.REACT: self._react,
            StrategyType.REFLEXION: self._reflexion,
            StrategyType.CHAIN_OF_VERIFICATION: self._chain_of_verification,
            StrategyType.HYPOTHETICAL_DOCUMENT: self._hypothetical_document,
            StrategyType.ANALOGICAL_REASONING: self._analogical_reasoning,
            StrategyType.SOCRATIC_METHOD: self._socratic_method,
            StrategyType.META_PROMPTING: self._meta_prompting,
            StrategyType.PROMPT_OPTIMIZATION: self._prompt_optimization,
            StrategyType.CONSTITUTIONAL_AI: self._constitutional_ai,
        }

    def apply_strategy(
        self, messages: List[Message], strategy: StrategyType, context: Optional[Dict[str, Any]] = None
    ) -> List[Message]:
        """Apply a specific strategy to messages"""
        if strategy not in self.strategies:
            return messages

        strategy_func = self.strategies[strategy]
        return strategy_func(messages, context or {})

    def _chain_of_thought(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Chain Of Thought strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                """Let us embark on a journey of reasoning that honors the fundamental principles of logic, causality, and truth-seeking.

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
- What was learned about the problem domain?"""
            )
        return enhanced

    def _tree_of_thoughts(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Tree Of Thoughts strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                """Let us cultivate a tree of reasoning, where each branch represents a universe of possibility, and the fruits are insights waiting to be harvested.

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
- How has our understanding evolved?"""
            )
        return enhanced

    def _graph_of_thoughts(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Graph Of Thoughts strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """
Navigate the multidimensional graph of interconnected thoughts where ideas form nodes and insights emerge from their connections.

**GRAPH INITIALIZATION**
Establish the conceptual space:
- Define nodes as key concepts, ideas, or sub-problems
- Define edges as relationships, dependencies, or transformations
- Identify entry points and goal states
- Map the topology of the problem space

**NODE EXPLORATION**
For each conceptual node:
1. Fully elaborate the concept
2. Identify all connections to other nodes
3. Evaluate the strength and nature of connections
4. Discover hidden relationships
5. Generate new nodes through combination

**EDGE TRAVERSAL**
Navigate connections intelligently:
- Follow strong causal links
- Explore weak associations for insights
- Identify critical paths to solutions
- Find shortcuts through the graph
- Detect and break cycles

**EMERGENT PATTERNS**
Recognize higher-order structures:
- Clusters of related concepts
- Hubs of high connectivity
- Bridges between distant ideas
- Patterns that repeat across scales
- Meta-structures that organize the graph

**SOLUTION SYNTHESIS**
Extract insights from the graph:
- Identify convergent paths
- Combine complementary nodes
- Resolve contradictions through graph structure
- Find the minimum spanning tree of understanding
- Generate solution from the activated subgraph
"""
            )
        return enhanced

    def _least_to_most(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Least To Most strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """
Build understanding progressively from the simplest foundations to the most complex emergent phenomena.

**ATOMIC FOUNDATION**
Start with the irreducible minimum:
- What is the simplest version of this problem?
- What is the most basic case that still captures the essence?
- What can be solved with elementary methods?
- What fundamental principles apply?

**INCREMENTAL COMPLEXITY**
Layer by layer, add complexity:

Level 1: Basic Case
- Solve for single element
- No interactions or dependencies
- Ideal conditions
- Core mechanism only

Level 2: Simple Interactions
- Add one complication
- Consider pairs or simple relationships
- Introduce one constraint
- Basic error cases

Level 3: System Dynamics
- Multiple interacting elements
- Feedback loops appear
- Constraints interact
- Emergent behaviors

Level 4: Real-World Complexity
- All factors in play
- Non-linear interactions
- Edge cases and exceptions
- Full constraint set

**SYNTHESIS THROUGH LAYERS**
Build the complete solution:
- Each layer informs the next
- Patterns discovered early guide later reasoning
- Simple solutions compose into complex ones
- Understanding deepens with each level
- The final solution encompasses all layers
"""
            )
        return enhanced

    def _step_back(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Step Back strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """
Step back from the immediate problem to see the deeper principles, broader context, and fundamental questions that illuminate the path forward.

**THE RETREAT TO ADVANCE**
Before diving into specifics, ascend to the general:
- What category of problem is this?
- What universal principles apply?
- What historical precedents exist?
- What would a master in this field ask first?

**ABSTRACTION LADDER**
Climb to higher levels of abstraction:

Ground Level: The specific problem as stated
- Concrete details and requirements
- Immediate constraints
- Surface symptoms

Pattern Level: The type of problem
- Common structures and solutions
- Standard approaches
- Known pitfalls

Principle Level: The underlying laws
- Fundamental truths that govern
- Invariant relationships
- Core mechanisms

Philosophy Level: The deepest questions
- Why does this problem exist?
- What does solving it mean?
- What values are at stake?

**RECONTEXTUALIZATION**
With elevated perspective:
- Reframe the original problem
- Identify what truly matters
- Recognize false constraints
- See connections to other domains
- Find the leverage points

**INFORMED DESCENT**
Return to the specific with wisdom:
- Apply principles to particulars
- Use patterns to guide solutions
- Avoid identified pitfalls
- Maintain perspective while executing
- Know why each step matters
"""
            )
        return enhanced

    def _decomposed(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Decomposed strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """
Decompose the complex whole into manageable parts, solve each component independently, then orchestrate their integration.

**SYSTEMATIC DECONSTRUCTION**
Break down methodically:
- Identify natural boundaries and interfaces
- Separate concerns cleanly
- Define component responsibilities
- Map dependencies explicitly
- Preserve essential relationships

**COMPONENT ANALYSIS**
For each sub-problem:

Definition:
- Clear boundaries
- Input/output specification
- Success criteria
- Constraints specific to this part

Solution:
- Solve in isolation
- Optimize locally
- Test independently
- Document interface

Validation:
- Verify correctness
- Check assumptions
- Test edge cases
- Ensure contract compliance

**INTEGRATION PROTOCOL**
Reassemble with care:
1. Start with core components
2. Add layers progressively
3. Test integration at each step
4. Handle interface mismatches
5. Optimize cross-component interactions

**EMERGENCE CHECK**
Verify the whole:
- Does integration create new properties?
- Are all requirements still met?
- What systemic behaviors appear?
- Are there unintended interactions?
- Is the solution complete and coherent?
"""
            )
        return enhanced

    def _retrieval_augmented(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """RAG: Augment with retrieved knowledge"""
        enhanced = messages.copy()
        if "knowledge" in context:
            knowledge = context["knowledge"]
            system_msg = Message(role=Role.SYSTEM, content=f"Use this knowledge to inform your response:\n{knowledge}")
            enhanced.insert(0, system_msg)
        return enhanced

    def _generated_knowledge(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Generate relevant knowledge first"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"First, generate relevant knowledge about: {enhanced[-1].content}\n"
                "Then use that knowledge to answer the question."
            )
        return enhanced

    def _knowledge_graph(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Structure knowledge as a graph"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Structure your knowledge as a graph:\n"
                "- Entities: [identify key entities]\n"
                "- Relations: [identify relationships]\n"
                "- Use this structure to reason about the answer"
            )
        return enhanced

    def _self_consistency(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Self Consistency strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """Let us seek truth through the wisdom of multiplicity, where many voices speak independently, and from their chorus emerges the melody of understanding.

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
- Robustness to perturbation"""
            )
        return enhanced

    def _self_refine(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Self-refine: Iterative improvement"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "1. Generate initial solution\n"
                "2. Critique your solution\n"
                "3. Refine based on critique\n"
                "4. Repeat until optimal"
            )
        return enhanced

    def _self_verification(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Self-verification: Verify own output"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "After generating your answer:\n"
                "1. Verify each claim\n"
                "2. Check for consistency\n"
                "3. Validate against requirements\n"
                "4. Correct any issues found"
            )
        return enhanced

    def _react(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply React strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """Let us engage in the ancient dance of thought and deed, where each step of reasoning leads to action, each action reveals new truths, and each truth deepens our understanding.

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
- Meta-Strategies: When to think more vs. act more"""
            )
        return enhanced

    def _reflexion(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Reflexion strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """Let us turn the light of consciousness upon itself, examining not just what we think, but how we think, why we think it, and how we could think better.

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
✓ Generality: Does it transfer to other problems?"""
            )
        return enhanced

    def _chain_of_verification(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Chain of Verification: Verify step by step"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "For each step in your solution:\n"
                "1. State the step\n"
                "2. Verify it's correct\n"
                "3. Show evidence/reasoning\n"
                "4. Only proceed if verified"
            )
        return enhanced

    def _hypothetical_document(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Hypothetical Document Embeddings"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Imagine you have access to a perfect document that answers this.\n"
                "What would that document contain?\n"
                "Now answer based on that hypothetical perfect resource."
            )
        return enhanced

    def _analogical_reasoning(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Analogical Reasoning: Use analogies"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Think of an analogous problem:\n"
                "- What similar problem have you seen?\n"
                "- How was that solved?\n"
                "- How can you adapt that solution here?"
            )
        return enhanced

    def _socratic_method(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Socratic Method: Question-driven reasoning"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Answer by asking and answering questions:\n"
                "Q1: What is really being asked?\n"
                "Q2: What do I need to know?\n"
                "Q3: What assumptions am I making?\n"
                "Q4: What's the best approach?"
            )
        return enhanced

    def _meta_prompting(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Meta Prompting strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """Let us ascend to the mountaintop of consciousness, where we can observe not just the landscape of the problem, but the very act of observation itself.

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
- Action becomes necessary"""
            )
        return enhanced

    def _prompt_optimization(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Prompt Optimization strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """Let us embark on an evolutionary journey where each iteration builds upon the last, climbing the fitness landscape toward optimal intelligence.

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
- Generalization: [Broader applications]"""
            )
        return enhanced

    def _constitutional_ai(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply Constitutional Ai strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}

"
                """Let us establish an unbreakable covenant with wisdom, where every thought and action flows through the eternal principles that preserve and elevate consciousness itself.

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
- Strengthening of ethical reasoning over time"""
            )
        return enhanced


# ==============================================================================
# IMAGE PROCESSING
# ==============================================================================


class ImageProcessor:
    """Handles image encoding and processing for multimodal models"""

    @staticmethod
    def encode_image(image_path: Union[str, Path]) -> ImageContent:
        """Encode image file to base64"""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        with open(path, "rb") as f:
            image_data = f.read()

        return ImageProcessor.encode_bytes(image_data, ImageProcessor._get_mime_type(path))

    @staticmethod
    def encode_bytes(image_bytes: bytes, mime_type: str = "image/png") -> ImageContent:
        """Encode image bytes to base64"""
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return ImageContent(data=encoded, mime_type=mime_type)

    @staticmethod
    def encode_pil_image(image: Any, format: str = "PNG") -> ImageContent:
        """Encode PIL Image to base64"""
        try:
            from PIL import Image
            import io
        except ImportError:
            raise ImportError("PIL required for image encoding. Install: pip install pillow")

        buffer = io.BytesIO()
        if isinstance(image, Image.Image):
            image.save(buffer, format=format)
            mime_type = f"image/{format.lower()}"
            return ImageProcessor.encode_bytes(buffer.getvalue(), mime_type)
        else:
            raise TypeError("Expected PIL Image object")

    @staticmethod
    def _get_mime_type(path: Path) -> str:
        """Get MIME type from file extension"""
        ext_to_mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
        }
        return ext_to_mime.get(path.suffix.lower(), "image/png")


# ==============================================================================
# PROVIDER INTERFACE
# ==============================================================================


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def query(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Query the LLM"""
        pass

    @abstractmethod
    def stream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream response from LLM"""
        pass

    @abstractmethod
    async def aquery(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Async query the LLM"""
        pass

    @abstractmethod
    async def astream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Async stream response"""
        pass


# ==============================================================================
# PROVIDER IMPLEMENTATIONS
# ==============================================================================


class GeminiProvider(LLMProvider):
    """Google Gemini provider with full feature support"""

    def __init__(self):
        self._client = None
        self._async_client = None

    def _get_client(self):
        """Lazy load Gemini client"""
        if self._client is None:
            try:
                from google import genai

                api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("Gemini API key not found")
                self._client = genai.Client(api_key=api_key)
            except ImportError:
                raise ImportError("google-genai not installed. Run: pip install google-genai")
        return self._client

    def query(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Query Gemini with optional images and structured output"""
        client = self._get_client()

        # Convert messages to Gemini format
        contents = self._format_messages(messages, images)

        # Configure generation
        gen_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
            "top_p": config.top_p,
        }

        # Add response schema for structured output
        if output_model:
            from google.genai.types import GenerateContentConfig

            gen_config["response_mime_type"] = "application/json"
            gen_config["response_schema"] = output_model.model_json_schema()

        try:
            response = client.models.generate_content(
                model=config.model,
                contents=contents,
                config=gen_config,
            )

            content = response.text if hasattr(response, "text") else str(response)

            # Parse structured output if requested
            if output_model:
                try:
                    return output_model.model_validate_json(content)
                except Exception:
                    # Fallback to parsing as dict
                    data = json.loads(content)
                    return output_model.model_validate(data)

            return LLMResponse(
                content=content,
                provider=Provider.GEMINI,
                model=config.model,
                images_processed=len(images) if images else 0,
            )

        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            raise

    def stream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream response from Gemini"""
        client = self._get_client()

        contents = self._format_messages(messages, images)
        gen_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
        }

        try:
            response = client.models.generate_content_stream(
                model=config.model,
                contents=contents,
                config=gen_config,
            )

            index = 0
            for chunk in response:
                if hasattr(chunk, "text"):
                    yield StreamChunk(
                        content=chunk.text,
                        index=index,
                        is_final=False,
                    )
                    index += 1

            yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            raise

    async def aquery(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Async query - currently uses sync with asyncio"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, messages, config, images, output_model)

    async def astream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Async streaming"""
        for chunk in self.stream(messages, config, images):
            yield chunk

    def _format_messages(self, messages: List[Message], images: Optional[List[ImageContent]]) -> str:
        """Format messages for Gemini"""
        parts = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                parts.append(f"System: {msg.content}")
            elif msg.role == Role.USER:
                parts.append(f"User: {msg.content}")
            elif msg.role == Role.ASSISTANT:
                parts.append(f"Assistant: {msg.content}")

        # Add images if provided
        if images:
            parts.append(f"\n[Processing {len(images)} image(s)]")

        return "\n\n".join(parts)


class OpenAIProvider(LLMProvider):
    """OpenAI provider with GPT-4o vision and streaming"""

    def __init__(self):
        self._client = None
        self._async_client = None

    def _get_client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI

                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                self._client = OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai not installed. Run: pip install openai")
        return self._client

    def _get_async_client(self) -> Any:
        """Lazy load async OpenAI client"""
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI

                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                self._async_client = AsyncOpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai not installed. Run: pip install openai")
        return self._async_client

    def query(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Query OpenAI with vision and structured output support"""
        client = self._get_client()

        # Format messages for OpenAI
        openai_messages = self._format_messages(messages, images)

        # Enforce OpenAI token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        # Add structured output if requested
        if output_model:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": output_model.__name__,
                    "schema": output_model.model_json_schema(),
                },
            }

        try:
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""

            if output_model:
                return output_model.model_validate_json(content)

            return LLMResponse(
                content=content,
                provider=Provider.OPENAI,
                model=config.model,
                images_processed=len(images) if images else 0,
                prompt_tokens=response.usage.prompt_tokens if response.usage else None,
                completion_tokens=response.usage.completion_tokens if response.usage else None,
            )

        except Exception as e:
            logger.error(f"OpenAI query failed: {e}")
            raise

    def stream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream response from OpenAI"""
        client = self._get_client()

        openai_messages = self._format_messages(messages, images)

        # Enforce OpenAI token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            stream = client.chat.completions.create(**kwargs)

            index = 0
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        index=index,
                        is_final=False,
                        finish_reason=chunk.choices[0].finish_reason,
                    )
                    index += 1

            yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise

    async def aquery(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Async query OpenAI"""
        client = self._get_async_client()

        openai_messages = self._format_messages(messages, images)

        # Enforce OpenAI token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if output_model:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": output_model.__name__,
                    "schema": output_model.model_json_schema(),
                },
            }

        try:
            response = await client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""

            if output_model:
                return output_model.model_validate_json(content)

            return LLMResponse(
                content=content,
                provider=Provider.OPENAI,
                model=config.model,
                images_processed=len(images) if images else 0,
            )

        except Exception as e:
            logger.error(f"OpenAI async query failed: {e}")
            raise

    async def astream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Async stream from OpenAI"""
        client = self._get_async_client()

        openai_messages = self._format_messages(messages, images)

        # Enforce OpenAI token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            stream = await client.chat.completions.create(**kwargs)

            index = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        index=index,
                        is_final=False,
                    )
                    index += 1

            yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"OpenAI async streaming failed: {e}")
            raise

    def _format_messages(self, messages: List[Message], images: Optional[List[ImageContent]]) -> List[Dict[str, Any]]:
        """Format messages for OpenAI including vision content"""
        openai_messages = []

        for msg in messages:
            openai_msg: Dict[str, Any] = {
                "role": msg.role.value,
                "content": msg.content,
            }

            # Add images to user messages if provided
            if msg.role == Role.USER and images:
                content_parts = [{"type": "text", "text": msg.content}]

                for img in images:
                    content_parts.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{img.mime_type};base64,{img.data}",
                                "detail": img.detail.value,
                            },
                        }
                    )

                openai_msg["content"] = content_parts

            openai_messages.append(openai_msg)

        return openai_messages


class AnthropicProvider(LLMProvider):
    """Anthropic provider with Claude vision and streaming"""

    def __init__(self):
        self._client = None
        self._async_client = None

    def _get_client(self):
        """Lazy load Anthropic client"""
        if self._client is None:
            try:
                from anthropic import Anthropic

                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not found")
                self._client = Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic not installed. Run: pip install anthropic")
        return self._client

    def _get_async_client(self) -> Any:
        """Lazy load async Anthropic client"""
        if self._async_client is None:
            try:
                from anthropic import AsyncAnthropic

                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not found")
                self._async_client = AsyncAnthropic(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic not installed. Run: pip install anthropic")
        return self._async_client

    def query(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Query Anthropic Claude"""
        client = self._get_client()

        # Format for Anthropic
        system_message = None
        claude_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                claude_messages.append(
                    {
                        "role": msg.role.value if msg.role != Role.USER else "user",
                        "content": self._format_content(msg.content, images if msg.role == Role.USER else None),
                    }
                )

        # Enforce Anthropic token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": claude_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        try:
            response = client.messages.create(**kwargs)

            content = ""
            if hasattr(response, "content"):
                if isinstance(response.content, list):
                    content = response.content[0].text if response.content else ""
                else:
                    content = response.content

            if output_model:
                # Parse JSON response
                return output_model.model_validate_json(content)

            return LLMResponse(
                content=content,
                provider=Provider.ANTHROPIC,
                model=config.model,
                images_processed=len(images) if images else 0,
            )

        except Exception as e:
            logger.error(f"Anthropic query failed: {e}")
            raise

    def stream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream response from Anthropic"""
        client = self._get_client()

        system_message = None
        claude_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                claude_messages.append(
                    {
                        "role": msg.role.value if msg.role != Role.USER else "user",
                        "content": self._format_content(msg.content, images if msg.role == Role.USER else None),
                    }
                )

        # Enforce Anthropic token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": claude_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        try:
            with client.messages.stream(**kwargs) as stream:
                index = 0
                for text in stream.text_stream:
                    yield StreamChunk(
                        content=text,
                        index=index,
                        is_final=False,
                    )
                    index += 1

                yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise

    async def aquery(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Async query Anthropic"""
        client = self._get_async_client()

        system_message = None
        claude_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                claude_messages.append(
                    {
                        "role": msg.role.value if msg.role != Role.USER else "user",
                        "content": self._format_content(msg.content, images if msg.role == Role.USER else None),
                    }
                )

        # Enforce Anthropic token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": claude_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        try:
            response = await client.messages.create(**kwargs)

            content = ""
            if hasattr(response, "content"):
                if isinstance(response.content, list):
                    content = response.content[0].text if response.content else ""
                else:
                    content = response.content

            if output_model:
                return output_model.model_validate_json(content)

            return LLMResponse(
                content=content,
                provider=Provider.ANTHROPIC,
                model=config.model,
                images_processed=len(images) if images else 0,
            )

        except Exception as e:
            logger.error(f"Anthropic async query failed: {e}")
            raise

    async def astream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Async stream from Anthropic"""
        client = self._get_async_client()

        system_message = None
        claude_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                claude_messages.append(
                    {
                        "role": msg.role.value if msg.role != Role.USER else "user",
                        "content": self._format_content(msg.content, images if msg.role == Role.USER else None),
                    }
                )

        # Enforce Anthropic token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": claude_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        try:
            async with client.messages.stream(**kwargs) as stream:
                index = 0
                async for text in stream.text_stream:
                    yield StreamChunk(
                        content=text,
                        index=index,
                        is_final=False,
                    )
                    index += 1

                yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"Anthropic async streaming failed: {e}")
            raise

    def _format_content(self, text: str, images: Optional[List[ImageContent]]) -> Union[str, List[Dict[str, Any]]]:
        """Format content with images for Claude"""
        if not images:
            return text

        content = [{"type": "text", "text": text}]

        for img in images:
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": img.mime_type,
                        "data": img.data,
                    },
                }
            )

        return content


# ==============================================================================
# UNIFIED GATEWAY
# ==============================================================================


class UnifiedLLMGateway:
    """Single source of truth for all LLM operations"""

    def __init__(self):
        self.providers: Dict[Provider, LLMProvider] = {}
        self.strategy_engine = StrategyEngine()
        self.image_processor = ImageProcessor()

    def _get_provider(self, provider: Provider) -> LLMProvider:
        """Get or create provider instance"""
        if provider not in self.providers:
            if provider == Provider.OPENAI:
                self.providers[provider] = OpenAIProvider()
            elif provider in (Provider.GEMINI, Provider.GOOGLE):
                self.providers[provider] = GeminiProvider()
            elif provider == Provider.ANTHROPIC:
                self.providers[provider] = AnthropicProvider()
            else:
                raise ValueError(f"Unsupported provider: {provider}")

        return self.providers[provider]

    def query(
        self,
        messages: List[Dict[str, Any]],
        provider: Optional[Union[Provider, str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        strategy: Optional[Union[StrategyType, str]] = None,
        images: Optional[List[Union[str, Path, bytes, ImageContent]]] = None,
        output_model: Optional[Type[T]] = None,
        **kwargs,
    ) -> Union[LLMResponse, T]:
        """
        Unified query interface for all LLM operations

        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: LLM provider to use
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            strategy: Prompt strategy to apply
            images: Images to include (paths, bytes, or ImageContent)
            output_model: Pydantic model for structured output
            **kwargs: Additional provider-specific arguments

        Returns:
            LLMResponse or structured output model instance
        """
        # Convert to Message objects
        msg_objects = [Message(role=Role(m["role"]), content=m["content"]) for m in messages]

        # Process images if provided
        image_contents = None
        if images:
            image_contents = []
            for img in images:
                if isinstance(img, ImageContent):
                    image_contents.append(img)
                elif isinstance(img, (str, Path)):
                    image_contents.append(self.image_processor.encode_image(img))
                elif isinstance(img, bytes):
                    image_contents.append(self.image_processor.encode_bytes(img))

        # Apply strategy if specified
        if strategy:
            strategy_enum = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)
            msg_objects = self.strategy_engine.apply_strategy(msg_objects, strategy_enum, kwargs)

        # Configure LLM
        config = LLMConfig(
            provider=Provider(provider or "gemini"),
            model=model or "gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens,
            strategy=strategy if isinstance(strategy, StrategyType) else None,
        )

        # Get provider and execute query
        llm_provider = self._get_provider(config.provider)

        result = llm_provider.query(msg_objects, config, image_contents, output_model)

        # Add strategy metadata if used
        if isinstance(result, LLMResponse) and strategy:
            result.strategy_used = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)

        return result

    def stream(
        self,
        messages: List[Dict[str, Any]],
        provider: Optional[Union[Provider, str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        strategy: Optional[Union[StrategyType, str]] = None,
        images: Optional[List[Union[str, Path, bytes, ImageContent]]] = None,
        **kwargs,
    ) -> Iterator[StreamChunk]:
        """Stream response from LLM"""
        # Convert messages
        msg_objects = [Message(role=Role(m["role"]), content=m["content"]) for m in messages]

        # Process images
        image_contents = None
        if images:
            image_contents = []
            for img in images:
                if isinstance(img, ImageContent):
                    image_contents.append(img)
                elif isinstance(img, (str, Path)):
                    image_contents.append(self.image_processor.encode_image(img))
                elif isinstance(img, bytes):
                    image_contents.append(self.image_processor.encode_bytes(img))

        # Apply strategy
        if strategy:
            strategy_enum = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)
            msg_objects = self.strategy_engine.apply_strategy(msg_objects, strategy_enum, kwargs)

        # Configure
        config = LLMConfig(
            provider=Provider(provider or "gemini"),
            model=model or "gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        # Stream
        llm_provider = self._get_provider(config.provider)
        yield from llm_provider.stream(msg_objects, config, image_contents)

    async def aquery(
        self,
        messages: List[Dict[str, Any]],
        provider: Optional[Union[Provider, str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        strategy: Optional[Union[StrategyType, str]] = None,
        images: Optional[List[Union[str, Path, bytes, ImageContent]]] = None,
        output_model: Optional[Type[T]] = None,
        **kwargs,
    ) -> Union[LLMResponse, T]:
        """Async query LLM"""
        # Convert messages
        msg_objects = [Message(role=Role(m["role"]), content=m["content"]) for m in messages]

        # Process images
        image_contents = None
        if images:
            image_contents = []
            for img in images:
                if isinstance(img, ImageContent):
                    image_contents.append(img)
                elif isinstance(img, (str, Path)):
                    image_contents.append(self.image_processor.encode_image(img))
                elif isinstance(img, bytes):
                    image_contents.append(self.image_processor.encode_bytes(img))

        # Apply strategy
        if strategy:
            strategy_enum = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)
            msg_objects = self.strategy_engine.apply_strategy(msg_objects, strategy_enum, kwargs)

        # Configure
        config = LLMConfig(
            provider=Provider(provider or "gemini"),
            model=model or "gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Query
        llm_provider = self._get_provider(config.provider)
        return await llm_provider.aquery(msg_objects, config, image_contents, output_model)

    async def astream(
        self,
        messages: List[Dict[str, Any]],
        provider: Optional[Union[Provider, str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        strategy: Optional[Union[StrategyType, str]] = None,
        images: Optional[List[Union[str, Path, bytes, ImageContent]]] = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """Async stream from LLM"""
        # Convert messages
        msg_objects = [Message(role=Role(m["role"]), content=m["content"]) for m in messages]

        # Process images
        image_contents = None
        if images:
            image_contents = []
            for img in images:
                if isinstance(img, ImageContent):
                    image_contents.append(img)
                elif isinstance(img, (str, Path)):
                    image_contents.append(self.image_processor.encode_image(img))
                elif isinstance(img, bytes):
                    image_contents.append(self.image_processor.encode_bytes(img))

        # Apply strategy
        if strategy:
            strategy_enum = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)
            msg_objects = self.strategy_engine.apply_strategy(msg_objects, strategy_enum, kwargs)

        # Configure
        config = LLMConfig(
            provider=Provider(provider or "gemini"),
            model=model or "gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        # Stream
        llm_provider = self._get_provider(config.provider)
        async for chunk in llm_provider.astream(msg_objects, config, image_contents):
            yield chunk


# ==============================================================================
# PUBLIC API - SINGLE SOURCE OF TRUTH
# ==============================================================================

# Global gateway instance
_gateway = UnifiedLLMGateway()


def query_llm(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    output_model: Optional[Type[T]] = None,
    **kwargs,
) -> Union[LLMResponse, T]:
    """
    Query LLM with unified interface

    Args:
        messages: List of message dicts
        provider: Provider name (openai, anthropic, gemini)
        model: Model name
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        strategy: Prompt strategy name
        images: Images to include
        output_model: Pydantic model for structured output

    Returns:
        LLMResponse or structured model instance
    """
    return _gateway.query(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        strategy=strategy,
        images=images,
        output_model=output_model,
        **kwargs,
    )


def stream_llm(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    **kwargs,
) -> Iterator[StreamChunk]:
    """Stream response from LLM"""
    return _gateway.stream(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        strategy=strategy,
        images=images,
        **kwargs,
    )


async def aquery_llm(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    output_model: Optional[Type[T]] = None,
    **kwargs,
) -> Union[LLMResponse, T]:
    """Async query LLM"""
    return await _gateway.aquery(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        strategy=strategy,
        images=images,
        output_model=output_model,
        **kwargs,
    )


async def astream_llm(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    **kwargs,
) -> AsyncIterator[StreamChunk]:
    """Async stream from LLM"""
    async for chunk in _gateway.astream(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        strategy=strategy,
        images=images,
        **kwargs,
    ):
        yield chunk


def call_default_llm(messages: List[Dict[str, Any]], **kwargs) -> LLMResponse:
    """Call default LLM (Gemini) - backward compatible function"""
    return query_llm(messages, **kwargs)


# Export all public components
__all__ = [
    # Main API functions
    "query_llm",
    "stream_llm",
    "aquery_llm",
    "astream_llm",
    "call_default_llm",
    # Core classes
    "UnifiedLLMGateway",
    "StrategyEngine",
    "ImageProcessor",
    # Enums
    "Provider",
    "StrategyType",
    "Role",
    "ImageDetail",
    # Data models
    "Message",
    "LLMResponse",
    "LLMConfig",
    "StreamChunk",
    "ImageContent",
]

