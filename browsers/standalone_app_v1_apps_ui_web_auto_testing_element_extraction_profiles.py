"""
Profile-based configurations for different use cases

This module defines various user profiles with specific configurations
for different roles and use cases in web crawling.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Define ElementType and DetectionMethod locally to avoid circular imports
class ElementType(Enum):
    """Enhanced element type classification"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    FORM = "form"
    NAVIGATION = "navigation"
    TABLE = "table"
    LIST = "list"
    IMAGE = "image"
    MODAL = "modal"
    DROPDOWN = "dropdown"
    TAB = "tab"
    ACCORDION = "accordion"
    CARD = "card"
    PAGINATION = "pagination"
    SEARCH = "search"
    FILTER = "filter"
    CAROUSEL = "carousel"
    TOOLTIP = "tooltip"
    BREADCRUMB = "breadcrumb"
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"
    PROGRESS_BAR = "progress_bar"
    LOADING_SPINNER = "loading_spinner"
    NOTIFICATION = "notification"
    ALERT = "alert"
    CHATBOT = "chatbot"
    VIDEO_PLAYER = "video_player"
    AUDIO_PLAYER = "audio_player"
    CALENDAR = "calendar"
    CHART = "chart"
    MAP = "map"
    SLIDER = "slider"
    RATING = "rating"
    SOCIAL_SHARE = "social_share"
    COMMENT_SECTION = "comment_section"
    PRICE_DISPLAY = "price_display"
    COUNTDOWN_TIMER = "countdown_timer"
    CAPTCHA = "captcha"


class DetectionMethod(Enum):
    """Method used to detect element"""
    RULE_BASED = "rule_based"
    SEMANTIC_AI = "semantic_ai"
    ML_CLASSIFICATION = "ml_classification"
    VISUAL_PATTERN = "visual_pattern"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    SHADOW_DOM = "shadow_dom"
    DYNAMIC_CONTENT = "dynamic_content"


class ProfileType(Enum):
    """Available profile types"""
    QA_MANUAL_TESTER = "qa_manual_tester"
    QA_AUTOMATION_TESTER = "qa_automation_tester"
    UX_DESIGNER = "ux_designer"
    UI_DESIGNER = "ui_designer"
    FRONTEND_DEVELOPER = "frontend_developer"
    BACKEND_DEVELOPER = "backend_developer"
    PRODUCT_MANAGER = "product_manager"
    ACCESSIBILITY_AUDITOR = "accessibility_auditor"
    SEO_SPECIALIST = "seo_specialist"
    SECURITY_TESTER = "security_tester"
    PERFORMANCE_TESTER = "performance_tester"
    CONTENT_CREATOR = "content_creator"


@dataclass
class ProfileConfig:
    """Configuration for a specific profile"""
    
    profile_name: str
    description: str
    
    # Element focus priorities
    priority_element_types: List[ElementType]
    secondary_element_types: List[ElementType]
    ignored_element_types: List[ElementType]
    
    # Detection preferences
    preferred_detection_methods: List[DetectionMethod]
    confidence_threshold: float
    
    # Crawling behavior
    max_depth: int
    max_pages: int
    focus_on_interactions: bool
    include_visual_analysis: bool
    include_accessibility_analysis: bool
    include_performance_analysis: bool
    
    # Anti-detection settings
    stealth_mode: bool
    human_simulation: bool
    
    # Output preferences
    include_test_scenarios: bool
    include_locator_strategies: bool
    include_semantic_analysis: bool
    include_ml_features: bool
    
    # Report focus areas
    report_sections: List[str]
    output_format: str
    
    # Custom extraction rules
    custom_selectors: Dict[str, List[str]]
    custom_patterns: List[Dict[str, Any]]


