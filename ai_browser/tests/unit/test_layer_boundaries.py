#!/usr/bin/env python3
"""
Critical Layer Boundary Tests for AI Browser v2.0.0

Tests the fundamental 5-layer architecture integrity:
- Layer 1: EXECUTION (Browser control, stealth ops)
- Layer 2: PERCEPTION (DOM processing, visual annotation)  
- Layer 3: COGNITION (LLM reasoning, action planning)
- Layer 4: MEMORY (Multi-tier storage systems)
- Layer 5: EXTENSIBILITY (Plugins, MCP protocol)

**CRITICAL**: These tests validate architectural boundaries that prevent
regression and maintain production quality.
"""

import pytest
import sys
import inspect
from pathlib import Path
from typing import Any, Set, Dict, List
import ast
import importlib
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import all layers for boundary testing
from execution.browser_manager import BrowserManager
from execution.stealth_manager import StealthManager
from execution.action_executor import ActionExecutor
from perception.state_observer import StateObserver
from perception.visual_annotator import VisualAnnotator
from perception.dom_processor import DOMProcessor
from cognition.orchestrator import AgentOrchestrator
from cognition.llm import LLMManager
from cognition.action_dispatcher import ActionDispatcher
from memory.memory_manager import MemoryManager
from extensibility.plugin_manager import PluginManager


class TestLayerBoundaryIntegrity:
    """Test that layers maintain strict separation of concerns."""
    
    def test_execution_layer_no_llm_imports(self):
        """CRITICAL: Execution layer MUST NOT import LLM or reasoning components."""
        forbidden_imports = {
            'openai', 'anthropic', 'google.generativeai', 'llm_manager', 
            'orchestrator', 'prompt_builder', 'cognition'
        }
        
        # Check execution module imports
        execution_files = list(Path("src/execution").glob("*.py"))
        for file_path in execution_files:
            if file_path.name == "__init__.py":
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST to find imports
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not any(forbidden in alias.name.lower() 
                                     for forbidden in forbidden_imports), \
                            f"Execution layer file {file_path} imports forbidden module: {alias.name}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        assert not any(forbidden in node.module.lower() 
                                     for forbidden in forbidden_imports), \
                            f"Execution layer file {file_path} imports from forbidden module: {node.module}"
    
    def test_perception_layer_no_llm_imports(self):
        """CRITICAL: Perception layer MUST NOT import LLM components."""
        forbidden_imports = {
            'openai', 'anthropic', 'google.generativeai', 'llm_manager',
            'orchestrator', 'prompt_builder'
        }
        
        perception_files = list(Path("src/perception").glob("*.py"))
        for file_path in perception_files:
            if file_path.name == "__init__.py":
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not any(forbidden in alias.name.lower() 
                                     for forbidden in forbidden_imports), \
                            f"Perception layer file {file_path} imports forbidden module: {alias.name}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        assert not any(forbidden in node.module.lower() 
                                     for forbidden in forbidden_imports), \
                            f"Perception layer file {file_path} imports from forbidden module: {node.module}"
    
    def test_execution_no_browser_in_cognition(self):
        """CRITICAL: Cognition layer MUST NOT directly control browser."""
        forbidden_imports = {'playwright', 'selenium', 'browser_manager'}
        
        cognition_files = list(Path("src/cognition").glob("*.py"))
        for file_path in cognition_files:
            if file_path.name == "__init__.py":
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for direct browser manipulation
            assert 'page.click' not in content, f"Cognition file {file_path} has direct browser manipulation"
            assert 'page.type' not in content, f"Cognition file {file_path} has direct browser manipulation"
            assert 'page.goto' not in content, f"Cognition file {file_path} has direct browser manipulation"
    
    def test_layer_dependency_direction(self):
        """CRITICAL: Test allowed vs forbidden layer dependencies."""
        
        # ALLOWED: Cognition can use Execution and Perception
        # FORBIDDEN: Execution cannot use Cognition
        # FORBIDDEN: Perception cannot use Memory directly
        
        # Test that these imports work (allowed dependencies)
        try:
            from cognition.orchestrator import AgentOrchestrator
            from execution.browser_manager import BrowserManager
            from perception.state_observer import StateObserver
            # This is allowed - cognition orchestrates other layers
        except ImportError as e:
            pytest.fail(f"Allowed layer dependency failed: {e}")
        
        # Test forbidden dependencies would fail
        with pytest.raises((ImportError, AttributeError, ModuleNotFoundError)):
            # This should fail - execution cannot use cognition
            exec("from execution.browser_manager import BrowserManager; from cognition.llm import LLMManager; BrowserManager().llm = LLMManager()")


