"""
Test Generation API Router
Step 2: Generate POM Playwright Pytest test cases based on extracted elements
"""

import asyncio
import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

# Active generations
active_generations = {}


class TestGenerationRequest(BaseModel):
    """Request model for test generation"""
    extracted_elements: List[Dict[str, Any]] = Field(..., description="List of extracted web elements")
    test_type: Optional[str] = Field(default="functional", description="Type of tests to generate")
    framework: Optional[str] = Field(default="playwright_pytest", description="Test framework to use")
    include_negative_tests: Optional[bool] = Field(default=True, description="Include negative test cases")
    
    model_config = {
            "example": {
                "extracted_elements": [
                    {
                        "id": "elem_0",
                        "type": "button",
                        "tag": "button",
                        "text": "Submit",
                        "selector": "#submit-btn"
                    }
                ],
                "test_type": "functional",
                "framework": "playwright_pytest",
                "include_negative_tests": True
            }
        }


class TestGenerationResponse(BaseModel):
    """Response model for test generation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")
    started_at: datetime = Field(..., description="Job start time")


class TestGenerationResult(BaseModel):
    """Result model for test generation"""
    job_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    test_files: Optional[Dict[str, str]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=TestGenerationResponse)
async def start_test_generation(
    request: TestGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Start test case generation from extracted elements"""
    job_id = f"gen_{uuid.uuid4().hex[:8]}"
    started_at = datetime.now()
    
    # Validate input
    if not request.extracted_elements:
        raise HTTPException(
            status_code=400,
            detail="No extracted elements provided"
        )
    
    # Store job info
    active_generations[job_id] = {
        "status": "running",
        "started_at": started_at,
        "request": request.model_dump()
    }
    
    # Start generation in background
    background_tasks.add_task(
        generate_tests_task,
        job_id,
        request
    )
    
    logger.info(f"Started test generation job {job_id} for {len(request.extracted_elements)} elements")
    
    return TestGenerationResponse(
        job_id=job_id,
        status="started",
        message="Test generation started successfully",
        started_at=started_at
    )


@router.get("/generate/{job_id}", response_model=TestGenerationResult)
async def get_generation_status(job_id: str):
    """Get the status and results of a test generation job"""
    
    if job_id not in active_generations:
        raise HTTPException(
            status_code=404,
            detail=f"Generation job '{job_id}' not found"
        )
    
    job_data = active_generations[job_id]
    
    return TestGenerationResult(
        job_id=job_id,
        status=job_data["status"],
        started_at=job_data["started_at"],
        completed_at=job_data.get("completed_at"),
        duration=job_data.get("duration"),
        test_cases=job_data.get("test_cases"),
        test_files=job_data.get("test_files"),
        error=job_data.get("error"),
        metadata=job_data.get("metadata")
    )


async def generate_tests_task(job_id: str, request: TestGenerationRequest):
    """Background task to generate test cases"""
    started_at = datetime.now()
    
    try:
        logger.info(f"Executing test generation job {job_id}")
        
        # Group elements by type and page
        elements_by_type = {}
        elements_by_page = {}
        
        for element in request.extracted_elements:
            elem_type = element.get("type", "unknown")
            page_url = element.get("page_url", "unknown")
            
            if elem_type not in elements_by_type:
                elements_by_type[elem_type] = []
            elements_by_type[elem_type].append(element)
            
            if page_url not in elements_by_page:
                elements_by_page[page_url] = []
            elements_by_page[page_url].append(element)
        
        # Generate test cases
        test_cases = []
        
        # Generate functional tests
        if request.test_type in ["functional", "all"]:
            test_cases.extend(generate_functional_tests(request.extracted_elements))
        
        # Generate negative tests
        if request.include_negative_tests:
            test_cases.extend(generate_negative_tests(request.extracted_elements))
        
        # Generate test files
        test_files = generate_test_files(test_cases, request.framework, elements_by_page)
        
        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()
        
        # Update job data
        active_generations[job_id].update({
            "status": "completed",
            "completed_at": completed_at,
            "duration": duration,
            "test_cases": test_cases,
            "test_files": test_files,
            "metadata": {
                "total_test_cases": len(test_cases),
                "total_elements": len(request.extracted_elements),
                "test_type": request.test_type,
                "framework": request.framework,
                "elements_by_type": {k: len(v) for k, v in elements_by_type.items()},
                "pages_covered": list(elements_by_page.keys())
            }
        })
        
        logger.info(f"Completed test generation job {job_id}: {len(test_cases)} test cases generated")
        
    except Exception as e:
        logger.error(f"Test generation job {job_id} failed: {e}")
        
        active_generations[job_id].update({
            "status": "failed",
            "completed_at": datetime.now(),
            "duration": (datetime.now() - started_at).total_seconds(),
            "error": str(e)
        })


