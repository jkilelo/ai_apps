"""Web Automation Router with improved error handling"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel, Field, validator
import asyncio
import logging

from services.web_automation_service import WebAutomationService
from services.validation import validate_url, validate_code_input
from services.cache import CacheService

router = APIRouter()
web_automation_service = WebAutomationService()
cache_service = CacheService()
logger = logging.getLogger(__name__)

# Request/Response Models
class ExtractElementsRequest(BaseModel):
    url: str = Field(..., description="URL to extract elements from")
    wait_time: int = Field(5, ge=1, le=30, description="Wait time for page load")
    
    @validator('url')
    def validate_url_format(cls, v):
        validation = validate_url(v)
        if not validation["valid"]:
            raise ValueError(validation["reason"])
        return v

class ExtractElementsResponse(BaseModel):
    elements: List[Dict[str, Any]]
    url: str
    extraction_time: float
    total_elements: int

class GenerateTestsRequest(BaseModel):
    elements: List[Dict[str, Any]]
    url: str
    test_framework: str = Field("pytest", description="Test framework to use")

class GenerateTestsResponse(BaseModel):
    gherkin_tests: str
    test_count: int
    framework: str

class GenerateCodeRequest(BaseModel):
    gherkin_tests: str
    language: str = Field("python", description="Programming language")
    framework: str = Field("playwright", description="Automation framework")

class GenerateCodeResponse(BaseModel):
    python_code: str
    language: str
    framework: str
    estimated_runtime: str

class ExecuteCodeRequest(BaseModel):
    python_code: str
    timeout: int = Field(30, ge=5, le=300, description="Execution timeout in seconds")

class ExecuteCodeResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    logs: List[str] = []

# Endpoints
@router.post("/web_automation/extract_elements", response_model=ExtractElementsResponse)
async def extract_elements(request: ExtractElementsRequest, req: Request):
    """
    Extract interactive elements from a webpage
    
    Features:
    - Intelligent element detection
    - Accessibility attributes extraction
    - Performance optimized
    - Caching support
    """
    try:
        # Check cache
        cache_key = f"elements:{request.url}:{request.wait_time}"
        cached = await cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache hit for URL: {request.url}")
            return ExtractElementsResponse(**cached)
        
        # Extract elements
        start_time = asyncio.get_event_loop().time()
        
        result = await web_automation_service.extract_elements(
            url=request.url,
            wait_time=request.wait_time
        )
        
        extraction_time = asyncio.get_event_loop().time() - start_time
        
        response_data = {
            "elements": result["elements"],
            "url": request.url,
            "extraction_time": round(extraction_time, 3),
            "total_elements": len(result["elements"])
        }
        
        # Cache successful result
        await cache_service.set(cache_key, response_data, ttl=1800)  # 30 minutes
        
        return ExtractElementsResponse(**response_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Element extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract elements from webpage"
        )

@router.post("/web_automation/generate_gherkin_tests", response_model=GenerateTestsResponse)
async def generate_gherkin_tests(request: GenerateTestsRequest, req: Request):
    """
    Generate Gherkin test scenarios from extracted elements
    
    Features:
    - Intelligent test scenario generation
    - Multiple test types (functional, accessibility, performance)
    - Customizable test frameworks
    """
    try:
        if not request.elements:
            raise ValueError("No elements provided")
        
        # Generate tests
        result = await web_automation_service.generate_gherkin_tests(
            elements=request.elements,
            url=request.url,
            framework=request.test_framework
        )
        
        return GenerateTestsResponse(
            gherkin_tests=result["gherkin_tests"],
            test_count=result["test_count"],
            framework=request.test_framework
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Test generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate test scenarios"
        )

@router.post("/web_automation/generate_python_code", response_model=GenerateCodeResponse)
async def generate_python_code(request: GenerateCodeRequest, req: Request):
    """
    Generate executable Python code from Gherkin tests
    
    Features:
    - Multiple framework support (Playwright, Selenium, Cypress)
    - Error handling and retry logic
    - Performance optimizations
    """
    try:
        if not request.gherkin_tests:
            raise ValueError("No Gherkin tests provided")
        
        # Generate code
        result = await web_automation_service.generate_python_code(
            gherkin_tests=request.gherkin_tests,
            language=request.language,
            framework=request.framework
        )
        
        return GenerateCodeResponse(
            python_code=result["code"],
            language=request.language,
            framework=request.framework,
            estimated_runtime=result.get("estimated_runtime", "Unknown")
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Code generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Python code"
        )

@router.post("/web_automation/execute_python_code", response_model=ExecuteCodeResponse)
async def execute_python_code(request: ExecuteCodeRequest, req: Request):
    """
    Execute Python automation code in a sandboxed environment
    
    Features:
    - Secure code execution
    - Timeout protection
    - Detailed logging
    - Resource limiting
    """
    try:
        # Validate code
        validation = validate_code_input(request.python_code, "python")
        if not validation["valid"]:
            raise ValueError(validation["reason"])
        
        # Execute code
        start_time = asyncio.get_event_loop().time()
        
        result = await web_automation_service.execute_code(
            code=request.python_code,
            timeout=request.timeout
        )
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return ExecuteCodeResponse(
            success=result["success"],
            output=result.get("output"),
            error=result.get("error"),
            execution_time=round(execution_time, 3),
            logs=result.get("logs", [])
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"Code execution timed out after {request.timeout} seconds"
        )
    except Exception as e:
        logger.error(f"Code execution failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute code"
        )

@router.get("/web_automation/templates/{template_name}")
async def get_code_template(template_name: str):
    """Get pre-built code templates for common scenarios"""
    templates = {
        "login_test": await web_automation_service.get_template("login_test"),
        "form_validation": await web_automation_service.get_template("form_validation"),
        "navigation_test": await web_automation_service.get_template("navigation_test"),
        "accessibility_test": await web_automation_service.get_template("accessibility_test")
    }
    
    if template_name not in templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_name}' not found"
        )
    
    return {
        "template_name": template_name,
        "code": templates[template_name],
        "description": f"Template for {template_name.replace('_', ' ')}"
    }

@router.get("/web_automation/frameworks")
async def get_supported_frameworks():
    """Get list of supported automation frameworks"""
    return {
        "frameworks": [
            {
                "name": "playwright",
                "description": "Modern web automation by Microsoft",
                "languages": ["python", "javascript", "java", "csharp"],
                "features": ["auto-wait", "web-sockets", "multiple-contexts"]
            },
            {
                "name": "selenium",
                "description": "Classic web automation framework",
                "languages": ["python", "javascript", "java", "csharp", "ruby"],
                "features": ["cross-browser", "grid-support", "mobile-testing"]
            },
            {
                "name": "puppeteer",
                "description": "Headless Chrome automation",
                "languages": ["javascript", "typescript"],
                "features": ["fast", "chrome-only", "pdf-generation"]
            }
        ]
    }