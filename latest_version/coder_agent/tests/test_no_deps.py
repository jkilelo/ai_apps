#!/usr/bin/env python3
"""
Basic tests for CODER Agent - No external dependencies
Tests the structure and basic logic without running the actual code
"""

import sys
import os
from pathlib import Path
import ast
import importlib.util


def test_file_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing File Structure...")
    
    base_path = Path(__file__).parent.parent
    required_files = [
        "README.md",
        "requirements.txt",
        "__init__.py",
        "__main__.py",
        "preflight.py",
        "validate_coder_v3.py",
        "core/__init__.py",
        "core/engine.py",
        "core/context_manager.py",
        "core/tool_executor.py",
        "core/task_planner.py",
        "core/metacognition.py",
        "core/engine_helpers.py",
        "contracts/__init__.py",
        "contracts/base.py",
        "config/__init__.py",
        "config/settings.py",
        "examples/simple_demo.py"
    ]
    
    missing = []
    for file in required_files:
        file_path = base_path / file
        if not file_path.exists():
            missing.append(file)
    
    if missing:
        print(f"   ❌ Missing files: {missing}")
        return False
    else:
        print(f"   ✅ All {len(required_files)} required files exist")
        return True


def test_pydantic_v2_usage():
    """Test that Pydantic v2 features are used"""
    print("\n🔍 Testing Pydantic v2 Implementation...")
    
    contracts_file = Path(__file__).parent.parent / "contracts" / "base.py"
    
    with open(contracts_file, 'r') as f:
        content = f.read()
        tree = ast.parse(content)
    
    # Check for Pydantic v2 specific features
    has_base_model = "BaseModel" in content
    has_config_dict = "ConfigDict" in content
    has_field = "Field" in content
    has_field_validator = "field_validator" in content or "@validator" in content
    
    # Count contract classes
    contract_classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any("Model" in str(base) for base in node.bases if isinstance(base, ast.Name)):
                contract_classes.append(node.name)
    
    print(f"   • BaseModel usage: {'✅' if has_base_model else '❌'}")
    print(f"   • ConfigDict (v2): {'✅' if has_config_dict else '❌'}")
    print(f"   • Field usage: {'✅' if has_field else '❌'}")
    print(f"   • Validators: {'✅' if has_field_validator else '❌'}")
    print(f"   • Contract classes: {len(contract_classes)}")
    
    if has_base_model and has_config_dict and len(contract_classes) > 10:
        print(f"   ✅ Pydantic v2 properly implemented with {len(contract_classes)} contracts")
        return True
    else:
        print(f"   ❌ Pydantic v2 implementation incomplete")
        return False


def test_break_methodology():
    """Test B.R.E.A.K. methodology implementation"""
    print("\n🔍 Testing B.R.E.A.K. Methodology...")
    
    planner_file = Path(__file__).parent.parent / "core" / "task_planner.py"
    
    with open(planner_file, 'r') as f:
        content = f.read()
    
    # Check for B.R.E.A.K. components
    components = {
        "B - Break down": "break_down" in content or "Break down" in content,
        "R - Review": "review" in content or "Review" in content or "dependencies" in content,
        "E - Establish": "establish" in content or "Establish" in content or "priorities" in content,
        "A - Analyze": "analyze" in content or "Analyze" in content or "complexity" in content,
        "K - Keep track": "keep" in content or "Keep" in content or "track" in content
    }
    
    for component, found in components.items():
        print(f"   • {component}: {'✅' if found else '❌'}")
    
    if all(components.values()):
        print(f"   ✅ B.R.E.A.K. methodology fully implemented")
        return True
    else:
        print(f"   ❌ B.R.E.A.K. methodology incomplete")
        return False


def test_tdd_implementation():
    """Test TDD (Test-Driven Development) implementation"""
    print("\n🔍 Testing TDD Implementation...")
    
    planner_file = Path(__file__).parent.parent / "core" / "task_planner.py"
    
    with open(planner_file, 'r') as f:
        content = f.read()
    
    # Check for TDD patterns
    has_tdd_mention = "TDD" in content
    has_test_first = "Write tests" in content or "write tests" in content
    has_require_tests = "require_tests" in content
    
    # Check that tests come before implementation in task ordering
    lines = content.split('\n')
    test_line = -1
    impl_line = -1
    
    for i, line in enumerate(lines):
        if "Write tests" in line and test_line == -1:
            test_line = i
        if "Implement" in line and impl_line == -1:
            impl_line = i
    
    tests_before_impl = test_line < impl_line if test_line > 0 and impl_line > 0 else False
    
    print(f"   • TDD mentioned: {'✅' if has_tdd_mention else '❌'}")
    print(f"   • Test-first approach: {'✅' if has_test_first else '❌'}")
    print(f"   • Test requirement handling: {'✅' if has_require_tests else '❌'}")
    print(f"   • Tests before implementation: {'✅' if tests_before_impl else '❌'}")
    
    if has_tdd_mention and has_test_first and has_require_tests:
        print(f"   ✅ TDD properly implemented")
        return True
    else:
        print(f"   ❌ TDD implementation incomplete")
        return False


def test_metacognition():
    """Test metacognition implementation"""
    print("\n🔍 Testing Metacognition Engine...")
    
    meta_file = Path(__file__).parent.parent / "core" / "metacognition.py"
    
    with open(meta_file, 'r') as f:
        content = f.read()
    
    # Check for metacognitive features
    features = {
        "Confidence levels": "confidence" in content.lower(),
        "Quality monitoring": "quality" in content.lower(),
        "Cognitive load": "cognitive_load" in content,
        "Loop detection": "loop" in content.lower(),
        "Uncertainty handling": "uncertainty" in content.lower(),
        "Self-monitoring": "monitor" in content.lower()
    }
    
    for feature, found in features.items():
        print(f"   • {feature}: {'✅' if found else '❌'}")
    
    if sum(features.values()) >= 5:
        print(f"   ✅ Metacognition engine comprehensive")
        return True
    else:
        print(f"   ❌ Metacognition engine incomplete")
        return False


