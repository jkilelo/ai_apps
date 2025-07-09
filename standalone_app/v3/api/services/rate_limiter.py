"""Rate limiting service using sliding window algorithm"""
import asyncio
import time
from typing import Dict, List
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter with sliding window"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "unique_clients": set()
        }
    
    async def is_allowed(self, client_id: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed for client"""
        async with self.lock:
            current_time = time.time()
            client_requests = self.requests[client_id]
            
            # Update stats
            self.stats["total_requests"] += 1
            self.stats["unique_clients"].add(client_id)
            
            # Remove old requests outside the window
            cutoff_time = current_time - window_seconds
            while client_requests and client_requests[0] < cutoff_time:
                client_requests.popleft()
            
            # Check if limit exceeded
            if len(client_requests) >= max_requests:
                self.stats["blocked_requests"] += 1
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                return False
            
            # Add current request
            client_requests.append(current_time)
            return True
    
    async def get_remaining(self, client_id: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests for client"""
        async with self.lock:
            current_time = time.time()
            client_requests = self.requests[client_id]
            
            # Remove old requests
            cutoff_time = current_time - window_seconds
            while client_requests and client_requests[0] < cutoff_time:
                client_requests.popleft()
            
            return max(0, max_requests - len(client_requests))
    
    async def reset(self, client_id: str):
        """Reset rate limit for specific client"""
        async with self.lock:
            if client_id in self.requests:
                del self.requests[client_id]
                logger.info(f"Rate limit reset for client: {client_id}")
    
    async def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        return {
            "total_requests": self.stats["total_requests"],
            "blocked_requests": self.stats["blocked_requests"],
            "block_rate": f"{(self.stats['blocked_requests'] / max(1, self.stats['total_requests'])) * 100:.2f}%",
            "unique_clients": len(self.stats["unique_clients"]),
            "active_clients": len(self.requests)
        }
    
    async def cleanup_old_entries(self, older_than_seconds: int = 3600):
        """Clean up old client entries"""
        async with self.lock:
            current_time = time.time()
            cutoff_time = current_time - older_than_seconds
            
            clients_to_remove = []
            for client_id, requests in self.requests.items():
                # Remove old requests
                while requests and requests[0] < cutoff_time:
                    requests.popleft()
                
                # Mark empty clients for removal
                if not requests:
                    clients_to_remove.append(client_id)
            
            # Remove empty clients
            for client_id in clients_to_remove:
                del self.requests[client_id]
            
            if clients_to_remove:
                logger.info(f"Cleaned up {len(clients_to_remove)} inactive clients")

# Global rate limiter instance
rate_limiter = RateLimiter()