#!/usr/bin/env python3
"""
Comprehensive test script for all UI Testing Automation modules
Tests basic functionality and imports for modules 1-8
"""

import sys
import asyncio
from pathlib import Path

# Add the module path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_module_1_stealth_browser():
    """Test Module 1: Stealth Browser"""
    print("\n[MODULE 1] Testing Stealth Browser...")
    try:
        from browser import UltimateStealthBrowser, StealthConfig, StealthLevel
        config = StealthConfig()
        config.level = StealthLevel.MAXIMUM
        browser = UltimateStealthBrowser(config)
        print("[OK] Stealth Browser module working")
        return True
    except Exception as e:
        print(f"[ERROR] Stealth Browser failed: {e}")
        return False

def test_module_2_llm():
    """Test Module 2: LLM Interface"""
    print("\n[MODULE 2] Testing LLM Interface...")
    try:
        from llm import query_llm, get_available_providers, LLMProvider
        providers = get_available_providers()
        print(f"[OK] LLM module working - {len(providers)} providers available")
        return True
    except Exception as e:
        print(f"[ERROR] LLM module failed: {e}")
        return False

def test_module_3_prompts():
    """Test Module 3: Prompt Strategies"""
    print("\n[MODULE 3] Testing Prompt Strategies...")
    try:
        from prompts import PromptEngine, PromptStrategy, TaskType, ComplexityLevel, PromptRequest
        engine = PromptEngine()
        strategies = list(PromptStrategy)
        print(f"[OK] Prompts module working - {len(strategies)} strategies available")
        return True
    except Exception as e:
        print(f"[ERROR] Prompts module failed: {e}")
        return False

def test_module_4_dom_extractor():
    """Test Module 4: DOM Extractor (No LLM)"""
    print("\n[MODULE 4] Testing DOM Extractor...")
    try:
        from elements_extractor_no_llm import ElementsExtractorNoLLM, ExtractionConfig, ElementType
        config = ExtractionConfig(max_elements=50)
        extractor = ElementsExtractorNoLLM(config)
        print("[OK] DOM Extractor module working")
        return True
    except Exception as e:
        print(f"[ERROR] DOM Extractor failed: {e}")
        return False

def test_module_5_ai_extractor():
    """Test Module 5: AI-Enhanced Extractor"""
    print("\n[MODULE 5] Testing AI-Enhanced Extractor...")
    try:
        from elements_extractor_with_llm import ElementsExtractorWithLLM, SemanticContext, AIAnalysis
        extractor = ElementsExtractorWithLLM()
        print("[OK] AI-Enhanced Extractor module working")
        return True
    except Exception as e:
        print(f"[ERROR] AI-Enhanced Extractor failed: {e}")
        return False

def test_module_6_test_generation():
    """Test Module 6: Test Generation with LLM"""
    print("\n[MODULE 6] Testing Test Generation...")
    try:
        from ui_testing_automation.test_generation_with_llm import TestGenerationWithLLM, TestScenario, TestCategory
        generator = TestGenerationWithLLM()
        print("[OK] Test Generation module working")
        return True
    except Exception as e:
        print(f"[ERROR] Test Generation failed: {e}")
        return False

def test_module_7_code_generation():
    """Test Module 7: Code Generation with LLM"""
    print("\n[MODULE 7] Testing Code Generation...")
    try:
        from code_generation_with_llm import CodeGenerationWithLLM, CodeGenerationResult
        generator = CodeGenerationWithLLM()
        print("[OK] Code Generation module working")
        return True
    except Exception as e:
        print(f"[ERROR] Code Generation failed: {e}")
        return False

def test_module_8_code_execution():
    """Test Module 8: Code Execution"""
    print("\n[MODULE 8] Testing Code Execution...")
    try:
        from code_execution import CodeExecutionEngine, CodeExecutionResult
        executor = CodeExecutionEngine()
        print("[OK] Code Execution module working")
        return True
    except Exception as e:
        print(f"[ERROR] Code Execution failed: {e}")
        return False

def main():
    """Run all module tests"""
    print("="*80)
    print("UI TESTING AUTOMATION FRAMEWORK - MODULE VERIFICATION")
    print("="*80)
    print("Testing all 8 modules for basic functionality...")
    
    results = []
    
    # Test all modules
    test_functions = [
        ("Stealth Browser", test_module_1_stealth_browser),
        ("LLM Interface", test_module_2_llm),
        ("Prompt Strategies", test_module_3_prompts),
        ("DOM Extractor", test_module_4_dom_extractor),
        ("AI Extractor", test_module_5_ai_extractor),
        ("Test Generation", test_module_6_test_generation),
        ("Code Generation", test_module_7_code_generation),
        ("Code Execution", test_module_8_code_execution)
    ]
    
    for name, test_func in test_functions:
        success = test_func()
        results.append((name, success))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "[OK] PASS" if success else "[ERROR] FAIL"
        print(f"{status:15} Module: {name}")
    
    print(f"\nTotal: {successful}/{total} modules working")
    print(f"Success rate: {successful/total*100:.1f}%")
    
    if successful == total:
        print("\n[SUCCESS] All modules are working correctly!")
        print("The UI Testing Automation Framework is ready for use.")
    else:
        print(f"\n[WARNING] {total - successful} modules have issues.")
        print("Please check the error messages above for details.")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)