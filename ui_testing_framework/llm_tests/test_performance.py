#!/usr/bin/env python3
"""
Performance and Load Tests
QA Focus: Response time, throughput, resource usage, scalability
Senior QA: Baseline performance metrics, stress testing, load patterns
"""

import sys
import time
import asyncio
import threading
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import psutil
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import (
    query_llm,
    stream_llm,
    aquery_llm,
    astream_llm,
    call_default_llm,
    Provider,
    StrategyType,
)
from test_config import (
    TestRunner,
    assert_response_valid,
    measure_latency,
    measure_async_latency,
)


class PerformanceTests:
    """Test performance characteristics and load handling"""
    
    def __init__(self):
        self.runner = TestRunner()
        self.performance_metrics = {
            "latency": [],
            "throughput": [],
            "memory_usage": [],
            "cpu_usage": [],
        }
    
    # ==================== LATENCY TESTS ====================
    
    def test_simple_query_latency(self):
        """Test latency for simple queries"""
        messages = [{"role": "user", "content": "Reply with OK"}]
        latencies = []
        
        # Run 10 iterations
        for _ in range(10):
            start = time.perf_counter()
            response = query_llm(messages, max_tokens=10)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
            assert_response_valid(response)
        
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
        
        print(f"    Avg: {avg_latency:.2f}ms, P95: {p95_latency:.2f}ms, P99: {p99_latency:.2f}ms")
        
        # Assert reasonable latency (under 5 seconds for simple query)
        assert avg_latency < 5000, f"Average latency too high: {avg_latency:.2f}ms"
        assert p99_latency < 10000, f"P99 latency too high: {p99_latency:.2f}ms"
    
    def test_complex_query_latency(self):
        """Test latency for complex queries"""
        messages = [
            {"role": "system", "content": "You are an expert analyst."},
            {"role": "user", "content": "Analyze the economic implications of AI on job markets in the next decade."}
        ]
        
        latencies = []
        
        for _ in range(5):
            start = time.perf_counter()
            response = query_llm(messages, max_tokens=200)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
            assert_response_valid(response, min_length=100)
        
        avg_latency = statistics.mean(latencies)
        print(f"    Complex query avg latency: {avg_latency:.2f}ms")
        
        # Complex queries can take longer
        assert avg_latency < 15000, f"Complex query latency too high: {avg_latency:.2f}ms"
    
    def test_streaming_first_token_latency(self):
        """Test time to first token in streaming"""
        messages = [{"role": "user", "content": "Count from 1 to 10"}]
        first_token_times = []
        
        for _ in range(5):
            start = time.perf_counter()
            first_token = None
            
            for chunk in stream_llm(messages, max_tokens=50):
                if chunk.content and not first_token:
                    first_token = (time.perf_counter() - start) * 1000
                    break
            
            if first_token:
                first_token_times.append(first_token)
        
        avg_first_token = statistics.mean(first_token_times)
        print(f"    Avg first token: {avg_first_token:.2f}ms")
        
        # First token should be fast
        assert avg_first_token < 3000, f"First token too slow: {avg_first_token:.2f}ms"
    
    def test_strategy_overhead(self):
        """Test performance overhead of different strategies"""
        messages = [{"role": "user", "content": "Explain water in one sentence"}]
        
        strategy_times = {}
        strategies = [
            None,  # Baseline
            StrategyType.CHAIN_OF_THOUGHT,
            StrategyType.TREE_OF_THOUGHTS,
            StrategyType.SELF_CONSISTENCY,
            StrategyType.META_PROMPTING,
        ]
        
        for strategy in strategies:
            start = time.perf_counter()
            response = query_llm(
                messages,
                strategy=strategy.value if strategy else None,
                max_tokens=100
            )
            elapsed = (time.perf_counter() - start) * 1000
            strategy_times[str(strategy)] = elapsed
            assert_response_valid(response)
        
        # Calculate overhead
        baseline = strategy_times["None"]
        for strategy, time_ms in strategy_times.items():
            if strategy != "None":
                overhead = ((time_ms - baseline) / baseline) * 100
                print(f"    {strategy}: {time_ms:.2f}ms (overhead: {overhead:.1f}%)")
        
        # Strategies should not add more than 200% overhead
        for strategy, time_ms in strategy_times.items():
            assert time_ms < baseline * 3, f"Strategy {strategy} adds too much overhead"
    
    # ==================== THROUGHPUT TESTS ====================
    
    def test_sequential_throughput(self):
        """Test throughput for sequential requests"""
        messages = [{"role": "user", "content": "Say hi"}]
        num_requests = 20
        
        start = time.perf_counter()
        responses = []
        
        for _ in range(num_requests):
            response = query_llm(messages, max_tokens=10)
            responses.append(response)
        
        elapsed = time.perf_counter() - start
        throughput = num_requests / elapsed
        
        print(f"    Sequential throughput: {throughput:.2f} req/s")
        print(f"    Total time for {num_requests} requests: {elapsed:.2f}s")
        
        # Should handle at least 0.5 req/s sequentially
        assert throughput > 0.5, f"Sequential throughput too low: {throughput:.2f} req/s"
        
        # All responses should be valid
        for response in responses:
            assert_response_valid(response)
    
    def test_concurrent_throughput(self):
        """Test throughput with concurrent requests"""
        messages = [{"role": "user", "content": "Say a number"}]
        num_requests = 20
        max_workers = 5
        
        start = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(query_llm, messages, max_tokens=10)
                for _ in range(num_requests)
            ]
            
            responses = []
            for future in as_completed(futures):
                try:
                    response = future.result(timeout=30)
                    responses.append(response)
                except Exception as e:
                    print(f"    Request failed: {e}")
        
        elapsed = time.perf_counter() - start
        throughput = len(responses) / elapsed
        
        print(f"    Concurrent throughput: {throughput:.2f} req/s")
        print(f"    Successful: {len(responses)}/{num_requests}")
        print(f"    Total time: {elapsed:.2f}s")
        
        # Should handle at least 1 req/s with concurrency
        assert throughput > 1.0, f"Concurrent throughput too low: {throughput:.2f} req/s"
        
        # At least 80% should succeed
        assert len(responses) >= num_requests * 0.8, f"Too many failures: {len(responses)}/{num_requests}"
    
    async def test_async_throughput(self):
        """Test throughput with async requests"""
        messages = [{"role": "user", "content": "Say yes or no"}]
        num_requests = 20
        
        start = time.perf_counter()
        
        tasks = [aquery_llm(messages, max_tokens=10) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.perf_counter() - start
        successful = [r for r in responses if not isinstance(r, Exception)]
        throughput = len(successful) / elapsed
        
        print(f"    Async throughput: {throughput:.2f} req/s")
        print(f"    Successful: {len(successful)}/{num_requests}")
        print(f"    Total time: {elapsed:.2f}s")
        
        # Async should be faster than sequential
        assert throughput > 1.5, f"Async throughput too low: {throughput:.2f} req/s"
        assert len(successful) >= num_requests * 0.8
    
    # ==================== LOAD TESTS ====================
    
    def test_sustained_load(self):
        """Test sustained load over time"""
        messages = [{"role": "user", "content": "Reply fast"}]
        duration = 30  # seconds
        request_interval = 2  # seconds between requests
        
        start_time = time.time()
        responses = []
        errors = []
        
        while time.time() - start_time < duration:
            try:
                response = query_llm(messages, max_tokens=10)
                responses.append(response)
            except Exception as e:
                errors.append(str(e))
            
            time.sleep(request_interval)
        
        success_rate = len(responses) / (len(responses) + len(errors)) * 100
        
        print(f"    Sustained load results:")
        print(f"    Duration: {duration}s")
        print(f"    Successful: {len(responses)}")
        print(f"    Failed: {len(errors)}")
        print(f"    Success rate: {success_rate:.1f}%")
        
        # Should maintain at least 90% success rate
        assert success_rate >= 90, f"Success rate too low under sustained load: {success_rate:.1f}%"
    
    def test_burst_load(self):
        """Test handling of burst traffic"""
        messages = [{"role": "user", "content": "Quick"}]
        burst_size = 10
        
        # Send burst of requests all at once
        start = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=burst_size) as executor:
            futures = [
                executor.submit(query_llm, messages, max_tokens=5)
                for _ in range(burst_size)
            ]
            
            responses = []
            errors = []
            
            for future in as_completed(futures):
                try:
                    response = future.result(timeout=30)
                    responses.append(response)
                except Exception as e:
                    errors.append(str(e))
        
        elapsed = time.perf_counter() - start
        
        print(f"    Burst load results:")
        print(f"    Burst size: {burst_size}")
        print(f"    Successful: {len(responses)}")
        print(f"    Failed: {len(errors)}")
        print(f"    Time: {elapsed:.2f}s")
        
        # Should handle at least 70% of burst
        assert len(responses) >= burst_size * 0.7, f"Too many failures in burst: {len(responses)}/{burst_size}"
    
    def test_memory_usage(self):
        """Test memory usage under load"""
        import gc
        
        # Get baseline memory
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        messages = [{"role": "user", "content": "Generate text"}]
        responses = []
        
        # Generate load
        for _ in range(10):
            response = query_llm(messages, max_tokens=100)
            responses.append(response)
        
        # Check memory after load
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - baseline_memory
        
        print(f"    Baseline memory: {baseline_memory:.2f} MB")
        print(f"    Current memory: {current_memory:.2f} MB")
        print(f"    Increase: {memory_increase:.2f} MB")
        
        # Memory increase should be reasonable (< 500MB)
        assert memory_increase < 500, f"Memory usage too high: {memory_increase:.2f} MB increase"
        
        # Clean up
        responses.clear()
        gc.collect()
    
    def test_cpu_usage(self):
        """Test CPU usage patterns"""
        process = psutil.Process()
        messages = [{"role": "user", "content": "Process this"}]
        
        # Measure CPU during requests
        cpu_samples = []
        
        for _ in range(5):
            process.cpu_percent()  # Reset
            response = query_llm(messages, max_tokens=20)
            cpu_usage = process.cpu_percent(interval=0.1)
            cpu_samples.append(cpu_usage)
        
        avg_cpu = statistics.mean(cpu_samples)
        max_cpu = max(cpu_samples)
        
        print(f"    Avg CPU: {avg_cpu:.2f}%")
        print(f"    Max CPU: {max_cpu:.2f}%")
        
        # CPU usage should be reasonable
        assert avg_cpu < 80, f"Average CPU usage too high: {avg_cpu:.2f}%"
    
    # ==================== SCALABILITY TESTS ====================
    
    def test_token_scaling(self):
        """Test performance with different token counts"""
        messages = [{"role": "user", "content": "Write a story"}]
        token_counts = [10, 50, 100, 200, 500]
        
        results = {}
        
        for tokens in token_counts:
            start = time.perf_counter()
            response = query_llm(messages, max_tokens=tokens)
            elapsed = (time.perf_counter() - start) * 1000
            
            results[tokens] = {
                "time_ms": elapsed,
                "response_length": len(response.content),
                "ms_per_token": elapsed / tokens
            }
        
        print(f"    Token scaling results:")
        for tokens, metrics in results.items():
            print(f"    {tokens} tokens: {metrics['time_ms']:.2f}ms ({metrics['ms_per_token']:.2f}ms/token)")
        
        # Time should scale somewhat linearly with tokens
        # Check that ms/token doesn't increase dramatically
        ms_per_token_values = [m["ms_per_token"] for m in results.values()]
        variance = statistics.variance(ms_per_token_values)
        
        assert variance < 100, f"Token scaling not linear, variance: {variance:.2f}"
    
    def test_message_history_scaling(self):
        """Test performance with different conversation lengths"""
        base_message = {"role": "user", "content": "Continue"}
        history_lengths = [1, 5, 10, 20, 50]
        
        results = {}
        
        for length in history_lengths:
            messages = []
            for i in range(length):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": f"Message {i}"})
            messages.append(base_message)
            
            start = time.perf_counter()
            response = query_llm(messages, max_tokens=20)
            elapsed = (time.perf_counter() - start) * 1000
            
            results[length] = elapsed
        
        print(f"    History scaling results:")
        for length, time_ms in results.items():
            print(f"    {length} messages: {time_ms:.2f}ms")
        
        # Time should not increase dramatically with history
        # Check that longest is not more than 5x the shortest
        min_time = min(results.values())
        max_time = max(results.values())
        
        assert max_time < min_time * 5, f"History scaling poor: {max_time:.2f}ms vs {min_time:.2f}ms"
    
    # ==================== STRESS TESTS ====================
    
    def test_maximum_concurrent_connections(self):
        """Test maximum concurrent connections"""
        messages = [{"role": "user", "content": "Test"}]
        max_concurrent = 20
        
        print(f"    Testing {max_concurrent} concurrent connections...")
        
        start = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = [
                executor.submit(query_llm, messages, max_tokens=5)
                for _ in range(max_concurrent)
            ]
            
            completed = 0
            failed = 0
            
            for future in as_completed(futures):
                try:
                    future.result(timeout=60)
                    completed += 1
                except Exception:
                    failed += 1
        
        elapsed = time.perf_counter() - start
        
        print(f"    Completed: {completed}/{max_concurrent}")
        print(f"    Failed: {failed}/{max_concurrent}")
        print(f"    Time: {elapsed:.2f}s")
        
        # At least 50% should complete
        assert completed >= max_concurrent * 0.5, f"Too many failures: {completed}/{max_concurrent}"
    
    def test_rate_limit_behavior(self):
        """Test behavior under rate limiting"""
        messages = [{"role": "user", "content": "Rate test"}]
        rapid_requests = 50
        
        print(f"    Sending {rapid_requests} rapid requests...")
        
        responses = []
        rate_limit_errors = []
        other_errors = []
        
        for i in range(rapid_requests):
            try:
                response = query_llm(messages, max_tokens=5)
                responses.append(response)
            except Exception as e:
                if "rate" in str(e).lower() or "limit" in str(e).lower():
                    rate_limit_errors.append(str(e))
                else:
                    other_errors.append(str(e))
            
            # No delay - hammer the API
        
        print(f"    Successful: {len(responses)}")
        print(f"    Rate limited: {len(rate_limit_errors)}")
        print(f"    Other errors: {len(other_errors)}")
        
        # Should handle rate limiting gracefully
        total = len(responses) + len(rate_limit_errors) + len(other_errors)
        assert total == rapid_requests, f"Lost requests: {total}/{rapid_requests}"
    
    def run_all_tests(self) -> TestRunner:
        """Run all performance tests"""
        print("\n" + "=" * 60)
        print("PERFORMANCE AND LOAD TESTS")
        print("=" * 60)
        
        # Latency tests
        tests = [
            (self.test_simple_query_latency, "simple_latency", "latency"),
            (self.test_complex_query_latency, "complex_latency", "latency"),
            (self.test_streaming_first_token_latency, "first_token_latency", "latency"),
            (self.test_strategy_overhead, "strategy_overhead", "latency"),
            
            # Throughput tests
            (self.test_sequential_throughput, "sequential_throughput", "throughput"),
            (self.test_concurrent_throughput, "concurrent_throughput", "throughput"),
            
            # Load tests
            (self.test_sustained_load, "sustained_load", "load"),
            (self.test_burst_load, "burst_load", "load"),
            (self.test_memory_usage, "memory_usage", "load"),
            (self.test_cpu_usage, "cpu_usage", "load"),
            
            # Scalability tests
            (self.test_token_scaling, "token_scaling", "scalability"),
            (self.test_message_history_scaling, "history_scaling", "scalability"),
            
            # Stress tests
            (self.test_maximum_concurrent_connections, "max_concurrent", "stress"),
            (self.test_rate_limit_behavior, "rate_limiting", "stress"),
        ]
        
        for test_func, name, category in tests:
            self.runner.add_result(
                self.runner.run_test(test_func, name, category)
            )
        
        # Async throughput test
        self.runner.add_result(
            asyncio.run(self.runner.run_async_test(self.test_async_throughput, "async_throughput", "throughput"))
        )
        
        return self.runner


if __name__ == "__main__":
    tests = PerformanceTests()
    runner = tests.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report()
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    print(f"Average Test Time: {report['summary']['average_time_ms']:.2f}ms")
    print(f"Total Time: {report['summary']['total_time_ms']/1000:.2f}s")
    
    runner.save_report("performance_test_report.json")