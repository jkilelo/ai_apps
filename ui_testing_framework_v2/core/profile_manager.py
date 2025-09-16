"""
Profile manager for loading and managing YAML-based profiles
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, List
from .models import ProfileConfig


class ProfileManager:
    """Manages profile loading and caching"""
    
    def __init__(self, profiles_dir: Optional[Path] = None):
        """Initialize profile manager"""
        if profiles_dir is None:
            profiles_dir = Path(__file__).parent.parent / "profiles"
        
        self.profiles_dir = profiles_dir
        self._cache: Dict[str, ProfileConfig] = {}
        self._load_all_profiles()
    
    def _load_all_profiles(self):
        """Load all YAML profiles from directory"""
        if not self.profiles_dir.exists():
            return
        
        for yaml_file in self.profiles_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                if data and "name" in data:
                    profile = ProfileConfig(data)
                    self._cache[profile.name] = profile
            except Exception as e:
                print(f"Error loading profile {yaml_file}: {e}")
    
    def get_profile(self, name: str) -> Optional[ProfileConfig]:
        """Get profile by name"""
        return self._cache.get(name)
    
    def list_profiles(self) -> List[str]:
        """List all available profile names"""
        return list(self._cache.keys())
    
    def reload_profiles(self):
        """Reload all profiles from disk"""
        self._cache.clear()
        self._load_all_profiles()
    
    def create_custom_profile(self, config: Dict) -> ProfileConfig:
        """Create a custom profile from config dict"""
        return ProfileConfig(config)
    
    def get_or_default(self, name: Optional[str] = None) -> ProfileConfig:
        """Get profile or return general profile as default"""
        if name and name in self._cache:
            return self._cache[name]
        
        # Return general profile or create minimal default
        if "general" in self._cache:
            return self._cache["general"]
        
        # Create minimal default profile
        return ProfileConfig({
            "name": "default",
            "description": "Default profile",
            "filters": [],
            "scoring": {"weights": {"default": 0.5}},
            "settings": {"max_elements": 1000}
        })