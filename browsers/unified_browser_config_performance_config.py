"""
Performance configuration module.

This module defines settings for optimizing browser performance, resource usage,
and monitoring metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core import (
    CACHE_SIZE_MB,
    CONNECTION_POOL_SIZE,
    MAX_CONCURRENT_DOWNLOADS,
    MAX_MEMORY_MB,
    METRICS_ENABLED,
    PERFORMANCE_MONITORING,
    PRELOAD_RESOURCES,
    RESOURCE_TIMEOUT,
)


@dataclass
class ResourceBlockingConfig:
    """Configuration for blocking resources."""

    # Resource blocking
    block_images: bool = False
    block_stylesheets: bool = False
    block_scripts: bool = False
    block_fonts: bool = False
    block_media: bool = False
    block_websockets: bool = False
    block_webrtc: bool = False

    # Selective blocking
    blocked_domains: List[str] = field(default_factory=list)
    blocked_url_patterns: List[str] = field(default_factory=list)
    blocked_resource_types: List[str] = field(default_factory=list)

    # Exceptions
    allowed_domains: List[str] = field(default_factory=list)
    allowed_url_patterns: List[str] = field(default_factory=list)

    # Third-party resources
    block_third_party: bool = False
    third_party_exceptions: List[str] = field(default_factory=list)


@dataclass
class CachingConfig:
    """Configuration for caching strategies."""

    # Cache settings
    enabled: bool = True
    cache_size_mb: int = CACHE_SIZE_MB
    cache_location: Optional[str] = None

    # Cache types
    memory_cache: bool = True
    disk_cache: bool = True
    http_cache: bool = True

    # Cache behavior
    cache_images: bool = True
    cache_scripts: bool = True
    cache_stylesheets: bool = True
    cache_fonts: bool = True

    # Cache control
    respect_cache_headers: bool = True
    override_cache_control: bool = False
    max_age_seconds: int = 3600

    # Cache invalidation
    clear_on_start: bool = False
    clear_on_navigation: bool = False
    auto_clear_interval_minutes: Optional[int] = None

    # Persistent storage
    persist_cache: bool = False
    persistent_cache_path: Optional[str] = None


@dataclass
class NetworkConfig:
    """Configuration for network optimization."""

    # Connection pooling
    connection_pool_size: int = CONNECTION_POOL_SIZE
    max_connections_per_host: int = 6
    keep_alive_timeout_ms: int = 30000

    # HTTP/2 settings
    enable_http2: bool = True
    enable_server_push: bool = True
    max_concurrent_streams: int = 100

    # DNS optimization
    prefetch_dns: bool = True
    dns_cache_size: int = 1000
    dns_cache_ttl_seconds: int = 300

    # Preconnect
    preconnect_origins: List[str] = field(default_factory=list)
    max_preconnect_sockets: int = 10

    # Request optimization
    enable_compression: bool = True
    accept_encoding: List[str] = field(default_factory=lambda: ["gzip", "deflate", "br"])

    # Timeouts
    connection_timeout_ms: int = 30000
    read_timeout_ms: int = 30000
    idle_timeout_ms: int = 90000


@dataclass
class RenderingConfig:
    """Configuration for rendering optimization."""

    # Viewport settings
    viewport_width: int = 1920
    viewport_height: int = 1080
    device_scale_factor: float = 1.0

    # Rendering behavior
    wait_for_fonts: bool = False
    wait_for_animations: bool = False
    disable_animations: bool = True
    disable_transitions: bool = True

    # Paint optimization
    enable_hardware_acceleration: bool = True
    force_compositing: bool = True
    use_angle_backend: str = "default"  # default, gl, d3d11, d3d9, vulkan

    # Frame rate
    target_fps: int = 60
    throttle_cpu: bool = False
    cpu_throttle_factor: float = 1.0

    # Lazy loading
    enable_lazy_loading: bool = True
    lazy_load_images: bool = True
    lazy_load_iframes: bool = True

    # Intersection observer
    use_intersection_observer: bool = True
    intersection_threshold: float = 0.1


@dataclass
class MemoryConfig:
    """Configuration for memory management."""

    # Memory limits
    max_memory_mb: int = MAX_MEMORY_MB
    max_heap_size_mb: Optional[int] = None
    max_old_space_size_mb: Optional[int] = None

    # Garbage collection
    aggressive_gc: bool = False
    gc_interval_ms: int = 60000
    idle_gc: bool = True

    # Memory optimization
    limit_dom_size: bool = True
    max_dom_nodes: int = 10000
    clear_unused_memory: bool = True

    # Tab memory management
    discard_idle_tabs: bool = True
    idle_timeout_minutes: int = 30
    max_tabs_in_memory: int = 10

    # Memory monitoring
    monitor_memory: bool = True
    memory_warning_threshold_mb: int = 1024
    memory_critical_threshold_mb: int = 2048


@dataclass
class PreloadConfig:
    """Configuration for resource preloading."""

    # Preload settings
    enabled: bool = PRELOAD_RESOURCES
    preload_strategy: str = "moderate"  # none, moderate, aggressive

    # Resource preloading
    preload_links: bool = True
    preload_scripts: bool = True
    preload_styles: bool = True
    preload_fonts: bool = False
    preload_images: bool = False

    # Prefetch settings
    prefetch_links: bool = True
    max_prefetch_links: int = 10
    prefetch_priority: str = "low"  # low, medium, high

    # Prerender settings
    prerender_links: bool = False
    max_prerender_pages: int = 1

    # Smart preloading
    use_ml_predictions: bool = False
    prediction_confidence_threshold: float = 0.7


@dataclass
class MetricsConfig:
    """Configuration for performance metrics."""

    # Metrics collection
    enabled: bool = METRICS_ENABLED
    collect_navigation_timing: bool = True
    collect_resource_timing: bool = True
    collect_paint_timing: bool = True
    collect_layout_shift: bool = True

    # Web Vitals
    measure_lcp: bool = True  # Largest Contentful Paint
    measure_fid: bool = True  # First Input Delay
    measure_cls: bool = True  # Cumulative Layout Shift
    measure_ttfb: bool = True  # Time to First Byte
    measure_fcp: bool = True  # First Contentful Paint

    # Custom metrics
    custom_metrics: Dict[str, str] = field(default_factory=dict)
    user_timing_marks: List[str] = field(default_factory=list)

    # Sampling
    sample_rate: float = 1.0
    sample_navigation: bool = True
    sample_resources: bool = True

    # Reporting
    report_interval_seconds: int = 60
    batch_metrics: bool = True
    max_batch_size: int = 100

    # Storage
    store_metrics: bool = True
    metrics_storage_path: Optional[str] = None
    retention_days: int = 30


@dataclass
class OptimizationConfig:
    """Configuration for automatic optimization."""

    # Auto-optimization
    auto_optimize: bool = True
    optimization_level: str = "balanced"  # minimal, balanced, aggressive

    # Content optimization
    compress_images: bool = True
    image_quality: int = 85
    convert_images_to_webp: bool = False

    # Code optimization
    minify_javascript: bool = False
    minify_css: bool = False
    remove_comments: bool = False

    # Request optimization
    batch_requests: bool = True
    max_batch_size: int = 10
    deduplicate_requests: bool = True

    # Parallel processing
    parallel_downloads: bool = True
    max_parallel_downloads: int = MAX_CONCURRENT_DOWNLOADS
    parallel_parsing: bool = True

    # Progressive enhancement
    progressive_rendering: bool = True
    stream_parsing: bool = True
    incremental_dom_updates: bool = True


@dataclass
class ThrottlingConfig:
    """Configuration for performance throttling."""

    # Network throttling
    throttle_network: bool = False
    download_throughput_kbps: Optional[int] = None
    upload_throughput_kbps: Optional[int] = None
    latency_ms: Optional[int] = None
    packet_loss_percent: float = 0.0

    # CPU throttling
    throttle_cpu: bool = False
    cpu_slowdown_factor: float = 1.0

    # Throttling profiles
    profile: Optional[str] = None  # slow-3g, fast-3g, slow-4g, fast-4g, wifi
    custom_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class PerformanceConfig:
    """Main performance configuration."""

    # Global settings
    monitoring_enabled: bool = PERFORMANCE_MONITORING
    resource_timeout: int = RESOURCE_TIMEOUT

    # Sub-configurations
    blocking: ResourceBlockingConfig = field(default_factory=ResourceBlockingConfig)
    caching: CachingConfig = field(default_factory=CachingConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    rendering: RenderingConfig = field(default_factory=RenderingConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    preload: PreloadConfig = field(default_factory=PreloadConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    throttling: ThrottlingConfig = field(default_factory=ThrottlingConfig)

    # Performance modes
    mode: str = "balanced"  # fast, balanced, quality, minimal

    @classmethod
    def fast_mode(cls) -> PerformanceConfig:
        """Create configuration for maximum speed."""
        return cls(
            mode="fast",
            blocking=ResourceBlockingConfig(
                block_images=True,
                block_fonts=True,
                block_media=True,
                block_third_party=True,
            ),
            caching=CachingConfig(
                enabled=True,
                memory_cache=True,
                disk_cache=True,
            ),
            network=NetworkConfig(
                enable_http2=True,
                prefetch_dns=True,
                enable_compression=True,
            ),
            rendering=RenderingConfig(
                disable_animations=True,
                disable_transitions=True,
                enable_lazy_loading=True,
            ),
            memory=MemoryConfig(
                aggressive_gc=True,
                limit_dom_size=True,
                discard_idle_tabs=True,
            ),
            optimization=OptimizationConfig(
                auto_optimize=True,
                optimization_level="aggressive",
                parallel_downloads=True,
            ),
        )

    @classmethod
    def balanced_mode(cls) -> PerformanceConfig:
        """Create balanced performance configuration."""
        return cls(
            mode="balanced",
            blocking=ResourceBlockingConfig(
                block_third_party=False,
            ),
            caching=CachingConfig(
                enabled=True,
                cache_images=True,
                cache_scripts=True,
            ),
            rendering=RenderingConfig(
                enable_hardware_acceleration=True,
                enable_lazy_loading=True,
            ),
            optimization=OptimizationConfig(
                auto_optimize=True,
                optimization_level="balanced",
            ),
        )

    @classmethod
    def quality_mode(cls) -> PerformanceConfig:
        """Create configuration for best quality."""
        return cls(
            mode="quality",
            blocking=ResourceBlockingConfig(
                block_images=False,
                block_fonts=False,
                block_media=False,
            ),
            rendering=RenderingConfig(
                wait_for_fonts=True,
                wait_for_animations=True,
                disable_animations=False,
                disable_transitions=False,
            ),
            optimization=OptimizationConfig(
                compress_images=False,
                minify_javascript=False,
                minify_css=False,
            ),
            metrics=MetricsConfig(
                enabled=True,
                measure_lcp=True,
                measure_fid=True,
                measure_cls=True,
            ),
        )

    @classmethod
    def minimal_mode(cls) -> PerformanceConfig:
        """Create minimal resource configuration."""
        return cls(
            mode="minimal",
            blocking=ResourceBlockingConfig(
                block_images=True,
                block_stylesheets=True,
                block_scripts=True,
                block_fonts=True,
                block_media=True,
                block_websockets=True,
                block_third_party=True,
            ),
            caching=CachingConfig(
                enabled=False,
            ),
            rendering=RenderingConfig(
                viewport_width=1024,
                viewport_height=768,
                disable_animations=True,
                enable_hardware_acceleration=False,
            ),
            memory=MemoryConfig(
                max_memory_mb=512,
                aggressive_gc=True,
                max_dom_nodes=5000,
            ),
            preload=PreloadConfig(
                enabled=False,
            ),
            optimization=OptimizationConfig(
                auto_optimize=False,
                parallel_downloads=False,
            ),
        )

    @classmethod
    def monitoring_mode(cls) -> PerformanceConfig:
        """Create configuration for performance monitoring."""
        return cls(
            monitoring_enabled=True,
            metrics=MetricsConfig(
                enabled=True,
                collect_navigation_timing=True,
                collect_resource_timing=True,
                collect_paint_timing=True,
                collect_layout_shift=True,
                measure_lcp=True,
                measure_fid=True,
                measure_cls=True,
                measure_ttfb=True,
                measure_fcp=True,
                store_metrics=True,
            ),
            throttling=ThrottlingConfig(
                throttle_network=True,
                profile="fast-3g",
            ),
        )
