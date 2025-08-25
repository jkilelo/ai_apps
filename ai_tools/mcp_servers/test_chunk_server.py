#!/usr/bin/env python3
"""
Unit Tests for ChunkServer
Comprehensive test coverage for production readiness

This test suite covers:
- Happy path scenarios
- Error handling
- Edge cases
- Security validation
- Performance under load
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, mock_open
from typing import Dict, Any, List
import time

# Import the server components
import sys
sys.path.append(str(Path(__file__).parent))

from chunk_server_fixed import (
    ChunkServer,
    ChunkStrategy,
    ChunkType,
    CodeChunk,
    ChunkingResult,
    LineBasedChunker,
    ASTBasedChunker,
    SemanticChunker,
    HybridChunker
)
from mcp_base import (
    ValidationError,
    ProcessingError,
    RateLimitError,
    ServerConfig
)

# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def server_config() -> ServerConfig:
    """Test server configuration"""
    return {
        'name': 'test-chunk-server',
        'version': '1.0.0',
        'rate_limit_calls': 10,
        'rate_limit_window': 60,
        'cache_ttl': 3600,
        'max_cache_size': 100,
        'log_level': 'DEBUG'
    }

@pytest.fixture
async def chunk_server(server_config):
    """Create test chunk server instance"""
    server = ChunkServer(server_config)
    yield server
    # Cleanup
    await server.shutdown()

@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code for testing"""
    return '''#!/usr/bin/env python3
"""Module docstring"""

import os
import sys
from typing import List

class TestClass:
    """Test class docstring"""
    
    def __init__(self):
        self.value = 0
    
    def method1(self) -> int:
        """Method docstring"""
        return self.value
    
    def method2(self, x: int) -> int:
        return self.value + x

def standalone_function(param: str) -> str:
    """Function docstring"""
    return param.upper()

def test_function():
    """Test function"""
    assert standalone_function("test") == "TEST"

if __name__ == "__main__":
    test_function()
'''

@pytest.fixture
def sample_large_code() -> str:
    """Generate large Python code for testing"""
    lines = []
    for i in range(200):
        if i % 20 == 0:
            lines.append(f"\nclass Class{i}:")
            lines.append(f"    '''Class {i} docstring'''")
        lines.append(f"    def method_{i}(self):")
        lines.append(f"        return {i}")
    return '\n'.join(lines)

# ============================================================================
# Unit Tests - Chunking Engines
# ============================================================================

class TestLineBasedChunker:
    """Test line-based chunking engine"""
    
    @pytest.mark.asyncio
    async def test_basic_chunking(self, sample_python_code):
        """Test basic line-based chunking"""
        chunker = LineBasedChunker(max_chunk_size=10)
        chunks = await chunker.chunk(sample_python_code, "test.py")
        
        assert len(chunks) > 0
        assert all(isinstance(c, CodeChunk) for c in chunks)
        assert all(c.size_lines <= 10 for c in chunks)
        assert all(c.type == ChunkType.CODE_BLOCK for c in chunks)
    
    @pytest.mark.asyncio
    async def test_chunking_with_overlap(self, sample_python_code):
        """Test chunking with overlap"""
        chunker = LineBasedChunker(max_chunk_size=10, overlap=2)
        chunks = await chunker.chunk(sample_python_code, "test.py")
        
        assert len(chunks) > 0
        # Check that overlap is applied
        for i in range(1, len(chunks)):
            # Chunks should have some overlapping content
            assert chunks[i].metadata.get('overlap_start', False) or i == len(chunks) - 1
    
    @pytest.mark.asyncio
    async def test_empty_content(self):
        """Test handling of empty content"""
        chunker = LineBasedChunker()
        chunks = await chunker.chunk("", "empty.py")
        
        assert len(chunks) == 0
    
    @pytest.mark.asyncio
    async def test_single_line(self):
        """Test handling of single line"""
        chunker = LineBasedChunker()
        chunks = await chunker.chunk("print('hello')", "single.py")
        
        assert len(chunks) == 1
        assert chunks[0].size_lines == 1

class TestASTBasedChunker:
    """Test AST-based chunking engine"""
    
    @pytest.mark.asyncio
    async def test_ast_chunking(self, sample_python_code):
        """Test AST-based chunking"""
        chunker = ASTBasedChunker(max_chunk_size=50)
        chunks = await chunker.chunk(sample_python_code, "test.py")
        
        assert len(chunks) > 0
        
        # Check chunk types
        chunk_types = {c.type for c in chunks}
        assert ChunkType.IMPORTS in chunk_types
        assert ChunkType.CLASS in chunk_types
        assert ChunkType.FUNCTION in chunk_types
        
        # Check metadata
        class_chunks = [c for c in chunks if c.type == ChunkType.CLASS]
        assert all('class_name' in c.metadata for c in class_chunks)
    
    @pytest.mark.asyncio
    async def test_large_class_splitting(self, sample_large_code):
        """Test splitting of large classes"""
        chunker = ASTBasedChunker(max_chunk_size=10)
        chunks = await chunker.chunk(sample_large_code, "large.py")
        
        # Should split large classes into methods
        method_chunks = [c for c in chunks if c.type == ChunkType.METHOD]
        assert len(method_chunks) > 0
    
    @pytest.mark.asyncio
    async def test_invalid_syntax_fallback(self):
        """Test fallback when AST parsing fails"""
        invalid_code = "def broken_function(\n    print('unclosed'"
        
        chunker = ASTBasedChunker(max_chunk_size=10)
        chunks = await chunker.chunk(invalid_code, "invalid.py")
        
        # Should fallback to line-based chunking
        assert len(chunks) > 0
        assert all(c.type == ChunkType.CODE_BLOCK for c in chunks)

