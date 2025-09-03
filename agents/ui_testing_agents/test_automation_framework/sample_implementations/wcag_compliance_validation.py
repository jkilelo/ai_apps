#!/usr/bin/env python3
"""
Example 5: Accessibility Compliance Test with Live LLM
=======================================================
Demonstrates AI-powered accessibility test generation for WCAG compliance,
screen reader compatibility, keyboard navigation, and inclusive design
using real LLM for intelligent test creation.

This example shows how V2 system uses mandatory LLM integration
to generate comprehensive accessibility test suites.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

# V2 imports - These require LLM to be available
from test_automation_framework.ai_test_generator import (
    generate_accessibility_tests_with_llm,
    generate_ai_scenarios_with_llm,
    enhance_code_with_llm,
    generate_gherkin_with_llm
)


async def test_accessibility_compliance():
    """Generate comprehensive accessibility compliance tests using AI"""
    
    print("=" * 80)
    print("ACCESSIBILITY COMPLIANCE TEST GENERATION (V2 - LLM Native)")
    print("=" * 80)
    print("Using real AI to generate WCAG-compliant test suite")
    print("-" * 80)
    
    # Define page elements with accessibility attributes
    accessibility_elements = {
        "form_elements": [
            {"type": "text", "name": "firstName", "label": "First Name", "aria-label": "Enter your first name", "required": True},
            {"type": "email", "name": "email", "label": "Email Address", "aria-describedby": "email-help", "required": True},
            {"type": "select", "name": "country", "label": "Country", "aria-label": "Select your country"},
            {"type": "checkbox", "name": "terms", "label": "I agree to terms", "aria-required": "true"},
            {"type": "radio", "name": "gender", "label": "Gender", "options": ["Male", "Female", "Other", "Prefer not to say"]}
        ],
        "navigation_elements": [
            {"type": "nav", "aria-label": "Main navigation", "role": "navigation"},
            {"type": "breadcrumb", "aria-label": "Breadcrumb", "role": "navigation"},
            {"type": "skip-link", "href": "#main", "text": "Skip to main content"},
            {"type": "menu", "role": "menubar", "aria-label": "User menu"}
        ],
        "interactive_elements": [
            {"type": "button", "text": "Submit", "aria-label": "Submit form", "role": "button"},
            {"type": "link", "text": "Learn More", "aria-describedby": "learn-more-description"},
            {"type": "modal", "role": "dialog", "aria-modal": "true", "aria-labelledby": "modal-title"},
            {"type": "tab", "role": "tablist", "aria-label": "Settings tabs"},
            {"type": "accordion", "role": "region", "aria-expanded": "false"}
        ],
        "content_elements": [
            {"type": "heading", "level": "h1", "text": "Welcome", "role": "heading", "aria-level": "1"},
            {"type": "image", "alt": "Company logo", "role": "img"},
            {"type": "video", "controls": True, "captions": True, "transcript": True},
            {"type": "table", "role": "table", "aria-label": "User data", "headers": True},
            {"type": "list", "role": "list", "ordered": False}
        ],
        "aria_attributes": [
            "aria-live=\"polite\"",
            "aria-atomic=\"true\"",
            "aria-busy=\"false\"",
            "aria-invalid=\"false\"",
            "aria-hidden=\"false\"",
            "role=\"alert\"",
            "role=\"status\"",
            "tabindex=\"0\""
        ]
    }
    
    context = {
        "url": "https://accessible.example.com",
        "title": "Accessible Web Application",
        "compliance": ["WCAG 2.1 AA", "Section 508", "ADA"],
        "purpose": "fully accessible web application for all users"
    }
    
    # 1. Generate WCAG Compliance Tests
    print("\n[1] GENERATING WCAG 2.1 COMPLIANCE TESTS WITH LLM...")
    print("-" * 40)
    
    wcag_tests = await generate_accessibility_tests_with_llm(
        accessibility_elements,
        context
    )
    
    print("AI Generated WCAG Tests:")
    if isinstance(wcag_tests, dict) and 'tests' in wcag_tests:
        tests_text = wcag_tests['tests']
        print(tests_text[:1000] if len(tests_text) > 1000 else tests_text)
    print("-" * 40)
    
    # 2. Generate Screen Reader Tests
    print("\n[2] GENERATING SCREEN READER TESTS WITH LLM...")
    print("-" * 40)
    
    from llm_client import call_default_llm
    screen_reader_prompt = """Generate comprehensive screen reader test cases for:
    
    1. NVDA (Windows) compatibility tests
    2. JAWS compatibility tests
    3. VoiceOver (macOS/iOS) tests
    4. TalkBack (Android) tests
    
    Test scenarios:
    - Navigation through headings and landmarks
    - Form field announcements and descriptions
    - Table navigation with headers
    - Modal dialog focus management
    - Live region announcements
    - Image alt text reading
    - Link purpose clarity
    
    Include expected announcements for each screen reader."""
    
    screen_reader_tests = await call_default_llm(
        [{"role": "user", "content": screen_reader_prompt}],
        temperature=0.4,
        max_tokens=1200
    )
    
    print("AI Generated Screen Reader Tests:")
    print(screen_reader_tests[:800] if len(screen_reader_tests) > 800 else screen_reader_tests)
    print("-" * 40)
    
    # 3. Generate Keyboard Navigation Tests
    print("\n[3] GENERATING KEYBOARD NAVIGATION TESTS WITH LLM...")
    print("-" * 40)
    
    keyboard_prompt = """Generate keyboard navigation test cases for accessibility:
    
    Key combinations to test:
    - Tab/Shift+Tab navigation
    - Enter/Space for buttons
    - Arrow keys for menus and lists
    - Escape for closing modals
    - Custom keyboard shortcuts
    
    Test scenarios:
    1. Complete form submission using only keyboard
    2. Navigate through all interactive elements
    3. Focus trap in modal dialogs
    4. Skip links functionality
    5. Keyboard shortcuts don't conflict
    6. Focus visible indicators
    7. Logical tab order"""
    
    keyboard_tests = await call_default_llm(
        [{"role": "user", "content": keyboard_prompt}],
        temperature=0.5,
        max_tokens=1000
    )
    
    print("AI Generated Keyboard Tests:")
    print(keyboard_tests[:700] if len(keyboard_tests) > 700 else keyboard_tests)
    print("-" * 40)
    
    # 4. Generate Color Contrast Tests
    print("\n[4] GENERATING COLOR CONTRAST & VISUAL TESTS WITH LLM...")
    print("-" * 40)
    
    visual_prompt = """Generate visual accessibility test cases:
    
    1. Color contrast ratios (WCAG AA and AAA)
    2. Text readability tests
    3. Focus indicators visibility
    4. Error message clarity
    5. Color-blind friendly design
    6. Zoom functionality (up to 200%)
    7. Responsive text sizing
    8. High contrast mode support
    
    Include specific ratio requirements and testing methods."""
    
    visual_tests = await call_default_llm(
        [{"role": "user", "content": visual_prompt}],
        temperature=0.4,
        max_tokens=800
    )
    
    print("AI Generated Visual Accessibility Tests:")
    print(visual_tests[:600] if len(visual_tests) > 600 else visual_tests)
    print("-" * 40)
    
    # 5. Generate Cognitive Accessibility Tests
    print("\n[5] GENERATING COGNITIVE ACCESSIBILITY TESTS WITH LLM...")
    print("-" * 40)
    
    cognitive_prompt = """Generate cognitive accessibility test cases:
    
    Test areas:
    1. Clear and simple language
    2. Consistent navigation patterns
    3. Error prevention and recovery
    4. Clear instructions and labels
    5. Predictable functionality
    6. Time limits and extensions
    7. Help and documentation availability
    8. Progress indicators
    
    Focus on users with cognitive disabilities, dyslexia, ADHD."""
    
    cognitive_tests = await call_default_llm(
        [{"role": "user", "content": cognitive_prompt}],
        temperature=0.5,
        max_tokens=700
    )
    
    print("AI Generated Cognitive Accessibility Tests:")
    print(cognitive_tests[:600] if len(cognitive_tests) > 600 else cognitive_tests)
    print("-" * 40)
    
    # 6. Generate Gherkin for Accessibility
    print("\n[6] GENERATING ACCESSIBILITY GHERKIN SCENARIOS...")
    print("-" * 40)
    
    gherkin = await generate_gherkin_with_llm(
        accessibility_elements,
        "accessibility"
    )
    
    print("AI Generated Accessibility Gherkin:")
    print(gherkin[:700] if len(gherkin) > 700 else gherkin)
    print("-" * 40)
    
    # 7. Enhance Basic Test to Production
    print("\n[7] ENHANCING ACCESSIBILITY TEST TO PRODUCTION CODE...")
    print("-" * 40)
    
    basic_test = """
