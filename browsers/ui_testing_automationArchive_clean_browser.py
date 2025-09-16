#!/usr/bin/env python3
"""Clean up browser.py by removing unused imports and unnecessary comments."""

import re
from pathlib import Path

def clean_browser_file():
    """Clean up the browser.py file."""
    
    browser_path = Path(__file__).parent / "browser.py"
    
    with open(browser_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track if we're in the main imports section
    cleaned_lines = []
    seen_imports = set()
    skip_next_logging = False
    logging_config_seen = False
    
    # Unused imports to remove
    unused_imports = {
        'ConfigDict', 'Counter', 'Path', 'cast', 'contextmanager',
        'defaultdict', 'field_validator', 'math', 'secrets', 
        'urljoin', 'urlparse'
    }
    
    # Remove unnecessary multi-line docstrings in middle of file
    skip_docstring = False
    docstring_start_line = 53  # The triple quote docstring that starts at line 53
    docstring_end_line = 68    # Where it ends
    
    for i, line in enumerate(lines, 1):
        # Skip the unnecessary docstring in middle of file
        if i >= docstring_start_line and i <= docstring_end_line:
            continue
            
        # Remove duplicate logging configuration
        if 'logging.basicConfig' in line:
            if logging_config_seen:
                # Skip the duplicate logging block (lines 125-130)
                if i >= 125 and i <= 130:
                    continue
            else:
                logging_config_seen = True
        
        # Skip duplicate logger creation
        if i == 130 and 'logger = logging.getLogger(__name__)' in line:
            continue
            
        # Remove unused imports
        if line.strip().startswith('from ') or line.strip().startswith('import '):
            # Check if this import contains unused names
            skip_line = False
            for unused in unused_imports:
                if re.search(r'\b' + unused + r'\b', line):
                    # Check if it's the only import on this line
                    if f'import {unused}' in line or f'from .* import.*{unused}' in re.sub(r'\s+', ' ', line):
                        skip_line = True
                        break
            
            if skip_line:
                continue
                
        # Remove duplicate imports (lines 70-91 are duplicates)
        if i >= 70 and i <= 91:
            # These are duplicate imports that were already defined earlier
            import_content = line.strip()
            if import_content.startswith('import ') or import_content.startswith('from '):
                # Skip duplicate basic imports
                if any(x in line for x in ['asyncio', 'json', 'logging', 'math', 'random', 're', 'time', 'hashlib', 
                                           'platform', 'os', 'sys', 'dataclasses', 'datetime', 'enum', 'typing',
                                           'urllib.parse', 'pathlib', 'collections', 'contextlib', 'functools']):
                    continue
        
        # Remove the duplicate Type variables definition
        if i == 51 and 'T = TypeVar' in line:
            # Check if we already have this
            already_defined = any('T = TypeVar' in l for l in cleaned_lines)
            if already_defined:
                continue
                
        cleaned_lines.append(line)
    
    # Write back the cleaned content
    with open(browser_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"Cleaned browser.py file")
    print(f"Original lines: {len(lines)}")
    print(f"Cleaned lines: {len(cleaned_lines)}")
    print(f"Removed: {len(lines) - len(cleaned_lines)} lines")

if __name__ == "__main__":
    clean_browser_file()