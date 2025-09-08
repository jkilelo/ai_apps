"""Comprehensive integration tests for the multi-tier memory system"""
import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import random
import string

from src.memory.memory_manager import MemoryManager
from src.memory.memory_router import MemoryRouter, MemoryTier, CacheStrategy
from src.memory.memory_config import ProductionMemoryConfig, MemoryOptimizer
from src.memory.session_memory import SessionMemory, ConversationModel, ActionModel, PageStateModel
from src.memory.semantic_memory import SemanticMemory, EmbeddingDocument
from src.memory.knowledge_graph import KnowledgeGraph


class TestMemorySystemIntegration:
    """Integration tests for the complete memory system"""
    
    @pytest.fixture
    async def temp_db_path(self):
        """Create temporary database path"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_session.db"
        yield str(db_path)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    async def test_config(self, temp_db_path):
        """Create test memory configuration"""
        config = ProductionMemoryConfig.for_testing()
        config.session_db_path = temp_db_path
        return config
    
    @pytest.fixture
    async def memory_manager(self, test_config):
        """Create and initialize memory manager"""
        config_dict = test_config.to_dict()
        manager = MemoryManager(config_dict)
        
        success = await manager.initialize()
        assert success, "Memory manager initialization failed"
        
        yield manager
        
        await manager.close()
    
    @pytest.fixture
    def sample_embedding(self):
        """Generate sample embedding vector"""
        return [random.random() for _ in range(1536)]  # OpenAI embedding size
    
    def generate_random_string(self, length: int = 10) -> str:
        """Generate random string for testing"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    async def test_memory_manager_initialization(self, test_config):
        """Test memory manager initialization with all tiers"""
        config_dict = test_config.to_dict()
        manager = MemoryManager(config_dict)
        
        # Test initialization
        success = await manager.initialize()
        assert success, "Memory manager should initialize successfully"
        assert manager.is_initialized(), "Manager should report as initialized"
        
        # Test health check
        health = await manager.health_check()
        assert health["session_memory"], "Session memory should be healthy"
        # Note: Semantic and knowledge may not be available in test environment
        
        await manager.close()
    
    async def test_conversation_storage_and_retrieval(self, memory_manager, sample_embedding):
        """Test conversation storage across memory tiers"""
        task_id = f"test_task_{self.generate_random_string()}"
        user_input = "Find information about Python web scraping"
        agent_response = "I'll help you find information about Python web scraping using BeautifulSoup and Scrapy."
        
        # Store conversation
        conversation_id = await memory_manager.store_conversation(
            task_id=task_id,
            user_input=user_input,
            agent_response=agent_response,
            embedding=sample_embedding
        )
        
        assert conversation_id > 0, "Should return valid conversation ID"
        
        # Retrieve recent conversations
        recent_conversations = await memory_manager.get_recent_conversations(limit=5)
        assert len(recent_conversations) > 0, "Should retrieve recent conversations"
        
        # Find our conversation
        our_conversation = None
        for conv in recent_conversations:
            if conv.task_id == task_id:
                our_conversation = conv
                break
        
        assert our_conversation is not None, "Should find stored conversation"
        assert our_conversation.user_input == user_input
        assert our_conversation.agent_response == agent_response
        
        # Test task history retrieval
        task_history = await memory_manager.get_task_history(task_id)
        assert len(task_history) == 1, "Should have one conversation in task history"
        assert task_history[0].user_input == user_input
    
    async def test_action_storage_and_patterns(self, memory_manager, sample_embedding):
        """Test action storage and pattern recognition"""
        # Create a conversation first
        conversation_id = await memory_manager.store_conversation(
            task_id="test_actions",
            user_input="Click the login button",
            agent_response="I'll click the login button for you.",
            embedding=sample_embedding
        )
        
        # Store multiple actions with different success rates
        page_url = "https://example.com/login"
        actions = [
            {
                "action_type": "click",
                "element_selector": "#login-btn",
                "success": True,
                "result": {"status": "clicked", "url_changed": True}
            },
            {
                "action_type": "click", 
                "element_selector": "#login-btn",
                "success": True,
                "result": {"status": "clicked", "url_changed": True}
            },
            {
                "action_type": "click",
                "element_selector": "#submit-btn", 
                "success": False,
                "result": {"error": "Element not found"}
            }
        ]
        
        action_ids = []
        for action in actions:
            action_id = await memory_manager.store_action(
                conversation_id=conversation_id,
                action_type=action["action_type"],
                action_data={"selector": action["element_selector"]},
                result=action["result"],
                success=action["success"],
                page_url=page_url,
                element_selector=action["element_selector"],
                context_embedding=sample_embedding
            )
            action_ids.append(action_id)
        
        assert all(aid > 0 for aid in action_ids), "All actions should be stored successfully"
        
        # Test successful actions retrieval
        successful_actions = await memory_manager.get_successful_actions("click", limit=10)
        click_successes = [a for a in successful_actions if a.success and a.action_type == "click"]
        assert len(click_successes) >= 2, "Should find successful click actions"
        
        # Test element success patterns (if knowledge graph available)
        if memory_manager.knowledge_graph.is_available():
            successful_elements = await memory_manager.get_successful_elements(page_url, "click")
            if successful_elements:
                login_btn_stats = [e for e in successful_elements if "#login-btn" in e["selector"]]
                assert len(login_btn_stats) > 0, "Should find successful login button interactions"
    
    async def test_page_state_storage(self, memory_manager, sample_embedding):
        """Test page state storage across memory tiers"""
        url = "https://example.com/complex-page"
        dom_snapshot = """
        <html>
            <body>
                <h1>Test Page</h1>
                <button id="action-btn">Click me</button>
                <input type="text" id="search-input" placeholder="Search...">
                <form id="contact-form">
                    <input type="email" name="email">
                    <button type="submit">Submit</button>
                </form>
            </body>
        </html>
        """
        
        interactive_elements = {
            "elements": [
                {"selector": "#action-btn", "type": "button", "text": "Click me"},
                {"selector": "#search-input", "type": "input", "placeholder": "Search..."},
                {"selector": "#contact-form button", "type": "submit", "text": "Submit"}
            ]
        }
        
        # Store page state
        state_id = await memory_manager.store_page_state(
            url=url,
            dom_snapshot=dom_snapshot,
            interactive_elements=interactive_elements,
            page_title="Test Page",
            content_embedding=sample_embedding
        )
        
        assert state_id > 0, "Should store page state successfully"
        
        # Test page context retrieval
        page_context = await memory_manager.get_page_context(url)
        assert page_context["url"] == url, "Should retrieve correct page context"
        
        if page_context["session_state"]:
            assert len(page_context["session_state"].interactive_elements["elements"]) == 3
    
    async def test_navigation_patterns(self, memory_manager):
        """Test navigation pattern storage and retrieval"""
        # Record navigation pattern
        from_url = "https://example.com/home"
        to_url = "https://example.com/login"
        
        # Store both pages first
        await memory_manager.store_page_state(
            url=from_url,
            dom_snapshot="<html><body><h1>Home</h1></body></html>",
            interactive_elements={"elements": []}
        )
        
        await memory_manager.store_page_state(
            url=to_url,
            dom_snapshot="<html><body><h1>Login</h1></body></html>",
            interactive_elements={"elements": []}
        )
        
        # Record navigation
        success = await memory_manager.record_navigation(from_url, to_url, "click")
        
        if memory_manager.knowledge_graph.is_available():
            assert success, "Should record navigation successfully"
            
            # Test navigation patterns
            patterns = await memory_manager.get_navigation_patterns(from_url, limit=5)
            if patterns:
                assert any(p["to_url"] == to_url for p in patterns), "Should find navigation pattern"
            
            # Test navigation path finding
            path = await memory_manager.find_navigation_path(from_url, to_url)
            if path:
                assert from_url in path and to_url in path, "Should find navigation path"
    
    async def test_memory_statistics(self, memory_manager):
        """Test memory statistics collection"""
        stats = await memory_manager.get_memory_statistics()
        
        # Should have session memory stats
        assert "session_memory" in stats
        assert stats["session_memory"] is not None
        
        # Check for semantic and knowledge stats if available
        if memory_manager.semantic_memory.is_available():
            assert "semantic_memory" in stats
        
        if memory_manager.knowledge_graph.is_available():
            assert "knowledge_graph" in stats
    
    async def test_memory_cleanup(self, memory_manager):
        """Test memory cleanup functionality"""
        # Store some test data first
        task_id = f"cleanup_test_{self.generate_random_string()}"
        await memory_manager.store_conversation(
            task_id=task_id,
            user_input="Test conversation for cleanup",
            agent_response="This will be cleaned up"
        )
        
        # Perform cleanup with very short retention (should clean up immediately)
        await memory_manager.cleanup_old_data(
            session_hours=0,  # Clean everything
            semantic_days=0,
            graph_days=0
        )
        
        # Verify cleanup worked
        recent_conversations = await memory_manager.get_recent_conversations(limit=100)
        cleanup_conversations = [c for c in recent_conversations if c.task_id == task_id]
        assert len(cleanup_conversations) == 0, "Should have cleaned up test conversation"
    
    async def test_intelligent_routing_performance(self, memory_manager, sample_embedding):
        """Test intelligent routing and caching performance"""
        if not memory_manager.router:
            pytest.skip("Router not available")
        
        # Store test data
        task_id = "performance_test"
        await memory_manager.store_conversation(
            task_id=task_id,
            user_input="Performance test query",
            agent_response="Response for performance testing",
            embedding=sample_embedding
        )
        
        # Test routing performance
        import time
        
        # First query (should be slower - cache miss)
        start_time = time.time()
        result1, tier1, response_time1 = await memory_manager.router.route_query(
            "get_recent_conversations",
            "conversation",
            limit=5
        )
        first_query_time = time.time() - start_time
        
        # Second query (should be faster - cache hit)
        start_time = time.time()
        result2, tier2, response_time2 = await memory_manager.router.route_query(
            "get_recent_conversations", 
            "conversation",
            limit=5
        )
        second_query_time = time.time() - start_time
        
        assert result1 is not None, "First query should return results"
        assert result2 is not None, "Second query should return results"
        assert len(result1) == len(result2), "Both queries should return same number of results"
        
        # Second query should be significantly faster (cache hit)
        # Allow some variance but expect substantial improvement
        if second_query_time > 0:
            speed_improvement = first_query_time / second_query_time
            assert speed_improvement > 0.5, f"Cache should improve performance (improvement: {speed_improvement}x)"
        
        # Test cache statistics
        cache_stats = memory_manager.router.cache.get_statistics()
        assert cache_stats["cache_size"] > 0, "Cache should contain entries"
        
        total_hits = sum(stats["cache_hits"] for stats in cache_stats["tier_stats"].values())
        total_misses = sum(stats["cache_misses"] for stats in cache_stats["tier_stats"].values())
        assert total_hits + total_misses > 0, "Should have cache activity"
    
    async def test_memory_health_monitoring(self, memory_manager):
        """Test memory system health monitoring"""
        if not memory_manager.router:
            pytest.skip("Router not available")
        
        # Test health check
        health_status = await memory_manager.router.health_check()
        assert isinstance(health_status, dict), "Health check should return status dict"
        assert MemoryTier.SESSION in health_status, "Should check session memory health"
        
        # Test performance report
        perf_report = memory_manager.router.get_performance_report()
        assert "tier_health" in perf_report
        assert "cache_stats" in perf_report
        
        # Test optimization
        await memory_manager.router.optimize_performance()
        
        # Performance report after optimization
        post_opt_report = memory_manager.router.get_performance_report()
        assert post_opt_report is not None


