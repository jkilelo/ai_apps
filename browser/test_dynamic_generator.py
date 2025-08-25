"""
Test the Dynamic Code Generator with Live Gemini LLM
====================================================
This script tests the dynamic code generator with actual Gemini-2.5-flash-lite
to ensure it generates real, executable code for any website.
"""

import asyncio
import json
from pathlib import Path
import sys
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from browser.dynamic_test_code_generator import (
    DynamicCodeGenConfig,
    DynamicTestCodeGenerator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_with_live_gemini():
    """Test the dynamic generator with live Gemini LLM."""
    
    print("\n" + "="*60)
    print("TESTING DYNAMIC CODE GENERATOR WITH LIVE GEMINI LLM")
    print("="*60)
    
    # Configure for faster testing
    config = DynamicCodeGenConfig(
        llm_provider="gemini",
        llm_model="gemini-2.5-flash-lite",
        llm_temperature=0.1,
        llm_max_retries=2,
        
        # Disable self-consistency for speed
        self_consistency_samples=1,
        
        # Enable key strategies only
        enable_pal=True,
        enable_chain_of_thought=True,
        enable_constitutional_ai=True,
        enable_reflexion=True,
        enable_few_shot=True,
        
        # Disable others for speed
        enable_tree_of_thoughts=False,
        enable_react=False,
        enable_meta_prompting=False,
        enable_scratchpad=False,
        enable_debate=False,
        enable_opro=False,
        enable_evolutionary=False,
        enable_reverse_engineering=False,
        enable_metacognitive=False,
        
        output_dir="test_gemini_output"
    )
    
    # Initialize generator
    generator = DynamicTestCodeGenerator(config)
    
    # Test files
    test_cases_file = "test_results_github/20250814_160251_github_com_tests.json"
    extraction_file = "test_results_github/20250814_160251_github_com_extraction.json"
    
    # Check if files exist
    if not Path(test_cases_file).exists():
        print(f"ERROR: Test cases file not found: {test_cases_file}")
        return False
    
    print(f"\nInput files:")
    print(f"  - Test cases: {test_cases_file}")
    print(f"  - Extraction: {extraction_file}")
    
    print(f"\nLLM Configuration:")
    print(f"  - Provider: {config.llm_provider}")
    print(f"  - Model: {config.llm_model}")
    print(f"  - Temperature: {config.llm_temperature}")
    
    print(f"\nEnabled Strategies:")
    strategies = []
    if config.enable_pal: strategies.append("PAL")
    if config.enable_chain_of_thought: strategies.append("Chain of Thought")
    if config.enable_constitutional_ai: strategies.append("Constitutional AI")
    if config.enable_reflexion: strategies.append("Reflexion")
    if config.enable_few_shot: strategies.append("Few-Shot")
    for s in strategies:
        print(f"  - {s}")
    
    print("\n" + "-"*60)
    print("Starting code generation with LIVE Gemini LLM...")
    print("-"*60 + "\n")
    
    try:
        # Generate code with live LLM
        results = await generator.generate_from_test_cases(
            test_cases_file,
            extraction_file
        )
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        
        print(f"Success: {results.get('success', False)}")
        print(f"LLM Calls Made: {results.get('llm_calls', 0)}")
        print(f"Files Generated: {len(results.get('generated_files', []))}")
        
        if results.get('errors'):
            print("\nErrors encountered:")
            for error in results['errors']:
                print(f"  - {error}")
        
        if results.get('generated_files'):
            print("\nGenerated files:")
            for file in results['generated_files']:
                print(f"  - {file}")
                # Check if file exists and has content
                if Path(file).exists():
                    size = Path(file).stat().st_size
                    print(f"    Size: {size} bytes")
        
        # Validate generated code
        if results.get('success'):
            print("\n" + "-"*60)
            print("VALIDATING GENERATED CODE")
            print("-"*60)
            
            # Check base_page.py
            base_page = Path(config.output_dir) / "pages" / "base_page.py"
            if base_page.exists():
                print(f"\n[OK] base_page.py exists ({base_page.stat().st_size} bytes)")
                
                # Try to compile it
                try:
                    with open(base_page, 'r', encoding='utf-8') as f:
                        code = f.read()
                    compile(code, str(base_page), 'exec')
                    print("  [OK] Syntax is valid")
                    
                    # Check for key methods
                    required_methods = [
                        'def __init__',
                        'def navigate_to',
                        'def click',
                        'def fill',
                        'def wait_for'
                    ]
                    for method in required_methods:
                        if method in code:
                            print(f"  [OK] Contains {method}")
                        else:
                            print(f"  [MISSING] {method}")
                            
                except SyntaxError as e:
                    print(f"  [ERROR] Syntax error: {e}")
            
            # Check for test files
            test_dir = Path(config.output_dir) / "tests"
            if test_dir.exists():
                test_files = list(test_dir.glob("test_*.py"))
                print(f"\n[OK] Generated {len(test_files)} test files")
                
                for test_file in test_files[:2]:  # Check first 2
                    print(f"\n  Checking {test_file.name}:")
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            code = f.read()
                        compile(code, str(test_file), 'exec')
                        print(f"    [OK] Syntax is valid")
                        
                        # Check for test methods
                        if 'def test_' in code:
                            print(f"    [OK] Contains test methods")
                        if 'import pytest' in code:
                            print(f"    [OK] Uses pytest")
                        if 'from pages.' in code or 'from pages import' in code:
                            print(f"    [OK] Imports page objects")
                            
                    except SyntaxError as e:
                        print(f"    [ERROR] Syntax error: {e}")
        
        return results.get('success', False)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    success = await test_with_live_gemini()
    
    print("\n" + "="*60)
    if success:
        print("SUCCESS: Dynamic code generation with Live Gemini LLM completed!")
        print("The framework successfully generated code using real LLM calls.")
    else:
        print("FAILED: Code generation encountered issues.")
        print("Check the logs above for details.")
    print("="*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)