class TestSemanticChunker:
    """Test semantic chunking engine"""
    
    @pytest.mark.asyncio
    async def test_semantic_boundaries(self):
        """Test detection of semantic boundaries"""
        code = '''
# ============================================================================
# Section 1
# ============================================================================

def function1():
    pass

# ----------------------------------------------------------------------------
# Section 2
# ----------------------------------------------------------------------------

def function2():
    pass
'''
        chunker = SemanticChunker(max_chunk_size=50)
        chunks = await chunker.chunk(code, "semantic.py")
        
        assert len(chunks) > 0
        # Should detect section boundaries
        assert any('boundary_type' in c.metadata for c in chunks)
    
    @pytest.mark.asyncio
    async def test_docstring_detection(self):
        """Test docstring chunk detection"""
        code = '''
"""
This is a module docstring
that spans multiple lines
"""

def function():
    """Function docstring"""
    pass
'''
        chunker = SemanticChunker(max_chunk_size=50)
        chunks = await chunker.chunk(code, "doc.py")
        
        # Should identify docstrings
        docstring_chunks = [c for c in chunks if c.type == ChunkType.DOCSTRING]
        assert len(docstring_chunks) > 0

class TestHybridChunker:
    """Test hybrid chunking engine"""
    
    @pytest.mark.asyncio
    async def test_python_file_uses_ast(self, sample_python_code):
        """Test that Python files use AST chunking"""
        chunker = HybridChunker(max_chunk_size=50)
        chunks = await chunker.chunk(sample_python_code, "test.py")
        
        # Should use AST chunking for Python files
        chunk_types = {c.type for c in chunks}
        assert ChunkType.CLASS in chunk_types or ChunkType.FUNCTION in chunk_types
    
    @pytest.mark.asyncio
    async def test_non_python_file_fallback(self):
        """Test fallback for non-Python files"""
        content = "This is a text file\nwith multiple lines\nof content"
        
        chunker = HybridChunker(max_chunk_size=10)
        chunks = await chunker.chunk(content, "test.txt")
        
        assert len(chunks) > 0

# ============================================================================
# Integration Tests - ChunkServer
# ============================================================================

