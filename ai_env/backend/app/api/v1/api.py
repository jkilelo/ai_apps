"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    infrastructure,
    profiles,
    audit,
    health,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    infrastructure.router,
    prefix="/infrastructure",
    tags=["infrastructure"]
)

api_router.include_router(
    profiles.router,
    prefix="/profiles",
    tags=["profiles"]
)

api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit"]
)