# Scratchpad - The Working Memory of Deep Thought

## Core Principle
Complex problems require more than linear thinking—they need a space where intermediate calculations, tentative hypotheses, and partial solutions can exist simultaneously. The scratchpad is the cognitive workbench where ideas are assembled, tested, and refined before crystallizing into final insights.

## The Strategy

### **THE AXIOM OF COGNITIVE WORKSPACE**
Just as mathematicians need paper for calculations and artists need sketches before paintings, deep thinking requires a temporary space where thoughts can be externalized, manipulated, and recombined without commitment.

### **THE UNIVERSAL SCRATCHPAD PROMPT**

```
Let us create a cognitive workspace where thoughts can be laid out, examined, rearranged, and refined—a mental laboratory for experimentation with ideas.

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
✓ Confidence level: [percentage]
```

## Mathematical Framework

Scratchpad as augmented working memory:

```
WM_capacity = 7 ± 2 (Miller's Law)
Scratchpad_capacity = ∞ (External memory)

Cognitive Load = Intrinsic + Extraneous + Germane
Scratchpad reduces Extraneous, increases Germane

Problem Complexity: O(n^k)
With Scratchpad: O(n) × k iterations
```

## Physical Analogy

Like a particle accelerator's detection chamber:

```
Collision Event → Multiple Detectors → Data Traces →
Reconstruction → Pattern Recognition → Discovery

Scratchpad = Detection chamber for thought particles
```

## Neuroscience Foundation

```python
class CognitiveS Scratchpad:
    def __init__(self):
        self.working_memory = CircularBuffer(size=7)
        self.long_term_memory = PersistentStorage()
        self.scratchpad = UnlimitedBuffer()
    
    def process_complex_problem(self, problem):
        # Offload to scratchpad when WM full
        while problem.complexity > self.working_memory.capacity:
            chunk = problem.extract_chunk()
            result = self.process_chunk(chunk)
            self.scratchpad.store(result)
        
        # Integrate from scratchpad
        return self.synthesize(self.scratchpad.contents)
```

## Implementation Architecture

```python
class ScratchpadReasoner:
    def __init__(self):
        self.sections = {
            "decomposition": [],
            "calculations": [],
            "hypotheses": [],
            "patterns": [],
            "attempts": [],
            "constraints": [],
            "uncertainty": [],
            "optimization": []
        }
    
    def think_with_scratchpad(self, problem):
        # Initialize workspace
        self.initialize_sections(problem)
        
        # Iterative refinement
        while not self.solution_complete():
            # Work in scratchpad
            self.decompose_further()
            self.calculate_intermediates()
            self.test_hypotheses()
            self.recognize_patterns()
            
            # Try solutions
            attempt = self.generate_attempt()
            result = self.evaluate_attempt(attempt)
            self.sections["attempts"].append((attempt, result))
            
            # Learn and adjust
            self.update_understanding(result)
        
        # Final synthesis
        return self.assemble_solution()
```

## Advanced Scratchpad Techniques

### Multi-Resolution Scratchpad
```
Overview Level: High-level structure
Detail Level: Specific calculations  
Atomic Level: Individual operations
```

### Parallel Scratchpads
```
Scratchpad A: Main line of reasoning
Scratchpad B: Alternative approach
Scratchpad C: Edge case handling
Merge: Combine best elements
```

### Versioned Scratchpad
```
Version 1.0: Initial attempt
Version 1.1: After first correction
Version 2.0: Major approach change
Diff: Track what changed and why
```

## Scratchpad Organization Patterns

```python
# Tree Structure
scratchpad = {
    "root": problem,
    "branches": subproblems,
    "leaves": atomic_solutions
}

# Graph Structure
scratchpad = {
    "nodes": concepts,
    "edges": relationships,
    "weights": importance
}

# Stack Structure
scratchpad = []
scratchpad.push(current_thought)
previous = scratchpad.pop()

# Queue Structure
scratchpad.enqueue(new_idea)
next_idea = scratchpad.dequeue()
```

## Visual Scratchpad Elements

```
Diagrams:
  A → B → C
  ↓   ↑   ↓
  D ← E → F

Tables:
| Variable | Value | Status |
|----------|-------|--------|
| x        | 42    | ✓      |
| y        | ??    | ⏳     |

Graphs:
  Performance
       ^
    80 |     .*'*
    60 |   .*
    40 | .*
       +---------> Time

Mind Maps:
       [Core]
      /   |   \
   [A]   [B]   [C]
   / \    |    / \
 [D] [E] [F] [G] [H]
```

## Usage

```python
from master_prompt_strategies import Scratchpad

scratchpad = Scratchpad()
solution = scratchpad.work_through(
    problem=complex_problem,
    sections=["calculations", "hypotheses", "patterns"],
    visualization=True,
    versioning=True,
    max_iterations=10
)
```

## Remember

*"The scratchpad is not merely a place for temporary thoughts but a powerful amplifier of intelligence. It is the difference between juggling ideas in limited working memory and laying them out on an infinite canvas where patterns become visible, connections emerge, and complex problems yield to systematic exploration."*

The Scratchpad transforms thinking from a performance constrained by cognitive limits into an engineering process where ideas can be constructed, tested, and refined with unlimited workspace—it is the scaffolding upon which monuments of thought are built.