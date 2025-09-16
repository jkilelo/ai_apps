"""Security hardening module for AI-First Smart Browser"""

from .encryption import (
    SecureKeyManager,
    APIKeyValidator,
    SecretSanitizer,
    SecurityAuditor as KeySecurityAuditor,
    get_secure_key_manager,
    get_api_key,
    sanitize_for_logging
)

from .rate_limiter import (
    RateLimiter,
    QuotaManager,
    TokenBucket,
    SlidingWindowCounter,
    RateLimitRule,
    QuotaInfo,
    get_rate_limiter,
    get_quota_manager,
    rate_limit,
    check_quota
)

from .audit import (
    SecurityAuditor,
    SecurityFinding,
    ComplianceCheck,
    run_security_audit
)

__all__ = [
    # Encryption and key management
    "SecureKeyManager",
    "APIKeyValidator", 
    "SecretSanitizer",
    "KeySecurityAuditor",
    "get_secure_key_manager",
    "get_api_key",
    "sanitize_for_logging",
    
    # Rate limiting and quotas
    "RateLimiter",
    "QuotaManager",
    "TokenBucket",
    "SlidingWindowCounter", 
    "RateLimitRule",
    "QuotaInfo",
    "get_rate_limiter",
    "get_quota_manager",
    "rate_limit",
    "check_quota",
    
    # Security auditing
    "SecurityAuditor",
    "SecurityFinding",
    "ComplianceCheck", 
    "run_security_audit"
]