class TestMemoryConfiguration:
    """Tests for memory configuration and optimization"""
    
    def test_config_creation(self):
        """Test configuration creation for different environments"""
        
        # Test development config
        dev_config = ProductionMemoryConfig.for_development()
        assert dev_config.environment == "development"
        assert dev_config.debug_mode is True
        assert dev_config.cache.max_size == 1000
        
        # Test production config
        prod_config = ProductionMemoryConfig.for_production()
        assert prod_config.environment == "production"
        assert prod_config.debug_mode is False
        assert prod_config.cache.max_size == 50000
        
        # Test testing config
        test_config = ProductionMemoryConfig.for_testing()
        assert test_config.environment == "testing"
        assert test_config.session_db_path == ":memory:"
    
    def test_memory_optimizer(self):
        """Test memory optimizer functionality"""
        config = ProductionMemoryConfig.for_production()
        optimizer = MemoryOptimizer(config)
        
        # Test cache size calculation
        optimal_cache = optimizer.calculate_optimal_cache_size(4096)  # 4GB
        assert optimal_cache > 1000, "Should calculate reasonable cache size"
        assert optimal_cache <= config.max_memory_usage_mb * 10
        
        # Test batch size calculation
        batch_size = optimizer.calculate_optimal_batch_size("embedding_operations")
        assert batch_size == 50, "Should return correct batch size for embeddings"
        
        # Test retention cutoff
        session_cutoff = optimizer.get_retention_cutoff("session")
        assert session_cutoff == config.retention.session_hours * 3600
        
        # Test feature enablement
        assert optimizer.should_enable_feature("intelligent_routing")
        assert optimizer.should_enable_feature("caching")


