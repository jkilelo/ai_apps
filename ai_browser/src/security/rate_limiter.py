"""Rate limiting and API quota management"""
import time
import asyncio
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
from pathlib import Path

from loguru import logger


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    name: str
    max_requests: int
    time_window: int  # seconds
    burst_limit: Optional[int] = None  # Allow burst above normal rate
    cooldown_period: int = 60  # seconds to wait after limit exceeded


@dataclass
class QuotaInfo:
    """API quota information"""
    provider: str
    daily_limit: int
    daily_used: int
    hourly_limit: int
    hourly_used: int
    cost_limit_usd: float
    cost_used_usd: float
    reset_time: datetime


class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum number of tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        async with self._lock:
            now = time.time()
            
            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + (elapsed * self.refill_rate)
            )
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_for_tokens(self, tokens: int = 1, timeout: float = 60) -> bool:
        """Wait until tokens are available"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.consume(tokens):
                return True
            
            # Calculate wait time until next token is available
            wait_time = min(1.0, tokens / self.refill_rate)
            await asyncio.sleep(wait_time)
        
        return False


class SlidingWindowCounter:
    """Sliding window rate limiter"""
    
    def __init__(self, window_size: int, max_requests: int):
        """
        Args:
            window_size: Window size in seconds
            max_requests: Maximum requests in window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """Check if request is allowed"""
        async with self._lock:
            now = time.time()
            
            # Remove old requests outside window
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            # Check if under limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def time_until_reset(self) -> float:
        """Time in seconds until next request is allowed"""
        if not self.requests:
            return 0.0
        
        oldest_request = self.requests[0]
        return max(0.0, oldest_request + self.window_size - time.time())


class RateLimiter:
    """Comprehensive rate limiting system"""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.limiters: Dict[str, SlidingWindowCounter] = {}
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.blocked_until: Dict[str, float] = {}
        
        # Request tracking
        self.request_counts = defaultdict(int)
        self.last_reset = defaultdict(float)
        
        # Setup default rules
        self._setup_default_rules()
        
        logger.info("Rate limiter initialized")
    
    def _setup_default_rules(self):
        """Setup default rate limiting rules"""
        default_rules = [
            RateLimitRule("openai_gpt4", 60, 60, burst_limit=10),  # 60 req/min
            RateLimitRule("openai_gpt3", 180, 60, burst_limit=30),  # 180 req/min
            RateLimitRule("anthropic_claude", 50, 60, burst_limit=10),  # 50 req/min
            RateLimitRule("google_gemini", 60, 60, burst_limit=15),  # 60 req/min
            RateLimitRule("browser_actions", 300, 60),  # 300 actions/min
            RateLimitRule("page_loads", 120, 60),  # 120 page loads/min
            RateLimitRule("api_global", 1000, 3600)  # 1000 requests/hour global
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: RateLimitRule):
        """Add a rate limiting rule"""
        self.rules[rule.name] = rule
        
        # Create sliding window counter
        self.limiters[rule.name] = SlidingWindowCounter(
            rule.time_window, 
            rule.max_requests
        )
        
        # Create token bucket for burst handling
        if rule.burst_limit:
            self.token_buckets[rule.name] = TokenBucket(
                rule.burst_limit,
                rule.max_requests / rule.time_window  # refill rate
            )
        
        logger.info(f"Added rate limiting rule: {rule.name}")
    
    async def check_rate_limit(self, rule_name: str, tokens: int = 1) -> Tuple[bool, Optional[str]]:
        """Check if request is allowed under rate limit"""
        
        # Check if currently blocked
        if rule_name in self.blocked_until:
            if time.time() < self.blocked_until[rule_name]:
                remaining_time = self.blocked_until[rule_name] - time.time()
                return False, f"Rate limit exceeded, blocked for {remaining_time:.1f}s"
            else:
                del self.blocked_until[rule_name]
        
        if rule_name not in self.rules:
            logger.warning(f"Unknown rate limit rule: {rule_name}")
            return True, None
        
        rule = self.rules[rule_name]
        limiter = self.limiters[rule_name]
        
        # Check sliding window limit
        if not await limiter.is_allowed():
            # Apply cooldown
            self.blocked_until[rule_name] = time.time() + rule.cooldown_period
            
            logger.warning(f"Rate limit exceeded: {rule_name}")
            return False, f"Rate limit exceeded: {rule.max_requests}/{rule.time_window}s"
        
        # Check token bucket for burst control
        if rule_name in self.token_buckets:
            bucket = self.token_buckets[rule_name]
            if not await bucket.consume(tokens):
                return False, "Burst limit exceeded, slow down requests"
        
        return True, None
    
    async def wait_for_rate_limit(self, rule_name: str, tokens: int = 1, timeout: float = 300) -> bool:
        """Wait until request is allowed under rate limit"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            allowed, reason = await self.check_rate_limit(rule_name, tokens)
            
            if allowed:
                return True
            
            # Wait before retrying
            if rule_name in self.limiters:
                wait_time = self.limiters[rule_name].time_until_reset()
                wait_time = min(wait_time, 5.0)  # Maximum 5 second wait
                
                if wait_time > 0:
                    logger.info(f"Waiting {wait_time:.1f}s for rate limit: {rule_name}")
                    await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(1.0)
        
        logger.error(f"Timeout waiting for rate limit: {rule_name}")
        return False
    
    def get_rate_limit_status(self, rule_name: str) -> Dict[str, Any]:
        """Get current rate limit status"""
        if rule_name not in self.rules:
            return {"error": f"Unknown rule: {rule_name}"}
        
        rule = self.rules[rule_name]
        limiter = self.limiters[rule_name]
        
        status = {
            "rule_name": rule_name,
            "max_requests": rule.max_requests,
            "time_window": rule.time_window,
            "current_requests": len(limiter.requests),
            "remaining_requests": rule.max_requests - len(limiter.requests),
            "time_until_reset": limiter.time_until_reset(),
            "is_blocked": rule_name in self.blocked_until
        }
        
        if rule_name in self.blocked_until:
            status["blocked_until"] = self.blocked_until[rule_name]
            status["block_remaining"] = max(0, self.blocked_until[rule_name] - time.time())
        
        return status
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all rate limiters"""
        return {
            rule_name: self.get_rate_limit_status(rule_name)
            for rule_name in self.rules.keys()
        }


