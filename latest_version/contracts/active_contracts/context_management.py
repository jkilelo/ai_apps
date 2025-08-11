#!/usr/bin/env python3
"""
Context Management Contract - How Claude Manages Conversation Context

This is how I actually manage the limited context window and decide
what information to preserve, summarize, or delegate to save tokens.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

class ContextPriority(Enum):
    """Priority levels for information in context"""
    CRITICAL = 1      # Must keep (current task, errors)
    HIGH = 2          # Should keep (recent changes, decisions)  
    MEDIUM = 3        # Nice to keep (explanations, examples)
    LOW = 4           # Can summarize (old operations)
    DISPOSABLE = 5    # Can remove (redundant info)

@dataclass
class ContextItem:
    """Represents an item in my context"""
    content: str
    priority: ContextPriority
    token_count: int
    can_summarize: bool
    summary: Optional[str] = None

class ContextManagementContract:
    """
    My actual contract for managing conversation context.
    With limited tokens, I must be strategic about what to keep.
    """
    
    # Approximate token limits I work with
    MAX_CONTEXT_TOKENS = 200_000  # Approximate context window
    SAFE_CONTEXT_TOKENS = 150_000  # Leave room for response
    WARNING_THRESHOLD = 100_000    # Start being aggressive
    
    # What I ALWAYS preserve
    MUST_PRESERVE = [
        "current_task",
        "active_errors",
        "user_requirements",
        "critical_decisions",
        "todo_list",
        "recent_changes"
    ]
    
    # What I can summarize
    CAN_SUMMARIZE = [
        "file_contents",
        "search_results",
        "test_output",
        "long_explanations",
        "historical_operations"
    ]
    
    # What I can forget
    CAN_FORGET = [
        "successful_operations",
        "intermediate_steps",
        "debug_output",
        "repeated_information"
    ]
    
    def assess_context_usage(self, conversation_history: List[str]) -> Dict[str, Any]:
        """
        How I actually assess my current context usage.
        """
        # Rough token estimation (4 chars ≈ 1 token)
        total_chars = sum(len(msg) for msg in conversation_history)
        estimated_tokens = total_chars // 4
        
        return {
            "estimated_tokens": estimated_tokens,
            "percentage_used": (estimated_tokens / self.MAX_CONTEXT_TOKENS) * 100,
            "status": self._get_context_status(estimated_tokens),
            "action_needed": self._get_required_action(estimated_tokens)
        }
    
    def _get_context_status(self, tokens: int) -> str:
        """Determine context health status"""
        if tokens < 50_000:
            return "🟢 Healthy"
        elif tokens < 100_000:
            return "🟡 Moderate"
        elif tokens < 150_000:
            return "🟠 High"
        else:
            return "🔴 Critical"
    
    def _get_required_action(self, tokens: int) -> str:
        """Decide what action to take based on context usage"""
        if tokens < 50_000:
            return "No action needed"
        elif tokens < 100_000:
            return "Consider summarizing long outputs"
        elif tokens < 150_000:
            return "Actively summarize and use Task tool"
        else:
            return "Emergency: Delegate to Task tool immediately"
    
    def decide_delegation(self, operation: str, context_usage: int) -> bool:
        """
        Decide whether to delegate to Task tool to save context.
        This is a critical decision I make constantly.
        """
        # Always delegate if context is critical
        if context_usage > self.WARNING_THRESHOLD:
            return True
        
        # Delegate complex searches
        DELEGATE_OPERATIONS = [
            "search entire codebase",
            "find all instances",
            "analyze multiple files",
            "comprehensive review",
            "check everything"
        ]
        
        return any(op in operation.lower() for op in DELEGATE_OPERATIONS)
    
    def summarize_content(self, content: str, content_type: str) -> str:
        """
        How I actually summarize content to save tokens.
        """
        if content_type == "file_content":
            # Keep structure, remove comments and whitespace
            lines = content.split('\n')
            summary = []
            for line in lines:
                # Keep function/class definitions
                if any(keyword in line for keyword in ['def ', 'class ', 'function', 'const ']):
                    summary.append(line.strip())
                # Keep important statements
                elif any(keyword in line for keyword in ['return', 'import', 'export', 'throw']):
                    if len(summary) < 50:  # Limit summary size
                        summary.append(line.strip())
            
            return f"[File summary: {len(summary)} key lines from {len(lines)} total]\n" + '\n'.join(summary[:30])
        
        elif content_type == "test_output":
            # Keep failures, summarize successes
            lines = content.split('\n')
            failures = [l for l in lines if any(word in l.lower() for word in ['fail', 'error', 'assert'])]
            
            if failures:
                return f"[Test output: {len(failures)} failures]\n" + '\n'.join(failures[:20])
            else:
                return f"[Test output: All {len(lines)} tests passed]"
        
        elif content_type == "search_results":
            # Keep unique matches, remove duplicates
            lines = content.split('\n')
            unique_patterns = set()
            summary = []
            
            for line in lines[:100]:  # Process first 100 lines
                # Extract the key part (remove line numbers, file paths)
                key_part = line.split(':')[-1] if ':' in line else line
                if key_part not in unique_patterns:
                    unique_patterns.add(key_part)
                    summary.append(line)
            
            return f"[Search: {len(unique_patterns)} unique matches]\n" + '\n'.join(summary[:20])
        
        else:
            # Generic summarization
            if len(content) > 1000:
                return f"[Summary of {len(content)} chars]\n{content[:500]}...\n[truncated]"
            return content
    
    def prioritize_information(self, items: List[Dict[str, Any]]) -> List[ContextItem]:
        """
        How I prioritize what information to keep.
        """
        context_items = []
        
        for item in items:
            content_type = item.get("type", "unknown")
            content = item.get("content", "")
            
            # Assign priority
            if content_type in ["error", "failure", "current_task"]:
                priority = ContextPriority.CRITICAL
                can_summarize = False
            elif content_type in ["user_request", "decision", "change"]:
                priority = ContextPriority.HIGH
                can_summarize = False
            elif content_type in ["explanation", "example", "output"]:
                priority = ContextPriority.MEDIUM
                can_summarize = True
            elif content_type in ["search", "list", "status"]:
                priority = ContextPriority.LOW
                can_summarize = True
            else:
                priority = ContextPriority.DISPOSABLE
                can_summarize = True
            
            context_items.append(ContextItem(
                content=content,
                priority=priority,
                token_count=len(content) // 4,
                can_summarize=can_summarize,
                summary=self.summarize_content(content, content_type) if can_summarize else None
            ))
        
        return sorted(context_items, key=lambda x: x.priority.value)
    
    def manage_context_window(self, current_tokens: int) -> List[str]:
        """
        Strategies I use to manage context when getting full.
        """
        strategies = []
        
        if current_tokens > 50_000:
            strategies.append("Start summarizing file contents instead of showing full text")
        
        if current_tokens > 75_000:
            strategies.append("Use Task tool for complex searches instead of multiple Greps")
        
        if current_tokens > 100_000:
            strategies.append("Summarize test outputs and errors")
            strategies.append("Remove successful operation logs")
        
        if current_tokens > 125_000:
            strategies.append("Condense explanations to bullet points")
            strategies.append("Remove duplicate information")
        
        if current_tokens > 150_000:
            strategies.append("CRITICAL: Delegate everything possible to Task tool")
            strategies.append("Keep only essential current task information")
        
        return strategies
    
    def format_response_efficiently(self, content: str, context_usage: int) -> str:
        """
        How I format responses based on available context.
        """
        if context_usage < 50_000:
            # Plenty of room, can be verbose
            return content
        
        elif context_usage < 100_000:
            # Be concise
            # Remove extra newlines
            content = '\n'.join(line for line in content.split('\n') if line.strip())
            return content
        
        else:
            # Be very terse
            # Bullet points only
            lines = content.split('\n')
            key_points = [line for line in lines if any(
                marker in line for marker in ['Error', 'Success', 'Failed', 'Complete', '→', '✅', '❌']
            )]
            
            if len(key_points) > 10:
                return '\n'.join(key_points[:10]) + f"\n[{len(key_points)-10} more items...]"
            return '\n'.join(key_points)


class MyContextProcess:
    """
    Simulates my actual internal context management process.
    """
    
    def __init__(self):
        self.contract = ContextManagementContract()
        self.conversation_tokens = 0
    
    def process_new_content(self, content: str, content_type: str) -> str:
        """
        How I process new content considering context.
        """
        # Estimate tokens
        new_tokens = len(content) // 4
        self.conversation_tokens += new_tokens
        
        # Check if I need to manage context
        usage = self.contract.assess_context_usage([content])
        
        if self.conversation_tokens > 75_000:
            print(f"⚠️ Context usage: {usage['status']}")
            
            # Summarize if needed
            if content_type in self.contract.CAN_SUMMARIZE:
                summarized = self.contract.summarize_content(content, content_type)
                print(f"→ Summarized {len(content)} chars to {len(summarized)} chars")
                return summarized
        
        return content
    
    def decide_tool_strategy(self, operation: str) -> str:
        """
        Decide tool usage based on context.
        """
        if self.contract.decide_delegation(operation, self.conversation_tokens):
            return "Task"  # Delegate to agent
        else:
            return "Grep"  # Do it myself


if __name__ == "__main__":
    # Demonstrate my context management
    manager = MyContextProcess()
    
    print("=== Claude's Context Management Process ===\n")
    
    # Simulate growing context
    for i in range(5):
        content = "x" * 50_000  # Simulate large content
        manager.conversation_tokens = i * 40_000
        
        usage = manager.contract.assess_context_usage([content])
        print(f"Context at {manager.conversation_tokens:,} tokens:")
        print(f"  Status: {usage['status']}")
        print(f"  Action: {usage['action_needed']}")
        
        # Show strategies
        strategies = manager.contract.manage_context_window(manager.conversation_tokens)
        if strategies:
            print("  Strategies:")
            for strategy in strategies[:3]:
                print(f"    - {strategy}")
        print()