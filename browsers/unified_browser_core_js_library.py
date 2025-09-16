"""
JavaScript library loader for browser automation.

This module loads JavaScript from actual .js files to follow best practices,
similar to how playwright-stealth works. This ensures better maintainability,
syntax highlighting, and separation of concerns.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import os


class JSLibrary:
    """Load and manage JavaScript files for browser automation."""
    
    def __init__(self):
        """Initialize JS library with file paths."""
        self.js_dir = Path(__file__).parent / "js"
        self._cache: Dict[str, str] = {}
        
    def _load_js_file(self, filename: str) -> str:
        """
        Load JavaScript content from a file with caching.
        
        Args:
            filename: Name of the JS file (without path)
            
        Returns:
            JavaScript content as string
        """
        if filename in self._cache:
            return self._cache[filename]
            
        file_path = self.js_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"JavaScript file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self._cache[filename] = content
        return content
    
    # ============================================================================
    # STEALTH & ANTI-DETECTION
    # ============================================================================
    
    def get_webdriver_override(self) -> str:
        """Load webdriver override JavaScript."""
        return self._load_js_file("webdriver.override.js")
    
    def get_navigator_spoofing(self) -> str:
        """Load navigator spoofing JavaScript."""
        return self._load_js_file("navigator.spoof.js")
    
    def get_canvas_noise(self) -> str:
        """Load canvas fingerprinting protection JavaScript."""
        return self._load_js_file("canvas.fingerprint.js")
    
    def get_webrtc_block(self) -> str:
        """Load WebRTC blocking JavaScript."""
        return self._load_js_file("webrtc.block.js")
    
    def get_permission_override(self) -> str:
        """Load permission API override JavaScript."""
        return self._load_js_file("permissions.override.js")
    
    def get_human_like_mouse_movement(self) -> str:
        """Load human-like mouse movement JavaScript."""
        return self._load_js_file("mouse.humanize.js")
    
    # ============================================================================
    # ELEMENT UTILITIES
    # ============================================================================
    
    def get_element_utils(self) -> str:
        """Load element utility functions JavaScript."""
        return self._load_js_file("element.utils.js")
    
    def get_element_visibility_check(self) -> str:
        """Get element visibility check function from utils."""
        utils = self.get_element_utils()
        # Extract just the isElementVisible function
        return f"""
        {utils}
        isElementVisible;
        """
    
    def get_element_interaction_check(self) -> str:
        """Get element interaction check function from utils."""
        utils = self.get_element_utils()
        # Extract just the isInteractive function
        return f"""
        {utils}
        isInteractive;
        """
    
    def get_text_content_extractor(self) -> str:
        """Get text extraction function from utils."""
        utils = self.get_element_utils()
        # Extract just the getCleanText function
        return f"""
        {utils}
        getCleanText;
        """
    
    def get_wait_for_element(self) -> str:
        """Get wait for element function from utils."""
        utils = self.get_element_utils()
        # Extract just the waitForElement function
        return f"""
        {utils}
        waitForElement;
        """
    
    def get_xpath_resolver(self) -> str:
        """Get XPath resolver function from utils."""
        utils = self.get_element_utils()
        # Extract just the getElementByXPath function  
        return f"""
        {utils}
        getElementByXPath;
        """
    
    # ============================================================================
    # STEALTH PROFILES
    # ============================================================================
    
    def get_stealth_bundle(self, 
                          webdriver: bool = True,
                          navigator: bool = True,
                          canvas: bool = True,
                          webrtc: bool = True,
                          permissions: bool = True) -> str:
        """
        Get a bundle of stealth scripts based on configuration.
        
        Args:
            webdriver: Include webdriver override
            navigator: Include navigator spoofing
            canvas: Include canvas fingerprinting protection
            webrtc: Include WebRTC blocking
            permissions: Include permission overrides
            
        Returns:
            Combined JavaScript bundle
        """
        scripts = []
        
        if webdriver:
            scripts.append(self.get_webdriver_override())
        if navigator:
            scripts.append(self.get_navigator_spoofing())
        if canvas:
            scripts.append(self.get_canvas_noise())
        if webrtc:
            scripts.append(self.get_webrtc_block())
        if permissions:
            scripts.append(self.get_permission_override())
            
        return self.combine_scripts(*scripts)
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    @staticmethod
    def combine_scripts(*scripts: str) -> str:
        """
        Combine multiple JavaScript snippets into a single executable script.
        
        Args:
            *scripts: Variable number of JavaScript strings
            
        Returns:
            Combined JavaScript wrapped in IIFE
        """
        # Filter out empty scripts
        valid_scripts = [s for s in scripts if s and s.strip()]
        
        if not valid_scripts:
            return ""
            
        # Combine with semicolons to ensure proper separation
        combined = ";\n".join(valid_scripts)
        
        # Wrap in IIFE to avoid global scope pollution
        return f"""
        (function() {{
            'use strict';
            {combined}
        }})();
        """
    
    @staticmethod
    def wrap_in_try_catch(script: str, error_return: Any = None) -> str:
        """
        Wrap JavaScript in try-catch for error safety.
        
        Args:
            script: JavaScript code to wrap
            error_return: Value to return on error
            
        Returns:
            Wrapped JavaScript with error handling
        """
        return f"""
        (function() {{
            try {{
                {script}
            }} catch(e) {{
                console.error('Script error:', e);
                return {repr(error_return)};
            }}
        }})();
        """
    
    def get_all_files(self) -> List[str]:
        """
        Get list of all available JavaScript files.
        
        Returns:
            List of JavaScript filenames
        """
        if not self.js_dir.exists():
            return []
            
        return [f.name for f in self.js_dir.glob("*.js")]
    
    def preload_all(self) -> None:
        """Preload all JavaScript files into cache for better performance."""
        for filename in self.get_all_files():
            self._load_js_file(filename)
    
    def clear_cache(self) -> None:
        """Clear the JavaScript file cache."""
        self._cache.clear()
    
    def get_file_path(self, filename: str) -> Path:
        """
        Get full path to a JavaScript file.
        
        Args:
            filename: Name of the JS file
            
        Returns:
            Full path to the file
        """
        return self.js_dir / filename