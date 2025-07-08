"""
Web automation API routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json
import asyncio
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb_client import get_mongodb, StepStatus
from web_automation.element_extractor import extract_elements_from_url
from web_automation.gherkin_generator import generate_gherkin_tests
from web_automation.python_generator import generate_python_code
from web_automation.code_executor import execute_python_code

logger = logging.getLogger(__name__)

router = APIRouter()


class ExtractElementsRequest(BaseModel):
    input: str  # URL to extract elements from


class ExtractElementsResponse(BaseModel):
    output: List[Dict[str, Any]]
    session_id: str


class GenerateGherkinRequest(BaseModel):
    input: str  # Test scenario description
    session_id: str


class GenerateGherkinResponse(BaseModel):
    output: List[Dict[str, Any]]


class GeneratePythonRequest(BaseModel):
    input: str  # Gherkin tests or test description
    session_id: str


class GeneratePythonResponse(BaseModel):
    output: str


class ExecutePythonRequest(BaseModel):
    input: str  # Python code to execute
    session_id: str


class ExecutePythonResponse(BaseModel):
    output: str


@router.post("/extract_elements", response_model=ExtractElementsResponse)
async def extract_elements_endpoint(request: ExtractElementsRequest, background_tasks: BackgroundTasks):
    """
    Step 1: Extract elements from a URL
    """
    try:
        # Create new session
        mongodb = await get_mongodb()
        session_id = await mongodb.create_web_session()
        
        # Update session with input and status
        await mongodb.update_web_session(session_id, {
            "extract_elements_input": request.input,
            "extract_elements_status": StepStatus.IN_PROGRESS
        })
        
        # Extract elements
        elements = await extract_elements_from_url(request.input)
        
        # Update session with output
        await mongodb.update_web_session(session_id, {
            "extract_elements_output": elements,
            "extract_elements_status": StepStatus.COMPLETED
        })
        
        return ExtractElementsResponse(output=elements, session_id=session_id)
        
    except Exception as e:
        logger.error(f"Extract elements error: {str(e)}")
        if 'session_id' in locals():
            await mongodb.update_web_session(session_id, {
                "extract_elements_status": StepStatus.ERROR
            })
        raise HTTPException(status_code=500, detail=f"Element extraction failed: {str(e)}")


@router.post("/generate_gherkin_tests", response_model=GenerateGherkinResponse)
async def generate_gherkin_endpoint(request: GenerateGherkinRequest):
    """
    Step 2: Generate Gherkin tests
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_web_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update status
        await mongodb.update_web_session(request.session_id, {
            "generate_gherkin_input": request.input,
            "generate_gherkin_status": StepStatus.IN_PROGRESS
        })
        
        # Generate Gherkin tests
        gherkin_tests = await generate_gherkin_tests(
            request.input,
            session.extract_elements_output
        )
        
        # Update session
        await mongodb.update_web_session(request.session_id, {
            "generate_gherkin_output": gherkin_tests,
            "generate_gherkin_status": StepStatus.COMPLETED
        })
        
        return GenerateGherkinResponse(output=gherkin_tests)
        
    except Exception as e:
        logger.error(f"Generate Gherkin error: {str(e)}")
        await mongodb.update_web_session(request.session_id, {
            "generate_gherkin_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"Gherkin generation failed: {str(e)}")


@router.post("/generate_python_code", response_model=GeneratePythonResponse)
async def generate_python_endpoint(request: GeneratePythonRequest):
    """
    Step 3: Generate Python code
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_web_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update status
        await mongodb.update_web_session(request.session_id, {
            "generate_python_input": request.input,
            "generate_python_status": StepStatus.IN_PROGRESS
        })
        
        # Generate Python code
        python_code = await generate_python_code(
            request.input,
            session.generate_gherkin_output or []
        )
        
        # Update session
        await mongodb.update_web_session(request.session_id, {
            "generate_python_output": python_code,
            "generate_python_status": StepStatus.COMPLETED
        })
        
        return GeneratePythonResponse(output=python_code)
        
    except Exception as e:
        logger.error(f"Generate Python error: {str(e)}")
        await mongodb.update_web_session(request.session_id, {
            "generate_python_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"Python generation failed: {str(e)}")


@router.post("/execute_python_code", response_model=ExecutePythonResponse)
async def execute_python_endpoint(request: ExecutePythonRequest):
    """
    Step 4: Execute Python code
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_web_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update status
        await mongodb.update_web_session(request.session_id, {
            "execute_python_input": request.input,
            "execute_python_status": StepStatus.IN_PROGRESS
        })
        
        # Execute Python code
        execution_result = await execute_python_code(request.input)
        
        # Update session
        await mongodb.update_web_session(request.session_id, {
            "execute_python_output": execution_result,
            "execute_python_status": StepStatus.COMPLETED
        })
        
        return ExecutePythonResponse(output=execution_result)
        
    except Exception as e:
        logger.error(f"Execute Python error: {str(e)}")
        await mongodb.update_web_session(request.session_id, {
            "execute_python_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"Python execution failed: {str(e)}")


@router.get("/session/{session_id}")
async def get_web_session(session_id: str):
    """Get web automation session details"""
    mongodb = await get_mongodb()
    session = await mongodb.get_web_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.dict(exclude_unset=True)