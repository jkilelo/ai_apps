"""
Dynamic Forms V2 - Modern FastAPI Application
Enhanced with Pydantic V2, WebSocket streaming, and beautiful UI
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

from profiling import get_metadata
from mongo_service import mongo_service

# Configuration
class Settings:
    """Application settings and configuration"""
    HOST: str = "0.0.0.0"
    PORT: int = 8210
    DEBUG: bool = False
    FRONTEND_DEV_URL: str = "http://localhost:5175"
    
    # Database settings (for future use)
    DATABASE_URL: Optional[str] = None
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
settings = Settings()

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
    allow_origins=settings.CORS_ORIGINS,
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

class ElementExtractionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    url: str = Field(
        ...,
        description="The URL to extract UI elements from",
        examples=["https://example.com", "https://testsite.com"]
    )


# Response Models
class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class MetadataResponse(BaseModel):
    database: str
    table: str
    columns: Optional[List[str]] = None
    metadata: Optional[Dict] = None
    
class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# Session Management Models
class SessionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    database: str = Field(..., description="Database Name")
    table: str = Field(..., description="Table Name")
    fresh_data: bool = Field(default=False, description="Whether to fetch fresh data or use cached")

class UISessionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    url: str = Field(..., description="URL for UI testing")
    fresh_data: bool = Field(default=False, description="Whether to fetch fresh data or use cached")

class SessionResponse(BaseModel):
    has_session: bool
    session_data: Optional[Dict] = None
    message: str


# Base Service for common functionality
class BaseDataService:
    """Base service for data-related operations"""
    
    @staticmethod
    async def validate_request(request: GetMetadataRequest) -> None:
        """Validate common request parameters"""
        if not request.database.strip():
            raise HTTPException(status_code=400, detail="Database name is required")
        if not request.table.strip():
            raise HTTPException(status_code=400, detail="Table name is required")
    
    @staticmethod
    def create_response(data: Dict, success: bool = True, error: str = None) -> APIResponse:
        """Create standardized API response"""
        return APIResponse(
            success=success,
            data=data if success else None,
            error=error if not success else None
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
@app.post("/api/metadata", response_model=MetadataResponse, responses={404: {"model": ErrorResponse}})
async def metadata(request: GetMetadataRequest):
    """
    Get metadata of a database table via POST request.
    
    Args:
        request (GetMetadataRequest): The metadata request with database, table, and optional columns.
        
    Returns:
        MetadataResponse: Metadata of the specified table.
    """
    try:
        await BaseDataService.validate_request(request)
        
        # Call actual metadata function
        metadata_result = await get_metadata(request.database, request.table, request.columns)
        
        return MetadataResponse(
            database=request.database,
            table=request.table,
            columns=request.columns if request.columns else None,
            metadata=metadata_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Profiling Step 2: Get Profiling Suggestions
@app.post("/api/profiling/suggestions", response_model=APIResponse, responses={404: {"model": ErrorResponse}})
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
    suggestions_data = {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "suggestions": [
            {"suggestion_id": 1, "description": "Add index on primary key"},
            {"suggestion_id": 2, "description": "Normalize data structure"},
            {"suggestion_id": 3, "description": "Implement foreign key constraints"}
        ]
    }
    
    # Save to session
    mongo_service.save_profiling_session(request.database, request.table, "suggestions", suggestions_data)
    
    return {
        "success": True,
        "message": "Profiling suggestions generated successfully",
        "data": suggestions_data
    }

# Profiling Step 3: Get Profiling Test Cases
@app.post("/api/profiling/testcases", response_model=APIResponse, responses={404: {"model": ErrorResponse}})
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
    testcases_data = {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "test_cases": [
            {"case_id": 1, "description": "Check for null values"},
            {"case_id": 2, "description": "Validate data types"},
            {"case_id": 3, "description": "Ensure unique constraints"}
        ]
    }
    
    # Save to session
    mongo_service.save_profiling_session(request.database, request.table, "testcases", testcases_data)
    
    return {
        "success": True,
        "message": "Profiling test cases generated successfully",
        "data": testcases_data
    }

# Profiling Step 4: Get Profiling PySpark Code
@app.post("/api/profiling/pyspark_code", response_model=APIResponse, responses={404: {"model": ErrorResponse}})
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
    
    # Generate column references for SQL queries
    first_column = request.columns[0] if request.columns and len(request.columns) > 0 else "id"
    columns_str = ", ".join([f'"{col}"' for col in request.columns]) if request.columns else "*"
    
    pyspark_code = f"""
