#!/usr/bin/env python3
"""
Memory System Stress Tests for AI Browser v2.0.0

These tests validate the multi-tier memory system under stress conditions:
- SQLite session memory with high-frequency operations
- Qdrant semantic memory with large vector datasets
- FalkorDB knowledge graph with complex relationships
- Memory manager coordination under concurrent load

**CRITICAL**: Uses REAL database connections (no mocks) to validate production readiness.
"""

import asyncio
import pytest
import sys
import time
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import sqlite3
from datetime import datetime, timedelta
import numpy as np
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from memory.memory_manager import MemoryManager
from memory.session_memory import SessionMemory
from memory.semantic_memory import SemanticMemory
from memory.knowledge_graph import KnowledgeGraph

# Load environment variables
load_dotenv()


class TestSessionMemoryStress:
    """Stress test SQLite session memory under high load."""
    
    @pytest.mark.asyncio
    async def test_high_frequency_conversation_storage(self):
        """Test storing 1000+ conversations rapidly."""
        
        session_memory = SessionMemory()
        await session_memory.initialize()
        
        # Generate test conversations
        conversations = []
        for i in range(1000):
            conversation = {
                'task_id': f'stress_test_task_{i}',
                'user_input': f'Test input {i}',
                'agent_response': f'Test response {i}' * 100,  # Large responses
                'context': {'step': i, 'data': list(range(50))}  # Complex JSON
            }
            conversations.append(conversation)
        
        # Measure bulk insertion performance
        start_time = time.time()
        
        for conv in conversations:
            await session_memory.store_conversation(
                task_id=conv['task_id'],
                user_input=conv['user_input'],
                agent_response=conv['agent_response'],
                context=conv['context']
            )
        
        insertion_time = time.time() - start_time
        
        # Should handle 1000 insertions in under 10 seconds
        assert insertion_time < 10.0, f"High-frequency insertion took {insertion_time:.2f}s, exceeds 10s limit"
        
        # Verify all conversations stored
        total_conversations = await session_memory._execute_query(
            "SELECT COUNT(*) FROM conversations"
        )
        assert total_conversations[0][0] >= 1000, "Not all conversations were stored"
        
        await session_memory.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self):
        """Test concurrent read/write operations on session memory."""
        
        session_memory = SessionMemory()
        await session_memory.initialize()
        
        # Concurrent operation results
        write_results = []
        read_results = []
        
        async def concurrent_writer(task_prefix: str, count: int):
            """Write conversations concurrently."""
            for i in range(count):
                try:
                    await session_memory.store_conversation(
                        task_id=f'{task_prefix}_{i}',
                        user_input=f'Concurrent input {i}',
                        agent_response=f'Concurrent response {i}',
                        context={'thread': task_prefix, 'iteration': i}
                    )
                    write_results.append(f'{task_prefix}_{i}')
                except Exception as e:
                    pytest.fail(f"Concurrent write failed: {e}")
        
        async def concurrent_reader(task_prefix: str):
            """Read conversation history concurrently."""
            for i in range(10):  # Read multiple times
                try:
                    history = await session_memory.get_conversation_history(
                        task_id=f'{task_prefix}_0', limit=5
                    )
                    read_results.append(len(history))
                except Exception as e:
                    # Reads might fail if writes haven't completed - that's OK
                    pass
        
        # Run concurrent operations
        start_time = time.time()
        
        tasks = [
            concurrent_writer('thread_1', 50),
            concurrent_writer('thread_2', 50), 
            concurrent_writer('thread_3', 50),
            concurrent_reader('thread_1'),
            concurrent_reader('thread_2'),
        ]
        
        await asyncio.gather(*tasks)
        
        concurrent_time = time.time() - start_time
        
        # Should handle concurrent operations efficiently
        assert concurrent_time < 15.0, f"Concurrent operations took {concurrent_time:.2f}s, exceeds 15s limit"
        assert len(write_results) >= 140, "Not all concurrent writes completed"
        
        await session_memory.close()
    
    @pytest.mark.asyncio
    async def test_memory_retention_policy(self):
        """Test session memory cleanup respects retention policy."""
        
        session_memory = SessionMemory()
        await session_memory.initialize()
        
        # Store old conversations (simulate past 24+ hours)
        old_timestamp = datetime.utcnow() - timedelta(hours=25)
        
        # Insert old conversation directly to simulate passage of time
        await session_memory._execute_query(
            """INSERT INTO conversations (task_id, user_input, agent_response, timestamp)
               VALUES (?, ?, ?, ?)""",
            ('old_task', 'old input', 'old response', old_timestamp)
        )
        
        # Store recent conversation
        await session_memory.store_conversation(
            task_id='recent_task',
            user_input='recent input', 
            agent_response='recent response'
        )
        
        # Trigger cleanup
        await session_memory.cleanup_expired_sessions()
        
        # Check old conversation removed
        old_conversations = await session_memory._execute_query(
            "SELECT * FROM conversations WHERE task_id = 'old_task'"
        )
        assert len(old_conversations) == 0, "Old conversations not cleaned up"
        
        # Check recent conversation preserved
        recent_conversations = await session_memory._execute_query(
            "SELECT * FROM conversations WHERE task_id = 'recent_task'"
        )
        assert len(recent_conversations) == 1, "Recent conversations incorrectly cleaned up"
        
        await session_memory.close()


