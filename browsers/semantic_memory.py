"""Qdrant-based semantic memory for vector embeddings"""
import asyncio
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    from qdrant_client.http.exceptions import ResponseHandlingException
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

from loguru import logger


@dataclass
class EmbeddingDocument:
    """Document with embedding"""
    id: Optional[int]
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: Optional[datetime] = None


class SemanticMemory:
    """Manages semantic memory using Qdrant vector database"""
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6333,
        collection_name: str = "browser_memory"
    ):
        if not QDRANT_AVAILABLE:
            logger.warning("Qdrant client not available. Install with: pip install qdrant-client")
            self.client = None
            return
        
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = None
        self.embedding_dim = 1536  # OpenAI text-embedding-3-small dimension
        
    async def initialize(self):
        """Initialize connection and create collection"""
        if not QDRANT_AVAILABLE:
            logger.error("Cannot initialize SemanticMemory: Qdrant client not available")
            return False
        
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            
            # Check if collection exists
            collections = await self._run_sync(self.client.get_collections)
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                await self.create_collection()
            
            logger.info(f"Semantic memory initialized with collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic memory: {e}")
            self.client = None
            return False
    
    async def _run_sync(self, func, *args, **kwargs):
        """Run synchronous function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    
    async def create_collection(self):
        """Create Qdrant collection for browser memory"""
        if not self.client:
            raise RuntimeError("Client not initialized")
        
        def create_collection_func():
            return self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
            )
        
        await self._run_sync(create_collection_func)
        logger.info(f"Created collection '{self.collection_name}'")
    
    def _generate_id(self, content: str) -> int:
        """Generate unique ID for content"""
        # Generate a hash and convert to integer within Qdrant's range
        hash_hex = hashlib.md5(content.encode()).hexdigest()
        # Convert to integer and ensure it's within acceptable range
        return int(hash_hex[:8], 16)  # Use first 8 hex chars for 32-bit integer
    
    async def store_document(self, document: EmbeddingDocument) -> bool:
        """Store document with embedding"""
        if not self.client:
            logger.warning("Semantic memory not available")
            return False
        
        try:
            if not document.embedding:
                logger.error("Document has no embedding")
                return False
            
            if not document.id:
                document.id = self._generate_id(document.content)
            
            # Prepare metadata
            payload = {
                "content": document.content,
                "timestamp": document.timestamp.isoformat() if document.timestamp else datetime.now().isoformat(),
                **document.metadata
            }
            
            point = PointStruct(
                id=document.id,
                vector=document.embedding,
                payload=payload
            )
            
            def upsert_func():
                return self.client.upsert(
                    collection_name=self.collection_name,
                    points=[point]
                )
            
            await self._run_sync(upsert_func)
            
            logger.debug(f"Stored document {document.id} in semantic memory")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store document: {e}")
            return False
    
    async def store_page_content(self, url: str, content: str, embedding: List[float], metadata: Optional[Dict] = None) -> bool:
        """Store page content with embedding"""
        doc_metadata = {
            "type": "page_content",
            "url": url,
            **(metadata or {})
        }
        
        document = EmbeddingDocument(
            id=self._generate_id(f"page_{url}_{content}"),
            content=content,
            metadata=doc_metadata,
            embedding=embedding,
            timestamp=datetime.now()
        )
        
        return await self.store_document(document)
    
    async def store_action_pattern(self, action_type: str, context: str, embedding: List[float], success: bool = True) -> bool:
        """Store successful action patterns"""
        doc_metadata = {
            "type": "action_pattern",
            "action_type": action_type,
            "success": success
        }
        
        document = EmbeddingDocument(
            id=self._generate_id(f"action_{action_type}_{context}"),
            content=context,
            metadata=doc_metadata,
            embedding=embedding,
            timestamp=datetime.now()
        )
        
        return await self.store_document(document)
    
    async def store_user_task(self, task: str, embedding: List[float], outcome: str) -> bool:
        """Store user task and outcome"""
        doc_metadata = {
            "type": "user_task",
            "outcome": outcome
        }
        
        document = EmbeddingDocument(
            id=self._generate_id(f"task_{task}"),
            content=task,
            metadata=doc_metadata,
            embedding=embedding,
            timestamp=datetime.now()
        )
        
        return await self.store_document(document)
    
    async def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        score_threshold: float = 0.7,
        filter_condition: Optional[Dict] = None
    ) -> List[Tuple[EmbeddingDocument, float]]:
        """Search for similar documents"""
        if not self.client:
            logger.warning("Semantic memory not available")
            return []
        
        try:
            # Build filter if provided
            query_filter = None
            if filter_condition:
                conditions = []
                for key, value in filter_condition.items():
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                query_filter = Filter(must=conditions)
            
            # Perform search using a lambda to handle keyword arguments
            def search_func():
                return self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=limit,
                    score_threshold=score_threshold,
                    query_filter=query_filter
                )
            
            search_result = await self._run_sync(search_func)
            
            results = []
            for point in search_result:
                doc = EmbeddingDocument(
                    id=point.id,
                    content=point.payload.get("content", ""),
                    metadata={k: v for k, v in point.payload.items() if k not in ["content", "timestamp"]},
                    timestamp=datetime.fromisoformat(point.payload.get("timestamp", datetime.now().isoformat()))
                )
                results.append((doc, point.score))
            
            logger.debug(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    async def search_similar_pages(self, query_embedding: List[float], limit: int = 5) -> List[Tuple[EmbeddingDocument, float]]:
        """Search for similar page content"""
        return await self.search_similar(
            query_embedding=query_embedding,
            limit=limit,
            filter_condition={"type": "page_content"}
        )
    
    async def search_similar_actions(self, query_embedding: List[float], action_type: Optional[str] = None, limit: int = 10) -> List[Tuple[EmbeddingDocument, float]]:
        """Search for similar successful actions"""
        filter_condition = {"type": "action_pattern", "success": True}
        if action_type:
            filter_condition["action_type"] = action_type
            
        return await self.search_similar(
            query_embedding=query_embedding,
            limit=limit,
            filter_condition=filter_condition
        )
    
    async def search_similar_tasks(self, query_embedding: List[float], limit: int = 5) -> List[Tuple[EmbeddingDocument, float]]:
        """Search for similar user tasks"""
        return await self.search_similar(
            query_embedding=query_embedding,
            limit=limit,
            filter_condition={"type": "user_task"}
        )
    
    async def get_document(self, doc_id: int) -> Optional[EmbeddingDocument]:
        """Get document by ID"""
        if not self.client:
            return None
        
        try:
            def retrieve_func():
                return self.client.retrieve(
                    collection_name=self.collection_name,
                    ids=[doc_id]
                )
            
            points = await self._run_sync(retrieve_func)
            
            if points:
                point = points[0]
                return EmbeddingDocument(
                    id=point.id,
                    content=point.payload.get("content", ""),
                    metadata={k: v for k, v in point.payload.items() if k not in ["content", "timestamp"]},
                    timestamp=datetime.fromisoformat(point.payload.get("timestamp", datetime.now().isoformat()))
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    async def delete_document(self, doc_id: int) -> bool:
        """Delete document by ID"""
        if not self.client:
            return False
        
        try:
            def delete_func():
                return self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=[doc_id]
                )
            
            await self._run_sync(delete_func)
            logger.debug(f"Deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    async def cleanup_old_documents(self, days: int = 30):
        """Clean up documents older than specified days"""
        if not self.client:
            return
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        try:
            # This would require custom filtering logic
            # For now, we'll skip automatic cleanup
            logger.info(f"Semantic memory cleanup not implemented for {days} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old documents: {e}")
    
    async def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """Get collection information"""
        if not self.client:
            return None
        
        try:
            def get_collection_func():
                return self.client.get_collection(
                    collection_name=self.collection_name
                )
            
            info = await self._run_sync(get_collection_func)
            
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.value
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if semantic memory is available"""
        return self.client is not None
    
    async def close(self):
        """Close connection"""
        if self.client:
            # Qdrant client doesn't need explicit closing
            self.client = None
            logger.debug("Semantic memory connection closed")