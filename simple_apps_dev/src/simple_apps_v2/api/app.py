"""
Modern FastAPI application factory with proper configuration.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from simple_apps_v2.api.routes import router
from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import get_logger, setup_logging

# Fix for Windows async subprocess
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    settings = get_settings()
    
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    settings.create_directories()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    # Setup logging first
    setup_logging()
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="A modern web automation testing application with consolidated dependencies",
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Add middleware
    _configure_middleware(app, settings)
    
    # Add exception handlers
    _configure_exception_handlers(app)
    
    # Include routers
    app.include_router(router, prefix="/api")
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.version,
            "debug": settings.debug,
        }
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.version,
            "docs": "/docs" if settings.debug else "Documentation disabled in production",
        }
    
    logger.info("FastAPI application created successfully")
    return app


def _configure_middleware(app: FastAPI, settings) -> None:
    """Configure application middleware."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log HTTP requests."""
        start_time = time.time()
        
        # Skip logging for health checks in production
        if not settings.debug and request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.3f}s"
        )
        
        return response
    
    # Error tracking middleware
    @app.middleware("http")
    async def error_tracking(request: Request, call_next):
        """Track and log errors."""
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                f"Unhandled error in {request.method} {request.url.path}: {e}",
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(e) if settings.debug else "An error occurred",
                    "path": str(request.url.path),
                }
            )


def _configure_exception_handlers(app: FastAPI) -> None:
    """Configure custom exception handlers."""
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions."""
        logger.warning(f"ValueError in {request.url.path}: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Bad Request",
                "message": str(exc),
                "path": str(request.url.path),
            }
        )
    
    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        """Handle FileNotFoundError exceptions."""
        logger.warning(f"FileNotFoundError in {request.url.path}: {exc}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "File Not Found",
                "message": str(exc),
                "path": str(request.url.path),
            }
        )
    
    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        """Handle PermissionError exceptions."""
        logger.error(f"PermissionError in {request.url.path}: {exc}")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Permission Denied",
                "message": "Insufficient permissions",
                "path": str(request.url.path),
            }
        )


# Import time for middleware
import time