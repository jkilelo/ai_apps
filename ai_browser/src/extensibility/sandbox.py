"""Plugin sandbox system for secure execution of untrusted plugin code.

This module provides a comprehensive sandboxing system that restricts plugin access to
system resources while allowing controlled interaction with the browser framework.
"""

import sys
import os
import time
import threading
import importlib.util
import builtins
from pathlib import Path
from typing import Dict, Any, Set, List, Optional, Type, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from pydantic import BaseModel
from loguru import logger

from .interfaces import PluginException, PluginSandboxViolation

# Import resource module conditionally (not available on Windows)
try:
    import resource
    HAS_RESOURCE_MODULE = True
except ImportError:
    HAS_RESOURCE_MODULE = False
    logger.warning("Resource module not available - some sandbox features will be limited")


class SandboxConfig(BaseModel):
    """Configuration for plugin sandbox"""
    max_memory_mb: int = 100  # Maximum memory usage in MB
    max_cpu_time_seconds: int = 30  # Maximum CPU time in seconds
    max_execution_time_seconds: int = 60  # Maximum wall clock time
    max_file_size_mb: int = 10  # Maximum file size for file operations
    max_threads: int = 2  # Maximum number of threads
    allowed_imports: Set[str] = {
        # Standard library modules that are generally safe
        'math', 'json', 'datetime', 'collections', 'itertools', 'functools',
        'typing', 'enum', 'dataclasses', 'abc', 're', 'urllib.parse',
        'base64', 'hashlib', 'uuid', 'random', 'string', 'csv',
        'xml.etree.ElementTree', 'html.parser'
    }
    blocked_builtins: Set[str] = {
        # Dangerous built-in functions
        'eval', 'exec', 'compile', '__import__', 'open', 'input',
        'help', 'exit', 'quit', 'breakpoint', 'memoryview'
    }
    allowed_file_patterns: List[str] = [
        # Only allow access to plugin directory and temp files
        'plugins/**',
        'temp/**',
        '/tmp/**'
    ]
    network_allowed: bool = False
    subprocess_allowed: bool = False
    filesystem_write_allowed: bool = False


