#!/usr/bin/env python3
"""
Helper methods for the CODER Engine
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

from ..contracts.base import EnvironmentCheck


logger = structlog.get_logger()


class EngineHelpers:
    """Helper methods for CODER Engine pre-flight and validation checks"""
    
    @staticmethod
    async def check_virtual_environment() -> EnvironmentCheck:
        """Check if running in a virtual environment"""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        venv_path = os.environ.get('VIRTUAL_ENV')
        
        # Also check if we're using a venv Python binary
        if "venv" in sys.executable or "/home/papa/projects/ui_testing_framework/venv" in sys.executable:
            in_venv = True
            venv_path = venv_path or "/home/papa/projects/ui_testing_framework/venv"
        
        if in_venv or venv_path:
            return EnvironmentCheck(
                check_name="Virtual Environment",
                passed=True,
                message=f"Running in virtual environment: {venv_path or sys.executable}",
                severity="critical",
                details={"venv_path": venv_path or sys.executable}
            )
        else:
            return EnvironmentCheck(
                check_name="Virtual Environment",
                passed=False,
                message="Not running in a virtual environment. Please activate venv.",
                severity="critical",
                details={"python_path": sys.executable}
            )
    
    @staticmethod
    async def check_llm_connection() -> EnvironmentCheck:
        """Check LLM connectivity"""
        # Check for API keys in environment
        has_openai = bool(os.environ.get('OPENAI_API_KEY'))
        has_anthropic = bool(os.environ.get('ANTHROPIC_API_KEY'))
        has_local = os.path.exists('/usr/local/bin/ollama') or os.path.exists('C:\\Program Files\\Ollama\\ollama.exe')
        
        if has_openai or has_anthropic or has_local:
            providers = []
            if has_openai:
                providers.append("OpenAI")
            if has_anthropic:
                providers.append("Anthropic")
            if has_local:
                providers.append("Local (Ollama)")
            
            return EnvironmentCheck(
                check_name="LLM Connection",
                passed=True,
                message=f"LLM providers available: {', '.join(providers)}",
                severity="critical",
                details={"providers": providers}
            )
        else:
            return EnvironmentCheck(
                check_name="LLM Connection",
                passed=False,
                message="No LLM provider configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.",
                severity="critical",
                details={}
            )
    
    @staticmethod
    async def check_project_directory(project_path: str) -> EnvironmentCheck:
        """Check if project directory exists and is valid"""
        path = Path(project_path)
        
        if not path.exists():
            return EnvironmentCheck(
                check_name="Project Directory",
                passed=False,
                message=f"Project directory does not exist: {project_path}",
                severity="critical",
                details={"path": project_path}
            )
        
        if not path.is_dir():
            return EnvironmentCheck(
                check_name="Project Directory",
                passed=False,
                message=f"Path is not a directory: {project_path}",
                severity="critical",
                details={"path": project_path}
            )
        
        # Check for common project markers
        markers = ['.git', 'requirements.txt', 'package.json', 'Cargo.toml', 'go.mod']
        found_markers = [m for m in markers if (path / m).exists()]
        
        return EnvironmentCheck(
            check_name="Project Directory",
            passed=True,
            message=f"Valid project directory: {project_path}",
            severity="info",
            details={"path": project_path, "markers": found_markers}
        )
    
    @staticmethod
    async def check_required_tools() -> EnvironmentCheck:
        """Check if required tools are available"""
        # Use the actual Python we're running with
        python_cmd = sys.executable
        
        required_tools = {
            'git': 'git --version',
            'python': f'{python_cmd} --version',
            'pip': f'{python_cmd} -m pip --version'
        }
        
        missing_tools = []
        available_tools = []
        
        for tool, command in required_tools.items():
            try:
                result = subprocess.run(
                    command,
                    shell=True,  # Use shell for complex commands
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    available_tools.append(tool)
                else:
                    missing_tools.append(tool)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing_tools.append(tool)
        
        if missing_tools:
            return EnvironmentCheck(
                check_name="Required Tools",
                passed=False,
                message=f"Missing required tools: {', '.join(missing_tools)}",
                severity="critical",
                details={"missing": missing_tools, "available": available_tools}
            )
        else:
            return EnvironmentCheck(
                check_name="Required Tools",
                passed=True,
                message="All required tools are available",
                severity="info",
                details={"available": available_tools}
            )
    
    @staticmethod
    async def check_platform(target_platform: str) -> EnvironmentCheck:
        """Check platform compatibility"""
        current_platform = platform.system().lower()
        
        platform_map = {
            'darwin': 'mac',
            'linux': 'linux',
            'windows': 'windows'
        }
        
        normalized_platform = platform_map.get(current_platform, current_platform)
        
        if target_platform == "any" or target_platform == normalized_platform:
            return EnvironmentCheck(
                check_name="Platform Compatibility",
                passed=True,
                message=f"Platform matches target: {normalized_platform}",
                severity="info",
                details={"current": normalized_platform, "target": target_platform}
            )
        else:
            return EnvironmentCheck(
                check_name="Platform Compatibility",
                passed=False,
                message=f"Platform mismatch. Current: {normalized_platform}, Target: {target_platform}",
                severity="warning",
                details={"current": normalized_platform, "target": target_platform}
            )
    
    @staticmethod
    async def infer_intent(request: Any) -> Dict[str, Any]:
        """Infer the true intent behind a request"""
        task_lower = request.task.lower()
        
        intent = {
            "action": "unknown",
            "target": "unknown",
            "scope": "unknown"
        }
        
        # Determine action
        action_keywords = {
            "create": ["create", "add", "new", "implement"],
            "update": ["update", "modify", "change", "edit"],
            "fix": ["fix", "repair", "resolve", "debug"],
            "refactor": ["refactor", "improve", "optimize", "clean"],
            "test": ["test", "verify", "validate", "check"],
            "document": ["document", "explain", "describe"]
        }
        
        for action, keywords in action_keywords.items():
            if any(kw in task_lower for kw in keywords):
                intent["action"] = action
                break
        
        # Determine target
        if "function" in task_lower or "method" in task_lower:
            intent["target"] = "function"
        elif "class" in task_lower:
            intent["target"] = "class"
        elif "file" in task_lower:
            intent["target"] = "file"
        elif "test" in task_lower:
            intent["target"] = "tests"
        elif "bug" in task_lower or "error" in task_lower:
            intent["target"] = "bug"
        
        # Determine scope
        if "all" in task_lower or "entire" in task_lower or "whole" in task_lower:
            intent["scope"] = "global"
        elif "this" in task_lower or "specific" in task_lower:
            intent["scope"] = "local"
        else:
            intent["scope"] = "targeted"
        
        return intent
    
    @staticmethod
    async def assess_capabilities(request: Any) -> List[str]:
        """Assess what capabilities are needed for the request"""
        task_lower = request.task.lower()
        capabilities = []
        
        # File operations
        if any(word in task_lower for word in ["read", "analyze", "review"]):
            capabilities.append("read_files")
        if any(word in task_lower for word in ["write", "create", "generate"]):
            capabilities.append("write_files")
        if any(word in task_lower for word in ["edit", "modify", "update"]):
            capabilities.append("edit_files")
        
        # Code operations
        if any(word in task_lower for word in ["test", "verify", "validate"]):
            capabilities.append("run_tests")
        if any(word in task_lower for word in ["search", "find", "locate"]):
            capabilities.append("search_code")
        if any(word in task_lower for word in ["refactor", "optimize"]):
            capabilities.append("refactor_code")
        
        # Analysis operations
        if any(word in task_lower for word in ["analyze", "understand", "explain"]):
            capabilities.append("code_analysis")
        if any(word in task_lower for word in ["debug", "fix", "resolve"]):
            capabilities.append("debugging")
        
        return capabilities if capabilities else ["general_coding"]
    
    @staticmethod
    async def gather_additional_context(request: Any) -> Dict[str, Any]:
        """Gather additional context when confidence is low"""
        context = {
            "file_patterns": [],
            "key_terms": [],
            "related_files": []
        }
        
        # Extract file patterns from request
        import re
        file_pattern = re.compile(r'\b\w+\.\w+\b')
        matches = file_pattern.findall(request.task)
        if matches:
            context["file_patterns"] = matches
        
        # Extract key technical terms
        tech_terms = ["api", "database", "frontend", "backend", "ui", "cli", 
                     "service", "model", "controller", "view", "component"]
        found_terms = [term for term in tech_terms if term in request.task.lower()]
        context["key_terms"] = found_terms
        
        # Suggest related files based on task type
        if "test" in request.task.lower():
            context["related_files"].append("*test*.py")
            context["related_files"].append("test_*.py")
        if "config" in request.task.lower():
            context["related_files"].append("*config*")
            context["related_files"].append("settings.*")
        
        return context
    
    @staticmethod
    async def determine_tools_for_task(task: Any) -> List[Any]:
        """Determine which tools are needed for a task"""
        from ..contracts.base import ToolCall, ToolType
        
        tools = []
        content_lower = task.content.lower()
        
        # Check if this is a code generation task - USE REAL LLM
        code_keywords = [
            "implement", "create", "generate", "write code", 
            "function", "class", "module", "fix", "refactor"
        ]
        
        is_code_task = any(keyword in content_lower for keyword in code_keywords)
        
        if is_code_task:
            # For code generation tasks, we'll use a special CODE_GENERATE tool
            # that will internally use the real LLM client
            tools.append(ToolCall(
                tool=ToolType.CODE_GENERATE,
                parameters={
                    "task_description": task.content,
                    "language": "python",  # Default, can be extracted from context
                    "follow_coder_v3": True
                },
                timeout=60,
                retry_on_failure=True,
                max_retries=1,
                estimated_tokens=5000
            ))
            
            # Also add test generation
            tools.append(ToolCall(
                tool=ToolType.TEST,
                parameters={"command": "pytest"},
                timeout=300,
                retry_on_failure=True,
                max_retries=1
            ))
        
        # Determine other tools based on task content
        elif "read" in content_lower or "analyze" in content_lower:
            tools.append(ToolCall(
                tool=ToolType.READ,
                parameters={"file_path": ""},
                timeout=5,
                retry_on_failure=False,
                max_retries=0
            ))
        
        elif "search" in content_lower or "find" in content_lower:
            tools.append(ToolCall(
                tool=ToolType.SEARCH,
                parameters={"query": ""},
                timeout=30,
                retry_on_failure=True,
                max_retries=2
            ))
        
        elif "test" in content_lower or "verify" in content_lower:
            tools.append(ToolCall(
                tool=ToolType.TEST,
                parameters={"command": "pytest"},
                timeout=300,
                retry_on_failure=True,
                max_retries=1
            ))
        
        elif "validate" in content_lower or "check" in content_lower:
            tools.append(ToolCall(
                tool=ToolType.VALIDATE,
                parameters={"target": ""},
                timeout=30,
                retry_on_failure=False,
                max_retries=0
            ))
        
        # Default to bash if no specific tool identified
        if not tools:
            tools.append(ToolCall(
                tool=ToolType.BASH,
                parameters={"command": ""},
                timeout=120,
                retry_on_failure=True,
                max_retries=2
            ))
        
        return tools
    
    @staticmethod
    def group_tasks_by_type(tasks: List[Any]) -> Dict[str, List[Any]]:
        """Group tasks by their primary tool type"""
        grouped = {}
        
        for task in tasks:
            # Simplified grouping based on task content
            content_lower = task.content.lower()
            
            if "read" in content_lower or "analyze" in content_lower:
                tool_type = "read"
            elif "search" in content_lower or "find" in content_lower:
                tool_type = "search"
            elif "write" in content_lower or "create" in content_lower:
                tool_type = "write"
            elif "test" in content_lower:
                tool_type = "test"
            else:
                tool_type = "general"
            
            if tool_type not in grouped:
                grouped[tool_type] = []
            grouped[tool_type].append(task)
        
        return grouped
    
    @staticmethod
    async def attempt_recovery(task_result: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to recover from a failed task"""
        error = task_result.get("error", "")
        
        recovery = {
            "success": False,
            "strategy": "none"
        }
        
        # Common recovery strategies
        if "permission denied" in error.lower():
            # Try with elevated permissions
            recovery["strategy"] = "retry_with_sudo"
        elif "file not found" in error.lower():
            # Create missing file/directory
            recovery["strategy"] = "create_missing"
        elif "timeout" in error.lower():
            # Increase timeout and retry
            recovery["strategy"] = "increase_timeout"
        elif "syntax error" in error.lower():
            # Fix syntax and retry
            recovery["strategy"] = "fix_syntax"
        
        # Simplified recovery - would need actual implementation
        if recovery["strategy"] != "none":
            logger.info(f"Attempting recovery: {recovery['strategy']}")
            # In real implementation, would execute recovery strategy
            recovery["success"] = False  # Placeholder
        
        return recovery
    
    @staticmethod
    async def run_test_suite(execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run test suite on execution results"""
        test_results = {
            "all_passed": True,
            "failures": []
        }
        
        # Extract test commands from execution
        for result in execution_result.get("results", []):
            for tool_result in result.get("tool_results", []):
                if tool_result.get("tool") == "test":
                    if not tool_result.get("success"):
                        test_results["all_passed"] = False
                        test_results["failures"].append({
                            "test": tool_result.get("test_name", "unknown"),
                            "error": tool_result.get("error", "Test failed")
                        })
        
        return test_results
    
    @staticmethod
    async def check_code_quality(execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check code quality of execution results"""
        quality_check = {
            "issues": []
        }
        
        # Check for common quality issues
        for result in execution_result.get("results", []):
            for tool_result in result.get("tool_results", []):
                if tool_result.get("tool") in ["write", "edit"]:
                    # Would run actual linters here
                    # Placeholder for quality checks
                    pass
        
        return quality_check