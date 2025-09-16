"""Example stealth plugin demonstrating the new plugin architecture.

This plugin shows how to implement a stealth plugin using the new plugin system
while maintaining compatibility with browser automation requirements.
"""

from typing import Dict, Any, List
from playwright.async_api import BrowserContext, Page

from src.extensibility.interfaces import (
    IStealthPlugin,
    PluginMetadata,
    PluginType,
    PluginContext,
    PluginResult
)


class ExampleStealthPlugin(IStealthPlugin):
    """Example stealth plugin that removes automation indicators"""
    
    def __init__(self):
        self._initialized = False
        self._config = {}
    
    async def initialize(self, context: PluginContext) -> PluginResult:
        """Initialize the plugin with configuration"""
        try:
            self._config = context.config
            self._initialized = True
            
            return PluginResult(
                success=True,
                data={"message": "Example stealth plugin initialized"}
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Initialization failed: {str(e)}"
            )
    
    async def execute(self, context: PluginContext, **kwargs) -> PluginResult:
        """Execute the main plugin functionality"""
        
        if not self._initialized:
            return PluginResult(
                success=False,
                error="Plugin not initialized"
            )
        
        results = {}
        
        # Apply to browser context if available
        if context.browser_context:
            context_result = await self.apply_to_context(
                context.browser_context,
                self._config
            )
            results["context_applied"] = context_result.success
            if not context_result.success:
                results["context_error"] = context_result.error
        
        # Apply to page if available
        if context.page:
            page_result = await self.apply_to_page(
                context.page,
                self._config
            )
            results["page_applied"] = page_result.success
            if not page_result.success:
                results["page_error"] = page_result.error
        
        return PluginResult(
            success=True,
            data=results
        )
    
    async def cleanup(self, context: PluginContext) -> PluginResult:
        """Cleanup plugin resources"""
        try:
            self._initialized = False
            self._config = {}
            
            return PluginResult(
                success=True,
                data={"message": "Plugin cleaned up successfully"}
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Cleanup failed: {str(e)}"
            )
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            name="example_stealth",
            version="1.0.0",
            author="AI Browser Team",
            description="Example stealth plugin that removes automation indicators",
            plugin_type=PluginType.STEALTH,
            dependencies=[],
            min_framework_version="2.0.0",
            priority=10,
            hooks=["StealthApply", "BrowserLaunch", "PageLoad"],
            sandbox_permissions={
                "network": False,
                "filesystem": False,
                "subprocess": False,
                "import_all": False
            }
        )
    
    def is_compatible(self, framework_version: str) -> bool:
        """Check compatibility with framework version"""
        try:
            # Compatible with version 2.x
            major_version = int(framework_version.split('.')[0])
            return major_version >= 2
        except:
            return False
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        # This plugin doesn't require specific configuration
        return True
    
    async def on_hook(self, hook_name: str, context: PluginContext, data: Any) -> PluginResult:
        """Handle hook events"""
        
        if hook_name in ["StealthApply", "BrowserLaunch", "PageLoad"]:
            # Execute stealth modifications when relevant hooks are triggered
            return await self.execute(context)
        
        return PluginResult(
            success=True,
            data={"message": f"Hook '{hook_name}' acknowledged but not handled"}
        )
    
    # IStealthPlugin specific methods
    
    async def apply_to_context(self, browser_context: BrowserContext, config: Dict[str, Any]) -> PluginResult:
        """Apply stealth modifications to browser context"""
        
        try:
            # Remove automation indicators at context level
            await browser_context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override user agent data
                Object.defineProperty(navigator, 'userAgentData', {
                    get: () => ({
                        brands: [
                            { brand: "Google Chrome", version: "120" },
                            { brand: "Chromium", version: "120" },
                            { brand: "Not_A Brand", version: "8" }
                        ],
                        mobile: false,
                        platform: "Windows"
                    })
                });
                
                // Add realistic timing
                if (!window.chrome) {
                    window.chrome = {
                        loadTimes: () => ({
                            requestTime: Date.now() / 1000,
                            startLoadTime: Date.now() / 1000,
                            commitLoadTime: Date.now() / 1000,
                            finishDocumentLoadTime: Date.now() / 1000,
                            finishLoadTime: Date.now() / 1000
                        }),
                        csi: () => ({
                            onloadT: Date.now(),
                            pageT: Date.now(),
                            startE: Date.now() - 100
                        })
                    };
                }
            """)
            
            return PluginResult(
                success=True,
                data={"stealth_scripts_injected": True}
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to apply context stealth: {str(e)}"
            )
    
    async def apply_to_page(self, page: Page, config: Dict[str, Any]) -> PluginResult:
        """Apply stealth modifications to specific page"""
        
        try:
            # Additional page-level stealth modifications
            await page.evaluate("""
                // Override permissions API
                if (navigator.permissions) {
                    const originalQuery = navigator.permissions.query;
                    navigator.permissions.query = (parameters) => {
                        if (parameters.name === 'notifications') {
                            return Promise.resolve({ state: 'default' });
                        }
                        return originalQuery(parameters);
                    };
                }
                
                // Modify screen properties to be more realistic
                Object.defineProperty(screen, 'availTop', { get: () => 0 });
                Object.defineProperty(screen, 'availLeft', { get: () => 0 });
            """)
            
            return PluginResult(
                success=True,
                data={"page_modifications_applied": True}
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to apply page stealth: {str(e)}"
            )
    
    async def test_evasion(self, page: Page) -> Dict[str, Any]:
        """Test effectiveness of evasion techniques"""
        
        test_results = {}
        
        try:
            # Test webdriver property
            webdriver_result = await page.evaluate("navigator.webdriver")
            test_results["webdriver_hidden"] = webdriver_result is None
            
            # Test chrome object
            chrome_present = await page.evaluate("typeof window.chrome !== 'undefined'")
            test_results["chrome_object_present"] = chrome_present
            
            # Test user agent data
            ua_data = await page.evaluate("navigator.userAgentData ? navigator.userAgentData.brands.length : 0")
            test_results["user_agent_data_brands"] = ua_data
            
            # Test screen properties
            screen_props = await page.evaluate("""
                ({
                    availTop: screen.availTop,
                    availLeft: screen.availLeft,
                    width: screen.width,
                    height: screen.height
                })
            """)
            test_results["screen_properties"] = screen_props
            
            # Overall assessment
            detection_indicators = []
            
            if not test_results["webdriver_hidden"]:
                detection_indicators.append("webdriver_property_present")
            
            if not test_results["chrome_object_present"]:
                detection_indicators.append("chrome_object_missing")
            
            if test_results["user_agent_data_brands"] == 0:
                detection_indicators.append("user_agent_data_missing")
            
            test_results["detection_indicators"] = detection_indicators
            test_results["stealth_effective"] = len(detection_indicators) == 0
            
        except Exception as e:
            test_results["test_error"] = str(e)
            test_results["stealth_effective"] = False
        
        return test_results
    
    def get_evasion_techniques(self) -> List[str]:
        """Get list of evasion techniques implemented by this plugin"""
        return [
            "webdriver_property_removal",
            "user_agent_data_spoofing", 
            "chrome_object_injection",
            "permissions_api_override",
            "screen_properties_modification"
        ]