"""Stealth configuration, enums, and data models extracted from monolith.

This module centralizes core data structures to enable modular reuse and
progressive decomposition of `stealth_browser.py`.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class StealthLevel(Enum):
    BASIC = "basic"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"
    PARANOID = "paranoid"


class ExtractionStrategy(Enum):
    DOM = "dom"
    VISUAL = "visual"
    ACCESSIBILITY = "accessibility"
    SHADOW_DOM = "shadow_dom"
    SEMANTIC_AI = "semantic_ai"
    ML_CLASSIFICATION = "ml_classification"
    HYBRID = "hybrid"


class ElementType(Enum):
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    FORM = "form"
    TABLE = "table"
    IMAGE = "image"
    VIDEO = "video"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    MODAL = "modal"
    NAVIGATION = "navigation"
    PAGINATION = "pagination"
    CAPTCHA = "captcha"
    UNKNOWN = "unknown"


@dataclass
class StealthConfig:
    level: StealthLevel = StealthLevel.MAXIMUM
    headless: bool = False
    hide_webdriver: bool = True
    hide_automation_indicators: bool = True
    spoof_plugins: bool = True
    spoof_languages: bool = True
    spoof_chrome_runtime: bool = True
    prevent_webrtc_leak: bool = True
    spoof_canvas_fingerprint: bool = True
    spoof_webgl: bool = True
    spoof_battery: bool = True
    spoof_hardware: bool = True
    bypass_csp: bool = True
    block_webrtc: bool = True
    bypass_cloudflare: bool = True
    bypass_f5_networks: bool = True
    bypass_shape_security: bool = True
    bypass_datadome: bool = True
    bypass_kasada: bool = True
    bypass_perimeter_x: bool = True
    enable_human_typing: bool = True
    enable_human_mouse: bool = True
    enable_human_scrolling: bool = True
    enable_human_delays: bool = True
    enable_micro_behaviors: bool = True
    use_bspline_mouse: bool = True
    use_lognormal_delays: bool = True
    detect_frameworks: bool = True
    detect_captcha: bool = True
    handle_cookies: bool = True
    build_trust: bool = False
    trust_domains: List[str] = field(default_factory=lambda: ["google.com", "github.com"])
    parallel_extraction: bool = True
    max_retry_attempts: int = 3
    timeout: int = 60
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    locale: str = "en-US"
    timezone: str = "America/New_York"
    human_delay_range: Tuple[int, int] = (100, 2000)
    typing_delay_range: Tuple[int, int] = (50, 200)
    mouse_delay_range: Tuple[int, int] = (10, 50)


@dataclass
class ElementData:
    element_id: str
    element_type: ElementType
    tag_name: str
    xpath: str
    css_selector: str
    text_content: str = ""
    inner_html: str = ""
    outer_html: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    id: Optional[str] = None
    class_names: List[str] = field(default_factory=list)
    name: Optional[str] = None
    href: Optional[str] = None
    src: Optional[str] = None
    is_visible: bool = False
    is_clickable: bool = False
    is_enabled: bool = True
    is_focusable: bool = False
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    role: Optional[str] = None
    aria_label: Optional[str] = None
    aria_description: Optional[str] = None
    tab_index: Optional[int] = None
    confidence_score: float = 1.0
    extraction_strategy: str = "unknown"
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    framework_detected: Optional[str] = None
    parent_xpath: Optional[str] = None
    children_count: int = 0
    sibling_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["element_type"] = self.element_type.value
        data["extraction_timestamp"] = self.extraction_timestamp.isoformat()
        return data


@dataclass
class ExtractionResult:
    url: str
    success: bool
    elements: List[ElementData]
    page_title: str = ""
    framework_detected: Optional[str] = None
    captcha_detected: bool = False
    captcha_type: Optional[str] = None
    extraction_time: float = 0
    retry_count: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "success": self.success,
            "elements": [e.to_dict() for e in self.elements],
            "page_title": self.page_title,
            "framework_detected": self.framework_detected,
            "captcha_detected": self.captcha_detected,
            "captcha_type": self.captcha_type,
            "extraction_time": self.extraction_time,
            "retry_count": self.retry_count,
            "errors": self.errors,
            "metadata": self.metadata,
            "timestamp": datetime.now().isoformat(),
        }


__all__ = [
    "StealthLevel",
    "ExtractionStrategy",
    "ElementType",
    "StealthConfig",
    "ElementData",
    "ExtractionResult",
]
