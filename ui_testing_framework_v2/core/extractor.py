"""
Intelligent extraction pipeline with streaming, caching, and auto-profile selection
"""

import asyncio
import hashlib
import time
from typing import List, Optional, Iterator, Dict, Any
from pathlib import Path

from playwright.async_api import Page

from .models import Element, ElementType, ExtractionResult, PageCharacteristics
from .profile_manager import ProfileManager
from ..storage.sqlite_storage import SQLiteStorage
from ..cache.memory_cache import MemoryCache
from ..browser import UltimateStealthBrowser, StealthConfig


class IntelligentExtractor:
    """Smart extraction with auto-profile selection and caching"""
    
    def __init__(self, 
                 profile_manager: Optional[ProfileManager] = None,
                 storage: Optional[SQLiteStorage] = None,
                 cache: Optional[MemoryCache] = None):
        """Initialize extractor with dependencies"""
        self.profile_manager = profile_manager or ProfileManager()
        self.storage = storage or SQLiteStorage()
        self.cache = cache or MemoryCache()
        self.stealth_browser = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._init_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup()
    
    async def _init_browser(self):
        """Initialize browser with stealth settings"""
        if not self.stealth_browser:
            # Create config with headless=False as per requirements
            config = StealthConfig(
                headless=False,
                shadow_dom_enabled=True,
                shadow_dom_max_depth=5
            )
            self.stealth_browser = UltimateStealthBrowser(config)
            await self.stealth_browser.initialize()
    
    async def _cleanup(self):
        """Clean up browser resources"""
        if self.stealth_browser:
            await self.stealth_browser.cleanup()
            self.stealth_browser = None
    
    async def extract(self, 
                     url: str, 
                     profile: Optional[str] = None,
                     use_cache: bool = True,
                     auto_profile: bool = True) -> ExtractionResult:
        """
        Main extraction method with intelligent features
        
        Args:
            url: URL to extract from
            profile: Profile name (optional, auto-detected if not provided)
            use_cache: Whether to use caching
            auto_profile: Whether to auto-select profile based on page analysis
        """
        start_time = time.time()
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(url, profile)
            cached = self.cache.get(cache_key)
            if cached:
                cached.cache_hit = True
                return cached
        
        # Initialize browser if needed
        if not self.stealth_browser:
            await self._init_browser()
        
        # Navigate to page
        await self.stealth_browser.navigate(url)
        page = self.stealth_browser.page
        
        # Analyze page characteristics
        characteristics = await self._analyze_page(page)
        
        # Auto-select profile if needed
        if auto_profile and not profile:
            profile = characteristics.suggest_profile()
            print(f"Auto-selected profile: {profile}")
        
        # Get profile config
        profile_config = self.profile_manager.get_or_default(profile)
        
        # Extract elements
        elements = await self._extract_elements(page, profile_config)
        
        # Score and filter elements
        elements = self._score_elements(elements, profile_config)
        elements = self._filter_elements(elements, profile_config)
        
        # Generate content hash for deduplication
        content_hash = self._generate_content_hash(elements)
        
        # Create result
        result = ExtractionResult(
            url=url,
            profile=profile or "auto",
            elements=elements,
            duration=time.time() - start_time,
            characteristics=characteristics,
            content_hash=content_hash
        )
        
        # Save to storage
        if self.storage:
            self.storage.save_extraction(result)
        
        # Update cache
        if use_cache:
            self.cache.set(cache_key, result)
        
        return result
    
    async def _analyze_page(self, page: Page) -> PageCharacteristics:
        """Analyze page to determine characteristics"""
        characteristics = PageCharacteristics(url=page.url)
        
        # Count various element types
        characteristics.form_count = await page.locator('form').count()
        characteristics.input_count = await page.locator('input').count()
        characteristics.button_count = await page.locator('button').count()
        characteristics.link_count = await page.locator('a').count()
        
        # Check for ARIA attributes
        aria_elements = await page.locator('[role], [aria-label], [aria-describedby]').count()
        characteristics.has_aria = aria_elements > 0
        
        # Check for forms
        characteristics.has_forms = characteristics.form_count > 0
        
        # Detect framework (simplified)
        html = await page.content()
        if 'ng-' in html or 'angular' in html.lower():
            characteristics.uses_framework = 'angular'
        elif 'react' in html.lower() or '_react' in html:
            characteristics.uses_framework = 'react'
        elif 'vue' in html.lower() or 'v-' in html:
            characteristics.uses_framework = 'vue'
        
        # Check if SPA
        characteristics.is_spa = bool(characteristics.uses_framework)
        
        # Calculate totals
        total = await page.locator('*').count()
        characteristics.total_elements = min(total, 10000)  # Cap for performance
        
        interactive = characteristics.button_count + characteristics.input_count + characteristics.link_count
        if characteristics.total_elements > 0:
            characteristics.interactive_ratio = interactive / characteristics.total_elements
        
        return characteristics
    
    async def _extract_elements(self, page: Page, profile_config) -> List[Element]:
        """Extract elements from page"""
        elements = []
        max_elements = profile_config.settings.get("max_elements", 1000)
        
        # JavaScript to extract element information
        js_code = """
        () => {
            const elements = document.querySelectorAll('*');
            const results = [];
            const maxElements = """ + str(max_elements) + """;
            
            for (let i = 0; i < Math.min(elements.length, maxElements); i++) {
                const el = elements[i];
                const rect = el.getBoundingClientRect();
                
                // Skip very small or invisible elements
                if (rect.width < 1 || rect.height < 1) continue;
                
                const computed = window.getComputedStyle(el);
                const isVisible = computed.display !== 'none' && 
                                computed.visibility !== 'hidden' && 
                                computed.opacity !== '0';
                
                results.push({
                    tagName: el.tagName.toLowerCase(),
                    selector: el.id ? `#${el.id}` : (el.className && typeof el.className === 'string') ? `.${el.className.split(' ')[0]}` : el.tagName.toLowerCase(),
                    text: el.textContent ? el.textContent.substring(0, 100) : null,
                    attributes: {
                        id: el.id || null,
                        className: el.className || null,
                        href: el.href || null,
                        name: el.name || null,
                        type: el.type || null,
                        role: el.getAttribute('role') || null,
                        'aria-label': el.getAttribute('aria-label') || null
                    },
                    isVisible: isVisible,
                    boundingBox: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    }
                });
            }
            
            return results;
        }
        """
        
        # Execute extraction
        raw_elements = await page.evaluate(js_code)
        
        # Convert to Element objects
        for raw in raw_elements:
            element_type = self._determine_element_type(raw['tagName'], raw['attributes'])
            
            element = Element(
                selector=raw['selector'],
                tag_name=raw['tagName'],
                element_type=element_type,
                text=raw.get('text'),
                attributes=raw['attributes'],
                is_visible=raw['isVisible'],
                is_interactive=self._is_interactive(raw['tagName'], raw['attributes']),
                bounding_box=raw['boundingBox']
            )
            
            elements.append(element)
        
        return elements
    
    def _determine_element_type(self, tag_name: str, attributes: Dict) -> ElementType:
        """Determine element type from tag and attributes"""
        tag = tag_name.lower()
        
        if tag == 'button':
            return ElementType.BUTTON
        elif tag == 'a':
            return ElementType.LINK
        elif tag == 'input':
            input_type = attributes.get('type', 'text')
            if input_type in ['checkbox']:
                return ElementType.CHECKBOX
            elif input_type in ['radio']:
                return ElementType.RADIO
            else:
                return ElementType.INPUT
        elif tag == 'select':
            return ElementType.SELECT
        elif tag == 'textarea':
            return ElementType.TEXTAREA
        elif tag == 'form':
            return ElementType.FORM
        elif tag == 'img':
            return ElementType.IMAGE
        else:
            return ElementType.OTHER
    
    def _is_interactive(self, tag_name: str, attributes: Dict) -> bool:
        """Check if element is interactive"""
        interactive_tags = ['button', 'a', 'input', 'select', 'textarea', 'label']
        interactive_roles = ['button', 'link', 'checkbox', 'radio', 'textbox']
        
        if tag_name.lower() in interactive_tags:
            return True
        
        if attributes.get('role') in interactive_roles:
            return True
        
        if attributes.get('onclick') or attributes.get('href'):
            return True
        
        return False
    
    def _score_elements(self, elements: List[Element], profile_config) -> List[Element]:
        """Score elements based on profile weights"""
        weights = profile_config.scoring.get("weights", {})
        
        for element in elements:
            score = 0.0
            
            # Apply scoring weights
            if element.attributes.get('id') and 'has_id' in weights:
                score += weights['has_id']
            
            if element.attributes.get('name') and 'has_name' in weights:
                score += weights['has_name']
            
            if element.is_interactive:
                if element.element_type == ElementType.BUTTON and 'is_clickable' in weights:
                    score += weights['is_clickable']
                elif element.element_type in [ElementType.INPUT, ElementType.TEXTAREA] and 'is_editable' in weights:
                    score += weights['is_editable']
            
            if element.attributes.get('aria-label') and 'has_aria_label' in weights:
                score += weights['has_aria_label']
            
            # Normalize score
            element.interaction_score = min(score, 1.0)
        
        # Sort by score
        elements.sort(key=lambda e: e.interaction_score, reverse=True)
        
        return elements
    
    def _filter_elements(self, elements: List[Element], profile_config) -> List[Element]:
        """Filter elements based on profile filters"""
        filtered = []
        filters = profile_config.filters
        
        for element in elements:
            passes = True
            
            for filter_config in filters:
                filter_type = filter_config.get('type')
                
                if filter_type == 'interactive':
                    min_score = filter_config.get('min_score', 0.5)
                    if element.interaction_score < min_score:
                        passes = False
                        break
                
                elif filter_type == 'visible':
                    if filter_config.get('required', True) and not element.is_visible:
                        passes = False
                        break
                
                elif filter_type == 'size':
                    if element.bounding_box:
                        min_width = filter_config.get('min_width', 1)
                        min_height = filter_config.get('min_height', 1)
                        if element.bounding_box['width'] < min_width or element.bounding_box['height'] < min_height:
                            passes = False
                            break
            
            if passes:
                filtered.append(element)
        
        # Apply max elements limit
        max_elements = profile_config.settings.get('max_elements', 1000)
        return filtered[:max_elements]
    
    def _generate_content_hash(self, elements: List[Element]) -> str:
        """Generate hash of content for deduplication"""
        content = ""
        for element in elements[:100]:  # Use first 100 elements for hash
            content += f"{element.tag_name}:{element.selector}:{element.text or ''}:"
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_key(self, url: str, profile: Optional[str]) -> str:
        """Generate cache key"""
        return f"{url}:{profile or 'auto'}"