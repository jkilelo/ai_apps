"""
Advanced Security Sandbox for Nexus Executor
Combines and enhances security features from all modules with cutting-edge techniques
"""

import ast
import contextlib
import io
import os
import re
import signal
import sys
import tempfile
import threading
try:
    import resource
except ImportError:
    # resource module not available on Windows
    resource = None
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib
import json
import logging
from dataclasses import dataclass, field

from .models import SecurityLevel, SecurityConfig, SecurityAuditLog

logger = logging.getLogger(__name__)


# ============================================================================
# SECURITY RULES ENGINE
# ============================================================================

class SecurityRules:
    """Comprehensive security rules database"""
    
    # Dangerous imports by category
    DANGEROUS_IMPORTS = {
        'system': ['os', 'sys', 'subprocess', 'shutil', 'platform'],
        'network': ['socket', 'urllib', 'requests', 'http', 'ftplib', 'smtplib', 'telnetlib'],
        'filesystem': ['pathlib', 'glob', 'tempfile', 'shutil'],
        'serialization': ['pickle', 'marshal', 'shelve', 'dill'],
        'database': ['sqlite3', 'psycopg2', 'pymongo', 'redis'],
        'execution': ['importlib', 'imp', 'runpy', 'code', 'codeop'],
        'introspection': ['inspect', 'dis', 'ast', 'types'],
        'threading': ['threading', 'multiprocessing', 'concurrent'],
        'ctypes': ['ctypes', 'cffi'],
    }
    
    # Dangerous builtins
    DANGEROUS_BUILTINS = {
        'eval', 'exec', 'compile', '__import__', 'open',
        'input', 'raw_input', 'file', 'execfile', 'reload',
        'vars', 'locals', 'globals', 'dir', 'getattr', 'setattr',
        'delattr', 'hasattr', 'memoryview', 'bytearray'
    }
    
    # Dangerous patterns (regex)
    DANGEROUS_PATTERNS = [
        r'__[a-z]+__',  # Dunder methods
        r'\.\_[a-z]+',  # Private attributes
        r'eval\s*\(',
        r'exec\s*\(',
        r'compile\s*\(',
        r'__import__\s*\(',
        r'open\s*\(',
        r'file\s*\(',
        r'input\s*\(',
        r'os\.',
        r'sys\.',
        r'subprocess\.',
        r'importlib\.',
        r'\\x[0-9a-f]{2}',  # Hex escapes
        r'\\[0-7]{3}',  # Octal escapes
        r'lambda\s*:.*exec',  # Lambda with exec
        r'type\s*\(.*\)\s*\(',  # Dynamic type creation
    ]
    
    # AST node types to check
    DANGEROUS_NODES = {
        ast.Import, ast.ImportFrom,
        ast.FunctionDef, ast.AsyncFunctionDef,
        ast.ClassDef, ast.Global, ast.Nonlocal
    }
    
    @classmethod
    def get_rules_for_level(cls, level: SecurityLevel) -> Dict[str, Any]:
        """Get security rules based on level"""
        if level == SecurityLevel.NONE:
            # ABSOLUTELY NO RESTRICTIONS - SANDBOX MACHINE ONLY
            return {
                'blocked_imports': [],  # Nothing blocked
                'blocked_builtins': [],  # Nothing blocked
                'blocked_patterns': [],  # No pattern checking
                'check_ast': False,  # No AST analysis
                'allow_network': True,  # Network allowed
                'allow_filesystem': True,  # Filesystem allowed
                'max_recursion': 100000,  # Very high limit
                'max_iterations': 10000000,  # Very high limit
                'allowed_imports': ['*'],  # Everything allowed
                'allowed_builtins': ['*'],  # Everything allowed
            }
        elif level == SecurityLevel.MINIMAL:
            return {
                'blocked_imports': cls.DANGEROUS_IMPORTS['execution'] + cls.DANGEROUS_IMPORTS['ctypes'],
                'blocked_builtins': {'eval', 'exec', 'compile', '__import__'},
                'blocked_patterns': cls.DANGEROUS_PATTERNS[:5],
                'check_ast': True,
                'allow_network': True,
                'allow_filesystem': True,
                'max_recursion': 5000,
                'max_iterations': 100000,
            }
        elif level == SecurityLevel.STANDARD:
            blocked = []
            for category in ['system', 'network', 'execution', 'ctypes', 'serialization']:
                blocked.extend(cls.DANGEROUS_IMPORTS[category])
            return {
                'blocked_imports': blocked,
                'blocked_builtins': cls.DANGEROUS_BUILTINS,
                'blocked_patterns': cls.DANGEROUS_PATTERNS,
                'check_ast': True,
                'allow_network': False,
                'allow_filesystem': False,
                'max_recursion': 1000,
                'max_iterations': 10000,
            }
        elif level == SecurityLevel.STRICT:
            # Block almost everything
            all_dangerous = []
            for imports in cls.DANGEROUS_IMPORTS.values():
                all_dangerous.extend(imports)
            return {
                'blocked_imports': all_dangerous,
                'blocked_builtins': cls.DANGEROUS_BUILTINS,
                'blocked_patterns': cls.DANGEROUS_PATTERNS,
                'check_ast': True,
                'allow_network': False,
                'allow_filesystem': False,
                'max_recursion': 100,
                'max_iterations': 1000,
                'allowed_imports': ['math', 'random', 'datetime', 'collections', 'itertools', 'functools'],
            }
        else:  # PARANOID
            return {
                'blocked_imports': ['*'],  # Block all imports
                'blocked_builtins': cls.DANGEROUS_BUILTINS | {'print', 'input', 'help'},
                'blocked_patterns': cls.DANGEROUS_PATTERNS + [r'.*'],  # Block everything suspicious
                'check_ast': True,
                'allow_network': False,
                'allow_filesystem': False,
                'max_recursion': 50,
                'max_iterations': 100,
                'allowed_imports': ['math'],  # Only math allowed
                'allowed_builtins': {
                    'True', 'False', 'None',
                    'int', 'float', 'str', 'bool',
                    'list', 'dict', 'tuple', 'set',
                    'len', 'range', 'enumerate',
                    'sum', 'min', 'max', 'abs'
                }
            }


