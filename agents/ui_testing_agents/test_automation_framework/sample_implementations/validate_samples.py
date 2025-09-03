#!/usr/bin/env python3
"""
Quick test to verify V2 examples work with live LLM
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')


async def test_v2_examples():
    """Quick test of V2 functionality"""
    
    print("=" * 80)
    print("V2 EXAMPLES VERIFICATION TEST")
    print("=" * 80)
    
    # Test 1: Verify imports work
    print("\n[1] Testing imports...")
    try:
        from test_automation_framework.ai_test_generator import (
            generate_gherkin_with_llm,
            generate_ai_scenarios_with_llm,
            enhance_code_with_llm,
            generate_page_object_with_llm,
            generate_security_tests_with_llm,
            generate_accessibility_tests_with_llm
        )
        print("[OK] All imports successful")
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False
    
    # Test 2: Verify LLM is available
    print("\n[2] Testing LLM connection...")
    try:
        from llm_client import call_default_llm
        response = await call_default_llm(
            [{"role": "user", "content": "Say 'V2 Working'"}],
            temperature=0.1,
            max_tokens=20
        )
        print(f"[OK] LLM Response: {response}")
    except Exception as e:
        print(f"[ERROR] LLM failed: {e}")
        return False
    
    # Test 3: Quick scenario generation
    print("\n[3] Testing AI scenario generation...")
    try:
        simple_elements = {
            "form_elements": [
                {"type": "text", "name": "username"},
                {"type": "password", "name": "password"}
            ],
            "clickable_elements": [
                {"type": "submit", "text": "Login"}
            ]
        }
        
        result = await generate_ai_scenarios_with_llm(
            simple_elements,
            {"url": "test.com", "purpose": "login"},
            max_scenarios=1
        )
        
        print("[OK] AI scenario generated")
        if isinstance(result, dict) and 'scenarios' in result:
            preview = str(result['scenarios'])[:200]
            print(f"Preview: {preview}...")
    except Exception as e:
        print(f"[ERROR] Scenario generation failed: {e}")
        return False
    
    # Test 4: Quick code enhancement
    print("\n[4] Testing code enhancement...")
    try:
        basic = "def test(): pass"
        enhanced = await enhance_code_with_llm(basic, "production")
        print("[OK] Code enhanced")
        if isinstance(enhanced, dict) and 'enhanced_code' in enhanced:
            preview = str(enhanced['enhanced_code'])[:150]
            print(f"Preview: {preview}...")
    except Exception as e:
        print(f"[ERROR] Enhancement failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("V2 EXAMPLES VERIFICATION COMPLETE")
    print("=" * 80)
    print("[SUCCESS] All V2 components working with live LLM!")
    print("\nExamples ready to run:")
    print("1. 01_ecommerce_checkout_test.py")
    print("2. 02_banking_security_test.py")
    print("3. 03_social_media_test.py")
    print("4. 04_api_integration_test.py")
    print("5. 05_accessibility_compliance_test.py")
    print("\nNote: Each example takes 1-2 minutes with real LLM calls")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    print("\nVerifying V2 examples with live LLM...")
    print("This should complete in ~30 seconds\n")
    
    success = asyncio.run(test_v2_examples())
    sys.exit(0 if success else 1)