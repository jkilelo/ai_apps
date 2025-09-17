#!/usr/bin/env python3
"""Fix data type imports in elements_extractor_no_llm.py"""

import re

# Read the file
with open('elements_extractor_no_llm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Remove BrowserElementData import from browser module since we use ElementData from data_types
content = re.sub(
    r'        ElementData as BrowserElementData,\n',
    '',
    content
)

content = re.sub(
    r'        ExtractionResult as BrowserExtractionResult,\n',
    '',
    content
)

# Fix 2: Remove the fallback class definitions for these types
content = re.sub(
    r'    class BrowserElementData:  # type: ignore\n        pass\n\n',
    '',
    content
)

content = re.sub(
    r'    class BrowserExtractionResult:  # type: ignore\n        pass\n\n',
    '',
    content
)

# Fix 3: Update the _convert_browser_elements method signature
content = re.sub(
    r'def _convert_browser_elements\(self, browser_elements: List\[BrowserElementData\]\)',
    'def _convert_browser_elements(self, browser_elements: List[ElementData])',
    content
)

# Write back
with open('elements_extractor_no_llm.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed data type imports in elements_extractor_no_llm.py")