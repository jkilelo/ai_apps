"""
Security configuration module.

This module defines security-related settings for input validation,
rate limiting, and secure operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ..core import (
    ALLOWED_DOWNLOAD_EXTENSIONS,
    ALLOWED_PROTOCOLS,
    BLOCKED_FILE_EXTENSIONS,
    MAX_LLM_CALLS_PER_MINUTE,
    MAX_NAVIGATION_PER_MINUTE,
    MAX_PATH_LENGTH,
    MAX_REQUESTS_PER_SECOND,
    MAX_SELECTOR_LENGTH,
    MAX_URL_LENGTH,
)


@dataclass
class ValidationConfig:
    """Input validation configuration."""

    # URL validation
    validate_urls: bool = True
    max_url_length: int = MAX_URL_LENGTH
    allowed_protocols: List[str] = field(default_factory=lambda: ALLOWED_PROTOCOLS.copy())
    blocked_domains: List[str] = field(default_factory=list)

    # Selector validation
    validate_selectors: bool = True
    max_selector_length: int = MAX_SELECTOR_LENGTH

    # Path validation
    validate_paths: bool = True
    max_path_length: int = MAX_PATH_LENGTH
    blocked_extensions: List[str] = field(default_factory=lambda: BLOCKED_FILE_EXTENSIONS.copy())
    allowed_download_extensions: List[str] = field(
        default_factory=lambda: ALLOWED_DOWNLOAD_EXTENSIONS.copy()
    )

    # Content validation
    sanitize_inputs: bool = True
    max_input_length: int = 10000
    strip_scripts: bool = True
    escape_html: bool = True


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    # Request rate limits
    enabled: bool = True
    max_requests_per_second: int = MAX_REQUESTS_PER_SECOND
    max_navigation_per_minute: int = MAX_NAVIGATION_PER_MINUTE
    max_llm_calls_per_minute: int = MAX_LLM_CALLS_PER_MINUTE

    # Burst settings
    burst_size: int = 10
    burst_window_seconds: int = 1

    # Throttling
    throttle_delay_ms: int = 100
    exponential_backoff: bool = True
    max_retry_delay_ms: int = 5000

    # Per-domain limits
    domain_limits: Dict[str, int] = field(default_factory=dict)

    # Exemptions
    exempt_domains: List[str] = field(default_factory=list)
    exempt_ips: List[str] = field(default_factory=list)


@dataclass
class SandboxConfig:
    """Sandbox configuration for isolated operations."""

    # Sandbox settings
    enabled: bool = False
    sandbox_dir: Optional[Path] = None
    max_sandbox_size_mb: int = 1000

    # Restrictions
    network_access: bool = True
    file_system_access: bool = False
    process_creation: bool = False

    # Allowed operations
    allowed_commands: List[str] = field(default_factory=list)
    allowed_file_ops: List[str] = field(default_factory=lambda: ["read", "write"])

    # Resource limits
    max_memory_mb: int = 512
    max_cpu_percent: int = 50
    max_execution_time_seconds: int = 300


@dataclass
class AuthenticationConfig:
    """Authentication configuration."""

    # Basic auth
    require_auth: bool = False
    username: Optional[str] = None
    password: Optional[str] = None

    # Token auth
    use_token_auth: bool = False
    token: Optional[str] = None
    token_header: str = "Authorization"
    token_prefix: str = "Bearer"

    # API key auth
    use_api_key: bool = False
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"

    # Session management
    session_timeout_minutes: int = 30
    refresh_token_enabled: bool = False

    # Multi-factor auth
    mfa_enabled: bool = False
    mfa_method: str = "totp"  # totp, sms, email


@dataclass
class EncryptionConfig:
    """Encryption configuration."""

    # Data encryption
    encrypt_storage: bool = False
    encryption_algorithm: str = "AES-256-GCM"
    key_derivation_function: str = "PBKDF2"

    # Communication encryption
    enforce_https: bool = True
    min_tls_version: str = "TLSv1.2"
    verify_certificates: bool = True

    # Credential encryption
    encrypt_credentials: bool = True
    credential_storage_path: Optional[Path] = None

    # Cookie encryption
    encrypt_cookies: bool = False
    cookie_encryption_key: Optional[str] = None


@dataclass
class AuditConfig:
    """Audit and logging configuration."""

    # Audit logging
    enabled: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file: Optional[Path] = None

    # What to log
    log_navigations: bool = True
    log_extractions: bool = True
    log_errors: bool = True
    log_security_events: bool = True
    log_performance_metrics: bool = False

    # Sensitive data
    redact_sensitive_data: bool = True
    sensitive_fields: List[str] = field(
        default_factory=lambda: ["password", "token", "api_key", "secret", "credential"]
    )

    # Log retention
    max_log_size_mb: int = 100
    max_log_files: int = 10
    compress_old_logs: bool = True

    # External logging
    send_to_siem: bool = False
    siem_endpoint: Optional[str] = None


@dataclass
class ContentSecurityConfig:
    """Content security policy configuration."""

    # CSP directives
    enabled: bool = True
    default_src: List[str] = field(default_factory=lambda: ["'self'"])
    script_src: List[str] = field(default_factory=lambda: ["'self'", "'unsafe-inline'"])
    style_src: List[str] = field(default_factory=lambda: ["'self'", "'unsafe-inline'"])
    img_src: List[str] = field(default_factory=lambda: ["'self'", "data:", "https:"])
    connect_src: List[str] = field(default_factory=lambda: ["'self'"])
    font_src: List[str] = field(default_factory=lambda: ["'self'"])

    # XSS protection
    xss_protection: bool = True
    xss_filter_mode: str = "block"  # block, sanitize, report

    # Frame options
    frame_ancestors: List[str] = field(default_factory=lambda: ["'none'"])
    x_frame_options: str = "DENY"  # DENY, SAMEORIGIN, ALLOW-FROM

    # Other headers
    strict_transport_security: bool = True
    hsts_max_age: int = 31536000
    content_type_nosniff: bool = True


@dataclass
class SecurityConfig:
    """Main security configuration."""

    # Overall security level
    security_level: str = "high"  # low, medium, high, maximum

    # Sub-configurations
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    authentication: AuthenticationConfig = field(default_factory=AuthenticationConfig)
    encryption: EncryptionConfig = field(default_factory=EncryptionConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    content_security: ContentSecurityConfig = field(default_factory=ContentSecurityConfig)

    # Global settings
    fail_secure: bool = True  # Fail closed on security errors
    paranoid_mode: bool = False  # Maximum security, may break functionality

    @classmethod
    def low_security(cls) -> SecurityConfig:
        """Create low security configuration (development)."""
        return cls(
            security_level="low",
            validation=ValidationConfig(
                validate_urls=False,
                validate_selectors=False,
                validate_paths=False,
                sanitize_inputs=False,
            ),
            rate_limit=RateLimitConfig(enabled=False),
            sandbox=SandboxConfig(enabled=False),
            authentication=AuthenticationConfig(require_auth=False),
            encryption=EncryptionConfig(
                encrypt_storage=False,
                enforce_https=False,
                verify_certificates=False,
            ),
            audit=AuditConfig(enabled=False),
            content_security=ContentSecurityConfig(enabled=False),
            fail_secure=False,
        )

    @classmethod
    def medium_security(cls) -> SecurityConfig:
        """Create medium security configuration (testing)."""
        return cls(
            security_level="medium",
            validation=ValidationConfig(
                validate_urls=True,
                validate_selectors=True,
                validate_paths=True,
                sanitize_inputs=True,
            ),
            rate_limit=RateLimitConfig(
                enabled=True,
                max_requests_per_second=20,
            ),
            sandbox=SandboxConfig(enabled=False),
            authentication=AuthenticationConfig(require_auth=False),
            encryption=EncryptionConfig(
                enforce_https=True,
                verify_certificates=True,
            ),
            audit=AuditConfig(
                enabled=True,
                log_security_events=True,
            ),
        )

    @classmethod
    def high_security(cls) -> SecurityConfig:
        """Create high security configuration (production)."""
        return cls(
            security_level="high",
            validation=ValidationConfig(
                validate_urls=True,
                validate_selectors=True,
                validate_paths=True,
                sanitize_inputs=True,
                strip_scripts=True,
                escape_html=True,
            ),
            rate_limit=RateLimitConfig(
                enabled=True,
                exponential_backoff=True,
            ),
            sandbox=SandboxConfig(
                enabled=True,
                network_access=True,
                file_system_access=False,
            ),
            authentication=AuthenticationConfig(
                require_auth=True,
                session_timeout_minutes=15,
            ),
            encryption=EncryptionConfig(
                encrypt_storage=True,
                encrypt_credentials=True,
                enforce_https=True,
                min_tls_version="TLSv1.3",
            ),
            audit=AuditConfig(
                enabled=True,
                log_security_events=True,
                redact_sensitive_data=True,
            ),
            content_security=ContentSecurityConfig(
                enabled=True,
                xss_protection=True,
            ),
            fail_secure=True,
        )

    @classmethod
    def maximum_security(cls) -> SecurityConfig:
        """Create maximum security configuration (paranoid mode)."""
        return cls(
            security_level="maximum",
            validation=ValidationConfig(
                validate_urls=True,
                validate_selectors=True,
                validate_paths=True,
                sanitize_inputs=True,
                strip_scripts=True,
                escape_html=True,
                max_input_length=1000,
            ),
            rate_limit=RateLimitConfig(
                enabled=True,
                max_requests_per_second=5,
                max_navigation_per_minute=10,
                exponential_backoff=True,
            ),
            sandbox=SandboxConfig(
                enabled=True,
                network_access=False,
                file_system_access=False,
                process_creation=False,
                max_memory_mb=256,
                max_cpu_percent=25,
            ),
            authentication=AuthenticationConfig(
                require_auth=True,
                mfa_enabled=True,
                session_timeout_minutes=5,
            ),
            encryption=EncryptionConfig(
                encrypt_storage=True,
                encrypt_credentials=True,
                encrypt_cookies=True,
                enforce_https=True,
                min_tls_version="TLSv1.3",
                verify_certificates=True,
            ),
            audit=AuditConfig(
                enabled=True,
                log_level="DEBUG",
                log_security_events=True,
                log_performance_metrics=True,
                redact_sensitive_data=True,
            ),
            content_security=ContentSecurityConfig(
                enabled=True,
                xss_protection=True,
                xss_filter_mode="block",
                frame_ancestors=["'none'"],
                strict_transport_security=True,
            ),
            fail_secure=True,
            paranoid_mode=True,
        )