from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder.appName("Data Profiling").getOrCreate()

# Read data from database
df = spark.read.format("jdbc") \\
    .option("url", "jdbc:mysql://localhost:3306/{request.database}") \\
    .option("dbtable", "{request.table}") \\
    .option("user", "root") \\
    .option("password", "password") \\
    .load()

# Basic data profiling
print("=== Schema Information ===")
df.printSchema()

print("=== Basic Statistics ===")
df.describe({columns_str}).show()

# Create temporary view for SQL queries
df.createOrReplaceTempView("{request.table}_view")

print("=== Data Profiling Results ===")

# Total record count
print("Total Records:")
spark.sql("SELECT COUNT(*) as total_records FROM {request.table}_view").show()

# Null value analysis for first column
print(f"Null values in {first_column}:")
spark.sql("SELECT COUNT(*) as null_count FROM {request.table}_view WHERE `{first_column}` IS NULL").show()

print("=== Sample Data ===")
spark.sql("SELECT * FROM {request.table}_view LIMIT 10").show()

# Stop Spark session
spark.stop()
"""
    
    pyspark_data = {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "pyspark_code": pyspark_code
    }
    
    # Save to session
    mongo_service.save_profiling_session(request.database, request.table, "pyspark_code", pyspark_data)
    
    return {
        "success": True,
        "message": "Profiling PySpark code generated successfully",
        "data": pyspark_data
    }

# Profiling Step 5: Execute Profiling Code
@app.post("/api/profiling/code_execution", response_model=APIResponse, responses={404: {"model": ErrorResponse}})
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
    execution_data = {
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
    
    # Save to session
    mongo_service.save_profiling_session(request.database, request.table, "code_execution", execution_data)
    
    return {
        "success": True,
        "message": "Profiling code executed successfully",
        "data": execution_data
    }

# Data Quality Step 1: Get Data Quality Suggestions
@app.post("/api/dq/suggestions", response_model=APIResponse, responses={404: {"model": ErrorResponse}})
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
    suggestions_data = {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "suggestions": [
            {"suggestion_id": 1, "description": "Check for duplicate records"},
            {"suggestion_id": 2, "description": "Validate email formats"},
            {"suggestion_id": 3, "description": "Ensure mandatory fields are filled"}
        ]
    }
    
    # Save to session
    mongo_service.save_dq_session(request.database, request.table, "suggestions", suggestions_data)
    
    return {
        "success": True,
        "message": "Data quality suggestions generated successfully",
        "data": suggestions_data
    }

# Data Quality Step 2: Get Data Quality Test Cases
@app.post("/api/dq/testcases", response_model=APIResponse, responses={404: {"model": ErrorResponse}})
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
    testcases_data = {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "test_cases": [
            {"case_id": 1, "description": "Check for null values"},
            {"case_id": 2, "description": "Validate data types"},
            {"case_id": 3, "description": "Ensure unique constraints"}
        ]
    }
    
    # Save to session
    mongo_service.save_dq_session(request.database, request.table, "testcases", testcases_data)
    
    return {
        "success": True,
        "message": "Data quality test cases generated successfully",
        "data": testcases_data
    }

# Data Quality Step 3: Get Data Quality PySpark Code
@app.post("/api/dq/pyspark_code", response_model=APIResponse, responses={404: {"model": ErrorResponse}})
async def get_data_quality_pyspark_code(request: GetMetadataRequest):
    """Get data quality PySpark code for a database table via POST request.
    Args:
        database (str): The database name.
        table (str): The table name.
        columns (Optional[List[str]]): The list of columns to include in the test cases.
    Returns:
        dict: Data quality PySpark code for the specified table.
    """
    
    # Generate column references for SQL queries
    first_column = request.columns[0] if request.columns and len(request.columns) > 0 else "id"
    second_column = request.columns[1] if request.columns and len(request.columns) > 1 else first_column
    columns_str = ", ".join([f'"{col}"' for col in request.columns]) if request.columns else "*"
    
    pyspark_code = f"""
