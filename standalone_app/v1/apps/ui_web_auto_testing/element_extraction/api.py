"""
Production-ready FastAPI server for Web Crawler

This module provides a comprehensive FastAPI interface for the web crawler
with authentication, rate limiting, validation, and monitoring.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, field_validator, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from apps.ui_web_auto_testing.element_extraction.profile_crawler import ProfileCrawler
from apps.ui_web_auto_testing.element_extraction.profiles import ProfileManager, ProfileType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Global state
app_state = {
    "crawler": None,
    "profile_manager": None,
    "active_crawls": {},
    "crawl_history": [],
    "server_start_time": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Web Crawler API Server...")
    app_state["crawler"] = ProfileCrawler()
    app_state["profile_manager"] = ProfileManager()
    app_state["server_start_time"] = datetime.now()
    logger.info("Server initialization complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Web Crawler API Server...")
    # Cancel any active crawls
    for crawl_id, task in app_state["active_crawls"].items():
        if not task.done():
            task.cancel()
            logger.info(f"Cancelled active crawl: {crawl_id}")
    logger.info("Server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Web Crawler API",
    description="Production-ready web crawler with profile-based analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this for production
)

app.add_middleware(SlowAPIMiddleware)

# Rate limiting error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security
security = HTTPBearer(auto_error=False)


# Pydantic models
class CrawlRequest(BaseModel):
    """Request model for crawl operations"""
    url: HttpUrl = Field(..., description="URL to crawl")
    profile: str = Field(..., description="Profile type to use", pattern="^[a-z_]+$")
    max_depth: Optional[int] = Field(default=None, ge=1, le=5, description="Maximum crawl depth")
    max_pages: Optional[int] = Field(default=None, ge=1, le=100, description="Maximum pages to crawl")
    save_results: Optional[bool] = Field(default=False, description="Save results to file")
    include_screenshots: Optional[bool] = Field(default=False, description="Include element screenshots")
    
    @field_validator('profile')
    @classmethod
    def validate_profile(cls, v):
        """Validate profile exists"""
        manager = ProfileManager()
        if v not in manager.list_profiles():
            raise ValueError(f"Profile '{v}' not found. Available: {', '.join(manager.list_profiles())}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com",
                "profile": "qa_manual_tester",
                "max_depth": 2,
                "max_pages": 10,
                "save_results": False
            }
        }


class QuickScanRequest(BaseModel):
    """Request model for quick scan operations"""
    url: HttpUrl = Field(..., description="URL to crawl")
    profile: str = Field(default="qa_manual_tester", description="Profile type to use")
    
    @field_validator('profile')
    @classmethod
    def validate_profile(cls, v):
        manager = ProfileManager()
        if v not in manager.list_profiles():
            raise ValueError(f"Profile '{v}' not found")
        return v


class CrawlResponse(BaseModel):
    """Response model for crawl operations"""
    crawl_id: str = Field(..., description="Unique crawl identifier")
    status: str = Field(..., description="Crawl status")
    message: str = Field(..., description="Status message")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "crawl_id": "crawl_12345",
                "status": "started",
                "message": "Crawl started successfully",
                "estimated_duration": 30
            }
        }


class CrawlResultResponse(BaseModel):
    """Response model for crawl results"""
    crawl_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProfileInfo(BaseModel):
    """Profile information model"""
    name: str
    description: str
    priority_elements: List[str]
    features: List[str]
    use_case: str


class ServerStatus(BaseModel):
    """Server status model"""
    status: str
    uptime: str
    active_crawls: int
    total_crawls: int
    available_profiles: int
    memory_usage: Optional[Dict[str, Any]] = None


# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple authentication - replace with your auth system"""
    if not credentials:
        return {"user": "anonymous", "permissions": ["read"]}
    
    # Simple token validation - replace with your auth logic
    token = credentials.credentials
    if token == "demo-token":
        return {"user": "demo", "permissions": ["read", "write"]}
    elif token.startswith("api-"):
        return {"user": "api_user", "permissions": ["read", "write"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_permissions(required_permission: str):
    """Check if user has required permission"""
    def permission_checker(user: dict = Depends(get_current_user)):
        if required_permission not in user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return user
    return permission_checker


# API Routes

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Web Crawler API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=ServerStatus)
async def health_check():
    """Health check endpoint"""
    uptime = datetime.now() - app_state["server_start_time"]
    
    # Get memory usage
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_info = {
            "rss": process.memory_info().rss,
            "vms": process.memory_info().vms,
            "percent": process.memory_percent()
        }
    except ImportError:
        memory_info = None
    
    return ServerStatus(
        status="healthy",
        uptime=str(uptime),
        active_crawls=len(app_state["active_crawls"]),
        total_crawls=len(app_state["crawl_history"]),
        available_profiles=len(app_state["profile_manager"].list_profiles()),
        memory_usage=memory_info
    )


@app.get("/profiles", response_model=List[ProfileInfo])
async def list_profiles():
    """List all available profiles"""
    profiles = []
    manager = app_state["profile_manager"]
    
    for profile_type in manager.list_profiles():
        profile_config = manager.get_profile(profile_type)
        if profile_config:
            profiles.append(ProfileInfo(
                name=profile_config.profile_name,
                description=profile_config.description,
                priority_elements=[elem.value for elem in profile_config.priority_element_types],
                features=profile_config.report_sections,
                use_case=profile_type.replace("_", " ").title()
            ))
    
    return profiles


@app.get("/profiles/{profile_name}", response_model=Dict[str, Any])
async def get_profile_details(profile_name: str):
    """Get detailed information about a specific profile"""
    manager = app_state["profile_manager"]
    profile_config = manager.get_profile_config_dict(profile_name)
    
    if not profile_config:
        raise HTTPException(
            status_code=404,
            detail=f"Profile '{profile_name}' not found"
        )
    
    return profile_config


@app.post("/crawl", response_model=CrawlResponse)
@limiter.limit("10/minute")
async def start_crawl(
    request: Request,
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(check_permissions("write"))
):
    """Start a new crawl with specified profile"""
    crawl_id = f"crawl_{uuid.uuid4().hex[:8]}"
    
    # Estimate duration based on depth and pages
    estimated_duration = (crawl_request.max_depth or 2) * (crawl_request.max_pages or 10) * 2
    
    # Create background task
    task = asyncio.create_task(
        _execute_crawl(crawl_id, crawl_request, user["user"])
    )
    
    app_state["active_crawls"][crawl_id] = task
    
    logger.info(f"Started crawl {crawl_id} for {crawl_request.url} with profile {crawl_request.profile}")
    
    return CrawlResponse(
        crawl_id=crawl_id,
        status="started",
        message="Crawl started successfully",
        estimated_duration=estimated_duration
    )


@app.post("/quick-scan", response_model=Dict[str, Any])
@limiter.limit("20/minute")
async def quick_scan(
    request: Request,
    scan_request: QuickScanRequest,
    user: dict = Depends(check_permissions("read"))
):
    """Perform a quick scan (depth=1, pages=1)"""
    try:
        logger.info(f"Quick scan requested for {scan_request.url} with profile {scan_request.profile}")
        
        result = await app_state["crawler"].quick_scan(
            str(scan_request.url),
            scan_request.profile
        )
        
        # Add request metadata
        result["request_info"] = {
            "requested_by": user["user"],
            "request_time": datetime.now().isoformat(),
            "scan_type": "quick"
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Quick scan failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick scan failed: {str(e)}"
        )


@app.get("/crawl/{crawl_id}/status", response_model=CrawlResultResponse)
async def get_crawl_status(
    crawl_id: str,
    user: dict = Depends(get_current_user)
):
    """Get the status of a specific crawl"""
    
    # Check active crawls
    if crawl_id in app_state["active_crawls"]:
        task = app_state["active_crawls"][crawl_id]
        
        if task.done():
            try:
                result = task.result()
                return CrawlResultResponse(
                    crawl_id=crawl_id,
                    status="completed",
                    started_at=result.get("started_at"),
                    completed_at=result.get("completed_at"),
                    duration=result.get("duration"),
                    results=result.get("results")
                )
            except Exception as e:
                return CrawlResultResponse(
                    crawl_id=crawl_id,
                    status="failed",
                    started_at=datetime.now(),
                    error=str(e)
                )
        else:
            return CrawlResultResponse(
                crawl_id=crawl_id,
                status="running",
                started_at=datetime.now()
            )
    
    # Check history
    for crawl in app_state["crawl_history"]:
        if crawl["crawl_id"] == crawl_id:
            return CrawlResultResponse(**crawl)
    
    raise HTTPException(
        status_code=404,
        detail=f"Crawl '{crawl_id}' not found"
    )


@app.get("/crawl/{crawl_id}/results", response_model=Dict[str, Any])
async def get_crawl_results(
    crawl_id: str,
    user: dict = Depends(get_current_user)
):
    """Get the full results of a completed crawl"""
    
    # Check if crawl exists and is completed
    crawl_status = await get_crawl_status(crawl_id, user)
    
    if crawl_status.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Crawl '{crawl_id}' is not completed. Status: {crawl_status.status}"
        )
    
    if not crawl_status.results:
        raise HTTPException(
            status_code=404,
            detail=f"Results for crawl '{crawl_id}' not found"
        )
    
    return crawl_status.results


