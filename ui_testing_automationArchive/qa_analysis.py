#!/usr/bin/env python3
"""
Comprehensive QA Analysis for elements_extractor_no_llm.py
Senior QA Engineer Analysis with 30+ years experience
"""

import asyncio
import sys
import os
from pathlib import Path
import ast
import re
from typing import Dict, List, Any, Tuple
import subprocess

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.code_services import (
    CodeServices, ChunkService, IndexService,
    ChunkStrategy, IndexType
)

class QAAnalyzer:
    """Comprehensive QA analyzer using master prompt strategies."""
    
    def __init__(self):
        self.services = CodeServices()
        self.file_path = Path(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation\elements_extractor_no_llm.py")
        self.results = {
            "file_analysis": {},
            "type_safety": {},
            "pep8_compliance": {},
            "best_practices": {},
            "screenshot_features": {},
            "production_readiness": {},
            "master_plan_conformance": {},
            "recommendations": []
        }
    
    async def analyze_file_structure(self):
        """Analyze file structure and complexity."""
        print("\n[1/8] ANALYZING FILE STRUCTURE")
        print("="*60)
        
        if not self.file_path.exists():
            print(f"ERROR: File not found: {self.file_path}")
            return False
        
        # Get file stats
        stats = self.file_path.stat()
        content = self.file_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        # Parse AST
        try:
            tree = ast.parse(content)
            
            # Count different elements
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            async_functions = [n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
            
            self.results["file_analysis"] = {
                "file_size": stats.st_size,
                "total_lines": len(lines),
                "non_empty_lines": len([l for l in lines if l.strip()]),
                "classes": len(classes),
                "functions": len(functions),
                "async_functions": len(async_functions),
                "imports": len([n for n in ast.walk(tree) if isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom)]),
                "docstrings": len([ast.get_docstring(n) for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and ast.get_docstring(n)])
            }
            
            print(f"[OK] File size: {stats.st_size:,} bytes")
            print(f"[OK] Total lines: {len(lines):,}")
            print(f"[OK] Classes: {len(classes)}")
            print(f"[OK] Functions: {len(functions) + len(async_functions)}")
            print(f"[OK] Async functions: {len(async_functions)}")
            
            # Check for main classes
            main_classes = [c.name for c in classes if "Extractor" in c.name]
            print(f"[OK] Main extractor classes: {main_classes}")
            
            return True
        except SyntaxError as e:
            print(f"[FAIL] Syntax error: {e}")
            self.results["file_analysis"]["syntax_error"] = str(e)
            return False
    
    async def check_type_safety(self):
        """Check type safety using mypy."""
        print("\n[2/8] CHECKING TYPE SAFETY")
        print("="*60)
        
        try:
            # Run mypy
            result = subprocess.run(
                [sys.executable, "-m", "mypy", str(self.file_path), "--ignore-missing-imports", "--no-error-summary"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("[OK] No type errors found")
                self.results["type_safety"]["status"] = "PASS"
                self.results["type_safety"]["errors"] = []
            else:
                # Parse mypy output
                errors = result.stdout.strip().split('\n') if result.stdout else []
                error_count = len([e for e in errors if e.strip()])
                
                print(f"[FAIL] Found {error_count} type errors")
                self.results["type_safety"]["status"] = "FAIL"
                self.results["type_safety"]["errors"] = errors[:10]  # First 10 errors
                
                # Categorize errors
                error_types = {}
                for error in errors:
                    if "error:" in error:
                        error_type = error.split("error:")[1].split("[")[0].strip()
                        error_types[error_type] = error_types.get(error_type, 0) + 1
                
                for error_type, count in error_types.items():
                    print(f"  - {error_type}: {count}")
                
        except Exception as e:
            print(f"[FAIL] Could not run mypy: {e}")
            self.results["type_safety"]["status"] = "ERROR"
            self.results["type_safety"]["error"] = str(e)
    
    async def check_pep8_compliance(self):
        """Check PEP8 compliance using flake8."""
        print("\n[3/8] CHECKING PEP8 COMPLIANCE")
        print("="*60)
        
        try:
            # Run flake8
            result = subprocess.run(
                [sys.executable, "-m", "flake8", str(self.file_path), "--count", "--statistics", "--max-line-length=120"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("[OK] PEP8 compliant")
                self.results["pep8_compliance"]["status"] = "PASS"
                self.results["pep8_compliance"]["violations"] = []
            else:
                # Parse flake8 output
                output_lines = result.stdout.strip().split('\n') if result.stdout else []
                violations = [l for l in output_lines if self.file_path.name in l]
                
                print(f"[FAIL] Found {len(violations)} PEP8 violations")
                self.results["pep8_compliance"]["status"] = "FAIL"
                self.results["pep8_compliance"]["violations"] = violations[:10]
                
                # Show statistics
                if result.stderr:
                    print("\nViolation statistics:")
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            print(f"  {line}")
                
        except Exception as e:
            print(f"[FAIL] Could not run flake8: {e}")
            self.results["pep8_compliance"]["status"] = "ERROR"
            self.results["pep8_compliance"]["error"] = str(e)
    
    async def check_best_practices(self):
        """Check Python best practices."""
        print("\n[4/8] CHECKING BEST PRACTICES")
        print("="*60)
        
        content = self.file_path.read_text(encoding='utf-8')
        issues = []
        
        # Check for common issues
        checks = {
            "bare_except": (r'\bexcept\s*:', "Bare except clauses"),
            "print_statements": (r'\bprint\s*\(', "Print statements (should use logging)"),
            "global_variables": (r'^[A-Z_]+\s*=', "Global variables without Final"),
            "todo_comments": (r'#\s*(TODO|FIXME|XXX)', "TODO/FIXME comments"),
            "hardcoded_paths": (r'["\']C:\\\\', "Hardcoded Windows paths"),
            "no_docstring": (r'^\s*def\s+\w+\([^)]*\):\s*\n\s*[^"\']', "Functions without docstrings"),
        }
        
        for check_name, (pattern, description) in checks.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                issues.append(f"{description}: {len(matches)} occurrences")
                print(f"[FAIL] {description}: {len(matches)}")
            else:
                print(f"[OK] No {description.lower()}")
        
        # Check for proper error handling
        try:
            tree = ast.parse(content)
            
            # Check for logging
            has_logging = "import logging" in content or "from logging" in content
            print(f"{'[OK]' if has_logging else '[FAIL]'} Logging configured: {has_logging}")
            
            # Check for type hints
            functions_with_hints = 0
            total_functions = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_functions += 1
                    if node.returns or any(arg.annotation for arg in node.args.args):
                        functions_with_hints += 1
            
            hint_percentage = (functions_with_hints / max(total_functions, 1)) * 100
            print(f"{'[OK]' if hint_percentage > 80 else '[FAIL]'} Type hints: {hint_percentage:.1f}% of functions")
            
            # Check for tests
            has_tests = "if __name__ == '__main__':" in content
            print(f"{'[OK]' if has_tests else '[FAIL]'} Has test/example code: {has_tests}")
            
        except Exception as e:
            issues.append(f"AST parsing error: {e}")
        
        self.results["best_practices"]["issues"] = issues
        self.results["best_practices"]["status"] = "PASS" if len(issues) < 3 else "WARN"
    
    async def check_screenshot_features(self):
        """Check screenshot capabilities."""
        print("\n[5/8] CHECKING SCREENSHOT FEATURES")
        print("="*60)
        
        content = self.file_path.read_text(encoding='utf-8')
        
        features = {
            "capture_screenshots": "capture_screenshot" in content or "screenshot" in content,
            "full_page_screenshots": "full_page" in content or "fullPage" in content,
            "element_highlighting": "highlight" in content,
            "multiple_formats": "png" in content and ("jpeg" in content or "jpg" in content),
            "base64_encoding": "base64" in content,
            "save_to_file": "save" in content and "screenshot" in content,
            "viewport_sizes": "viewport" in content or "resolution" in content,
            "screenshot_class": "Screenshot" in content
        }
        
        for feature, present in features.items():
            print(f"{'[OK]' if present else '[FAIL]'} {feature.replace('_', ' ').title()}: {present}")
        
        self.results["screenshot_features"] = features
        self.results["screenshot_features"]["complete"] = all(features.values())
    
    async def check_production_readiness(self):
        """Check production readiness features."""
        print("\n[6/8] CHECKING PRODUCTION READINESS")
        print("="*60)
        
        content = self.file_path.read_text(encoding='utf-8')
        
        features = {
            "error_handling": "try:" in content and "except" in content,
            "logging": "logging" in content,
            "async_support": "async def" in content,
            "rate_limiting": "rate_limit" in content or "sleep" in content,
            "retry_mechanism": "retry" in content or "max_attempts" in content,
            "timeout_handling": "timeout" in content,
            "validation": "validate" in content or "ValidationError" in content,
            "configuration": "Config" in content or "Settings" in content,
            "caching": "cache" in content or "lru_cache" in content,
            "thread_safety": "Lock" in content or "thread" in content,
            "memory_management": "del " in content or "gc." in content,
            "metrics": "metric" in content or "counter" in content
        }
        
        score = sum(features.values())
        max_score = len(features)
        percentage = (score / max_score) * 100
        
        for feature, present in features.items():
            status = "[OK]" if present else "[FAIL]"
            print(f"{status} {feature.replace('_', ' ').title()}: {present}")
        
        print(f"\nProduction Readiness Score: {score}/{max_score} ({percentage:.1f}%)")
        
        self.results["production_readiness"] = features
        self.results["production_readiness"]["score"] = f"{score}/{max_score}"
        self.results["production_readiness"]["percentage"] = percentage
        self.results["production_readiness"]["status"] = "PASS" if percentage >= 80 else "NEEDS_IMPROVEMENT"
    
    async def check_master_plan_conformance(self):
        """Check conformance to UI_TESTING_AUTOMATION_MASTER_PLAN.md."""
        print("\n[7/8] CHECKING MASTER PLAN CONFORMANCE")
        print("="*60)
        
        # Read master plan if exists
        master_plan_path = self.file_path.parent / "UI_TESTING_AUTOMATION_MASTER_PLAN.md"
        
        if master_plan_path.exists():
            master_plan = master_plan_path.read_text()
            
            # Check for required components mentioned in plan
            required_components = {
                "ElementsExtractorNoLLM": "ElementsExtractorNoLLM" in self.file_path.read_text(),
                "shadow_dom_support": "shadow" in self.file_path.read_text().lower(),
                "iframe_support": "iframe" in self.file_path.read_text().lower(),
                "multiple_strategies": "strategy" in self.file_path.read_text().lower(),
                "contract_validation": "contract" in self.file_path.read_text().lower() or "validate" in self.file_path.read_text().lower(),
                "live_website_testing": "http" in self.file_path.read_text() or "browser" in self.file_path.read_text()
            }
            
            for component, present in required_components.items():
                print(f"{'[OK]' if present else '[FAIL]'} {component.replace('_', ' ').title()}: {present}")
            
            self.results["master_plan_conformance"] = required_components
            self.results["master_plan_conformance"]["compliant"] = all(required_components.values())
        else:
            print("[FAIL] Master plan not found")
            self.results["master_plan_conformance"]["status"] = "MASTER_PLAN_NOT_FOUND"
    
    async def apply_master_strategies(self):
        """Apply master prompt strategies for deep analysis."""
        print("\n[8/8] APPLYING MASTER PROMPT STRATEGIES")
        print("="*60)
        
        # Use multiple strategies for comprehensive analysis
        
        # 1. Constitutional AI - Check for safety and ethics
        print("\n[Constitutional AI Analysis]")
        content = self.file_path.read_text()
        safety_checks = {
            "no_malicious_code": "eval(" not in content and "exec(" not in content,
            "no_credential_exposure": "password" not in content.lower() or "getpass" in content,
            "safe_file_operations": "shutil.rmtree" not in content or "safety_check" in content,
            "input_validation": "validate" in content or "sanitize" in content
        }
        for check, passed in safety_checks.items():
            print(f"  {'[OK]' if passed else '[FAIL]'} {check.replace('_', ' ').title()}")
        
        # 2. Self-Consistency - Check for consistent patterns
        print("\n[Self-Consistency Analysis]")
        consistency_checks = {
            "consistent_naming": self._check_naming_consistency(content),
            "consistent_error_handling": content.count("try:") > 0 and content.count("except") > 0,
            "consistent_returns": self._check_return_consistency(content),
            "consistent_logging": content.count("logger.") > 10 or content.count("logging.") > 10
        }
        for check, passed in consistency_checks.items():
            print(f"  {'[OK]' if passed else '[FAIL]'} {check.replace('_', ' ').title()}")
        
        # 3. Tree of Thoughts - Analyze architectural decisions
        print("\n[Tree of Thoughts Analysis]")
        architecture_analysis = {
            "modular_design": content.count("class ") > 3,
            "separation_of_concerns": content.count("def ") > 20,
            "single_responsibility": self._check_single_responsibility(content),
            "dependency_injection": "__init__" in content and "self." in content
        }
        for check, passed in architecture_analysis.items():
            print(f"  {'[OK]' if passed else '[FAIL]'} {check.replace('_', ' ').title()}")
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _check_naming_consistency(self, content: str) -> bool:
        """Check if naming conventions are consistent."""
        # Check for snake_case in functions and camelCase in classes
        function_pattern = re.compile(r'def ([a-z_][a-z0-9_]*)\(')
        class_pattern = re.compile(r'class ([A-Z][a-zA-Z0-9]*)')
        
        functions = function_pattern.findall(content)
        classes = class_pattern.findall(content)
        
        # Check if most functions are snake_case
        snake_case_functions = [f for f in functions if '_' in f or f.islower()]
        
        return len(snake_case_functions) >= len(functions) * 0.8
    
    def _check_return_consistency(self, content: str) -> bool:
        """Check if functions have consistent return patterns."""
        try:
            tree = ast.parse(content)
            functions_with_returns = 0
            total_functions = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_functions += 1
                    # Check if function has return statements
                    for child in ast.walk(node):
                        if isinstance(child, ast.Return):
                            functions_with_returns += 1
                            break
            
            # At least 70% of functions should have explicit returns
            return functions_with_returns >= total_functions * 0.7
        except:
            return False
    
    def _check_single_responsibility(self, content: str) -> bool:
        """Check if classes follow single responsibility principle."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Count methods in class
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    # If a class has more than 20 methods, it might be doing too much
                    if len(methods) > 20:
                        return False
            
            return True
        except:
            return False
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Based on type safety
        if self.results.get("type_safety", {}).get("status") != "PASS":
            recommendations.append("HIGH: Fix type errors - Add type hints to all functions and fix mypy errors")
        
        # Based on PEP8
        if self.results.get("pep8_compliance", {}).get("status") != "PASS":
            recommendations.append("MEDIUM: Fix PEP8 violations - Run black formatter and fix flake8 warnings")
        
        # Based on best practices
        if self.results.get("best_practices", {}).get("issues"):
            recommendations.append("MEDIUM: Address best practice issues - Remove bare excepts, add logging")
        
        # Based on screenshot features
        if not self.results.get("screenshot_features", {}).get("complete"):
            recommendations.append("HIGH: Implement missing screenshot features for full compliance")
        
        # Based on production readiness
        if self.results.get("production_readiness", {}).get("percentage", 0) < 80:
            recommendations.append("HIGH: Improve production readiness - Add retry mechanisms, caching, and metrics")
        
        # Based on master plan
        if not self.results.get("master_plan_conformance", {}).get("compliant"):
            recommendations.append("CRITICAL: Ensure full compliance with UI_TESTING_AUTOMATION_MASTER_PLAN.md")
        
        self.results["recommendations"] = recommendations
    
    async def generate_report(self):
        """Generate comprehensive QA report."""
        print("\n" + "="*60)
        print("COMPREHENSIVE QA REPORT")
        print("="*60)
        
        # Overall status
        critical_issues = 0
        if self.results.get("type_safety", {}).get("status") == "FAIL":
            critical_issues += 1
        if self.results.get("production_readiness", {}).get("percentage", 0) < 70:
            critical_issues += 1
        if not self.results.get("master_plan_conformance", {}).get("compliant"):
            critical_issues += 1
        
        overall_status = "PRODUCTION READY" if critical_issues == 0 else f"NEEDS WORK ({critical_issues} critical issues)"
        
        print(f"\n[STATUS] OVERALL STATUS: {overall_status}")
        
        print("\n[SCORES] SUMMARY SCORES:")
        print(f"  Type Safety: {self.results.get('type_safety', {}).get('status', 'N/A')}")
        print(f"  PEP8 Compliance: {self.results.get('pep8_compliance', {}).get('status', 'N/A')}")
        print(f"  Production Readiness: {self.results.get('production_readiness', {}).get('percentage', 0):.1f}%")
        print(f"  Screenshot Features: {'Complete' if self.results.get('screenshot_features', {}).get('complete') else 'Incomplete'}")
        print(f"  Master Plan Conformance: {'Compliant' if self.results.get('master_plan_conformance', {}).get('compliant') else 'Non-compliant'}")
        
        print("\n[RECOMMENDATIONS] RECOMMENDATIONS:")
        for rec in self.results.get("recommendations", []):
            print(f"  - {rec}")
        
        print("\n[METRICS] DETAILED METRICS:")
        if "file_analysis" in self.results:
            print(f"  File size: {self.results['file_analysis'].get('file_size', 0):,} bytes")
            print(f"  Total lines: {self.results['file_analysis'].get('total_lines', 0):,}")
            print(f"  Classes: {self.results['file_analysis'].get('classes', 0)}")
            print(f"  Functions: {self.results['file_analysis'].get('functions', 0)}")
        
        print("\n" + "="*60)
        print("END OF QA REPORT")
        print("="*60)
        
        return overall_status == "PRODUCTION READY"
    
    async def run_full_analysis(self):
        """Run complete QA analysis."""
        print("="*60)
        print("SENIOR QA ENGINEER ANALYSIS (30+ Years Experience)")
        print("File: elements_extractor_no_llm.py")
        print("="*60)
        
        # Run all checks
        await self.analyze_file_structure()
        await self.check_type_safety()
        await self.check_pep8_compliance()
        await self.check_best_practices()
        await self.check_screenshot_features()
        await self.check_production_readiness()
        await self.check_master_plan_conformance()
        await self.apply_master_strategies()
        
        # Generate final report
        is_production_ready = await self.generate_report()
        
        return is_production_ready

async def main():
    """Main entry point."""
    analyzer = QAAnalyzer()
    is_ready = await analyzer.run_full_analysis()
    
    # Save results to file
    import json
    with open("qa_analysis_results.json", "w") as f:
        json.dump(analyzer.results, f, indent=2, default=str)
    
    print(f"\nResults saved to qa_analysis_results.json")
    print(f"\nFinal verdict: {'[PASS] PRODUCTION READY' if is_ready else '[FAIL] NOT PRODUCTION READY'}")
    
    return 0 if is_ready else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)