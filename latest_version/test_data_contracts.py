#!/usr/bin/env python3
"""
Tests for data contracts between Steps 1-4
Written BEFORE implementation as per CODER protocol
"""
import pytest
import json
from typing import List, Dict, Any
from pathlib import Path

def test_step1_output_contract():
    """Test Step 1 output conforms to ElementExtraction contract"""
    from data_contracts import ElementExtraction, ExtractedElement
    
    # Step 1 should output ElementExtraction
    sample_output = ElementExtraction(
        url="https://example.com",
        timestamp="2025-08-08T10:00:00",
        success=True,
        elements=[
            ExtractedElement(
                tag_name="button",
                element_type="submit",
                xpath="//button",
                css_selector="button.submit",
                text_content="Submit"
            )
        ],
        metadata={
            "extractor_version": "1.0.0",
            "extraction_time": 1.5
        }
    )
    
    # Should be serializable
    json_output = sample_output.model_dump_json()
    assert json_output
    
    # Should be deserializable
    reloaded = ElementExtraction.model_validate_json(json_output)
    assert reloaded.url == "https://example.com"
    assert len(reloaded.elements) == 1

def test_step2_input_output_contract():
    """Test Step 2 accepts Step 1 output and produces GherkinGeneration"""
    from data_contracts import ElementExtraction, ExtractedElement, GherkinGeneration, GherkinFeature
    
    # Step 2 input (from Step 1)
    step1_output = ElementExtraction(
        url="https://example.com",
        timestamp="2025-08-08T10:00:00",
        success=True,
        elements=[
            ExtractedElement(
                tag_name="input",
                element_type="text",
                xpath="//input[@id='username']",
                css_selector="#username",
                text_content=""
            )
        ]
    )
    
    # Step 2 output
    step2_output = GherkinGeneration(
        source_url=step1_output.url,
        timestamp="2025-08-08T10:01:00",
        success=True,
        features=[
            GherkinFeature(
                name="Login Test",
                description="Test login functionality",
                scenarios=[
                    {
                        "name": "Valid login",
                        "steps": [
                            {"keyword": "Given", "text": "I am on login page"},
                            {"keyword": "When", "text": "I enter credentials"},
                            {"keyword": "Then", "text": "I should be logged in"}
                        ]
                    }
                ]
            )
        ]
    )
    
    # Verify serialization
    assert step2_output.model_dump()
    assert step2_output.features[0].name == "Login Test"

def test_step3_input_output_contract():
    """Test Step 3 accepts Step 2 output and produces CodeGeneration"""
    from data_contracts import GherkinGeneration, GherkinFeature, CodeGeneration, GeneratedFile
    
    # Step 3 input (from Step 2)
    step2_output = GherkinGeneration(
        source_url="https://example.com",
        timestamp="2025-08-08T10:01:00",
        success=True,
        features=[
            GherkinFeature(
                name="Test Feature",
                description="Test description",
                scenarios=[
                    {
                        "name": "Test scenario",
                        "steps": [
                            {"keyword": "Given", "text": "a precondition"}
                        ]
                    }
                ]
            )
        ]
    )
    
    # Step 3 output
    step3_output = CodeGeneration(
        source_features=step2_output.features,
        timestamp="2025-08-08T10:02:00",
        success=True,
        files=[
            GeneratedFile(
                name="test_feature.py",
                path=Path("generated_tests/test_feature.py"),
                content="import pytest\n\ndef test_scenario():\n    pass",
                file_type="test"
            )
        ],
        test_framework="pytest",
        language="python"
    )
    
    # Verify
    assert step3_output.files[0].name == "test_feature.py"
    assert step3_output.test_framework == "pytest"

def test_step4_input_output_contract():
    """Test Step 4 accepts Step 3 output and produces ExecutionResult"""
    from data_contracts import CodeGeneration, GeneratedFile, ExecutionResult, TestResult
    
    # Step 4 input (from Step 3)
    step3_output = CodeGeneration(
        source_features=[],
        timestamp="2025-08-08T10:02:00",
        success=True,
        files=[
            GeneratedFile(
                name="test_example.py",
                path=Path("generated_tests/test_example.py"),
                content="def test_example(): assert True",
                file_type="test"
            )
        ],
        test_framework="pytest",
        language="python"
    )
    
    # Step 4 output
    step4_output = ExecutionResult(
        test_files=[f.path for f in step3_output.files],
        timestamp="2025-08-08T10:03:00",
        success=True,
        results=[
            TestResult(
                test_name="test_example",
                test_file=Path("generated_tests/test_example.py"),
                status="passed",
                duration=0.01,
                error_message=None
            )
        ],
        summary={
            "total": 1,
            "passed": 1,
            "failed": 0,
            "skipped": 0
        }
    )
    
    # Verify
    assert step4_output.summary["total"] == 1
    assert step4_output.results[0].status == "passed"

