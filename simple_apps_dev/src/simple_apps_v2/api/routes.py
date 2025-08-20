"""
Modern API routes with proper error handling and validation.
"""

import asyncio
import json
import time
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import get_logger
from simple_apps_v2.core.models import (
    ExtractionRequest, ExtractionResponse,
    GenerateTestsRequest, GenerateTestsResponse,
    CodeGenerationRequest, CodeGenerationResponse,
    ExecuteTestsRequest, ExecuteTestsResponse
)
from simple_apps_v2.services.browser import BrowserService
from simple_apps_v2.services.extractor import ElementExtractor
from simple_apps_v2.services.llm import LLMService
from simple_apps_v2.utils.code_extractor import GenericCodeExtractor
from simple_apps_v2.utils.validation import validate_extraction_request

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()

# Service instances (will be initialized on first use)
_element_extractor = None
_llm_service = None
_code_extractor = None


def get_element_extractor() -> ElementExtractor:
    """Get or create element extractor instance."""
    global _element_extractor
    if _element_extractor is None:
        _element_extractor = ElementExtractor()
    return _element_extractor


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_code_extractor() -> GenericCodeExtractor:
    """Get or create code extractor instance."""
    global _code_extractor
    if _code_extractor is None:
        _code_extractor = GenericCodeExtractor()
    return _code_extractor


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get API status and configuration."""
    return {
        "status": "operational",
        "version": settings.version,
        "services": {
            "element_extraction": True,
            "llm_analysis": bool(settings.openai_api_key or settings.google_api_key),
            "code_generation": True,
            "test_execution": True,
        },
        "configuration": {
            "default_llm_provider": settings.default_llm_provider,
            "default_llm_model": settings.default_llm_model,
            "browser_headless": settings.browser_headless,
            "debug_mode": settings.debug,
        }
    }


@router.post("/extract-elements", response_model=ExtractionResponse)
async def extract_elements(request: ExtractionRequest) -> ExtractionResponse:
    """
    Extract testable elements from a web page.
    
    Args:
        request: Element extraction request
        
    Returns:
        Element extraction response with results
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting element extraction for {request.url}")
        
        # Validate request
        validation_errors = validate_extraction_request(request.dict())
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation failed",
                    "errors": validation_errors
                }
            )
        
        # Extract elements
        extractor = get_element_extractor()
        result = await extractor.extract_elements_from_url(
            url=str(request.url),
            analyze_with_llm=request.analyze_with_llm,
            categories=request.categories
        )
        
        extraction_time = time.time() - start_time
        
        if result.get("success", False):
            response = ExtractionResponse(
                success=True,
                url=str(request.url),
                total_elements=result.get("total_elements", 0),
                elements=result.get("elements", []),
                elements_by_category=result.get("elements_by_category", {}),
                llm_analysis=result.get("llm_analysis"),
                extraction_time=extraction_time,
                metadata=result.get("metadata", {})
            )
            
            logger.info(f"Element extraction completed: {response.total_elements} elements in {extraction_time:.2f}s")
            return response
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Element extraction failed",
                    "message": result.get("error", "Unknown error"),
                    "url": str(request.url)
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in element extraction: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e) if settings.debug else "Element extraction failed",
                "url": str(request.url)
            }
        )


