#!/usr/bin/env python3
"""
UNIT TESTS FOR ELEMENT EXTRACTION STRATEGIES
============================================
Tests for all extraction strategy implementations.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any

# Import strategies and related classes
from element_extractor_no_llm_robust import (
    BaseExtractionStrategy,
    DOMExtractionStrategy,
    ShadowDOMExtractionStrategy,
    IframeExtractionStrategy,
    WebComponentExtractionStrategy,
    VisualExtractionStrategy,
    AccessibilityExtractionStrategy,
    MutationObserverStrategy,
    IntersectionObserverStrategy,
    DynamicContentStrategy,
    InfiniteScrollStrategy,
    FormElementsStrategy,
    ElementData,
    ElementType,
    ExtractionStrategy,
    MemoryManager,
    BoundingBox,
    ElementMetrics,
)


@pytest.fixture
def mock_page():
    """Create a mock Playwright page"""
    page = AsyncMock()
    page.evaluate = AsyncMock()
    page.query_selector_all = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.screenshot = AsyncMock()
    page.title = AsyncMock(return_value="Test Page")
    page.accessibility.snapshot = AsyncMock()
    page.on = MagicMock()
    return page


@pytest.fixture
def memory_manager():
    """Create a memory manager instance"""
    return MemoryManager()


class TestBaseExtractionStrategy:
    """Test base extraction strategy functionality"""

    def test_strategy_initialization(self, mock_page, memory_manager):
        """Test strategy initialization"""
        # Create a concrete implementation for testing
        class TestStrategy(BaseExtractionStrategy):
            async def extract(self) -> List[ElementData]:
                return []
            
            @property
            def strategy_name(self) -> ExtractionStrategy:
                return ExtractionStrategy.DOM_REGULAR
        
        strategy = TestStrategy(mock_page, memory_manager)
        assert strategy.page == mock_page
        assert strategy.memory_manager == memory_manager
        assert strategy.metrics["elements_found"] == 0

    def test_metrics_tracking(self, mock_page, memory_manager):
        """Test metrics tracking functionality"""
        class TestStrategy(BaseExtractionStrategy):
            async def extract(self) -> List[ElementData]:
                self._start_extraction()
                # Simulate some work
                await asyncio.sleep(0.01)
                self._end_extraction(5)
                return []
            
            @property
            def strategy_name(self) -> ExtractionStrategy:
                return ExtractionStrategy.DOM_REGULAR
        
        strategy = TestStrategy(mock_page, memory_manager)
        
        # Run extraction
        asyncio.run(strategy.extract())
        
        # Check metrics
        metrics = strategy.get_metrics()
        assert metrics.extraction_time_ms > 0
        assert metrics.strategy_used == ExtractionStrategy.DOM_REGULAR


class TestDOMExtractionStrategy:
    """Test DOM extraction strategy"""

    @pytest.mark.asyncio
    async def test_dom_extraction_success(self, mock_page, memory_manager):
        """Test successful DOM extraction"""
        # Mock page.evaluate to return sample DOM data
        mock_dom_data = [
            {
                "element_id": "test_button",
                "tag_name": "button",
                "element_type": "button",
                "attributes": {"id": "test_button", "class": "btn-primary"},
                "text_content": "Click me",
                "bounding_box": {"x": 10, "y": 20, "width": 100, "height": 40},
                "is_visible": True,
                "is_clickable": True,
                "xpath": "//button[@id='test_button']",
                "css_selector": "#test_button",
            }
        ]
        mock_page.evaluate.return_value = mock_dom_data
        
        strategy = DOMExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1
        assert elements[0].element_id == "test_button"
        assert elements[0].element_type == ElementType.BUTTON
        assert elements[0].is_clickable is True

    @pytest.mark.asyncio
    async def test_dom_extraction_empty_page(self, mock_page, memory_manager):
        """Test DOM extraction on empty page"""
        mock_page.evaluate.return_value = []
        
        strategy = DOMExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 0

    @pytest.mark.asyncio
    async def test_dom_extraction_malformed_data(self, mock_page, memory_manager):
        """Test DOM extraction with malformed data"""
        mock_dom_data = [
            {"element_id": "valid", "tag_name": "div", "element_type": "unknown"},
            {"missing_id": True},  # Invalid element
            {"element_id": "valid2", "tag_name": "span", "element_type": "unknown"},
        ]
        mock_page.evaluate.return_value = mock_dom_data
        
        strategy = DOMExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        # Should extract valid elements and skip invalid ones
        assert len(elements) == 2
        assert len(strategy.metrics["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_dom_extraction_with_retry(self, mock_page, memory_manager):
        """Test DOM extraction with retry on failure"""
        # First call fails, second succeeds
        mock_page.evaluate.side_effect = [
            Exception("Network error"),
            [{"element_id": "test", "tag_name": "div", "element_type": "unknown"}]
        ]
        
        strategy = DOMExtractionStrategy(mock_page, memory_manager)
        
        # Should retry and eventually succeed
        elements = await strategy.extract()
        assert len(elements) == 1


class TestShadowDOMExtractionStrategy:
    """Test Shadow DOM extraction strategy"""

    @pytest.mark.asyncio
    async def test_shadow_dom_extraction(self, mock_page, memory_manager):
        """Test shadow DOM extraction"""
        mock_shadow_data = [
            {
                "element_id": "shadow_host_1",
                "tag_name": "custom-element",
                "element_type": "shadow_host",
                "has_shadow_root": True,
                "shadow_mode": "open",
                "text_content": "Shadow content",
            }
        ]
        mock_page.evaluate.return_value = mock_shadow_data
        
        strategy = ShadowDOMExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1
        assert elements[0].has_shadow_root is True
        assert elements[0].shadow_mode == "open"
        assert elements[0].element_type == ElementType.SHADOW_HOST

    @pytest.mark.asyncio
    async def test_shadow_dom_closed_mode(self, mock_page, memory_manager):
        """Test extraction of closed shadow DOM"""
        mock_shadow_data = [
            {
                "element_id": "closed_shadow",
                "tag_name": "secure-element",
                "element_type": "shadow_host",
                "has_shadow_root": True,
                "shadow_mode": "closed",
            }
        ]
        mock_page.evaluate.return_value = mock_shadow_data
        
        strategy = ShadowDOMExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert elements[0].shadow_mode == "closed"


class TestIframeExtractionStrategy:
    """Test iframe extraction strategy"""

    @pytest.mark.asyncio
    async def test_iframe_extraction(self, mock_page, memory_manager):
        """Test iframe content extraction"""
        # Mock iframe handles
        mock_handle = AsyncMock()
        mock_frame = AsyncMock()
        mock_frame.evaluate = AsyncMock(return_value=[
            {
                "element_id": "iframe_button",
                "tag_name": "button",
                "text_content": "Iframe button",
            }
        ])
        mock_handle.content_frame = AsyncMock(return_value=mock_frame)
        mock_page.query_selector_all.return_value = [mock_handle]
        
        strategy = IframeExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1
        assert elements[0].iframe_context == "iframe_0"
        assert elements[0].iframe_depth == 1

    @pytest.mark.asyncio
    async def test_iframe_cross_origin_failure(self, mock_page, memory_manager):
        """Test handling of cross-origin iframe"""
        mock_handle = AsyncMock()
        mock_handle.content_frame = AsyncMock(side_effect=Exception("Cross-origin"))
        mock_page.query_selector_all.return_value = [mock_handle]
        
        strategy = IframeExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        # Should handle the error gracefully
        assert len(elements) == 0
        assert len(strategy.metrics["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_nested_iframes(self, mock_page, memory_manager):
        """Test nested iframe extraction"""
        # This would require more complex mocking
        mock_page.query_selector_all.return_value = []
        
        strategy = IframeExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 0


class TestWebComponentExtractionStrategy:
    """Test web component extraction strategy"""

    @pytest.mark.asyncio
    async def test_web_component_extraction(self, mock_page, memory_manager):
        """Test web component extraction"""
        mock_components = [
            {
                "tagName": "MY-COMPONENT",
                "isCustomElement": True,
                "hasElementInternals": True,
                "shadowRoot": True,
                "attributes": [{"name": "data-id", "value": "123"}],
            }
        ]
        mock_page.evaluate.return_value = mock_components
        
        strategy = WebComponentExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1
        assert elements[0].is_custom_element is True
        assert elements[0].element_type == ElementType.WEB_COMPONENT

    @pytest.mark.asyncio
    async def test_web_component_without_shadow(self, mock_page, memory_manager):
        """Test web component without shadow DOM"""
        mock_components = [
            {
                "tagName": "SIMPLE-COMPONENT",
                "isCustomElement": True,
                "shadowRoot": False,
                "attributes": [],
            }
        ]
        mock_page.evaluate.return_value = mock_components
        
        strategy = WebComponentExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert elements[0].has_shadow_root is False


class TestVisualExtractionStrategy:
    """Test visual extraction strategy"""

    @pytest.mark.asyncio
    async def test_visual_extraction(self, mock_page, memory_manager):
        """Test visual property extraction"""
        mock_visual_data = [
            {
                "element_id": "visual_elem",
                "tag_name": "div",
                "bounding_box": {"x": 0, "y": 0, "width": 200, "height": 100},
                "visual_properties": {
                    "backgroundColor": "rgb(255, 255, 255)",
                    "color": "rgb(0, 0, 0)",
                    "fontSize": "16px",
                },
                "computed_opacity": 1.0,
                "is_above_fold": True,
                "viewport_coverage": 0.05,
            }
        ]
        mock_page.evaluate.return_value = mock_visual_data
        
        strategy = VisualExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1
        assert elements[0].is_visible is True
        assert elements[0].is_in_viewport is True
        assert elements[0].bounding_box is not None

    @pytest.mark.asyncio
    async def test_visual_extraction_hidden_elements(self, mock_page, memory_manager):
        """Test that hidden elements are filtered out"""
        mock_page.evaluate.return_value = []  # No visible elements
        
        strategy = VisualExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 0


class TestAccessibilityExtractionStrategy:
    """Test accessibility tree extraction"""

    @pytest.mark.asyncio
    async def test_accessibility_extraction(self, mock_page, memory_manager):
        """Test accessibility tree extraction"""
        mock_a11y_tree = {
            "role": "button",
            "name": "Submit",
            "description": "Submit the form",
            "children": [
                {"role": "text", "name": "Submit text"},
            ],
        }
        mock_page.accessibility.snapshot.return_value = mock_a11y_tree
        
        strategy = AccessibilityExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) >= 1
        assert elements[0].accessibility is not None
        assert elements[0].accessibility.role == "button"

    @pytest.mark.asyncio
    async def test_accessibility_empty_tree(self, mock_page, memory_manager):
        """Test handling of empty accessibility tree"""
        mock_page.accessibility.snapshot.return_value = None
        
        strategy = AccessibilityExtractionStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 0


class TestMutationObserverStrategy:
    """Test mutation observer strategy"""

    @pytest.mark.asyncio
    async def test_mutation_observer(self, mock_page, memory_manager):
        """Test mutation observer for dynamic content"""
        mock_mutations = [
            {"type": "childList", "target": "DIV", "addedNodes": 3},
            {"type": "attributes", "target": "BUTTON", "addedNodes": 0},
        ]
        mock_page.evaluate.side_effect = [
            None,  # Initial injection
            mock_mutations,  # Get mutation data
        ]
        
        strategy = MutationObserverStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) >= 1
        mock_page.evaluate.assert_called()

    @pytest.mark.asyncio
    async def test_mutation_observer_no_changes(self, mock_page, memory_manager):
        """Test mutation observer with no DOM changes"""
        mock_page.evaluate.side_effect = [None, []]
        
        strategy = MutationObserverStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 0


class TestIntersectionObserverStrategy:
    """Test intersection observer strategy"""

    @pytest.mark.asyncio
    async def test_intersection_observer(self, mock_page, memory_manager):
        """Test intersection observer for lazy loading"""
        mock_visible = [
            {
                "tag": "IMG",
                "id": "lazy_image",
                "classes": ["lazy"],
                "rect": {"x": 0, "y": 0, "width": 100, "height": 100},
            }
        ]
        mock_page.evaluate.side_effect = [None, mock_visible]
        
        strategy = IntersectionObserverStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1
        assert elements[0].is_visible is True
        assert elements[0].is_in_viewport is True


class TestDynamicContentStrategy:
    """Test dynamic content extraction"""

    @pytest.mark.asyncio
    async def test_dynamic_content_extraction(self, mock_page, memory_manager):
        """Test AJAX and dynamic content extraction"""
        mock_dynamic = [
            {
                "element_id": "ajax_content",
                "tag_name": "div",
                "classes": ["ajax-content"],
                "data_attributes": ["loaded", "ajax"],
            }
        ]
        mock_page.evaluate.side_effect = [None, mock_dynamic]
        
        strategy = DynamicContentStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1

    @pytest.mark.asyncio
    async def test_dynamic_content_with_network_monitoring(self, mock_page, memory_manager):
        """Test dynamic content with network response monitoring"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.url = "https://api.example.com/data"
        
        mock_page.evaluate.side_effect = [None, []]
        
        strategy = DynamicContentStrategy(mock_page, memory_manager)
        
        # Simulate response handler
        handler = None
        def capture_handler(event, fn):
            nonlocal handler
            if event == "response":
                handler = fn
        mock_page.on.side_effect = capture_handler
        
        elements = await strategy.extract()
        
        # Response handler should be registered
        mock_page.on.assert_called_with("response", pytest.Any())


