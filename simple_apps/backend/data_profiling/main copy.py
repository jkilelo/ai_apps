"""
Dynamic Forms V2 - Modern FastAPI Application
Enhanced with Pydantic V2, WebSocket streaming, and beautiful UI
"""

import os
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Dict, List, Any, Optional, Union, Literal
import json
import asyncio
from datetime import datetime, date
from enum import Enum
import uuid
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from profiling import get_metadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Dynamic Forms V3 - AI-Powered Application...")
    logger.info("Initializing AI models and services...")
    logger.info("Setting up WebSocket and WebRTC connections...")
    logger.info("API Documentation available at /api/docs")
    yield
    # Shutdown
    logger.info("Shutting down Dynamic Forms V3 Application...")

# Initialize FastAPI app with V3 configuration
app = FastAPI(
    title="AI-Powered Testing Platform",
    description="Next-generation testing system with AI capabilities",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware for modern web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React build files
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "assets"), name="static")
else:
    print(f"Warning: Frontend build directory not found at {FRONTEND_DIR}")
    print("Please run 'npm run build' in the frontend directory first.")


# Enhanced WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0
        }
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_stats["total_connections"] += 1
        self.connection_stats["active_connections"] = len(self.active_connections)
        logger.info(f"Client {client_id} connected. Active connections: {self.connection_stats['active_connections']}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            self.connection_stats["active_connections"] = len(self.active_connections)
            logger.info(f"Client {client_id} disconnected. Active connections: {self.connection_stats['active_connections']}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
            self.connection_stats["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast(self, message: str, exclude_client: Optional[str] = None):
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_client:
                try:
                    await connection.send_text(message)
                    self.connection_stats["messages_sent"] += 1
                except:
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

manager = ConnectionManager()

# Enhanced Pydantic V2 Models with advanced validation
class GetMetadataRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    database: str = Field(
        ..., 
        min_length=2, 
        max_length=50, 
        description="Database Name",
        examples=["test_db", "production_db"]
    )
    table: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="Table Name",
        examples=["users", "orders"]
    )
    columns: list[str] = Field(
        default=[], 
        max_length=100,
        description="List of Columns",
        examples=[["id", "name", "email"]]
    )


# API Routes
@app.get("/")
async def root(request: Request):
    """Serve the React frontend"""
    # Check if React build exists
    react_build = FRONTEND_DIR / "index.html"
    if react_build.exists():
        return FileResponse(react_build)
    else:
        # Fallback message if React build not found
        return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI-Powered Testing Platform</title>
                <style>
                    body { 
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
                        margin: 0; 
                        padding: 40px; 
                        background: #f9fafb;
                        color: #1f2937;
                    }
                    .container { 
                        max-width: 800px; 
                        margin: 0 auto; 
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    }
                    .info { 
                        color: #2563eb; 
                        background: #eff6ff; 
                        padding: 20px; 
                        border-radius: 8px; 
                        border-left: 4px solid #2563eb;
                    }
                    .command {
                        background: #f3f4f6;
                        padding: 12px 16px;
                        border-radius: 6px;
                        font-family: monospace;
                        margin: 10px 0;
                    }
                    h1 { color: #1f2937; margin-bottom: 20px; }
                    h3 { color: #2563eb; margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 AI-Powered Testing Platform</h1>
                    <div class="info">
                        <h3>React Frontend Available</h3>
                        <p>The React frontend is running on the development server. Please visit:</p>
                        <div class="command">http://localhost:5175</div>
                        <p>To build the React app for production, run:</p>
                        <div class="command">cd /var/www/ai_apps/simple_apps/frontend && npm run build</div>
                        <ul style="margin-top: 20px;">
                            <li><strong>Version:</strong> 1.0.0</li>
                            <li><strong>Frontend:</strong> React 19.1 + Tailwind CSS 4.1</li>
                            <li><strong>Backend:</strong> FastAPI + WebSocket</li>
                            <li><strong>Features:</strong> AI-Powered Data Profiling</li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
        """)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Enhanced WebSocket endpoint with client identification"""
    await manager.connect(websocket, client_id)
    
    try:
        # Send welcome message with stats
        await manager.send_personal_message(json.dumps({
            'type': 'connection',
            'message': 'Connected to Dynamic Forms V2 real-time updates',
            'client_id': client_id,
            'timestamp': datetime.now().isoformat(),
        }), websocket)
        
        while True:
            # Handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get('type') == 'ping':
                await manager.send_personal_message(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }), websocket)
            elif message_data.get('type') == 'form_start':
                # Broadcast to others that someone started filling a form
                await manager.broadcast(json.dumps({
                    'type': 'form_activity',
                    'message': f"A user started filling the {message_data.get('form_name', 'form')}",
                    'timestamp': datetime.now().isoformat()
                }), exclude_client=client_id)
            elif message_data.get('type') == 'get_stats':
                # Send current statistics
                await manager.send_personal_message(json.dumps({
                    'type': 'stats_update',
                    'timestamp': datetime.now().isoformat()
                }), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        # Notify others about disconnection
        await manager.broadcast(json.dumps({
            'type': 'user_disconnect',
            'message': 'A user disconnected',
            'timestamp': datetime.now().isoformat(),
            'active_connections': manager.connection_stats['active_connections']
        }))

# Catch-all route for React Router (SPA)
@app.get("/{path:path}")
async def catch_all(path: str):
    """Serve React app for all non-API routes"""
    # Skip API routes
    if path.startswith("api/") or path.startswith("ws/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    react_build = FRONTEND_DIR / "index.html"
    if react_build.exists():
        return FileResponse(react_build)
    else:
        # Redirect to development server
        return HTMLResponse("""
            <script>
                window.location.href = 'http://localhost:5175';
            </script>
            <p>Redirecting to React development server...</p>
        """, status_code=302)


## PROFILING & DATA QUALITY ENDPOINTS

# Profiling Step 1: Get Metadata
@app.post("/api/metadata")
async def metadata(request: GetMetadataRequest):
    """
    Get metadata of a database table via POST request.
    
    Args:
        request (GetMetadataRequest): The metadata request with database, table, and optional columns.
        
    Returns:
        dict: Metadata of the specified table.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "metadata": {
            "column_count": 5,
            "row_count": 1000,
            "primary_key": "id",
            "foreign_keys": ["user_id"],
            "indexes": ["idx_created_at"]
        }
    }

# Profiling Step 2: Get Profiling Suggestions
@app.post("/api/profiling/suggestions")
async def get_profiling_suggestions(request: GetMetadataRequest):
    """
    Get profiling suggestions for a database table via POST request.

    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the suggestions.

    Returns:
        dict: Profiling suggestions for the specified table.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "suggestions": [
            {"suggestion_id": 1, "description": "Add index on primary key"},
            {"suggestion_id": 2, "description": "Normalize data structure"},
            {"suggestion_id": 3, "description": "Implement foreign key constraints"}
        ]
    }

# Profiling Step 3: Get Profiling Test Cases
@app.post("/api/profiling/testcases")
async def get_profiling_testcases(request: GetMetadataRequest):
    """
    Get profiling test cases for a database table via POST request.

    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the test cases.

    Returns:
        dict: Profiling test cases for the specified table.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "test_cases": [
            {"case_id": 1, "description": "Check for null values"},
            {"case_id": 2, "description": "Validate data types"},
            {"case_id": 3, "description": "Ensure unique constraints"}
        ]
    }

# Profiling Step 4: Get Profiling PySpark Code
@app.post("/api/profiling/pyspark_code")
async def get_profiling_pyspark_code(request: GetMetadataRequest):
    """
    Get profiling PySpark code for a database table via GET request.

    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the test cases.

    Returns:
        dict: Profiling test cases for the specified table.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "pyspark_code": f"""
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("Data Profiling").getOrCreate()
df = spark.read.format("jdbc").option("url", "jdbc:mysql://localhost:3306/{request.database}").option("dbtable", "{request.table}").option("user", "root").option("password", "password").load()
df.printSchema()
df.describe({request.columns if request.columns else '*'}).show()
df.createOrReplaceTempView("{request.table}")
spark.sql("SELECT * FROM {request.table} WHERE {request.columns[0]} IS NULL").show()
spark.sql("SELECT COUNT(*) FROM {request.table}").show()
"""}

# Profiling Step 5: Execute Profiling Code
app.post("/api/profiling/code_execution")
async def execute_profiling_code(request: GetMetadataRequest):
    """
    Execute profiling code for a database table via POST request.

    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the test cases.

    Returns:
        dict: Execution results of the profiling code.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "execution_result": "Code executed successfully",
        "details": [
            {"step": 1, "result": "Schema printed"},
            {"step": 2, "result": "Data described"},
            {"step": 3, "result": "Null values checked"}
        ]
    }

# Data Quality Step 1: Get Data Quality Suggestions
@app.post("/api/dq/suggestions")
async def get_data_quality_suggestions(request: GetMetadataRequest):
    """
    Get data quality suggestions for a database table via POST request.

    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the suggestions.

    Returns:
        dict: Data quality suggestions for the specified table.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "suggestions": [
            {"suggestion_id": 1, "description": "Check for duplicate records"},
            {"suggestion_id": 2, "description": "Validate email formats"},
            {"suggestion_id": 3, "description": "Ensure mandatory fields are filled"}
        ]
    }

# Data Quality Step 2: Get Data Quality Test Cases
@app.post("/api/dq/testcases")
async def get_data_quality_testcases(request: GetMetadataRequest):
    """
    Get data quality test cases for a database table via POST request.

    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the test cases.

    Returns:
        dict: Data quality test cases for the specified table.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "test_cases": [
            {"case_id": 1, "description": "Check for null values"},
            {"case_id": 2, "description": "Validate data types"},
            {"case_id": 3, "description": "Ensure unique constraints"}
        ]
    }

# Data Quality Step 3: Get Data Quality PySpark Code
@app.post("/api/dq/pyspark_code")
async def get_data_quality_pyspark_code(request: GetMetadataRequest):
    """Get data quality PySpark code for a database table via POST request.
    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the test cases.
    Returns:
        dict: Data quality PySpark code for the specified table.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "pyspark_code": f"""
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("Data Quality").getOrCreate()
df = spark.read.format("jdbc").option("url", "jdbc:mysql://localhost:3306/{request.database}").option("dbtable", "{request.table}").option("user", "root").option("password", "password").load()
df.printSchema()
df.describe({request.columns if request.columns else '*'}).show()
df.createOrReplaceTempView("{request.table}")
spark.sql("SELECT * FROM {request.table} WHERE {request.columns[0]} IS NULL").show()
spark.sql("SELECT COUNT(*) FROM {request.table}").show()
spark.sql("SELECT COUNT(*) FROM {request.table} WHERE {request.columns[0]} IS NULL").show()
spark.sql("SELECT COUNT(*) FROM {request.table} WHERE {request.columns[0]} IS NOT NULL").show()
spark.sql("SELECT COUNT(*) FROM {request.table} WHERE {request.columns[0]} IS NOT NULL AND {request.columns[1]} IS NOT NULL").show()
"""
    }

