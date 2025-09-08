"""
Element extraction configuration module.

This module defines settings for extracting and analyzing web page elements,
including text, tables, forms, and shadow DOM content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..core import (
    ContentType,
    DEFAULT_TIMEOUT,
    EXTRACTION_BATCH_SIZE,
    ExtractionMethod,
    MAX_EXTRACTION_DEPTH,
    MAX_EXTRACTION_WORKERS,
    MAX_RETRIES,
    SHADOW_DOM_DEPTH,
    USE_ASYNC_EXTRACTION,
    USE_BATCH_EXTRACTION,
    USE_PARALLEL_EXTRACTION,
)


@dataclass
class TextExtractionConfig:
    """Configuration for text extraction."""

    # Text extraction settings
    extract_text: bool = True
    include_hidden_text: bool = False
    preserve_whitespace: bool = False
    normalize_unicode: bool = True

    # Content filtering
    min_text_length: int = 3
    max_text_length: Optional[int] = None
    filter_empty: bool = True
    remove_duplicates: bool = True

    # Text processing
    strip_html_tags: bool = True
    decode_entities: bool = True
    fix_encoding: bool = True
    language_detection: bool = False

    # Advanced extraction
    extract_attributes: List[str] = field(
        default_factory=lambda: ["title", "alt", "placeholder", "aria-label"]
    )
    combine_text_nodes: bool = True
    extract_pseudo_content: bool = False


@dataclass
class TableExtractionConfig:
    """Configuration for table extraction."""

    # Table detection
    auto_detect_tables: bool = True
    include_layout_tables: bool = False
    min_rows: int = 2
    min_columns: int = 2

    # Header detection
    detect_headers: bool = True
    first_row_as_header: bool = True
    first_column_as_header: bool = False

    # Cell processing
    merge_cells: bool = True
    clean_cell_text: bool = True
    preserve_cell_formatting: bool = False

    # Output format
    output_format: str = "dict"  # dict, list, dataframe, csv, json
    include_metadata: bool = True
    flatten_nested_tables: bool = True


@dataclass
class FormExtractionConfig:
    """Configuration for form extraction."""

    # Form detection
    extract_forms: bool = True
    include_hidden_fields: bool = False
    include_disabled_fields: bool = False

    # Field extraction
    extract_field_types: List[str] = field(
        default_factory=lambda: [
            "text",
            "password",
            "email",
            "number",
            "tel",
            "url",
            "search",
            "date",
            "time",
            "checkbox",
            "radio",
            "select",
            "textarea",
            "file",
            "submit",
            "button",
            "hidden",
        ]
    )

    # Field metadata
    extract_labels: bool = True
    extract_placeholders: bool = True
    extract_validations: bool = True
    extract_default_values: bool = True

    # Form analysis
    detect_form_purpose: bool = True
    identify_required_fields: bool = True
    map_field_relationships: bool = True


@dataclass
class LinkExtractionConfig:
    """Configuration for link extraction."""

    # Link extraction
    extract_links: bool = True
    include_internal_links: bool = True
    include_external_links: bool = True
    include_anchor_links: bool = True

    # Link filtering
    follow_redirects: bool = False
    validate_links: bool = False
    check_link_status: bool = False

    # Link metadata
    extract_link_text: bool = True
    extract_link_context: bool = True
    categorize_links: bool = True

    # URL processing
    normalize_urls: bool = True
    resolve_relative_urls: bool = True
    remove_tracking_params: bool = True
    decode_url_entities: bool = True


@dataclass
class MediaExtractionConfig:
    """Configuration for media extraction."""

    # Image extraction
    extract_images: bool = True
    include_background_images: bool = True
    include_svg_images: bool = True
    min_image_width: int = 50
    min_image_height: int = 50

    # Video extraction
    extract_videos: bool = True
    include_video_metadata: bool = True
    extract_video_sources: bool = True

    # Audio extraction
    extract_audio: bool = True
    include_audio_metadata: bool = True

    # Media metadata
    extract_alt_text: bool = True
    extract_captions: bool = True
    calculate_dimensions: bool = True
    check_media_availability: bool = False

    # Download options
    download_media: bool = False
    media_download_timeout: int = 30000
    max_media_size_mb: int = 100


@dataclass
class MetadataExtractionConfig:
    """Configuration for metadata extraction."""

    # Page metadata
    extract_title: bool = True
    extract_description: bool = True
    extract_keywords: bool = True
    extract_author: bool = True

    # Open Graph
    extract_og_tags: bool = True

    # Twitter Cards
    extract_twitter_tags: bool = True

    # Schema.org
    extract_json_ld: bool = True
    extract_microdata: bool = True
    extract_rdfa: bool = True

    # Custom metadata
    custom_meta_tags: List[str] = field(default_factory=list)

    # Headers
    extract_headers: bool = True
    header_levels: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5, 6])


@dataclass
class ShadowDOMConfig:
    """Configuration for shadow DOM extraction."""

    # Shadow DOM handling
    pierce_shadow_dom: bool = True
    max_shadow_depth: int = SHADOW_DOM_DEPTH

    # Shadow root detection
    auto_detect_shadow_roots: bool = True
    shadow_root_selectors: List[str] = field(default_factory=list)

    # Extraction behavior
    extract_closed_shadow_roots: bool = False
    merge_shadow_content: bool = True
    preserve_shadow_boundaries: bool = False

    # Performance
    lazy_load_shadow_content: bool = True
    cache_shadow_roots: bool = True


@dataclass
class XPathConfig:
    """Configuration for XPath extraction."""

    # XPath support
    enable_xpath: bool = True
    xpath_version: str = "1.0"  # 1.0, 2.0

    # Namespace handling
    register_namespaces: Dict[str, str] = field(default_factory=dict)
    use_default_namespace: bool = True

    # XPath optimization
    compile_xpath_expressions: bool = True
    cache_xpath_results: bool = True

    # Error handling
    strict_xpath_evaluation: bool = False
    fallback_to_css: bool = True


@dataclass
class BatchExtractionConfig:
    """Configuration for batch extraction."""

    # Batch settings
    enabled: bool = USE_BATCH_EXTRACTION
    batch_size: int = EXTRACTION_BATCH_SIZE

    # Parallel processing
    use_parallel: bool = USE_PARALLEL_EXTRACTION
    max_workers: int = MAX_EXTRACTION_WORKERS

    # Async extraction
    use_async: bool = USE_ASYNC_EXTRACTION
    async_timeout: int = DEFAULT_TIMEOUT

    # Optimization
    deduplicate_selectors: bool = True
    group_by_type: bool = True
    prioritize_visible: bool = True


@dataclass
class ExtractionPerformanceConfig:
    """Configuration for extraction performance."""

    # Caching
    cache_extractions: bool = True
    cache_ttl_seconds: int = 300
    max_cache_size_mb: int = 100

    # Throttling
    throttle_extraction: bool = False
    extraction_delay_ms: int = 0
    max_extractions_per_second: int = 100

    # Resource limits
    max_extraction_time_ms: int = 30000
    max_memory_usage_mb: int = 512

    # Optimization
    lazy_evaluation: bool = True
    stream_large_extractions: bool = True
    compress_results: bool = False


@dataclass
class ExtractionConfig:
    """Main extraction configuration."""

    # Extraction method
    method: ExtractionMethod = ExtractionMethod.PLAYWRIGHT
    content_types: List[ContentType] = field(
        default_factory=lambda: [ContentType.TEXT, ContentType.TABLE, ContentType.FORM]
    )

    # Global settings
    max_depth: int = MAX_EXTRACTION_DEPTH
    max_retries: int = MAX_RETRIES
    timeout: int = DEFAULT_TIMEOUT

    # Sub-configurations
    text: TextExtractionConfig = field(default_factory=TextExtractionConfig)
    table: TableExtractionConfig = field(default_factory=TableExtractionConfig)
    form: FormExtractionConfig = field(default_factory=FormExtractionConfig)
    link: LinkExtractionConfig = field(default_factory=LinkExtractionConfig)
    media: MediaExtractionConfig = field(default_factory=MediaExtractionConfig)
    metadata: MetadataExtractionConfig = field(default_factory=MetadataExtractionConfig)
    shadow_dom: ShadowDOMConfig = field(default_factory=ShadowDOMConfig)
    xpath: XPathConfig = field(default_factory=XPathConfig)
    batch: BatchExtractionConfig = field(default_factory=BatchExtractionConfig)
    performance: ExtractionPerformanceConfig = field(default_factory=ExtractionPerformanceConfig)

    # Output settings
    output_format: str = "json"  # json, html, markdown, plain
    pretty_print: bool = True
    include_screenshot: bool = False
    include_source_html: bool = False

    @classmethod
    def minimal_extraction(cls) -> ExtractionConfig:
        """Create minimal extraction configuration."""
        return cls(
            content_types=[ContentType.TEXT],
            text=TextExtractionConfig(
                extract_text=True,
                include_hidden_text=False,
                extract_attributes=[],
            ),
            table=TableExtractionConfig(auto_detect_tables=False),
            form=FormExtractionConfig(extract_forms=False),
            link=LinkExtractionConfig(extract_links=False),
            media=MediaExtractionConfig(
                extract_images=False,
                extract_videos=False,
                extract_audio=False,
            ),
            metadata=MetadataExtractionConfig(
                extract_title=True,
                extract_og_tags=False,
                extract_json_ld=False,
            ),
            shadow_dom=ShadowDOMConfig(pierce_shadow_dom=False),
            batch=BatchExtractionConfig(enabled=False),
        )

    @classmethod
    def full_extraction(cls) -> ExtractionConfig:
        """Create full extraction configuration."""
        return cls(
            content_types=[
                ContentType.TEXT,
                ContentType.TABLE,
                ContentType.FORM,
                ContentType.LINK,
                ContentType.IMAGE,
                ContentType.VIDEO,
                ContentType.METADATA,
            ],
            text=TextExtractionConfig(
                extract_text=True,
                include_hidden_text=True,
                extract_pseudo_content=True,
            ),
            table=TableExtractionConfig(
                auto_detect_tables=True,
                detect_headers=True,
                include_metadata=True,
            ),
            form=FormExtractionConfig(
                extract_forms=True,
                include_hidden_fields=True,
                detect_form_purpose=True,
            ),
            link=LinkExtractionConfig(
                extract_links=True,
                extract_link_context=True,
                categorize_links=True,
            ),
            media=MediaExtractionConfig(
                extract_images=True,
                extract_videos=True,
                extract_audio=True,
                include_background_images=True,
            ),
            metadata=MetadataExtractionConfig(
                extract_og_tags=True,
                extract_twitter_tags=True,
                extract_json_ld=True,
                extract_microdata=True,
            ),
            shadow_dom=ShadowDOMConfig(
                pierce_shadow_dom=True,
                auto_detect_shadow_roots=True,
            ),
            batch=BatchExtractionConfig(
                enabled=True,
                use_parallel=True,
                use_async=True,
            ),
        )

    @classmethod
    def fast_extraction(cls) -> ExtractionConfig:
        """Create fast extraction configuration."""
        return cls(
            method=ExtractionMethod.PLAYWRIGHT,
            max_retries=1,
            timeout=5000,
            text=TextExtractionConfig(
                extract_text=True,
                extract_attributes=[],
            ),
            shadow_dom=ShadowDOMConfig(
                pierce_shadow_dom=False,
            ),
            batch=BatchExtractionConfig(
                enabled=True,
                use_parallel=True,
                batch_size=100,
            ),
            performance=ExtractionPerformanceConfig(
                cache_extractions=True,
                lazy_evaluation=True,
                stream_large_extractions=True,
            ),
        )

    @classmethod
    def ai_extraction(cls) -> ExtractionConfig:
        """Create AI-powered extraction configuration."""
        return cls(
            method=ExtractionMethod.LLM_VISION,
            content_types=[
                ContentType.TEXT,
                ContentType.TABLE,
                ContentType.FORM,
                ContentType.METADATA,
            ],
            text=TextExtractionConfig(
                language_detection=True,
                extract_pseudo_content=True,
            ),
            table=TableExtractionConfig(
                auto_detect_tables=True,
                detect_headers=True,
                output_format="dataframe",
            ),
            form=FormExtractionConfig(
                detect_form_purpose=True,
                identify_required_fields=True,
                map_field_relationships=True,
            ),
            metadata=MetadataExtractionConfig(
                extract_json_ld=True,
                extract_microdata=True,
                extract_rdfa=True,
            ),
            include_screenshot=True,
        )
