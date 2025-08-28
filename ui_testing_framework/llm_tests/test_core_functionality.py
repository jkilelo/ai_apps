#!/usr/bin/env python3
"""
Core Functionality Tests
Tests basic LLM operations: query, streaming, async operations
QA Focus: Smoke tests, basic validation, API compliance
"""

import sys
import asyncio
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import (
    query_llm,
    stream_llm,
    aquery_llm,
    astream_llm,
    call_default_llm,
    Provider,
    LLMResponse,
    StreamChunk,
    Message,
    Role,
)
from test_config import (
    TestRunner,
    assert_response_valid,
    assert_streaming_valid,
    skip_if_no_api_key,
    measure_latency,
    measure_async_latency,
)


class CoreFunctionalityTests:
    """Test core LLM functionality"""
    
    def __init__(self):
        self.runner = TestRunner()
    
    # ==================== BASIC QUERY TESTS ====================
    
    def test_basic_query_default(self):
        """Test basic query with default settings"""
        messages = [
            {"role": "user", "content": "Reply with exactly: OK"}
        ]
        
        response = call_default_llm(messages)
        assert_response_valid(response)
        assert "OK" in response.content.upper() or "ok" in response.content.lower(), \
            f"Expected 'OK' in response, got: {response.content[:100]}"
    
    def test_query_with_system_message(self):
        """Test query with system message"""
        messages = [
            {"role": "system", "content": "You are a calculator. Only respond with numbers."},
            {"role": "user", "content": "What is 2 + 2?"}
        ]
        
        response = query_llm(messages)
        assert_response_valid(response)
        assert "4" in response.content, f"Expected '4' in response, got: {response.content}"
    
    def test_query_with_conversation_history(self):
        """Test multi-turn conversation"""
        messages = [
            {"role": "user", "content": "My name is TestBot. Remember it."},
            {"role": "assistant", "content": "I'll remember your name is TestBot."},
            {"role": "user", "content": "What is my name?"}
        ]
        
        response = query_llm(messages)
        assert_response_valid(response)
        assert "TestBot" in response.content or "testbot" in response.content.lower(), \
            f"Expected 'TestBot' in response, got: {response.content[:100]}"
    
    def test_query_with_temperature(self):
        """Test temperature parameter effect"""
        messages = [{"role": "user", "content": "Write a creative word"}]
        
        # Low temperature (deterministic)
        response1 = query_llm(messages, temperature=0.0)
        response2 = query_llm(messages, temperature=0.0)
        assert_response_valid(response1)
        assert_response_valid(response2)
        
        # High temperature (creative)
        response3 = query_llm(messages, temperature=1.5)
        assert_response_valid(response3)
        # Note: Can't assert different responses due to non-determinism
    
    def test_query_with_max_tokens(self):
        """Test max_tokens parameter"""
        messages = [{"role": "user", "content": "Count from 1 to 100"}]
        
        # Very limited tokens
        response = query_llm(messages, max_tokens=20)
        assert_response_valid(response)
        assert len(response.content) < 200, \
            f"Response should be short, got {len(response.content)} chars"
    
    # ==================== STREAMING TESTS ====================
    
    def test_basic_streaming(self):
        """Test basic streaming functionality"""
        messages = [{"role": "user", "content": "Count from 1 to 5 slowly"}]
        
        chunks = []
        for chunk in stream_llm(messages):
            chunks.append(chunk)
            if chunk.is_final:
                break
        
        assert_streaming_valid(chunks)
        
        # Reconstruct full response
        full_content = "".join(c.content for c in chunks if c.content)
        assert len(full_content) > 0, "No content in stream"
        assert any(str(i) in full_content for i in range(1, 6)), \
            f"Expected numbers 1-5 in stream, got: {full_content[:100]}"
    
    def test_streaming_with_early_termination(self):
        """Test early termination of streaming"""
        messages = [{"role": "user", "content": "Count from 1 to 1000"}]
        
        chunks = []
        for i, chunk in enumerate(stream_llm(messages)):
            chunks.append(chunk)
            if i >= 5:  # Stop after 5 chunks
                break
        
        assert len(chunks) == 6, f"Expected 6 chunks, got {len(chunks)}"
        assert all(isinstance(c, StreamChunk) for c in chunks)
    
    # ==================== ASYNC TESTS ====================
    
    async def test_async_query(self):
        """Test async query functionality"""
        messages = [{"role": "user", "content": "Say 'async works'"}]
        
        response = await aquery_llm(messages)
        assert_response_valid(response)
        assert "async" in response.content.lower() or "works" in response.content.lower(), \
            f"Expected 'async' or 'works' in response, got: {response.content[:100]}"
    
    async def test_async_streaming(self):
        """Test async streaming functionality"""
        messages = [{"role": "user", "content": "List 3 colors"}]
        
        chunks = []
        async for chunk in astream_llm(messages):
            chunks.append(chunk)
            if chunk.is_final:
                break
        
        assert_streaming_valid(chunks)
        full_content = "".join(c.content for c in chunks if c.content)
        assert len(full_content) > 0, "No content in async stream"
    
    async def test_concurrent_async_queries(self):
        """Test multiple concurrent async queries"""
        messages = [
            [{"role": "user", "content": "Say 'first'"}],
            [{"role": "user", "content": "Say 'second'"}],
            [{"role": "user", "content": "Say 'third'"}],
        ]
        
        # Run queries concurrently
        tasks = [aquery_llm(msg) for msg in messages]
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 3, f"Expected 3 responses, got {len(responses)}"
        for response in responses:
            assert_response_valid(response)
    
    # ==================== PROVIDER TESTS ====================
    
    @skip_if_no_api_key("gemini")
    def test_gemini_provider(self):
        """Test Gemini provider specifically"""
        messages = [{"role": "user", "content": "Say 'Gemini OK'"}]
        
        response = query_llm(messages, provider="gemini")
        assert_response_valid(response)
        assert response.provider == Provider.GEMINI
        assert "gemini" in response.model.lower()
    
    @skip_if_no_api_key("openai")
    def test_openai_provider(self):
        """Test OpenAI provider specifically"""
        messages = [{"role": "user", "content": "Say 'OpenAI OK'"}]
        
        response = query_llm(messages, provider="openai", model="gpt-3.5-turbo")
        assert_response_valid(response)
        assert response.provider == Provider.OPENAI
        assert "gpt" in response.model.lower()
    
    @skip_if_no_api_key("anthropic")
    def test_anthropic_provider(self):
        """Test Anthropic provider specifically"""
        messages = [{"role": "user", "content": "Say 'Claude OK'"}]
        
        response = query_llm(messages, provider="anthropic", model="claude-3-haiku-20240307")
        assert_response_valid(response)
        assert response.provider == Provider.ANTHROPIC
        assert "claude" in response.model.lower()
    
    # ==================== ERROR HANDLING TESTS ====================
    
    def test_empty_messages(self):
        """Test handling of empty messages"""
        try:
            response = query_llm([])
            # Some providers might handle empty messages
            assert_response_valid(response)
        except Exception as e:
            # Expected to fail
            assert "message" in str(e).lower() or "empty" in str(e).lower()
    
    def test_invalid_role(self):
        """Test handling of invalid message role"""
        messages = [{"role": "invalid_role", "content": "Test"}]
        
        try:
            response = query_llm(messages)
            # Should fail or handle gracefully
        except Exception as e:
            assert "role" in str(e).lower()
    
    def test_invalid_provider(self):
        """Test handling of invalid provider"""
        messages = [{"role": "user", "content": "Test"}]
        
        try:
            response = query_llm(messages, provider="invalid_provider")
            assert False, "Should have raised error for invalid provider"
        except Exception as e:
            assert "provider" in str(e).lower() or "unsupported" in str(e).lower()
    
    def test_network_timeout_handling(self):
        """Test timeout handling"""
        messages = [{"role": "user", "content": "Generate a very long response" * 100}]
        
        # This should handle timeout gracefully
        try:
            response = query_llm(messages, max_tokens=10)
            assert_response_valid(response)
        except Exception as e:
            # Timeout errors are acceptable
            assert "timeout" in str(e).lower() or "time" in str(e).lower()
    
    # ==================== PERFORMANCE TESTS ====================
    
    def test_response_latency(self):
        """Test response latency is within acceptable bounds"""
        messages = [{"role": "user", "content": "Say 'fast'"}]
        
        latency = measure_latency(lambda: query_llm(messages, max_tokens=10))
        
        # Should respond within 10 seconds for simple query
        assert latency < 10000, f"Response too slow: {latency:.2f}ms"
        print(f"    Latency: {latency:.2f}ms")
    
    def test_streaming_latency(self):
        """Test first token latency in streaming"""
        import time
        
        messages = [{"role": "user", "content": "Start immediately"}]
        
        first_chunk_time = None
        start = time.time()
        
        for chunk in stream_llm(messages, max_tokens=50):
            if chunk.content and not first_chunk_time:
                first_chunk_time = (time.time() - start) * 1000
                break
        
        assert first_chunk_time is not None, "No chunks received"
        assert first_chunk_time < 5000, f"First token too slow: {first_chunk_time:.2f}ms"
        print(f"    First token: {first_chunk_time:.2f}ms")
    
    def run_all_tests(self) -> TestRunner:
        """Run all core functionality tests"""
        print("\n" + "=" * 60)
        print("CORE FUNCTIONALITY TESTS")
        print("=" * 60)
        
        # Basic query tests
        self.runner.add_result(
            self.runner.run_test(self.test_basic_query_default, "basic_query_default", "core")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_query_with_system_message, "query_with_system", "core")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_query_with_conversation_history, "query_with_history", "core")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_query_with_temperature, "query_temperature", "core")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_query_with_max_tokens, "query_max_tokens", "core")
        )
        
        # Streaming tests
        self.runner.add_result(
            self.runner.run_test(self.test_basic_streaming, "basic_streaming", "streaming")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_streaming_with_early_termination, "streaming_early_stop", "streaming")
        )
        
        # Async tests
        self.runner.add_result(
            asyncio.run(self.runner.run_async_test(self.test_async_query, "async_query", "async"))
        )
        self.runner.add_result(
            asyncio.run(self.runner.run_async_test(self.test_async_streaming, "async_streaming", "async"))
        )
        self.runner.add_result(
            asyncio.run(self.runner.run_async_test(self.test_concurrent_async_queries, "concurrent_queries", "async"))
        )
        
        # Provider tests
        self.runner.add_result(
            self.runner.run_test(self.test_gemini_provider, "gemini_provider", "providers")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_openai_provider, "openai_provider", "providers")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_anthropic_provider, "anthropic_provider", "providers")
        )
        
        # Error handling tests
        self.runner.add_result(
            self.runner.run_test(self.test_empty_messages, "empty_messages", "error_handling")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_invalid_role, "invalid_role", "error_handling")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_invalid_provider, "invalid_provider", "error_handling")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_network_timeout_handling, "timeout_handling", "error_handling")
        )
        
        # Performance tests
        self.runner.add_result(
            self.runner.run_test(self.test_response_latency, "response_latency", "performance")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_streaming_latency, "streaming_latency", "performance")
        )
        
        return self.runner


if __name__ == "__main__":
    tests = CoreFunctionalityTests()
    runner = tests.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report()
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Errors: {report['summary']['errors']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    print(f"Average Time: {report['summary']['average_time_ms']:.2f}ms")
    
    runner.save_report("core_functionality_test_report.json")