"""
Advanced Prompt Strategies Implementation

This module implements state-of-the-art prompting strategies for reverse prompting,
including Chain of Thought, Self-Consistency, Tree of Thoughts, Mixture of Experts,
and other cutting-edge techniques.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4
import json
import random
import re
from datetime import datetime

from ..core.models import (
    CodeArtifact,
    PromptTemplate,
    PromptGeneration,
    PromptStrategy,
    CodeLanguage,
    VersionInfo,
)


class BasePromptStrategy(ABC):
    """Base class for all prompting strategies."""

    def __init__(self, name: str, strategy_type: PromptStrategy):
        self.name = name
        self.strategy_type = strategy_type
        self.version = VersionInfo()
        self.metadata = {}

    @abstractmethod
    def generate_prompt(
        self, target_artifact: CodeArtifact, context: Optional[Dict[str, Any]] = None
    ) -> PromptGeneration:
        """Generate a prompt for creating the target code artifact."""
        pass

    @abstractmethod
    def get_template(self) -> PromptTemplate:
        """Get the prompt template for this strategy."""
        pass

    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate the context for this strategy."""
        return True


class ZeroShotStrategy(BasePromptStrategy):
    """Zero-shot prompting strategy."""

    def __init__(self):
        super().__init__("Zero-Shot", PromptStrategy.ZERO_SHOT)

    def generate_prompt(
        self, target_artifact: CodeArtifact, context: Optional[Dict[str, Any]] = None
    ) -> PromptGeneration:
        """Generate a zero-shot prompt."""
        context = context or {}

        template = self.get_template()

        # Extract key information from the target artifact
        code_analysis = self._analyze_code(target_artifact)

        prompt_content = template.render(
            language=target_artifact.language.value,
            description=target_artifact.description or "Generate the following code",
            functionality=code_analysis["functionality"],
            requirements=code_analysis["requirements"],
            code_style=context.get("style", "clean and readable"),
            additional_context=context.get("additional_context", ""),
        )

        return PromptGeneration(
            template_id=template.id,
            strategy=self.strategy_type,
            content=prompt_content,
            target_artifact_id=target_artifact.id,
            variables=context,
            metadata={"analysis": code_analysis, "strategy_version": str(self.version)},
        )

    def get_template(self) -> PromptTemplate:
        """Get zero-shot template."""
        return PromptTemplate(
            name="Zero-Shot Code Generation",
            strategy=PromptStrategy.ZERO_SHOT,
            template="""Create {language} code that {description}.

Requirements:
{requirements}

The code should:
- {functionality}
- Follow {code_style} coding practices
- Include appropriate comments and documentation
- Handle edge cases appropriately
{additional_context}

Please provide complete, working {language} code.""",
            variables=[
                "language",
                "description",
                "functionality",
                "requirements",
                "code_style",
                "additional_context",
            ],
            system_prompt="You are an expert software developer. Generate high-quality, production-ready code based on the requirements.",
        )

    def _analyze_code(self, artifact: CodeArtifact) -> Dict[str, str]:
        """Analyze the target code to extract key characteristics."""
        code = artifact.content

        # Basic analysis - could be enhanced with AST parsing
        analysis = {
            "functionality": self._extract_functionality(code),
            "requirements": self._extract_requirements(code, artifact.language),
        }

        return analysis

    def _extract_functionality(self, code: str) -> str:
        """Extract what the code does."""
        # Look for docstrings, comments, and function names
        functionality_hints = []

        # Find docstrings
        docstring_pattern = r'"""(.*?)"""'
        docstrings = re.findall(docstring_pattern, code, re.DOTALL)
        for docstring in docstrings:
            functionality_hints.append(docstring.strip())

        # Find function names
        function_pattern = r"def\s+(\w+)\s*\("
        functions = re.findall(function_pattern, code)
        if functions:
            functionality_hints.append(f"Implement functions: {', '.join(functions)}")

        # Find class names
        class_pattern = r"class\s+(\w+)\s*[\(:]"
        classes = re.findall(class_pattern, code)
        if classes:
            functionality_hints.append(f"Implement classes: {', '.join(classes)}")

        return (
            "; ".join(functionality_hints)
            if functionality_hints
            else "Implement the required functionality"
        )

    def _extract_requirements(self, code: str, language: CodeLanguage) -> str:
        """Extract technical requirements from the code."""
        requirements = []

        if language == CodeLanguage.PYTHON:
            # Check for imports
            import_pattern = r"import\s+(\w+)|from\s+(\w+)\s+import"
            imports = re.findall(import_pattern, code)
            if imports:
                flat_imports = [imp for group in imports for imp in group if imp]
                requirements.append(f"Use libraries: {', '.join(set(flat_imports))}")

        # Check for specific patterns
        if "async" in code or "await" in code:
            requirements.append("Use asynchronous programming")

        if "class" in code:
            requirements.append("Use object-oriented programming")

        if "try:" in code and "except" in code:
            requirements.append("Include proper error handling")

        return "; ".join(requirements) if requirements else "Follow best practices"


