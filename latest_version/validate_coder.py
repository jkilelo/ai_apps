#!/usr/bin/env python3
"""
CODER™ Validation Script
Automatically checks if code follows CODER protocol
"""

import os
import sys
import ast
import re
from pathlib import Path
from datetime import datetime

class CODERValidator:
    """Validates code against CODER protocol requirements"""
    
    def __init__(self, directory="."):
        self.directory = Path(directory)
        self.violations = []
        self.score = 100
        self.report = []
        
    def validate(self):
        """Run all validation checks"""
        print("="*60)
        print("🔍 CODER™ Protocol Validation")
        print("="*60)
        
        # Run all checks
        self.check_tests_exist()
        self.check_test_first()
        self.check_single_file_components()
        self.check_no_unnecessary_files()
        self.check_no_deprecated_modules()
        self.check_no_magic_numbers()
        self.check_function_length()
        self.check_exception_handling()
        self.check_dependencies()
        self.check_documentation()
        
        # Generate report
        self.generate_report()
        
        return self.score >= 90
    
    def check_tests_exist(self):
        """Check if tests exist for all modules"""
        print("\n✓ Checking for tests...")
        
        py_files = list(self.directory.glob("*.py"))
        test_files = [f for f in py_files if f.name.startswith("test_")]
        non_test_files = [f for f in py_files if not f.name.startswith("test_") 
                          and f.name != "setup.py" 
                          and f.name != "validate_coder.py"]
        
        for module in non_test_files:
            test_name = f"test_{module.stem}.py"
            if not (self.directory / test_name).exists():
                # Check if tests are in a consolidated test file
                if not self.directory.joinpath("tests.py").exists():
                    self.add_violation(f"No tests found for {module.name}", 30)
        
    def check_test_first(self):
        """Check if tests were written before implementation"""
        print("✓ Checking test-first development...")
        
        # Check file modification times
        for test_file in self.directory.glob("test_*.py"):
            module_name = test_file.stem.replace("test_", "") + ".py"
            module_file = self.directory / module_name
            
            if module_file.exists():
                test_stat = test_file.stat()
                module_stat = module_file.stat()
                
                # Note: This is a heuristic - can't always determine definitively
                if test_stat.st_mtime > module_stat.st_mtime:
                    self.report.append(f"⚠️  Warning: {test_file.name} modified after {module_name}")
    
    def check_single_file_components(self):
        """Check for single file per component principle"""
        print("✓ Checking single-file architecture...")
        
        # Look for common violations
        utils_files = list(self.directory.glob("**/utils.py"))
        helper_files = list(self.directory.glob("**/helper*.py"))
        
        if utils_files:
            self.add_violation(f"Found utils files: {utils_files}", 20)
        if helper_files:
            self.add_violation(f"Found helper files: {helper_files}", 20)
    
    def check_no_unnecessary_files(self):
        """Check for unnecessary files"""
        print("✓ Checking for unnecessary files...")
        
        unnecessary_patterns = [
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            "Thumbs.db",
            "*.log",
            "*.tmp",
            "*.bak"
        ]
        
        for pattern in unnecessary_patterns:
            files = list(self.directory.glob(f"**/{pattern}"))
            if files:
                self.add_violation(f"Unnecessary files found: {pattern}", 10)
    
    def check_no_deprecated_modules(self):
        """Check for deprecated module usage"""
        print("✓ Checking for deprecated modules...")
        
        deprecated = {
            'imp': 'Use importlib instead',
            'urllib2': 'Use urllib.request instead',
            'ConfigParser': 'Use configparser instead',
            'collections.Mapping': 'Use collections.abc.Mapping instead'
        }
        
        for py_file in self.directory.glob("**/*.py"):
            content = py_file.read_text()
            for module, suggestion in deprecated.items():
                if f"import {module}" in content or f"from {module}" in content:
                    self.add_violation(f"Deprecated module {module} in {py_file.name}. {suggestion}", 10)
    
    def check_no_magic_numbers(self):
        """Check for magic numbers in code"""
        print("✓ Checking for magic numbers...")
        
        for py_file in self.directory.glob("**/*.py"):
            if py_file.name == "validate_coder.py":
                continue
                
            content = py_file.read_text()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Skip comments and strings
                if '#' in line:
                    line = line[:line.index('#')]
                
                # Look for numbers not in constants
                if re.search(r'\b\d+\b', line) and not line.strip().startswith(('CONST', 'MAX', 'MIN', 'DEFAULT')):
                    if not any(x in line for x in ['=', 'range(', '[', ']', '(', ')', 'return']):
                        continue
                    # Check if it's a simple assignment to a CONSTANT
                    if re.match(r'^[A-Z_]+\s*=\s*\d+', line.strip()):
                        continue
                    # Otherwise might be a magic number
                    if any(op in line for op in ['>', '<', '==', '!=', '>=', '<=']):
                        self.report.append(f"⚠️  Possible magic number in {py_file.name}:{i}")
    
    def check_function_length(self):
        """Check that functions are under 20 lines"""
        print("✓ Checking function length...")
        
        for py_file in self.directory.glob("**/*.py"):
            try:
                tree = ast.parse(py_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        length = node.end_lineno - node.lineno
                        if length > 20:
                            self.add_violation(
                                f"Function {node.name} in {py_file.name} is {length} lines (max: 20)",
                                10
                            )
            except:
                pass  # Skip files that can't be parsed
    
    def check_exception_handling(self):
        """Check for proper exception handling"""
        print("✓ Checking exception handling...")
        
        for py_file in self.directory.glob("**/*.py"):
            content = py_file.read_text()
            
            # Check for bare except
            if re.search(r'except\s*:', content):
                self.add_violation(f"Bare except in {py_file.name}", 10)
            
            # Check for pass in exception
            if re.search(r'except.*:\s*\n\s*pass', content):
                self.add_violation(f"Silent exception failure in {py_file.name}", 10)
    
    def check_dependencies(self):
        """Check for minimal dependencies"""
        print("✓ Checking dependencies...")
        
        imports = set()
        for py_file in self.directory.glob("**/*.py"):
            content = py_file.read_text()
            
            # Extract imports
            import_lines = re.findall(r'^(?:import|from)\s+(\S+)', content, re.MULTILINE)
            imports.update(import_lines)
        
        # Count non-stdlib imports
        stdlib = {'os', 'sys', 'json', 'pathlib', 're', 'ast', 'datetime', 
                  'collections', 'itertools', 'functools', 'typing'}
        external = [imp for imp in imports if not any(imp.startswith(s) for s in stdlib)]
        
        if len(external) > 10:
            self.add_violation(f"Too many external dependencies: {len(external)}", 10)
    
    def check_documentation(self):
        """Check for proper documentation"""
        print("✓ Checking documentation...")
        
        for py_file in self.directory.glob("**/*.py"):
            if py_file.name == "validate_coder.py":
                continue
                
            try:
                tree = ast.parse(py_file.read_text())
                
                # Check module docstring
                if not ast.get_docstring(tree):
                    self.report.append(f"⚠️  No module docstring in {py_file.name}")
                
                # Check function docstrings
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            self.report.append(f"⚠️  No docstring for {node.name} in {py_file.name}")
            except:
                pass
    
    def add_violation(self, message, penalty):
        """Add a violation and reduce score"""
        self.violations.append(message)
        self.score -= penalty
        print(f"  ❌ {message} (-{penalty} points)")
    
    def generate_report(self):
        """Generate final validation report"""
        print("\n" + "="*60)
        print("📊 CODER™ Validation Report")
        print("="*60)
        
        if self.violations:
            print("\n❌ Violations Found:")
            for v in self.violations:
                print(f"  • {v}")
        else:
            print("\n✅ No violations found!")
        
        if self.report:
            print("\n⚠️  Warnings:")
            for r in self.report:
                print(f"  • {r}")
        
        print(f"\n📈 Final Score: {self.score}/100")
        
        if self.score >= 90:
            print("✅ PASSED - Code meets CODER standards!")
        else:
            print("❌ FAILED - Code does not meet CODER standards")
            print(f"   Need {90 - self.score} more points to pass")
        
        print("\n" + "="*60)
        
        # Return report as dict
        return {
            "score": self.score,
            "passed": self.score >= 90,
            "violations": self.violations,
            "warnings": self.report,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Run validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate code against CODER protocol")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to validate")
    parser.add_argument("--strict", action="store_true", help="Strict mode (fail on warnings)")
    args = parser.parse_args()
    
    validator = CODERValidator(args.directory)
    passed = validator.validate()
    
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()