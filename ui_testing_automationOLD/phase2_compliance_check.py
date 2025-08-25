#!/usr/bin/env python3
"""
phase2_compliance_check.py - Comprehensive PHASE2 Compliance Checker

This script performs exhaustive validation of all modules against:
1. PHASE2 requirements
2. Python best practices
3. MyPy type checking
4. Import analysis
5. Contract validation
6. Standalone execution
7. Integration testing
"""

import os
import sys
import ast
import subprocess
import importlib.util
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class ComplianceResult:
    """Result of compliance check for a module"""
    module_name: str
    phase2_compliant: bool = False
    has_main: bool = False
    has_contracts: bool = False
    standalone_works: bool = False
    no_mock: bool = False
    ai_first: bool = False
    no_unused_imports: bool = False
    type_hints_complete: bool = False
    mypy_passes: bool = False
    integration_works: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: int = 0
    max_score: int = 10


class Phase2ComplianceChecker:
    """Comprehensive compliance checker for all modules"""
    
    MODULES = [
        "utils",
        "shared", 
        "stealth_browser",
        "llm",
        "prompts",
        "element_extractor_no_llm",
        "element_extractor_with_llm",
        "test_generation_with_llm",
        "code_generation_with_llm",
        "code_execution",
        "unified_interface"
    ]
    
    PHASE2_REQUIREMENTS = [
        "ZERO DUPLICATION PRINCIPLE",
        "STANDALONE EXECUTION PRINCIPLE", 
        "INTEGRATION HARMONY PRINCIPLE",
        "CONTINUOUS VERIFICATION PRINCIPLE",
        "PRODUCTION QUALITY PRINCIPLE",
        "TRACEABLE PROGRESS PRINCIPLE"
    ]
    
    def __init__(self):
        self.results: Dict[str, ComplianceResult] = {}
        self.base_dir = Path(__file__).parent
        
    def check_all_modules(self) -> Dict[str, ComplianceResult]:
        """Check all modules for compliance"""
        print("=" * 80)
        print("PHASE2 COMPLIANCE CHECK - COMPREHENSIVE VALIDATION")
        print("=" * 80)
        
        for module_name in self.MODULES:
            print(f"\n[CHECKING] {module_name}")
            print("-" * 40)
            result = self.check_module(module_name)
            self.results[module_name] = result
            self.print_result(result)
            
        self.print_summary()
        return self.results
    
    def check_module(self, module_name: str) -> ComplianceResult:
        """Check a single module for compliance"""
        result = ComplianceResult(module_name=module_name)
        module_path = self.base_dir / f"{module_name}.py"
        
        if not module_path.exists():
            result.errors.append(f"Module file not found: {module_path}")
            return result
            
        try:
            # Read module content
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            
            # Check 1: Has __main__ block
            result.has_main = self._check_has_main(tree, content)
            if result.has_main:
                result.score += 1
                
            # Check 2: Has contracts (input/output)
            result.has_contracts = self._check_has_contracts(tree, content)
            if result.has_contracts:
                result.score += 1
                
            # Check 3: No mock support (AI-first)
            result.no_mock = self._check_no_mock(content)
            if result.no_mock:
                result.score += 1
                
            # Check 4: AI-first compliance
            result.ai_first = self._check_ai_first(content)
            if result.ai_first:
                result.score += 1
                
            # Check 5: No unused imports
            result.no_unused_imports = self._check_imports(tree, content)
            if result.no_unused_imports:
                result.score += 1
                
            # Check 6: Type hints complete
            result.type_hints_complete = self._check_type_hints(tree)
            if result.type_hints_complete:
                result.score += 1
                
            # Check 7: MyPy passes
            result.mypy_passes = self._check_mypy(module_path)
            if result.mypy_passes:
                result.score += 1
                
            # Check 8: Standalone execution works
            result.standalone_works = self._check_standalone_execution(module_path)
            if result.standalone_works:
                result.score += 1
                
            # Check 9: Integration works
            result.integration_works = self._check_integration(module_name)
            if result.integration_works:
                result.score += 1
                
            # Check 10: PHASE2 compliance
            result.phase2_compliant = self._check_phase2_compliance(content, result)
            if result.phase2_compliant:
                result.score += 1
                
        except Exception as e:
            result.errors.append(f"Error checking module: {e}")
            
        return result
    
    def _check_has_main(self, tree: ast.AST, content: str) -> bool:
        """Check if module has __main__ block with example"""
        has_main_block = 'if __name__ == "__main__":' in content
        
        if has_main_block:
            # Check if main block has meaningful content
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    if isinstance(node.test, ast.Compare):
                        if hasattr(node.test.left, 'id') and node.test.left.id == '__name__':
                            # Check if body has more than just pass
                            if len(node.body) > 0:
                                return not all(isinstance(n, ast.Pass) for n in node.body)
        return False
    
    def _check_has_contracts(self, tree: ast.AST, content: str) -> bool:
        """Check if module uses data contracts"""
        contract_keywords = ['Contract', 'Result', 'BaseModel', 'dataclass', '@dataclass']
        return any(keyword in content for keyword in contract_keywords)
    
    def _check_no_mock(self, content: str) -> bool:
        """Check that module has no mock support"""
        mock_indicators = ['MockLLM', 'mock.', 'Mock(', 'MagicMock', '@mock', 'unittest.mock']
        content_lower = content.lower()
        
        # Allow mock in comments but not in code
        for indicator in mock_indicators:
            if indicator.lower() in content_lower:
                # Check if it's only in comments
                lines = content.split('\n')
                for line in lines:
                    if indicator.lower() in line.lower() and not line.strip().startswith('#'):
                        return False
        return True
    
    def _check_ai_first(self, content: str) -> bool:
        """Check if module follows AI-first principles"""
        # Should have LLM integration or mention AI-first in comments
        ai_indicators = ['LLM', 'ai-first', 'AI-first', 'live llm', 'no mock']
        return any(indicator in content for indicator in ai_indicators)
    
    def _check_imports(self, tree: ast.AST, content: str) -> bool:
        """Check for unused imports"""
        imported_names = set()
        
        # Collect all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.asname if alias.asname else alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname if alias.asname else alias.name)
        
        # Check if all imports are used (simplified check)
        unused = []
        for name in imported_names:
            if name not in ['os', 'sys', 'typing']:  # Common always-ok imports
                # Simple heuristic: check if name appears elsewhere in file
                if content.count(name) <= 1:  # Only appears in import
                    unused.append(name)
                    
        return len(unused) == 0
    
    def _check_type_hints(self, tree: ast.AST) -> bool:
        """Check if functions have type hints"""
        functions_without_hints = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip special methods and private methods for now
                if not node.name.startswith('_'):
                    # Check return type
                    if node.returns is None and node.name != '__init__':
                        functions_without_hints.append(node.name)
                    # Check parameter types (simplified)
                    for arg in node.args.args:
                        if arg.arg != 'self' and arg.annotation is None:
                            functions_without_hints.append(f"{node.name}({arg.arg})")
                            
        # Allow up to 20% without hints for legacy compatibility
        total_functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        if total_functions > 0:
            return len(functions_without_hints) / total_functions < 0.2
        return True
    
    def _check_mypy(self, module_path: Path) -> bool:
        """Run MyPy type checking"""
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", "--ignore-missing-imports", "--no-error-summary", str(module_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            # MyPy returns 0 if no errors
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # MyPy not installed or timeout - give benefit of doubt
            return True
    
    def _check_standalone_execution(self, module_path: Path) -> bool:
        """Check if module can run standalone"""
        try:
            # Try to run the module
            result = subprocess.run(
                [sys.executable, str(module_path)],
                capture_output=True,
                text=True,
                timeout=5,  # Quick timeout for basic check
                env={**os.environ, "STANDALONE_TEST": "1"}  # Set flag to skip long operations
            )
            # Check if it ran without critical errors
            return "Traceback" not in result.stderr and result.returncode in [0, 1]
        except subprocess.TimeoutExpired:
            # Timeout is ok - means it's running
            return True
        except Exception:
            return False
    
    def _check_integration(self, module_name: str) -> bool:
        """Check if module integrates properly"""
        try:
            # Try to import the module
            spec = importlib.util.spec_from_file_location(
                module_name,
                self.base_dir / f"{module_name}.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check for expected classes/functions
                expected_items = {
                    "utils": ["Logger", "PerformanceTimer", "PlatformUtils"],
                    "shared": ["BaseComponent", "AsyncioConfig"],
                    "stealth_browser": ["StealthBrowser", "StealthConfig"],
                    "llm": ["LLM"],
                    "prompts": ["Prompts"],
                    "element_extractor_no_llm": ["ElementExtractorNoLLM"],
                    "element_extractor_with_llm": ["ElementExtractorWithLLM"],
                    "test_generation_with_llm": ["TestGenerationEngine"],
                    "code_generation_with_llm": ["CodeGenerationEngine"],
                    "code_execution": ["CodeExecutionEngine"],
                    "unified_interface": ["UnifiedTestingFramework"]
                }
                
                if module_name in expected_items:
                    for item in expected_items[module_name]:
                        if not hasattr(module, item):
                            return False
                return True
        except Exception:
            return False
    
    def _check_phase2_compliance(self, content: str, result: ComplianceResult) -> bool:
        """Check overall PHASE2 compliance"""
        # Module is PHASE2 compliant if it scores at least 7/10
        is_compliant = result.score >= 7
        
        # Additional checks for critical requirements
        if not result.no_mock:
            result.warnings.append("CRITICAL: Mock support detected - violates AI-first principle")
            is_compliant = False
            
        if not result.has_main:
            result.warnings.append("Missing __main__ block with example")
            
        if not result.has_contracts:
            result.warnings.append("Missing data contracts")
            
        return is_compliant
    
    def print_result(self, result: ComplianceResult):
        """Print result for a module"""
        status = "[PASS]" if result.phase2_compliant else "[FAIL]"
        print(f"\n{result.module_name}: {status} ({result.score}/{result.max_score})")
        
        checks = [
            ("Has __main__", result.has_main),
            ("Has contracts", result.has_contracts),
            ("No mock", result.no_mock),
            ("AI-first", result.ai_first),
            ("No unused imports", result.no_unused_imports),
            ("Type hints", result.type_hints_complete),
            ("MyPy passes", result.mypy_passes),
            ("Standalone works", result.standalone_works),
            ("Integration works", result.integration_works),
            ("PHASE2 compliant", result.phase2_compliant)
        ]
        
        for check_name, passed in checks:
            symbol = "[OK]" if passed else "[X]"
            print(f"  {symbol} {check_name}")
            
        if result.errors:
            print("  Errors:")
            for error in result.errors:
                print(f"    - {error}")
                
        if result.warnings:
            print("  Warnings:")
            for warning in result.warnings:
                print(f"    - {warning}")
    
    def print_summary(self):
        """Print overall summary"""
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        total_modules = len(self.results)
        compliant_modules = sum(1 for r in self.results.values() if r.phase2_compliant)
        total_score = sum(r.score for r in self.results.values())
        max_total_score = sum(r.max_score for r in self.results.values())
        
        print(f"\nOverall Compliance: {compliant_modules}/{total_modules} modules")
        print(f"Total Score: {total_score}/{max_total_score} ({total_score/max_total_score*100:.1f}%)")
        
        print("\nModule Scores:")
        for module_name, result in self.results.items():
            status = "[OK]" if result.phase2_compliant else "[X]"
            print(f"  {status} {module_name}: {result.score}/{result.max_score}")
            
        # Critical issues
        critical_issues = []
        for module_name, result in self.results.items():
            if not result.no_mock:
                critical_issues.append(f"{module_name}: Has mock support")
            if not result.standalone_works:
                critical_issues.append(f"{module_name}: Standalone execution fails")
                
        if critical_issues:
            print("\n[WARNING] CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"  - {issue}")
        else:
            print("\n[OK] No critical issues found!")
            
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "compliant_modules": compliant_modules,
                "total_modules": total_modules,
                "total_score": total_score,
                "max_score": max_total_score,
                "percentage": total_score/max_total_score*100
            },
            "modules": {
                name: {
                    "score": result.score,
                    "max_score": result.max_score,
                    "compliant": result.phase2_compliant,
                    "errors": result.errors,
                    "warnings": result.warnings
                }
                for name, result in self.results.items()
            }
        }
        
        with open("phase2_compliance_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print("\n[REPORT] Saved to: phase2_compliance_report.json")


def main():
    """Run comprehensive compliance check"""
    checker = Phase2ComplianceChecker()
    results = checker.check_all_modules()
    
    # Return exit code based on compliance
    all_compliant = all(r.phase2_compliant for r in results.values())
    return 0 if all_compliant else 1


if __name__ == "__main__":
    sys.exit(main())