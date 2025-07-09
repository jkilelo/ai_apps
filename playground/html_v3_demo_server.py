#!/usr/bin/env python3
"""
FastAPI Demo Server for HTML Form Chain Engine v3.0

This server demonstrates the form chain engine in action, showing how
forms can be chained together as input-output processors.

Run with: python html_v3_demo_server.py
Then visit: http://localhost:8037
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import json
import base64
from typing import Dict, Any, Optional
import uvicorn
from datetime import datetime

# Import our form chain examples
from html_v3_examples import (
    create_data_quality_chain,
    create_job_application_chain,
    create_insurance_claim_chain,
    create_support_ticket_chain
)

app = FastAPI(title="Form Chain Engine v3 Demo")

# Store active chains in memory (in production, use Redis or database)
active_chains: Dict[str, Any] = {}


@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Display all available form chains"""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Form Chain Engine v3 - Demo</title>
    <style>
        * { box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f0f2f5;
            margin: 0;
            padding: 0;
        }
        
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 20px;
            text-align: center;
        }
        
        .hero h1 {
            margin: 0 0 20px 0;
            font-size: 3em;
            font-weight: 300;
        }
        
        .hero p {
            font-size: 1.3em;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .concept-section {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }
        
        .concept-section h2 {
            color: #2c3e50;
            margin-top: 0;
        }
        
        .concept-diagram {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }
        
        .flow-diagram {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .flow-step {
            background: #e3f2fd;
            padding: 15px 25px;
            border-radius: 8px;
            border: 2px solid #2196f3;
        }
        
        .flow-arrow {
            font-size: 24px;
            color: #2196f3;
        }
        
        .chains-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }
        
        .chain-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s;
        }
        
        .chain-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        .chain-header {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 25px;
        }
        
        .chain-header h3 {
            margin: 0 0 10px 0;
            font-size: 1.5em;
        }
        
        .chain-description {
            opacity: 0.9;
        }
        
        .chain-body {
            padding: 25px;
        }
        
        .process-flow {
            margin: 20px 0;
        }
        
        .process-step {
            display: flex;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        
        .step-number {
            background: #3498db;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
        }
        
        .features {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        
        .feature-tag {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .start-button {
            display: inline-block;
            background: #3498db;
            color: white;
            text-decoration: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .start-button:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        
        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin: 20px 0;
        }
        
        .info-box h4 {
            margin-top: 0;
            color: #1976d2;
        }
        
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        
        .api-section {
            background: #263238;
            color: #eceff1;
            padding: 30px;
            border-radius: 8px;
            margin-top: 40px;
        }
        
        .api-section h3 {
            margin-top: 0;
            color: #80cbc4;
        }
        
        .endpoint {
            background: #37474f;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
        
        .method {
            color: #81c784;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🔗 Form Chain Engine v3</h1>
        <p>Revolutionary approach to forms as input-output processors in a chain</p>
    </div>
    
    <div class="container">
        <div class="concept-section">
            <h2>The Form Chain Paradigm</h2>
            <p>
                Unlike traditional form wizards that simply collect data step by step, 
                Form Chain Engine v3 treats each form as a <strong>processor</strong> that:
            </p>
            <ul>
                <li>Takes input via a Pydantic model (Request)</li>
                <li>Processes the data (potentially calling APIs, databases, etc.)</li>
                <li>Returns output via another Pydantic model (Response)</li>
                <li>The response data flows into the next form, pre-populating fields and potentially adding new ones</li>
            </ul>
            
            <div class="concept-diagram">
                <h4>How It Works</h4>
                <div class="flow-diagram">
                    <div class="flow-step">Form 1<br><small>Request Model</small></div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">Process<br><small>Business Logic</small></div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">Response<br><small>Output Model</small></div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">Form 2<br><small>Pre-populated</small></div>
                </div>
            </div>
            
            <div class="info-box">
                <h4>💡 Key Innovation</h4>
                <p>
                    Each step's <strong>response</strong> becomes part of the next step's <strong>context</strong>. 
                    This allows for dynamic, data-driven form flows where the process adapts based on previous inputs and processing results.
                </p>
            </div>
        </div>
        
        <h2>Live Examples</h2>
        <div class="chains-grid">
            <!-- Data Quality Check -->
            <div class="chain-card">
                <div class="chain-header">
                    <h3>📊 Data Quality Check Process</h3>
                    <p class="chain-description">Analyze database tables and implement quality improvements</p>
                </div>
                <div class="chain-body">
                    <div class="process-flow">
                        <div class="process-step">
                            <div class="step-number">1</div>
                            <div>
                                <strong>Connect to Database</strong><br>
                                <small>Select database type and table → Returns table metadata & sample data</small>
                            </div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">2</div>
                            <div>
                                <strong>Configure Checks</strong><br>
                                <small>Select columns (dynamically generated) → Returns quality issues & score</small>
                            </div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">3</div>
                            <div>
                                <strong>Take Actions</strong><br>
                                <small>Choose remediation options → Returns completion status</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="features">
                        <span class="feature-tag">Dynamic Field Injection</span>
                        <span class="feature-tag">Metadata Processing</span>
                        <span class="feature-tag">Quality Scoring</span>
                    </div>
                    
                    <a href="/chain/data_quality_check/start" class="start-button">Start Data Quality Check</a>
                </div>
            </div>
            
            <!-- Job Application -->
            <div class="chain-card">
                <div class="chain-header">
                    <h3>💼 Dynamic Job Application</h3>
                    <p class="chain-description">Adaptive application process based on role and experience</p>
                </div>
                <div class="chain-body">
                    <div class="process-flow">
                        <div class="process-step">
                            <div class="step-number">1</div>
                            <div>
                                <strong>Basic Information</strong><br>
                                <small>Personal details & department → Returns screening score & next assessments</small>
                            </div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">2</div>
                            <div>
                                <strong>Department-Specific Assessment</strong><br>
                                <small>Technical OR Sales assessment (routed dynamically) → Returns evaluation results</small>
                            </div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">3</div>
                            <div>
                                <strong>Interview Scheduling</strong><br>
                                <small>Availability & preferences → Returns scheduled interview details</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="features">
                        <span class="feature-tag">Conditional Routing</span>
                        <span class="feature-tag">Experience-based Fields</span>
                        <span class="feature-tag">Multi-path Flow</span>
                    </div>
                    
                    <a href="/chain/job_application/start" class="start-button">Start Application</a>
                </div>
            </div>
            
            <!-- Insurance Claim -->
            <div class="chain-card">
                <div class="chain-header">
                    <h3>🛡️ Insurance Claim Process</h3>
                    <p class="chain-description">File claims with type-specific requirements</p>
                </div>
                <div class="chain-body">
                    <div class="process-flow">
                        <div class="process-step">
                            <div class="step-number">1</div>
                            <div>
                                <strong>Claim Initiation</strong><br>
                                <small>Policy & incident info → Returns claim ID & required documents</small>
                            </div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">2</div>
                            <div>
                                <strong>Claim-Specific Details</strong><br>
                                <small>Auto/Home/Health specific form → Returns adjuster assignment</small>
                            </div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">3</div>
                            <div>
                                <strong>Document Upload</strong><br>
                                <small>Required documents (dynamic list) → Returns claim status</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="features">
                        <span class="feature-tag">Type-based Routing</span>
                        <span class="feature-tag">Document Requirements</span>
                        <span class="feature-tag">Status Tracking</span>
                    </div>
                    
                    <a href="/chain/insurance_claim/start" class="start-button">File a Claim</a>
                </div>
            </div>
            
            <!-- Support Ticket -->
            <div class="chain-card">
                <div class="chain-header">
                    <h3>🎯 AI-Powered Support</h3>
                    <p class="chain-description">Intelligent ticket routing with automated solutions</p>
                </div>
                <div class="chain-body">
                    <div class="process-flow">
                        <div class="process-step">
                            <div class="step-number">1</div>
                            <div>
                                <strong>Issue Description</strong><br>
                                <small>Describe problem → Returns AI suggestions & routing decision</small>
                            </div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">2</div>
                            <div>
                                <strong>Category-Specific Diagnostics</strong><br>
                                <small>Technical/Billing details → Returns automated fix attempts</small>
                            </div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">3</div>
                            <div>
                                <strong>Resolution & Escalation</strong><br>
                                <small>Feedback & escalation options → Returns ticket status & actions</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="features">
                        <span class="feature-tag">AI Analysis</span>
                        <span class="feature-tag">Auto-remediation</span>
                        <span class="feature-tag">Smart Routing</span>
                    </div>
                    
                    <a href="/chain/support_ticket/start" class="start-button">Get Support</a>
                </div>
            </div>
        </div>
        
        <div class="api-section">
            <h3>API Architecture</h3>
            <p>Each form chain follows a consistent API pattern:</p>
            
            <div class="endpoint">
                <span class="method">GET</span> /chain/{chain_id}/start
                <br><small>Get the entry point form</small>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> /api/chain/{chain_id}/process/{step_id}
                <br><small>Process a step and get the next form or completion status</small>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> /api/chain/{chain_id}/status
                <br><small>Get the current status of a chain execution</small>
            </div>
            
            <p style="margin-top: 20px;">
                Each POST returns either:
                <ul>
                    <li><code>next_form_html</code> - The next form in the chain, pre-populated with response data</li>
                    <li><code>completed</code> - Chain completion status with final data</li>
                </ul>
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)


# Chain initialization endpoints
@app.get("/chain/{chain_id}/start", response_class=HTMLResponse)
async def start_chain(chain_id: str):
    """Start a new form chain execution"""
    
    # Create the appropriate chain
    if chain_id == "data_quality_check":
        chain = create_data_quality_chain()
    elif chain_id == "job_application":
        chain = create_job_application_chain()
    elif chain_id == "insurance_claim":
        chain = create_insurance_claim_chain()
    elif chain_id == "support_ticket":
        chain = create_support_ticket_chain()
    else:
        raise HTTPException(status_code=404, detail=f"Chain {chain_id} not found")
    
    # Store chain in memory
    chain_instance_id = f"{chain_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    active_chains[chain_instance_id] = {
        "chain": chain,
        "state": {},
        "started_at": datetime.now()
    }
    
    # Get entry point
    entry_point = chain.get_entry_point()
    
    # Generate initial form
    form_html = chain.generate_form_html(entry_point.id)
    
    # Inject chain instance ID
    form_html = form_html.replace(
        f'action="/api/chain/{chain_id}/process/{entry_point.id}"',
        f'action="/api/chain/{chain_instance_id}/process/{entry_point.id}"'
    )
    
    return HTMLResponse(content=form_html)


# Process form submission
@app.post("/api/chain/{chain_instance_id}/process/{step_id}")
async def process_chain_step(
    chain_instance_id: str,
    step_id: str,
    request: Request
):
    """Process a form submission and return the next step"""
    
    # Get chain instance
    if chain_instance_id not in active_chains:
        raise HTTPException(status_code=404, detail="Chain instance not found")
    
    chain_data = active_chains[chain_instance_id]
    chain = chain_data["chain"]
    
    # Parse form data
    form_data = await request.form()
    form_dict = {}
    
    for key, value in form_data.items():
        if key not in ["csrf_token", "chain_state"]:
            # Handle array fields
            if value.startswith('[') and value.endswith(']'):
                try:
                    form_dict[key] = json.loads(value)
                except:
                    form_dict[key] = value
            else:
                form_dict[key] = value
    
    # Get chain state
    encoded_state = form_data.get("chain_state", "")
    if encoded_state:
        try:
            chain_state = json.loads(base64.b64decode(encoded_state).decode())
        except:
            chain_state = chain_data["state"]
    else:
        chain_state = chain_data["state"]
    
    # Process the step
    try:
        result = await chain.process_step(step_id, form_dict, chain_state)
        
        # Update stored state
        chain_data["state"] = result.get("chain_state", chain_state)
        
        # Handle completion
        if result.get("completed"):
            # Clean up
            del active_chains[chain_instance_id]
            
            return JSONResponse({
                "completed": True,
                "message": result.get("message", "Process completed successfully!"),
                "final_data": result.get("final_data", {})
            })
        
        # Return next form
        if result.get("next_form_html"):
            # Update form action to include instance ID
            next_form = result["next_form_html"]
            next_form = next_form.replace(
                f'action="/api/chain/{chain.chain_id}/process/',
                f'action="/api/chain/{chain_instance_id}/process/'
            )
            
            return JSONResponse({
                "next_form_html": next_form,
                "next_step_id": result.get("next_step_id")
            })
        
        # Handle errors
        if result.get("error"):
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "errors": result.get("errors", []),
                    "message": result.get("message", "Validation failed")
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": str(e)
            }
        )


# Get chain status
@app.get("/api/chain/{chain_instance_id}/status")
async def get_chain_status(chain_instance_id: str):
    """Get the current status of a chain execution"""
    
    if chain_instance_id not in active_chains:
        return JSONResponse({
            "status": "not_found",
            "message": "Chain instance not found"
        })
    
    chain_data = active_chains[chain_instance_id]
    chain = chain_data["chain"]
    state = chain_data["state"]
    
    # Determine current step
    completed_steps = [key.replace("step_", "").replace("_response", "") 
                      for key in state.keys() if "_response" in key]
    
    return JSONResponse({
        "status": "in_progress",
        "chain_id": chain.chain_id,
        "started_at": chain_data["started_at"].isoformat(),
        "completed_steps": completed_steps,
        "total_steps": len(chain.steps),
        "current_data": state
    })


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_chains": len(active_chains),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🚀 Starting Form Chain Engine v3 Demo Server")
    print("📍 Visit http://localhost:8037 to explore the examples")
    print("🔗 Each form chain demonstrates input-output processing")
    print("\nKey Features:")
    print("- Forms as processors with request/response models")
    print("- Dynamic field injection based on previous responses")
    print("- Conditional routing between steps")
    print("- State management across the chain")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8037)