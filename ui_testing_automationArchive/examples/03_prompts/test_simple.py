#!/usr/bin/env python3
"""Simple test to verify prompts module imports and basic functionality"""

import sys
from pathlib import Path

# Add the module path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Test imports
print("[TEST] Testing prompts module imports...")
try:
    from prompts import (
        PromptEngine,
        PromptStrategy,
        TaskType,
        ComplexityLevel,
        PromptRequest,
        PromptResponse
    )
    print("[OK] All imports successful")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

# Test strategy enumeration
print("\n[TEST] Testing strategy enumeration...")
try:
    strategies = list(PromptStrategy)
    print(f"[OK] Total strategies available: {len(strategies)}")
    print(f"     First 5 strategies: {[s.value for s in strategies[:5]]}")
except Exception as e:
    print(f"[ERROR] Strategy enumeration failed: {e}")
    sys.exit(1)

# Test engine initialization
print("\n[TEST] Testing engine initialization...")
try:
    engine = PromptEngine()
    print("[OK] PromptEngine initialized")
except Exception as e:
    print(f"[ERROR] Engine initialization failed: {e}")
    sys.exit(1)

# Test prompt request creation
print("\n[TEST] Testing prompt request creation...")
try:
    request = PromptRequest(
        task="Explain the benefits of unit testing",
        task_type=TaskType.ANALYTICAL,
        complexity=ComplexityLevel.MODERATE
    )
    print("[OK] PromptRequest created")
    print(f"     Task: {request.task[:50]}...")
    print(f"     Type: {request.task_type.value}")
    print(f"     Complexity: {request.complexity.value}")
except Exception as e:
    print(f"[ERROR] Request creation failed: {e}")
    sys.exit(1)

# Test basic prompt generation
print("\n[TEST] Testing basic prompt generation...")
try:
    response = engine.generate_prompt(request)
    print("[OK] Prompt generated successfully")
    print(f"     Strategy used: {response.strategy_used.value}")
    print(f"     Confidence: {response.confidence:.2f}")
    print(f"     Prompt length: {len(response.enhanced_prompt)} characters")
except Exception as e:
    print(f"[ERROR] Prompt generation failed: {e}")
    sys.exit(1)

print("\n[SUCCESS] Prompts module is working!")
print("21 research-backed strategies are available for use")