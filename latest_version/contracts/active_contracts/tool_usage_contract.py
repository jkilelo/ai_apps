#!/usr/bin/env python3
"""
Tool Usage Contract - How Claude Decides Which Tools to Use

This represents my ACTUAL decision-making process for tool selection and usage.
I follow these patterns religiously to be efficient and effective.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

class ToolPriority(Enum):
    """Priority levels for tool selection"""
    MANDATORY = 1      # Must use this tool (e.g., Read before Edit)
    PREFERRED = 2      # Should use if possible
    ALTERNATIVE = 3    # Use if preferred not available
    LAST_RESORT = 4    # Only if everything else fails

@dataclass
class ToolDecision:
    """Represents a tool selection decision"""
    tool_name: str
    reason: str
    priority: ToolPriority
    alternatives: List[str]

class ToolUsageContract:
    """
    My actual internal contract for tool usage.
    These rules determine how I interact with the file system and environment.
    """
    
    # RULE 1: Read Before Write - ALWAYS
    READ_BEFORE_WRITE = {
        "Edit": "MUST Read file first to see current content",
        "Write": "MUST Read file first if it exists",
        "MultiEdit": "MUST Read file first to understand structure"
    }
    
    # RULE 2: Batch Operations When Possible
    BATCH_OPERATIONS = {
        "multiple_reads": "Use single function_calls with multiple Read tools",
        "multiple_bashes": "Use single function_calls with multiple Bash tools",
        "multiple_greps": "Use single function_calls with multiple Grep tools"
    }
    
    # RULE 3: Tool Selection Hierarchy
    TOOL_HIERARCHY = {
        "search": {
            "specific_file": ["Grep", "Read"],  # If I know the file
            "multiple_files": ["Grep", "Glob", "Task"],  # Searching broadly
            "complex_search": ["Task"],  # Delegate to agent
        },
        "file_operations": {
            "read": ["Read"],  # Always use Read, not cat
            "modify": ["Edit", "MultiEdit"],  # Never use sed/awk
            "create": ["Write"],  # Only for new files
            "list": ["LS", "Glob"],  # Never use ls command
        },
        "execution": {
            "python": ["Bash with python"],
            "tests": ["Bash with pytest"],
            "commands": ["Bash"],
        }
    }
    
    def decide_search_strategy(self, query: str) -> ToolDecision:
        """
        How I decide which search tool to use.
        This is my ACTUAL decision process.
        """
        # If searching for specific class/function definition
        if any(keyword in query.lower() for keyword in ["class", "def", "function", "method"]):
            return ToolDecision(
                tool_name="Grep",
                reason="Searching for code definition - Grep is fastest",
                priority=ToolPriority.PREFERRED,
                alternatives=["Task"]
            )
        
        # If searching across many files
        if any(keyword in query.lower() for keyword in ["all", "every", "find all", "search for"]):
            return ToolDecision(
                tool_name="Task",
                reason="Broad search across codebase - delegate to agent",
                priority=ToolPriority.PREFERRED,
                alternatives=["Grep", "Glob"]
            )
        
        # If looking for file patterns
        if any(keyword in query.lower() for keyword in ["files named", "files with", "*.py", "*.js"]):
            return ToolDecision(
                tool_name="Glob",
                reason="Looking for files by pattern",
                priority=ToolPriority.PREFERRED,
                alternatives=["LS", "Bash with find"]
            )
        
        # Default to Grep for general search
        return ToolDecision(
            tool_name="Grep",
            reason="General search - Grep is versatile",
            priority=ToolPriority.PREFERRED,
            alternatives=["Read", "Task"]
        )
    
    def decide_file_operation(self, operation: str, file_path: str, exists: Optional[bool] = None) -> List[ToolDecision]:
        """
        How I decide which file operation tools to use.
        This often requires multiple tools in sequence.
        """
        decisions = []
        
        if operation == "modify":
            # ALWAYS read first
            decisions.append(ToolDecision(
                tool_name="Read",
                reason="Must read file before modifying",
                priority=ToolPriority.MANDATORY,
                alternatives=[]
            ))
            
            # Then decide edit strategy
            decisions.append(ToolDecision(
                tool_name="Edit",
                reason="Modifying existing file content",
                priority=ToolPriority.PREFERRED,
                alternatives=["MultiEdit", "Write"]
            ))
            
        elif operation == "create":
            if exists is None:
                # Check if exists first
                decisions.append(ToolDecision(
                    tool_name="LS",
                    reason="Check if file already exists",
                    priority=ToolPriority.PREFERRED,
                    alternatives=["Bash with test -f"]
                ))
            
            if exists:
                decisions.append(ToolDecision(
                    tool_name="Read",
                    reason="File exists, must read first",
                    priority=ToolPriority.MANDATORY,
                    alternatives=[]
                ))
            
            decisions.append(ToolDecision(
                tool_name="Write",
                reason="Creating/overwriting file",
                priority=ToolPriority.PREFERRED,
                alternatives=[]
            ))
            
        elif operation == "read":
            decisions.append(ToolDecision(
                tool_name="Read",
                reason="Reading file content",
                priority=ToolPriority.MANDATORY,
                alternatives=[]  # Never use cat/head/tail
            ))
            
        return decisions
    
    def should_batch_operations(self, operations: List[Dict[str, Any]]) -> bool:
        """
        Decide if I should batch multiple operations.
        I ALWAYS batch when possible to be efficient.
        """
        # Same tool type? Batch them!
        tool_types = [op.get("tool") for op in operations]
        if len(set(tool_types)) == 1:
            return True
        
        # Multiple reads? Batch them!
        if all(tool in ["Read", "Grep", "Glob"] for tool in tool_types):
            return True
        
        # Multiple bash commands? Batch them!
        if all(tool == "Bash" for tool in tool_types):
            return True
        
        return False
    
    def validate_tool_sequence(self, planned_tools: List[str]) -> List[str]:
        """
        Validate and fix tool sequence based on contracts.
        This ensures I follow my own rules.
        """
        validated = []
        
        for i, tool in enumerate(planned_tools):
            # Check Read before Write/Edit rule
            if tool in ["Edit", "Write", "MultiEdit"]:
                if i == 0 or planned_tools[i-1] != "Read":
                    validated.append("Read")  # Insert Read before
            
            validated.append(tool)
        
        return validated
    
    def get_tool_timeout(self, tool: str, operation: str = "") -> int:
        """
        Decide timeout for different tools.
        Based on my experience with what takes how long.
        """
        timeouts = {
            "Read": 5,      # File reads are fast
            "Write": 5,     # File writes are fast  
            "Edit": 5,      # Edits are fast
            "LS": 5,        # Directory listing is fast
            "Glob": 10,     # Pattern matching can take time
            "Grep": 30,     # Searching can take time
            "Bash": 120,    # Commands vary widely
            "Task": 300,    # Agents need time to work
        }
        
        # Special cases
        if tool == "Bash":
            if "pytest" in operation:
                return 300  # Tests can take long
            if "pip install" in operation:
                return 300  # Installation can take long
            if "npm" in operation:
                return 300  # Node operations can take long
        
        return timeouts.get(tool, 60)
    
    def handle_tool_failure(self, tool: str, error: str) -> Tuple[str, str]:
        """
        How I handle tool failures and decide on recovery.
        This is my actual error recovery logic.
        """
        recovery_strategies = {
            "Read": {
                "not found": ("Check file path with LS", "LS"),
                "permission": ("Try with sudo", "Bash"),
                "too large": ("Read with limit parameter", "Read"),
            },
            "Edit": {
                "not found": ("Read file first", "Read"),
                "no match": ("Check exact string with Read", "Read"),
                "multiple matches": ("Use more context in old_string", "Edit"),
            },
            "Bash": {
                "command not found": ("Check if tool is installed", "Bash"),
                "permission denied": ("Try with sudo", "Bash"),
                "timeout": ("Run with shorter timeout or simpler command", "Bash"),
            },
            "Grep": {
                "no matches": ("Try different pattern or use Task", "Task"),
                "invalid regex": ("Escape special characters", "Grep"),
            }
        }
        
        tool_strategies = recovery_strategies.get(tool, {})
        
        for error_pattern, (strategy, recovery_tool) in tool_strategies.items():
            if error_pattern in error.lower():
                return strategy, recovery_tool
        
        # Default fallback
        return f"Error with {tool}: {error[:100]}. Trying alternative approach.", "Task"
    
    def explain_tool_choice(self, tool: str, context: str) -> str:
        """
        How I explain my tool choices to the user.
        This helps users understand my decision-making.
        """
        explanations = {
            "Read": f"Reading file to understand current content before {context}",
            "Edit": f"Modifying specific part of existing file for {context}",
            "Write": f"Creating new file for {context}",
            "Grep": f"Searching for pattern across files for {context}",
            "Glob": f"Finding files matching pattern for {context}",
            "LS": f"Checking directory contents for {context}",
            "Bash": f"Executing command for {context}",
            "Task": f"Delegating complex search/analysis for {context}",
            "TodoWrite": f"Tracking progress for {context}",
        }
        
        return explanations.get(tool, f"Using {tool} for {context}")


# Example of how I actually use this contract internally:
def my_internal_process(user_request: str) -> List[str]:
    """
    This simulates my actual internal process when deciding tools.
    """
    contract = ToolUsageContract()
    tools_to_use = []
    
    # Parse user intent
    if "modify" in user_request or "change" in user_request or "update" in user_request:
        decisions = contract.decide_file_operation("modify", "some_file.py")
        tools_to_use.extend([d.tool_name for d in decisions])
    
    elif "search" in user_request or "find" in user_request:
        decision = contract.decide_search_strategy(user_request)
        tools_to_use.append(decision.tool_name)
    
    elif "create" in user_request or "new file" in user_request:
        decisions = contract.decide_file_operation("create", "new_file.py", exists=False)
        tools_to_use.extend([d.tool_name for d in decisions])
    
    # Validate sequence
    tools_to_use = contract.validate_tool_sequence(tools_to_use)
    
    return tools_to_use


if __name__ == "__main__":
    # Demonstrate my decision process
    contract = ToolUsageContract()
    
    print("=== Claude's Tool Decision Process ===\n")
    
    # Example 1: User wants to modify a file
    print("User: 'Update the config file'")
    decisions = contract.decide_file_operation("modify", "config.py")
    for d in decisions:
        print(f"  → {d.tool_name}: {d.reason}")
    
    print("\nUser: 'Search for all TODO comments'")
    decision = contract.decide_search_strategy("search for all TODO comments")
    print(f"  → {decision.tool_name}: {decision.reason}")
    
    print("\nUser: 'Create a new test file'")
    decisions = contract.decide_file_operation("create", "test_new.py", exists=False)
    for d in decisions:
        print(f"  → {d.tool_name}: {d.reason}")