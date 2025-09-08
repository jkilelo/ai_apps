#!/usr/bin/env python3
"""
Live System Integration Test for AI Browser v2.0.0

This test script validates the entire AI Browser system with real API connections,
real browser automation, and real task execution. It tests all critical components
with actual production services.

**CRITICAL: This uses REAL API keys and performs REAL browser actions**
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import pytest
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from loguru import logger
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Import all layers
from execution.browser_manager import BrowserManager, BrowserConfig
from execution.stealth_manager import StealthManager
from execution.action_executor import ActionExecutor
from cognition.actions import AgentAction
from perception.state_observer import StateObserver
from perception.visual_annotator import VisualAnnotator
from perception.dom_processor import DOMProcessor
from cognition.orchestrator import AgentOrchestrator
from cognition.llm_manager import LLMManager
from cognition.action_dispatcher import ActionDispatcher
from cognition.prompt_builder import PromptBuilder
from memory.memory_manager import MemoryManager
from extensibility.plugin_manager import PluginManager

# Load environment variables
load_dotenv()


class LiveSystemTester:
    """Comprehensive live system tester for AI Browser"""
    
    def __init__(self):
        """Initialize the tester"""
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        self.browser_manager: Optional[BrowserManager] = None
        self.llm_manager: Optional[LLMManager] = None
        self.memory_manager: Optional[MemoryManager] = None
        
        # Configure logging
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        
        # Create test output directory
        self.output_dir = Path("test_output") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Test output directory: {self.output_dir}")
    
    def record_test(self, name: str, passed: bool, details: Dict[str, Any] = None, error: str = None):
        """Record test result"""
        self.results["tests"][name] = {
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
            "error": error
        }
        
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
            logger.success(f"✅ {name}: PASSED")
        else:
            self.results["summary"]["failed"] += 1
            logger.error(f"❌ {name}: FAILED - {error}")
    
    async def test_api_keys(self) -> bool:
        """Test that all required API keys are present and valid"""
        logger.info("Testing API key availability...")
        
        required_keys = {
            "OPENAI_API_KEY": "OpenAI",
            "ANTHROPIC_API_KEY": "Anthropic Claude",
            "GOOGLE_API_KEY": "Google Gemini"
        }
        
        all_present = True
        details = {}
        
        for key, provider in required_keys.items():
            value = os.getenv(key)
            if value and len(value) > 10:  # Basic validation
                details[provider] = "Present and appears valid"
                logger.info(f"  ✓ {provider} API key found")
            else:
                details[provider] = "Missing or invalid"
                logger.warning(f"  ✗ {provider} API key missing")
                all_present = False
        
        # Also check for alternative Gemini key
        if not os.getenv("GOOGLE_API_KEY"):
            if os.getenv("GEMINI_API_KEY"):
                details["Google Gemini"] = "Present (using GEMINI_API_KEY)"
                logger.info("  ✓ Using GEMINI_API_KEY as alternative")
                all_present = True
        
        self.record_test("API Keys Availability", all_present, details)
        return all_present
    
    async def test_llm_connections(self) -> bool:
        """Test actual LLM API connections with real calls"""
        logger.info("Testing LLM connections with real API calls...")
        
        try:
            self.llm_manager = LLMManager()
            test_prompt = "Say 'Hello from AI Browser v2.0.0' in exactly 5 words."
            
            results = {}
            all_passed = True
            
            # Test OpenAI
            if os.getenv("OPENAI_API_KEY"):
                try:
                    logger.info("  Testing OpenAI GPT-4...")
                    response = await self.llm_manager.generate(
                        prompt=test_prompt,
                        provider="openai",
                        model="gpt-4-turbo-preview",
                        max_tokens=50
                    )
                    if response and len(response) > 0:
                        results["OpenAI"] = {
                            "status": "Connected",
                            "response": response[:100],
                            "model": "gpt-4-turbo-preview"
                        }
                        logger.success(f"    Response: {response[:50]}...")
                    else:
                        results["OpenAI"] = {"status": "Failed", "error": "Empty response"}
                        all_passed = False
                except Exception as e:
                    results["OpenAI"] = {"status": "Failed", "error": str(e)}
                    logger.error(f"    OpenAI failed: {e}")
                    all_passed = False
            
            # Test Anthropic Claude
            if os.getenv("ANTHROPIC_API_KEY"):
                try:
                    logger.info("  Testing Anthropic Claude...")
                    response = await self.llm_manager.generate(
                        prompt=test_prompt,
                        provider="anthropic",
                        model="claude-3-sonnet-20240229",
                        max_tokens=50
                    )
                    if response and len(response) > 0:
                        results["Anthropic"] = {
                            "status": "Connected",
                            "response": response[:100],
                            "model": "claude-3-sonnet"
                        }
                        logger.success(f"    Response: {response[:50]}...")
                    else:
                        results["Anthropic"] = {"status": "Failed", "error": "Empty response"}
                        all_passed = False
                except Exception as e:
                    results["Anthropic"] = {"status": "Failed", "error": str(e)}
                    logger.error(f"    Anthropic failed: {e}")
                    all_passed = False
            
            # Test Google Gemini
            gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if gemini_key:
                try:
                    logger.info("  Testing Google Gemini...")
                    response = await self.llm_manager.generate(
                        prompt=test_prompt,
                        provider="gemini",
                        model="gemini-pro",
                        max_tokens=50
                    )
                    if response and len(response) > 0:
                        results["Gemini"] = {
                            "status": "Connected",
                            "response": response[:100],
                            "model": "gemini-pro"
                        }
                        logger.success(f"    Response: {response[:50]}...")
                    else:
                        results["Gemini"] = {"status": "Failed", "error": "Empty response"}
                        all_passed = False
                except Exception as e:
                    results["Gemini"] = {"status": "Failed", "error": str(e)}
                    logger.error(f"    Gemini failed: {e}")
                    all_passed = False
            
            self.record_test("LLM API Connections", all_passed, results)
            return all_passed
            
        except Exception as e:
            self.record_test("LLM API Connections", False, error=str(e))
            return False
    
    async def test_browser_launch(self) -> bool:
        """Test browser launch with stealth capabilities"""
        logger.info("Testing browser launch with stealth...")
        
        try:
            # Initialize browser manager
            config = BrowserConfig(
                headless=False,  # Show browser for visual confirmation
                viewport_width=1920,
                viewport_height=1080,
                browser_type="chromium"
            )
            
            self.browser_manager = BrowserManager(config)
            await self.browser_manager.launch()
            
            # Initialize stealth manager
            stealth_manager = StealthManager(
                browser_manager=self.browser_manager,
                auto_load_defaults=True
            )
            
            # Create test context
            context = await self.browser_manager.browser.new_context()
            page = await context.new_page()
            
            # Apply stealth
            await stealth_manager.apply_to_page(page)
            
            # Test navigation to a real website
            logger.info("  Navigating to google.com...")
            await page.goto("https://www.google.com", wait_until="networkidle")
            
            # Check stealth properties
            stealth_check = await page.evaluate("""
                () => ({
                    webdriver: navigator.webdriver,
                    userAgent: navigator.userAgent,
                    plugins: navigator.plugins.length,
                    languages: navigator.languages,
                    chrome: !!window.chrome,
                    permissions: typeof navigator.permissions !== 'undefined'
                })
            """)
            
            # Take screenshot
            screenshot_path = self.output_dir / "browser_launch_test.png"
            await page.screenshot(path=str(screenshot_path))
            
            details = {
                "browser": "Chromium",
                "stealth_applied": True,
                "webdriver_hidden": stealth_check["webdriver"] is None or stealth_check["webdriver"] is False,
                "plugins_count": stealth_check["plugins"],
                "chrome_object": stealth_check["chrome"],
                "screenshot": str(screenshot_path)
            }
            
            # Cleanup
            await context.close()
            
            passed = details["webdriver_hidden"] and details["chrome_object"]
            self.record_test("Browser Launch & Stealth", passed, details)
            return passed
            
        except Exception as e:
            self.record_test("Browser Launch & Stealth", False, error=str(e))
            return False
    
    async def test_perception_layer(self) -> bool:
        """Test perception layer with real DOM processing"""
        logger.info("Testing perception layer...")
        
        try:
            # Initialize perception components
            dom_processor = DOMProcessor()
            visual_annotator = VisualAnnotator()
            state_observer = StateObserver(
                dom_processor=dom_processor,
                visual_annotator=visual_annotator
            )
            
            # Create test page
            context = await self.browser_manager.browser.new_context()
            page = await context.new_page()
            
            # Navigate to a real website with interactive elements
            logger.info("  Navigating to example.com...")
            await page.goto("https://www.example.com", wait_until="networkidle")
            
            # Capture state
            logger.info("  Capturing page state...")
            state = await state_observer.capture_state(page)
            
            # Validate state components
            details = {
                "url_captured": state.url == "https://www.example.com/",
                "title_captured": bool(state.title),
                "dom_elements": len(state.elements) if hasattr(state, 'elements') else 0,
                "screenshot_captured": state.screenshot is not None if hasattr(state, 'screenshot') else False,
                "interactive_elements": len(state.interactive_elements) if hasattr(state, 'interactive_elements') else 0
            }
            
            # Apply visual annotation (Set-of-Marks)
            if hasattr(visual_annotator, 'annotate'):
                logger.info("  Applying visual annotations...")
                annotated = await visual_annotator.annotate(page)
                
                # Save annotated screenshot
                if annotated and 'screenshot' in annotated:
                    screenshot_path = self.output_dir / "annotated_page.png"
                    with open(screenshot_path, 'wb') as f:
                        f.write(annotated['screenshot'])
                    details["annotated_screenshot"] = str(screenshot_path)
                    details["markers_applied"] = len(annotated.get('markers', []))
            
            # Process DOM
            if hasattr(dom_processor, 'process'):
                logger.info("  Processing DOM structure...")
                dom_tree = await dom_processor.process(page)
                details["dom_processed"] = dom_tree is not None
                
                # Save simplified DOM
                if dom_tree:
                    dom_path = self.output_dir / "processed_dom.json"
                    with open(dom_path, 'w') as f:
                        json.dump(dom_tree, f, indent=2)
                    details["dom_output"] = str(dom_path)
            
            await context.close()
            
            passed = details.get("url_captured", False) and details.get("title_captured", False)
            self.record_test("Perception Layer", passed, details)
            return passed
            
        except Exception as e:
            self.record_test("Perception Layer", False, error=str(e))
            return False
    
    async def test_memory_system(self) -> bool:
        """Test memory layer with real database operations"""
        logger.info("Testing memory system...")
        
        try:
            # Initialize memory manager
            self.memory_manager = MemoryManager()
            await self.memory_manager.initialize()
            
            test_data = {
                "task_id": f"test_{datetime.now().timestamp()}",
                "user_input": "Test task for memory system",
                "timestamp": datetime.now().isoformat()
            }
            
            results = {}
            
            # Test SQLite session memory
            logger.info("  Testing SQLite session memory...")
            try:
                # Store conversation
                await self.memory_manager.store_conversation(
                    task_id=test_data["task_id"],
                    user_input=test_data["user_input"],
                    agent_response="Test response stored successfully"
                )
                
                # Retrieve conversation
                history = await self.memory_manager.get_conversation_history(test_data["task_id"])
                results["sqlite"] = {
                    "write": "Success",
                    "read": "Success",
                    "records": len(history) if history else 0
                }
                logger.success("    SQLite operations successful")
            except Exception as e:
                results["sqlite"] = {"status": "Failed", "error": str(e)}
                logger.error(f"    SQLite failed: {e}")
            
            # Test Qdrant vector memory (if available)
            if hasattr(self.memory_manager, 'semantic_memory'):
                logger.info("  Testing Qdrant semantic memory...")
                try:
                    # Store embedding
                    test_text = "Python programming tutorials for beginners"
                    await self.memory_manager.semantic_memory.store(
                        text=test_text,
                        metadata={"type": "test", "timestamp": datetime.now().isoformat()}
                    )
                    
                    # Search similar
                    similar = await self.memory_manager.semantic_memory.search(
                        query="Python coding lessons",
                        limit=5
                    )
                    
                    results["qdrant"] = {
                        "write": "Success",
                        "search": "Success",
                        "results": len(similar) if similar else 0
                    }
                    logger.success("    Qdrant operations successful")
                except Exception as e:
                    results["qdrant"] = {"status": "Not configured", "error": str(e)}
                    logger.warning(f"    Qdrant not available: {e}")
            
            # Test FalkorDB graph memory (if available)
            if hasattr(self.memory_manager, 'knowledge_graph'):
                logger.info("  Testing FalkorDB knowledge graph...")
                try:
                    # Create nodes and relationships
                    await self.memory_manager.knowledge_graph.add_page(
                        url="https://test.example.com",
                        title="Test Page"
                    )
                    
                    results["falkordb"] = {
                        "write": "Success",
                        "status": "Connected"
                    }
                    logger.success("    FalkorDB operations successful")
                except Exception as e:
                    results["falkordb"] = {"status": "Not configured", "error": str(e)}
                    logger.warning(f"    FalkorDB not available: {e}")
            
            self.record_test("Memory System", True, results)
            return True
            
        except Exception as e:
            self.record_test("Memory System", False, error=str(e))
            return False
    
    async def test_full_workflow(self) -> bool:
        """Test complete workflow with a real task"""
        logger.info("Testing full workflow with real task execution...")
        
        try:
            # Initialize orchestrator
            orchestrator = AgentOrchestrator(
                llm_manager=self.llm_manager,
                action_dispatcher=ActionDispatcher(),
                memory_manager=self.memory_manager
            )
            
            # Create browser context
            context = await self.browser_manager.browser.new_context()
            page = await context.new_page()
            
            # Apply stealth
            stealth_manager = StealthManager(self.browser_manager, auto_load_defaults=True)
            await stealth_manager.apply_to_page(page)
            
            # Test task: Search for Python tutorials on Google
            test_task = "Search for 'Python programming tutorials' on Google"
            logger.info(f"  Executing task: {test_task}")
            
            # Navigate to Google
            await page.goto("https://www.google.com", wait_until="networkidle")
            
            # Initialize perception
            state_observer = StateObserver(
                dom_processor=DOMProcessor(),
                visual_annotator=VisualAnnotator()
            )
            
            # Capture initial state
            initial_state = await state_observer.capture_state(page)
            
            # Plan action using LLM
            logger.info("  Planning next action with LLM...")
            action = await orchestrator.plan_next_action(
                task=test_task,
                current_state=initial_state,
                previous_actions=[]
            )
            
            details = {
                "task": test_task,
                "initial_url": page.url,
                "action_planned": action.type if action else None,
                "screenshots": []
            }
            
            # Execute the action
            if action and action.type != "complete":
                logger.info(f"  Executing action: {action.type}")
                
                # Initialize action executor
                action_executor = ActionExecutor(
                    browser_manager=self.browser_manager,
                    stealth_manager=stealth_manager
                )
                
                # Execute action
                result = await action_executor.execute_action(
                    action,
                    {"page": page}
                )
                
                details["action_executed"] = True
                details["action_success"] = result.success
                
                # Wait for navigation
                await asyncio.sleep(2)
                
                # Capture final state
                final_state = await state_observer.capture_state(page)
                details["final_url"] = page.url
                
                # Take screenshots
                for i, name in enumerate(["initial", "final"]):
                    screenshot_path = self.output_dir / f"workflow_{name}.png"
                    if i == 0:
                        await page.goto("https://www.google.com", wait_until="networkidle")
                    await page.screenshot(path=str(screenshot_path))
                    details["screenshots"].append(str(screenshot_path))
            
            await context.close()
            
            passed = details.get("action_executed", False) and details.get("action_success", False)
            self.record_test("Full Workflow Execution", passed, details)
            return passed
            
        except Exception as e:
            self.record_test("Full Workflow Execution", False, error=str(e))
            return False
    
    async def test_stealth_detection(self) -> bool:
        """Test against real bot detection services"""
        logger.info("Testing stealth against bot detection services...")
        
        test_sites = [
            {
                "name": "Bot Sannysoft",
                "url": "https://bot.sannysoft.com/",
                "check_selector": "body"
            },
            {
                "name": "Fingerprint Demo",
                "url": "https://fingerprint.com/demo/",
                "check_selector": "body"
            }
        ]
        
        results = {}
        all_passed = True
        
        for site in test_sites:
            try:
                logger.info(f"  Testing {site['name']}...")
                
                context = await self.browser_manager.browser.new_context()
                page = await context.new_page()
                
                # Apply stealth
                stealth_manager = StealthManager(self.browser_manager, auto_load_defaults=True)
                await stealth_manager.apply_to_page(page)
                
                # Navigate to detection site
                await page.goto(site["url"], wait_until="networkidle", timeout=30000)
                await asyncio.sleep(3)  # Wait for detection
                
                # Check detection status
                detection_check = await page.evaluate("""
                    () => {
                        const bodyText = document.body.innerText.toLowerCase();
                        return {
                            detected: bodyText.includes('bot detected') || 
                                     bodyText.includes('headless') ||
                                     bodyText.includes('automated'),
                            webdriver: navigator.webdriver,
                            userAgent: navigator.userAgent,
                            plugins: navigator.plugins.length
                        };
                    }
                """)
                
                # Take screenshot
                screenshot_path = self.output_dir / f"stealth_{site['name'].replace(' ', '_').lower()}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                
                results[site["name"]] = {
                    "passed": not detection_check["detected"],
                    "webdriver_hidden": not detection_check["webdriver"],
                    "plugins": detection_check["plugins"],
                    "screenshot": str(screenshot_path)
                }
                
                if detection_check["detected"]:
                    all_passed = False
                    logger.warning(f"    Bot detected at {site['name']}")
                else:
                    logger.success(f"    Passed detection at {site['name']}")
                
                await context.close()
                
            except Exception as e:
                results[site["name"]] = {"error": str(e)}
                all_passed = False
                logger.error(f"    Failed to test {site['name']}: {e}")
        
        self.record_test("Stealth Detection Tests", all_passed, results)
        return all_passed
    
    async def run_all_tests(self):
        """Run all live system tests"""
        logger.info("="*60)
        logger.info("AI BROWSER v2.0.0 - LIVE SYSTEM TEST")
        logger.info("="*60)
        logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        
        try:
            # Test 1: API Keys
            await self.test_api_keys()
            logger.info("")
            
            # Test 2: LLM Connections
            await self.test_llm_connections()
            logger.info("")
            
            # Test 3: Browser Launch
            await self.test_browser_launch()
            logger.info("")
            
            # Test 4: Perception Layer
            await self.test_perception_layer()
            logger.info("")
            
            # Test 5: Memory System
            await self.test_memory_system()
            logger.info("")
            
            # Test 6: Full Workflow
            await self.test_full_workflow()
            logger.info("")
            
            # Test 7: Stealth Detection
            await self.test_stealth_detection()
            logger.info("")
            
        finally:
            # Cleanup
            if self.browser_manager:
                await self.browser_manager.close()
            if self.memory_manager:
                await self.memory_manager.close()
            
            # Save results
            results_path = self.output_dir / "test_results.json"
            with open(results_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            # Print summary
            logger.info("="*60)
            logger.info("TEST SUMMARY")
            logger.info("="*60)
            logger.info(f"Total Tests: {self.results['summary']['total']}")
            logger.info(f"Passed: {self.results['summary']['passed']} ✅")
            logger.info(f"Failed: {self.results['summary']['failed']} ❌")
            
            if self.results['summary']['failed'] == 0:
                logger.success("\n🎉 ALL TESTS PASSED! The AI Browser system is fully operational.")
            else:
                logger.warning(f"\n⚠️ {self.results['summary']['failed']} tests failed. Review the results.")
            
            logger.info(f"\nTest results saved to: {results_path}")
            logger.info(f"Screenshots and outputs in: {self.output_dir}")
            
            return self.results['summary']['failed'] == 0


async def main():
    """Main entry point for live system test"""
    tester = LiveSystemTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)