#!/usr/bin/env python3
"""
Extraction Profile System for Elements Extractor
Implements Registry + Strategy patterns for specialized extraction profiles

Architecture:
- Registry Pattern: Central registry for all extraction profiles
- Strategy Pattern: Each profile implements different extraction strategies
- Decorator-based Registration: Easy profile registration
- Results Persistence: All results saved in profile-specific directories
"""

import json
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, Callable, Set
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


# ==================== PROFILE REGISTRY ====================

class ProfileRegistry:
    """
    Central registry for extraction profiles
    Uses singleton pattern to ensure single registry instance
    """
    _instance = None
    _profiles: Dict[str, Type['ExtractionProfile']] = {}
    _profile_instances: Dict[str, 'ExtractionProfile'] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, name: str, description: str = ""):
        """Decorator to register extraction profiles"""
        def decorator(profile_class: Type['ExtractionProfile']):
            profile_class._name = name
            profile_class._description = description
            cls._profiles[name] = profile_class
            return profile_class
        return decorator
    
    @classmethod
    def get_profile(cls, name: str, module_name: str = "elements_extractor_no_llm") -> Optional['ExtractionProfile']:
        """Get an instance of a registered profile"""
        if name not in cls._profiles:
            raise ValueError(f"Profile '{name}' not registered. Available profiles: {list(cls._profiles.keys())}")
        
        # Create a unique key for profile+module combination
        instance_key = f"{name}_{module_name}"
        
        # Use singleton instances for profiles per module
        if instance_key not in cls._profile_instances:
            cls._profile_instances[instance_key] = cls._profiles[name](module_name=module_name)
        
        return cls._profile_instances[instance_key]
    
    @classmethod
    def list_profiles(cls) -> Dict[str, str]:
        """List all registered profiles with descriptions"""
        return {
            name: profile_class._description 
            for name, profile_class in cls._profiles.items()
        }
    
    @classmethod
    def clear_registry(cls):
        """Clear all registered profiles (mainly for testing)"""
        cls._profiles.clear()
        cls._profile_instances.clear()


# ==================== BASE PROFILE ====================

