"""
FastAPI Server with MongoDB Integration for Web Automation Pipeline
Includes database persistence, session recovery, and caching
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
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import database functions
from ai_db_layer.ui_db import (
    # Core functions
    get_ui_session, save_ui_session, delete_ui_session,
    # Step save functions
    save_browser_setup, save_element_extraction, save_ai_enrichment,
    save_test_generation, save_code_generation,
    # Step load functions
    load_browser_setup, load_element_extraction, load_ai_enrichment,
    load_test_generation, load_code_generation,
    # Recovery functions
    get_resume_point, mark_step_in_progress, mark_step_failed,
    # Utility functions
    list_all_sessions, get_session_summary, clear_session_cache,
    export_session_to_json, get_statistics,
    # Enums
    PipelineStep, StepStatus, LoadStrategy
)

# Import pipeline modules from same directory
from data_types import (
    ExtractionResult,
    ExtractionConfig,
    PageAnalysis,
    TestCategory,
    Element,
    EnrichedElement,
    clean_for_llm,
)

from elements_extractor_no_llm import (
    extract_from_url as extract_no_llm,
    extract_elements as extract_elements_async,
)

from elements_extractor_with_llm import (
    ElementsExtractorWithLLM,
)

try:
    from test_generation_with_llm import (
        TestGenerationEngine,
    )
except ImportError:
    TestGenerationEngine = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Web Automation Pipeline API with Database",
    description="API with MongoDB persistence for web element extraction, test generation, and automation",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExtractRequest(BaseModel):
    url: str = Field(..., description="URL to extract elements from")
    max_elements: int = Field(10, description="Maximum elements for LLM processing")
    use_cache: bool = Field(True, description="Use cached results if available")
    cache_strategy: str = Field("auto", description="Cache strategy: fresh, cached, auto")

class ExtractResponse(BaseModel):
    success: bool
    elements: List[Dict[str, Any]]
    total_found: int
    page_type: str
    extraction_time: float
    from_cache: bool = False
    session_id: Optional[str] = None

class AnalyzeElementsRequest(BaseModel):
    url: str
    elements: Optional[List[Dict[str, Any]]] = None
    max_elements: int = Field(10, description="Maximum elements for AI analysis")
    use_cache: bool = Field(True, description="Use cached results if available")

class TestGenerationRequest(BaseModel):
    url: str
    elements: Optional[List[Dict[str, Any]]] = None
    use_cache: bool = Field(True, description="Use cached results if available")

class TestGenerationResponse(BaseModel):
    success: bool
    tests: List[Dict[str, Any]]
    generation_time: float
    from_cache: bool = False

class CodeGenerationRequest(BaseModel):
    url: str
    tests: Optional[List[Dict[str, Any]]] = None
    language: str = "python"
    framework: str = "playwright"
    use_cache: bool = Field(True, description="Use cached results if available")

class CodeGenerationResponse(BaseModel):
    success: bool
    code: str
    language: str
    framework: str
    from_cache: bool = False

class SessionSummaryResponse(BaseModel):
    url: str
    netloc: str
    page_title: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_complete: bool
    completion_percentage: float
    last_successful_step: Optional[str]
    total_elements: int
    interactive_elements: int
    test_scenarios_count: int
    step_statuses: Dict[str, Dict[str, Any]]

class SessionListResponse(BaseModel):
    sessions: List[Dict[str, Any]]
    total_count: int

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_load_strategy(strategy_str: str) -> LoadStrategy:
    """Convert string to LoadStrategy enum"""
    strategy_map = {
        "fresh": LoadStrategy.FRESH,
        "cached": LoadStrategy.CACHED,
        "auto": LoadStrategy.AUTO
    }
    return strategy_map.get(strategy_str.lower(), LoadStrategy.AUTO)

# ============================================================================
# API ENDPOINTS WITH DATABASE INTEGRATION
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API info"""
    stats = get_statistics()
    return {
        "name": "Web Automation Pipeline API with Database",
        "version": "2.0.0",
        "database_stats": stats,
        "endpoints": [
            "/api/web-automation/extract",
            "/api/web-automation/analyze-elements",
            "/api/web-automation/generate-tests",
            "/api/web-automation/generate-code",
            "/api/web-automation/session?url=<url>",
            "/api/web-automation/sessions",
            "/api/web-automation/resume/{url}",
        ],
    }

