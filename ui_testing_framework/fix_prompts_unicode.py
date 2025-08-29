#!/usr/bin/env python3
"""
Comprehensive fix for all Unicode characters in prompts.py
"""

import re

# Read the file
with open('prompts.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track which lines we're modifying
modified_lines = []

for i, line in enumerate(lines, 1):
    original_line = line
    
    # Replace all common Unicode mathematical symbols
    line = line.replace('→', '->')
    line = line.replace('←', '<-')
    line = line.replace('↔', '<->')
    line = line.replace('⇒', '=>')
    line = line.replace('⇔', '<=>')
    line = line.replace('↑', '^')
    line = line.replace('↓', 'v')
    line = line.replace('×', '*')
    line = line.replace('÷', '/')
    line = line.replace('≤', '<=')
    line = line.replace('≥', '>=')
    line = line.replace('≠', '!=')
    line = line.replace('≈', '~=')
    line = line.replace('∞', 'inf')
    line = line.replace('∀', 'for all')
    line = line.replace('∃', 'exists')
    line = line.replace('∈', 'in')
    line = line.replace('∉', 'not in')
    line = line.replace('⊆', 'subset')
    line = line.replace('⊇', 'superset')
    line = line.replace('∧', 'and')
    line = line.replace('∨', 'or')
    line = line.replace('¬', 'not')
    line = line.replace('⊕', 'XOR')
    line = line.replace('⊗', 'tensor')
    line = line.replace('Σ', 'SUM')
    line = line.replace('∏', 'PROD')
    line = line.replace('∫', 'INT')
    line = line.replace('∇', 'grad')
    line = line.replace('∂', 'partial')
    line = line.replace('√', 'sqrt')
    line = line.replace('∝', 'proportional')
    line = line.replace('⟨', '<')
    line = line.replace('⟩', '>')
    line = line.replace('⟨', '<')
    line = line.replace('⟩', '>')
    line = line.replace('⟩', '>')
    
    # Greek letters
    line = line.replace('α', 'alpha')
    line = line.replace('β', 'beta')
    line = line.replace('γ', 'gamma')
    line = line.replace('δ', 'delta')
    line = line.replace('ε', 'epsilon')
    line = line.replace('θ', 'theta')
    line = line.replace('λ', 'lambda')
    line = line.replace('μ', 'mu')
    line = line.replace('π', 'pi')
    line = line.replace('σ', 'sigma')
    line = line.replace('τ', 'tau')
    line = line.replace('φ', 'phi')
    line = line.replace('ω', 'omega')
    line = line.replace('Ω', 'Omega')
    
    # Subscripts and superscripts
    line = line.replace('₀', '_0')
    line = line.replace('₁', '_1')
    line = line.replace('₂', '_2')
    line = line.replace('₃', '_3')
    line = line.replace('₄', '_4')
    line = line.replace('₅', '_5')
    line = line.replace('₆', '_6')
    line = line.replace('₇', '_7')
    line = line.replace('₈', '_8')
    line = line.replace('₉', '_9')
    line = line.replace('⁰', '^0')
    line = line.replace('¹', '^1')
    line = line.replace('²', '^2')
    line = line.replace('³', '^3')
    line = line.replace('⁴', '^4')
    line = line.replace('⁵', '^5')
    line = line.replace('⁶', '^6')
    line = line.replace('⁷', '^7')
    line = line.replace('⁸', '^8')
    line = line.replace('⁹', '^9')
    line = line.replace('ⁿ', '^n')
    line = line.replace('ᵢ', '_i')
    line = line.replace('ⱼ', '_j')
    line = line.replace('ₙ', '_n')
    line = line.replace('ₜ', '_t')
    
    # Checkmarks and crosses
    line = line.replace('✓', '[OK]')
    line = line.replace('✗', '[X]')
    line = line.replace('✔', '[OK]')
    line = line.replace('✖', '[X]')
    line = line.replace('☐', '[ ]')
    line = line.replace('☑', '[x]')
    line = line.replace('☒', '[X]')
    
    # Other symbols
    line = line.replace('•', '-')
    line = line.replace('°', 'deg')
    line = line.replace('′', "'")
    line = line.replace('″', '"')
    line = line.replace('…', '...')
    line = line.replace('—', '--')
    line = line.replace('–', '-')
    line = line.replace(''', "'")
    line = line.replace(''', "'")
    line = line.replace('"', '"')
    line = line.replace('"', '"')
    line = line.replace('‹', '<')
    line = line.replace('›', '>')
    line = line.replace('«', '<<')
    line = line.replace('»', '>>')
    line = line.replace('№', 'No.')
    line = line.replace('©', '(c)')
    line = line.replace('®', '(R)')
    line = line.replace('™', '(TM)')
    line = line.replace('±', '+/-')
    line = line.replace('½', '1/2')
    line = line.replace('⅓', '1/3')
    line = line.replace('¼', '1/4')
    line = line.replace('⅔', '2/3')
    line = line.replace('¾', '3/4')
    
    # Set theory
    line = line.replace('∅', 'empty')
    line = line.replace('∪', 'union')
    line = line.replace('∩', 'intersection')
    line = line.replace('⊂', 'subset')
    line = line.replace('⊃', 'superset')
    line = line.replace('∼', '~')
    line = line.replace('≡', '===')
    
    # Brackets
    line = line.replace('⌊', 'floor(')
    line = line.replace('⌋', ')')
    line = line.replace('⌈', 'ceil(')
    line = line.replace('⌉', ')')
    line = line.replace('〈', '<')
    line = line.replace('〉', '>')
    line = line.replace('⟨', '<')
    line = line.replace('⟩', '>')
    
    # Special mathematical symbols
    line = line.replace('ℝ', 'R')
    line = line.replace('ℕ', 'N')
    line = line.replace('ℤ', 'Z')
    line = line.replace('ℚ', 'Q')
    line = line.replace('ℂ', 'C')
    line = line.replace('∆', 'Delta')
    line = line.replace('∇', 'nabla')
    
    # Replace any remaining non-ASCII characters with safe alternatives
    # This catches anything we might have missed
    if any(ord(c) > 127 for c in line):
        # More aggressive replacement for any remaining Unicode
        new_line = ''
        for c in line:
            if ord(c) > 127:
                # Replace with a placeholder
                new_line += '?'
            else:
                new_line += c
        line = new_line
    
    if line != original_line:
        modified_lines.append((i, original_line.strip()[:50], line.strip()[:50]))
    
    lines[i-1] = line

# Write the cleaned content
with open('prompts.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Modified {len(modified_lines)} lines")

# Test if it's valid Python
try:
    with open('prompts.py', 'r', encoding='utf-8') as f:
        content = f.read()
    compile(content, 'prompts.py', 'exec')
    print("\n✓ File is valid Python syntax!")
except SyntaxError as e:
    print(f"\n✗ Syntax error at line {e.lineno}: {e.msg}")
    if e.text:
        print(f"  Text: {e.text}")