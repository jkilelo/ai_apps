#!/usr/bin/env python3
"""
Response Validator for Claude Code
Ensures all responses follow the strict rules defined in .claude/
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

class ResponseValidator:
    """Validates Claude responses against strict rules"""
    
    # Banned Unicode characters and their replacements
    UNICODE_REPLACEMENTS = {
        '✓': '[OK]',
        '✗': '[FAIL]',
        '✅': '[PASS]',
        '❌': '[ERROR]',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '•': '-',
        '◦': 'o',
        '▪': '*',
        '—': '--',
        '–': '-',
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"',
        '…': '...',
        '°': 'deg',
        '×': 'x',
        '÷': '/',
        '±': '+/-',
        '≈': '~',
        '≠': '!=',
        '≤': '<=',
        '≥': '>=',
        '∞': 'inf',
        'π': 'pi',
    }
    
    # Banned emoji patterns
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    
    # Banned phrases that indicate wrong behavior
    BANNED_PHRASES = [
        "let me provide a summary",
        "let me summarize",
        "here's what we accomplished",
        "although it failed",
        "despite the errors",
        "the module is working but",
        "there are issues but",
        "moving on to",
        "let's continue with",
        "the test failed but",
        "it's failing but"
    ]
    
    def __init__(self):
        self.violations = []
        
    def validate(self, text: str) -> Tuple[bool, List[str]]:
        """Validate text against all rules"""
        self.violations = []
        
        # Check for Unicode characters
        self._check_unicode(text)
        
        # Check for emojis
        self._check_emojis(text)
        
        # Check for banned phrases
        self._check_banned_phrases(text)
        
        # Check for testing pattern violations
        self._check_testing_pattern(text)
        
        return len(self.violations) == 0, self.violations
    
    def _check_unicode(self, text: str):
        """Check for banned Unicode characters"""
        for char, replacement in self.UNICODE_REPLACEMENTS.items():
            if char in text:
                self.violations.append(
                    f"Unicode violation: Found '{char}', should use '{replacement}'"
                )
                
        # Check for any non-ASCII characters
        for i, char in enumerate(text):
            if ord(char) > 127:
                if char not in self.UNICODE_REPLACEMENTS:
                    self.violations.append(
                        f"Non-ASCII character at position {i}: '{char}' (code: {ord(char)})"
                    )
    
    def _check_emojis(self, text: str):
        """Check for emoji usage"""
        emojis = self.EMOJI_PATTERN.findall(text)
        if emojis:
            self.violations.append(
                f"Emoji violation: Found emojis {emojis}"
            )
    
    def _check_banned_phrases(self, text: str):
        """Check for banned phrases"""
        text_lower = text.lower()
        for phrase in self.BANNED_PHRASES:
            if phrase in text_lower:
                self.violations.append(
                    f"Banned phrase: '{phrase}'"
                )
    
    def _check_testing_pattern(self, text: str):
        """Check if testing pattern is followed"""
        lines = text.lower().split('\n')
        
        # Check for test failure followed by summary
        for i, line in enumerate(lines):
            if 'test failed' in line or 'error' in line:
                # Check next few lines for summaries
                for j in range(i+1, min(i+5, len(lines))):
                    if any(phrase in lines[j] for phrase in [
                        'summary', 'accomplished', 'but', 'however',
                        'overall', 'in conclusion'
                    ]):
                        self.violations.append(
                            f"Testing pattern violation: Summary after failure at line {j+1}"
                        )
    
    def fix_text(self, text: str) -> str:
        """Fix violations in text"""
        fixed = text
        
        # Replace Unicode characters
        for char, replacement in self.UNICODE_REPLACEMENTS.items():
            fixed = fixed.replace(char, replacement)
        
        # Remove emojis
        fixed = self.EMOJI_PATTERN.sub('', fixed)
        
        # Ensure ASCII only
        fixed = fixed.encode('ascii', 'replace').decode('ascii')
        
        return fixed
    
    def validate_file(self, filepath: Path) -> Tuple[bool, List[str]]:
        """Validate a file's content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.validate(content)
        except Exception as e:
            return False, [f"Error reading file: {e}"]

def main():
    """CLI interface for validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Claude responses')
    parser.add_argument('input', help='Text or file to validate')
    parser.add_argument('--file', action='store_true', help='Input is a file path')
    parser.add_argument('--fix', action='store_true', help='Fix violations')
    
    args = parser.parse_args()
    
    validator = ResponseValidator()
    
    if args.file:
        filepath = Path(args.input)
        is_valid, violations = validator.validate_file(filepath)
        
        if args.fix and not is_valid:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            fixed = validator.fix_text(content)
            
            # Save to new file
            fixed_path = filepath.with_suffix('.fixed' + filepath.suffix)
            with open(fixed_path, 'w', encoding='utf-8') as f:
                f.write(fixed)
            print(f"Fixed content saved to: {fixed_path}")
    else:
        is_valid, violations = validator.validate(args.input)
        
        if args.fix and not is_valid:
            fixed = validator.fix_text(args.input)
            print("Fixed text:")
            print(fixed)
    
    if is_valid:
        print("[OK] No violations found")
    else:
        print(f"[FAIL] Found {len(violations)} violations:")
        for v in violations:
            # Ensure ASCII output
            v_safe = v.encode('ascii', 'replace').decode('ascii')
            print(f"  - {v_safe}")
        sys.exit(1)

if __name__ == "__main__":
    main()