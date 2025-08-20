"""
Code generation endpoints.
"""

from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from simple_apps_v2.core.logging import get_logger
from simple_apps_v2.services.code_generator import CodeGenerator

router = APIRouter()
logger = get_logger(__name__)


class GenerateCodeRequest(BaseModel):
    """Request model for code generation."""
    extraction_data: Dict[str, Any] = Field(..., description="Extracted elements data")
    test_data: Dict[str, Any] = Field(..., description="Generated test scenarios")
    code_type: str = Field(default="pytest", description="Type of code to generate")
    language: str = Field(default="python", description="Programming language")
    include_fixtures: bool = Field(default=True, description="Include test fixtures")
    include_page_objects: bool = Field(default=True, description="Include page objects")


class GenerateCodeResponse(BaseModel):
    """Response model for code generation."""
    success: bool
    url: str
    generated_files: Dict[str, str]  # filename -> code content
    file_structure: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/generate", response_model=GenerateCodeResponse)
async def generate_code(request: GenerateCodeRequest) -> GenerateCodeResponse:
    """Generate test code from test scenarios."""
    try:
        logger.info(f"Generating {request.code_type} code")
        
        generator = CodeGenerator(
            code_type=request.code_type,
            language=request.language
        )
        
        generated_files = await generator.generate_code(
            extraction_data=request.extraction_data,
            test_data=request.test_data,
            include_fixtures=request.include_fixtures,
            include_page_objects=request.include_page_objects
        )
        
        # Create file structure
        file_structure = {
            "test_files": [],
            "support_files": [],
            "config_files": [],
        }
        
        for filename in generated_files.keys():
            if "test_" in filename:
                file_structure["test_files"].append(filename)
            elif filename.endswith((".yml", ".yaml", ".json", ".ini")):
                file_structure["config_files"].append(filename)
            else:
                file_structure["support_files"].append(filename)
        
        # Calculate statistics
        stats = {
            "total_files": len(generated_files),
            "total_lines": sum(
                len(code.splitlines()) 
                for code in generated_files.values()
            ),
            "test_files": len(file_structure["test_files"]),
            "support_files": len(file_structure["support_files"]),
        }
        
        return GenerateCodeResponse(
            success=True,
            url=request.extraction_data.get("url", ""),
            generated_files=generated_files,
            file_structure=file_structure,
            statistics=stats,
        )
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/format")
async def format_code(code: str, language: str = "python") -> Dict[str, Any]:
    """Format generated code."""
    try:
        logger.info(f"Formatting {language} code")
        
        if language == "python":
            # Use black for Python formatting
            try:
                import black
                formatted = black.format_str(code, mode=black.FileMode())
            except ImportError:
                # Fallback to basic formatting
                formatted = code
        else:
            formatted = code
        
        return {
            "success": True,
            "formatted_code": formatted,
            "changes_made": formatted != code,
        }
        
    except Exception as e:
        logger.error(f"Code formatting failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "original_code": code,
        }