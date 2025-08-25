#!/usr/bin/env python3
"""Simple test to verify browser module imports and basic functionality"""

import sys
from pathlib import Path

# Add the module path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Test imports
print("[TEST] Testing browser module imports...")
try:
    from browser import (
        UltimateStealthBrowser,
        StealthConfig,
        StealthLevel,
        ExtractionStrategy,
        ProfileType
    )
    print("[OK] All imports successful")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

# Test configuration
print("\n[TEST] Testing configuration...")
try:
    config = StealthConfig()
    config.level = StealthLevel.MAXIMUM
    config.headless = True
    print(f"[OK] Config created with level: {config.level.value}")
except Exception as e:
    print(f"[ERROR] Config failed: {e}")
    sys.exit(1)

# Test browser initialization (without actually launching)
print("\n[TEST] Testing browser initialization...")
try:
    browser = UltimateStealthBrowser(config)
    print("[OK] Browser object created")
    print(f"     Session ID: {browser.session_id}")
    print(f"     Config level: {browser.config.level.value}")
except Exception as e:
    print(f"[ERROR] Browser init failed: {e}")
    sys.exit(1)

print("\n[SUCCESS] Browser module is working!")
print("Note: Actual browser launch requires network access and may fail in testing")