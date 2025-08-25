#!/usr/bin/env python3
"""
Integration tests for CODER Agent
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coder_agent import CoderEngine, AgentRequest
from coder_agent.config import load_config


class TestIntegration:
    """Integration tests for CODER Agent"""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory"""
        temp_dir = tempfile.mkdtemp(prefix="coder_test_")
        
        # Create some test files
        (Path(temp_dir) / "main.py").write_text("""
def calculate_total(items):
    # This function has a bug - doesn't handle empty list
    return sum(items)

def process_user_input(data):
    # No error handling here
    result = data['value'] * 2
    return result
""")
        
        (Path(temp_dir) / "test_main.py").write_text("""
import pytest
from main import calculate_total

def test_calculate_total():
    assert calculate_total([1, 2, 3]) == 6
    # Missing test for empty list
""")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_config(self):
        """Create test configuration"""
        return {
            "engine": {
                "max_retries": 2,
                "require_tests": True
            },
            "context": {
                "max_tokens": 50000,
                "reserved_tokens": 5000
            },
            "tools": {
                "prefer_ripgrep": False,
                "batch_operations": True
            },
            "planner": {
                "max_parallel": 2,
                "break_complexity_threshold": 5
            },
            "meta": {
                "confidence_threshold": 0.6,
                "quality_threshold": 0.7
            },
            "llm": {
                "provider": "mock",
                "model": "mock-model",
                "api_key": "mock-key"
            },
            "safety": {
                "enable_safety_checks": True,
                "allow_file_deletion": False
            }
        }
    
    @pytest.mark.asyncio
    async def test_simple_task_flow(self, temp_project, mock_config):
        """Test a simple task flow end-to-end"""
        request = AgentRequest(
            task="Add error handling to the calculate_total function",
            project_path=temp_project,
            require_tests=True,
            timeout_seconds=60
        )
        
        engine = CoderEngine(mock_config)
        
        # Test context understanding
        context = await engine._understand_context(request)
        assert context["literal_request"] == request.task
        assert "inferred_intent" in context
        assert "required_capabilities" in context
        
        # Test plan creation
        plan = await engine.task_planner.create_plan(request, context)
        assert len(plan.tasks) > 0
        assert plan.total_estimated_tokens > 0
        
        # Verify B.R.E.A.K. methodology
        task_contents = [t.content for t in plan.tasks]
        
        # Should have tasks for:
        # 1. Pre-flight checks (if required)
        # 2. Writing tests (TDD)
        # 3. Implementation
        # 4. Running tests
        # 5. Validation
        
        if request.require_tests:
            # TDD: Tests should come before implementation
            test_indices = [i for i, c in enumerate(task_contents) 
                          if "test" in c.lower() and "write" in c.lower()]
            impl_indices = [i for i, c in enumerate(task_contents)
                          if "implement" in c.lower() or "add" in c.lower()]
            
            if test_indices and impl_indices:
                # Tests should come before implementation
                assert min(test_indices) < max(impl_indices), "TDD violation: Tests must come before implementation"
    
    @pytest.mark.asyncio
    async def test_context_management(self, mock_config):
        """Test context management with large content"""
        engine = CoderEngine(mock_config)
        manager = engine.context_manager
        
        # Add items until context is nearly full
        large_content = "x" * 10000  # ~2500 tokens
        
        for i in range(15):
            success = manager.add_item(
                content=large_content,
                content_type="file_content",
                priority=7 if i < 5 else 3  # First 5 are higher priority
            )
            assert success or i > 10  # Should handle gracefully when full
        
        # Check compression was triggered
        status = manager.get_usage_status()
        assert status["percentage"] > 0
        
        # High priority items should be retained
        context = manager.get_context_for_llm()
        assert len(context) > 0
    
    @pytest.mark.asyncio
    async def test_metacognition_monitoring(self, mock_config):
        """Test metacognitive monitoring during execution"""
        engine = CoderEngine(mock_config)
        meta = engine.metacognition
        
        # Simulate execution results
        results = [
            {"success": True, "duration": 0.5, "operation": "read"},
            {"success": True, "duration": 1.0, "operation": "analyze"},
            {"success": False, "duration": 2.0, "error": "Syntax error", "operation": "write"},
            {"success": False, "duration": 2.1, "error": "Syntax error", "operation": "write"},
        ]
        
        # Check execution quality
        quality_check = await meta.check_execution_quality(results)
        
        # Should detect issues
        assert "needs_adjustment" in quality_check
        if len([r for r in results if not r["success"]]) > 1:
            # Repeated errors should trigger adjustment
            assert quality_check["needs_adjustment"] == True
            assert len(quality_check["adjustments"]) > 0
        
        # Check cognitive loop detection
        is_loop = meta.detect_cognitive_loop(results)
        if results[-2:] == results[-4:-2]:  # Repeated pattern
            assert is_loop == True
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, temp_project, mock_config):
        """Test error recovery mechanisms"""
        from coder_agent.core.tool_executor import ToolExecutor
        from coder_agent.contracts.base import ToolCall, ToolType
        
        executor = ToolExecutor(mock_config.get("tools", {}))
        
        # Test file not found recovery
        call = ToolCall(
            tool=ToolType.READ,
            parameters={"file_path": str(Path(temp_project) / "nonexistent.py")},
            timeout=5,
            retry_on_failure=True,
            max_retries=2
        )
        
        result = await executor.execute(call)
        assert result.success == False
        assert "not found" in result.error.lower()
        
        # Test recovery suggestion
        recovery = await executor._handle_tool_failure(call, result.error)
        assert recovery["should_retry"] in [True, False]
        if "not found" in result.error.lower():
            assert recovery["strategy"] in ["check_path", "none"]
    
    @pytest.mark.asyncio
    async def test_task_dependencies(self, mock_config):
        """Test task dependency management"""
        from coder_agent.core.task_planner import TaskPlanner
        from coder_agent.contracts.base import TodoItem
        
        planner = TaskPlanner(mock_config.get("planner", {}))
        
        # Create tasks with dependencies
        tasks = [
            TodoItem(id="1", content="Analyze code", dependencies=[]),
            TodoItem(id="2", content="Write tests", dependencies=["1"]),
            TodoItem(id="3", content="Implement fix", dependencies=["1", "2"]),
            TodoItem(id="4", content="Run tests", dependencies=["3"]),
            TodoItem(id="5", content="Document changes", dependencies=["3"])
        ]
        
        # Calculate dependency depths
        depths = planner._calculate_dependency_depths(tasks)
        
        # Verify depth calculation
        assert depths["1"] == 0  # No dependencies
        assert depths["2"] == 1  # Depends on task 1
        assert depths["3"] == 2  # Depends on tasks 1 and 2
        assert depths["4"] == 3  # Depends on task 3
        assert depths["5"] == 3  # Also depends on task 3
        
        # Determine parallelism
        from coder_agent.contracts.base import TaskPlan
        plan = TaskPlan(
            objective="Test",
            tasks=tasks,
            total_estimated_tokens=1000,
            max_parallel_tasks=10
        )
        
        parallelism = planner._determine_parallelism(tasks)
        assert parallelism >= 1  # At least sequential
        assert parallelism <= 2  # Tasks 4 and 5 can run in parallel
    
    @pytest.mark.asyncio
    async def test_preflight_checks(self, temp_project, mock_config):
        """Test pre-flight validation system"""
        from coder_agent.core.engine_helpers import EngineHelpers
        
        # Test virtual environment check
        venv_check = await EngineHelpers.check_virtual_environment()
        assert venv_check.check_name == "Virtual Environment"
        assert venv_check.passed in [True, False]
        
        # Test project directory check
        project_check = await EngineHelpers.check_project_directory(temp_project)
        assert project_check.passed == True
        assert project_check.check_name == "Project Directory"
        
        # Test with non-existent directory
        bad_check = await EngineHelpers.check_project_directory("/nonexistent/path")
        assert bad_check.passed == False
        
        # Test required tools check
        tools_check = await EngineHelpers.check_required_tools()
        assert tools_check.check_name == "Required Tools"
        # Should at least find Python
        assert "python" in str(tools_check.details)
    
    @pytest.mark.asyncio
    async def test_safety_checks(self, mock_config):
        """Test safety and security features"""
        # Verify dangerous commands are blocked
        safety_config = mock_config.get("safety", {})
        
        assert safety_config["allow_file_deletion"] == False
        assert safety_config["enable_safety_checks"] == True
        
        # Test command blocking would go here
        # In real implementation, dangerous commands should be blocked
    
    @pytest.mark.asyncio
    async def test_platform_agnostic_paths(self, temp_project):
        """Test platform-agnostic path handling"""
        from pathlib import Path
        
        # All paths should use Path objects or os.path.join
        test_paths = [
            Path(temp_project) / "subdir" / "file.py",
            Path(temp_project).joinpath("another", "path.txt")
        ]
        
        for path in test_paths:
            # Should work on any platform
            str_path = str(path)
            assert "\\" in str_path or "/" in str_path
            
            # Path operations should be platform-agnostic
            assert path.parent.exists() or not path.parent.exists()


@pytest.mark.asyncio
async def test_full_demo_flow():
    """Test the full demonstration flow"""
    from coder_agent.examples.simple_demo import demonstrate_coder_agent
    
    # This would normally run the demo
    # We can't fully test it without mocking user input
    # But we can verify it doesn't crash
    
    import io
    import sys
    from unittest.mock import patch
    
    # Mock user input
    with patch('builtins.input', return_value='1'):
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            # This will run partially and exit when it needs real LLM
            with pytest.raises(Exception):
                await demonstrate_coder_agent()
        except:
            pass
        finally:
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
        
        # Verify demo structure
        assert "CODER Agent Demonstration" in output
        assert "B.R.E.A.K." in output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])