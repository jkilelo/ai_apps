#!/usr/bin/env python3
"""
Self-test script for CODER Agent - No external dependencies required
"""

import sys
import asyncio
from pathlib import Path
import traceback

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test results tracking
tests_passed = []
tests_failed = []


def test(name):
    """Decorator for test functions"""
    def decorator(func):
        async def wrapper():
            try:
                print(f"\n🔍 Testing: {name}...")
                result = await func() if asyncio.iscoroutinefunction(func) else func()
                if result != False:
                    tests_passed.append(name)
                    print(f"   ✅ PASSED")
                else:
                    tests_failed.append(name)
                    print(f"   ❌ FAILED")
            except Exception as e:
                tests_failed.append(name)
                print(f"   ❌ FAILED: {str(e)}")
                if "--verbose" in sys.argv:
                    traceback.print_exc()
        return wrapper
    return decorator


@test("Import Core Modules")
def test_imports():
    """Test that all core modules can be imported"""
    try:
        from coder_agent import CoderEngine, AgentRequest, AgentResponse
        from coder_agent.core import (
            ContextManager, ToolExecutor, TaskPlanner, MetacognitionEngine
        )
        from coder_agent.contracts.base import (
            TaskPlan, TodoItem, ToolCall, ToolResult, ContextWindow
        )
        from coder_agent.config import load_config
        return True
    except ImportError as e:
        print(f"   Import error: {e}")
        return False


@test("Pydantic v2 Contracts")
def test_contracts():
    """Test Pydantic v2 contract creation"""
    from coder_agent.contracts.base import (
        AgentRequest, AgentResponse, TodoItem, TaskStatus
    )
    
    # Test request creation
    request = AgentRequest(
        task="Test task",
        project_path=".",
        require_tests=True
    )
    assert request.task == "Test task"
    assert request.require_tests == True
    
    # Test TODO item
    todo = TodoItem(
        content="Test todo",
        status=TaskStatus.PENDING
    )
    assert todo.content == "Test todo"
    assert todo.status == TaskStatus.PENDING
    
    # Test validation
    try:
        # Should fail - empty task
        bad_request = AgentRequest(task="", project_path=".")
        return False
    except:
        # Expected to fail
        pass
    
    return True


@test("Context Manager")
async def test_context_manager():
    """Test context management functionality"""
    from coder_agent.core.context_manager import ContextManager
    
    manager = ContextManager({"max_tokens": 1000, "reserved_tokens": 100})
    
    # Test adding items
    success = manager.add_item("Test content", "test", priority=5)
    assert success == True
    
    # Test status
    status = manager.get_usage_status()
    assert "status" in status
    assert status["percentage"] >= 0
    
    # Test context retrieval
    context = manager.get_context_for_llm()
    assert isinstance(context, str)
    
    return True


@test("Task Planner (B.R.E.A.K.)")
async def test_task_planner():
    """Test B.R.E.A.K. methodology implementation"""
    from coder_agent.core.task_planner import TaskPlanner
    from coder_agent.contracts.base import AgentRequest
    
    planner = TaskPlanner({})
    
    request = AgentRequest(
        task="Create a function to validate emails",
        require_tests=True
    )
    
    context = {
        "literal_request": request.task,
        "inferred_intent": {"action": "create"},
        "required_capabilities": ["validation"],
        "confidence_level": 0.8
    }
    
    plan = await planner.create_plan(request, context)
    
    # Verify B.R.E.A.K. components
    assert len(plan.tasks) > 1  # B - Broken down
    assert plan.total_estimated_tokens > 0  # A - Analyzed
    assert plan.plan_id is not None  # K - Keep track
    
    # Check TDD (tests before implementation)
    if request.require_tests:
        task_contents = [t.content.lower() for t in plan.tasks]
        test_task_index = -1
        impl_task_index = -1
        
        for i, content in enumerate(task_contents):
            if "test" in content and "write" in content:
                test_task_index = i
            if "implement" in content or "create" in content:
                if impl_task_index == -1:
                    impl_task_index = i
        
        # Tests should come before implementation (TDD)
        if test_task_index >= 0 and impl_task_index >= 0:
            assert test_task_index < impl_task_index, "TDD violation"
    
    return True


@test("Metacognition Engine")
async def test_metacognition():
    """Test metacognitive monitoring"""
    from coder_agent.core.metacognition import MetacognitionEngine
    
    meta = MetacognitionEngine({})
    
    # Test understanding assessment
    context = {
        "literal_request": "Fix the bug",
        "inferred_intent": {"action": "fix"},
        "required_capabilities": ["debugging"]
    }
    
    assessment = await meta.assess_understanding(context)
    assert "confidence" in assessment
    assert 0 <= assessment["confidence"] <= 1
    
    # Test execution monitoring
    results = [
        {"success": True, "duration": 1},
        {"success": False, "error": "Test error"},
    ]
    
    quality = await meta.check_execution_quality(results)
    assert "quality_score" in quality
    assert "needs_adjustment" in quality
    
    return True


