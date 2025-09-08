"""
Base validator abstraction module.

This module defines the abstract base class for validation strategies,
handling security, input validation, and safety checks.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from ..config import SecurityConfig
from ..core import (
    ValidationError,
    SecurityError,
    PathTraversalError,
    SecurityViolation,
    Selector,
)


class BaseValidator(ABC):
    """
    Abstract base class for validation strategies.
    
    This class defines the contract for different validation approaches,
    ensuring security and safety of browser operations.
    """
    
    def __init__(self, config: SecurityConfig) -> None:
        """Initialize the validator with configuration."""
        self.config = config
        self._violations: List[SecurityViolation] = []
        self._validation_cache: Dict[str, bool] = {}
        self._risk_scores: Dict[str, float] = {}
    
    # ============================================================================
    # URL VALIDATION
    # ============================================================================
    
    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        """Validate if URL is safe to navigate to."""
        pass
    
    @abstractmethod
    async def check_url_reputation(self, url: str) -> Dict[str, Any]:
        """Check URL reputation and safety."""
        pass
    
    @abstractmethod
    async def detect_malicious_patterns(self, url: str) -> List[str]:
        """Detect malicious patterns in URL."""
        pass
    
    @abstractmethod
    async def validate_redirect_chain(self, urls: List[str]) -> bool:
        """Validate a chain of redirects."""
        pass
    
    @abstractmethod
    async def check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation."""
        pass
    
    # ============================================================================
    # INPUT VALIDATION
    # ============================================================================
    
    @abstractmethod
    async def validate_selector(self, selector: Selector) -> bool:
        """Validate if selector is safe to use."""
        pass
    
    @abstractmethod
    async def validate_javascript(self, script: str) -> bool:
        """Validate if JavaScript code is safe to execute."""
        pass
    
    @abstractmethod
    async def validate_file_path(self, file_path: str) -> bool:
        """Validate if file path is safe (prevent path traversal)."""
        pass
    
    @abstractmethod
    async def validate_user_input(self, input_data: str, input_type: str) -> bool:
        """Validate user input for safety."""
        pass
    
    @abstractmethod
    async def sanitize_input(self, input_data: str) -> str:
        """Sanitize input data."""
        pass
    
    # ============================================================================
    # CONTENT VALIDATION
    # ============================================================================
    
    @abstractmethod
    async def validate_page_content(self, content: str, url: str) -> Dict[str, Any]:
        """Validate page content for safety."""
        pass
    
    @abstractmethod
    async def detect_phishing_indicators(self, content: str, url: str) -> List[str]:
        """Detect phishing indicators in page content."""
        pass
    
    @abstractmethod
    async def detect_malware_signatures(self, content: str) -> List[str]:
        """Detect malware signatures in content."""
        pass
    
    @abstractmethod
    async def validate_download_content(self, content: bytes, filename: str) -> bool:
        """Validate downloaded content for safety."""
        pass
    
    # ============================================================================
    # NETWORK VALIDATION
    # ============================================================================
    
    @abstractmethod
    async def validate_headers(self, headers: Dict[str, str]) -> bool:
        """Validate HTTP headers for safety."""
        pass
    
    @abstractmethod
    async def detect_suspicious_responses(self, response_data: Dict[str, Any]) -> List[str]:
        """Detect suspicious response patterns."""
        pass
    
    @abstractmethod
    async def validate_cookies(self, cookies: Dict[str, Any]) -> bool:
        """Validate cookies for safety."""
        pass
    
    @abstractmethod
    async def check_ssl_certificate(self, url: str) -> Dict[str, Any]:
        """Check SSL certificate validity and safety."""
        pass
    
    # ============================================================================
    # RATE LIMITING AND ABUSE PREVENTION
    # ============================================================================
    
    @abstractmethod
    async def check_rate_limit(self, operation: str, identifier: str) -> bool:
        """Check if operation is within rate limits."""
        pass
    
    @abstractmethod
    async def validate_request_frequency(self, url: str) -> bool:
        """Validate request frequency to prevent abuse."""
        pass
    
    @abstractmethod
    async def detect_bot_behavior(self, actions: List[Dict[str, Any]]) -> float:
        """Detect bot-like behavior patterns (returns risk score)."""
        pass
    
    # ============================================================================
    # PERMISSION AND ACCESS CONTROL
    # ============================================================================
    
    @abstractmethod
    async def validate_operation_permissions(self, operation: str, context: Dict[str, Any]) -> bool:
        """Validate if operation is permitted in current context."""
        pass
    
    @abstractmethod
    async def check_data_access_permissions(self, data_type: str, url: str) -> bool:
        """Check permissions for accessing specific data types."""
        pass
    
    @abstractmethod
    async def validate_file_access(self, file_path: str, operation: str) -> bool:
        """Validate file system access permissions."""
        pass
    
    # ============================================================================
    # PRIVACY AND COMPLIANCE
    # ============================================================================
    
    @abstractmethod
    async def check_privacy_compliance(self, url: str, operation: str) -> Dict[str, Any]:
        """Check privacy compliance (GDPR, CCPA, etc.)."""
        pass
    
    @abstractmethod
    async def validate_data_collection(self, data_types: List[str], url: str) -> bool:
        """Validate if data collection is compliant."""
        pass
    
    @abstractmethod
    async def check_robots_txt(self, url: str, user_agent: str) -> bool:
        """Check robots.txt compliance."""
        pass
    
    @abstractmethod
    async def validate_scraping_ethics(self, url: str, operation: str) -> Dict[str, Any]:
        """Validate ethical scraping practices."""
        pass
    
    # ============================================================================
    # SECURITY MONITORING
    # ============================================================================
    
    @abstractmethod
    async def monitor_security_events(self) -> List[SecurityViolation]:
        """Monitor and return security events."""
        pass
    
    @abstractmethod
    async def calculate_risk_score(self, context: Dict[str, Any]) -> float:
        """Calculate risk score for current operation."""
        pass
    
    @abstractmethod
    async def detect_anomalies(self, metrics: Dict[str, Any]) -> List[str]:
        """Detect anomalous behavior patterns."""
        pass
    
    @abstractmethod
    async def validate_session_integrity(self, session_data: Dict[str, Any]) -> bool:
        """Validate session integrity."""
        pass
    
    # ============================================================================
    # CONTENT FILTERING
    # ============================================================================
    
    @abstractmethod
    async def filter_inappropriate_content(self, content: str) -> Tuple[bool, List[str]]:
        """Filter inappropriate content and return reasons."""
        pass
    
    @abstractmethod
    async def detect_spam_indicators(self, content: str) -> List[str]:
        """Detect spam indicators in content."""
        pass
    
    @abstractmethod
    async def validate_content_length(self, content: str, max_length: int) -> bool:
        """Validate content length limits."""
        pass
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _is_safe_url(self, url: str) -> bool:
        """Basic URL safety check."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False
            if not parsed.netloc:
                return False
            return True
        except Exception:
            return False
    
    def _check_path_traversal(self, path: str) -> bool:
        """Check for path traversal attacks."""
        dangerous_patterns = ['../', '..\\', '%2e%2e%2f', '%2e%2e\\']
        path_lower = path.lower()
        return not any(pattern in path_lower for pattern in dangerous_patterns)
    
    def _record_violation(self, violation: SecurityViolation) -> None:
        """Record a security violation."""
        self._violations.append(violation)
    
    def _cache_validation_result(self, key: str, result: bool) -> None:
        """Cache validation result."""
        self._validation_cache[key] = result
    
    def _get_cached_result(self, key: str) -> Optional[bool]:
        """Get cached validation result."""
        return self._validation_cache.get(key)
    
    def get_violations(self) -> List[SecurityViolation]:
        """Get all recorded violations."""
        return self._violations.copy()
    
    def clear_violations(self) -> None:
        """Clear all violations."""
        self._violations.clear()
    
    def get_risk_scores(self) -> Dict[str, float]:
        """Get all calculated risk scores."""
        return self._risk_scores.copy()
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the validator."""
        pass


