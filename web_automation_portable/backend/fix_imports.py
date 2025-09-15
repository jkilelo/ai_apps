#!/usr/bin/env python3
"""Fix import issues in elements_extractor_no_llm.py"""

import re

# Read the file
with open('elements_extractor_no_llm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the imports
content = content.replace(
    'DOMExtractionConfig as ExtractionConfig',
    'BrowserExtractionConfig as ExtractionConfig'
)
content = content.replace(
    'DOMExtractionResult as ExtractionResult',
    'BrowserExtractionResult as ExtractionResult'
)

# Also update the comment
content = content.replace(
    '# ExtractionConfig is now imported from data_types.py as DOMExtractionConfig',
    '# ExtractionConfig is now imported from data_types.py as BrowserExtractionConfig'
)

# Write back
with open('elements_extractor_no_llm.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed imports in elements_extractor_no_llm.py")