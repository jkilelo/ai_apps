"""Action executor for orchestrating browser operations.

This module provides the ActionExecutor class which coordinates the execution
of browser actions while maintaining strict layer separation. NO LLM calls
are allowed in this execution layer.
"""

from typing import Dict, Any, Optional, List, Type
from dataclasses import dataclass, field
from enum import Enum
from playwright.async_api import Page, BrowserContext
from pydantic import BaseModel, Field
from loguru import logger
import asyncio
import time
from datetime import datetime

from .actions import (
    IAction,
    ActionResult,
    ClickAction,
    TypeAction,
    ScrollAction,
    NavigateAction,
    WaitAction,
    ScreenshotAction,
    ExtractTextAction,
    ExtractAttributeAction,
    HoverAction,
    SelectAction,
    CheckAction,
    KeyPressAction,
    EvaluateAction,
    FileUploadAction,
)


class ActionType(str, Enum):
    """Supported action types."""
    
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    NAVIGATE = "navigate"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    EXTRACT_TEXT = "extract_text"
    EXTRACT_ATTRIBUTE = "extract_attribute"
    HOVER = "hover"
    SELECT = "select"
    CHECK = "check"
    KEY_PRESS = "key_press"
    EVALUATE = "evaluate"
    FILE_UPLOAD = "file_upload"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    RELOAD = "reload"


class ActionConfig(BaseModel):
    """Configuration for action execution."""
    
    type: ActionType = Field(..., description="Type of action to execute")
    selector: Optional[str] = Field(None, description="CSS/XPath selector for element")
    element_id: Optional[int] = Field(None, description="Element ID from SoM annotation")
    text: Optional[str] = Field(None, description="Text for type action")
    url: Optional[str] = Field(None, description="URL for navigation")
    direction: Optional[str] = Field(None, description="Scroll direction")
    distance: Optional[int] = Field(None, description="Scroll distance in pixels")
    key: Optional[str] = Field(None, description="Key to press")
    script: Optional[str] = Field(None, description="JavaScript to evaluate")
    attribute: Optional[str] = Field(None, description="Attribute to extract")
    value: Optional[str] = Field(None, description="Value for select/check")
    files: Optional[List[str]] = Field(None, description="File paths for upload")
    timeout: int = Field(30000, description="Action timeout in milliseconds")
    wait_after: int = Field(0, description="Wait after action in milliseconds")
    retry_count: int = Field(3, description="Number of retries on failure")
    screenshot_before: bool = Field(False, description="Take screenshot before action")
    screenshot_after: bool = Field(False, description="Take screenshot after action")
    
    class Config:
        use_enum_values = True


@dataclass
class ExecutionContext:
    """Context for action execution."""
    
    page: Page
    context: BrowserContext
    element_map: Dict[int, str] = field(default_factory=dict)
    screenshots: List[str] = field(default_factory=list)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    
    def log_action(self, action: str, result: ActionResult, duration_ms: float) -> None:
        """Log action execution details."""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "success": result.success,
            "duration_ms": duration_ms,
            "error": result.error,
            "retry_count": result.retry_count,
        })


