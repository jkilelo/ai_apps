"""
Health check endpoints.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status

from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.version,
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """Readiness check endpoint."""
    checks = {
        "config": True,
        "directories": True,
    }
    
    # Check if directories exist
    try:
        checks["directories"] = (
            settings.test_output_dir.exists() and 
            settings.screenshot_dir.exists()
        )
    except Exception as e:
        logger.error(f"Directory check failed: {e}")
        checks["directories"] = False
    
    all_ready = all(checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/config", status_code=status.HTTP_200_OK)
async def get_config() -> Dict[str, Any]:
    """Get current configuration (non-sensitive)."""
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "api": {
            "host": settings.api_host,
            "port": settings.api_port,
        },
        "browser": {
            "headless": settings.browser_headless,
            "viewport": {
                "width": settings.browser_viewport_width,
                "height": settings.browser_viewport_height,
            }
        },
    }