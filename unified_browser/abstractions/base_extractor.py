"""
Base extractor abstraction module.

This module defines the abstract base class for content extraction strategies,
handling different approaches to extracting and processing web content.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Union

from ..config import ExtractionConfig
from ..core import (
    ContentType,
    ExtractionMethod,
    ExtractionResult,
    ElementData,
    Selector,
    SelectorList,
    ExtractionCallback,
    BoundingBox,
)


class BaseExtractor(ABC):
    """
    Abstract base class for content extraction strategies.
    
    This class defines the contract for different extraction approaches,
    allowing for flexible content extraction based on page types and requirements.
    """
    
    def __init__(self, config: ExtractionConfig) -> None:
        """Initialize the extractor with configuration."""
        self.config = config
        self._callbacks: List[ExtractionCallback] = []
        self._cache: Dict[str, Any] = {}
        self._metrics: Dict[str, Any] = {}
    
    # ============================================================================
    # CALLBACK MANAGEMENT
    # ============================================================================
    
    def add_callback(self, callback: ExtractionCallback) -> None:
        """Add an extraction callback."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: ExtractionCallback) -> None:
        """Remove an extraction callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def _trigger_callbacks(self, event: str, data: Dict[str, Any]) -> None:
        """Trigger extraction callbacks."""
        for callback in self._callbacks:
            try:
                await callback(event, data)
            except Exception as e:
                self._log_error(f"Callback error: {e}")
    
    # ============================================================================
    # CORE EXTRACTION METHODS
    # ============================================================================
    
    @abstractmethod
    async def extract_content(
        self, 
        content_types: List[ContentType],
        selectors: Optional[SelectorList] = None,
        **kwargs
    ) -> ExtractionResult:
        """Extract content based on specified types and selectors."""
        pass
    
    @abstractmethod
    async def extract_elements(self, selectors: SelectorList, **kwargs) -> List[ElementData]:
        """Extract elements using selectors."""
        pass
    
    @abstractmethod
    async def extract_text(self, selector: Optional[Selector] = None, **kwargs) -> List[str]:
        """Extract text content from the page or specific elements."""
        pass
    
    @abstractmethod
    async def extract_links(self, **kwargs) -> List[Dict[str, str]]:
        """Extract all links from the page."""
        pass
    
    @abstractmethod
    async def extract_images(self, **kwargs) -> List[Dict[str, str]]:
        """Extract image information from the page."""
        pass
    
    @abstractmethod
    async def extract_tables(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract table data from the page."""
        pass
    
    @abstractmethod
    async def extract_forms(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract form information from the page."""
        pass
    
    @abstractmethod
    async def extract_metadata(self, **kwargs) -> Dict[str, Any]:
        """Extract page metadata (title, description, etc.)."""
        pass
    
    # ============================================================================
    # ADVANCED EXTRACTION METHODS
    # ============================================================================
    
    @abstractmethod
    async def extract_with_context(self, selector: Selector, context_size: int = 3) -> Dict[str, Any]:
        """Extract element with surrounding context."""
        pass
    
    @abstractmethod
    async def extract_structured_data(self, schema_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD, microdata, etc.)."""
        pass
    
    @abstractmethod
    async def extract_shadow_dom(self, **kwargs) -> List[ElementData]:
        """Extract content from shadow DOM."""
        pass
    
    @abstractmethod
    async def extract_iframe_content(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract content from iframes."""
        pass
    
    # ============================================================================
    # BATCH EXTRACTION METHODS
    # ============================================================================
    
    @abstractmethod
    async def extract_batch(self, extraction_specs: List[Dict[str, Any]]) -> List[ExtractionResult]:
        """Perform batch extraction with multiple specifications."""
        pass
    
    @abstractmethod
    async def extract_parallel(
        self, 
        selectors: SelectorList,
        max_workers: Optional[int] = None
    ) -> List[ElementData]:
        """Extract elements in parallel."""
        pass
    
    # ============================================================================
    # FILTERING AND PROCESSING
    # ============================================================================
    
    @abstractmethod
    async def filter_elements(
        self,
        elements: List[ElementData],
        criteria: Dict[str, Any]
    ) -> List[ElementData]:
        """Filter elements based on criteria."""
        pass
    
    @abstractmethod
    async def process_text(self, text: str, **kwargs) -> str:
        """Process and clean text content."""
        pass
    
    @abstractmethod
    async def deduplicate_results(self, results: List[Any]) -> List[Any]:
        """Remove duplicate results."""
        pass
    
    @abstractmethod
    async def rank_results(self, results: List[Any], criteria: str) -> List[Any]:
        """Rank results by relevance or other criteria."""
        pass
    
    # ============================================================================
    # VALIDATION AND QUALITY CONTROL
    # ============================================================================
    
    @abstractmethod
    async def validate_extraction(self, result: ExtractionResult) -> Dict[str, Any]:
        """Validate extraction results quality."""
        pass
    
    @abstractmethod
    async def estimate_extraction_confidence(self, result: ExtractionResult) -> float:
        """Estimate confidence score for extraction results."""
        pass
    
    @abstractmethod
    async def detect_extraction_errors(self, result: ExtractionResult) -> List[str]:
        """Detect potential errors in extraction results."""
        pass
    
    # ============================================================================
    # ADAPTIVE EXTRACTION
    # ============================================================================
    
    @abstractmethod
    async def analyze_page_structure(self) -> Dict[str, Any]:
        """Analyze page structure to optimize extraction."""
        pass
    
    @abstractmethod
    async def select_optimal_method(
        self, 
        content_types: List[ContentType]
    ) -> ExtractionMethod:
        """Select optimal extraction method for content types."""
        pass
    
    @abstractmethod
    async def learn_from_extraction(
        self, 
        content_types: List[ContentType],
        result: ExtractionResult
    ) -> None:
        """Learn from extraction results to improve future extractions."""
        pass
    
    # ============================================================================
    # CACHING AND PERFORMANCE
    # ============================================================================
    
    def _get_cache_key(self, selector: Selector, **kwargs) -> str:
        """Generate cache key for extraction results."""
        key_parts = [str(selector)]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return "|".join(key_parts)
    
    def _cache_result(self, key: str, result: Any) -> None:
        """Cache extraction result."""
        if self.config.performance.cache_extractions:
            self._cache[key] = result
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached extraction result."""
        return self._cache.get(key) if self.config.performance.cache_extractions else None
    
    def clear_cache(self) -> None:
        """Clear extraction cache."""
        self._cache.clear()
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _log_metric(self, name: str, value: Any) -> None:
        """Log an extraction metric."""
        self._metrics[name] = value
    
    def _log_error(self, message: str) -> None:
        """Log an error message."""
        # Implementation would use proper logging
        print(f"Extractor Error: {message}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics."""
        return self._metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the extractor."""
        pass


class PlaywrightExtractor(BaseExtractor):
    """Extractor implementation using Playwright."""
    
    async def extract_content(
        self, 
        content_types: List[ContentType],
        selectors: Optional[SelectorList] = None,
        **kwargs
    ) -> ExtractionResult:
        """Extract content using Playwright."""
        # Implementation would be in concrete classes
        pass


class BeautifulSoupExtractor(BaseExtractor):
    """Extractor implementation using BeautifulSoup."""
    
    async def extract_content(
        self, 
        content_types: List[ContentType],
        selectors: Optional[SelectorList] = None,
        **kwargs
    ) -> ExtractionResult:
        """Extract content using BeautifulSoup."""
        # Implementation would be in concrete classes
        pass


class LLMVisionExtractor(BaseExtractor):
    """Extractor implementation using LLM vision models."""
    
    def __init__(self, config: ExtractionConfig) -> None:
        super().__init__(config)
        self._vision_model = None  # Would be initialized with actual model
    
    async def extract_content(
        self, 
        content_types: List[ContentType],
        selectors: Optional[SelectorList] = None,
        **kwargs
    ) -> ExtractionResult:
        """Extract content using LLM vision analysis."""
        # Implementation would use vision models to understand page content
        pass
    
    async def extract_with_ai_understanding(self, query: str, **kwargs) -> Dict[str, Any]:
        """Extract content based on natural language query."""
        # Implementation would interpret query and extract relevant content
        pass


class HybridExtractor(BaseExtractor):
    """Hybrid extractor that combines multiple extraction methods."""
    
    def __init__(self, config: ExtractionConfig) -> None:
        super().__init__(config)
        self._extractors = {
            ExtractionMethod.PLAYWRIGHT: PlaywrightExtractor(config),
            ExtractionMethod.BEAUTIFUL_SOUP: BeautifulSoupExtractor(config),
            ExtractionMethod.LLM_VISION: LLMVisionExtractor(config),
        }
        self._primary_extractor: Optional[BaseExtractor] = None
    
    async def extract_content(
        self, 
        content_types: List[ContentType],
        selectors: Optional[SelectorList] = None,
        **kwargs
    ) -> ExtractionResult:
        """Extract content using hybrid approach."""
        method = await self.select_optimal_method(content_types)
        self._primary_extractor = self._extractors[method]
        
        await self._trigger_callbacks('method_selected', {
            'method': method.value,
            'content_types': [ct.value for ct in content_types]
        })
        
        return await self._primary_extractor.extract_content(content_types, selectors, **kwargs)
    
    async def select_optimal_method(self, content_types: List[ContentType]) -> ExtractionMethod:
        """Select optimal extraction method based on content types."""
        # Simple heuristics - could be enhanced with ML
        if ContentType.TABLE in content_types:
            return ExtractionMethod.PLAYWRIGHT  # Better for complex tables
        elif any(ct in [ContentType.FORM, ContentType.INTERACTIVE] for ct in content_types):
            return ExtractionMethod.PLAYWRIGHT  # Better for interactive elements
        elif ContentType.IMAGE in content_types:
            return ExtractionMethod.LLM_VISION  # Better for image understanding
        else:
            return ExtractionMethod.BEAUTIFUL_SOUP  # Faster for simple text