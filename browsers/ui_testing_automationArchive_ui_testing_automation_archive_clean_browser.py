import re

# Read the file
with open(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation\browser.py", "r") as f:
    content = f.read()

# Find positions of definitions to remove
lines = content.split('\n')
new_lines = []
skip_until = -1

i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if we should start skipping
    if i > skip_until:
        # Skip enum definitions
        if 'class ProfileType(' in line or 'class StealthLevel(' in line or 'class ExtractionStrategy(' in line:
            # Find the end of the enum (next class or major section)
            j = i + 1
            while j < len(lines):
                if lines[j].startswith('class ') or lines[j].startswith('@') or lines[j].startswith('# ==='):
                    skip_until = j - 1
                    break
                j += 1
            i = skip_until + 1
            continue
            
        # Skip @dataclass definitions that are now in contracts
        elif line.strip() == '@dataclass':
            next_line = lines[i+1] if i+1 < len(lines) else ''
            if any(cls in next_line for cls in ['TimingProfile:', 'StealthProfile:', 'BrowserProfile:', 
                                                  'StealthConfig:', 'ElementData:', 'ExtractionResult:']):
                # Find the end of the dataclass
                j = i + 2
                indent_level = len(next_line) - len(next_line.lstrip())
                brace_count = 0
                in_method = False
                
                while j < len(lines):
                    curr_line = lines[j]
                    curr_indent = len(curr_line) - len(curr_line.lstrip())
                    
                    # Check if we're in a method
                    if 'def ' in curr_line and curr_indent <= indent_level + 4:
                        in_method = True
                    
                    # Check if we've exited the class
                    if curr_line and not curr_line.startswith(' ') and not curr_line.startswith('\t'):
                        skip_until = j - 1
                        break
                    elif curr_line.startswith('class ') or curr_line.startswith('@'):
                        skip_until = j - 1
                        break
                    elif curr_line.strip() and curr_indent == 0:
                        skip_until = j - 1
                        break
                    
                    j += 1
                
                if skip_until < i:
                    skip_until = j - 1
                
                i = skip_until + 1
                continue
    
    # Add the line if we're not skipping
    if i > skip_until:
        new_lines.append(line)
    
    i += 1

# Join the lines back
content = '\n'.join(new_lines)

# Clean up multiple blank lines
content = re.sub(r'\n{3,}', '\n\n', content)

# Ensure proper imports at the top
if 'from browser_contracts import' not in content:
    # This should already be there from our previous edit
    pass

# Write the cleaned content
with open(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation\browser.py", "w") as f:
    f.write(content)

print("[OK] Removed duplicate definitions from browser.py")
print(f"Original lines: {len(lines)}")
print(f"New lines: {len(new_lines)}")