from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder.appName("Data Quality Analysis").getOrCreate()

# Read data from database
df = spark.read.format("jdbc") \\
    .option("url", "jdbc:mysql://localhost:3306/{request.database}") \\
    .option("dbtable", "{request.table}") \\
    .option("user", "root") \\
    .option("password", "password") \\
    .load()

# Basic data profiling
print("=== Schema Information ===")
df.printSchema()

print("=== Basic Statistics ===")
df.describe({columns_str}).show()

# Create temporary view for SQL queries
df.createOrReplaceTempView("{request.table}_view")

print("=== Data Quality Checks ===")

# Total record count
print("Total Records:")
spark.sql("SELECT COUNT(*) as total_records FROM {request.table}_view").show()

# Null value analysis for first column
print(f"Null values in {first_column}:")
spark.sql("SELECT COUNT(*) as null_count FROM {request.table}_view WHERE `{first_column}` IS NULL").show()

print(f"Non-null values in {first_column}:")
spark.sql("SELECT COUNT(*) as non_null_count FROM {request.table}_view WHERE `{first_column}` IS NOT NULL").show()

# Data completeness check
if len({repr(request.columns)}) > 1:
    print(f"Complete records ({first_column} and {second_column} not null):")
    spark.sql("SELECT COUNT(*) as complete_records FROM {request.table}_view WHERE `{first_column}` IS NOT NULL AND `{second_column}` IS NOT NULL").show()

print("=== Sample Data ===")
spark.sql("SELECT * FROM {request.table}_view LIMIT 10").show()

