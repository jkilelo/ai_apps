#!/usr/bin/env python3
"""
Clean all Unicode characters from prompts.py and replace with ASCII equivalents
"""

import re

# Read the file
with open('prompts.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacements for common Unicode characters
replacements = {
    '→': '->',
    '←': '<-',
    '↔': '<->',
    '⇒': '=>',
    '⇔': '<=>',
    '↑': '^',
    '↓': 'v',
    '×': '*',
    '÷': '/',
    '≤': '<=',
    '≥': '>=',
    '≠': '!=',
    '≈': '~=',
    '∞': 'inf',
    '∀': 'forall',
    '∃': 'exists',
    '∈': 'in',
    '∉': 'not in',
    '⊆': 'subset',
    '⊇': 'superset',
    '∧': 'and',
    '∨': 'or',
    '¬': 'not',
    '⊕': 'XOR',
    '⊗': 'tensor',
    'Σ': 'SUM',
    '∏': 'PROD',
    '∫': 'INT',
    '∇': 'grad',
    '∂': 'partial',
    '√': 'sqrt',
    '∝': 'proportional',
    '⟨': '<',
    '⟩': '>',
    'α': 'alpha',
    'β': 'beta',
    'γ': 'gamma',
    'δ': 'delta',
    'ε': 'epsilon',
    'θ': 'theta',
    'λ': 'lambda',
    'μ': 'mu',
    'π': 'pi',
    'σ': 'sigma',
    'τ': 'tau',
    'φ': 'phi',
    'ω': 'omega',
    '₀': '_0',
    '₁': '_1',
    '₂': '_2',
    '₃': '_3',
    '₄': '_4',
    '₅': '_5',
    '₆': '_6',
    '₇': '_7',
    '₈': '_8',
    '₉': '_9',
    '⁰': '^0',
    '¹': '^1',
    '²': '^2',
    '³': '^3',
    '⁴': '^4',
    '⁵': '^5',
    '⁶': '^6',
    '⁷': '^7',
    '⁸': '^8',
    '⁹': '^9',
    'ⁿ': '^n',
    'ᵢ': '_i',
    'ⱼ': '_j',
    'ₙ': '_n',
    'ₜ': '_t',
    '✓': '[OK]',
    '✗': '[X]',
    '•': '-',
    '°': 'deg',
    '′': "'",
    '″': '"',
    '…': '...',
    '—': '--',
    '–': '-',
    ''': "'",
    ''': "'",
    '"': '"',
    '"': '"',
    '‹': '<',
    '›': '>',
    '«': '<<',
    '»': '>>',
    '№': 'No.',
    '©': '(c)',
    '®': '(R)',
    '™': '(TM)',
    '±': '+/-',
    '²': '2',
    '³': '3',
    '½': '1/2',
    '⅓': '1/3',
    '¼': '1/4',
    '⅔': '2/3',
    '¾': '3/4',
    '∅': 'empty',
    '∪': 'union',
    '∩': 'intersection',
    '⊂': 'subset',
    '⊃': 'superset',
    '∼': '~',
    '≡': '===',
    '⌊': 'floor(',
    '⌋': ')',
    '⌈': 'ceil(',
    '⌉': ')',
    '〈': '<',
    '〉': '>',
    '【': '[',
    '】': ']',
    '〔': '[',
    '〕': ']',
    '《': '<<',
    '》': '>>',
    '「': '"',
    '」': '"',
    '『': '"',
    '』': '"',
    '【': '[',
    '】': ']',
    '〖': '[',
    '〗': ']',
    '〘': '[',
    '〙': ']',
    '〚': '[',
    '〛': ']',
    # Add more macron characters
    'A\u0304': 'A_',
    'a\u0304': 'a_',
    'I\u0304': 'I_',
    'i\u0304': 'i_',
    'U\u0304': 'U_',
    'u\u0304': 'u_',
    'O\u0304': 'O_',
    'o\u0304': 'o_',
    'E\u0304': 'E_',
    'e\u0304': 'e_',
}

# Apply replacements
for unicode_char, ascii_replacement in replacements.items():
    content = content.replace(unicode_char, ascii_replacement)

# Remove any remaining non-ASCII characters (replace with ?)
def replace_non_ascii(match):
    char = match.group(0)
    # Try to handle common cases
    if ord(char) > 127:
        return '?'
    return char

# Find remaining non-ASCII characters
remaining_unicode = re.findall(r'[^\x00-\x7F]', content)
if remaining_unicode:
    print(f"Warning: {len(set(remaining_unicode))} unique non-ASCII characters remain")
    # Just replace them without trying to print them
    content = re.sub(r'[^\x00-\x7F]', '?', content)
    print("Replaced remaining non-ASCII characters with '?'")

# Write the cleaned content back
with open('prompts_cleaned.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Cleaned file written to prompts_cleaned.py")

# Check if it can be imported
try:
    import ast
    ast.parse(content)
    print("✓ File is valid Python syntax")
except SyntaxError as e:
    print(f"✗ Syntax error: {e}")