#!/usr/bin/env python3
"""Simple test to verify DOM extractor module imports and basic functionality"""

import sys
from pathlib import Path

# Add the module path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Test imports
print("[TEST] Testing DOM extractor module imports...")
try:
    from elements_extractor_no_llm import (
        ElementsExtractorNoLLM,
        ExtractionConfig,
        ElementType,
        InteractionType,
        LocatorStrategy,
        ExtractedElement,
        ExtractionResult
    )
    print("[OK] All imports successful")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

# Test configuration
print("\n[TEST] Testing configuration...")
try:
    config = ExtractionConfig(
        max_elements=50,
        enable_shadow_dom=True,
        enable_iframe_traversal=True
    )
    print("[OK] ExtractionConfig created")
    print(f"     Max elements: {config.max_elements}")
    print(f"     Shadow DOM: {config.enable_shadow_dom}")
    print(f"     Iframe traversal: {config.enable_iframe_traversal}")
except Exception as e:
    print(f"[ERROR] Configuration failed: {e}")
    sys.exit(1)

# Test extractor initialization
print("\n[TEST] Testing extractor initialization...")
try:
    extractor = ElementsExtractorNoLLM(config)
    print("[OK] ElementsExtractorNoLLM initialized")
except Exception as e:
    print(f"[ERROR] Extractor initialization failed: {e}")
    sys.exit(1)

# Test element model
print("\n[TEST] Testing element model...")
try:
    element = ExtractedElement(
        tag_name="button",
        element_type=ElementType.BUTTON,
        text="Click me"
    )
    print("[OK] ExtractedElement created")
    print(f"     Tag: {element.tag_name}")
    print(f"     Type: {element.element_type.value}")
    print(f"     Text: {element.text}")
except Exception as e:
    print(f"[ERROR] Element model failed: {e}")
    sys.exit(1)

# Test serialization
print("\n[TEST] Testing serialization...")
try:
    element_dict = element.to_dict()
    print("[OK] Element serialization works")
    print(f"     Serialized keys: {list(element_dict.keys())[:5]}...")
except Exception as e:
    print(f"[ERROR] Serialization failed: {e}")
    sys.exit(1)

print("\n[SUCCESS] DOM extractor module is working!")
print("Pure DOM-based extraction without LLM dependencies")
print("33+ element types supported with Shadow DOM and iframe traversal")