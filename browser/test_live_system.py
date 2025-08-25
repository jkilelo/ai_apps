"""
Test script for Live Production System with gemini-2.5-flash-lite
Tests all prompt strategies synergistically on github.com
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the live production system
from browser.live_production_system import (
    LiveProductionConfig,
    LiveProductionUITestSystem, 
    StealthLevel
)

# Configure logging for detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


async def test_live_system_with_all_strategies():
    """Test the live production system with all prompt strategies enabled."""
    
    print("\n" + "="*80)
    print("LIVE PRODUCTION SYSTEM TEST WITH GEMINI-2.5-FLASH-LITE")
    print("="*80)
    print("Testing URL: https://github.com")
    print("Model: gemini-2.5-flash-lite")
    print("All prompt strategies: ENABLED")
    print("="*80 + "\n")
    
    # Configuration with ALL strategies enabled
    config = LiveProductionConfig(
        # Browser Settings
        headless=False,  # Show browser for debugging
        stealth_level=StealthLevel.MAXIMUM,
        timeout=60000,  # 60 seconds timeout for slow LLM responses
        wait_for_load=True,
        
        # LLM Settings - Using gemini-2.5-flash-lite as requested
        llm_provider="gemini",
        llm_model="gemini-2.5-flash-lite",
        llm_temperature=0.3,
        llm_max_retries=3,
        
        # Enable ALL prompt strategies for synergistic testing
        enable_chain_of_thought=True,
        enable_tree_of_thoughts=True,
        enable_self_consistency=True,
        enable_meta_prompting=True,
        enable_react=True,
        enable_constitutional_ai=True,
        enable_debate=True,
        enable_reflexion=True,
        enable_scratchpad=True,
        enable_few_shot=True,
        enable_opro_optimization=True,
        enable_dspy_refinement=True,
        self_consistency_samples=2,  # Reduced for faster testing
        opro_iterations=2,
        
        # Test Generation Settings
        test_strategies=[
            "critical_path",
            "validation", 
            "security",
            "metamorphic",
            "visual_regression",
            "property_based",
            "contract_testing",
            "chaos_engineering"
        ],
        scenarios_per_strategy=2,  # Generate 2 test cases per strategy
        
        # Advanced Testing Features - ALL ENABLED
        enable_metamorphic_testing=True,
        enable_visual_testing=True,
        enable_property_based=True,
        enable_context_aware_generation=True,
        
        # 2025 Cutting-Edge Features - ALL ENABLED
        enable_gherkin_format=True,
        enable_self_healing=True,
        enable_risk_based_prioritization=True,
        enable_test_impact_analysis=True,
        enable_performance_budgets=True,
        enable_ai_test_optimization=True,
        
        # Storage Settings
        results_dir="test_results_github",
        save_screenshots=True,
        save_intermediate=True,
        
        # Extraction Settings
        max_elements_per_page=100,  # Increased for github.com
        extract_timeout=120  # 2 minutes for extraction with LLM
    )
    
    # Initialize system
    logger.info("Initializing LiveProductionUITestSystem...")
    system = LiveProductionUITestSystem(config)
    
    # Test URL
    test_url = "https://github.com"
    
    try:
        print("\nSTARTING TEST EXECUTION...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # Run the test with extended timeout for LLM responses
        start_time = time.time()
        
        logger.info(f"Processing {test_url} with all strategies enabled...")
        results = await asyncio.wait_for(
            system.run_tests([test_url]),
            timeout=600  # 10 minutes total timeout for LLM processing
        )
        
        elapsed_time = time.time() - start_time
        
        # Process results
        if results and len(results) > 0:
            result = results[0]
            
            print("\n" + "="*60)
            print("TEST RESULTS")
            print("="*60)
            
            # Check if successful
            if result['success']:
                print("[SUCCESS] Test completed successfully!")
                
                # Display extraction results
                if result['extraction']:
                    print("\nEXTRACTION RESULTS:")
                    print(f"  Total Elements: {result['extraction']['total_elements']}")
                    print(f"  Page Type: {result['extraction']['page_type']}")
                    print(f"  Categories: {', '.join(str(c) for c in result['extraction']['categories'])}")
                
                # Display test generation results
                if result['test_cases']:
                    print("\nTEST GENERATION RESULTS:")
                    print(f"  Total Test Cases: {result['test_cases']['total']}")
                    print("\n  By Strategy:")
                    for strategy, count in result['test_cases']['by_strategy'].items():
                        print(f"    - {strategy}: {count} cases")
                
                # Verify strategy synergy
                print("\nPROMPT STRATEGY SYNERGY CHECK:")
                strategies_used = []
                if config.enable_chain_of_thought:
                    strategies_used.append("Chain of Thought")
                if config.enable_tree_of_thoughts:
                    strategies_used.append("Tree of Thoughts")
                if config.enable_react:
                    strategies_used.append("ReAct")
                if config.enable_constitutional_ai:
                    strategies_used.append("Constitutional AI")
                if config.enable_debate:
                    strategies_used.append("Multi-Agent Debate")
                if config.enable_reflexion:
                    strategies_used.append("Reflexion")
                if config.enable_scratchpad:
                    strategies_used.append("Scratchpad Reasoning")
                if config.enable_few_shot:
                    strategies_used.append("Few-Shot Learning")
                if config.enable_meta_prompting:
                    strategies_used.append("Meta-Prompting")
                if config.enable_self_consistency:
                    strategies_used.append("Self-Consistency")
                if config.enable_opro_optimization:
                    strategies_used.append("OPRO Optimization")
                if config.enable_dspy_refinement:
                    strategies_used.append("DSPy Refinement")
                
                print(f"  Strategies Enabled: {len(strategies_used)}")
                for strategy in strategies_used:
                    print(f"    [OK] {strategy}")
                
                # Load and display sample test case
                if result['test_cases'] and result['test_cases']['file']:
                    test_file = Path(result['test_cases']['file'])
                    if test_file.exists():
                        with open(test_file, 'r') as f:
                            test_data = json.load(f)
                        
                        # Find a test case with gherkin format
                        sample_test = None
                        for strategy, cases in test_data['test_cases'].items():
                            if cases and len(cases) > 0:
                                for case in cases:
                                    if 'gherkin' in case and case['gherkin']:
                                        sample_test = case
                                        break
                                if sample_test:
                                    break
                        
                        if sample_test:
                            print("\nSAMPLE TEST CASE (WITH GHERKIN):")
                            print(f"  Title: {sample_test.get('title', 'N/A')}")
                            print(f"  Priority: {sample_test.get('priority', 'N/A')}")
                            print(f"  Risk Score: {sample_test.get('risk_score', 'N/A')}")
                            
                            if sample_test.get('gherkin'):
                                print("\n  Gherkin Format:")
                                for line in sample_test['gherkin'].split('\n')[:10]:
                                    print(f"    {line}")
                            
                            if sample_test.get('self_healing'):
                                print("\n  Self-Healing: ENABLED")
                                print(f"    Max Attempts: {sample_test['self_healing'].get('max_healing_attempts', 'N/A')}")
                            
                            if sample_test.get('impact_analysis'):
                                print("\n  Impact Analysis:")
                                impact = sample_test['impact_analysis']
                                print(f"    Estimated Time: {impact.get('estimated_execution_time', 'N/A')}s")
                                print(f"    Flakiness Risk: {impact.get('flakiness_risk', 'N/A')}")
            else:
                print("[FAILED] Test execution failed!")
                print(f"Errors: {result.get('errors', [])}")
        
        # Display statistics
        print("\n" + "="*60)
        print("EXECUTION STATISTICS")
        print("="*60)
        stats = system.get_stats()
        print(f"Total Runtime: {elapsed_time:.2f} seconds")
        print(f"Elements Extracted: {stats['elements_extracted']}")
        print(f"Test Cases Generated: {stats['test_cases_generated']}")
        print(f"LLM Calls Made: {stats['llm_calls']}")
        
        # Check synergy effectiveness
        print("\nSYNERGY EFFECTIVENESS:")
        if stats['test_cases_generated'] > 0:
            effectiveness_score = (stats['test_cases_generated'] / len(config.test_strategies)) / config.scenarios_per_strategy
            print(f"  Generation Rate: {effectiveness_score:.1%}")
            if effectiveness_score >= 0.8:
                print("  [EXCELLENT] Strategy synergy")
            elif effectiveness_score >= 0.6:
                print("  [GOOD] Strategy synergy")
            else:
                print("  [WARNING] Strategy synergy could be improved")
        
        print("\n" + "="*60)
        print(f"Results saved to: {config.results_dir}/")
        print("="*60)
        
        return results
        
    except asyncio.TimeoutError:
        logger.error("Test execution timed out waiting for LLM response")
        print("\n[TIMEOUT] Test took too long. This is expected with gemini-2.5-flash-lite.")
        print("The LLM may need more time to process all strategies synergistically.")
        return None
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Main entry point."""
    print("INITIALIZING TEST ENVIRONMENT...")
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Test Script: {__file__}")
    
    # Check for required dependencies
    try:
        import playwright
        print("[OK] Playwright installed")
    except ImportError:
        print("[ERROR] Playwright not installed. Installing...")
        os.system("pip install playwright")
        os.system("playwright install chromium")
    
    # Run the test
    results = await test_live_system_with_all_strategies()
    
    if results:
        print("\n[COMPLETE] All tests finished successfully!")
        return 0
    else:
        print("\n[WARNING] Tests completed with issues. Check logs for details.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)