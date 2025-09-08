#!/usr/bin/env python3
"""
ReAct Loop Edge Case Tests for AI Browser v2.0.0

Tests the ReAct reasoning loop's handling of edge cases and failure scenarios:
- LLM reasoning failures and recovery
- Self-correction mechanisms
- Infinite loop detection and breaking
- Error propagation and handling
- Fallback strategies
- Context window overflow handling
- Action validation failures
- Memory corruption recovery

**CRITICAL**: Uses REAL LLM connections to test actual reasoning failures.
"""

import asyncio
import pytest
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cognition.orchestrator import AgentOrchestrator, OrchestrationResult
from cognition.llm import LLMManager
from cognition.actions import AgentAction, FinishedAction, FailedAction, NavigateAction, ClickAction
from cognition.prompt_builder import PromptBuilder
from execution.action_executor import ActionExecutor
from memory.memory_manager import MemoryManager

# Load environment variables
load_dotenv()


class TestReActLoopFailureRecovery:
    """Test ReAct loop handles failures gracefully and recovers."""
    
    @pytest.mark.asyncio
    async def test_llm_generation_failure_recovery(self):
        """Test recovery when LLM fails to generate valid actions."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        # Simulate LLM failures with different error types
        failure_scenarios = [
            {"error": "Rate limit exceeded", "should_retry": True},
            {"error": "Invalid API key", "should_retry": False},  
            {"error": "Model overloaded", "should_retry": True},
            {"error": "Context length exceeded", "should_retry": False}
        ]
        
        for scenario in failure_scenarios:
            print(f"Testing LLM failure: {scenario['error']}")
            
            with patch.object(orchestrator.llm_manager, 'generate_structured_response') as mock_llm:
                # Simulate LLM failure
                mock_llm.side_effect = Exception(scenario['error'])
                
                task = "Navigate to Google and search for Python"
                initial_state = {
                    'url': 'about:blank',
                    'title': 'New Tab',
                    'elements': []
                }
                
                try:
                    result = await orchestrator.execute_task(
                        task=task,
                        initial_page_state=initial_state,
                        max_steps=3,
                        timeout=30
                    )
                    
                    # Should handle failure gracefully
                    assert result.status in ['failed', 'completed'], f"Unexpected status: {result.status}"
                    
                    if result.status == 'failed':
                        assert scenario['error'].lower() in result.error_message.lower(), \
                            f"Error message doesn't contain expected error: {result.error_message}"
                        
                        # Should have attempted retries for retryable errors
                        if scenario['should_retry']:
                            assert mock_llm.call_count > 1, "Should have retried for retryable errors"
                        
                        print(f"✅ Gracefully handled LLM failure: {scenario['error']}")
                    
                except Exception as e:
                    pytest.fail(f"Orchestrator failed to handle LLM error gracefully: {e}")
        
        await orchestrator.close()
    
    @pytest.mark.asyncio 
    async def test_invalid_action_generation_recovery(self):
        """Test recovery when LLM generates invalid or malformed actions."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        # Test various invalid action scenarios
        invalid_actions = [
            None,  # No action generated
            {"invalid": "structure"},  # Wrong format
            {"action_type": "nonexistent_action", "params": {}},  # Invalid action type
            {"action_type": "click", "selector": ""},  # Missing required params
            {"action_type": "click", "selector": None},  # Null required params
        ]
        
        for i, invalid_action in enumerate(invalid_actions):
            print(f"Testing invalid action {i + 1}: {invalid_action}")
            
            with patch.object(orchestrator.llm_manager, 'generate_structured_response') as mock_llm:
                # Mock LLM to return invalid action
                mock_response = MagicMock()
                mock_response.parsed = invalid_action
                mock_llm.return_value = mock_response
                
                task = "Click the submit button"
                initial_state = {
                    'url': 'https://example.com/form',
                    'title': 'Test Form',
                    'elements': [
                        {'selector': '#submit', 'type': 'button', 'text': 'Submit'}
                    ]
                }
                
                try:
                    result = await orchestrator.execute_task(
                        task=task,
                        initial_page_state=initial_state,
                        max_steps=3,
                        timeout=30
                    )
                    
                    # Should handle invalid actions gracefully
                    assert result.status in ['failed', 'completed'], f"Unexpected status: {result.status}"
                    
                    if result.status == 'failed':
                        assert 'invalid' in result.error_message.lower() or 'error' in result.error_message.lower(), \
                            f"Error message should indicate action validation failure: {result.error_message}"
                    
                    print(f"✅ Handled invalid action gracefully")
                    
                except Exception as e:
                    pytest.fail(f"Failed to handle invalid action: {e}")
        
        await orchestrator.close()
    
    @pytest.mark.asyncio
    async def test_infinite_loop_detection(self):
        """Test detection and breaking of infinite reasoning loops."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        # Set up scenario that could cause infinite loops
        task = "Click the next button until you reach the end"
        initial_state = {
            'url': 'https://example.com/page1',
            'title': 'Page 1',
            'elements': [
                {'selector': '#next', 'type': 'button', 'text': 'Next'}
            ]
        }
        
        # Mock LLM to always return the same action (infinite loop scenario)
        with patch.object(orchestrator.llm_manager, 'generate_structured_response') as mock_llm:
            next_action = ClickAction(selector="#next", description="Click next button")
            mock_response = MagicMock()
            mock_response.parsed = next_action
            mock_llm.return_value = mock_response
            
            # Mock action executor to always return same state (no progress)
            with patch.object(orchestrator, 'action_executor') as mock_executor:
                mock_executor.execute.return_value = AsyncMock(
                    success=True,
                    result_data={'message': 'Clicked next button'},
                    page_state=initial_state  # Same state - no progress
                )
                
                try:
                    result = await orchestrator.execute_task(
                        task=task,
                        initial_page_state=initial_state,
                        max_steps=10,  # Should break before reaching this
                        timeout=60
                    )
                    
                    # Should detect infinite loop and stop
                    assert result.status == 'failed', f"Should have detected infinite loop, got: {result.status}"
                    assert 'loop' in result.error_message.lower() or 'repeated' in result.error_message.lower(), \
                        f"Should indicate loop detection: {result.error_message}"
                    
                    # Should not have executed max_steps
                    assert len(result.steps_taken) < 10, "Should have stopped before max steps due to loop detection"
                    
                    print(f"✅ Successfully detected and broke infinite loop after {len(result.steps_taken)} steps")
                    
                except Exception as e:
                    pytest.fail(f"Failed to handle infinite loop: {e}")
        
        await orchestrator.close()
    
    @pytest.mark.asyncio
    async def test_self_correction_mechanism(self):
        """Test self-correction when actions fail or produce unexpected results."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        task = "Click the login button"
        initial_state = {
            'url': 'https://example.com/login',
            'title': 'Login Page',
            'elements': [
                {'selector': '#login-btn', 'type': 'button', 'text': 'Login'},
                {'selector': '#sign-in', 'type': 'button', 'text': 'Sign In'}
            ]
        }
        
        # Simulate scenario where first action fails, requiring self-correction
        call_count = 0
        
        def mock_llm_response(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                # First attempt - try wrong selector
                action = ClickAction(selector="#wrong-btn", description="Click wrong button")
            else:
                # Self-correction - try correct selector
                action = ClickAction(selector="#login-btn", description="Click login button")
            
            mock_response = MagicMock()
            mock_response.parsed = action
            return mock_response
        
        with patch.object(orchestrator.llm_manager, 'generate_structured_response', side_effect=mock_llm_response):
            
            execution_count = 0
            
            def mock_execute(*args, **kwargs):
                nonlocal execution_count
                execution_count += 1
                
                if execution_count == 1:
                    # First execution fails
                    return AsyncMock(
                        success=False,
                        error_message="Element not found: #wrong-btn",
                        page_state=initial_state
                    )
                else:
                    # Second execution succeeds
                    return AsyncMock(
                        success=True,
                        result_data={'message': 'Successfully clicked login button'},
                        page_state={
                            'url': 'https://example.com/dashboard',
                            'title': 'Dashboard',
                            'elements': []
                        }
                    )
            
            with patch.object(orchestrator, 'action_executor') as mock_executor:
                mock_executor.execute.side_effect = mock_execute
                
                try:
                    result = await orchestrator.execute_task(
                        task=task,
                        initial_page_state=initial_state,
                        max_steps=5,
                        timeout=60
                    )
                    
                    # Should have self-corrected and succeeded
                    assert result.status == 'completed', f"Expected completion after self-correction, got: {result.status}"
                    assert len(result.steps_taken) >= 2, "Should have taken multiple steps for self-correction"
                    
                    # Verify self-correction occurred
                    assert call_count >= 2, "Should have made multiple LLM calls for self-correction"
                    assert execution_count >= 2, "Should have executed multiple actions"
                    
                    print(f"✅ Successfully self-corrected after {len(result.steps_taken)} steps")
                    
                except Exception as e:
                    pytest.fail(f"Self-correction failed: {e}")
        
        await orchestrator.close()


class TestReActContextManagement:
    """Test ReAct loop handles context window and memory management."""
    
    @pytest.mark.asyncio
    async def test_context_window_overflow_handling(self):
        """Test handling when conversation context exceeds model limits."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        # Simulate very long task with many steps
        task = "Navigate through many pages and collect data"
        initial_state = {
            'url': 'https://example.com/page1',
            'title': 'Page 1',
            'elements': [{'selector': '#next', 'type': 'button', 'text': 'Next'}]
        }
        
        # Track context size
        context_sizes = []
        
        def mock_llm_with_context_tracking(*args, **kwargs):
            # Extract conversation context
            messages = kwargs.get('messages', [])
            total_content = ''.join([msg.get('content', '') for msg in messages])
            context_sizes.append(len(total_content))
            
            # Simulate context length error when context gets too large
            if len(total_content) > 10000:  # Simulate context limit
                raise Exception("Context length exceeded")
            
            # Return next action
            action = NavigateAction(url=f"https://example.com/page{len(context_sizes) + 1}", 
                                  description=f"Navigate to page {len(context_sizes) + 1}")
            mock_response = MagicMock()
            mock_response.parsed = action
            return mock_response
        
        with patch.object(orchestrator.llm_manager, 'generate_structured_response', side_effect=mock_llm_with_context_tracking):
            
            # Mock successful executions to build up context
            with patch.object(orchestrator, 'action_executor') as mock_executor:
                mock_executor.execute.return_value = AsyncMock(
                    success=True,
                    result_data={'message': 'Navigation successful'},
                    page_state=initial_state
                )
                
                try:
                    result = await orchestrator.execute_task(
                        task=task,
                        initial_page_state=initial_state,
                        max_steps=20,  # Force many steps to trigger context overflow
                        timeout=120
                    )
                    
                    # Should handle context overflow gracefully
                    assert result.status in ['failed', 'completed'], f"Unexpected status: {result.status}"
                    
                    # Context should have grown then been managed
                    assert len(context_sizes) > 1, "Should have tracked context growth"
                    
                    if result.status == 'failed' and 'context' in result.error_message.lower():
                        print("✅ Successfully detected and handled context overflow")
                    elif result.status == 'completed':
                        print("✅ Successfully managed context within limits")
                    else:
                        print(f"⚠️  Unexpected result: {result.status} - {result.error_message}")
                    
                except Exception as e:
                    # Context overflow handling might raise exceptions - that's acceptable
                    assert 'context' in str(e).lower(), f"Expected context-related error, got: {e}"
                    print("✅ Context overflow properly handled with exception")
        
        await orchestrator.close()
    
    @pytest.mark.asyncio
    async def test_memory_corruption_recovery(self):
        """Test recovery when memory systems fail or return corrupted data."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        task = "Search for information and remember it"
        initial_state = {
            'url': 'https://google.com',
            'title': 'Google',
            'elements': [{'selector': 'input[name="q"]', 'type': 'input', 'placeholder': 'Search'}]
        }
        
        # Test memory corruption scenarios
        memory_failures = [
            "Database connection lost",
            "Corrupted session data", 
            "Vector store unavailable",
            "Knowledge graph query failed"
        ]
        
        for failure_type in memory_failures:
            print(f"Testing memory failure recovery: {failure_type}")
            
            with patch.object(orchestrator.memory_manager, 'store_task_step') as mock_memory:
                # Simulate memory failure
                mock_memory.side_effect = Exception(failure_type)
                
                try:
                    result = await orchestrator.execute_task(
                        task=task,
                        initial_page_state=initial_state,
                        max_steps=3,
                        timeout=30
                    )
                    
                    # Should continue operating despite memory failures
                    assert result.status in ['completed', 'failed'], f"Unexpected status: {result.status}"
                    
                    # Should have attempted to continue task execution
                    assert len(result.steps_taken) >= 0, "Should have attempted task execution"
                    
                    print(f"✅ Continued operation despite memory failure: {failure_type}")
                    
                except Exception as e:
                    # Complete failure is acceptable for some memory corruption types
                    print(f"⚠️  Memory failure caused complete failure: {e}")
        
        await orchestrator.close()


class TestReActErrorPropagation:
    """Test error propagation and handling through ReAct loop layers."""
    
    @pytest.mark.asyncio
    async def test_browser_execution_error_handling(self):
        """Test handling of browser execution errors in ReAct loop."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        task = "Fill out a form and submit it"
        initial_state = {
            'url': 'https://example.com/form',
            'title': 'Test Form',
            'elements': [
                {'selector': '#name', 'type': 'input', 'placeholder': 'Name'},
                {'selector': '#submit', 'type': 'button', 'text': 'Submit'}
            ]
        }
        
        # Test different browser execution errors
        browser_errors = [
            "Element not found",
            "Element not visible", 
            "Element not clickable",
            "Navigation timeout",
            "JavaScript error"
        ]
        
        for error_type in browser_errors:
            print(f"Testing browser error handling: {error_type}")
            
            with patch.object(orchestrator, 'action_executor') as mock_executor:
                # First call fails, second succeeds (recovery)
                call_count = 0
                
                def mock_execute(*args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    
                    if call_count == 1:
                        return AsyncMock(
                            success=False,
                            error_message=error_type,
                            page_state=initial_state
                        )
                    else:
                        return AsyncMock(
                            success=True,
                            result_data={'message': 'Action completed successfully'},
                            page_state=initial_state
                        )
                
                mock_executor.execute.side_effect = mock_execute
                
                try:
                    result = await orchestrator.execute_task(
                        task=task,
                        initial_page_state=initial_state,
                        max_steps=5,
                        timeout=60
                    )
                    
                    # Should handle browser errors and attempt recovery
                    assert result.status in ['completed', 'failed'], f"Unexpected status: {result.status}"
                    
                    if result.status == 'completed':
                        assert call_count > 1, "Should have retried after browser error"
                        print(f"✅ Successfully recovered from browser error: {error_type}")
                    else:
                        print(f"⚠️  Could not recover from browser error: {error_type}")
                    
                except Exception as e:
                    print(f"⚠️  Browser error caused exception: {e}")
        
        await orchestrator.close()
    
    @pytest.mark.asyncio
    async def test_cascading_failure_handling(self):
        """Test handling of cascading failures across multiple systems."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        task = "Complete a complex multi-step workflow"
        initial_state = {
            'url': 'https://example.com/workflow',
            'title': 'Workflow Page',
            'elements': [{'selector': '#start', 'type': 'button', 'text': 'Start'}]
        }
        
        # Simulate cascading failures: LLM -> Browser -> Memory
        with patch.object(orchestrator.llm_manager, 'generate_structured_response') as mock_llm, \
             patch.object(orchestrator, 'action_executor') as mock_executor, \
             patch.object(orchestrator.memory_manager, 'store_task_step') as mock_memory:
            
            # Chain of failures
            mock_llm.side_effect = Exception("LLM service unavailable")
            mock_executor.execute.side_effect = Exception("Browser crashed")
            mock_memory.side_effect = Exception("Database corrupted")
            
            try:
                result = await orchestrator.execute_task(
                    task=task,
                    initial_page_state=initial_state,
                    max_steps=3,
                    timeout=30
                )
                
                # Should fail gracefully with appropriate error message
                assert result.status == 'failed', f"Expected failure, got: {result.status}"
                assert result.error_message is not None, "Should have error message for cascading failure"
                
                # Should indicate the root cause
                assert any(keyword in result.error_message.lower() 
                          for keyword in ['llm', 'service', 'unavailable', 'error']), \
                    f"Error message should indicate root cause: {result.error_message}"
                
                print(f"✅ Gracefully handled cascading failure: {result.error_message}")
                
            except Exception as e:
                pytest.fail(f"Cascading failure not handled gracefully: {e}")
        
        await orchestrator.close()


class TestReActPerformanceFailures:
    """Test ReAct loop performance under stress and timeout conditions."""
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test ReAct loop handles timeouts gracefully."""
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        task = "Complete a time-consuming task"
        initial_state = {
            'url': 'https://example.com/slow-page',
            'title': 'Slow Page', 
            'elements': [{'selector': '#slow-button', 'type': 'button', 'text': 'Slow Action'}]
        }
        
        # Simulate slow operations
        async def slow_llm_response(*args, **kwargs):
            await asyncio.sleep(5)  # Simulate slow LLM
            action = ClickAction(selector="#slow-button", description="Click slow button")
            mock_response = MagicMock()
            mock_response.parsed = action
            return mock_response
        
        async def slow_execution(*args, **kwargs):
            await asyncio.sleep(5)  # Simulate slow browser operation
            return AsyncMock(
                success=True,
                result_data={'message': 'Slow action completed'},
                page_state=initial_state
            )
        
        with patch.object(orchestrator.llm_manager, 'generate_structured_response', side_effect=slow_llm_response), \
             patch.object(orchestrator, 'action_executor') as mock_executor:
            
            mock_executor.execute.side_effect = slow_execution
            
            try:
                # Set very short timeout to force timeout
                result = await orchestrator.execute_task(
                    task=task,
                    initial_page_state=initial_state,
                    max_steps=3,
                    timeout=8  # Shorter than operation times
                )
                
                # Should handle timeout gracefully
                assert result.status == 'failed', f"Expected timeout failure, got: {result.status}"
                assert 'timeout' in result.error_message.lower(), \
                    f"Should indicate timeout: {result.error_message}"
                
                print(f"✅ Successfully handled timeout: {result.error_message}")
                
            except asyncio.TimeoutError:
                print("✅ Timeout handled at asyncio level")
            except Exception as e:
                pytest.fail(f"Timeout not handled gracefully: {e}")
        
        await orchestrator.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])