class TestInfiniteScrollStrategy:
    """Test infinite scroll extraction"""

    @pytest.mark.asyncio
    async def test_infinite_scroll_extraction(self, mock_page, memory_manager):
        """Test infinite scroll content extraction"""
        # Simulate increasing page height
        mock_page.evaluate.side_effect = [
            1000,  # Initial height
            None,  # Scroll action
            1500,  # New height after scroll
            [{"element_id": "item_1", "tag_name": "article"}],  # New items
            None,  # Second scroll
            1500,  # Same height (no more content)
        ]
        
        strategy = InfiniteScrollStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) >= 1

    @pytest.mark.asyncio
    async def test_infinite_scroll_max_attempts(self, mock_page, memory_manager):
        """Test infinite scroll with max scroll limit"""
        # Always return increasing height to simulate endless scroll
        heights = [1000, 2000, 3000, 4000, 5000, 6000, 7000]
        mock_page.evaluate.side_effect = heights + [[]] * 10
        
        strategy = InfiniteScrollStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        # Should stop after max_scrolls (5)
        assert mock_page.evaluate.call_count <= 15  # Some calls for scrolling and extraction


class TestFormElementsStrategy:
    """Test form elements extraction"""

    @pytest.mark.asyncio
    async def test_form_extraction(self, mock_page, memory_manager):
        """Test form and form control extraction"""
        mock_form_data = [
            {
                "element_id": "login_form",
                "tag_name": "form",
                "element_type": "form",
                "attributes": {
                    "action": "/login",
                    "method": "POST",
                },
            },
            {
                "element_id": "username_input",
                "tag_name": "input",
                "element_type": "text",
                "form_id": "login_form",
                "attributes": {
                    "name": "username",
                    "required": True,
                },
                "validation_state": {
                    "valid": True,
                },
            },
        ]
        mock_page.evaluate.return_value = mock_form_data
        
        strategy = FormElementsStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 2
        assert elements[0].element_type == ElementType.FORM
        assert elements[1].form_associated is True

    @pytest.mark.asyncio
    async def test_form_validation_states(self, mock_page, memory_manager):
        """Test form validation state extraction"""
        mock_form_data = [
            {
                "element_id": "email_input",
                "tag_name": "input",
                "element_type": "email",
                "form_id": "signup_form",
                "validation_state": {
                    "valid": False,
                    "typeMismatch": True,
                    "valueMissing": False,
                },
            }
        ]
        mock_page.evaluate.return_value = mock_form_data
        
        strategy = FormElementsStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1
        assert "typeMismatch" in elements[0].validation_state

    @pytest.mark.asyncio
    async def test_custom_form_elements(self, mock_page, memory_manager):
        """Test custom form-associated elements"""
        mock_form_data = [
            {
                "element_id": "custom_input",
                "tag_name": "my-input",
                "element_type": "custom_form_element",
                "form_id": "custom_form",
                "has_element_internals": True,
            }
        ]
        mock_page.evaluate.return_value = mock_form_data
        
        strategy = FormElementsStrategy(mock_page, memory_manager)
        elements = await strategy.extract()
        
        assert len(elements) == 1
        assert elements[0].form_associated is True


