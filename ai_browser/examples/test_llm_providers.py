#!/usr/bin/env python3
"""Test script to verify LLM providers are working correctly"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cognition.llm import LLMManager
from dotenv import load_dotenv
import os

async def test_providers():
    """Test the configured LLM providers"""
    
    # Load environment variables
    load_dotenv()
    
    print("Testing LLM Provider Configuration")
    print("=" * 50)
    
    # Initialize LLM Manager
    llm_manager = LLMManager(auto_load=True)
    
    # List available providers
    providers = llm_manager.list_providers()
    print(f"\nAvailable providers: {providers}")
    
    if llm_manager.default_provider:
        print(f"Default provider: {llm_manager.default_provider}")
        
        # Get provider details
        provider = llm_manager.get_provider()
        print(f"Provider name: {provider.get_name()}")
        print(f"Model: {provider.get_model()}")
        print(f"Max context window: {provider.get_max_context_window()}")
    else:
        print("No default provider set")
        return
    
    # Test simple generation if API key is available
    if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("XAI_API_KEY"):
        print("\nTesting text generation...")
        try:
            prompt = "Say 'Hello, World!' in exactly 3 words."
            response = await llm_manager.generate(prompt, temperature=0.1)
            print(f"Prompt: {prompt}")
            print(f"Response: {response}")
            print("Text generation test: SUCCESS")
        except Exception as e:
            print(f"Text generation test: FAILED - {e}")
    else:
        print("\nNo API keys found. Skipping generation test.")
    
    # Show usage stats
    stats = llm_manager.get_usage_stats()
    print(f"\nUsage stats: {stats}")
    
    print("\n" + "=" * 50)
    print("LLM Provider Test Complete")

if __name__ == "__main__":
    asyncio.run(test_providers())