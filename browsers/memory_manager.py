"""Unified memory manager for all memory layers with intelligent routing and optimization"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger

from .session_memory import SessionMemory, ConversationModel, ActionModel, PageStateModel
from .semantic_memory import SemanticMemory, EmbeddingDocument
from .knowledge_graph import KnowledgeGraph
from .memory_router import MemoryRouter, MemoryTier


class MemoryManager:
    """Unified manager for all memory layers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize memory manager with configuration"""
        self.config = config or {}
        
        # Initialize memory layers
        self.session_memory = SessionMemory(
            db_path=self.config.get('session_db_path', '.claude/memory/session.db')
        )
        
        self.semantic_memory = SemanticMemory(
            host=self.config.get('qdrant_host', 'localhost'),
            port=self.config.get('qdrant_port', 6333),
            collection_name=self.config.get('qdrant_collection', 'browser_memory')
        )
        
        self.knowledge_graph = KnowledgeGraph(
            host=self.config.get('falkordb_host', 'localhost'),
            port=self.config.get('falkordb_port', 6380),  # Updated port
            graph_name=self.config.get('falkordb_graph', 'browser_knowledge')
        )
        
        # Initialize intelligent router
        self.router = None
        self._initialized = False
        logger.info("Memory manager created")
    
    async def initialize(self) -> bool:
        """Initialize all memory layers"""
        try:
            # Initialize session memory (always available)
            logger.info("Initializing session memory...")
            # Session memory initializes automatically in constructor
            
            # Initialize semantic memory (optional)
            logger.info("Initializing semantic memory...")
            semantic_ok = await self.semantic_memory.initialize()
            if not semantic_ok:
                logger.warning("Semantic memory not available - continuing without vector search")
            
            # Initialize knowledge graph (optional)
            logger.info("Initializing knowledge graph...")
            graph_ok = await self.knowledge_graph.initialize()
            if not graph_ok:
                logger.warning("Knowledge graph not available - continuing without graph storage")
            
            # Initialize intelligent router
            self.router = MemoryRouter(
                self.session_memory,
                self.semantic_memory,
                self.knowledge_graph,
                cache_size=self.config.get('cache_size', 10000)
            )
            
            self._initialized = True
            logger.info("Memory manager initialized with intelligent routing")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            return False
    
    async def store_conversation(
        self, 
        task_id: str, 
        user_input: str, 
        agent_response: str,
        embedding: Optional[List[float]] = None
    ) -> int:
        """Store conversation across all applicable layers"""
        # Store in session memory
        conversation = ConversationModel(
            task_id=task_id,
            user_input=user_input,
            agent_response=agent_response
        )
        conversation_id = await self.session_memory.store_conversation(conversation)
        
        # Store in semantic memory if available and embedding provided
        if self.semantic_memory.is_available() and embedding:
            await self.semantic_memory.store_user_task(
                task=user_input,
                embedding=embedding,
                outcome=agent_response
            )
        
        logger.debug(f"Stored conversation {conversation_id} for task {task_id}")
        return conversation_id
    
    async def store_action(
        self, 
        conversation_id: int,
        action_type: str,
        action_data: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        success: bool = False,
        page_url: Optional[str] = None,
        element_selector: Optional[str] = None,
        context_embedding: Optional[List[float]] = None
    ) -> int:
        """Store action across all applicable layers"""
        # Store in session memory
        action = ActionModel(
            conversation_id=conversation_id,
            action_type=action_type,
            action_data=action_data,
            result=result,
            success=success
        )
        action_id = await self.session_memory.store_action(action)
        
        # Store in semantic memory if successful and embedding available
        if success and self.semantic_memory.is_available() and context_embedding:
            context = f"Action: {action_type} on {element_selector or 'unknown'}"
            await self.semantic_memory.store_action_pattern(
                action_type=action_type,
                context=context,
                embedding=context_embedding,
                success=success
            )
        
        # Store in knowledge graph if page context available
        if self.knowledge_graph.is_available() and page_url and element_selector:
            await self.knowledge_graph.record_action(
                action_type=action_type,
                element_selector=element_selector,
                page_url=page_url,
                success=success,
                metadata=action_data
            )
        
        logger.debug(f"Stored action {action_id}: {action_type}")
        return action_id
    
    async def store_page_state(
        self,
        url: str,
        dom_snapshot: str,
        interactive_elements: Dict[str, Any],
        screenshot_path: Optional[str] = None,
        page_title: Optional[str] = None,
        content_embedding: Optional[List[float]] = None
    ) -> int:
        """Store page state across all layers"""
        # Store in session memory
        page_state = PageStateModel(
            url=url,
            dom_snapshot=dom_snapshot,
            screenshot_path=screenshot_path,
            interactive_elements=interactive_elements
        )
        state_id = await self.session_memory.store_page_state(page_state)
        
        # Store in semantic memory
        if self.semantic_memory.is_available() and content_embedding:
            await self.semantic_memory.store_page_content(
                url=url,
                content=dom_snapshot[:1000],  # Truncate for embedding
                embedding=content_embedding,
                metadata={
                    "title": page_title,
                    "element_count": len(interactive_elements.get("elements", []))
                }
            )
        
        # Store in knowledge graph
        if self.knowledge_graph.is_available():
            await self.knowledge_graph.create_page_node(
                url=url,
                title=page_title or url,
                metadata={
                    "element_count": len(interactive_elements.get("elements", [])),
                    "screenshot_available": screenshot_path is not None
                }
            )
            
            # Store elements
            for element in interactive_elements.get("elements", []):
                if "selector" in element and "type" in element:
                    await self.knowledge_graph.create_element_node(
                        selector=element["selector"],
                        element_type=element["type"],
                        page_url=url,
                        metadata=element
                    )
        
        logger.debug(f"Stored page state {state_id} for {url}")
        return state_id
    
    async def record_navigation(self, from_url: str, to_url: str, action_type: str = "navigate") -> bool:
        """Record navigation between pages"""
        if self.knowledge_graph.is_available():
            return await self.knowledge_graph.create_navigation_path(
                from_url=from_url,
                to_url=to_url,
                action_type=action_type
            )
        return False
    
    async def get_recent_conversations(self, limit: int = 10) -> List[ConversationModel]:
        """Get recent conversations using intelligent routing"""
        if self.router:
            result, tier, response_time = await self.router.route_query(
                "get_recent_conversations", 
                "conversation",
                limit=limit
            )
            if result is not None:
                return result
        
        # Fallback to direct session memory
        return await self.session_memory.get_recent_conversations(limit)
    
    async def get_task_history(self, task_id: str) -> List[ConversationModel]:
        """Get conversation history for a task using intelligent routing"""
        if self.router:
            result, tier, response_time = await self.router.route_query(
                "get_task_history",
                "conversation", 
                task_id=task_id
            )
            if result is not None:
                return result
        
        # Fallback to direct session memory
        return await self.session_memory.get_task_history(task_id)
    
    async def search_similar_tasks(
        self, 
        query_embedding: List[float], 
        limit: int = 5
    ) -> List[Tuple[EmbeddingDocument, float]]:
        """Search for similar tasks using semantic memory"""
        if self.semantic_memory.is_available():
            return await self.semantic_memory.search_similar_tasks(query_embedding, limit)
        return []
    
    async def search_similar_pages(
        self, 
        query_embedding: List[float], 
        limit: int = 5
    ) -> List[Tuple[EmbeddingDocument, float]]:
        """Search for similar pages using semantic memory"""
        if self.semantic_memory.is_available():
            return await self.semantic_memory.search_similar_pages(query_embedding, limit)
        return []
    
    async def get_successful_actions(
        self, 
        action_type: Optional[str] = None, 
        limit: int = 50
    ) -> List[ActionModel]:
        """Get successful actions from session memory"""
        return await self.session_memory.get_successful_actions(action_type, limit)
    
    async def get_successful_elements(
        self, 
        page_url: str, 
        action_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get elements with high success rates from knowledge graph"""
        if self.knowledge_graph.is_available():
            return await self.knowledge_graph.get_successful_elements(page_url, action_type)
        return []
    
    async def get_navigation_patterns(
        self, 
        from_url: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get navigation patterns from knowledge graph"""
        if self.knowledge_graph.is_available():
            return await self.knowledge_graph.get_navigation_patterns(from_url, limit)
        return []
    
    async def find_navigation_path(self, from_url: str, to_url: str) -> Optional[List[str]]:
        """Find shortest navigation path between pages"""
        if self.knowledge_graph.is_available():
            return await self.knowledge_graph.find_shortest_path(from_url, to_url)
        return None
    
    async def get_page_context(self, url: str) -> Dict[str, Any]:
        """Get comprehensive context for a page from all memory layers"""
        context = {
            "url": url,
            "session_state": None,
            "statistics": None,
            "successful_elements": [],
            "similar_pages": []
        }
        
        # Get from session memory
        context["session_state"] = await self.session_memory.get_page_state(url)
        
        # Get statistics from knowledge graph
        if self.knowledge_graph.is_available():
            context["statistics"] = await self.knowledge_graph.get_page_statistics(url)
            context["successful_elements"] = await self.knowledge_graph.get_successful_elements(url)
        
        return context
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics from all memory layers"""
        stats = {
            "session_memory": await self.session_memory.get_statistics(),
            "semantic_memory": None,
            "knowledge_graph": None
        }
        
        if self.semantic_memory.is_available():
            stats["semantic_memory"] = await self.semantic_memory.get_collection_info()
        
        if self.knowledge_graph.is_available():
            stats["knowledge_graph"] = await self.knowledge_graph.get_graph_statistics()
        
        return stats
    
    async def cleanup_old_data(self, session_hours: int = 24, semantic_days: int = 30, graph_days: int = 90):
        """Clean up old data from all memory layers"""
        logger.info("Starting memory cleanup...")
        
        # Cleanup session memory
        await self.session_memory.cleanup_old_data(session_hours)
        
        # Cleanup semantic memory
        if self.semantic_memory.is_available():
            await self.semantic_memory.cleanup_old_documents(semantic_days)
        
        # Cleanup knowledge graph
        if self.knowledge_graph.is_available():
            await self.knowledge_graph.cleanup_old_data(graph_days)
        
        logger.info("Memory cleanup completed")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all memory layers"""
        health = {
            "session_memory": True,  # Always available
            "semantic_memory": self.semantic_memory.is_available(),
            "knowledge_graph": self.knowledge_graph.is_available()
        }
        
        # Test basic operations
        try:
            await self.session_memory.get_statistics()
        except Exception:
            health["session_memory"] = False
        
        if self.semantic_memory.is_available():
            try:
                await self.semantic_memory.get_collection_info()
            except Exception:
                health["semantic_memory"] = False
        
        if self.knowledge_graph.is_available():
            try:
                await self.knowledge_graph.get_graph_statistics()
            except Exception:
                health["knowledge_graph"] = False
        
        return health
    
    def is_initialized(self) -> bool:
        """Check if memory manager is initialized"""
        return self._initialized
    
    async def close(self):
        """Close all memory connections"""
        logger.info("Closing memory manager...")
        
        self.session_memory.close()
        
        if self.semantic_memory.is_available():
            await self.semantic_memory.close()
        
        if self.knowledge_graph.is_available():
            await self.knowledge_graph.close()
        
        logger.info("Memory manager closed")