class QuotaManager:
    """Manage API quotas and costs"""
    
    def __init__(self, quota_file: Path = Path(".claude/security/quotas.json")):
        self.quota_file = quota_file
        self.quota_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.quotas: Dict[str, QuotaInfo] = {}
        self.usage_history = defaultdict(list)
        
        # Load existing quotas
        self._load_quotas()
        
        # Setup default quotas
        self._setup_default_quotas()
        
        logger.info("Quota manager initialized")
    
    def _setup_default_quotas(self):
        """Setup default quotas for providers"""
        default_quotas = {
            "openai": QuotaInfo(
                provider="openai",
                daily_limit=100000,  # tokens
                daily_used=0,
                hourly_limit=10000,
                hourly_used=0,
                cost_limit_usd=50.0,
                cost_used_usd=0.0,
                reset_time=datetime.now() + timedelta(days=1)
            ),
            "anthropic": QuotaInfo(
                provider="anthropic", 
                daily_limit=50000,
                daily_used=0,
                hourly_limit=5000,
                hourly_used=0,
                cost_limit_usd=30.0,
                cost_used_usd=0.0,
                reset_time=datetime.now() + timedelta(days=1)
            ),
            "google": QuotaInfo(
                provider="google",
                daily_limit=80000,
                daily_used=0,
                hourly_limit=8000, 
                hourly_used=0,
                cost_limit_usd=20.0,
                cost_used_usd=0.0,
                reset_time=datetime.now() + timedelta(days=1)
            )
        }
        
        for provider, quota in default_quotas.items():
            if provider not in self.quotas:
                self.quotas[provider] = quota
    
    def check_quota(self, provider: str, tokens: int, cost: float = 0.0) -> Tuple[bool, str]:
        """Check if request is within quota limits"""
        if provider not in self.quotas:
            logger.warning(f"No quota configured for provider: {provider}")
            return True, "No quota limits"
        
        quota = self.quotas[provider]
        
        # Check if quotas need reset
        if datetime.now() > quota.reset_time:
            self._reset_quota(provider)
        
        # Check daily token limit
        if quota.daily_used + tokens > quota.daily_limit:
            return False, f"Daily token limit exceeded: {quota.daily_used + tokens}/{quota.daily_limit}"
        
        # Check hourly token limit  
        if quota.hourly_used + tokens > quota.hourly_limit:
            return False, f"Hourly token limit exceeded: {quota.hourly_used + tokens}/{quota.hourly_limit}"
        
        # Check cost limit
        if quota.cost_used_usd + cost > quota.cost_limit_usd:
            return False, f"Cost limit exceeded: ${quota.cost_used_usd + cost:.2f}/${quota.cost_limit_usd:.2f}"
        
        return True, "Within quota limits"
    
    def consume_quota(self, provider: str, tokens: int, cost: float = 0.0) -> bool:
        """Consume quota for a request"""
        allowed, reason = self.check_quota(provider, tokens, cost)
        
        if not allowed:
            logger.warning(f"Quota consumption denied for {provider}: {reason}")
            return False
        
        if provider in self.quotas:
            quota = self.quotas[provider]
            quota.daily_used += tokens
            quota.hourly_used += tokens
            quota.cost_used_usd += cost
            
            # Track usage history
            self.usage_history[provider].append({
                "timestamp": datetime.now().isoformat(),
                "tokens": tokens,
                "cost": cost
            })
            
            # Save updated quotas
            self._save_quotas()
            
            logger.debug(f"Quota consumed for {provider}: {tokens} tokens, ${cost:.4f}")
        
        return True
    
    def _reset_quota(self, provider: str):
        """Reset quota for provider"""
        if provider in self.quotas:
            quota = self.quotas[provider]
            
            # Reset daily counters
            quota.daily_used = 0
            quota.cost_used_usd = 0.0
            quota.reset_time = datetime.now() + timedelta(days=1)
            
            # Reset hourly counter (separate from daily reset)
            quota.hourly_used = 0
            
            logger.info(f"Quota reset for provider: {provider}")
            self._save_quotas()
    
    def get_quota_status(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get quota status for provider"""
        if provider not in self.quotas:
            return None
        
        quota = self.quotas[provider]
        
        return {
            "provider": provider,
            "daily_usage": {
                "used": quota.daily_used,
                "limit": quota.daily_limit,
                "percentage": (quota.daily_used / quota.daily_limit) * 100
            },
            "hourly_usage": {
                "used": quota.hourly_used,
                "limit": quota.hourly_limit, 
                "percentage": (quota.hourly_used / quota.hourly_limit) * 100
            },
            "cost_usage": {
                "used": quota.cost_used_usd,
                "limit": quota.cost_limit_usd,
                "percentage": (quota.cost_used_usd / quota.cost_limit_usd) * 100
            },
            "reset_time": quota.reset_time.isoformat(),
            "time_until_reset": (quota.reset_time - datetime.now()).total_seconds()
        }
    
    def _load_quotas(self):
        """Load quotas from file"""
        if not self.quota_file.exists():
            return
        
        try:
            with open(self.quota_file, 'r') as f:
                data = json.load(f)
            
            for provider, quota_data in data.get("quotas", {}).items():
                self.quotas[provider] = QuotaInfo(
                    provider=quota_data["provider"],
                    daily_limit=quota_data["daily_limit"],
                    daily_used=quota_data["daily_used"],
                    hourly_limit=quota_data["hourly_limit"],
                    hourly_used=quota_data["hourly_used"],
                    cost_limit_usd=quota_data["cost_limit_usd"],
                    cost_used_usd=quota_data["cost_used_usd"],
                    reset_time=datetime.fromisoformat(quota_data["reset_time"])
                )
            
        except Exception as e:
            logger.error(f"Failed to load quotas: {e}")
    
    def _save_quotas(self):
        """Save quotas to file"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "quotas": {}
            }
            
            for provider, quota in self.quotas.items():
                data["quotas"][provider] = {
                    "provider": quota.provider,
                    "daily_limit": quota.daily_limit,
                    "daily_used": quota.daily_used,
                    "hourly_limit": quota.hourly_limit,
                    "hourly_used": quota.hourly_used,
                    "cost_limit_usd": quota.cost_limit_usd,
                    "cost_used_usd": quota.cost_used_usd,
                    "reset_time": quota.reset_time.isoformat()
                }
            
            with open(self.quota_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save quotas: {e}")


# Global instances
_rate_limiter = None
_quota_manager = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_quota_manager() -> QuotaManager:
    """Get global quota manager instance"""
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager()
    return _quota_manager


async def rate_limit(rule_name: str, tokens: int = 1):
    """Decorator and context manager for rate limiting"""
    limiter = get_rate_limiter()
    
    allowed, reason = await limiter.check_rate_limit(rule_name, tokens)
    if not allowed:
        # Wait for rate limit
        success = await limiter.wait_for_rate_limit(rule_name, tokens)
        if not success:
            raise Exception(f"Rate limit exceeded and timeout: {reason}")


def check_quota(provider: str, tokens: int, cost: float = 0.0) -> bool:
    """Check and consume quota for API request"""
    quota_manager = get_quota_manager()
    return quota_manager.consume_quota(provider, tokens, cost)