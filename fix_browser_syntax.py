"""
Fix all syntax errors in browser.py related to multi-line f-strings
"""
import re

# Read the file
with open('web_automation_portable/backend/browser.py', 'r') as f:
    content = f.read()

# Fix pattern: f-strings broken across multiple lines
# Pattern 1: f"{ followed by newline
content = re.sub(r'f"{\s*\n\s*', r'f"{', content)
# Pattern 2: }\s*_{ across lines
content = re.sub(r'}\s*_\s*{\s*\n\s*', r'}_{', content)
# Pattern 3: Handle remaining broken f-strings
lines = content.split('\n')
fixed_lines = []
in_fstring = False
fstring_buffer = []

for i, line in enumerate(lines):
    # Check if line starts an unclosed f-string
    if 'f"' in line or "f'" in line:
        # Count quotes to see if string is complete
        double_quotes = line.count('"') - line.count('\\"')
        single_quotes = line.count("'") - line.count("\\'")

        if (('f"' in line and double_quotes % 2 != 0) or
            ("f'" in line and single_quotes % 2 != 0)):
            # Unclosed f-string
            in_fstring = True
            fstring_buffer = [line.rstrip()]
        else:
            fixed_lines.append(line)
    elif in_fstring:
        # Continue collecting f-string lines
        fstring_buffer.append(line.strip())

        # Check if this line closes the f-string
        if '"' in line or "'" in line:
            # Join all parts and fix formatting
            combined = ' '.join(fstring_buffer)
            # Remove excessive whitespace
            combined = re.sub(r'\s+', ' ', combined)
            fixed_lines.append(combined)
            in_fstring = False
            fstring_buffer = []
    else:
        fixed_lines.append(line)

content = '\n'.join(fixed_lines)

# Write the fixed content back
with open('web_automation_portable/backend/browser.py', 'w') as f:
    f.write(content)

print("Fixed browser.py syntax errors")