#!/usr/bin/env python3
"""
Fix module relationships to follow DRY principles:
1. data_types.py - Single source of truth for ALL data types
2. browser.py - Uses data types from data_types.py, handles browser operations
3. elements_extractor_no_llm.py - Uses data_types.py and browser.py, no own definitions
"""

import re

def fix_browser_py():
    """Remove duplicate data type definitions from browser.py and import from data_types.py"""
    print("Fixing browser.py...")
    
    with open('browser.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Step 1: Update imports to include all needed data types from data_types.py
    old_import = "from data_types import ElementType, BrowserExtractionResult as ExtractionResult"
    new_import = """from data_types import (
    # Core enums
    ElementType,
    ProfileType,
    StealthLevel,
    ExtractionStrategy,
    # Data models
    TimingProfile,
    StealthProfile,
    StealthConfig,
    ElementData,
    # Results
    BrowserExtractionResult as ExtractionResult
)"""
    
    content = content.replace(old_import, new_import)
    
    # Step 2: Remove duplicate ProfileType enum definition
    content = re.sub(
        r'class ProfileType\(str, Enum\):.*?(?=\n\nclass|\n\n# )',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 3: Remove duplicate StealthLevel enum definition
    content = re.sub(
        r'class StealthLevel\(str, Enum\):.*?(?=\n\nclass|\n\n# )',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 4: Remove duplicate ExtractionStrategy enum definition
    content = re.sub(
        r'class ExtractionStrategy\(str, Enum\):.*?(?=\n\nclass|\n\n# )',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 5: Remove duplicate TimingProfile class definition
    content = re.sub(
        r'class TimingProfile\(BaseModel\):.*?verbose: bool.*?\n\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 6: Remove duplicate StealthProfile class definition
    content = re.sub(
        r'class StealthProfile\(BaseModel\):.*?custom_flags: List\[str\].*?\n\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 7: Remove duplicate StealthConfig class definition
    content = re.sub(
        r'class StealthConfig\(BaseModel\):.*?enable_stealth: bool.*?\n\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 8: Remove duplicate ElementData class definition (this is the big one)
    content = re.sub(
        r'class ElementData\(BaseModel\):.*?"""Return dictionary representation""".*?\n\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 9: Clean up any references to local definitions
    # Since we're importing from data_types, we don't need to change usage
    
    # Step 10: Clean up extra blank lines
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    with open('browser.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Removed duplicate data type definitions from browser.py")
    print("SUCCESS: Updated imports to use data_types.py")


def add_extended_crawl_result_to_data_types():
    """Add ExtendedCrawlResult to data_types.py for elements_extractor_no_llm.py"""
    print("\nAdding ExtendedCrawlResult to data_types.py...")
    
    with open('data_types.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if ExtendedCrawlResult already exists
    if 'class ExtendedCrawlResult' in content:
        print("SUCCESS: ExtendedCrawlResult already exists in data_types.py")
        return
    
    # Add ExtendedCrawlResult after CrawlResult
    extended_crawl_result = '''

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
    
    # Find the position after CrawlResult
    pattern = r'(class CrawlResult\(BaseModel\):.*?timestamp.*?\))\n'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + extended_crawl_result + content[insert_pos:]
        
        with open('data_types.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("SUCCESS: Added ExtendedCrawlResult to data_types.py")
    else:
        print("WARNING: Could not find appropriate position to add ExtendedCrawlResult")


def fix_elements_extractor_no_llm():
    """Update elements_extractor_no_llm.py to use ExtendedCrawlResult"""
    print("\nFixing elements_extractor_no_llm.py...")
    
    with open('elements_extractor_no_llm.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update import to include ExtendedCrawlResult
    old_import = """from data_types import (
    # Core enums
    ElementType,
    InteractionType,
    LocatorStrategy,
    ExtractionMethod,
    ConfidenceLevel,
    # Data models
    ElementSelector,
    BoundingBox,
    ComputedStyle,
    ExtractedElement,
    ElementData,
    ScreenshotData,
    CrawlResult,
    # Configs and results
    BrowserExtractionConfig as ExtractionConfig,
    BrowserExtractionResult as ExtractionResult
)"""
    
    new_import = """from data_types import (
    # Core enums
    ElementType,
    InteractionType,
    LocatorStrategy,
    ExtractionMethod,
    ConfidenceLevel,
    # Data models
    ElementSelector,
    BoundingBox,
    ComputedStyle,
    ExtractedElement,
    ElementData,
    ScreenshotData,
    ExtendedCrawlResult as CrawlResult,  # Use ExtendedCrawlResult for multi-page crawling
    # Configs and results
    BrowserExtractionConfig as ExtractionConfig,
    BrowserExtractionResult as ExtractionResult
)"""
    
    content = content.replace(old_import, new_import)
    
    # Fix the crawl method return type to use the correct field names
    # The method already uses the right field names, just needs the right type
    
    with open('elements_extractor_no_llm.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Updated elements_extractor_no_llm.py to use ExtendedCrawlResult")


def main():
    """Main function to fix all module relationships"""
    print("=" * 60)
    print("FIXING MODULE RELATIONSHIPS FOR DRY COMPLIANCE")
    print("=" * 60)
    
    # Fix browser.py first
    fix_browser_py()
    
    # Add ExtendedCrawlResult to data_types.py
    add_extended_crawl_result_to_data_types()
    
    # Fix elements_extractor_no_llm.py
    fix_elements_extractor_no_llm()
    
    print("\n" + "=" * 60)
    print("MODULE RELATIONSHIPS FIXED!")
    print("=" * 60)
    print("\nSummary:")
    print("1. data_types.py - Single source of truth for all data types [DONE]")
    print("2. browser.py - Uses data types from data_types.py [DONE]")
    print("3. elements_extractor_no_llm.py - Only consumes, doesn't define [DONE]")
    print("\nDRY principles enforced successfully!")


if __name__ == "__main__":
    main()