class TestMemoryLayerIsolation:
    """Test memory layer maintains isolation and consistency."""
    
    @pytest.mark.asyncio
    async def test_memory_layer_interfaces(self):
        """Test memory layer provides correct interfaces to other layers."""
        
        memory_manager = MemoryManager()
        
        # Test session memory interface
        assert hasattr(memory_manager, 'session')
        assert hasattr(memory_manager.session, 'store_conversation')
        assert hasattr(memory_manager.session, 'get_conversation_history')
        
        # Test semantic memory interface  
        assert hasattr(memory_manager, 'semantic')
        assert hasattr(memory_manager.semantic, 'store_embedding')
        assert hasattr(memory_manager.semantic, 'search_similar')
        
        # Test knowledge graph interface
        assert hasattr(memory_manager, 'knowledge_graph')
        assert hasattr(memory_manager.knowledge_graph, 'add_relationship')
        assert hasattr(memory_manager.knowledge_graph, 'query_graph')
    
    @pytest.mark.asyncio  
    async def test_memory_layer_no_direct_browser_access(self):
        """CRITICAL: Memory layer MUST NOT directly access browser."""
        
        memory_manager = MemoryManager()
        
        # Memory should not have browser attributes
        assert not hasattr(memory_manager, 'browser')
        assert not hasattr(memory_manager, 'page')
        assert not hasattr(memory_manager, 'context')
        
        # Memory should not have playwright imports
        memory_module = inspect.getmodule(memory_manager)
        memory_source = inspect.getsource(memory_module)
        
        assert 'from playwright' not in memory_source
        assert 'import playwright' not in memory_source


class TestExecutionLayerStealth:
    """Test execution layer stealth capabilities are isolated."""
    
    @pytest.mark.asyncio
    async def test_stealth_manager_initialization(self):
        """Test stealth manager initializes without external dependencies."""
        
        stealth_manager = StealthManager()
        
        # Should initialize without requiring LLM or other layers
        assert stealth_manager is not None
        assert hasattr(stealth_manager, 'apply_stealth_plugins')
        
    def test_stealth_plugins_isolation(self):
        """Test stealth plugins don't leak into other layers."""
        
        # Stealth should be contained in execution layer
        stealth_manager = StealthManager()
        
        # Should not expose LLM functionality
        assert not hasattr(stealth_manager, 'generate_response')
        assert not hasattr(stealth_manager, 'reason_about_action')


class TestPerceptionLayerPurity:
    """Test perception layer maintains purity (no side effects)."""
    
    @pytest.mark.asyncio
    async def test_state_observer_no_actions(self):
        """CRITICAL: State observer MUST NOT perform actions, only observe."""
        
        state_observer = StateObserver()
        
        # Should only have observation methods
        methods = [method for method in dir(state_observer) 
                  if not method.startswith('_') and callable(getattr(state_observer, method))]
        
        action_verbs = {'click', 'type', 'navigate', 'submit', 'press', 'upload', 'download'}
        
        for method in methods:
            assert not any(verb in method.lower() for verb in action_verbs), \
                f"Perception layer method {method} suggests action capability"
    
    @pytest.mark.asyncio
    async def test_dom_processor_read_only(self):
        """Test DOM processor only reads, never modifies DOM."""
        
        dom_processor = DOMProcessor()
        
        # Should have only processing methods, no mutation methods
        methods = [method for method in dir(dom_processor) 
                  if not method.startswith('_') and callable(getattr(dom_processor, method))]
        
        mutation_verbs = {'set', 'update', 'modify', 'change', 'alter', 'inject', 'insert'}
        
        for method in methods:
            assert not any(verb in method.lower() for verb in mutation_verbs), \
                f"DOM processor method {method} suggests mutation capability"


