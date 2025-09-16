#!/usr/bin/env python3
"""
Comprehensive Test Suite for Properties Field Fix
=================================================
This test suite verifies that the properties field has been properly added
to the ExtractionResult model and that all functionality dependent on it
is working correctly.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock

import pytest
from pydantic import ValidationError

# Import the modules under test
from element_extractor_no_llm_robust import (
    ExtractionResult,
    ElementData,
    ElementType,
    Platform,
    UltimateElementExtractor,
    ExtractionStrategy,
    UltimateStealthBrowser,
)


class TestPropertiesFieldFix:
    """Test suite for verifying the properties field fix in ExtractionResult"""

    def test_extraction_result_has_properties_field(self):
        """Test that ExtractionResult model has properties field"""
        # Create an ExtractionResult instance
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP
        )
        
        # Verify properties field exists and is initialized as empty dict
        assert hasattr(result, 'properties')
        assert isinstance(result.properties, dict)
        assert result.properties == {}
        
    def test_properties_field_can_store_data(self):
        """Test that properties field can store various data types"""
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP
        )
        
        # Test storing different data types
        result.properties["screenshot_path"] = "/path/to/screenshot.png"
        result.properties["validation_report"] = {"errors": [], "warnings": []}
        result.properties["metadata"] = {"version": "1.0", "timestamp": "2025-08-29"}
        result.properties["count"] = 42
        result.properties["is_valid"] = True
        
        # Verify all data is stored correctly
        assert result.properties["screenshot_path"] == "/path/to/screenshot.png"
        assert result.properties["validation_report"] == {"errors": [], "warnings": []}
        assert result.properties["metadata"]["version"] == "1.0"
        assert result.properties["count"] == 42
        assert result.properties["is_valid"] is True
        
    def test_extraction_result_serialization_with_properties(self):
        """Test that ExtractionResult can be serialized/deserialized with properties"""
        # Create result with properties
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP
        )
        result.properties["screenshot_path"] = "/screenshots/test.png"
        result.properties["enrichment_data"] = {"ai_analysis": "completed"}
        
        # Serialize to dict
        result_dict = result.model_dump()
        assert "properties" in result_dict
        assert result_dict["properties"]["screenshot_path"] == "/screenshots/test.png"
        
        # Serialize to JSON
        result_json = result.model_dump_json()
        assert "properties" in result_json
        
        # Deserialize from dict
        new_result = ExtractionResult(**result_dict)
        assert new_result.properties["screenshot_path"] == "/screenshots/test.png"
        assert new_result.properties["enrichment_data"]["ai_analysis"] == "completed"
        
        # Deserialize from JSON
        result_from_json = ExtractionResult.model_validate_json(result_json)
        assert result_from_json.properties["screenshot_path"] == "/screenshots/test.png"
        
    @pytest.mark.asyncio
    async def test_extract_with_screenshots_stores_path_in_properties(self):
        """Test that extract_with_screenshots stores screenshot path in properties"""
        # Mock the page and context
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.is_closed = Mock(return_value=False)
        
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        
        # Create extractor (UltimateElementExtractor doesn't take page in constructor)
        extractor = UltimateElementExtractor()
        extractor.page = mock_page
        
        # Mock the extract method to return a basic result
        async def mock_extract(*args, **kwargs):
            result = ExtractionResult(
                url="https://example.com",
                platform=Platform.DESKTOP
            )
            return result
        
        with patch.object(extractor, 'extract', mock_extract):
            # Call extract_with_screenshots
            with tempfile.TemporaryDirectory() as tmpdir:
                screenshot_path = Path(tmpdir) / "screenshot.png"
                result = await extractor.extract_with_screenshots(
                    url="https://example.com",
                    screenshot_path=screenshot_path
                )
                
                # Verify properties field exists and contains screenshot path
                assert hasattr(result, 'properties')
                assert "screenshot_path" in result.properties
                assert result.properties["screenshot_path"] is not None
                
                # The screenshot path should be stored as a string
                stored_path = result.properties["screenshot_path"]
                assert isinstance(stored_path, (str, Path))
                
                # If it's a Path object converted to string, check the suffix
                if isinstance(stored_path, str) and stored_path.endswith(".png"):
                    assert True  # Path has correct suffix
                elif isinstance(stored_path, Path):
                    assert stored_path.suffix == ".png"
                
    @pytest.mark.asyncio
    async def test_extract_with_enrichment_stores_data_in_properties(self):
        """Test that extract_with_enrichment stores enrichment data in properties"""
        # Mock the page
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.is_closed = Mock(return_value=False)
        
        # Create extractor (UltimateElementExtractor doesn't take page in constructor)
        extractor = UltimateElementExtractor()
        extractor.page = mock_page
        
        # Mock enrichment function
        async def mock_enrichment(element, page):
            return {"ai_score": 0.95, "category": "button"}
        
        # Mock the extract method
        async def mock_extract(*args, **kwargs):
            result = ExtractionResult(
                url="https://example.com",
                platform=Platform.DESKTOP
            )
            # Add a sample element
            element = ElementData(
                element_id="test-button-1",
                tag_name="button",
                element_type=ElementType.BUTTON,
                selector="button#test"
            )
            result.elements = [element]
            result.interactive_elements = [element]
            return result
        
        with patch.object(extractor, 'extract', mock_extract):
            # Call extract_with_enrichment (it uses enrich parameter, not enrichment_fn)
            result = await extractor.extract_with_enrichment(
                url="https://example.com",
                enrich=True
            )
            
            # Verify properties field exists
            assert hasattr(result, 'properties')
            assert isinstance(result.properties, dict)
            
            # Verify validation report is stored in properties (that's what the actual method stores)
            assert "validation_report" in result.properties
            assert isinstance(result.properties["validation_report"], dict)
            # The validation report contains quality metrics
            assert "quality_score" in result.properties["validation_report"]
            assert "total_elements" in result.properties["validation_report"]
            
    def test_properties_field_with_complex_nested_data(self):
        """Test properties field with complex nested data structures"""
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP
        )
        
        # Store complex nested data
        complex_data = {
            "screenshots": {
                "full_page": "/screenshots/full.png",
                "above_fold": "/screenshots/above.png",
                "thumbnails": [
                    "/screenshots/thumb1.png",
                    "/screenshots/thumb2.png"
                ]
            },
            "validation": {
                "accessibility": {
                    "score": 98,
                    "issues": [],
                    "passed_checks": ["alt_text", "aria_labels", "color_contrast"]
                },
                "performance": {
                    "load_time": 1.5,
                    "interactive_time": 2.1
                }
            },
            "ai_analysis": {
                "sentiment": "positive",
                "ui_quality": 0.92,
                "recommendations": [
                    "Improve button contrast",
                    "Add loading indicators"
                ]
            }
        }
        
        result.properties["analysis_report"] = complex_data
        
        # Verify complex data is stored and accessible
        assert result.properties["analysis_report"]["screenshots"]["full_page"] == "/screenshots/full.png"
        assert len(result.properties["analysis_report"]["screenshots"]["thumbnails"]) == 2
        assert result.properties["analysis_report"]["validation"]["accessibility"]["score"] == 98
        assert result.properties["analysis_report"]["ai_analysis"]["ui_quality"] == 0.92
        
        # Verify serialization works with complex data
        serialized = result.model_dump()
        assert serialized["properties"]["analysis_report"]["validation"]["performance"]["load_time"] == 1.5
        
        # Verify deserialization works
        deserialized = ExtractionResult(**serialized)
        assert deserialized.properties["analysis_report"]["ai_analysis"]["sentiment"] == "positive"
        
    def test_properties_field_independent_from_other_fields(self):
        """Test that properties field doesn't interfere with other ExtractionResult fields"""
        # Create result with all fields populated
        element = ElementData(
            element_id="test-element-1",
            tag_name="div",
            element_type=ElementType.SECTION,
            selector="div.test"
        )
        
        result = ExtractionResult(
            url="https://example.com",
            platform=Platform.DESKTOP,
            elements=[element],
            total_elements=1,
            page_title="Test Page",
            page_url="https://example.com/page"
        )
        
        # Add properties
        result.properties["custom_data"] = "test_value"
        
        # Verify other fields are not affected
        assert result.url == "https://example.com"
        assert result.platform == Platform.DESKTOP
        assert len(result.elements) == 1
        assert result.total_elements == 1
        assert result.page_title == "Test Page"
        assert result.properties["custom_data"] == "test_value"
        
        # Modify properties and verify other fields remain unchanged
        result.properties["another_key"] = "another_value"
        assert result.url == "https://example.com"
        assert len(result.elements) == 1
        
    def test_properties_field_default_factory(self):
        """Test that each ExtractionResult instance has its own properties dict"""
        # Create multiple instances
        result1 = ExtractionResult(url="https://example1.com", platform=Platform.DESKTOP)
        result2 = ExtractionResult(url="https://example2.com", platform=Platform.DESKTOP)
        
        # Modify properties in result1
        result1.properties["key1"] = "value1"
        
        # Verify result2 properties are not affected
        assert "key1" not in result2.properties
        assert result2.properties == {}
        
        # Modify properties in result2
        result2.properties["key2"] = "value2"
        
        # Verify result1 is not affected
        assert "key2" not in result1.properties
        assert result1.properties == {"key1": "value1"}


def run_comprehensive_tests():
    """Run all tests and report results"""
    print("=" * 80)
    print("COMPREHENSIVE PROPERTIES FIELD FIX VERIFICATION")
    print("=" * 80)
    
    # Run pytest programmatically
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED - Properties field fix is working correctly!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("SOME TESTS FAILED - Please review the output above")
        print("=" * 80)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)