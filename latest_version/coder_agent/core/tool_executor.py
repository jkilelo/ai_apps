#!/usr/bin/env python3
"""
Tool Executor - Implements Claude's actual tool usage patterns
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import subprocess
import structlog

from ..contracts.base import ToolCall, ToolResult, ToolType


logger = structlog.get_logger()


class ToolExecutor:
    """
    Implements my actual tool usage patterns and decision logic.
    Based on contracts/active_contracts/tool_usage_contract.py
    """
    
    # RULE 1: Read Before Write - ALWAYS
    READ_BEFORE_WRITE = {
        ToolType.EDIT: "MUST Read file first to see current content",
        ToolType.WRITE: "MUST Read file first if it exists"
    }
    
    # Tool timeouts based on experience
    TOOL_TIMEOUTS = {
        ToolType.READ: 5,
        ToolType.WRITE: 5,
        ToolType.EDIT: 5,
        ToolType.GREP: 30,
        ToolType.BASH: 120,
        ToolType.TEST: 300,
        ToolType.SEARCH: 60,
        ToolType.VALIDATE: 30
    }
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.execution_history: List[Dict[str, Any]] = []
        self.file_cache: Dict[str, str] = {}  # Cache for read files
        
    async def execute(self, call: ToolCall) -> ToolResult:
        """
        Execute a tool call following my internal patterns.
        """
        start_time = time.time()
        logger.info("Executing tool", tool=call.tool, params=call.parameters)
        
        # Pre-execution validation
        validation = await self._validate_tool_call(call)
        if not validation["valid"]:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=validation["error"],
                duration_ms=int((time.time() - start_time) * 1000),
                retries=0,
                tokens_used=0
            )
        
        # Execute with retry logic
        result = None
        retries = 0
        max_retries = call.max_retries if call.retry_on_failure else 0
        
        while retries <= max_retries:
            try:
                result = await self._execute_tool(call)
                if result.success or not call.retry_on_failure:
                    break
                    
                # Handle failure with recovery strategy
                recovery = await self._handle_tool_failure(call, result.error)
                if recovery["should_retry"]:
                    call = self._modify_call_for_retry(call, recovery)
                    retries += 1
                    await asyncio.sleep(min(2 ** retries, 10))  # Exponential backoff
                else:
                    break
                    
            except asyncio.TimeoutError:
                result = ToolResult(
                    tool=call.tool,
                    success=False,
                    output=None,
                    error=f"Tool execution timed out after {call.timeout}s",
                    duration_ms=call.timeout * 1000,
                    retries=retries,
                    tokens_used=0
                )
                break
            except Exception as e:
                logger.error("Tool execution failed", tool=call.tool, error=str(e))
                result = ToolResult(
                    tool=call.tool,
                    success=False,
                    output=None,
                    error=str(e),
                    duration_ms=int((time.time() - start_time) * 1000),
                    retries=retries,
                    tokens_used=0
                )
                break
        
        # Record execution history
        self.execution_history.append({
            "tool": call.tool,
            "success": result.success if result else False,
            "duration_ms": result.duration_ms if result else 0,
            "retries": retries
        })
        
        return result
    
    async def batch_execute(self, calls: List[ToolCall]) -> List[ToolResult]:
        """
        Execute multiple tool calls efficiently (batching when possible).
        """
        # Group by tool type for potential batching
        grouped = {}
        for call in calls:
            if call.tool not in grouped:
                grouped[call.tool] = []
            grouped[call.tool].append(call)
        
        results = []
        
        for tool_type, tool_calls in grouped.items():
            if tool_type in [ToolType.READ, ToolType.GREP] and len(tool_calls) > 1:
                # These can be batched
                batch_results = await self._execute_batch(tool_calls)
                results.extend(batch_results)
            else:
                # Execute sequentially
                for call in tool_calls:
                    result = await self.execute(call)
                    results.append(result)
        
        return results
    
    async def _validate_tool_call(self, call: ToolCall) -> Dict[str, Any]:
        """
        Validate tool call before execution.
        Implements my actual validation logic.
        """
        # Check Read before Write rule
        if call.tool in self.READ_BEFORE_WRITE:
            file_path = call.parameters.get("file_path", "")
            if file_path and file_path not in self.file_cache:
                # Need to read first
                if Path(file_path).exists():
                    return {
                        "valid": False,
                        "error": f"Must read {file_path} before {call.tool}"
                    }
        
        # Validate parameters
        required_params = self._get_required_params(call.tool)
        for param in required_params:
            if param not in call.parameters:
                return {
                    "valid": False,
                    "error": f"Missing required parameter: {param}"
                }
        
        return {"valid": True}
    
    async def _execute_tool(self, call: ToolCall) -> ToolResult:
        """
        Execute the actual tool based on type.
        """
        if call.tool == ToolType.READ:
            return await self._execute_read(call)
        elif call.tool == ToolType.WRITE:
            return await self._execute_write(call)
        elif call.tool == ToolType.EDIT:
            return await self._execute_edit(call)
        elif call.tool == ToolType.BASH:
            return await self._execute_bash(call)
        elif call.tool == ToolType.GREP:
            return await self._execute_grep(call)
        elif call.tool == ToolType.TEST:
            return await self._execute_test(call)
        elif call.tool == ToolType.SEARCH:
            return await self._execute_search(call)
        elif call.tool == ToolType.VALIDATE:
            return await self._execute_validate(call)
        elif call.tool == ToolType.CODE_GENERATE:
            return await self._execute_code_generate(call)
        else:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=f"Unknown tool type: {call.tool}",
                duration_ms=0,
                retries=0,
                tokens_used=0
            )
    
    async def _execute_read(self, call: ToolCall) -> ToolResult:
        """Execute file read operation."""
        start = time.time()
        file_path = Path(call.parameters["file_path"])
        
        try:
            if not file_path.exists():
                return ToolResult(
                    tool=call.tool,
                    success=False,
                    output=None,
                    error=f"File not found: {file_path}",
                    duration_ms=int((time.time() - start) * 1000),
                    retries=0,
                    tokens_used=0
                )
            
            content = file_path.read_text(encoding='utf-8')
            
            # Cache for future operations
            self.file_cache[str(file_path)] = content
            
            # Estimate tokens (rough: 4 chars = 1 token)
            tokens = len(content) // 4
            
            return ToolResult(
                tool=call.tool,
                success=True,
                output=content,
                error=None,
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=tokens
            )
            
        except Exception as e:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=0
            )
    
    async def _execute_write(self, call: ToolCall) -> ToolResult:
        """Execute file write operation."""
        start = time.time()
        file_path = Path(call.parameters["file_path"])
        content = call.parameters["content"]
        
        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            file_path.write_text(content, encoding='utf-8')
            
            # Update cache
            self.file_cache[str(file_path)] = content
            
            return ToolResult(
                tool=call.tool,
                success=True,
                output=f"Written {len(content)} chars to {file_path}",
                error=None,
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=len(content) // 4
            )
            
        except Exception as e:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=0
            )
    
    async def _execute_edit(self, call: ToolCall) -> ToolResult:
        """Execute file edit operation."""
        start = time.time()
        file_path = Path(call.parameters["file_path"])
        old_string = call.parameters["old_string"]
        new_string = call.parameters["new_string"]
        
        try:
            # Get content from cache or read
            if str(file_path) in self.file_cache:
                content = self.file_cache[str(file_path)]
            else:
                if not file_path.exists():
                    return ToolResult(
                        tool=call.tool,
                        success=False,
                        output=None,
                        error=f"File not found: {file_path}",
                        duration_ms=int((time.time() - start) * 1000),
                        retries=0,
                        tokens_used=0
                    )
                content = file_path.read_text(encoding='utf-8')
            
            # Check if old_string exists
            if old_string not in content:
                return ToolResult(
                    tool=call.tool,
                    success=False,
                    output=None,
                    error=f"String not found in file: {old_string[:50]}...",
                    duration_ms=int((time.time() - start) * 1000),
                    retries=0,
                    tokens_used=0
                )
            
            # Perform replacement
            new_content = content.replace(old_string, new_string, 1)
            
            # Write back
            file_path.write_text(new_content, encoding='utf-8')
            
            # Update cache
            self.file_cache[str(file_path)] = new_content
            
            return ToolResult(
                tool=call.tool,
                success=True,
                output=f"Edited {file_path}",
                error=None,
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=(len(old_string) + len(new_string)) // 4
            )
            
        except Exception as e:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=0
            )
    
    async def _execute_bash(self, call: ToolCall) -> ToolResult:
        """Execute bash command."""
        start = time.time()
        command = call.parameters["command"]
        timeout = call.timeout or self.TOOL_TIMEOUTS[ToolType.BASH]
        
        try:
            # Special handling for certain commands
            if "pytest" in command:
                timeout = max(timeout, 300)
            elif "pip install" in command or "npm" in command:
                timeout = max(timeout, 300)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            return ToolResult(
                tool=call.tool,
                success=success,
                output=output,
                error=None if success else f"Command failed with code {result.returncode}",
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=len(output) // 4
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=f"Command timed out after {timeout}s",
                duration_ms=timeout * 1000,
                retries=0,
                tokens_used=0
            )
        except Exception as e:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=0
            )
    
    async def _execute_grep(self, call: ToolCall) -> ToolResult:
        """Execute grep/search operation."""
        start = time.time()
        pattern = call.parameters["pattern"]
        path = call.parameters.get("path", ".")
        
        try:
            # Use ripgrep if available, fallback to grep
            command = f"rg '{pattern}' {path} 2>/dev/null || grep -r '{pattern}' {path}"
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=call.timeout or self.TOOL_TIMEOUTS[ToolType.GREP]
            )
            
            output = result.stdout
            matches = output.split('\n') if output else []
            
            return ToolResult(
                tool=call.tool,
                success=True,
                output=matches,
                error=None,
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=len(output) // 4
            )
            
        except Exception as e:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=0
            )
    
    async def _execute_test(self, call: ToolCall) -> ToolResult:
        """Execute test suite."""
        start = time.time()
        test_command = call.parameters.get("command", "pytest")
        
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=call.timeout or self.TOOL_TIMEOUTS[ToolType.TEST]
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            # Parse test results
            test_summary = self._parse_test_output(output)
            
            return ToolResult(
                tool=call.tool,
                success=success,
                output=test_summary,
                error=None if success else "Tests failed",
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=len(output) // 4
            )
            
        except Exception as e:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=0
            )
    
    async def _handle_tool_failure(self, call: ToolCall, error: str) -> Dict[str, Any]:
        """
        Determine recovery strategy for tool failure.
        Based on my actual error recovery patterns.
        """
        recovery_strategies = {
            "not found": {"should_retry": True, "strategy": "check_path"},
            "permission": {"should_retry": True, "strategy": "use_sudo"},
            "timeout": {"should_retry": True, "strategy": "increase_timeout"},
            "no match": {"should_retry": False, "strategy": "none"}
        }
        
        for pattern, strategy in recovery_strategies.items():
            if pattern in error.lower():
                return strategy
        
        return {"should_retry": False, "strategy": "none"}
    
    def _get_required_params(self, tool: ToolType) -> List[str]:
        """Get required parameters for a tool."""
        required = {
            ToolType.READ: ["file_path"],
            ToolType.WRITE: ["file_path", "content"],
            ToolType.EDIT: ["file_path", "old_string", "new_string"],
            ToolType.BASH: ["command"],
            ToolType.GREP: ["pattern"],
            ToolType.TEST: [],
            ToolType.SEARCH: ["query"],
            ToolType.VALIDATE: ["target"],
            ToolType.CODE_GENERATE: ["task_description"]
        }
        return required.get(tool, [])
    
    async def _execute_code_generate(self, call: ToolCall) -> ToolResult:
        """Execute code generation using real LLM."""
        start = time.time()
        
        try:
            # Import the code generator
            from .code_generator import CodeGenerator
            
            # Create code generator instance
            generator = CodeGenerator()
            
            # Extract parameters
            task_description = call.parameters.get("task_description", "")
            language = call.parameters.get("language", "python")
            follow_coder_v3 = call.parameters.get("follow_coder_v3", True)
            context = call.parameters.get("context")
            requirements = call.parameters.get("requirements", [])
            
            logger.info(f"Generating code with real LLM for: {task_description[:100]}...")
            
            # Generate code using real LLM
            result = await generator.generate_code(
                task_description=task_description,
                language=language,
                context=context,
                requirements=requirements,
                follow_coder_v3=follow_coder_v3
            )
            
            if result.success:
                # Format output
                output = {
                    "code": result.code,
                    "tests": result.tests,
                    "contracts": result.contracts,
                    "documentation": result.documentation,
                    "coder_v3_compliant": result.coder_v3_compliant
                }
                
                # If we have code, write it to a file
                if result.code:
                    # Determine file name from task
                    file_name = self._extract_file_name(task_description, language)
                    file_path = Path(file_name)
                    
                    # Write code to file
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(result.code, encoding='utf-8')
                    output["file_written"] = str(file_path)
                    
                    # Write tests if available
                    if result.tests:
                        test_file = file_path.parent / f"test_{file_path.name}"
                        test_file.write_text(result.tests, encoding='utf-8')
                        output["test_file_written"] = str(test_file)
                
                return ToolResult(
                    tool=call.tool,
                    success=True,
                    output=output,
                    error=None,
                    duration_ms=int((time.time() - start) * 1000),
                    retries=0,
                    tokens_used=result.tokens_used
                )
            else:
                return ToolResult(
                    tool=call.tool,
                    success=False,
                    output=None,
                    error=result.error_message,
                    duration_ms=int((time.time() - start) * 1000),
                    retries=0,
                    tokens_used=result.tokens_used
                )
                
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=0
            )
    
    def _extract_file_name(self, task_description: str, language: str) -> str:
        """Extract or generate appropriate file name from task."""
        # Simple extraction logic - can be enhanced
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "go": ".go",
            "rust": ".rs"
        }
        
        ext = extensions.get(language, ".txt")
        
        # Try to extract meaningful name from task
        words = task_description.lower().split()
        for word in ["function", "class", "module", "component", "service"]:
            if word in words:
                idx = words.index(word)
                if idx + 1 < len(words):
                    name = words[idx + 1].strip('.,!?"\'')
                    if name.isalnum():
                        return f"{name}{ext}"
        
        # Default name
        return f"generated_code{ext}"
    
    async def _execute_search(self, call: ToolCall) -> ToolResult:
        """Execute search operation."""
        # Implementation placeholder - integrate with actual search
        start = time.time()
        query = call.parameters.get("query", "")
        
        # For now, use grep as search
        grep_call = ToolCall(
            tool=ToolType.GREP,
            parameters={"pattern": query, "path": "."},
            timeout=call.timeout,
            retry_on_failure=call.retry_on_failure,
            max_retries=call.max_retries
        )
        
        return await self._execute_grep(grep_call)
    
    async def _execute_validate(self, call: ToolCall) -> ToolResult:
        """Execute validation operation."""
        start = time.time()
        target = call.parameters.get("target", "")
        
        try:
            # Run validation checks (linting, type checking, etc.)
            commands = []
            
            if Path("pyproject.toml").exists() or Path("setup.py").exists():
                commands.extend([
                    "python -m py_compile *.py 2>&1",
                    "python -m flake8 . 2>&1 || true",
                    "python -m mypy . 2>&1 || true"
                ])
            
            if Path("package.json").exists():
                commands.extend([
                    "npm run lint 2>&1 || true",
                    "npm run type-check 2>&1 || true"
                ])
            
            results = []
            for cmd in commands:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                results.append(f"Command: {cmd}\nOutput: {result.stdout}\n")
            
            return ToolResult(
                tool=call.tool,
                success=True,
                output="\n".join(results),
                error=None,
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=len("\n".join(results)) // 4
            )
            
        except Exception as e:
            return ToolResult(
                tool=call.tool,
                success=False,
                output=None,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
                retries=0,
                tokens_used=0
            )
    
    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse test output for summary."""
        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "raw_output": output[:1000]  # Keep first 1000 chars
        }
        
        # Parse pytest output
        if "passed" in output or "failed" in output:
            import re
            # Look for pytest summary line
            match = re.search(r'(\d+) passed', output)
            if match:
                summary["passed"] = int(match.group(1))
            match = re.search(r'(\d+) failed', output)
            if match:
                summary["failed"] = int(match.group(1))
            summary["total"] = summary["passed"] + summary["failed"]
        
        return summary
    
    def _modify_call_for_retry(self, call: ToolCall, recovery: Dict[str, Any]) -> ToolCall:
        """Modify tool call based on recovery strategy."""
        strategy = recovery.get("strategy", "none")
        
        if strategy == "increase_timeout":
            call.timeout = min(call.timeout * 2, 600)
        elif strategy == "check_path":
            # Could modify path parameter
            pass
        elif strategy == "use_sudo":
            if call.tool == ToolType.BASH:
                call.parameters["command"] = f"sudo {call.parameters.get('command', '')}"
        
        return call