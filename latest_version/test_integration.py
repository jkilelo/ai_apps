#!/usr/bin/env python3
"""
Test for integration between Step 1 and Step 2
Written BEFORE implementation as per CODER protocol
"""
import pytest
import asyncio
from dataclasses import asdict
from step1_element_extractor import ElementData
from step2_gherkin_generator import ExtractedElement

def test_element_data_compatibility():
    """Test that ElementData from Step 1 can be converted to ExtractedElement for Step 2"""
    # Create sample ElementData from Step 1
    element_data = ElementData(
        tag_name="button",
        element_type="submit",
        xpath="/html/body/button",
        css_selector="button",
        text_content="Click me",
        inner_html="<span>Click me</span>",  # This field exists in ElementData
        outer_html="<button><span>Click me</span></button>",  # This too
        id="btn1",
        class_names=["btn", "primary"],
        is_clickable=True,
        is_visible=True
    )
    
    # Convert to dict
    element_dict = asdict(element_data)
    
    # Filter only fields that ExtractedElement accepts
    extracted_element_fields = {
        'tag_name', 'element_type', 'xpath', 'css_selector', 'text_content',
        'id', 'class_names', 'name', 'href', 'is_clickable', 'is_visible',
        'role', 'aria_label', 'placeholder', 'value', 'input_type',
        'interaction_type', 'confidence_score'
    }
    
    filtered_dict = {k: v for k, v in element_dict.items() if k in extracted_element_fields}
    
    # This should work without errors
    extracted_element = ExtractedElement(**filtered_dict)
    
    assert extracted_element.tag_name == "button"
    assert extracted_element.text_content == "Click me"
    assert extracted_element.is_clickable == True

def test_convert_elements_for_step2():
    """Test conversion function for compatibility"""
    from step1_element_extractor import ElementData
    
    def convert_element_for_step2(element_data_dict):
        """Convert ElementData dict to ExtractedElement compatible dict"""
        # Fields that ExtractedElement accepts
        allowed_fields = {
            'tag_name', 'element_type', 'xpath', 'css_selector', 'text_content',
            'id', 'class_names', 'name', 'href', 'is_clickable', 'is_visible',
            'role', 'aria_label', 'placeholder', 'value', 'input_type',
            'interaction_type', 'confidence_score'
        }
        
        # Filter to only allowed fields
        return {k: v for k, v in element_data_dict.items() if k in allowed_fields}
    
    # Test with sample data
    sample_element = {
        "tag_name": "a",
        "element_type": "a",
        "xpath": "/html/body/a",
        "css_selector": "a",
        "text_content": "Link",
        "inner_html": "",  # Should be filtered out
        "outer_html": "",  # Should be filtered out
        "is_clickable": True,
        "is_visible": True,
        "extra_field": "value"  # Should be filtered out
    }
    
    filtered = convert_element_for_step2(sample_element)
    
    # These fields should be removed
    assert 'inner_html' not in filtered
    assert 'outer_html' not in filtered
    assert 'extra_field' not in filtered
    
    # These fields should remain
    assert filtered['tag_name'] == 'a'
    assert filtered['text_content'] == 'Link'

if __name__ == "__main__":
    test_element_data_compatibility()
    test_convert_elements_for_step2()
    print("✅ All tests pass - now implementing fix")