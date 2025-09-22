"""
Infrastructure management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()

@router.get("/components")
async def get_components(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all infrastructure components
    """
    # TODO: Implement database query for components
    return [
        {
            "id": 1,
            "code": "gemini_api",
            "name": "Google Gemini API",
            "category": "ai_services",
            "is_ai_component": True,
            "status": "active"
        },
        {
            "id": 2,
            "code": "postgresql",
            "name": "PostgreSQL 17",
            "category": "databases",
            "is_ai_component": False,
            "status": "active"
        }
    ]

@router.get("/layers")
async def get_layers(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get infrastructure layers
    """
    return [
        {"id": 1, "name": "Infrastructure", "order": 1},
        {"id": 2, "name": "Backend", "order": 2},
        {"id": 3, "name": "Frontend", "order": 3},
        {"id": 4, "name": "AI/LLM", "order": 4}
    ]

@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get component categories
    """
    return [
        {"id": 1, "name": "AI Services", "code": "ai_services"},
        {"id": 2, "name": "Databases", "code": "databases"},
        {"id": 3, "name": "Web Frameworks", "code": "web_frameworks"},
        {"id": 4, "name": "Monitoring", "code": "monitoring"}
    ]