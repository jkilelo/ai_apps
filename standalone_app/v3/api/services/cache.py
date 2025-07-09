"""Advanced caching service with TTL and memory management"""
import asyncio
import time
import json
from typing import Any, Optional, Dict
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """In-memory cache with TTL support and size limits"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        self._cleanup_task = None
    
    async def initialize(self):
        """Initialize cache service"""
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())
        logger.info("Cache service initialized")
    
    async def cleanup(self):
        """Cleanup cache service"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Cache service cleaned up")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        self.stats["total_requests"] += 1
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if entry["expires_at"] > time.time():
                # Move to end (LRU)
                self.cache.move_to_end(key)
                self.stats["hits"] += 1
                logger.debug(f"Cache hit for key: {key}")
                return entry["value"]
            else:
                # Remove expired entry
                del self.cache[key]
                logger.debug(f"Cache entry expired for key: {key}")
        
        self.stats["misses"] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        
        # Check size limit
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Evict oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats["evictions"] += 1
            logger.debug(f"Evicted cache entry: {oldest_key}")
        
        # Add/update entry
        self.cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time()
        }
        
        # Move to end (LRU)
        self.cache.move_to_end(key)
        logger.debug(f"Cache set for key: {key}, TTL: {ttl}s")
    
    async def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache entry deleted: {key}")
            return True
        return False
    
    async def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0
        if self.stats["total_requests"] > 0:
            hit_rate = (self.stats["hits"] / self.stats["total_requests"]) * 100
        
        return {
            **self.stats,
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": f"{hit_rate:.2f}%"
        }
    
    async def warm_up(self):
        """Warm up cache with common queries"""
        # Can be extended to pre-load common queries
        logger.info("Cache warmed up")
    
    async def _cleanup_expired(self):
        """Background task to cleanup expired entries"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                current_time = time.time()
                expired_keys = []
                
                for key, entry in self.cache.items():
                    if entry["expires_at"] <= current_time:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")

# Global cache instance
cache = CacheService()