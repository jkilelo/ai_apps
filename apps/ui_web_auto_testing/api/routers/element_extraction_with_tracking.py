"""
Element Extraction API Router with MongoDB tracking
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
from apps.common.services.execution_tracker import get_execution_tracker
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
        "json_schema_extra": {
            "example": {
                "web_page_url": "https://example.com",
                "profile": "qa_manual_tester",
                "include_screenshots": False,
                "max_depth": 1
            }
        }
    }


class ElementExtractionResponse(BaseModel):
    """Response model for element extraction"""
    status: str = Field(..., description="Status of the extraction")
    extraction_id: str = Field(..., description="Unique ID for tracking the extraction")
    message: str = Field(..., description="Status message")
    data: Optional[Dict[str, Any]] = Field(None, description="Extraction results")
    timestamp: str = Field(..., description="Timestamp of the response")


async def extract_elements_with_tracking(
    extraction_id: str,
    web_page_url: str,
    profile: str,
    include_screenshots: bool,
    max_depth: int,
    execution_id: str,
    user_id: Optional[str] = None
):
    """Background task to extract elements with MongoDB tracking"""
    tracker = await get_execution_tracker()
    
    try:
        # Track the step execution
        async with tracker.track_step(
            execution_id=execution_id,
            step_id=1,
            step_name="element_extraction_using_python_playwright",
            step_version="1.0.0",
            input_data={
                "web_page_url": web_page_url,
                "profile": profile,
                "include_screenshots": include_screenshots,
                "max_depth": max_depth
            }
        ) as set_output:
            
            # Update status
            active_extractions[extraction_id] = {
                "status": "running",
                "started_at": datetime.utcnow().isoformat(),
                "message": "Starting element extraction..."
            }
            
            # Initialize crawler and profile
            profile_instance = profile_manager.get_profile(profile)()
            elements = []
            pages_crawled = 0
            
            # Initialize Playwright
            await crawler.initialize()
            
            try:
                # Crawl the URL
                async for element in crawler.crawl(
                    web_page_url, 
                    profile_instance, 
                    max_depth=max_depth
                ):
                    elements.append(element)
                    
                    # Update progress
                    active_extractions[extraction_id]["message"] = f"Extracted {len(elements)} elements..."
                    
                    # Log screenshots as artifacts if enabled
                    if include_screenshots and element.get("screenshot"):
                        await tracker.log_artifact(
                            execution_id=execution_id,
                            step_id=1,
                            artifact_type="screenshot",
                            artifact_name=f"element_{element['id']}.png",
                            content=element["screenshot"],
                            mime_type="image/png",
                            metadata={
                                "element_type": element.get("type"),
                                "selector": element.get("selector")
                            }
                        )
                
                pages_crawled = crawler.pages_crawled
                
                # Format results
                extraction_results = {
                    "extracted_elements": elements,
                    "metadata": {
                        "total_elements": len(elements),
                        "pages_crawled": pages_crawled,
                        "profile_used": profile,
                        "max_depth": max_depth,
                        "url": web_page_url
                    }
                }
                
                # Set output for MongoDB
                set_output(extraction_results)
                
                # Update active extractions
                active_extractions[extraction_id] = {
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat(),
                    "data": extraction_results,
                    "message": f"Successfully extracted {len(elements)} elements from {pages_crawled} pages"
                }
                
            finally:
                # Clean up
                await crawler.cleanup()
                
    except Exception as e:
        logger.error(f"Element extraction failed: {str(e)}")
        error_message = f"Extraction failed: {str(e)}"
        
        active_extractions[extraction_id] = {
            "status": "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "error": error_message,
            "message": error_message
        }
        
        # Re-raise to let tracker handle the error
        raise


@router.post("/extract", response_model=ElementExtractionResponse)
async def extract_elements(
    request: ElementExtractionRequest,
    background_tasks: BackgroundTasks,
    req: Request
):
    """
    Extract web elements from a given URL using Playwright
    
    This endpoint initiates an asynchronous element extraction process.
    The extraction runs in the background and results can be retrieved using the extraction_id.
    """
    extraction_id = str(uuid.uuid4())
    
    # Get user info from request if available
    user_id = getattr(req.state, "user_id", None)
    
    # Get execution tracker
    tracker = await get_execution_tracker()
    
    # Create main execution record
    async with tracker.track_execution(
        app_id=2,
        app_name="ui_web_auto_testing",
        user_id=user_id,
        metadata={
            "endpoint": "/extract",
            "ip_address": req.client.host if req.client else None,
            "user_agent": req.headers.get("user-agent")
        }
    ) as execution_id:
        
        # Start background task
        background_tasks.add_task(
            extract_elements_with_tracking,
            extraction_id=extraction_id,
            web_page_url=str(request.web_page_url),
            profile=request.profile,
            include_screenshots=request.include_screenshots,
            max_depth=request.max_depth,
            execution_id=execution_id,
            user_id=user_id
        )
        
        # Store initial status
        active_extractions[extraction_id] = {
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "message": "Extraction job queued"
        }
        
        return ElementExtractionResponse(
            status="accepted",
            extraction_id=extraction_id,
            message="Element extraction started. Use the extraction_id to check status.",
            timestamp=datetime.utcnow().isoformat()
        )


@router.get("/extract/{extraction_id}", response_model=ElementExtractionResponse)
async def get_extraction_status(extraction_id: str):
    """
    Get the status and results of an element extraction job
    
    Use the extraction_id returned from the /extract endpoint to check the status
    and retrieve results once the extraction is complete.
    """
    if extraction_id not in active_extractions:
        raise HTTPException(
            status_code=404,
            detail=f"Extraction job {extraction_id} not found"
        )
    
    extraction_data = active_extractions[extraction_id]
    
    return ElementExtractionResponse(
        status=extraction_data["status"],
        extraction_id=extraction_id,
        message=extraction_data.get("message", ""),
        data=extraction_data.get("data"),
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/history")
async def get_extraction_history(
    req: Request,
    limit: int = 10
):
    """
    Get extraction history for the current user
    
    Returns a list of recent element extraction executions with their results
    """
    user_id = getattr(req.state, "user_id", None)
    tracker = await get_execution_tracker()
    
    history = await tracker.get_execution_history(
        user_id=user_id,
        app_id=2,  # ui_web_auto_testing
        limit=limit
    )
    
    return {
        "history": history,
        "count": len(history),
        "timestamp": datetime.utcnow().isoformat()
    }