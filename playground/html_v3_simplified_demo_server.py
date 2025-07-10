#!/usr/bin/env python3
"""
FastAPI Demo Server for Simplified HTML Form Chain Engine v3.0

This server demonstrates the simplified form chain engine that addresses all the
issues found in the original implementation:
- No JSON serialization/deserialization in hidden fields
- Server-side session storage
- Pure semantic HTML with minimal JavaScript
- POST-Redirect-GET pattern for clean form handling

Run with: python html_v3_simplified_demo_server.py
Then visit: http://localhost:8038
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from datetime import datetime

# Import the simplified engine and examples
from html_v3_simplified import SimplifiedFormChain, FormStep
from html_v3_examples import (
    DataSourceRequest, DataSourceResponse, DataSourceProcessor,
    QualityCheckRequest, QualityCheckResponse, QualityCheckProcessor,
    QualityActionRequest, QualityActionResponse, QualityActionProcessor
)

app = FastAPI(title="Simplified Form Chain Engine v3 Demo")


# Create the data quality chain using simplified engine
def create_simplified_data_quality_chain() -> SimplifiedFormChain:
    """Create the data quality check form chain with simplified engine"""
    
    steps = [
        FormStep(
            id="step_1",
            title="Select Data Source",
            description="Connect to your database and select a table to analyze",
            request_model=DataSourceRequest,
            response_model=DataSourceResponse,
            processor=DataSourceProcessor(),
            is_entry_point=True,
            next_step_id="step_2"
        ),
        FormStep(
            id="step_2",
            title="Configure Quality Checks",
            description="Select columns and quality checks to perform",
            request_model=QualityCheckRequest,
            response_model=QualityCheckResponse,
            processor=QualityCheckProcessor(),
            next_step_id="step_3"
        ),
        FormStep(
            id="step_3",
            title="Take Action",
            description="Review results and choose actions to take",
            request_model=QualityActionRequest,
            response_model=QualityActionResponse,
            processor=QualityActionProcessor(),
            is_exit_point=True
        )
    ]
    
    return SimplifiedFormChain(steps=steps)


# Initialize the chain
chain = create_simplified_data_quality_chain()


@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Display the homepage with explanation"""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simplified Form Chain Engine v3 - Demo</title>
    <style>
        body {
            font-family: system-ui, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        
        .hero {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }
        
        .hero h1 {
            margin: 0 0 20px 0;
            font-size: 2.5em;
        }
        
        .hero p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
        }
        
        .feature-box {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .feature-box h2 {
            margin-top: 0;
            color: #333;
        }
        
        .improvements {
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            padding: 20px;
            margin: 20px 0;
        }
        
        .improvements h3 {
            margin-top: 0;
            color: #2e7d32;
        }
        
        .improvements ul {
            margin: 10px 0;
        }
        
        .comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        
        .comparison-col {
            padding: 20px;
            border-radius: 4px;
        }
        
        .old-way {
            background: #ffebee;
            border: 1px solid #ffcdd2;
        }
        
        .new-way {
            background: #e8f5e9;
            border: 1px solid #c8e6c9;
        }
        
        .comparison-col h4 {
            margin-top: 0;
        }
        
        .start-btn {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 4px;
            font-size: 1.1em;
            transition: background 0.3s;
        }
        
        .start-btn:hover {
            background: #45a049;
        }
        
        .center {
            text-align: center;
            margin: 40px 0;
        }
        
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="hero">
        <h1>✨ Simplified Form Chain Engine v3</h1>
        <p>A cleaner, more robust implementation with server-side sessions</p>
    </div>
    
    <div class="container">
        <div class="feature-box">
            <h2>What's New in the Simplified Version?</h2>
            <p>
                After experiencing issues with the original implementation, we've completely
                redesigned the form chain engine to be simpler, more reliable, and bug-free.
            </p>
            
            <div class="improvements">
                <h3>🚀 Key Improvements</h3>
                <ul>
                    <li><strong>Server-side sessions</strong> - No more JSON in hidden fields</li>
                    <li><strong>Pure semantic HTML</strong> - Minimal JavaScript, maximum compatibility</li>
                    <li><strong>POST-Redirect-GET pattern</strong> - Clean browser history and refresh handling</li>
                    <li><strong>Type-safe form handling</strong> - Direct HTML to Pydantic conversion</li>
                    <li><strong>No chain instance tracking</strong> - Sessions handle everything</li>
                </ul>
            </div>
        </div>
        
        <div class="feature-box">
            <h2>Architecture Comparison</h2>
            <div class="comparison">
                <div class="comparison-col old-way">
                    <h4>❌ Original Implementation</h4>
                    <ul>
                        <li>Complex state → JSON → Base64 → Hidden field</li>
                        <li>JavaScript-heavy form submission</li>
                        <li>Chain instance IDs in URLs</li>
                        <li>JSON serialization errors</li>
                        <li>Client-side state management</li>
                    </ul>
                </div>
                <div class="comparison-col new-way">
                    <h4>✅ Simplified Implementation</h4>
                    <ul>
                        <li>Direct server-side session storage</li>
                        <li>Standard HTML form POST</li>
                        <li>Clean session-based routing</li>
                        <li>No JSON in forms</li>
                        <li>Server manages all state</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="feature-box">
            <h2>How It Works</h2>
            <ol>
                <li><strong>Session Creation</strong> - When you start, a session ID is created and stored in the URL</li>
                <li><strong>Form Rendering</strong> - Each step renders pure HTML with proper form fields</li>
                <li><strong>Form Submission</strong> - Standard POST submission, no JavaScript required</li>
                <li><strong>Processing</strong> - Server validates with Pydantic and processes the step</li>
                <li><strong>Redirect</strong> - After processing, redirect to next step (PRG pattern)</li>
                <li><strong>State Persistence</strong> - All state stored server-side, accessible via session</li>
            </ol>
        </div>
        
        <div class="feature-box">
            <h2>Try the Demo</h2>
            <p>
                Experience the same data quality check workflow, but with a much more
                robust and reliable implementation. No more "Chain instance not found" errors!
            </p>
            
            <div class="center">
                <a href="/start" class="start-btn">Start Data Quality Check Demo</a>
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)


