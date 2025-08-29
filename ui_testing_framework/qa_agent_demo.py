#!/usr/bin/env python3
"""
QA Engineer AI Agent Demo

This demonstrates the new QA Engineer AI Agent prompt that was created
by rewriting the original Software Engineering AI Agent prompt.

The QA Engineer Agent embodies 30+ years of QA experience and systematic
testing methodologies.
"""

from prompts import get_strategy, render_prompt


def main():
    print("=" * 80)
    print("QA ENGINEER AI AGENT DEMONSTRATION")
    print("=" * 80)
    print()

    # Get the QA Engineer Agent strategy
    qa_agent = get_strategy("qa_engineer_agent")

    print("🎯 STRATEGY OVERVIEW:")
    print(f"Name: {qa_agent.name}")
    print(f"Title: {qa_agent.title}")
    print(f"Core Principle: {qa_agent.core_principle}")
    print()

    print("🧠 SAMPLE APPLICATIONS:")
    print()

    # Sample testing scenarios
    test_scenarios = [
        "Create a test plan for a mobile banking app login feature",
        "Design automated tests for an API that processes payments",
        "Analyze quality risks for a real-time chat application",
        "Create a performance testing strategy for a video streaming service",
        "Design security tests for a user registration system",
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📋 SCENARIO {i}: {scenario}")
        print("-" * 60)

        # Render the prompt with this scenario
        rendered_prompt = render_prompt("qa_engineer_agent", scenario)

        # Show just the methodology section for brevity
        lines = rendered_prompt.split("\n")
        methodology_start = None
        for j, line in enumerate(lines):
            if "**YOUR QA METHODOLOGY:**" in line:
                methodology_start = j
                break

        if methodology_start:
            methodology_section = "\n".join(
                lines[methodology_start : methodology_start + 15]
            )
            print(methodology_section)
        else:
            print(rendered_prompt[:300] + "...")

        print()
        print("=" * 60)
        print()

    print("🌟 KEY DIFFERENCES FROM SOFTWARE ENGINEER AGENT:")
    print()
    print("✓ Focus on TESTING and QUALITY ASSURANCE instead of coding")
    print("✓ Emphasizes TEST DESIGN and COVERAGE ANALYSIS")
    print("✓ Uses QA tools (pytest, selenium, playwright) as first-class citizens")
    print("✓ Applies RISK-BASED TESTING and systematic test planning")
    print("✓ Focuses on DEFECT PREVENTION and early quality feedback")
    print("✓ Employs COMPREHENSIVE TEST STRATEGIES covering all quality aspects")
    print("✓ Champions QUALITY ADVOCACY throughout the development process")
    print()

    print("🛠️ USAGE IN PRACTICE:")
    print()
    print("from prompts import render_prompt")
    print()
    print("# Apply QA methodology to any testing challenge")
    print("qa_prompt = render_prompt('qa_engineer_agent', 'Your testing task here')")
    print("# qa_prompt now contains comprehensive QA guidance")
    print()

    print("=" * 80)
    print("QA ENGINEER AI AGENT - Ready for comprehensive quality assurance!")
    print("=" * 80)


if __name__ == "__main__":
    main()
