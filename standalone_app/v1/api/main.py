"""
Main FastAPI application for v1 standalone app
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Dict, Any, List
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb_client import get_mongodb, StepStatus
from api.llm_routes import router as llm_router
from api.web_automation_routes import router as web_automation_router
from api.data_profiling_routes import router as data_profiling_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting v1 standalone app...")
    try:
        mongodb = await get_mongodb()
        await mongodb.connect()
        logger.info("MongoDB connected")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Running without database.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down v1 standalone app...")
    try:
        mongodb = await get_mongodb()
        if mongodb.client:
            await mongodb.disconnect()
            logger.info("MongoDB disconnected")
    except:
        pass


# Create FastAPI app
app = FastAPI(
    title="AI Apps Standalone v1",
    description="Standalone fullstack AI application with web automation and data profiling",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8004", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(llm_router, prefix="/api", tags=["LLM"])
app.include_router(web_automation_router, prefix="/api/web_automation", tags=["Web Automation"])
app.include_router(data_profiling_router, prefix="/api/data_profiling", tags=["Data Profiling"])

# Serve React app
if os.path.exists("/var/www/ai_apps/standalone_app/v1/frontend/dist"):
    app.mount("/", StaticFiles(directory="/var/www/ai_apps/standalone_app/v1/frontend/dist", html=True), name="static")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Apps Standalone v1",
        "version": "1.0.0"
    }


@app.get("/api/sessions/web_automation")
async def list_web_automation_sessions(limit: int = 10, skip: int = 0):
    """List web automation sessions"""
    mongodb = await get_mongodb()
    sessions = await mongodb.list_web_sessions(limit=limit, skip=skip)
    return [
        {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "current_step": _get_current_web_step(session)
        }
        for session in sessions
    ]


@app.get("/api/sessions/data_profiling")
async def list_data_profiling_sessions(limit: int = 10, skip: int = 0):
    """List data profiling sessions"""
    mongodb = await get_mongodb()
    sessions = await mongodb.list_data_sessions(limit=limit, skip=skip)
    return [
        {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "current_step": _get_current_data_step(session)
        }
        for session in sessions
    ]


def _get_current_web_step(session) -> str:
    """Get current step for web automation session"""
    if session.execute_python_status == StepStatus.COMPLETED:
        return "completed"
    elif session.generate_python_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_4"
    elif session.generate_gherkin_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_3"
    elif session.extract_elements_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_2"
    else:
        return "step_1"


def _get_current_data_step(session) -> str:
    """Get current step for data profiling session"""
    if session.execute_pyspark_dq_status == StepStatus.COMPLETED:
        return "completed"
    elif session.generate_pyspark_dq_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_8"
    elif session.dq_tests_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_7"
    elif session.dq_suggestions_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_6"
    elif session.execute_pyspark_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_5"
    elif session.generate_pyspark_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_4"
    elif session.profiling_testcases_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_3"
    elif session.profiling_suggestions_status in [StepStatus.IN_PROGRESS, StepStatus.COMPLETED]:
        return "step_2"
    else:
        return "step_1"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)