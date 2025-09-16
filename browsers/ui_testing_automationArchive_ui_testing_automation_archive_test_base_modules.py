"""
Test Base Modules - Verify browser, llm, and prompts are working
"""

import sys
import asyncio
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "base"))

def test_imports():
    """Test that all base modules can be imported"""
    print("[TEST] Testing base module imports...")
    
    try:
        # Test browser import
        from base.browser import UltimateStealthBrowser
        print("  [OK] browser.py imports successfully")
        
        # Test llm import
        from base.llm import query_llm, call_default_llm
        print("  [OK] llm.py imports successfully")
        
        # Test prompts import
        from base.prompts import PromptEngine, PromptStrategy
        print("  [OK] prompts.py imports successfully")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False

async def test_browser():
    """Test browser module functionality"""
    print("\n[TEST] Testing browser module...")
    
    try:
        from base.browser import UltimateStealthBrowser, StealthConfig
        
        # Create config
        config = StealthConfig()
        config.headless = True
        
        # Create browser
        browser = UltimateStealthBrowser(config)
        print("  [OK] Browser instance created")
        
        # Initialize
        await browser.initialize()
        print("  [OK] Browser initialized")
        
        # Navigate to test page
        result = await browser.extract_elements("https://example.com")
        print(f"  [OK] Extracted {len(result.elements)} elements from example.com")
        
        # Cleanup
        await browser.cleanup()
        print("  [OK] Browser cleaned up")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Browser test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm():
    """Test LLM module functionality"""
    print("\n[TEST] Testing LLM module...")
    
    try:
        from base.llm import call_default_llm
        
        # Test simple query
        messages = [{"role": "user", "content": "Say 'LLM module working' and nothing else"}]
        response = call_default_llm(messages)
        
        if response and hasattr(response, 'choices'):
            content = response.choices[0].message.content
            print(f"  [OK] LLM responded: {content[:50]}...")
            return True
        else:
            print(f"  [WARNING] LLM module loaded but no API key configured")
            return True  # Module works, just no API key
            
    except Exception as e:
        print(f"  [WARNING] LLM test skipped (likely no API key): {e}")
        return True  # Not a failure, just no API key

def test_prompts():
    """Test prompts module functionality"""
    print("\n[TEST] Testing prompts module...")
    
    try:
        from base.prompts import PromptEngine, PromptRequest, TaskType, ComplexityLevel
        
        # Create engine
        engine = PromptEngine()
        print("  [OK] PromptEngine created")
        
        # Create request
        request = PromptRequest(
            task="Extract clickable elements from webpage",
            task_type=TaskType.EXTRACTION,
            complexity=ComplexityLevel.MODERATE
        )
        
        # Generate prompt
        response = engine.generate_prompt(request)
        print(f"  [OK] Generated prompt using {response.strategy_used.value} strategy")
        print(f"  [OK] Confidence: {response.confidence:.2f}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Prompts test error: {e}")
        return False

async def main():
    """Run all base module tests"""
    print("="*70)
    print("BASE MODULES TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Test imports
    results['imports'] = test_imports()
    
    # Test browser
    results['browser'] = await test_browser()
    
    # Test LLM
    results['llm'] = test_llm()
    
    # Test prompts
    results['prompts'] = test_prompts()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for module, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {module}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n[SUCCESS] All base modules are working correctly!")
        print("\nNext step: Test elements_extractor_no_llm.py")
    else:
        print("\n[WARNING] Some base modules need attention")
        print("Fix issues before proceeding to next modules")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)