class ActionExecutor:
    """Orchestrates browser action execution with error handling and retries.
    
    This class is responsible for:
    - Mapping action configurations to concrete action implementations
    - Managing execution context and state
    - Handling retries and error recovery
    - Collecting execution metrics and logs
    
    IMPORTANT: This is part of the Execution Layer - NO LLM calls allowed!
    """
    
    def __init__(self):
        """Initialize the action executor."""
        self.action_registry: Dict[ActionType, Type[IAction]] = {}
        self._register_default_actions()
        logger.info("ActionExecutor initialized with default actions")
    
    def _register_default_actions(self) -> None:
        """Register default action implementations."""
        self.action_registry = {
            ActionType.CLICK: ClickAction,
            ActionType.TYPE: TypeAction,
            ActionType.SCROLL: ScrollAction,
            ActionType.NAVIGATE: NavigateAction,
            ActionType.WAIT: WaitAction,
            ActionType.SCREENSHOT: ScreenshotAction,
            ActionType.EXTRACT_TEXT: ExtractTextAction,
            ActionType.EXTRACT_ATTRIBUTE: ExtractAttributeAction,
            ActionType.HOVER: HoverAction,
            ActionType.SELECT: SelectAction,
            ActionType.CHECK: CheckAction,
            ActionType.KEY_PRESS: KeyPressAction,
            ActionType.EVALUATE: EvaluateAction,
            ActionType.FILE_UPLOAD: FileUploadAction,
        }
    
    def register_action(self, action_type: ActionType, action_class: Type[IAction]) -> None:
        """Register a custom action implementation.
        
        Args:
            action_type: Type of action to register
            action_class: Class implementing IAction interface
        """
        self.action_registry[action_type] = action_class
        logger.info(f"Registered custom action: {action_type.value}")
    
    async def execute_action(
        self,
        config: ActionConfig,
        context: ExecutionContext
    ) -> ActionResult:
        """Execute a single action with the given configuration.
        
        Args:
            config: Action configuration
            context: Execution context with page and state
            
        Returns:
            ActionResult with execution details
        """
        start_time = time.perf_counter()
        
        try:
            # Take screenshot before if requested
            if config.screenshot_before:
                await self._take_screenshot(context, f"before_{config.type.value}")
            
            # Get action implementation
            action_class = self.action_registry.get(config.type)
            if not action_class:
                return ActionResult(
                    success=False,
                    error=f"Unknown action type: {config.type}"
                )
            
            # Create action instance
            action = action_class()
            
            # Prepare action parameters
            params = self._prepare_action_params(config, context)
            
            # Execute with retry logic
            if config.retry_count > 0:
                result = await action.execute_with_retry(
                    context.page,
                    max_retries=config.retry_count,
                    **params
                )
            else:
                result = await action.execute(context.page, **params)
            
            # Wait after action if specified
            if config.wait_after > 0:
                await asyncio.sleep(config.wait_after / 1000)
            
            # Take screenshot after if requested
            if config.screenshot_after:
                await self._take_screenshot(context, f"after_{config.type.value}")
            
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            result.duration_ms = duration_ms
            
            # Log execution
            context.log_action(config.type.value, result, duration_ms)
            
            logger.info(
                f"Action {config.type.value} completed in {duration_ms:.2f}ms "
                f"(success={result.success})"
            )
            
            return result
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Action {config.type.value} failed: {e}")
            
            result = ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )
            
            context.log_action(config.type.value, result, duration_ms)
            return result
    
    async def execute_sequence(
        self,
        actions: List[ActionConfig],
        context: ExecutionContext,
        stop_on_failure: bool = True
    ) -> List[ActionResult]:
        """Execute a sequence of actions.
        
        Args:
            actions: List of action configurations
            context: Execution context
            stop_on_failure: Whether to stop on first failure
            
        Returns:
            List of action results
        """
        results = []
        
        for i, action_config in enumerate(actions):
            logger.info(f"Executing action {i+1}/{len(actions)}: {action_config.type.value}")
            
            result = await self.execute_action(action_config, context)
            results.append(result)
            
            if not result.success and stop_on_failure:
                logger.warning(f"Stopping sequence due to failure at action {i+1}")
                break
        
        # Generate execution summary
        success_count = sum(1 for r in results if r.success)
        total_duration = sum(r.duration_ms or 0 for r in results)
        
        logger.info(
            f"Sequence completed: {success_count}/{len(results)} successful, "
            f"total duration: {total_duration:.2f}ms"
        )
        
        return results
    
    async def execute_parallel(
        self,
        actions: List[ActionConfig],
        context: ExecutionContext,
        max_concurrent: int = 5
    ) -> List[ActionResult]:
        """Execute multiple actions in parallel.
        
        Args:
            actions: List of action configurations
            context: Execution context
            max_concurrent: Maximum concurrent executions
            
        Returns:
            List of action results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(action_config: ActionConfig) -> ActionResult:
            async with semaphore:
                return await self.execute_action(action_config, context)
        
        tasks = [execute_with_semaphore(action) for action in actions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to ActionResults
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(
                    ActionResult(success=False, error=str(result))
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _prepare_action_params(
        self,
        config: ActionConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Prepare parameters for action execution.
        
        Args:
            config: Action configuration
            context: Execution context
            
        Returns:
            Dictionary of action parameters
        """
        params = {}
        
        # Add common parameters
        if config.selector:
            params["selector"] = config.selector
        if config.element_id is not None:
            params["element_id"] = config.element_id
            params["element_map"] = context.element_map
        if config.timeout:
            params["timeout"] = config.timeout
        
        # Add action-specific parameters
        if config.type == ActionType.TYPE:
            params["text"] = config.text or ""
        elif config.type == ActionType.NAVIGATE:
            params["url"] = config.url
        elif config.type == ActionType.SCROLL:
            params["direction"] = config.direction or "down"
            params["distance"] = config.distance or 500
        elif config.type == ActionType.KEY_PRESS:
            params["key"] = config.key
        elif config.type == ActionType.EVALUATE:
            params["script"] = config.script
        elif config.type == ActionType.EXTRACT_ATTRIBUTE:
            params["attribute"] = config.attribute
        elif config.type == ActionType.SELECT:
            params["value"] = config.value
        elif config.type == ActionType.CHECK:
            params["checked"] = config.value == "true"
        elif config.type == ActionType.FILE_UPLOAD:
            params["files"] = config.files or []
        elif config.type == ActionType.WAIT:
            params["duration"] = config.timeout
        
        return params
    
    async def _take_screenshot(
        self,
        context: ExecutionContext,
        name_suffix: str
    ) -> Optional[str]:
        """Take a screenshot and add to context.
        
        Args:
            context: Execution context
            name_suffix: Suffix for screenshot filename
            
        Returns:
            Path to saved screenshot or None on failure
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}_{name_suffix}.png"
            
            screenshot_action = ScreenshotAction()
            result = await screenshot_action.execute(
                context.page,
                filename=filename
            )
            
            if result.success and result.data:
                context.screenshots.append(result.data)
                return result.data
                
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
        
        return None
    
    async def handle_navigation_actions(
        self,
        page: Page,
        action_type: str
    ) -> ActionResult:
        """Handle browser navigation actions.
        
        Args:
            page: Playwright page instance
            action_type: Type of navigation action
            
        Returns:
            ActionResult with execution details
        """
        try:
            if action_type == "go_back":
                await page.go_back()
            elif action_type == "go_forward":
                await page.go_forward()
            elif action_type == "reload":
                await page.reload()
            else:
                return ActionResult(
                    success=False,
                    error=f"Unknown navigation action: {action_type}"
                )
            
            return ActionResult(success=True)
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Navigation action failed: {e}"
            )
    
    def get_execution_summary(self, context: ExecutionContext) -> Dict[str, Any]:
        """Get summary of execution context.
        
        Args:
            context: Execution context
            
        Returns:
            Dictionary with execution summary
        """
        total_actions = len(context.execution_log)
        successful_actions = sum(
            1 for log in context.execution_log if log["success"]
        )
        total_duration = sum(
            log["duration_ms"] for log in context.execution_log
        )
        
        return {
            "start_time": context.start_time.isoformat(),
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": total_actions - successful_actions,
            "total_duration_ms": total_duration,
            "average_duration_ms": total_duration / total_actions if total_actions > 0 else 0,
            "screenshots_taken": len(context.screenshots),
            "execution_log": context.execution_log,
        }