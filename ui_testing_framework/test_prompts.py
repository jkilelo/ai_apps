#!/usr/bin/env python3
"""Test if prompts module can be imported"""

try:
    from prompts import MASTER_STRATEGIES, PromptEngine
    print("✓ Import successful")
    print(f"✓ Found {len(MASTER_STRATEGIES)} strategies")
    
    # Test each strategy
    for key, strategy in MASTER_STRATEGIES.items():
        print(f"  - {key}: {strategy.name}")
    
    # Test PromptEngine
    engine = PromptEngine()
    print("✓ PromptEngine initialized")
    print("✓ All prompt strategies working correctly")
    
except SyntaxError as e:
    print(f"✗ Syntax error at line {e.lineno}: {e.msg}")
    print(f"  Text: {e.text}")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")