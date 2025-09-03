#!/usr/bin/env python3
"""
Fix indentation issues in quantum.py
"""

with open('quantum.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line starts with "    def " (4 spaces + def)
    if line.startswith("    def ") or line.startswith("    async def "):
        # Remove the leading spaces - these should be at module level
        fixed_lines.append(line[4:])  # Remove the 4 spaces
    else:
        fixed_lines.append(line)
    
    i += 1

# Write the fixed content
with open('quantum.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed indentation issues in quantum.py")