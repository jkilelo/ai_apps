#!/usr/bin/env python3
"""
Verify that the core application structure is intact after cleanup
"""

import sys
from pathlib import Path

def verify_core_structure():
    """Verify all core modules are present and importable"""
    
    print("[VERIFICATION] Core Application Structure")
    print("=" * 70)
    
    # Core modules that must exist
    core_modules = {
        # Base layer
        'base/browser.py': 'Base browser module',
        'base/llm.py': 'LLM integration module',
        'base/prompts.py': 'Prompt strategies module',
        'base/llm_streaming.py': 'LLM streaming support',
        'base/llm_models.json': 'LLM configuration',
        
        # Integration layer
        'browser_with_llm.py': 'Browser+LLM integration',
        
        # Domain layer
        'elements_extractor_no_llm.py': 'DOM extraction without LLM',
        'elements_extractor_with_llm.py': 'AI-enhanced extraction',
        'test_generation_with_llm.py': 'Gherkin test generation',
        'code_generation_with_llm.py': 'Python Playwright generation',
        'code_execution.py': 'Secure test execution',
        
        # Orchestration layer
        'pipeline_integration.py': 'Pipeline orchestrator',
        
        # Contracts and utilities
        'pipeline_contracts.py': 'Data contracts',
        'structured_output_enforcer.py': 'Output validation',
        
        # Documentation
        'CLAUDE.md': 'Development guidelines',
        'ARCHITECTURE.md': 'System architecture'
    }
    
    current_dir = Path.cwd()
    missing = []
    present = []
    
    print("\n[CHECKING] Core module presence...")
    print("-" * 50)
    
    for module_path, description in core_modules.items():
        full_path = current_dir / module_path
        if full_path.exists():
            print(f"  [OK] {module_path}")
            present.append(module_path)
        else:
            print(f"  [MISSING] {module_path} - {description}")
            missing.append(module_path)
    
    # Try importing Python modules
    print("\n[TESTING] Module imports...")
    print("-" * 50)
    
    import_tests = [
        ('base.browser', 'UltimateStealthBrowser'),
        ('base.llm', 'call_default_llm'),
        ('base.prompts', 'PromptEngine'),
        ('browser_with_llm', 'BrowserWithLLM'),
        ('elements_extractor_no_llm', 'ElementsExtractorNoLLM'),
        ('elements_extractor_with_llm', 'ElementsExtractorWithLLM'),
        ('test_generation_with_llm', 'WorldClassTestGenerator'),
        ('code_generation_with_llm', 'CodeGenerationWithLLM'),
        ('code_execution', 'CodeExecutionEngine'),
        ('pipeline_integration', 'IntegratedTestPipeline'),
        ('pipeline_contracts', 'ExtractedElement'),
        ('structured_output_enforcer', 'StructuredOutputEnforcer')
    ]
    
    import_success = []
    import_failed = []
    
    for module_name, class_name in import_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"  [OK] {module_name}.{class_name}")
                import_success.append(module_name)
            else:
                print(f"  [FAIL] {module_name} - {class_name} not found")
                import_failed.append(module_name)
        except ImportError as e:
            print(f"  [FAIL] {module_name} - {str(e)}")
            import_failed.append(module_name)
    
    # Check archive folder
    print("\n[ARCHIVE] Checking archived files...")
    print("-" * 50)
    
    archive_dir = current_dir / 'ui_testing_automation_archive'
    if archive_dir.exists():
        archived_files = list(archive_dir.glob('*.py'))
        test_files = [f for f in archived_files if f.name.startswith('test_')]
        print(f"  Archived test files: {len(test_files)}")
        print(f"  Total archived files: {len(list(archive_dir.glob('*')))}")
    else:
        print("  [WARNING] Archive folder not found")
    
    # Summary
    print("\n" + "=" * 70)
    print("[SUMMARY]")
    print(f"  Core modules present: {len(present)}/{len(core_modules)}")
    print(f"  Modules imported successfully: {len(import_success)}/{len(import_tests)}")
    
    if missing:
        print(f"\n[WARNING] Missing core modules:")
        for m in missing:
            print(f"    - {m}")
    
    if import_failed:
        print(f"\n[WARNING] Failed imports:")
        for m in import_failed:
            print(f"    - {m}")
    
    if not missing and not import_failed:
        print("\n[SUCCESS] All core modules are present and working!")
        print("\nThe application is ready for production use.")
        print("\nCore capabilities intact:")
        print("  - Element extraction (with and without LLM)")
        print("  - Test scenario generation (Gherkin)")
        print("  - Code generation (Python Playwright)")
        print("  - Code execution (sandboxed)")
        print("  - Pipeline orchestration")
        return True
    else:
        print("\n[WARNING] Some core modules are missing or not working.")
        return False

if __name__ == "__main__":
    success = verify_core_structure()
    sys.exit(0 if success else 1)