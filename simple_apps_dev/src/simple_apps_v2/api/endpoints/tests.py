"""
Test generation endpoints.
"""

from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from simple_apps_v2.core.logging import get_logger
from simple_apps_v2.services.test_generator import TestGenerator

router = APIRouter()
logger = get_logger(__name__)


class GenerateTestsRequest(BaseModel):
    """Request model for test generation."""
    extraction_data: Dict[str, Any] = Field(..., description="Extracted elements data")
    test_categories: Optional[List[str]] = Field(
        default=None, 
        description="Specific test categories to generate"
    )
    test_framework: str = Field(default="pytest", description="Test framework")
    include_edge_cases: bool = Field(default=True, description="Include edge cases")
    max_tests_per_category: int = Field(default=10, description="Max tests per category")


class GenerateTestsResponse(BaseModel):
    """Response model for test generation."""
    success: bool
    url: str
    features: Dict[str, Any]
    test_suite: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/generate", response_model=GenerateTestsResponse)
async def generate_tests(request: GenerateTestsRequest) -> GenerateTestsResponse:
    """Generate test scenarios from extracted elements."""
    try:
        logger.info("Generating test scenarios")
        
        generator = TestGenerator(framework=request.test_framework)
        
        test_suite = await generator.generate_tests(
            extraction_data=request.extraction_data,
            categories=request.test_categories,
            include_edge_cases=request.include_edge_cases,
            max_per_category=request.max_tests_per_category
        )
        
        # Calculate statistics
        stats = {
            "total_scenarios": len(test_suite.get("scenarios", [])),
            "total_features": len(test_suite.get("features", [])),
            "categories": list(set(
                s.get("category", "unknown") 
                for s in test_suite.get("scenarios", [])
            )),
        }
        
        return GenerateTestsResponse(
            success=True,
            url=request.extraction_data.get("url", ""),
            features=test_suite.get("features", {}),
            test_suite=test_suite,
            statistics=stats,
        )
        
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/validate")
async def validate_tests(test_suite: Dict[str, Any]) -> Dict[str, Any]:
    """Validate generated test suite."""
    try:
        logger.info("Validating test suite")
        
        issues = []
        warnings = []
        
        # Check for required fields
        if not test_suite.get("scenarios"):
            issues.append("No test scenarios found")
        
        # Validate each scenario
        for idx, scenario in enumerate(test_suite.get("scenarios", [])):
            if not scenario.get("name"):
                issues.append(f"Scenario {idx} missing name")
            if not scenario.get("steps"):
                issues.append(f"Scenario {idx} missing steps")
            elif len(scenario["steps"]) == 0:
                warnings.append(f"Scenario {idx} has no steps")
        
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "statistics": {
                "total_scenarios": len(test_suite.get("scenarios", [])),
                "total_steps": sum(
                    len(s.get("steps", [])) 
                    for s in test_suite.get("scenarios", [])
                ),
            }
        }
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {
            "valid": False,
            "error": str(e),
        }