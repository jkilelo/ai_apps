#!/usr/bin/env python
"""Fix all remaining linting issues in data_types.py and browser.py"""

import re

def fix_long_lines(file_path):
    """Fix lines that are too long"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    for i, line in enumerate(lines):
        # Skip if line is not too long
        if len(line.rstrip()) <= 79:
            fixed_lines.append(line)
            continue

        # Handle specific cases
        if "elif isinstance(step, dict) and 'keyword' in step and 'text' in step:" in line:
            fixed_lines.append("                elif isinstance(step, dict) and \\\n")
            fixed_lines.append("                        'keyword' in step and 'text' in step:\n")
        elif "\"\"\"Shared utilities for element selector generation and type determination\"\"\"" in line:
            fixed_lines.append('    """Shared utilities for element selector generation"""\n')
        elif "'text': ElementType.TEXT_INPUT,  # Fixed: TEXT doesn't exist, use TEXT_INPUT" in line:
            fixed_lines.append("                'text': ElementType.TEXT_INPUT,  # Use TEXT_INPUT\n")
        elif "interaction_types: List[InteractionType] = Field(default_factory=list, description=\"Possible interactions\")" in line:
            fixed_lines.append("    interaction_types: List[InteractionType] = Field(\n")
            fixed_lines.append("        default_factory=list, description=\"Possible interactions\")\n")
        elif "possible_values: Optional[List[str]] = Field(None, description=\"Possible values for select/radio\")" in line:
            fixed_lines.append("    possible_values: Optional[List[str]] = Field(\n")
            fixed_lines.append("        None, description=\"Possible values for select/radio\")\n")
        elif "validation_patterns: Optional[List[str]] = Field(None, description=\"Validation patterns for inputs\")" in line:
            fixed_lines.append("    validation_patterns: Optional[List[str]] = Field(\n")
            fixed_lines.append("        None, description=\"Validation patterns for inputs\")\n")
        elif "test_code: str = Field(..., description=\"Actual test code in specified framework (Selenium/Playwright)\")" in line:
            fixed_lines.append("    test_code: str = Field(\n")
            fixed_lines.append("        ..., description=\"Test code in specified framework\")\n")
        elif "enriched_elements: List[EnrichedElement] = Field(default_factory=list, description=\"Enhanced elements\")" in line:
            fixed_lines.append("    enriched_elements: List[EnrichedElement] = Field(\n")
            fixed_lines.append("        default_factory=list, description=\"Enhanced elements\")\n")
        elif len(line.rstrip()) > 79 and "description=" in line:
            # Generic field with long description
            parts = line.split("description=")
            if len(parts) == 2:
                fixed_lines.append(parts[0] + "\n")
                fixed_lines.append("        description=" + parts[1])
            else:
                fixed_lines.append(line)
        else:
            # Try to break at logical points
            if " = Field(" in line and len(line.rstrip()) > 79:
                parts = line.split(" = Field(")
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(parts[0] + " = Field(\n")
                fixed_lines.append(" " * (indent + 4) + parts[1])
            elif ", description=" in line and len(line.rstrip()) > 79:
                parts = line.split(", description=")
                fixed_lines.append(parts[0] + ",\n")
                fixed_lines.append("        description=" + parts[1])
            else:
                fixed_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    print(f"Fixed long lines in {file_path}")


def fix_browser_issues():
    """Fix remaining issues in browser.py"""
    file_path = 'browser.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove unused imports
    content = re.sub(r'^# import json.*$', '', content, flags=re.MULTILINE)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed issues in {file_path}")


if __name__ == "__main__":
    fix_long_lines('data_types.py')
    fix_browser_issues()
    print("All linting issues fixed!")