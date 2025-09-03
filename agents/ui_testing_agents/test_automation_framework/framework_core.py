"""
Core components for Workplace Agents SDK
Designed to work with limited LLM APIs like call_default_llm
"""

from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import asyncio
from datetime import datetime
import sys
import os

# Add parent directory to path to import call_default_llm
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# V2: LLM is MANDATORY - No fallbacks
from llm_client import call_default_llm

# Verify LLM connection on import
async def verify_llm_connection():
    """Verify LLM is available or halt the system"""
    try:
        response = await call_default_llm([{"role": "user", "content": "test"}])
        if not response:
            raise SystemExit("FATAL: LLM connection failed. Please configure API keys in .env file.")
    except Exception as e:
        raise SystemExit(f"FATAL: LLM is REQUIRED but not available: {e}\nPlease install llm.py and configure API keys.")


class AgentRole(Enum):
    """Predefined agent roles"""
    EXECUTOR = "executor"
    PLANNER = "planner"
    CRITIC = "critic"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    COORDINATOR = "coordinator"


@dataclass
class Tool:
    """Tool definition for agents"""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]
    returns: str = "string"
    
    def to_prompt_format(self) -> str:
        """Convert tool to prompt-friendly format"""
        params_str = ", ".join([f"{k}: {v}" for k, v in self.parameters.items()])
        return f"{self.name}({params_str}): {self.description} -> {self.returns}"


