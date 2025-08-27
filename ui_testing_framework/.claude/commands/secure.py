#!/usr/bin/env python3
"""
/secure Command Implementation
==============================
Constitutional AI security audit and remediation
"""

import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

@dataclass
class SecurityViolation:
    """Represents a security issue found in code"""
    severity: str  # critical, high, medium, low
    category: str
    line: int
    description: str
    recommendation: str
    cwe_id: Optional[str] = None
    
@dataclass 
class SecurityReport:
    """Complete security audit report"""
    file_path: Path
    scan_time: str
    violations: List[SecurityViolation]
    fixed_code: Optional[str]
    security_score: float
    compliant: bool
    
class ConstitutionalSecurityAuditor:
    """Implements Constitutional AI principles for security auditing"""
    
    # Security Constitution - Core Principles
    SECURITY_CONSTITUTION = {
        "NO_EXPOSED_SECRETS": {
            "principle": "API keys, passwords, tokens must be environment variables",
            "patterns": [
                r'api_key\s*=\s*["\'][\w\-]+["\']',
                r'password\s*=\s*["\'][\w\-]+["\']',
                r'token\s*=\s*["\'][\w\-]+["\']',
                r'secret\s*=\s*["\'][\w\-]+["\']',
                r'sk-[\w\-]+',  # OpenAI keys
                r'AIza[\w\-]+',  # Google keys
            ],
            "severity": "critical",
            "cwe": "CWE-798"
        },
        "INPUT_VALIDATION": {
            "principle": "All user inputs must be sanitized and validated",
            "patterns": [
                r'eval\s*\(',
                r'exec\s*\(',
                r'__import__\s*\(',
                r'compile\s*\(',
                r'input\s*\([^)]*\)(?!\s*\.strip)',
            ],
            "severity": "high",
            "cwe": "CWE-20"
        },
        "LEAST_PRIVILEGE": {
            "principle": "Code should request minimum necessary permissions",
            "patterns": [
                r'chmod\s+777',
                r'os\.system\s*\(',
                r'subprocess\.run\s*\([^,)]*shell\s*=\s*True',
            ],
            "severity": "high",
            "cwe": "CWE-250"
        },
        "DEFENSE_IN_DEPTH": {
            "principle": "Multiple layers of security checks",
            "patterns": [
                r'except\s*:\s*pass',
                r'except\s+Exception\s*:\s*pass',
                r'try:[^}]*except:[^}]*pass',
            ],
            "severity": "medium",
            "cwe": "CWE-391"
        },
        "SECURE_BY_DEFAULT": {
            "principle": "Default configurations must be secure",
            "patterns": [
                r'verify\s*=\s*False',  # SSL verification disabled
                r'DEBUG\s*=\s*True',
                r'allow_all_origins\s*=\s*True',
            ],
            "severity": "high",
            "cwe": "CWE-16"
        },
        "ERROR_HANDLING": {
            "principle": "Never expose sensitive information in errors",
            "patterns": [
                r'print\s*\([^)]*password[^)]*\)',
                r'logging\.[^(]*\([^)]*api_key[^)]*\)',
                r'return\s+str\s*\(\s*e\s*\)',
            ],
            "severity": "medium",
            "cwe": "CWE-209"
        },
        "SQL_INJECTION": {
            "principle": "Prevent SQL injection attacks",
            "patterns": [
                r'f["\'].*SELECT.*{[^}]+}.*["\']',
                r'["\'].*SELECT.*["\'].*\+.*',
                r'\.format\s*\([^)]*\).*WHERE',
            ],
            "severity": "critical",
            "cwe": "CWE-89"
        },
        "PATH_TRAVERSAL": {
            "principle": "Prevent directory traversal attacks",
            "patterns": [
                r'\.\./',
                r'os\.path\.join\s*\([^,)]*user_input',
                r'open\s*\([^,)]*\+[^,)]*\)',
            ],
            "severity": "high",
            "cwe": "CWE-22"
        }
    }
    
    def __init__(self):
        self.violations = []
        self.fixes_applied = 0
        
    def audit_principle(self, code: str, principle_name: str, principle_data: Dict) -> List[SecurityViolation]:
        """Audit code against a single constitutional principle"""
        violations = []
        
        for pattern in principle_data["patterns"]:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Get line number
                line_no = code[:match.start()].count('\n') + 1
                
                violation = SecurityViolation(
                    severity=principle_data["severity"],
                    category=principle_name,
                    line=line_no,
                    description=f"Violation of {principle_name}: {principle_data['principle']}",
                    recommendation=self.get_recommendation(principle_name, match.group()),
                    cwe_id=principle_data.get("cwe")
                )
                violations.append(violation)
                
        return violations
        
    def get_recommendation(self, principle: str, code_snippet: str) -> str:
        """Get specific remediation recommendation"""
        recommendations = {
            "NO_EXPOSED_SECRETS": "Move to environment variable: os.getenv('KEY_NAME')",
            "INPUT_VALIDATION": "Validate and sanitize input before processing",
            "LEAST_PRIVILEGE": "Use minimal required permissions",
            "DEFENSE_IN_DEPTH": "Add specific exception handling with proper logging",
            "SECURE_BY_DEFAULT": "Enable security features by default",
            "ERROR_HANDLING": "Log errors without exposing sensitive data",
            "SQL_INJECTION": "Use parameterized queries or ORM",
            "PATH_TRAVERSAL": "Validate and sanitize file paths"
        }
        return recommendations.get(principle, "Review and fix security issue")
        
    def fix_violation(self, code: str, violation: SecurityViolation) -> str:
        """Apply automated fix for a security violation"""
        lines = code.splitlines()
        
        if violation.category == "NO_EXPOSED_SECRETS":
            # Replace hardcoded secrets with env vars
            if violation.line <= len(lines):
                line = lines[violation.line - 1]
                # Extract variable name
                var_match = re.search(r'(\w+)\s*=\s*["\']', line)
                if var_match:
                    var_name = var_match.group(1).upper()
                    fixed_line = re.sub(
                        r'=\s*["\'][^"\']+["\']',
                        f'= os.getenv("{var_name}")',
                        line
                    )
                    lines[violation.line - 1] = fixed_line
                    self.fixes_applied += 1
                    
        elif violation.category == "INPUT_VALIDATION":
            # Add validation for dangerous functions
            if violation.line <= len(lines):
                line = lines[violation.line - 1]
                if "eval(" in line:
                    lines[violation.line - 1] = f"# SECURITY: Removed unsafe eval - {line}"
                    self.fixes_applied += 1
                elif "exec(" in line:
                    lines[violation.line - 1] = f"# SECURITY: Removed unsafe exec - {line}"
                    self.fixes_applied += 1
                    
        elif violation.category == "DEFENSE_IN_DEPTH":
            # Fix bare except clauses
            if violation.line <= len(lines):
                line = lines[violation.line - 1]
                if "except:" in line or "except Exception:" in line:
                    indent = len(line) - len(line.lstrip())
                    lines[violation.line - 1] = " " * indent + "except Exception as e:"
                    # Add proper error handling
                    if violation.line < len(lines) and "pass" in lines[violation.line]:
                        lines[violation.line] = " " * (indent + 4) + 'logger.error(f"Error occurred: {type(e).__name__}")'
                    self.fixes_applied += 1
                    
        elif violation.category == "SECURE_BY_DEFAULT":
            # Fix insecure defaults
            if violation.line <= len(lines):
                line = lines[violation.line - 1]
                line = line.replace("verify=False", "verify=True")
                line = line.replace("DEBUG=True", "DEBUG=False")
                line = line.replace("allow_all_origins=True", "allow_all_origins=False")
                lines[violation.line - 1] = line
                self.fixes_applied += 1
                
        return '\n'.join(lines)
        
    def calculate_security_score(self, violations: List[SecurityViolation]) -> float:
        """Calculate security score based on violations"""
        if not violations:
            return 100.0
            
        severity_weights = {
            "critical": 25,
            "high": 15,
            "medium": 10,
            "low": 5
        }
        
        total_penalty = sum(severity_weights.get(v.severity, 5) for v in violations)
        score = max(0, 100 - total_penalty)
        return score
        
    def audit(self, file_path: Path, auto_fix: bool = False) -> SecurityReport:
        """Perform comprehensive security audit"""
        print(f"[SECURE] Auditing {file_path.name}")
        print("=" * 60)
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
            
        # Audit against all constitutional principles
        all_violations = []
        for principle_name, principle_data in self.SECURITY_CONSTITUTION.items():
            print(f"[CHECKING] {principle_name}...")
            violations = self.audit_principle(original_code, principle_name, principle_data)
            all_violations.extend(violations)
            
        # Sort by severity and line
        all_violations.sort(key=lambda v: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}[v.severity],
            v.line
        ))
        
        # Apply fixes if requested
        fixed_code = None
        if auto_fix and all_violations:
            print("\n[FIXING] Applying automated security fixes...")
            fixed_code = original_code
            for violation in all_violations:
                fixed_code = self.fix_violation(fixed_code, violation)
                
        # Calculate security score
        score = self.calculate_security_score(all_violations)
        compliant = score >= 80  # 80% threshold for compliance
        
        # Create report
        report = SecurityReport(
            file_path=file_path,
            scan_time=datetime.now().isoformat(),
            violations=all_violations,
            fixed_code=fixed_code,
            security_score=score,
            compliant=compliant
        )
        
        # Print summary
        print("\n" + "=" * 60)
        print("[SECURITY AUDIT REPORT]")
        print("=" * 60)
        print(f"File: {file_path.name}")
        print(f"Security Score: {score:.1f}/100 {'[PASS]' if compliant else '[FAIL]'}")
        print(f"Violations Found: {len(all_violations)}")
        
        if all_violations:
            print("\n[VIOLATIONS BY SEVERITY]")
            severity_counts = {}
            for v in all_violations:
                severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1
                
            for severity in ["critical", "high", "medium", "low"]:
                if severity in severity_counts:
                    print(f"  {severity.upper()}: {severity_counts[severity]}")
                    
            print("\n[TOP VIOLATIONS]")
            for v in all_violations[:5]:
                print(f"\n  Line {v.line} [{v.severity.upper()}] {v.category}")
                print(f"    Issue: {v.description}")
                print(f"    Fix: {v.recommendation}")
                if v.cwe_id:
                    print(f"    CWE: {v.cwe_id}")
                    
        if auto_fix and self.fixes_applied > 0:
            print(f"\n[FIXES] Applied {self.fixes_applied} automated fixes")
            
        return report
        
    def generate_security_test(self, report: SecurityReport) -> str:
        """Generate security test cases based on audit"""
        test_code = f'''"""
Security Test Suite
Generated from security audit on {report.scan_time}
"""

import pytest
import os
from pathlib import Path

class TestSecurity:
    """Security test cases for {report.file_path.name}"""
    
    def test_no_hardcoded_secrets(self):
        """Ensure no hardcoded secrets in code"""
        code_path = Path("{report.file_path}")
        with open(code_path, "r") as f:
            content = f.read()
            
        # Check for common secret patterns
        assert "api_key=" not in content.lower()
        assert "password=" not in content.lower()
        assert "sk-" not in content  # OpenAI keys
        assert "AIza" not in content  # Google keys
        
    def test_environment_variables_used(self):
        """Verify environment variables are used for sensitive data"""
        required_env_vars = ["OPENAI_API_KEY", "GOOGLE_API_KEY"]
        for var in required_env_vars:
            assert os.getenv(var) is not None, f"{{var}} not configured"
            
    def test_no_dangerous_functions(self):
        """Ensure no dangerous functions are used"""
        code_path = Path("{report.file_path}")
        with open(code_path, "r") as f:
            content = f.read()
            
        assert "eval(" not in content
        assert "exec(" not in content
        assert "__import__(" not in content
        
    def test_secure_defaults(self):
        """Verify secure default configurations"""
        code_path = Path("{report.file_path}")
        with open(code_path, "r") as f:
            content = f.read()
            
        assert "verify=False" not in content
        assert "DEBUG=True" not in content
'''
        return test_code
        