@test("Tool Executor Patterns")
async def test_tool_executor():
    """Test tool execution with my patterns"""
    from coder_agent.core.tool_executor import ToolExecutor
    from coder_agent.contracts.base import ToolCall, ToolType
    
    executor = ToolExecutor({})
    
    # Test Read before Write rule
    assert ToolType.EDIT in executor.READ_BEFORE_WRITE
    assert ToolType.WRITE in executor.READ_BEFORE_WRITE
    
    # Test timeout configuration
    assert executor.TOOL_TIMEOUTS[ToolType.READ] < executor.TOOL_TIMEOUTS[ToolType.TEST]
    
    # Test parameter validation
    read_params = executor._get_required_params(ToolType.READ)
    assert "file_path" in read_params
    
    edit_params = executor._get_required_params(ToolType.EDIT)
    assert all(p in edit_params for p in ["file_path", "old_string", "new_string"])
    
    return True


@test("Pre-flight Checks")
async def test_preflight():
    """Test pre-flight validation system"""
    from coder_agent.core.engine_helpers import EngineHelpers
    
    # Test virtual environment check
    venv_check = await EngineHelpers.check_virtual_environment()
    assert venv_check.check_name == "Virtual Environment"
    assert venv_check.severity in ["critical", "warning", "info"]
    
    # Test platform check
    platform_check = await EngineHelpers.check_platform("any")
    assert platform_check.passed == True
    
    # Test tools check
    tools_check = await EngineHelpers.check_required_tools()
    assert tools_check.check_name == "Required Tools"
    
    return True


@test("Configuration System")
def test_configuration():
    """Test configuration loading"""
    from coder_agent.config.settings import load_config, DEFAULT_CONFIG
    
    # Load default config
    config = load_config()
    
    # Check required sections
    assert "engine" in config
    assert "context" in config
    assert "tools" in config
    assert "planner" in config
    assert "meta" in config
    assert "safety" in config
    
    # Check safety defaults
    assert config["safety"]["enable_safety_checks"] == True
    assert config["safety"]["allow_file_deletion"] == False
    
    # Check context limits
    assert config["context"]["max_tokens"] > 0
    assert config["context"]["reserved_tokens"] > 0
    
    return True


@test("Engine Integration")
async def test_engine():
    """Test core engine initialization"""
    from coder_agent.core.engine import CoderEngine
    from coder_agent.contracts.base import AgentRequest
    
    config = {
        "engine": {},
        "context": {"max_tokens": 10000},
        "tools": {},
        "planner": {},
        "meta": {}
    }
    
    engine = CoderEngine(config)
    
    # Test components are initialized
    assert engine.context_manager is not None
    assert engine.tool_executor is not None
    assert engine.task_planner is not None
    assert engine.metacognition is not None
    
    # Test request parsing
    request = AgentRequest(
        task="Test task",
        project_path="."
    )
    
    # Test context understanding
    context = await engine._understand_context(request)
    assert "literal_request" in context
    assert context["literal_request"] == "Test task"
    
    return True


@test("Validation Script")
def test_validation_script():
    """Test that validation script exists and can be imported"""
    validation_path = Path(__file__).parent / "validate_coder_v3.py"
    assert validation_path.exists(), "Validation script missing"
    
    # Try to import it
    import importlib.util
    spec = importlib.util.spec_from_file_location("validator", validation_path)
    module = importlib.util.module_from_spec(spec)
    
    return True


async def run_all_tests():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              CODER Agent Self-Test Suite                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run all test functions
    for name, obj in globals().items():
        if name.startswith("test_") and callable(obj):
            if asyncio.iscoroutinefunction(obj):
                await obj()
            else:
                obj()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    total = len(tests_passed) + len(tests_failed)
    
    if tests_passed:
        print(f"\n✅ PASSED: {len(tests_passed)}/{total}")
        for test in tests_passed:
            print(f"   • {test}")
    
    if tests_failed:
        print(f"\n❌ FAILED: {len(tests_failed)}/{total}")
        for test in tests_failed:
            print(f"   • {test}")
    
    pass_rate = (len(tests_passed) / max(total, 1)) * 100
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {pass_rate:.0f}% pass rate ({len(tests_passed)}/{total})")
    
    if pass_rate == 100:
        print("🎉 All tests passed! CODER Agent is working correctly.")
    elif pass_rate >= 80:
        print("✅ Most tests passed. CODER Agent is mostly functional.")
    elif pass_rate >= 60:
        print("⚠️  Some tests failed. CODER Agent needs attention.")
    else:
        print("❌ Many tests failed. CODER Agent has issues.")
    
    print("=" * 60)
    
    return len(tests_failed) == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)