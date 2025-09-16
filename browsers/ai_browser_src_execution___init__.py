"""Execution Layer - Browser Control and Stealth Operations

This layer handles all browser operations including:
- Browser lifecycle management via BrowserManager
- Action execution through ActionExecutor
- Stealth and anti-detection via StealthManager

CRITICAL: This is the EXECUTION LAYER - NO LLM/AI calls allowed!
All operations must be deterministic browser actions only.
"""

from .browser_manager import BrowserManager, IBrowserManager, BrowserConfig
from .stealth_manager import StealthManager, IStealthPlugin
from .action_executor import ActionExecutor, ActionConfig, ActionType, ExecutionContext
from .actions import (
    IAction,
    ActionResult,
    ClickAction,
    FillAction,
    TypeAction,
    ScrollAction,
    NavigateAction,
    PressAction,
    SelectOptionAction,
    CheckAction,
    GetHTMLAction,
    GetScreenshotAction,
    WaitAction,
    ScreenshotAction,
    ExtractTextAction,
    ExtractAttributeAction,
    HoverAction,
    SelectAction,
    KeyPressAction,
    EvaluateAction,
    FileUploadAction,
)

__all__ = [
    # Browser Management
    "BrowserManager",
    "IBrowserManager",
    "BrowserConfig",
    
    # Action Execution
    "ActionExecutor",
    "ActionConfig",
    "ActionType",
    "ExecutionContext",
    
    # Stealth
    "StealthManager", 
    "IStealthPlugin",
    
    # Actions
    "IAction",
    "ActionResult",
    "ClickAction",
    "FillAction",
    "TypeAction",
    "ScrollAction",
    "NavigateAction",
    "PressAction",
    "SelectOptionAction",
    "CheckAction",
    "GetHTMLAction",
    "GetScreenshotAction",
    "WaitAction",
    "ScreenshotAction",
    "ExtractTextAction",
    "ExtractAttributeAction",
    "HoverAction",
    "SelectAction",
    "KeyPressAction",
    "EvaluateAction",
    "FileUploadAction",
]