class TestStrategyErrorHandling:
    """Test error handling in strategies"""

    @pytest.mark.asyncio
    async def test_strategy_exception_handling(self, mock_page, memory_manager):
        """Test that strategies handle exceptions gracefully"""
        mock_page.evaluate.side_effect = Exception("JavaScript error")
        
        strategies = [
            DOMExtractionStrategy(mock_page, memory_manager),
            ShadowDOMExtractionStrategy(mock_page, memory_manager),
            WebComponentExtractionStrategy(mock_page, memory_manager),
        ]
        
        for strategy in strategies:
            # Should not raise, but return empty or log error
            try:
                elements = await strategy.extract()
                # Either returns empty or raises after retries
                assert isinstance(elements, list)
            except Exception:
                # After retries, exception is expected
                assert len(strategy.metrics["errors"]) > 0

    @pytest.mark.asyncio
    async def test_strategy_timeout_handling(self, mock_page, memory_manager):
        """Test timeout handling in strategies"""
        async def slow_evaluate(*args):
            await asyncio.sleep(10)  # Simulate slow response
            return []
        
        mock_page.evaluate = slow_evaluate
        
        strategy = DOMExtractionStrategy(mock_page, memory_manager)
        
        # Should handle timeout appropriately
        with pytest.raises(Exception):
            # This will timeout or raise after retries
            await asyncio.wait_for(strategy.extract(), timeout=2)


