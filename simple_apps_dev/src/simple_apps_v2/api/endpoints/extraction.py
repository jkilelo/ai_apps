"""
Element extraction endpoints.
"""

from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field

from simple_apps_v2.core.logging import get_logger
from simple_apps_v2.services.extractor import ElementExtractor

router = APIRouter()
logger = get_logger(__name__)


class ExtractionRequest(BaseModel):
    """Request model for element extraction."""
    url: HttpUrl = Field(..., description="URL to extract elements from")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    analyze_with_llm: bool = Field(default=False, description="Analyze with LLM")
    viewport_width: Optional[int] = Field(default=1920, description="Viewport width")
    viewport_height: Optional[int] = Field(default=1080, description="Viewport height")


class ExtractionResponse(BaseModel):
    """Response model for element extraction."""
    success: bool
    url: str
    total_elements: int
    elements: list[Dict[str, Any]]
    elements_by_category: Dict[str, list[Dict[str, Any]]]
    llm_analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/extract", response_model=ExtractionResponse)
async def extract_elements(request: ExtractionRequest) -> ExtractionResponse:
    """Extract elements from a URL."""
    try:
        logger.info(f"Extracting elements from {request.url}")
        
        extractor = ElementExtractor(
            headless=request.headless,
            viewport_size=(request.viewport_width, request.viewport_height)
        )
        
        result = await extractor.extract_elements_from_url(
            str(request.url),
            analyze_with_llm=request.analyze_with_llm
        )
        
        return ExtractionResponse(
            success=True,
            url=str(request.url),
            total_elements=result.get("total_elements", 0),
            elements=result.get("elements", []),
            elements_by_category=result.get("elements_by_category", {}),
            llm_analysis=result.get("llm_analysis"),
        )
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/analyze")
async def analyze_page(request: ExtractionRequest) -> Dict[str, Any]:
    """Analyze a page and return detailed insights."""
    try:
        logger.info(f"Analyzing page {request.url}")
        
        extractor = ElementExtractor(
            headless=request.headless,
            viewport_size=(request.viewport_width, request.viewport_height)
        )
        
        # Extract elements
        result = await extractor.extract_elements_from_url(
            str(request.url),
            analyze_with_llm=True
        )
        
        # Add analysis insights
        analysis = {
            "url": str(request.url),
            "total_elements": result.get("total_elements", 0),
            "categories": list(result.get("elements_by_category", {}).keys()),
            "interactive_elements": len([
                e for e in result.get("elements", [])
                if e.get("category") in ["button", "link", "form_input"]
            ]),
            "form_elements": len([
                e for e in result.get("elements", [])
                if e.get("category") == "form_input"
            ]),
            "navigation_elements": len([
                e for e in result.get("elements", [])
                if e.get("category") == "navigation"
            ]),
        }
        
        if result.get("llm_analysis"):
            analysis["llm_insights"] = result["llm_analysis"]
        
        return {
            "success": True,
            "analysis": analysis,
            "raw_data": result,
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }