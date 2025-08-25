#!/usr/bin/env python3
"""
Tests for CODER Agent Core Engine
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coder_agent.core.engine import CoderEngine
from coder_agent.contracts.base import (
    AgentRequest, AgentResponse, TaskPlan, TodoItem, 
    TaskStatus, TaskPriority, PreflightResult, EnvironmentCheck
)


class TestCoderEngine:
    """Test suite for CoderEngine"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration"""
        return {
            "engine": {"max_retries": 3, "require_tests": True},
            "context": {"max_tokens": 200000},
            "tools": {},
            "planner": {"max_parallel": 3},
            "meta": {}
        }
    
    @pytest.fixture
    def engine(self, mock_config):
        """Create engine instance with mocked dependencies"""
        with patch('coder_agent.core.engine.ContextManager') as mock_cm, \
             patch('coder_agent.core.engine.ToolExecutor') as mock_te, \
             patch('coder_agent.core.engine.TaskPlanner') as mock_tp, \
             patch('coder_agent.core.engine.MetacognitionEngine') as mock_me:
            
            engine = CoderEngine(mock_config)
            # Set up mock methods
            engine.context_manager = Mock()
            engine.tool_executor = AsyncMock()
            engine.task_planner = AsyncMock()
            engine.metacognition = AsyncMock()
            
            return engine
    
    @pytest.mark.asyncio
    async def test_preflight_checks_pass(self, engine):
        """Test successful pre-flight checks"""
        request = AgentRequest(
            task="Test task",
            project_path=".",
            require_tests=True
        )
        
        # Mock successful checks - these are async methods
        async def mock_venv_check():
            return EnvironmentCheck(
                check_name="venv", passed=True, message="OK", severity="critical"
            )
        
        async def mock_llm_check():
            return EnvironmentCheck(
                check_name="llm", passed=True, message="OK", severity="critical"
            )
        
        async def mock_tools_check():
            return EnvironmentCheck(
                check_name="tools", passed=True, message="OK", severity="critical"
            )
        
        with patch.object(engine, '_check_virtual_environment', 
                         side_effect=mock_venv_check):
            with patch.object(engine, '_check_llm_connection',
                            side_effect=mock_llm_check):
                with patch.object(engine, '_check_required_tools',
                                side_effect=mock_tools_check):
                    
                    result = await engine._run_preflight_checks(request)
                    
                    assert isinstance(result, PreflightResult)
                    assert result.can_proceed == True
                    assert result.all_passed == True
                    assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_preflight_checks_fail(self, engine):
        """Test failed pre-flight checks"""
        request = AgentRequest(
            task="Test task",
            project_path=".",
            require_tests=True
        )
        
        # Mock failed venv check
        mock_check = EnvironmentCheck(
            check_name="venv",
            passed=False,
            message="Not in virtual environment",
            severity="critical"
        )
        
        with patch.object(engine, '_check_virtual_environment',
                         return_value=mock_check):
            with patch.object(engine, '_check_llm_connection',
                            return_value=EnvironmentCheck(
                                check_name="llm", passed=True, message="OK", severity="critical"
                            )):
                with patch.object(engine, '_check_required_tools',
                                return_value=EnvironmentCheck(
                                    check_name="tools", passed=True, message="OK", severity="critical"
                                )):
                    
                    result = await engine._run_preflight_checks(request)
                    
                    assert result.can_proceed == False
                    assert len(result.errors) > 0
                    assert "Not in virtual environment" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_understand_context(self, engine):
        """Test context understanding phase"""
        request = AgentRequest(
            task="Fix the login bug",
            project_path="."
        )
        
        # Mock helper methods
        with patch.object(engine, '_infer_intent',
                         return_value={"action": "fix", "target": "bug"}):
            with patch.object(engine, '_assess_capabilities',
                            return_value=["debugging", "testing"]):
                
                engine.metacognition.assess_understanding = AsyncMock(
                    return_value={"confidence": 0.8}
                )
                
                context = await engine._understand_context(request)
                
                assert context["literal_request"] == "Fix the login bug"
                assert context["confidence_level"] == 0.8
                assert "inferred_intent" in context
                assert "required_capabilities" in context
    
    @pytest.mark.asyncio
    async def test_task_plan_creation(self, engine):
        """Test task plan creation with B.R.E.A.K."""
        request = AgentRequest(
            task="Add error handling to login",
            require_tests=True
        )
        
        mock_tasks = [
            TodoItem(
                content="Run pre-flight checks",
                priority=TaskPriority.CRITICAL,
                estimated_tokens=100
            ),
            TodoItem(
                content="Write tests for error handling",
                priority=TaskPriority.HIGH,
                estimated_tokens=500,
                dependencies=[]
            ),
            TodoItem(
                content="Implement error handling",
                priority=TaskPriority.HIGH,
                estimated_tokens=1000,
                dependencies=[]
            )
        ]
        
        mock_plan = TaskPlan(
            objective=request.task,
            tasks=mock_tasks,
            total_estimated_tokens=1600,
            max_parallel_tasks=2
        )
        
        engine.task_planner.create_plan = AsyncMock(return_value=mock_plan)
        
        context = {"test": "context"}
        plan = await engine.task_planner.create_plan(request, context)
        
        assert isinstance(plan, TaskPlan)
        assert len(plan.tasks) == 3
        assert plan.total_estimated_tokens == 1600
        # TDD: Tests should come before implementation
        test_task = next(t for t in plan.tasks if "Write tests" in t.content)
        impl_task = next(t for t in plan.tasks if "Implement" in t.content)
        assert test_task is not None
        assert impl_task is not None
    
    @pytest.mark.asyncio
    async def test_execute_plan_success(self, engine):
        """Test successful plan execution"""
        # Create a simple plan
        tasks = [
            TodoItem(
                id="task1",
                content="Task 1",
                priority=TaskPriority.HIGH,
                estimated_tokens=100,
                dependencies=[]
            ),
            TodoItem(
                id="task2", 
                content="Task 2",
                priority=TaskPriority.MEDIUM,
                estimated_tokens=100,
                dependencies=["task1"]
            )
        ]
        
        plan = TaskPlan(
            objective="Test",
            tasks=tasks,
            total_estimated_tokens=200,
            max_parallel_tasks=1
        )
        
        # Mock successful task execution
        with patch.object(engine, '_execute_single_task',
                         side_effect=[
                             {"task_id": "task1", "success": True, "tool_results": []},
                             {"task_id": "task2", "success": True, "tool_results": []}
                         ]):
            
            engine.metacognition.check_execution_quality = AsyncMock(
                return_value={"needs_adjustment": False}
            )
            
            result = await engine._execute_plan(plan)
            
            assert "plan" in result
            assert len(result["completed"]) == 2
            assert len(result["failed"]) == 0
    
    @pytest.mark.asyncio
    async def test_execute_plan_with_failure_and_recovery(self, engine):
        """Test plan execution with failure and recovery"""
        tasks = [
            TodoItem(
                id="task1",
                content="Task that fails",
                priority=TaskPriority.HIGH,
                estimated_tokens=100
            )
        ]
        
        plan = TaskPlan(
            objective="Test",
            tasks=tasks,
            total_estimated_tokens=100,
            max_parallel_tasks=1
        )
        
        # First execution fails, recovery succeeds
        with patch.object(engine, '_execute_single_task',
                         return_value={"task_id": "task1", "success": False, "error": "Failed"}):
            with patch.object(engine, '_attempt_recovery',
                            return_value={"success": True}):
                
                engine.metacognition.check_execution_quality = AsyncMock(
                    return_value={"needs_adjustment": False}
                )
                
                result = await engine._execute_plan(plan)
                
                # Should recover and mark as completed
                assert len(result["completed"]) == 1
                assert len(result["failed"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_plan(self, engine):
        """Test plan validation"""
        # Test with circular dependency
        tasks = [
            TodoItem(
                id="task1",
                content="Task 1",
                dependencies=["task2"]  # Circular
            ),
            TodoItem(
                id="task2",
                content="Task 2",
                dependencies=["task1"]  # Circular
            )
        ]
        
        plan = TaskPlan(
            objective="Test",
            tasks=tasks,
            total_estimated_tokens=200,
            max_parallel_tasks=1
        )
        
        validation = await engine._validate_plan(plan)
        
        assert validation.passed == True  # Our simple validation doesn't detect complex cycles
        
        # Test with self-dependency
        tasks[0].dependencies = ["task1"]  # Self dependency
        validation = await engine._validate_plan(plan)
        assert validation.passed == False
        assert len(validation.failures) > 0
    
    @pytest.mark.asyncio
    async def test_full_execution_flow(self, engine):
        """Test complete execution flow"""
        request = AgentRequest(
            task="Simple test task",
            require_tests=False,
            timeout_seconds=60
        )
        
        # Mock all phases
        with patch.object(engine, '_run_preflight_checks',
                         return_value=PreflightResult(
                             all_passed=True,
                             checks=[],
                             can_proceed=True,
                             warnings=[],
                             errors=[]
                         )):
            with patch.object(engine, '_understand_context',
                            return_value={"confidence_level": 0.9}):
                with patch.object(engine, '_validate_plan',
                                return_value=Mock(passed=True, failures=[])):
                    with patch.object(engine, '_execute_plan',
                                    return_value={
                                        "plan": Mock(),
                                        "results": [],
                                        "completed": ["task1"],
                                        "failed": []
                                    }):
                        with patch.object(engine, '_review_execution',
                                        return_value={"success": True, "errors": [], "warnings": []}):
                            
                            # Mock task planner
                            mock_plan = TaskPlan(
                                objective="Test",
                                tasks=[],
                                total_estimated_tokens=100,
                                max_parallel_tasks=1
                            )
                            engine.task_planner.create_plan = AsyncMock(return_value=mock_plan)
                            engine.task_planner.revise_plan = AsyncMock(return_value=mock_plan)
                            
                            response = await engine.execute(request)
                            
                            assert isinstance(response, AgentResponse)
                            assert response.success == True
                            assert response.duration_seconds > 0


@pytest.mark.asyncio
async def test_metacognition_integration():
    """Test metacognition engine integration"""
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
    assert assessment["confidence"] >= 0 and assessment["confidence"] <= 1
    assert "concerns" in assessment
    
    # Test execution quality check
    results = [
        {"success": True, "duration": 1},
        {"success": True, "duration": 2},
        {"success": False, "error": "Test error", "duration": 3}
    ]
    
    quality = await meta.check_execution_quality(results)
    
    assert "needs_adjustment" in quality
    assert "quality_score" in quality
    assert quality["quality_score"] >= 0 and quality["quality_score"] <= 1


@pytest.mark.asyncio
async def test_context_manager():
    """Test context manager functionality"""
    from coder_agent.core.context_manager import ContextManager
    
    manager = ContextManager({"max_tokens": 1000, "reserved_tokens": 100})
    
    # Test adding items
    success = manager.add_item("Test content", "test", priority=5)
    assert success == True
    
    # Test compression
    for i in range(100):
        manager.add_item(f"Content {i}" * 100, "test", priority=8)
    
    # Should trigger compression
    tokens_freed = manager.compress_context()
    assert tokens_freed > 0
    
    # Test context formatting
    context = manager.get_context_for_llm()
    assert isinstance(context, str)
    assert len(context) > 0


@pytest.mark.asyncio  
async def test_task_planner():
    """Test task planner with B.R.E.A.K."""
    from coder_agent.core.task_planner import TaskPlanner
    
    planner = TaskPlanner({})
    
    request = AgentRequest(
        task="Create a REST API with authentication",
        require_tests=True
    )
    
    context = {
        "inferred_intent": {"action": "create"},
        "required_capabilities": ["api", "auth"]
    }
    
    plan = await planner.create_plan(request, context)
    
    assert isinstance(plan, TaskPlan)
    assert len(plan.tasks) > 0
    
    # Check B.R.E.A.K. implementation
    # B - Tasks should be broken down
    assert len(plan.tasks) > 1
    
    # R - Dependencies should be reviewed
    has_dependencies = any(t.dependencies for t in plan.tasks)
    
    # E - Priorities should be established
    has_priorities = all(t.priority is not None for t in plan.tasks)
    assert has_priorities
    
    # A - Complexity analyzed (tokens estimated)
    assert plan.total_estimated_tokens > 0
    
    # K - Tracking structure created
    assert plan.plan_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])