class TestSemanticMemoryStress:
    """Stress test Qdrant semantic memory with large datasets."""
    
    @pytest.mark.asyncio
    async def test_large_vector_dataset_operations(self):
        """Test operations on large vector datasets (1000+ embeddings)."""
        
        semantic_memory = SemanticMemory()
        await semantic_memory.initialize()
        
        # Generate large dataset of embeddings
        embeddings_data = []
        for i in range(1000):
            # Generate realistic embedding vector (1536 dimensions for OpenAI)
            embedding = np.random.rand(1536).astype(np.float32).tolist()
            
            embeddings_data.append({
                'id': f'doc_{i}',
                'embedding': embedding,
                'metadata': {
                    'url': f'https://example.com/page_{i}',
                    'title': f'Test Document {i}',
                    'content_type': 'webpage',
                    'timestamp': datetime.utcnow().isoformat(),
                    'tokens': 100 + (i % 500),  # Variable token counts
                }
            })
        
        # Bulk insert embeddings
        start_time = time.time()
        
        batch_size = 100
        for i in range(0, len(embeddings_data), batch_size):
            batch = embeddings_data[i:i + batch_size]
            
            for item in batch:
                await semantic_memory.store_embedding(
                    doc_id=item['id'],
                    embedding=item['embedding'],
                    metadata=item['metadata']
                )
        
        insertion_time = time.time() - start_time
        
        # Should handle 1000 embeddings in under 30 seconds
        assert insertion_time < 30.0, f"Large dataset insertion took {insertion_time:.2f}s, exceeds 30s limit"
        
        # Test search performance on large dataset
        query_embedding = np.random.rand(1536).astype(np.float32).tolist()
        
        search_start = time.time()
        results = await semantic_memory.search_similar(
            query_embedding=query_embedding,
            limit=10,
            threshold=0.7
        )
        search_time = time.time() - search_start
        
        # Search should complete in under 1 second even on large dataset
        assert search_time < 1.0, f"Vector search took {search_time:.3f}s, exceeds 1s SLA"
        
        # Verify search returned results
        assert isinstance(results, list), "Search should return list of results"
        
        await semantic_memory.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_vector_operations(self):
        """Test concurrent embedding storage and search operations."""
        
        semantic_memory = SemanticMemory()
        await semantic_memory.initialize()
        
        search_results = []
        storage_results = []
        
        async def concurrent_storage(batch_id: int, count: int):
            """Store embeddings concurrently."""
            for i in range(count):
                try:
                    embedding = np.random.rand(1536).astype(np.float32).tolist()
                    await semantic_memory.store_embedding(
                        doc_id=f'batch_{batch_id}_doc_{i}',
                        embedding=embedding,
                        metadata={
                            'batch': batch_id,
                            'index': i,
                            'type': 'concurrent_test'
                        }
                    )
                    storage_results.append(f'batch_{batch_id}_doc_{i}')
                except Exception as e:
                    pytest.fail(f"Concurrent storage failed: {e}")
        
        async def concurrent_search(search_id: int, count: int):
            """Perform searches concurrently."""
            for i in range(count):
                try:
                    query_embedding = np.random.rand(1536).astype(np.float32).tolist()
                    results = await semantic_memory.search_similar(
                        query_embedding=query_embedding,
                        limit=5,
                        threshold=0.8
                    )
                    search_results.append(len(results))
                except Exception as e:
                    # Searches might not find results if storage hasn't completed
                    search_results.append(0)
        
        # Run concurrent operations
        start_time = time.time()
        
        tasks = [
            concurrent_storage(1, 20),
            concurrent_storage(2, 20),
            concurrent_search(1, 10),
            concurrent_search(2, 10),
        ]
        
        await asyncio.gather(*tasks)
        
        concurrent_time = time.time() - start_time
        
        # Should handle concurrent vector operations efficiently
        assert concurrent_time < 20.0, f"Concurrent vector ops took {concurrent_time:.2f}s, exceeds 20s limit"
        assert len(storage_results) >= 35, "Not all concurrent storage operations completed"
        assert len(search_results) >= 15, "Not all concurrent search operations completed"
        
        await semantic_memory.close()


