#!/usr/bin/env python3
"""
Refactor elements_extractor_no_llm.py to use all data types from data_types.py
This ensures DRY compliance and no duplicate definitions
"""

import re

# Read the current file
with open('elements_extractor_no_llm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Update the imports to include all data types from data_types.py
new_imports = """# Import ALL data types from data_types.py for DRY compliance
from data_types import (
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

# Replace the old import
content = re.sub(
    r'# Import from data_types for DRY compliance\nfrom data_types import \([^)]+\)',
    new_imports,
    content,
    flags=re.DOTALL
)

# Step 2: Remove all duplicate enum definitions
# Remove InteractionType class
content = re.sub(
    r'class InteractionType\(Enum\):.*?(?=\n\nclass|\n\n# )',
    '',
    content,
    flags=re.DOTALL
)

# Remove LocatorStrategy class
content = re.sub(
    r'class LocatorStrategy\(Enum\):.*?(?=\n\nclass|\n\n# )',
    '',
    content,
    flags=re.DOTALL
)

# Remove ExtractionMethod class
content = re.sub(
    r'class ExtractionMethod\(Enum\):.*?(?=\n\nclass|\n\n# )',
    '',
    content,
    flags=re.DOTALL
)

# Remove ConfidenceLevel class
content = re.sub(
    r'class ConfidenceLevel\(Enum\):.*?(?=\n\n# )',
    '',
    content,
    flags=re.DOTALL
)

# Step 3: Remove duplicate data model classes
# Remove ElementSelector class
content = re.sub(
    r'class ElementSelector\(BaseModel\):.*?(?=\n\nclass)',
    '',
    content,
    flags=re.DOTALL
)

# Remove BoundingBox class
content = re.sub(
    r'class BoundingBox\(BaseModel\):.*?contains_point.*?\n        return self\.left.*?\n\n',
    '',
    content,
    flags=re.DOTALL
)

# Remove ComputedStyle class
content = re.sub(
    r'class ComputedStyle\(BaseModel\):.*?is_visible.*?\n        return self\.display.*?\n\n',
    '',
    content,
    flags=re.DOTALL
)

# Remove ScreenshotData class
content = re.sub(
    r'class ScreenshotData\(BaseModel\):.*?save.*?\n        path\.write_bytes.*?\n\n',
    '',
    content,
    flags=re.DOTALL
)

# Remove CrawlResult class (keeping the one from data_types)
content = re.sub(
    r'class CrawlResult\(BaseModel\):.*?errors: List\[str\].*?\n\n',
    '',
    content,
    flags=re.DOTALL
)

# Remove ExtractedElement class
content = re.sub(
    r'class ExtractedElement\(BaseModel\):.*?to_pipeline_contract.*?\n        \}',
    '',
    content,
    flags=re.DOTALL
)

# Step 4: Clean up the ENUMS section comment
content = re.sub(
    r'# ==================== ENUMS ====================\n\n\n# ElementType is now imported from data_types\.py\n\n',
    '# ==================== ENUMS ====================\n# All enums are now imported from data_types.py for DRY compliance\n\n',
    content
)

# Step 5: Clean up the DATA MODELS section
content = re.sub(
    r'# ==================== DATA MODELS ====================\n\n\n',
    '# ==================== DATA MODELS ====================\n# All data models are now imported from data_types.py for DRY compliance\n\n',
    content
)

# Step 6: Remove any remaining standalone comments about imports
content = re.sub(
    r'\n# ExtractionConfig is now imported from data_types\.py as BrowserExtractionConfig\n',
    '',
    content
)

content = re.sub(
    r'\n# ExtractionResult is now imported from data_types\.py as DOMExtractionResult\n',
    '',
    content
)

content = re.sub(
    r'\n\n# ==================== EXTRACTED ELEMENT MODEL ====================\n',
    '',
    content
)

# Step 7: Clean up extra blank lines
content = re.sub(r'\n{4,}', '\n\n\n', content)

# Write the refactored content
with open('elements_extractor_no_llm.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully refactored elements_extractor_no_llm.py to use data_types.py")
print("All duplicate definitions have been removed")