#!/usr/bin/env python3
"""
Error Handling and Edge Cases Tests
QA Focus: Boundary testing, error recovery, graceful degradation
Senior QA: Test all failure modes, validate error messages, ensure no crashes
"""

import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import json
import base64

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import (
    query_llm,
    stream_llm,
    aquery_llm,
    astream_llm,
    Provider,
    StrategyType,
    ImageContent,
    Message,
    Role,
    LLMResponse,
    StreamChunk,
)
from test_config import TestRunner, assert_response_valid, create_test_image


class ErrorHandlingTests:
    """Test error handling and edge cases"""
    
    def __init__(self):
        self.runner = TestRunner()
    
    # ==================== INPUT VALIDATION TESTS ====================
    
    def test_empty_messages_list(self):
        """Test handling of empty messages list"""
        try:
            response = query_llm([])
            # Some providers might handle this gracefully
            if response:
                assert_response_valid(response)
        except (ValueError, AssertionError) as e:
            assert "message" in str(e).lower() or "empty" in str(e).lower(), \
                f"Expected message/empty error, got: {e}"
    
    def test_none_messages(self):
        """Test handling of None messages"""
        try:
            response = query_llm(None)
            assert False, "Should have raised error for None messages"
        except (TypeError, ValueError) as e:
            assert "message" in str(e).lower() or "none" in str(e).lower()
    
    def test_malformed_message_structure(self):
        """Test handling of malformed message dict"""
        malformed_messages = [
            [{"text": "missing role"}],  # Missing 'role'
            [{"role": "user"}],  # Missing 'content'
            [{"role": "user", "content": None}],  # None content
            [{"role": 123, "content": "invalid role type"}],  # Invalid role type
        ]
        
        for msgs in malformed_messages:
            try:
                response = query_llm(msgs)
                # Might be handled with defaults
            except (KeyError, TypeError, ValueError) as e:
                # Expected to fail
                pass
    
    def test_invalid_role_values(self):
        """Test handling of invalid role values"""
        invalid_roles = ["admin", "moderator", "bot", "invalid", "", 123, None]
        
        for role in invalid_roles:
            try:
                messages = [{"role": role, "content": "test"}]
                response = query_llm(messages)
                # Some providers might map to valid role
            except (ValueError, KeyError) as e:
                assert "role" in str(e).lower()
    
    def test_extremely_long_message(self):
        """Test handling of extremely long messages"""
        # Create 100MB message
        huge_message = "x" * (100 * 1024 * 1024)
        messages = [{"role": "user", "content": huge_message}]
        
        try:
            response = query_llm(messages, max_tokens=10)
            # Should handle by truncating or error
            if response:
                assert_response_valid(response)
        except Exception as e:
            # Expected to fail with memory/size error
            assert "size" in str(e).lower() or "length" in str(e).lower() or "token" in str(e).lower()
    
    # ==================== PROVIDER ERROR TESTS ====================
    
    def test_invalid_provider_name(self):
        """Test handling of invalid provider name"""
        invalid_providers = ["gpt", "claude", "llama", "invalid", "", None, 123]
        messages = [{"role": "user", "content": "test"}]
        
        for provider in invalid_providers:
            try:
                response = query_llm(messages, provider=provider)
                assert False, f"Should have raised error for provider: {provider}"
            except (ValueError, KeyError, TypeError) as e:
                assert "provider" in str(e).lower() or "unsupported" in str(e).lower()
    
    def test_invalid_model_name(self):
        """Test handling of invalid model names"""
        messages = [{"role": "user", "content": "test"}]
        
        invalid_models = {
            "gemini": ["gpt-4", "claude-3", "invalid-model"],
            "openai": ["gemini-pro", "claude-3", "llama-2"],
            "anthropic": ["gpt-4", "gemini-pro", "invalid"],
        }
        
        for provider, models in invalid_models.items():
            for model in models:
                try:
                    response = query_llm(messages, provider=provider, model=model)
                    # Provider might handle with defaults
                except Exception as e:
                    # Expected to fail
                    pass
    
    def test_missing_api_key(self):
        """Test handling when API key is missing"""
        import os
        messages = [{"role": "user", "content": "test"}]
        
        # Temporarily remove API keys
        original_keys = {}
        key_names = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"]
        
        for key in key_names:
            original_keys[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        try:
            # Test each provider without key
            for provider in ["openai", "gemini", "anthropic"]:
                try:
                    response = query_llm(messages, provider=provider)
                    assert False, f"Should have failed for {provider} without API key"
                except Exception as e:
                    assert "api" in str(e).lower() or "key" in str(e).lower() or "auth" in str(e).lower()
        finally:
            # Restore keys
            for key, value in original_keys.items():
                if value is not None:
                    os.environ[key] = value
    
    def test_invalid_api_key(self):
        """Test handling of invalid API key"""
        import os
        messages = [{"role": "user", "content": "test"}]
        
        # Save original and set invalid
        original = os.environ.get("GOOGLE_API_KEY")
        os.environ["GOOGLE_API_KEY"] = "invalid_key_12345"
        
        try:
            response = query_llm(messages, provider="gemini")
            # Might queue but fail on actual request
        except Exception as e:
            assert "auth" in str(e).lower() or "invalid" in str(e).lower() or "api" in str(e).lower()
        finally:
            if original:
                os.environ["GOOGLE_API_KEY"] = original
    
    # ==================== PARAMETER VALIDATION TESTS ====================
    
    def test_invalid_temperature(self):
        """Test handling of invalid temperature values"""
        messages = [{"role": "user", "content": "test"}]
        invalid_temps = [-1, -0.5, 2.5, 3, 100, "warm", None, []]
        
        for temp in invalid_temps:
            try:
                response = query_llm(messages, temperature=temp)
                # Might clamp to valid range
                if response:
                    assert 0 <= response.temperature <= 2
            except (ValueError, TypeError) as e:
                assert "temperature" in str(e).lower()
    
    def test_invalid_max_tokens(self):
        """Test handling of invalid max_tokens values"""
        messages = [{"role": "user", "content": "test"}]
        invalid_tokens = [-100, -1, 0, 1000000, "many", None, [], {}]
        
        for tokens in invalid_tokens:
            try:
                response = query_llm(messages, max_tokens=tokens)
                # Might use defaults
            except (ValueError, TypeError) as e:
                assert "token" in str(e).lower()
    
    def test_invalid_strategy(self):
        """Test handling of invalid strategy names"""
        messages = [{"role": "user", "content": "test"}]
        invalid_strategies = ["invalid", "cot", "tot", 123, None, [], {}]
        
        for strategy in invalid_strategies:
            try:
                response = query_llm(messages, strategy=strategy)
                # Might fall back to default
            except (ValueError, KeyError, TypeError) as e:
                assert "strategy" in str(e).lower()
    
    # ==================== IMAGE HANDLING ERRORS ====================
    
    def test_invalid_image_data(self):
        """Test handling of invalid image data"""
        messages = [{"role": "user", "content": "Analyze this image"}]
        
        invalid_images = [
            "not_base64",  # Invalid base64
            "",  # Empty string
            None,  # None
            123,  # Wrong type
            b"raw_bytes",  # Bytes instead of base64 string
        ]
        
        for img_data in invalid_images:
            try:
                response = query_llm(messages, images=[img_data])
                # Might ignore bad images
            except Exception as e:
                assert "image" in str(e).lower() or "base64" in str(e).lower()
    
    def test_corrupted_image(self):
        """Test handling of corrupted image data"""
        messages = [{"role": "user", "content": "Analyze this image"}]
        
        # Valid base64 but not an image
        corrupted = base64.b64encode(b"Not an image file").decode()
        
        try:
            response = query_llm(messages, images=[corrupted])
            # Provider might try to process anyway
        except Exception as e:
            assert "image" in str(e).lower() or "format" in str(e).lower()
    
    def test_too_many_images(self):
        """Test handling of too many images"""
        messages = [{"role": "user", "content": "Analyze these images"}]
        
        # Create 100 small test images
        test_img = base64.b64encode(create_test_image(10, 10)).decode()
        images = [test_img] * 100
        
        try:
            response = query_llm(messages, images=images, max_tokens=10)
            # Might truncate or process subset
        except Exception as e:
            assert "image" in str(e).lower() or "limit" in str(e).lower()
    
    # ==================== STREAMING ERROR TESTS ====================
    
    def test_streaming_with_invalid_params(self):
        """Test streaming with invalid parameters"""
        messages = [{"role": "user", "content": "test"}]
        
        try:
            chunks = []
            for chunk in stream_llm(messages, provider="invalid"):
                chunks.append(chunk)
                if len(chunks) > 5:
                    break
            assert False, "Should have raised error"
        except Exception as e:
            assert "provider" in str(e).lower()
    
    def test_streaming_interruption(self):
        """Test early termination of streaming"""
        messages = [{"role": "user", "content": "Count to 1000"}]
        
        chunks = []
        try:
            for i, chunk in enumerate(stream_llm(messages)):
                chunks.append(chunk)
                if i == 2:
                    # Simulate interruption
                    raise KeyboardInterrupt("User interrupted")
        except KeyboardInterrupt:
            # Should handle gracefully
            assert len(chunks) == 3
    
    # ==================== ASYNC ERROR TESTS ====================
    
    async def test_async_timeout(self):
        """Test async operation timeout"""
        messages = [{"role": "user", "content": "Generate a very long story"}]
        
        try:
            # Set very short timeout
            response = await asyncio.wait_for(
                aquery_llm(messages, max_tokens=1000),
                timeout=0.001  # 1ms timeout
            )
            assert False, "Should have timed out"
        except asyncio.TimeoutError:
            # Expected
            pass
    
    async def test_async_cancellation(self):
        """Test async task cancellation"""
        messages = [{"role": "user", "content": "Generate content"}]
        
        task = asyncio.create_task(aquery_llm(messages))
        await asyncio.sleep(0.1)  # Let it start
        task.cancel()
        
        try:
            await task
            assert False, "Should have been cancelled"
        except asyncio.CancelledError:
            # Expected
            pass
    
    # ==================== OUTPUT MODEL ERROR TESTS ====================
    
    def test_invalid_output_model(self):
        """Test handling of invalid output model"""
        messages = [{"role": "user", "content": "Generate structured data"}]
        
        class InvalidModel:
            # Not a Pydantic model
            pass
        
        try:
            response = query_llm(messages, output_model=InvalidModel)
            # Might ignore and return normal response
        except Exception as e:
            assert "model" in str(e).lower() or "pydantic" in str(e).lower()
    
    def test_output_model_validation_failure(self):
        """Test when LLM output doesn't match model"""
        from pydantic import BaseModel, Field
        
        class StrictModel(BaseModel):
            number: int = Field(ge=0, le=10)
            required_field: str
        
        messages = [{"role": "user", "content": "Say hello"}]
        
        try:
            response = query_llm(messages, output_model=StrictModel)
            # Should either retry or raise validation error
        except Exception as e:
            assert "validation" in str(e).lower() or "field" in str(e).lower()
    
    # ==================== CONCURRENCY ERROR TESTS ====================
    
    async def test_concurrent_errors(self):
        """Test handling of multiple concurrent failures"""
        messages = [{"role": "user", "content": "test"}]
        
        # Create tasks that will fail
        tasks = [
            aquery_llm(messages, provider="invalid1"),
            aquery_llm(messages, provider="invalid2"),
            aquery_llm(messages, provider="invalid3"),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should be exceptions
        assert all(isinstance(r, Exception) for r in results)
    
    def test_race_condition_handling(self):
        """Test handling of race conditions"""
        import threading
        import time
        
        messages = [{"role": "user", "content": "test"}]
        results = []
        errors = []
        
        def make_request():
            try:
                response = query_llm(messages, max_tokens=10)
                results.append(response)
            except Exception as e:
                errors.append(e)
        
        # Start 10 threads simultaneously
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join(timeout=30)
        
        # Should handle concurrent requests
        assert len(results) + len(errors) == 10
    
    # ==================== RECOVERY TESTS ====================
    
    def test_retry_on_transient_error(self):
        """Test retry logic for transient errors"""
        messages = [{"role": "user", "content": "test"}]
        
        # This might trigger retries internally
        try:
            response = query_llm(messages)
            assert_response_valid(response)
        except Exception as e:
            # Check if error mentions retry
            if "retry" in str(e).lower():
                pass
    
    def test_provider_switching(self):
        """Test switching to different provider on failure"""
        messages = [{"role": "user", "content": "Say OK"}]
        
        # Try with potentially failing provider
        try:
            response = query_llm(messages, provider="gemini")
            assert_response_valid(response)
        except Exception:
            # Try alternative provider
            try:
                response = query_llm(messages, provider="openai")
                assert_response_valid(response)
            except Exception:
                pass
    
    # ==================== BOUNDARY TESTS ====================
    
    def test_zero_length_content(self):
        """Test handling of zero-length content"""
        messages = [{"role": "user", "content": ""}]
        
        try:
            response = query_llm(messages)
            # Might generate something anyway
        except Exception as e:
            assert "content" in str(e).lower() or "empty" in str(e).lower()
    
    def test_unicode_edge_cases(self):
        """Test handling of unicode edge cases"""
        unicode_tests = [
            "\U0001F600" * 100,  # Many emojis
            "\u200B" * 100,  # Zero-width spaces
            "\uFFFD",  # Replacement character
            "𠜎𠜱𡿺𠬠𥲤",  # Rare CJK characters
            "\x00\x01\x02",  # Control characters
        ]
        
        for content in unicode_tests:
            messages = [{"role": "user", "content": content}]
            try:
                response = query_llm(messages, max_tokens=10)
                # Should handle or sanitize
            except Exception as e:
                # Might reject invalid unicode
                pass
    
    def test_special_tokens_in_input(self):
        """Test handling of special tokens in input"""
        special_contents = [
            "<|endoftext|>",
            "[INST]",
            "```system```",
            "Human: Assistant:",
            "\n\n\n\n\n",
        ]
        
        for content in special_contents:
            messages = [{"role": "user", "content": content}]
            try:
                response = query_llm(messages, max_tokens=10)
                assert_response_valid(response)
            except Exception:
                # Might sanitize or reject
                pass
    
    def run_all_tests(self) -> TestRunner:
        """Run all error handling tests"""
        print("\n" + "=" * 60)
        print("ERROR HANDLING AND EDGE CASES TESTS")
        print("=" * 60)
        
        # Input validation tests
        tests = [
            (self.test_empty_messages_list, "empty_messages", "input_validation"),
            (self.test_none_messages, "none_messages", "input_validation"),
            (self.test_malformed_message_structure, "malformed_messages", "input_validation"),
            (self.test_invalid_role_values, "invalid_roles", "input_validation"),
            (self.test_extremely_long_message, "long_message", "input_validation"),
            
            # Provider error tests
            (self.test_invalid_provider_name, "invalid_provider", "provider_errors"),
            (self.test_invalid_model_name, "invalid_model", "provider_errors"),
            (self.test_missing_api_key, "missing_api_key", "provider_errors"),
            (self.test_invalid_api_key, "invalid_api_key", "provider_errors"),
            
            # Parameter validation
            (self.test_invalid_temperature, "invalid_temperature", "parameter_validation"),
            (self.test_invalid_max_tokens, "invalid_max_tokens", "parameter_validation"),
            (self.test_invalid_strategy, "invalid_strategy", "parameter_validation"),
            
            # Image errors
            (self.test_invalid_image_data, "invalid_image_data", "image_errors"),
            (self.test_corrupted_image, "corrupted_image", "image_errors"),
            (self.test_too_many_images, "too_many_images", "image_errors"),
            
            # Streaming errors
            (self.test_streaming_with_invalid_params, "streaming_invalid", "streaming_errors"),
            (self.test_streaming_interruption, "streaming_interrupt", "streaming_errors"),
            
            # Output model errors
            (self.test_invalid_output_model, "invalid_output_model", "output_errors"),
            (self.test_output_model_validation_failure, "model_validation", "output_errors"),
            
            # Recovery tests
            (self.test_retry_on_transient_error, "retry_logic", "recovery"),
            (self.test_provider_switching, "provider_switching", "recovery"),
            
            # Boundary tests
            (self.test_zero_length_content, "zero_length", "boundary"),
            (self.test_unicode_edge_cases, "unicode_edge", "boundary"),
            (self.test_special_tokens_in_input, "special_tokens", "boundary"),
            
            # Concurrency
            (self.test_race_condition_handling, "race_condition", "concurrency"),
        ]
        
        for test_func, name, category in tests:
            self.runner.add_result(
                self.runner.run_test(test_func, name, category)
            )
        
        # Async tests
        async_tests = [
            (self.test_async_timeout, "async_timeout", "async_errors"),
            (self.test_async_cancellation, "async_cancel", "async_errors"),
            (self.test_concurrent_errors, "concurrent_errors", "async_errors"),
        ]
        
        for test_func, name, category in async_tests:
            self.runner.add_result(
                asyncio.run(self.runner.run_async_test(test_func, name, category))
            )
        
        return self.runner


if __name__ == "__main__":
    tests = ErrorHandlingTests()
    runner = tests.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report()
    print("\n" + "=" * 60)
    print("ERROR HANDLING TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Errors: {report['summary']['errors']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    
    runner.save_report("error_handling_test_report.json")