#!/usr/bin/env python3
"""
AI-First Smart Browser v2.0.0 - Main Entry Point

This is the primary CLI interface for the autonomous web agent that executes
natural language tasks through intelligent browser automation.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import argparse
from datetime import datetime
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Layer imports
from execution.browser_manager import BrowserManager, BrowserConfig
from execution.stealth_manager import StealthManager
from execution.action_executor import ActionExecutor
from perception.state_observer import StateObserver
from perception.visual_annotator import VisualAnnotator
from perception.dom_processor import DOMProcessor
from cognition.orchestrator import AgentOrchestrator
from cognition.llm import LLMManager
from cognition.dispatcher import ActionDispatcher
from memory.memory_manager import MemoryManager
from extensibility.plugin_manager import PluginManager
from extensibility.hooks import HookSystem


class TaskConfig(BaseModel):
    """Configuration for a browser task"""
    task: str = Field(..., description="Natural language task to execute")
    url: Optional[str] = Field(None, description="Starting URL")
    headless: bool = Field(True, description="Run browser in headless mode")
    timeout: int = Field(60000, description="Task timeout in milliseconds")
    max_steps: int = Field(50, description="Maximum action steps")
    screenshot_on_error: bool = Field(True, description="Capture screenshots on error")
    debug: bool = Field(False, description="Enable debug mode")
    config_file: Optional[str] = Field(None, description="Path to configuration file")
    test_stealth: bool = Field(False, description="Run stealth capability tests")
    plugin_dir: Optional[str] = Field(None, description="Additional plugin directory")
    disable_plugins: List[str] = Field(default_factory=list, description="Plugins to disable")
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 1000:
            raise ValueError("Timeout must be at least 1000ms")
        if v > 600000:
            raise ValueError("Timeout cannot exceed 600000ms (10 minutes)")
        return v


class AIBrowser:
    """Main AI Browser orchestrator that coordinates all layers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AI Browser with configuration"""
        self.config = config or {}
        self.browser_manager: Optional[BrowserManager] = None
        self.stealth_manager: Optional[StealthManager] = None
        self.action_executor: Optional[ActionExecutor] = None
        self.state_observer: Optional[StateObserver] = None
        self.visual_annotator: Optional[VisualAnnotator] = None
        self.dom_processor: Optional[DOMProcessor] = None
        self.orchestrator: Optional[AgentOrchestrator] = None
        self.llm_manager: Optional[LLMManager] = None
        self.action_dispatcher: Optional[ActionDispatcher] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.plugin_manager: Optional[PluginManager] = None
        self.hook_system: Optional[HookSystem] = None
        
        # Configure logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure structured logging"""
        log_level = self.config.get("log_level", "INFO")
        log_file = self.config.get("log_file", "logs/ai_browser.log")
        
        # Remove default handler
        logger.remove()
        
        # Add console handler with formatting
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level
        )
        
        # Add file handler if specified
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            logger.add(
                log_file,
                rotation="10 MB",
                retention="7 days",
                level=log_level
            )
    
    async def initialize(self, task_config: TaskConfig) -> None:
        """Initialize all layers and components"""
        logger.info("Initializing AI Browser v2.0.0")
        
        try:
            # Load environment variables
            load_dotenv()
            
            # Load configuration file if specified
            if task_config.config_file:
                with open(task_config.config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            
            # Initialize Memory Layer (first, as others may use it)
            logger.info("Initializing Memory Layer")
            self.memory_manager = MemoryManager()
            await self.memory_manager.initialize()
            
            # Initialize Extensibility Layer
            logger.info("Initializing Extensibility Layer")
            self.plugin_manager = PluginManager()
            
            # Add custom plugin directory if specified
            if task_config.plugin_dir:
                self.plugin_manager.plugin_dirs.append(task_config.plugin_dir)
            
            await self.plugin_manager.discover_plugins()
            
            # Disable specified plugins
            for plugin_name in task_config.disable_plugins:
                if plugin_name in self.plugin_manager.plugins:
                    logger.info(f"Disabling plugin: {plugin_name}")
                    await self.plugin_manager.unload_plugin(plugin_name)
            
            # Initialize Hook System
            self.hook_system = HookSystem()
            hooks_config = Path(".claude/hooks.json")
            if hooks_config.exists():
                self.hook_system.load_hooks_config(str(hooks_config))
                logger.info(f"Loaded {len(self.hook_system.handlers)} hook handlers")
            
            # Initialize Execution Layer
            logger.info("Initializing Execution Layer")
            browser_config = BrowserConfig(
                headless=task_config.headless,
                viewport_width=self.config.get("viewport_width", 1920),
                viewport_height=self.config.get("viewport_height", 1080),
                browser_type=self.config.get("browser_type", "chromium"),
                user_agent=self.config.get("user_agent"),
                proxy=self.config.get("proxy")
            )
            
            self.browser_manager = BrowserManager()
            await self.browser_manager.launch(browser_config)
            
            self.stealth_manager = StealthManager(auto_load_defaults=True)
            
            self.action_executor = ActionExecutor()
            
            # Initialize Perception Layer
            logger.info("Initializing Perception Layer")
            self.dom_processor = DOMProcessor()
            self.visual_annotator = VisualAnnotator()
            self.state_observer = StateObserver()
            
            # Initialize Cognition Layer
            logger.info("Initializing Cognition Layer")
            self.llm_manager = LLMManager()
            self.action_dispatcher = ActionDispatcher()
            
            # Get the default LLM provider for the orchestrator
            default_provider = self.llm_manager.get_provider()
            self.orchestrator = AgentOrchestrator(
                llm_provider=default_provider,
                enable_self_correction=True
            )
            
            # Trigger SessionStart hook
            await self.hook_system.trigger_hook(
                "SessionStart",
                data={
                    "timestamp": datetime.now().isoformat(),
                    "config": task_config.dict()
                }
            )
            
            logger.success("AI Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Browser: {e}")
            raise
    
    async def execute_task(self, task_config: TaskConfig) -> Dict[str, Any]:
        """Execute a natural language task"""
        logger.info(f"Executing task: {task_config.task}")
        
        result = {
            "task": task_config.task,
            "status": "pending",
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "error": None,
            "final_url": None,
            "screenshots": []
        }
        
        try:
            # Create new browser context
            context = await self.browser_manager.browser.new_context()
            page = await context.new_page()
            
            # Apply stealth to page
            await self.stealth_manager.apply_to_page(page)
            
            # Navigate to starting URL if provided
            if task_config.url:
                logger.info(f"Navigating to: {task_config.url}")
                await page.goto(task_config.url, wait_until="networkidle")
            
            # Trigger UserPromptSubmit hook
            await self.hook_system.trigger_hook(
                "UserPromptSubmit",
                data={
                    "prompt": task_config.task,
                    "url": task_config.url
                }
            )
            
            # Execute task through orchestrator using ReAct loop
            orchestrator_result = await self.orchestrator.execute_task_with_react(
                page=page,
                task=task_config.task,
                context=None  # No previous context for initial execution
            )
            
            # Process orchestrator results
            if orchestrator_result.get("success"):
                logger.info("Task completed successfully")
                result["status"] = "completed"
                result["summary"] = orchestrator_result.get("summary", "")
                result["extracted_data"] = orchestrator_result.get("extracted_data")
                result["reasoning_steps"] = orchestrator_result.get("reasoning_steps", [])
                result["iterations"] = orchestrator_result.get("iterations", 0)
            else:
                logger.error(f"Task failed: {orchestrator_result.get('error')}")
                result["status"] = "failed"
                result["error"] = orchestrator_result.get("error")
                result["reasoning_steps"] = orchestrator_result.get("reasoning_steps", [])
            
            # Capture final state
            result["final_url"] = page.url
            
            if task_config.screenshot_on_error or result["status"] == "completed":
                screenshot_path = f"screenshots/task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=screenshot_path)
                result["screenshots"].append(screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Trigger Stop hook
            await self.hook_system.trigger_hook(
                "Stop",
                data={
                    "task": task_config.task,
                    "status": result["status"],
                    "iterations": result.get("iterations", 0)
                }
            )
            
            # Clean up
            await context.close()
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            
            if task_config.screenshot_on_error and page:
                try:
                    screenshot_path = f"screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=screenshot_path)
                    result["screenshots"].append(screenshot_path)
                    logger.info(f"Error screenshot saved: {screenshot_path}")
                except:
                    pass
        
        result["end_time"] = datetime.now().isoformat()
        
        # Store result in memory
        await self.memory_manager.store_conversation(
            task_id=f"task_{datetime.now().timestamp()}",
            user_input=task_config.task,
            agent_response=result.get("summary", "Task executed")
        )
        
        return result
    
    async def test_stealth(self) -> Dict[str, Any]:
        """Test stealth capabilities against bot detection"""
        logger.info("Running stealth capability tests")
        
        test_sites = [
            "https://bot.sannysoft.com/",
            "https://arh.antoinevastel.com/bots/areyouheadless",
            "https://fingerprint.com/demo/",
        ]
        
        results = {}
        
        for site in test_sites:
            logger.info(f"Testing against: {site}")
            
            try:
                context = await self.browser_manager.browser.new_context()
                page = await context.new_page()
                
                # Apply stealth
                await self.stealth_manager.apply_to_page(page)
                
                # Navigate to test site
                await page.goto(site, wait_until="networkidle", timeout=30000)
                
                # Wait for detection results
                await asyncio.sleep(3)
                
                # Take screenshot
                screenshot_path = f"screenshots/stealth_{Path(site).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Try to extract detection results
                detection_result = await page.evaluate("""
                    () => {
                        // Try to find detection indicators
                        const bodyText = document.body.innerText.toLowerCase();
                        const isBot = bodyText.includes('bot') || 
                                      bodyText.includes('headless') ||
                                      bodyText.includes('automated');
                        
                        return {
                            detected: isBot,
                            webdriver: navigator.webdriver,
                            userAgent: navigator.userAgent,
                            plugins: navigator.plugins.length,
                            languages: navigator.languages
                        };
                    }
                """)
                
                results[site] = {
                    "passed": not detection_result.get("detected", True),
                    "details": detection_result,
                    "screenshot": screenshot_path
                }
                
                await context.close()
                
            except Exception as e:
                logger.error(f"Failed to test {site}: {e}")
                results[site] = {
                    "passed": False,
                    "error": str(e)
                }
        
        # Calculate overall score
        passed = sum(1 for r in results.values() if r.get("passed", False))
        total = len(results)
        
        return {
            "overall_score": f"{passed}/{total}",
            "passed_percentage": (passed / total) * 100 if total > 0 else 0,
            "test_results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def cleanup(self) -> None:
        """Clean up all resources"""
        logger.info("Cleaning up AI Browser resources")
        
        try:
            if self.browser_manager:
                await self.browser_manager.close()
            
            if self.memory_manager:
                await self.memory_manager.close()
            
            if self.plugin_manager:
                await self.plugin_manager.shutdown()
            
            logger.success("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI-First Smart Browser v2.0.0 - Autonomous Web Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py --task "Search for Python tutorials" --url "https://google.com"
  python src/main.py --task "Fill out the contact form" --url "https://example.com/contact"
  python src/main.py --test-stealth
  python src/main.py --task "..." --debug --headless false
  python src/main.py --task "..." --config configs/production.json
        """
    )
    
    # Task arguments
    parser.add_argument(
        "--task",
        type=str,
        help="Natural language task to execute"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Starting URL for the task"
    )
    
    # Configuration arguments
    parser.add_argument(
        "--headless",
        type=lambda x: x.lower() in ['true', '1', 'yes'],
        default=True,
        help="Run browser in headless mode (default: true)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60000,
        help="Task timeout in milliseconds (default: 60000)"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=50,
        help="Maximum number of action steps (default: 50)"
    )
    parser.add_argument(
        "--config",
        type=str,
        dest="config_file",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--plugin-dir",
        type=str,
        help="Additional plugin directory to load"
    )
    parser.add_argument(
        "--disable-plugin",
        action="append",
        dest="disable_plugins",
        default=[],
        help="Disable specific plugin(s)"
    )
    
    # Operation modes
    parser.add_argument(
        "--test-stealth",
        action="store_true",
        help="Run stealth capability tests"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging"
    )
    parser.add_argument(
        "--screenshot-on-error",
        type=lambda x: x.lower() in ['true', '1', 'yes'],
        default=True,
        help="Capture screenshots on error (default: true)"
    )
    
    # Logging
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.test_stealth and not args.task:
        parser.error("Either --task or --test-stealth must be specified")
    
    # Create configuration
    config = {
        "log_level": "DEBUG" if args.debug else args.log_level,
        "log_file": args.log_file
    }
    
    # Initialize browser
    browser = AIBrowser(config)
    
    try:
        # Create task configuration
        task_config = TaskConfig(
            task=args.task or "test",
            url=args.url,
            headless=args.headless,
            timeout=args.timeout,
            max_steps=args.max_steps,
            screenshot_on_error=args.screenshot_on_error,
            debug=args.debug,
            config_file=args.config_file,
            test_stealth=args.test_stealth,
            plugin_dir=args.plugin_dir,
            disable_plugins=args.disable_plugins
        )
        
        # Initialize components
        await browser.initialize(task_config)
        
        # Execute operation
        if args.test_stealth:
            result = await browser.test_stealth()
            
            # Print results
            print("\n" + "="*60)
            print("STEALTH TEST RESULTS")
            print("="*60)
            print(f"Overall Score: {result['overall_score']} ({result['passed_percentage']:.1f}% passed)")
            print("\nDetailed Results:")
            for site, details in result['test_results'].items():
                status = "✅ PASSED" if details.get('passed') else "❌ FAILED"
                print(f"\n{site}:")
                print(f"  Status: {status}")
                if 'error' in details:
                    print(f"  Error: {details['error']}")
                elif 'details' in details:
                    print(f"  WebDriver: {details['details'].get('webdriver')}")
                    print(f"  Plugins: {details['details'].get('plugins')}")
                if 'screenshot' in details:
                    print(f"  Screenshot: {details['screenshot']}")
        else:
            result = await browser.execute_task(task_config)
            
            # Print results
            print("\n" + "="*60)
            print("TASK EXECUTION RESULTS")
            print("="*60)
            print(f"Task: {result['task']}")
            print(f"Status: {result['status'].upper()}")
            print(f"Steps Executed: {len(result['actions'])}")
            
            if result['final_url']:
                print(f"Final URL: {result['final_url']}")
            
            if result['error']:
                print(f"Error: {result['error']}")
            
            if result['screenshots']:
                print(f"Screenshots: {', '.join(result['screenshots'])}")
            
            # Print action summary
            if result['actions']:
                print("\nAction Summary:")
                for action in result['actions'][-5:]:  # Show last 5 actions
                    status = "✓" if action['success'] else "✗"
                    print(f"  {status} Step {action['step']}: {action['type']}")
                    if action.get('error'):
                        print(f"    Error: {action['error']}")
        
        print("\n" + "="*60)
        
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user")
        print("\n\nExecution interrupted by user")
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        print(f"\n\nExecution failed: {e}")
        return 1
    finally:
        await browser.cleanup()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)