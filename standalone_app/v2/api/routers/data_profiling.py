"""Data Profiling Router with 8-step process"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
import logging

from services.data_profiling_service import DataProfilingService
from services.validation import validate_data_sample
from services.cache import CacheService

router = APIRouter()
profiling_service = DataProfilingService()
cache_service = CacheService()
logger = logging.getLogger(__name__)

# Request/Response Models for 8-step process

# Step 1: Generate Profiling Suggestions
class ProfilingSuggestionsRequest(BaseModel):
    data_sample: str = Field(..., description="Sample of data to profile")
    data_description: str = Field(..., description="Description of the data")
    
    @validator('data_sample')
    def validate_sample(cls, v):
        validation = validate_data_sample(v)
        if not validation["valid"]:
            raise ValueError(validation["reason"])
        return v

class ProfilingSuggestionsResponse(BaseModel):
    profiling_suggestions: str
    data_format: str
    row_count: int

# Step 2: Generate Profiling Test Cases
class ProfilingTestcasesRequest(BaseModel):
    profiling_suggestions: str

class ProfilingTestcasesResponse(BaseModel):
    testcases: str
    test_count: int

# Step 3: Generate PySpark Code
class GeneratePySparkRequest(BaseModel):
    testcases: str

class GeneratePySparkResponse(BaseModel):
    pyspark_code: str
    estimated_runtime: str

# Step 4: Execute PySpark Code
class ExecutePySparkRequest(BaseModel):
    pyspark_code: str
    timeout: int = Field(60, ge=10, le=300)

class ExecutePySparkResponse(BaseModel):
    success: bool
    results: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float

# Step 5: Generate DQ Suggestions
class DQSuggestionsRequest(BaseModel):
    profiling_results: str

class DQSuggestionsResponse(BaseModel):
    dq_suggestions: str
    issue_count: int

# Step 6: Generate DQ Tests
class DQTestsRequest(BaseModel):
    dq_suggestions: str

class DQTestsResponse(BaseModel):
    dq_tests: str
    test_count: int

# Step 7: Generate DQ PySpark Code
class DQPySparkRequest(BaseModel):
    dq_tests: str

class DQPySparkResponse(BaseModel):
    pyspark_code: str
    estimated_runtime: str

# Step 8: Execute DQ PySpark Code
class ExecuteDQRequest(BaseModel):
    pyspark_code: str
    timeout: int = Field(60, ge=10, le=300)

class ExecuteDQResponse(BaseModel):
    success: bool
    results: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    quality_score: Optional[float] = None

# Endpoints for 8-step process

@router.post("/data_profiling/generate_profiling_suggestions", response_model=ProfilingSuggestionsResponse)
async def generate_profiling_suggestions(request: ProfilingSuggestionsRequest, req: Request):
    """Step 1: Generate intelligent profiling suggestions based on data sample"""
    try:
        # Detect data format
        validation = validate_data_sample(request.data_sample)
        
        result = await profiling_service.generate_profiling_suggestions(
            data_sample=request.data_sample,
            data_description=request.data_description,
            data_format=validation.get("format", "unknown")
        )
        
        return ProfilingSuggestionsResponse(
            profiling_suggestions=result["suggestions"],
            data_format=validation.get("format", "unknown"),
            row_count=validation.get("rows", 0)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate profiling suggestions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate profiling suggestions"
        )

@router.post("/data_profiling/generate_profiling_testcases", response_model=ProfilingTestcasesResponse)
async def generate_profiling_testcases(request: ProfilingTestcasesRequest, req: Request):
    """Step 2: Generate comprehensive test cases from profiling suggestions"""
    try:
        result = await profiling_service.generate_profiling_testcases(
            profiling_suggestions=request.profiling_suggestions
        )
        
        return ProfilingTestcasesResponse(
            testcases=result["testcases"],
            test_count=result["test_count"]
        )
        
    except Exception as e:
        logger.error(f"Failed to generate test cases: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate test cases"
        )

@router.post("/data_profiling/generate_pyspark_code", response_model=GeneratePySparkResponse)
async def generate_pyspark_code(request: GeneratePySparkRequest, req: Request):
    """Step 3: Generate PySpark code from test cases"""
    try:
        result = await profiling_service.generate_pyspark_code(
            testcases=request.testcases
        )
        
        return GeneratePySparkResponse(
            pyspark_code=result["code"],
            estimated_runtime=result.get("estimated_runtime", "1-2 minutes")
        )
        
    except Exception as e:
        logger.error(f"Failed to generate PySpark code: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PySpark code"
        )

@router.post("/data_profiling/execute_pyspark_code", response_model=ExecutePySparkResponse)
async def execute_pyspark_code(request: ExecutePySparkRequest, req: Request):
    """Step 4: Execute PySpark profiling code"""
    try:
        import asyncio
        start_time = asyncio.get_event_loop().time()
        
        result = await profiling_service.execute_pyspark_code(
            code=request.pyspark_code,
            timeout=request.timeout
        )
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return ExecutePySparkResponse(
            success=result["success"],
            results=result.get("results"),
            output=result.get("output"),
            error=result.get("error"),
            execution_time=round(execution_time, 3)
        )
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"Execution timed out after {request.timeout} seconds"
        )
    except Exception as e:
        logger.error(f"Failed to execute PySpark code: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute PySpark code"
        )

@router.post("/data_profiling/generate_dq_suggestions", response_model=DQSuggestionsResponse)
async def generate_dq_suggestions(request: DQSuggestionsRequest, req: Request):
    """Step 5: Generate data quality improvement suggestions"""
    try:
        result = await profiling_service.generate_dq_suggestions(
            profiling_results=request.profiling_results
        )
        
        return DQSuggestionsResponse(
            dq_suggestions=result["suggestions"],
            issue_count=result["issue_count"]
        )
        
    except Exception as e:
        logger.error(f"Failed to generate DQ suggestions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate DQ suggestions"
        )

@router.post("/data_profiling/generate_dq_tests", response_model=DQTestsResponse)
async def generate_dq_tests(request: DQTestsRequest, req: Request):
    """Step 6: Generate data quality test cases"""
    try:
        result = await profiling_service.generate_dq_tests(
            dq_suggestions=request.dq_suggestions
        )
        
        return DQTestsResponse(
            dq_tests=result["tests"],
            test_count=result["test_count"]
        )
        
    except Exception as e:
        logger.error(f"Failed to generate DQ tests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate DQ tests"
        )

@router.post("/data_profiling/generate_pyspark_dq_code", response_model=DQPySparkResponse)
async def generate_pyspark_dq_code(request: DQPySparkRequest, req: Request):
    """Step 7: Generate PySpark code for data quality checks"""
    try:
        result = await profiling_service.generate_dq_pyspark_code(
            dq_tests=request.dq_tests
        )
        
        return DQPySparkResponse(
            pyspark_code=result["code"],
            estimated_runtime=result.get("estimated_runtime", "2-3 minutes")
        )
        
    except Exception as e:
        logger.error(f"Failed to generate DQ PySpark code: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate DQ PySpark code"
        )

@router.post("/data_profiling/execute_pyspark_dq_code", response_model=ExecuteDQResponse)
async def execute_pyspark_dq_code(request: ExecuteDQRequest, req: Request):
    """Step 8: Execute data quality PySpark code and get final results"""
    try:
        import asyncio
        start_time = asyncio.get_event_loop().time()
        
        result = await profiling_service.execute_dq_code(
            code=request.pyspark_code,
            timeout=request.timeout
        )
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return ExecuteDQResponse(
            success=result["success"],
            results=result.get("results"),
            output=result.get("output"),
            error=result.get("error"),
            execution_time=round(execution_time, 3),
            quality_score=result.get("quality_score")
        )
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"Execution timed out after {request.timeout} seconds"
        )
    except Exception as e:
        logger.error(f"Failed to execute DQ code: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute DQ code"
        )

@router.get("/data_profiling/sample_data/{data_type}")
async def get_sample_data(data_type: str):
    """Get sample data for testing"""
    samples = {
        "csv": """id,name,email,age,salary
1,John Doe,john@example.com,30,50000
2,Jane Smith,jane@example.com,25,45000
3,Bob Johnson,bob@example.com,35,60000
4,Alice Brown,alice@example.com,28,52000
5,Charlie Wilson,charlie@example.com,42,75000""",
        
        "json": """[
  {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30, "salary": 50000},
  {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25, "salary": 45000},
  {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 35, "salary": 60000}
]""",
        
        "sql": """CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    age INT,
    salary DECIMAL(10,2)
);

INSERT INTO employees VALUES
(1, 'John Doe', 'john@example.com', 30, 50000),
(2, 'Jane Smith', 'jane@example.com', 25, 45000);"""
    }
    
    if data_type not in samples:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample data type '{data_type}' not found"
        )
    
    return {
        "data_type": data_type,
        "sample": samples[data_type],
        "description": f"Sample {data_type.upper()} data for testing"
    }