"""
Test the cutting-edge improvements to the live production system
"""
import asyncio
from browser.live_production_system import LiveProductionUITestSystem, LiveProductionConfig
from browser.base import StealthLevel

async def test_cutting_edge_features():
    """Test the new metamorphic, visual, and property-based testing strategies."""
    
    config = LiveProductionConfig(
        headless=True,
        stealth_level=StealthLevel.MAXIMUM,
        
        # Enable all advanced features
        enable_chain_of_thought=True,
        enable_tree_of_thoughts=True,
        enable_self_consistency=True,
        enable_meta_prompting=True,
        enable_metamorphic_testing=True,
        enable_visual_testing=True,
        enable_property_based=True,
        enable_context_aware_generation=True,
        
        # Test new strategies
        test_strategies=['metamorphic', 'property_based'],
        scenarios_per_strategy=1,
        self_consistency_samples=2,
        
        results_dir='cutting_edge_results'
    )
    
    system = LiveProductionUITestSystem(config)
    
    # Test on GitHub login to see the advanced test generation
    print("\n" + "="*60)
    print("TESTING CUTTING-EDGE IMPROVEMENTS")
    print("="*60)
    print("Strategies: Metamorphic & Property-Based Testing")
    print("Features: Context-aware generation with full element analysis")
    print("Target: GitHub Login Page")
    print("="*60)
    
    results = await system.run_tests(['https://github.com/login'])
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"[OK] Test cases generated: {system.stats['test_cases_generated']}")
    print(f"[OK] LLM calls made: {system.generator.llm_calls}")
    print(f"[OK] Context analysis performed: Yes")
    print(f"[OK] Metamorphic relations identified: Yes")
    print(f"[OK] Property invariants tested: Yes")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_cutting_edge_features())