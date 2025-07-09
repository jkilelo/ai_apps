"""
Platform-agnostic Main API entry point for UI Web Auto Testing
Works on Windows, macOS, and Linux
"""

import os
import sys
import logging
import platform
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Import platform utilities
from utils.platform_utils import setup_event_loop, get_platform_info

# Setup platform-appropriate event loop
setup_event_loop()

from .routers import element_extraction, test_generation, test_execution

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log platform info
platform_info = get_platform_info()
logger.info(f"Running on {platform_info['system']} {platform_info['release']}")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Global state
app_state = {
    "server_start_time": None,
    "active_jobs": {},
    "job_history": [],
    "platform_info": platform_info
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting UI Web Auto Testing API Server...")
    logger.info(f"Platform: {platform_info['system']} ({platform_info['python_version'].split()[0]})")
    app_state["server_start_time"] = datetime.now()
    
    # Platform-specific startup
    if platform_info['is_windows']:
        logger.info("Windows detected: Single-worker mode enabled")
    else:
        logger.info(f"Unix-like system detected: Multi-worker support available")
    
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
    description="Automated testing framework for web applications (Cross-platform)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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

# Serve static files from React build
static_dir = Path(__file__).parent.parent.parent.parent / "ui" / "dist"
if static_dir.exists():
    # Normalize path for platform
    static_path = str(static_dir / "assets")
    if platform.system() == "Windows":
        static_path = static_path.replace("/", "\\")
    app.mount("/assets", StaticFiles(directory=static_path), name="static")

# Root endpoint
@app.get("/api", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "UI Web Auto Testing API",
        "version": "1.0.0",
        "status": "running",
        "platform": platform_info['system'],
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
        "platform": {
            "system": platform_info['system'],
            "python": platform_info['python_version'].split()[0],
            "is_windows": platform_info['is_windows']
        },
        "uptime": str(uptime),
        "active_jobs": len(app_state["active_jobs"]),
        "total_jobs": len(app_state["job_history"]),
        "timestamp": datetime.now().isoformat()
    }


# Platform info endpoint
@app.get("/api/platform", response_model=Dict[str, Any])
async def platform_details():
    """Get detailed platform information"""
    return {
        "system": platform_info['system'],
        "release": platform_info['release'],
        "machine": platform_info['machine'],
        "processor": platform_info['processor'],
        "python_version": platform_info['python_version'],
        "python_implementation": platform_info['python_implementation'],
        "features": {
            "multi_worker": not platform_info['is_windows'],
            "uvloop_available": 'uvloop' in sys.modules and not platform_info['is_windows'],
            "async_optimized": True
        }
    }


# Catch-all route to serve the React app
@app.get("/{path:path}")
async def serve_react_app(path: str):
    """Serve the React app for all non-API routes"""
    static_dir = Path(__file__).parent.parent.parent.parent / "ui" / "dist"
    
    # Normalize paths for platform
    if platform.system() == "Windows":
        path = path.replace("/", "\\") if path else ""
    
    index_file = static_dir / "index.html"
    
    # Try to serve the requested file if it exists
    requested_file = static_dir / path if path else index_file
    if requested_file.exists() and requested_file.is_file():
        return FileResponse(str(requested_file))
    
    # Otherwise serve index.html for client-side routing
    if index_file.exists():
        return FileResponse(str(index_file))
    
    raise HTTPException(status_code=404, detail="React app not found. Please build the frontend.")


# Platform-agnostic server runner
def run_server():
    """Run the server with platform-appropriate settings"""
    import uvicorn
    from utils.platform_utils import get_recommended_workers, is_port_available
    
    # Get configuration
    host = os.environ.get("FASTAPI_HOST", "0.0.0.0")
    port = int(os.environ.get("FASTAPI_PORT", "8002"))
    
    # Check port availability
    if not is_port_available(port):
        logger.error(f"Port {port} is already in use!")
        sys.exit(1)
    
    # Platform-specific configuration
    config = {
        "app": "main_platform_agnostic:app",
        "host": host,
        "port": port,
        "log_level": "info"
    }
    
    # Development mode settings
    if os.environ.get("ENVIRONMENT", "development") == "development":
        config["reload"] = True
        config["workers"] = 1  # Single worker in dev mode
    else:
        # Production mode
        config["workers"] = get_recommended_workers()
        
        # Try to use uvloop on Unix systems
        if not platform_info['is_windows']:
            config["loop"] = "uvloop"
        else:
            # Windows doesn't support uvloop
            config["loop"] = "asyncio"
    
    logger.info(f"Starting server with config: {config}")
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()