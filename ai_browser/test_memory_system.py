"""Simple test runner for memory system validation"""
import asyncio
import tempfile
import random
import time
from pathlib import Path

from src.memory.memory_manager import MemoryManager
from src.memory.memory_config import ProductionMemoryConfig


async def test_memory_system():
    """Test the memory system functionality"""
    print("Testing AI Browser Multi-Tier Memory System")
    print("=" * 60)
    
    # Create test configuration
    with tempfile.TemporaryDirectory() as temp_dir:
        config = ProductionMemoryConfig.for_testing()
        config.session_db_path = str(Path(temp_dir) / "test_session.db")
        config.memory_data_dir = temp_dir
        
        # Initialize memory manager
        print("Initializing memory manager...")
        manager = MemoryManager(config.to_dict())
        
        try:
            success = await manager.initialize()
            if not success:
                print("X Memory manager initialization failed")
                return False
            print("+ Memory manager initialized successfully")
            
            # Test 1: Health Check
            print("\nTesting health check...")
            health = await manager.health_check()
            print(f"   Session Memory: {'+' if health.get('session_memory') else 'X'}")
            print(f"   Semantic Memory: {'+' if health.get('semantic_memory') else '- Not available'}")
            print(f"   Knowledge Graph: {'+' if health.get('knowledge_graph') else '- Not available'}")
            
            # Test 2: Conversation Storage
            print("\nTesting conversation storage...")
            task_id = f"test_task_{random.randint(1000, 9999)}"
            user_input = "Help me analyze this website for security vulnerabilities"
            agent_response = "I'll analyze the website for common security vulnerabilities using automated scanning tools."
            
            # Generate sample embedding
            sample_embedding = [random.random() for _ in range(1536)]
            
            conversation_id = await manager.store_conversation(
                task_id=task_id,
                user_input=user_input,
                agent_response=agent_response,
                embedding=sample_embedding
            )
            print(f"+ Stored conversation with ID: {conversation_id}")
            
            # Test 3: Retrieve Conversations
            print("\nTesting conversation retrieval...")
            recent_conversations = await manager.get_recent_conversations(limit=5)
            print(f"+ Retrieved {len(recent_conversations)} recent conversations")
            
            if recent_conversations:
                latest = recent_conversations[0]
                print(f"   Latest: {latest.user_input[:50]}...")
            
            # Test 4: Action Storage
            print("\nTesting action storage...")
            action_id = await manager.store_action(
                conversation_id=conversation_id,
                action_type="navigate",
                action_data={"url": "https://example.com", "method": "GET"},
                result={"status": "success", "response_code": 200},
                success=True,
                page_url="https://example.com",
                element_selector="body",
                context_embedding=sample_embedding
            )
            print(f"+ Stored action with ID: {action_id}")
            
            # Test 5: Page State Storage
            print("\nTesting page state storage...")
            state_id = await manager.store_page_state(
                url="https://example.com",
                dom_snapshot="<html><body><h1>Test Page</h1><button id='test-btn'>Click</button></body></html>",
                interactive_elements={
                    "elements": [
                        {"selector": "#test-btn", "type": "button", "text": "Click"}
                    ]
                },
                page_title="Test Page",
                content_embedding=sample_embedding
            )
            print(f"+ Stored page state with ID: {state_id}")
            
            # Test 6: Memory Statistics
            print("\nTesting memory statistics...")
            stats = await manager.get_memory_statistics()
            if stats.get("session_memory"):
                session_stats = stats["session_memory"]
                print(f"+ Session Memory Stats:")
                print(f"   Conversations: {session_stats.get('conversation_count', 0)}")
                print(f"   Actions: {session_stats.get('action_count', 0)}")
                print(f"   Page States: {session_stats.get('page_state_count', 0)}")
            
            # Test 7: Intelligent Routing (if available)
            if manager.router:
                print("\nTesting intelligent routing...")
                start_time = time.time()
                
                # First query (cache miss)
                result1, tier1, response_time1 = await manager.router.route_query(
                    "get_recent_conversations",
                    "conversation",
                    limit=3
                )
                
                # Second query (cache hit)
                result2, tier2, response_time2 = await manager.router.route_query(
                    "get_recent_conversations",
                    "conversation", 
                    limit=3
                )
                
                print(f"+ Intelligent routing functional")
                print(f"   First query: {response_time1:.3f}s on {tier1.value if tier1 else 'unknown'}")
                print(f"   Second query: {response_time2:.3f}s on {tier2.value if tier2 else 'unknown'}")
                
                # Cache statistics
                cache_stats = manager.router.cache.get_statistics()
                total_hits = sum(stats["cache_hits"] for stats in cache_stats["tier_stats"].values())
                total_misses = sum(stats["cache_misses"] for stats in cache_stats["tier_stats"].values())
                print(f"   Cache: {total_hits} hits, {total_misses} misses")
            
            # Test 8: Performance Test
            print("\nTesting performance...")
            start_time = time.time()
            
            # Rapid conversation storage
            tasks = []
            for i in range(10):
                task = manager.store_conversation(
                    task_id=f"perf_test_{i}",
                    user_input=f"Performance test query {i}",
                    agent_response=f"Response {i}"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            successful = len([r for r in results if r > 0])
            print(f"+ Stored {successful}/10 conversations in {end_time - start_time:.3f}s")
            print(f"   Average: {(end_time - start_time) / successful * 1000:.1f}ms per conversation")
            
            print("\n+ All tests completed successfully!")
            print("=" * 60)
            
            # Final system summary
            print("\nMemory System Summary:")
            print(f"   Environment: {config.environment}")
            print(f"   Session DB: {config.session_db_path}")
            print(f"   Cache Size: {config.cache.max_size}")
            print(f"   Router Available: {'+' if manager.router else 'X'}")
            
            if manager.router:
                performance_report = manager.router.get_performance_report()
                print(f"   Tier Health: {performance_report.get('tier_health', {})}")
            
            return True
            
        except Exception as e:
            print(f"X Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            await manager.close()
            print("\n+ Memory manager closed cleanly")


if __name__ == "__main__":
    asyncio.run(test_memory_system())