"""
Core models for the improved extraction framework v2
Simplified, efficient, and type-safe
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Protocol
from datetime import datetime
from enum import Enum
import hashlib
import json


class ElementType(str, Enum):
    """Element types - simplified"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    TEXT = "text"
    IMAGE = "image"
    FORM = "form"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    OTHER = "other"


@dataclass
class Element:
    """Simplified element model - only essential fields"""
    selector: str
    tag_name: str
    element_type: ElementType
    text: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_visible: bool = True
    is_interactive: bool = False
    interaction_score: float = 0.0
    bounding_box: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "selector": self.selector,
            "tag_name": self.tag_name,
            "element_type": self.element_type.value,
            "text": self.text,
            "attributes": self.attributes,
            "is_visible": self.is_visible,
            "is_interactive": self.is_interactive,
            "interaction_score": self.interaction_score,
            "bounding_box": self.bounding_box
        }
    
    def hash(self) -> str:
        """Generate unique hash for deduplication"""
        content = f"{self.tag_name}:{self.selector}:{self.text or ''}:{json.dumps(self.attributes, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


@dataclass
class PageCharacteristics:
    """Characteristics of a page for intelligent profile selection"""
    url: str
    form_count: int = 0
    input_count: int = 0
    button_count: int = 0
    link_count: int = 0
    has_aria: bool = False
    has_forms: bool = False
    uses_framework: Optional[str] = None
    is_spa: bool = False
    total_elements: int = 0
    interactive_ratio: float = 0.0
    
    def suggest_profile(self) -> str:
        """Suggest best profile based on characteristics"""
        scores = {
            "general": 0.5,  # Default baseline
            "interactive": 0.0,
            "qa": 0.0,
            "accessibility": 0.0,
            "performance": 0.0
        }
        
        # Score interactive profile
        if self.interactive_ratio > 0.3:
            scores["interactive"] = 0.8
        if self.is_spa:
            scores["interactive"] += 0.2
            
        # Score QA profile
        if self.form_count > 0:
            scores["qa"] = 0.7
        if self.input_count > 5:
            scores["qa"] += 0.3
            
        # Score accessibility profile
        if self.has_aria:
            scores["accessibility"] = 0.9
            
        # Score performance profile
        if self.total_elements > 500:
            scores["performance"] = 0.7
            
        # Return profile with highest score
        return max(scores, key=scores.get)


@dataclass
class ExtractionResult:
    """Result of an extraction operation"""
    url: str
    profile: str
    elements: List[Element]
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    characteristics: Optional[PageCharacteristics] = None
    cache_hit: bool = False
    content_hash: Optional[str] = None
    
    def stats(self) -> Dict[str, Any]:
        """Generate statistics"""
        return {
            "total_elements": len(self.elements),
            "interactive": sum(1 for e in self.elements if e.is_interactive),
            "visible": sum(1 for e in self.elements if e.is_visible),
            "by_type": self._count_by_type(),
            "avg_interaction_score": self._avg_interaction_score()
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count elements by type"""
        counts = {}
        for element in self.elements:
            type_name = element.element_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def _avg_interaction_score(self) -> float:
        """Calculate average interaction score"""
        if not self.elements:
            return 0.0
        total = sum(e.interaction_score for e in self.elements)
        return total / len(self.elements)


@dataclass
class DiffResult:
    """Result of comparing two extractions"""
    added: List[Element]
    removed: List[Element]
    changed: List[tuple[Element, Element]]  # (old, new)
    
    def has_changes(self) -> bool:
        """Check if there are any changes"""
        return bool(self.added or self.removed or self.changed)
    
    def summary(self) -> str:
        """Generate a summary of changes"""
        return f"+{len(self.added)} -{len(self.removed)} ~{len(self.changed)}"


class ElementFilter(Protocol):
    """Protocol for element filters"""
    
    def filter(self, element: Element) -> bool:
        """Return True if element passes filter"""
        ...
    
    def priority(self) -> int:
        """Return filter priority (higher = runs first)"""
        return 0


class ProfileConfig:
    """Profile configuration loaded from YAML"""
    
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name", "default")
        self.description = data.get("description", "")
        self.version = data.get("version", "1.0.0")
        self.filters = data.get("filters", [])
        self.scoring = data.get("scoring", {})
        self.categories = data.get("categories", [])
        self.settings = data.get("settings", {})
        
    def __repr__(self) -> str:
        return f"ProfileConfig(name={self.name}, version={self.version})"