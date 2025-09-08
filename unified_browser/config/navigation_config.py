"""
Navigation configuration module.

This module defines settings for browser navigation strategies and behaviors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core import (
    ADAPTIVE_WAIT_ENABLED,
    DEFAULT_NAVIGATION_TIMEOUT,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_WAIT_TIMEOUT,
    INFINITE_SCROLL_DETECTION,
    LAZY_LOAD_DETECTION,
    MAX_NAVIGATION_PER_MINUTE,
    MAX_RETRY_COUNT,
    MUTATION_OBSERVER_ENABLED,
    NavigationStrategy,
    PAGE_STABILITY_CHECK,
    PAGE_STABILITY_TIMEOUT,
    PREDICTIVE_WAIT_MODEL,
    RECOVERY_STRATEGIES,
    WAIT_STRATEGY_LEARNING,
)


@dataclass
class WaitStrategyConfig:
    """Configuration for page wait strategies."""

    # Default strategy
    default_strategy: NavigationStrategy = NavigationStrategy.LOAD

    # Timeout settings
    navigation_timeout: int = DEFAULT_NAVIGATION_TIMEOUT
    wait_timeout: int = DEFAULT_WAIT_TIMEOUT
    stability_timeout: int = PAGE_STABILITY_TIMEOUT

    # Advanced waiting
    adaptive_wait: bool = ADAPTIVE_WAIT_ENABLED
    predictive_wait: bool = PREDICTIVE_WAIT_MODEL
    wait_strategy_learning: bool = WAIT_STRATEGY_LEARNING

    # Page state detection
    check_page_stability: bool = PAGE_STABILITY_CHECK
    detect_lazy_load: bool = LAZY_LOAD_DETECTION
    detect_infinite_scroll: bool = INFINITE_SCROLL_DETECTION
    use_mutation_observer: bool = MUTATION_OBSERVER_ENABLED

    # Network idle settings
    network_idle_timeout: int = 500
    network_idle_inflight: int = 0

    # Custom wait conditions
    wait_for_selectors: List[str] = field(default_factory=list)
    wait_until_visible: List[str] = field(default_factory=list)
    wait_for_functions: List[str] = field(default_factory=list)


@dataclass
class RetryConfig:
    """Configuration for navigation retry logic."""

    # Retry settings
    enabled: bool = True
    max_retries: int = DEFAULT_RETRY_COUNT
    max_total_retries: int = MAX_RETRY_COUNT
    initial_delay_ms: int = DEFAULT_RETRY_DELAY

    # Backoff strategy
    use_exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    max_delay_ms: int = 10000
    jitter: bool = True

    # Retry conditions
    retry_on_timeout: bool = True
    retry_on_network_error: bool = True
    retry_on_http_error: bool = True
    retry_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])

    # Recovery strategies
    recovery_strategies: List[str] = field(default_factory=lambda: RECOVERY_STRATEGIES.copy())
    auto_select_strategy: bool = True


@dataclass
class RedirectConfig:
    """Configuration for handling redirects."""

    # Redirect following
    follow_redirects: bool = True
    max_redirects: int = 10

    # Redirect types
    follow_http_redirects: bool = True
    follow_meta_redirects: bool = True
    follow_javascript_redirects: bool = True

    # Security
    allow_external_redirects: bool = True
    trusted_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)

    # Redirect handling
    preserve_method: bool = False  # Preserve POST on 301/302
    strip_sensitive_headers: bool = True
    redirect_timeout_ms: int = 5000


@dataclass
class ScrollConfig:
    """Configuration for page scrolling."""

    # Auto-scrolling
    auto_scroll: bool = False
    scroll_to_load_content: bool = True

    # Scroll behavior
    scroll_speed: str = "smooth"  # instant, smooth, auto
    scroll_step_pixels: int = 100
    scroll_delay_ms: int = 100

    # Infinite scroll
    handle_infinite_scroll: bool = True
    max_scroll_attempts: int = 10
    scroll_threshold_pixels: int = 200

    # Scroll detection
    detect_scroll_end: bool = True
    wait_after_scroll_ms: int = 500
    check_new_content: bool = True


@dataclass
class HistoryConfig:
    """Configuration for navigation history."""

    # History tracking
    track_history: bool = True
    max_history_size: int = 100

    # History features
    enable_back_forward: bool = True
    cache_pages: bool = False
    preserve_scroll_position: bool = True

    # Session management
    save_session: bool = False
    session_file: Optional[str] = None
    restore_tabs: bool = False

    # Breadcrumbs
    generate_breadcrumbs: bool = True
    max_breadcrumb_depth: int = 10


@dataclass
class PerformanceConfig:
    """Configuration for navigation performance."""

    # Resource blocking
    block_images: bool = False
    block_stylesheets: bool = False
    block_fonts: bool = False
    block_media: bool = False

    # Caching
    use_cache: bool = True
    cache_size_mb: int = 100
    clear_cache_on_start: bool = False

    # Parallel navigation
    allow_parallel_navigation: bool = False
    max_parallel_navigations: int = 3

    # Preloading
    preload_links: bool = False
    prefetch_dns: bool = True
    preconnect_origins: List[str] = field(default_factory=list)

    # Metrics collection
    collect_metrics: bool = True
    metrics_sample_rate: float = 1.0


@dataclass
class InterceptionConfig:
    """Configuration for request/response interception."""

    # Interception
    intercept_requests: bool = False
    intercept_responses: bool = False

    # Request modification
    modify_headers: Dict[str, str] = field(default_factory=dict)
    block_patterns: List[str] = field(default_factory=list)
    allow_patterns: List[str] = field(default_factory=list)

    # Response modification
    inject_scripts: List[str] = field(default_factory=list)
    inject_styles: List[str] = field(default_factory=list)
    modify_content: bool = False

    # Mock responses
    mock_responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Logging
    log_intercepted: bool = False
    save_har: bool = False


@dataclass
class NavigationConfig:
    """Main navigation configuration."""

    # Rate limiting
    max_navigations_per_minute: int = MAX_NAVIGATION_PER_MINUTE
    throttle_navigations: bool = False
    navigation_delay_ms: int = 0

    # Sub-configurations
    wait_strategy: WaitStrategyConfig = field(default_factory=WaitStrategyConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    redirect: RedirectConfig = field(default_factory=RedirectConfig)
    scroll: ScrollConfig = field(default_factory=ScrollConfig)
    history: HistoryConfig = field(default_factory=HistoryConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    interception: InterceptionConfig = field(default_factory=InterceptionConfig)

    # Error handling
    continue_on_error: bool = False
    screenshot_on_error: bool = True
    collect_console_logs: bool = True

    @classmethod
    def fast_navigation(cls) -> NavigationConfig:
        """Create configuration optimized for speed."""
        return cls(
            wait_strategy=WaitStrategyConfig(
                default_strategy=NavigationStrategy.COMMIT,
                navigation_timeout=10000,
                adaptive_wait=False,
                check_page_stability=False,
            ),
            retry=RetryConfig(
                enabled=False,
            ),
            performance=PerformanceConfig(
                block_images=True,
                block_stylesheets=True,
                block_fonts=True,
                block_media=True,
                use_cache=True,
            ),
        )

    @classmethod
    def reliable_navigation(cls) -> NavigationConfig:
        """Create configuration optimized for reliability."""
        return cls(
            wait_strategy=WaitStrategyConfig(
                default_strategy=NavigationStrategy.NETWORK_IDLE,
                navigation_timeout=60000,
                adaptive_wait=True,
                check_page_stability=True,
                detect_lazy_load=True,
                detect_infinite_scroll=True,
            ),
            retry=RetryConfig(
                enabled=True,
                max_retries=5,
                use_exponential_backoff=True,
                recovery_strategies=RECOVERY_STRATEGIES.copy(),
            ),
            scroll=ScrollConfig(
                auto_scroll=True,
                handle_infinite_scroll=True,
            ),
        )

    @classmethod
    def stealth_navigation(cls) -> NavigationConfig:
        """Create configuration for stealth navigation."""
        return cls(
            throttle_navigations=True,
            navigation_delay_ms=2000,
            wait_strategy=WaitStrategyConfig(
                default_strategy=NavigationStrategy.LOAD,
                adaptive_wait=True,
                use_mutation_observer=False,  # Can be detected
            ),
            retry=RetryConfig(
                enabled=True,
                jitter=True,  # Random delays
            ),
            performance=PerformanceConfig(
                block_images=False,  # Load everything normally
                block_stylesheets=False,
                collect_metrics=False,  # Don't collect metrics
            ),
            interception=InterceptionConfig(
                intercept_requests=False,  # Don't intercept
                intercept_responses=False,
            ),
        )

    @classmethod
    def debug_navigation(cls) -> NavigationConfig:
        """Create configuration for debugging."""
        return cls(
            wait_strategy=WaitStrategyConfig(
                default_strategy=NavigationStrategy.NETWORK_IDLE,
                navigation_timeout=120000,
                check_page_stability=True,
            ),
            retry=RetryConfig(
                enabled=True,
                max_retries=1,
            ),
            history=HistoryConfig(
                track_history=True,
                generate_breadcrumbs=True,
            ),
            performance=PerformanceConfig(
                collect_metrics=True,
            ),
            interception=InterceptionConfig(
                intercept_requests=True,
                intercept_responses=True,
                log_intercepted=True,
                save_har=True,
            ),
            screenshot_on_error=True,
            collect_console_logs=True,
        )