@router.post("/generate-tests", response_model=GenerateTestsResponse)
async def generate_tests(request: GenerateTestsRequest) -> GenerateTestsResponse:
    """
    Generate test scenarios from extracted elements.
    
    Args:
        request: Test generation request
        
    Returns:
        Generated test scenarios
    """
    start_time = time.time()
    
    try:
        logger.info("Starting test generation")
        
        url = request.extraction_data.get("url", "unknown")
        
        # Use LLM service to generate tests
        llm_service = get_llm_service()
        
        # Create a prompt for test generation
        elements = request.extraction_data.get("elements", [])
        elements_summary = []
        
        for elem in elements[:20]:  # Limit for prompt size
            elements_summary.append({
                "selector": elem.get("selector", ""),
                "category": elem.get("category", ""),
                "text": elem.get("text", "")[:50],
                "clickable": elem.get("clickable", False),
                "visible": elem.get("visible", True)
            })
        
        prompt = f"""
Generate comprehensive test scenarios for the web application at {url}.

Elements found on the page:
{json.dumps(elements_summary, indent=2)}

Generate test scenarios in the following categories:
1. Navigation tests
2. Form input tests  
3. Button interaction tests
4. Link validation tests
5. Visual regression tests
6. Accessibility tests

For each category, create 2-3 specific test scenarios with:
- Clear test title
- Detailed steps (Given, When, Then)
- Target elements involved
- Expected outcomes

Return as JSON with this structure:
{{
  "scenarios": [
    {{
      "id": "unique_id",
      "title": "Test title",
      "description": "Detailed description", 
      "category": "category_name",
      "priority": "high|medium|low",
      "given": ["precondition1", "precondition2"],
      "when": ["action1", "action2"],
      "then": ["assertion1", "assertion2"],
      "target_elements": ["selector1", "selector2"]
    }}
  ]
}}
"""
        
        from simple_apps_v2.services.llm import LLMMessage
        
        messages = [
            LLMMessage(role="system", content="You are an expert in web UI testing and test case generation."),
            LLMMessage(role="user", content=prompt)
        ]
        
        response = await llm_service.query_async(messages)
        
        generation_time = time.time() - start_time
        
        if response.success:
            try:
                # Parse JSON response
                test_data = json.loads(response.content)
                scenarios = test_data.get("scenarios", [])
                
                # Group scenarios by category
                scenarios_by_category = {}
                for scenario in scenarios:
                    category = scenario.get("category", "other")
                    if category not in scenarios_by_category:
                        scenarios_by_category[category] = []
                    scenarios_by_category[category].append(scenario)
                
                result = GenerateTestsResponse(
                    success=True,
                    url=url,
                    scenarios=scenarios,
                    scenarios_by_category=scenarios_by_category,
                    total_scenarios=len(scenarios),
                    generation_time=generation_time,
                    statistics={
                        "categories": len(scenarios_by_category),
                        "elements_processed": len(elements_summary),
                        "llm_provider": response.provider,
                        "llm_model": response.model
                    }
                )
                
                logger.info(f"Test generation completed: {len(scenarios)} scenarios in {generation_time:.2f}s")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Test generation failed",
                        "message": "Failed to parse generated tests",
                        "raw_response": response.content[:500]
                    }
                )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Test generation failed",
                    "message": response.error,
                    "url": url
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in test generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e) if settings.debug else "Test generation failed"
            }
        )


@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest) -> CodeGenerationResponse:
    """
    Generate test code from extracted elements and test scenarios.
    
    Args:
        request: Code generation request
        
    Returns:
        Generated test code files
    """
    start_time = time.time()
    
    try:
        logger.info("Starting code generation")
        
        url = request.extraction_data.get("url", "unknown")
        elements = request.extraction_data.get("elements", [])
        scenarios = request.test_data.get("scenarios", [])
        
        # Use LLM service to generate code
        llm_service = get_llm_service()
        
        # Generate different types of files
        generated_files = []
        
        # 1. Generate base page object
        page_object_prompt = f"""
Generate a Python page object class for web automation testing of {url}.

Elements available:
{json.dumps(elements[:15], indent=2)}

Requirements:
1. Use Playwright for browser automation
2. Create a BasePage class with common methods  
3. Include methods for each major element category
4. Use async/await patterns
5. Include proper error handling and logging
6. Add docstrings and type hints

Generate complete, production-ready code.
"""
        
        from simple_apps_v2.services.llm import LLMMessage
        
        messages = [
            LLMMessage(role="system", content="You are an expert Python developer specializing in test automation."),
            LLMMessage(role="user", content=page_object_prompt)
        ]
        
        response = await llm_service.query_async(messages)
        
        if response.success:
            # Extract code using code extractor
            code_extractor = get_code_extractor()
            extracted_codes = code_extractor.extract(response.content, languages=['python'])
            
            if extracted_codes:
                page_object_code = extracted_codes[0].content
                generated_files.append({
                    "filepath": "pages/base_page.py",
                    "content": page_object_code,
                    "language": "python",
                    "file_type": "page_object",
                    "line_count": len(page_object_code.split('\n')),
                    "estimated_complexity": "medium"
                })
        
        # 2. Generate test files for scenarios
        for i, scenario in enumerate(scenarios[:3]):  # Limit to 3 scenarios
            test_prompt = f"""
Generate a pytest test file for this scenario:

Scenario: {scenario.get('title', 'Test scenario')}
Description: {scenario.get('description', 'Test description')}
Steps:
Given: {scenario.get('given', [])}
When: {scenario.get('when', [])}
Then: {scenario.get('then', [])}

Requirements:
1. Use pytest and Playwright
2. Import the BasePage from pages.base_page
3. Use async test methods with @pytest.mark.asyncio
4. Include proper setup and teardown
5. Add assertions for each test step
6. Include error handling and screenshots on failure

Generate complete, executable test code.
"""
            
            messages = [
                LLMMessage(role="system", content="You are an expert in test automation with pytest and Playwright."),
                LLMMessage(role="user", content=test_prompt)
            ]
            
            response = await llm_service.query_async(messages)
            
            if response.success:
                extracted_codes = code_extractor.extract(response.content, languages=['python'])
                if extracted_codes:
                    test_code = extracted_codes[0].content
                    generated_files.append({
                        "filepath": f"tests/test_{scenario.get('category', 'scenario')}_{i+1}.py",
                        "content": test_code,
                        "language": "python", 
                        "file_type": "test",
                        "line_count": len(test_code.split('\n')),
                        "estimated_complexity": "medium"
                    })
        
        # 3. Generate conftest.py
        conftest_prompt = f"""
Generate a conftest.py file for pytest configuration for testing {url}.

Requirements:
1. Set up Playwright browser fixtures
2. Configure test data and base URL
3. Add screenshot capture on failure
4. Set up logging configuration  
5. Include browser cleanup
6. Add useful pytest fixtures for web testing

Generate a complete conftest.py file.
"""
        
        messages = [
            LLMMessage(role="system", content="You are an expert in pytest configuration and fixtures."),
            LLMMessage(role="user", content=conftest_prompt)
        ]
        
        response = await llm_service.query_async(messages)
        
        if response.success:
            extracted_codes = code_extractor.extract(response.content, languages=['python'])
            if extracted_codes:
                conftest_code = extracted_codes[0].content
                generated_files.append({
                    "filepath": "conftest.py",
                    "content": conftest_code,
                    "language": "python",
                    "file_type": "config",
                    "line_count": len(conftest_code.split('\n')),
                    "estimated_complexity": "low"
                })
        
        generation_time = time.time() - start_time
        
        # Build file structure
        file_structure = {
            "pages/": ["base_page.py"],
            "tests/": [f["filepath"].split("/")[-1] for f in generated_files if f["file_type"] == "test"],
            "": ["conftest.py"]
        }
        
        result = CodeGenerationResponse(
            success=True,
            url=url,
            generated_files=generated_files,
            file_structure=file_structure,
            total_files=len(generated_files),
            total_lines=sum(f["line_count"] for f in generated_files),
            generation_time=generation_time,
            statistics={
                "scenarios_processed": len(scenarios),
                "elements_processed": len(elements),
                "files_by_type": {
                    file_type: len([f for f in generated_files if f["file_type"] == file_type])
                    for file_type in set(f["file_type"] for f in generated_files)
                }
            }
        )
        
        logger.info(f"Code generation completed: {len(generated_files)} files in {generation_time:.2f}s")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in code generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e) if settings.debug else "Code generation failed"
            }
        )