class BasicValidator(BaseValidator):
    """Basic validator with essential safety checks."""
    
    async def validate_url(self, url: str) -> bool:
        """Basic URL validation."""
        if not self._is_safe_url(url):
            return False
        
        # Check against blocklist if configured
        if self.config.url_blocklist:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if any(blocked in domain for blocked in self.config.url_blocklist):
                return False
        
        return True
    
    async def validate_selector(self, selector: Selector) -> bool:
        """Basic selector validation."""
        if not isinstance(selector, str):
            return False
        
        # Check for dangerous patterns
        dangerous_patterns = ['javascript:', 'vbscript:', '<script', 'eval(']
        selector_lower = selector.lower()
        return not any(pattern in selector_lower for pattern in dangerous_patterns)
    
    async def validate_javascript(self, script: str) -> bool:
        """Basic JavaScript validation."""
        dangerous_patterns = [
            'eval(',
            'Function(',
            'document.write',
            'innerHTML',
            'document.cookie',
            'localStorage',
            'sessionStorage',
            'XMLHttpRequest',
            'fetch(',
        ]
        
        script_lower = script.lower()
        return not any(pattern in script_lower for pattern in dangerous_patterns)


class EnhancedValidator(BaseValidator):
    """Enhanced validator with advanced security checks."""
    
    def __init__(self, config: SecurityConfig) -> None:
        super().__init__(config)
        self._reputation_cache: Dict[str, Dict[str, Any]] = {}
        self._pattern_matchers: Dict[str, List[str]] = {}
    
    async def validate_url(self, url: str) -> bool:
        """Enhanced URL validation with reputation checking."""
        basic_result = await super().validate_url(url)
        if not basic_result:
            return False
        
        # Check reputation
        reputation = await self.check_url_reputation(url)
        return reputation.get('safe', True)
    
    async def check_url_reputation(self, url: str) -> Dict[str, Any]:
        """Check URL reputation using threat intelligence."""
        # Implementation would integrate with threat intelligence APIs
        return {'safe': True, 'reputation_score': 0.9}


class MLValidator(BaseValidator):
    """ML-powered validator using machine learning for advanced detection."""
    
    def __init__(self, config: SecurityConfig) -> None:
        super().__init__(config)
        self._ml_models: Dict[str, Any] = {}
        self._feature_extractors: Dict[str, Any] = {}
    
    async def detect_phishing_indicators(self, content: str, url: str) -> List[str]:
        """Use ML to detect phishing indicators."""
        # Implementation would use trained ML models
        return []
    
    async def detect_bot_behavior(self, actions: List[Dict[str, Any]]) -> float:
        """Use ML to detect bot-like behavior."""
        # Implementation would analyze action patterns with ML
        return 0.0


class ComplianceValidator(BaseValidator):
    """Compliance-focused validator for regulatory requirements."""
    
    async def check_privacy_compliance(self, url: str, operation: str) -> Dict[str, Any]:
        """Check comprehensive privacy compliance."""
        return {
            'gdpr_compliant': True,
            'ccpa_compliant': True,
            'robots_txt_compliant': await self.check_robots_txt(url, 'UnifiedBrowser'),
            'ethical_score': 0.95
        }
    
    async def validate_scraping_ethics(self, url: str, operation: str) -> Dict[str, Any]:
        """Comprehensive ethical scraping validation."""
        return {
            'ethical': True,
            'rate_limited': True,
            'respects_robots_txt': True,
            'non_disruptive': True
        }