"""DOM Analyzer Plugin - Example analysis plugin for the new plugin system.

This plugin demonstrates how to implement page analysis capabilities using
the new plugin architecture.
"""

from typing import Dict, Any, List, Optional
from playwright.async_api import Page
import json

from src.extensibility.interfaces import (
    IAnalysisPlugin,
    PluginMetadata,
    PluginType,
    PluginContext,
    PluginResult
)


class DOMAnalyzerPlugin(IAnalysisPlugin):
    """Plugin for analyzing page DOM structure and extracting elements"""
    
    def __init__(self):
        self._initialized = False
        self._config = {}
    
    async def initialize(self, context: PluginContext) -> PluginResult:
        """Initialize the plugin"""
        try:
            self._config = context.config or {}
            self._initialized = True
            
            return PluginResult(
                success=True,
                data={"message": "DOM Analyzer plugin initialized"}
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Initialization failed: {str(e)}"
            )
    
    async def execute(self, context: PluginContext, **kwargs) -> PluginResult:
        """Execute DOM analysis"""
        
        if not self._initialized:
            return PluginResult(
                success=False,
                error="Plugin not initialized"
            )
        
        if not context.page:
            return PluginResult(
                success=False,
                error="Page context required for DOM analysis"
            )
        
        try:
            # Perform comprehensive page analysis
            analysis_result = await self.analyze_page(context.page, self._config)
            
            return PluginResult(
                success=True,
                data=analysis_result
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"DOM analysis failed: {str(e)}"
            )
    
    async def cleanup(self, context: PluginContext) -> PluginResult:
        """Cleanup plugin resources"""
        try:
            self._initialized = False
            self._config = {}
            
            return PluginResult(
                success=True,
                data={"message": "DOM Analyzer plugin cleaned up"}
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Cleanup failed: {str(e)}"
            )
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            name="dom_analyzer",
            version="1.0.0",
            author="AI Browser Team",
            description="Analyzes page DOM structure and extracts interactive elements",
            plugin_type=PluginType.ANALYSIS,
            dependencies=[],
            min_framework_version="2.0.0",
            priority=50,
            hooks=["PageAnalyze", "ElementExtract", "PageLoad"],
            sandbox_permissions={
                "network": False,
                "filesystem": True,  # For caching analysis results
                "subprocess": False,
                "import_all": False
            },
            config_schema={
                "type": "object",
                "properties": {
                    "include_hidden_elements": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include hidden elements in analysis"
                    },
                    "max_elements": {
                        "type": "integer",
                        "default": 1000,
                        "description": "Maximum number of elements to analyze"
                    },
                    "element_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["button", "input", "select", "textarea", "a"],
                        "description": "Element types to focus on"
                    }
                }
            }
        )
    
    def is_compatible(self, framework_version: str) -> bool:
        """Check compatibility with framework version"""
        try:
            major_version = int(framework_version.split('.')[0])
            return major_version >= 2
        except:
            return False
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        try:
            # Check max_elements is reasonable
            max_elements = config.get("max_elements", 1000)
            if not isinstance(max_elements, int) or max_elements < 1 or max_elements > 10000:
                return False
            
            # Check element_types is valid
            element_types = config.get("element_types", [])
            if not isinstance(element_types, list):
                return False
            
            valid_types = {"button", "input", "select", "textarea", "a", "div", "span", "img", "form"}
            for elem_type in element_types:
                if elem_type not in valid_types:
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def on_hook(self, hook_name: str, context: PluginContext, data: Any) -> PluginResult:
        """Handle hook events"""
        
        if hook_name == "PageAnalyze":
            return await self.execute(context)
        
        elif hook_name == "ElementExtract":
            # Extract elements based on hook data
            if context.page and isinstance(data, dict):
                strategy = data.get("strategy", "interactive")
                elements = await self.extract_elements(context.page, strategy)
                return PluginResult(
                    success=True,
                    data={"elements": elements}
                )
        
        elif hook_name == "PageLoad":
            # Perform automatic analysis on page load if enabled
            if self._config.get("auto_analyze_on_load", False):
                return await self.execute(context)
        
        return PluginResult(
            success=True,
            data={"message": f"Hook '{hook_name}' acknowledged"}
        )
    
    # IAnalysisPlugin specific methods
    
    async def analyze_page(self, page: Page, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze page structure and content"""
        
        try:
            # Get basic page information
            page_info = await page.evaluate("""
                () => ({
                    title: document.title,
                    url: window.location.href,
                    readyState: document.readyState,
                    contentType: document.contentType,
                    characterSet: document.characterSet,
                    elementCount: document.querySelectorAll('*').length,
                    scripts: Array.from(document.scripts).length,
                    styles: Array.from(document.styleSheets).length,
                    images: Array.from(document.images).length,
                    links: Array.from(document.links).length,
                    forms: Array.from(document.forms).length
                })
            """)
            
            # Analyze viewport and layout
            viewport_info = await page.evaluate("""
                () => ({
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight,
                    scrollWidth: document.documentElement.scrollWidth,
                    scrollHeight: document.documentElement.scrollHeight,
                    scrollX: window.scrollX,
                    scrollY: window.scrollY
                })
            """)
            
            # Extract interactive elements
            interactive_elements = await self.extract_elements(page, "interactive")
            
            # Analyze page structure
            structure_analysis = await self._analyze_structure(page)
            
            # Assess page complexity
            complexity_metrics = await self.assess_complexity(page)
            
            return {
                "page_info": page_info,
                "viewport_info": viewport_info,
                "interactive_elements": interactive_elements,
                "structure_analysis": structure_analysis,
                "complexity_metrics": complexity_metrics,
                "analysis_timestamp": await page.evaluate("Date.now()"),
                "config_used": config
            }
            
        except Exception as e:
            raise Exception(f"Page analysis failed: {str(e)}")
    
    async def extract_elements(self, page: Page, selector_strategy: str) -> List[Dict[str, Any]]:
        """Extract interactive elements from page"""
        
        try:
            # Define element selectors based on strategy
            selectors = {
                "interactive": """
                    button, input, select, textarea, a[href], 
                    [onclick], [role="button"], [role="link"], 
                    [tabindex]:not([tabindex="-1"])
                """,
                "all_visible": "*:not([hidden]):not([style*='display: none'])",
                "forms": "form, input, select, textarea, button[type='submit']",
                "navigation": "nav, a[href], button, [role='navigation']",
                "content": "h1, h2, h3, h4, h5, h6, p, div, span, article, section"
            }
            
            selector = selectors.get(selector_strategy, selectors["interactive"])
            
            # Extract elements with their properties
            elements = await page.evaluate(f"""
                (selector) => {{
                    const elements = Array.from(document.querySelectorAll(selector));
                    const maxElements = {self._config.get('max_elements', 1000)};
                    
                    return elements.slice(0, maxElements).map((el, index) => {{
                        const rect = el.getBoundingClientRect();
                        const styles = window.getComputedStyle(el);
                        
                        return {{
                            index: index,
                            tag: el.tagName.toLowerCase(),
                            type: el.type || null,
                            id: el.id || null,
                            className: el.className || null,
                            text: el.textContent?.trim().slice(0, 200) || null,
                            href: el.href || null,
                            value: el.value || null,
                            placeholder: el.placeholder || null,
                            disabled: el.disabled || false,
                            hidden: el.hidden || false,
                            readonly: el.readOnly || false,
                            required: el.required || false,
                            bounds: {{
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                top: Math.round(rect.top),
                                left: Math.round(rect.left),
                                bottom: Math.round(rect.bottom),
                                right: Math.round(rect.right)
                            }},
                            visible: rect.width > 0 && rect.height > 0 && 
                                    styles.visibility !== 'hidden' && 
                                    styles.display !== 'none',
                            clickable: el.onclick !== null || 
                                      el.tagName.toLowerCase() === 'button' ||
                                      el.tagName.toLowerCase() === 'a' ||
                                      el.getAttribute('role') === 'button',
                            selectors: {{
                                css: `{el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.className ? '.' + el.className.replace(/\\s+/g, '.') : ''}`.slice(0, 100),
                                xpath: null // Would need more complex calculation
                            }},
                            attributes: Array.from(el.attributes).reduce((acc, attr) => {{
                                acc[attr.name] = attr.value;
                                return acc;
                            }}, {{}})
                        }};
                    }});
                }}
            """, selector)
            
            # Filter elements based on config
            if not self._config.get("include_hidden_elements", False):
                elements = [el for el in elements if el["visible"]]
            
            return elements
            
        except Exception as e:
            raise Exception(f"Element extraction failed: {str(e)}")
    
    async def assess_complexity(self, page: Page) -> Dict[str, float]:
        """Assess page complexity metrics"""
        
        try:
            complexity = await page.evaluate("""
                () => {
                    const all_elements = document.querySelectorAll('*');
                    const interactive_elements = document.querySelectorAll(
                        'button, input, select, textarea, a[href], [onclick], [role="button"]'
                    );
                    const forms = document.forms.length;
                    const iframes = document.querySelectorAll('iframe').length;
                    const scripts = document.scripts.length;
                    const styles = document.styleSheets.length;
                    
                    // Calculate nesting depth
                    let max_depth = 0;
                    function getDepth(element, current_depth = 0) {
                        max_depth = Math.max(max_depth, current_depth);
                        Array.from(element.children).forEach(child => 
                            getDepth(child, current_depth + 1)
                        );
                    }
                    getDepth(document.body);
                    
                    // Calculate text density
                    const text_length = document.body.textContent.length;
                    const element_count = all_elements.length;
                    const text_density = element_count > 0 ? text_length / element_count : 0;
                    
                    return {
                        total_elements: all_elements.length,
                        interactive_elements: interactive_elements.length,
                        forms_count: forms,
                        iframes_count: iframes,
                        scripts_count: scripts,
                        styles_count: styles,
                        max_nesting_depth: max_depth,
                        text_density: text_density,
                        interactivity_ratio: all_elements.length > 0 ? 
                            interactive_elements.length / all_elements.length : 0
                    };
                }
            """)
            
            # Calculate overall complexity score (0-1)
            factors = {
                'element_complexity': min(complexity['total_elements'] / 1000, 1.0),
                'interaction_complexity': min(complexity['interactive_elements'] / 100, 1.0),
                'structure_complexity': min(complexity['max_nesting_depth'] / 20, 1.0),
                'script_complexity': min(complexity['scripts_count'] / 50, 1.0),
                'form_complexity': min(complexity['forms_count'] / 10, 1.0)
            }
            
            overall_complexity = sum(factors.values()) / len(factors)
            
            return {
                **complexity,
                'complexity_factors': factors,
                'overall_complexity': overall_complexity
            }
            
        except Exception as e:
            raise Exception(f"Complexity assessment failed: {str(e)}")
    
    async def _analyze_structure(self, page: Page) -> Dict[str, Any]:
        """Analyze page structure and semantic elements"""
        
        try:
            structure = await page.evaluate("""
                () => {
                    const semantic_elements = {
                        header: document.querySelectorAll('header, [role="banner"]').length,
                        nav: document.querySelectorAll('nav, [role="navigation"]').length,
                        main: document.querySelectorAll('main, [role="main"]').length,
                        aside: document.querySelectorAll('aside, [role="complementary"]').length,
                        footer: document.querySelectorAll('footer, [role="contentinfo"]').length,
                        article: document.querySelectorAll('article').length,
                        section: document.querySelectorAll('section').length
                    };
                    
                    const headings = {
                        h1: document.querySelectorAll('h1').length,
                        h2: document.querySelectorAll('h2').length,
                        h3: document.querySelectorAll('h3').length,
                        h4: document.querySelectorAll('h4').length,
                        h5: document.querySelectorAll('h5').length,
                        h6: document.querySelectorAll('h6').length
                    };
                    
                    const landmarks = Array.from(document.querySelectorAll('[role]'))
                        .map(el => el.getAttribute('role'))
                        .reduce((acc, role) => {
                            acc[role] = (acc[role] || 0) + 1;
                            return acc;
                        }, {});
                    
                    return {
                        semantic_elements,
                        headings,
                        landmarks,
                        has_semantic_structure: Object.values(semantic_elements).some(count => count > 0),
                        heading_structure_proper: headings.h1 > 0 && headings.h1 <= 3
                    };
                }
            """)
            
            return structure
            
        except Exception as e:
            raise Exception(f"Structure analysis failed: {str(e)}")