# Data Quality Step 4: Execute Data Quality Code
@app.post("/api/dq/code_execution")
async def execute_data_quality_code(request: GetMetadataRequest):
    """
    Execute data quality code for a database table via POST request.

    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the test cases.

    Returns:
        dict: Execution results of the data quality code.
    """
    return {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "execution_result": "Code executed successfully",
        "details": [
            {"step": 1, "result": "Schema printed"},
            {"step": 2, "result": "Data described"},
            {"step": 3, "result": "Null values checked"}
        ]
    }


## WEB UI TESTING AUTOMATION ENDPOINTS
class ElementExtractionRequest(BaseModel):
    url: str = Field(
        ...,
        description="The URL to extract UI elements from",
        examples=["https://example.com", "https://testsite.com"]
    )

# UI Step 1: Element Extraction
@app.post("/api/ui/url")
async def element_extraction(request: ElementExtractionRequest):
    """
    Extract UI elements from a given URL.
    
    Args:
        request (ElementExtractionRequest): The request containing the URL to extract elements from.
        
    Returns:
        dict: Extracted UI elements.
    """
    url = request.url    
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Simulate element extraction
    return {
        "url": url,
        "elements": [
            {"tag": "button", "text": "Submit"},
            {"tag": "input", "type": "text", "placeholder": "Enter your name"},
            {"tag": "div", "class": "header", "text": "Welcome to the AI Platform"}
        ]
    }