class ProfileManager:
    """Manages different user profiles and their configurations"""
    
    def __init__(self):
        self.profiles = self._initialize_profiles()
    
    def _initialize_profiles(self) -> Dict[str, ProfileConfig]:
        """Initialize all predefined profiles"""
        profiles = {}
        
        # QA Manual Tester Profile
        profiles[ProfileType.QA_MANUAL_TESTER.value] = ProfileConfig(
            profile_name="QA Manual Tester",
            description="Focus on interactive elements, forms, and user flows for manual testing",
            priority_element_types=[
                ElementType.BUTTON, ElementType.INPUT, ElementType.FORM,
                ElementType.LINK, ElementType.DROPDOWN, ElementType.MODAL,
                ElementType.TAB, ElementType.PAGINATION
            ],
            secondary_element_types=[
                ElementType.NAVIGATION, ElementType.TABLE, ElementType.SEARCH,
                ElementType.FILTER, ElementType.CAROUSEL
            ],
            ignored_element_types=[
                ElementType.FOOTER, ElementType.HEADER, ElementType.SIDEBAR
            ],
            preferred_detection_methods=[
                DetectionMethod.SEMANTIC_AI, DetectionMethod.RULE_BASED,
                DetectionMethod.BEHAVIORAL_ANALYSIS
            ],
            confidence_threshold=0.7,
            max_depth=3,
            max_pages=20,
            focus_on_interactions=True,
            include_visual_analysis=True,
            include_accessibility_analysis=True,
            include_performance_analysis=False,
            stealth_mode=False,
            human_simulation=True,
            include_test_scenarios=True,
            include_locator_strategies=True,
            include_semantic_analysis=True,
            include_ml_features=False,
            report_sections=[
                "interactive_elements", "user_flows", "test_scenarios",
                "accessibility_issues", "form_validation"
            ],
            output_format="detailed",
            custom_selectors={
                "error_messages": [".error", ".invalid", ".alert-danger", "[aria-invalid='true']"],
                "success_messages": [".success", ".valid", ".alert-success", ".confirmation"],
                "loading_indicators": [".loading", ".spinner", ".skeleton", "[data-loading='true']"]
            },
            custom_patterns=[
                {
                    "pattern_id": "form_validation",
                    "keywords": ["required", "invalid", "error", "validation"],
                    "context": "form_fields"
                }
            ]
        )
        
        # QA Automation Tester Profile
        profiles[ProfileType.QA_AUTOMATION_TESTER.value] = ProfileConfig(
            profile_name="QA Automation Tester",
            description="Focus on robust locators and automation-friendly elements",
            priority_element_types=[
                ElementType.BUTTON, ElementType.INPUT, ElementType.FORM,
                ElementType.LINK, ElementType.DROPDOWN, ElementType.TABLE
            ],
            secondary_element_types=[
                ElementType.MODAL, ElementType.TAB, ElementType.PAGINATION,
                ElementType.NAVIGATION, ElementType.SEARCH
            ],
            ignored_element_types=[
                ElementType.TOOLTIP, ElementType.FOOTER, ElementType.HEADER
            ],
            preferred_detection_methods=[
                DetectionMethod.RULE_BASED, DetectionMethod.SEMANTIC_AI
            ],
            confidence_threshold=0.8,
            max_depth=2,
            max_pages=15,
            focus_on_interactions=True,
            include_visual_analysis=False,
            include_accessibility_analysis=False,
            include_performance_analysis=False,
            stealth_mode=True,
            human_simulation=False,
            include_test_scenarios=True,
            include_locator_strategies=True,
            include_semantic_analysis=False,
            include_ml_features=True,
            report_sections=[
                "automation_locators", "page_objects", "test_data",
                "interaction_maps", "reliability_scores"
            ],
            output_format="automation_friendly",
            custom_selectors={
                "test_attributes": ["[data-testid]", "[data-test]", "[data-automation]", "[test-id]"],
                "stable_locators": ["[id]", "[name]", "[data-*]"],
                "dynamic_elements": ["[class*='random']", "[id*='generated']"]
            },
            custom_patterns=[
                {
                    "pattern_id": "automation_friendly",
                    "keywords": ["testid", "automation", "test"],
                    "context": "data_attributes"
                }
            ]
        )
        
        # UX Designer Profile
        profiles[ProfileType.UX_DESIGNER.value] = ProfileConfig(
            profile_name="UX Designer",
            description="Focus on user experience, flows, and interaction patterns",
            priority_element_types=[
                ElementType.NAVIGATION, ElementType.BUTTON, ElementType.FORM,
                ElementType.MODAL, ElementType.CAROUSEL, ElementType.TAB,
                ElementType.BREADCRUMB, ElementType.PAGINATION
            ],
            secondary_element_types=[
                ElementType.INPUT, ElementType.DROPDOWN, ElementType.SEARCH,
                ElementType.FILTER, ElementType.LINK
            ],
            ignored_element_types=[],
            preferred_detection_methods=[
                DetectionMethod.SEMANTIC_AI, DetectionMethod.VISUAL_PATTERN,
                DetectionMethod.BEHAVIORAL_ANALYSIS
            ],
            confidence_threshold=0.6,
            max_depth=4,
            max_pages=25,
            focus_on_interactions=True,
            include_visual_analysis=True,
            include_accessibility_analysis=True,
            include_performance_analysis=True,
            stealth_mode=False,
            human_simulation=True,
            include_test_scenarios=False,
            include_locator_strategies=False,
            include_semantic_analysis=True,
            include_ml_features=True,
            report_sections=[
                "user_flows", "interaction_patterns", "navigation_structure",
                "visual_hierarchy", "accessibility_compliance", "user_journey"
            ],
            output_format="ux_focused",
            custom_selectors={
                "navigation_elements": ["nav", ".navbar", ".menu", ".breadcrumb", "[role='navigation']"],
                "interactive_zones": [".clickable", "[onclick]", "button", "a", "[role='button']"],
                "content_areas": ["main", ".content", "article", "[role='main']"]
            },
            custom_patterns=[
                {
                    "pattern_id": "user_flow",
                    "keywords": ["next", "continue", "skip", "back", "finish"],
                    "context": "navigation_flow"
                }
            ]
        )
        
        # UI Designer Profile
        profiles[ProfileType.UI_DESIGNER.value] = ProfileConfig(
            profile_name="UI Designer",
            description="Focus on visual elements, layout, and design system components",
            priority_element_types=[
                ElementType.BUTTON, ElementType.INPUT, ElementType.CARD,
                ElementType.MODAL, ElementType.DROPDOWN, ElementType.TAB,
                ElementType.TOOLTIP, ElementType.PROGRESS_BAR, ElementType.SLIDER
            ],
            secondary_element_types=[
                ElementType.NAVIGATION, ElementType.TABLE, ElementType.FORM,
                ElementType.CAROUSEL, ElementType.ACCORDION
            ],
            ignored_element_types=[],
            preferred_detection_methods=[
                DetectionMethod.VISUAL_PATTERN, DetectionMethod.SEMANTIC_AI,
                DetectionMethod.RULE_BASED
            ],
            confidence_threshold=0.6,
            max_depth=3,
            max_pages=20,
            focus_on_interactions=False,
            include_visual_analysis=True,
            include_accessibility_analysis=True,
            include_performance_analysis=False,
            stealth_mode=False,
            human_simulation=False,
            include_test_scenarios=False,
            include_locator_strategies=False,
            include_semantic_analysis=True,
            include_ml_features=True,
            report_sections=[
                "visual_components", "design_patterns", "color_analysis",
                "typography", "spacing", "responsiveness", "component_library"
            ],
            output_format="design_focused",
            custom_selectors={
                "design_components": [".btn", ".card", ".badge", ".chip", ".avatar"],
                "layout_elements": [".container", ".grid", ".flex", ".row", ".col"],
                "typography": ["h1", "h2", "h3", "h4", "h5", "h6", "p", ".text-*"]
            },
            custom_patterns=[
                {
                    "pattern_id": "design_system",
                    "keywords": ["primary", "secondary", "success", "warning", "danger"],
                    "context": "design_tokens"
                }
            ]
        )
        
        # Frontend Developer Profile
        profiles[ProfileType.FRONTEND_DEVELOPER.value] = ProfileConfig(
            profile_name="Frontend Developer",
            description="Focus on code structure, components, and technical implementation",
            priority_element_types=[
                ElementType.FORM, ElementType.INPUT, ElementType.BUTTON,
                ElementType.TABLE, ElementType.MODAL, ElementType.DROPDOWN,
                ElementType.TAB, ElementType.CAROUSEL
            ],
            secondary_element_types=[
                ElementType.NAVIGATION, ElementType.LINK, ElementType.SEARCH,
                ElementType.FILTER, ElementType.PAGINATION
            ],
            ignored_element_types=[
                ElementType.TOOLTIP, ElementType.BREADCRUMB
            ],
            preferred_detection_methods=[
                DetectionMethod.RULE_BASED, DetectionMethod.SHADOW_DOM,
                DetectionMethod.DYNAMIC_CONTENT, DetectionMethod.ML_CLASSIFICATION
            ],
            confidence_threshold=0.8,
            max_depth=2,
            max_pages=15,
            focus_on_interactions=True,
            include_visual_analysis=False,
            include_accessibility_analysis=True,
            include_performance_analysis=True,
            stealth_mode=True,
            human_simulation=False,
            include_test_scenarios=False,
            include_locator_strategies=True,
            include_semantic_analysis=False,
            include_ml_features=True,
            report_sections=[
                "component_structure", "shadow_dom_elements", "dynamic_content",
                "performance_metrics", "accessibility_compliance", "code_patterns"
            ],
            output_format="technical",
            custom_selectors={
                "framework_components": ["[data-react]", "[data-vue]", "[data-angular]", "[ng-*]"],
                "custom_elements": ["*[is]", "*:not(div):not(span):not(p):not(a):not(button):not(input)"],
                "state_indicators": ["[data-state]", "[aria-expanded]", "[aria-selected]"]
            },
            custom_patterns=[
                {
                    "pattern_id": "spa_routing",
                    "keywords": ["route", "router", "navigation", "spa"],
                    "context": "single_page_app"
                }
            ]
        )
        
        # Accessibility Auditor Profile
        profiles[ProfileType.ACCESSIBILITY_AUDITOR.value] = ProfileConfig(
            profile_name="Accessibility Auditor",
            description="Focus on accessibility compliance and WCAG guidelines",
            priority_element_types=[
                ElementType.BUTTON, ElementType.INPUT, ElementType.FORM,
                ElementType.LINK, ElementType.NAVIGATION, ElementType.TABLE,
                ElementType.MODAL, ElementType.TAB
            ],
            secondary_element_types=[
                ElementType.DROPDOWN, ElementType.CAROUSEL, ElementType.ACCORDION,
                ElementType.SEARCH, ElementType.PAGINATION
            ],
            ignored_element_types=[],
            preferred_detection_methods=[
                DetectionMethod.SEMANTIC_AI, DetectionMethod.RULE_BASED,
                DetectionMethod.BEHAVIORAL_ANALYSIS
            ],
            confidence_threshold=0.9,
            max_depth=4,
            max_pages=30,
            focus_on_interactions=True,
            include_visual_analysis=True,
            include_accessibility_analysis=True,
            include_performance_analysis=False,
            stealth_mode=False,
            human_simulation=True,
            include_test_scenarios=True,
            include_locator_strategies=False,
            include_semantic_analysis=True,
            include_ml_features=False,
            report_sections=[
                "accessibility_violations", "aria_analysis", "keyboard_navigation",
                "screen_reader_compatibility", "color_contrast", "wcag_compliance"
            ],
            output_format="accessibility_focused",
            custom_selectors={
                "aria_elements": ["[aria-*]", "[role]"],
                "focusable_elements": ["[tabindex]", "button", "a", "input", "select", "textarea"],
                "headings": ["h1", "h2", "h3", "h4", "h5", "h6", "[role='heading']"]
            },
            custom_patterns=[
                {
                    "pattern_id": "accessibility_issues",
                    "keywords": ["alt", "aria", "label", "role", "tabindex"],
                    "context": "accessibility_attributes"
                }
            ]
        )
        
        return profiles
    
    def get_profile(self, profile_type: str) -> Optional[ProfileConfig]:
        """Get a specific profile configuration"""
        return self.profiles.get(profile_type)
    
    def list_profiles(self) -> List[str]:
        """List all available profile types"""
        return list(self.profiles.keys())
    
    def get_profile_description(self, profile_type: str) -> str:
        """Get description for a specific profile"""
        profile = self.get_profile(profile_type)
        return profile.description if profile else "Profile not found"
    
    def create_custom_profile(self, profile_config: ProfileConfig) -> str:
        """Create a custom profile"""
        profile_id = f"custom_{profile_config.profile_name.lower().replace(' ', '_')}"
        self.profiles[profile_id] = profile_config
        return profile_id
    
    def update_profile(self, profile_type: str, updates: Dict[str, Any]) -> bool:
        """Update an existing profile with new settings"""
        if profile_type not in self.profiles:
            return False
        
        profile = self.profiles[profile_type]
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        return True
    
    def get_profile_config_dict(self, profile_type: str) -> Dict[str, Any]:
        """Get profile configuration as dictionary"""
        profile = self.get_profile(profile_type)
        if not profile:
            return {}
        
        return asdict(profile)


def convert_profile_to_crawler_config(profile: ProfileConfig) -> Dict[str, Any]:
    """Convert profile configuration to crawler configuration"""
    return {
        "browser": "chromium",
        "headless": True,
        "anti_detection": {
            "randomize_delays": profile.stealth_mode,
            "min_delay": 0.5 if profile.human_simulation else 0.1,
            "max_delay": 2.0 if profile.human_simulation else 0.5,
            "randomize_viewport": profile.stealth_mode,
            "rotate_user_agents": profile.stealth_mode,
            "use_stealth_mode": profile.stealth_mode,
            "simulate_human_behavior": profile.human_simulation,
            "avoid_bot_patterns": profile.stealth_mode,
            "randomize_mouse_movements": profile.human_simulation
        },
        "retry_config": {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 30.0,
            "backoff_factor": 2.0
        },
        "logging": {
            "level": "INFO",
            "file": f"{profile.profile_name.lower().replace(' ', '_')}_crawler.log"
        },
        "monitoring": {
            "enabled": False
        },
        "profile": {
            "name": profile.profile_name,
            "type": profile.profile_name.lower().replace(' ', '_'),
            "config": asdict(profile)
        }
    }