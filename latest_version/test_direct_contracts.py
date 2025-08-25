#!/usr/bin/env python3
"""
Test that steps use contracts directly (no backward compatibility)
Written BEFORE implementation as per CODER protocol
"""
import pytest
import asyncio
from pathlib import Path
from data_contracts import (
    ElementExtraction, ExtractedElement,
    GherkinGeneration, GherkinFeature,
    CodeGeneration, GeneratedFile,
    ExecutionResult, TestResult
)

async def test_step1_only_uses_contracts():
    """Test Step 1 ONLY has contract-based extract method"""
    from step1_element_extractor import UltimateElementExtractor, ExtractionConfig
    
    config = ExtractionConfig(timeout=5, headless=True)
    extractor = UltimateElementExtractor(config)
    
    # Should ONLY have extract method that returns contract
    result = await extractor.extract("https://example.com")
    
    # Result should be ElementExtraction contract, NOT List[ElementData]
    assert isinstance(result, ElementExtraction)
    assert not isinstance(result, list)  # Old method returned list
    
    # Should NOT have extract_with_contract method (no duplication)
    assert not hasattr(extractor, 'extract_with_contract')

async def test_step2_only_uses_contracts():
    """Test Step 2 ONLY accepts/returns contracts"""
    from step2_gherkin_generator import GherkinTestGenerator
    
    # Input must be ElementExtraction contract
    input_contract = ElementExtraction(
        url="https://example.com",
        timestamp="2025-08-08T10:00:00",
        success=True,
        elements=[]
    )
    
    generator = GherkinTestGenerator()
    
    # Should ONLY have generate method that accepts contract
    result = await generator.generate(input_contract)
    
    # Result should be GherkinGeneration contract
    assert isinstance(result, GherkinGeneration)
    
    # Should NOT have old generate_gherkin_tests method
    assert not hasattr(generator, 'generate_with_contract')

def test_step3_only_uses_contracts():
    """Test Step 3 ONLY accepts/returns contracts"""
    from step3_code_generator import PythonTestCodeGenerator
    
    # Input must be GherkinGeneration contract
    input_contract = GherkinGeneration(
        source_url="https://example.com",
        timestamp="2025-08-08T10:00:00",
        success=True,
        features=[]
    )
    
    generator = PythonTestCodeGenerator()
    
    # Should ONLY have generate method that accepts contract
    result = generator.generate(input_contract)
    
    # Result should be CodeGeneration contract
    assert isinstance(result, CodeGeneration)
    
    # Should NOT have old generate_from_feature_file method exposed
    assert not hasattr(generator, 'generate_with_contract')

async def test_step4_only_uses_contracts():
    """Test Step 4 ONLY accepts/returns contracts"""
    from step4_test_executor import TestExecutor, ExecutionConfig
    
    # Input must be CodeGeneration contract
    input_contract = CodeGeneration(
        source_features=[],
        timestamp="2025-08-08T10:00:00",
        success=True,
        files=[],
        test_framework="pytest",
        language="python"
    )
    
    config = ExecutionConfig(headless=True)
    executor = TestExecutor(config)
    
    # Should ONLY have execute method that accepts contract
    result = await executor.execute(input_contract)
    
    # Result should be ExecutionResult contract
    assert isinstance(result, ExecutionResult)
    
    # Should NOT have old execute method with test_files parameter
    assert not hasattr(executor, 'execute_with_contract')

async def test_pipeline_flow_with_contracts():
    """Test complete pipeline uses contracts throughout"""
    from step1_element_extractor import UltimateElementExtractor, ExtractionConfig
    from step2_gherkin_generator import GherkinTestGenerator
    from step3_code_generator import PythonTestCodeGenerator
    from step4_test_executor import TestExecutor, ExecutionConfig
    
    # Step 1: URL → ElementExtraction
    extractor = UltimateElementExtractor(ExtractionConfig(timeout=5, headless=True))
    step1_result = await extractor.extract("https://example.com")
    assert isinstance(step1_result, ElementExtraction)
    
    # Step 2: ElementExtraction → GherkinGeneration
    generator2 = GherkinTestGenerator()
    step2_result = await generator2.generate(step1_result)
    assert isinstance(step2_result, GherkinGeneration)
    
    # Step 3: GherkinGeneration → CodeGeneration
    generator3 = PythonTestCodeGenerator()
    step3_result = generator3.generate(step2_result)
    assert isinstance(step3_result, CodeGeneration)
    
    # Step 4: CodeGeneration → ExecutionResult
    executor = TestExecutor(ExecutionConfig(headless=True))
    step4_result = await executor.execute(step3_result)
    assert isinstance(step4_result, ExecutionResult)
    
    print("✅ Complete pipeline uses contracts directly!")

if __name__ == "__main__":
    asyncio.run(test_step1_only_uses_contracts())
    print("✅ Step 1 uses contracts directly")
    
    asyncio.run(test_step2_only_uses_contracts())
    print("✅ Step 2 uses contracts directly")
    
    test_step3_only_uses_contracts()
    print("✅ Step 3 uses contracts directly")
    
    asyncio.run(test_step4_only_uses_contracts())
    print("✅ Step 4 uses contracts directly")
    
    asyncio.run(test_pipeline_flow_with_contracts())
    print("✅ Pipeline flow works with contracts")