"""
Browser with LLM Integration - Simplified Version
Uses single source of truth LLM from llm.py
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

# LLM - Single Source of Truth
from llm import call_default_llm

# Browser Integration
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

# Environment Setup
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class BrowserConfig:
    """Browser configuration"""
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    timeout: int = 30000
    enable_javascript: bool = True
    enable_cookies: bool = True
    
@dataclass
class ExtractionResult:
    """Result from browser extraction"""
    url: str
    html: Optional[str] = None
    text: Optional[str] = None
    elements: List[Dict[str, Any]] = field(default_factory=list)
    llm_analysis: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None
    extraction_time: float = 0.0

# ============================================================================
# BROWSER WITH LLM
# ============================================================================

class BrowserWithLLM:
    """
    Browser automation with integrated LLM analysis
    Uses single source of truth LLM from llm.py
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self.browser = None
        self.context = None
        self.page = None
        
    async def initialize(self):
        """Initialize browser"""
        if not HAS_PLAYWRIGHT:
            raise ImportError("Playwright not installed. Run: pip install playwright")
            
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless
            )
            self.context = await self.browser.new_context(
                viewport={
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                },
                user_agent=self.config.user_agent
            )
            self.page = await self.context.new_page()
            logger.info("Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
            
    async def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            await self.page.goto(url, timeout=self.config.timeout)
            await self.page.wait_for_load_state('networkidle')
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
            
    async def extract_elements(self, selector: str = "*") -> List[Dict[str, Any]]:
        """Extract elements from page"""
        try:
            elements = await self.page.query_selector_all(selector)
            result = []
            
            for element in elements:
                try:
                    tag_name = await element.evaluate("el => el.tagName")
                    text = await element.inner_text() if tag_name not in ['SCRIPT', 'STYLE'] else ''
                    attributes = await element.evaluate("el => Object.fromEntries(Array.from(el.attributes).map(a => [a.name, a.value]))")
                    
                    result.append({
                        'tag': tag_name.lower(),
                        'text': text.strip() if text else '',
                        'attributes': attributes
                    })
                except:
                    continue
                    
            return result
            
        except Exception as e:
            logger.error(f"Element extraction failed: {e}")
            return []
            
    async def analyze_with_llm(self, content: str, prompt: str = "Analyze this web content") -> Dict[str, Any]:
        """
        Analyze content with LLM using single source of truth
        """
        try:
            messages = [
                {"role": "system", "content": "You are a web content analyzer."},
                {"role": "user", "content": f"{prompt}\n\nContent:\n{content[:4000]}"}  # Limit content size
            ]
            
            # Use the default LLM from llm.py
            response = await asyncio.to_thread(call_default_llm, messages)
            
            return {
                'analysis': response,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                'analysis': None,
                'success': False,
                'error': str(e)
            }
            
    async def extract_and_analyze(self, url: str) -> ExtractionResult:
        """
        Extract content from URL and analyze with LLM
        """
        start_time = time.time()
        result = ExtractionResult(url=url)
        
        try:
            # Navigate to URL
            if not await self.navigate(url):
                result.success = False
                result.error = "Navigation failed"
                return result
                
            # Extract HTML and text
            result.html = await self.page.content()
            result.text = await self.page.inner_text('body')
            
            # Extract elements
            result.elements = await self.extract_elements()
            
            # Analyze with LLM
            if result.text:
                result.llm_analysis = await self.analyze_with_llm(
                    result.text,
                    f"Analyze the content from {url} and identify key information"
                )
                
            result.extraction_time = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            result.success = False
            result.error = str(e)
            
        return result
        
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Browser cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# ============================================================================
# MAIN EXAMPLE
# ============================================================================

async def main():
    """Example usage"""
    logger.info("=" * 60)
    logger.info("Browser with LLM - Using Single Source of Truth")
    logger.info("=" * 60)
    
    # Initialize browser
    browser = BrowserWithLLM(BrowserConfig(headless=True))
    await browser.initialize()
    
    try:
        # Test extraction and analysis
        url = "https://example.com"
        logger.info(f"Extracting and analyzing: {url}")
        
        result = await browser.extract_and_analyze(url)
        
        if result.success:
            logger.info(f"✓ Extraction successful")
            logger.info(f"  Elements found: {len(result.elements)}")
            logger.info(f"  Text length: {len(result.text) if result.text else 0}")
            
            if result.llm_analysis and result.llm_analysis.get('success'):
                logger.info(f"✓ LLM Analysis completed")
                logger.info(f"  Analysis: {result.llm_analysis['analysis'][:200]}...")
            else:
                logger.info("✗ LLM Analysis failed")
                
            logger.info(f"  Time: {result.extraction_time:.2f}s")
        else:
            logger.error(f"✗ Extraction failed: {result.error}")
            
    finally:
        await browser.cleanup()
        
    logger.info("=" * 60)
    logger.info("Test completed - Using centralized LLM from llm.py")

if __name__ == "__main__":
    asyncio.run(main())