@dataclass
class Memory:
    """Agent memory management"""
    short_term: List[Dict[str, str]] = field(default_factory=list)
    long_term: Dict[str, Any] = field(default_factory=dict)
    working: Dict[str, Any] = field(default_factory=dict)
    max_short_term: int = 20
    
    def add_message(self, role: str, content: str):
        """Add message to short-term memory"""
        self.short_term.append({"role": role, "content": content})
        # Trim if exceeds max
        if len(self.short_term) > self.max_short_term:
            self.short_term = self.short_term[-self.max_short_term:]
    
    def get_context(self, last_n: int = 10) -> List[Dict[str, str]]:
        """Get recent context from memory"""
        return self.short_term[-last_n:] if self.short_term else []
    
    def store_long_term(self, key: str, value: Any):
        """Store in long-term memory"""
        self.long_term[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def recall_long_term(self, key: str) -> Any:
        """Recall from long-term memory"""
        return self.long_term.get(key, {}).get("value")


@dataclass
class AgentResponse:
    """Structured agent response"""
    content: str
    reasoning: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    final_answer: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


class BaseAgent:
    """Base agent implementation for workplace LLM"""
    
    def __init__(self,
                 name: str,
                 role: AgentRole = AgentRole.EXECUTOR,
                 system_prompt: Optional[str] = None,
                 tools: Optional[List[Tool]] = None,
                 memory_enabled: bool = True,
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None,
                 verbose: bool = False):
        """
        Initialize base agent
        
        Args:
            name: Agent identifier
            role: Agent role type
            system_prompt: Custom system prompt
            tools: List of available tools
            memory_enabled: Enable memory management
            temperature: LLM sampling temperature
            max_tokens: Maximum response tokens
            verbose: Enable verbose logging
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.tools = tools or []
        self.memory = Memory() if memory_enabled else None
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.verbose = verbose
        self.execution_history: List[AgentResponse] = []
    
    def _default_system_prompt(self) -> str:
        """Generate default system prompt based on role"""
        prompts = {
            AgentRole.EXECUTOR: "You are an execution agent. Complete tasks efficiently and accurately.",
            AgentRole.PLANNER: "You are a planning agent. Break down complex tasks into manageable steps.",
            AgentRole.CRITIC: "You are a critic agent. Evaluate solutions and provide constructive feedback.",
            AgentRole.RESEARCHER: "You are a research agent. Gather and analyze information thoroughly.",
            AgentRole.ANALYST: "You are an analyst agent. Analyze data and provide insights.",
            AgentRole.COORDINATOR: "You are a coordinator agent. Manage and delegate tasks effectively."
        }
        return prompts.get(self.role, "You are a helpful AI assistant.")
    
    async def think(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate reasoning about a task
        
        Args:
            task: Task description
            context: Additional context
            
        Returns:
            Agent's reasoning
        """
        messages = self._build_messages(task, context, include_tools=False)
        
        if self.verbose:
            print(f"[{self.name}] Thinking about: {task[:100]}...")
        
        response = await call_default_llm(
            messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        if self.memory:
            self.memory.add_message("assistant", response)
        
        return response
    
    async def act(self, task: str, max_steps: int = 5, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Execute task with ReAct-style loop
        
        Args:
            task: Task to execute
            max_steps: Maximum reasoning steps
            context: Additional context
            
        Returns:
            Structured agent response
        """
        response = AgentResponse(content="")
        
        if self.memory:
            self.memory.add_message("user", task)
        
        for step in range(max_steps):
            if self.verbose:
                print(f"[{self.name}] Step {step + 1}/{max_steps}")
            
            # Build messages with current context
            messages = self._build_messages(task, context, include_tools=True)
            
            # Add previous steps to context
            if response.reasoning:
                messages.append({
                    "role": "assistant",
                    "content": f"Previous reasoning:\n{response.reasoning}"
                })
            
            # Get LLM response
            try:
                llm_response = await call_default_llm(
                    messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                # Parse response
                parsed = self._parse_response(llm_response)
                
                # Update response
                response.content = llm_response
                response.reasoning = parsed.get("reasoning", llm_response)
                
                # Check for tool calls
                if parsed.get("tool_calls"):
                    for tool_call in parsed["tool_calls"]:
                        result = await self._execute_tool(tool_call)
                        response.tool_calls.append(tool_call)
                        response.observations.append(str(result))
                        
                        if self.memory:
                            self.memory.add_message(
                                "system",
                                f"Tool '{tool_call['name']}' returned: {result}"
                            )
                
                # Check for final answer
                if parsed.get("final_answer"):
                    response.final_answer = parsed["final_answer"]
                    response.success = True
                    break
                
                # Check if task is complete
                if self._is_task_complete(llm_response, task):
                    response.final_answer = parsed.get("answer", llm_response)
                    response.success = True
                    break
                    
            except Exception as e:
                response.success = False
                response.error = str(e)
                if self.verbose:
                    print(f"[{self.name}] Error: {e}")
                break
        
        # Store in history
        self.execution_history.append(response)
        
        return response
    
    def _build_messages(self, task: str, context: Optional[Dict[str, Any]] = None, 
                       include_tools: bool = True) -> List[Dict[str, str]]:
        """Build message list for LLM"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add memory context
        if self.memory:
            memory_context = self.memory.get_context(last_n=5)
            messages.extend(memory_context)
        
        # Add tools description
        if include_tools and self.tools:
            tools_prompt = self._format_tools_prompt()
            messages.append({
                "role": "system",
                "content": tools_prompt
            })
        
        # Add context if provided
        if context:
            context_str = json.dumps(context, indent=2)
            messages.append({
                "role": "system",
                "content": f"Context:\n{context_str}"
            })
        
        # Add current task
        messages.append({"role": "user", "content": task})
        
        return messages
    
    def _format_tools_prompt(self) -> str:
        """Format tools for prompt"""
        if not self.tools:
            return ""
        
        tools_desc = "Available tools:\n"
        for tool in self.tools:
            tools_desc += f"- {tool.to_prompt_format()}\n"
        
        tools_desc += "\nTo use a tool, format as: TOOL: tool_name(param1=value1, param2=value2)"
        tools_desc += "\nAfter tool execution, you'll receive the result as an observation."
        tools_desc += "\nWhen task is complete, start response with: FINAL ANSWER:"
        
        return tools_desc
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for structured elements"""
        parsed = {
            "reasoning": None,
            "tool_calls": [],
            "final_answer": None,
            "answer": None
        }
        
        # Extract reasoning (text before any tool calls)
        reasoning_match = re.search(r"^(.*?)(?:TOOL:|FINAL ANSWER:)", response, re.DOTALL)
        if reasoning_match:
            parsed["reasoning"] = reasoning_match.group(1).strip()
        
        # Extract tool calls
        tool_pattern = r"TOOL:\s*(\w+)\((.*?)\)"
        tool_matches = re.finditer(tool_pattern, response)
        for match in tool_matches:
            tool_name = match.group(1)
            params_str = match.group(2)
            
            # Parse parameters
            params = {}
            if params_str:
                # Simple parameter parsing (can be enhanced)
                param_pattern = r"(\w+)\s*=\s*([^,]+)"
                for param_match in re.finditer(param_pattern, params_str):
                    key = param_match.group(1)
                    value = param_match.group(2).strip().strip("'\"")
                    params[key] = value
            
            parsed["tool_calls"].append({
                "name": tool_name,
                "params": params
            })
        
        # Extract final answer
        final_answer_match = re.search(r"FINAL ANSWER:\s*(.*)", response, re.DOTALL)
        if final_answer_match:
            parsed["final_answer"] = final_answer_match.group(1).strip()
        
        # General answer extraction (fallback)
        if not parsed["final_answer"]:
            parsed["answer"] = response
        
        return parsed
    
    async def _execute_tool(self, tool_call: Dict[str, Any]) -> Any:
        """Execute a tool function"""
        tool_name = tool_call.get("name")
        params = tool_call.get("params", {})
        
        tool = next((t for t in self.tools if t.name == tool_name), None)
        
        if not tool:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            # Check if tool function is async
            if asyncio.iscoroutinefunction(tool.func):
                result = await tool.func(**params)
            else:
                result = tool.func(**params)
            
            if self.verbose:
                print(f"[{self.name}] Tool '{tool_name}' executed successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            if self.verbose:
                print(f"[{self.name}] {error_msg}")
            return error_msg
    
    def _is_task_complete(self, response: str, task: str) -> bool:
        """Check if task is complete"""
        completion_indicators = [
            "task is complete",
            "task completed",
            "final answer",
            "in conclusion",
            "to summarize",
            "the answer is",
            "therefore"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in completion_indicators)
    
    def reset_memory(self):
        """Reset agent memory"""
        if self.memory:
            self.memory = Memory()
        self.execution_history = []
    
    def get_history(self) -> List[AgentResponse]:
        """Get execution history"""
        return self.execution_history
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', role={self.role.value}, tools={len(self.tools)})"