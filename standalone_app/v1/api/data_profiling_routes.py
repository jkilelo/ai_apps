"""
Data profiling API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb_client import get_mongodb, StepStatus
from data_profiling.profiling_suggestions import generate_profiling_suggestions
from data_profiling.testcase_generator import generate_profiling_testcases
from data_profiling.pyspark_generator import generate_pyspark_code, generate_pyspark_dq_code
from data_profiling.pyspark_executor import execute_pyspark_code
from data_profiling.dq_suggestions import generate_dq_suggestions
from data_profiling.dq_test_generator import generate_dq_tests

logger = logging.getLogger(__name__)

router = APIRouter()


class ProfilingSuggestionsRequest(BaseModel):
    database_name: str
    table_name: str
    columns: List[str]


class ProfilingSuggestionsResponse(BaseModel):
    output: List[Dict[str, Any]]
    session_id: str


class ProfilingTestcasesRequest(BaseModel):
    input: List[Dict[str, Any]]  # Output from step 1
    session_id: str


class ProfilingTestcasesResponse(BaseModel):
    output: List[Dict[str, Any]]


class GeneratePySparkRequest(BaseModel):
    input: List[Dict[str, Any]]  # Output from step 2
    session_id: str


class GeneratePySparkResponse(BaseModel):
    output: str


class ExecutePySparkRequest(BaseModel):
    input: str  # PySpark code
    session_id: str


class ExecutePySparkResponse(BaseModel):
    output: str


class DQSuggestionsRequest(BaseModel):
    input: str  # Output from step 4
    session_id: str


class DQSuggestionsResponse(BaseModel):
    output: List[Dict[str, Any]]


class DQTestsRequest(BaseModel):
    input: List[Dict[str, Any]]  # Output from step 5
    session_id: str


class DQTestsResponse(BaseModel):
    output: List[Dict[str, Any]]


@router.post("/generate_profiling_suggestions", response_model=ProfilingSuggestionsResponse)
async def profiling_suggestions_endpoint(request: ProfilingSuggestionsRequest):
    """
    Step 1: Generate profiling suggestions
    """
    try:
        # Create new session
        mongodb = await get_mongodb()
        session_id = await mongodb.create_data_session()
        
        # Update session with input
        input_data = {
            "database_name": request.database_name,
            "table_name": request.table_name,
            "columns": request.columns
        }
        
        await mongodb.update_data_session(session_id, {
            "profiling_suggestions_input": input_data,
            "profiling_suggestions_status": StepStatus.IN_PROGRESS
        })
        
        # Generate suggestions
        suggestions = await generate_profiling_suggestions(
            request.database_name,
            request.table_name,
            request.columns
        )
        
        # Update session
        await mongodb.update_data_session(session_id, {
            "profiling_suggestions_output": suggestions,
            "profiling_suggestions_status": StepStatus.COMPLETED
        })
        
        return ProfilingSuggestionsResponse(output=suggestions, session_id=session_id)
        
    except Exception as e:
        logger.error(f"Profiling suggestions error: {str(e)}")
        if 'session_id' in locals():
            await mongodb.update_data_session(session_id, {
                "profiling_suggestions_status": StepStatus.ERROR
            })
        raise HTTPException(status_code=500, detail=f"Profiling suggestions failed: {str(e)}")


@router.post("/generate_profiling_testcases", response_model=ProfilingTestcasesResponse)
async def profiling_testcases_endpoint(request: ProfilingTestcasesRequest):
    """
    Step 2: Generate profiling test cases
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_data_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await mongodb.update_data_session(request.session_id, {
            "profiling_testcases_input": request.input,
            "profiling_testcases_status": StepStatus.IN_PROGRESS
        })
        
        # Generate test cases
        testcases = await generate_profiling_testcases(request.input)
        
        await mongodb.update_data_session(request.session_id, {
            "profiling_testcases_output": testcases,
            "profiling_testcases_status": StepStatus.COMPLETED
        })
        
        return ProfilingTestcasesResponse(output=testcases)
        
    except Exception as e:
        logger.error(f"Profiling testcases error: {str(e)}")
        await mongodb.update_data_session(request.session_id, {
            "profiling_testcases_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"Testcase generation failed: {str(e)}")


@router.post("/generate_pyspark_code", response_model=GeneratePySparkResponse)
async def generate_pyspark_endpoint(request: GeneratePySparkRequest):
    """
    Step 3: Generate PySpark code
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_data_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await mongodb.update_data_session(request.session_id, {
            "generate_pyspark_input": request.input,
            "generate_pyspark_status": StepStatus.IN_PROGRESS
        })
        
        # Generate PySpark code
        pyspark_code = await generate_pyspark_code(request.input)
        
        await mongodb.update_data_session(request.session_id, {
            "generate_pyspark_output": pyspark_code,
            "generate_pyspark_status": StepStatus.COMPLETED
        })
        
        return GeneratePySparkResponse(output=pyspark_code)
        
    except Exception as e:
        logger.error(f"Generate PySpark error: {str(e)}")
        await mongodb.update_data_session(request.session_id, {
            "generate_pyspark_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"PySpark generation failed: {str(e)}")


@router.post("/execute_pyspark_code", response_model=ExecutePySparkResponse)
async def execute_pyspark_endpoint(request: ExecutePySparkRequest):
    """
    Step 4: Execute PySpark code
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_data_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await mongodb.update_data_session(request.session_id, {
            "execute_pyspark_input": request.input,
            "execute_pyspark_status": StepStatus.IN_PROGRESS
        })
        
        # Execute PySpark code
        result = await execute_pyspark_code(request.input)
        
        await mongodb.update_data_session(request.session_id, {
            "execute_pyspark_output": result,
            "execute_pyspark_status": StepStatus.COMPLETED
        })
        
        return ExecutePySparkResponse(output=result)
        
    except Exception as e:
        logger.error(f"Execute PySpark error: {str(e)}")
        await mongodb.update_data_session(request.session_id, {
            "execute_pyspark_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"PySpark execution failed: {str(e)}")


@router.post("/generate_dq_suggestions", response_model=DQSuggestionsResponse)
async def dq_suggestions_endpoint(request: DQSuggestionsRequest):
    """
    Step 5: Generate DQ suggestions
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_data_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await mongodb.update_data_session(request.session_id, {
            "dq_suggestions_input": request.input,
            "dq_suggestions_status": StepStatus.IN_PROGRESS
        })
        
        # Generate DQ suggestions
        suggestions = await generate_dq_suggestions(request.input)
        
        await mongodb.update_data_session(request.session_id, {
            "dq_suggestions_output": suggestions,
            "dq_suggestions_status": StepStatus.COMPLETED
        })
        
        return DQSuggestionsResponse(output=suggestions)
        
    except Exception as e:
        logger.error(f"DQ suggestions error: {str(e)}")
        await mongodb.update_data_session(request.session_id, {
            "dq_suggestions_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"DQ suggestions failed: {str(e)}")


@router.post("/generate_dq_tests", response_model=DQTestsResponse)
async def dq_tests_endpoint(request: DQTestsRequest):
    """
    Step 6: Generate DQ tests
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_data_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await mongodb.update_data_session(request.session_id, {
            "dq_tests_input": request.input,
            "dq_tests_status": StepStatus.IN_PROGRESS
        })
        
        # Generate DQ tests
        tests = await generate_dq_tests(request.input)
        
        await mongodb.update_data_session(request.session_id, {
            "dq_tests_output": tests,
            "dq_tests_status": StepStatus.COMPLETED
        })
        
        return DQTestsResponse(output=tests)
        
    except Exception as e:
        logger.error(f"DQ tests error: {str(e)}")
        await mongodb.update_data_session(request.session_id, {
            "dq_tests_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"DQ test generation failed: {str(e)}")


@router.post("/generate_pyspark_dq_code", response_model=GeneratePySparkResponse)
async def generate_pyspark_dq_endpoint(request: GeneratePySparkRequest):
    """
    Step 7: Generate PySpark DQ code
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_data_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await mongodb.update_data_session(request.session_id, {
            "generate_pyspark_dq_input": request.input,
            "generate_pyspark_dq_status": StepStatus.IN_PROGRESS
        })
        
        # Generate PySpark DQ code
        pyspark_code = await generate_pyspark_dq_code(request.input)
        
        await mongodb.update_data_session(request.session_id, {
            "generate_pyspark_dq_output": pyspark_code,
            "generate_pyspark_dq_status": StepStatus.COMPLETED
        })
        
        return GeneratePySparkResponse(output=pyspark_code)
        
    except Exception as e:
        logger.error(f"Generate PySpark DQ error: {str(e)}")
        await mongodb.update_data_session(request.session_id, {
            "generate_pyspark_dq_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"PySpark DQ generation failed: {str(e)}")


@router.post("/execute_pyspark_dq_code", response_model=ExecutePySparkResponse)
async def execute_pyspark_dq_endpoint(request: ExecutePySparkRequest):
    """
    Step 8: Execute PySpark DQ code
    """
    try:
        mongodb = await get_mongodb()
        session = await mongodb.get_data_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await mongodb.update_data_session(request.session_id, {
            "execute_pyspark_dq_input": request.input,
            "execute_pyspark_dq_status": StepStatus.IN_PROGRESS
        })
        
        # Execute PySpark DQ code
        result = await execute_pyspark_code(request.input)
        
        await mongodb.update_data_session(request.session_id, {
            "execute_pyspark_dq_output": result,
            "execute_pyspark_dq_status": StepStatus.COMPLETED
        })
        
        return ExecutePySparkResponse(output=result)
        
    except Exception as e:
        logger.error(f"Execute PySpark DQ error: {str(e)}")
        await mongodb.update_data_session(request.session_id, {
            "execute_pyspark_dq_status": StepStatus.ERROR
        })
        raise HTTPException(status_code=500, detail=f"PySpark DQ execution failed: {str(e)}")


@router.get("/session/{session_id}")
async def get_data_session(session_id: str):
    """Get data profiling session details"""
    mongodb = await get_mongodb()
    session = await mongodb.get_data_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.dict(exclude_unset=True)