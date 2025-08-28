#!/usr/bin/env python3
"""Test script for unified LLM module"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the unified module
from llm import (
    query_llm,
    stream_llm,
    call_default_llm,
    Provider,
    StrategyType,
    ImageProcessor,
    LLMResponse,
)

def test_basic_query():
    """Test basic query functionality"""
    print("[TEST] Basic Query")
    print("-" * 60)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello Test' and nothing else."}
    ]
    
    try:
        # Test with default provider (Gemini)
        response = call_default_llm(messages)
        print(f"[OK] Default LLM response: {response.content[:50]}")
        print(f"     Provider: {response.provider}")
        print(f"     Model: {response.model}")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_with_strategy():
    """Test query with strategy"""
    print("\n[TEST] Query with Strategy")
    print("-" * 60)
    
    messages = [
        {"role": "user", "content": "What is 2 + 2?"}
    ]
    
    try:
        # Test with Chain of Thought strategy
        response = query_llm(
            messages,
            strategy=StrategyType.CHAIN_OF_THOUGHT.value,
            provider="gemini",
            model="gemini-2.0-flash"
        )
        print(f"[OK] Strategy response: {response.content[:100]}")
        print(f"     Strategy used: {response.strategy_used}")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_streaming():
    """Test streaming response"""
    print("\n[TEST] Streaming Response")
    print("-" * 60)
    
    messages = [
        {"role": "user", "content": "Count from 1 to 3."}
    ]
    
    try:
        print("Streaming: ", end="", flush=True)
        chunk_count = 0
        
        for chunk in stream_llm(messages, provider="gemini"):
            if chunk.content:
                print(".", end="", flush=True)
                chunk_count += 1
            if chunk.is_final:
                break
        
        print(f"\n[OK] Received {chunk_count} chunks")
        return True
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False

def test_image_processor():
    """Test image processing utilities"""
    print("\n[TEST] Image Processor")
    print("-" * 60)
    
    try:
        processor = ImageProcessor()
        
        # Test base64 encoding
        test_data = b"test_image_data"
        image_content = processor.encode_bytes(test_data, "image/png")
        
        print(f"[OK] Image encoding works")
        print(f"     MIME type: {image_content.mime_type}")
        print(f"     Data length: {len(image_content.data)} chars")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TESTING UNIFIED LLM MODULE")
    print("=" * 60)
    
    # Check environment
    import os
    print("\n[ENVIRONMENT CHECK]")
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Google": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    }
    
    for provider, key in api_keys.items():
        if key:
            print(f"[OK] {provider} API key found")
        else:
            print(f"[MISSING] {provider} API key not set")
    
    # Run tests
    results = []
    results.append(test_basic_query())
    results.append(test_with_strategy())
    results.append(test_streaming())
    results.append(test_image_processor())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {total - passed} tests failed")

if __name__ == "__main__":
    main()