#!/usr/bin/env python3
"""
Context Manager - Implements Claude's context window management patterns
Based on contracts/active_contracts/context_management.py
"""

import hashlib
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import structlog

from ..contracts.base import ContextWindow, ContextItem


logger = structlog.get_logger()


class ContextPriority(Enum):
    """Priority levels for information in context"""
    CRITICAL = 1      # Must keep (current task, errors)
    HIGH = 2          # Should keep (recent changes, decisions)  
    MEDIUM = 3        # Nice to keep (explanations, examples)
    LOW = 4           # Can summarize (old operations)
    DISPOSABLE = 5    # Can remove (redundant info)


class ContextManager:
    """
    Manages conversation context with intelligent compression and prioritization.
    Implements my actual context management strategies.
    """
    
    # Thresholds based on my experience
    MAX_CONTEXT_TOKENS = 200_000
    SAFE_CONTEXT_TOKENS = 150_000
    WARNING_THRESHOLD = 100_000
    CRITICAL_THRESHOLD = 175_000
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.window = ContextWindow(
            total_tokens=config.get("max_tokens", self.MAX_CONTEXT_TOKENS),
            used_tokens=0,
            reserved_tokens=config.get("reserved_tokens", 10_000)
        )
        
        self.items: List[ContextItem] = []
        self.compression_history: List[Dict[str, Any]] = []
        self.summarization_cache: Dict[str, str] = {}
        
    def add_item(
        self, 
        content: str, 
        content_type: str, 
        priority: int = 5
    ) -> bool:
        """
        Add item to context with priority management.
        """
        # Estimate tokens (rough: 4 chars = 1 token)
        tokens = len(content) // 4
        
        # Check if we need compression first
        if not self.window.can_add(tokens):
            logger.info("Context full, attempting compression")
            self.compress_context()
            
            # Check again after compression
            if not self.window.can_add(tokens):
                logger.warning("Cannot add item even after compression", 
                             tokens=tokens, available=self.window.available_tokens)
                return False
        
        # Determine if content can be summarized
        can_summarize = content_type in [
            "file_content", "search_results", "test_output", 
            "long_explanation", "historical_operation"
        ]
        
        # Create summary if needed and priority is low
        summary = None
        if can_summarize and priority > 3:
            summary = self._summarize_content(content, content_type)
        
        item = ContextItem(
            content=content,
            content_type=content_type,
            tokens=tokens,
            priority=priority,
            can_summarize=can_summarize,
            summary=summary
        )
        
        self.items.append(item)
        self.window.used_tokens += tokens
        
        # Log context status
        self._log_context_status()
        
        return True
    
    def compress_context(self) -> int:
        """
        Compress context using my actual strategies.
        Returns number of tokens freed.
        """
        initial_tokens = self.window.used_tokens
        
        # Strategy 1: Remove disposable items
        self._remove_disposable_items()
        
        # Strategy 2: Summarize low priority items
        if self.window.usage_percentage > 50:
            self._summarize_low_priority_items()
        
        # Strategy 3: Deduplicate content
        if self.window.usage_percentage > 60:
            self._deduplicate_content()
        
        # Strategy 4: Aggressive summarization
        if self.window.usage_percentage > 75:
            self._aggressive_summarization()
        
        # Strategy 5: Emergency mode - keep only critical
        if self.window.usage_percentage > 90:
            self._emergency_compression()
        
        tokens_freed = initial_tokens - self.window.used_tokens
        
        logger.info("Context compressed", 
                   tokens_freed=tokens_freed,
                   usage_before=f"{initial_tokens}/{self.window.total_tokens}",
                   usage_after=f"{self.window.used_tokens}/{self.window.total_tokens}")
        
        self.compression_history.append({
            "tokens_freed": tokens_freed,
            "strategy": self._get_compression_strategy(),
            "usage_percentage": self.window.usage_percentage
        })
        
        return tokens_freed
    
    def get_context_for_llm(self) -> str:
        """
        Get formatted context for LLM consumption.
        """
        # Sort by priority (critical first)
        sorted_items = sorted(self.items, key=lambda x: x.priority)
        
        context_parts = []
        remaining_tokens = self.window.available_tokens
        
        for item in sorted_items:
            # Use summary if available and we're low on tokens
            if item.summary and remaining_tokens < 50_000:
                content = item.summary
                tokens = len(content) // 4
            else:
                content = item.content
                tokens = item.tokens
            
            if tokens <= remaining_tokens:
                context_parts.append(f"[{item.content_type}]\n{content}")
                remaining_tokens -= tokens
            else:
                # Truncate if needed
                max_chars = remaining_tokens * 4
                if max_chars > 100:
                    truncated = content[:max_chars] + "\n[truncated]"
                    context_parts.append(f"[{item.content_type}]\n{truncated}")
                break
        
        return "\n\n".join(context_parts)
    
    def can_add_tokens(self, tokens: int) -> bool:
        """Check if we can add tokens to context."""
        return self.window.can_add(tokens)
    
    def get_usage_status(self) -> Dict[str, Any]:
        """Get current context usage status."""
        percentage = self.window.usage_percentage
        
        if percentage < 25:
            status = "🟢 Healthy"
            action = "No action needed"
        elif percentage < 50:
            status = "🟡 Moderate"
            action = "Monitor usage"
        elif percentage < 75:
            status = "🟠 High"
            action = "Start summarizing"
        elif percentage < 90:
            status = "🔴 Critical"
            action = "Aggressive compression"
        else:
            status = "⚠️ Emergency"
            action = "Delegate to sub-agents"
        
        return {
            "status": status,
            "percentage": percentage,
            "used_tokens": self.window.used_tokens,
            "available_tokens": self.window.available_tokens,
            "action": action,
            "items_count": len(self.items),
            "compression_count": len(self.compression_history)
        }
    
    # Private compression strategies
    
    def _remove_disposable_items(self):
        """Remove items marked as disposable."""
        before_count = len(self.items)
        # Keep only items with priority <= 4 (remove priority 5 - disposable)
        self.items = [item for item in self.items if item.priority <= 4]
        removed = before_count - len(self.items)
        
        if removed > 0:
            # Recalculate tokens
            self.window.used_tokens = sum(item.tokens for item in self.items)
            logger.debug(f"Removed {removed} disposable items")
        
        # If no items were removed and we're still over capacity, need more aggressive approach
        if removed == 0 and self.window.used_tokens >= self.window.total_tokens - self.window.reserved_tokens:
            # Remove lowest priority items
            if self.items:
                self.items = self.items[:-1]  # Remove last item
                self.window.used_tokens = sum(item.tokens for item in self.items)
    
    def _summarize_low_priority_items(self):
        """Replace low priority items with summaries."""
        for item in self.items:
            if item.priority >= 4 and item.can_summarize and not item.summary:
                item.summary = self._summarize_content(item.content, item.content_type)
                
                # Replace content with summary
                summary_tokens = len(item.summary) // 4
                if summary_tokens < item.tokens:
                    tokens_saved = item.tokens - summary_tokens
                    item.content = item.summary
                    item.tokens = summary_tokens
                    self.window.used_tokens -= tokens_saved
    
    def _deduplicate_content(self):
        """Remove duplicate or very similar content."""
        seen_hashes = set()
        unique_items = []
        
        for item in self.items:
            # Create content hash
            content_hash = hashlib.md5(item.content.encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_items.append(item)
        
        removed = len(self.items) - len(unique_items)
        if removed > 0:
            self.items = unique_items
            self.window.used_tokens = sum(item.tokens for item in self.items)
            logger.debug(f"Removed {removed} duplicate items")
    
    def _aggressive_summarization(self):
        """Aggressively summarize all medium priority items."""
        for item in self.items:
            if item.priority >= 3 and item.can_summarize:
                if not item.summary:
                    item.summary = self._summarize_content(item.content, item.content_type)
                
                # Force use summary
                summary_tokens = len(item.summary) // 4
                if summary_tokens < item.tokens:
                    tokens_saved = item.tokens - summary_tokens
                    item.content = item.summary
                    item.tokens = summary_tokens
                    self.window.used_tokens -= tokens_saved
    
    def _emergency_compression(self):
        """Emergency mode - keep only critical items."""
        critical_items = [item for item in self.items if item.priority <= 2]
        
        if len(critical_items) < len(self.items):
            removed = len(self.items) - len(critical_items)
            self.items = critical_items
            self.window.used_tokens = sum(item.tokens for item in self.items)
            logger.warning(f"Emergency compression: removed {removed} non-critical items")
    
    def _summarize_content(self, content: str, content_type: str) -> str:
        """
        Summarize content based on type.
        Implements my actual summarization strategies.
        """
        # Check cache first
        cache_key = hashlib.md5(f"{content_type}:{content[:100]}".encode()).hexdigest()
        if cache_key in self.summarization_cache:
            return self.summarization_cache[cache_key]
        
        summary = ""
        
        if content_type == "file_content":
            # Keep structure, remove comments and whitespace
            lines = content.split('\n')
            key_lines = []
            for line in lines:
                # Keep function/class definitions
                if any(keyword in line for keyword in ['def ', 'class ', 'function', 'const ']):
                    key_lines.append(line.strip())
                # Keep imports
                elif any(keyword in line for keyword in ['import', 'from', 'require']):
                    if len(key_lines) < 20:
                        key_lines.append(line.strip())
            
            summary = f"[File summary: {len(key_lines)} key lines from {len(lines)} total]\n"
            summary += '\n'.join(key_lines[:30])
            
        elif content_type == "test_output":
            # Keep failures, summarize successes
            lines = content.split('\n')
            failures = [l for l in lines if any(word in l.lower() 
                       for word in ['fail', 'error', 'assert'])]
            
            if failures:
                summary = f"[Test output: {len(failures)} failures]\n"
                summary += '\n'.join(failures[:20])
            else:
                summary = f"[Test output: All tests passed]"
        
        elif content_type == "search_results":
            # Keep unique matches
            lines = content.split('\n')[:100]
            unique_patterns = []
            seen = set()
            
            for line in lines:
                # Extract key part
                key_part = line.split(':')[-1] if ':' in line else line
                key_part = key_part.strip()
                
                if key_part and key_part not in seen:
                    seen.add(key_part)
                    unique_patterns.append(line)
            
            summary = f"[Search: {len(unique_patterns)} unique matches]\n"
            summary += '\n'.join(unique_patterns[:20])
        
        else:
            # Generic summarization
            if len(content) > 1000:
                summary = f"[Summary of {len(content)} chars]\n{content[:500]}...\n[truncated]"
            else:
                summary = content
        
        # Cache the summary
        self.summarization_cache[cache_key] = summary
        
        return summary
    
    def _get_compression_strategy(self) -> str:
        """Get current compression strategy based on usage."""
        percentage = self.window.usage_percentage
        
        if percentage < 50:
            return "light_cleanup"
        elif percentage < 60:
            return "summarization"
        elif percentage < 75:
            return "deduplication"
        elif percentage < 90:
            return "aggressive"
        else:
            return "emergency"
    
    def _log_context_status(self):
        """Log current context status for monitoring."""
        if self.window.usage_percentage > 75:
            status = self.get_usage_status()
            logger.warning("High context usage", **status)