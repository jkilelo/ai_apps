"""
Web Automation SDK - Python SDK for the 4-step automation framework
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Configuration classes
@dataclass
class WorkflowConfig:
    """Configuration for workflow initialization"""
    target_url: str
    test_name: str = "Automated Test Suite"
    description: str = ""
    profile: str = "qa_manual_tester"
    browser_type: str = "chrome"
    viewport: Dict[str, int] = None
    include_accessibility: bool = True
    
    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}

@dataclass
class ExecutionConfig:
    """Configuration for test execution"""
    execution_mode: str = "sequential"  # sequential or parallel
    browser: str = "chromium"
    capture_screenshots: bool = True
    max_retries: int = 3
    timeout: int = 300
    cross_browser: bool = False
    browsers: List[str] = None
    include_mobile: bool = False

class TestType(Enum):
    """Types of tests that can be generated"""
    FUNCTIONAL = "functional"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SECURITY = "security"
    VISUAL = "visual"
    ALL = "all"

@dataclass
class WorkflowSession:
    """Workflow session data"""
    session_id: str
    status: str
    created_at: datetime
    current_step: int
    steps_completed: List[str]
    target_data: Optional[Dict[str, Any]] = None
    elements_data: Optional[Dict[str, Any]] = None
    workflow_data: Optional[Dict[str, Any]] = None
    execution_data: Optional[Dict[str, Any]] = None
    results_data: Optional[Dict[str, Any]] = None

@dataclass
class StepResponse:
    """Response from a workflow step"""
    success: bool
    session_id: str
    step: int
    job_id: Optional[str]
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class WebAutomationSDK:
    """
    SDK for Web Automation Testing Framework
    
    Provides programmatic access to the 4-step workflow:
    1. Target Setup - URL analysis & element extraction
    2. Workflow Builder - Test case generation
    3. Test Execution - Running automated tests
    4. Results & Report - Comprehensive reporting
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8002"):
        """
        Initialize the SDK
        
        Args:
            api_base_url: Base URL for the API server
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        await self._ensure_session()
        
        url = f"{self.api_base_url}{endpoint}"
        
        async with self.session.request(method, url, **kwargs) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"API Error ({response.status}): {error_text}")
            
            return await response.json()
    
    # ===== WORKFLOW METHODS =====
    
    async def start_workflow(self, config: WorkflowConfig) -> WorkflowSession:
        """
        Start a new workflow session (Step 1: Target Setup)
        
        Args:
            config: Workflow configuration
            
        Returns:
            WorkflowSession object with session details
        """
        data = {
            "target_url": config.target_url,
            "test_name": config.test_name,
            "description": config.description,
            "browser_type": config.browser_type,
            "viewport": config.viewport,
            "user_profile": config.profile
        }
        
        response = await self._request(
            "POST",
            "/api/v1/web-automation/workflow/step1/target-setup",
            json=data
        )
        
        # Start monitoring the extraction job
        if response.get("job_id"):
            logger.info(f"Started element extraction job: {response['job_id']}")
        
        return WorkflowSession(
            session_id=response["session_id"],
            status="active",
            created_at=datetime.now(),
            current_step=1,
            steps_completed=[]
        )
    
    async def build_workflow(self, session_id: str, 
                           test_types: List[str] = None,
                           include_accessibility: bool = True) -> StepResponse:
        """
        Build test workflow (Step 2: Workflow Builder)
        
        Args:
            session_id: Workflow session ID
            test_types: Types of tests to generate
            include_accessibility: Include accessibility tests
            
        Returns:
            StepResponse with job details
        """
        if test_types is None:
            test_types = ["functional"]
        
        data = {
            "session_id": session_id,
            "test_types": test_types,
            "include_accessibility": include_accessibility
        }
        
        response = await self._request(
            "POST",
            f"/api/v1/web-automation/workflow/{session_id}/step2/build-workflow",
            json=data
        )
        
        return StepResponse(**response)
    
    async def execute_tests(self, session_id: str, 
                          config: ExecutionConfig = None) -> StepResponse:
        """
        Execute generated tests (Step 3: Test Execution)
        
        Args:
            session_id: Workflow session ID
            config: Execution configuration
            
        Returns:
            StepResponse with execution job details
        """
        if config is None:
            config = ExecutionConfig()
        
        data = {
            "session_id": session_id,
            "execution_mode": config.execution_mode,
            "capture_screenshots": config.capture_screenshots,
            "max_retries": config.max_retries
        }
        
        # Handle cross-browser testing
        if config.cross_browser:
            endpoint = f"/api/v1/web-automation/workflow/{session_id}/step3/execute-tests/cross-browser"
            data.update({
                "cross_browser": True,
                "browsers": config.browsers,
                "include_mobile": config.include_mobile
            })
        else:
            endpoint = f"/api/v1/web-automation/workflow/{session_id}/step3/execute-tests"
        
        response = await self._request("POST", endpoint, json=data)
        
        return StepResponse(**response)
    
    async def get_results(self, session_id: str, 
                         format: str = "json") -> Dict[str, Any]:
        """
        Get test results and report (Step 4: Results & Report)
        
        Args:
            session_id: Workflow session ID
            format: Report format (json, html, pdf)
            
        Returns:
            Dictionary containing comprehensive test results
        """
        response = await self._request(
            "GET",
            f"/api/v1/web-automation/workflow/{session_id}/step4/results",
            params={"format": format}
        )
        
        return response.get("data", {})
    
    # ===== STATUS & MONITORING METHODS =====
    
    async def get_workflow_status(self, session_id: str) -> WorkflowSession:
        """
        Get current workflow session status
        
        Args:
            session_id: Workflow session ID
            
        Returns:
            WorkflowSession with current status
        """
        response = await self._request(
            "GET",
            f"/api/v1/web-automation/workflow/{session_id}/status"
        )
        
        return WorkflowSession(
            session_id=response["session_id"],
            status=response["status"],
            created_at=datetime.fromisoformat(response["created_at"]),
            current_step=response["current_step"],
            steps_completed=response["steps_completed"],
            target_data=response.get("target_data"),
            elements_data=response.get("elements_data"),
            workflow_data=response.get("workflow_data"),
            execution_data=response.get("execution_data"),
            results_data=response.get("results_data")
        )
    
    async def get_step_status(self, session_id: str, step: int) -> StepResponse:
        """
        Get status of a specific workflow step
        
        Args:
            session_id: Workflow session ID
            step: Step number (1-4)
            
        Returns:
            StepResponse with step status
        """
        step_endpoints = {
            1: "/step1/status",
            2: "/step2/status", 
            3: "/step3/status"
        }
        
        if step not in step_endpoints:
            raise ValueError(f"Invalid step number: {step}")
        
        response = await self._request(
            "GET",
            f"/api/v1/web-automation/workflow/{session_id}{step_endpoints[step]}"
        )
        
        return StepResponse(**response)
    
    async def wait_for_step_completion(self, session_id: str, step: int,
                                     timeout: int = 300, 
                                     poll_interval: int = 2) -> StepResponse:
        """
        Wait for a workflow step to complete
        
        Args:
            session_id: Workflow session ID
            step: Step number to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            StepResponse when step completes
            
        Raises:
            TimeoutError if step doesn't complete within timeout
        """
        start_time = datetime.now()
        
        while True:
            step_status = await self.get_step_status(session_id, step)
            
            if step_status.status == "completed":
                return step_status
            elif step_status.status == "failed":
                raise Exception(f"Step {step} failed: {step_status.message}")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout:
                raise TimeoutError(f"Step {step} did not complete within {timeout} seconds")
            
            await asyncio.sleep(poll_interval)
    
    # ===== SESSION MANAGEMENT METHODS =====
    
    async def list_sessions(self) -> List[WorkflowSession]:
        """
        List all workflow sessions
        
        Returns:
            List of WorkflowSession objects
        """
        response = await self._request("GET", "/api/v1/web-automation/workflows")
        
        sessions = []
        for session_data in response:
            sessions.append(WorkflowSession(
                session_id=session_data["session_id"],
                status=session_data["status"],
                created_at=datetime.fromisoformat(session_data["created_at"]),
                current_step=session_data["current_step"],
                steps_completed=session_data["steps_completed"],
                target_data=session_data.get("target_data"),
                elements_data=session_data.get("elements_data"),
                workflow_data=session_data.get("workflow_data"),
                execution_data=session_data.get("execution_data"),
                results_data=session_data.get("results_data")
            ))
        
        return sessions
    
    async def delete_session(self, session_id: str) -> Dict[str, str]:
        """
        Delete a workflow session
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            Confirmation message
        """
        response = await self._request(
            "DELETE",
            f"/api/v1/web-automation/workflow/{session_id}"
        )
        
        return response
    
    # ===== CONVENIENCE METHODS =====
    
    async def run_complete_workflow(self, 
                                  config: WorkflowConfig,
                                  execution_config: ExecutionConfig = None,
                                  test_types: List[str] = None,
                                  report_format: str = "json") -> Dict[str, Any]:
        """
        Run a complete workflow from start to finish
        
        Args:
            config: Workflow configuration
            execution_config: Execution configuration
            test_types: Types of tests to generate
            report_format: Format for final report
            
        Returns:
            Dictionary containing complete test results
        """
        if execution_config is None:
            execution_config = ExecutionConfig()
        
        if test_types is None:
            test_types = ["functional"]
        
        # Step 1: Target Setup
        logger.info("Starting workflow...")
        session = await self.start_workflow(config)
        session_id = session.session_id
        
        # Wait for element extraction
        logger.info("Extracting elements...")
        await self.wait_for_step_completion(session_id, 1)
        
        # Step 2: Workflow Builder
        logger.info("Building test workflow...")
        await self.build_workflow(session_id, test_types, config.include_accessibility)
        await self.wait_for_step_completion(session_id, 2)
        
        # Step 3: Test Execution
        logger.info("Executing tests...")
        await self.execute_tests(session_id, execution_config)
        await self.wait_for_step_completion(session_id, 3)
        
        # Step 4: Results & Report
        logger.info("Generating report...")
        results = await self.get_results(session_id, report_format)
        
        return results
    
    async def run_quick_test(self, url: str, 
                           test_name: str = "Quick Test") -> Dict[str, Any]:
        """
        Run a quick test with default settings
        
        Args:
            url: Target URL to test
            test_name: Name for the test
            
        Returns:
            Test results dictionary
        """
        config = WorkflowConfig(
            target_url=url,
            test_name=test_name
        )
        
        return await self.run_complete_workflow(config)
    
    # ===== INDIVIDUAL COMPONENT ACCESS =====
    
    async def extract_elements(self, url: str, 
                             profile: str = "qa_manual_tester") -> Dict[str, Any]:
        """
        Extract elements from a URL (standalone)
        
        Args:
            url: Target URL
            profile: Testing profile
            
        Returns:
            Extracted elements data
        """
        data = {
            "web_page_url": url,
            "profile": profile,
            "include_screenshots": False,
            "max_depth": 1
        }
        
        response = await self._request(
            "POST",
            "/api/v1/element-extraction/extract",
            json=data
        )
        
        job_id = response["job_id"]
        
        # Poll for completion
        while True:
            result = await self._request(
                "GET",
                f"/api/v1/element-extraction/extract/{job_id}"
            )
            
            if result["status"] == "completed":
                return result["extracted_elements"]
            elif result["status"] == "failed":
                raise Exception(f"Element extraction failed: {result.get('error')}")
            
            await asyncio.sleep(2)
    
    async def generate_tests(self, elements: List[Dict[str, Any]], 
                           test_type: str = "functional") -> Dict[str, Any]:
        """
        Generate tests from elements (standalone)
        
        Args:
            elements: List of extracted elements
            test_type: Type of tests to generate
            
        Returns:
            Generated test cases
        """
        data = {
            "extracted_elements": elements,
            "test_type": test_type,
            "framework": "playwright_pytest",
            "include_negative_tests": True
        }
        
        response = await self._request(
            "POST",
            "/api/v1/test-generation/generate",
            json=data
        )
        
        job_id = response["job_id"]
        
        # Poll for completion
        while True:
            result = await self._request(
                "GET",
                f"/api/v1/test-generation/generate/{job_id}"
            )
            
            if result["status"] == "completed":
                return {
                    "test_cases": result["test_cases"],
                    "test_files": result["test_files"]
                }
            elif result["status"] == "failed":
                raise Exception(f"Test generation failed: {result.get('error')}")
            
            await asyncio.sleep(2)
    
    async def close(self):
        """Close the SDK session"""
        if self.session:
            await self.session.close()
            self.session = None

# Example usage
async def example_usage():
    """Example of using the SDK"""
    # Using context manager
    async with WebAutomationSDK() as sdk:
        # Run complete workflow
        config = WorkflowConfig(
            target_url="https://example.com",
            test_name="Example Test Suite",
            profile="qa_tester"
        )
        
        results = await sdk.run_complete_workflow(config)
        print(f"Test Results: {results}")
    
    # Or manual session management
    sdk = WebAutomationSDK()
    try:
        # Run quick test
        results = await sdk.run_quick_test("https://example.com")
        print(f"Quick Test Results: {results}")
    finally:
        await sdk.close()

if __name__ == "__main__":
    asyncio.run(example_usage())