class FewShotStrategy(BasePromptStrategy):
    """Few-shot prompting strategy with examples."""

    def __init__(self, num_examples: int = 3):
        super().__init__("Few-Shot", PromptStrategy.FEW_SHOT)
        self.num_examples = num_examples

    def generate_prompt(
        self, target_artifact: CodeArtifact, context: Optional[Dict[str, Any]] = None
    ) -> PromptGeneration:
        """Generate a few-shot prompt with examples."""
        context = context or {}

        template = self.get_template()
        examples = self._generate_examples(target_artifact, context)

        prompt_content = template.render(
            language=target_artifact.language.value,
            examples=examples,
            target_description=target_artifact.description or "Generate similar code",
            style_guide=context.get("style_guide", "Follow clean code principles"),
        )

        return PromptGeneration(
            template_id=template.id,
            strategy=self.strategy_type,
            content=prompt_content,
            target_artifact_id=target_artifact.id,
            variables=context,
            metadata={
                "num_examples": len(examples),
                "strategy_version": str(self.version),
            },
        )

    def get_template(self) -> PromptTemplate:
        """Get few-shot template."""
        return PromptTemplate(
            name="Few-Shot Code Generation",
            strategy=PromptStrategy.FEW_SHOT,
            template="""Here are examples of {language} code implementations:

{examples}

Now, create similar {language} code that {target_description}.

{style_guide}

Provide complete, working code following the patterns shown in the examples.""",
            variables=["language", "examples", "target_description", "style_guide"],
            system_prompt="You are an expert programmer. Learn from the provided examples and generate similar high-quality code.",
        )

    def _generate_examples(
        self, target_artifact: CodeArtifact, context: Dict[str, Any]
    ) -> str:
        """Generate relevant examples for the target artifact."""
        # This would ideally pull from a database of similar code examples
        # For now, we'll create synthetic examples based on the target

        examples = []
        language = target_artifact.language

        if language == CodeLanguage.PYTHON:
            examples = self._python_examples(target_artifact)
        elif language == CodeLanguage.JAVASCRIPT:
            examples = self._javascript_examples(target_artifact)
        # Add more languages as needed

        return "\n\n".join(
            [
                f"Example {i+1}:\n{example}"
                for i, example in enumerate(examples[: self.num_examples])
            ]
        )

    def _python_examples(self, target_artifact: CodeArtifact) -> List[str]:
        """Generate Python examples."""
        return [
            '''def calculate_area(length, width):
    """Calculate the area of a rectangle."""
    if length <= 0 or width <= 0:
        raise ValueError("Length and width must be positive")
    return length * width''',
            '''class DataProcessor:
    """Process and validate data."""
    
    def __init__(self, data):
        self.data = self._validate_data(data)
    
    def _validate_data(self, data):
        if not isinstance(data, list):
            raise TypeError("Data must be a list")
        return data
    
    def process(self):
        return [item.strip().lower() for item in self.data if item]''',
            '''async def fetch_data(url, session):
    """Fetch data from API endpoint."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return None''',
        ]

    def _javascript_examples(self, target_artifact: CodeArtifact) -> List[str]:
        """Generate JavaScript examples."""
        return [
            """function calculateTotal(items) {
    if (!Array.isArray(items)) {
        throw new Error('Items must be an array');
    }
    
    return items.reduce((total, item) => {
        return total + (item.price || 0);
    }, 0);
}""",
            """class UserManager {
    constructor() {
        this.users = new Map();
    }
    
    addUser(id, userData) {
        if (!id || !userData) {
            throw new Error('ID and user data are required');
        }
        
        this.users.set(id, { ...userData, createdAt: new Date() });
        return true;
    }
    
    getUser(id) {
        return this.users.get(id) || null;
    }
}""",
            """async function processApiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}""",
        ]


