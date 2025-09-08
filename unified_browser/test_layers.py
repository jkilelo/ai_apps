"""
Test script to verify Layer 0 (Core) and Layer 1 (Config) are working correctly.
"""

import sys
from pathlib import Path

# Add the parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_browser.core import (
    BrowserEngine,
    StealthLevel,
    NavigationStrategy,
    ExtractionMethod,
    ContentType,
    LLMProvider,
)
from unified_browser.config import (
    ConfigFactory,
    ConfigProfile,
    UnifiedConfig,
    BrowserConfig,
    StealthConfig,
    NavigationConfig,
    ExtractionConfig,
    SecurityConfig,
    PerformanceConfig,
    AIConfig,
)


def test_core_enums():
    """Test that all core enums are accessible."""
    print("Testing Core Enums...")
    
    # Test BrowserEngine
    assert BrowserEngine.PLAYWRIGHT
    assert BrowserEngine.SELENIUM
    assert BrowserEngine.UNDETECTED
    print(f"✓ BrowserEngine has {len(BrowserEngine)} engines")
    
    # Test StealthLevel
    assert StealthLevel.BASIC
    assert StealthLevel.ENHANCED
    assert StealthLevel.MAXIMUM
    print(f"✓ StealthLevel has {len(StealthLevel)} levels")
    
    # Test NavigationStrategy
    assert NavigationStrategy.LOAD
    assert NavigationStrategy.NETWORK_IDLE
    print(f"✓ NavigationStrategy has {len(NavigationStrategy)} strategies")
    
    # Test ExtractionMethod
    assert ExtractionMethod.PLAYWRIGHT
    assert ExtractionMethod.BEAUTIFUL_SOUP
    print(f"✓ ExtractionMethod has {len(ExtractionMethod)} methods")
    
    # Test ContentType
    assert ContentType.TEXT
    assert ContentType.TABLE
    print(f"✓ ContentType has {len(ContentType)} types")
    
    # Test LLMProvider
    assert LLMProvider.OPENAI
    assert LLMProvider.GEMINI
    print(f"✓ LLMProvider has {len(LLMProvider)} providers")
    
    print("✓ All core enums working!\n")


def test_config_profiles():
    """Test that all config profiles can be created."""
    print("Testing Config Profiles...")
    
    profiles_to_test = [
        ConfigProfile.DEFAULT,
        ConfigProfile.MINIMAL,
        ConfigProfile.DEVELOPMENT,
        ConfigProfile.TESTING,
        ConfigProfile.PRODUCTION,
        ConfigProfile.SCRAPING,
        ConfigProfile.AUTOMATION,
        ConfigProfile.STEALTH,
        ConfigProfile.FAST,
        ConfigProfile.SECURE,
        ConfigProfile.INTELLIGENT,
    ]
    
    for profile in profiles_to_test:
        try:
            config = ConfigFactory.create_config(profile)
            assert isinstance(config, UnifiedConfig)
            assert config.profile == profile
            print(f"✓ {profile.value} profile created successfully")
        except Exception as e:
            print(f"✗ Failed to create {profile.value}: {e}")
            return False
    
    print("✓ All config profiles working!\n")
    return True


def test_individual_configs():
    """Test individual configuration classes."""
    print("Testing Individual Configurations...")
    
    # Test BrowserConfig
    browser_config = BrowserConfig()
    assert browser_config.headless == True
    assert browser_config.viewport.width == 1920
    print("✓ BrowserConfig created")
    
    # Test StealthConfig
    stealth_config = StealthConfig()
    assert stealth_config.level == StealthLevel.ENHANCED
    assert stealth_config.hide_webdriver == True
    print("✓ StealthConfig created")
    
    # Test NavigationConfig
    nav_config = NavigationConfig()
    assert nav_config.wait_strategy.default_strategy == NavigationStrategy.LOAD
    print("✓ NavigationConfig created")
    
    # Test ExtractionConfig
    extract_config = ExtractionConfig()
    assert extract_config.method == ExtractionMethod.PLAYWRIGHT
    print("✓ ExtractionConfig created")
    
    # Test SecurityConfig
    security_config = SecurityConfig()
    assert security_config.security_level == "high"
    print("✓ SecurityConfig created")
    
    # Test PerformanceConfig
    perf_config = PerformanceConfig()
    assert perf_config.mode == "balanced"
    print("✓ PerformanceConfig created")
    
    # Test AIConfig
    ai_config = AIConfig()
    assert ai_config.primary_provider == LLMProvider.GEMINI
    print("✓ AIConfig created")
    
    print("✓ All individual configs working!\n")
    return True


