#!/usr/bin/env python3
"""
Direct test of the properties field fix in ExtractionResult model
"""

import sys
from pathlib import Path
from typing import Dict, Any
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_testing_framework.element_extractor_no_llm_robust import (
    ExtractionResult,
    Platform,
    ElementType,
    ElementData,
)


def test_properties_field():
    """Test that the properties field works correctly in ExtractionResult"""
    
    print("Testing Properties Field Fix")
    print("=" * 60)
    
    # Test 1: Create ExtractionResult with empty properties
    print("\nTest 1: Creating ExtractionResult with default properties")
    result = ExtractionResult(
        url="https://example.com",
        platform=Platform.DESKTOP
    )
    
    assert hasattr(result, "properties"), "ExtractionResult should have properties field"
    assert isinstance(result.properties, dict), "properties should be a dict"
    assert len(result.properties) == 0, "properties should be empty by default"
    print("[PASS] ExtractionResult has properties field of type dict")
    
    # Test 2: Add data to properties
    print("\nTest 2: Adding data to properties field")
    result.properties["screenshot_path"] = "/path/to/screenshot.png"
    result.properties["validation_report"] = {
        "quality_score": 0.95,
        "completeness": 1.0,
        "errors": []
    }
    result.properties["custom_metadata"] = {
        "timestamp": "2025-08-29T15:00:00",
        "version": "1.0.0"
    }
    
    assert result.properties["screenshot_path"] == "/path/to/screenshot.png"
    assert result.properties["validation_report"]["quality_score"] == 0.95
    assert result.properties["custom_metadata"]["version"] == "1.0.0"
    print("[PASS] Properties field can store various data types")
    
    # Test 3: Serialization and deserialization
    print("\nTest 3: Testing serialization/deserialization")
    
    # Add some elements to make it more realistic
    element = ElementData(
        element_id="btn-001",
        element_type=ElementType.BUTTON,
        selector="button#submit",
        text="Submit",
        tag_name="button",
        attributes={"id": "submit", "class": "btn btn-primary"}
    )
    result.elements.append(element)
    
    # Serialize to dict
    result_dict = result.model_dump()
    
    assert "properties" in result_dict, "properties should be in serialized dict"
    assert result_dict["properties"]["screenshot_path"] == "/path/to/screenshot.png"
    print("[PASS] Properties field serializes correctly")
    
    # Deserialize from dict
    restored_result = ExtractionResult(**result_dict)
    
    assert hasattr(restored_result, "properties")
    assert restored_result.properties["screenshot_path"] == "/path/to/screenshot.png"
    assert restored_result.properties["validation_report"]["quality_score"] == 0.95
    assert len(restored_result.elements) == 1
    print("[PASS] Properties field deserializes correctly")
    
    # Test 4: JSON export/import
    print("\nTest 4: Testing JSON export/import")
    
    # Export to JSON string
    json_str = json.dumps(result_dict, indent=2, default=str)
    
    # Import from JSON string
    loaded_dict = json.loads(json_str)
    loaded_result = ExtractionResult(**loaded_dict)
    
    assert loaded_result.properties["screenshot_path"] == "/path/to/screenshot.png"
    assert loaded_result.properties["custom_metadata"]["version"] == "1.0.0"
    print("[PASS] Properties field works with JSON export/import")
    
    # Test 5: Empty properties initialization
    print("\nTest 5: Testing empty properties initialization")
    
    empty_result = ExtractionResult(
        url="https://test.com",
        platform=Platform.MOBILE,
        properties={}  # Explicitly empty
    )
    
    assert isinstance(empty_result.properties, dict)
    assert len(empty_result.properties) == 0
    
    # Can still add to it
    empty_result.properties["new_key"] = "new_value"
    assert empty_result.properties["new_key"] == "new_value"
    print("[PASS] Empty properties initialization works correctly")
    
    # Test 6: Properties with initial values
    print("\nTest 6: Testing properties with initial values")
    
    initial_props = {
        "test_mode": True,
        "extraction_id": "abc123",
        "metadata": {"source": "test"}
    }
    
    result_with_props = ExtractionResult(
        url="https://test.com",
        platform=Platform.TABLET,
        properties=initial_props
    )
    
    assert result_with_props.properties["test_mode"] is True
    assert result_with_props.properties["extraction_id"] == "abc123"
    assert result_with_props.properties["metadata"]["source"] == "test"
    print("[PASS] Properties initialization with values works correctly")
    
    # Test 7: Type checking
    print("\nTest 7: Testing type annotations")
    
    # This should work with type checkers
    props: Dict[str, Any] = result.properties
    assert isinstance(props, dict)
    
    # Properties should accept any value type
    result.properties["string_val"] = "text"
    result.properties["int_val"] = 42
    result.properties["float_val"] = 3.14
    result.properties["bool_val"] = True
    result.properties["list_val"] = [1, 2, 3]
    result.properties["dict_val"] = {"nested": "dict"}
    result.properties["none_val"] = None
    
    print("[PASS] Properties field accepts all value types")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("The properties field has been successfully added to ExtractionResult")
    print("\nSummary:")
    print("- Properties field is now a Dict[str, Any]")
    print("- Default value is an empty dict")
    print("- Supports serialization/deserialization")
    print("- Type-safe for use with mypy")
    print("- Can store screenshot paths, validation reports, and any custom data")
    
    return True


if __name__ == "__main__":
    try:
        success = test_properties_field()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)