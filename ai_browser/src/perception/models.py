"""Data models for perception layer"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
import time


class ElementType(str, Enum):
    """Types of interactive elements"""
    BUTTON = "button"
    LINK = "link"
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    IMAGE = "image"
    VIDEO = "video"
    IFRAME = "iframe"
    FORM = "form"
    TABLE = "table"
    OTHER = "other"


class InteractiveElement(BaseModel):
    """Represents an interactive element on the page"""
    id: int = Field(..., description="Unique numerical ID for the element")
    selector: str = Field(..., description="CSS selector to locate the element")
    xpath: Optional[str] = Field(None, description="XPath to locate the element")
    type: ElementType = Field(..., description="Type of the element")
    tag_name: str = Field(..., description="HTML tag name")
    text: Optional[str] = Field(None, description="Visible text content")
    value: Optional[str] = Field(None, description="Current value (for inputs)")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    href: Optional[str] = Field(None, description="Link URL (for anchors)")
    attributes: Dict[str, str] = Field(default_factory=dict, description="Element attributes")
    is_visible: bool = Field(True, description="Whether element is visible")
    is_enabled: bool = Field(True, description="Whether element is enabled")
    is_checked: Optional[bool] = Field(None, description="Whether checkbox/radio is checked")
    bounding_box: Optional[Dict[str, float]] = Field(None, description="Element position and size")
    aria_label: Optional[str] = Field(None, description="ARIA label for accessibility")
    aria_role: Optional[str] = Field(None, description="ARIA role")
    
    model_config = {"use_enum_values": True}


class AnnotatedElement(BaseModel):
    """Element with visual annotation"""
    element: InteractiveElement
    annotation_id: int = Field(..., description="Visual annotation ID shown on screenshot")
    color: str = Field("red", description="Annotation color")
    confidence: float = Field(1.0, description="Confidence score for element detection")


class PageMetadata(BaseModel):
    """Metadata about the web page"""
    url: str = Field(..., description="Current page URL")
    title: str = Field(..., description="Page title")
    description: Optional[str] = Field(None, description="Page meta description")
    keywords: Optional[List[str]] = Field(None, description="Page keywords")
    language: Optional[str] = Field(None, description="Page language")
    viewport_width: int = Field(1920, description="Viewport width")
    viewport_height: int = Field(1080, description="Viewport height")
    scroll_position: Dict[str, int] = Field(
        default_factory=lambda: {"x": 0, "y": 0},
        description="Current scroll position"
    )
    page_width: Optional[int] = Field(None, description="Total page width")
    page_height: Optional[int] = Field(None, description="Total page height")
    load_time_ms: Optional[float] = Field(None, description="Page load time in milliseconds")


class DOMStructure(BaseModel):
    """Simplified DOM structure"""
    raw_html: Optional[str] = Field(None, description="Raw HTML content")
    distilled_content: str = Field(..., description="Simplified text/markdown content")
    text_content: str = Field(..., description="Plain text content")
    headings: List[Dict[str, str]] = Field(default_factory=list, description="Page headings hierarchy")
    forms: List[Dict[str, Any]] = Field(default_factory=list, description="Form structures")
    tables: List[Dict[str, Any]] = Field(default_factory=list, description="Table structures")
    images: List[Dict[str, str]] = Field(default_factory=list, description="Image information")
    links: List[Dict[str, str]] = Field(default_factory=list, description="Link information")
    
    def get_token_count(self) -> int:
        """Estimate token count for LLM context"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(self.distilled_content) // 4


class AccessibilityTree(BaseModel):
    """Accessibility tree information"""
    tree: Optional[Dict[str, Any]] = Field(None, description="Full accessibility tree")
    focusable_elements: List[Dict[str, Any]] = Field(default_factory=list, description="Focusable elements")
    landmarks: List[Dict[str, str]] = Field(default_factory=list, description="ARIA landmarks")
    headings_hierarchy: List[Dict[str, str]] = Field(default_factory=list, description="Heading structure")


class WebPageState(BaseModel):
    """Complete state of a web page"""
    # Metadata
    metadata: PageMetadata = Field(..., description="Page metadata")
    
    # Structure
    dom_structure: DOMStructure = Field(..., description="DOM structure and content")
    
    # Interactive elements
    interactive_elements: List[InteractiveElement] = Field(
        default_factory=list,
        description="All interactive elements on the page"
    )
    
    # Visual state
    screenshot: Optional[bytes] = Field(None, description="Raw screenshot bytes")
    screenshot_base64: Optional[str] = Field(None, description="Base64 encoded screenshot")
    annotated_screenshot: Optional[bytes] = Field(None, description="Screenshot with annotations")
    annotated_screenshot_base64: Optional[str] = Field(None, description="Base64 annotated screenshot")
    
    # Annotation mapping
    element_map: Dict[int, str] = Field(
        default_factory=dict,
        description="Map from annotation ID to CSS selector"
    )
    annotated_elements: List[AnnotatedElement] = Field(
        default_factory=list,
        description="Elements with visual annotations"
    )
    
    # Accessibility
    accessibility: Optional[AccessibilityTree] = Field(None, description="Accessibility information")
    
    # Timing
    timestamp: float = Field(default_factory=time.time, description="State capture timestamp")
    capture_duration_ms: Optional[float] = Field(None, description="Time to capture state")
    
    # Analysis
    is_error_page: bool = Field(False, description="Whether this is an error page")
    requires_authentication: bool = Field(False, description="Whether page requires login")
    has_captcha: bool = Field(False, description="Whether page has CAPTCHA")
    detected_frameworks: List[str] = Field(default_factory=list, description="Detected web frameworks")
    
    def get_summary(self) -> str:
        """Get a brief summary of the page state"""
        return f"""
Page: {self.metadata.title}
URL: {self.metadata.url}
Interactive Elements: {len(self.interactive_elements)}
Text Length: {len(self.dom_structure.text_content)} chars
Has Screenshot: {self.screenshot is not None}
Has Annotations: {len(self.annotated_elements)} elements
Captured: {self.timestamp}
"""
    
    def get_context_for_llm(self, max_chars: int = 4000) -> str:
        """Get optimized context for LLM processing"""
        context = f"""
## Current Page State

**URL:** {self.metadata.url}
**Title:** {self.metadata.title}

### Page Content (Simplified):
{self.dom_structure.distilled_content[:max_chars]}

### Interactive Elements ({len(self.interactive_elements)} total):
"""
        # Add interactive elements
        for elem in self.interactive_elements[:20]:  # Limit to first 20
            if elem.text:
                context += f"\n[{elem.id}] {elem.type}: {elem.text[:50]}"
            else:
                context += f"\n[{elem.id}] {elem.type}: <{elem.tag_name}>"
        
        if len(self.interactive_elements) > 20:
            context += f"\n... and {len(self.interactive_elements) - 20} more elements"
        
        return context
    
    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "exclude": ["screenshot", "annotated_screenshot", "raw_html"]
        }
    }


class PerceptionResult(BaseModel):
    """Result of perception operation"""
    success: bool = Field(..., description="Whether perception succeeded")
    state: Optional[WebPageState] = Field(None, description="Captured page state")
    error: Optional[str] = Field(None, description="Error message if failed")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")