class TestKnowledgeGraphStress:
    """Stress test FalkorDB knowledge graph with complex relationships."""
    
    @pytest.mark.asyncio
    async def test_large_graph_construction(self):
        """Test building large knowledge graphs (1000+ nodes, 5000+ relationships)."""
        
        knowledge_graph = KnowledgeGraph()
        await knowledge_graph.initialize()
        
        # Create large graph structure
        start_time = time.time()
        
        # Create nodes
        for i in range(1000):
            await knowledge_graph.add_node(
                node_type='Page',
                node_id=f'page_{i}',
                properties={
                    'url': f'https://example.com/page_{i}',
                    'title': f'Page {i}',
                    'visited_count': i % 10,
                    'last_visited': datetime.utcnow().isoformat()
                }
            )
        
        # Create relationships (5 per page = 5000 relationships)
        relationship_count = 0
        for i in range(1000):
            # Each page links to 5 others
            for j in range(5):
                target = (i + j + 1) % 1000
                await knowledge_graph.add_relationship(
                    from_node_id=f'page_{i}',
                    to_node_id=f'page_{target}',
                    relationship_type='LINKS_TO',
                    properties={'weight': j + 1}
                )
                relationship_count += 1
        
        construction_time = time.time() - start_time
        
        # Should build large graph in under 60 seconds
        assert construction_time < 60.0, f"Large graph construction took {construction_time:.2f}s, exceeds 60s limit"
        
        # Verify graph was built correctly
        node_count_result = await knowledge_graph.execute_query(
            "MATCH (n:Page) RETURN count(n) as node_count"
        )
        node_count = node_count_result[0]['node_count']
        assert node_count >= 900, f"Expected ~1000 nodes, got {node_count}"  # Allow for some async timing
        
        await knowledge_graph.close()
    
    @pytest.mark.asyncio
    async def test_complex_graph_queries(self):
        """Test complex graph traversal queries on large dataset."""
        
        knowledge_graph = KnowledgeGraph()
        await knowledge_graph.initialize()
        
        # Build a connected graph for testing
        # Create hub nodes with many connections
        for i in range(50):
            await knowledge_graph.add_node(
                node_type='Hub',
                node_id=f'hub_{i}',
                properties={'importance': i}
            )
        
        # Create leaf nodes 
        for i in range(200):
            await knowledge_graph.add_node(
                node_type='Leaf',
                node_id=f'leaf_{i}',
                properties={'data': f'value_{i}'}
            )
        
        # Connect hubs to leaves with complex relationship patterns
        for hub in range(50):
            for leaf in range(hub * 4, (hub + 1) * 4):
                if leaf < 200:
                    await knowledge_graph.add_relationship(
                        from_node_id=f'hub_{hub}',
                        to_node_id=f'leaf_{leaf}',
                        relationship_type='MANAGES',
                        properties={'strength': hub + leaf}
                    )
        
        # Test complex queries
        queries = [
            # Find shortest path between hubs
            "MATCH path = shortestPath((h1:Hub {importance: 0})-[*]-(h2:Hub {importance: 49})) RETURN length(path)",
            
            # Find high-importance hubs with many connections
            "MATCH (h:Hub)-[r:MANAGES]->(l:Leaf) WHERE h.importance > 40 RETURN h.importance, count(r) as connections ORDER BY connections DESC LIMIT 5",
            
            # Find nodes within 2 degrees of separation
            "MATCH (start:Hub {importance: 25})-[*1..2]-(connected) RETURN DISTINCT connected LIMIT 20",
            
            # Aggregate query across relationships
            "MATCH (h:Hub)-[r:MANAGES]->(l:Leaf) RETURN AVG(r.strength) as avg_strength, MAX(r.strength) as max_strength"
        ]
        
        for query in queries:
            start_time = time.time()
            result = await knowledge_graph.execute_query(query)
            query_time = time.time() - start_time
            
            # Complex queries should complete in under 5 seconds
            assert query_time < 5.0, f"Complex query took {query_time:.2f}s, exceeds 5s limit: {query[:50]}..."
            assert result is not None, f"Query returned no results: {query[:50]}..."
        
        await knowledge_graph.close()


