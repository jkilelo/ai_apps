#!/usr/bin/env python3
"""
Fix syntax errors in quantum.py by properly formatting method definitions
"""

import re

# Read the file
with open('quantum.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find lines with multiple method definitions concatenated
# Look for patterns like: some_code async def or some_code def
pattern = r'(\S.*?)\s+(async\s+def|def)\s+(\w+)\('

def fix_line(match):
    """Replace concatenated methods with proper formatting"""
    before = match.group(1)
    def_type = match.group(2)
    method_name = match.group(3)
    
    # Add newline and proper indentation
    return f"{before}\n    \n    {def_type} {method_name}("

# Apply the fix
fixed_content = re.sub(pattern, fix_line, content)

# Write the fixed content back
with open('quantum_fixed.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed quantum.py written to quantum_fixed.py")
print("Please review and replace quantum.py with quantum_fixed.py if correct")