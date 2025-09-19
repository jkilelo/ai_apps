"""
Elements Extractor Module - No LLM Required
Handles DOM element extraction and analysis without LLM dependencies
"""
import asyncio
import json
import logging
import os
import sys
import time
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import ALL data types from data_types.py for DRY compliance
try:
    # Try relative import first (when used as a module)
    from .data_types import (
        # Core enums
        ElementType,
        # Data models
        Element,
        CrawlResult,
        # Configs and results
        ExtractionConfig,
        ExtractionResult,
        # Utilities
        ElementSelectorUtils,
        ThreadSafeCache,
        memory_cleanup,
        # Constants
        CONFIDENCE_BASE,
        CONFIDENCE_INCREMENT,
        SELECTOR_SCORE_ID,
        SELECTOR_SCORE_DATA_TESTID,
        SELECTOR_SCORE_ARIA_LABEL,
        SELECTOR_SCORE_CLASS,
        ELEMENT_INTERACTIONS
    )
    from .browser import UltimateStealthBrowser
except ImportError:
    # Fall back to absolute import (when run directly)
    from data_types import (
        # Core enums
        ElementType,
        # Data models
        Element,
        CrawlResult,
        # Configs and results
        ExtractionConfig,
        ExtractionResult,
        # Utilities
        ElementSelectorUtils,
        ThreadSafeCache,
        memory_cleanup,
        # Constants
        CONFIDENCE_BASE,
        CONFIDENCE_INCREMENT,
        SELECTOR_SCORE_ID,
        SELECTOR_SCORE_DATA_TESTID,
        SELECTOR_SCORE_ARIA_LABEL,
        SELECTOR_SCORE_CLASS,
        ELEMENT_INTERACTIONS
    )
    from browser import UltimateStealthBrowser


class ElementsExtractorNoLLM:
    """Non-LLM based element extractor using heuristics"""

    def __init__(self, config: Optional[ExtractionConfig] = None):
        """Initialize the extractor"""
        self.config = config or ExtractionConfig()
        self.browser: Optional[UltimateStealthBrowser] = None
        self.cache = ThreadSafeCache(max_size=100)

    async def initialize_browser(self) -> None:
        """Initialize the browser instance"""
        if not self.browser:
            self.browser = UltimateStealthBrowser(self.config)
            await self.browser.initialize()

    async def cleanup(self) -> None:
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.cleanup()
            self.browser = None
        memory_cleanup()

    def _calculate_confidence(self, element: Element) -> float:
        """Calculate confidence score for an element"""
        score = CONFIDENCE_BASE

        # Boost for good selectors
        if element.selector:
            selector = element.selector
            if selector.id:
                score += SELECTOR_SCORE_ID
            if selector.data_testid:
                score += SELECTOR_SCORE_DATA_TESTID
            if selector.aria_label:
                score += SELECTOR_SCORE_ARIA_LABEL
            if selector.class_names:
                score += SELECTOR_SCORE_CLASS

        # Boost for interactive elements
        if element.is_clickable:
            score += CONFIDENCE_INCREMENT
        if element.element_type in [
            ElementType.BUTTON,
            ElementType.LINK,
            ElementType.TEXT_INPUT
        ]:
            score += CONFIDENCE_INCREMENT

        # Boost for visible elements
        if element.is_visible:
            score += CONFIDENCE_INCREMENT

        # Boost for elements with text
        if element.text and len(element.text.strip()) > 0:
            score += CONFIDENCE_INCREMENT

        return min(score, 1.0)

    def _filter_elements(self, elements: List[Element]) -> List[Element]:
        """Filter elements based on configuration"""
        filtered = elements

        # Filter invisible elements
        if self.config.filter_invisible:
            filtered = [e for e in filtered if e.is_visible]

        # Filter duplicates
        if self.config.filter_duplicates:
            seen_hashes = set()
            unique = []
            for elem in filtered:
                elem_hash = self._get_element_hash(elem)
                if elem_hash not in seen_hashes:
                    seen_hashes.add(elem_hash)
                    unique.append(elem)
            filtered = unique

        # Apply confidence threshold
        if self.config.min_confidence > 0:
            filtered = [
                e for e in filtered
                if self._calculate_confidence(e) >= self.config.min_confidence
            ]

        return filtered

    def _get_element_hash(self, element: Element) -> str:
        """Generate hash for element deduplication"""
        key_parts = [
            element.tag_name or "",
            element.text or "",
            str(element.element_type.value if element.element_type else ""),
            element.selector.css if element.selector else ""
        ]
        return "|".join(key_parts)

    def _enrich_element(self, element: Element) -> Element:
        """Enrich element with additional data"""
        # Calculate confidence
        element.confidence = self._calculate_confidence(element)

        # Set interaction types using shared utility
        element.interaction_types = list(
            ELEMENT_INTERACTIONS.get(element.element_type, [])
        )

        # Ensure element has proper type
        if not element.element_type:
            element.element_type = ElementSelectorUtils.determine_element_type(
                element.tag_name
            )

        return element

    async def extract_from_url(
        self,
        url: str
    ) -> ExtractionResult:
        """
        Extract elements from a URL

        Args:
            url: The URL to extract from

        Returns:
            ExtractionResult (always, even on error)
        """
        start_time = time.time()

        try:
            # Initialize browser if needed
            await self.initialize_browser()

            if not self.browser:
                return ExtractionResult(
                    url=url,
                    success=False,
                    elements=[],
                    errors=["Failed to initialize browser"],
                    extraction_time=time.time() - start_time
                )

            # Navigate to URL
            nav_success = await self.browser.navigate(url)
            if not nav_success:
                return ExtractionResult(
                    url=url,
                    success=False,
                    elements=[],
                    errors=["Navigation failed"],
                    extraction_time=time.time() - start_time
                )

            # Get DOM elements from current page using extract_elements
            # The browser.extract_elements() already returns an ExtractionResult
            extraction_result = await self.browser.extract_elements(url)

            # Process elements from the extraction result
            if extraction_result.success and extraction_result.elements:
                # The elements are already Element objects, so enrich them
                enriched = [self._enrich_element(e) for e in extraction_result.elements]

                # Filter elements
                filtered = self._filter_elements(enriched)
            else:
                filtered = []

            # Create result
            return ExtractionResult(
                url=url,
                success=True,
                elements=filtered,
                extraction_time=time.time() - start_time,
                metadata={
                    "filtered_count": len(filtered),
                    "original_count": len(extraction_result.elements) if extraction_result and extraction_result.elements else 0
                }
            )

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return ExtractionResult(
                url=url,
                success=False,
                elements=[],
                errors=[str(e)],
                extraction_time=time.time() - start_time
            )

    async def crawl_page(
        self,
        url: str,
        depth: int = 0,
        max_depth: int = 2,
        visited: Optional[Set[str]] = None
    ) -> CrawlResult:
        """
        Crawl a single page and optionally its links

        Args:
            url: URL to crawl
            depth: Current crawl depth
            max_depth: Maximum crawl depth
            visited: Set of visited URLs

        Returns:
            CrawlResult containing crawl data
        """
        if visited is None:
            visited = set()

        # Skip if already visited
        normalized_url = urlparse(url).geturl()
        if normalized_url in visited:
            return CrawlResult(
                start_url=url,
                crawled_urls=[],
                total_elements=0,
                crawl_time=0,
                errors=["URL already visited"]
            )

        visited.add(normalized_url)
        start_time = time.time()
        crawled_urls = [normalized_url]
        total_elements = 0
        errors = []

        try:
            # Extract elements from current page
            result = await self.extract_from_url(url)

            if result.success and result.elements:
                total_elements += len(result.elements)

                # Find links if we haven't reached max depth
                if depth < max_depth:
                    links = [
                        e for e in result.elements
                        if e.element_type == ElementType.LINK and e.href
                    ]

                    # Crawl child pages
                    for link in links[:10]:  # Limit to 10 links per page
                        if link.href:
                            absolute_url = urljoin(url, link.href)
                            # Only crawl same domain
                            same_domain = (
                                urlparse(absolute_url).netloc ==
                                urlparse(url).netloc
                            )
                            if same_domain:
                                child_result = await self.crawl_page(
                                    absolute_url,
                                    depth + 1,
                                    max_depth,
                                    visited
                                )
                                crawled_urls.extend(child_result.crawled_urls)
                                total_elements += child_result.total_elements
                                errors.extend(child_result.errors)
            else:
                errors.extend(result.errors)

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            errors.append(str(e))

        return CrawlResult(
            start_url=url,
            crawled_urls=crawled_urls,
            total_elements=total_elements,
            crawl_time=time.time() - start_time,
            errors=errors if errors else None
        )


