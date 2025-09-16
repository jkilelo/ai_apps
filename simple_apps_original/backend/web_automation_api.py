"""
Simplified FastAPI backend for Web Automation
This provides mock endpoints for testing the simplified frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import time
import random

app = FastAPI(title="Web Automation API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request/Response Models ===
class ExtractRequest(BaseModel):
    url: str

class ExtractResponse(BaseModel):
    elements: List[Dict[str, Any]]

class TestGenerationRequest(BaseModel):
    url: str
    elements: List[Dict[str, Any]]

class TestGenerationResponse(BaseModel):
    tests: List[Dict[str, Any]]

class CodeGenerationRequest(BaseModel):
    tests: List[Dict[str, Any]]
    language: str = "python"
    url: str

class CodeGenerationResponse(BaseModel):
    code: str

class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"

class ExecuteResponse(BaseModel):
    results: Dict[str, Any]

# === API Endpoints ===
@app.post("/api/web-automation/extract", response_model=ExtractResponse)
async def extract_elements(request: ExtractRequest):
    """Extract elements from a webpage"""
    # Simulate processing time
    time.sleep(1)

    # Return mock elements
    return ExtractResponse(
        elements=[
            {"selector": "button#submit", "type": "button", "text": "Submit Form"},
            {"selector": "input#email", "type": "input", "text": "Email field"},
            {"selector": "input#password", "type": "input", "text": "Password field"},
            {"selector": "a.nav-link", "type": "link", "text": "Navigation Link"},
            {"selector": "div.content", "type": "div", "text": "Main content area"},
            {"selector": "h1.title", "type": "heading", "text": "Page Title"},
        ]
    )

@app.post("/api/web-automation/generate-tests", response_model=TestGenerationResponse)
async def generate_tests(request: TestGenerationRequest):
    """Generate test cases from elements"""
    # Simulate processing time
    time.sleep(1)

    # Generate mock tests based on elements
    tests = []
    for i, element in enumerate(request.elements[:3]):  # Use first 3 elements
        tests.append({
            "name": f"Test_{element.get('type', 'element')}_{i+1}",
            "description": f"Verify {element.get('text', 'element')} functionality",
            "steps": [
                f"Navigate to {request.url}",
                f"Locate element: {element.get('selector', 'unknown')}",
                f"Interact with {element.get('type', 'element')}",
                "Verify expected behavior"
            ]
        })

    return TestGenerationResponse(tests=tests)

@app.post("/api/web-automation/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate automation code from tests"""
    # Simulate processing time
    time.sleep(1)

    if request.language == "python":
        code = f"""# Web Automation Script
# Generated for: {request.url}
# Language: Python with Selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_automation():
    # Initialize driver
    driver = webdriver.Chrome()
    driver.get("{request.url}")

    try:
        # Wait for page to load
        wait = WebDriverWait(driver, 10)

"""
        for test in request.tests:
            code += f"""        # {test['name']}
        print("Running: {test['description']}")

"""

        code += """        # Test completed successfully
        print("All tests passed!")

    except Exception as e:
        print(f"Test failed: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_automation()
"""
    else:  # JavaScript
        code = f"""// Web Automation Script
// Generated for: {request.url}
// Language: JavaScript with Playwright

const {{ chromium }} = require('playwright');

async function runAutomation() {{
    const browser = await chromium.launch({{ headless: false }});
    const page = await browser.newPage();

    try {{
        await page.goto('{request.url}');

"""
        for test in request.tests:
            code += f"""        // {test['name']}
        console.log("Running: {test['description']}");

"""

        code += """        // Test completed successfully
        console.log("All tests passed!");

    } catch (error) {
        console.error("Test failed:", error);
    } finally {
        await browser.close();
    }
}

runAutomation();
"""

    return CodeGenerationResponse(code=code)

@app.post("/api/web-automation/execute", response_model=ExecuteResponse)
async def execute_code(request: ExecuteRequest):
    """Execute the generated code (mock execution)"""
    # Simulate processing time
    time.sleep(2)

    # Return mock execution results
    success = random.choice([True, True, True, False])  # 75% success rate

    return ExecuteResponse(
        results={
            "status": "success" if success else "failed",
            "execution_time": f"{random.uniform(1.5, 5.0):.2f}s",
            "tests_run": 3,
            "tests_passed": 3 if success else 2,
            "tests_failed": 0 if success else 1,
            "logs": [
                "Starting automation...",
                "Browser initialized",
                f"Navigating to URL",
                "Running test 1: Test_button_1",
                "✓ Test 1 passed",
                "Running test 2: Test_input_2",
                "✓ Test 2 passed" if success else "✗ Test 2 failed: Element not found",
                "Running test 3: Test_input_3",
                "✓ Test 3 passed",
                "Automation complete"
            ],
            "error": None if success else "Element not found: input#password"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "web-automation-api"}

if __name__ == "__main__":
    print("Starting Web Automation API on http://localhost:8000")
    print("API documentation available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)