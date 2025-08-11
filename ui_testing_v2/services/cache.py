"""
Cache service for UI Testing Framework v2
Redis-based caching with fallback to in-memory storage
"""

import asyncio
import json
import logging
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import redis.asyncio as redis
from redis.asyncio.retry import Retry
# from redis.asyncio.backoff import ExponentialBackoff  # Not available in this version

# Define ExponentialBackoff if not available
try:
    from redis.asyncio.backoff import ExponentialBackoff
except ImportError:
    class ExponentialBackoff:
        """Fallback ExponentialBackoff implementation"""
        def __init__(self, cap=0.512, base=0.008):
            self.cap = cap
            self.base = base

from ..core.config import CacheConfig
from ..core.base import BaseCache

logger = logging.getLogger(__name__)


class CacheKey:
    """Cache key generator with consistent naming"""
    
    @staticmethod
    def element_extraction(session_id: UUID, url: str) -> str:
        """Cache key for element extraction results"""
        return f"extraction:{session_id}:{hash(url)}"
    
    @staticmethod
    def ai_analysis(provider: str, prompt_hash: str) -> str:
        """Cache key for AI analysis results"""
        return f"ai:{provider}:{prompt_hash}"
    
    @staticmethod
    def test_generation_legacy(elements_hash: str, requirements_hash: str) -> str:
        """Cache key for test generation results (legacy)"""
        return f"tests:{elements_hash}:{requirements_hash}"
    
    @staticmethod
    def test_generation(session_id: str, url: str) -> str:
        """Cache key for test generation results by session and URL"""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"test_gen:{session_id}:{url_hash}"
    
    @staticmethod
    def code_generation(test_cases_hash: str, framework: str, language: str) -> str:
        """Cache key for code generation results"""
        return f"code:{test_cases_hash}:{framework}:{language}"
    
    @staticmethod
    def session_data(session_id: UUID) -> str:
        """Cache key for session data"""
        return f"session:{session_id}"
    
    @staticmethod
    def user_preferences(user_id: str) -> str:
        """Cache key for user preferences"""
        return f"user:{user_id}:prefs"
    
    @staticmethod
    def workflow_state(workflow_id: str) -> str:
        """Cache key for workflow state"""
        return f"workflow:{workflow_id}"