@app.get("/start")
async def start_workflow():
    """Create a new session and redirect to first step"""
    session_id = chain.create_session()
    return RedirectResponse(f"/form/{session_id}/step_1", status_code=303)


@app.get("/form/{session_id}/{step_id}", response_class=HTMLResponse)
async def show_form(session_id: str, step_id: str, errors: str = ""):
    """Display a form step"""
    # Parse errors if any
    error_list = errors.split("|") if errors else None
    
    # Render the form
    html = chain.render_step(step_id, session_id, error_list)
    return HTMLResponse(content=html)


@app.post("/process/{session_id}/{step_id}")
async def process_form(session_id: str, step_id: str, request: Request):
    """Process form submission and redirect"""
    # Get form data
    form_data = await request.form()
    form_dict = {}
    
    # Convert form data to dict, handling arrays
    for key, value in form_data.items():
        if key.endswith("[]"):
            # Handle array fields
            base_key = key[:-2]
            if base_key not in form_dict:
                form_dict[base_key] = []
            form_dict[base_key].append(value)
        else:
            form_dict[key] = value
    
    # Process the step
    next_step, error = await chain.process_step(session_id, step_id, form_dict)
    
    if error:
        # Redirect back to form with errors
        return RedirectResponse(
            f"/form/{session_id}/{step_id}?errors={error}",
            status_code=303
        )
    elif next_step == "completed":
        # Redirect to completion page
        return RedirectResponse(f"/completed/{session_id}", status_code=303)
    else:
        # Redirect to next step
        return RedirectResponse(f"/form/{session_id}/{next_step}", status_code=303)


@app.get("/completed/{session_id}", response_class=HTMLResponse)
async def show_completion(session_id: str):
    """Show completion page"""
    html = chain.render_completion(session_id)
    return HTMLResponse(content=html)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(chain.SESSIONS),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🚀 Starting Simplified Form Chain Engine v3 Demo Server")
    print("📍 Visit http://localhost:8038 to see the improvements")
    print("✨ Features:")
    print("  - No JSON serialization errors")
    print("  - Clean server-side session management")
    print("  - Pure semantic HTML forms")
    print("  - Reliable state handling")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8038)