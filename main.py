"""
FastAPI Server for Web Automation Pipeline
Connects the backend pipeline to the React frontend
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import our pipeline modules
from ai_frontend_v4.data_types import (
    ExtractionResult,
    ExtractionConfig,
    PageAnalysis,
    TestCategory,
    Element,
    EnrichedElement,
    clean_for_llm,
)

from ai_frontend_v4.elements_extractor_no_llm import (
    extract_from_url as extract_no_llm,
    extract_elements as extract_elements_async,
)

from ai_frontend_v4.elements_extractor_with_llm import (
    ElementsExtractorWithLLM,
)

from ai_frontend_v4.test_generation_with_llm import (
    TestGenerationEngine,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Web Automation Pipeline API",
    description="API for web element extraction, test generation, and automation",
    version="1.0.0",
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class ExtractRequest(BaseModel):
    url: str = Field(..., description="URL to extract elements from")


class ExtractResponse(BaseModel):
    success: bool
    elements: List[Dict[str, Any]]
    total_found: int
    page_type: str
    extraction_time: float


class AnalyzeElementsRequest(BaseModel):
    url: str
    elements: List[Dict[str, Any]]
    max_elements: int = Field(10, description="Maximum elements for AI analysis")


class TestGenerationRequest(BaseModel):
    url: str
    elements: List[Dict[str, Any]]


class TestGenerationResponse(BaseModel):
    success: bool
    tests: List[Dict[str, Any]]
    generation_time: float


class CodeGenerationRequest(BaseModel):
    tests: List[Dict[str, Any]]
    language: str = "python"
    url: str


class CodeGenerationResponse(BaseModel):
    success: bool
    code: str
    language: str


class ExecutionRequest(BaseModel):
    code: str
    language: str


class ExecutionResponse(BaseModel):
    success: bool
    results: Dict[str, Any]
    execution_time: float


# ============================================================================
# GLOBAL STATE (for caching between steps)
# ============================================================================

pipeline_cache = {
    "extraction_result": None,
    "page_analysis": None,
    "test_scenarios": None,
}

# ============================================================================
# API ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Web Automation Pipeline API",
        "version": "1.0.0",
        "endpoints": [
            "/api/ui/extract_elements",
            "/api/ui/analyze_elements",
            "/api/ui/generate_tests",
            "/api/ui/generate_code",
            "/api/ui/execute_code",
        ],
    }


@app.post("/api/ui/extract_elements", response_model=ExtractResponse)
async def extract_elements_ui(request: ExtractRequest):
    """
    Extract elements from a URL using the async extract_elements function
    """
    try:
        logger.info(f"Extracting elements from: {request.url}")
        start_time = datetime.now()

        # Use the async extract_elements function directly
        # Pass the URL string, not the request object
        extraction_result = await extract_elements_async(request.url)

        if not extraction_result.success:
            raise HTTPException(
                status_code=400, detail="Failed to extract elements from URL"
            )

        # Cache the extraction result
        pipeline_cache["extraction_result"] = extraction_result

        # Prepare response with cleaned data
        elements_for_frontend = []
        for elem in extraction_result.elements:
            # Create simplified element for frontend
            elem_dict = {
                "id": elem.id,
                "type": elem.element_type.value if elem.element_type else "unknown",
                "selector": elem.css_selector or elem.xpath or f"#{elem.id}",
                "text": elem.text[:100] if elem.text else "",
                "tag": elem.tag_name,
                "classes": elem.classes if elem.classes else [],
                "is_interactive": elem.is_clickable or elem.is_editable,
                "confidence": elem.confidence,
            }
            elements_for_frontend.append(elem_dict)

        duration = (datetime.now() - start_time).total_seconds()

        return ExtractResponse(
            success=True,
            elements=elements_for_frontend,
            total_found=len(extraction_result.elements),
            page_type="unknown",
            extraction_time=duration,
        )

    except Exception as e:
        import traceback

        logger.error(f"Extraction failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ui/analyze_elements", response_model=PageAnalysis)
async def analyze_elements_with_ai(request: AnalyzeElementsRequest):
    """
    Analyze and enrich extracted elements with AI
    """
    try:
        logger.info(f"Analyzing {len(request.elements)} elements with AI")

        # Create an ElementsExtractorWithLLM instance
        llm_extractor = ElementsExtractorWithLLM()

        # Convert the raw elements back into Element objects for processing
        elements = []
        for elem_dict in request.elements:
            element = Element(
                id=elem_dict.get("id", ""),
                tag_name=elem_dict.get("tag", ""),
                text=elem_dict.get("text", ""),
                css_selector=elem_dict.get("selector", ""),
                classes=elem_dict.get("classes", []),
                is_clickable=elem_dict.get("is_interactive", False),
                confidence=elem_dict.get("confidence", 0.5),
            )
            elements.append(element)

        # Create an ExtractionResult to pass to the enrichment function
        extraction_result = ExtractionResult(
            url=request.url, success=True, elements=elements
        )

        # Enrich the elements with AI analysis and return PageAnalysis directly
        page_analysis = await llm_extractor.enrich_extracted_elements(
            extraction_result, analyze_with_llm=True, max_elements=request.max_elements
        )

        # Return the PageAnalysis object directly - let Pydantic handle serialization
        return page_analysis

    except Exception as e:
        import traceback

        logger.error(f"AI analysis failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ui/generate_tests", response_model=TestGenerationResponse)
async def generate_tests(request: TestGenerationRequest):
    """
    Generate test scenarios from extracted elements
    """
    try:
        logger.info(f"Generating tests for {len(request.elements)} elements")
        start_time = datetime.now()

        # Use cached page analysis if available
        page_analysis = pipeline_cache.get("page_analysis")

        if not page_analysis:
            # Create minimal page analysis from provided elements
            from web_automation_portable_v2.backend.data_types import Element

            elements = [
                Element(
                    id=elem.get("id", f"elem_{i}"),
                    tag_name=elem.get("tag", "div"),
                    text=elem.get("text", ""),
                )
                for i, elem in enumerate(request.elements)
            ]

            page_analysis = PageAnalysis(
                url=request.url,
                elements=elements,
                enriched_elements=[],
                page_type="unknown",
            )

        # Generate mock test scenarios without LLM for now
        # This ensures the flow works end-to-end
        tests_for_frontend = []

        # Generate tests based on element types
        button_count = sum(1 for e in request.elements if e.get("type") == "button")
        input_count = sum(
            1 for e in request.elements if e.get("type") in ["text_input", "input"]
        )
        form_count = sum(1 for e in request.elements if e.get("type") == "form")

        if form_count > 0:
            tests_for_frontend.append(
                {
                    "name": "Test Form Submission",
                    "description": "Verify the form can be submitted successfully",
                    "steps": [
                        {"keyword": "Given", "text": f"the user is on {request.url}"},
                        {
                            "keyword": "When",
                            "text": "the user fills out all required fields",
                        },
                        {"keyword": "And", "text": "clicks the submit button"},
                        {
                            "keyword": "Then",
                            "text": "the form should be submitted successfully",
                        },
                    ],
                    "category": "functional",
                }
            )

        if input_count > 0:
            tests_for_frontend.append(
                {
                    "name": "Test Input Validation",
                    "description": "Verify input fields accept valid data",
                    "steps": [
                        {"keyword": "Given", "text": f"the user is on {request.url}"},
                        {
                            "keyword": "When",
                            "text": "the user enters valid data in input fields",
                        },
                        {
                            "keyword": "Then",
                            "text": "the input should be accepted without errors",
                        },
                    ],
                    "category": "validation",
                }
            )

        if button_count > 0:
            tests_for_frontend.append(
                {
                    "name": "Test Button Interactions",
                    "description": "Verify all buttons are clickable and functional",
                    "steps": [
                        {"keyword": "Given", "text": f"the user is on {request.url}"},
                        {
                            "keyword": "When",
                            "text": "the user clicks on interactive buttons",
                        },
                        {"keyword": "Then", "text": "the expected action should occur"},
                    ],
                    "category": "functional",
                }
            )

        # Add a general test
        tests_for_frontend.append(
            {
                "name": "Test Page Load",
                "description": "Verify the page loads without errors",
                "steps": [
                    {"keyword": "Given", "text": "the user navigates to the URL"},
                    {"keyword": "When", "text": f"the page {request.url} loads"},
                    {
                        "keyword": "Then",
                        "text": "all elements should be visible and functional",
                    },
                ],
                "category": "functional",
            }
        )

        # Cache test scenarios
        pipeline_cache["test_scenarios"] = tests_for_frontend

        duration = (datetime.now() - start_time).total_seconds()

        return TestGenerationResponse(
            success=True, tests=tests_for_frontend, generation_time=duration
        )

    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ui/generate_code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """
    Generate automation code from test scenarios
    """
    try:
        logger.info(
            f"Generating {request.language} code for {len(request.tests)} tests"
        )

        if request.language == "python":
            code = generate_python_selenium_code(request.url, request.tests)
        elif request.language == "javascript":
            code = generate_javascript_playwright_code(request.url, request.tests)
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported language: {request.language}"
            )

        return CodeGenerationResponse(
            success=True, code=code, language=request.language
        )

    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ui/execute_code", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    """
    Execute generated automation code
    Note: This is a simplified implementation.
    In production, this should run in a sandboxed environment.
    """
    try:
        logger.info(f"Executing {request.language} code")
        start_time = datetime.now()

        # For safety, we'll just return a mock result
        # In production, this would execute in a sandboxed environment
        results = {
            "status": "completed",
            "tests_run": 3,
            "tests_passed": 3,
            "tests_failed": 0,
            "message": "Code execution simulated for demo purposes",
            "timestamp": datetime.now().isoformat(),
        }

        duration = (datetime.now() - start_time).total_seconds()

        return ExecutionResponse(success=True, results=results, execution_time=duration)

    except Exception as e:
        logger.error(f"Code execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CODE GENERATION UTILITIES
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Web Automation Pipeline API Server")
    print("=" * 80)
    print()
    print("Starting server on http://localhost:8210")
    print("API documentation: http://localhost:8210/docs")
    print()
    print("Frontend expects endpoints at:")
    print("  - POST /api/ui/extract_elements")
    print("  - POST /api/ui/analyze_elements")
    print("  - POST /api/ui/generate_tests")
    print("  - POST /api/ui/generate_code")
    print("  - POST /api/ui/execute_code")
    print()
    print("=" * 80)

    # Run the server
    # localhost:8210
    uvicorn.run(app, host="localhost", port=8210)
