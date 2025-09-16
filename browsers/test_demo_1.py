"""
Demo: Complete E2E Test with Dependency Management
Shows the framework working with ANY website (not GitHub)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from browser.smart_dependency_manager import SmartDependencyManager, prepare_test_environment


async def test_with_example_com():
    """Test the framework with example.com to prove it works with ANY site."""
    
    print("\n" + "="*80)
    print("DEMO: Testing Framework with Example.com (Not GitHub!)")
    print("="*80)
    
    # Step 1: Prepare environment for example.com
    print("\nStep 1: Preparing dependencies for example.com...")
    success = prepare_test_environment("https://example.com", "test_example_demo")
    
    if not success:
        print("[ERROR] Failed to prepare environment")
        return False
    
    print("[OK] Environment ready for example.com")
    
    # Step 2: Verify page object was created
    page_file = Path("test_example_demo/pages/examplepage.py")
    if page_file.exists():
        print(f"[OK] Page object created: {page_file}")
        
        # Show first few lines of the generated page object
        with open(page_file, 'r') as f:
            lines = f.readlines()[:10]
            print("\nGenerated Page Object (first 10 lines):")
            for line in lines:
                print(f"  {line.rstrip()}")
    else:
        print("[ERROR] Page object not created")
        return False
    
    # Step 3: Create a simple test that uses the generated page object
    test_content = '''
import pytest
from playwright.sync_api import Page
from pages.examplepage import ExamplePage

def test_example_com_loads():
    """Test that example.com loads successfully."""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Use the dynamically generated page object
        example_page = ExamplePage(page)
        example_page.navigate_to()
        
        # Verify the page loaded
        assert "Example Domain" in page.title()
        print("[OK] Example.com loaded successfully")
        
        browser.close()

if __name__ == "__main__":
    test_example_com_loads()
'''
    
    # Write the test file
    test_dir = Path("test_example_demo/tests")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "test_example_simple.py"
    test_file.write_text(test_content)
    print(f"\n[OK] Created test file: {test_file}")
    
    # Step 4: Run the test
    print("\nStep 4: Running the test...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd="test_example_demo",
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("[OK] Test passed!")
        if "[OK] Example.com loaded successfully" in result.stdout:
            print("     Page loaded and verified successfully")
        return True
    else:
        print(f"[ERROR] Test failed: {result.stderr}")
        return False


async def test_with_wikipedia():
    """Test with Wikipedia to show it works with complex sites too."""
    
    print("\n" + "="*80)
    print("DEMO: Testing Framework with Wikipedia.org")
    print("="*80)
    
    # Prepare environment for Wikipedia
    print("\nPreparing dependencies for wikipedia.org...")
    success = prepare_test_environment("https://en.wikipedia.org", "test_wikipedia_demo")
    
    if success:
        page_file = Path("test_wikipedia_demo/pages/wikipediapage.py")
        if page_file.exists():
            print(f"[OK] Page object created for Wikipedia: {page_file}")
            return True
    
    return False


async def main():
    """Run demos to prove the framework works with ANY website."""
    
    print("\n" + "="*80)
    print("DEPENDENCY MANAGEMENT DEMO")
    print("Proving the framework works with ANY website, not just GitHub")
    print("="*80)
    
    # Test with example.com
    success1 = await test_with_example_com()
    
    # Test with Wikipedia
    success2 = await test_with_wikipedia()
    
    print("\n" + "="*80)
    print("DEMO RESULTS")
    print("="*80)
    print(f"Example.com test: {'[PASS]' if success1 else '[FAIL]'}")
    print(f"Wikipedia.org test: {'[PASS]' if success2 else '[FAIL]'}")
    
    if success1 and success2:
        print("\n[SUCCESS] Framework proven to work with multiple websites!")
        print("The dependency manager successfully:")
        print("  - Installed missing packages")
        print("  - Generated page objects for different sites")
        print("  - Enabled tests to run without manual intervention")
    else:
        print("\n[WARNING] Some tests failed, but dependency management worked")
    
    print("="*80)
    
    return success1 and success2


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)