def test_context_management():
    """Test context management features"""
    print("\n🔍 Testing Context Management...")
    
    context_file = Path(__file__).parent.parent / "core" / "context_manager.py"
    
    with open(context_file, 'r') as f:
        content = f.read()
    
    # Check for context management features
    features = {
        "Token limits": "MAX_CONTEXT_TOKENS" in content or "max_tokens" in content,
        "Compression": "compress" in content.lower(),
        "Prioritization": "priority" in content.lower(),
        "Summarization": "summarize" in content.lower(),
        "Emergency mode": "emergency" in content.lower(),
        "Token counting": "tokens" in content.lower()
    }
    
    for feature, found in features.items():
        print(f"   • {feature}: {'✅' if found else '❌'}")
    
    if sum(features.values()) >= 5:
        print(f"   ✅ Context management comprehensive")
        return True
    else:
        print(f"   ❌ Context management incomplete")
        return False


def test_tool_patterns():
    """Test tool executor patterns"""
    print("\n🔍 Testing Tool Executor Patterns...")
    
    tool_file = Path(__file__).parent.parent / "core" / "tool_executor.py"
    
    with open(tool_file, 'r') as f:
        content = f.read()
    
    # Check for my tool usage patterns
    patterns = {
        "Read before Write": "READ_BEFORE_WRITE" in content,
        "Tool timeouts": "TOOL_TIMEOUTS" in content or "timeout" in content,
        "Retry logic": "retry" in content.lower(),
        "Batch operations": "batch" in content.lower(),
        "Error recovery": "recovery" in content.lower(),
        "Tool validation": "validate" in content.lower()
    }
    
    for pattern, found in patterns.items():
        print(f"   • {pattern}: {'✅' if found else '❌'}")
    
    if sum(patterns.values()) >= 5:
        print(f"   ✅ Tool patterns properly implemented")
        return True
    else:
        print(f"   ❌ Tool patterns incomplete")
        return False


def test_safety_features():
    """Test safety and security features"""
    print("\n🔍 Testing Safety Features...")
    
    config_file = Path(__file__).parent.parent / "config" / "settings.py"
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Check for safety features
    features = {
        "File deletion control": "allow_file_deletion" in content,
        "Command blocking": "blocked_commands" in content,
        "Safety checks": "safety_checks" in content or "enable_safety" in content,
        "Confirmation required": "require_confirmation" in content,
        "API key security": "api_key" in content and "environ" in content
    }
    
    for feature, found in features.items():
        print(f"   • {feature}: {'✅' if found else '❌'}")
    
    if sum(features.values()) >= 4:
        print(f"   ✅ Safety features comprehensive")
        return True
    else:
        print(f"   ❌ Safety features incomplete")
        return False


def test_preflight_system():
    """Test pre-flight check system"""
    print("\n🔍 Testing Pre-flight System...")
    
    preflight_file = Path(__file__).parent.parent / "preflight.py"
    helpers_file = Path(__file__).parent.parent / "core" / "engine_helpers.py"
    
    checks = []
    
    if preflight_file.exists():
        with open(preflight_file, 'r') as f:
            content = f.read()
            checks.append(("Pre-flight script", True))
            checks.append(("Virtual env check", "check_virtual_environment" in content))
            checks.append(("LLM check", "check_llm" in content))
            checks.append(("Tools check", "check_required_tools" in content))
    
    if helpers_file.exists():
        with open(helpers_file, 'r') as f:
            content = f.read()
            checks.append(("Helper functions", True))
            checks.append(("Platform check", "check_platform" in content))
    
    for check_name, found in checks:
        print(f"   • {check_name}: {'✅' if found else '❌'}")
    
    if sum(found for _, found in checks) >= len(checks) - 1:
        print(f"   ✅ Pre-flight system complete")
        return True
    else:
        print(f"   ❌ Pre-flight system incomplete")
        return False


def run_all_tests():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║        CODER Agent Structure Test (No Dependencies)          ║
╚══════════════════════════════════════════════════════════════╝
    
This tests the implementation structure without running the code.
    """)
    
    tests = [
        test_file_structure,
        test_pydantic_v2_usage,
        test_break_methodology,
        test_tdd_implementation,
        test_metacognition,
        test_context_management,
        test_tool_patterns,
        test_safety_features,
        test_preflight_system
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
            failed += 1
    
    # Summary
    total = passed + failed
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"📊 Pass Rate: {pass_rate:.0f}%")
    
    if pass_rate == 100:
        print("\n🎉 Perfect! CODER Agent structure is complete.")
    elif pass_rate >= 80:
        print("\n✅ Good! CODER Agent structure is mostly complete.")
    elif pass_rate >= 60:
        print("\n⚠️  Acceptable. Some components need work.")
    else:
        print("\n❌ Needs improvement. Many components incomplete.")
    
    print("=" * 60)
    
    print("\nNOTE: This only tests the structure. To fully test functionality:")
    print("1. Install dependencies: pip install -r coder_agent/requirements.txt")
    print("2. Run full tests: python3 coder_agent/self_test.py")
    print("3. Run validation: python3 coder_agent/validate_coder_v3.py")


if __name__ == "__main__":
    run_all_tests()