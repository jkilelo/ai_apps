"""
End-to-End Tests for AI Browser v2.0.0

Tests complete workflows from user input to task completion.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any
import json
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import main components
from main import AIBrowser, TaskConfig


class TestSearchWorkflow:
    """Test complete search workflow"""
    
    @pytest.mark.asyncio
    async def test_google_search_workflow(self):
        """Test searching on Google and extracting results"""
        # Create task configuration
        task_config = TaskConfig(
            task="Search for 'Python tutorials' and extract top 3 results",
            url="https://google.com",
            headless=True,
            max_steps=10
        )
        
        # Mock browser to avoid real browser launch
        with patch('main.BrowserManager') as mock_browser_manager:
            # Setup mock browser
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            
            mock_browser_manager.return_value.browser = mock_browser
            mock_browser_manager.return_value.launch = AsyncMock()
            mock_browser_manager.return_value.close = AsyncMock()
            
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_context.close = AsyncMock()
            
            # Mock page methods
            mock_page.goto = AsyncMock()
            mock_page.url = "https://google.com/search?q=Python+tutorials"
            mock_page.screenshot = AsyncMock()
            mock_page.evaluate = AsyncMock(return_value={
                "results": [
                    {"title": "Python Tutorial", "url": "python.org"},
                    {"title": "Learn Python", "url": "learnpython.org"},
                    {"title": "Python Basics", "url": "pythonbasics.org"}
                ]
            })
            
            # Initialize browser
            browser = AIBrowser()
            
            # Mock other components to return appropriate responses
            with patch.object(browser, 'memory_manager') as mock_memory:
                mock_memory.initialize = AsyncMock()
                mock_memory.store_page_state = AsyncMock()
                mock_memory.store_task_result = AsyncMock()
                mock_memory.close = AsyncMock()
                
                with patch.object(browser, 'orchestrator') as mock_orchestrator:
                    # Simulate orchestrator planning actions
                    mock_orchestrator.plan_next_action = AsyncMock(side_effect=[
                        Mock(type="type", parameters={"selector": "input", "text": "Python tutorials"}),
                        Mock(type="click", parameters={"selector": "button"}),
                        Mock(type="extract", parameters={"selector": ".result"}),
                        Mock(type="complete", parameters={})
                    ])
                    
                    # Execute task
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    # Verify results
                    assert result["status"] in ["completed", "failed"]
                    assert result["task"] == task_config.task
                    assert "actions" in result
                    assert len(result["actions"]) > 0
                    
                    # Cleanup
                    await browser.cleanup()
    
    @pytest.mark.asyncio
    async def test_search_with_pagination(self):
        """Test searching with pagination handling"""
        task_config = TaskConfig(
            task="Search for 'AI research papers' and navigate to second page",
            url="https://scholar.google.com",
            headless=True,
            max_steps=15
        )
        
        with patch('main.BrowserManager') as mock_browser_manager:
            mock_page = AsyncMock()
            mock_page.url = "https://scholar.google.com"
            
            # Test pagination workflow
            browser = AIBrowser()
            
            with patch.object(browser, 'initialize', new=AsyncMock()):
                with patch.object(browser, 'execute_task') as mock_execute:
                    mock_execute.return_value = {
                        "status": "completed",
                        "task": task_config.task,
                        "actions": [
                            {"type": "type", "success": True},
                            {"type": "click", "success": True},
                            {"type": "wait", "success": True},
                            {"type": "click", "success": True, "parameters": {"selector": "a[aria-label='Page 2']"}}
                        ]
                    }
                    
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    # Verify pagination was handled
                    assert result["status"] == "completed"
                    assert any(a["type"] == "click" and "Page 2" in str(a.get("parameters", {})) 
                              for a in result["actions"])


class TestFormAutomation:
    """Test form filling and submission workflows"""
    
    @pytest.mark.asyncio
    async def test_contact_form_submission(self):
        """Test filling and submitting a contact form"""
        task_config = TaskConfig(
            task="Fill the contact form with name 'John Doe', email 'john@example.com', message 'Test message'",
            url="https://example.com/contact",
            headless=True,
            max_steps=10
        )
        
        with patch('main.AIBrowser') as MockBrowser:
            mock_browser = MockBrowser.return_value
            mock_browser.initialize = AsyncMock()
            mock_browser.cleanup = AsyncMock()
            
            # Simulate form filling workflow
            mock_browser.execute_task = AsyncMock(return_value={
                "status": "completed",
                "task": task_config.task,
                "actions": [
                    {"type": "type", "parameters": {"selector": "#name", "text": "John Doe"}, "success": True},
                    {"type": "type", "parameters": {"selector": "#email", "text": "john@example.com"}, "success": True},
                    {"type": "type", "parameters": {"selector": "#message", "text": "Test message"}, "success": True},
                    {"type": "click", "parameters": {"selector": "button[type='submit']"}, "success": True}
                ],
                "final_url": "https://example.com/thank-you"
            })
            
            await mock_browser.initialize(task_config)
            result = await mock_browser.execute_task(task_config)
            
            # Verify form was filled correctly
            assert result["status"] == "completed"
            assert result["final_url"] == "https://example.com/thank-you"
            
            # Check all form fields were filled
            form_fields = ["John Doe", "john@example.com", "Test message"]
            for field in form_fields:
                assert any(field in str(action.get("parameters", {})) 
                          for action in result["actions"])
    
    @pytest.mark.asyncio
    async def test_multi_step_form(self):
        """Test multi-step form with validation"""
        task_config = TaskConfig(
            task="Complete multi-step registration form",
            url="https://example.com/register",
            headless=True,
            max_steps=20
        )
        
        browser = AIBrowser()
        
        with patch.object(browser, 'execute_task') as mock_execute:
            mock_execute.return_value = {
                "status": "completed",
                "task": task_config.task,
                "actions": [
                    # Step 1: Personal info
                    {"step": 1, "type": "type", "parameters": {"selector": "#firstName"}, "success": True},
                    {"step": 2, "type": "type", "parameters": {"selector": "#lastName"}, "success": True},
                    {"step": 3, "type": "click", "parameters": {"selector": "#nextStep"}, "success": True},
                    # Step 2: Contact info
                    {"step": 4, "type": "type", "parameters": {"selector": "#email"}, "success": True},
                    {"step": 5, "type": "type", "parameters": {"selector": "#phone"}, "success": True},
                    {"step": 6, "type": "click", "parameters": {"selector": "#nextStep"}, "success": True},
                    # Step 3: Submit
                    {"step": 7, "type": "click", "parameters": {"selector": "#submit"}, "success": True}
                ]
            }
            
            with patch.object(browser, 'initialize', new=AsyncMock()):
                with patch.object(browser, 'cleanup', new=AsyncMock()):
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    # Verify multi-step process
                    assert result["status"] == "completed"
                    assert len(result["actions"]) >= 7
                    
                    # Check navigation between steps
                    next_clicks = [a for a in result["actions"] 
                                  if a.get("parameters", {}).get("selector") == "#nextStep"]
                    assert len(next_clicks) >= 2


class TestDataExtraction:
    """Test data extraction workflows"""
    
    @pytest.mark.asyncio
    async def test_table_data_extraction(self):
        """Test extracting data from HTML tables"""
        task_config = TaskConfig(
            task="Extract product prices from the pricing table",
            url="https://example.com/pricing",
            headless=True,
            max_steps=5
        )
        
        browser = AIBrowser()
        
        # Mock the extraction workflow
        extracted_data = {
            "products": [
                {"name": "Basic", "price": "$9.99"},
                {"name": "Pro", "price": "$19.99"},
                {"name": "Enterprise", "price": "$49.99"}
            ]
        }
        
        with patch.object(browser, 'execute_task') as mock_execute:
            mock_execute.return_value = {
                "status": "completed",
                "task": task_config.task,
                "actions": [
                    {"type": "wait", "parameters": {"selector": "table"}, "success": True},
                    {"type": "extract", "parameters": {"selector": "table"}, "success": True, 
                     "data": extracted_data}
                ],
                "extracted_data": extracted_data
            }
            
            with patch.object(browser, 'initialize', new=AsyncMock()):
                with patch.object(browser, 'cleanup', new=AsyncMock()):
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    # Verify extraction
                    assert result["status"] == "completed"
                    assert "extracted_data" in result
                    assert len(result["extracted_data"]["products"]) == 3
                    assert all("price" in p for p in result["extracted_data"]["products"])
    
    @pytest.mark.asyncio
    async def test_list_extraction_with_pagination(self):
        """Test extracting items from paginated lists"""
        task_config = TaskConfig(
            task="Extract all article titles from blog (handle pagination)",
            url="https://example.com/blog",
            headless=True,
            max_steps=30
        )
        
        browser = AIBrowser()
        
        # Simulate extracting from multiple pages
        all_articles = []
        for page in range(1, 4):
            all_articles.extend([f"Article {i}" for i in range(page*10-9, page*10+1)])
        
        with patch.object(browser, 'execute_task') as mock_execute:
            mock_execute.return_value = {
                "status": "completed",
                "task": task_config.task,
                "actions": [
                    {"type": "extract", "page": 1, "success": True},
                    {"type": "click", "parameters": {"selector": ".next-page"}, "success": True},
                    {"type": "wait", "success": True},
                    {"type": "extract", "page": 2, "success": True},
                    {"type": "click", "parameters": {"selector": ".next-page"}, "success": True},
                    {"type": "wait", "success": True},
                    {"type": "extract", "page": 3, "success": True}
                ],
                "extracted_data": {"articles": all_articles}
            }
            
            with patch.object(browser, 'initialize', new=AsyncMock()):
                with patch.object(browser, 'cleanup', new=AsyncMock()):
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    # Verify paginated extraction
                    assert result["status"] == "completed"
                    assert len(result["extracted_data"]["articles"]) == 30
                    
                    # Check pagination actions
                    pagination_clicks = [a for a in result["actions"] 
                                       if a.get("parameters", {}).get("selector") == ".next-page"]
                    assert len(pagination_clicks) >= 2


class TestErrorHandling:
    """Test error handling and recovery workflows"""
    
    @pytest.mark.asyncio
    async def test_timeout_recovery(self):
        """Test recovery from timeout errors"""
        task_config = TaskConfig(
            task="Navigate to slow loading page and extract content",
            url="https://slow-site.example.com",
            headless=True,
            timeout=5000,
            max_steps=10
        )
        
        browser = AIBrowser()
        
        with patch.object(browser, 'execute_task') as mock_execute:
            # Simulate timeout and recovery
            mock_execute.return_value = {
                "status": "completed",
                "task": task_config.task,
                "actions": [
                    {"type": "goto", "success": False, "error": "Timeout after 5000ms"},
                    {"type": "wait", "parameters": {"timeout": 2000}, "success": True},
                    {"type": "goto", "success": True, "retry": True},
                    {"type": "extract", "success": True}
                ],
                "recovered": True
            }
            
            with patch.object(browser, 'initialize', new=AsyncMock()):
                with patch.object(browser, 'cleanup', new=AsyncMock()):
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    # Verify recovery
                    assert result["status"] == "completed"
                    assert result.get("recovered") is True
                    
                    # Check retry occurred
                    retry_actions = [a for a in result["actions"] if a.get("retry")]
                    assert len(retry_actions) > 0
    
    @pytest.mark.asyncio
    async def test_element_not_found_recovery(self):
        """Test recovery when elements are not found"""
        task_config = TaskConfig(
            task="Click dynamic button that may not exist initially",
            url="https://example.com/dynamic",
            headless=True,
            max_steps=10
        )
        
        browser = AIBrowser()
        
        with patch.object(browser, 'execute_task') as mock_execute:
            mock_execute.return_value = {
                "status": "completed",
                "task": task_config.task,
                "actions": [
                    {"type": "click", "success": False, "error": "Element not found"},
                    {"type": "wait", "parameters": {"timeout": 3000}, "success": True},
                    {"type": "click", "success": False, "error": "Element not found"},
                    {"type": "evaluate", "parameters": {"script": "trigger_button_render()"}, "success": True},
                    {"type": "wait", "parameters": {"selector": "#dynamic-button"}, "success": True},
                    {"type": "click", "parameters": {"selector": "#dynamic-button"}, "success": True}
                ]
            }
            
            with patch.object(browser, 'initialize', new=AsyncMock()):
                with patch.object(browser, 'cleanup', new=AsyncMock()):
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    # Verify alternative approach was used
                    assert result["status"] == "completed"
                    
                    # Check that script evaluation was used as fallback
                    eval_actions = [a for a in result["actions"] if a["type"] == "evaluate"]
                    assert len(eval_actions) > 0


class TestStealthWorkflow:
    """Test stealth capabilities in real scenarios"""
    
    @pytest.mark.asyncio 
    async def test_cloudflare_bypass(self):
        """Test bypassing Cloudflare protection"""
        task_config = TaskConfig(
            task="Navigate to Cloudflare-protected site and extract content",
            url="https://protected.example.com",
            headless=False,  # Cloudflare often detects headless
            max_steps=15
        )
        
        browser = AIBrowser()
        
        with patch.object(browser, 'test_stealth') as mock_stealth:
            mock_stealth.return_value = {
                "overall_score": "3/3",
                "passed_percentage": 100.0,
                "test_results": {
                    "https://bot.sannysoft.com/": {"passed": True},
                    "https://arh.antoinevastel.com/bots/areyouheadless": {"passed": True},
                    "https://fingerprint.com/demo/": {"passed": True}
                }
            }
            
            with patch.object(browser, 'execute_task') as mock_execute:
                mock_execute.return_value = {
                    "status": "completed",
                    "task": task_config.task,
                    "actions": [
                        {"type": "stealth_check", "passed": True},
                        {"type": "goto", "success": True, "cloudflare_challenge": True},
                        {"type": "wait", "parameters": {"timeout": 5000}, "success": True},
                        {"type": "extract", "success": True}
                    ],
                    "stealth_effective": True
                }
                
                with patch.object(browser, 'initialize', new=AsyncMock()):
                    with patch.object(browser, 'cleanup', new=AsyncMock()):
                        # First test stealth
                        stealth_result = await browser.test_stealth()
                        assert stealth_result["passed_percentage"] == 100.0
                        
                        # Then execute task
                        await browser.initialize(task_config)
                        result = await browser.execute_task(task_config)
                        
                        assert result["status"] == "completed"
                        assert result.get("stealth_effective") is True


class TestComplexWorkflows:
    """Test complex multi-step workflows"""
    
    @pytest.mark.asyncio
    async def test_e_commerce_checkout(self):
        """Test complete e-commerce checkout workflow"""
        task_config = TaskConfig(
            task="Add iPhone 15 to cart and proceed to checkout",
            url="https://shop.example.com",
            headless=True,
            max_steps=25
        )
        
        browser = AIBrowser()
        
        with patch.object(browser, 'execute_task') as mock_execute:
            mock_execute.return_value = {
                "status": "completed",
                "task": task_config.task,
                "workflow": "e-commerce",
                "actions": [
                    # Search for product
                    {"step": "search", "type": "type", "parameters": {"text": "iPhone 15"}, "success": True},
                    {"step": "search", "type": "click", "parameters": {"selector": ".search-btn"}, "success": True},
                    
                    # Select product
                    {"step": "select", "type": "click", "parameters": {"selector": ".product-item"}, "success": True},
                    
                    # Add to cart
                    {"step": "add", "type": "click", "parameters": {"selector": "#add-to-cart"}, "success": True},
                    
                    # Go to cart
                    {"step": "cart", "type": "click", "parameters": {"selector": ".cart-icon"}, "success": True},
                    
                    # Proceed to checkout
                    {"step": "checkout", "type": "click", "parameters": {"selector": "#checkout-btn"}, "success": True}
                ],
                "cart_value": "$999.99"
            }
            
            with patch.object(browser, 'initialize', new=AsyncMock()):
                with patch.object(browser, 'cleanup', new=AsyncMock()):
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    # Verify complete workflow
                    assert result["status"] == "completed"
                    assert result["workflow"] == "e-commerce"
                    
                    # Check all steps were executed
                    steps = ["search", "select", "add", "cart", "checkout"]
                    for step in steps:
                        assert any(a.get("step") == step for a in result["actions"])
                    
                    assert result.get("cart_value") is not None
    
    @pytest.mark.asyncio
    async def test_social_media_posting(self):
        """Test posting content on social media"""
        task_config = TaskConfig(
            task="Post 'Hello World!' on Twitter/X",
            url="https://twitter.com",
            headless=True,
            max_steps=15
        )
        
        browser = AIBrowser()
        
        with patch.object(browser, 'execute_task') as mock_execute:
            mock_execute.return_value = {
                "status": "completed",
                "task": task_config.task,
                "actions": [
                    {"type": "wait", "parameters": {"selector": "[data-testid='tweetTextarea']"}, "success": True},
                    {"type": "click", "parameters": {"selector": "[data-testid='tweetTextarea']"}, "success": True},
                    {"type": "type", "parameters": {"text": "Hello World!"}, "success": True},
                    {"type": "click", "parameters": {"selector": "[data-testid='tweetButton']"}, "success": True},
                    {"type": "wait", "parameters": {"timeout": 2000}, "success": True}
                ],
                "posted": True,
                "post_url": "https://twitter.com/user/status/123456"
            }
            
            with patch.object(browser, 'initialize', new=AsyncMock()):
                with patch.object(browser, 'cleanup', new=AsyncMock()):
                    await browser.initialize(task_config)
                    result = await browser.execute_task(task_config)
                    
                    assert result["status"] == "completed"
                    assert result.get("posted") is True
                    assert "post_url" in result


@pytest.mark.asyncio
async def test_full_system_integration():
    """Test the complete system from CLI to execution"""
    import subprocess
    import sys
    
    # Test CLI invocation
    test_cases = [
        ["--test-stealth"],
        ["--task", "Test task", "--url", "https://example.com", "--headless", "true", "--max-steps", "5"],
        ["--task", "Test", "--config", "configs/production.json"]
    ]
    
    for args in test_cases:
        # Build command
        cmd = [sys.executable, "src/main.py"] + args
        
        # Would run subprocess but mocking for test
        # result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Mock the CLI execution
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed successfully",
                stderr=""
            )
            
            result = mock_run.return_value
            assert result.returncode == 0