class ChainOfThoughtStrategy(BasePromptStrategy):
    """Chain of Thought (CoT) prompting strategy."""

    def __init__(self):
        super().__init__("Chain of Thought", PromptStrategy.CHAIN_OF_THOUGHT)

    def generate_prompt(
        self, target_artifact: CodeArtifact, context: Optional[Dict[str, Any]] = None
    ) -> PromptGeneration:
        """Generate a Chain of Thought prompt."""
        context = context or {}

        template = self.get_template()
        thinking_steps = self._generate_thinking_steps(target_artifact)

        prompt_content = template.render(
            language=target_artifact.language.value,
            description=target_artifact.description or "Generate the required code",
            thinking_steps=thinking_steps,
            requirements=context.get("requirements", "Follow best practices"),
        )

        return PromptGeneration(
            template_id=template.id,
            strategy=self.strategy_type,
            content=prompt_content,
            target_artifact_id=target_artifact.id,
            variables=context,
            metadata={
                "thinking_steps": len(thinking_steps.split("\n")),
                "strategy_version": str(self.version),
            },
        )

    def get_template(self) -> PromptTemplate:
        """Get Chain of Thought template."""
        return PromptTemplate(
            name="Chain of Thought Code Generation",
            strategy=PromptStrategy.CHAIN_OF_THOUGHT,
            template="""I need to create {language} code that {description}.

Let me think through this step by step:

{thinking_steps}

Based on this analysis, I'll implement the solution:

Requirements: {requirements}

Let me code this step by step, explaining my reasoning for each part.""",
            variables=["language", "description", "thinking_steps", "requirements"],
            system_prompt="You are an expert programmer who thinks through problems methodically. Explain your reasoning step by step before and during coding.",
        )

    def _generate_thinking_steps(self, target_artifact: CodeArtifact) -> str:
        """Generate thinking steps for the CoT prompt."""
        steps = [
            "1. First, I need to understand what this code should do",
            "2. I should identify the main components and functions needed",
            "3. I need to consider the data structures and algorithms required",
            "4. I should think about error handling and edge cases",
            "5. I need to plan the overall structure and flow",
            "6. I should consider performance and optimization aspects",
            "7. Finally, I'll implement the solution with clear, readable code",
        ]

        # Customize based on artifact analysis
        code_analysis = self._analyze_artifact(target_artifact)
        if code_analysis["has_classes"]:
            steps.insert(
                3, "3a. I need to design the class structure and relationships"
            )
        if code_analysis["has_async"]:
            steps.insert(
                4, "4a. I should consider asynchronous operations and concurrency"
            )

        return "\n".join(steps)

    def _analyze_artifact(self, artifact: CodeArtifact) -> Dict[str, bool]:
        """Analyze the artifact for specific patterns."""
        code = artifact.content.lower()
        return {
            "has_classes": "class " in code,
            "has_functions": "def " in code or "function " in code,
            "has_async": "async " in code or "await " in code,
            "has_loops": any(keyword in code for keyword in ["for ", "while ", "loop"]),
            "has_conditionals": any(
                keyword in code for keyword in ["if ", "else", "switch"]
            ),
        }