class RedisCache(BaseCache):
    """Redis-based cache implementation"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config.dict())
        self.redis_url = config.redis_url
        self.password = config.redis_password
        self.max_connections = config.redis_max_connections
        self.default_ttl = config.redis_ttl
        self.pool: Optional[redis.ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
    
    async def _initialize_impl(self) -> None:
        """Initialize Redis connection"""
        try:
            # Create connection pool with retry logic
            retry = Retry(ExponentialBackoff(), retries=3)
            
            self.pool = redis.ConnectionPool.from_url(
                self.redis_url,
                password=self.password,
                max_connections=self.max_connections,
                retry=retry,
                health_check_interval=30,
            )
            
            self.client = redis.Redis(
                connection_pool=self.pool,
                decode_responses=False,  # We'll handle encoding ourselves
            )
            
            # Test connection
            await self.client.ping()
            logger.info("Redis cache initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            raise
    
    async def _cleanup_impl(self) -> None:
        """Cleanup Redis connections"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        logger.info("Redis cache connections closed")
    
    async def _health_check_impl(self) -> Dict[str, Any]:
        """Redis health check"""
        if not self.client:
            return {"status": "not_initialized"}
        
        try:
            latency = await self.client.ping()
            info = await self.client.info()
            
            return {
                "status": "healthy",
                "latency_ms": latency * 1000 if isinstance(latency, float) else 0,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            data = await self.client.get(key)
            if data is None:
                return None
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(data)
        
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in Redis cache"""
        try:
            # Try to serialize as JSON first, then pickle
            try:
                data = json.dumps(value, default=str).encode('utf-8')
            except (TypeError, ValueError):
                data = pickle.dumps(value)
            
            ttl = ttl or self.default_ttl
            result = await self.client.setex(key, ttl, data)
            return bool(result)
        
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            result = await self.client.delete(key)
            return result > 0
        
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        try:
            result = await self.client.exists(key)
            return result > 0
        
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries by pattern"""
        try:
            if pattern:
                keys = await self.client.keys(pattern)
                if keys:
                    return await self.client.delete(*keys)
                return 0
            else:
                # Clear all keys (use with caution)
                return await self.client.flushdb()
        
        except Exception as e:
            logger.error(f"Cache clear error for pattern {pattern}: {e}")
            return 0
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        try:
            values = await self.client.mget(keys)
            result = {}
            
            for key, data in zip(keys, values):
                if data is not None:
                    try:
                        result[key] = json.loads(data.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        result[key] = pickle.loads(data)
            
            return result
        
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return {}
    
    async def set_many(
        self,
        mapping: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> int:
        """Set multiple values in cache"""
        try:
            pipe = self.client.pipeline()
            ttl = ttl or self.default_ttl
            count = 0
            
            for key, value in mapping.items():
                try:
                    data = json.dumps(value, default=str).encode('utf-8')
                except (TypeError, ValueError):
                    data = pickle.dumps(value)
                
                pipe.setex(key, ttl, data)
                count += 1
            
            await pipe.execute()
            return count
        
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return 0
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value"""
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key"""
        try:
            return await self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False


class MemoryCache(BaseCache):
    """In-memory cache implementation (fallback)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_size = config.get("max_size", 1000)
        self.default_ttl = config.get("ttl", 3600)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, datetime] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def _initialize_impl(self) -> None:
        """Initialize memory cache"""
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Memory cache initialized")
    
    async def _cleanup_impl(self) -> None:
        """Cleanup memory cache"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self._cache.clear()
        self._access_times.clear()
        logger.info("Memory cache cleaned up")
    
    async def _health_check_impl(self) -> Dict[str, Any]:
        """Memory cache health check"""
        return {
            "status": "healthy",
            "cache_size": len(self._cache),
            "max_size": self.max_size,
            "memory_usage_percent": (len(self._cache) / self.max_size) * 100,
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        entry = self._cache.get(key)
        if not entry:
            return None
        
        # Check expiration
        if entry["expires_at"] and datetime.utcnow() > entry["expires_at"]:
            await self.delete(key)
            return None
        
        # Update access time
        self._access_times[key] = datetime.utcnow()
        return entry["value"]
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in memory cache"""
        # Check size limit and evict if necessary
        if len(self._cache) >= self.max_size and key not in self._cache:
            await self._evict_lru()
        
        ttl = ttl or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None
        
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
        }
        self._access_times[key] = datetime.utcnow()
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache"""
        if key in self._cache:
            del self._cache[key]
            self._access_times.pop(key, None)
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache"""
        return key in self._cache
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear memory cache entries"""
        if pattern:
            # Simple pattern matching (only supports * wildcard)
            import fnmatch
            keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
            for key in keys_to_delete:
                await self.delete(key)
            return len(keys_to_delete)
        else:
            count = len(self._cache)
            self._cache.clear()
            self._access_times.clear()
            return count
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        await self.delete(lru_key)
    
    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                now = datetime.utcnow()
                expired_keys = []
                
                for key, entry in self._cache.items():
                    if entry["expires_at"] and now > entry["expires_at"]:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    await self.delete(key)
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")


class CacheService:
    """High-level cache service with intelligent fallback"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.primary_cache: Optional[BaseCache] = None
        self.fallback_cache: Optional[BaseCache] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize cache service with primary and fallback caches"""
        if self._initialized:
            return
        
        try:
            # Try to initialize Redis cache first
            self.primary_cache = RedisCache(self.config)
            await self.primary_cache.initialize()
            logger.info("Using Redis as primary cache")
        
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}")
            self.primary_cache = None
        
        # Always initialize memory cache as fallback
        self.fallback_cache = MemoryCache(self.config.dict())
        await self.fallback_cache.initialize()
        logger.info("Memory cache initialized as fallback")
        
        self._initialized = True
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with fallback logic"""
        # Try primary cache first
        if self.primary_cache:
            try:
                value = await self.primary_cache.get(key)
                if value is not None:
                    return value
            except Exception as e:
                logger.error(f"Primary cache get error: {e}")
        
        # Fallback to memory cache
        if self.fallback_cache:
            return await self.fallback_cache.get(key)
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in both caches"""
        primary_success = False
        fallback_success = False
        
        # Set in primary cache
        if self.primary_cache:
            try:
                primary_success = await self.primary_cache.set(key, value, ttl)
            except Exception as e:
                logger.error(f"Primary cache set error: {e}")
        
        # Set in fallback cache
        if self.fallback_cache:
            try:
                fallback_success = await self.fallback_cache.set(key, value, ttl)
            except Exception as e:
                logger.error(f"Fallback cache set error: {e}")
        
        return primary_success or fallback_success
    
    async def delete(self, key: str) -> bool:
        """Delete value from both caches"""
        primary_success = False
        fallback_success = False
        
        if self.primary_cache:
            try:
                primary_success = await self.primary_cache.delete(key)
            except Exception as e:
                logger.error(f"Primary cache delete error: {e}")
        
        if self.fallback_cache:
            try:
                fallback_success = await self.fallback_cache.delete(key)
            except Exception as e:
                logger.error(f"Fallback cache delete error: {e}")
        
        return primary_success or fallback_success
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries"""
        total_cleared = 0
        
        if self.primary_cache:
            try:
                total_cleared += await self.primary_cache.clear(pattern)
            except Exception as e:
                logger.error(f"Primary cache clear error: {e}")
        
        if self.fallback_cache:
            try:
                total_cleared += await self.fallback_cache.clear(pattern)
            except Exception as e:
                logger.error(f"Fallback cache clear error: {e}")
        
        return total_cleared
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all cache backends"""
        health = {"cache_service": "healthy"}
        
        if self.primary_cache:
            health["primary_cache"] = await self.primary_cache.health_check()
        else:
            health["primary_cache"] = {"status": "not_available"}
        
        if self.fallback_cache:
            health["fallback_cache"] = await self.fallback_cache.health_check()
        else:
            health["fallback_cache"] = {"status": "not_available"}
        
        return health
    
    async def cleanup(self) -> None:
        """Cleanup all cache resources"""
        if self.primary_cache:
            await self.primary_cache.cleanup()
        
        if self.fallback_cache:
            await self.fallback_cache.cleanup()
        
        logger.info("Cache service cleaned up")