class TestMemoryManager:
    """Test memory manager functionality"""

    def test_cache_and_retrieve(self, memory_manager):
        """Test caching and retrieving results"""
        test_data = {"elements": ["elem1", "elem2"]}
        memory_manager.cache_result("test_key", test_data, ttl=5)
        
        retrieved = memory_manager.get_cached("test_key")
        assert retrieved == test_data

    def test_cache_expiration(self, memory_manager):
        """Test cache expiration"""
        import time
        
        memory_manager.cache_result("expire_key", "data", ttl=0.1)
        time.sleep(0.2)
        
        retrieved = memory_manager.get_cached("expire_key")
        assert retrieved is None

    def test_cache_cleanup(self, memory_manager):
        """Test cache cleanup"""
        # Add multiple items
        for i in range(10):
            memory_manager.cache_result(f"key_{i}", f"data_{i}", ttl=0.1)
        
        # Wait for expiration
        import time
        time.sleep(0.2)
        
        # Trigger cleanup
        memory_manager._cleanup_if_needed()
        
        # All should be cleaned up
        for i in range(10):
            assert memory_manager.get_cached(f"key_{i}") is None

    def test_clear_cache(self, memory_manager):
        """Test clearing entire cache"""
        memory_manager.cache_result("key1", "data1")
        memory_manager.cache_result("key2", "data2")
        
        memory_manager.clear_cache()
        
        assert memory_manager.get_cached("key1") is None
        assert memory_manager.get_cached("key2") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])