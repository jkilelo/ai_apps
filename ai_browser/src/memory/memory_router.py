"""Intelligent memory router and caching layer for optimal memory tier coordination"""
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
from collections import OrderedDict, defaultdict

from loguru import logger

from .session_memory import SessionMemory, ConversationModel, ActionModel, PageStateModel
from .semantic_memory import SemanticMemory, EmbeddingDocument
from .knowledge_graph import KnowledgeGraph


class MemoryTier(Enum):
    """Memory tier enumeration"""
    SESSION = "session"          # SQLite - fastest, ephemeral
    SEMANTIC = "semantic"        # Qdrant - vector search, medium-term
    KNOWLEDGE = "knowledge"      # FalkorDB - relationships, long-term


class CacheStrategy(Enum):
    """Cache strategy enumeration"""
    LRU = "lru"                 # Least Recently Used
    LFU = "lfu"                 # Least Frequently Used
    TTL = "ttl"                 # Time To Live
    ADAPTIVE = "adaptive"       # Adaptive based on access patterns


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    hit_ratio: float = 0.0
    tier: MemoryTier = MemoryTier.SESSION
    size_bytes: int = 0
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update access timestamp and count"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class MemoryStats:
    """Memory tier statistics"""
    tier: MemoryTier
    total_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    data_size: int = 0
    
    @property
    def hit_ratio(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


class IntelligentCache:
    """Multi-tier intelligent cache with adaptive strategies"""
    
    def __init__(self, max_size: int = 10000, strategy: CacheStrategy = CacheStrategy.ADAPTIVE):
        self.max_size = max_size
        self.strategy = strategy
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.access_patterns: Dict[str, List[float]] = defaultdict(list)
        self.tier_preferences: Dict[str, MemoryTier] = {}
        
        # Cache statistics
        self.stats = {
            MemoryTier.SESSION: MemoryStats(MemoryTier.SESSION),
            MemoryTier.SEMANTIC: MemoryStats(MemoryTier.SEMANTIC),
            MemoryTier.KNOWLEDGE: MemoryStats(MemoryTier.KNOWLEDGE)
        }
    
    def _generate_cache_key(self, operation: str, **params) -> str:
        """Generate consistent cache key"""
        key_data = {"op": operation, **params}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value"""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (list, tuple)):
                return sum(self._estimate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(self._estimate_size(k) + self._estimate_size(v) for k, v in value.items())
            else:
                return len(str(value))
        except Exception:
            return 1000  # Default estimate
    
    def _should_cache(self, tier: MemoryTier, operation: str, response_time: float) -> bool:
        """Determine if operation should be cached"""
        # Always cache expensive operations
        if response_time > 1.0:  # > 1 second
            return True
        
        # Cache based on tier characteristics
        if tier == MemoryTier.SEMANTIC and response_time > 0.1:  # Vector search
            return True
        elif tier == MemoryTier.KNOWLEDGE and response_time > 0.05:  # Graph queries
            return True
        elif tier == MemoryTier.SESSION and response_time > 0.01:  # Database queries
            return True
        
        return False
    
    def _select_eviction_candidate(self) -> Optional[str]:
        """Select cache entry for eviction based on strategy"""
        if not self.cache:
            return None
        
        if self.strategy == CacheStrategy.LRU:
            # Least recently used
            return min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        
        elif self.strategy == CacheStrategy.LFU:
            # Least frequently used
            return min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
        
        elif self.strategy == CacheStrategy.TTL:
            # Expired entries first, then LRU
            expired = [k for k, v in self.cache.items() if v.is_expired()]
            if expired:
                return expired[0]
            return min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        
        elif self.strategy == CacheStrategy.ADAPTIVE:
            # Adaptive strategy based on hit ratios and access patterns
            candidates = []
            for key, entry in self.cache.items():
                score = (
                    entry.hit_ratio * 0.4 +  # Hit ratio importance
                    (time.time() - entry.last_accessed) * 0.3 +  # Recency importance
                    (1.0 / max(entry.access_count, 1)) * 0.3  # Frequency importance
                )
                candidates.append((key, score))
            
            # Return candidate with highest eviction score
            return min(candidates, key=lambda x: x[1])[0]
        
        return list(self.cache.keys())[0]  # Fallback
    
    def _evict_entries(self, target_size: int):
        """Evict entries to reach target size"""
        while len(self.cache) > target_size:
            evict_key = self._select_eviction_candidate()
            if evict_key:
                del self.cache[evict_key]
                self.access_patterns.pop(evict_key, None)
                logger.debug(f"Evicted cache entry: {evict_key}")
    
    async def get(self, operation: str, tier: MemoryTier, **params) -> Tuple[Optional[Any], bool]:
        """Get from cache with hit/miss tracking"""
        cache_key = self._generate_cache_key(operation, **params)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired():
                entry.touch()
                self.stats[tier].cache_hits += 1
                
                # Update access patterns for adaptive strategy
                self.access_patterns[cache_key].append(time.time())
                if len(self.access_patterns[cache_key]) > 100:
                    self.access_patterns[cache_key] = self.access_patterns[cache_key][-50:]
                
                logger.debug(f"Cache HIT: {operation} (tier: {tier.value})")
                return entry.value, True
        
        self.stats[tier].cache_misses += 1
        logger.debug(f"Cache MISS: {operation} (tier: {tier.value})")
        return None, False
    
    async def put(
        self, 
        operation: str, 
        tier: MemoryTier, 
        value: Any, 
        ttl: Optional[float] = None,
        **params
    ):
        """Store in cache with eviction management"""
        if not self._should_cache(tier, operation, 0.1):  # Default response time for caching decision
            return
        
        cache_key = self._generate_cache_key(operation, **params)
        
        # Evict if necessary
        if len(self.cache) >= self.max_size:
            self._evict_entries(int(self.max_size * 0.9))  # Evict to 90% capacity
        
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            value=value,
            tier=tier,
            size_bytes=self._estimate_size(value),
            ttl=ttl
        )
        
        self.cache[cache_key] = entry
        logger.debug(f"Cached: {operation} (tier: {tier.value}, size: {entry.size_bytes} bytes)")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_size = sum(entry.size_bytes for entry in self.cache.values())
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "total_memory_bytes": total_size,
            "strategy": self.strategy.value,
            "tier_stats": {tier.value: {
                "total_queries": stat.total_queries,
                "cache_hits": stat.cache_hits,
                "cache_misses": stat.cache_misses,
                "hit_ratio": stat.hit_ratio,
                "avg_response_time": stat.avg_response_time
            } for tier, stat in self.stats.items()},
            "top_accessed": [
                {"key": k, "access_count": v.access_count, "hit_ratio": v.hit_ratio}
                for k, v in sorted(self.cache.items(), key=lambda x: x[1].access_count, reverse=True)[:10]
            ]
        }


class MemoryRouter:
    """Intelligent router for memory tier operations"""
    
    def __init__(
        self, 
        session_memory: SessionMemory,
        semantic_memory: SemanticMemory,
        knowledge_graph: KnowledgeGraph,
        cache_size: int = 10000
    ):
        self.session_memory = session_memory
        self.semantic_memory = semantic_memory
        self.knowledge_graph = knowledge_graph
        self.cache = IntelligentCache(max_size=cache_size)
        
        # Tier health status
        self.tier_health = {
            MemoryTier.SESSION: True,
            MemoryTier.SEMANTIC: semantic_memory.is_available(),
            MemoryTier.KNOWLEDGE: knowledge_graph.is_available()
        }
        
        # Performance metrics
        self.performance_metrics = defaultdict(lambda: defaultdict(list))
        
        logger.info("Memory router initialized")
    
    def _record_performance(self, tier: MemoryTier, operation: str, response_time: float, success: bool):
        """Record performance metrics"""
        self.performance_metrics[tier][operation].append({
            "response_time": response_time,
            "success": success,
            "timestamp": time.time()
        })
        
        # Keep only recent metrics (last 1000 entries per operation)
        if len(self.performance_metrics[tier][operation]) > 1000:
            self.performance_metrics[tier][operation] = self.performance_metrics[tier][operation][-500:]
    
    def _select_optimal_tier(self, operation: str, data_type: str) -> List[MemoryTier]:
        """Select optimal memory tier(s) based on operation and data characteristics"""
        
        # Tier selection strategy based on operation type and data characteristics
        strategies = {
            # Conversation operations - prefer session for recency, semantic for similarity
            "get_recent_conversations": [MemoryTier.SESSION],
            "search_similar_conversations": [MemoryTier.SEMANTIC, MemoryTier.SESSION],
            "store_conversation": [MemoryTier.SESSION, MemoryTier.SEMANTIC],
            
            # Page operations - all tiers benefit different aspects
            "store_page_state": [MemoryTier.SESSION, MemoryTier.SEMANTIC, MemoryTier.KNOWLEDGE],
            "get_page_context": [MemoryTier.KNOWLEDGE, MemoryTier.SESSION],
            "search_similar_pages": [MemoryTier.SEMANTIC],
            
            # Action operations - knowledge graph for patterns, session for recent
            "store_action": [MemoryTier.SESSION, MemoryTier.KNOWLEDGE],
            "get_successful_actions": [MemoryTier.KNOWLEDGE, MemoryTier.SESSION],
            "search_action_patterns": [MemoryTier.SEMANTIC, MemoryTier.KNOWLEDGE],
            
            # Navigation operations - primarily knowledge graph
            "record_navigation": [MemoryTier.KNOWLEDGE],
            "find_navigation_path": [MemoryTier.KNOWLEDGE],
            "get_navigation_patterns": [MemoryTier.KNOWLEDGE],
            
            # Statistics and analytics
            "get_statistics": [MemoryTier.SESSION, MemoryTier.SEMANTIC, MemoryTier.KNOWLEDGE]
        }
        
        # Get base strategy
        preferred_tiers = strategies.get(operation, [MemoryTier.SESSION])
        
        # Filter by availability
        available_tiers = [tier for tier in preferred_tiers if self.tier_health[tier]]
        
        if not available_tiers:
            # Fallback to session memory if nothing else available
            available_tiers = [MemoryTier.SESSION]
        
        logger.debug(f"Operation '{operation}' routed to tiers: {[t.value for t in available_tiers]}")
        return available_tiers
    
    async def route_query(
        self, 
        operation: str, 
        data_type: str = "generic",
        cache_ttl: Optional[float] = 300,  # 5 minutes default TTL
        **params
    ) -> Tuple[Any, MemoryTier, float]:
        """Route query to optimal memory tier with caching"""
        
        # Try cache first
        cached_result, cache_hit = await self.cache.get(operation, MemoryTier.SESSION, **params)
        if cache_hit:
            return cached_result, MemoryTier.SESSION, 0.001  # Cache access time
        
        # Select optimal tiers
        candidate_tiers = self._select_optimal_tier(operation, data_type)
        
        # Try each tier in preference order
        for tier in candidate_tiers:
            if not self.tier_health[tier]:
                continue
            
            start_time = time.time()
            try:
                result = await self._execute_tier_operation(tier, operation, **params)
                response_time = time.time() - start_time
                
                if result is not None:
                    # Record successful performance
                    self._record_performance(tier, operation, response_time, True)
                    
                    # Cache result
                    await self.cache.put(operation, tier, result, ttl=cache_ttl, **params)
                    
                    logger.debug(f"Query '{operation}' successful on {tier.value} ({response_time:.3f}s)")
                    return result, tier, response_time
            
            except Exception as e:
                response_time = time.time() - start_time
                self._record_performance(tier, operation, response_time, False)
                logger.warning(f"Query '{operation}' failed on {tier.value}: {e}")
                
                # Mark tier as potentially unhealthy if consistent failures
                await self._check_tier_health(tier)
        
        # No successful result from any tier
        logger.error(f"Query '{operation}' failed on all available tiers")
        return None, MemoryTier.SESSION, 0.0
    
    async def _execute_tier_operation(self, tier: MemoryTier, operation: str, **params) -> Any:
        """Execute operation on specific memory tier"""
        
        if tier == MemoryTier.SESSION:
            return await self._execute_session_operation(operation, **params)
        elif tier == MemoryTier.SEMANTIC:
            return await self._execute_semantic_operation(operation, **params)
        elif tier == MemoryTier.KNOWLEDGE:
            return await self._execute_knowledge_operation(operation, **params)
        
        raise ValueError(f"Unknown memory tier: {tier}")
    
    async def _execute_session_operation(self, operation: str, **params) -> Any:
        """Execute operation on session memory"""
        if operation == "get_recent_conversations":
            return await self.session_memory.get_recent_conversations(params.get("limit", 10))
        elif operation == "get_task_history":
            return await self.session_memory.get_task_history(params["task_id"])
        elif operation == "get_successful_actions":
            return await self.session_memory.get_successful_actions(
                params.get("action_type"), params.get("limit", 50)
            )
        elif operation == "get_page_state":
            return await self.session_memory.get_page_state(params["url"])
        elif operation == "get_statistics":
            return await self.session_memory.get_statistics()
        
        return None
    
    async def _execute_semantic_operation(self, operation: str, **params) -> Any:
        """Execute operation on semantic memory"""
        if not self.semantic_memory.is_available():
            return None
        
        if operation == "search_similar_pages":
            return await self.semantic_memory.search_similar_pages(
                params["query_embedding"], params.get("limit", 5)
            )
        elif operation == "search_similar_tasks":
            return await self.semantic_memory.search_similar_tasks(
                params["query_embedding"], params.get("limit", 5)
            )
        elif operation == "search_similar_actions":
            return await self.semantic_memory.search_similar_actions(
                params["query_embedding"], params.get("action_type"), params.get("limit", 10)
            )
        elif operation == "get_statistics":
            return await self.semantic_memory.get_collection_info()
        
        return None
    
    async def _execute_knowledge_operation(self, operation: str, **params) -> Any:
        """Execute operation on knowledge graph"""
        if not self.knowledge_graph.is_available():
            return None
        
        if operation == "get_successful_elements":
            return await self.knowledge_graph.get_successful_elements(
                params["page_url"], params.get("action_type")
            )
        elif operation == "get_navigation_patterns":
            return await self.knowledge_graph.get_navigation_patterns(
                params.get("from_url"), params.get("limit", 10)
            )
        elif operation == "find_navigation_path":
            return await self.knowledge_graph.find_shortest_path(
                params["from_url"], params["to_url"]
            )
        elif operation == "get_page_statistics":
            return await self.knowledge_graph.get_page_statistics(params["url"])
        elif operation == "get_statistics":
            return await self.knowledge_graph.get_graph_statistics()
        
        return None
    
    async def _check_tier_health(self, tier: MemoryTier):
        """Check and update tier health status"""
        try:
            if tier == MemoryTier.SESSION:
                await self.session_memory.get_statistics()
                self.tier_health[tier] = True
            elif tier == MemoryTier.SEMANTIC and self.semantic_memory.is_available():
                await self.semantic_memory.get_collection_info()
                self.tier_health[tier] = True
            elif tier == MemoryTier.KNOWLEDGE and self.knowledge_graph.is_available():
                await self.knowledge_graph.get_graph_statistics()
                self.tier_health[tier] = True
        except Exception:
            self.tier_health[tier] = False
            logger.warning(f"Memory tier {tier.value} marked as unhealthy")
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform comprehensive health check on all tiers"""
        for tier in MemoryTier:
            await self._check_tier_health(tier)
        
        return self.tier_health.copy()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        report = {
            "tier_health": self.tier_health.copy(),
            "cache_stats": self.cache.get_statistics(),
            "tier_performance": {}
        }
        
        for tier, operations in self.performance_metrics.items():
            tier_stats = {}
            for operation, metrics in operations.items():
                if not metrics:
                    continue
                
                recent_metrics = [m for m in metrics if time.time() - m["timestamp"] < 3600]  # Last hour
                successful_metrics = [m for m in recent_metrics if m["success"]]
                
                if recent_metrics:
                    tier_stats[operation] = {
                        "total_requests": len(recent_metrics),
                        "successful_requests": len(successful_metrics),
                        "success_rate": len(successful_metrics) / len(recent_metrics),
                        "avg_response_time": sum(m["response_time"] for m in successful_metrics) / len(successful_metrics) if successful_metrics else 0,
                        "p95_response_time": sorted([m["response_time"] for m in successful_metrics])[int(len(successful_metrics) * 0.95)] if successful_metrics else 0
                    }
            
            if tier_stats:
                report["tier_performance"][tier.value] = tier_stats
        
        return report
    
    async def optimize_performance(self):
        """Optimize memory system performance based on collected metrics"""
        logger.info("Starting memory performance optimization...")
        
        # Analyze performance patterns
        report = self.get_performance_report()
        
        # Adjust cache strategy based on hit ratios
        cache_stats = report["cache_stats"]
        overall_hit_ratio = sum(
            stats["cache_hits"] / max(stats["cache_hits"] + stats["cache_misses"], 1)
            for stats in cache_stats["tier_stats"].values()
        ) / len(cache_stats["tier_stats"])
        
        if overall_hit_ratio < 0.3:  # Low hit ratio
            self.cache.strategy = CacheStrategy.LFU  # Focus on frequently used items
        elif overall_hit_ratio > 0.8:  # High hit ratio
            self.cache.strategy = CacheStrategy.TTL  # Can afford to be more aggressive with TTL
        else:
            self.cache.strategy = CacheStrategy.ADAPTIVE  # Balanced approach
        
        # Clean up unhealthy tiers
        for tier, healthy in self.tier_health.items():
            if not healthy:
                logger.warning(f"Attempting to restore unhealthy tier: {tier.value}")
                await self._check_tier_health(tier)
        
        # Preemptive cache warming for frequently accessed operations
        await self._warm_cache()
        
        logger.info("Memory performance optimization completed")
    
    async def _warm_cache(self):
        """Preemptively warm cache with frequently accessed data"""
        try:
            # Warm with recent conversations
            recent_conversations = await self.session_memory.get_recent_conversations(10)
            if recent_conversations:
                await self.cache.put(
                    "get_recent_conversations", 
                    MemoryTier.SESSION, 
                    recent_conversations,
                    ttl=300,
                    limit=10
                )
            
            # Warm with general statistics
            session_stats = await self.session_memory.get_statistics()
            if session_stats:
                await self.cache.put(
                    "get_statistics",
                    MemoryTier.SESSION,
                    session_stats,
                    ttl=600
                )
            
            logger.debug("Cache warmed with frequently accessed data")
        
        except Exception as e:
            logger.warning(f"Cache warming failed: {e}")