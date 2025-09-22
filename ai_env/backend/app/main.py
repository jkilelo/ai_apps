"""
Main FastAPI application
AI-Driven Infrastructure Audit System Backend
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any

from app.config import settings
from app.database import init_db, check_database_connection
from app.api.v1.api import api_router
from app.core.mcp_client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Infrastructure Audit API...")

    # Check database connection
    if await check_database_connection():
        logger.info("Database connected successfully")
        await init_db()
    else:
        logger.error("Failed to connect to database")

    # Initialize MCP client
    app.state.mcp_client = MCPClient(settings.MCP_SERVER_URL)
    if await app.state.mcp_client.check_health():
        logger.info("MCP server connected successfully")
    else:
        logger.warning("MCP server not available")

    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Infrastructure Audit API...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with system information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "ai_first": True,
        "llm_provider": settings.DEFAULT_LLM_PROVIDER,
        "api_docs": f"{settings.API_V1_STR}/docs",
        "features": {
            "infrastructure_audit": True,
            "ai_driven_database": True,
            "mcp_integration": True,
            "real_time_monitoring": True
        }
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring
    Returns system health status
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }

    # Check database
    db_healthy = await check_database_connection()
    health_status["services"]["database"] = {
        "status": "healthy" if db_healthy else "unhealthy",
        "type": "postgresql"
    }

    # Check MCP server
    mcp_client = getattr(app.state, "mcp_client", None)
    if mcp_client:
        mcp_healthy = await mcp_client.check_health()
        health_status["services"]["mcp_server"] = {
            "status": "healthy" if mcp_healthy else "unhealthy",
            "url": settings.MCP_SERVER_URL
        }

    # Overall health
    all_healthy = all(
        service["status"] == "healthy"
        for service in health_status["services"].values()
    )
    health_status["status"] = "healthy" if all_healthy else "degraded"

    return health_status

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "type": type(exc).__name__,
            "message": str(exc) if settings.DEBUG else "Internal server error"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )