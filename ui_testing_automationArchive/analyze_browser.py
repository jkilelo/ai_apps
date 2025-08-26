#!/usr/bin/env python3
"""Analyze browser.py to identify unused imports and clean up the file."""

import sys
import os
import ast
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.code_services import ChunkService, ChunkConfig, ChunkStrategy

async def analyze_browser_file():
    """Analyze browser.py file for unused imports and structure."""
    
    # Initialize ChunkService
    config = ChunkConfig(
        strategy=ChunkStrategy.SMART,
        max_chunk_size=500,
        overlap_size=50
    )
    chunk_service = ChunkService(config)
    
    # Read and chunk the browser.py file
    browser_path = Path(__file__).parent / "browser.py"
    
    try:
        # Read the entire file first
        with open(browser_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            
        # Parse AST to find all imports
        tree = ast.parse(full_content)
        
        # Collect all imports
        imports = set()
        imported_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
                    imported_names.add(alias.asname if alias.asname else alias.name.split('.')[-1])
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.add(f"{module}.{alias.name}" if module else alias.name)
                    imported_names.add(alias.asname if alias.asname else alias.name)
        
        # Find which imports are actually used
        # Remove imports from the content to avoid false positives
        lines = full_content.split('\n')
        code_without_imports = []
        for line in lines:
            if not (line.strip().startswith('import ') or line.strip().startswith('from ')):
                code_without_imports.append(line)
        code_body = '\n'.join(code_without_imports)
        
        # Check which imported names are used
        used_names = set()
        for name in imported_names:
            # Check if the name appears in the code (not in comments or strings)
            # Simple heuristic: look for word boundaries
            pattern = r'\b' + re.escape(name) + r'\b'
            if re.search(pattern, code_body):
                used_names.add(name)
        
        unused_imports = imported_names - used_names
        
        print("Analysis Results:")
        print("=" * 60)
        print(f"Total imports found: {len(imported_names)}")
        print(f"Used imports: {len(used_names)}")
        print(f"Unused imports: {len(unused_imports)}")
        print("\nUnused imports:")
        for imp in sorted(unused_imports):
            print(f"  - {imp}")
            
        # Find duplicate imports
        import_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_lines.append((i, line))
        
        print("\nDuplicate import blocks found:")
        # Check for duplicate logging configuration
        logging_configs = [i for i, line in enumerate(lines) if 'logging.basicConfig' in line]
        if len(logging_configs) > 1:
            print(f"  - Multiple logging configurations at lines: {logging_configs}")
            
        return unused_imports, lines
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return set(), []

if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_browser_file())