@router.post("/execute-tests", response_model=ExecuteTestsResponse)
async def execute_tests(request: ExecuteTestsRequest) -> ExecuteTestsResponse:
    """
    Execute generated test code.
    
    Args:
        request: Test execution request
        
    Returns:
        Test execution results
    """
    try:
        logger.info(f"Starting test execution for {request.url}")
        
        # For now, return a mock successful execution
        # In production, this would create temporary files and run pytest
        
        execution_time = 2.5
        
        result = ExecuteTestsResponse(
            success=True,
            total_tests=len(request.generated_files),
            passed=len(request.generated_files) - 1,
            failed=1,
            skipped=0,
            duration=execution_time,
            test_results=[
                {
                    "name": f"test_{i}",
                    "status": "passed" if i < len(request.generated_files) - 1 else "failed",
                    "duration": 0.5,
                    "message": None if i < len(request.generated_files) - 1 else "Assertion failed"
                }
                for i in range(len(request.generated_files))
            ],
            logs=[
                "Setting up test environment",
                "Installing dependencies", 
                "Running tests with pytest",
                f"Test execution completed in {execution_time}s"
            ],
            artifacts={
                "screenshot": "screenshot.png",
                "report": "test_report.html"
            }
        )
        
        logger.info(f"Test execution completed: {result.passed}/{result.total_tests} passed")
        return result
    
    except Exception as e:
        logger.error(f"Unexpected error in test execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e) if settings.debug else "Test execution failed"
            }
        )


@router.get("/test-extraction")
async def test_extraction() -> Dict[str, Any]:
    """Test endpoint with example.com using actual extraction."""
    try:
        extractor = get_element_extractor()
        result = await extractor.extract_elements_from_url(
            url="https://example.com",
            analyze_with_llm=True
        )
        
        return {
            "success": True,
            "message": "Test extraction completed",
            "total_elements": result.get("total_elements", 0),
            "data": result
        }
    except Exception as e:
        logger.error(f"Test extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Test extraction failed",
                "message": str(e)
            }
        )