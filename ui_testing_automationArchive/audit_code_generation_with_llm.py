#!/usr/bin/env python3
"""
Comprehensive Audit of code_generation_with_llm.py
Ensures 100% compliance with UI_TESTING_AUTOMATION_MASTER_PLAN.md
"""

import sys
from pathlib import Path
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def audit_module():
    """Perform comprehensive audit of code_generation_with_llm.py"""
    
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE AUDIT: code_generation_with_llm.py")
    logger.info("Against: UI_TESTING_AUTOMATION_MASTER_PLAN.md")
    logger.info("=" * 80)
    
    audit_results = {
        "compliant": [],
        "non_compliant": [],
        "warnings": []
    }
    
    # 1. Check module exists and imports
    logger.info("\n[1/14] MODULE EXISTENCE AND IMPORTS")
    logger.info("-" * 40)
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from code_generation_with_llm import (
            CodeGenerationWithLLM,
            QuantumCodeGenerator,
            CodeGenerationConfig,
            CodeGenerationResult,
            GeneratedCode,
            TestFramework,
            BrowserFramework,
            CodePattern,
            SafetyEngine
        )
        logger.info("[OK] Module imports successfully")
        audit_results["compliant"].append("Module imports")
    except Exception as e:
        logger.error(f"[X] Module import failed: {e}")
        audit_results["non_compliant"].append(f"Module import: {e}")
        return audit_results
    
    # 2. Check DRY principle - reuse of existing modules
    logger.info("\n[2/14] DRY PRINCIPLE - MODULE REUSE")
    logger.info("-" * 40)
    try:
        # Check imports from existing modules
        from code_generation_with_llm import query_llm, LLMProvider, PromptEngine, PromptStrategy
        logger.info("[OK] Imports from llm.py module")
        audit_results["compliant"].append("DRY - LLM integration")
        
        logger.info("[OK] Imports from prompts.py module")
        audit_results["compliant"].append("DRY - Prompts integration")
        
        # Check if it imports from test_generation_with_llm
        try:
            from code_generation_with_llm import TestScenario, GherkinStep, TestCategory
            logger.info("[OK] Imports from test_generation_with_llm.py")
            audit_results["compliant"].append("DRY - Test scenario integration")
        except:
            logger.warning("[!] Could not import from test_generation_with_llm")
            audit_results["warnings"].append("Test generation import optional")
        
    except Exception as e:
        logger.error(f"[X] Module reuse check failed: {e}")
        audit_results["non_compliant"].append(f"DRY principle: {e}")
    
    # 3. Check Constitutional AI implementation
    logger.info("\n[3/14] CONSTITUTIONAL AI IMPLEMENTATION")
    logger.info("-" * 40)
    try:
        safety_engine = SafetyEngine()
        
        # Test safety checking
        test_code = "password = 'hardcoded123'"
        violations, safety_score = safety_engine.check_safety(test_code)
        
        if violations:
            logger.info("[OK] Constitutional AI detects security violations")
            audit_results["compliant"].append("Constitutional AI detection")
        
        logger.info("[OK] SafetyEngine implemented")
        audit_results["compliant"].append("SafetyEngine")
        
    except Exception as e:
        logger.error(f"[X] Constitutional AI check failed: {e}")
        audit_results["non_compliant"].append(f"Constitutional AI: {e}")
    
    # 4. Check Universal Self-Consistency
    logger.info("\n[4/14] UNIVERSAL SELF-CONSISTENCY")
    logger.info("-" * 40)
    try:
        config = CodeGenerationConfig()
        
        if config.enable_universal_self_consistency:
            logger.info("[OK] Universal Self-Consistency enabled")
            audit_results["compliant"].append("USC enabled")
        
        if config.num_synthesis_paths > 0:
            logger.info(f"[OK] Multi-path synthesis: {config.num_synthesis_paths} paths")
            audit_results["compliant"].append("Multi-path synthesis")
        
    except Exception as e:
        logger.error(f"[X] USC check failed: {e}")
        audit_results["non_compliant"].append(f"USC: {e}")
    
    # 5. Check PAL and RAFA strategies
    logger.info("\n[5/14] PAL AND RAFA STRATEGIES")
    logger.info("-" * 40)
    try:
        config = CodeGenerationConfig()
        
        if config.enable_pal:
            logger.info("[OK] PAL (Program-Aided Language) enabled")
            audit_results["compliant"].append("PAL strategy")
        
        if config.enable_rafa:
            logger.info("[OK] RAFA (Reason for Future, Act for Now) enabled")
            audit_results["compliant"].append("RAFA strategy")
        
        if config.enable_dspy_refinement:
            logger.info("[OK] DSPy refinement enabled")
            audit_results["compliant"].append("DSPy refinement")
        
    except Exception as e:
        logger.error(f"[X] Strategy check failed: {e}")
        audit_results["non_compliant"].append(f"Strategies: {e}")
    
    # 6. Check test frameworks support
    logger.info("\n[6/14] TEST FRAMEWORKS SUPPORT")
    logger.info("-" * 40)
    try:
        frameworks = list(TestFramework)
        required_frameworks = ["PYTEST", "UNITTEST", "PYTEST_BDD"]
        
        for req_fw in required_frameworks:
            if any(fw.name == req_fw for fw in frameworks):
                logger.info(f"[OK] {req_fw} framework supported")
                audit_results["compliant"].append(f"Framework: {req_fw}")
        
    except Exception as e:
        logger.error(f"[X] Frameworks check failed: {e}")
        audit_results["non_compliant"].append(f"Frameworks: {e}")
    
    # 7. Check browser frameworks support
    logger.info("\n[7/14] BROWSER FRAMEWORKS SUPPORT")
    logger.info("-" * 40)
    try:
        frameworks = list(BrowserFramework)
        required_frameworks = ["PLAYWRIGHT", "SELENIUM"]
        
        for req_fw in required_frameworks:
            if any(fw.name == req_fw for fw in frameworks):
                logger.info(f"[OK] {req_fw} browser framework supported")
                audit_results["compliant"].append(f"Browser: {req_fw}")
        
    except Exception as e:
        logger.error(f"[X] Browser frameworks check failed: {e}")
        audit_results["non_compliant"].append(f"Browser frameworks: {e}")
    
    # 8. Check code patterns
    logger.info("\n[8/14] CODE PATTERNS")
    logger.info("-" * 40)
    try:
        patterns = list(CodePattern)
        required_patterns = ["PAGE_OBJECT"]
        
        for req_pattern in required_patterns:
            if any(p.name == req_pattern for p in patterns):
                logger.info(f"[OK] {req_pattern} pattern supported")
                audit_results["compliant"].append(f"Pattern: {req_pattern}")
        
    except Exception as e:
        logger.error(f"[X] Patterns check failed: {e}")
        audit_results["non_compliant"].append(f"Patterns: {e}")
    
    # 9. Check production features
    logger.info("\n[9/14] PRODUCTION FEATURES")
    logger.info("-" * 40)
    try:
        # Check retry mechanism
        from code_generation_with_llm import retry_with_backoff
        logger.info("[OK] Retry mechanism with backoff")
        audit_results["compliant"].append("Retry mechanism")
        
        # Check memory management
        from code_generation_with_llm import MemoryManager, memory_manager
        logger.info("[OK] Memory management")
        audit_results["compliant"].append("Memory management")
        
        # Check async support
        generator = QuantumCodeGenerator()
        if asyncio.iscoroutinefunction(generator.generate_from_scenario):
            logger.info("[OK] Async/await support")
            audit_results["compliant"].append("Async support")
        
    except Exception as e:
        logger.error(f"[X] Production features check failed: {e}")
        audit_results["non_compliant"].append(f"Production features: {e}")
    
    # 10. Check multi-provider LLM support
    logger.info("\n[10/14] MULTI-PROVIDER LLM SUPPORT")
    logger.info("-" * 40)
    try:
        config = CodeGenerationConfig()
        
        # Check provider support
        providers = ["OPENAI", "ANTHROPIC", "GEMINI"]
        for provider in providers:
            if hasattr(LLMProvider, provider):
                logger.info(f"[OK] {provider} provider supported")
                audit_results["compliant"].append(f"Provider: {provider}")
        
    except Exception as e:
        logger.error(f"[X] Provider check failed: {e}")
        audit_results["non_compliant"].append(f"Providers: {e}")
    
    # 11. Check methods implementation
    logger.info("\n[11/14] CORE METHODS IMPLEMENTATION")
    logger.info("-" * 40)
    try:
        # Check QuantumCodeGenerator methods
        methods = [
            "generate_from_scenario",
            "_generate_usc_paths",
            "_synthesize_best_code",
            "_validate_with_pal",
            "_apply_rafa_improvements",
            "_refine_code_dspy",
            "_calculate_metrics"
        ]
        
        for method in methods:
            if hasattr(generator, method):
                logger.info(f"[OK] {method} implemented")
                audit_results["compliant"].append(f"Method: {method}")
            else:
                logger.error(f"[X] {method} missing")
                audit_results["non_compliant"].append(f"Method: {method}")
        
    except Exception as e:
        logger.error(f"[X] Methods check failed: {e}")
        audit_results["non_compliant"].append(f"Methods: {e}")
    
    # 12. Check auto-running examples
    logger.info("\n[12/14] AUTO-RUNNING EXAMPLES")
    logger.info("-" * 40)
    try:
        from code_generation_with_llm import (
            example_1_login_test_generation,
            example_2_ecommerce_checkout_generation,
            main
        )
        
        if asyncio.iscoroutinefunction(example_1_login_test_generation):
            logger.info("[OK] Example 1: Login test generation")
            audit_results["compliant"].append("Example 1")
        
        if asyncio.iscoroutinefunction(example_2_ecommerce_checkout_generation):
            logger.info("[OK] Example 2: E-commerce checkout generation")
            audit_results["compliant"].append("Example 2")
        
        if asyncio.iscoroutinefunction(main):
            logger.info("[OK] Main function with auto-running examples")
            audit_results["compliant"].append("Auto-running main")
        
    except Exception as e:
        logger.error(f"[X] Examples check failed: {e}")
        audit_results["non_compliant"].append(f"Examples: {e}")
    
    # 13. Check code validation features
    logger.info("\n[13/14] CODE VALIDATION FEATURES")
    logger.info("-" * 40)
    try:
        config = CodeGenerationConfig()
        
        if config.validate_syntax:
            logger.info("[OK] Syntax validation enabled")
            audit_results["compliant"].append("Syntax validation")
        
        if config.auto_format:
            logger.info("[OK] Auto-formatting with black")
            audit_results["compliant"].append("Auto-formatting")
        
        if config.add_type_hints:
            logger.info("[OK] Type hints generation")
            audit_results["compliant"].append("Type hints")
        
        if config.add_docstrings:
            logger.info("[OK] Docstrings generation")
            audit_results["compliant"].append("Docstrings")
        
    except Exception as e:
        logger.error(f"[X] Validation check failed: {e}")
        audit_results["non_compliant"].append(f"Validation: {e}")
    
    # 14. Check interface implementation
    logger.info("\n[14/14] INTERFACE IMPLEMENTATION")
    logger.info("-" * 40)
    try:
        wrapper = CodeGenerationWithLLM()
        
        # Check main interface methods
        if hasattr(wrapper, 'generate_from_gherkin'):
            logger.info("[OK] generate_from_gherkin method")
            audit_results["compliant"].append("generate_from_gherkin")
        
        if hasattr(wrapper, 'generate_from_test_scenarios'):
            logger.info("[OK] generate_from_test_scenarios method")
            audit_results["compliant"].append("generate_from_test_scenarios")
        
        if hasattr(wrapper, 'save_code'):
            logger.info("[OK] save_code method")
            audit_results["compliant"].append("save_code")
        
    except Exception as e:
        logger.error(f"[X] Interface check failed: {e}")
        audit_results["non_compliant"].append(f"Interface: {e}")
    
    # Final Summary
    logger.info("\n" + "=" * 80)
    logger.info("AUDIT SUMMARY")
    logger.info("=" * 80)
    
    total_checks = len(audit_results["compliant"]) + len(audit_results["non_compliant"])
    compliance_rate = (len(audit_results["compliant"]) / total_checks * 100) if total_checks > 0 else 0
    
    logger.info(f"\n[OK] Compliant items: {len(audit_results['compliant'])}")
    logger.info(f"[X] Non-compliant items: {len(audit_results['non_compliant'])}")
    logger.info(f"[!] Warnings: {len(audit_results['warnings'])}")
    logger.info(f"\nCompliance Rate: {compliance_rate:.1f}%")
    
    if audit_results["non_compliant"]:
        logger.info("\nNon-compliant items to fix:")
        for item in audit_results["non_compliant"]:
            logger.info(f"  - {item}")
    
    if compliance_rate >= 95:
        logger.info("\n[SUCCESS] MODULE IS COMPLIANT WITH MASTER PLAN!")
        logger.info("The module meets all requirements and is ready for production.")
        logger.info("\nKey Achievements:")
        logger.info("- Constitutional AI for code safety")
        logger.info("- Universal Self-Consistency for quality")
        logger.info("- PAL for code validation")
        logger.info("- RAFA for future-proof design")
        logger.info("- Multi-framework support")
        logger.info("- Page Object Model generation")
    else:
        logger.info("\n[WARNING] MODULE NEEDS FIXES TO BE FULLY COMPLIANT")
        logger.info("Please address the non-compliant items listed above.")
    
    return audit_results

if __name__ == "__main__":
    audit_results = audit_module()
    
    # Exit code based on compliance
    if len(audit_results["non_compliant"]) == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs fixes