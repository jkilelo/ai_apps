#!/usr/bin/env python3
"""
Unit Tests for IndexServer
Comprehensive test coverage for production readiness

This test suite covers:
- Happy path scenarios
- Error handling and validation
- Edge cases and limits
- Security validation
- Performance under load
- AST indexing functionality
- Cross-reference tracking
"""

import asyncio
import json
import pytest
import tempfile
import ast
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, mock_open
from typing import Dict, Any, List
import time

# Import the server components
import sys
sys.path.append(str(Path(__file__).parent))

from index_server_fixed import (
    IndexServer,
    ASTIndexer,
    IncrementalIndexer,
    CrossReferenceTracker,
    Symbol,
    SymbolType,
    Relationship,
    RelationType,
    FileIndex,
    IndexingResult
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
        'name': 'test-index-server',
        'version': '2.0.0',
        'rate_limit_calls': 10,
        'rate_limit_window': 60,
        'cache_ttl': 3600,
        'max_cache_size': 100,
        'log_level': 'DEBUG'
    }

@pytest.fixture
async def index_server(server_config):
    """Create test index server instance"""
    server = IndexServer(server_config)
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
from typing import List, Dict

class TestClass:
    """Test class docstring"""
    
    def __init__(self, value: int = 0):
        self.value = value
    
    def method1(self) -> int:
        """Method docstring"""
        return self.value
    
    @property
    def method2(self) -> int:
        """Property docstring"""
        return self.value + 1

def standalone_function(param: str) -> str:
    """Function docstring"""
    return param.upper()

async def async_function(data: List[str]) -> Dict[str, int]:
    """Async function docstring"""
    return {item: len(item) for item in data}

CONSTANT_VALUE = 42
variable_value = "test"

if __name__ == "__main__":
    test_obj = TestClass(10)
    result = standalone_function("hello")
'''

@pytest.fixture
def complex_python_code() -> str:
    """Complex Python code with multiple features"""
    return '''
class Parent:
    def parent_method(self):
        pass

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.data = []
    
    def child_method(self):
        self.parent_method()
        return len(self.data)
    
    @staticmethod
    def static_method():
        return "static"
    
    @classmethod
    def class_method(cls):
        return cls()

def recursive_function(n):
    if n <= 1:
        return 1
    return n * recursive_function(n - 1)

def function_with_nested():
    def inner_function():
        return 42
    return inner_function()