class SelfConsistencyStrategy(BasePromptStrategy):
    """Self-Consistency prompting strategy."""

    def __init__(self, num_paths: int = 5):
        super().__init__("Self-Consistency", PromptStrategy.SELF_CONSISTENCY)
        self.num_paths = num_paths

    def generate_prompt(
        self, target_artifact: CodeArtifact, context: Optional[Dict[str, Any]] = None
    ) -> PromptGeneration:
        """Generate a self-consistency prompt."""
        context = context or {}

        template = self.get_template()
        reasoning_paths = self._generate_reasoning_paths(target_artifact)

        prompt_content = template.render(
            language=target_artifact.language.value,
            description=target_artifact.description or "Generate the required code",
            num_paths=self.num_paths,
            reasoning_example=reasoning_paths,
            final_instruction="Choose the most consistent and reliable approach",
        )

        return PromptGeneration(
            template_id=template.id,
            strategy=self.strategy_type,
            content=prompt_content,
            target_artifact_id=target_artifact.id,
            variables=context,
            metadata={
                "num_paths": self.num_paths,
                "strategy_version": str(self.version),
            },
        )

    def get_template(self) -> PromptTemplate:
        """Get self-consistency template."""
        return PromptTemplate(
            name="Self-Consistency Code Generation",
            strategy=PromptStrategy.SELF_CONSISTENCY,
            template="""I need to create {language} code that {description}.

I'll explore {num_paths} different reasoning paths to find the most reliable solution:

{reasoning_example}

Now I'll generate {num_paths} different approaches and select the most consistent one:

Path 1: [Think through approach 1]
Path 2: [Think through approach 2]
Path 3: [Think through approach 3]
Path 4: [Think through approach 4]
Path 5: [Think through approach 5]

{final_instruction} and implement the final solution.""",
            variables=[
                "language",
                "description",
                "num_paths",
                "reasoning_example",
                "final_instruction",
            ],
            system_prompt="You are an expert programmer who considers multiple approaches before settling on the best solution. Generate diverse reasoning paths and choose the most consistent approach.",
        )

    def _generate_reasoning_paths(self, target_artifact: CodeArtifact) -> str:
        """Generate example reasoning paths."""
        return """Example reasoning paths:
Path A: Focus on simplicity and readability
Path B: Optimize for performance and efficiency  
Path C: Emphasize error handling and robustness
Path D: Prioritize modularity and reusability
Path E: Balance all aspects for production use"""


class TreeOfThoughtsStrategy(BasePromptStrategy):
    """Tree of Thoughts (ToT) prompting strategy."""

    def __init__(self, depth: int = 3, breadth: int = 3):
        super().__init__("Tree of Thoughts", PromptStrategy.TREE_OF_THOUGHTS)
        self.depth = depth
        self.breadth = breadth

    def generate_prompt(
        self, target_artifact: CodeArtifact, context: Optional[Dict[str, Any]] = None
    ) -> PromptGeneration:
        """Generate a Tree of Thoughts prompt."""
        context = context or {}

        template = self.get_template()
        thought_tree = self._generate_thought_tree(target_artifact)

        prompt_content = template.render(
            language=target_artifact.language.value,
            description=target_artifact.description or "Generate the required code",
            thought_tree=thought_tree,
            evaluation_criteria="Consider correctness, efficiency, readability, and maintainability",
        )

        return PromptGeneration(
            template_id=template.id,
            strategy=self.strategy_type,
            content=prompt_content,
            target_artifact_id=target_artifact.id,
            variables=context,
            metadata={
                "tree_depth": self.depth,
                "tree_breadth": self.breadth,
                "strategy_version": str(self.version),
            },
        )

    def get_template(self) -> PromptTemplate:
        """Get Tree of Thoughts template."""
        return PromptTemplate(
            name="Tree of Thoughts Code Generation",
            strategy=PromptStrategy.TREE_OF_THOUGHTS,
            template="""I need to create {language} code that {description}.

I'll use a tree of thoughts approach to explore different solution paths:

{thought_tree}

Evaluation criteria: {evaluation_criteria}

I'll now evaluate each path, prune the less promising ones, and develop the best solution further.""",
            variables=[
                "language",
                "description",
                "thought_tree",
                "evaluation_criteria",
            ],
            system_prompt="You are an expert programmer using systematic exploration of solution space. Consider multiple approaches, evaluate them, and develop the most promising ones.",
        )

    def _generate_thought_tree(self, target_artifact: CodeArtifact) -> str:
        """Generate a thought tree structure."""
        tree = """
Level 1 - Initial Approaches:
├── Approach A: Procedural implementation
├── Approach B: Object-oriented design
└── Approach C: Functional programming style

Level 2 - Refined Strategies:
├── A1: Simple procedural with functions
├── A2: Procedural with modules
├── B1: Single class design
├── B2: Multiple class hierarchy
├── C1: Pure functional approach
└── C2: Functional with side effects

Level 3 - Implementation Details:
├── A1.1: Direct implementation
├── A1.2: Helper functions
├── B1.1: All methods in one class
├── B1.2: Class with private methods
└── ... (continue evaluation)
"""
        return tree


