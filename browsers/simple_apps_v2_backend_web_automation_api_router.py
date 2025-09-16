"""
API Router for Web Automation Pipeline
Maps frontend steps to backend functions
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import traceback

# Import pipeline functions
from .automation_pipeline import (
    element_extraction,
    test_generation,
    code_generation,
    code_execution,
    run_full_pipeline
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ui", tags=["web-automation"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

# Step 1: Element Extraction
class ElementExtractionRequest(BaseModel):
    url: HttpUrl
    headless: bool = True
    
class ElementExtractionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# Step 2: Test Generation
class TestGenerationRequest(BaseModel):
    extraction_data: Dict[str, Any]  # Output from Step 1
    test_categories: Optional[List[str]] = ["functional", "validation", "navigation"]
    
class TestGenerationResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# Step 3: Code Generation
class CodeGenerationRequest(BaseModel):
    test_data: Dict[str, Any]  # Output from Step 2
    language: str = "python"
    framework: str = "playwright"
    
class CodeGenerationResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# Step 4: Code Execution
class CodeExecutionRequest(BaseModel):
    code_data: Dict[str, Any]  # Output from Step 3
    run_tests: bool = True  # Set to False for dry run
    
class CodeExecutionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# Full Pipeline
class FullPipelineRequest(BaseModel):
    url: HttpUrl
    headless: bool = True
    language: str = "python"
    framework: str = "playwright"
    execute: bool = True
    
class FullPipelineResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/element_extraction", response_model=ElementExtractionResponse)
async def api_element_extraction(request: ElementExtractionRequest):
    """
    Step 1: Extract elements from a webpage
    
    This endpoint:
    - Launches a browser (headless or visible)
    - Navigates to the specified URL
    - Extracts all testable elements
    - Analyzes the page with LLM
    - Returns structured element data
    """
    try:
        logger.info(f"API Step 1: Element Extraction for {request.url}")
        
        # Call the pipeline function
        result = await element_extraction(
            url=str(request.url),
            headless=request.headless
        )
        
        return ElementExtractionResponse(
            success=True,
            data=result,
            error=None,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"API Step 1 Error: {str(e)}")
        return ElementExtractionResponse(
            success=False,
            data=None,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@router.post("/test_generation", response_model=TestGenerationResponse)
async def api_test_generation(request: TestGenerationRequest):
    """
    Step 2: Generate test scenarios from extracted elements
    
    This endpoint:
    - Takes the extraction data from Step 1
    - Generates test scenarios using LLM
    - Creates Gherkin-style test features
    - Returns structured test data
    """
    try:
        logger.info(f"API Step 2: Test Generation")
        
        # Call the pipeline function
        result = await test_generation(
            extraction_data=request.extraction_data
        )
        
        return TestGenerationResponse(
            success=True,
            data=result,
            error=None,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"API Step 2 Error: {str(e)}")
        return TestGenerationResponse(
            success=False,
            data=None,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@router.post("/code_generation", response_model=CodeGenerationResponse)
async def api_code_generation(request: CodeGenerationRequest):
    """
    Step 3: Generate executable test code
    
    This endpoint:
    - Takes the test data from Step 2
    - Generates executable test code
    - Creates page object models
    - Returns generated code files
    """
    try:
        logger.info(f"API Step 3: Code Generation ({request.language}/{request.framework})")
        
        # Call the pipeline function (not async)
        result = code_generation(
            test_data=request.test_data,
            language=request.language,
            framework=request.framework
        )
        
        return CodeGenerationResponse(
            success=True,
            data=result,
            error=None,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"API Step 3 Error: {str(e)}")
        return CodeGenerationResponse(
            success=False,
            data=None,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@router.post("/code_execution", response_model=CodeExecutionResponse)
async def api_code_execution(request: CodeExecutionRequest):
    """
    Step 4: Execute the generated test code
    
    This endpoint:
    - Takes the code data from Step 3
    - Executes the tests (or does a dry run)
    - Collects test results
    - Returns execution report
    """
    try:
        logger.info(f"API Step 4: Code Execution (run_tests={request.run_tests})")
        
        # Call the pipeline function
        result = await code_execution(
            code_data=request.code_data,
            run_tests=request.run_tests
        )
        
        return CodeExecutionResponse(
            success=True,
            data=result,
            error=None,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"API Step 4 Error: {str(e)}")
        return CodeExecutionResponse(
            success=False,
            data=None,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

# ============================================================================
# ADDITIONAL ENDPOINTS
# ============================================================================

@router.post("/full_pipeline", response_model=FullPipelineResponse)
async def api_full_pipeline(request: FullPipelineRequest):
    """
    Run the complete 4-step pipeline in one call
    
    This endpoint:
    - Runs all 4 steps sequentially
    - Returns combined results
    - Useful for automation and testing
    """
    try:
        logger.info(f"API Full Pipeline: Starting for {request.url}")
        
        # Call the full pipeline function
        result = await run_full_pipeline(
            url=str(request.url),
            headless=request.headless,
            language=request.language,
            framework=request.framework,
            execute=request.execute
        )
        
        return FullPipelineResponse(
            success=result.get('success', False),
            data=result,
            error=result.get('error') if not result.get('success') else None,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"API Full Pipeline Error: {str(e)}")
        return FullPipelineResponse(
            success=False,
            data=None,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@router.get("/health")
async def health_check():
    """Health check for the automation pipeline"""
    return {
        "status": "healthy",
        "service": "web-automation-pipeline",
        "endpoints": [
            "/api/ui/element_extraction",
            "/api/ui/test_generation",
            "/api/ui/code_generation",
            "/api/ui/code_execution",
            "/api/ui/full_pipeline"
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/pipeline_info")
async def pipeline_info():
    """Get information about the pipeline steps"""
    return {
        "pipeline": "Web Automation Testing",
        "version": "2.0",
        "steps": [
            {
                "step": 1,
                "name": "Element Extraction",
                "endpoint": "/api/ui/element_extraction",
                "description": "Extract testable elements from a webpage",
                "input": "URL",
                "output": "Extracted elements and metadata"
            },
            {
                "step": 2,
                "name": "Test Generation",
                "endpoint": "/api/ui/test_generation",
                "description": "Generate test scenarios from elements",
                "input": "Extraction data from Step 1",
                "output": "Test scenarios and Gherkin features"
            },
            {
                "step": 3,
                "name": "Code Generation",
                "endpoint": "/api/ui/code_generation",
                "description": "Generate executable test code",
                "input": "Test data from Step 2",
                "output": "Test code, page objects, and config"
            },
            {
                "step": 4,
                "name": "Code Execution",
                "endpoint": "/api/ui/code_execution",
                "description": "Execute generated test code",
                "input": "Code data from Step 3",
                "output": "Test results and reports"
            }
        ],
        "supported_languages": ["python", "javascript", "typescript"],
        "supported_frameworks": ["playwright", "selenium", "puppeteer"],
        "timestamp": datetime.now().isoformat()
    }