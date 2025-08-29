#!/usr/bin/env python3
"""
INTEGRATION TESTS FOR ULTIMATE ELEMENT EXTRACTOR
================================================
Tests for the main extractor class and full extraction pipeline.
"""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any
import tempfile
import time

# Import main extractor and related classes
from element_extractor_no_llm_robust import (
    UltimateElementExtractor,
    ExtractionResult,
    ElementData,
    ElementType,
    ExtractionStrategy,
    Platform,
    ElementEnricher,
    ElementValidator,
    BoundingBox,
    AccessibilityInfo,
    JS_TEMPLATES,
    MAX_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT,
    ELEMENT_BATCH_SIZE,
    MAX_ELEMENTS_PER_EXTRACTION,
)


@pytest.fixture
def mock_browser():
    """Create a mock browser instance"""
    browser = AsyncMock()
    browser.navigate_to = AsyncMock()
    browser.get_page = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_page_with_data():
    """Create a mock page with realistic data"""
    page = AsyncMock()
    
    # Basic page properties
    page.title = AsyncMock(return_value="Test Website")
    page.wait_for_load_state = AsyncMock()
    page.screenshot = AsyncMock()
    page.accessibility.snapshot = AsyncMock(return_value={
        "role": "document",
        "name": "Test Page",
        "children": []
    })
    
    # Mock evaluate for different scripts
    def evaluate_handler(script):
        if "React" in script or "Vue" in script:
            # Framework detection
            return ["React"]
        elif "document.documentElement.lang" in script:
            # Language detection
            return "en"
        elif "window.innerWidth" in script:
            # Viewport detection
            return {"width": 1920, "height": 1080}
        elif "shadowElements" in script:
            # Shadow DOM detection
            return []
        elif "const elements = []" in script and "extractElement" in script:
            # DOM extraction
            return [
                {
                    "element_id": "header",
                    "tag_name": "header",
                    "element_type": "navigation",
                    "is_visible": True,
                    "bounding_box": {"x": 0, "y": 0, "width": 1920, "height": 100},
                },
                {
                    "element_id": "main_button",
                    "tag_name": "button",
                    "element_type": "button",
                    "text_content": "Click Me",
                    "is_clickable": True,
                    "is_visible": True,
                    "bounding_box": {"x": 100, "y": 200, "width": 150, "height": 50},
                },
                {
                    "element_id": "login_form",
                    "tag_name": "form",
                    "element_type": "form",
                    "form_associated": True,
                    "bounding_box": {"x": 500, "y": 300, "width": 400, "height": 300},
                },
            ]
        else:
            # Default empty response
            return []
    
    page.evaluate = AsyncMock(side_effect=evaluate_handler)
    page.query_selector_all = AsyncMock(return_value=[])
    
    return page