class MixtureOfExpertsStrategy(BasePromptStrategy):
    """Mixture of Experts (MoE) prompting strategy."""

    def __init__(self, experts: Optional[List[str]] = None):
        super().__init__("Mixture of Experts", PromptStrategy.MIXTURE_OF_EXPERTS)
        self.experts = experts or [
            "Performance Optimization Expert",
            "Code Quality Expert",
            "Security Expert",
            "Maintainability Expert",
            "Algorithm Design Expert",
        ]

    def generate_prompt(
        self, target_artifact: CodeArtifact, context: Optional[Dict[str, Any]] = None
    ) -> PromptGeneration:
        """Generate a Mixture of Experts prompt."""
        context = context or {}

        template = self.get_template()
        expert_consultations = self._generate_expert_consultations(target_artifact)

        prompt_content = template.render(
            language=target_artifact.language.value,
            description=target_artifact.description or "Generate the required code",
            experts=", ".join(self.experts),
            expert_consultations=expert_consultations,
            synthesis_instruction="Synthesize the expert advice into optimal code",
        )

        return PromptGeneration(
            template_id=template.id,
            strategy=self.strategy_type,
            content=prompt_content,
            target_artifact_id=target_artifact.id,
            variables=context,
            metadata={"experts": self.experts, "strategy_version": str(self.version)},
        )

    def get_template(self) -> PromptTemplate:
        """Get Mixture of Experts template."""
        return PromptTemplate(
            name="Mixture of Experts Code Generation",
            strategy=PromptStrategy.MIXTURE_OF_EXPERTS,
            template="""I need to create {language} code that {description}.

I'll consult with multiple experts: {experts}

{expert_consultations}

Now I'll {synthesis_instruction} that incorporates the best insights from each expert.""",
            variables=[
                "language",
                "description",
                "experts",
                "expert_consultations",
                "synthesis_instruction",
            ],
            system_prompt="You are a lead architect consulting with multiple domain experts. Consider each expert's perspective and synthesize the best solution.",
        )

    def _generate_expert_consultations(self, target_artifact: CodeArtifact) -> str:
        """Generate expert consultation dialogue."""
        consultations = []

        for expert in self.experts:
            if "Performance" in expert:
                advice = "Focus on algorithmic efficiency, memory usage, and computational complexity"
            elif "Quality" in expert:
                advice = "Emphasize readable, well-documented code with proper naming and structure"
            elif "Security" in expert:
                advice = "Consider input validation, error handling, and potential vulnerabilities"
            elif "Maintainability" in expert:
                advice = (
                    "Design for extensibility, testability, and future modifications"
                )
            elif "Algorithm" in expert:
                advice = "Choose optimal data structures and algorithms for the problem domain"
            else:
                advice = "Apply domain-specific best practices and patterns"

            consultations.append(f"{expert}: {advice}")

        return "\n".join(consultations)


