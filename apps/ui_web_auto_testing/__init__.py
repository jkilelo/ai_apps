"""
Web Automation Testing Framework

A comprehensive 4-step framework for automated web testing.
"""

__version__ = "1.0.0"
__author__ = "Web Automation Team"

# Import main components
from .sdk import (
    WebAutomationSDK,
    WorkflowConfig,
    ExecutionConfig,
    TestType,
    WorkflowSession,
    StepResponse
)

# Import CLI for programmatic access
from .cli import cli as cli_main

__all__ = [
    "WebAutomationSDK",
    "WorkflowConfig", 
    "ExecutionConfig",
    "TestType",
    "WorkflowSession",
    "StepResponse",
    "cli_main"
]

# Package metadata
def get_version():
    """Get the current version of the package"""
    return __version__

def get_info():
    """Get package information"""
    return {
        "name": "Web Automation Testing Framework",
        "version": __version__,
        "author": __author__,
        "description": "A powerful 4-step framework for automated web testing",
        "features": [
            "Intelligent Element Extraction",
            "Smart Test Generation",
            "Parallel Test Execution",
            "Cross-Browser Testing",
            "Comprehensive Reporting",
            "CLI & SDK Interfaces"
        ]
    }