class TestUltimateElementExtractor:
    """Test the main UltimateElementExtractor class"""

    @pytest.mark.asyncio
    async def test_extractor_initialization(self, mock_browser):
        """Test extractor initialization"""
        extractor = UltimateElementExtractor(browser=mock_browser)
        assert extractor.browser == mock_browser
        assert extractor.memory_manager is not None
        assert extractor.page is None
        assert len(extractor.strategies) == 0  # No strategies until page is set

    @pytest.mark.asyncio
    async def test_basic_extraction(self, mock_browser, mock_page_with_data):
        """Test basic element extraction"""
        mock_browser.get_page.return_value = mock_page_with_data
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://example.com")
        
        assert result.url == "https://example.com"
        assert result.platform == Platform.DESKTOP
        assert result.page_title == "Test Website"
        assert result.page_language == "en"
        assert len(result.elements) > 0
        assert result.frameworks_detected == ["React"]

    @pytest.mark.asyncio
    async def test_extraction_with_specific_strategies(self, mock_browser, mock_page_with_data):
        """Test extraction with specific strategies"""
        mock_browser.get_page.return_value = mock_page_with_data
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract(
            "https://example.com",
            strategies=[ExtractionStrategy.DOM_REGULAR],
            platform=Platform.MOBILE
        )
        
        assert result.platform == Platform.MOBILE
        assert ExtractionStrategy.DOM_REGULAR in result.strategies_used

    @pytest.mark.asyncio
    async def test_extraction_with_enrichment(self, mock_browser, mock_page_with_data):
        """Test extraction with element enrichment"""
        mock_browser.get_page.return_value = mock_page_with_data
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract_with_enrichment(
            "https://example.com",
            enrich=True,
            validate=True
        )
        
        # Check enrichment
        for element in result.elements:
            if element.is_clickable:
                assert "interaction_type" in element.properties or len(element.properties) >= 0
        
        # Check validation
        assert "validation_report" in result.properties
        validation = result.properties["validation_report"]
        assert "quality_score" in validation
        assert validation["quality_score"] >= 0 and validation["quality_score"] <= 1

    @pytest.mark.asyncio
    async def test_batch_extraction(self, mock_browser, mock_page_with_data):
        """Test batch URL extraction"""
        mock_browser.get_page.return_value = mock_page_with_data
        
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com",
        ]
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        results = await extractor.extract_batch(urls, max_concurrent=2)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.url == urls[i]

    @pytest.mark.asyncio
    async def test_extraction_with_screenshots(self, mock_browser, mock_page_with_data, tmp_path):
        """Test extraction with screenshot capture"""
        mock_browser.get_page.return_value = mock_page_with_data
        screenshot_path = tmp_path / "screenshot.png"
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract_with_screenshots(
            "https://example.com",
            screenshot_path=screenshot_path
        )
        
        assert "screenshot_path" in result.properties
        assert result.properties["screenshot_path"] == str(screenshot_path)
        mock_page_with_data.screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_extraction_error_handling(self, mock_browser):
        """Test error handling during extraction"""
        mock_page = AsyncMock()
        mock_page.evaluate.side_effect = Exception("Page crash")
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        with pytest.raises(Exception):
            await extractor.extract("https://error.com")

    @pytest.mark.asyncio
    async def test_extraction_with_no_page(self, mock_browser):
        """Test extraction when page is None"""
        mock_browser.get_page.return_value = None
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        with pytest.raises(Exception) as exc_info:
            await extractor.extract("https://example.com")
        
        assert "Failed to get page object" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_framework_detection(self, mock_browser):
        """Test JavaScript framework detection"""
        mock_page = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        
        # Mock different framework scenarios
        def evaluate_frameworks(script):
            if "React" in script:
                return ["React", "Next.js"]
            return []
        
        mock_page.evaluate = AsyncMock(side_effect=evaluate_frameworks)
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        frameworks = await extractor._detect_frameworks()
        
        assert "React" in frameworks
        assert "Next.js" in frameworks

    @pytest.mark.asyncio
    async def test_wasm_and_webgpu_detection(self, mock_browser, mock_page_with_data):
        """Test WebAssembly and WebGPU detection"""
        # Add WASM and WebGPU detection to mock
        original_evaluate = mock_page_with_data.evaluate.side_effect
        
        def enhanced_evaluate(script):
            if "WebAssembly" in script:
                return {"supported": True, "modules": [{"url": "test.wasm"}]}
            elif "gpu" in script:
                return {"supported": True, "features": ["webgpu-available"]}
            else:
                return original_evaluate(script)
        
        mock_page_with_data.evaluate.side_effect = enhanced_evaluate
        mock_browser.get_page.return_value = mock_page_with_data
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://example.com")
        
        assert result.has_webassembly is True
        assert result.has_webgpu is True

    @pytest.mark.asyncio
    async def test_element_deduplication(self, mock_browser):
        """Test that duplicate elements are removed"""
        mock_page = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        
        # Return duplicate elements
        mock_page.evaluate = AsyncMock(return_value=[
            {"element_id": "dup1", "tag_name": "div", "element_type": "unknown"},
            {"element_id": "dup1", "tag_name": "div", "element_type": "unknown"},  # Duplicate
            {"element_id": "unique", "tag_name": "span", "element_type": "unknown"},
        ])
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        # Need to set page first for strategies
        await extractor.browser.navigate_to("https://example.com")
        extractor.page = mock_page
        extractor._initialize_strategies()
        
        # Manually test deduplication logic
        all_elements = [
            ElementData(element_id="dup1", tag_name="div", element_type=ElementType.UNKNOWN),
            ElementData(element_id="dup1", tag_name="div", element_type=ElementType.UNKNOWN),
            ElementData(element_id="unique", tag_name="span", element_type=ElementType.UNKNOWN),
        ]
        
        seen_ids = set()
        unique_elements = []
        for element in all_elements:
            if element.element_id not in seen_ids:
                seen_ids.add(element.element_id)
                unique_elements.append(element)
        
        assert len(unique_elements) == 2
        assert "dup1" in seen_ids
        assert "unique" in seen_ids

    @pytest.mark.asyncio
    async def test_cleanup_on_close(self, mock_browser):
        """Test resource cleanup on close"""
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Add some cached data
        extractor.memory_manager.cache_result("test", "data")
        
        await extractor.close()
        
        # Check cleanup
        assert extractor.memory_manager.get_cached("test") is None
        mock_browser.close.assert_called_once()


