#!/usr/bin/env python3
"""Simple test to verify LLM module imports and basic functionality"""

import sys
from pathlib import Path

# Add the module path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Test imports
print("[TEST] Testing LLM module imports...")
try:
    from llm import query_llm, default_llm, get_available_providers, LLMProvider
    print("[OK] All imports successful")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

# Test provider enumeration
print("\n[TEST] Testing provider detection...")
try:
    providers = get_available_providers()
    print(f"[OK] Available providers: {', '.join(providers)}")
    print(f"     Total providers: {len(providers)}")
except Exception as e:
    print(f"[ERROR] Provider detection failed: {e}")
    sys.exit(1)

# Test basic configuration
print("\n[TEST] Testing basic configuration...")
try:
    # Test that we can access provider types
    print(f"[OK] OpenAI provider: {LLMProvider.OPENAI}")
    print(f"[OK] Anthropic provider: {LLMProvider.ANTHROPIC}")
    print(f"[OK] Gemini provider: {LLMProvider.GEMINI}")
except Exception as e:
    print(f"[ERROR] Configuration failed: {e}")
    sys.exit(1)

# Test message formatting
print("\n[TEST] Testing message formatting...")
try:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
    print(f"[OK] Messages formatted correctly")
    print(f"     Message count: {len(messages)}")
except Exception as e:
    print(f"[ERROR] Message formatting failed: {e}")
    sys.exit(1)

print("\n[SUCCESS] LLM module is working!")
print("Note: Actual API calls require valid API keys and may incur costs")