@app.post("/api/web-automation/extract", response_model=ExtractResponse)
async def extract_elements(request: ExtractRequest):
    """
    Extract elements from a URL with database caching
    """
    try:
        logger.info(f"Extracting elements from: {request.url}")
        start_time = datetime.now()
        from_cache = False

        # Check for cached results if requested
        if request.use_cache:
            strategy = get_load_strategy(request.cache_strategy)
            cached_data = load_element_extraction(request.url, strategy)

            if cached_data:
                logger.info(f"Using cached extraction for {request.url}")
                from_cache = True

                # Convert cached data to response
                elements = cached_data.get("elements", [])[:50]

                return ExtractResponse(
                    success=True,
                    elements=elements,
                    total_found=cached_data.get("total_elements", len(elements)),
                    page_type=cached_data.get("page_type", "unknown"),
                    extraction_time=cached_data.get("extraction_time", 0),
                    from_cache=True,
                    session_id=cached_data.get("session_id")
                )

        # Mark step as in progress
        mark_step_in_progress(request.url, PipelineStep.ELEMENT_EXTRACTION)

        # Perform extraction with config
        config = ExtractionConfig(headless=True, enable_stealth=True)
        extraction_result = await extract_no_llm(request.url, config)

        if not extraction_result.success:
            mark_step_failed(request.url, PipelineStep.ELEMENT_EXTRACTION, "Extraction failed")
            raise HTTPException(
                status_code=400, detail="Failed to extract elements from URL"
            )

        # Prepare elements for frontend
        elements_for_frontend = []
        for elem in extraction_result.elements[:50]:
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

        # Save to database
        extraction_data = {
            "elements": elements_for_frontend,
            "total_elements": len(extraction_result.elements),
            "interactive_elements": sum(1 for e in extraction_result.elements if e.is_clickable or e.is_editable),
            "extraction_time": duration,
            "page_type": "unknown",  # Will be updated after AI analysis
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

        save_element_extraction(request.url, extraction_data)

        return ExtractResponse(
            success=True,
            elements=elements_for_frontend,
            total_found=len(extraction_result.elements),
            page_type="unknown",
            extraction_time=duration,
            from_cache=False,
            session_id=extraction_data["session_id"]
        )

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        mark_step_failed(request.url, PipelineStep.ELEMENT_EXTRACTION, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web-automation/analyze-elements", response_model=PageAnalysis)
async def analyze_elements_with_ai(request: AnalyzeElementsRequest):
    """
    Analyze and enrich extracted elements with AI, with database caching
    """
    try:
        logger.info(f"Analyzing elements for {request.url}")

        # Check for cached AI enrichment
        if request.use_cache:
            cached_data = load_ai_enrichment(request.url)

            if cached_data:
                logger.info(f"Using cached AI enrichment for {request.url}")
                # Convert cached data to PageAnalysis
                return PageAnalysis(**cached_data.get("page_analysis", {}))

        # If no elements provided, load from previous extraction
        if not request.elements:
            extraction_data = load_element_extraction(request.url)
            if not extraction_data:
                raise HTTPException(status_code=400, detail="No extraction data found. Please extract elements first.")
            request.elements = extraction_data.get("elements", [])

        # Mark step as in progress
        mark_step_in_progress(request.url, PipelineStep.AI_ENRICHMENT)

        # Perform AI analysis
        llm_extractor = ElementsExtractorWithLLM()

        elements = []
        for elem_dict in request.elements[:request.max_elements]:
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

        extraction_result = ExtractionResult(
            url=request.url, success=True, elements=elements
        )

        page_analysis = await llm_extractor.enrich_extracted_elements(
            extraction_result, analyze_with_llm=True, max_elements=request.max_elements
        )

        # Save to database
        enrichment_data = {
            "page_analysis": page_analysis.model_dump() if hasattr(page_analysis, 'model_dump') else page_analysis.__dict__,
            "enrichment_time": 0,  # You can track actual time if needed
            "llm_tokens_used": 0,  # Track if available
        }

        save_ai_enrichment(request.url, enrichment_data)

        return page_analysis

    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        mark_step_failed(request.url, PipelineStep.AI_ENRICHMENT, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web-automation/generate-tests", response_model=TestGenerationResponse)
async def generate_tests(request: TestGenerationRequest):
    """
    Generate test scenarios with database caching
    """
    try:
        logger.info(f"Generating tests for {request.url}")
        start_time = datetime.now()

        # Check for cached tests
        if request.use_cache:
            cached_data = load_test_generation(request.url)

            if cached_data:
                logger.info(f"Using cached tests for {request.url}")
                return TestGenerationResponse(
                    success=True,
                    tests=cached_data.get("scenarios", []),
                    generation_time=cached_data.get("generation_time", 0),
                    from_cache=True
                )

        # Load elements if not provided
        if not request.elements:
            extraction_data = load_element_extraction(request.url)
            if not extraction_data:
                raise HTTPException(status_code=400, detail="No extraction data found. Please extract elements first.")
            request.elements = extraction_data.get("elements", [])

        # Mark step as in progress
        mark_step_in_progress(request.url, PipelineStep.TEST_GENERATION)

        # Generate tests
        tests_for_frontend = []

        # Create basic tests based on element types
        button_count = sum(1 for e in request.elements if e.get("type") == "button")
        input_count = sum(1 for e in request.elements if e.get("type") in ["text_input", "input"])
        form_count = sum(1 for e in request.elements if e.get("type") == "form")

        if form_count > 0:
            tests_for_frontend.append({
                "name": "Test Form Submission",
                "description": "Verify the form can be submitted successfully",
                "steps": [
                    {"keyword": "Given", "text": f"the user is on {request.url}"},
                    {"keyword": "When", "text": "the user fills out all required fields"},
                    {"keyword": "And", "text": "clicks the submit button"},
                    {"keyword": "Then", "text": "the form should be submitted successfully"},
                ],
                "category": "functional",
            })

        if input_count > 0:
            tests_for_frontend.append({
                "name": "Test Input Validation",
                "description": "Verify input fields accept valid data",
                "steps": [
                    {"keyword": "Given", "text": f"the user is on {request.url}"},
                    {"keyword": "When", "text": "the user enters valid data in input fields"},
                    {"keyword": "Then", "text": "the input should be accepted without errors"},
                ],
                "category": "validation",
            })

        duration = (datetime.now() - start_time).total_seconds()

        # Save to database
        test_data = {
            "scenarios": tests_for_frontend,
            "total_scenarios": len(tests_for_frontend),
            "generation_time": duration
        }

        save_test_generation(request.url, test_data)

        return TestGenerationResponse(
            success=True,
            tests=tests_for_frontend,
            generation_time=duration,
            from_cache=False
        )

    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        mark_step_failed(request.url, PipelineStep.TEST_GENERATION, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web-automation/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """
    Generate test code with database caching
    """
    try:
        logger.info(f"Generating {request.framework} code for {request.url}")

        # Check for cached code
        if request.use_cache:
            cached_data = load_code_generation(request.url)

            if cached_data and cached_data.get("framework") == request.framework:
                logger.info(f"Using cached code for {request.url}")
                return CodeGenerationResponse(
                    success=True,
                    code=cached_data.get("code", ""),
                    language=cached_data.get("language", request.language),
                    framework=cached_data.get("framework", request.framework),
                    from_cache=True
                )

        # Load tests if not provided
        if not request.tests:
            test_data = load_test_generation(request.url)
            if not test_data:
                raise HTTPException(status_code=400, detail="No test data found. Please generate tests first.")
            request.tests = test_data.get("scenarios", [])

        # Mark step as in progress
        mark_step_in_progress(request.url, PipelineStep.CODE_GENERATION)

        # Generate simple Playwright code
        code_lines = [
            f"# Generated test code for {request.url}",
            f"# Framework: {request.framework}",
            f"# Generated: {datetime.now().isoformat()}",
            "",
            "import pytest",
            "from playwright.sync_api import Page, expect",
            "",
            f"def test_web_automation(page: Page):",
            f'    """Automated tests for {request.url}"""',
            f'    page.goto("{request.url}")',
            ""
        ]

        for test in request.tests:
            code_lines.append(f"    # Test: {test['name']}")
            for step in test.get("steps", []):
                code_lines.append(f"    # {step['keyword']}: {step['text']}")
            code_lines.append("")

        code = "\n".join(code_lines)

        # Save to database
        code_data = {
            "code": code,
            "language": request.language,
            "framework": request.framework,
            "frameworks": [request.framework],
            "generation_time": 0
        }

        save_code_generation(request.url, code_data)

        return CodeGenerationResponse(
            success=True,
            code=code,
            language=request.language,
            framework=request.framework,
            from_cache=False
        )

    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        mark_step_failed(request.url, PipelineStep.CODE_GENERATION, str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/web-automation/session", response_model=SessionSummaryResponse)
async def get_session(url: str = Query(..., description="URL to get session for")):
    """Get session summary for a URL"""
    try:
        summary = get_session_summary(url)
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionSummaryResponse(**summary)

    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web-automation/sessions", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(10, description="Number of sessions to return"),
    skip: int = Query(0, description="Number of sessions to skip"),
    complete_only: Optional[bool] = Query(None, description="Filter by completion status")
):
    """List all sessions with optional filtering"""
    try:
        sessions = list_all_sessions(limit=limit, skip=skip, filter_complete=complete_only)

        return SessionListResponse(
            sessions=sessions,
            total_count=len(sessions)
        )

    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web-automation/resume")
async def get_resume_point(url: str = Query(..., description="URL to get resume point for")):
    """Get the resume point for a partially completed session"""
    try:
        resume_step = get_resume_point(url)

        if resume_step is None:
            return {"message": "Session is complete", "next_step": None}

        return {
            "message": f"Resume from {resume_step.value}",
            "next_step": resume_step.value,
            "steps_remaining": [
                s.value for s in PipelineStep
                if list(PipelineStep).index(s) >= list(PipelineStep).index(resume_step)
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get resume point: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/web-automation/session")
async def delete_session(url: str = Query(..., description="URL to delete session for")):
    """Delete a session"""
    try:
        success = delete_ui_session(url)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": f"Session for {url} deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web-automation/clear-cache")
async def clear_cache(url: str = Query(..., description="URL to clear cache for"), steps: Optional[List[str]] = None):
    """Clear cache for specific steps or entire session"""
    try:
        if steps:
            pipeline_steps = [PipelineStep(s) for s in steps]
        else:
            pipeline_steps = None

        success = clear_session_cache(url, pipeline_steps)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": f"Cache cleared for {url}", "steps_cleared": steps or "all"}

    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web-automation/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api_server_with_db:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )