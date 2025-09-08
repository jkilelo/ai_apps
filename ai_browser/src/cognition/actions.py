"""Structured action models for agent execution"""

from typing import Literal, Union, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ActionType(str, Enum):
    """Types of actions the agent can perform"""
    CLICK = "click"
    TYPE = "type"
    FILL = "fill"
    SCROLL = "scroll"
    NAVIGATE = "navigate"
    SELECT = "select"
    WAIT = "wait"
    READ_TEXT = "read_text"
    PRESS_KEY = "press_key"
    HOVER = "hover"
    DRAG = "drag"
    SCREENSHOT = "screenshot"
    FINISHED = "finished"
    FAILED = "failed"


class BaseAction(BaseModel):
    """Base class for all actions"""
    justification: str = Field(
        ...,
        description="Brief reasoning for why this action helps achieve the goal"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this action (0-1)"
    )


class ClickAction(BaseAction):
    """Action to click an interactive element on the page"""
    action: Literal["click"] = "click"
    element_id: int = Field(
        ...,
        description="The numerical ID from the annotated screenshot of the element to click"
    )
    click_type: Literal["left", "right", "middle", "double"] = Field(
        default="left",
        description="Type of click to perform"
    )
    modifiers: List[Literal["Alt", "Control", "Meta", "Shift"]] = Field(
        default_factory=list,
        description="Keyboard modifiers to hold during click"
    )


class TypeAction(BaseAction):
    """Action to type text with human-like delay"""
    action: Literal["type"] = "type"
    element_id: int = Field(
        ...,
        description="The numerical ID of the input field to type into"
    )
    text_to_type: str = Field(
        ...,
        description="The exact text to be typed"
    )
    clear_first: bool = Field(
        default=False,
        description="Whether to clear the field before typing"
    )
    delay_ms: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Delay between keystrokes in milliseconds"
    )


class FillAction(BaseAction):
    """Action to instantly fill an input field"""
    action: Literal["fill"] = "fill"
    element_id: int = Field(
        ...,
        description="The numerical ID of the input field to fill"
    )
    text: str = Field(
        ...,
        description="The text to fill into the field"
    )
    clear_first: bool = Field(
        default=True,
        description="Whether to clear the field before filling"
    )


class ScrollAction(BaseAction):
    """Action to scroll the webpage"""
    action: Literal["scroll"] = "scroll"
    direction: Literal["up", "down", "left", "right"] = Field(
        ...,
        description="The direction to scroll the page"
    )
    amount: int = Field(
        default=500,
        ge=100,
        le=5000,
        description="Amount to scroll in pixels"
    )
    smooth: bool = Field(
        default=True,
        description="Whether to use smooth scrolling"
    )
    element_id: Optional[int] = Field(
        None,
        description="Optional element to scroll into view"
    )


class NavigateAction(BaseAction):
    """Action to navigate to a specific URL"""
    action: Literal["navigate"] = "navigate"
    url: str = Field(
        ...,
        description="The full URL to navigate to"
    )
    wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = Field(
        default="networkidle",
        description="When to consider navigation complete"
    )


class SelectAction(BaseAction):
    """Action to select an option from a dropdown"""
    action: Literal["select"] = "select"
    element_id: int = Field(
        ...,
        description="The numerical ID of the select element"
    )
    option_text: Optional[str] = Field(
        None,
        description="Text of the option to select"
    )
    option_value: Optional[str] = Field(
        None,
        description="Value of the option to select"
    )
    option_index: Optional[int] = Field(
        None,
        description="Index of the option to select (0-based)"
    )


class WaitAction(BaseAction):
    """Action to wait for a condition or timeout"""
    action: Literal["wait"] = "wait"
    wait_type: Literal["time", "element", "condition"] = Field(
        default="time",
        description="Type of wait to perform"
    )
    duration_ms: Optional[int] = Field(
        None,
        ge=100,
        le=30000,
        description="Duration to wait in milliseconds (for time wait)"
    )
    element_id: Optional[int] = Field(
        None,
        description="Element to wait for (for element wait)"
    )
    element_state: Optional[Literal["visible", "hidden", "enabled", "disabled"]] = Field(
        None,
        description="State to wait for the element to reach"
    )
    condition: Optional[str] = Field(
        None,
        description="JavaScript condition to wait for (for condition wait)"
    )


class ReadTextAction(BaseAction):
    """Action to read text from an element for information gathering"""
    action: Literal["read_text"] = "read_text"
    element_id: int = Field(
        ...,
        description="The numerical ID of the element from which to extract text"
    )
    purpose: str = Field(
        ...,
        description="Why this information is needed for the task"
    )


class PressKeyAction(BaseAction):
    """Action to press a keyboard key or combination"""
    action: Literal["press_key"] = "press_key"
    key: str = Field(
        ...,
        description="The key to press (e.g., 'Enter', 'Tab', 'Escape', 'Control+A')"
    )
    element_id: Optional[int] = Field(
        None,
        description="Optional element to focus before pressing the key"
    )


class HoverAction(BaseAction):
    """Action to hover over an element"""
    action: Literal["hover"] = "hover"
    element_id: int = Field(
        ...,
        description="The numerical ID of the element to hover over"
    )
    duration_ms: int = Field(
        default=1000,
        ge=100,
        le=5000,
        description="Duration to maintain hover in milliseconds"
    )


class DragAction(BaseAction):
    """Action to drag an element"""
    action: Literal["drag"] = "drag"
    source_element_id: int = Field(
        ...,
        description="The numerical ID of the element to drag from"
    )
    target_element_id: Optional[int] = Field(
        None,
        description="The numerical ID of the element to drag to"
    )
    offset_x: Optional[int] = Field(
        None,
        description="X offset in pixels if dragging to position"
    )
    offset_y: Optional[int] = Field(
        None,
        description="Y offset in pixels if dragging to position"
    )


class ScreenshotAction(BaseAction):
    """Action to take a screenshot"""
    action: Literal["screenshot"] = "screenshot"
    full_page: bool = Field(
        default=False,
        description="Whether to capture the full page or just viewport"
    )
    element_id: Optional[int] = Field(
        None,
        description="Optional element to screenshot specifically"
    )
    purpose: str = Field(
        ...,
        description="Why this screenshot is needed"
    )


class FinishedAction(BaseAction):
    """Action to signal that the current task is successfully completed"""
    action: Literal["finished"] = "finished"
    summary: str = Field(
        ...,
        description="A brief summary of what was accomplished in this task"
    )
    extracted_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Any data extracted during the task"
    )
    next_steps: Optional[List[str]] = Field(
        None,
        description="Suggested next steps if applicable"
    )


class FailedAction(BaseAction):
    """Action to signal that the task cannot be completed"""
    action: Literal["failed"] = "failed"
    reason: str = Field(
        ...,
        description="Detailed explanation of why the task failed"
    )
    error_type: Literal["element_not_found", "page_error", "timeout", 
                        "captcha", "authentication_required", "other"] = Field(
        ...,
        description="Category of failure"
    )
    attempted_actions: List[str] = Field(
        default_factory=list,
        description="List of actions that were attempted before failure"
    )
    suggestions: Optional[List[str]] = Field(
        None,
        description="Suggestions for how to resolve the issue"
    )


# Union type for all possible actions
AgentAction = Union[
    ClickAction,
    TypeAction,
    FillAction,
    ScrollAction,
    NavigateAction,
    SelectAction,
    WaitAction,
    ReadTextAction,
    PressKeyAction,
    HoverAction,
    DragAction,
    ScreenshotAction,
    FinishedAction,
    FailedAction
]


class ActionPlan(BaseModel):
    """A plan consisting of multiple actions"""
    actions: List[AgentAction] = Field(
        ...,
        description="Ordered list of actions to execute"
    )
    goal: str = Field(
        ...,
        description="The overall goal this plan aims to achieve"
    )
    estimated_duration_ms: Optional[int] = Field(
        None,
        description="Estimated time to complete all actions"
    )


class TaskDecomposition(BaseModel):
    """Decomposition of a complex task into sub-tasks"""
    main_task: str = Field(
        ...,
        description="The main task to be accomplished"
    )
    sub_tasks: List[str] = Field(
        ...,
        description="Ordered list of sub-tasks to complete the main task"
    )
    dependencies: Optional[Dict[int, List[int]]] = Field(
        None,
        description="Task dependencies (task_id -> list of dependent task_ids)"
    )
    estimated_duration_minutes: Optional[float] = Field(
        None,
        description="Estimated total duration in minutes"
    )