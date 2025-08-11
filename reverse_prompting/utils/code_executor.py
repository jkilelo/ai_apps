"""
Code Executor Utility

This module provides safe code execution capabilities for testing and
comparing generated code against original implementations.
"""

import asyncio
import subprocess
import tempfile
import os
import sys
import time
import signal
import shlex
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

from ..core.models import CodeArtifact, CodeLanguage, ExecutionStatus, EngineConfig


@dataclass
class ExecutionResult:
    """Result of code execution."""

    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    execution_time: float = 0.0
    memory_usage: Optional[int] = None
    error_message: Optional[str] = None

    @property
    def is_successful(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,
            "memory_usage": self.memory_usage,
            "error_message": self.error_message,
            "is_successful": self.is_successful,
        }


class SecuritySandbox:
    """Security sandbox for safe code execution."""

    RESTRICTED_IMPORTS = {
        "os",
        "subprocess",
        "sys",
        "shutil",
        "tempfile",
        "pathlib",
        "socket",
        "urllib",
        "requests",
        "http",
        "ftplib",
        "smtplib",
        "pickle",
        "marshal",
        "shelve",
        "dbm",
        "sqlite3",
        "__import__",
        "eval",
        "exec",
        "compile",
        "open",
    }

    RESTRICTED_BUILTINS = {
        "__import__",
        "eval",
        "exec",
        "compile",
        "open",
        "input",
        "raw_input",
        "file",
        "execfile",
        "reload",
        "vars",
        "locals",
        "globals",
    }

    @classmethod
    def is_code_safe(cls, code: str) -> tuple[bool, List[str]]:
        """Check if code is safe to execute."""
        violations = []

        # Check for restricted imports
        for restricted in cls.RESTRICTED_IMPORTS:
            if f"import {restricted}" in code or f"from {restricted}" in code:
                violations.append(f"Restricted import: {restricted}")

        # Check for restricted builtins
        for builtin in cls.RESTRICTED_BUILTINS:
            if builtin in code:
                violations.append(f"Restricted builtin: {builtin}")

        # Check for file operations
        file_operations = ["open(", "file(", "with open"]
        for op in file_operations:
            if op in code:
                violations.append(f"File operation detected: {op}")

        # Check for network operations
        network_patterns = ["socket.", "urllib.", "requests.", "http."]
        for pattern in network_patterns:
            if pattern in code:
                violations.append(f"Network operation detected: {pattern}")

        # Check for subprocess/system calls
        system_patterns = ["subprocess.", "os.system", "os.popen", "os.spawn"]
        for pattern in system_patterns:
            if pattern in code:
                violations.append(f"System call detected: {pattern}")

        return len(violations) == 0, violations


