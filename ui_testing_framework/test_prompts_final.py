#!/usr/bin/env python3
"""Final test of prompts module"""

try:
    from prompts import MASTER_STRATEGIES, PromptEngine
    print(f"SUCCESS: Imported {len(MASTER_STRATEGIES)} strategies")
    
    # List strategies
    print("\nStrategies available:")
    for i, key in enumerate(MASTER_STRATEGIES.keys(), 1):
        print(f"  {i}. {key}")
    
    # Test PromptEngine
    engine = PromptEngine()
    print("\nPromptEngine initialized successfully")
    
    # Verify no filename field
    first_strategy = list(MASTER_STRATEGIES.values())[0]
    fields = [f for f in dir(first_strategy) if not f.startswith('_')]
    print(f"\nStrategy fields: {fields}")
    assert 'filename' not in fields, "filename field should be removed"
    print("✓ filename field successfully removed")
    
    print("\n✓ ALL TESTS PASSED!")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()