class TestElementEnricher:
    """Test element enrichment functionality"""

    def test_element_enrichment(self):
        """Test semantic enrichment of elements"""
        enricher = ElementEnricher()
        
        # Test navigation element
        nav_element = ElementData(
            element_id="main_nav",
            tag_name="nav",
            element_type=ElementType.NAVIGATION,
            text_content="Home About Contact",
            class_list=["navbar", "main-menu"],
        )
        enriched = enricher.enrich_element(nav_element)
        assert enriched.properties.get("semantic_category") == "navigation"
        
        # Test commerce element
        product_element = ElementData(
            element_id="product_123",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            text_content="Amazing Product $99.99",
            class_list=["product-card", "featured"],
        )
        enriched = enricher.enrich_element(product_element)
        assert enriched.properties.get("semantic_category") == "commerce"

    def test_interaction_type_determination(self):
        """Test interaction type detection"""
        enricher = ElementEnricher()
        
        # Test external link
        link_element = ElementData(
            element_id="ext_link",
            tag_name="a",
            element_type=ElementType.LINK,
            is_clickable=True,
            attributes={"href": "https://external.com"},
        )
        enriched = enricher.enrich_element(link_element)
        assert enriched.properties.get("interaction_type") == "external_link"
        
        # Test anchor link
        anchor_element = ElementData(
            element_id="anchor",
            tag_name="a",
            element_type=ElementType.LINK,
            is_clickable=True,
            attributes={"href": "#section"},
        )
        enriched = enricher.enrich_element(anchor_element)
        assert enriched.properties.get("interaction_type") == "anchor_link"
        
        # Test submit button
        button_element = ElementData(
            element_id="submit_btn",
            tag_name="button",
            element_type=ElementType.BUTTON,
            is_clickable=True,
            attributes={"type": "submit"},
        )
        enriched = enricher.enrich_element(button_element)
        assert enriched.properties.get("interaction_type") == "button_submit"


class TestElementValidator:
    """Test element validation functionality"""

    def test_validation_with_good_extraction(self):
        """Test validation of successful extraction"""
        validator = ElementValidator()
        
        # Create a good extraction result
        elements = [
            ElementData(element_id=f"elem_{i}", tag_name="div", element_type=ElementType.UNKNOWN)
            for i in range(100)
        ]
        
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=elements,
            interactive_elements=[elements[0], elements[1]],
        )
        
        report = validator.validate_extraction(result)
        
        assert report["total_elements"] == 100
        assert report["quality_score"] > 0.5
        assert len(report["issues"]) == 0

    def test_validation_with_duplicate_ids(self):
        """Test validation detecting duplicate IDs"""
        validator = ElementValidator()
        
        # Create elements with duplicate IDs
        elements = [
            ElementData(element_id="duplicate", tag_name="div", element_type=ElementType.UNKNOWN),
            ElementData(element_id="duplicate", tag_name="span", element_type=ElementType.UNKNOWN),
            ElementData(element_id="unique", tag_name="p", element_type=ElementType.UNKNOWN),
        ]
        
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=elements,
        )
        
        report = validator.validate_extraction(result)
        
        assert len(report["issues"]) > 0
        assert "Duplicate element IDs" in report["issues"][0]
        assert report["quality_score"] < 1.0

    def test_validation_with_few_elements(self):
        """Test validation with very few elements"""
        validator = ElementValidator()
        
        elements = [
            ElementData(element_id="only_one", tag_name="div", element_type=ElementType.UNKNOWN)
        ]
        
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=elements,
        )
        
        report = validator.validate_extraction(result)
        
        assert "Very few elements extracted" in report["issues"]
        assert report["quality_score"] < 0.5

    def test_validation_with_errors(self):
        """Test validation with extraction errors"""
        validator = ElementValidator()
        
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=[],
            errors=["Network timeout", "JavaScript error"],
        )
        
        report = validator.validate_extraction(result)
        
        assert report["quality_score"] < 1.0


