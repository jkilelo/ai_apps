#!/usr/bin/env python3
"""
Advanced automation examples for AI-First Smart Browser

This script demonstrates advanced features including:
- AI-powered task execution
- Memory integration
- Stealth capabilities
- Error recovery
- Multi-modal interactions
"""
import asyncio
import os
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path for local imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from execution.browser_manager import BrowserManager
from perception.dom_processor import DOMProcessor
from perception.visual_annotator import VisualAnnotator
from cognition.llm import LLMManager
from memory.memory_manager import MemoryManager
from monitoring.metrics import get_metrics_collector, timer
from common.logger import logger


class AdvancedAutomationExamples:
    """Advanced browser automation examples with AI integration"""
    
    def __init__(self):
        self.browser_manager = None
        self.dom_processor = DOMProcessor()
        self.visual_annotator = VisualAnnotator()
        self.llm_manager = LLMManager()
        self.memory_manager = MemoryManager()
        self.metrics = get_metrics_collector()
    
    async def setup(self):
        """Initialize all components"""
        logger.info("Setting up advanced automation components")
        
        # Initialize components
        self.browser_manager = BrowserManager()
        await self.browser_manager.initialize()
        
        # Initialize memory system
        await self.memory_manager.initialize()
        
        # Launch browser with full stealth
        self.browser = await self.browser_manager.launch(
            headless=False,
            stealth_mode=True,
            viewport_width=1920,
            viewport_height=1080,
            extra_stealth_plugins=["canvas_noise", "webrtc_disable", "timezone_spoof"]
        )
        
        logger.info("Advanced automation setup complete")
    
    async def teardown(self):
        """Clean up all resources"""
        if self.memory_manager:
            await self.memory_manager.close()
        if self.browser_manager:
            await self.browser_manager.close()
        logger.info("Advanced automation cleanup complete")
    
    async def example_1_ai_task_execution(self):
        """Example 1: AI-powered natural language task execution"""
        logger.info("Example 1: AI task execution")
        
        with await timer("ai_task_execution"):
            page = await self.browser.new_page()
            await page.goto("https://news.ycombinator.com")
            
            # Capture page state for AI analysis
            screenshot = await page.screenshot()
            dom_content = await page.content()
            
            # Process DOM and annotate visually
            processed_dom = await self.dom_processor.process_page(dom_content)
            annotated_image = await self.visual_annotator.annotate_screenshot(
                screenshot, processed_dom["interactive_elements"]
            )
            
            # Save annotated screenshot
            output_path = Path("examples/outputs/hackernews_annotated.png")
            annotated_image.save(output_path)
            
            # Use AI to understand the page
            task_prompt = """
            Analyze this Hacker News page and:
            1. Identify the top 3 story titles
            2. Find the "new" link to view newest stories
            3. Determine how to navigate to comments for the first story
            
            Return your analysis as structured JSON.
            """
            
            context = {
                "screenshot_path": str(output_path),
                "dom_structure": processed_dom,
                "task": "analyze_hackernews_page"
            }
            
            try:
                ai_response = await self.llm_manager.analyze_page(task_prompt, context)
                logger.info(f"AI Analysis: {ai_response}")
                
                # Store the task and result in memory
                await self.memory_manager.store_conversation(
                    task_id="hackernews_analysis",
                    user_input=task_prompt,
                    agent_response=str(ai_response)
                )
                
            except Exception as e:
                logger.warning(f"AI analysis failed (API key needed): {e}")
            
            await page.close()
    
    async def example_2_stealth_verification(self):
        """Example 2: Verify stealth capabilities against detection"""
        logger.info("Example 2: Stealth verification")
        
        stealth_test_sites = [
            "https://bot.sannysoft.com/",
            "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html",
            "https://arh.antoinevastel.com/bots/areyouheadless"
        ]
        
        results = {}
        
        for site_url in stealth_test_sites:
            try:
                page = await self.browser.new_page()
                
                # Navigate with stealth enabled
                await page.goto(site_url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # Capture results
                content = await page.content()
                screenshot_path = Path(f"examples/outputs/stealth_test_{len(results)}.png")
                await page.screenshot(path=screenshot_path)
                
                # Analyze for detection indicators
                detection_indicators = [
                    "headless", "webdriver", "automation", "bot", "detected"
                ]
                
                detected = any(indicator in content.lower() for indicator in detection_indicators)
                
                results[site_url] = {
                    "detected": detected,
                    "screenshot": str(screenshot_path),
                    "content_length": len(content)
                }
                
                # Log stealth metrics
                self.metrics.track_stealth_detection(site_url, detected, {
                    "test_type": "stealth_verification",
                    "content_length": len(content)
                })
                
                logger.info(f"Stealth test {site_url}: {'❌ DETECTED' if detected else '✅ PASSED'}")
                
                await page.close()
                
            except Exception as e:
                logger.error(f"Stealth test failed for {site_url}: {e}")
                results[site_url] = {"error": str(e)}
        
        # Save stealth test results
        results_path = Path("examples/outputs/stealth_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Stealth test results saved: {results_path}")
    
    async def example_3_memory_integration(self):
        """Example 3: Memory system integration and learning"""
        logger.info("Example 3: Memory integration")
        
        page = await self.browser.new_page()
        
        # Navigate and store page state
        await page.goto("https://httpbin.org/forms/post")
        
        # Capture current state
        dom_content = await page.content()
        screenshot = await page.screenshot()
        
        # Extract interactive elements
        processed_dom = await self.dom_processor.process_page(dom_content)
        
        # Store page state in memory
        await self.memory_manager.store_page_state(
            url="https://httpbin.org/forms/post",
            dom_snapshot=dom_content[:1000],  # Truncated for storage
            interactive_elements=processed_dom,
            screenshot_path="examples/outputs/form_page.png",
            page_title=await page.title()
        )
        
        # Simulate form interaction and store action
        conversation_id = await self.memory_manager.store_conversation(
            task_id="form_automation_example",
            user_input="Fill out the customer information form",
            agent_response="Filling form fields with test data"
        )
        
        # Fill form (store each action)
        actions = [
            {"type": "fill", "selector": 'input[name="custname"]', "value": "AI Test User"},
            {"type": "fill", "selector": 'input[name="custtel"]', "value": "555-0123"},
            {"type": "fill", "selector": 'input[name="custemail"]', "value": "ai@test.com"},
            {"type": "click", "selector": 'input[name="size"][value="large"]', "value": None},
            {"type": "select", "selector": 'select[name="topping"]', "value": "cheese"}
        ]
        
        for action in actions:
            try:
                if action["type"] == "fill":
                    await page.fill(action["selector"], action["value"])
                elif action["type"] == "click":
                    await page.check(action["selector"])
                elif action["type"] == "select":
                    await page.select_option(action["selector"], action["value"])
                
                # Store successful action in memory
                await self.memory_manager.store_action(
                    conversation_id=conversation_id,
                    action_type=action["type"],
                    action_data=action,
                    success=True,
                    page_url="https://httpbin.org/forms/post",
                    element_selector=action["selector"]
                )
                
                logger.debug(f"Action stored: {action['type']} on {action['selector']}")
                
            except Exception as e:
                # Store failed action
                await self.memory_manager.store_action(
                    conversation_id=conversation_id,
                    action_type=action["type"],
                    action_data=action,
                    success=False,
                    page_url="https://httpbin.org/forms/post"
                )
                logger.warning(f"Action failed: {e}")
        
        # Retrieve memory statistics
        memory_stats = await self.memory_manager.get_memory_statistics()
        logger.info(f"Memory statistics: {memory_stats}")
        
        await page.close()
    
    async def example_4_error_recovery_with_ai(self):
        """Example 4: AI-powered error recovery and self-correction"""
        logger.info("Example 4: Error recovery with AI")
        
        page = await self.browser.new_page()
        
        # Simulate a scenario that might fail
        target_url = "https://httpbin.org/"
        
        try:
            # Attempt navigation with short timeout
            await page.goto(target_url, timeout=5000)
            
            # Try to interact with element that might not exist
            await page.click("#nonexistent-button", timeout=2000)
            
        except Exception as e:
            logger.warning(f"Expected error occurred: {e}")
            
            # Use AI to analyze the situation and suggest recovery
            recovery_prompt = f"""
            A browser automation task failed with the following error:
            {str(e)}
            
            Current page URL: {page.url}
            Task: Click on a button
            
            Suggest a recovery strategy:
            1. What might have gone wrong?
            2. How should we recover?
            3. What alternative actions could we try?
            """
            
            try:
                # Get current page state for AI analysis
                screenshot = await page.screenshot()
                dom_content = await page.content()
                processed_dom = await self.dom_processor.process_page(dom_content)
                
                context = {
                    "error": str(e),
                    "url": page.url,
                    "dom_structure": processed_dom,
                    "task": "error_recovery"
                }
                
                recovery_suggestion = await self.llm_manager.analyze_page(
                    recovery_prompt, context
                )
                
                logger.info(f"AI Recovery Suggestion: {recovery_suggestion}")
                
                # Try recovery - navigate to a known working state
                await page.goto("https://httpbin.org/", timeout=30000)
                title = await page.title()
                logger.info(f"Recovery successful - page title: {title}")
                
            except Exception as ai_error:
                logger.warning(f"AI recovery analysis failed: {ai_error}")
                
                # Fallback recovery strategy
                await page.goto("https://httpbin.org/")
                logger.info("Fallback recovery completed")
        
        await page.close()
    
    async def example_5_performance_monitoring(self):
        """Example 5: Performance monitoring and optimization"""
        logger.info("Example 5: Performance monitoring")
        
        # Track browser initialization time
        self.metrics.start_timer("browser_init")
        page = await self.browser.new_page()
        init_time = self.metrics.stop_timer("browser_init")
        
        # Track page load performance
        test_urls = [
            "https://httpbin.org/",
            "https://httpbin.org/json",
            "https://httpbin.org/html"
        ]
        
        for url in test_urls:
            with await timer("page_load"):
                start_time = asyncio.get_event_loop().time()
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                load_time = asyncio.get_event_loop().time() - start_time
                
                # Track performance metrics
                self.metrics.track_page_load(url, load_time)
                
                logger.info(f"Page load time for {url}: {load_time:.2f}s")
        
        # Get performance summary
        performance_summary = self.metrics.get_performance_summary()
        logger.info(f"Performance summary: {performance_summary}")
        
        # Save performance report
        report_path = Path("examples/outputs/performance_report.json")
        with open(report_path, 'w') as f:
            json.dump(performance_summary, f, indent=2)
        
        await page.close()
    
    async def example_6_multi_modal_interaction(self):
        """Example 6: Multi-modal interaction with visual understanding"""
        logger.info("Example 6: Multi-modal interaction")
        
        page = await self.browser.new_page()
        await page.goto("https://httpbin.org/")
        
        # Capture screenshot and analyze visually
        screenshot = await page.screenshot()
        dom_content = await page.content()
        processed_dom = await self.dom_processor.process_page(dom_content)
        
        # Create visual annotation with Set-of-Marks
        annotated_image = await self.visual_annotator.annotate_screenshot(
            screenshot, processed_dom["interactive_elements"]
        )
        
        output_path = Path("examples/outputs/multimodal_annotated.png")
        annotated_image.save(output_path)
        
        # Use AI to understand the visual layout
        visual_prompt = """
        Analyze this annotated screenshot and describe:
        1. The main sections of the page
        2. Available interactive elements (numbered)
        3. The overall layout and navigation structure
        4. What actions a user could perform on this page
        """
        
        try:
            context = {
                "screenshot_path": str(output_path),
                "dom_structure": processed_dom,
                "task": "visual_analysis"
            }
            
            visual_analysis = await self.llm_manager.analyze_page(visual_prompt, context)
            logger.info(f"Visual Analysis: {visual_analysis}")
            
            # Store the multi-modal interaction
            await self.memory_manager.store_conversation(
                task_id="multimodal_analysis",
                user_input=visual_prompt,
                agent_response=str(visual_analysis)
            )
            
        except Exception as e:
            logger.warning(f"Visual analysis failed: {e}")
        
        await page.close()
    
    async def run_all_examples(self):
        """Run all advanced examples"""
        logger.info("Starting advanced automation examples")
        
        try:
            await self.setup()
            
            await self.example_1_ai_task_execution()
            await self.example_2_stealth_verification()
            await self.example_3_memory_integration()
            await self.example_4_error_recovery_with_ai()
            await self.example_5_performance_monitoring()
            await self.example_6_multi_modal_interaction()
            
            logger.info("All advanced examples completed successfully")
            
            # Generate final metrics report
            await self.metrics.flush_metrics()
            
        except Exception as e:
            logger.error(f"Advanced example failed: {e}")
            raise
        finally:
            await self.teardown()


async def main():
    """Main execution function"""
    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_google = bool(os.getenv("GOOGLE_API_KEY"))
    
    if not (has_openai or has_anthropic or has_google):
        logger.warning("No LLM API keys found. AI features will not work.")
        response = input("Continue with basic automation only? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Create output directory
    Path("examples/outputs").mkdir(exist_ok=True, parents=True)
    
    # Run advanced examples
    examples = AdvancedAutomationExamples()
    await examples.run_all_examples()


if __name__ == "__main__":
    print("🤖 AI-First Smart Browser - Advanced Automation Examples")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
        print("\n✅ All advanced examples completed successfully!")
        print("\n📊 Check examples/outputs/ for generated files and reports")
    except KeyboardInterrupt:
        print("\n⚠️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        sys.exit(1)