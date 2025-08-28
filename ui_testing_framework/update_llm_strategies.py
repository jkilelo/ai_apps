#!/usr/bin/env python3
"""
Update llm.py with comprehensive strategy prompts from master_prompt_strategies/*.md files
This script extracts the rich prompts and replaces the simplified versions
"""

import re
from pathlib import Path
from typing import Dict, Tuple

def extract_universal_prompt_from_md(file_path: Path) -> str:
    """Extract the universal prompt section from a .md file"""
    content = file_path.read_text(encoding='utf-8')
    
    # Look for THE UNIVERSAL ... PROMPT section
    pattern = r'\*\*THE UNIVERSAL.*?PROMPT\*\*\s*```(.*?)```'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # If not found, look for the main strategy section
    pattern = r'## The Strategy\s*(.*?)(?:##|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Extract the core content
        strategy_content = match.group(1)
        # Look for code blocks within
        code_pattern = r'```(.*?)```'
        code_match = re.search(code_pattern, strategy_content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
    
    return ""

def get_strategy_implementations() -> Dict[str, str]:
    """Get all comprehensive strategy implementations"""
    
    strategies_dir = Path(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\master_prompt_strategies")
    
    # Mapping of StrategyType enum values to .md files and their rich prompts
    strategy_mapping = {
        # Core reasoning strategies
        "chain_of_thought": strategies_dir / "01_chain_of_thought.md",
        "tree_of_thoughts": strategies_dir / "02_tree_of_thoughts.md",
        "graph_of_thoughts": None,  # May need custom or use tree_of_thoughts variant
        
        # Problem decomposition
        "least_to_most": None,  # Will create based on pattern
        "step_back": None,  # Will create based on pattern
        "decomposed": None,  # Will create based on pattern
        
        # Knowledge enhancement  
        "retrieval_augmented": None,  # Will create based on pattern
        "generated_knowledge": None,  # Will create based on pattern
        "knowledge_graph": None,  # Will create based on pattern
        
        # Self-improvement
        "self_consistency": strategies_dir / "05_self_consistency.md",
        "self_refine": None,  # Will create based on reflexion
        "self_verification": None,  # Will create based on pattern
        
        # Reasoning frameworks
        "react": strategies_dir / "03_react.md",
        "reflexion": strategies_dir / "08_reflexion.md",
        "chain_of_verification": None,  # Will create based on pattern
        
        # Advanced reasoning
        "hypothetical_document": None,  # Will create based on pattern
        "analogical_reasoning": None,  # Will create based on pattern
        "socratic_method": None,  # Will create based on pattern
        
        # Meta strategies
        "meta_prompting": strategies_dir / "06_meta_prompting.md",
        "prompt_optimization": strategies_dir / "12_opro.md",
        "constitutional_ai": strategies_dir / "04_constitutional_ai.md",
    }
    
    # Extract prompts from available .md files
    implementations = {}
    
    for strategy_name, md_path in strategy_mapping.items():
        if md_path and md_path.exists():
            prompt = extract_universal_prompt_from_md(md_path)
            if prompt:
                implementations[strategy_name] = prompt
    
    # Add custom implementations for missing strategies
    implementations.update(get_additional_strategies())
    
    return implementations

def get_additional_strategies() -> Dict[str, str]:
    """Get strategies from other .md files or create comprehensive versions"""
    
    strategies_dir = Path(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\master_prompt_strategies")
    
    additional = {}
    
    # Check if we have debate, scratchpad, few-shot, etc.
    extra_files = {
        "debate": strategies_dir / "07_debate.md",
        "scratchpad": strategies_dir / "09_scratchpad.md",
        "few_shot": strategies_dir / "10_few_shot.md",
        "zero_shot": strategies_dir / "11_zero_shot.md",
        "mixture_of_experts": strategies_dir / "13_mixture_of_experts.md",
        "quantum": strategies_dir / "14_quantum_prompting.md",
        "reverse": strategies_dir / "15_reverse_prompting.md",
        "evolutionary": strategies_dir / "16_evolutionary_optimization.md",
        "psychological": strategies_dir / "17_psychological_triggers.md",
        "universal_self_consistency": strategies_dir / "18_universal_self_consistency.md",
        "program_aided": strategies_dir / "19_program_aided_language.md",
        "chain_of_table": strategies_dir / "20_chain_of_table.md",
        "meta_cognitive": strategies_dir / "21_meta_cognitive_framework.md",
    }
    
    for name, path in extra_files.items():
        if path.exists():
            prompt = extract_universal_prompt_from_md(path)
            if prompt:
                additional[name] = prompt
    
    # Create comprehensive versions for missing core strategies
    additional["graph_of_thoughts"] = """
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
    
    additional["least_to_most"] = """
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
    
    additional["step_back"] = """
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
    
    additional["decomposed"] = """
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
    
    # Add more as needed...
    
    return additional

def generate_strategy_method(strategy_name: str, prompt: str) -> str:
    """Generate a Python method implementation for a strategy"""
    
    # Escape the prompt for Python string
    escaped_prompt = prompt.replace('"""', '\\"""').replace('\\', '\\\\')
    
    method_name = f"_{strategy_name}"
    
    return f'''
    def {method_name}(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Apply {strategy_name.replace('_', ' ').title()} strategy"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{{enhanced[-1].content}}\\n\\n"
                """{escaped_prompt}"""
            )
        return enhanced
'''

def update_llm_file():
    """Update the llm.py file with comprehensive strategies"""
    
    llm_path = Path(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_framework\llm.py")
    
    # Read the current file
    content = llm_path.read_text(encoding='utf-8')
    
    # Get all strategy implementations
    strategies = get_strategy_implementations()
    
    print(f"[INFO] Found {len(strategies)} strategy implementations")
    
    # For each strategy, replace the simplified version with the comprehensive one
    for strategy_name, prompt in strategies.items():
        print(f"[UPDATE] Updating {strategy_name}")
        
        # Find the current method implementation
        pattern = rf'def _{strategy_name}\(self.*?\n(?:.*?\n)*?        return enhanced'
        
        # Generate new implementation
        new_method = generate_strategy_method(strategy_name, prompt)
        
        # Replace in content
        if re.search(pattern, content):
            content = re.sub(pattern, new_method.strip(), content)
            print(f"  [OK] Replaced {strategy_name}")
        else:
            print(f"  [WARN] Could not find {strategy_name} method")
    
    # Write back the updated content
    backup_path = llm_path.with_suffix('.py.backup')
    llm_path.rename(backup_path)
    print(f"[BACKUP] Original saved to {backup_path}")
    
    llm_path.write_text(content, encoding='utf-8')
    print(f"[OK] Updated {llm_path}")
    
    return len(strategies)

if __name__ == "__main__":
    print("[START] Updating LLM strategies with comprehensive prompts")
    print("=" * 60)
    
    try:
        count = update_llm_file()
        print("=" * 60)
        print(f"[SUCCESS] Updated {count} strategies in llm.py")
        print("[INFO] The strategies now use the rich, comprehensive prompts from master_prompt_strategies/*.md")
    except Exception as e:
        print(f"[ERROR] Update failed: {e}")
        import traceback
        traceback.print_exc()