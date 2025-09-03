"""
Core Executor Engine for Nexus Executor
High-performance async execution engine with advanced features
"""

import asyncio
import contextvars
import hashlib
import io
import json
import logging
import os
import psutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field

from .models import (
    CodeArtifact, ExecutionConfig, ExecutionRequest, ExecutionResult,
    ExecutionStatus, CodeLanguage, ExecutionMode, MetricType, ResourceType,
    PerformanceMetrics, CacheEntry, SecurityLevel
)
from .sandbox import NexusSandbox, SandboxFactory

logger = logging.getLogger(__name__)


# ============================================================================
# EXECUTION CONTEXT
# ============================================================================

# Context variables for tracking execution state
current_execution = contextvars.ContextVar('current_execution', default=None)
execution_metrics = contextvars.ContextVar('execution_metrics', default={})


# ============================================================================
# LANGUAGE EXECUTORS
# ============================================================================

class LanguageExecutor:
    """Base class for language-specific executors"""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.interpreters = {}
        self._detect_interpreters()
    
    def _detect_interpreters(self):
        """Detect available interpreters/compilers"""
        pass
    
    async def execute(self, artifact: CodeArtifact) -> ExecutionResult:
        """Execute code artifact"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if executor is available"""
        return bool(self.interpreters)


class PythonExecutor(LanguageExecutor):
    """Python-specific executor with advanced features"""
    
    def _detect_interpreters(self):
        """Detect Python interpreters"""
        for python_cmd in [sys.executable, 'python3', 'python', 'pypy3', 'pypy']:
            try:
                result = subprocess.run(
                    [python_cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.interpreters[python_cmd] = result.stdout.strip()
            except:
                continue
    
    async def execute(self, artifact: CodeArtifact) -> ExecutionResult:
        """Execute Python code with sandboxing"""
        request_id = artifact.id
        result = ExecutionResult(
            request_id=request_id,
            artifact_id=artifact.id,
            status=ExecutionStatus.PREPARING,
            started_at=datetime.now()
        )
        
        try:
            # Create sandbox
            sandbox = SandboxFactory.create(self.config.security)
            
            # SKIP VALIDATION FOR NONE LEVEL - SANDBOX MACHINE ONLY
            if self.config.security.level != SecurityLevel.NONE:
                # Validate code
                is_safe, violations = sandbox.validate_code(artifact.content, artifact.id)
                if not is_safe:
                    result.status = ExecutionStatus.SECURITY_VIOLATION
                    result.error_message = f"Security violations detected: {violations}"
                    return result
            
            # Choose execution method based on mode
            if self.config.mode == ExecutionMode.ISOLATED:
                return await self._execute_isolated(artifact, sandbox)
            elif self.config.mode == ExecutionMode.CONTAINERIZED:
                return await self._execute_containerized(artifact)
            else:
                return await self._execute_sandboxed(artifact, sandbox)
                
        except Exception as e:
            result.status = ExecutionStatus.ERROR
            result.error_message = str(e)
            result.error_traceback = traceback.format_exc()
        finally:
            result.completed_at = datetime.now()
            result.duration_ms = (result.completed_at - result.started_at).total_seconds() * 1000
        
        return result
    
    async def _execute_sandboxed(self, artifact: CodeArtifact, sandbox: NexusSandbox) -> ExecutionResult:
        """Execute in sandboxed environment"""
        result = ExecutionResult(
            request_id=artifact.id,
            artifact_id=artifact.id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now()
        )
        
        # Prepare namespace
        namespace = sandbox.create_restricted_namespace()
        
        # For NONE level, ensure __name__ == '__main__' works
        if self.config.security.level == SecurityLevel.NONE:
            namespace['__name__'] = '__main__'
        
        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Track resources
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()
        
        with sandbox.sandbox_context(self.config.resources.to_dict()):
            try:
                # Redirect output
                old_stdout, old_stderr = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = stdout_capture, stderr_capture
                
                # Execute code with timeout
                if self.config.resources.max_execution_time:
                    exec_task = asyncio.create_task(
                        asyncio.to_thread(exec, artifact.content, namespace, namespace)
                    )
                    await asyncio.wait_for(exec_task, timeout=self.config.resources.max_execution_time)
                else:
                    exec(artifact.content, namespace, namespace)
                
                # Check for test results in namespace
                if 'test_passed' in namespace:
                    result.status = ExecutionStatus.SUCCESS if namespace['test_passed'] else ExecutionStatus.FAILED
                elif 'result' in namespace:
                    result.return_value = namespace['result']
                    result.status = ExecutionStatus.SUCCESS
                else:
                    result.status = ExecutionStatus.SUCCESS
                    
            except asyncio.TimeoutError:
                result.status = ExecutionStatus.TIMEOUT
                result.error_message = f"Execution timed out after {self.config.resources.max_execution_time}s"
            except AssertionError as e:
                result.status = ExecutionStatus.FAILED
                result.error_message = str(e)
                result.error_traceback = traceback.format_exc()
            except Exception as e:
                result.status = ExecutionStatus.RUNTIME_ERROR
                result.error_message = str(e)
                result.error_traceback = traceback.format_exc()
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr
        
        # Capture output
        result.stdout = stdout_capture.getvalue()
        result.stderr = stderr_capture.getvalue()
        
        # Capture resource usage
        end_memory = process.memory_info().rss / 1024 / 1024
        end_cpu = process.cpu_percent()
        
        result.resource_usage[ResourceType.MEMORY] = end_memory - start_memory
        result.resource_usage[ResourceType.CPU] = (end_cpu + start_cpu) / 2
        
        result.completed_at = datetime.now()
        result.duration_ms = (result.completed_at - result.started_at).total_seconds() * 1000
        
        return result
    
    async def _execute_isolated(self, artifact: CodeArtifact, sandbox: NexusSandbox) -> ExecutionResult:
        """Execute in separate process"""
        result = ExecutionResult(
            request_id=artifact.id,
            artifact_id=artifact.id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now()
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name
        
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                self.interpreters.get(sys.executable, 'python3'),
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=self.config.resources.max_output_size_kb * 1024
            )
            
            # Execute with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.resources.max_execution_time
                )
                
                result.stdout = stdout.decode('utf-8', errors='ignore')
                result.stderr = stderr.decode('utf-8', errors='ignore')
                result.exit_code = process.returncode
                
                if process.returncode == 0:
                    result.status = ExecutionStatus.SUCCESS
                else:
                    result.status = ExecutionStatus.RUNTIME_ERROR
                    
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                result.status = ExecutionStatus.TIMEOUT
                result.error_message = f"Process timed out after {self.config.resources.max_execution_time}s"
                
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        result.completed_at = datetime.now()
        result.duration_ms = (result.completed_at - result.started_at).total_seconds() * 1000
        
        return result
    
    async def _execute_containerized(self, artifact: CodeArtifact) -> ExecutionResult:
        """Execute in Docker container"""
        # This would integrate with Docker SDK
        # For now, returning a placeholder
        return ExecutionResult(
            request_id=artifact.id,
            artifact_id=artifact.id,
            status=ExecutionStatus.ERROR,
            error_message="Containerized execution not yet implemented"
        )


class JavaScriptExecutor(LanguageExecutor):
    """JavaScript executor using Node.js"""
    
    def _detect_interpreters(self):
        """Detect Node.js"""
        for node_cmd in ['node', 'nodejs', 'deno', 'bun']:
            try:
                result = subprocess.run(
                    [node_cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.interpreters[node_cmd] = result.stdout.strip()
            except:
                continue
    
    async def execute(self, artifact: CodeArtifact) -> ExecutionResult:
        """Execute JavaScript code"""
        if not self.interpreters:
            return ExecutionResult(
                request_id=artifact.id,
                artifact_id=artifact.id,
                status=ExecutionStatus.ERROR,
                error_message="No JavaScript runtime found"
            )
        
        result = ExecutionResult(
            request_id=artifact.id,
            artifact_id=artifact.id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now()
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name
        
        try:
            runtime = list(self.interpreters.keys())[0]
            process = await asyncio.create_subprocess_exec(
                runtime,
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.resources.max_execution_time
            )
            
            result.stdout = stdout.decode('utf-8', errors='ignore')
            result.stderr = stderr.decode('utf-8', errors='ignore')
            result.exit_code = process.returncode
            result.status = ExecutionStatus.SUCCESS if process.returncode == 0 else ExecutionStatus.RUNTIME_ERROR
            
        except asyncio.TimeoutError:
            result.status = ExecutionStatus.TIMEOUT
            result.error_message = "Execution timed out"
        except Exception as e:
            result.status = ExecutionStatus.ERROR
            result.error_message = str(e)
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
            result.completed_at = datetime.now()
            result.duration_ms = (result.completed_at - result.started_at).total_seconds() * 1000
        
        return result


# ============================================================================
# MAIN EXECUTOR
# ============================================================================

class NexusExecutor:
    """Main execution engine with advanced features"""
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self.executors: Dict[CodeLanguage, LanguageExecutor] = {}
        self.cache: Dict[str, CacheEntry] = {}
        self.metrics = PerformanceMetrics()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.parallel_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.config.parallel_workers)
        
        # Initialize language executors
        self._initialize_executors()
        
        # Performance tracking
        self.execution_history: List[ExecutionResult] = []
        self.performance_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'avg_duration_ms': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _initialize_executors(self):
        """Initialize language-specific executors"""
        self.executors[CodeLanguage.PYTHON] = PythonExecutor(self.config)
        self.executors[CodeLanguage.JAVASCRIPT] = JavaScriptExecutor(self.config)
        # Add more executors as needed
    
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a code request"""
        self.performance_stats['total_executions'] += 1
        
        # Check cache
        if self.config.cache_results:
            cache_key = request.get_cache_key()
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if not entry.is_expired():
                    entry.touch()
                    self.performance_stats['cache_hits'] += 1
                    self.metrics.cache_hits += 1
                    logger.info(f"Cache hit for request {request.artifact.id}")
                    return entry.result
        
        self.performance_stats['cache_misses'] += 1
        self.metrics.cache_misses += 1
        
        # Set execution context
        current_execution.set(request)
        
        # Select executor
        language = request.artifact.language
        if language not in self.executors:
            return ExecutionResult(
                request_id=request.artifact.id,
                artifact_id=request.artifact.id,
                status=ExecutionStatus.ERROR,
                error_message=f"No executor available for {language.value}"
            )
        
        executor = self.executors[language]
        if not executor.is_available():
            return ExecutionResult(
                request_id=request.artifact.id,
                artifact_id=request.artifact.id,
                status=ExecutionStatus.ERROR,
                error_message=f"No runtime available for {language.value}"
            )
        
        # Execute based on mode
        if request.config.mode == ExecutionMode.PARALLEL:
            result = await self._execute_parallel(request, executor)
        elif request.config.mode == ExecutionMode.BATCH:
            result = await self._execute_batch(request, executor)
        else:
            result = await executor.execute(request.artifact)
        
        # Update statistics
        if result.is_success:
            self.performance_stats['successful_executions'] += 1
        else:
            self.performance_stats['failed_executions'] += 1
        
        # Update average duration
        self.execution_history.append(result)
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]  # Keep last 100
        
        avg_duration = sum(r.duration_ms for r in self.execution_history) / len(self.execution_history)
        self.performance_stats['avg_duration_ms'] = avg_duration
        
        # Cache result
        if self.config.cache_results and result.is_success:
            cache_key = request.get_cache_key()
            self.cache[cache_key] = CacheEntry(
                key=cache_key,
                result=result,
                size_bytes=len(result.stdout) + len(result.stderr)
            )
            self._cleanup_cache()
        
        return result
    
    async def _execute_parallel(self, request: ExecutionRequest, executor: LanguageExecutor) -> ExecutionResult:
        """Execute code in parallel (for batch operations)"""
        # This would split the code into parallelizable chunks
        # For now, just execute normally
        return await executor.execute(request.artifact)
    
    async def _execute_batch(self, request: ExecutionRequest, executor: LanguageExecutor) -> ExecutionResult:
        """Execute multiple code artifacts in batch"""
        # This would handle batch execution
        # For now, just execute normally
        return await executor.execute(request.artifact)
    
    def _cleanup_cache(self):
        """Clean up expired cache entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
        
        # Also limit cache size
        max_cache_size = 100
        if len(self.cache) > max_cache_size:
            # Remove least recently accessed
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].accessed_at
            )
            for key, _ in sorted_entries[:len(self.cache) - max_cache_size]:
                del self.cache[key]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            **self.performance_stats,
            'cache_size': len(self.cache),
            'available_languages': list(self.executors.keys()),
            'metrics': self.metrics.get_summary()
        }
    
    async def shutdown(self):
        """Clean shutdown"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        self.cache.clear()
        logger.info("Nexus Executor shut down successfully")


# ============================================================================
# EXECUTOR FACTORY
# ============================================================================

class ExecutorFactory:
    """Factory for creating executor instances"""
    
    _default_instance: Optional[NexusExecutor] = None
    
    @classmethod
    def create(cls, config: Optional[ExecutionConfig] = None) -> NexusExecutor:
        """Create new executor instance"""
        return NexusExecutor(config)
    
    @classmethod
    def get_default(cls) -> NexusExecutor:
        """Get default executor instance"""
        if cls._default_instance is None:
            cls._default_instance = NexusExecutor()
        return cls._default_instance
    
    @classmethod
    async def reset_default(cls):
        """Reset default instance"""
        if cls._default_instance:
            await cls._default_instance.shutdown()
            cls._default_instance = None