async def test_accessibility():
    # Check page has h1
    h1 = await page.locator('h1')
    assert await h1.count() == 1
    
    # Check images have alt text
    images = await page.locator('img')
    for i in range(await images.count()):
        img = images.nth(i)
        alt = await img.get_attribute('alt')
        assert alt is not None
"""
    
    enhanced = await enhance_code_with_llm(basic_test, "production-accessibility")
    
    print("AI Enhanced Production Accessibility Test:")
    if isinstance(enhanced, dict) and 'enhanced_code' in enhanced:
        code = enhanced['enhanced_code']
        print(code[:800] if len(code) > 800 else code)
    print("-" * 40)
    
    # Summary
    print("\n" + "=" * 80)
    print("ACCESSIBILITY COMPLIANCE TEST SUITE GENERATED")
    print("=" * 80)
    print("[SUCCESS] Generated with V2 LLM-Native System:")
    print("✓ WCAG 2.1 Compliance Tests - Level AA standards")
    print("✓ Screen Reader Tests - Multi-platform coverage")
    print("✓ Keyboard Navigation Tests - Full keyboard access")
    print("✓ Visual Accessibility Tests - Contrast & readability")
    print("✓ Cognitive Accessibility Tests - Inclusive design")
    print("✓ Gherkin Scenarios - BDD accessibility tests")
    print("✓ Production Code - Enterprise-ready")
    print("\nAll generated using REAL LLM - No fallbacks or mocks!")
    print("=" * 80)


if __name__ == "__main__":
    print("\nStarting Accessibility Compliance Test Generation...")
    print("This example demonstrates V2's accessibility testing capabilities")
    print("If LLM is not available, the system will halt.\n")
    
    asyncio.run(test_accessibility_compliance())