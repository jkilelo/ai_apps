"""Security audit and compliance monitoring"""
import os
import json
import hashlib
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import re

from loguru import logger


@dataclass
class SecurityFinding:
    """Security audit finding"""
    id: str
    severity: str  # critical, high, medium, low
    category: str  # secrets, permissions, dependencies, etc.
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: Optional[str] = None
    remediation_effort: str = "low"  # low, medium, high


@dataclass
class ComplianceCheck:
    """Compliance requirement check"""
    standard: str  # OWASP, PCI-DSS, GDPR, etc.
    requirement: str
    status: str  # pass, fail, warning, not_applicable
    description: str
    evidence: Optional[str] = None


class SecurityAuditor:
    """Comprehensive security auditing system"""
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root
        self.findings: List[SecurityFinding] = []
        self.compliance_checks: List[ComplianceCheck] = []
        
        # File patterns to scan
        self.code_patterns = ["**/*.py", "**/*.js", "**/*.ts", "**/*.json", "**/*.yml", "**/*.yaml"]
        self.exclude_patterns = [
            "**/node_modules/**",
            "**/.git/**", 
            "**/venv/**",
            "**/__pycache__/**",
            "**/logs/**",
            "**/.claude/memory/**"
        ]
        
        logger.info(f"Security auditor initialized for {project_root}")
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        logger.info("Starting comprehensive security audit")
        
        # Clear previous findings
        self.findings.clear()
        self.compliance_checks.clear()
        
        # Run all audit checks
        self._audit_secrets_and_keys()
        self._audit_file_permissions()
        self._audit_dependencies()
        self._audit_configuration_security()
        self._audit_code_security()
        self._audit_container_security()
        self._run_compliance_checks()
        
        # Generate audit report
        report = self._generate_audit_report()
        
        logger.info(f"Security audit complete: {len(self.findings)} findings")
        return report
    
    def _audit_secrets_and_keys(self):
        """Audit for exposed secrets and API keys"""
        logger.debug("Auditing secrets and API keys")
        
        # Secret patterns to detect
        secret_patterns = [
            (r'sk-[a-zA-Z0-9]{48,}', "OpenAI API Key"),
            (r'sk-ant-[a-zA-Z0-9]{48,}', "Anthropic API Key"),
            (r'AIza[a-zA-Z0-9]{35,}', "Google API Key"),
            (r'aws_secret_access_key\s*=\s*["\'][^"\']{20,}["\']', "AWS Secret Key"),
            (r'github_token\s*=\s*["\'][^"\']{40}["\']', "GitHub Token"),
            (r'["\']password["\']\s*:\s*["\'][^"\']{8,}["\']', "Hardcoded Password"),
            (r'["\']secret["\']\s*:\s*["\'][^"\']{10,}["\']', "Hardcoded Secret"),
        ]
        
        for pattern_glob in self.code_patterns:
            for file_path in self.project_root.glob(pattern_glob):
                if self._should_exclude_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for line_num, line in enumerate(content.splitlines(), 1):
                        for pattern, secret_type in secret_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                self.findings.append(SecurityFinding(
                                    id=f"secret_{hashlib.md5(f'{file_path}:{line_num}'.encode()).hexdigest()[:8]}",
                                    severity="critical",
                                    category="secrets",
                                    title=f"Potential {secret_type} exposed",
                                    description=f"Detected potential {secret_type} in source code",
                                    file_path=str(file_path.relative_to(self.project_root)),
                                    line_number=line_num,
                                    recommendation="Move secrets to encrypted storage or environment variables",
                                    remediation_effort="medium"
                                ))
                                
                except Exception as e:
                    logger.debug(f"Could not scan file {file_path}: {e}")
        
        # Check for .env files in repository
        env_files = [".env", ".env.local", ".env.production", ".env.development"]
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                self.findings.append(SecurityFinding(
                    id=f"env_{env_file}",
                    severity="high",
                    category="secrets",
                    title=f"Environment file {env_file} in repository",
                    description="Environment files may contain secrets and should not be committed",
                    file_path=env_file,
                    recommendation="Add to .gitignore and use encrypted storage",
                    remediation_effort="low"
                ))
    
    def _audit_file_permissions(self):
        """Audit file permissions for security issues"""
        logger.debug("Auditing file permissions")
        
        sensitive_files = [
            ".claude/security/keys.enc",
            ".claude/security/master.key",
            "config/production.json",
            "docker-compose.yml",
            "pyproject.toml"
        ]
        
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    stat_info = os.stat(full_path)
                    file_mode = stat_info.st_mode & 0o777
                    
                    # Check for overly permissive permissions
                    if file_mode & 0o044:  # World/group readable
                        self.findings.append(SecurityFinding(
                            id=f"perm_{file_path.replace('/', '_')}",
                            severity="medium",
                            category="permissions",
                            title=f"Overly permissive file permissions: {file_path}",
                            description=f"File has permissions {oct(file_mode)}, should be more restrictive",
                            file_path=file_path,
                            recommendation="Set restrictive permissions (600 or 640)",
                            remediation_effort="low"
                        ))
                        
                except OSError as e:
                    logger.debug(f"Could not check permissions for {file_path}: {e}")
    
    def _audit_dependencies(self):
        """Audit Python dependencies for known vulnerabilities"""
        logger.debug("Auditing dependencies")
        
        requirements_files = ["requirements.txt", "requirements-dev.txt", "pyproject.toml"]
        
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    # Run safety check if available
                    result = subprocess.run(
                        ["python", "-m", "safety", "check", "-r", str(req_path)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode != 0 and "found" in result.stdout.lower():
                        self.findings.append(SecurityFinding(
                            id=f"deps_{req_file}",
                            severity="medium",
                            category="dependencies",
                            title="Vulnerable dependencies detected",
                            description="safety check found vulnerable packages",
                            file_path=req_file,
                            recommendation="Update vulnerable packages to secure versions",
                            remediation_effort="medium"
                        ))
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    # Safety not available or timeout
                    logger.debug("Safety check not available or timed out")
                    
        # Check for outdated dependencies
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                if len(outdated) > 10:  # More than 10 outdated packages
                    self.findings.append(SecurityFinding(
                        id="deps_outdated",
                        severity="low",
                        category="dependencies",
                        title=f"Many outdated dependencies ({len(outdated)})",
                        description="Large number of outdated packages may contain security issues",
                        recommendation="Regularly update dependencies and monitor for security advisories",
                        remediation_effort="medium"
                    ))
                    
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            logger.debug("Could not check for outdated dependencies")
    
    def _audit_configuration_security(self):
        """Audit configuration files for security issues"""
        logger.debug("Auditing configuration security")
        
        config_files = ["configs/default.json", "configs/production.json", ".claude/settings.local.json"]
        
        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Check for insecure configurations
                    self._check_insecure_config(config, config_file)
                    
                except (json.JSONDecodeError, OSError) as e:
                    logger.debug(f"Could not parse config {config_file}: {e}")
    
    def _check_insecure_config(self, config: Dict, file_path: str):
        """Check configuration for insecure settings"""
        insecure_patterns = [
            ("debug", True, "Debug mode enabled in configuration"),
            ("ssl_verify", False, "SSL verification disabled"),
            ("allow_insecure", True, "Insecure operations allowed"),
        ]
        
        def check_nested(obj, path=""):
            for key, value in obj.items() if isinstance(obj, dict) else []:
                current_path = f"{path}.{key}" if path else key
                
                # Check for insecure values
                for pattern_key, pattern_value, description in insecure_patterns:
                    if pattern_key in key.lower() and value == pattern_value:
                        self.findings.append(SecurityFinding(
                            id=f"config_{hashlib.md5(f'{file_path}:{current_path}'.encode()).hexdigest()[:8]}",
                            severity="medium",
                            category="configuration",
                            title=f"Insecure configuration: {current_path}",
                            description=description,
                            file_path=file_path,
                            recommendation="Review and secure configuration setting",
                            remediation_effort="low"
                        ))
                
                # Recurse into nested objects
                if isinstance(value, dict):
                    check_nested(value, current_path)
        
        check_nested(config)
    
    def _audit_code_security(self):
        """Audit code for security anti-patterns"""
        logger.debug("Auditing code security")
        
        # Security anti-patterns
        security_patterns = [
            (r'eval\s*\(', "Use of eval() function", "critical"),
            (r'exec\s*\(', "Use of exec() function", "high"),
            (r'shell=True', "Shell injection risk", "high"),
            (r'os\.system\s*\(', "OS command execution", "medium"),
            (r'subprocess\.run\([^)]*shell=True', "Subprocess with shell=True", "high"),
            (r'pickle\.loads?\s*\(', "Unsafe pickle usage", "high"),
            (r'yaml\.load\s*\([^)]*Loader=None', "Unsafe YAML loading", "medium"),
            (r'requests\..*verify=False', "SSL verification disabled", "medium"),
        ]
        
        for pattern_glob in ["**/*.py"]:
            for file_path in self.project_root.glob(pattern_glob):
                if self._should_exclude_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for line_num, line in enumerate(content.splitlines(), 1):
                        for pattern, title, severity in security_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                self.findings.append(SecurityFinding(
                                    id=f"code_{hashlib.md5(f'{file_path}:{line_num}'.encode()).hexdigest()[:8]}",
                                    severity=severity,
                                    category="code_security",
                                    title=title,
                                    description=f"Potentially unsafe code pattern detected: {pattern}",
                                    file_path=str(file_path.relative_to(self.project_root)),
                                    line_number=line_num,
                                    recommendation="Review code for security implications",
                                    remediation_effort="medium"
                                ))
                                
                except Exception as e:
                    logger.debug(f"Could not scan file {file_path}: {e}")
    
    def _audit_container_security(self):
        """Audit container configuration for security"""
        logger.debug("Auditing container security")
        
        docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]
        
        for docker_file in docker_files:
            docker_path = self.project_root / docker_file
            if docker_path.exists():
                try:
                    with open(docker_path, 'r') as f:
                        content = f.read()
                    
                    # Check for insecure Docker practices
                    insecure_patterns = [
                        (r'USER\s+root', "Running as root user", "high"),
                        (r'--privileged', "Privileged container", "critical"),
                        (r'--cap-add\s+ALL', "All capabilities added", "high"),
                        (r'network_mode:\s*host', "Host network mode", "medium"),
                        (r'security_opt:\s*none', "Security options disabled", "medium"),
                    ]
                    
                    for line_num, line in enumerate(content.splitlines(), 1):
                        for pattern, title, severity in insecure_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                self.findings.append(SecurityFinding(
                                    id=f"docker_{hashlib.md5(f'{docker_file}:{line_num}'.encode()).hexdigest()[:8]}",
                                    severity=severity,
                                    category="container_security",
                                    title=f"Docker security issue: {title}",
                                    description=f"Insecure Docker configuration detected",
                                    file_path=docker_file,
                                    line_number=line_num,
                                    recommendation="Follow Docker security best practices",
                                    remediation_effort="medium"
                                ))
                                
                except Exception as e:
                    logger.debug(f"Could not scan Docker file {docker_file}: {e}")
    
    def _run_compliance_checks(self):
        """Run compliance checks for security standards"""
        logger.debug("Running compliance checks")
        
        # OWASP Top 10 compliance
        self._check_owasp_compliance()
        
        # General security compliance
        self._check_general_compliance()
    
    def _check_owasp_compliance(self):
        """Check OWASP Top 10 compliance"""
        # A1: Injection
        has_input_validation = self._has_pattern(r'validate|sanitize|escape')
        self.compliance_checks.append(ComplianceCheck(
            standard="OWASP",
            requirement="A1: Injection Prevention",
            status="pass" if has_input_validation else "warning",
            description="Input validation and sanitization implementation",
            evidence=f"Found {len(self._find_pattern_matches(r'validate|sanitize|escape'))} validation patterns"
        ))
        
        # A2: Broken Authentication
        has_auth_security = self._has_pattern(r'authentication|authorize|login')
        self.compliance_checks.append(ComplianceCheck(
            standard="OWASP",
            requirement="A2: Authentication Security",
            status="pass" if has_auth_security else "not_applicable",
            description="Authentication security implementation",
            evidence=f"Found authentication patterns: {has_auth_security}"
        ))
        
        # A3: Sensitive Data Exposure
        uses_encryption = self._has_pattern(r'encrypt|crypto|secure')
        self.compliance_checks.append(ComplianceCheck(
            standard="OWASP",
            requirement="A3: Sensitive Data Protection",
            status="pass" if uses_encryption else "warning",
            description="Encryption and data protection implementation",
            evidence=f"Found encryption patterns: {uses_encryption}"
        ))
    
    def _check_general_compliance(self):
        """Check general security compliance"""
        # Logging and monitoring
        has_logging = any(finding.category == "logging" for finding in self.findings) or \
                      self._has_pattern(r'logger|log\.|logging')
        self.compliance_checks.append(ComplianceCheck(
            standard="General",
            requirement="Security Logging and Monitoring",
            status="pass" if has_logging else "warning",
            description="Security event logging implementation",
            evidence=f"Logging patterns found: {has_logging}"
        ))
        
        # Secrets management
        secrets_findings = [f for f in self.findings if f.category == "secrets"]
        self.compliance_checks.append(ComplianceCheck(
            standard="General", 
            requirement="Secrets Management",
            status="fail" if secrets_findings else "pass",
            description="Secure secrets and API key management",
            evidence=f"Found {len(secrets_findings)} secrets issues"
        ))
    
    def _has_pattern(self, pattern: str) -> bool:
        """Check if pattern exists in codebase"""
        for pattern_glob in self.code_patterns:
            for file_path in self.project_root.glob(pattern_glob):
                if self._should_exclude_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
                        
                except Exception:
                    continue
        
        return False
    
    def _find_pattern_matches(self, pattern: str) -> List[str]:
        """Find all matches of pattern in codebase"""
        matches = []
        
        for pattern_glob in self.code_patterns:
            for file_path in self.project_root.glob(pattern_glob):
                if self._should_exclude_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    file_matches = re.findall(pattern, content, re.IGNORECASE)
                    matches.extend(file_matches)
                    
                except Exception:
                    continue
        
        return matches
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning"""
        str_path = str(file_path)
        
        for exclude_pattern in self.exclude_patterns:
            if file_path.match(exclude_pattern):
                return True
        
        return False
    
    def _generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        # Categorize findings by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        category_counts = {}
        
        for finding in self.findings:
            severity_counts[finding.severity] += 1
            category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
        
        # Calculate security score
        score = 100
        score -= severity_counts["critical"] * 20
        score -= severity_counts["high"] * 10  
        score -= severity_counts["medium"] * 5
        score -= severity_counts["low"] * 1
        security_score = max(0, score)
        
        # Compliance summary
        compliance_summary = {}
        for check in self.compliance_checks:
            standard = check.standard
            if standard not in compliance_summary:
                compliance_summary[standard] = {"pass": 0, "fail": 0, "warning": 0, "not_applicable": 0}
            compliance_summary[standard][check.status] += 1
        
        return {
            "audit_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "summary": {
                "total_findings": len(self.findings),
                "security_score": security_score,
                "severity_breakdown": severity_counts,
                "category_breakdown": category_counts
            },
            "findings": [asdict(finding) for finding in self.findings],
            "compliance": {
                "summary": compliance_summary,
                "checks": [asdict(check) for check in self.compliance_checks]
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Critical issues first
        critical_findings = [f for f in self.findings if f.severity == "critical"]
        if critical_findings:
            recommendations.append({
                "priority": "immediate",
                "action": "Address critical security issues",
                "description": f"Fix {len(critical_findings)} critical security findings immediately",
                "effort": "varies"
            })
        
        # Secrets management
        secrets_findings = [f for f in self.findings if f.category == "secrets"]
        if secrets_findings:
            recommendations.append({
                "priority": "high",
                "action": "Implement secure secrets management",
                "description": "Move all secrets to encrypted storage and remove from source code",
                "effort": "medium"
            })
        
        # Dependency updates
        deps_findings = [f for f in self.findings if f.category == "dependencies"]
        if deps_findings:
            recommendations.append({
                "priority": "medium",
                "action": "Update vulnerable dependencies",
                "description": "Update packages with known vulnerabilities",
                "effort": "low"
            })
        
        return recommendations
    
    def export_report(self, output_path: Optional[Path] = None) -> Path:
        """Export audit report to file"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.project_root / f".claude/security/audit_report_{timestamp}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self._generate_audit_report()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Security audit report exported to {output_path}")
        return output_path


def run_security_audit(project_root: Path = Path(".")) -> Dict[str, Any]:
    """Run comprehensive security audit"""
    auditor = SecurityAuditor(project_root)
    return auditor.run_comprehensive_audit()