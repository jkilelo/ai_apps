"""
Main API entry point for UI Web Auto Testing
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .routers import element_extraction, test_generation, test_execution

# Import data quality router
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_quality.api.router import router as data_quality_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Global state
app_state = {
    "server_start_time": None,
    "active_jobs": {},
    "job_history": []
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting UI Web Auto Testing API Server...")
    app_state["server_start_time"] = datetime.now()
    logger.info("Server initialization complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down UI Web Auto Testing API Server...")
    # Cancel any active jobs
    for job_id, task in app_state["active_jobs"].items():
        if hasattr(task, 'cancel') and not task.done():
            task.cancel()
            logger.info(f"Cancelled active job: {job_id}")
    logger.info("Server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="UI Web Auto Testing API",
    description="Automated testing framework for web applications",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)

# Rate limiting error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(
    element_extraction.router,
    prefix="/api/v1/element-extraction",
    tags=["element-extraction"]
)

app.include_router(
    test_generation.router,
    prefix="/api/v1/test-generation",
    tags=["test-generation"]
)

app.include_router(
    test_execution.router,
    prefix="/api/v1/test-execution",
    tags=["test-execution"]
)

# Include data quality router
app.include_router(data_quality_router)

# Serve static files from React build
static_dir = Path(__file__).parent.parent.parent.parent / "ui" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="static")

# Root endpoint
@app.get("/api", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "UI Web Auto Testing API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs",
        "health": "/api/health"
    }


# Health check
@app.get("/api/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint"""
    uptime = datetime.now() - app_state["server_start_time"]
    
    return {
        "status": "healthy",
        "uptime": str(uptime),
        "active_jobs": len(app_state["active_jobs"]),
        "total_jobs": len(app_state["job_history"]),
        "timestamp": datetime.now().isoformat()
    }


# Catch-all route to serve the React app
@app.get("/{path:path}")
async def serve_react_app(path: str):
    """Serve the React app for all non-API routes"""
    static_dir = Path(__file__).parent.parent.parent.parent / "ui" / "dist"
    index_file = static_dir / "index.html"
    
    # Try to serve the requested file if it exists
    requested_file = static_dir / path
    if requested_file.exists() and requested_file.is_file():
        return FileResponse(str(requested_file))
    
    # Otherwise serve index.html for client-side routing
    if index_file.exists():
        return FileResponse(str(index_file))
    
    raise HTTPException(status_code=404, detail="React app not found. Please build the frontend.")


if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable, default to 8002
    port = int(os.environ.get("UI_WEB_AUTO_TESTING_PORT", "8002"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )