#!/usr/bin/env python3
"""
Tests for Tool Executor
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coder_agent.core.tool_executor import ToolExecutor
from coder_agent.contracts.base import ToolCall, ToolResult, ToolType


class TestToolExecutor:
    """Test suite for ToolExecutor"""
    
    @pytest.fixture
    def executor(self):
        """Create tool executor instance"""
        return ToolExecutor({})
    
    @pytest.mark.asyncio
    async def test_read_before_write_validation(self, executor):
        """Test that Read before Write rule is enforced"""
        # Try to edit without reading first
        call = ToolCall(
            tool=ToolType.EDIT,
            parameters={
                "file_path": "/test/file.py",
                "old_string": "old",
                "new_string": "new"
            },
            timeout=5,
            retry_on_failure=False,
            max_retries=0
        )
        
        with patch('pathlib.Path.exists', return_value=True):
            result = await executor.execute(call)
            
            # Should fail because file not read first
            assert result.success == False
            assert "Must read" in result.error
    
    @pytest.mark.asyncio
    async def test_read_operation_success(self, executor):
        """Test successful file read"""
        call = ToolCall(
            tool=ToolType.READ,
            parameters={"file_path": "/test/file.py"},
            timeout=5,
            retry_on_failure=False,
            max_retries=0
        )
        
        mock_content = "def test():\n    return True"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=mock_content):
                result = await executor.execute(call)
                
                assert result.success == True
                assert result.output == mock_content
                assert result.tokens_used > 0
                # File should be cached
                assert "/test/file.py" in executor.file_cache
    
    @pytest.mark.asyncio
    async def test_write_operation_success(self, executor):
        """Test successful file write"""
        call = ToolCall(
            tool=ToolType.WRITE,
            parameters={
                "file_path": "/test/newfile.py",
                "content": "print('Hello')"
            },
            timeout=5,
            retry_on_failure=False,
            max_retries=0
        )
        
        with patch('pathlib.Path.mkdir'):
            with patch('pathlib.Path.write_text') as mock_write:
                result = await executor.execute(call)
                
                assert result.success == True
                mock_write.assert_called_once_with("print('Hello')", encoding='utf-8')
                assert "/test/newfile.py" in executor.file_cache
    
    @pytest.mark.asyncio
    async def test_edit_operation_with_cache(self, executor):
        """Test edit operation using cached content"""
        # First cache the file
        executor.file_cache["/test/file.py"] = "old content here"
        
        call = ToolCall(
            tool=ToolType.EDIT,
            parameters={
                "file_path": "/test/file.py",
                "old_string": "old content",
                "new_string": "new content"
            },
            timeout=5,
            retry_on_failure=False,
            max_retries=0
        )
        
        with patch('pathlib.Path.write_text') as mock_write:
            result = await executor.execute(call)
            
            assert result.success == True
            mock_write.assert_called_once()
            # Cache should be updated
            assert "new content" in executor.file_cache["/test/file.py"]
    
    @pytest.mark.asyncio
    async def test_bash_command_execution(self, executor):
        """Test bash command execution"""
        call = ToolCall(
            tool=ToolType.BASH,
            parameters={"command": "echo 'test'"},
            timeout=5,
            retry_on_failure=False,
            max_retries=0
        )
        
        mock_result = Mock()
        mock_result.stdout = "test\n"
        mock_result.stderr = ""
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            result = await executor.execute(call)
            
            assert result.success == True
            assert "test" in result.output
    
    @pytest.mark.asyncio
    async def test_grep_operation(self, executor):
        """Test grep/search operation"""
        call = ToolCall(
            tool=ToolType.GREP,
            parameters={
                "pattern": "TODO",
                "path": "."
            },
            timeout=30,
            retry_on_failure=False,
            max_retries=0
        )
        
        mock_result = Mock()
        mock_result.stdout = "file1.py:10:# TODO: Fix this\nfile2.py:20:# TODO: Implement"
        mock_result.stderr = ""
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            result = await executor.execute(call)
            
            assert result.success == True
            assert isinstance(result.output, list)
            assert len(result.output) > 0
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self, executor):
        """Test retry mechanism on failure"""
        call = ToolCall(
            tool=ToolType.BASH,
            parameters={"command": "failing_command"},
            timeout=5,
            retry_on_failure=True,
            max_retries=2
        )
        
        # Simulate failure then success
        mock_results = [
            Mock(stdout="", stderr="Error", returncode=1),  # First attempt fails
            Mock(stdout="", stderr="Error", returncode=1),  # Second attempt fails
            Mock(stdout="Success", stderr="", returncode=0)  # Third attempt succeeds
        ]
        
        with patch('subprocess.run', side_effect=mock_results):
            with patch('asyncio.sleep'):  # Skip sleep in tests
                result = await executor.execute(call)
                
                assert result.success == True
                assert result.retries == 2
                assert "Success" in result.output
    
    @pytest.mark.asyncio
    async def test_batch_execution(self, executor):
        """Test batch execution of multiple tools"""
        calls = [
            ToolCall(
                tool=ToolType.READ,
                parameters={"file_path": f"/test/file{i}.py"},
                timeout=5,
                retry_on_failure=False,
                max_retries=0
            )
            for i in range(3)
        ]
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value="content"):
                results = await executor.batch_execute(calls)
                
                assert len(results) == 3
                assert all(r.success for r in results)
                # All files should be cached
                assert len(executor.file_cache) == 3
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, executor):
        """Test timeout handling"""
        call = ToolCall(
            tool=ToolType.BASH,
            parameters={"command": "sleep 100"},
            timeout=1,  # 1 second timeout
            retry_on_failure=False,
            max_retries=0
        )
        
        import subprocess
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('cmd', 1)):
            result = await executor.execute(call)
            
            assert result.success == False
            assert "timed out" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_test_execution(self, executor):
        """Test test suite execution"""
        call = ToolCall(
            tool=ToolType.TEST,
            parameters={"command": "pytest tests/"},
            timeout=300,
            retry_on_failure=False,
            max_retries=0
        )
        
        mock_result = Mock()
        mock_result.stdout = "===== 5 passed in 1.23s ====="
        mock_result.stderr = ""
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            result = await executor.execute(call)
            
            assert result.success == True
            assert "passed" in str(result.output).lower()
    
    def test_required_params_validation(self, executor):
        """Test required parameters validation"""
        # READ requires file_path
        params = executor._get_required_params(ToolType.READ)
        assert "file_path" in params
        
        # WRITE requires file_path and content
        params = executor._get_required_params(ToolType.WRITE)
        assert "file_path" in params
        assert "content" in params
        
        # EDIT requires file_path, old_string, new_string
        params = executor._get_required_params(ToolType.EDIT)
        assert "file_path" in params
        assert "old_string" in params
        assert "new_string" in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])