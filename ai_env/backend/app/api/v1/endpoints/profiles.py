"""
Profile management endpoints
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()

@router.get("/")
async def get_profiles(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all infrastructure profiles"""
    return [
        {"id": 1, "name": "POC", "type": "poc", "ai_first": True, "llm_provider": "gemini"},
        {"id": 2, "name": "Local Dev", "type": "local", "ai_first": True, "llm_provider": "gemini"},
        {"id": 3, "name": "Enterprise", "type": "enterprise", "ai_first": True, "llm_provider": "multi"}
    ]