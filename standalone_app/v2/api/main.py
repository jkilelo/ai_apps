"""
AI Apps v2 Backend - Improved FastAPI application with better performance and error handling
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
import uvicorn

# Import routers
from routers.llm import router as llm_router
from routers.web_automation import router as web_automation_router
from routers.data_profiling import router as data_profiling_router

# Import services
from services.cache import CacheService
from services.rate_limiter import RateLimiter
from services.health_check import HealthChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
cache_service = CacheService()
rate_limiter = RateLimiter()
health_checker = HealthChecker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Apps v2 Backend...")
    
    # Initialize services
    await cache_service.initialize()
    await health_checker.initialize()
    
    # Warm up cache
    await cache_service.warm_up()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Apps v2 Backend...")
    
    # Cleanup services
    await cache_service.cleanup()
    await health_checker.cleanup()
    
    logger.info("Application shut down successfully")

# Create FastAPI app with lifespan
app = FastAPI(
    title="AI Apps v2 API",
    description="Modern web API with pure technologies - no frameworks in frontend",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"]
)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware for request tracking
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request"""
    import uuid
    request_id = str(uuid.uuid4())
    
    # Add to request state
    request.state.request_id = request_id
    
    # Process request
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{process_time:.3f}s"
    
    # Log request
    logger.info(
        f"Request {request_id}: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        f"Unhandled exception in request {request_id}: {exc}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request_id
        }
    )

# Validation error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id
        }
    )

# Rate limiting decorator
def rate_limit(max_requests: int = 10, window: int = 60):
    """Rate limiting decorator"""
    async def decorator(request: Request):
        client_ip = request.client.host
        
        if not await rate_limiter.is_allowed(client_ip, max_requests, window):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
    
    return decorator

# Health check endpoint
@app.get("/api/health", tags=["System"])
async def health_check():
    """Check application health status"""
    health_status = await health_checker.check_health()
    
    if not health_status["healthy"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status

# API Info endpoint
@app.get("/api/info", tags=["System"])
async def api_info():
    """Get API information"""
    return {
        "name": "AI Apps v2 API",
        "version": "2.0.0",
        "description": "Modern web API with improved performance and error handling",
        "features": [
            "LLM Query Interface",
            "Web Automation (4-step process)",
            "Data Profiling (8-step process)",
            "Caching for performance",
            "Rate limiting",
            "Request tracking",
            "Health monitoring"
        ],
        "improvements": [
            "Better error handling",
            "Request/response caching",
            "Async/await throughout",
            "Structured logging",
            "Request ID tracking",
            "Performance monitoring"
        ]
    }

# Include routers
app.include_router(llm_router, prefix="/api", tags=["LLM"])
app.include_router(web_automation_router, prefix="/api", tags=["Web Automation"])
app.include_router(data_profiling_router, prefix="/api", tags=["Data Profiling"])

# Serve static files (frontend)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Performance monitoring endpoint
@app.get("/api/metrics", tags=["System"])
async def get_metrics():
    """Get performance metrics"""
    return {
        "cache_stats": await cache_service.get_stats(),
        "rate_limit_stats": await rate_limiter.get_stats(),
        "health_stats": await health_checker.get_stats()
    }

if __name__ == "__main__":
    # Run with uvloop for better performance
    import platform
    
    config = {
        "host": "0.0.0.0",
        "port": 8004,
        "log_level": "info",
        "access_log": True,
        "reload": False  # Set to True for development
    }
    
    # Use uvloop on Unix systems for better performance
    # if platform.system() != "Windows":
    #     config["loop"] = "uvloop"
    
    uvicorn.run("main:app", **config)