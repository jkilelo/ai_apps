#!/usr/bin/env python3
"""
Prompt Optimization Script
Systematically optimizes prompts_ascii.py for token efficiency while preserving information density.
"""

import re

# Common optimization patterns
OPTIMIZATION_PATTERNS = [
    # Remove verbose openings
    (r"Let us \w+[^.]*\.", "Apply "),
    (
        r"embark on a journey of reasoning that honors the fundamental principles of[^.]*\.",
        "systematic reasoning:",
    ),
    # Compress step headers
    (r"\*\*STEP \d+: ([^*]+)\*\* \([^)]+\)", r"**\1**"),
    (r"\*\*([^*]+)\*\* \([^)]+\)", r"**\1**"),
    # Simplify bullet points
    (r"- What are the ([^?]+)\?", r"- \1"),
    (r"- What ([^?]+)\?", r"- \1"),
    (r"- How ([^?]+)\?", r"- \1"),
    (r"- Why ([^?]+)\?", r"- \1"),
    # Remove redundant phrases
    (r"Before we begin, let us acknowledge:", "Acknowledge:"),
    (r"From the root, grow multiple branches simultaneously:", "Multiple branches:"),
    (r"Each instance independently:", "Each instance:"),
    # Compress verbose descriptions
    (
        r"Break down the problem into its atomic components:",
        "Break into atomic components:",
    ),
    (r"For each component, in logical order:", "For each component:"),
    (r"Combine the analyzed components:", "Combine components:"),
    (r"Test the reasoning chain:", "Test reasoning:"),
    (r"Examine the reasoning process itself:", "Examine process:"),
]


def optimize_prompt_content(content):
    """Apply optimization patterns to prompt content."""
    optimized = content

    for pattern, replacement in OPTIMIZATION_PATTERNS:
        optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)

    # Remove excessive whitespace
    optimized = re.sub(r"\n\n\n+", "\n\n", optimized)

    # Compress verbose lists
    optimized = re.sub(
        r"- ([^-\n]+)\n- ([^-\n]+)\n- ([^-\n]+)\n- ([^-\n]+)",
        r"- \1, \2, \3, \4",
        optimized,
    )

    return optimized


def batch_optimize_strategies():
    """Identify strategies that can be batch optimized."""
    strategies_to_optimize = [
        "DEBATE",
        "REFLEXION",
        "FEW_SHOT",
        "ZERO_SHOT",
        "OPRO",
        "MIXTURE_OF_EXPERTS",
        "QUANTUM_PROMPTING",
        "REVERSE_PROMPTING",
        "EVOLUTIONARY_OPTIMIZATION",
        "PSYCHOLOGICAL_TRIGGERS",
        "UNIVERSAL_SELF_CONSISTENCY",
        "PROGRAM_AIDED_LANGUAGE",
        "CHAIN_OF_TABLE",
        "META_COGNITIVE_FRAMEWORK",
        "QA_ENGINEER_AGENT",
    ]

    print(f"Strategies to optimize: {len(strategies_to_optimize)}")
    print("Optimization patterns available:", len(OPTIMIZATION_PATTERNS))

    return strategies_to_optimize


if __name__ == "__main__":
    strategies = batch_optimize_strategies()
    print(
        "\nOptimization script ready. Run individual optimizations with the patterns above."
    )
