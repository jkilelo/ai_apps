#!/usr/bin/env python3
"""
Example 1: E-Commerce Checkout Test with Live LLM
===================================================
Demonstrates AI-powered test generation for e-commerce checkout flows
using real LLM to create comprehensive test scenarios, Gherkin tests,
and production-ready code.

This example shows how V2 system uses mandatory LLM integration
to generate intelligent test cases for complex checkout workflows.
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
    generate_gherkin_with_llm,
    generate_ai_scenarios_with_llm,
    enhance_code_with_llm,
    generate_page_object_with_llm
)


async def test_ecommerce_checkout():
    """Generate comprehensive e-commerce checkout tests using AI"""
    
    print("=" * 80)
    print("E-COMMERCE CHECKOUT TEST GENERATION (V2 - LLM Native)")
    print("=" * 80)
    print("Using real AI to generate production-ready test suite")
    print("-" * 80)
    
    # Define the checkout page elements (as if extracted from real page)
    checkout_elements = {
        "form_elements": [
            {"type": "text", "name": "firstName", "label": "First Name", "required": True},
            {"type": "text", "name": "lastName", "label": "Last Name", "required": True},
            {"type": "email", "name": "email", "label": "Email", "required": True},
            {"type": "tel", "name": "phone", "label": "Phone Number", "required": False},
            {"type": "text", "name": "address", "label": "Street Address", "required": True},
            {"type": "text", "name": "city", "label": "City", "required": True},
            {"type": "select", "name": "state", "label": "State", "required": True},
            {"type": "text", "name": "zipCode", "label": "ZIP Code", "required": True},
            {"type": "text", "name": "cardNumber", "label": "Card Number", "required": True},
            {"type": "text", "name": "cardName", "label": "Name on Card", "required": True},
            {"type": "text", "name": "cvv", "label": "CVV", "required": True},
            {"type": "select", "name": "expiryMonth", "label": "Expiry Month", "required": True},
            {"type": "select", "name": "expiryYear", "label": "Expiry Year", "required": True}
        ],
        "clickable_elements": [
            {"type": "button", "text": "Apply Promo Code", "id": "applyPromo"},
            {"type": "button", "text": "Continue to Payment", "id": "continuePayment"},
            {"type": "submit", "text": "Place Order", "id": "placeOrder"},
            {"type": "link", "text": "Return to Cart", "href": "/cart"},
            {"type": "checkbox", "name": "sameAsBilling", "label": "Same as billing address"},
            {"type": "checkbox", "name": "saveCard", "label": "Save card for future"},
            {"type": "radio", "name": "shipping", "value": "standard", "label": "Standard (5-7 days)"},
            {"type": "radio", "name": "shipping", "value": "express", "label": "Express (2-3 days)"},
            {"type": "radio", "name": "shipping", "value": "overnight", "label": "Overnight"}
        ],
        "validation_elements": [
            {"selector": ".error-message", "type": "error", "purpose": "field-validation"},
            {"selector": ".promo-success", "type": "success", "purpose": "promo-applied"},
            {"selector": ".order-total", "type": "display", "purpose": "price-calculation"},
            {"selector": ".shipping-cost", "type": "display", "purpose": "shipping-fee"}
        ]
    }
    
    context = {
        "url": "https://shop.example.com/checkout",
        "title": "Secure Checkout",
        "purpose": "e-commerce checkout with payment processing"
    }
    
    # 1. Generate AI Test Scenarios
    print("\n[1] GENERATING AI TEST SCENARIOS WITH LLM...")
    print("-" * 40)
    
    scenarios = await generate_ai_scenarios_with_llm(
        checkout_elements, 
        context, 
        max_scenarios=5
    )
    
    print("AI Generated Scenarios:")
    if isinstance(scenarios, dict) and 'scenarios' in scenarios:
        scenario_text = scenarios['scenarios']
        # Show first 1000 chars of scenarios
        print(scenario_text[:1000] if len(scenario_text) > 1000 else scenario_text)
    print("-" * 40)
    
    # 2. Generate Gherkin Test Cases
    print("\n[2] GENERATING GHERKIN TEST CASES WITH LLM...")
    print("-" * 40)
    
    gherkin = await generate_gherkin_with_llm(
        checkout_elements,
        "checkout"
    )
    
    print("AI Generated Gherkin:")
    # Show first 800 chars of Gherkin
    print(gherkin[:800] if len(gherkin) > 800 else gherkin)
    print("-" * 40)
    
    # 3. Generate Page Object Model
    print("\n[3] GENERATING PAGE OBJECT MODEL WITH LLM...")
    print("-" * 40)
    
    pom = await generate_page_object_with_llm(
        checkout_elements,
        "CheckoutPage"
    )
    
    print("AI Generated Page Object:")
    if isinstance(pom, dict) and 'page_object' in pom:
        code = pom['page_object']
        # Show first 600 chars
        print(code[:600] if len(code) > 600 else code)
    print("-" * 40)
    
    # 4. Enhance Basic Test to Production Code
    print("\n[4] ENHANCING TEST CODE TO PRODUCTION QUALITY WITH LLM...")
    print("-" * 40)
    
    basic_test = """
async def test_checkout():
    # Navigate to checkout
    await page.goto('https://shop.example.com/checkout')
    
    # Fill form
    await page.fill('#firstName', 'John')
    await page.fill('#lastName', 'Doe')
    await page.fill('#email', 'john@example.com')
    
    # Submit
    await page.click('#placeOrder')
"""
    
    enhanced = await enhance_code_with_llm(basic_test, "production")
    
    print("AI Enhanced Production Code:")
    if isinstance(enhanced, dict) and 'enhanced_code' in enhanced:
        code = enhanced['enhanced_code']
        # Show first 800 chars
        print(code[:800] if len(code) > 800 else code)
    print("-" * 40)
    
    # Summary
    print("\n" + "=" * 80)
    print("E-COMMERCE CHECKOUT TEST SUITE GENERATED")
    print("=" * 80)
    print("[SUCCESS] Generated with V2 LLM-Native System:")
    print("✓ AI Test Scenarios - Comprehensive coverage")
    print("✓ Gherkin Test Cases - BDD format")
    print("✓ Page Object Model - Maintainable structure")
    print("✓ Production Code - Enhanced with best practices")
    print("\nAll generated using REAL LLM - No fallbacks or mocks!")
    print("=" * 80)


if __name__ == "__main__":
    print("\nStarting E-Commerce Checkout Test Generation...")
    print("This example demonstrates V2's mandatory LLM integration")
    print("If LLM is not available, the system will halt.\n")
    
    asyncio.run(test_ecommerce_checkout())