"""
FastAPI application for Simple Apps v2.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import get_logger
from simple_apps_v2.api.endpoints import extraction, health, tests, code

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage application lifecycle."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    settings.create_directories()
    yield
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(extraction.router, prefix="/api/extraction", tags=["extraction"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])
app.include_router(code.router, prefix="/api/code", tags=["code"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }