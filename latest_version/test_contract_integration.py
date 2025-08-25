#!/usr/bin/env python3
"""
Tests for contract integration in Steps 1-4
Written BEFORE implementation as per CODER protocol
"""
import pytest
import asyncio
from pathlib import Path
from data_contracts import (
    ElementExtraction, ExtractedElement,
    GherkinGeneration, GherkinFeature,
    CodeGeneration, GeneratedFile,
    ExecutionResult, TestResult, TestStatus
)

async def test_step1_returns_contract():
    """Test Step 1 returns ElementExtraction contract"""
    from step1_element_extractor import UltimateElementExtractor, ExtractionConfig
    
    config = ExtractionConfig(
        timeout=5,
        headless=True,
        max_elements=5
    )
    
    extractor = UltimateElementExtractor(config)
    
    # Mock extraction for testing
    result = await extractor.extract_with_contract("https://example.com")
    
    # Should return ElementExtraction contract
    assert isinstance(result, ElementExtraction)
    assert result.url == "https://example.com"
    assert isinstance(result.elements, list)
    
    # Should be serializable
    json_output = result.model_dump_json()
    assert json_output

async def test_step2_accepts_contract():
    """Test Step 2 accepts ElementExtraction and returns GherkinGeneration"""
    from step2_gherkin_generator import GherkinTestGenerator
    
    # Create Step 1 output contract
    step1_output = ElementExtraction(
        url="https://example.com",
        timestamp="2025-08-08T10:00:00",
        success=True,
        elements=[
            ExtractedElement(
                tag_name="button",
                element_type="submit",
                xpath="//button",
                css_selector="button",
                text_content="Click me"
            )
        ]
    )
    
    generator = GherkinTestGenerator()
    
    # Should accept contract and return GherkinGeneration
    result = await generator.generate_with_contract(step1_output)
    
    assert isinstance(result, GherkinGeneration)
    assert result.source_url == step1_output.url

def test_step3_accepts_contract():
    """Test Step 3 accepts GherkinGeneration and returns CodeGeneration"""
    from step3_code_generator import PythonTestCodeGenerator
    
    # Create Step 2 output contract
    step2_output = GherkinGeneration(
        source_url="https://example.com",
        timestamp="2025-08-08T10:00:00",
        success=True,
        features=[
            GherkinFeature(
                name="Test Feature",
                description="Test",
                scenarios=[{
                    "name": "Test scenario",
                    "steps": []
                }]
            )
        ]
    )
    
    generator = PythonTestCodeGenerator()
    
    # Should accept contract and return CodeGeneration
    result = generator.generate_with_contract(step2_output)
    
    assert isinstance(result, CodeGeneration)
    assert len(result.source_features) == len(step2_output.features)

async def test_step4_accepts_contract():
    """Test Step 4 accepts CodeGeneration and returns ExecutionResult"""
    from step4_test_executor import TestExecutor, ExecutionConfig
    
    # Create Step 3 output contract
    step3_output = CodeGeneration(
        source_features=[],
        timestamp="2025-08-08T10:00:00",
        success=True,
        files=[
            GeneratedFile(
                name="test.py",
                path=Path("test.py"),
                content="def test(): pass",
                file_type="test"
            )
        ],
        test_framework="pytest",
        language="python"
    )
    
    config = ExecutionConfig(
        headless=True,
        timeout_per_test=5
    )
    executor = TestExecutor(config)
    
    # Should accept contract and return ExecutionResult
    result = await executor.execute_with_contract(step3_output)
    
    assert isinstance(result, ExecutionResult)
    assert result.test_files == [f.path for f in step3_output.files]

async def test_full_pipeline_with_contracts():
    """Test complete pipeline with contracts"""
    from step1_element_extractor import UltimateElementExtractor, ExtractionConfig
    from step2_gherkin_generator import GherkinTestGenerator
    from step3_code_generator import PythonTestCodeGenerator
    from step4_test_executor import TestExecutor, ExecutionConfig
    
    # Step 1
    extractor = UltimateElementExtractor(ExtractionConfig(timeout=5, headless=True))
    step1_result = await extractor.extract_with_contract("https://example.com")
    assert isinstance(step1_result, ElementExtraction)
    
    # Step 2
    generator2 = GherkinTestGenerator()
    step2_result = await generator2.generate_with_contract(step1_result)
    assert isinstance(step2_result, GherkinGeneration)
    
    # Step 3
    generator3 = PythonTestCodeGenerator()
    step3_result = generator3.generate_with_contract(step2_result)
    assert isinstance(step3_result, CodeGeneration)
    
    # Step 4
    executor = TestExecutor(ExecutionConfig(headless=True))
    step4_result = await executor.execute_with_contract(step3_result)
    assert isinstance(step4_result, ExecutionResult)
    
    print("✅ Full pipeline with contracts works!")

if __name__ == "__main__":
    # Run async tests
    asyncio.run(test_step1_returns_contract())
    print("✅ Step 1 contract integration test passed")
    
    asyncio.run(test_step2_accepts_contract())
    print("✅ Step 2 contract integration test passed")
    
    test_step3_accepts_contract()
    print("✅ Step 3 contract integration test passed")
    
    asyncio.run(test_step4_accepts_contract())
    print("✅ Step 4 contract integration test passed")
    
    asyncio.run(test_full_pipeline_with_contracts())
    print("✅ Full pipeline contract test passed")