class TestChunkServer:
    """Test the complete ChunkServer"""
    
    @pytest.mark.asyncio
    async def test_chunk_file_success(self, chunk_server, tmp_path):
        """Test successful file chunking"""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test():\n    return 42")
        
        # Mock the MCP tool response
        with patch.object(chunk_server, 'process_request') as mock_process:
            mock_process.return_value = [
                CodeChunk(
                    id="test1",
                    content="def test():\n    return 42",
                    type=ChunkType.FUNCTION,
                    line_start=1,
                    line_end=2,
                    size_bytes=25,
                    size_lines=2
                )
            ]
            
            # Create the tool function (simulating MCP tool call)
            tool_func = None
            for tool in chunk_server.server._tools:
                if tool.__name__ == 'chunk_file':
                    tool_func = tool
                    break
            
            if tool_func:
                result = await tool_func(
                    file_path=str(test_file),
                    strategy="line_based",
                    max_chunk_size=10
                )
                
                # Parse response
                response = json.loads(result.text)
                assert response['success']
                assert 'data' in response
    
    @pytest.mark.asyncio
    async def test_chunk_file_validation_error(self, chunk_server):
        """Test validation error handling"""
        # Test with invalid file path
        with pytest.raises(ValidationError) as exc:
            await chunk_server.validator.validate_file_path("../../../etc/passwd")
        
        assert "Path traversal" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_chunk_file_invalid_strategy(self, chunk_server, tmp_path):
        """Test invalid strategy handling"""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('test')")
        
        # Test with invalid strategy
        # This would be called through the MCP tool in production
        with pytest.raises(ValidationError) as exc:
            strategy = "invalid_strategy"
            ChunkStrategy(strategy.lower())
        
        assert "invalid_strategy" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, chunk_server):
        """Test caching functionality"""
        test_data = {"test": "data"}
        cache_key = "test_key"
        
        # Set cache
        await chunk_server.cache.set(cache_key, json.dumps(test_data))
        
        # Get from cache
        cached = await chunk_server.cache.get(cache_key)
        assert cached is not None
        assert json.loads(cached) == test_data
        
        # Test cache stats
        stats = chunk_server.cache.get_stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, chunk_server):
        """Test rate limiting functionality"""
        # Configure aggressive rate limiting for test
        chunk_server.rate_limiter.max_calls = 2
        chunk_server.rate_limiter.time_window = 1
        
        # First two calls should succeed
        assert await chunk_server.rate_limiter.check_rate_limit("test_client")
        assert await chunk_server.rate_limiter.check_rate_limit("test_client")
        
        # Third call should fail
        assert not await chunk_server.rate_limiter.check_rate_limit("test_client")
        
        # Wait for window to pass
        await asyncio.sleep(1.1)
        
        # Should succeed again
        assert await chunk_server.rate_limiter.check_rate_limit("test_client")
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, chunk_server):
        """Test metrics tracking"""
        # Simulate successful request
        chunk_server.metrics.update(success=True, processing_time=0.5)
        
        assert chunk_server.metrics.requests_total == 1
        assert chunk_server.metrics.requests_success == 1
        assert chunk_server.metrics.average_response_time == 0.5
        
        # Simulate failed request
        chunk_server.metrics.update(success=False, processing_time=0.1)
        
        assert chunk_server.metrics.requests_total == 2
        assert chunk_server.metrics.requests_failed == 1
        assert chunk_server.metrics.error_rate == 0.5
    
    @pytest.mark.asyncio
    async def test_health_check(self, chunk_server):
        """Test health check endpoint"""
        health = await chunk_server._get_health_status()
        
        assert health['status'] == 'healthy'
        assert 'uptime_seconds' in health
        assert 'metrics' in health
        assert 'cache_stats' in health
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self, chunk_server, tmp_path):
        """Test handling of large files"""
        # Create large file
        large_content = "x" * (chunk_server.config['max_request_size'] + 1)
        test_file = tmp_path / "large.py"
        test_file.write_text(large_content)
        
        # Should raise validation error for file too large
        with pytest.raises(ValidationError) as exc:
            chunk_server.validator.validate_json_input(
                {"data": large_content},
                max_size=chunk_server.config['max_request_size']
            )
        
        assert "too large" in str(exc.value)

# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, chunk_server):
        """Test handling concurrent requests"""
        async def make_request(i):
            return await chunk_server.rate_limiter.check_rate_limit(f"client_{i}")
        
        # Make concurrent requests
        tasks = [make_request(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed (within rate limit)
        assert all(results)
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, chunk_server):
        """Test cache performance"""
        # Populate cache
        for i in range(100):
            await chunk_server.cache.set(f"key_{i}", f"value_{i}")
        
        # Test retrieval speed
        start = time.time()
        for i in range(100):
            await chunk_server.cache.get(f"key_{i}")
        duration = time.time() - start
        
        # Should be fast (< 1 second for 100 retrievals)
        assert duration < 1.0
        
        # Check cache stats
        stats = chunk_server.cache.get_stats()
        assert stats['hits'] == 100

# ============================================================================
# Security Tests
# ============================================================================

class TestSecurity:
    """Security validation tests"""
    
    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, chunk_server):
        """Test prevention of path traversal attacks"""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "~/../../etc/passwd"
        ]
        
        for path in dangerous_paths:
            with pytest.raises(ValidationError) as exc:
                chunk_server.validator.validate_file_path(path, must_exist=False)
            
            assert "Path traversal" in str(exc.value) or "Invalid" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_input_sanitization(self, chunk_server):
        """Test input sanitization"""
        # Test string sanitization
        dirty_string = "Hello\x00World\x01Test\x1f"
        clean = chunk_server.validator.sanitize_string(dirty_string)
        
        # Control characters should be removed
        assert "\x00" not in clean
        assert "\x01" not in clean
        assert "\x1f" not in clean
        
        # Test max length enforcement
        long_string = "x" * 20000
        truncated = chunk_server.validator.sanitize_string(long_string, max_length=100)
        assert len(truncated) == 100
    
    @pytest.mark.asyncio
    async def test_json_validation(self, chunk_server):
        """Test JSON input validation"""
        # Valid JSON
        valid_json = {"key": "value", "number": 42}
        result = chunk_server.validator.validate_json_input(valid_json)
        assert result == valid_json
        
        # Invalid JSON string
        with pytest.raises(ValidationError) as exc:
            chunk_server.validator.validate_json_input("{invalid json}")
        assert "Invalid JSON" in str(exc.value)
        
        # Non-dict top level
        with pytest.raises(ValidationError) as exc:
            chunk_server.validator.validate_json_input(["array", "not", "allowed"])
        assert "must be an object" in str(exc.value)

# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=chunk_server_fixed",
        "--cov=mcp_base",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-W", "ignore::DeprecationWarning"
    ])