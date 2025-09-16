#!/usr/bin/env python3
"""Test script for Google Scholar access improvements"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import AIBrowser, TaskConfig
from execution.google_scholar_handler import GoogleScholarHandler


async def test_google_scholar_access():
    """Test Google Scholar access with improved handling"""
    browser = None
    try:
        logger.info("Initializing AI Browser for Google Scholar test")
        browser = AIBrowser()
        task_config = TaskConfig(task="Test Google Scholar", headless=True)
        await browser.initialize(task_config)
        
        # Initialize Google Scholar handler
        scholar_handler = GoogleScholarHandler()
        
        # Setup browser context with Scholar-specific stealth
        page = await browser.browser_manager.get_page()
        await scholar_handler.setup_scholar_context(page.context)
        
        logger.info("Testing Google Scholar navigation...")
        
        # Test navigation to Scholar
        result = await scholar_handler.navigate_to_scholar(page, "machine learning bias detection")
        if not result.success:
            logger.error(f"Navigation failed: {result.error}")
            return False
        
        logger.info("Navigation successful, testing search...")
        
        # Test search functionality
        search_result = await scholar_handler.perform_search(page, "machine learning bias detection")
        if not search_result.success:
            logger.error(f"Search failed: {search_result.error}")
            return False
        
        logger.info("Search successful, testing paper extraction...")
        
        # Test paper extraction
        papers = await scholar_handler.extract_papers(page, max_papers=3)
        logger.info(f"Extracted {len(papers)} papers:")
        
        for i, paper in enumerate(papers):
            logger.info(f"Paper {i+1}: {paper.get('title', 'No title')[:100]}...")
            logger.info(f"  Authors: {paper.get('authors_raw', 'No authors')}")
            logger.info(f"  Citations: {paper.get('citation_count', 0)}")
        
        if len(papers) > 0:
            logger.success("Google Scholar access test PASSED")
            return True
        else:
            logger.error("No papers extracted - test FAILED")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        return False
    finally:
        if browser:
            await browser.cleanup()


async def test_element_validation():
    """Test element validation improvements"""
    browser = None
    try:
        logger.info("Testing element validation improvements")
        browser = AIBrowser()
        task_config = TaskConfig(task="Test element validation", headless=True)
        await browser.initialize(task_config)
        
        page = await browser.browser_manager.get_page()
        
        # Navigate to Google Scholar
        await page.goto('https://scholar.google.com', wait_until='domcontentloaded')
        
        # Test search box detection and validation
        search_selectors = [
            '#gs_hdr_tsb',
            'input[name="q"]',
            '.gs_in_txt'
        ]
        
        for selector in search_selectors:
            try:
                count = await page.locator(selector).count()
                if count > 0:
                    logger.info(f"Found search element: {selector}")
                    
                    # Test validation logic
                    from cognition.dispatcher import ActionDispatcher
                    dispatcher = ActionDispatcher()
                    
                    validation_result = await dispatcher._validate_element_before_action(
                        page, selector, "fill"
                    )
                    
                    if validation_result.success:
                        logger.success(f"Element {selector} validation PASSED")
                    else:
                        logger.warning(f"Element {selector} validation failed: {validation_result.error}")
                        
                else:
                    logger.warning(f"Element not found: {selector}")
                    
            except Exception as e:
                logger.error(f"Error testing selector {selector}: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Element validation test failed: {e}")
        return False
    finally:
        if browser:
            await browser.cleanup()


async def main():
    """Run all Google Scholar tests"""
    logger.info("Starting Google Scholar access tests")
    
    # Test 1: Basic access and navigation
    test1_result = await test_google_scholar_access()
    
    # Test 2: Element validation improvements
    test2_result = await test_element_validation()
    
    # Summary
    logger.info(f"Test Results:")
    logger.info(f"  Google Scholar Access: {'PASS' if test1_result else 'FAIL'}")
    logger.info(f"  Element Validation: {'PASS' if test2_result else 'FAIL'}")
    
    overall_success = test1_result and test2_result
    if overall_success:
        logger.success("All Google Scholar tests PASSED")
    else:
        logger.error("Some Google Scholar tests FAILED")
    
    return overall_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)