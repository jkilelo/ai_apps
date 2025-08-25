#!/usr/bin/env python3
"""
Test for Step 2 to accept ElementData from Step 1
Written BEFORE implementation as per CODER protocol
"""
import pytest
from dataclasses import asdict
from step1_element_extractor import ElementData
from step2_gherkin_generator import ExtractedElement

def test_step2_accepts_step1_elements():
    """Test that Step 2 can directly use ElementData from Step 1"""
    # Create ElementData from Step 1 with ALL fields
    element_data = ElementData(
        tag_name="button",
        element_type="submit",
        xpath="/html/body/button",
        css_selector="button",
        text_content="Click me",
        inner_html="<span>Click me</span>",  # Extra field
        outer_html="<button><span>Click me</span></button>",  # Extra field
        id="btn1",
        class_names=["btn", "primary"],
        name="submit-btn",
        href=None,
        src=None,  # Extra field
        alt=None,  # Extra field
        title="Submit button",  # Extra field
        is_clickable=True,
        is_visible=True,
        is_enabled=True  # Extra field
    )
    
    # Convert to dict
    element_dict = asdict(element_data)
    
    # Step 2 should accept this directly (currently fails)
    # This test will fail until we fix ExtractedElement
    extracted_element = ExtractedElement(**element_dict)
    
    assert extracted_element.tag_name == "button"
    assert extracted_element.text_content == "Click me"

if __name__ == "__main__":
    test_step2_accepts_step1_elements()
    print("✅ Test passes - Step 2 accepts Step 1 elements")