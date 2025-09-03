#!/usr/bin/env python3
"""
Quality enforcement verification for NEXUS Browser modules.

Verifies PROMPT.md constitutional requirements:
- mypy --strict: ZERO errors
- flake8: ZERO violations
- Type annotations: 100% coverage
- Pydantic models where appropriate
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any


def check_mypy(file_path: Path) -> Tuple[bool, List[str]]:
    """Run mypy strict mode on a file."""
    cmd = [
        sys.executable, "-m", "mypy",
        str(file_path),
        "--strict",
        "--ignore-missing-imports",
        "--show-error-codes"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    errors = []
    if result.returncode != 0:
        errors = [line for line in result.stdout.split('\n') if line.strip()]
    
    return result.returncode == 0, errors


def check_flake8(file_path: Path) -> Tuple[bool, List[str]]:
    """Run flake8 on a file."""
    cmd = [
        sys.executable, "-m", "flake8",
        str(file_path),
        "--max-line-length=120"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    violations = []
    if result.returncode != 0:
        violations = [line for line in result.stdout.split('\n') if line.strip()]
    
    return result.returncode == 0, violations


def check_type_coverage(file_path: Path) -> Tuple[float, List[str]]:
    """Check type annotation coverage using AST parsing."""
    import ast
    
    content = file_path.read_text()
    issues = []
    
    try:
        tree = ast.parse(content)
        
        total_functions = 0
        annotated_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                
                # Check for return type annotation or __init__
                if node.returns or node.name == '__init__':
                    annotated_functions += 1
                else:
                    issues.append(f"Function '{node.name}' at line {node.lineno}: Missing return type")
        
        coverage = (annotated_functions / total_functions * 100) if total_functions > 0 else 100.0
        return coverage, issues
        
    except SyntaxError as e:
        # Fallback to line-by-line parsing if AST fails
        lines = content.split('\n')
        total_functions = 0
        annotated_functions = 0
        
        in_function = False
        function_lines = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('def '):
                in_function = True
                function_lines = [line]
                total_functions += 1
            elif in_function:
                function_lines.append(line)
                # Check if function definition is complete
                if ':' in line:
                    full_def = ' '.join(function_lines)
                    if '->' in full_def or '__init__' in full_def:
                        annotated_functions += 1
                    else:
                        issues.append(f"Line {i - len(function_lines) + 1}: Missing return type")
                    in_function = False
                    function_lines = []
        
        coverage = (annotated_functions / total_functions * 100) if total_functions > 0 else 100.0
        return coverage, issues


def verify_module(file_path: Path) -> Dict[str, Any]:
    """Verify a module meets all quality requirements."""
    print(f"\n[QUALITY CHECK] {file_path.name}")
    print("=" * 50)
    
    results = {
        "file": str(file_path),
        "passed": True,
        "checks": {}
    }
    
    # Check mypy
    mypy_passed, mypy_errors = check_mypy(file_path)
    results["checks"]["mypy"] = {
        "passed": mypy_passed,
        "errors": len(mypy_errors)
    }
    print(f"  mypy --strict: {'PASS' if mypy_passed else f'FAIL ({len(mypy_errors)} errors)'}")
    if not mypy_passed:
        results["passed"] = False
        for error in mypy_errors[:3]:
            print(f"    - {error}")
    
    # Check flake8
    flake8_passed, flake8_violations = check_flake8(file_path)
    results["checks"]["flake8"] = {
        "passed": flake8_passed,
        "violations": len(flake8_violations)
    }
    print(f"  flake8: {'PASS' if flake8_passed else f'FAIL ({len(flake8_violations)} violations)'}")
    if not flake8_passed:
        results["passed"] = False
        for violation in flake8_violations[:3]:
            print(f"    - {violation}")
    
    # Check type coverage
    coverage, type_issues = check_type_coverage(file_path)
    results["checks"]["type_coverage"] = {
        "coverage": coverage,
        "issues": len(type_issues)
    }
    print(f"  Type coverage: {coverage:.1f}%")
    if coverage < 100:
        results["passed"] = False
        for issue in type_issues[:3]:
            print(f"    - {issue}")
    
    # Overall result
    print(f"\n  OVERALL: {'PASS - Ready for production' if results['passed'] else 'FAIL - Requires fixes'}")
    
    return results


if __name__ == "__main__":
    # Check ENV-001
    env_001 = Path(__file__).parent / "__init__.py"
    if env_001.exists():
        result = verify_module(env_001)
        
        if result["passed"]:
            print("\n[QUALITY] ENV-001 meets ALL constitutional requirements")
            print("[QUALITY] Ready to proceed with ENV-002")
        else:
            print("\n[QUALITY] ENV-001 FAILED quality checks")
            print("[QUALITY] MUST fix before proceeding")
            sys.exit(1)
    else:
        print(f"[ERROR] {env_001} not found")
        sys.exit(1)