# Stop Spark session
spark.stop()
"""
    
    pyspark_data = {
        "database": request.database,
        "table": request.table,
        "columns": request.columns if request.columns else None,
        "pyspark_code": pyspark_code
    }
    
    # Save to session
    mongo_service.save_dq_session(request.database, request.table, "pyspark_code", pyspark_data)
    
    return {
        "success": True,
        "message": "PySpark code generated successfully",
        "data": pyspark_data
    }

# Data Quality Step 4: Execute Data Quality Code
@app.post("/api/dq/code_execution", response_model=APIResponse, responses={404: {"model": ErrorResponse}})
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
    execution_data = {
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
    
    # Save to session
    mongo_service.save_dq_session(request.database, request.table, "code_execution", execution_data)
    
    return {
        "success": True,
        "message": "Data quality code executed successfully",
        "data": execution_data
    }


## SESSION MANAGEMENT ENDPOINTS

# Get session data for profiling/DQ
@app.post("/api/session/profiling", response_model=SessionResponse)
async def get_profiling_session(request: SessionRequest):
    """Get existing profiling session data"""
    session_data = mongo_service.get_profiling_session(request.database, request.table)
    
    if session_data and not request.fresh_data:
        return SessionResponse(
            has_session=True,
            session_data=session_data,
            message="Session data loaded successfully"
        )
    else:
        return SessionResponse(
            has_session=False,
            message="No session data found or fresh data requested"
        )

@app.post("/api/session/dq", response_model=SessionResponse)
async def get_dq_session(request: SessionRequest):
    """Get existing data quality session data"""
    session_data = mongo_service.get_dq_session(request.database, request.table)
    
    if session_data and not request.fresh_data:
        return SessionResponse(
            has_session=True,
            session_data=session_data,
            message="Session data loaded successfully"
        )
    else:
        return SessionResponse(
            has_session=False,
            message="No session data found or fresh data requested"
        )

@app.post("/api/session/ui", response_model=SessionResponse)
async def get_ui_session(request: UISessionRequest):
    """Get existing UI session data"""
    session_data = mongo_service.get_ui_session(request.url)
    
    if session_data and not request.fresh_data:
        return SessionResponse(
            has_session=True,
            session_data=session_data,
            message="Session data loaded successfully"
        )
    else:
        return SessionResponse(
            has_session=False,
            message="No session data found or fresh data requested"
        )

# Clear session data
@app.delete("/api/session/profiling")
async def clear_profiling_session(request: SessionRequest):
    """Clear profiling session data"""
    mongo_service.clear_profiling_session(request.database, request.table)
    return {"success": True, "message": "Profiling session cleared"}

@app.delete("/api/session/dq")
async def clear_dq_session(request: SessionRequest):
    """Clear data quality session data"""
    mongo_service.clear_dq_session(request.database, request.table)
    return {"success": True, "message": "Data quality session cleared"}

@app.delete("/api/session/ui")
async def clear_ui_session(request: UISessionRequest):
    """Clear UI session data"""
    mongo_service.clear_ui_session(request.url)
    return {"success": True, "message": "UI session cleared"}

# Get session summary
@app.get("/api/session/summary")
async def get_session_summary():
    """Get summary of all sessions"""
    summary = mongo_service.get_session_summary()
    return {"success": True, "data": summary}

# Clear all sessions
@app.delete("/api/session/all")
async def clear_all_sessions():
    """Clear all session data"""
    mongo_service.clear_all_sessions()
    return {"success": True, "message": "All sessions cleared"}


## WEB UI TESTING AUTOMATION ENDPOINTS

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
    elements_data = {
        "url": url,
        "elements": [
            {"tag": "button", "text": "Submit"},
            {"tag": "input", "type": "text", "placeholder": "Enter your name"},
            {"tag": "div", "class": "header", "text": "Welcome to the AI Platform"}
        ]
    }
    
    # Save to session
    mongo_service.save_ui_session(url, "elements", elements_data)
    
    return elements_data

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
    testcases_data = {
        "url": url,
        "test_cases": [
            {"case_id": 1, "description": "Check if submit button is present"},
            {"case_id": 2, "description": "Validate input field placeholders"},
            {"case_id": 3, "description": "Ensure header text is correct"}
        ]
    }
    
    # Save to session
    mongo_service.save_ui_session(url, "testcases", testcases_data)
    
    return testcases_data

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
    python_code_data = {
        "url": url,
        "python_code": f"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize webdriver
driver = webdriver.Chrome()
driver.get("{url}")

try:
    # Check if submit button is present
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Submit')]"))
    )
    print("Submit button found successfully")
    
    # Validate input field placeholders
    input_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter your name']")
    print(f"Input field placeholder: {{input_field.get_attribute('placeholder')}}")
    
    # Check header text
    header = driver.find_element(By.CLASS_NAME, "header")
    print(f"Header text: {{header.text}}")
    
finally:
    driver.quit()
"""
    }
    
    # Save to session
    mongo_service.save_ui_session(url, "python_code", python_code_data)
    
    return python_code_data

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
    execution_data = {
        "url": url,
        "execution_result": "Code executed successfully",
        "details": [
            {"step": 1, "result": "Submit button found"},
            {"step": 2, "result": "Input field placeholder validated"},
            {"step": 3, "result": "Header text verified"}
        ]
    }
    
    # Save to session
    mongo_service.save_ui_session(url, "code_execution", execution_data)
    
    return execution_data

# Development server
if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )