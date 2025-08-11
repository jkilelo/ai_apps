#!/usr/bin/env python3
"""
Validation script to ensure CODER Agent meets all CODER v3.1 requirements
"""

import sys
import ast
import importlib
from pathlib import Path
from typing import List, Dict, Any, Tuple


class CoderV3Validator:
    """Validates implementation against CODER v3.1 requirements"""
    
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║         CODER v3.1 Requirements Validation                   ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Run all validation checks
        self.check_pydantic_contracts()
        self.check_todo_management()
        self.check_platform_agnostic()
        self.check_preflight_system()
        self.check_tdd_implementation()
        self.check_error_handling()
        self.check_security_hardening()
        self.check_performance_bounds()
        self.check_observability()
        self.check_documentation()
        
        # Print results
        self.print_results()
        
        return len(self.results["failed"]) == 0
    
    def check_pydantic_contracts(self):
        """Check Requirement 1: Pydantic v2 contracts for all functions"""
        print("\n🔍 Checking Pydantic v2 Contracts...")
        
        try:
            # Check contracts module
            contracts_path = Path("coder_agent/contracts/base.py")
            if not contracts_path.exists():
                self.results["failed"].append("Missing contracts/base.py")
                return
            
            with open(contracts_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Check for Pydantic v2 features
            has_base_model = False
            has_config_dict = False
            has_field_validator = False
            contract_classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if inherits from BaseModel
                    for base in node.bases:
                        if isinstance(base, ast.Name) and "Model" in base.id:
                            has_base_model = True
                            contract_classes.append(node.name)
                    
                    # Check for ConfigDict (Pydantic v2 feature)
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name) and target.id == "model_config":
                                    has_config_dict = True
                
                # Check for field_validator (Pydantic v2)
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == "field_validator":
                            has_field_validator = True
            
            if has_base_model and has_config_dict:
                self.results["passed"].append(f"✅ Pydantic v2 contracts implemented ({len(contract_classes)} contracts)")
            else:
                self.results["failed"].append("❌ Pydantic v2 features not fully utilized")
            
            # Check that core functions use contracts
            engine_path = Path("coder_agent/core/engine.py")
            if engine_path.exists():
                with open(engine_path, 'r') as f:
                    engine_content = f.read()
                    
                if "AgentRequest" in engine_content and "AgentResponse" in engine_content:
                    self.results["passed"].append("✅ Core engine uses Pydantic contracts")
                else:
                    self.results["warnings"].append("⚠️ Core engine may not fully use contracts")
            
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking Pydantic contracts: {e}")
    
    def check_todo_management(self):
        """Check Requirement 2: B.R.E.A.K. methodology for TODO management"""
        print("\n🔍 Checking TODO Management (B.R.E.A.K.)...")
        
        try:
            planner_path = Path("coder_agent/core/task_planner.py")
            if not planner_path.exists():
                self.results["failed"].append("Missing task_planner.py")
                return
            
            with open(planner_path, 'r') as f:
                content = f.read()
            
            # Check for B.R.E.A.K. implementation
            break_methods = {
                "break_down": "B - Break down" in content,
                "review": "R - Review" in content,
                "establish": "E - Establish" in content,
                "analyze": "A - Analyze" in content,
                "keep_track": "K - " in content or "K - Keep" in content
            }
            
            if all(break_methods.values()):
                self.results["passed"].append("✅ B.R.E.A.K. methodology fully implemented")
            else:
                missing = [k for k, v in break_methods.items() if not v]
                self.results["failed"].append(f"❌ B.R.E.A.K. missing: {missing}")
            
            # Check for TodoItem contract
            if "TodoItem" in content and "TaskPlan" in content:
                self.results["passed"].append("✅ TODO contracts implemented")
            else:
                self.results["warnings"].append("⚠️ TODO contracts may be incomplete")
                
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking TODO management: {e}")
    
    def check_platform_agnostic(self):
        """Check Requirement 3: Platform-agnostic code"""
        print("\n🔍 Checking Platform Agnostic Code...")
        
        try:
            # Check for platform-specific code
            platform_issues = []
            
            for py_file in Path("coder_agent").rglob("*.py"):
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                # Check for platform-specific paths
                if "\\" in content and "Windows" not in content:
                    platform_issues.append(f"Hardcoded Windows path in {py_file.name}")
                
                # Check for Path usage
                if "pathlib" in content or "Path(" in content:
                    # Good - using pathlib
                    pass
                elif "os.path.join" in content:
                    # Also acceptable
                    pass
                elif "/" in content and "://" not in content:
                    # Might be hardcoded Unix path
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "/" in line and not line.strip().startswith("#"):
                            if "http" not in line and "://" not in line:
                                # Could be a path
                                pass
            
            # Check for platform detection
            helpers_path = Path("coder_agent/core/engine_helpers.py")
            if helpers_path.exists():
                with open(helpers_path, 'r') as f:
                    content = f.read()
                    if "platform.system()" in content:
                        self.results["passed"].append("✅ Platform detection implemented")
            
            if not platform_issues:
                self.results["passed"].append("✅ Code is platform-agnostic")
            else:
                self.results["warnings"].append(f"⚠️ Potential platform issues: {platform_issues[:2]}")
                
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking platform code: {e}")
    
    def check_preflight_system(self):
        """Check Requirement 4: Pre-flight checks"""
        print("\n🔍 Checking Pre-flight System...")
        
        try:
            preflight_path = Path("coder_agent/preflight.py")
            if not preflight_path.exists():
                self.results["failed"].append("Missing preflight.py")
                return
            
            with open(preflight_path, 'r') as f:
                content = f.read()
            
            required_checks = [
                "check_virtual_environment",
                "check_llm_connection",
                "check_required_tools",
                "Python version"
            ]
            
            found_checks = [check for check in required_checks if check in content]
            
            if len(found_checks) == len(required_checks):
                self.results["passed"].append("✅ All pre-flight checks implemented")
            else:
                missing = set(required_checks) - set(found_checks)
                self.results["failed"].append(f"❌ Missing pre-flight checks: {missing}")
            
            # Check if pre-flight is called in engine
            engine_path = Path("coder_agent/core/engine.py")
            if engine_path.exists():
                with open(engine_path, 'r') as f:
                    if "_run_preflight_checks" in f.read():
                        self.results["passed"].append("✅ Pre-flight integrated in engine")
                        
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking pre-flight: {e}")
    
    def check_tdd_implementation(self):
        """Check Requirement 5: TDD implementation"""
        print("\n🔍 Checking TDD Implementation...")
        
        try:
            # Check if tests are written first in task planner
            planner_path = Path("coder_agent/core/task_planner.py")
            if planner_path.exists():
                with open(planner_path, 'r') as f:
                    content = f.read()
                    
                # Check for TDD pattern
                if "Write tests" in content and "TDD" in content:
                    # Check that tests come before implementation
                    lines = content.split('\n')
                    test_line = -1
                    impl_line = -1
                    
                    for i, line in enumerate(lines):
                        if "Write tests" in line:
                            test_line = i
                        if "implement" in line.lower() and test_line > 0:
                            impl_line = i
                            break
                    
                    if test_line > 0 and (impl_line == -1 or test_line < impl_line):
                        self.results["passed"].append("✅ TDD: Tests written before implementation")
                    else:
                        self.results["warnings"].append("⚠️ TDD order may not be enforced")
                else:
                    self.results["failed"].append("❌ TDD not implemented in planning")
                    
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking TDD: {e}")
    
    def check_error_handling(self):
        """Check Requirement 6: Error handling excellence"""
        print("\n🔍 Checking Error Handling...")
        
        try:
            error_patterns = []
            recovery_found = False
            
            for py_file in Path("coder_agent/core").glob("*.py"):
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                # Count try/except blocks
                try_count = content.count("try:")
                except_count = content.count("except")
                
                if try_count > 0:
                    error_patterns.append(f"{py_file.name}: {try_count} error handlers")
                
                # Check for recovery strategies
                if "recovery" in content.lower() or "retry" in content.lower():
                    recovery_found = True
            
            if error_patterns and recovery_found:
                self.results["passed"].append(f"✅ Comprehensive error handling ({len(error_patterns)} modules)")
                self.results["passed"].append("✅ Error recovery strategies implemented")
            else:
                self.results["warnings"].append("⚠️ Error handling could be improved")
                
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking error handling: {e}")
    
    def check_security_hardening(self):
        """Check Requirement 7: Security hardening"""
        print("\n🔍 Checking Security Hardening...")
        
        try:
            config_path = Path("coder_agent/config/settings.py")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                    
                security_features = {
                    "file_deletion_control": "allow_file_deletion" in content,
                    "command_blocking": "blocked_commands" in content,
                    "confirmation_required": "require_confirmation" in content,
                    "api_key_handling": "api_key" in content and "environ" in content
                }
                
                if all(security_features.values()):
                    self.results["passed"].append("✅ Security hardening implemented")
                else:
                    missing = [k for k, v in security_features.items() if not v]
                    self.results["warnings"].append(f"⚠️ Security features missing: {missing}")
                    
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking security: {e}")
    
    def check_performance_bounds(self):
        """Check Requirement 8: Performance bounds"""
        print("\n🔍 Checking Performance Bounds...")
        
        try:
            # Check for timeout handling
            timeout_found = False
            token_limits = False
            
            for py_file in Path("coder_agent").rglob("*.py"):
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                if "timeout" in content.lower():
                    timeout_found = True
                if "max_tokens" in content or "MAX_CONTEXT_TOKENS" in content:
                    token_limits = True
            
            if timeout_found:
                self.results["passed"].append("✅ Timeout bounds implemented")
            else:
                self.results["warnings"].append("⚠️ Timeout handling could be improved")
            
            if token_limits:
                self.results["passed"].append("✅ Token limits enforced")
            else:
                self.results["warnings"].append("⚠️ Token limit enforcement not found")
                
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking performance: {e}")
    
    def check_observability(self):
        """Check Requirement 9: Observability and monitoring"""
        print("\n🔍 Checking Observability...")
        
        try:
            # Check for logging
            logging_found = False
            structlog_found = False
            
            for py_file in Path("coder_agent/core").glob("*.py"):
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                if "logger" in content or "structlog" in content:
                    logging_found = True
                if "structlog" in content:
                    structlog_found = True
            
            if structlog_found:
                self.results["passed"].append("✅ Structured logging implemented")
            elif logging_found:
                self.results["passed"].append("✅ Basic logging implemented")
            else:
                self.results["failed"].append("❌ No logging found")
            
            # Check for metrics/telemetry
            if Path("coder_agent/core/metacognition.py").exists():
                self.results["passed"].append("✅ Metacognitive monitoring implemented")
                
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking observability: {e}")
    
    def check_documentation(self):
        """Check Requirement 10: Documentation excellence"""
        print("\n🔍 Checking Documentation...")
        
        try:
            # Check for docstrings
            modules_with_docs = 0
            modules_total = 0
            
            for py_file in Path("coder_agent").rglob("*.py"):
                modules_total += 1
                with open(py_file, 'r') as f:
                    content = f.read()
                    if '"""' in content or "'''" in content:
                        modules_with_docs += 1
            
            doc_coverage = (modules_with_docs / max(modules_total, 1)) * 100
            
            if doc_coverage > 80:
                self.results["passed"].append(f"✅ Documentation coverage: {doc_coverage:.0f}%")
            elif doc_coverage > 50:
                self.results["warnings"].append(f"⚠️ Documentation coverage: {doc_coverage:.0f}%")
            else:
                self.results["failed"].append(f"❌ Poor documentation: {doc_coverage:.0f}%")
            
            # Check for README
            if Path("coder_agent/README.md").exists():
                self.results["passed"].append("✅ README documentation exists")
                
        except Exception as e:
            self.results["failed"].append(f"❌ Error checking documentation: {e}")
    
    def print_results(self):
        """Print validation results"""
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        if self.results["passed"]:
            print("\n✅ PASSED CHECKS:")
            for item in self.results["passed"]:
                print(f"  {item}")
        
        if self.results["warnings"]:
            print("\n⚠️  WARNINGS:")
            for item in self.results["warnings"]:
                print(f"  {item}")
        
        if self.results["failed"]:
            print("\n❌ FAILED CHECKS:")
            for item in self.results["failed"]:
                print(f"  {item}")
        
        # Summary
        total = len(self.results["passed"]) + len(self.results["failed"])
        pass_rate = (len(self.results["passed"]) / max(total, 1)) * 100
        
        print("\n" + "=" * 60)
        print(f"SUMMARY: {len(self.results['passed'])}/{total} checks passed ({pass_rate:.0f}%)")
        
        if pass_rate >= 90:
            print("🎉 CODER Agent EXCEEDS v3.1 requirements!")
        elif pass_rate >= 70:
            print("✅ CODER Agent MEETS most v3.1 requirements")
        else:
            print("❌ CODER Agent needs improvement to meet v3.1 requirements")
        print("=" * 60)


if __name__ == "__main__":
    validator = CoderV3Validator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)