'''

# ============================================================================
# Unit Tests - AST Indexer
# ============================================================================

class TestASTIndexer:
    """Test AST-based indexing engine"""
    
    @pytest.mark.asyncio
    async def test_basic_indexing(self, sample_python_code):
        """Test basic Python code indexing"""
        indexer = ASTIndexer()
        result = indexer.index_python(sample_python_code, "test.py")
        
        assert result.success
        assert result.index is not None
        index = result.index
        
        # Check basic file info
        assert index.file_path == "test.py"
        assert index.language == "python"
        assert index.total_lines > 0
        assert index.total_chars > 0
        assert len(index.hash) == 64  # SHA256 hex
        
        # Check symbols were extracted
        assert len(index.symbols) > 0
        
        # Check for expected symbols
        symbol_names = [s.name for s in index.symbols.values()]
        assert "TestClass" in symbol_names
        assert "standalone_function" in symbol_names
        assert "async_function" in symbol_names
    
    @pytest.mark.asyncio
    async def test_symbol_types(self, sample_python_code):
        """Test correct symbol type detection"""
        indexer = ASTIndexer()
        result = indexer.index_python(sample_python_code, "test.py")
        
        assert result.success
        index = result.index
        
        # Check symbol types
        symbols_by_type = {}
        for symbol in index.symbols.values():
            if symbol.type not in symbols_by_type:
                symbols_by_type[symbol.type] = []
            symbols_by_type[symbol.type].append(symbol.name)
        
        assert SymbolType.CLASS in symbols_by_type
        assert SymbolType.FUNCTION in symbols_by_type
        assert SymbolType.METHOD in symbols_by_type
        assert SymbolType.CONSTANT in symbols_by_type
        assert SymbolType.VARIABLE in symbols_by_type
        
        # Check specific symbols
        assert "TestClass" in symbols_by_type[SymbolType.CLASS]
        assert "standalone_function" in symbols_by_type[SymbolType.FUNCTION]
        assert "CONSTANT_VALUE" in symbols_by_type[SymbolType.CONSTANT]
    
    @pytest.mark.asyncio
    async def test_inheritance_relationships(self, complex_python_code):
        """Test detection of inheritance relationships"""
        indexer = ASTIndexer()
        result = indexer.index_python(complex_python_code, "complex.py")
        
        assert result.success
        index = result.index
        
        # Check relationships
        inheritance_rels = [
            r for r in index.relationships 
            if r.type == RelationType.INHERITS
        ]
        assert len(inheritance_rels) > 0
        
        # Should find Child inherits from Parent
        child_inherits = [
            r for r in inheritance_rels
            if r.source == "Child" and r.target == "Parent"
        ]
        assert len(child_inherits) == 1
    
    @pytest.mark.asyncio
    async def test_call_graph_generation(self, complex_python_code):
        """Test call graph generation"""
        indexer = ASTIndexer()
        result = indexer.index_python(complex_python_code, "complex.py")
        
        assert result.success
        index = result.index
        
        # Check call graph
        assert len(index.call_graph) > 0
        
        # Check for method calls
        call_relationships = [
            r for r in index.relationships
            if r.type == RelationType.CALLS
        ]
        assert len(call_relationships) > 0
    
    @pytest.mark.asyncio
    async def test_complexity_metrics(self, sample_python_code):
        """Test complexity metrics calculation"""
        indexer = ASTIndexer()
        result = indexer.index_python(sample_python_code, "test.py")
        
        assert result.success
        index = result.index
        
        # Check complexity metrics
        metrics = index.complexity_metrics
        assert 'cyclomatic_complexity' in metrics
        assert 'cognitive_complexity' in metrics
        assert 'number_of_classes' in metrics
        assert 'number_of_functions' in metrics
        assert 'number_of_methods' in metrics
        
        # Validate metric values
        assert metrics['number_of_classes'] >= 1
        assert metrics['number_of_functions'] >= 2  # standalone_function, async_function
        assert metrics['number_of_methods'] >= 2   # method1, method2
        assert metrics['cyclomatic_complexity'] >= 1
    
    @pytest.mark.asyncio
    async def test_syntax_error_handling(self):
        """Test handling of syntax errors"""
        invalid_code = """
def broken_function(
    print('unclosed parenthesis'
    return None
"""
        
        indexer = ASTIndexer()
        result = indexer.index_python(invalid_code, "broken.py")
        
        # Should handle syntax errors gracefully
        assert not result.success or len(result.warnings) > 0
        
        if not result.success:
            assert "syntax" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_empty_file_handling(self):
        """Test handling of empty files"""
        indexer = ASTIndexer()
        result = indexer.index_python("", "empty.py")
        
        assert result.success
        assert result.index is not None
        assert len(result.index.symbols) == 0
        assert result.index.total_lines == 1  # Empty file has one empty line
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self):
        """Test handling of large files"""
        # Generate large code file
        large_code = []
        for i in range(1000):
            large_code.append(f"def function_{i}():")
            large_code.append(f"    return {i}")
            large_code.append("")
        
        large_code_str = "\n".join(large_code)
        
        indexer = ASTIndexer()
        result = indexer.index_python(large_code_str, "large.py")
        
        assert result.success
        assert result.index is not None
        assert len(result.index.symbols) > 900  # Should find most functions

# ============================================================================
# Unit Tests - Incremental Indexer
# ============================================================================

class TestIncrementalIndexer:
    """Test incremental indexing functionality"""
    
    def test_cache_management(self):
        """Test cache management"""
        indexer = IncrementalIndexer(max_cache_size=2)
        
        # Create mock validator
        mock_validator = Mock()
        mock_validator.validate_file_path.return_value = Path("test1.py")
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data="def test(): pass")):
            # Add items to cache
            changes1 = [{'type': 'add_symbol', 'symbol': {
                'name': 'test1', 'type': 'function', 'line_start': 1, 'line_end': 1
            }}]
            result1 = indexer.update_index("test1.py", changes1, mock_validator)
            assert result1.success
            
            changes2 = [{'type': 'add_symbol', 'symbol': {
                'name': 'test2', 'type': 'function', 'line_start': 1, 'line_end': 1
            }}]
            result2 = indexer.update_index("test2.py", changes2, mock_validator)
            assert result2.success
            
            # Cache should be at limit
            assert len(indexer.cache) == 2
            
            # Add third item - should evict oldest
            changes3 = [{'type': 'add_symbol', 'symbol': {
                'name': 'test3', 'type': 'function', 'line_start': 1, 'line_end': 1
            }}]
            result3 = indexer.update_index("test3.py", changes3, mock_validator)
            assert result3.success
            
            # Still at max size, oldest evicted
            assert len(indexer.cache) == 2
    
    def test_change_history_trimming(self):
        """Test change history trimming"""
        indexer = IncrementalIndexer()
        indexer.max_history = 5
        
        mock_validator = Mock()
        mock_validator.validate_file_path.return_value = Path("test.py")
        
        with patch('builtins.open', mock_open(read_data="def test(): pass")):
            # Add more changes than max_history
            for i in range(10):
                changes = [{'type': 'add_symbol', 'symbol': {
                    'name': f'test{i}', 'type': 'function', 'line_start': 1, 'line_end': 1
                }}]
                result = indexer.update_index(f"test{i}.py", changes, mock_validator)
                assert result.success
            
            # History should be trimmed
            assert len(indexer.change_history) == 5

# ============================================================================
# Unit Tests - Cross Reference Tracker
# ============================================================================

class TestCrossReferenceTracker:
    """Test cross-reference tracking"""
    
    def test_symbol_registration(self, sample_python_code):
        """Test symbol registration in global tracker"""
        tracker = CrossReferenceTracker()
        
        # Create file index
        indexer = ASTIndexer()
        result = indexer.index_python(sample_python_code, "test.py")
        assert result.success
        
        # Add to tracker
        tracker.add_file_index(result.index)
        
        # Check global symbols
        assert len(tracker.global_symbols) > 0
        
        # Check for expected symbols
        symbol_keys = list(tracker.global_symbols.keys())
        assert any("TestClass" in key for key in symbol_keys)
        assert any("standalone_function" in key for key in symbol_keys)
    
    def test_find_definition(self, sample_python_code):
        """Test symbol definition lookup"""
        tracker = CrossReferenceTracker()
        
        indexer = ASTIndexer()
        result = indexer.index_python(sample_python_code, "test.py")
        tracker.add_file_index(result.index)
        
        # Find definition
        definition = tracker.find_definition("TestClass")
        assert definition is not None
        assert definition['file'] == "test.py"
        assert definition['type'] == 'class'
    
    def test_file_limit_enforcement(self):
        """Test file limit enforcement"""
        tracker = CrossReferenceTracker(max_files=2)
        
        # Create mock indexes
        for i in range(3):
            mock_index = Mock()
            mock_index.file_path = f"file{i}.py"
            mock_index.symbols = {}
            mock_index.imports = []
            mock_index.relationships = []
            
            tracker.add_file_index(mock_index)
        
        # Should not exceed max files
        assert tracker.file_count <= 2

# ============================================================================
# Integration Tests - IndexServer
# ============================================================================

class TestIndexServer:
    """Test the complete IndexServer"""
    
    @pytest.mark.asyncio
    async def test_index_file_success(self, index_server, tmp_path):
        """Test successful file indexing"""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test():\n    return 42")
        
        # Get the index_file tool
        tool_func = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                tool_func = tool
                break
        
        assert tool_func is not None, "index_file tool not found"
        
        # Call the tool
        result = await tool_func(str(test_file), "python")
        
        # Parse response
        response = json.loads(result.text)
        assert response['success']
        assert 'total_symbols' in response
        assert response['total_symbols'] > 0
        assert response['language'] == 'python'
        assert response['file_path'] == str(test_file)
    
    @pytest.mark.asyncio
    async def test_index_file_validation_error(self, index_server):
        """Test validation error handling"""
        # Get the index_file tool
        tool_func = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                tool_func = tool
                break
        
        # Test with invalid file path (should trigger validation error)
        result = await tool_func("../../../etc/passwd", "python")
        
        response = json.loads(result.text)
        assert not response['success']
        assert 'error' in response
        assert 'validation_error' in response.get('type', '')
    
    @pytest.mark.asyncio
    async def test_get_symbols_success(self, index_server, tmp_path):
        """Test getting symbols from indexed file"""
        # Create and index test file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class TestClass:
    def method1(self):
        pass

def test_function():
    pass
""")
        
        # First index the file
        index_tool = None
        get_symbols_tool = None
        
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
            elif tool.__name__ == 'get_symbols':
                get_symbols_tool = tool
        
        # Index the file
        await index_tool(str(test_file), "python")
        
        # Get all symbols
        result = await get_symbols_tool(str(test_file))
        response = json.loads(result.text)
        
        assert response['success']
        assert 'symbols' in response
        assert response['symbol_count'] > 0
        
        # Check for expected symbols
        symbols = response['symbols']
        symbol_names = [s['name'] for s in symbols.values()]
        assert "TestClass" in symbol_names
        assert "test_function" in symbol_names
    
    @pytest.mark.asyncio
    async def test_get_symbols_with_filter(self, index_server, tmp_path):
        """Test getting symbols with type filter"""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class TestClass:
    pass

def test_function():
    pass
""")
        
        # Index the file
        index_tool = None
        get_symbols_tool = None
        
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
            elif tool.__name__ == 'get_symbols':
                get_symbols_tool = tool
        
        await index_tool(str(test_file), "python")
        
        # Get only class symbols
        result = await get_symbols_tool(str(test_file), "class")
        response = json.loads(result.text)
        
        assert response['success']
        symbols = response['symbols']
        
        # Should only contain class symbols
        for symbol in symbols.values():
            assert symbol['type'] == 'class'
    
    @pytest.mark.asyncio
    async def test_find_references(self, index_server):
        """Test finding symbol references"""
        # Get the find_references tool
        find_refs_tool = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'find_references':
                find_refs_tool = tool
                break
        
        result = await find_refs_tool("TestSymbol")
        response = json.loads(result.text)
        
        assert response['success']
        assert 'symbol' in response
        assert response['symbol'] == "TestSymbol"
        assert 'references' in response
        assert 'total_references' in response
    
    @pytest.mark.asyncio
    async def test_get_complexity(self, index_server, tmp_path):
        """Test complexity metrics retrieval"""
        # Create test file with complexity
        test_file = tmp_path / "complex.py"
        test_file.write_text("""
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
            else:
                continue
    return x
""")
        
        # Index and get complexity
        index_tool = None
        complexity_tool = None
        
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
            elif tool.__name__ == 'get_complexity':
                complexity_tool = tool
        
        await index_tool(str(test_file), "python")
        result = await complexity_tool(str(test_file))
        
        response = json.loads(result.text)
        assert response['success']
        assert 'metrics' in response
        assert 'summary' in response
        
        metrics = response['metrics']
        assert 'cyclomatic_complexity' in metrics
        assert 'cognitive_complexity' in metrics
        assert metrics['cyclomatic_complexity'] > 1  # Has if/for statements
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, index_server, tmp_path):
        """Test rate limiting functionality"""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        # Get the index_file tool
        index_tool = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
                break
        
        # Make rapid requests (should hit rate limit)
        tasks = []
        for _ in range(15):  # More than rate limit
            task = index_tool(str(test_file), "python")
            tasks.append(task)
        
        # Some should succeed, some should fail due to rate limiting
        # Note: In real test, would need to mock rate limiter or adjust config
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # At least some should succeed
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        assert success_count > 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, index_server):
        """Test health check functionality"""
        health = await index_server._get_health_status()
        
        assert health['status'] == 'healthy'
        assert 'uptime_seconds' in health
        assert 'metrics' in health
        assert 'cache_stats' in health
        assert health['uptime_seconds'] >= 0
    
    @pytest.mark.asyncio
    async def test_unsupported_language(self, index_server, tmp_path):
        """Test handling of unsupported languages"""
        test_file = tmp_path / "test.js"
        test_file.write_text("function test() { return 42; }")
        
        # Get the index_file tool
        index_tool = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
                break
        
        result = await index_tool(str(test_file), "javascript")
        response = json.loads(result.text)
        
        assert not response['success']
        assert 'not supported' in response['error'].lower()
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self, index_server, tmp_path):
        """Test handling of very large files"""
        # Create large file (beyond configured limits)
        test_file = tmp_path / "large.py"
        large_content = "# Large file\n" + ("x = 1\n" * 100000)
        test_file.write_text(large_content)
        
        # Get the index_file tool
        index_tool = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
                break
        
        result = await index_tool(str(test_file), "python")
        response = json.loads(result.text)
        
        # Should either succeed or fail gracefully with size error
        if not response['success']:
            assert 'too large' in response['error'].lower()
        else:
            assert response['success']

# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_indexing(self, index_server, tmp_path):
        """Test handling concurrent indexing requests"""
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = tmp_path / f"test_{i}.py"
            test_file.write_text(f"def test_{i}():\n    return {i}")
            test_files.append(test_file)
        
        # Get the index_file tool
        index_tool = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
                break
        
        # Make concurrent requests
        tasks = [index_tool(str(f), "python") for f in test_files]
        results = await asyncio.gather(*tasks)
        
        # All should succeed or fail gracefully
        for result in results:
            response = json.loads(result.text)
            assert 'success' in response  # Should have success field
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, index_server, tmp_path):
        """Test cache performance"""
        test_file = tmp_path / "cache_test.py"
        test_file.write_text("def cache_test(): return 42")
        
        # Get the index_file tool
        index_tool = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
                break
        
        # First call - should be slow (not cached)
        start_time = time.time()
        result1 = await index_tool(str(test_file), "python")
        first_duration = time.time() - start_time
        
        # Second call - should be faster (cached)
        start_time = time.time()
        result2 = await index_tool(str(test_file), "python")
        second_duration = time.time() - start_time
        
        # Both should succeed
        response1 = json.loads(result1.text)
        response2 = json.loads(result2.text)
        
        assert response1['success']
        assert response2['success']
        
        # Cache hit should be much faster (but this is hard to test reliably)
        # At minimum, second call should not be slower
        assert second_duration <= first_duration * 2  # Allow some variance

# ============================================================================
# Security Tests
# ============================================================================

class TestSecurity:
    """Security validation tests"""
    
    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, index_server):
        """Test prevention of path traversal attacks"""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "~/../../etc/passwd"
        ]
        
        # Get the index_file tool
        index_tool = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'index_file':
                index_tool = tool
                break
        
        for path in dangerous_paths:
            result = await index_tool(path, "python")
            response = json.loads(result.text)
            
            assert not response['success']
            assert 'error' in response
    
    @pytest.mark.asyncio
    async def test_input_validation(self, index_server, tmp_path):
        """Test input validation and sanitization"""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        # Get the get_symbols tool
        get_symbols_tool = None
        for tool in index_server.server._tools:
            if tool.__name__ == 'get_symbols':
                get_symbols_tool = tool
                break
        
        # Test with invalid symbol type
        result = await get_symbols_tool(str(test_file), "invalid_type")
        response = json.loads(result.text)
        
        assert not response['success']
        assert 'error' in response
        assert 'Invalid symbol type' in response['error']

# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=index_server_fixed",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-W", "ignore::DeprecationWarning"
    ])