class ProfileConfig(BaseModel):
    """Base configuration for all extraction profiles"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Core settings
    name: str = Field(..., description="Profile name")
    description: str = Field(default="", description="Profile description")
    version: str = Field(default="1.0.0", description="Profile version")
    
    # Extraction settings
    element_limit: int = Field(default=1000, ge=1, le=10000)
    timeout: float = Field(default=30.0, ge=1.0, le=300.0)
    
    # Filtering settings
    filter_invisible: bool = Field(default=True)
    filter_duplicates: bool = Field(default=True)
    min_element_size: int = Field(default=0, ge=0)
    
    # Output settings
    save_screenshots: bool = Field(default=False)
    save_html: bool = Field(default=False)
    compress_output: bool = Field(default=False)
    
    # Custom profile settings (override in subclasses)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class ExtractionProfile(ABC):
    """
    Abstract base class for extraction profiles
    Each profile implements a specific extraction strategy
    """
    
    _name: str = "base"
    _description: str = "Base extraction profile"
    
    def __init__(self, config: Optional[ProfileConfig] = None, module_name: str = "elements_extractor_no_llm"):
        self.config = config or self.get_default_config()
        self.module_name = module_name
        self.results_dir = self._setup_results_directory(module_name)
    
    @abstractmethod
    def get_default_config(self) -> ProfileConfig:
        """Return default configuration for this profile"""
        pass
    
    @abstractmethod
    def score_element(self, element: Dict[str, Any]) -> float:
        """
        Score an element's relevance for this profile (0.0 to 1.0)
        Higher scores indicate more relevant elements
        """
        pass
    
    @abstractmethod
    def filter_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter elements based on profile-specific criteria
        """
        pass
    
    @abstractmethod
    def categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize elements into profile-specific groups
        """
        pass
    
    @abstractmethod
    def generate_insights(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate profile-specific insights from extracted elements
        """
        pass
    
    def _setup_results_directory(self, module_name: str = "elements_extractor_no_llm") -> Path:
        """Setup profile-specific results directory relative to script location
        
        Directory structure:
        extraction_results/
        ├── elements_extractor_no_llm/
        │   ├── qa/
        │   ├── interactive/
        │   └── ...
        ├── elements_extractor_with_llm/
        │   ├── qa/
        │   └── ...
        └── other_modules/
            └── ...
        """
        # Get the directory where this script is located
        script_dir = Path(__file__).parent.resolve()
        base_dir = script_dir / "extraction_results" / module_name / self._name
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir
    
    def save_results(self, 
                    url: str,
                    elements: List[Dict[str, Any]], 
                    metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        Save extraction results with full state persistence
        Results are saved in: extraction_results/{profile_name}/{timestamp}_{url_hash}.json
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{timestamp}_{url_hash}.json"
        filepath = self.results_dir / filename
        
        # Prepare results document
        results = {
            "profile": self._name,
            "version": self.config.version,
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "config": self.config.model_dump(),
            "statistics": {
                "total_elements": len(elements),
                "filtered_elements": len(self.filter_elements(elements)),
                "categories": {
                    cat: len(elems) 
                    for cat, elems in self.categorize_elements(elements).items()
                }
            },
            "insights": self.generate_insights(elements),
            "elements": elements,
            "metadata": metadata or {}
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Also save a latest.json symlink/copy for easy access
        latest_path = self.results_dir / "latest.json"
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        return filepath
    
    def load_results(self, filepath: Optional[Path] = None) -> Dict[str, Any]:
        """Load previously saved results"""
        if filepath is None:
            filepath = self.results_dir / "latest.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Results file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_results_history(self) -> List[Dict[str, Any]]:
        """Get history of all saved results for this profile"""
        history = []
        for filepath in sorted(self.results_dir.glob("*.json")):
            if filepath.name == "latest.json":
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history.append({
                        "filepath": str(filepath),
                        "timestamp": data.get("timestamp"),
                        "url": data.get("url"),
                        "element_count": data.get("statistics", {}).get("total_elements", 0)
                    })
            except Exception:
                continue
        
        return history


# ==================== QA ENGINEER PROFILE ====================

@ProfileRegistry.register("qa", "Senior QA Engineer focused extraction")
class QAEngineerProfile(ExtractionProfile):
    """
    Extraction profile optimized for QA engineers
    Focuses on testable, interactive elements
    """
    
    def get_default_config(self) -> ProfileConfig:
        return ProfileConfig(
            name="qa",
            description="QA Engineer Profile - Focus on testable interactive elements",
            version="1.0.0",
            element_limit=500,
            filter_invisible=True,
            filter_duplicates=True,
            min_element_size=10,
            custom_settings={
                "min_interaction_score": 0.7,
                "include_disabled": True,  # For negative testing
                "include_hidden_toggles": True,  # For modal/dropdown testing
                "track_validation": True,
                "track_error_states": True
            }
        )
    
    def score_element(self, element: Dict[str, Any]) -> float:
        """Score element relevance for QA testing"""
        score = 0.0
        
        # Interactive elements get high scores
        interactive_tags = ['input', 'button', 'select', 'textarea', 'a']
        if element.get('tag_name', '').lower() in interactive_tags:
            score += 0.5
        
        # Form elements
        if element.get('tag_name', '').lower() in ['form', 'fieldset', 'label']:
            score += 0.3
        
        # Elements with event handlers
        event_attrs = ['onclick', 'onchange', 'onsubmit', 'onfocus', 'onblur']
        attrs = element.get('attributes', {})
        if any(attr in attrs for attr in event_attrs):
            score += 0.3
        
        # Elements with validation attributes
        validation_attrs = ['required', 'pattern', 'min', 'max', 'minlength', 'maxlength']
        if any(attr in attrs for attr in validation_attrs):
            score += 0.2
        
        # ARIA interactive roles
        aria_role = attrs.get('role', '')
        interactive_roles = ['button', 'checkbox', 'radio', 'textbox', 'combobox', 'menu']
        if aria_role in interactive_roles:
            score += 0.3
        
        # Disabled elements (for negative testing)
        if attrs.get('disabled') or attrs.get('aria-disabled') == 'true':
            score += 0.1
        
        return min(score, 1.0)
    
    def filter_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter elements relevant for QA testing"""
        min_score = self.config.custom_settings.get("min_interaction_score", 0.7)
        filtered = []
        
        for element in elements:
            score = self.score_element(element)
            
            # Add score to element metadata
            element['qa_score'] = score
            
            # Include if score meets threshold
            if score >= min_score:
                filtered.append(element)
            # Also include disabled elements if configured
            elif self.config.custom_settings.get("include_disabled"):
                attrs = element.get('attributes', {})
                if attrs.get('disabled') or attrs.get('aria-disabled') == 'true':
                    filtered.append(element)
        
        return filtered
    
    def categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize elements by QA test type"""
        categories = {
            'input_validation': [],
            'navigation': [],
            'forms': [],
            'actions': [],
            'disabled': [],
            'hidden_interactive': [],
            'aria_elements': []
        }
        
        for element in elements:
            tag = element.get('tag_name', '').lower()
            attrs = element.get('attributes', {})
            
            # Input validation elements
            if tag in ['input', 'textarea', 'select']:
                categories['input_validation'].append(element)
            
            # Navigation elements
            if tag == 'a' or attrs.get('role') == 'link':
                categories['navigation'].append(element)
            
            # Form elements
            if tag in ['form', 'fieldset', 'input', 'select', 'textarea', 'button']:
                categories['forms'].append(element)
            
            # Action elements
            if tag == 'button' or attrs.get('role') == 'button':
                categories['actions'].append(element)
            
            # Disabled elements
            if attrs.get('disabled') or attrs.get('aria-disabled') == 'true':
                categories['disabled'].append(element)
            
            # Hidden but interactive
            style = element.get('computed_style', {})
            if style.get('display') == 'none' or style.get('visibility') == 'hidden':
                if self.score_element(element) > 0.5:
                    categories['hidden_interactive'].append(element)
            
            # ARIA elements
            if 'role' in attrs or any(k.startswith('aria-') for k in attrs.keys()):
                categories['aria_elements'].append(element)
        
        return categories
    
    def generate_insights(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate QA-specific insights"""
        filtered = self.filter_elements(elements)
        categories = self.categorize_elements(filtered)
        
        return {
            'test_coverage': {
                'total_testable': len(filtered),
                'input_fields': len(categories['input_validation']),
                'navigation_links': len(categories['navigation']),
                'action_buttons': len(categories['actions']),
                'forms': len(set(e.get('parent_selector', '') for e in categories['forms'] if e.get('tag_name') == 'form')),
                'disabled_elements': len(categories['disabled']),
                'hidden_interactive': len(categories['hidden_interactive']),
                'aria_compliant': len(categories['aria_elements'])
            },
            'test_recommendations': self._generate_test_recommendations(categories),
            'accessibility_score': self._calculate_accessibility_score(filtered),
            'form_complexity': self._analyze_form_complexity(categories['forms'])
        }
    
    def _generate_test_recommendations(self, categories: Dict[str, List]) -> List[str]:
        """Generate specific test recommendations"""
        recommendations = []
        
        if categories['input_validation']:
            recommendations.append("Test input validation with boundary values and invalid data")
        
        if categories['disabled']:
            recommendations.append(f"Perform negative testing on {len(categories['disabled'])} disabled elements")
        
        if categories['hidden_interactive']:
            recommendations.append(f"Test {len(categories['hidden_interactive'])} hidden interactive elements for modal/dropdown functionality")
        
        if not categories['aria_elements']:
            recommendations.append("Consider adding ARIA attributes for better accessibility testing")
        
        return recommendations
    
    def _calculate_accessibility_score(self, elements: List[Dict[str, Any]]) -> float:
        """Calculate accessibility score based on ARIA compliance"""
        if not elements:
            return 0.0
        
        aria_count = sum(1 for e in elements if 'role' in e.get('attributes', {}))
        return (aria_count / len(elements)) * 100
    
    def _analyze_form_complexity(self, form_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze form complexity for testing prioritization"""
        if not form_elements:
            return {"complexity": "none", "fields": 0}
        
        field_count = len([e for e in form_elements if e.get('tag_name', '').lower() in ['input', 'select', 'textarea']])
        
        if field_count == 0:
            complexity = "none"
        elif field_count <= 5:
            complexity = "simple"
        elif field_count <= 15:
            complexity = "moderate"
        else:
            complexity = "complex"
        
        return {
            "complexity": complexity,
            "fields": field_count,
            "requires_comprehensive_testing": field_count > 10
        }


# ==================== ACCESSIBILITY PROFILE ====================

@ProfileRegistry.register("accessibility", "WCAG compliance and accessibility testing")
class AccessibilityProfile(ExtractionProfile):
    """
    Extraction profile for accessibility testing
    Focuses on WCAG compliance and screen reader compatibility
    """
    
    def get_default_config(self) -> ProfileConfig:
        return ProfileConfig(
            name="accessibility",
            description="Accessibility Profile - WCAG compliance and screen reader testing",
            version="1.0.0",
            element_limit=1000,
            filter_invisible=False,  # Include hidden elements for screen readers
            custom_settings={
                "check_wcag_level": "AA",
                "check_color_contrast": True,
                "check_focus_order": True,
                "check_landmarks": True
            }
        )
    
    def score_element(self, element: Dict[str, Any]) -> float:
        """Score element for accessibility relevance"""
        score = 0.0
        attrs = element.get('attributes', {})
        
        # Elements needing accessibility attention
        if not attrs.get('alt') and element.get('tag_name', '').lower() == 'img':
            score += 0.8  # Missing alt text
        
        # Interactive elements without labels
        if element.get('tag_name', '').lower() in ['input', 'select', 'textarea']:
            if not attrs.get('aria-label') and not attrs.get('aria-labelledby'):
                score += 0.7
        
        # ARIA attributes present
        if any(k.startswith('aria-') for k in attrs.keys()):
            score += 0.5
        
        # Landmark roles
        if attrs.get('role') in ['banner', 'navigation', 'main', 'complementary', 'contentinfo']:
            score += 0.6
        
        # Headings (important for structure)
        if element.get('tag_name', '').lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            score += 0.5
        
        return min(score, 1.0)
    
    def filter_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter elements relevant for accessibility testing"""
        return [e for e in elements if self.score_element(e) > 0.3]
    
    def categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize by accessibility concerns"""
        categories = {
            'missing_alt_text': [],
            'missing_labels': [],
            'missing_aria': [],
            'landmarks': [],
            'headings': [],
            'focusable': []
        }
        
        for element in elements:
            tag = element.get('tag_name', '').lower()
            attrs = element.get('attributes', {})
            
            # Check for missing alt text
            if tag == 'img' and not attrs.get('alt'):
                categories['missing_alt_text'].append(element)
            
            # Check for missing labels
            if tag in ['input', 'select', 'textarea']:
                if not attrs.get('aria-label') and not attrs.get('aria-labelledby'):
                    categories['missing_labels'].append(element)
            
            # Check for missing ARIA
            if tag in ['button', 'a', 'input'] and not any(k.startswith('aria-') for k in attrs.keys()):
                categories['missing_aria'].append(element)
            
            # Landmarks
            if attrs.get('role') in ['banner', 'navigation', 'main', 'complementary', 'contentinfo']:
                categories['landmarks'].append(element)
            
            # Headings
            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                categories['headings'].append(element)
            
            # Focusable elements
            if attrs.get('tabindex') or tag in ['a', 'button', 'input', 'select', 'textarea']:
                categories['focusable'].append(element)
        
        return categories
    
    def generate_insights(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate accessibility insights"""
        categories = self.categorize_elements(elements)
        
        return {
            'wcag_issues': {
                'missing_alt_text': len(categories['missing_alt_text']),
                'missing_labels': len(categories['missing_labels']),
                'missing_aria': len(categories['missing_aria'])
            },
            'structure': {
                'landmarks': len(categories['landmarks']),
                'headings': len(categories['headings']),
                'heading_hierarchy': self._check_heading_hierarchy(categories['headings'])
            },
            'keyboard_navigation': {
                'focusable_elements': len(categories['focusable']),
                'tab_order_defined': self._check_tab_order(categories['focusable'])
            },
            'compliance_score': self._calculate_compliance_score(categories)
        }
    
    def _check_heading_hierarchy(self, headings: List[Dict[str, Any]]) -> str:
        """Check if heading hierarchy is correct"""
        if not headings:
            return "No headings found"
        
        levels = [int(h.get('tag_name', 'h1')[1]) for h in headings]
        
        # Check for skipped levels
        for i in range(1, len(levels)):
            if levels[i] - levels[i-1] > 1:
                return "Warning: Heading levels skip (bad for screen readers)"
        
        return "Heading hierarchy appears correct"
    
    def _check_tab_order(self, focusable: List[Dict[str, Any]]) -> bool:
        """Check if tab order is explicitly defined"""
        return any(e.get('attributes', {}).get('tabindex') for e in focusable)
    
    def _calculate_compliance_score(self, categories: Dict[str, List]) -> float:
        """Calculate overall accessibility compliance score"""
        issues = (
            len(categories['missing_alt_text']) +
            len(categories['missing_labels']) +
            len(categories['missing_aria'])
        )
        
        total = sum(len(v) for v in categories.values())
        
        if total == 0:
            return 100.0
        
        return max(0, (1 - issues / total)) * 100


# ==================== PERFORMANCE PROFILE ====================

@ProfileRegistry.register("performance", "Performance and optimization analysis")
class PerformanceProfile(ExtractionProfile):
    """
    Extraction profile for performance analysis
    Focuses on elements affecting page load and runtime performance
    """
    
    def get_default_config(self) -> ProfileConfig:
        return ProfileConfig(
            name="performance",
            description="Performance Profile - Analyze elements affecting page performance",
            version="1.0.0",
            custom_settings={
                "check_image_optimization": True,
                "check_lazy_loading": True,
                "check_async_loading": True,
                "track_dom_depth": True
            }
        )
    
    def score_element(self, element: Dict[str, Any]) -> float:
        """Score element for performance impact"""
        score = 0.0
        tag = element.get('tag_name', '').lower()
        attrs = element.get('attributes', {})
        
        # Images without lazy loading
        if tag == 'img':
            if not attrs.get('loading'):
                score += 0.6
            if not attrs.get('width') or not attrs.get('height'):
                score += 0.3  # Missing dimensions cause reflow
        
        # Scripts without async/defer
        if tag == 'script':
            if not attrs.get('async') and not attrs.get('defer'):
                score += 0.8
        
        # Large inline styles
        if attrs.get('style', ''):
            if len(attrs['style']) > 100:
                score += 0.4
        
        # Iframes (performance impact)
        if tag == 'iframe':
            score += 0.7
        
        return min(score, 1.0)
    
    def filter_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter elements affecting performance"""
        return [e for e in elements if self.score_element(e) > 0.2]
    
    def categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize by performance impact"""
        categories = {
            'unoptimized_images': [],
            'blocking_scripts': [],
            'inline_styles': [],
            'iframes': [],
            'heavy_dom': []
        }
        
        for element in elements:
            tag = element.get('tag_name', '').lower()
            attrs = element.get('attributes', {})
            
            if tag == 'img' and not attrs.get('loading'):
                categories['unoptimized_images'].append(element)
            
            if tag == 'script' and not attrs.get('async') and not attrs.get('defer'):
                categories['blocking_scripts'].append(element)
            
            if attrs.get('style') and len(attrs['style']) > 100:
                categories['inline_styles'].append(element)
            
            if tag == 'iframe':
                categories['iframes'].append(element)
            
            # Check DOM depth (nested elements)
            if element.get('xpath', '').count('/') > 10:
                categories['heavy_dom'].append(element)
        
        return categories
    
    def generate_insights(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate performance insights"""
        categories = self.categorize_elements(elements)
        
        return {
            'performance_issues': {
                'unoptimized_images': len(categories['unoptimized_images']),
                'blocking_scripts': len(categories['blocking_scripts']),
                'inline_styles': len(categories['inline_styles']),
                'iframes': len(categories['iframes']),
                'deep_dom_elements': len(categories['heavy_dom'])
            },
            'optimization_opportunities': self._generate_optimizations(categories),
            'estimated_impact': self._estimate_performance_impact(categories)
        }
    
    def _generate_optimizations(self, categories: Dict[str, List]) -> List[str]:
        """Generate optimization recommendations"""
        optimizations = []
        
        if categories['unoptimized_images']:
            optimizations.append(f"Add lazy loading to {len(categories['unoptimized_images'])} images")
        
        if categories['blocking_scripts']:
            optimizations.append(f"Add async/defer to {len(categories['blocking_scripts'])} scripts")
        
        if categories['inline_styles']:
            optimizations.append(f"Move {len(categories['inline_styles'])} inline styles to CSS files")
        
        return optimizations
    
    def _estimate_performance_impact(self, categories: Dict[str, List]) -> str:
        """Estimate overall performance impact"""
        score = 0
        score += len(categories['blocking_scripts']) * 3
        score += len(categories['unoptimized_images']) * 2
        score += len(categories['iframes']) * 4
        
        if score < 5:
            return "Low impact"
        elif score < 15:
            return "Medium impact"
        else:
            return "High impact - optimization recommended"


# ==================== INTERACTIVE ELEMENTS PROFILE ====================

@ProfileRegistry.register("interactive", "Pure focus on interactive elements only")
class InteractiveElementsProfile(ExtractionProfile):
    """
    Extraction profile purely focused on interactive elements
    Filters out all non-interactive content
    """
    
    def get_default_config(self) -> ProfileConfig:
        return ProfileConfig(
            name="interactive",
            description="Interactive Elements Profile - Extract only clickable, editable, and actionable elements",
            version="1.0.0",
            element_limit=1000,
            filter_invisible=True,
            filter_duplicates=True,
            min_element_size=5,
            custom_settings={
                "min_interaction_score": 0.5,
                "include_hover_only": False,
                "include_focusable": True,
                "strict_interactive": True
            }
        )
    
    def score_element(self, element: Dict[str, Any]) -> float:
        """Score element based on interactivity"""
        score = 0.0
        tag = element.get('tag_name', '').lower()
        attrs = element.get('attributes', {})
        
        # Highly interactive elements
        highly_interactive = ['button', 'input', 'select', 'textarea', 'a']
        if tag in highly_interactive:
            score = 1.0
        
        # Form-related elements
        elif tag in ['form', 'label', 'fieldset', 'optgroup', 'option']:
            score = 0.8
        
        # Elements with explicit click handlers
        elif any(attr.startswith('on') for attr in attrs.keys()):
            score = 0.9
        
        # Elements with interactive ARIA roles
        interactive_roles = [
            'button', 'link', 'menuitem', 'option', 'radio', 'switch',
            'tab', 'textbox', 'checkbox', 'combobox', 'slider', 'spinbutton'
        ]
        if attrs.get('role') in interactive_roles:
            score = max(score, 0.9)
        
        # Elements with tabindex (keyboard navigable)
        if 'tabindex' in attrs and attrs['tabindex'] != '-1':
            score = max(score, 0.7)
        
        # Clickable or editable flags
        if element.get('is_clickable'):
            score = max(score, 0.8)
        if element.get('is_editable'):
            score = max(score, 0.9)
        
        # Video/audio controls
        if tag in ['video', 'audio']:
            score = 0.7
        
        # Canvas elements (potentially interactive)
        if tag == 'canvas':
            score = 0.6
        
        # Details/summary elements
        if tag in ['details', 'summary']:
            score = 0.8
        
        return score
    
    def filter_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter to only interactive elements"""
        min_score = self.config.custom_settings.get("min_interaction_score", 0.5)
        strict = self.config.custom_settings.get("strict_interactive", True)
        
        filtered = []
        for element in elements:
            score = self.score_element(element)
            element['interaction_score'] = score
            
            # In strict mode, only include elements with high interaction scores
            if strict:
                if score >= 0.7:
                    filtered.append(element)
            else:
                if score >= min_score:
                    filtered.append(element)
        
        # Sort by interaction score (most interactive first)
        filtered.sort(key=lambda x: x.get('interaction_score', 0), reverse=True)
        
        return filtered
    
    def categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize by interaction type"""
        categories = {
            'clickable': [],
            'editable': [],
            'navigational': [],
            'form_controls': [],
            'media_controls': [],
            'keyboard_accessible': [],
            'touch_interactive': []
        }
        
        for element in elements:
            tag = element.get('tag_name', '').lower()
            attrs = element.get('attributes', {})
            
            # Clickable elements
            if element.get('is_clickable') or tag in ['button', 'a'] or attrs.get('onclick'):
                categories['clickable'].append(element)
            
            # Editable elements
            if element.get('is_editable') or tag in ['input', 'textarea', 'select']:
                categories['editable'].append(element)
            
            # Navigation elements
            if tag == 'a' or attrs.get('role') == 'link' or tag == 'nav':
                categories['navigational'].append(element)
            
            # Form controls
            if tag in ['input', 'select', 'textarea', 'button', 'label', 'fieldset']:
                categories['form_controls'].append(element)
            
            # Media controls
            if tag in ['video', 'audio', 'button'] and any(
                'play' in str(attrs.get('class', '')).lower() or
                'pause' in str(attrs.get('class', '')).lower() or
                'media' in str(attrs.get('class', '')).lower()
                for attr in ['class', 'id']
            ):
                categories['media_controls'].append(element)
            
            # Keyboard accessible
            if 'tabindex' in attrs or tag in ['a', 'button', 'input', 'select', 'textarea']:
                categories['keyboard_accessible'].append(element)
            
            # Touch interactive (mobile-friendly)
            if any(attr in attrs for attr in ['ontouchstart', 'ontouchend', 'ontouchmove']):
                categories['touch_interactive'].append(element)
        
        return categories
    
    def generate_insights(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights about interactive elements"""
        categories = self.categorize_elements(elements)
        
        # Calculate interaction complexity
        total_interactive = len(elements)
        complexity = "simple"
        if total_interactive > 50:
            complexity = "complex"
        elif total_interactive > 20:
            complexity = "moderate"
        
        # Check for accessibility
        keyboard_accessible = len(categories['keyboard_accessible'])
        accessibility_ratio = keyboard_accessible / total_interactive if total_interactive > 0 else 0
        
        return {
            'interaction_summary': {
                'total_interactive': total_interactive,
                'clickable': len(categories['clickable']),
                'editable': len(categories['editable']),
                'navigational': len(categories['navigational']),
                'form_controls': len(categories['form_controls']),
                'media_controls': len(categories['media_controls']),
                'keyboard_accessible': keyboard_accessible,
                'touch_interactive': len(categories['touch_interactive'])
            },
            'interaction_complexity': complexity,
            'keyboard_accessibility': {
                'ratio': accessibility_ratio * 100,
                'assessment': 'good' if accessibility_ratio > 0.8 else 'needs improvement'
            },
            'top_interaction_types': self._get_top_interaction_types(elements),
            'recommendations': self._generate_interaction_recommendations(categories)
        }
    
    def _get_top_interaction_types(self, elements: List[Dict[str, Any]]) -> List[str]:
        """Get the most common interaction types"""
        interaction_counts = {}
        
        for element in elements:
            interactions = element.get('interaction_types', [])
            for interaction in interactions:
                interaction_counts[interaction] = interaction_counts.get(interaction, 0) + 1
        
        # Sort by count and return top 5
        sorted_interactions = sorted(interaction_counts.items(), key=lambda x: x[1], reverse=True)
        return [interaction for interaction, _ in sorted_interactions[:5]]
    
    def _generate_interaction_recommendations(self, categories: Dict[str, List]) -> List[str]:
        """Generate recommendations for interaction testing"""
        recommendations = []
        
        if len(categories['clickable']) > 20:
            recommendations.append("High number of clickable elements - consider automation testing")
        
        if len(categories['editable']) > 10:
            recommendations.append("Multiple input fields - implement comprehensive validation testing")
        
        if len(categories['keyboard_accessible']) < len(categories['clickable']) * 0.8:
            recommendations.append("Some interactive elements may not be keyboard accessible")
        
        if not categories['media_controls'] and categories['navigational']:
            recommendations.append("No media controls detected - verify if media elements exist")
        
        return recommendations


# ==================== GENERAL PROFILE ====================

@ProfileRegistry.register("general", "General purpose extraction with comprehensive coverage")
class GeneralProfile(ExtractionProfile):
    """
    General extraction profile - comprehensive element extraction
    Balanced approach suitable for most use cases
    """
    
    def get_default_config(self) -> ProfileConfig:
        return ProfileConfig(
            name="general",
            description="General Profile - Comprehensive balanced extraction",
            version="1.0.0",
            element_limit=2000,
            filter_invisible=True,
            filter_duplicates=True
        )
    
    def score_element(self, element: Dict[str, Any]) -> float:
        """Balanced scoring for general extraction"""
        # All visible elements get base score
        return 0.5
    
    def filter_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Minimal filtering for comprehensive extraction"""
        # Return all elements that meet basic criteria
        return elements
    
    def categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize by element type"""
        categories = {}
        
        for element in elements:
            tag = element.get('tag_name', 'unknown').lower()
            if tag not in categories:
                categories[tag] = []
            categories[tag].append(element)
        
        return categories
    
    def generate_insights(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate general insights"""
        categories = self.categorize_elements(elements)
        
        return {
            'element_distribution': {
                tag: len(elems) for tag, elems in categories.items()
            },
            'total_elements': len(elements),
            'unique_tags': len(categories),
            'interactive_elements': sum(
                len(elems) for tag, elems in categories.items()
                if tag in ['a', 'button', 'input', 'select', 'textarea']
            )
        }


# ==================== UTILITY FUNCTIONS ====================

def list_available_profiles() -> Dict[str, str]:
    """List all available extraction profiles"""
    return ProfileRegistry.list_profiles()


def get_profile(name: str, module_name: str = "elements_extractor_no_llm") -> ExtractionProfile:
    """Get an extraction profile by name"""
    return ProfileRegistry.get_profile(name, module_name)


def create_custom_profile(name: str, 
                         description: str,
                         base_profile: str = "general") -> Type[ExtractionProfile]:
    """
    Create a custom profile based on an existing profile
    Useful for creating variations of existing profiles
    """
    base = ProfileRegistry.get_profile(base_profile)
    
    class CustomProfile(base.__class__):
        _name = name
        _description = description
    
    # Register the custom profile
    ProfileRegistry._profiles[name] = CustomProfile
    
    return CustomProfile


if __name__ == "__main__":
    # Example usage
    print("Available Extraction Profiles:")
    for name, desc in list_available_profiles().items():
        print(f"  - {name}: {desc}")
    
    # Example: Using QA profile
    qa_profile = get_profile("qa")
    print(f"\nQA Profile Config: {qa_profile.config.model_dump()}")
    
    # The profile system is ready to be integrated with elements_extractor_no_llm.py