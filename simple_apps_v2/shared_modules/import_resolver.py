"""
Dynamic Import Resolver
=======================
A modern, robust solution for handling cross-package imports in Python projects.
This module provides utilities to dynamically resolve and import modules from
various locations in the project structure without hardcoding paths.
"""

import sys
import os
import importlib
import importlib.util
from pathlib import Path
from typing import Optional, Any, List, Tuple
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class ImportResolver:
    """
    A dynamic import resolver that can find and import modules from various
    locations in the project structure.
    """
    
    def __init__(self, search_patterns: Optional[List[str]] = None):
        """
        Initialize the import resolver.
        
        Args:
            search_patterns: List of directory patterns to search for modules.
                            Defaults to common project structure patterns.
        """
        self.search_patterns = search_patterns or [
            "utils",
            "shared_modules", 
            "backend/shared",
            "../utils",
            "../../utils",
            "../../../utils",
            "../../../../utils",
            "../shared_modules",
            "../../shared_modules",
            "../backend/shared"
        ]
        self._module_cache = {}
        self._path_cache = {}
    
    @lru_cache(maxsize=128)
    def find_project_root(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """
        Find the project root by looking for common project markers.
        
        Args:
            start_path: Starting path for the search. Defaults to current file location.
            
        Returns:
            Path to project root or None if not found.
        """
        if start_path is None:
            # Get the directory of the calling module
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_file = frame.f_back.f_code.co_filename
                start_path = Path(caller_file).parent
            else:
                start_path = Path.cwd()
        
        current = Path(start_path).resolve()
        
        # Project root markers in order of preference
        markers = [
            ".git",
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            ".venv",
            "venv",
            "package.json",  # For mixed projects
        ]
        
        # Search up the directory tree
        while current != current.parent:
            for marker in markers:
                if (current / marker).exists():
                    logger.debug(f"Found project root at {current} (marker: {marker})")
                    return current
            current = current.parent
        
        logger.warning("Could not find project root")
        return None
    
    @lru_cache(maxsize=128)
    def find_module_path(self, module_name: str, start_path: Optional[Path] = None) -> Optional[Path]:
        """
        Find the path to a module by searching in various locations.
        
        Args:
            module_name: Name of the module to find (e.g., 'platform_utils')
            start_path: Starting path for the search
            
        Returns:
            Path to the module or None if not found
        """
        # Check cache first
        cache_key = (module_name, str(start_path))
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]
        
        # Find project root
        project_root = self.find_project_root(start_path)
        if not project_root:
            project_root = Path.cwd()
        
        # Search locations
        search_locations = []
        
        # Add current directory
        if start_path:
            search_locations.append(Path(start_path))
        
        # Add project root
        search_locations.append(project_root)
        
        # Add pattern-based locations
        for pattern in self.search_patterns:
            if pattern.startswith(".."):
                # Relative patterns from start_path
                if start_path:
                    search_locations.append(Path(start_path) / pattern)
            else:
                # Patterns from project root
                search_locations.append(project_root / pattern)
        
        # Also check parent directories up to project root
        if start_path:
            current = Path(start_path).parent
            while current >= project_root and current != current.parent:
                search_locations.append(current)
                search_locations.append(current / "utils")
                search_locations.append(current / "shared_modules")
                current = current.parent
        
        # Search for the module
        for location in search_locations:
            if not location.exists():
                continue
            
            # Check for Python module file
            module_file = location / f"{module_name}.py"
            if module_file.exists():
                logger.debug(f"Found module {module_name} at {module_file}")
                self._path_cache[cache_key] = module_file
                return module_file
            
            # Check for package directory
            module_dir = location / module_name
            if module_dir.exists() and (module_dir / "__init__.py").exists():
                logger.debug(f"Found package {module_name} at {module_dir}")
                self._path_cache[cache_key] = module_dir
                return module_dir
        
        logger.warning(f"Could not find module {module_name}")
        return None
    
    def import_module(self, module_name: str, start_path: Optional[Path] = None) -> Any:
        """
        Dynamically import a module from various locations.
        
        Args:
            module_name: Name of the module to import
            start_path: Starting path for the search
            
        Returns:
            The imported module
            
        Raises:
            ImportError: If the module cannot be found or imported
        """
        # Check cache
        if module_name in self._module_cache:
            return self._module_cache[module_name]
        
        # Find module path
        module_path = self.find_module_path(module_name, start_path)
        if not module_path:
            # Try standard import as fallback
            try:
                module = importlib.import_module(module_name)
                self._module_cache[module_name] = module
                return module
            except ImportError:
                raise ImportError(f"Cannot find module '{module_name}'")
        
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if not spec or not spec.loader:
            raise ImportError(f"Cannot load module '{module_name}' from {module_path}")
        
        module = importlib.util.module_from_spec(spec)
        
        # Add parent directory to sys.path temporarily
        parent_dir = str(module_path.parent)
        sys_path_added = False
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            sys_path_added = True
        
        try:
            spec.loader.exec_module(module)
            self._module_cache[module_name] = module
            
            # Also add to sys.modules for consistency
            sys.modules[module_name] = module
            
            return module
        finally:
            # Clean up sys.path
            if sys_path_added and parent_dir in sys.path:
                sys.path.remove(parent_dir)
    
    def import_from(self, module_name: str, *names: str, start_path: Optional[Path] = None) -> Tuple[Any, ...]:
        """
        Import specific names from a module.
        
        Args:
            module_name: Name of the module to import from
            *names: Names to import from the module
            start_path: Starting path for the search
            
        Returns:
            Tuple of imported objects
            
        Raises:
            ImportError: If the module or names cannot be imported
        """
        module = self.import_module(module_name, start_path)
        
        results = []
        for name in names:
            if not hasattr(module, name):
                raise ImportError(f"Cannot import '{name}' from module '{module_name}'")
            results.append(getattr(module, name))
        
        return tuple(results) if len(results) > 1 else results[0] if results else None


# Global resolver instance
_global_resolver = ImportResolver()


def dynamic_import(module_name: str, start_path: Optional[str] = None) -> Any:
    """
    Convenience function to dynamically import a module.
    
    Args:
        module_name: Name of the module to import
        start_path: Starting path for the search (optional)
        
    Returns:
        The imported module
    """
    import inspect
    
    # If no start_path provided, use the caller's directory
    if start_path is None:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_file = frame.f_back.f_code.co_filename
            start_path = Path(caller_file).parent
    else:
        start_path = Path(start_path)
    
    return _global_resolver.import_module(module_name, start_path)


def dynamic_import_from(module_name: str, *names: str, start_path: Optional[str] = None) -> Tuple[Any, ...]:
    """
    Convenience function to import specific names from a module.
    
    Args:
        module_name: Name of the module to import from
        *names: Names to import from the module
        start_path: Starting path for the search (optional)
        
    Returns:
        Tuple of imported objects (or single object if only one name)
    """
    import inspect
    
    # If no start_path provided, use the caller's directory
    if start_path is None:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_file = frame.f_back.f_code.co_filename
            start_path = Path(caller_file).parent
    else:
        start_path = Path(start_path)
    
    return _global_resolver.import_from(module_name, *names, start_path=start_path)


def setup_import_paths(additional_patterns: Optional[List[str]] = None):
    """
    Setup import paths for the current environment.
    
    Args:
        additional_patterns: Additional search patterns to add
    """
    global _global_resolver
    
    if additional_patterns:
        _global_resolver.search_patterns.extend(additional_patterns)
    
    # Find and add project root to sys.path if not already there
    project_root = _global_resolver.find_project_root()
    if project_root and str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


# Auto-setup on import
setup_import_paths()