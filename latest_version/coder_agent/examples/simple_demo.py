#!/usr/bin/env python3
"""
Simple demonstration of CODER Agent capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coder_agent import CoderEngine, AgentRequest
from coder_agent.config import load_config


async def demonstrate_coder_agent():
    """
    Demonstrate CODER Agent with a simple task.
    """
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║            CODER Agent Demonstration                         ║
    ╚══════════════════════════════════════════════════════════════╝
    
    This demo shows CODER Agent's capabilities:
    1. Understanding complex requests
    2. Creating comprehensive task plans (B.R.E.A.K. methodology)
    3. Executing with metacognitive monitoring
    4. Managing context intelligently
    5. Following CODER v3.1 principles strictly
    """)
    
    # Example tasks to demonstrate
    demo_tasks = [
        {
            "name": "Simple Function Creation",
            "task": "Create a Python function that validates email addresses with comprehensive tests",
            "require_tests": True
        },
        {
            "name": "Bug Fix",
            "task": "Fix the TypeError in the calculate_total function and add error handling",
            "require_tests": True
        },
        {
            "name": "Refactoring",
            "task": "Refactor the database connection code to use connection pooling",
            "require_tests": False
        }
    ]
    
    print("\nAvailable demo tasks:")
    for i, demo in enumerate(demo_tasks, 1):
        print(f"{i}. {demo['name']}: {demo['task'][:50]}...")
    
    # Get user choice
    try:
        choice = int(input("\nSelect a demo task (1-3): ")) - 1
        if choice < 0 or choice >= len(demo_tasks):
            raise ValueError
    except (ValueError, KeyboardInterrupt):
        print("Invalid choice. Using task 1.")
        choice = 0
    
    selected_task = demo_tasks[choice]
    
    print(f"\n📋 Selected: {selected_task['name']}")
    print(f"📝 Task: {selected_task['task']}")
    print("-" * 60)
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"⚠️  Using default configuration: {e}")
        config = {"engine": {}, "context": {}, "tools": {}, "planner": {}, "meta": {}}
    
    # Create request
    request = AgentRequest(
        task=selected_task["task"],
        project_path=".",
        require_tests=selected_task["require_tests"],
        timeout_seconds=300
    )
    
    # Initialize engine
    engine = CoderEngine(config)
    
    # Show the planning phase
    print("\n🧠 PHASE 1: Understanding Context...")
    context = await engine._understand_context(request)
    
    print(f"  • Literal understanding: {context.get('confidence_level', 0):.1%}")
    print(f"  • Inferred intent: {context.get('inferred_intent', {})}")
    print(f"  • Required capabilities: {context.get('required_capabilities', [])}")
    
    # Create plan
    print("\n📋 PHASE 2: Creating Task Plan (B.R.E.A.K.)...")
    plan = await engine.task_planner.create_plan(request, context)
    
    print(f"\n  B - Break down: {len(plan.tasks)} tasks identified")
    print(f"  R - Review: Dependencies established")
    print(f"  E - Establish: Priorities assigned")
    print(f"  A - Analyze: {plan.total_estimated_tokens:,} tokens estimated")
    print(f"  K - Keep track: Plan ID {plan.plan_id[:8]}...")
    
    print("\n  Task breakdown:")
    for i, task in enumerate(plan.tasks[:5], 1):  # Show first 5
        prefix = "    ├─" if i < min(5, len(plan.tasks)) else "    └─"
        deps = f" [deps: {len(task.dependencies)}]" if task.dependencies else ""
        print(f"{prefix} {task.priority.value}: {task.content[:50]}...{deps}")
    
    if len(plan.tasks) > 5:
        print(f"    ... and {len(plan.tasks) - 5} more tasks")
    
    # Validate plan
    print("\n✅ PHASE 3: Validating Plan...")
    validation = await engine._validate_plan(plan)
    
    if validation.passed:
        print("  • No circular dependencies ✓")
        print("  • All dependencies resolved ✓")
        print("  • Token budget acceptable ✓")
    else:
        print(f"  • Issues found: {len(validation.failures)}")
        for failure in validation.failures[:3]:
            print(f"    - {failure.get('message')}")
    
    # Demonstrate metacognition
    print("\n🧠 Metacognitive Monitoring:")
    print("  • Confidence level tracking")
    print("  • Quality metrics assessment")
    print("  • Cognitive load monitoring")
    print("  • Error pattern detection")
    
    # Context management demo
    print("\n📊 Context Management:")
    context_status = engine.context_manager.get_usage_status()
    print(f"  • Status: {context_status['status']}")
    print(f"  • Usage: {context_status['percentage']:.1f}%")
    print(f"  • Strategy: {context_status['action']}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    
    print("""
    Key Differentiators from Cursor/Replit:
    
    1. STRICT TDD: Tests written BEFORE implementation
    2. Pre-flight Checks: Environment validated before execution
    3. Metacognition: Self-monitoring and quality assurance
    4. Context Intelligence: Smart compression and prioritization
    5. B.R.E.A.K. Planning: Systematic task decomposition
    6. CODER v3.1: Production-grade contracts and validation
    
    To run the actual agent:
      python -m coder_agent "Your task here"
    """)


async def demonstrate_multi_agent():
    """
    Demonstrate multi-agent orchestration capabilities.
    """
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         Multi-Agent Orchestration Demonstration              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    CODER Agent can orchestrate multiple specialized sub-agents:
    
    1. Search Agent: Finds relevant code across the codebase
    2. Analysis Agent: Understands code structure and dependencies
    3. Implementation Agent: Writes production-ready code
    4. Test Agent: Creates comprehensive test suites
    5. Review Agent: Validates quality and best practices
    
    Each agent has:
    • Specialized tool access
    • Domain-specific reasoning
    • Independent context management
    • Coordinated execution
    """)
    
    # This would demonstrate actual multi-agent coordination
    # For now, just showing the concept
    
    agents = [
        ("Search Agent", "Finding all authentication-related code..."),
        ("Analysis Agent", "Analyzing dependencies and impact..."),
        ("Implementation Agent", "Implementing OAuth2 integration..."),
        ("Test Agent", "Writing comprehensive test suite..."),
        ("Review Agent", "Validating code quality and security...")
    ]
    
    for agent_name, action in agents:
        print(f"\n🤖 {agent_name}")
        print(f"   {action}")
        await asyncio.sleep(0.5)  # Simulate work
    
    print("\n✅ All agents completed successfully")
    print("📊 Aggregated results available")


if __name__ == "__main__":
    print("Select demonstration:")
    print("1. Simple CODER Agent Demo")
    print("2. Multi-Agent Orchestration Demo")
    
    try:
        choice = input("\nChoice (1-2): ").strip()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    
    if choice == "2":
        asyncio.run(demonstrate_multi_agent())
    else:
        asyncio.run(demonstrate_coder_agent())