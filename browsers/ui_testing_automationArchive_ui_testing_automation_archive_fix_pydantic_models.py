#!/usr/bin/env python3
"""
Script to fix all dataclasses to Pydantic v2 models in elements_extractor_no_llm.py
"""

import re

# Read the file
with open("elements_extractor_no_llm.py", "r") as f:
    content = f.read()

# Remove all @dataclass decorators
content = re.sub(r'@dataclass\n', '', content)

# Remove dataclass import and field import
content = re.sub(r'from dataclasses import dataclass, field, asdict\n', '', content)

# Fix ComputedStyle fields
content = content.replace(
    """class ComputedStyle(BaseModel):
    \"\"\"Computed CSS styles for an element\"\"\"
    display: str
    visibility: str
    opacity: str
    position: str
    z_index: str
    background_color: str
    color: str
    font_size: str
    font_weight: str
    cursor: str
    overflow: str""",
    """class ComputedStyle(BaseModel):
    \"\"\"Computed CSS styles for an element\"\"\"
    model_config = ConfigDict(str_strip_whitespace=True)
    
    display: str = Field(default="block")
    visibility: str = Field(default="visible")
    opacity: str = Field(default="1")
    position: str = Field(default="static")
    z_index: str = Field(default="auto")
    background_color: str = Field(default="transparent")
    color: str = Field(default="black")
    font_size: str = Field(default="16px")
    font_weight: str = Field(default="normal")
    cursor: str = Field(default="auto")
    overflow: str = Field(default="visible")"""
)

# Fix ScreenshotData
content = content.replace(
    """class ScreenshotData(BaseModel):
    \"\"\"Screenshot data with metadata\"\"\"
    format: str
    width: int
    height: int
    data: str  # Base64 encoded
    timestamp: float
    url: str
    highlighted_elements: List[str] = field(default_factory=list)""",
    """class ScreenshotData(BaseModel):
    \"\"\"Screenshot data with metadata\"\"\"
    model_config = ConfigDict(str_strip_whitespace=True)
    
    format: str = Field(default="png")
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)
    data: str = Field(...)  # Base64 encoded
    timestamp: float = Field(default_factory=time.time)
    url: str = Field(...)
    highlighted_elements: List[str] = Field(default_factory=list)"""
)

# Fix ExtractionConfig
old_config = """class ExtractionConfig:
    \"\"\"Configuration for element extraction\"\"\"
    # Extraction settings
    enable_shadow_dom: bool = True
    enable_iframe_traversal: bool = True
    enable_dynamic_wait: bool = True
    enable_mutation_observer: bool = False
    max_depth: int = 10
    max_elements: int = 1000
    extraction_timeout: int = 30000
    
    # Filtering
    filter_invisible: bool = True
    filter_duplicates: bool = True
    min_element_size: int = 5  # Minimum pixel size
    
    # Anti-detection (delegated to browser.py)
    enable_stealth: bool = True
    randomize_delays: bool = True
    min_delay: float = 0.1
    max_delay: float = 0.5
    
    # Performance
    batch_size: int = 100
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    
    # Output
    include_computed_styles: bool = True
    include_accessibility_info: bool = True
    include_event_listeners: bool = False
    
    # Screenshot settings
    capture_screenshots: bool = False
    screenshot_full_page: bool = True
    screenshot_format: str = "png"
    screenshot_quality: int = 90
    highlight_elements: bool = True
    highlight_color: str = "red"
    highlight_width: int = 2"""

new_config = """class ExtractionConfig(BaseModel):
    \"\"\"Configuration for element extraction\"\"\"
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Extraction settings
    enable_shadow_dom: bool = Field(default=True)
    enable_iframe_traversal: bool = Field(default=True)
    enable_dynamic_wait: bool = Field(default=True)
    enable_mutation_observer: bool = Field(default=False)
    max_depth: int = Field(default=10, ge=1, le=100)
    max_elements: int = Field(default=1000, ge=1, le=10000)
    extraction_timeout: int = Field(default=30000, ge=1000, le=120000)
    
    # Filtering
    filter_invisible: bool = Field(default=True)
    filter_duplicates: bool = Field(default=True)
    min_element_size: int = Field(default=5, ge=0)  # Minimum pixel size
    
    # Anti-detection (delegated to browser.py)
    enable_stealth: bool = Field(default=True)
    randomize_delays: bool = Field(default=True)
    min_delay: float = Field(default=0.1, ge=0.0, le=10.0)
    max_delay: float = Field(default=0.5, ge=0.0, le=10.0)
    
    # Performance
    batch_size: int = Field(default=100, ge=1, le=1000)
    enable_caching: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, ge=60, le=86400)  # seconds
    
    # Output
    include_computed_styles: bool = Field(default=True)
    include_accessibility_info: bool = Field(default=True)
    include_event_listeners: bool = Field(default=False)
    
    # Screenshot settings
    capture_screenshots: bool = Field(default=False)
    screenshot_full_page: bool = Field(default=True)
    screenshot_format: str = Field(default="png", pattern="^(png|jpeg|jpg)$")
    screenshot_quality: int = Field(default=90, ge=1, le=100)
    highlight_elements: bool = Field(default=True)
    highlight_color: str = Field(default="red")
    highlight_width: int = Field(default=2, ge=1, le=10)"""

content = content.replace(old_config, new_config)

# Fix ExtractionResult
content = content.replace(
    """class ExtractionResult:
    \"\"\"Result of element extraction\"\"\"
    url: str
    elements: List[ExtractedElement]
    extraction_time: float
    success: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    screenshots: List[ScreenshotData] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)""",
    """class ExtractionResult(BaseModel):
    \"\"\"Result of element extraction\"\"\"
    model_config = ConfigDict(str_strip_whitespace=True)
    
    url: str = Field(..., min_length=1)
    elements: List['ExtractedElement'] = Field(default_factory=list)
    extraction_time: float = Field(..., ge=0.0)
    success: bool = Field(default=True)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    screenshots: List[ScreenshotData] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)"""
)

# Fix CrawlResult
content = content.replace(
    """class CrawlResult:
    \"\"\"Result of web crawling\"\"\"
    start_url: str
    pages_visited: List[str]
    extraction_results: List[ExtractionResult]
    total_elements: int
    crawl_time: float
    max_depth_reached: int
    errors: List[str] = field(default_factory=list)""",
    """class CrawlResult(BaseModel):
    \"\"\"Result of web crawling\"\"\"
    model_config = ConfigDict(str_strip_whitespace=True)
    
    start_url: str = Field(..., min_length=1)
    pages_visited: List[str] = Field(default_factory=list)
    extraction_results: List[ExtractionResult] = Field(default_factory=list)
    total_elements: int = Field(default=0, ge=0)
    crawl_time: float = Field(..., ge=0.0)
    max_depth_reached: int = Field(default=0, ge=0)
    errors: List[str] = Field(default_factory=list)"""
)

# Replace asdict calls with model_dump
content = content.replace('asdict(s)', 's.model_dump()')

# Replace .to_dict() methods with proper Pydantic methods
content = re.sub(
    r'def to_dict\(self\) -> Dict\[str, Any\]:\s*"""Convert to dictionary"""\s*return \{[^}]+\}',
    '',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Save the file
with open("elements_extractor_no_llm.py", "w") as f:
    f.write(content)

print("[OK] Fixed all dataclasses to Pydantic v2 models")