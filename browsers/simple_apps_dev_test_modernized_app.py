"""
Test script to verify the modernized Simple Apps v2 application.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import get_logger
from simple_apps_v2.services.browser import BrowserService
from simple_apps_v2.services.extractor import ElementExtractor
from simple_apps_v2.utils.validation import validate_url, validate_email


def test_configuration():
    """Test configuration loading."""
    print("\n✅ Testing Configuration...")
    settings = get_settings()
    print(f"  App Name: {settings.app_name}")
    print(f"  Version: {settings.version}")
    print(f"  API Port: {settings.api_port}")
    print(f"  Browser Headless: {settings.browser_headless}")
    return True


def test_logging():
    """Test logging system."""
    print("\n✅ Testing Logging...")
    logger = get_logger("test")
    logger.info("Test log message")
    logger.debug("Debug message")
    logger.warning("Warning message")
    return True


def test_validation():
    """Test validation utilities."""
    print("\n✅ Testing Validation...")
    
    # Test URL validation
    assert validate_url("https://example.com") is True
    assert validate_url("not-a-url") is False
    print("  URL validation: ✓")
    
    # Test email validation
    assert validate_email("test@example.com") is True
    assert validate_email("invalid-email") is False
    print("  Email validation: ✓")
    
    return True


async def test_browser_service():
    """Test browser service."""
    print("\n✅ Testing Browser Service...")
    try:
        service = BrowserService()
        await service.initialize()
        
        # Test basic browser functionality
        async with service.managed_page("https://example.com") as page:
            title = await page.title()
            print(f"  Page title: {title}")
            assert "Example" in title
        
        await service.close()
        print("  Browser service: ✓")
        return True
    except Exception as e:
        print(f"  Browser service test failed: {e}")
        print("  Note: This may be expected if Playwright browsers are not installed")
        return False


async def test_element_extractor():
    """Test element extractor service."""
    print("\n✅ Testing Element Extractor...")
    try:
        extractor = ElementExtractor()
        
        # Test with a simple URL
        result = await extractor.extract_elements_from_url("https://example.com")
        
        print(f"  Found {result['total_elements']} elements")
        print(f"  Categories: {list(result['elements_by_category'].keys())}")
        print("  Element extraction: ✓")
        return True
    except Exception as e:
        print(f"  Element extractor test failed: {e}")
        print("  Note: This may be expected if Playwright browsers are not installed")
        return False


def test_imports():
    """Test all major imports."""
    print("\n✅ Testing Imports...")
    try:
        # Core imports
        from simple_apps_v2.core.config import Settings
        from simple_apps_v2.core.logging import setup_logging
        from simple_apps_v2.core.models import ExtractionRequest, ExtractionResponse
        
        # Service imports
        from simple_apps_v2.services.browser import BrowserService
        from simple_apps_v2.services.extractor import ElementExtractor
        from simple_apps_v2.services.llm import LLMService
        
        # API imports
        from simple_apps_v2.api.main import app
        from simple_apps_v2.api.endpoints import extraction, health
        
        # Utils imports
        from simple_apps_v2.utils.validation import validate_url, validate_email
        from simple_apps_v2.utils.helpers import format_timestamp, generate_unique_id
        
        print("  All imports successful: ✓")
        return True
    except ImportError as e:
        print(f"  Import failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 SIMPLE APPS V2 - MODERNIZATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Synchronous tests
    results.append(("Configuration", test_configuration()))
    results.append(("Logging", test_logging()))
    results.append(("Validation", test_validation()))
    results.append(("Imports", test_imports()))
    
    # Asynchronous tests
    browser_result = await test_browser_service()
    results.append(("Browser Service", browser_result))
    
    extractor_result = await test_element_extractor()
    results.append(("Element Extractor", extractor_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {name}: {status}")
    
    print("\n" + "-" * 60)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The modernization was successful!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. See details above.")
        print("\nNote: Browser-related tests may fail if Playwright browsers")
        print("are not installed. Run: playwright install chromium")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    sys.exit(0 if success else 1)