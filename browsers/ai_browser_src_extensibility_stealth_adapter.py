"""Adapter to integrate existing stealth plugins with new plugin system.

This module provides adapters and utilities to migrate the existing stealth system
to the new plugin architecture while maintaining backward compatibility.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
from playwright.async_api import BrowserContext, Page
from loguru import logger

from .interfaces import (
    IStealthPlugin as NewIStealthPlugin,
    PluginMetadata,
    PluginType,
    PluginContext,
    PluginResult,
    PluginState
)
from ..execution.stealth_manager import IStealthPlugin as OldIStealthPlugin, StealthManager


class StealthPluginAdapter(NewIStealthPlugin):
    """Adapter to wrap old stealth plugins in new plugin interface"""
    
    def __init__(self, old_plugin: OldIStealthPlugin):
        self.old_plugin = old_plugin
        self._metadata = None
        self._is_initialized = False
        
    async def initialize(self, context: PluginContext) -> PluginResult:
        """Initialize the adapted plugin"""
        try:
            self._is_initialized = True
            return PluginResult(
                success=True,
                data={"message": f"Stealth plugin '{self.old_plugin.get_name()}' initialized"}
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    async def execute(self, context: PluginContext, **kwargs) -> PluginResult:
        """Execute the stealth plugin"""
        try:
            browser_context = context.browser_context
            page = context.page
            
            if browser_context:
                await self.old_plugin.apply_to_context(browser_context)
            
            if page:
                await self.old_plugin.apply_to_page(page)
            
            return PluginResult(
                success=True,
                data={
                    "plugin_name": self.old_plugin.get_name(),
                    "applied_to_context": browser_context is not None,
                    "applied_to_page": page is not None
                }
            )
            
        except Exception as e:
            logger.error(f"Stealth plugin execution failed: {e}")
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    async def cleanup(self, context: PluginContext) -> PluginResult:
        """Clean up the plugin"""
        try:
            self._is_initialized = False
            return PluginResult(success=True)
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        if self._metadata is None:
            self._metadata = PluginMetadata(
                name=self.old_plugin.get_name(),
                version="1.0.0",  # Legacy plugins default to 1.0.0
                author="AI Browser Legacy",
                description=self.old_plugin.get_description(),
                plugin_type=PluginType.STEALTH,
                priority=self.old_plugin.get_priority(),
                min_framework_version="1.0.0",
                max_framework_version="2.0.0",
                hooks=["StealthApply", "BrowserLaunch", "PageLoad"],
                sandbox_permissions={
                    "network": False,
                    "filesystem": False,
                    "subprocess": False,
                    "import_all": False
                }
            )
        
        return self._metadata
    
    def is_compatible(self, framework_version: str) -> bool:
        """Check if plugin is compatible with framework version"""
        # Legacy plugins are compatible with versions 1.x and 2.x
        try:
            major_version = int(framework_version.split('.')[0])
            return major_version in [1, 2]
        except:
            return False
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        # Legacy plugins don't have complex configuration validation
        return True
    
    async def on_hook(self, hook_name: str, context: PluginContext, data: Any) -> PluginResult:
        """Handle hook events"""
        try:
            if hook_name in ["StealthApply", "BrowserLaunch", "PageLoad"]:
                # Execute the plugin when relevant hooks are triggered
                return await self.execute(context)
            
            return PluginResult(
                success=True,
                data={"message": f"Hook '{hook_name}' not handled by stealth plugin"}
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    # IStealthPlugin specific methods
    async def apply_to_context(self, browser_context: BrowserContext, config: Dict[str, Any]) -> PluginResult:
        """Apply stealth modifications to browser context"""
        try:
            await self.old_plugin.apply_to_context(browser_context)
            return PluginResult(
                success=True,
                data={"applied_to_context": True}
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    async def apply_to_page(self, page: Page, config: Dict[str, Any]) -> PluginResult:
        """Apply stealth modifications to specific page"""
        try:
            await self.old_plugin.apply_to_page(page)
            return PluginResult(
                success=True,
                data={"applied_to_page": True}
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    async def test_evasion(self, page: Page) -> Dict[str, Any]:
        """Test effectiveness of evasion techniques"""
        # For legacy plugins, we provide basic detection tests
        results = {}
        
        try:
            # Test webdriver flag
            results["webdriver"] = await page.evaluate("navigator.webdriver")
            
            # Test Chrome runtime
            results["chrome"] = await page.evaluate("typeof window.chrome !== 'undefined'")
            
            # Test plugins
            results["plugins_length"] = await page.evaluate("navigator.plugins.length")
            
            # Basic bot detection
            is_detected = results.get("webdriver", False) or results.get("plugins_length", 0) == 0
            results["is_bot_detected"] = is_detected
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def get_evasion_techniques(self) -> List[str]:
        """Get list of evasion techniques implemented"""
        # Map old plugin types to techniques
        technique_map = {
            "webdriver_flag": ["webdriver_removal", "navigator_modification"],
            "chrome_runtime": ["chrome_object_injection"],
            "plugins_array": ["plugin_spoofing"],
            "webgl_vendor": ["webgl_fingerprint_spoofing"],
            "languages": ["language_spoofing"],
            "permissions": ["permissions_api"],
            "user_agent": ["user_agent_spoofing"],
            "canvas_noise": ["canvas_fingerprint_noise"]
        }
        
        plugin_name = self.old_plugin.get_name()
        return technique_map.get(plugin_name, [plugin_name])


class StealthManagerIntegration:
    """Integration layer between old StealthManager and new plugin system"""
    
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.stealth_manager = StealthManager(auto_load_defaults=False)
        self.adapted_plugins = {}
        
    async def migrate_stealth_plugins(self) -> None:
        """Migrate existing stealth plugins to new system"""
        
        logger.info("Migrating legacy stealth plugins to new plugin system...")
        
        # Get all default stealth plugins
        for old_plugin in self.stealth_manager._default_plugins:
            plugin_name = old_plugin.get_name()
            
            # Create adapter
            adapter = StealthPluginAdapter(old_plugin)
            self.adapted_plugins[plugin_name] = adapter
            
            # Add to plugin manager registry manually (bypass loading)
            from .plugin_manager import PluginInfo
            plugin_info = PluginInfo(
                plugin=adapter,
                metadata=adapter.get_metadata(),
                state=PluginState.LOADED,
                dependencies_resolved=True
            )
            
            self.plugin_manager.registry.plugins[plugin_name] = plugin_info
            
            # Initialize the plugin
            context = PluginContext(
                plugin_name=plugin_name,
                config={}
            )
            
            result = await adapter.initialize(context)
            if result.success:
                plugin_info.state = PluginState.ACTIVE
                
                # Register hooks
                await self.plugin_manager.register_plugin_hooks(adapter, adapter.get_metadata())
                
                logger.debug(f"Migrated stealth plugin: {plugin_name}")
            else:
                logger.error(f"Failed to initialize migrated plugin {plugin_name}: {result.error}")
        
        logger.info(f"Successfully migrated {len(self.adapted_plugins)} stealth plugins")
    
    async def apply_stealth_to_context(self, context: BrowserContext, plugins: Optional[List[str]] = None) -> None:
        """Apply stealth plugins to browser context using new system"""
        
        # Determine which plugins to apply
        if plugins:
            active_plugins = plugins
        else:
            active_plugins = [
                name for name, info in self.plugin_manager.registry.plugins.items()
                if (info.metadata.plugin_type == PluginType.STEALTH and 
                    info.state == PluginState.ACTIVE)
            ]
        
        # Sort by priority
        plugin_items = [
            (name, self.plugin_manager.registry.plugins[name])
            for name in active_plugins
            if name in self.plugin_manager.registry.plugins
        ]
        plugin_items.sort(key=lambda x: x[1].metadata.priority)
        
        # Apply each plugin
        for plugin_name, plugin_info in plugin_items:
            try:
                plugin_context = PluginContext(
                    plugin_name=plugin_name,
                    config={},
                    browser_context=context
                )
                
                # Execute the stealth plugin
                result = await plugin_info.plugin.execute(plugin_context)
                
                if result.success:
                    logger.debug(f"Applied stealth plugin to context: {plugin_name}")
                else:
                    logger.error(f"Failed to apply stealth plugin {plugin_name}: {result.error}")
                    
            except Exception as e:
                logger.error(f"Error applying stealth plugin {plugin_name}: {e}")
    
    async def apply_stealth_to_page(self, page: Page, plugins: Optional[List[str]] = None) -> None:
        """Apply stealth plugins to page using new system"""
        
        # Similar to apply_stealth_to_context but for pages
        if plugins:
            active_plugins = plugins
        else:
            active_plugins = [
                name for name, info in self.plugin_manager.registry.plugins.items()
                if (info.metadata.plugin_type == PluginType.STEALTH and 
                    info.state == PluginState.ACTIVE)
            ]
        
        # Sort by priority
        plugin_items = [
            (name, self.plugin_manager.registry.plugins[name])
            for name in active_plugins
            if name in self.plugin_manager.registry.plugins
        ]
        plugin_items.sort(key=lambda x: x[1].metadata.priority)
        
        # Apply each plugin
        for plugin_name, plugin_info in plugin_items:
            try:
                plugin_context = PluginContext(
                    plugin_name=plugin_name,
                    config={},
                    page=page
                )
                
                # Execute the stealth plugin
                result = await plugin_info.plugin.execute(plugin_context)
                
                if result.success:
                    logger.debug(f"Applied stealth plugin to page: {plugin_name}")
                else:
                    logger.error(f"Failed to apply stealth plugin {plugin_name}: {result.error}")
                    
            except Exception as e:
                logger.error(f"Error applying stealth plugin {plugin_name}: {e}")
    
    async def test_stealth_effectiveness(self, page: Page) -> Dict[str, Any]:
        """Test stealth effectiveness using all active stealth plugins"""
        
        results = {
            "overall_detection_risk": "low",
            "individual_tests": {},
            "recommendations": []
        }
        
        # Test each stealth plugin
        for plugin_name, plugin_info in self.plugin_manager.registry.plugins.items():
            if (plugin_info.metadata.plugin_type == PluginType.STEALTH and 
                plugin_info.state == PluginState.ACTIVE and
                isinstance(plugin_info.plugin, StealthPluginAdapter)):
                
                try:
                    test_result = await plugin_info.plugin.test_evasion(page)
                    results["individual_tests"][plugin_name] = test_result
                    
                    # Check for detection indicators
                    if test_result.get("is_bot_detected", False):
                        results["overall_detection_risk"] = "high"
                        results["recommendations"].append(f"Plugin '{plugin_name}' may not be effective")
                        
                except Exception as e:
                    logger.error(f"Failed to test stealth plugin {plugin_name}: {e}")
                    results["individual_tests"][plugin_name] = {"error": str(e)}
        
        # Overall assessment
        detection_count = sum(
            1 for test in results["individual_tests"].values()
            if test.get("is_bot_detected", False)
        )
        
        total_tests = len(results["individual_tests"])
        if detection_count == 0:
            results["overall_detection_risk"] = "low"
        elif detection_count < total_tests // 2:
            results["overall_detection_risk"] = "medium"
        else:
            results["overall_detection_risk"] = "high"
        
        logger.info(f"Stealth test complete - Risk: {results['overall_detection_risk']}")
        return results


async def integrate_legacy_stealth_system(plugin_manager) -> StealthManagerIntegration:
    """Create and initialize the stealth system integration"""
    
    integration = StealthManagerIntegration(plugin_manager)
    await integration.migrate_stealth_plugins()
    
    return integration