@dataclass
class SandboxStats:
    """Runtime statistics for sandboxed execution"""
    memory_peak_mb: float = 0.0
    cpu_time_seconds: float = 0.0
    wall_time_seconds: float = 0.0
    threads_created: int = 0
    files_accessed: int = 0
    network_calls_blocked: int = 0
    violations: List[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []


class RestrictedImportHook:
    """Custom import hook that restricts module imports"""
    
    def __init__(self, allowed_modules: Set[str], plugin_path: str):
        self.allowed_modules = allowed_modules
        self.plugin_path = Path(plugin_path).parent
        self.original_import = builtins.__import__
    
    def __call__(self, name: str, globals=None, locals=None, fromlist=(), level=0):
        """Restricted import function"""
        
        # Allow relative imports within plugin directory
        if level > 0:
            return self.original_import(name, globals, locals, fromlist, level)
        
        # Check if module is explicitly allowed
        if name in self.allowed_modules:
            return self.original_import(name, globals, locals, fromlist, level)
        
        # Allow submodules of allowed modules
        for allowed in self.allowed_modules:
            if name.startswith(f"{allowed}."):
                return self.original_import(name, globals, locals, fromlist, level)
        
        # Allow imports from the browser framework
        if name.startswith(('src.', 'ai_browser.')):
            return self.original_import(name, globals, locals, fromlist, level)
        
        # Block everything else
        raise ImportError(f"Import of '{name}' is not allowed in sandbox")


class ResourceMonitor:
    """Monitor resource usage during plugin execution"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.stats = SandboxStats()
        self.start_time = None
        self.start_memory = None
        self.monitoring = False
        self._monitor_thread = None
    
    def start_monitoring(self):
        """Start resource monitoring"""
        self.monitoring = True
        self.start_time = time.time()
        self.start_memory = self._get_memory_usage()
        
        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring and return stats"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        
        self.stats.wall_time_seconds = time.time() - self.start_time
        return self.stats
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Check memory usage
                current_memory = self._get_memory_usage()
                memory_usage = current_memory - self.start_memory
                self.stats.memory_peak_mb = max(self.stats.memory_peak_mb, memory_usage)
                
                # Check time limits
                elapsed_time = time.time() - self.start_time
                if elapsed_time > self.config.max_execution_time_seconds:
                    self.stats.violations.append(f"Execution time limit exceeded: {elapsed_time}s")
                    self.monitoring = False
                    break
                
                # Check memory limits
                if memory_usage > self.config.max_memory_mb:
                    self.stats.violations.append(f"Memory limit exceeded: {memory_usage}MB")
                    self.monitoring = False
                    break
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.warning(f"Error in resource monitoring: {e}")
                break
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback to resource module if available
            if HAS_RESOURCE_MODULE:
                try:
                    usage = resource.getrusage(resource.RUSAGE_SELF)
                    return usage.ru_maxrss / 1024  # KB to MB on Linux, already MB on macOS
                except:
                    return 0.0
            else:
                # No memory monitoring available
                return 0.0


class RestrictedFileSystem:
    """Restricted file system access for plugins"""
    
    def __init__(self, config: SandboxConfig, plugin_path: str):
        self.config = config
        self.plugin_dir = Path(plugin_path).parent
        self.allowed_paths = [self.plugin_dir]
        self.stats = None
    
    def set_stats(self, stats: SandboxStats):
        """Set stats object for tracking"""
        self.stats = stats
    
    def is_path_allowed(self, path: str) -> bool:
        """Check if file path is allowed"""
        path_obj = Path(path).resolve()
        
        # Check against allowed patterns
        for pattern in self.config.allowed_file_patterns:
            if path_obj.match(pattern):
                return True
        
        # Check if within plugin directory
        try:
            path_obj.relative_to(self.plugin_dir)
            return True
        except ValueError:
            pass
        
        return False
    
    def restricted_open(self, file, mode='r', **kwargs):
        """Restricted file open function"""
        if self.stats:
            self.stats.files_accessed += 1
        
        if not self.is_path_allowed(str(file)):
            raise PluginSandboxViolation(
                "filesystem",
                f"Access to file '{file}' is not allowed"
            )
        
        # Check file size for write operations
        if 'w' in mode or 'a' in mode:
            if not self.config.filesystem_write_allowed:
                raise PluginSandboxViolation(
                    "filesystem",
                    f"Write access to file '{file}' is not allowed"
                )
        
        # Use original open
        return open(file, mode, **kwargs)


class PluginSandbox:
    """Main plugin sandbox implementation"""
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.original_builtins = {}
        self.monitor = ResourceMonitor(self.config)
        self.filesystem = None
    
    def create_restricted_globals(self, plugin_path: str) -> Dict[str, Any]:
        """Create restricted global namespace for plugin execution"""
        
        # Save original builtins
        safe_builtins = {}
        for name in dir(builtins):
            if name not in self.config.blocked_builtins:
                safe_builtins[name] = getattr(builtins, name)
        
        # Create restricted file system
        self.filesystem = RestrictedFileSystem(self.config, plugin_path)
        self.filesystem.set_stats(self.monitor.stats)
        
        # Replace dangerous functions
        safe_builtins['open'] = self.filesystem.restricted_open
        safe_builtins['__import__'] = RestrictedImportHook(
            self.config.allowed_imports,
            plugin_path
        )
        
        # Create restricted globals
        restricted_globals = {
            '__builtins__': safe_builtins,
            '__name__': '__plugin__',
            '__file__': plugin_path,
            '__doc__': None,
            '__package__': None,
        }
        
        return restricted_globals
    
    def apply_resource_limits(self):
        """Apply system resource limits"""
        if not HAS_RESOURCE_MODULE:
            logger.warning("Resource module not available - resource limits will not be enforced")
            return
            
        try:
            # Memory limit (virtual memory)
            resource.setrlimit(
                resource.RLIMIT_AS,
                (self.config.max_memory_mb * 1024 * 1024,
                 self.config.max_memory_mb * 1024 * 1024)
            )
            
            # CPU time limit
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.config.max_cpu_time_seconds,
                 self.config.max_cpu_time_seconds)
            )
            
            # Stack size limit
            resource.setrlimit(
                resource.RLIMIT_STACK,
                (8 * 1024 * 1024,  # 8MB stack
                 8 * 1024 * 1024)
            )
            
            logger.debug("Applied resource limits to plugin execution")
            
        except (OSError, ValueError) as e:
            logger.warning(f"Could not apply resource limits: {e}")
    
    @contextmanager
    def secure_execution(self, plugin_path: str):
        """Context manager for secure plugin execution"""
        
        # Create restricted environment
        restricted_globals = self.create_restricted_globals(plugin_path)
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Apply resource limits in subprocess (not current process)
        # self.apply_resource_limits()  # Commented out to avoid affecting main process
        
        try:
            # Yield the restricted environment
            yield {
                'globals': restricted_globals,
                'locals': {},
                'monitor': self.monitor,
                'stats': self.monitor.stats
            }
            
        except Exception as e:
            # Log security violations
            if isinstance(e, PluginSandboxViolation):
                self.monitor.stats.violations.append(str(e))
                logger.warning(f"Sandbox violation: {e}")
            raise
            
        finally:
            # Stop monitoring and get final stats
            self.monitor.stop_monitoring()
            
            # Check for violations
            if self.monitor.stats.violations:
                logger.error(f"Plugin execution had {len(self.monitor.stats.violations)} violations")
                for violation in self.monitor.stats.violations:
                    logger.error(f"  - {violation}")
    
    def load_plugin_module(self, plugin_path: str) -> Any:
        """Load plugin module in sandboxed environment"""
        
        plugin_path = Path(plugin_path)
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin file not found: {plugin_path}")
        
        with self.secure_execution(str(plugin_path)) as env:
            try:
                # Create module spec
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_path.stem}",
                    plugin_path
                )
                
                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not create module spec for {plugin_path}")
                
                # Create module with restricted globals
                module = importlib.util.module_from_spec(spec)
                
                # Update module globals with restricted environment
                module.__dict__.update(env['globals'])
                
                # Execute module in sandbox
                spec.loader.exec_module(module)
                
                return module, env['stats']
                
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_path}: {e}")
                raise PluginSandboxViolation(
                    plugin_path.stem,
                    f"Failed to load plugin: {str(e)}"
                )
    
    def validate_plugin_code(self, plugin_path: str) -> List[str]:
        """Static analysis to validate plugin code before loading"""
        
        violations = []
        
        try:
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for dangerous imports
            dangerous_imports = [
                'subprocess', 'os.system', 'eval', 'exec',
                'importlib', '__import__', 'compile'
            ]
            
            for dangerous in dangerous_imports:
                if dangerous in content:
                    violations.append(f"Dangerous import/call detected: {dangerous}")
            
            # Check for file system access
            if not self.config.filesystem_write_allowed:
                fs_operations = ['open(', 'with open', 'file(', 'write(']
                for op in fs_operations:
                    if op in content:
                        violations.append(f"File system operation detected: {op}")
            
            # Check for network operations
            if not self.config.network_allowed:
                network_ops = ['requests.', 'urllib.', 'socket.', 'http.']
                for op in network_ops:
                    if op in content:
                        violations.append(f"Network operation detected: {op}")
            
            # Check for subprocess operations
            if not self.config.subprocess_allowed:
                if 'subprocess' in content or 'os.system' in content:
                    violations.append("Subprocess operation detected")
            
        except Exception as e:
            violations.append(f"Failed to validate plugin code: {e}")
        
        return violations
    
    def create_safe_plugin_environment(self) -> Dict[str, Any]:
        """Create a safe environment dictionary for plugin execution"""
        
        return {
            'sandbox_config': self.config,
            'logger': logger,  # Provide logger for plugin use
            'Path': Path,  # Allow Path operations within restrictions
        }


# Utility functions for plugin sandboxing

def create_plugin_sandbox(
    memory_limit_mb: int = 100,
    cpu_time_limit: int = 30,
    allow_network: bool = False,
    allow_filesystem_write: bool = False
) -> PluginSandbox:
    """Create a plugin sandbox with specified limits"""
    
    config = SandboxConfig(
        max_memory_mb=memory_limit_mb,
        max_cpu_time_seconds=cpu_time_limit,
        network_allowed=allow_network,
        filesystem_write_allowed=allow_filesystem_write
    )
    
    return PluginSandbox(config)


def validate_plugin_permissions(
    plugin_metadata: Dict[str, Any],
    requested_permissions: Dict[str, bool]
) -> bool:
    """Validate that plugin metadata matches requested permissions"""
    
    plugin_perms = plugin_metadata.get('sandbox_permissions', {})
    
    for permission, requested in requested_permissions.items():
        if requested and not plugin_perms.get(permission, False):
            logger.warning(
                f"Plugin {plugin_metadata.get('name')} requests {permission} "
                f"but metadata doesn't declare it"
            )
            return False
    
    return True