# ============================================================================
# AST SECURITY ANALYZER
# ============================================================================

class ASTSecurityAnalyzer(ast.NodeVisitor):
    """Advanced AST-based security analyzer"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.violations = []
        self.imports = []
        self.function_calls = []
        self.suspicious_constructs = []
        self.complexity = 0
        self.max_depth = 0
        self.current_depth = 0
        
    def visit_Import(self, node: ast.Import):
        """Check import statements"""
        for alias in node.names:
            module = alias.name
            self.imports.append(module)
            if not self.config.is_import_allowed(module):
                self.violations.append({
                    'type': 'blocked_import',
                    'module': module,
                    'line': node.lineno,
                    'severity': 'high'
                })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check from...import statements"""
        module = node.module or ''
        self.imports.append(module)
        if not self.config.is_import_allowed(module):
            self.violations.append({
                'type': 'blocked_import_from',
                'module': module,
                'line': node.lineno,
                'severity': 'high'
            })
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        """Check function calls"""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            self.function_calls.append(func_name)
            
            # Check for dangerous functions
            if func_name in self.config.blocked_builtins:
                self.violations.append({
                    'type': 'blocked_function',
                    'function': func_name,
                    'line': node.lineno,
                    'severity': 'critical'
                })
        
        # Check for dynamic execution patterns
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id in ['os', 'sys', 'subprocess']:
                    self.violations.append({
                        'type': 'dangerous_module_access',
                        'module': node.func.value.id,
                        'attribute': node.func.attr,
                        'line': node.lineno,
                        'severity': 'critical'
                    })
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track function complexity"""
        self.complexity += 1
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        
        # Check for suspicious function names
        if node.name.startswith('_') or '__' in node.name:
            self.suspicious_constructs.append({
                'type': 'suspicious_function_name',
                'name': node.name,
                'line': node.lineno
            })
        
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_Lambda(self, node: ast.Lambda):
        """Check lambda functions"""
        self.complexity += 0.5
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        """Check attribute access"""
        if node.attr.startswith('_'):
            self.suspicious_constructs.append({
                'type': 'private_attribute_access',
                'attribute': node.attr,
                'line': node.lineno
            })
        self.generic_visit(node)
    
    def visit_Global(self, node: ast.Global):
        """Check global statements"""
        self.violations.append({
            'type': 'global_statement',
            'names': node.names,
            'line': node.lineno,
            'severity': 'medium'
        })
        self.generic_visit(node)
    
    def analyze(self, code: str) -> Tuple[bool, List[Dict], Dict[str, Any]]:
        """Analyze code and return results"""
        try:
            tree = ast.parse(code)
            self.visit(tree)
            
            analysis = {
                'imports': self.imports,
                'function_calls': self.function_calls,
                'complexity': self.complexity,
                'max_depth': self.max_depth,
                'suspicious_constructs': self.suspicious_constructs,
                'violations': self.violations
            }
            
            is_safe = len(self.violations) == 0
            return is_safe, self.violations, analysis
            
        except SyntaxError as e:
            return False, [{'type': 'syntax_error', 'error': str(e), 'severity': 'critical'}], {}


# ============================================================================
# ADVANCED SANDBOX
# ============================================================================

class NexusSandbox:
    """Advanced security sandbox with multiple isolation layers"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.rules = SecurityRules.get_rules_for_level(config.level)
        self.ast_analyzer = ASTSecurityAnalyzer(config)
        self.audit_logs: List[SecurityAuditLog] = []
        self.resource_limits_set = False
        
    def validate_code(self, code: str, artifact_id: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]]]:
        """Comprehensive code validation"""
        # COMPLETELY BYPASS ALL SECURITY FOR NONE LEVEL - SANDBOX MACHINE ONLY
        if self.config.level == SecurityLevel.NONE:
            # Log for audit but don't restrict anything
            self._log_audit(
                event_type='code_validation_bypassed',
                severity='INFO',
                description='Security validation bypassed (NONE level - sandbox mode)',
                artifact_id=artifact_id,
                metadata={'code_length': len(code)}
            )
            return True, []  # Always safe, no violations
        
        violations = []
        
        # Level 1: Pattern matching
        for pattern in self.rules.get('blocked_patterns', []):
            if re.search(pattern, code, re.IGNORECASE):
                violations.append({
                    'type': 'pattern_match',
                    'pattern': pattern,
                    'severity': 'high'
                })
        
        # Level 2: String-based checks
        for module in self.rules.get('blocked_imports', []):
            if f"import {module}" in code or f"from {module}" in code:
                violations.append({
                    'type': 'import_string',
                    'module': module,
                    'severity': 'high'
                })
        
        # Level 3: AST analysis
        if self.rules.get('check_ast', True):
            is_safe, ast_violations, analysis = self.ast_analyzer.analyze(code)
            violations.extend(ast_violations)
            
            # Check complexity
            if analysis.get('complexity', 0) > 50:
                violations.append({
                    'type': 'high_complexity',
                    'complexity': analysis['complexity'],
                    'severity': 'low'
                })
        
        # Level 4: Check for infinite loops
        if 'while True:' in code and 'break' not in code:
            violations.append({
                'type': 'infinite_loop',
                'severity': 'high'
            })
        
        # Log validation attempt
        self._log_audit(
            event_type='code_validation',
            severity='INFO' if len(violations) == 0 else 'WARNING',
            description=f"Code validation: {len(violations)} violations found",
            artifact_id=artifact_id,
            metadata={'violations': violations}
        )
        
        return len(violations) == 0, violations
    
    def create_restricted_namespace(self) -> Dict[str, Any]:
        """Create restricted execution namespace"""
        if self.config.level == SecurityLevel.NONE:
            # FULL UNRESTRICTED ACCESS - SANDBOX MACHINE ONLY
            import builtins
            return {
                '__builtins__': builtins.__dict__.copy(),  # All builtins available
                '__name__': '__main__',  # Allow __main__ execution
                '__doc__': None,
                '__package__': None,
                '__file__': '<sandbox>',
            }
        
        # Start with safe builtins
        safe_builtins = {
            'None': None,
            'True': True,
            'False': False,
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'bytes': bytes,
            'chr': chr,
            'dict': dict,
            'enumerate': enumerate,
            'filter': filter,
            'float': float,
            'format': format,
            'frozenset': frozenset,
            'int': int,
            'isinstance': isinstance,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'ord': ord,
            'pow': pow,
            'range': range,
            'reversed': reversed,
            'round': round,
            'set': set,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'type': type,
            'zip': zip,
        }
        
        # Add exceptions for error handling
        safe_builtins.update({
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'IndexError': IndexError,
            'AttributeError': AttributeError,
            'RuntimeError': RuntimeError,
            'StopIteration': StopIteration,
            'AssertionError': AssertionError,
        })
        
        # Conditionally add print based on level
        if self.config.level.value <= SecurityLevel.STANDARD.value:
            safe_builtins['print'] = self._safe_print
        
        # Remove blocked builtins
        for blocked in self.config.blocked_builtins:
            safe_builtins.pop(blocked, None)
        
        # Add only allowed builtins for PARANOID level
        if self.config.level == SecurityLevel.PARANOID:
            allowed = self.rules.get('allowed_builtins', set())
            safe_builtins = {k: v for k, v in safe_builtins.items() if k in allowed}
        
        return {
            '__builtins__': safe_builtins,
            '__name__': '__sandboxed__',
            '__doc__': None,
            '__package__': None,
        }
    
    def _safe_print(self, *args, **kwargs):
        """Safe print function with output limiting"""
        output = io.StringIO()
        print(*args, **kwargs, file=output)
        content = output.getvalue()
        
        # Limit output size
        max_size = 10000  # 10KB
        if len(content) > max_size:
            content = content[:max_size] + "\n... (output truncated)"
        
        sys.stdout.write(content)
        return None
    
    @contextlib.contextmanager
    def sandbox_context(self, resource_limits: Optional[Dict[str, Any]] = None):
        """Context manager for sandboxed execution"""
        # Store original values
        original_recursion = sys.getrecursionlimit()
        original_modules = sys.modules.copy()
        
        try:
            # Set recursion limit
            sys.setrecursionlimit(self.rules.get('max_recursion', 1000))
            
            # Set resource limits (Unix only)
            if resource and hasattr(resource, 'setrlimit') and resource_limits:
                self._set_resource_limits(resource_limits)
            
            # Set up signal handlers for timeout
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, self._timeout_handler)
            
            yield
            
        finally:
            # Restore original values
            sys.setrecursionlimit(original_recursion)
            
            # Clean up any modules that were imported
            for module in list(sys.modules.keys()):
                if module not in original_modules:
                    del sys.modules[module]
            
            # Reset signal handlers
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
    
    def _set_resource_limits(self, limits: Dict[str, Any]):
        """Set system resource limits (Unix only)"""
        if resource is None or not hasattr(resource, 'setrlimit'):
            return
        
        try:
            # Memory limit
            if 'memory_mb' in limits:
                memory_bytes = limits['memory_mb'] * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            
            # CPU time limit
            if 'cpu_seconds' in limits:
                resource.setrlimit(resource.RLIMIT_CPU, (limits['cpu_seconds'], limits['cpu_seconds']))
            
            # File descriptor limit
            if 'file_descriptors' in limits:
                resource.setrlimit(resource.RLIMIT_NOFILE, (limits['file_descriptors'], limits['file_descriptors']))
            
            # Process limit
            if 'processes' in limits:
                resource.setrlimit(resource.RLIMIT_NPROC, (limits['processes'], limits['processes']))
            
            self.resource_limits_set = True
            
        except Exception as e:
            logger.warning(f"Failed to set resource limits: {e}")
    
    def _timeout_handler(self, signum, frame):
        """Handle execution timeout"""
        raise TimeoutError("Code execution timed out")
    
    def _log_audit(self, event_type: str, severity: str, description: str, 
                   artifact_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Log security audit event"""
        from datetime import datetime
        
        log = SecurityAuditLog(
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            description=description,
            artifact_id=artifact_id,
            metadata=metadata or {}
        )
        self.audit_logs.append(log)
        
        if self.config.enable_audit_log:
            logger.log(
                logging.INFO if severity == 'INFO' else logging.WARNING,
                f"SECURITY AUDIT: {event_type} - {description}"
            )
    
    def get_audit_logs(self) -> List[SecurityAuditLog]:
        """Get audit logs"""
        return self.audit_logs.copy()
    
    def clear_audit_logs(self):
        """Clear audit logs"""
        self.audit_logs.clear()


# ============================================================================
# SANDBOX FACTORY
# ============================================================================

class SandboxFactory:
    """Factory for creating appropriate sandbox instances"""
    
    _instances: Dict[SecurityLevel, NexusSandbox] = {}
    
    @classmethod
    def create(cls, config: SecurityConfig) -> NexusSandbox:
        """Create or get cached sandbox instance"""
        if config.level not in cls._instances:
            cls._instances[config.level] = NexusSandbox(config)
        return cls._instances[config.level]
    
    @classmethod
    def create_temporary(cls, level: SecurityLevel = SecurityLevel.STANDARD) -> NexusSandbox:
        """Create temporary sandbox for one-off use"""
        config = SecurityConfig(level=level)
        return NexusSandbox(config)
    
    @classmethod
    def clear_cache(cls):
        """Clear cached sandbox instances"""
        cls._instances.clear()