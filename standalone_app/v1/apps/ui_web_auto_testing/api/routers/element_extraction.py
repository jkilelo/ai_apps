"""
Element Extraction API Router
Step 1: Extract web elements using Python Playwright
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, HttpUrl, Field

import sys
sys.path.append('/var/www/ai_apps')

from apps.ui_web_auto_testing.element_extraction.profile_crawler import ProfileCrawler
from apps.ui_web_auto_testing.element_extraction.profiles import ProfileManager
from utils.web_testing_utils import job_manager, result_formatter

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances
crawler = ProfileCrawler()
profile_manager = ProfileManager()

# Active extractions
active_extractions = {}


class ElementExtractionRequest(BaseModel):
    """Request model for element extraction"""
    web_page_url: HttpUrl = Field(..., description="URL of the web page to extract elements from")
    profile: Optional[str] = Field(default="qa_manual_tester", description="Profile type to use")
    include_screenshots: Optional[bool] = Field(default=False, description="Include element screenshots")
    max_depth: Optional[int] = Field(default=1, ge=1, le=3, description="Maximum crawl depth")
    
    model_config = {
            "example": {
                "web_page_url": "https://example.com",
                "profile": "qa_manual_tester",
                "include_screenshots": False,
                "max_depth": 1
            }
        }


class ElementExtractionResponse(BaseModel):
    """Response model for element extraction"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")
    started_at: datetime = Field(..., description="Job start time")
    
    model_config = {
            "example": {
                "job_id": "ext_12345678",
                "status": "started",
                "message": "Element extraction started successfully",
                "started_at": "2024-01-15T10:30:00"
            }
        }


class ElementExtractionResult(BaseModel):
    """Result model for element extraction"""
    job_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    extracted_elements: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/extract", response_model=ElementExtractionResponse)
async def start_element_extraction(
    request: ElementExtractionRequest,
    background_tasks: BackgroundTasks
):
    """Start element extraction from a web page"""
    job_id = f"ext_{uuid.uuid4().hex[:8]}"
    started_at = datetime.now()
    
    # Store job info
    active_extractions[job_id] = {
        "status": "running",
        "started_at": started_at,
        "request": request.model_dump()
    }
    
    # Start extraction in background
    background_tasks.add_task(
        extract_elements_task,
        job_id,
        request
    )
    
    logger.info(f"Started element extraction job {job_id} for {request.web_page_url}")
    
    return ElementExtractionResponse(
        job_id=job_id,
        status="started",
        message="Element extraction started successfully",
        started_at=started_at
    )


@router.get("/extract/{job_id}", response_model=ElementExtractionResult)
async def get_extraction_status(job_id: str):
    """Get the status and results of an element extraction job"""
    
    if job_id not in active_extractions:
        raise HTTPException(
            status_code=404,
            detail=f"Extraction job '{job_id}' not found"
        )
    
    job_data = active_extractions[job_id]
    
    return ElementExtractionResult(
        job_id=job_id,
        status=job_data["status"],
        started_at=job_data["started_at"],
        completed_at=job_data.get("completed_at"),
        duration=job_data.get("duration"),
        extracted_elements=job_data.get("extracted_elements"),
        error=job_data.get("error"),
        metadata=job_data.get("metadata")
    )


@router.get("/profiles", response_model=List[Dict[str, Any]])
async def list_extraction_profiles():
    """List available extraction profiles"""
    profiles = []
    
    for profile_name in profile_manager.list_profiles():
        profile_config = profile_manager.get_profile(profile_name)
        if profile_config:
            profiles.append({
                "name": profile_name,
                "description": profile_config.description,
                "priority_elements": [elem.value for elem in profile_config.priority_element_types],
                "report_sections": profile_config.report_sections
            })
    
    return profiles


async def extract_elements_task(job_id: str, request: ElementExtractionRequest):
    """Background task to extract elements"""
    started_at = datetime.now()
    
    try:
        logger.info(f"Executing element extraction job {job_id}")
        
        # Perform the extraction
        result = await crawler.quick_scan(
            str(request.web_page_url),
            request.profile
        )
        
        # Extract elements from the result
        extracted_elements = []
        
        if result and "results" in result:
            page_results = result["results"]
            for page_url, page_data in page_results.items():
                if "elements" in page_data:
                    for element in page_data["elements"]:
                        # Format element data for the frontend
                        extracted_elements.append({
                            "id": element.get("id", f"elem_{len(extracted_elements)}"),
                            "type": element.get("type", "unknown"),
                            "tag": element.get("tag", ""),
                            "text": element.get("text", ""),
                            "href": element.get("href", ""),
                            "selector": element.get("selector", ""),
                            "xpath": element.get("xpath", ""),
                            "attributes": element.get("attributes", {}),
                            "is_visible": element.get("is_visible", True),
                            "is_interactive": element.get("is_interactive", False),
                            "screenshot": element.get("screenshot") if request.include_screenshots else None,
                            "page_url": page_url
                        })
        
        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()
        
        # Update job data
        active_extractions[job_id].update({
            "status": "completed",
            "completed_at": completed_at,
            "duration": duration,
            "extracted_elements": extracted_elements,
            "metadata": {
                "total_elements": len(extracted_elements),
                "pages_crawled": len(result.get("results", {})),
                "profile_used": request.profile,
                "url": str(request.web_page_url)
            }
        })
        
        logger.info(f"Completed element extraction job {job_id}: {len(extracted_elements)} elements extracted")
        
    except Exception as e:
        logger.error(f"Element extraction job {job_id} failed: {e}")
        
        active_extractions[job_id].update({
            "status": "failed",
            "completed_at": datetime.now(),
            "duration": (datetime.now() - started_at).total_seconds(),
            "error": str(e)
        })


@router.delete("/extract/{job_id}")
async def cancel_extraction(job_id: str):
    """Cancel an active extraction job"""
    
    if job_id not in active_extractions:
        raise HTTPException(
            status_code=404,
            detail=f"Extraction job '{job_id}' not found"
        )
    
    job_data = active_extractions[job_id]
    
    if job_data["status"] != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Job '{job_id}' is not running (status: {job_data['status']})"
        )
    
    # Mark as cancelled
    job_data["status"] = "cancelled"
    job_data["completed_at"] = datetime.now()
    
    logger.info(f"Cancelled extraction job {job_id}")
    
    return {"message": f"Extraction job '{job_id}' cancelled successfully"}