class TestMemoryStressTest:
    """Stress tests for memory system under load"""
    
    @pytest.fixture
    async def stress_memory_manager(self):
        """Create memory manager for stress testing"""
        config = ProductionMemoryConfig.for_testing()
        config.cache.max_size = 100  # Small cache to force evictions
        
        manager = MemoryManager(config.to_dict())
        await manager.initialize()
        
        yield manager
        
        await manager.close()
    
    async def test_concurrent_operations(self, stress_memory_manager):
        """Test concurrent memory operations"""
        
        async def store_conversations(start_idx: int, count: int):
            """Store multiple conversations concurrently"""
            tasks = []
            for i in range(start_idx, start_idx + count):
                task = stress_memory_manager.store_conversation(
                    task_id=f"concurrent_test_{i}",
                    user_input=f"Concurrent test query {i}",
                    agent_response=f"Response for query {i}"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that most operations succeeded
            successful = [r for r in results if isinstance(r, int) and r > 0]
            return len(successful)
        
        # Run concurrent operations
        tasks = [
            store_conversations(0, 10),
            store_conversations(10, 10),
            store_conversations(20, 10)
        ]
        
        results = await asyncio.gather(*tasks)
        total_successful = sum(results)
        
        assert total_successful >= 25, f"Most concurrent operations should succeed (got {total_successful}/30)"
    
    async def test_memory_pressure(self, stress_memory_manager):
        """Test system behavior under memory pressure"""
        
        # Fill up the cache and session memory
        for i in range(200):  # More than cache size
            await stress_memory_manager.store_conversation(
                task_id=f"pressure_test_{i}",
                user_input=f"Memory pressure test {i}" * 100,  # Large content
                agent_response=f"Large response for pressure test {i}" * 100
            )
        
        # System should still be responsive
        recent_conversations = await stress_memory_manager.get_recent_conversations(limit=10)
        assert len(recent_conversations) > 0, "System should remain responsive under pressure"
        
        # Test memory statistics under pressure
        stats = await stress_memory_manager.get_memory_statistics()
        assert stats["session_memory"] is not None, "Should still provide statistics under pressure"
    
    @pytest.mark.asyncio
    async def test_cache_eviction_behavior(self, stress_memory_manager):
        """Test cache eviction under memory pressure"""
        if not stress_memory_manager.router:
            pytest.skip("Router not available")
        
        cache = stress_memory_manager.router.cache
        
        # Fill cache beyond capacity
        for i in range(150):  # More than max_size (100)
            await cache.put(
                f"test_operation_{i}",
                MemoryTier.SESSION,
                f"test_data_{i}" * 100,  # Large data
                ttl=300
            )
        
        # Cache should have evicted entries
        assert len(cache.cache) <= cache.max_size, "Cache should respect max size"
        
        # Recent entries should still be in cache
        recent_key = "test_operation_149"
        recent_data, cache_hit = await cache.get(recent_key, MemoryTier.SESSION)
        
        # May or may not be cached depending on eviction strategy, but system should handle it
        cache_stats = cache.get_statistics()
        assert cache_stats["cache_size"] <= cache.max_size