class TestCognitionLayerOrchestration:
    """Test cognition layer properly orchestrates without direct execution."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_delegates_actions(self):
        """Test orchestrator delegates to execution layer rather than executing directly."""
        
        with patch('execution.action_executor.ActionExecutor') as mock_executor:
            mock_executor.return_value.execute.return_value = AsyncMock()
            
            orchestrator = AgentOrchestrator()
            
            # Orchestrator should delegate, not execute directly
            assert hasattr(orchestrator, 'execute_task')
            
            # Should not have direct browser manipulation methods
            assert not hasattr(orchestrator, 'click')
            assert not hasattr(orchestrator, 'type') 
            assert not hasattr(orchestrator, 'navigate')
    
    @pytest.mark.asyncio
    async def test_llm_manager_no_browser_access(self):
        """Test LLM manager doesn't directly access browser."""
        
        llm_manager = LLMManager()
        
        # Should not have browser attributes
        assert not hasattr(llm_manager, 'browser')
        assert not hasattr(llm_manager, 'page')
        assert not hasattr(llm_manager, 'context')
        
        # Should only have LLM-related methods
        methods = [method for method in dir(llm_manager) 
                  if not method.startswith('_') and callable(getattr(llm_manager, method))]
        
        browser_methods = {'click', 'type', 'navigate', 'screenshot', 'wait'}
        
        for method in methods:
            assert not any(browser_method in method.lower() for browser_method in browser_methods), \
                f"LLM manager has browser method: {method}"


class TestExtensibilityLayerSandboxing:
    """Test extensibility layer maintains proper sandboxing."""
    
    def test_plugin_manager_isolation(self):
        """Test plugin manager maintains plugin isolation."""
        
        plugin_manager = PluginManager()
        
        # Should have plugin management capabilities
        assert hasattr(plugin_manager, 'load_plugin')
        assert hasattr(plugin_manager, 'unload_plugin')
        
        # Should have sandbox controls
        assert hasattr(plugin_manager, 'plugin_configs')


class TestLayerPerformanceBoundaries:
    """Test layer performance stays within SLA boundaries."""
    
    @pytest.mark.asyncio
    async def test_layer_initialization_performance(self):
        """Test all layers initialize within performance SLAs."""
        import time
        
        # Browser init: <2 seconds (SLA requirement)
        start_time = time.time()
        browser_manager = BrowserManager()
        browser_init_time = time.time() - start_time
        assert browser_init_time < 2.0, f"Browser init took {browser_init_time:.2f}s, exceeds 2s SLA"
        
        # Memory init: <100ms (SLA requirement) 
        start_time = time.time()
        memory_manager = MemoryManager()
        memory_init_time = time.time() - start_time
        assert memory_init_time < 0.1, f"Memory init took {memory_init_time:.3f}s, exceeds 100ms SLA"
        
        # Perception init: <1 second
        start_time = time.time()
        state_observer = StateObserver()
        perception_init_time = time.time() - start_time
        assert perception_init_time < 1.0, f"Perception init took {perception_init_time:.2f}s, exceeds 1s SLA"
    
    @pytest.mark.asyncio
    async def test_memory_query_performance(self):
        """Test memory queries meet <100ms SLA."""
        import time
        
        memory_manager = MemoryManager()
        await memory_manager.initialize()
        
        # Test session memory query
        start_time = time.time()
        await memory_manager.session.get_conversation_history("test_task", limit=10)
        query_time = time.time() - start_time
        assert query_time < 0.1, f"Session memory query took {query_time:.3f}s, exceeds 100ms SLA"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])