# Standalone functions for backwards compatibility
async def extract_elements(
    url: str,
    config: Optional[ExtractionConfig] = None
) -> ExtractionResult:
    """
    Standalone function to extract elements from a URL

    Args:
        url: URL to extract from
        config: Extraction configuration

    Returns:
        ExtractionResult (always, even on error)
    """
    extractor = ElementsExtractorNoLLM(config)
    try:
        result = await extractor.extract_from_url(url)
        return result
    finally:
        await extractor.cleanup()


async def crawl_website(
    start_url: str,
    max_pages: int = 10,
    max_depth: int = 2,
    config: Optional[ExtractionConfig] = None
) -> CrawlResult:
    """
    Crawl a website starting from the given URL

    Args:
        start_url: Starting URL
        max_pages: Maximum pages to crawl
        max_depth: Maximum crawl depth
        config: Extraction configuration

    Returns:
        CrawlResult containing crawl data
    """
    extractor = ElementsExtractorNoLLM(config)
    try:
        result = await extractor.crawl_page(
            start_url,
            max_depth=max_depth
        )
        return result
    finally:
        await extractor.cleanup()


def extract_elements_sync(
    url: str,
    config: Optional[ExtractionConfig] = None
) -> ExtractionResult:
    """
    Synchronous wrapper for extract_elements

    Args:
        url: URL to extract from
        config: Extraction configuration

    Returns:
        ExtractionResult (always, even on error)
    """
    return asyncio.run(extract_elements(url, config))


# Main entry points
async def extract_from_url(
    url: str,
    config: Optional[ExtractionConfig] = None,
) -> ExtractionResult:
    """
    Main async entry point for element extraction

    Args:
        url: URL to extract elements from
        config: Extraction configuration

    Returns:
        ExtractionResult (always returns this type)
    """
    return await extract_elements(url, config)


def extract_from_url_sync(
    url: str,
    config: Optional[ExtractionConfig] = None
) -> ExtractionResult:
    """
    Main sync entry point for element extraction

    Args:
        url: URL to extract elements from
        config: Extraction configuration

    Returns:
        ExtractionResult (always returns this type)
    """
    return asyncio.run(extract_from_url(url, config))

async def main(url: str):
    parent=os.path.dirname(os.path.abspath(__file__))
    filename=os.path.join(parent, "test_elements_extractor_no_llm.json")
    result = await extract_from_url(url)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(result.elements)} elements from {url}")
    print(f"[OK] Results written to: {filename}")

if __name__ == "__main__":
    url="https://uat01.citi.com"
    asyncio.run(main(url))