def generate_functional_tests(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate functional test cases for elements"""
    test_cases = []
    
    for element in elements:
        elem_type = element.get("type", "unknown")
        elem_text = element.get("text", "")
        elem_selector = element.get("selector", "")
        
        # Generate tests based on element type
        if elem_type == "button":
            test_cases.append({
                "id": f"test_button_click_{len(test_cases)}",
                "name": f"Test clicking {elem_text or 'button'}",
                "type": "functional",
                "element_id": element.get("id"),
                "element": element,  # Include full element data
                "steps": [
                    f"Navigate to page",
                    f"Wait for element '{elem_selector}' to be visible",
                    f"Click on element '{elem_selector}'",
                    f"Verify action completed successfully"
                ],
                "expected_result": "Button click triggers expected action",
                "selector": elem_selector
            })
        
        elif elem_type == "input":
            test_cases.append({
                "id": f"test_input_field_{len(test_cases)}",
                "name": f"Test input field {elem_text or 'input'}",
                "type": "functional",
                "element_id": element.get("id"),
                "element": element,  # Include full element data
                "steps": [
                    f"Navigate to page",
                    f"Wait for element '{elem_selector}' to be visible",
                    f"Enter valid text into '{elem_selector}'",
                    f"Verify input is accepted"
                ],
                "expected_result": "Input field accepts valid text",
                "selector": elem_selector
            })
        
        elif elem_type == "link":
            test_cases.append({
                "id": f"test_link_navigation_{len(test_cases)}",
                "name": f"Test link navigation for {elem_text or 'link'}",
                "type": "functional",
                "element_id": element.get("id"),
                "element": element,  # Include full element data
                "steps": [
                    f"Navigate to page",
                    f"Wait for element '{elem_selector}' to be visible",
                    f"Click on link '{elem_selector}'",
                    f"Verify navigation to correct page"
                ],
                "expected_result": "Link navigates to correct destination",
                "selector": elem_selector,
                "href": element.get("href", "")
            })
    
    return test_cases


def generate_negative_tests(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate negative test cases for elements"""
    test_cases = []
    
    for element in elements:
        elem_type = element.get("type", "unknown")
        elem_selector = element.get("selector", "")
        
        if elem_type == "input":
            test_cases.append({
                "id": f"test_input_invalid_{len(test_cases)}",
                "name": f"Test invalid input for {element.get('text', 'field')}",
                "type": "negative",
                "element_id": element.get("id"),
                "steps": [
                    f"Navigate to page",
                    f"Wait for element '{elem_selector}' to be visible",
                    f"Enter invalid/empty data into '{elem_selector}'",
                    f"Verify appropriate error handling"
                ],
                "expected_result": "Invalid input is handled gracefully with error message",
                "selector": elem_selector
            })
    
    return test_cases


def generate_test_files(test_cases: List[Dict[str, Any]], framework: str, elements_by_page: Dict[str, List]) -> Dict[str, str]:
    """Generate test files in the specified framework format"""
    test_files = {}
    
    if framework == "playwright_pytest":
        # Generate conftest.py
        test_files["conftest.py"] = '''import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    page = browser.new_page()
    yield page
    page.close()
'''
        
        # Generate page objects
        for page_url, elements in elements_by_page.items():
            page_name = page_url.split('/')[-1] or "home"
            page_class = f"""from playwright.sync_api import Page

class {page_name.capitalize()}Page:
    def __init__(self, page: Page):
        self.page = page
        self.url = "{page_url}"
        
        # Element locators
"""
            for element in elements:
                if element.get("selector"):
                    elem_name = element.get("text", "element").lower().replace(" ", "_")
                    page_class += f'        self.{elem_name} = "{element["selector"]}"\n'
            
            page_class += '''
    def navigate(self):
        self.page.goto(self.url)
        
    def wait_for_load(self):
        self.page.wait_for_load_state("networkidle")
'''
            test_files[f"pages/{page_name}_page.py"] = page_class
        
        # Generate test files
        test_class = '''import pytest
from playwright.sync_api import Page

class TestWebUI:
'''
        for test_case in test_cases:
            test_name = test_case["name"].lower().replace(" ", "_")
            test_class += f'''
    def {test_name}(self, page: Page):
        """
        {test_case["name"]}
        Expected: {test_case["expected_result"]}
        """
        # Test implementation
        page.goto("your_url_here")
        page.wait_for_selector("{test_case.get("selector", "")}")
        # Add test steps here
        
'''
        test_files["test_web_ui.py"] = test_class
    
    return test_files


@router.delete("/generate/{job_id}")
async def cancel_generation(job_id: str):
    """Cancel an active generation job"""
    
    if job_id not in active_generations:
        raise HTTPException(
            status_code=404,
            detail=f"Generation job '{job_id}' not found"
        )
    
    job_data = active_generations[job_id]
    
    if job_data["status"] != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Job '{job_id}' is not running (status: {job_data['status']})"
        )
    
    # Mark as cancelled
    job_data["status"] = "cancelled"
    job_data["completed_at"] = datetime.now()
    
    logger.info(f"Cancelled generation job {job_id}")
    
    return {"message": f"Generation job '{job_id}' cancelled successfully"}