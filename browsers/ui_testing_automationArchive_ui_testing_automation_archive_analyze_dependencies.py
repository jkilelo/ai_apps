#!/usr/bin/env python3
"""
Analyze module dependencies to determine core files vs test/archive files
"""

import os
import re
import ast
from pathlib import Path
from typing import Set, Dict, List

class DependencyAnalyzer:
    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = {}
        self.core_modules = {
            # Layer 0: Base modules
            'base/browser.py',
            'base/llm.py', 
            'base/prompts.py',
            'base/llm_streaming.py',
            
            # Layer 1: Integration
            'browser_with_llm.py',
            
            # Layer 2: Domain modules
            'elements_extractor_no_llm.py',
            'elements_extractor_with_llm.py',
            'test_generation_with_llm.py',
            'code_generation_with_llm.py',
            'code_execution.py',
            
            # Layer 3: Orchestration
            'pipeline_integration.py',
            
            # Contracts and shared
            'pipeline_contracts.py',
            'structured_output_enforcer.py',
            
            # Configuration
            'llm_models.json',
            'CLAUDE.md',
            'ARCHITECTURE.md',
            
            # Setup
            'requirements.txt',
            '__init__.py'
        }
        
    def extract_imports(self, filepath: Path) -> Set[str]:
        """Extract imported modules from a Python file"""
        imports = set()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except:
            pass
        return imports
    
    def analyze_directory(self, directory: Path):
        """Analyze all Python files in directory"""
        py_files = list(directory.glob('*.py'))
        py_files.extend(list((directory / 'base').glob('*.py')) if (directory / 'base').exists() else [])
        
        # Categorize files
        core_files = []
        test_files = []
        example_files = []
        utility_files = []
        archive_candidates = []
        
        for file in py_files:
            relative_path = file.relative_to(directory)
            filepath_str = str(relative_path)
            
            # Check if it's a core module
            if filepath_str in self.core_modules or relative_path.name == '__init__.py':
                core_files.append(filepath_str)
            # Check if it's a test file
            elif filepath_str.startswith('test_') or 'test' in filepath_str.lower():
                test_files.append(filepath_str)
            # Check if it's an example
            elif 'example' in filepath_str.lower() or filepath_str.startswith('demo_'):
                example_files.append(filepath_str)
            # Check if it's a utility/helper
            elif filepath_str in ['analyze_dependencies.py', 'setup.py', 'claude_setup.py']:
                utility_files.append(filepath_str)
            # Everything else is archive candidate
            else:
                archive_candidates.append(filepath_str)
        
        return {
            'core': core_files,
            'tests': test_files,
            'examples': example_files,
            'utilities': utility_files,
            'archive': archive_candidates
        }
    
    def find_duplicates(self, directory: Path):
        """Find duplicate and backup files"""
        duplicates = []
        
        patterns = [
            '*.py.backup',
            '*_copy.py',
            '*_old.py',
            '*_backup.py',
            '* copy.py',
            '*_refactored.py',
            '*_original.py',
            '*_fixed.py',
            '*_v2.py'
        ]
        
        for pattern in patterns:
            duplicates.extend(directory.glob(pattern))
            
        # Also find numbered copies
        for file in directory.glob('*.py'):
            if re.search(r'_\d+\.py$', file.name) or ' copy' in file.name:
                duplicates.append(file)
                
        return [str(f.relative_to(directory)) for f in duplicates]

def main():
    analyzer = DependencyAnalyzer()
    current_dir = Path.cwd()
    
    print("[DEPENDENCY ANALYSIS] UI Testing Automation Framework")
    print("=" * 70)
    
    # Analyze all files
    categories = analyzer.analyze_directory(current_dir)
    
    print("\n[CORE APPLICATION FILES] (Keep these)")
    print("-" * 50)
    for file in sorted(categories['core']):
        print(f"  [KEEP] {file}")
    
    print(f"\nTotal: {len(categories['core'])} core files")
    
    print("\n[TEST FILES] (Move to archive)")
    print("-" * 50)
    for file in sorted(categories['tests']):
        print(f"  [ARCHIVE] {file}")
    
    print(f"\nTotal: {len(categories['tests'])} test files")
    
    print("\n[EXAMPLE FILES] (Move to archive)")
    print("-" * 50)
    for file in sorted(categories['examples']):
        print(f"  [ARCHIVE] {file}")
        
    print(f"\nTotal: {len(categories['examples'])} example files")
    
    print("\n[UTILITY FILES] (Move to archive)")
    print("-" * 50)
    for file in sorted(categories['utilities']):
        print(f"  [ARCHIVE] {file}")
        
    print(f"\nTotal: {len(categories['utilities'])} utility files")
    
    print("\n[OTHER FILES] (Move to archive)")
    print("-" * 50)
    for file in sorted(categories['archive']):
        print(f"  [ARCHIVE] {file}")
        
    print(f"\nTotal: {len(categories['archive'])} other files")
    
    # Find duplicates
    duplicates = analyzer.find_duplicates(current_dir)
    if duplicates:
        print("\n[DUPLICATE/BACKUP FILES] (Move to archive)")
        print("-" * 50)
        for file in sorted(duplicates):
            print(f"  [ARCHIVE] {file}")
        print(f"\nTotal: {len(duplicates)} duplicate files")
    
    # Non-Python files to check
    print("\n[NON-PYTHON FILES TO CHECK]")
    print("-" * 50)
    
    other_files = [
        '*.json',
        '*.md', 
        '*.txt',
        '*.yaml',
        '*.yml',
        '*.bat',
        '*.sh',
        '*.html',
        '*.log'
    ]
    
    keep_files = {
        'llm_models.json',
        'CLAUDE.md',
        'ARCHITECTURE.md', 
        'requirements.txt',
        '.gitignore',
        'README.md'
    }
    
    for pattern in other_files:
        for file in current_dir.glob(pattern):
            relative = file.relative_to(current_dir)
            if relative.name in keep_files:
                print(f"  [KEEP] {relative}")
            else:
                print(f"  [ARCHIVE] {relative}")
    
    # Calculate totals
    total_archive = (len(categories['tests']) + len(categories['examples']) + 
                    len(categories['utilities']) + len(categories['archive']) + 
                    len(duplicates))
    
    print("\n" + "=" * 70)
    print("[SUMMARY]")
    print(f"  Core files to keep: {len(categories['core'])}")
    print(f"  Files to archive: {total_archive}")
    print(f"  Space to be freed: ~{total_archive * 10}KB (estimated)")
    
    return categories, duplicates

if __name__ == "__main__":
    categories, duplicates = main()