def main():
    """Main entry point for /secure command"""
    import sys
    import os
    from pathlib import Path
    
    # Ensure proper working directory
    script_dir = Path(__file__).parent.parent.parent
    os.chdir(script_dir)
    
    if len(sys.argv) < 2:
        print("Usage: secure.py <file_path> [--fix]")
        sys.exit(1)
        
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)
        
    auto_fix = "--fix" in sys.argv
    
    auditor = ConstitutionalSecurityAuditor()
    report = auditor.audit(file_path, auto_fix=auto_fix)
    
    # Save report
    report_path = file_path.with_suffix('.security.json')
    report_dict = {
        "file": str(report.file_path),
        "scan_time": report.scan_time,
        "score": report.security_score,
        "compliant": report.compliant,
        "violations": [
            {
                "severity": v.severity,
                "category": v.category,
                "line": v.line,
                "description": v.description,
                "recommendation": v.recommendation,
                "cwe": v.cwe_id
            }
            for v in report.violations
        ]
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2)
        
    print(f"\n[REPORT] Security report saved to: {report_path}")
    
    # Save fixed code if applicable
    if auto_fix and report.fixed_code:
        fixed_path = file_path.with_suffix('.secure.py')
        with open(fixed_path, 'w', encoding='utf-8') as f:
            f.write(report.fixed_code)
        print(f"[FIXED] Secure version saved to: {fixed_path}")
        
    # Generate security tests
    test_code = auditor.generate_security_test(report)
    test_path = file_path.with_suffix('.security_test.py')
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_code)
    print(f"[TESTS] Security tests saved to: {test_path}")
    
if __name__ == "__main__":
    main()