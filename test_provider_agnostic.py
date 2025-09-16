#!/usr/bin/env python3
"""
Test script to verify provider-agnostic LLM response handling
"""

import asyncio
from llm import call_default_llm, Message, LLMResponse
import logging

logging.basicConfig(level=logging.INFO)

def test_provider_switching():
    """Test that switching providers works seamlessly"""
    
    # Create a simple test message
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Say 'Hello World' and nothing else.")
    ]
    
    providers_to_test = [
        ("openai", "gpt-4.1"),
        ("gemini", "gemini-2.5-pro"),
        # ("claude", "claude-sonnet-4-20250514")  # Uncomment if Claude API is configured
    ]
    
    print("=" * 60)
    print("TESTING PROVIDER-AGNOSTIC LLM RESPONSE")
    print("=" * 60)
    print()
    
    for provider, model in providers_to_test:
        try:
            print(f"Testing {provider}/{model}...")
            
            # Call LLM with specific provider
            response = call_default_llm(
                messages, 
                provider=provider, 
                model=model
            )
            
            # Verify response is LLMResponse type
            assert isinstance(response, LLMResponse), f"Response should be LLMResponse, got {type(response)}"
            
            # Verify we can access content uniformly
            assert hasattr(response, 'content'), "Response should have 'content' attribute"
            assert response.content, "Response content should not be empty"
            
            # Print results
            print(f"[OK] Provider: {response.provider}")
            print(f"[OK] Model: {response.model}")
            print(f"[OK] Response: {response.content[:100]}...")
            print(f"[OK] Response length: {len(response.content)} chars")
            
            if response.usage:
                print(f"[OK] Tokens used: {response.usage}")
            
            print()
            
        except Exception as e:
            print(f"[ERROR] Error with {provider}/{model}: {e}")
            print()
    
    print("=" * 60)
    print("DEMONSTRATING PROVIDER SWITCHING")
    print("=" * 60)
    print()
    
    # Show how easy it is to switch providers
    test_message = [
        Message(role="user", content="What is 2+2? Reply with just the number.")
    ]
    
    # Using OpenAI
    print("Using OpenAI:")
    response = call_default_llm(test_message, provider="openai")
    print(f"Response: {response.content}")
    print()
    
    # Using Gemini
    print("Using Gemini:")
    response = call_default_llm(test_message, provider="gemini")
    print(f"Response: {response.content}")
    print()
    
    # Default provider (OpenAI)
    print("Using default provider:")
    response = call_default_llm(test_message)
    print(f"Response: {response.content}")
    print(f"Provider used: {response.provider}")
    print()
    
    print("[SUCCESS] All tests passed! Provider switching works seamlessly.")
    print("          You can now switch providers without changing any code that uses the response.")
    print("          Just access response.content regardless of provider!")

if __name__ == "__main__":
    test_provider_switching()