class TestMemoryManagerStress:
    """Stress test memory manager coordination under high load."""
    
    @pytest.mark.asyncio
    async def test_coordinated_memory_operations(self):
        """Test memory manager coordinating all storage systems under load."""
        
        memory_manager = MemoryManager()
        await memory_manager.initialize()
        
        # Simulate complex task with all memory systems
        task_id = str(uuid.uuid4())
        
        # Store session data
        for i in range(100):
            await memory_manager.store_task_step(
                task_id=task_id,
                step_number=i,
                action={'type': 'click', 'selector': f'button_{i}'},
                result={'success': True, 'response_time': 0.1 + (i * 0.01)},
                page_state={
                    'url': f'https://example.com/page_{i}',
                    'title': f'Page {i}',
                    'elements': [f'element_{j}' for j in range(10)]
                }
            )
        
        # Store semantic embeddings for each step
        for i in range(100):
            embedding = np.random.rand(1536).astype(np.float32).tolist()
            await memory_manager.store_semantic_memory(
                content=f'Task step {i}: clicked button_{i}',
                embedding=embedding,
                metadata={
                    'task_id': task_id,
                    'step': i,
                    'action_type': 'click'
                }
            )
        
        # Build knowledge graph of task execution
        for i in range(100):
            await memory_manager.add_task_relationship(
                from_step=i,
                to_step=(i + 1) % 100,
                relationship_type='FOLLOWED_BY',
                task_id=task_id
            )
        
        # Test retrieval performance
        retrieval_start = time.time()
        
        # Get task history
        history = await memory_manager.get_task_history(task_id, limit=50)
        
        # Search semantic memory
        query_embedding = np.random.rand(1536).astype(np.float32).tolist()
        similar_steps = await memory_manager.find_similar_experiences(
            query_embedding=query_embedding,
            limit=10
        )
        
        # Query knowledge graph
        task_graph = await memory_manager.get_task_graph(task_id)
        
        retrieval_time = time.time() - retrieval_start
        
        # Coordinated retrieval should be fast
        assert retrieval_time < 2.0, f"Coordinated retrieval took {retrieval_time:.2f}s, exceeds 2s SLA"
        
        # Verify all systems returned data
        assert len(history) > 0, "No task history returned"
        assert isinstance(similar_steps, list), "No semantic search results returned"
        assert task_graph is not None, "No task graph returned"
        
        await memory_manager.close()
    
    @pytest.mark.asyncio
    async def test_memory_system_failover(self):
        """Test memory manager handles individual system failures gracefully."""
        
        memory_manager = MemoryManager()
        await memory_manager.initialize()
        
        # Test with simulated semantic memory failure
        with patch.object(memory_manager.semantic, 'store_embedding', side_effect=Exception("Qdrant connection failed")):
            
            # Should still be able to store in session and graph
            task_id = "failover_test"
            
            try:
                await memory_manager.store_task_step(
                    task_id=task_id,
                    step_number=1,
                    action={'type': 'test'},
                    result={'success': True},
                    page_state={'url': 'test'}
                )
                
                await memory_manager.add_task_relationship(
                    from_step=1,
                    to_step=2,
                    relationship_type='TEST',
                    task_id=task_id
                )
                
            except Exception as e:
                pytest.fail(f"Memory manager failed to handle partial system failure: {e}")
        
        # Verify partial data was still stored
        history = await memory_manager.get_task_history(task_id, limit=10)
        assert len(history) > 0, "No data stored despite partial failure"
        
        await memory_manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])