"""
CODER Agent - Autonomous Coding Intelligence Framework

A powerful coding agent that implements Claude's internal reasoning patterns
with CODER v3.1 methodology for autonomous software development.
"""

from .core.engine import CoderEngine
from .contracts.base import AgentRequest, AgentResponse

__version__ = "1.0.0"
__all__ = ["CoderEngine", "AgentRequest", "AgentResponse"]