def test_config_factory_methods():
    """Test configuration factory methods."""
    print("Testing Config Factory Methods...")
    
    # Test BrowserConfig factory methods
    headless = BrowserConfig.headless_config()
    assert headless.headless == True
    print("✓ BrowserConfig.headless_config() works")
    
    debug = BrowserConfig.debug_config()
    assert debug.headless == False
    assert debug.debug.devtools == True
    print("✓ BrowserConfig.debug_config() works")
    
    # Test StealthConfig factory methods
    basic_stealth = StealthConfig.basic_stealth()
    assert basic_stealth.level == StealthLevel.BASIC
    print("✓ StealthConfig.basic_stealth() works")
    
    max_stealth = StealthConfig.maximum_stealth()
    assert max_stealth.level == StealthLevel.MAXIMUM
    print("✓ StealthConfig.maximum_stealth() works")
    
    # Test NavigationConfig factory methods
    fast_nav = NavigationConfig.fast_navigation()
    assert fast_nav.wait_strategy.default_strategy == NavigationStrategy.COMMIT
    print("✓ NavigationConfig.fast_navigation() works")
    
    reliable_nav = NavigationConfig.reliable_navigation()
    assert reliable_nav.wait_strategy.default_strategy == NavigationStrategy.NETWORK_IDLE
    print("✓ NavigationConfig.reliable_navigation() works")
    
    # Test ExtractionConfig factory methods
    minimal_extract = ExtractionConfig.minimal_extraction()
    assert ContentType.TEXT in minimal_extract.content_types
    print("✓ ExtractionConfig.minimal_extraction() works")
    
    # Test SecurityConfig factory methods
    low_security = SecurityConfig.low_security()
    assert low_security.security_level == "low"
    print("✓ SecurityConfig.low_security() works")
    
    high_security = SecurityConfig.high_security()
    assert high_security.security_level == "high"
    print("✓ SecurityConfig.high_security() works")
    
    # Test PerformanceConfig factory methods
    fast_perf = PerformanceConfig.fast_mode()
    assert fast_perf.mode == "fast"
    print("✓ PerformanceConfig.fast_mode() works")
    
    # Test AIConfig factory methods
    basic_ai = AIConfig.basic_config()
    assert basic_ai.vision.enabled == False
    print("✓ AIConfig.basic_config() works")
    
    print("✓ All factory methods working!\n")
    return True


def test_config_serialization():
    """Test configuration serialization."""
    print("Testing Config Serialization...")
    
    # Create a config
    config = ConfigFactory.create_config(ConfigProfile.DEFAULT)
    
    # Test to_dict
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert config_dict["profile"] == "default"
    assert "browser" in config_dict
    assert "navigation" in config_dict
    print("✓ Config.to_dict() works")
    
    # Test from_dict
    new_config = UnifiedConfig.from_dict(config_dict)
    assert isinstance(new_config, UnifiedConfig)
    assert new_config.profile == ConfigProfile.DEFAULT
    print("✓ Config.from_dict() works")
    
    print("✓ Config serialization working!\n")
    return True


def test_imports():
    """Test that all imports work correctly."""
    print("Testing Imports...")
    
    try:
        # Test core imports
        from unified_browser.core import (
            constants,
            enums,
            types,
            exceptions,
            utils,
        )
        print("✓ Core module imports work")
        
        # Test config imports
        from unified_browser.config import (
            browser_config,
            stealth_config,
            navigation_config,
            extraction_config,
            security_config,
            ai_config,
            performance_config,
            config_factory,
        )
        print("✓ Config module imports work")
        
        # Test specific exception imports
        from unified_browser.core.exceptions import (
            UnifiedBrowserError,
            NavigationError,
            TimeoutError,
            ExtractionError,
        )
        print("✓ Exception imports work")
        
        # Test utility imports
        from unified_browser.core.utils import (
            validate_url,
            sanitize_filename,
        )
        print("✓ Utility imports work")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print("✓ All imports working!\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("UNIFIED BROWSER - LAYER 0 & 1 TEST SUITE")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Run tests
    try:
        test_imports()
        test_core_enums()
        test_individual_configs()
        test_config_factory_methods()
        test_config_profiles()
        test_config_serialization()
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED! Layers 0 and 1 are working correctly!")
    else:
        print("❌ Some tests failed. Please review the errors above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)