def test_pipeline_data_flow():
    """Test complete data flow from Step 1 to Step 4"""
    from data_contracts import (
        ElementExtraction, ExtractedElement,
        GherkinGeneration, GherkinFeature,
        CodeGeneration, GeneratedFile,
        ExecutionResult, TestResult
    )
    
    # Step 1 → Step 2
    step1_out = ElementExtraction(
        url="https://test.com",
        timestamp="2025-08-08T10:00:00",
        success=True,
        elements=[ExtractedElement(
            tag_name="a",
            element_type="link",
            xpath="//a",
            css_selector="a",
            text_content="Click"
        )]
    )
    
    # Step 2 can use Step 1's elements
    assert step1_out.elements[0].tag_name == "a"
    
    # Step 2 → Step 3
    step2_out = GherkinGeneration(
        source_url=step1_out.url,
        timestamp="2025-08-08T10:01:00",
        success=True,
        features=[GherkinFeature(
            name="Test",
            description="",
            scenarios=[{"name": "test", "steps": []}]
        )]
    )
    
    # Step 3 can use Step 2's features
    assert len(step2_out.features) == 1
    
    # Step 3 → Step 4
    step3_out = CodeGeneration(
        source_features=step2_out.features,
        timestamp="2025-08-08T10:02:00",
        success=True,
        files=[GeneratedFile(
            name="test.py",
            path=Path("test.py"),
            content="",
            file_type="test"
        )],
        test_framework="pytest",
        language="python"
    )
    
    # Step 4 can use Step 3's files
    step4_out = ExecutionResult(
        test_files=[f.path for f in step3_out.files],
        timestamp="2025-08-08T10:03:00",
        success=True,
        results=[],
        summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    )
    
    # Complete pipeline maintains data integrity
    assert step4_out.test_files[0] == step3_out.files[0].path

def test_contract_validation():
    """Test that contracts validate input properly"""
    from data_contracts import ExtractedElement
    
    # Should fail with missing required fields
    with pytest.raises(Exception):  # Will be ValidationError with pydantic
        ExtractedElement()  # Missing required fields
    
    # Should fail with wrong types
    with pytest.raises(Exception):
        ExtractedElement(
            tag_name=123,  # Should be string
            element_type="button",
            xpath="//button",
            css_selector="button",
            text_content="Click"
        )

def test_backward_compatibility():
    """Test contracts work with existing Step 1 ElementData"""
    from step1_element_extractor import ElementData
    from data_contracts import ExtractedElement
    from dataclasses import asdict
    
    # Existing ElementData from Step 1
    old_element = ElementData(
        tag_name="div",
        element_type="container", 
        xpath="//div",
        css_selector="div",
        text_content="Content",
        inner_html="<span>Content</span>",  # Extra field
        is_focusable=True,  # Extra field
        x=100, y=200  # Extra fields
    )
    
    # Should be convertible to new contract
    old_dict = asdict(old_element)
    
    # Filter to valid fields
    valid_fields = {k: v for k, v in old_dict.items() 
                   if k in ExtractedElement.model_fields}
    
    # Should create new contract object
    new_element = ExtractedElement(**valid_fields)
    assert new_element.tag_name == "div"

if __name__ == "__main__":
    # Run tests
    test_step1_output_contract()
    print("✅ Step 1 output contract test passed")
    
    test_step2_input_output_contract()
    print("✅ Step 2 input/output contract test passed")
    
    test_step3_input_output_contract()
    print("✅ Step 3 input/output contract test passed")
    
    test_step4_input_output_contract()
    print("✅ Step 4 input/output contract test passed")
    
    test_pipeline_data_flow()
    print("✅ Pipeline data flow test passed")
    
    test_contract_validation()
    print("✅ Contract validation test passed")
    
    test_backward_compatibility()
    print("✅ Backward compatibility test passed")
    
    print("\n✅ All tests defined - now implementing contracts")