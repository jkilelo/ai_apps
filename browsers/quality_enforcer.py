#!/usr/bin/env python3
"""
QUALITY ENFORCEMENT MODULE
==========================
Ensures all NEXUS Browser modules meet production quality standards.

Quality Gates:
- mypy strict mode: ZERO errors
- flake8: ZERO violations  
- Pydantic v2 models: REQUIRED for data structures
- Full type annotations: 100% coverage
- Input/output typing: GUARANTEED
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class QualityCheckType(Enum):
    """Types of quality checks"""
    MYPY = "mypy"
    FLAKE8 = "flake8"
    BLACK = "black"
    PYDANTIC = "pydantic"
    TYPE_COVERAGE = "type_coverage"


class QualityViolation(BaseModel):
    """Model for quality violations"""
    check_type: QualityCheckType
    file_path: str
    line_number: Optional[int] = None
    message: str
    severity: str = Field(default="error", pattern="^(error|warning|info)$")
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        if not v.endswith('.py'):
            raise ValueError('File path must be a Python file')
        return v


class QualityReport(BaseModel):
    """Comprehensive quality report"""
    file_path: str
    passed: bool
    violations: List[QualityViolation] = Field(default_factory=list)
    mypy_errors: int = 0
    flake8_violations: int = 0
    type_coverage_percent: float = 100.0
    has_pydantic_models: bool = False
    
    @field_validator('type_coverage_percent')
    @classmethod
    def validate_coverage(cls, v: float) -> float:
        if not 0 <= v <= 100:
            raise ValueError('Coverage must be between 0 and 100')
        return v


@dataclass
class QualityRequirements:
    """Immutable quality requirements"""
    mypy_strict: bool = True
    mypy_max_errors: int = 0
    flake8_max_violations: int = 0
    flake8_max_line_length: int = 120
    require_pydantic_models: bool = True
    min_type_coverage: float = 100.0
    require_return_types: bool = True
    require_parameter_types: bool = True
    black_formatting: bool = True


class QualityEnforcer:
    """
    Enforces production quality standards for all code.
    
    CONSTITUTIONAL PRINCIPLE:
    No code shall pass without meeting ALL quality gates.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.requirements = QualityRequirements()
        self.reports: List[QualityReport] = []
        
    def check_mypy(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Run mypy strict mode type checking"""
        cmd = [
            sys.executable, "-m", "mypy",
            str(file_path),
            "--strict",
            "--ignore-missing-imports",
            "--show-error-codes",
            "--no-error-summary"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path)
            )
            
            errors = []
            if result.returncode != 0:
                errors = result.stdout.strip().split('\n') if result.stdout else []
                errors.extend(result.stderr.strip().split('\n') if result.stderr else [])
                errors = [e for e in errors if e and 'error:' in e]
            
            return result.returncode == 0, errors
            
        except Exception as e:
            return False, [f"Failed to run mypy: {str(e)}"]
    
    def check_flake8(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Run flake8 linting"""
        cmd = [
            sys.executable, "-m", "flake8",
            str(file_path),
            f"--max-line-length={self.requirements.flake8_max_line_length}",
            "--show-source",
            "--statistics"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path)
            )
            
            violations = []
            if result.returncode != 0:
                violations = result.stdout.strip().split('\n') if result.stdout else []
                violations = [v for v in violations if v and '.py:' in v]
            
            return result.returncode == 0, violations
            
        except Exception as e:
            return False, [f"Failed to run flake8: {str(e)}"]
    
    def check_black(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check black formatting"""
        cmd = [
            sys.executable, "-m", "black",
            str(file_path),
            "--check",
            "--diff",
            f"--line-length={self.requirements.flake8_max_line_length}"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path)
            )
            
            if result.returncode != 0:
                return False, ["File needs black formatting"]
            return True, []
            
        except Exception as e:
            return False, [f"Failed to run black: {str(e)}"]
    
    def check_pydantic_usage(self, file_path: Path) -> bool:
        """Check if file uses Pydantic models for data structures"""
        try:
            content = file_path.read_text()
            
            # Check for Pydantic imports
            has_pydantic = 'from pydantic import' in content or 'import pydantic' in content
            
            # Check for BaseModel usage
            has_basemodel = 'BaseModel' in content
            
            # Check if file has data structures that should use Pydantic
            needs_pydantic = any([
                'class ' in content and '@dataclass' in content,
                'Dict[str, Any]' in content,
                'def __init__' in content and 'self.' in content
            ])
            
            if needs_pydantic and not (has_pydantic and has_basemodel):
                return False
                
            return True
            
        except Exception:
            return False
    
    def check_type_annotations(self, file_path: Path) -> Tuple[float, List[str]]:
        """Check type annotation coverage"""
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            
            issues = []
            total_functions = 0
            annotated_functions = 0
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check function definitions
                if line.startswith('def '):
                    total_functions += 1
                    
                    # Check for return type annotation
                    if '->' not in line and 'def __init__' not in line:
                        issues.append(f"Line {i}: Missing return type annotation")
                    else:
                        annotated_functions += 1
                    
                    # Check for parameter type annotations
                    if '(' in line and ')' in line:
                        params = line[line.index('(')+1:line.index(')')].strip()
                        if params and params != 'self' and ':' not in params:
                            issues.append(f"Line {i}: Missing parameter type annotations")
            
            coverage = (annotated_functions / total_functions * 100) if total_functions > 0 else 100.0
            return coverage, issues
            
        except Exception as e:
            return 0.0, [f"Failed to check type annotations: {str(e)}"]
    
    def enforce_quality(self, file_path: Path) -> QualityReport:
        """
        Enforce all quality standards on a file.
        
        CONSTITUTIONAL ENFORCEMENT:
        ANY violation = IMMEDIATE FAILURE
        """
        report = QualityReport(file_path=str(file_path), passed=True)
        
        # Check mypy
        mypy_passed, mypy_errors = self.check_mypy(file_path)
        if not mypy_passed:
            report.passed = False
            report.mypy_errors = len(mypy_errors)
            for error in mypy_errors:
                report.violations.append(QualityViolation(
                    check_type=QualityCheckType.MYPY,
                    file_path=str(file_path),
                    message=error,
                    severity="error"
                ))
        
        # Check flake8
        flake8_passed, flake8_violations = self.check_flake8(file_path)
        if not flake8_passed:
            report.passed = False
            report.flake8_violations = len(flake8_violations)
            for violation in flake8_violations:
                report.violations.append(QualityViolation(
                    check_type=QualityCheckType.FLAKE8,
                    file_path=str(file_path),
                    message=violation,
                    severity="error"
                ))
        
        # Check black formatting
        black_passed, black_issues = self.check_black(file_path)
        if not black_passed:
            report.passed = False
            for issue in black_issues:
                report.violations.append(QualityViolation(
                    check_type=QualityCheckType.BLACK,
                    file_path=str(file_path),
                    message=issue,
                    severity="warning"
                ))
        
        # Check Pydantic usage
        if self.requirements.require_pydantic_models:
            has_pydantic = self.check_pydantic_usage(file_path)
            report.has_pydantic_models = has_pydantic
            if not has_pydantic and 'test' not in str(file_path):
                report.passed = False
                report.violations.append(QualityViolation(
                    check_type=QualityCheckType.PYDANTIC,
                    file_path=str(file_path),
                    message="Data structures should use Pydantic models",
                    severity="error"
                ))
        
        # Check type annotation coverage
        coverage, type_issues = self.check_type_annotations(file_path)
        report.type_coverage_percent = coverage
        if coverage < self.requirements.min_type_coverage:
            report.passed = False
            for issue in type_issues:
                report.violations.append(QualityViolation(
                    check_type=QualityCheckType.TYPE_COVERAGE,
                    file_path=str(file_path),
                    message=issue,
                    severity="error"
                ))
        
        self.reports.append(report)
        return report
    
    def generate_quality_summary(self) -> Dict[str, Any]:
        """Generate comprehensive quality summary"""
        total_files = len(self.reports)
        passed_files = len([r for r in self.reports if r.passed])
        total_violations = sum(len(r.violations) for r in self.reports)
        
        return {
            "total_files_checked": total_files,
            "files_passed": passed_files,
            "files_failed": total_files - passed_files,
            "pass_rate": (passed_files / total_files * 100) if total_files > 0 else 0,
            "total_violations": total_violations,
            "mypy_errors": sum(r.mypy_errors for r in self.reports),
            "flake8_violations": sum(r.flake8_violations for r in self.reports),
            "average_type_coverage": sum(r.type_coverage_percent for r in self.reports) / total_files if total_files > 0 else 0,
            "requirements": {
                "mypy_strict": self.requirements.mypy_strict,
                "max_errors_allowed": self.requirements.mypy_max_errors,
                "max_violations_allowed": self.requirements.flake8_max_violations,
                "min_type_coverage": self.requirements.min_type_coverage
            }
        }


def enforce_module_quality(module_path: str, project_path: str) -> bool:
    """
    Enforce quality standards on a module.
    Returns True only if ALL quality gates pass.
    """
    enforcer = QualityEnforcer(project_path)
    report = enforcer.enforce_quality(Path(module_path))
    
    if not report.passed:
        print(f"\n[QUALITY] ENFORCEMENT FAILED for {module_path}")
        print(f"[QUALITY] Violations: {len(report.violations)}")
        for violation in report.violations[:5]:  # Show first 5
            print(f"  - {violation.check_type.value}: {violation.message[:100]}")
        
        return False
    
    print(f"[QUALITY] All quality gates PASSED for {module_path}")
    return True


if __name__ == "__main__":
    print("[QUALITY] Quality Enforcement System Initialized")
    print("[QUALITY] Requirements:")
    print("  - mypy strict mode: ZERO errors")
    print("  - flake8: ZERO violations")
    print("  - Black formatting: REQUIRED")
    print("  - Pydantic models: REQUIRED for data")
    print("  - Type annotations: 100% coverage")
    print("[QUALITY] Zero tolerance for violations")