# UI Step 2: Test Case Generation
@app.post("/api/ui/testcases")
async def get_ui_test_cases(request: ElementExtractionRequest):
    """
    Get UI test cases for a given URL.

    Args:
        request (ElementExtractionRequest): The request containing the URL to extract elements from.

    Returns:
        dict: UI test cases for the specified URL.
    """
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Simulate test case generation
    return {
        "url": url,
        "test_cases": [
            {"case_id": 1, "description": "Check if submit button is present"},
            {"case_id": 2, "description": "Validate input field placeholders"},
            {"case_id": 3, "description": "Ensure header text is correct"}
        ]
    }

# UI Step 3: Python Code Generation
@app.post("/api/ui/python_code")
async def get_ui_python_code(request: ElementExtractionRequest):
    """
    Get Python code for UI testing automation for a given URL.

    Args:
        request (ElementExtractionRequest): The request containing the URL to extract elements from.

    Returns:
        dict: Python code for UI testing automation.
    """
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Simulate Python code generation
    return {
        "url": url,
        "python_code": f"""
import requests
from bs4 import BeautifulSoup
response = requests.get("{url}")
soup = BeautifulSoup(response.text, 'html.parser')
# Check if submit button is present
submit_button = soup.find('button', text='Submit')
if submit_button:
    print("Submit button is present")
# Validate input field placeholders
input_field = soup.find('input', {'placeholder': 'Enter your name'})
"""    }

# UI Step 4: Code Execution
@app.post("/api/ui/code_execution")
async def execute_ui_code(request: ElementExtractionRequest):
    """
    Execute UI testing code for a given URL.

    Args:
        request (ElementExtractionRequest): The request containing the URL to execute code for.

    Returns:
        dict: Execution results of the UI testing code.
    """
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Simulate code execution
    return {
        "url": url,
        "execution_result": "Code executed successfully",
        "details": [
            {"step": 1, "result": "Submit button found"},
            {"step": 2, "result": "Input field placeholder validated"}
        ]
    }

# Development server
if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8210,
        # reload=True,
        log_level="info"
    )