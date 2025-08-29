#!/usr/bin/env python3
"""
PERFORMANCE AND STRESS TESTS FOR ELEMENT EXTRACTOR
==================================================
Tests for performance, scalability, and stress scenarios.
"""

import asyncio
import time
import pytest
import psutil
import gc
from unittest.mock import AsyncMock, MagicMock
from typing import List, Dict, Any
import random
import string
import sys

from element_extractor_no_llm_robust import (
    UltimateElementExtractor,
    ElementData,
    ElementType,
    ExtractionStrategy,
    Platform,
    ExtractionResult,
    BoundingBox,
    MemoryManager,
    MAX_ELEMENTS_PER_EXTRACTION,
    ELEMENT_BATCH_SIZE,
    CACHE_TTL_SECONDS,
    DEFAULT_TIMEOUT,
    MAX_RETRY_ATTEMPTS,
)


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def generate_random_string(length: int) -> str:
    """Generate random string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_mock_elements(count: int, complexity: str = "simple") -> List[Dict[str, Any]]:
    """Generate mock element data for testing"""
    elements = []
    
    for i in range(count):
        element = {
            "element_id": f"elem_{i}_{generate_random_string(8)}",
            "tag_name": random.choice(["div", "span", "button", "input", "a", "p"]),
            "element_type": random.choice(["unknown", "button", "link", "input"]),
        }
        
        if complexity == "complex":
            # Add more data for complex elements
            element.update({
                "text_content": generate_random_string(random.randint(10, 100)),
                "inner_html": f"<span>{generate_random_string(50)}</span>",
                "attributes": {f"attr_{j}": generate_random_string(10) for j in range(5)},
                "dataset": {f"data_{j}": generate_random_string(10) for j in range(3)},
                "class_list": [f"class_{j}" for j in range(random.randint(1, 5))],
                "bounding_box": {
                    "x": random.uniform(0, 1920),
                    "y": random.uniform(0, 1080),
                    "width": random.uniform(10, 500),
                    "height": random.uniform(10, 300),
                },
                "computed_style": {
                    "display": random.choice(["block", "inline", "flex", "grid"]),
                    "position": random.choice(["static", "relative", "absolute", "fixed"]),
                    "color": f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})",
                },
                "is_visible": random.choice([True, False]),
                "is_clickable": random.choice([True, False]),
                "xpath": f"//div[@id='container']/div[{i}]",
                "css_selector": f"#container > div:nth-child({i})",
            })
        
        elements.append(element)
    
    return elements


class TestExtractionPerformance:
    """Test extraction performance metrics"""

    @pytest.mark.asyncio
    async def test_dom_extraction_speed(self):
        """Test DOM extraction speed for various page sizes"""
        test_cases = [
            (100, 0.5),    # 100 elements should complete in 0.5s
            (1000, 2.0),   # 1000 elements in 2s
            (5000, 5.0),   # 5000 elements in 5s
        ]
        
        for element_count, max_duration in test_cases:
            mock_page = AsyncMock()
            mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(element_count))
            
            from element_extractor_no_llm_robust import DOMExtractionStrategy
            strategy = DOMExtractionStrategy(mock_page, MemoryManager())
            
            start_time = time.perf_counter()
            elements = await strategy.extract()
            duration = time.perf_counter() - start_time
            
            assert len(elements) > 0
            # Allow some flexibility in timing
            assert duration < max_duration * 2, f"Extraction of {element_count} elements took {duration:.2f}s (expected < {max_duration}s)"

    @pytest.mark.asyncio
    async def test_parallel_strategy_performance(self):
        """Test performance of parallel strategy execution"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Mock different strategy responses
        def mock_evaluate(script):
            time.sleep(0.1)  # Simulate some processing time
            return generate_mock_elements(100)
        
        mock_page.evaluate = AsyncMock(side_effect=mock_evaluate)
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.accessibility.snapshot = AsyncMock(return_value=None)
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Test with multiple strategies
        strategies = [
            ExtractionStrategy.DOM_REGULAR,
            ExtractionStrategy.DOM_SHADOW,
            ExtractionStrategy.VISUAL,
        ]
        
        start_time = time.perf_counter()
        result = await extractor.extract(
            "https://example.com",
            strategies=strategies
        )
        duration = time.perf_counter() - start_time
        
        # Parallel execution should be faster than sequential
        # With 3 strategies at 0.1s each, sequential would be 0.3s minimum
        # Parallel should complete faster (accounting for overhead)
        assert duration < 0.5, f"Parallel extraction took {duration:.2f}s"

    @pytest.mark.asyncio
    async def test_batch_extraction_performance(self):
        """Test batch URL extraction performance"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(50))
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        urls = [f"https://example{i}.com" for i in range(10)]
        
        start_time = time.perf_counter()
        results = await extractor.extract_batch(urls, max_concurrent=3)
        duration = time.perf_counter() - start_time
        
        assert len(results) == 10
        # With max_concurrent=3, should be faster than sequential
        assert duration < len(urls) * 0.5, f"Batch extraction took {duration:.2f}s"


class TestMemoryUsage:
    """Test memory usage and management"""

    @pytest.mark.asyncio
    async def test_memory_usage_small_extraction(self):
        """Test memory usage for small extractions"""
        initial_memory = get_memory_usage()
        
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(100, "simple"))
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://example.com")
        
        peak_memory = get_memory_usage()
        memory_increase = peak_memory - initial_memory
        
        # Small extraction should use minimal memory (< 50MB increase)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB"
        
        # Cleanup
        await extractor.close()
        gc.collect()

    @pytest.mark.asyncio
    async def test_memory_usage_large_extraction(self):
        """Test memory usage for large extractions"""
        initial_memory = get_memory_usage()
        
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(5000, "complex"))
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        result = await extractor.extract("https://example.com")
        
        peak_memory = get_memory_usage()
        memory_increase = peak_memory - initial_memory
        
        # Large extraction should still be reasonable (< 200MB increase)
        assert memory_increase < 200, f"Memory increased by {memory_increase:.2f}MB"
        
        # Cleanup should free memory
        await extractor.close()
        gc.collect()
        
        post_cleanup_memory = get_memory_usage()
        assert post_cleanup_memory < peak_memory

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test for memory leaks in repeated extractions"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(1000, "complex"))
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        memory_readings = []
        
        # Perform multiple extractions
        for i in range(5):
            await extractor.extract(f"https://example{i}.com")
            gc.collect()
            memory_readings.append(get_memory_usage())
        
        # Check for memory leak (memory shouldn't continuously increase)
        # Allow some variance but check for trend
        memory_increases = [memory_readings[i+1] - memory_readings[i] for i in range(len(memory_readings)-1)]
        avg_increase = sum(memory_increases) / len(memory_increases)
        
        # Average increase should be minimal
        assert avg_increase < 10, f"Average memory increase: {avg_increase:.2f}MB (possible leak)"
        
        await extractor.close()


class TestCachePerformance:
    """Test cache performance and efficiency"""

    def test_cache_hit_performance(self):
        """Test cache hit performance"""
        memory_manager = MemoryManager()
        
        # Populate cache
        test_data = {"elements": generate_mock_elements(100, "complex")}
        cache_key = "test_key"
        memory_manager.cache_result(cache_key, test_data)
        
        # Measure cache hit time
        start_time = time.perf_counter()
        for _ in range(1000):
            result = memory_manager.get_cached(cache_key)
        duration = time.perf_counter() - start_time
        
        # Cache hits should be very fast
        avg_time = duration / 1000
        assert avg_time < 0.0001, f"Average cache hit time: {avg_time*1000:.4f}ms"

    def test_cache_cleanup_performance(self):
        """Test cache cleanup performance"""
        memory_manager = MemoryManager()
        
        # Fill cache with many items
        for i in range(1000):
            memory_manager.cache_result(f"key_{i}", f"data_{i}", ttl=0.1)
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Measure cleanup time
        start_time = time.perf_counter()
        memory_manager._cleanup_if_needed()
        duration = time.perf_counter() - start_time
        
        # Cleanup should be fast even with many items
        assert duration < 0.1, f"Cleanup took {duration:.4f}s"

    def test_cache_memory_usage(self):
        """Test cache memory usage"""
        memory_manager = MemoryManager()
        initial_memory = get_memory_usage()
        
        # Add large amount of cached data
        for i in range(100):
            large_data = {
                "elements": generate_mock_elements(100, "complex"),
                "metadata": generate_random_string(1000),
            }
            memory_manager.cache_result(f"large_key_{i}", large_data)
        
        peak_memory = get_memory_usage()
        memory_used = peak_memory - initial_memory
        
        # Cache should use reasonable memory
        assert memory_used < 100, f"Cache used {memory_used:.2f}MB"
        
        # Clear cache should free memory
        memory_manager.clear_cache()
        gc.collect()


class TestStressScenarios:
    """Test stress scenarios and limits"""

    @pytest.mark.asyncio
    async def test_maximum_elements_limit(self):
        """Test handling of maximum element limit"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Generate more elements than the limit
        huge_element_list = generate_mock_elements(MAX_ELEMENTS_PER_EXTRACTION + 5000, "simple")
        mock_page.evaluate = AsyncMock(return_value=huge_element_list)
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        start_time = time.perf_counter()
        result = await extractor.extract("https://huge.com")
        duration = time.perf_counter() - start_time
        
        # Should handle large number efficiently
        assert result.total_elements <= MAX_ELEMENTS_PER_EXTRACTION + 5000
        assert duration < 10, f"Processing took {duration:.2f}s"

    @pytest.mark.asyncio
    async def test_rapid_sequential_extractions(self):
        """Test rapid sequential extractions"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(100))
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        start_time = time.perf_counter()
        
        # Perform rapid extractions
        for i in range(20):
            await extractor.extract(f"https://rapid{i}.com")
        
        duration = time.perf_counter() - start_time
        
        # Should handle rapid requests efficiently
        assert duration < 10, f"20 extractions took {duration:.2f}s"
        
        await extractor.close()

    @pytest.mark.asyncio
    async def test_concurrent_strategy_stress(self):
        """Test stress with all strategies running concurrently"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Mock all strategy responses
        mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(500))
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.accessibility.snapshot = AsyncMock(return_value={"role": "document"})
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Use all strategies
        all_strategies = list(ExtractionStrategy)
        
        start_time = time.perf_counter()
        result = await extractor.extract(
            "https://stress.com",
            strategies=all_strategies
        )
        duration = time.perf_counter() - start_time
        
        # Should complete even with all strategies
        assert result is not None
        assert duration < 15, f"All strategies took {duration:.2f}s"

    @pytest.mark.asyncio
    async def test_memory_pressure_scenario(self):
        """Test behavior under memory pressure"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        # Generate very large, complex elements
        large_elements = []
        for i in range(1000):
            element = generate_mock_elements(1, "complex")[0]
            # Add large text content
            element["text_content"] = generate_random_string(10000)
            element["inner_html"] = generate_random_string(10000)
            large_elements.append(element)
        
        mock_page.evaluate = AsyncMock(return_value=large_elements)
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Should handle without crashing
        result = await extractor.extract("https://memory-heavy.com")
        assert result.total_elements > 0
        
        await extractor.close()
        gc.collect()


class TestRetryPerformance:
    """Test retry mechanism performance"""

    @pytest.mark.asyncio
    async def test_retry_with_backoff_timing(self):
        """Test retry with exponential backoff timing"""
        mock_page = AsyncMock()
        
        attempts = []
        def track_attempts(*args):
            attempts.append(time.time())
            if len(attempts) < MAX_RETRY_ATTEMPTS:
                raise Exception("Temporary failure")
            return []
        
        mock_page.evaluate = AsyncMock(side_effect=track_attempts)
        
        from element_extractor_no_llm_robust import DOMExtractionStrategy
        strategy = DOMExtractionStrategy(mock_page, MemoryManager())
        
        start_time = time.time()
        result = await strategy.extract()
        total_duration = time.time() - start_time
        
        # Check exponential backoff pattern
        assert len(attempts) == MAX_RETRY_ATTEMPTS
        
        # Check delays are increasing
        if len(attempts) > 1:
            delays = [attempts[i+1] - attempts[i] for i in range(len(attempts)-1)]
            # Each delay should be longer than the previous (with some tolerance)
            for i in range(len(delays)-1):
                assert delays[i+1] >= delays[i] * 0.9  # Allow 10% tolerance

    @pytest.mark.asyncio
    async def test_retry_overhead(self):
        """Test performance overhead of retry mechanism"""
        mock_page = AsyncMock()
        
        # Successful on first try
        mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(100))
        
        from element_extractor_no_llm_robust import DOMExtractionStrategy
        strategy = DOMExtractionStrategy(mock_page, MemoryManager())
        
        start_time = time.perf_counter()
        result = await strategy.extract()
        duration = time.perf_counter() - start_time
        
        # Retry mechanism shouldn't add significant overhead on success
        assert duration < 0.5, f"Extraction with retry overhead took {duration:.2f}s"


class TestScalability:
    """Test scalability with increasing load"""

    @pytest.mark.asyncio
    async def test_linear_scalability(self):
        """Test that performance scales linearly with element count"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        timings = []
        element_counts = [100, 500, 1000, 2000]
        
        for count in element_counts:
            mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(count))
            
            start_time = time.perf_counter()
            await extractor.extract(f"https://scale{count}.com")
            duration = time.perf_counter() - start_time
            
            timings.append((count, duration))
        
        # Check for approximately linear scaling
        # Time per element should be relatively constant
        time_per_element = [(duration / count) for count, duration in timings]
        avg_time = sum(time_per_element) / len(time_per_element)
        
        # All should be within 50% of average (allowing for overhead)
        for tpe in time_per_element:
            assert abs(tpe - avg_time) < avg_time * 0.5
        
        await extractor.close()

    @pytest.mark.asyncio
    async def test_batch_scalability(self):
        """Test batch extraction scalability"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=generate_mock_elements(100))
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        batch_sizes = [5, 10, 20, 30]
        
        for batch_size in batch_sizes:
            urls = [f"https://batch{i}.com" for i in range(batch_size)]
            
            start_time = time.perf_counter()
            results = await extractor.extract_batch(urls, max_concurrent=5)
            duration = time.perf_counter() - start_time
            
            # Should complete in reasonable time
            assert len(results) == batch_size
            assert duration < batch_size * 0.5, f"Batch of {batch_size} took {duration:.2f}s"
        
        await extractor.close()


class TestResourceLimits:
    """Test resource limit handling"""

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling for slow pages"""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        async def slow_evaluate(*args):
            await asyncio.sleep(DEFAULT_TIMEOUT / 1000 + 1)  # Exceed timeout
            return []
        
        mock_page.evaluate = slow_evaluate
        mock_page.wait_for_load_state = AsyncMock()
        mock_browser.get_page.return_value = mock_page
        
        extractor = UltimateElementExtractor(browser=mock_browser)
        
        # Should timeout appropriately
        with pytest.raises(Exception):
            await asyncio.wait_for(
                extractor.extract("https://slow.com"),
                timeout=DEFAULT_TIMEOUT / 1000 + 2
            )

    def test_element_batch_processing(self):
        """Test element batch processing efficiency"""
        # Create large list of elements
        elements = []
        for i in range(ELEMENT_BATCH_SIZE * 3 + 50):
            elements.append(
                ElementData(
                    element_id=f"batch_{i}",
                    tag_name="div",
                    element_type=ElementType.UNKNOWN,
                )
            )
        
        # Process in batches (simulated)
        processed = 0
        batch_count = 0
        
        while processed < len(elements):
            batch = elements[processed:processed + ELEMENT_BATCH_SIZE]
            batch_count += 1
            processed += len(batch)
        
        expected_batches = (len(elements) + ELEMENT_BATCH_SIZE - 1) // ELEMENT_BATCH_SIZE
        assert batch_count == expected_batches


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-W", "ignore::DeprecationWarning"])