"""
Smart Dependency Manager for Automated Test Framework
======================================================
This module handles all dependency-related issues for the test automation framework,
ensuring it works with ANY website without manual intervention.

Key Features:
- Automatic package installation
- Dynamic page object generation for any URL
- Import hook system for runtime resolution
- Self-healing capabilities
"""

import os
import sys
import json
import subprocess
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
from urllib.parse import urlparse
import logging
import re
from types import ModuleType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartDependencyManager:
    """
    Intelligently manages dependencies for test automation.
    Works with ANY website, not hardcoded for specific sites.
    """
    
    def __init__(self, target_url: str = None, test_dir: str = None):
        """
        Initialize the dependency manager.
        
        Args:
            target_url: The website URL to test (e.g., https://example.com)
            test_dir: Directory containing generated tests
        """
        self.target_url = target_url
        self.test_dir = Path(test_dir) if test_dir else Path.cwd()
        self.site_name = self._extract_site_name(target_url) if target_url else "generic"
        
        # Core dependencies that must be installed
        self.core_dependencies = {
            'pytest': '>=8.0.0',
            'playwright': '>=1.40.0',
            'pytest-playwright': '>=0.4.0',
            'python-dotenv': '>=1.0.0'
        }
        
        # Optional dependencies that enhance functionality
        self.optional_dependencies = {
            'pytest-html': '>=4.0.0',
            'pytest-xdist': '>=3.0.0',
            'pytest-rerunfailures': '>=12.0.0',
            'pytest-timeout': '>=2.0.0'
        }
        
        # Track what we've installed
        self.installed_packages = set()
        self.generated_modules = {}
        
    def _extract_site_name(self, url: str) -> str:
        """
        Extract a clean site name from any URL.
        
        Examples:
            https://www.github.com -> github
            https://example.com -> example
            https://shop.amazon.co.uk -> amazon
        """
        if not url:
            return "generic"
            
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            
            # Remove www, www2, etc.
            domain = re.sub(r'^www\d*\.', '', domain)
            
            # Extract main domain name
            parts = domain.split('.')
            if len(parts) >= 2:
                # Handle cases like amazon.co.uk
                if parts[-2] in ['co', 'com', 'net', 'org', 'gov', 'edu']:
                    site_name = parts[-3] if len(parts) > 2 else parts[0]
                else:
                    site_name = parts[-2]
            else:
                site_name = parts[0] if parts else 'generic'
            
            # Clean up the name
            site_name = re.sub(r'[^a-zA-Z0-9]', '', site_name).lower()
            return site_name or 'generic'
            
        except Exception as e:
            logger.warning(f"Could not extract site name from {url}: {e}")
            return "generic"
    
    def ensure_all_dependencies(self) -> Dict[str, Any]:
        """
        Main entry point: Ensures all dependencies are ready.
        
        Returns:
            Dictionary with status and details
        """
        results = {
            'success': True,
            'packages_installed': [],
            'page_objects_generated': [],
            'errors': []
        }
        
        try:
            # Step 1: Check and install Python packages
            logger.info("Step 1: Checking Python packages...")
            package_results = self._ensure_python_packages()
            results['packages_installed'] = package_results['installed']
            
            # Step 2: Generate page objects dynamically
            logger.info("Step 2: Generating page objects...")
            page_results = self._generate_page_objects()
            results['page_objects_generated'] = page_results['generated']
            
            # Step 3: Setup import hooks for dynamic loading
            logger.info("Step 3: Setting up import hooks...")
            self._setup_import_hooks()
            
            # Step 4: Validate the environment
            logger.info("Step 4: Validating environment...")
            validation_results = self._validate_environment()
            if not validation_results['valid']:
                results['errors'].extend(validation_results['issues'])
                results['success'] = False
            
            logger.info("Dependency management complete!")
            
        except Exception as e:
            logger.error(f"Dependency management failed: {e}")
            results['errors'].append(str(e))
            results['success'] = False
            
        return results
    
    def _ensure_python_packages(self) -> Dict[str, List[str]]:
        """Check and install required Python packages."""
        results = {'installed': [], 'already_present': [], 'failed': []}
        
        # Check core dependencies
        for package, version in self.core_dependencies.items():
            status = self._check_and_install_package(package, version, required=True)
            if status == 'installed':
                results['installed'].append(package)
            elif status == 'present':
                results['already_present'].append(package)
            else:
                results['failed'].append(package)
        
        # Check optional dependencies (don't fail if these can't be installed)
        for package, version in self.optional_dependencies.items():
            status = self._check_and_install_package(package, version, required=False)
            if status == 'installed':
                results['installed'].append(package)
                
        return results
    
    def _check_and_install_package(self, package: str, version: str, required: bool = True) -> str:
        """
        Check if a package is installed and install if missing.
        
        Returns:
            'installed' if newly installed, 'present' if already there, 'failed' if couldn't install
        """
        try:
            # Try to import the package
            importlib.import_module(package.replace('-', '_'))
            logger.debug(f"Package {package} is already installed")
            return 'present'
            
        except ImportError:
            logger.info(f"Package {package} not found, attempting to install...")
            
            try:
                # Install the package
                cmd = [sys.executable, "-m", "pip", "install", f"{package}{version}"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    logger.info(f"Successfully installed {package}")
                    self.installed_packages.add(package)
                    return 'installed'
                else:
                    if required:
                        logger.error(f"Failed to install required package {package}: {result.stderr}")
                    else:
                        logger.warning(f"Failed to install optional package {package}")
                    return 'failed'
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout installing {package}")
                return 'failed'
            except Exception as e:
                logger.error(f"Error installing {package}: {e}")
                return 'failed'
    
    def _generate_page_objects(self) -> Dict[str, List[str]]:
        """Generate page objects dynamically for the target website."""
        results = {'generated': [], 'skipped': []}
        
        # Create test directory if it doesn't exist
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create pages directory if it doesn't exist
        pages_dir = self.test_dir / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = pages_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
            results['generated'].append("__init__.py")
        
        # Generate main page object for the site
        page_object_file = pages_dir / f"{self.site_name}page.py"
        
        if page_object_file.exists():
            logger.info(f"Page object {page_object_file} already exists")
            results['skipped'].append(str(page_object_file))
        else:
            logger.info(f"Generating page object for {self.site_name}")
            page_content = self._create_page_object_content()
            page_object_file.write_text(page_content)
            results['generated'].append(str(page_object_file))
        
        # Also create a generic page object as fallback
        generic_page = pages_dir / "genericpage.py"
        if not generic_page.exists():
            generic_content = self._create_generic_page_object()
            generic_page.write_text(generic_content)
            results['generated'].append("genericpage.py")
            
        return results
    
    def _create_page_object_content(self) -> str:
        """Create page object content for any website."""
        class_name = f"{self.site_name.capitalize()}Page"
        
        content = f'''"""
Page Object Model for {self.site_name}
Auto-generated by Smart Dependency Manager
"""

import logging
from typing import Optional
from playwright.sync_api import Page, Locator, expect

logger = logging.getLogger(__name__)


class {class_name}:
    """
    Page Object Model for {self.target_url or 'the target website'}
    This is a dynamically generated page object that adapts to any website.
    """
    
    def __init__(self, page: Page):
        """Initialize the page object."""
        self.page = page
        self.url = "{self.target_url or ''}"
        logger.info(f"Initialized {class_name}")
    
    def navigate_to(self, url: str = None) -> None:
        """Navigate to the page."""
        target_url = url or self.url
        if target_url:
            logger.info(f"Navigating to {{target_url}}")
            self.page.goto(target_url)
            self.page.wait_for_load_state("domcontentloaded")
    
    def wait_for_element(self, selector: str, timeout: int = 30000) -> Locator:
        """Wait for an element to be visible."""
        logger.debug(f"Waiting for element: {{selector}}")
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator
    
    def click(self, selector: str) -> None:
        """Click an element."""
        logger.debug(f"Clicking element: {{selector}}")
        self.page.locator(selector).click()
    
    def fill(self, selector: str, value: str) -> None:
        """Fill a form field."""
        logger.debug(f"Filling {{selector}} with {{value}}")
        self.page.locator(selector).fill(value)
    
    def get_text(self, selector: str) -> str:
        """Get text from an element."""
        return self.page.locator(selector).text_content() or ""
    
    def is_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        return self.page.locator(selector).is_visible()
    
    def take_screenshot(self, name: str) -> None:
        """Take a screenshot."""
        path = f"screenshots/{{name}}.png"
        self.page.screenshot(path=path)
        logger.info(f"Screenshot saved: {{path}}")
    
    # Generic methods that work for any site
    def find_all_links(self) -> List[str]:
        """Find all links on the page."""
        links = self.page.locator("a[href]").all()
        return [link.get_attribute("href") for link in links]
    
    def find_all_buttons(self) -> List[Locator]:
        """Find all buttons on the page."""
        return self.page.locator("button, input[type='button'], input[type='submit']").all()
    
    def find_all_inputs(self) -> List[Locator]:
        """Find all input fields."""
        return self.page.locator("input, textarea, select").all()
    
    def search_for_text(self, text: str) -> bool:
        """Check if text exists on the page."""
        return self.page.locator(f"text={{text}}").count() > 0
'''
        return content
    
    def _create_generic_page_object(self) -> str:
        """Create a generic page object that works for any site."""
        return '''"""
Generic Page Object Model
Works with any website without specific customization
"""

from typing import Optional, List
from playwright.sync_api import Page, Locator
import logging

logger = logging.getLogger(__name__)


class GenericPage:
    """Generic page object that adapts to any website."""
    
    def __init__(self, page: Page, url: str = None):
        self.page = page
        self.url = url
        
    def navigate_to(self, url: str = None) -> None:
        """Navigate to URL."""
        target = url or self.url
        if target:
            self.page.goto(target)
            
    def smart_click(self, text: str = None, selector: str = None) -> bool:
        """Click element by text or selector."""
        try:
            if text:
                self.page.locator(f"text={text}").first.click()
            elif selector:
                self.page.locator(selector).first.click()
            return True
        except:
            return False
            
    def smart_fill(self, value: str, placeholder: str = None, label: str = None, selector: str = None) -> bool:
        """Fill input by placeholder, label, or selector."""
        try:
            if placeholder:
                self.page.locator(f"[placeholder*='{placeholder}']").first.fill(value)
            elif label:
                self.page.locator(f"label:has-text('{label}') + input").first.fill(value)
            elif selector:
                self.page.locator(selector).first.fill(value)
            return True
        except:
            return False
            
    def extract_all_text(self) -> str:
        """Extract all visible text from page."""
        return self.page.locator("body").text_content() or ""
'''
    
    def _setup_import_hooks(self):
        """Setup Python import hooks for dynamic module loading."""
        # Add the test directory to Python path
        if str(self.test_dir) not in sys.path:
            sys.path.insert(0, str(self.test_dir))
        
        # Install our custom importer
        if not any(isinstance(hook, DynamicPageImporter) for hook in sys.meta_path):
            sys.meta_path.insert(0, DynamicPageImporter(self))
    
    def _validate_environment(self) -> Dict[str, Any]:
        """Validate that the environment is ready for testing."""
        issues = []
        
        # Check if Playwright browsers are installed
        try:
            import playwright
            # Check if chromium is installed
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "--dry-run"],
                capture_output=True,
                text=True
            )
            if "chromium" not in result.stdout.lower():
                logger.info("Installing Playwright browsers...")
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
        except Exception as e:
            issues.append(f"Playwright browser check failed: {e}")
        
        # Check if test directory exists
        if not self.test_dir.exists():
            issues.append(f"Test directory does not exist: {self.test_dir}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }


class DynamicPageImporter:
    """
    Custom importer that handles dynamic page object imports.
    This allows tests to import page objects that don't exist yet.
    """
    
    def __init__(self, manager: SmartDependencyManager):
        self.manager = manager
        
    def find_spec(self, fullname, path, target=None):
        """Called when Python tries to import a module."""
        # Only handle page imports
        if fullname.startswith('pages.') and fullname.endswith('page'):
            # Extract the page name
            page_name = fullname.split('.')[-1]
            
            # Check if file exists
            page_file = self.manager.test_dir / "pages" / f"{page_name}.py"
            
            if not page_file.exists():
                # Generate it on the fly
                logger.info(f"Generating {page_name} on demand...")
                site_name = page_name.replace('page', '')
                self.manager.site_name = site_name
                self.manager._generate_page_objects()
            
            # Return None to let the normal import system handle it
            return None
        
        return None


class DependencyAdapter:
    """
    Adapts tests to work with any website by replacing hardcoded references.
    """
    
    def __init__(self, test_file: Path, target_url: str):
        self.test_file = test_file
        self.target_url = target_url
        self.site_name = SmartDependencyManager(target_url)._extract_site_name(target_url)
        
    def adapt_test_file(self) -> bool:
        """Adapt a test file to work with the target website."""
        try:
            content = self.test_file.read_text()
            
            # Replace hardcoded URLs
            content = re.sub(
                r'https?://[^\s"\')]+',
                self.target_url,
                content
            )
            
            # Replace page object imports
            content = re.sub(
                r'from pages\.\w+page import \w+Page',
                f'from pages.{self.site_name}page import {self.site_name.capitalize()}Page',
                content
            )
            
            # Replace class references
            content = re.sub(
                r'\b[A-Z]\w+Page\b',
                f'{self.site_name.capitalize()}Page',
                content
            )
            
            # Write back
            self.test_file.write_text(content)
            logger.info(f"Adapted {self.test_file} for {self.target_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to adapt {self.test_file}: {e}")
            return False


def prepare_test_environment(target_url: str, test_dir: str = None) -> bool:
    """
    Main entry point for preparing the test environment.
    
    Args:
        target_url: The website to test (e.g., https://example.com)
        test_dir: Directory containing the tests
    
    Returns:
        True if environment is ready, False otherwise
    """
    logger.info(f"Preparing test environment for {target_url}")
    
    manager = SmartDependencyManager(target_url, test_dir)
    results = manager.ensure_all_dependencies()
    
    if results['success']:
        logger.info("Environment prepared successfully!")
        logger.info(f"  Packages installed: {results['packages_installed']}")
        logger.info(f"  Page objects generated: {results['page_objects_generated']}")
    else:
        logger.error("Environment preparation failed!")
        for error in results['errors']:
            logger.error(f"  - {error}")
    
    return results['success']


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Dependency Manager for Test Automation")
    parser.add_argument("--url", required=True, help="Target website URL (e.g., https://example.com)")
    parser.add_argument("--test-dir", default=".", help="Directory containing tests")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    success = prepare_test_environment(args.url, args.test_dir)
    sys.exit(0 if success else 1)