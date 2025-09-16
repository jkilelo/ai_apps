#!/usr/bin/env python3
"""
Example showing how to use elements_extractor_with_llm.py with different LLM providers
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "ui_testing_framework_prod"))
sys.path.insert(0, str(Path(__file__).parent))

from llm import call_default_llm, Message

# Example 1: Using different providers with the same code
def demonstrate_provider_switching():
    """Show how easy it is to switch between providers"""
    
    messages = [
        Message(role="user", content="What is the capital of France? Reply in 5 words or less.")
    ]
    
    print("=" * 60)
    print("PROVIDER SWITCHING DEMONSTRATION")
    print("=" * 60)
    print()
    
    # Test with OpenAI (default)
    print("1. Using OpenAI (default):")
    response = call_default_llm(messages)
    print(f"   Response: {response.content}")
    print(f"   Provider: {response.provider}")
    print()
    
    # Test with Gemini
    print("2. Using Gemini:")
    response = call_default_llm(messages, provider="gemini")
    print(f"   Response: {response.content}")
    print(f"   Provider: {response.provider}")
    print()
    
    # Test with custom model
    print("3. Using OpenAI with specific model:")
    response = call_default_llm(messages, provider="openai", model="gpt-4o-mini")
    print(f"   Response: {response.content}")
    print(f"   Model: {response.model}")
    print()
    
    print("KEY BENEFITS:")
    print("- Single unified interface: response.content")
    print("- No code changes needed when switching providers")
    print("- Automatic handling of provider-specific response formats")
    print("- Easy provider/model configuration")
    print()

# Example 2: How to modify elements_extractor_with_llm.py to use different providers
def show_extractor_modification():
    """Show how to modify elements_extractor to use different providers"""
    
    print("=" * 60)
    print("HOW TO USE DIFFERENT PROVIDERS IN ELEMENTS_EXTRACTOR")
    print("=" * 60)
    print()
    
    print("To use a different provider in elements_extractor_with_llm.py:")
    print()
    print("1. Option A - Modify the call_default_llm calls directly:")
    print("   Change:")
    print("     response = call_default_llm(messages, strategy=strategy)")
    print("   To:")
    print("     response = call_default_llm(messages, strategy=strategy, provider='gemini')")
    print()
    
    print("2. Option B - Set default provider in llm.py:")
    print("   In call_default_llm function, change:")
    print("     provider = 'openai'  # default")
    print("   To:")
    print("     provider = 'gemini'  # or any other provider")
    print()
    
    print("3. Option C - Add provider parameter to ElementLLMAnalyzerV3:")
    print("   Add __init__ parameter:")
    print("     def __init__(self, batch_size: int = 10, provider: str = 'openai'):")
    print("         self.provider = provider")
    print("   Then use:")
    print("     response = call_default_llm(messages, provider=self.provider)")
    print()
    
    print("The response handling remains the same regardless of provider!")
    print("Always access: response.content")
    print()

if __name__ == "__main__":
    demonstrate_provider_switching()
    show_extractor_modification()