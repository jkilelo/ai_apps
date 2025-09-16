"""
Fix ALL syntax errors in browser.py related to multi-line f-strings
"""
import re

# Read the file
with open('web_automation_portable/backend/browser.py', 'r') as f:
    lines = f.readlines()

# Find and fix broken f-strings
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Check if this line contains an f-string start
    if 'f"' in line and not line.strip().endswith('")') and not line.strip().endswith('"),') and not line.strip().endswith('"'):
        # This might be a multi-line f-string
        # Collect all lines until we find the closing quote
        combined = line.rstrip()
        j = i + 1
        while j < len(lines):
            next_line = lines[j].strip()
            combined += ' ' + next_line
            if '"' in next_line and (next_line.endswith(')') or next_line.endswith('),') or next_line.endswith('"')):
                # Found the end
                # Clean up the combined string
                combined = re.sub(r'\s+', ' ', combined)
                # Remove any orphaned quotes or braces
                combined = re.sub(r'\s+\'\'}\s*"', '"', combined)
                combined = re.sub(r'"\s+\'\'}\s*"', '"', combined)
                combined = re.sub(r'\)\s*,\s*"', ', "', combined)

                # Preserve original indentation from first line
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + combined + '\n')
                i = j + 1
                break
            j += 1
        else:
            # Couldn't find end, just keep the line as is
            fixed_lines.append(line)
            i += 1
    else:
        fixed_lines.append(line)
        i += 1

# Write the fixed content back
with open('web_automation_portable/backend/browser.py', 'w') as f:
    f.writelines(fixed_lines)

print("Fixed all browser.py syntax errors")