class CodeExecutor:
    """Safe code executor with multiple language support."""

    def __init__(self, config: EngineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sandbox = SecuritySandbox()

        # Execution timeouts and limits
        self.timeout = getattr(config, "execution_timeout", 30)  # 30 seconds default
        self.memory_limit = getattr(config, "memory_limit", 512)  # 512MB default
        self.enable_sandbox = getattr(config, "enable_sandbox", True)

        # Language-specific configurations
        self.interpreters = {
            CodeLanguage.PYTHON: self._get_python_interpreter(),
            CodeLanguage.JAVASCRIPT: self._get_node_interpreter(),
            CodeLanguage.TYPESCRIPT: self._get_ts_interpreter(),
            CodeLanguage.JAVA: self._get_java_compiler(),
            CodeLanguage.CSHARP: self._get_dotnet_compiler(),
            CodeLanguage.CPP: self._get_cpp_compiler(),
            CodeLanguage.RUST: self._get_rust_compiler(),
            CodeLanguage.GO: self._get_go_compiler(),
        }

    def _get_python_interpreter(self) -> Optional[str]:
        """Get Python interpreter path."""
        try:
            result = subprocess.run(
                [sys.executable, "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return sys.executable
        except Exception:
            pass

        # Try common Python executables
        for python_cmd in ["python3", "python"]:
            try:
                result = subprocess.run(
                    [python_cmd, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return python_cmd
            except Exception:
                continue

        return None

    def _get_node_interpreter(self) -> Optional[str]:
        """Get Node.js interpreter path."""
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "node"
        except Exception:
            pass
        return None

    def _get_ts_interpreter(self) -> Optional[str]:
        """Get TypeScript interpreter path."""
        try:
            result = subprocess.run(
                ["ts-node", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "ts-node"
        except Exception:
            pass
        return None

    def _get_java_compiler(self) -> Optional[str]:
        """Get Java compiler path."""
        try:
            result = subprocess.run(
                ["javac", "-version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "javac"
        except Exception:
            pass
        return None

    def _get_dotnet_compiler(self) -> Optional[str]:
        """Get .NET compiler path."""
        try:
            result = subprocess.run(
                ["dotnet", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "dotnet"
        except Exception:
            pass
        return None

    def _get_cpp_compiler(self) -> Optional[str]:
        """Get C++ compiler path."""
        for compiler in ["g++", "clang++", "cl"]:
            try:
                result = subprocess.run(
                    [compiler, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return compiler
            except Exception:
                continue
        return None

    def _get_rust_compiler(self) -> Optional[str]:
        """Get Rust compiler path."""
        try:
            result = subprocess.run(
                ["rustc", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "rustc"
        except Exception:
            pass
        return None

    def _get_go_compiler(self) -> Optional[str]:
        """Get Go compiler path."""
        try:
            result = subprocess.run(
                ["go", "version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "go"
        except Exception:
            pass
        return None

    async def execute(self, artifact: CodeArtifact) -> ExecutionResult:
        """Execute a code artifact safely."""
        start_time = time.time()

        try:
            # Check if language is supported
            if artifact.language not in self.interpreters:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    error_message=f"Language {artifact.language.value} not supported",
                )

            interpreter = self.interpreters[artifact.language]
            if not interpreter:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    error_message=f"No interpreter found for {artifact.language.value}",
                )

            # Security check
            if self.enable_sandbox and artifact.language == CodeLanguage.PYTHON:
                is_safe, violations = self.sandbox.is_code_safe(artifact.content)
                if not is_safe:
                    return ExecutionResult(
                        status=ExecutionStatus.SECURITY_VIOLATION,
                        error_message=f"Security violations: {', '.join(violations)}",
                    )

            # Execute based on language
            if artifact.language == CodeLanguage.PYTHON:
                result = await self._execute_python(artifact, interpreter)
            elif artifact.language == CodeLanguage.JAVASCRIPT:
                result = await self._execute_javascript(artifact, interpreter)
            elif artifact.language == CodeLanguage.TYPESCRIPT:
                result = await self._execute_typescript(artifact, interpreter)
            elif artifact.language == CodeLanguage.JAVA:
                result = await self._execute_java(artifact, interpreter)
            elif artifact.language == CodeLanguage.CSHARP:
                result = await self._execute_csharp(artifact, interpreter)
            elif artifact.language == CodeLanguage.CPP:
                result = await self._execute_cpp(artifact, interpreter)
            elif artifact.language == CodeLanguage.RUST:
                result = await self._execute_rust(artifact, interpreter)
            elif artifact.language == CodeLanguage.GO:
                result = await self._execute_go(artifact, interpreter)
            else:
                result = ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    error_message=f"Execution not implemented for {artifact.language.value}",
                )

            result.execution_time = time.time() - start_time
            return result

        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error_message=str(e),
                execution_time=time.time() - start_time,
            )

    async def _execute_python(
        self, artifact: CodeArtifact, interpreter: str
    ) -> ExecutionResult:
        """Execute Python code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name

        try:
            # Run the Python script
            process = await asyncio.create_subprocess_exec(
                interpreter,
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024 * 1024,  # 1MB output limit
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )

                status = (
                    ExecutionStatus.SUCCESS
                    if process.returncode == 0
                    else ExecutionStatus.RUNTIME_ERROR
                )

                return ExecutionResult(
                    status=status,
                    stdout=stdout.decode("utf-8", errors="ignore"),
                    stderr=stderr.decode("utf-8", errors="ignore"),
                    exit_code=process.returncode,
                )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {self.timeout} seconds",
                )

        finally:
            # Cleanup temporary file
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    async def _execute_javascript(
        self, artifact: CodeArtifact, interpreter: str
    ) -> ExecutionResult:
        """Execute JavaScript code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                interpreter,
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024 * 1024,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )

                status = (
                    ExecutionStatus.SUCCESS
                    if process.returncode == 0
                    else ExecutionStatus.RUNTIME_ERROR
                )

                return ExecutionResult(
                    status=status,
                    stdout=stdout.decode("utf-8", errors="ignore"),
                    stderr=stderr.decode("utf-8", errors="ignore"),
                    exit_code=process.returncode,
                )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {self.timeout} seconds",
                )

        finally:
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    async def _execute_typescript(
        self, artifact: CodeArtifact, interpreter: str
    ) -> ExecutionResult:
        """Execute TypeScript code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                interpreter,
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024 * 1024,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )

                status = (
                    ExecutionStatus.SUCCESS
                    if process.returncode == 0
                    else ExecutionStatus.RUNTIME_ERROR
                )

                return ExecutionResult(
                    status=status,
                    stdout=stdout.decode("utf-8", errors="ignore"),
                    stderr=stderr.decode("utf-8", errors="ignore"),
                    exit_code=process.returncode,
                )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {self.timeout} seconds",
                )

        finally:
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    async def _execute_java(
        self, artifact: CodeArtifact, compiler: str
    ) -> ExecutionResult:
        """Execute Java code."""
        # Create temporary directory for Java files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract class name from code
            class_name = self._extract_java_class_name(artifact.content)
            if not class_name:
                return ExecutionResult(
                    status=ExecutionStatus.COMPILATION_ERROR,
                    error_message="Could not find public class in Java code",
                )

            java_file = os.path.join(temp_dir, f"{class_name}.java")
            class_file = os.path.join(temp_dir, f"{class_name}.class")

            # Write Java source
            with open(java_file, "w") as f:
                f.write(artifact.content)

            try:
                # Compile
                compile_process = await asyncio.create_subprocess_exec(
                    compiler,
                    java_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=temp_dir,
                )

                compile_stdout, compile_stderr = await asyncio.wait_for(
                    compile_process.communicate(), timeout=self.timeout
                )

                if compile_process.returncode != 0:
                    return ExecutionResult(
                        status=ExecutionStatus.COMPILATION_ERROR,
                        stderr=compile_stderr.decode("utf-8", errors="ignore"),
                        exit_code=compile_process.returncode,
                    )

                # Execute
                run_process = await asyncio.create_subprocess_exec(
                    "java",
                    class_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=temp_dir,
                )

                run_stdout, run_stderr = await asyncio.wait_for(
                    run_process.communicate(), timeout=self.timeout
                )

                status = (
                    ExecutionStatus.SUCCESS
                    if run_process.returncode == 0
                    else ExecutionStatus.RUNTIME_ERROR
                )

                return ExecutionResult(
                    status=status,
                    stdout=run_stdout.decode("utf-8", errors="ignore"),
                    stderr=run_stderr.decode("utf-8", errors="ignore"),
                    exit_code=run_process.returncode,
                )

            except asyncio.TimeoutError:
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {self.timeout} seconds",
                )

    def _extract_java_class_name(self, code: str) -> Optional[str]:
        """Extract the public class name from Java code."""
        import re

        match = re.search(r"public\s+class\s+(\w+)", code)
        return match.group(1) if match else None

    async def _execute_csharp(
        self, artifact: CodeArtifact, compiler: str
    ) -> ExecutionResult:
        """Execute C# code."""
        # This is a simplified implementation
        # In practice, you'd want to create a proper project structure
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cs", delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name

        try:
            # For now, just try to compile (full execution would require more setup)
            process = await asyncio.create_subprocess_exec(
                compiler,
                "run",
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )

                status = (
                    ExecutionStatus.SUCCESS
                    if process.returncode == 0
                    else ExecutionStatus.RUNTIME_ERROR
                )

                return ExecutionResult(
                    status=status,
                    stdout=stdout.decode("utf-8", errors="ignore"),
                    stderr=stderr.decode("utf-8", errors="ignore"),
                    exit_code=process.returncode,
                )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {self.timeout} seconds",
                )

        finally:
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    async def _execute_cpp(
        self, artifact: CodeArtifact, compiler: str
    ) -> ExecutionResult:
        """Execute C++ code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name

        executable = temp_file.replace(".cpp", ".exe" if os.name == "nt" else "")

        try:
            # Compile
            compile_process = await asyncio.create_subprocess_exec(
                compiler,
                temp_file,
                "-o",
                executable,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            compile_stdout, compile_stderr = await asyncio.wait_for(
                compile_process.communicate(), timeout=self.timeout
            )

            if compile_process.returncode != 0:
                return ExecutionResult(
                    status=ExecutionStatus.COMPILATION_ERROR,
                    stderr=compile_stderr.decode("utf-8", errors="ignore"),
                    exit_code=compile_process.returncode,
                )

            # Execute
            run_process = await asyncio.create_subprocess_exec(
                executable,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                run_stdout, run_stderr = await asyncio.wait_for(
                    run_process.communicate(), timeout=self.timeout
                )

                status = (
                    ExecutionStatus.SUCCESS
                    if run_process.returncode == 0
                    else ExecutionStatus.RUNTIME_ERROR
                )

                return ExecutionResult(
                    status=status,
                    stdout=run_stdout.decode("utf-8", errors="ignore"),
                    stderr=run_stderr.decode("utf-8", errors="ignore"),
                    exit_code=run_process.returncode,
                )

            except asyncio.TimeoutError:
                run_process.kill()
                await run_process.wait()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {self.timeout} seconds",
                )

        finally:
            for file_path in [temp_file, executable]:
                try:
                    os.unlink(file_path)
                except Exception:
                    pass

    async def _execute_rust(
        self, artifact: CodeArtifact, compiler: str
    ) -> ExecutionResult:
        """Execute Rust code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name

        executable = temp_file.replace(".rs", ".exe" if os.name == "nt" else "")

        try:
            # Compile
            compile_process = await asyncio.create_subprocess_exec(
                compiler,
                temp_file,
                "-o",
                executable,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            compile_stdout, compile_stderr = await asyncio.wait_for(
                compile_process.communicate(), timeout=self.timeout
            )

            if compile_process.returncode != 0:
                return ExecutionResult(
                    status=ExecutionStatus.COMPILATION_ERROR,
                    stderr=compile_stderr.decode("utf-8", errors="ignore"),
                    exit_code=compile_process.returncode,
                )

            # Execute
            run_process = await asyncio.create_subprocess_exec(
                executable,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                run_stdout, run_stderr = await asyncio.wait_for(
                    run_process.communicate(), timeout=self.timeout
                )

                status = (
                    ExecutionStatus.SUCCESS
                    if run_process.returncode == 0
                    else ExecutionStatus.RUNTIME_ERROR
                )

                return ExecutionResult(
                    status=status,
                    stdout=run_stdout.decode("utf-8", errors="ignore"),
                    stderr=run_stderr.decode("utf-8", errors="ignore"),
                    exit_code=run_process.returncode,
                )

            except asyncio.TimeoutError:
                run_process.kill()
                await run_process.wait()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {self.timeout} seconds",
                )

        finally:
            for file_path in [temp_file, executable]:
                try:
                    os.unlink(file_path)
                except Exception:
                    pass

    async def _execute_go(
        self, artifact: CodeArtifact, compiler: str
    ) -> ExecutionResult:
        """Execute Go code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".go", delete=False) as f:
            f.write(artifact.content)
            temp_file = f.name

        try:
            # Go can run directly without explicit compilation
            process = await asyncio.create_subprocess_exec(
                compiler,
                "run",
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )

                status = (
                    ExecutionStatus.SUCCESS
                    if process.returncode == 0
                    else ExecutionStatus.RUNTIME_ERROR
                )

                return ExecutionResult(
                    status=status,
                    stdout=stdout.decode("utf-8", errors="ignore"),
                    stderr=stderr.decode("utf-8", errors="ignore"),
                    exit_code=process.returncode,
                )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {self.timeout} seconds",
                )

        finally:
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return [
            lang.value
            for lang, interpreter in self.interpreters.items()
            if interpreter is not None
        ]

    def is_language_supported(self, language: CodeLanguage) -> bool:
        """Check if a language is supported."""
        return language in self.interpreters and self.interpreters[language] is not None


# For easy importing
__all__ = ["CodeExecutor", "ExecutionResult", "SecuritySandbox"]
