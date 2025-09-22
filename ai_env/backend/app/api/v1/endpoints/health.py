"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.core.mcp_client import MCPClient
from app.config import settings

router = APIRouter()

@router.get("/status")
async def health_status(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get detailed health status of all services
    """
    status = {
        "api": "healthy",
        "database": "unknown",
        "mcp_server": "unknown",
        "ai_services": {}
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"unhealthy: {str(e)}"

    # Check MCP server
    try:
        async with MCPClient(settings.MCP_SERVER_URL) as mcp:
            if await mcp.check_health():
                status["mcp_server"] = "healthy"
                stats = await mcp.get_database_stats()
                if stats:
                    status["database_size"] = stats.get("database_size", {}).get("size_pretty")
            else:
                status["mcp_server"] = "unhealthy"
    except Exception as e:
        status["mcp_server"] = f"error: {str(e)}"

    # Check AI services
    status["ai_services"]["gemini"] = "configured" if settings.GEMINI_API_KEY else "not configured"
    status["ai_services"]["openai"] = "configured" if settings.OPENAI_API_KEY else "not configured"
    status["ai_services"]["anthropic"] = "configured" if settings.ANTHROPIC_API_KEY else "not configured"

    return status

@router.get("/readiness")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, bool]:
    """
    Kubernetes readiness probe endpoint
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except:
        return {"ready": False}

@router.get("/liveness")
async def liveness_check() -> Dict[str, bool]:
    """
    Kubernetes liveness probe endpoint
    """
    return {"alive": True}