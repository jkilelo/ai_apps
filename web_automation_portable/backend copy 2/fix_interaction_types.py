#!/usr/bin/env python3
"""Fix InteractionType references to match data_types.py"""

import re

# Read the file
with open('elements_extractor_no_llm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix NAVIGATE references (not in InteractionType enum)
content = content.replace(', InteractionType.NAVIGATE', '')

# Fix RESET references (not in InteractionType enum)
content = content.replace(', InteractionType.RESET', '')

# Fix NONE references (not in InteractionType enum)
content = re.sub(
    r'interactions = \[InteractionType\.NONE\]',
    'interactions = []',
    content
)

# Fix the _classify_elements method to not use NAVIGATE
content = re.sub(
    r'interactions = \[InteractionType\.CLICK, InteractionType\.HOVER, InteractionType\.NAVIGATE\]',
    'interactions = [InteractionType.CLICK, InteractionType.HOVER]',
    content
)

# Write back
with open('elements_extractor_no_llm.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed InteractionType references in elements_extractor_no_llm.py")