class MetaPromptingStrategy(BasePromptStrategy):
    """Meta-prompting strategy that generates prompts about prompting."""

    def __init__(self):
        super().__init__("Meta-Prompting", PromptStrategy.META_PROMPTING)

    def generate_prompt(
        self, target_artifact: CodeArtifact, context: Optional[Dict[str, Any]] = None
    ) -> PromptGeneration:
        """Generate a meta-prompting prompt."""
        context = context or {}

        template = self.get_template()
        meta_analysis = self._generate_meta_analysis(target_artifact)

        prompt_content = template.render(
            language=target_artifact.language.value,
            description=target_artifact.description or "Generate the required code",
            meta_analysis=meta_analysis,
            prompt_optimization="Design the optimal prompt for generating this specific code",
        )

        return PromptGeneration(
            template_id=template.id,
            strategy=self.strategy_type,
            content=prompt_content,
            target_artifact_id=target_artifact.id,
            variables=context,
            metadata={"meta_level": 2, "strategy_version": str(self.version)},
        )

    def get_template(self) -> PromptTemplate:
        """Get meta-prompting template."""
        return PromptTemplate(
            name="Meta-Prompting Code Generation",
            strategy=PromptStrategy.META_PROMPTING,
            template="""I need to create {language} code that {description}.

First, let me analyze what would be the optimal prompting strategy for this task:

{meta_analysis}

Now I'll {prompt_optimization}, then use that optimized approach to generate the code.""",
            variables=[
                "language",
                "description",
                "meta_analysis",
                "prompt_optimization",
            ],
            system_prompt="You are a meta-cognitive AI that first optimizes the prompting approach before solving the actual problem.",
        )

    def _generate_meta_analysis(self, target_artifact: CodeArtifact) -> str:
        """Generate meta-analysis of the prompting task."""
        return """Meta-analysis considerations:
1. What type of problem is this? (algorithmic, data processing, UI, etc.)
2. What level of complexity is required?
3. What are the key constraints and requirements?
4. What examples or context would be most helpful?
5. What potential pitfalls should be avoided?
6. What would make the prompt most effective for this specific task?"""


# Strategy Registry
STRATEGY_REGISTRY = {
    PromptStrategy.ZERO_SHOT: ZeroShotStrategy,
    PromptStrategy.FEW_SHOT: FewShotStrategy,
    PromptStrategy.CHAIN_OF_THOUGHT: ChainOfThoughtStrategy,
    PromptStrategy.SELF_CONSISTENCY: SelfConsistencyStrategy,
    PromptStrategy.TREE_OF_THOUGHTS: TreeOfThoughtsStrategy,
    PromptStrategy.MIXTURE_OF_EXPERTS: MixtureOfExpertsStrategy,
    PromptStrategy.META_PROMPTING: MetaPromptingStrategy,
}


def get_strategy(strategy_type: PromptStrategy, **kwargs) -> BasePromptStrategy:
    """Get a strategy instance by type."""
    if strategy_type not in STRATEGY_REGISTRY:
        raise ValueError(f"Unknown strategy: {strategy_type}")

    strategy_class = STRATEGY_REGISTRY[strategy_type]
    return strategy_class(**kwargs)


def list_available_strategies() -> List[PromptStrategy]:
    """List all available prompting strategies."""
    return list(STRATEGY_REGISTRY.keys())


__all__ = [
    "BasePromptStrategy",
    "ZeroShotStrategy",
    "FewShotStrategy",
    "ChainOfThoughtStrategy",
    "SelfConsistencyStrategy",
    "TreeOfThoughtsStrategy",
    "MixtureOfExpertsStrategy",
    "MetaPromptingStrategy",
    "STRATEGY_REGISTRY",
    "get_strategy",
    "list_available_strategies",
]
