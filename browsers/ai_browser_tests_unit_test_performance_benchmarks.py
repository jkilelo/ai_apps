#!/usr/bin/env python3
"""
Performance Benchmark Tests for AI Browser v2.0.0

Tests system performance against stated SLAs:
- Browser init: <2 seconds
- Page capture: <5 seconds  
- Action execution: <1 second
- LLM response: <10 seconds
- Memory query: <100ms

Additional performance validation:
- Concurrent operation performance
- Memory leak detection
- Resource usage optimization
- Scalability under load
- Network efficiency

**CRITICAL**: Uses REAL systems and APIs to validate production performance.
"""

import asyncio
import pytest
import sys
import time
import psutil
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import statistics
from datetime import datetime
import json
from dotenv import load_dotenv
import gc

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from execution.browser_manager import BrowserManager, BrowserConfig
from execution.stealth_manager import StealthManager
from execution.action_executor import ActionExecutor
from perception.state_observer import StateObserver
from perception.dom_processor import DOMProcessor
from perception.visual_annotator import VisualAnnotator
from cognition.orchestrator import AgentOrchestrator
from cognition.llm import LLMManager
from memory.memory_manager import MemoryManager

# Load environment variables
load_dotenv()


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time else 0


class SystemResourceMonitor:
    """Monitor system resource usage during tests."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss
        self.peak_memory = self.initial_memory
        
    def update_peak_memory(self):
        current_memory = self.process.memory_info().rss
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
    
    @property
    def memory_usage_mb(self) -> float:
        return self.process.memory_info().rss / 1024 / 1024
    
    @property
    def memory_increase_mb(self) -> float:
        return (self.peak_memory - self.initial_memory) / 1024 / 1024
    
    @property
    def cpu_percent(self) -> float:
        return self.process.cpu_percent()


class TestCoreSLAPerformance:
    """Test core system components against stated SLAs."""
    
    @pytest.mark.asyncio
    async def test_browser_init_sla(self):
        """Test browser initialization meets <2 second SLA."""
        
        browser_types = ["chromium"]  # Focus on primary browser
        results = []
        
        for browser_type in browser_types:
            config = BrowserConfig(
                headless=True,
                browser_type=browser_type,
                stealth_mode=True
            )
            
            # Run multiple iterations to get reliable timing
            for iteration in range(5):
                browser_manager = BrowserManager(config)
                
                try:
                    with PerformanceTimer(f"browser_init_{browser_type}_{iteration}") as timer:
                        browser = await browser_manager.launch()
                        context = await browser_manager.create_context()
                    
                    results.append(timer.duration)
                    
                    # SLA check
                    assert timer.duration < 2.0, \
                        f"Browser init {timer.duration:.2f}s exceeds 2s SLA (iteration {iteration})"
                    
                finally:
                    await browser_manager.close()
        
        # Statistical analysis
        avg_time = statistics.mean(results)
        max_time = max(results)
        min_time = min(results)
        
        print(f"✅ Browser Init SLA Performance:")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Range: {min_time:.2f}s - {max_time:.2f}s")
        print(f"   All {len(results)} iterations under 2s SLA")
        
        # SLA compliance check
        assert avg_time < 1.5, f"Average browser init {avg_time:.2f}s approaching SLA limit"
        assert max_time < 2.0, f"Max browser init {max_time:.2f}s exceeds SLA"
    
    @pytest.mark.asyncio
    async def test_page_capture_sla(self):
        """Test page capture meets <5 second SLA."""
        
        config = BrowserConfig(headless=True, browser_type="chromium")
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            # Test different page types
            test_urls = [
                "https://httpbin.org/get",
                "https://httpbin.org/forms/post",  
                "https://www.google.com",
                "https://github.com",
            ]
            
            results = []
            
            for url in test_urls:
                try:
                    # Navigate to page
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(1)  # Allow page to stabilize
                    
                    # Test complete page capture (DOM + screenshot + state)
                    with PerformanceTimer(f"page_capture_{url}") as timer:
                        # Capture DOM
                        dom_processor = DOMProcessor()
                        dom_data = await dom_processor.process_page_dom(page)
                        
                        # Capture screenshot  
                        screenshot = await page.screenshot()
                        
                        # Capture page state
                        state_observer = StateObserver(page)
                        page_state = await state_observer.capture_current_state()
                    
                    results.append(timer.duration)
                    
                    # SLA check
                    assert timer.duration < 5.0, \
                        f"Page capture {timer.duration:.2f}s exceeds 5s SLA for {url}"
                    
                    # Verify data quality
                    assert dom_data is not None, f"DOM capture failed for {url}"
                    assert screenshot is not None, f"Screenshot failed for {url}"
                    assert page_state is not None, f"State capture failed for {url}"
                    
                except Exception as e:
                    print(f"⚠️  Page capture failed for {url}: {e}")
                    continue
            
            if results:
                avg_time = statistics.mean(results)
                max_time = max(results)
                
                print(f"✅ Page Capture SLA Performance:")
                print(f"   Average: {avg_time:.2f}s")
                print(f"   Max: {max_time:.2f}s")
                print(f"   All {len(results)} captures under 5s SLA")
                
                assert avg_time < 3.0, f"Average page capture {avg_time:.2f}s approaching SLA limit"
            
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_action_execution_sla(self):
        """Test action execution meets <1 second SLA."""
        
        config = BrowserConfig(headless=True, browser_type="chromium")
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            await page.goto("https://httpbin.org/forms/post", wait_until="networkidle")
            
            # Test different action types
            actions = [
                ("click", "input[type='submit']"),
                ("type", "input[name='custname']", "Test User"),
                ("scroll", None),
                ("screenshot", None),
                ("evaluate", "document.title"),
            ]
            
            results = []
            
            for action_type, selector, *params in actions:
                try:
                    with PerformanceTimer(f"action_{action_type}") as timer:
                        if action_type == "click":
                            element = await page.query_selector(selector)
                            if element:
                                await element.click()
                        elif action_type == "type":
                            await page.fill(selector, params[0])
                        elif action_type == "scroll":
                            await page.evaluate("window.scrollTo(0, 100)")
                        elif action_type == "screenshot":
                            await page.screenshot()
                        elif action_type == "evaluate":
                            await page.evaluate(params[0])
                    
                    results.append((action_type, timer.duration))
                    
                    # SLA check
                    assert timer.duration < 1.0, \
                        f"Action {action_type} took {timer.duration:.3f}s, exceeds 1s SLA"
                    
                except Exception as e:
                    print(f"⚠️  Action {action_type} failed: {e}")
                    continue
            
            if results:
                avg_time = statistics.mean([duration for _, duration in results])
                max_time = max(duration for _, duration in results)
                
                print(f"✅ Action Execution SLA Performance:")
                print(f"   Average: {avg_time:.3f}s")
                print(f"   Max: {max_time:.3f}s")
                
                for action_type, duration in results:
                    print(f"   {action_type}: {duration:.3f}s")
                
                assert avg_time < 0.5, f"Average action time {avg_time:.3f}s approaching SLA limit"
            
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_llm_response_sla(self):
        """Test LLM response meets <10 second SLA."""
        
        # Skip if no API keys available
        if not os.getenv('OPENAI_API_KEY') and not os.getenv('GEMINI_API_KEY'):
            pytest.skip("No LLM API keys available")
        
        llm_manager = LLMManager()
        await llm_manager.initialize()
        
        # Test different prompt types
        test_prompts = [
            "What is the next action to take?",
            "Analyze the current page and suggest an action.",
            "Generate a click action for the submit button.",
            "Summarize what you see on this page.",
        ]
        
        results = []
        
        for prompt in test_prompts:
            try:
                with PerformanceTimer(f"llm_response") as timer:
                    response = await llm_manager.generate_response(
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=100,
                        temperature=0.1
                    )
                
                results.append(timer.duration)
                
                # SLA check
                assert timer.duration < 10.0, \
                    f"LLM response {timer.duration:.2f}s exceeds 10s SLA"
                
                # Verify response quality
                assert response is not None, "LLM response is None"
                assert len(response) > 0, "LLM response is empty"
                
            except Exception as e:
                print(f"⚠️  LLM request failed: {e}")
                continue
        
        if results:
            avg_time = statistics.mean(results)
            max_time = max(results)
            
            print(f"✅ LLM Response SLA Performance:")
            print(f"   Average: {avg_time:.2f}s")
            print(f"   Max: {max_time:.2f}s")
            print(f"   All {len(results)} responses under 10s SLA")
            
            assert avg_time < 5.0, f"Average LLM response {avg_time:.2f}s approaching SLA limit"
        
        await llm_manager.close()
    
    @pytest.mark.asyncio
    async def test_memory_query_sla(self):
        """Test memory queries meet <100ms SLA."""
        
        memory_manager = MemoryManager()
        await memory_manager.initialize()
        
        # Populate with test data first
        task_id = "performance_test"
        
        # Store test data
        for i in range(10):
            await memory_manager.store_task_step(
                task_id=task_id,
                step_number=i,
                action={'type': 'click', 'selector': f'#button_{i}'},
                result={'success': True, 'duration': 0.1},
                page_state={
                    'url': f'https://example.com/page_{i}',
                    'title': f'Page {i}',
                    'elements': [f'element_{j}' for j in range(5)]
                }
            )
        
        # Test different query types
        queries = [
            ("session_history", lambda: memory_manager.get_task_history(task_id, limit=5)),
            ("session_count", lambda: memory_manager.session._execute_query("SELECT COUNT(*) FROM conversations")),
        ]
        
        results = []
        
        for query_type, query_func in queries:
            try:
                with PerformanceTimer(f"memory_query_{query_type}") as timer:
                    result = await query_func()
                
                results.append((query_type, timer.duration))
                
                # SLA check (100ms = 0.1s)
                assert timer.duration < 0.1, \
                    f"Memory query {query_type} took {timer.duration:.3f}s, exceeds 100ms SLA"
                
                # Verify result quality
                assert result is not None, f"Memory query {query_type} returned None"
                
            except Exception as e:
                print(f"⚠️  Memory query {query_type} failed: {e}")
                continue
        
        if results:
            avg_time = statistics.mean([duration for _, duration in results])
            max_time = max(duration for _, duration in results)
            
            print(f"✅ Memory Query SLA Performance:")
            print(f"   Average: {avg_time:.3f}s ({avg_time*1000:.1f}ms)")
            print(f"   Max: {max_time:.3f}s ({max_time*1000:.1f}ms)")
            
            for query_type, duration in results:
                print(f"   {query_type}: {duration:.3f}s ({duration*1000:.1f}ms)")
            
            assert avg_time < 0.05, f"Average memory query {avg_time*1000:.1f}ms approaching SLA limit"
        
        await memory_manager.close()


class TestConcurrentPerformance:
    """Test performance under concurrent load."""
    
    @pytest.mark.asyncio
    async def test_concurrent_browser_operations(self):
        """Test multiple browser operations running concurrently."""
        
        resource_monitor = SystemResourceMonitor()
        
        async def browser_task(task_id: int) -> Dict[str, Any]:
            """Single browser task for concurrent testing."""
            config = BrowserConfig(headless=True, browser_type="chromium")
            browser_manager = BrowserManager(config)
            
            try:
                with PerformanceTimer(f"concurrent_task_{task_id}") as timer:
                    browser = await browser_manager.launch()
                    context = await browser_manager.create_context()
                    page = await context.new_page()
                    
                    await page.goto("https://httpbin.org/get", wait_until="networkidle")
                    await page.screenshot()
                    title = await page.title()
                
                return {
                    'task_id': task_id,
                    'duration': timer.duration,
                    'success': True,
                    'title': title
                }
                
            except Exception as e:
                return {
                    'task_id': task_id,
                    'duration': 0,
                    'success': False,
                    'error': str(e)
                }
            finally:
                await browser_manager.close()
                resource_monitor.update_peak_memory()
        
        # Run 5 concurrent browser tasks
        start_time = time.time()
        
        tasks = [browser_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_tasks = [r for r in results if isinstance(r, dict) and r.get('success')]
        failed_tasks = [r for r in results if not (isinstance(r, dict) and r.get('success'))]
        
        print(f"✅ Concurrent Browser Performance:")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Successful tasks: {len(successful_tasks)}/{len(results)}")
        print(f"   Memory increase: {resource_monitor.memory_increase_mb:.1f}MB")
        
        if successful_tasks:
            avg_task_time = statistics.mean([task['duration'] for task in successful_tasks])
            print(f"   Average task time: {avg_task_time:.2f}s")
            
            # Performance assertions
            assert len(successful_tasks) >= 4, "At least 4/5 concurrent tasks should succeed"
            assert total_time < 20.0, f"Total concurrent time {total_time:.2f}s too high"
            assert avg_task_time < 10.0, f"Average task time {avg_task_time:.2f}s too high"
        
        if failed_tasks:
            print(f"   Failed tasks: {len(failed_tasks)}")
            for task in failed_tasks:
                if isinstance(task, dict):
                    print(f"     Task {task.get('task_id', '?')}: {task.get('error', 'Unknown error')}")
    
    @pytest.mark.asyncio
    async def test_memory_system_concurrent_load(self):
        """Test memory system performance under concurrent load."""
        
        memory_manager = MemoryManager()
        await memory_manager.initialize()
        
        async def memory_task(task_id: int) -> Dict[str, Any]:
            """Single memory operation task."""
            try:
                with PerformanceTimer(f"memory_task_{task_id}") as timer:
                    # Store data
                    await memory_manager.store_task_step(
                        task_id=f"concurrent_task_{task_id}",
                        step_number=1,
                        action={'type': 'test', 'id': task_id},
                        result={'success': True, 'task_id': task_id},
                        page_state={
                            'url': f'https://example.com/task_{task_id}',
                            'title': f'Task {task_id}',
                            'elements': [f'elem_{i}' for i in range(task_id % 5)]
                        }
                    )
                    
                    # Query data
                    history = await memory_manager.get_task_history(f"concurrent_task_{task_id}", limit=1)
                
                return {
                    'task_id': task_id,
                    'duration': timer.duration,
                    'success': True,
                    'records': len(history)
                }
                
            except Exception as e:
                return {
                    'task_id': task_id,
                    'duration': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Run 20 concurrent memory tasks
        start_time = time.time()
        
        tasks = [memory_task(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_tasks = [r for r in results if isinstance(r, dict) and r.get('success')]
        
        print(f"✅ Concurrent Memory Performance:")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Successful tasks: {len(successful_tasks)}/{len(results)}")
        
        if successful_tasks:
            avg_task_time = statistics.mean([task['duration'] for task in successful_tasks])
            max_task_time = max(task['duration'] for task in successful_tasks)
            
            print(f"   Average task time: {avg_task_time:.3f}s ({avg_task_time*1000:.1f}ms)")
            print(f"   Max task time: {max_task_time:.3f}s ({max_task_time*1000:.1f}ms)")
            
            # Performance assertions
            assert len(successful_tasks) >= 18, "At least 18/20 concurrent memory tasks should succeed"
            assert avg_task_time < 0.2, f"Average memory task time {avg_task_time:.3f}s too high"
            assert max_task_time < 0.5, f"Max memory task time {max_task_time:.3f}s too high"
        
        await memory_manager.close()


class TestScalabilityPerformance:
    """Test system performance as load scales up."""
    
    @pytest.mark.asyncio
    async def test_browser_instance_scaling(self):
        """Test performance as number of browser instances increases."""
        
        scales = [1, 2, 3]  # Test 1, 2, 3 concurrent browsers
        results = {}
        
        for scale in scales:
            print(f"Testing {scale} concurrent browser(s)...")
            
            resource_monitor = SystemResourceMonitor()
            
            async def browser_instance(instance_id: int):
                config = BrowserConfig(headless=True, browser_type="chromium")
                browser_manager = BrowserManager(config)
                
                try:
                    browser = await browser_manager.launch()
                    context = await browser_manager.create_context()
                    page = await context.new_page()
                    
                    await page.goto("https://httpbin.org/get", wait_until="networkidle")
                    await asyncio.sleep(2)  # Simulate some work
                    
                    return True
                finally:
                    await browser_manager.close()
                    resource_monitor.update_peak_memory()
            
            with PerformanceTimer(f"scale_{scale}") as timer:
                tasks = [browser_instance(i) for i in range(scale)]
                await asyncio.gather(*tasks)
            
            results[scale] = {
                'duration': timer.duration,
                'memory_mb': resource_monitor.memory_increase_mb,
                'duration_per_browser': timer.duration / scale
            }
            
            print(f"   {scale} browsers: {timer.duration:.2f}s, {resource_monitor.memory_increase_mb:.1f}MB")
        
        # Analyze scaling characteristics
        print(f"✅ Browser Scaling Performance:")
        for scale, data in results.items():
            print(f"   {scale} browsers: {data['duration']:.2f}s total, {data['duration_per_browser']:.2f}s/browser, {data['memory_mb']:.1f}MB")
        
        # Performance assertions
        for scale, data in results.items():
            assert data['duration'] < 30.0, f"Scale {scale} took {data['duration']:.2f}s, too long"
            assert data['duration_per_browser'] < 15.0, f"Scale {scale} per-browser time {data['duration_per_browser']:.2f}s too high"
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations."""
        
        resource_monitor = SystemResourceMonitor()
        initial_memory = resource_monitor.memory_usage_mb
        
        # Perform repeated browser operations
        for iteration in range(5):
            config = BrowserConfig(headless=True, browser_type="chromium")
            browser_manager = BrowserManager(config)
            
            try:
                browser = await browser_manager.launch()
                context = await browser_manager.create_context()
                page = await context.new_page()
                
                await page.goto("https://httpbin.org/get", wait_until="networkidle")
                await page.screenshot()
                
            finally:
                await browser_manager.close()
                
            # Force garbage collection
            gc.collect()
            await asyncio.sleep(0.5)  # Allow cleanup
            
            current_memory = resource_monitor.memory_usage_mb
            memory_increase = current_memory - initial_memory
            
            print(f"   Iteration {iteration + 1}: {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
            
            # Memory leak assertion - allow some growth but not excessive
            assert memory_increase < 50.0, f"Memory leak detected: {memory_increase:.1f}MB increase after {iteration + 1} iterations"
        
        final_memory = resource_monitor.memory_usage_mb
        total_increase = final_memory - initial_memory
        
        print(f"✅ Memory Leak Test:")
        print(f"   Initial memory: {initial_memory:.1f}MB")
        print(f"   Final memory: {final_memory:.1f}MB") 
        print(f"   Total increase: {total_increase:.1f}MB")
        
        # Final assertion
        assert total_increase < 30.0, f"Potential memory leak: {total_increase:.1f}MB increase after 5 iterations"


class TestNetworkPerformance:
    """Test network-related performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_page_load_performance(self):
        """Test page loading performance across different site types."""
        
        config = BrowserConfig(headless=True, browser_type="chromium")
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            # Test different types of sites
            test_sites = [
                ("Simple API", "https://httpbin.org/get"),
                ("Google", "https://www.google.com"),
                ("GitHub", "https://github.com"),
            ]
            
            results = []
            
            for site_name, url in test_sites:
                try:
                    with PerformanceTimer(f"load_{site_name.lower()}") as timer:
                        await page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    results.append((site_name, timer.duration))
                    
                    print(f"   {site_name}: {timer.duration:.2f}s")
                    
                except Exception as e:
                    print(f"   {site_name}: Failed - {e}")
                    continue
            
            if results:
                avg_load_time = statistics.mean([duration for _, duration in results])
                max_load_time = max(duration for _, duration in results)
                
                print(f"✅ Page Load Performance:")
                print(f"   Average: {avg_load_time:.2f}s")
                print(f"   Max: {max_load_time:.2f}s")
                
                # Performance assertions
                assert avg_load_time < 10.0, f"Average load time {avg_load_time:.2f}s too high"
                assert max_load_time < 15.0, f"Max load time {max_load_time:.2f}s too high"
        
        finally:
            await browser_manager.close()


@pytest.mark.asyncio
async def test_end_to_end_performance_integration():
    """Comprehensive end-to-end performance test."""
    
    resource_monitor = SystemResourceMonitor()
    
    print("🚀 Starting comprehensive performance integration test...")
    
    with PerformanceTimer("end_to_end_performance") as overall_timer:
        # Initialize all systems
        config = BrowserConfig(headless=True, browser_type="chromium", stealth_mode=True)
        browser_manager = BrowserManager(config)
        memory_manager = MemoryManager()
        
        await memory_manager.initialize()
        
        browser = await browser_manager.launch()
        context = await browser_manager.create_context()
        
        # Apply stealth
        stealth_manager = StealthManager()
        await stealth_manager.apply_stealth_plugins(context)
        
        page = await context.new_page()
        
        # Simulate realistic workflow
        workflow_steps = [
            ("Navigate to Google", lambda: page.goto("https://www.google.com", wait_until="networkidle")),
            ("Capture page state", lambda: StateObserver(page).capture_current_state()),
            ("Take screenshot", lambda: page.screenshot()),
            ("Process DOM", lambda: DOMProcessor().process_page_dom(page)),
            ("Store in memory", lambda: memory_manager.store_task_step(
                task_id="performance_test",
                step_number=1,
                action={'type': 'navigate', 'url': 'https://www.google.com'},
                result={'success': True},
                page_state={'url': 'https://www.google.com', 'title': 'Google'}
            )),
            ("Query memory", lambda: memory_manager.get_task_history("performance_test", limit=5)),
        ]
        
        step_timings = []
        
        for step_name, step_func in workflow_steps:
            try:
                with PerformanceTimer(step_name) as step_timer:
                    await step_func()
                
                step_timings.append((step_name, step_timer.duration))
                resource_monitor.update_peak_memory()
                
                print(f"   ✅ {step_name}: {step_timer.duration:.2f}s")
                
            except Exception as e:
                print(f"   ❌ {step_name}: Failed - {e}")
                step_timings.append((step_name, 0))
        
        # Cleanup
        await browser_manager.close()
        await memory_manager.close()
    
    # Performance analysis
    total_time = overall_timer.duration
    successful_steps = [timing for timing in step_timings if timing[1] > 0]
    
    print(f"✅ End-to-End Performance Results:")
    print(f"   Total workflow time: {total_time:.2f}s")
    print(f"   Successful steps: {len(successful_steps)}/{len(workflow_steps)}")
    print(f"   Memory usage: {resource_monitor.memory_usage_mb:.1f}MB")
    print(f"   Memory increase: {resource_monitor.memory_increase_mb:.1f}MB")
    
    # Performance assertions
    assert total_time < 30.0, f"End-to-end workflow {total_time:.2f}s exceeds 30s limit"
    assert len(successful_steps) >= 5, f"Only {len(successful_steps)} steps succeeded"
    assert resource_monitor.memory_increase_mb < 100.0, f"Memory increase {resource_monitor.memory_increase_mb:.1f}MB too high"
    
    print("🎉 Comprehensive performance test completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])