#!/usr/bin/env python3
"""Complete the data_types.py file with all missing models"""

import time
from pathlib import Path

# Read current content
with open('data_types.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove incomplete else block at the end
if content.endswith('else:\n    # Dataclass fallback'):
    content = content[:-len('else:\n    # Dataclass fallback')]

# Add missing import if needed
if 'import time' not in content:
    # Find the imports section and add time import
    import_lines = content.split('\n')
    for i, line in enumerate(import_lines):
        if line.startswith('from pathlib import Path'):
            import_lines.insert(i, 'import time')
            break
    content = '\n'.join(import_lines)

# Now add all missing models as Pydantic BaseModel classes
missing_models = '''

# ==================== DATA MODELS ====================

class BoundingBox(BaseModel):
    """Element bounding box"""
    x: float
    y: float
    width: float
    height: float
    
    def is_visible(self) -> bool:
        return self.width > 0 and self.height > 0

class ComputedStyle(BaseModel):
    """Computed CSS styles"""
    display: Optional[str] = None
    visibility: Optional[str] = None
    opacity: Optional[str] = None
    position: Optional[str] = None
    zIndex: Optional[str] = None
    backgroundColor: Optional[str] = None
    color: Optional[str] = None
    fontSize: Optional[str] = None
    
    def is_visible(self) -> bool:
        return (self.display != 'none' and 
                self.visibility != 'hidden' and 
                self.opacity != '0')

class ElementSelector(BaseModel):
    """Element selector strategy"""
    strategy: LocatorStrategy
    value: str
    score: float = 0.5
    is_unique: bool = False

class ElementData(BaseModel):
    """Core element data structure"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Identification
    element_id: str = Field(description="Unique identifier")
    tag_name: str = Field(description="HTML tag name")
    
    # Content
    text_content: Optional[str] = Field(default=None, description="Text content")
    inner_html: Optional[str] = Field(default=None, description="Inner HTML")
    outer_html: Optional[str] = Field(default=None, description="Outer HTML")
    
    # Attributes
    id: Optional[str] = Field(default=None, description="Element ID")
    class_names: List[str] = Field(default_factory=list, description="CSS classes")
    name: Optional[str] = Field(default=None, description="Name attribute")
    value: Optional[str] = Field(default=None, description="Value attribute")
    href: Optional[str] = Field(default=None, description="Href for links")
    src: Optional[str] = Field(default=None, description="Source for images/scripts")
    alt: Optional[str] = Field(default=None, description="Alt text")
    title: Optional[str] = Field(default=None, description="Title attribute")
    placeholder: Optional[str] = Field(default=None, description="Placeholder text")
    type: Optional[str] = Field(default=None, description="Type attribute")
    role: Optional[str] = Field(default=None, description="ARIA role")
    aria_label: Optional[str] = Field(default=None, description="ARIA label")
    data_testid: Optional[str] = Field(default=None, description="Test ID")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="All attributes")
    
    # State
    is_visible: bool = Field(default=True, description="Visibility state")
    is_enabled: bool = Field(default=True, description="Enabled state")
    is_selected: bool = Field(default=False, description="Selected state")
    is_checked: bool = Field(default=False, description="Checked state")
    is_focused: bool = Field(default=False, description="Focus state")
    is_required: bool = Field(default=False, description="Required field")
    is_readonly: bool = Field(default=False, description="Read-only state")
    
    # Position and style
    bounding_box: Optional[BoundingBox] = Field(default=None, description="Element position")
    computed_style: Optional[ComputedStyle] = Field(default=None, description="Computed styles")
    
    # Selectors
    xpath: Optional[str] = Field(default=None, description="XPath selector")
    css_selector: Optional[str] = Field(default=None, description="CSS selector")
    full_xpath: Optional[str] = Field(default=None, description="Full XPath from root")
    
    # Hierarchy
    parent_id: Optional[str] = Field(default=None, description="Parent element ID")
    children_ids: List[str] = Field(default_factory=list, description="Child element IDs")
    depth: int = Field(default=0, description="DOM tree depth")
    shadow_dom_path: List[str] = Field(default_factory=list, description="Shadow DOM path")

class ExtractedElement(BaseModel):
    """Extended element with classification and validation"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Core fields (required)
    selector: str
    element_type: ElementType
    tag_name: str
    
    # Content
    text: Optional[str] = None
    value: Optional[str] = None
    placeholder: Optional[str] = None
    
    # Attributes
    id: Optional[str] = None
    name: Optional[str] = None
    classes: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    
    # Interaction capabilities
    is_clickable: bool = False
    is_editable: bool = False
    is_visible: bool = True
    is_enabled: bool = True
    interaction_types: List[InteractionType] = Field(default_factory=list)
    
    # Selectors
    xpath: Optional[str] = None
    css_path: Optional[str] = None
    selectors: List[ElementSelector] = Field(default_factory=list)
    
    # Position
    bounding_box: Optional[BoundingBox] = None
    computed_style: Optional[ComputedStyle] = None
    
    # Hierarchy
    parent_selector: Optional[str] = None
    child_count: int = 0
    depth: int = 0
    
    # Classification
    confidence: float = 0.5
    importance_score: float = 0.5
    
    # Metadata
    extraction_method: Optional[ExtractionMethod] = None
    extraction_timestamp: Optional[float] = None
    is_shadow_element: bool = False
    is_iframe_element: bool = False
    
    # Validation
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    
    # AI/LLM fields
    ai_description: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_suggested_actions: List[str] = Field(default_factory=list)
    
    def get_best_selector(self) -> Optional[ElementSelector]:
        """Get the best selector based on score"""
        if not self.selectors:
            return None
        return max(self.selectors, key=lambda s: s.score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)

class ScreenshotData(BaseModel):
    """Screenshot information"""
    format: str = "png"
    width: int
    height: int
    data: str  # Base64 encoded
    timestamp: float
    url: Optional[str] = None
    highlighted_elements: List[str] = Field(default_factory=list)
    annotations: Dict[str, Any] = Field(default_factory=dict)

class PageAnalysis(BaseModel):
    """Comprehensive page analysis result"""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    lang: Optional[str] = None
    viewport: Optional[Dict[str, Any]] = None
    
    # Content analysis
    has_forms: bool = False
    has_tables: bool = False
    has_media: bool = False
    has_iframes: bool = False
    has_shadow_dom: bool = False
    
    # Performance metrics
    dom_ready_time: Optional[float] = None
    load_time: Optional[float] = None
    element_count: int = 0
    
    # Accessibility
    has_aria: bool = False
    has_semantic_html: bool = False
    accessibility_score: Optional[float] = None

class InteractionResult(BaseModel):
    """Result of element interaction"""
    success: bool
    action: InteractionType
    element_selector: str
    timestamp: float
    
    # Outcomes
    page_changed: bool = False
    new_elements: List[str] = Field(default_factory=list)
    removed_elements: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    # Screenshots
    before_screenshot: Optional[ScreenshotData] = None
    after_screenshot: Optional[ScreenshotData] = None

class ValidationResult(BaseModel):
    """Element validation result"""
    element_selector: str
    is_valid: bool
    validation_type: str
    
    # Details
    expected: Any = None
    actual: Any = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class TestScenario(BaseModel):
    """Test scenario definition"""
    name: str
    description: Optional[str] = None
    category: TestCategory
    priority: TestPriority = TestPriority.MEDIUM
    
    # Steps
    preconditions: List[str] = Field(default_factory=list)
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    expected_results: List[str] = Field(default_factory=list)
    
    # Elements involved
    target_elements: List[str] = Field(default_factory=list)
    
    # Validation
    validations: List[ValidationResult] = Field(default_factory=list)
    
    # Metadata
    created_at: float = Field(default_factory=lambda: time.time())
    framework: Optional[TestFramework] = None
    tags: List[str] = Field(default_factory=list)

class CrawlResult(BaseModel):
    """Website crawl result"""
    start_url: str
    pages_visited: List[str] = Field(default_factory=list)
    pages_discovered: List[str] = Field(default_factory=list)
    
    # Statistics
    total_pages: int = 0
    total_elements: int = 0
    crawl_time: float = 0.0
    max_depth_reached: int = 0
    
    # Data
    page_analyses: List[PageAnalysis] = Field(default_factory=list)
    all_elements: List[ExtractedElement] = Field(default_factory=list)
    
    # Errors
    failed_pages: Dict[str, str] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    
    timestamp: float = Field(default_factory=lambda: time.time())

# Configuration classes
class BrowserExtractionConfig(BaseModel):
    """Configuration for browser-based extraction"""
    # Browser settings
    headless: bool = False
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    
    # Extraction settings
    enable_shadow_dom: bool = True
    enable_iframe_traversal: bool = True
    enable_stealth: bool = True
    wait_for_network_idle: bool = True
    timeout: int = 30000
    
    # Element filtering
    filter_invisible: bool = True
    filter_duplicates: bool = True
    min_element_size: int = 5
    max_elements: int = 1000
    
    # Screenshots
    capture_screenshots: bool = False
    screenshot_format: str = "png"
    screenshot_quality: int = 80
    screenshot_full_page: bool = False
    highlight_elements: bool = False
    highlight_color: str = "red"
    highlight_width: int = 2
    
    # Caching
    enable_caching: bool = True
    cache_ttl: int = 3600
    
    # Performance
    parallel_extraction: bool = False
    batch_size: int = 10
    
    # QA Mode settings
    qa_mode: bool = False
    qa_priority_tags: List[str] = Field(default_factory=lambda: [
        'button', 'input', 'select', 'textarea', 'a', 'form'
    ])
    qa_interaction_indicators: List[str] = Field(default_factory=lambda: [
        'click', 'submit', 'change', 'focus', 'blur'
    ])
    qa_min_interaction_score: float = 0.3
    qa_include_disabled: bool = True
    qa_include_hidden_toggles: bool = True
    
    # Extraction strategies
    extraction_strategy: ExtractionStrategy = ExtractionStrategy.HYBRID
    fallback_strategies: List[ExtractionStrategy] = Field(default_factory=list)

class DOMExtractionConfig(BrowserExtractionConfig):
    """Alias for backward compatibility"""
    pass

class BrowserExtractionResult(BaseModel):
    """Result from browser extraction"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    url: str
    success: bool
    elements: List[ElementData] = Field(default_factory=list)
    page_title: Optional[str] = None
    page_description: Optional[str] = None
    page_analysis: Optional[PageAnalysis] = None
    
    # Timing
    extraction_time: float = 0.0
    network_time: float = 0.0
    
    # Statistics
    total_elements_found: int = 0
    elements_filtered: int = 0
    shadow_dom_elements: int = 0
    iframe_elements: int = 0
    
    # Screenshots
    screenshots: List[ScreenshotData] = Field(default_factory=list)
    
    # Metadata
    browser_version: Optional[str] = None
    extraction_strategy: Optional[ExtractionStrategy] = None
    config: Optional[Dict[str, Any]] = None
    
    # Errors
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Additional data
    statistics: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def save_screenshots(self, directory: Path) -> List[Path]:
        """Save screenshots to directory"""
        import base64
        saved_paths = []
        
        directory.mkdir(parents=True, exist_ok=True)
        
        for i, screenshot in enumerate(self.screenshots):
            filename = f"screenshot_{i+1}.{screenshot.format}"
            filepath = directory / filename
            
            # Decode and save
            image_data = base64.b64decode(screenshot.data)
            filepath.write_bytes(image_data)
            saved_paths.append(filepath)
        
        return saved_paths

class ExtendedCrawlResult(BaseModel):
    """Extended crawl result for multi-page extraction"""
    start_url: str = Field(..., description="Starting URL for crawl")
    pages_visited: List[str] = Field(default_factory=list, description="URLs visited during crawl")
    extraction_results: List[BrowserExtractionResult] = Field(default_factory=list, description="Extraction results for each page")
    total_elements: int = Field(default=0, ge=0, description="Total elements extracted across all pages")
    crawl_time: float = Field(..., ge=0.0, description="Total crawl time in seconds")
    max_depth_reached: int = Field(default=0, ge=0, description="Maximum depth reached during crawl")
    errors: List[str] = Field(default_factory=list, description="Errors encountered during crawl")
'''

# Append the missing models
content = content.rstrip() + missing_models

# Write back
with open('data_types.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('SUCCESS: Completed data_types.py with all necessary models')
print('Added all missing Pydantic models:')
print('  - BoundingBox')
print('  - ComputedStyle')
print('  - ElementSelector')
print('  - ElementData')
print('  - ExtractedElement')
print('  - ScreenshotData')
print('  - PageAnalysis')
print('  - InteractionResult')
print('  - ValidationResult')
print('  - TestScenario')
print('  - CrawlResult')
print('  - BrowserExtractionConfig/DOMExtractionConfig')
print('  - BrowserExtractionResult')
print('  - ExtendedCrawlResult')