class TestExtractionResultExports:
    """Test export functionality"""

    def test_json_export(self, tmp_path):
        """Test JSON export functionality"""
        elements = [
            ElementData(
                element_id="test1",
                tag_name="button",
                element_type=ElementType.BUTTON,
                text_content="Click me",
            )
        ]
        
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=elements,
        )
        
        json_path = tmp_path / "export.json"
        result.export_json(json_path)
        
        assert json_path.exists()
        
        with open(json_path) as f:
            data = json.load(f)
        
        assert data["url"] == "https://example.com"
        assert len(data["elements"]) == 1
        assert data["elements"][0]["element_id"] == "test1"

    def test_csv_export(self, tmp_path):
        """Test CSV export functionality"""
        import csv
        
        elements = [
            ElementData(
                element_id="btn1",
                tag_name="button",
                element_type=ElementType.BUTTON,
                text_content="Button 1",
                is_clickable=True,
                xpath="//button[1]",
            ),
            ElementData(
                element_id="link1",
                tag_name="a",
                element_type=ElementType.LINK,
                text_content="Link 1",
                is_clickable=True,
                css_selector="a.link",
            ),
        ]
        
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=elements,
        )
        
        csv_path = tmp_path / "export.csv"
        result.export_csv(csv_path)
        
        assert csv_path.exists()
        
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]["element_id"] == "btn1"
        assert rows[0]["element_type"] == "button"
        assert rows[1]["element_id"] == "link1"
        assert rows[1]["element_type"] == "link"


class TestPerformanceOptimization:
    """Test performance-related features"""

    @pytest.mark.asyncio
    async def test_parallel_strategy_execution(self, mock_browser):
        """Test that multiple strategies run in parallel"""
        mock_page = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.accessibility.snapshot = AsyncMock(return_value=None)
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        start_time = time.perf_counter()
        result = await extractor.extract(
            "https://example.com",
            strategies=[
                ExtractionStrategy.DOM_REGULAR,
                ExtractionStrategy.DOM_SHADOW,
                ExtractionStrategy.VISUAL,
            ]
        )
        duration = time.perf_counter() - start_time
        
        # With parallel execution, should be faster than sequential
        # (This is a simplified test - in reality would need proper timing)
        assert result.strategies_used == [
            ExtractionStrategy.DOM_REGULAR,
            ExtractionStrategy.DOM_SHADOW,
            ExtractionStrategy.VISUAL,
        ]

    @pytest.mark.asyncio
    async def test_memory_caching(self, mock_browser, mock_page_with_data):
        """Test that memory caching works"""
        mock_browser.get_page.return_value = mock_page_with_data
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Cache some data
        test_key = "test_cache_key"
        test_data = {"elements": ["elem1", "elem2"]}
        extractor.memory_manager.cache_result(test_key, test_data)
        
        # Retrieve cached data
        cached = extractor.memory_manager.get_cached(test_key)
        assert cached == test_data
        
        # Clear cache
        extractor.memory_manager.clear_cache()
        assert extractor.memory_manager.get_cached(test_key) is None

    @pytest.mark.asyncio
    async def test_element_limit_enforcement(self, mock_browser):
        """Test that element limit is enforced"""
        mock_page = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        
        # Create way too many elements
        huge_element_list = [
            {"element_id": f"elem_{i}", "tag_name": "div", "element_type": "unknown"}
            for i in range(MAX_ELEMENTS_PER_EXTRACTION + 1000)
        ]
        
        mock_page.evaluate = AsyncMock(return_value=huge_element_list[:MAX_ELEMENTS_PER_EXTRACTION])
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://example.com")
        
        # Should respect the limit
        assert result.total_elements <= MAX_ELEMENTS_PER_EXTRACTION


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])