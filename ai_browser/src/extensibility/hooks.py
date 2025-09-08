"""Hook system for event-driven plugin integration.

This module provides a comprehensive hook system that allows plugins to respond
to events throughout the browser automation lifecycle. It integrates with the
hooks.json configuration and provides both synchronous and asynchronous hooks.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union, Awaitable, Set
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel
from loguru import logger

from .interfaces import IHookListener, PluginContext, PluginResult


class HookType(Enum):
    """Types of hooks available in the system"""
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    SESSION_START = "SessionStart"
    SESSION_END = "SessionEnd"
    STOP = "Stop"
    NOTIFICATION = "Notification"
    
    # Browser-specific hooks
    BROWSER_LAUNCH = "BrowserLaunch"
    BROWSER_CLOSE = "BrowserClose"
    PAGE_LOAD = "PageLoad"
    PAGE_NAVIGATE = "PageNavigate"
    ELEMENT_INTERACT = "ElementInteract"
    
    # Plugin lifecycle hooks
    PLUGIN_LOAD = "PluginLoad"
    PLUGIN_UNLOAD = "PluginUnload"
    PLUGIN_ERROR = "PluginError"
    
    # Stealth hooks
    STEALTH_APPLY = "StealthApply"
    DETECTION_TEST = "DetectionTest"
    
    # Analysis hooks
    PAGE_ANALYZE = "PageAnalyze"
    ELEMENT_EXTRACT = "ElementExtract"
    
    # Custom hooks
    CUSTOM = "Custom"


class HookPriority(Enum):
    """Hook execution priorities"""
    CRITICAL = 0
    HIGH = 10
    NORMAL = 50
    LOW = 100
    BACKGROUND = 200


@dataclass
class HookEvent:
    """Represents a hook event"""
    name: str
    hook_type: HookType
    data: Any = None
    context: Optional[PluginContext] = None
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    source: Optional[str] = None
    blocking: bool = False
    timeout: Optional[float] = None


@dataclass
class HookHandler:
    """Represents a hook handler registration"""
    name: str
    callback: Union[Callable, Awaitable]
    priority: int = HookPriority.NORMAL.value
    plugin_name: Optional[str] = None
    async_handler: bool = False
    matcher: Optional[str] = None
    path_matcher: Optional[str] = None
    enabled: bool = True
    timeout: Optional[float] = None


class HookResult(BaseModel):
    """Result from hook execution"""
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    continue_chain: bool = True
    modified_data: Any = None
    execution_time_ms: float = 0.0
    handler_name: Optional[str] = None


class HookChainResult(BaseModel):
    """Result from executing a chain of hooks"""
    success: bool = True
    results: List[HookResult] = field(default_factory=list)
    final_data: Any = None
    total_execution_time_ms: float = 0.0
    handlers_executed: int = 0
    errors: List[str] = field(default_factory=list)


class HookSystem:
    """Central hook management system"""
    
    def __init__(self, hooks_config_path: Optional[str] = None):
        self.handlers: Dict[str, List[HookHandler]] = {}
        self.listeners: Dict[str, List[IHookListener]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing = False
        self.hooks_config = {}
        self.stats = {
            'hooks_triggered': 0,
            'handlers_executed': 0,
            'errors': 0,
            'average_execution_time': 0.0
        }
        
        # Load hooks configuration if provided
        if hooks_config_path:
            self.load_hooks_config(hooks_config_path)
    
    def load_hooks_config(self, config_path: str) -> None:
        """Load hooks configuration from JSON file"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.hooks_config = json.load(f)
                logger.info(f"Loaded hooks configuration from {config_path}")
                
                # Register hooks from configuration
                self._register_config_hooks()
            else:
                logger.warning(f"Hooks config file not found: {config_path}")
                
        except Exception as e:
            logger.error(f"Failed to load hooks configuration: {e}")
    
    def _register_config_hooks(self) -> None:
        """Register hooks from loaded configuration"""
        hooks_data = self.hooks_config.get('hooks', {})
        
        for hook_type, hook_configs in hooks_data.items():
            if isinstance(hook_configs, list):
                for config in hook_configs:
                    self._register_config_hook(hook_type, config)
    
    def _register_config_hook(self, hook_type: str, config: Dict[str, Any]) -> None:
        """Register a single hook from configuration"""
        try:
            name = config.get('name', f"config_{hook_type}")
            matcher = config.get('matcher')
            path_matcher = config.get('pathMatcher')
            
            # Create handlers for each hook command
            hooks_list = config.get('hooks', [])
            for i, hook_config in enumerate(hooks_list):
                if hook_config.get('type') == 'command':
                    handler = HookHandler(
                        name=f"{name}_{i}",
                        callback=self._create_command_handler(hook_config),
                        priority=HookPriority.NORMAL.value,
                        matcher=matcher,
                        path_matcher=path_matcher,
                        async_handler=hook_config.get('async', False),
                        timeout=hook_config.get('timeout')
                    )
                    self.register_hook_handler(hook_type, handler)
                    
        except Exception as e:
            logger.error(f"Failed to register config hook {hook_type}: {e}")
    
    def _create_command_handler(self, config: Dict[str, Any]) -> Callable:
        """Create a command handler from configuration"""
        command = config.get('command', '')
        is_async = config.get('async', False)
        blocking = config.get('blocking', False)
        
        async def command_handler(event: HookEvent) -> HookResult:
            """Execute command hook"""
            try:
                import subprocess
                import os
                
                # Substitute environment variables
                env_vars = {
                    'CLAUDE_PROJECT_DIR': os.getcwd(),
                    'FILE_PATH': getattr(event.context, 'file_path', ''),
                    'USER_PROMPT': str(event.data) if event.data else '',
                }
                
                expanded_command = command
                for var, value in env_vars.items():
                    expanded_command = expanded_command.replace(f'${var}', str(value))
                
                # Execute command
                if is_async:
                    process = await asyncio.create_subprocess_shell(
                        expanded_command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    returncode = process.returncode
                else:
                    result = subprocess.run(
                        expanded_command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    stdout = result.stdout
                    stderr = result.stderr
                    returncode = result.returncode
                
                # Handle blocking hooks that return JSON
                if blocking and stdout.strip():
                    try:
                        result_data = json.loads(stdout.strip())
                        return HookResult(
                            success=result_data.get('continue', True),
                            data=result_data,
                            continue_chain=result_data.get('continue', True)
                        )
                    except json.JSONDecodeError:
                        pass
                
                return HookResult(
                    success=returncode == 0,
                    data=stdout.strip() if stdout else None,
                    error=stderr.strip() if stderr and returncode != 0 else None
                )
                
            except Exception as e:
                return HookResult(
                    success=False,
                    error=str(e)
                )
        
        return command_handler
    
    def register_hook_handler(self, hook_name: str, handler: HookHandler) -> None:
        """Register a hook handler"""
        if hook_name not in self.handlers:
            self.handlers[hook_name] = []
        
        self.handlers[hook_name].append(handler)
        
        # Sort handlers by priority
        self.handlers[hook_name].sort(key=lambda h: h.priority)
        
        logger.debug(f"Registered hook handler '{handler.name}' for '{hook_name}'")
    
    def unregister_hook_handler(self, hook_name: str, handler_name: str) -> bool:
        """Unregister a hook handler"""
        if hook_name in self.handlers:
            self.handlers[hook_name] = [
                h for h in self.handlers[hook_name] 
                if h.name != handler_name
            ]
            logger.debug(f"Unregistered hook handler '{handler_name}' from '{hook_name}'")
            return True
        return False
    
    def register_hook_listener(self, hook_name: str, listener: IHookListener) -> None:
        """Register a hook listener (plugin-based)"""
        if hook_name not in self.listeners:
            self.listeners[hook_name] = []
        
        self.listeners[hook_name].append(listener)
        
        # Sort listeners by priority
        self.listeners[hook_name].sort(key=lambda l: l.get_hook_priority(hook_name))
        
        logger.debug(f"Registered hook listener for '{hook_name}'")
    
    def unregister_hook_listener(self, hook_name: str, listener: IHookListener) -> bool:
        """Unregister a hook listener"""
        if hook_name in self.listeners:
            try:
                self.listeners[hook_name].remove(listener)
                logger.debug(f"Unregistered hook listener from '{hook_name}'")
                return True
            except ValueError:
                pass
        return False
    
    async def trigger_hook(
        self,
        hook_name: str,
        data: Any = None,
        context: Optional[PluginContext] = None,
        blocking: bool = False,
        timeout: Optional[float] = None
    ) -> HookChainResult:
        """Trigger a hook and execute all registered handlers"""
        
        start_time = asyncio.get_event_loop().time()
        
        # Create hook event
        event = HookEvent(
            name=hook_name,
            hook_type=self._get_hook_type(hook_name),
            data=data,
            context=context,
            blocking=blocking,
            timeout=timeout
        )
        
        # Execute handlers
        chain_result = await self._execute_hook_chain(event)
        
        # Update statistics
        execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
        chain_result.total_execution_time_ms = execution_time
        
        self.stats['hooks_triggered'] += 1
        self.stats['handlers_executed'] += chain_result.handlers_executed
        if chain_result.errors:
            self.stats['errors'] += len(chain_result.errors)
        
        # Update average execution time
        current_avg = self.stats['average_execution_time']
        total_hooks = self.stats['hooks_triggered']
        self.stats['average_execution_time'] = (
            (current_avg * (total_hooks - 1) + execution_time) / total_hooks
        )
        
        logger.debug(
            f"Hook '{hook_name}' executed in {execution_time:.2f}ms "
            f"({chain_result.handlers_executed} handlers)"
        )
        
        return chain_result
    
    async def _execute_hook_chain(self, event: HookEvent) -> HookChainResult:
        """Execute the chain of handlers for a hook"""
        
        results = []
        current_data = event.data
        total_handlers = 0
        errors = []
        
        # Execute registered handlers
        if event.name in self.handlers:
            for handler in self.handlers[event.name]:
                if not handler.enabled:
                    continue
                
                # Check matcher conditions
                if not self._check_handler_matches(handler, event):
                    continue
                
                try:
                    # Execute handler
                    handler_start = asyncio.get_event_loop().time()
                    
                    if handler.async_handler:
                        if asyncio.iscoroutinefunction(handler.callback):
                            result = await handler.callback(event)
                        else:
                            result = await asyncio.to_thread(handler.callback, event)
                    else:
                        if asyncio.iscoroutinefunction(handler.callback):
                            result = await handler.callback(event)
                        else:
                            result = handler.callback(event)
                    
                    # Convert result to HookResult if needed
                    if not isinstance(result, HookResult):
                        result = HookResult(
                            success=True,
                            data=result,
                            modified_data=result if result != current_data else None
                        )
                    
                    # Update execution time
                    handler_time = (asyncio.get_event_loop().time() - handler_start) * 1000
                    result.execution_time_ms = handler_time
                    result.handler_name = handler.name
                    
                    results.append(result)
                    total_handlers += 1
                    
                    # Update current data if modified
                    if result.modified_data is not None:
                        current_data = result.modified_data
                    
                    # Check if chain should continue
                    if not result.continue_chain:
                        logger.debug(f"Hook chain stopped by handler: {handler.name}")
                        break
                        
                    # Check for blocking errors
                    if event.blocking and not result.success:
                        logger.warning(f"Blocking hook failed: {handler.name}")
                        errors.append(f"Blocking handler '{handler.name}' failed: {result.error}")
                        break
                        
                except Exception as e:
                    error_msg = f"Handler '{handler.name}' failed: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
                    # Add error result
                    results.append(HookResult(
                        success=False,
                        error=str(e),
                        handler_name=handler.name
                    ))
                    
                    total_handlers += 1
        
        # Execute plugin listeners
        if event.name in self.listeners:
            for listener in self.listeners[event.name]:
                try:
                    listener_result = await listener.on_hook_triggered(
                        event.name,
                        event.context,
                        current_data
                    )
                    
                    if listener_result is not None:
                        current_data = listener_result
                        
                    total_handlers += 1
                    
                except Exception as e:
                    error_msg = f"Listener for '{event.name}' failed: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
        
        return HookChainResult(
            success=len(errors) == 0,
            results=results,
            final_data=current_data,
            handlers_executed=total_handlers,
            errors=errors
        )
    
    def _check_handler_matches(self, handler: HookHandler, event: HookEvent) -> bool:
        """Check if handler matches event conditions"""
        
        # Check matcher pattern
        if handler.matcher and event.data:
            import re
            data_str = str(event.data)
            if not re.search(handler.matcher, data_str, re.IGNORECASE):
                return False
        
        # Check path matcher
        if handler.path_matcher and event.context:
            import re
            file_path = getattr(event.context, 'file_path', '')
            if file_path and not re.search(handler.path_matcher, file_path):
                return False
        
        return True
    
    def _get_hook_type(self, hook_name: str) -> HookType:
        """Get hook type from hook name"""
        for hook_type in HookType:
            if hook_type.value == hook_name:
                return hook_type
        return HookType.CUSTOM
    
    async def emit_event(
        self,
        hook_name: str,
        data: Any = None,
        context: Optional[PluginContext] = None
    ) -> HookChainResult:
        """Emit a hook event (alias for trigger_hook)"""
        return await self.trigger_hook(hook_name, data, context)
    
    async def emit_filtered_event(
        self,
        hook_name: str,
        data: Any,
        context: Optional[PluginContext] = None
    ) -> Any:
        """Emit a hook event that can modify data"""
        result = await self.trigger_hook(hook_name, data, context)
        return result.final_data if result.final_data is not None else data
    
    def get_hook_stats(self) -> Dict[str, Any]:
        """Get hook system statistics"""
        return {
            **self.stats,
            'registered_hooks': len(self.handlers),
            'total_handlers': sum(len(handlers) for handlers in self.handlers.values()),
            'total_listeners': sum(len(listeners) for listeners in self.listeners.values())
        }
    
    def list_hooks(self) -> List[str]:
        """Get list of all registered hooks"""
        return list(self.handlers.keys())
    
    def get_hook_handlers(self, hook_name: str) -> List[HookHandler]:
        """Get handlers for a specific hook"""
        return self.handlers.get(hook_name, [])
    
    async def start_event_processing(self):
        """Start background event processing"""
        self.processing = True
        asyncio.create_task(self._process_events())
    
    async def stop_event_processing(self):
        """Stop background event processing"""
        self.processing = False
    
    async def _process_events(self):
        """Background event processing loop"""
        while self.processing:
            try:
                # Process events from queue
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._execute_hook_chain(event)
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing hook event: {e}")


# Global hook system instance
_hook_system: Optional[HookSystem] = None


def get_hook_system() -> HookSystem:
    """Get global hook system instance"""
    global _hook_system
    if _hook_system is None:
        # Try to load hooks.json from project directory
        hooks_config_path = Path('.claude/hooks.json')
        if hooks_config_path.exists():
            _hook_system = HookSystem(str(hooks_config_path))
        else:
            _hook_system = HookSystem()
    
    return _hook_system


def register_hook(hook_name: str, handler: Union[Callable, HookHandler]) -> None:
    """Register a hook handler (convenience function)"""
    hook_system = get_hook_system()
    
    if isinstance(handler, HookHandler):
        hook_system.register_hook_handler(hook_name, handler)
    else:
        hook_handler = HookHandler(
            name=f"handler_{len(hook_system.handlers.get(hook_name, []))}",
            callback=handler,
            async_handler=asyncio.iscoroutinefunction(handler)
        )
        hook_system.register_hook_handler(hook_name, hook_handler)


async def trigger_hook(hook_name: str, data: Any = None, context: Optional[PluginContext] = None) -> HookChainResult:
    """Trigger a hook (convenience function)"""
    hook_system = get_hook_system()
    return await hook_system.trigger_hook(hook_name, data, context)