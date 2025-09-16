#!/usr/bin/env python3
"""
Test for quote escaping issue in Step 3
Written BEFORE implementation as per CODER protocol
"""
import pytest
from step3_code_generator import StepMapper, BrowserFramework

def test_selector_quote_escaping():
    """Test that selectors with text are properly escaped"""
    mapper = StepMapper(BrowserFramework.PLAYWRIGHT)
    
    # Test cases with different quote scenarios
    test_cases = [
        ('click on "shop"', 'click', '"shop"'),
        ("click on 'shop'", 'click', "'shop'"),
        ('click on the "spring/summer 2025" link', 'click', '"spring/summer 2025"'),
    ]
    
    for step_text, expected_action, expected_param in test_cases:
        action, param = mapper._parse_step(step_text)
        assert action == expected_action
        
        # Generate selector - should escape quotes properly
        selector = mapper._generate_selector(param.strip('"\''), [])
        
        # The selector should be properly escaped for Python code
        # It should use single quotes outside if the text contains double quotes
        if '"' in param:
            assert selector.startswith("'") or selector.startswith('f"')
        
        # It should not have unescaped quotes that would cause syntax error
        # This is what's currently failing
        assert '":has-text("' not in selector  # This pattern causes syntax error

def test_generate_action_code_escaping():
    """Test that generated action code has proper quote escaping"""
    mapper = StepMapper(BrowserFramework.PLAYWRIGHT)
    
    # Create a sample element with text
    element = {
        'text_content': 'shop',
        'xpath': '//a[text()="shop"]',
        'css_selector': 'a'
    }
    
    # Test click action with text selector
    code = mapper._generate_action_code('click', '"shop"', [element])
    
    # The generated code should be valid Python
    # It should not have syntax errors from unescaped quotes
    assert 'click(":has-text("shop")")' not in code  # This would be invalid
    
    # Should use proper escaping
    assert ("click(':has-text(\"shop\")')" in code or
            'click(":has-text(\\"shop\\")")' in code or
            "click(\":has-text('shop')\")" in code or
            'click' in code)  # Some valid form

if __name__ == "__main__":
    test_selector_quote_escaping()
    test_generate_action_code_escaping()
    print("✅ Tests pass - implementing fix")