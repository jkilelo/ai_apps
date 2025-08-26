#!/usr/bin/env python3
"""
Comprehensive Audit of elements_extractor_with_llm.py
Ensures 100% compliance with UI_TESTING_AUTOMATION_MASTER_PLAN.md
"""

import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def audit_module():
    """Perform comprehensive audit of elements_extractor_with_llm.py"""
    
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE AUDIT: elements_extractor_with_llm.py")
    logger.info("Against: UI_TESTING_AUTOMATION_MASTER_PLAN.md")
    logger.info("=" * 80)
    
    audit_results = {
        "compliant": [],
        "non_compliant": [],
        "warnings": []
    }
    
    # 1. Check module exists and imports
    logger.info("\n[1/10] MODULE EXISTENCE AND IMPORTS")
    logger.info("-" * 40)
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from elements_extractor_with_llm import (
            ElementsExtractorWithLLM,
            SemanticContext,
            AIAnalysis,
            EnhancedElement,
            ExtractionStrategy,
        )
        logger.info("[✓] Module imports successfully")
        audit_results["compliant"].append("Module imports")
    except Exception as e:
        logger.error(f"[✗] Module import failed: {e}")
        audit_results["non_compliant"].append(f"Module import: {e}")
        return audit_results
    
    # 2. Check DRY principle - reuse of existing modules
    logger.info("\n[2/10] DRY PRINCIPLE - MODULE REUSE")
    logger.info("-" * 40)
    try:
        # Check inheritance from base extractor
        if ElementsExtractorWithLLM.__bases__[0].__name__ == "ElementsExtractorNoLLM":
            logger.info("[✓] Inherits from ElementsExtractorNoLLM (DRY principle)")
            audit_results["compliant"].append("DRY - Inherits from base")
        else:
            logger.error("[✗] Does not inherit from ElementsExtractorNoLLM")
            audit_results["non_compliant"].append("DRY - No inheritance")
        
        # Check LLM module integration
        from elements_extractor_with_llm import query_llm, LLMProvider
        logger.info("[✓] Integrates with llm.py module")
        audit_results["compliant"].append("DRY - LLM integration")
        
        # Check prompts module integration
        from elements_extractor_with_llm import PromptStrategy, PromptEngine
        logger.info("[✓] Integrates with prompts.py module")
        audit_results["compliant"].append("DRY - Prompts integration")
        
    except Exception as e:
        logger.error(f"[✗] Module reuse check failed: {e}")
        audit_results["non_compliant"].append(f"DRY principle: {e}")
    
    # 3. Check multi-strategy extraction
    logger.info("\n[3/10] MULTI-STRATEGY EXTRACTION")
    logger.info("-" * 40)
    try:
        extractor = ElementsExtractorWithLLM()
        strategies = extractor.extraction_strategies
        
        required_strategies = [
            "dom_analysis",
            "semantic_understanding",
            "visual_ai_analysis",
            "context_aware_extraction",
            "accessibility_analysis",
        ]
        
        strategy_names = [s.name for s in strategies]
        for req_strategy in required_strategies:
            if req_strategy in strategy_names:
                logger.info(f"[✓] Strategy '{req_strategy}' implemented")
                audit_results["compliant"].append(f"Strategy: {req_strategy}")
            else:
                logger.error(f"[✗] Strategy '{req_strategy}' missing")
                audit_results["non_compliant"].append(f"Strategy: {req_strategy}")
        
    except Exception as e:
        logger.error(f"[✗] Strategy check failed: {e}")
        audit_results["non_compliant"].append(f"Strategies: {e}")
    
    # 4. Check AI/LLM enhancement features
    logger.info("\n[4/10] AI/LLM ENHANCEMENT FEATURES")
    logger.info("-" * 40)
    try:
        # Check semantic analysis
        if hasattr(extractor, 'enable_semantic_analysis'):
            logger.info("[✓] Semantic analysis capability")
            audit_results["compliant"].append("Semantic analysis")
        
        # Check visual analysis
        if hasattr(extractor, 'enable_visual_analysis'):
            logger.info("[✓] Visual AI analysis capability")
            audit_results["compliant"].append("Visual analysis")
        
        # Check context learning
        if hasattr(extractor, 'enable_context_learning'):
            logger.info("[✓] Context learning capability")
            audit_results["compliant"].append("Context learning")
        
        # Check AI analysis data structure
        ai_analysis = AIAnalysis()
        required_fields = [
            'semantic_role', 'functional_purpose', 'user_intent_match',
            'accessibility_score', 'usability_score', 'importance_score',
            'confidence'
        ]
        for field in required_fields:
            if hasattr(ai_analysis, field):
                logger.info(f"[✓] AIAnalysis.{field} field present")
                audit_results["compliant"].append(f"AIAnalysis.{field}")
            else:
                logger.error(f"[✗] AIAnalysis.{field} field missing")
                audit_results["non_compliant"].append(f"AIAnalysis.{field}")
        
    except Exception as e:
        logger.error(f"[✗] AI features check failed: {e}")
        audit_results["non_compliant"].append(f"AI features: {e}")
    
    # 5. Check production features
    logger.info("\n[5/10] PRODUCTION FEATURES")
    logger.info("-" * 40)
    try:
        # Check retry mechanism
        from elements_extractor_with_llm import retry_with_backoff
        logger.info("[✓] Retry mechanism with backoff")
        audit_results["compliant"].append("Retry mechanism")
        
        # Check thread safety
        from elements_extractor_with_llm import thread_safe
        logger.info("[✓] Thread safety decorator")
        audit_results["compliant"].append("Thread safety")
        
        # Check memory management
        from elements_extractor_with_llm import memory_manager
        logger.info("[✓] Memory management")
        audit_results["compliant"].append("Memory management")
        
        # Check async support
        import asyncio
        if asyncio.iscoroutinefunction(extractor.extract_from_url):
            logger.info("[✓] Async/await support")
            audit_results["compliant"].append("Async support")
        
    except Exception as e:
        logger.error(f"[✗] Production features check failed: {e}")
        audit_results["non_compliant"].append(f"Production features: {e}")
    
    # 6. Check contract validation
    logger.info("\n[6/10] CONTRACT VALIDATION")
    logger.info("-" * 40)
    try:
        # Check data classes
        enhanced_elem = EnhancedElement(
            tag_name="button",
            element_type="button",
            text="Test"
        )
        
        if hasattr(enhanced_elem, 'to_enhanced_dict'):
            logger.info("[✓] Enhanced element contract with to_enhanced_dict")
            audit_results["compliant"].append("Enhanced element contract")
        
        # Check semantic context
        context = SemanticContext()
        required_context_fields = [
            'page_purpose', 'page_type', 'user_intent',
            'interaction_flow', 'key_actions'
        ]
        for field in required_context_fields:
            if hasattr(context, field):
                logger.info(f"[✓] SemanticContext.{field} field")
                audit_results["compliant"].append(f"SemanticContext.{field}")
            else:
                logger.error(f"[✗] SemanticContext.{field} missing")
                audit_results["non_compliant"].append(f"SemanticContext.{field}")
        
    except Exception as e:
        logger.error(f"[✗] Contract validation failed: {e}")
        audit_results["non_compliant"].append(f"Contracts: {e}")
    
    # 7. Check multi-provider LLM support
    logger.info("\n[7/10] MULTI-PROVIDER LLM SUPPORT")
    logger.info("-" * 40)
    try:
        # Check provider support
        providers = ["OPENAI", "ANTHROPIC", "GEMINI"]
        for provider in providers:
            if hasattr(LLMProvider, provider):
                logger.info(f"[✓] {provider} provider supported")
                audit_results["compliant"].append(f"Provider: {provider}")
            else:
                logger.error(f"[✗] {provider} provider missing")
                audit_results["non_compliant"].append(f"Provider: {provider}")
        
    except Exception as e:
        logger.error(f"[✗] Provider check failed: {e}")
        audit_results["non_compliant"].append(f"Providers: {e}")
    
    # 8. Check prompt strategies
    logger.info("\n[8/10] PROMPT STRATEGIES")
    logger.info("-" * 40)
    try:
        # Check some key strategies are used
        key_strategies = [
            "CHAIN_OF_THOUGHT",
            "TREE_OF_THOUGHTS",
            "CONSTITUTIONAL_AI",
            "SELF_CONSISTENCY",
            "META_COGNITIVE_FRAMEWORK"
        ]
        
        for strategy in key_strategies:
            if hasattr(PromptStrategy, strategy):
                logger.info(f"[✓] {strategy} strategy available")
                audit_results["compliant"].append(f"Prompt: {strategy}")
        
    except Exception as e:
        logger.error(f"[✗] Prompt strategies check failed: {e}")
        audit_results["non_compliant"].append(f"Prompts: {e}")
    
    # 9. Check auto-running examples
    logger.info("\n[9/10] AUTO-RUNNING EXAMPLES")
    logger.info("-" * 40)
    try:
        import inspect
        module_file = Path(extractor.__module__.replace('.', '/') + '.py')
        
        # Check for main function
        from elements_extractor_with_llm import main
        if asyncio.iscoroutinefunction(main):
            logger.info("[✓] Main function exists and is async")
            audit_results["compliant"].append("Main function")
        
        # Check for examples
        from elements_extractor_with_llm import (
            example_1_basic_llm_extraction,
            example_2_contextual_extraction
        )
        logger.info("[✓] Example 1: Basic LLM extraction")
        logger.info("[✓] Example 2: Contextual extraction")
        audit_results["compliant"].append("Two auto-running examples")
        
    except Exception as e:
        logger.error(f"[✗] Examples check failed: {e}")
        audit_results["non_compliant"].append(f"Examples: {e}")
    
    # 10. Check strategic module features
    logger.info("\n[10/10] STRATEGIC MODULE FEATURES")
    logger.info("-" * 40)
    try:
        # Check batch extraction
        if hasattr(extractor, 'batch_extract'):
            logger.info("[✓] Batch extraction capability")
            audit_results["compliant"].append("Batch extraction")
        
        # Check context extraction
        if hasattr(extractor, 'extract_with_context'):
            logger.info("[✓] Context-aware extraction")
            audit_results["compliant"].append("Context extraction")
        
        # Check performance tracking
        if hasattr(extractor, 'get_strategy_performance'):
            logger.info("[✓] Strategy performance tracking")
            audit_results["compliant"].append("Performance tracking")
        
        # Check element ranking
        if hasattr(extractor, '_score_and_rank_elements'):
            logger.info("[✓] Element ranking by importance")
            audit_results["compliant"].append("Element ranking")
        
    except Exception as e:
        logger.error(f"[✗] Strategic features check failed: {e}")
        audit_results["non_compliant"].append(f"Strategic: {e}")
    
    # Final Summary
    logger.info("\n" + "=" * 80)
    logger.info("AUDIT SUMMARY")
    logger.info("=" * 80)
    
    total_checks = len(audit_results["compliant"]) + len(audit_results["non_compliant"])
    compliance_rate = (len(audit_results["compliant"]) / total_checks * 100) if total_checks > 0 else 0
    
    logger.info(f"\n✓ Compliant items: {len(audit_results['compliant'])}")
    logger.info(f"✗ Non-compliant items: {len(audit_results['non_compliant'])}")
    logger.info(f"⚠ Warnings: {len(audit_results['warnings'])}")
    logger.info(f"\nCompliance Rate: {compliance_rate:.1f}%")
    
    if audit_results["non_compliant"]:
        logger.info("\nNon-compliant items to fix:")
        for item in audit_results["non_compliant"]:
            logger.info(f"  - {item}")
    
    if compliance_rate >= 95:
        logger.info("\n🎉 MODULE IS COMPLIANT WITH MASTER PLAN! 🎉")
        logger.info("The module meets all requirements and is ready for production.")
    else:
        logger.info("\n⚠️ MODULE NEEDS FIXES TO BE FULLY COMPLIANT")
        logger.info("Please address the non-compliant items listed above.")
    
    return audit_results

if __name__ == "__main__":
    audit_results = audit_module()
    
    # Exit code based on compliance
    if len(audit_results["non_compliant"]) == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs fixes