@app.delete("/crawl/{crawl_id}")
async def cancel_crawl(
    crawl_id: str,
    user: dict = Depends(check_permissions("write"))
):
    """Cancel an active crawl"""
    
    if crawl_id not in app_state["active_crawls"]:
        raise HTTPException(
            status_code=404,
            detail=f"Active crawl '{crawl_id}' not found"
        )
    
    task = app_state["active_crawls"][crawl_id]
    
    if task.done():
        raise HTTPException(
            status_code=400,
            detail=f"Crawl '{crawl_id}' is already completed"
        )
    
    task.cancel()
    del app_state["active_crawls"][crawl_id]
    
    logger.info(f"Cancelled crawl {crawl_id} by user {user['user']}")
    
    return {"message": f"Crawl '{crawl_id}' cancelled successfully"}


@app.get("/crawls", response_model=List[Dict[str, Any]])
async def list_crawls(
    status_filter: Optional[str] = None,
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """List recent crawls with optional status filter"""
    
    crawls = []
    
    # Add active crawls
    for crawl_id, task in app_state["active_crawls"].items():
        crawls.append({
            "crawl_id": crawl_id,
            "status": "completed" if task.done() else "running",
            "started_at": datetime.now().isoformat()  # Placeholder
        })
    
    # Add historical crawls
    crawls.extend(app_state["crawl_history"])
    
    # Filter by status
    if status_filter:
        crawls = [c for c in crawls if c.get("status") == status_filter]
    
    # Sort by start time and limit
    crawls.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    
    return crawls[:limit]


@app.get("/stats", response_model=Dict[str, Any])
async def get_stats(user: dict = Depends(get_current_user)):
    """Get server statistics"""
    
    total_crawls = len(app_state["crawl_history"]) + len(app_state["active_crawls"])
    completed_crawls = len([c for c in app_state["crawl_history"] if c.get("status") == "completed"])
    failed_crawls = len([c for c in app_state["crawl_history"] if c.get("status") == "failed"])
    
    return {
        "server_uptime": str(datetime.now() - app_state["server_start_time"]),
        "total_crawls": total_crawls,
        "active_crawls": len(app_state["active_crawls"]),
        "completed_crawls": completed_crawls,
        "failed_crawls": failed_crawls,
        "success_rate": (completed_crawls / total_crawls * 100) if total_crawls > 0 else 0,
        "available_profiles": len(app_state["profile_manager"].list_profiles())
    }


# Background task for crawl execution
async def _execute_crawl(crawl_id: str, crawl_request: CrawlRequest, user: str):
    """Execute crawl in background"""
    started_at = datetime.now()
    
    try:
        logger.info(f"Executing crawl {crawl_id}")
        
        # Perform the crawl
        results = await app_state["crawler"].crawl_with_profile(
            url=str(crawl_request.url),
            profile_type=crawl_request.profile,
            max_depth=crawl_request.max_depth,
            max_pages=crawl_request.max_pages,
            save_results=crawl_request.save_results
        )
        
        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()
        
        # Store results
        crawl_data = {
            "crawl_id": crawl_id,
            "status": "completed",
            "started_at": started_at,
            "completed_at": completed_at,
            "duration": duration,
            "results": results,
            "requested_by": user,
            "profile_used": crawl_request.profile,
            "url": str(crawl_request.url)
        }
        
        app_state["crawl_history"].append(crawl_data)
        
        # Remove from active crawls
        if crawl_id in app_state["active_crawls"]:
            del app_state["active_crawls"][crawl_id]
        
        logger.info(f"Completed crawl {crawl_id} in {duration:.2f}s")
        
        return crawl_data
        
    except Exception as e:
        logger.error(f"Crawl {crawl_id} failed: {e}")
        
        # Store error
        crawl_data = {
            "crawl_id": crawl_id,
            "status": "failed",
            "started_at": started_at,
            "error": str(e),
            "requested_by": user,
            "profile_used": crawl_request.profile,
            "url": str(crawl_request.url)
        }
        
        app_state["crawl_history"].append(crawl_data)
        
        # Remove from active crawls
        if crawl_id in app_state["active_crawls"]:
            del app_state["active_crawls"][crawl_id]
        
        raise e


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )