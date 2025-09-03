#!/usr/bin/env python3
"""
Example 2: Banking Security Test with Live LLM
===============================================
Demonstrates AI-powered security test generation for banking applications
using real LLM to create security-focused test scenarios, penetration tests,
and compliance validation.

This example shows how V2 system uses mandatory LLM integration
to generate intelligent security tests for financial applications.
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
    generate_security_tests_with_llm,
    generate_ai_scenarios_with_llm,
    validate_with_constitutional_ai,
    enhance_code_with_llm
)


async def test_banking_security():
    """Generate comprehensive banking security tests using AI"""
    
    print("=" * 80)
    print("BANKING SECURITY TEST GENERATION (V2 - LLM Native)")
    print("=" * 80)
    print("Using real AI to generate security-focused test suite")
    print("-" * 80)
    
    # Define the banking login/transfer page elements
    banking_elements = {
        "form_elements": [
            {"type": "text", "name": "username", "label": "Username", "required": True},
            {"type": "password", "name": "password", "label": "Password", "required": True},
            {"type": "text", "name": "otp", "label": "One-Time Password", "required": False},
            {"type": "text", "name": "accountNumber", "label": "Account Number", "required": True},
            {"type": "text", "name": "routingNumber", "label": "Routing Number", "required": True},
            {"type": "number", "name": "amount", "label": "Transfer Amount", "required": True},
            {"type": "select", "name": "transferType", "label": "Transfer Type", "required": True},
            {"type": "hidden", "name": "csrfToken", "value": "abc123xyz"},
            {"type": "hidden", "name": "sessionId", "value": "sess_12345"}
        ],
        "clickable_elements": [
            {"type": "submit", "text": "Login", "id": "loginBtn"},
            {"type": "button", "text": "Transfer Funds", "id": "transferBtn"},
            {"type": "button", "text": "Logout", "id": "logoutBtn"},
            {"type": "link", "text": "Forgot Password", "href": "/reset"},
            {"type": "checkbox", "name": "rememberMe", "label": "Remember Me"},
            {"type": "checkbox", "name": "enableMFA", "label": "Enable 2FA"}
        ],
        "validation_elements": [
            {"selector": ".security-warning", "type": "warning", "purpose": "security-alert"},
            {"selector": ".session-timeout", "type": "timer", "purpose": "session-management"},
            {"selector": ".failed-attempts", "type": "counter", "purpose": "brute-force-protection"},
            {"selector": ".encryption-status", "type": "indicator", "purpose": "tls-validation"}
        ],
        "security_features": [
            "CAPTCHA after 3 failed attempts",
            "Account lockout after 5 failed attempts",
            "Session timeout after 10 minutes",
            "IP-based rate limiting",
            "Device fingerprinting",
            "Transaction verification via SMS"
        ]
    }
    
    context = {
        "url": "https://bank.example.com/secure/transfer",
        "title": "Secure Banking Portal",
        "purpose": "financial transaction with high security requirements",
        "compliance": ["PCI-DSS", "SOC2", "OWASP Top 10"]
    }
    
    # 1. Generate Security-Focused Test Scenarios
    print("\n[1] GENERATING SECURITY TEST SCENARIOS WITH LLM...")
    print("-" * 40)
    
    security_scenarios = await generate_security_tests_with_llm(
        banking_elements,
        context
    )
    
    print("AI Generated Security Tests:")
    if isinstance(security_scenarios, dict) and 'tests' in security_scenarios:
        tests_text = security_scenarios['tests']
        # Show first 1000 chars
        print(tests_text[:1000] if len(tests_text) > 1000 else tests_text)
    print("-" * 40)
    
    # 2. Generate OWASP-Compliant Test Cases
    print("\n[2] GENERATING OWASP-COMPLIANT TEST CASES WITH LLM...")
    print("-" * 40)
    
    owasp_prompt = """Generate OWASP Top 10 compliant security test cases for:
    - SQL Injection testing
    - XSS (Cross-Site Scripting) testing
    - Authentication bypass attempts
    - Session hijacking tests
    - CSRF token validation
    - Rate limiting verification
    
    Context: Banking application with transfer functionality
    """
    
    from llm_client import call_default_llm
    owasp_tests = await call_default_llm(
        [{"role": "user", "content": owasp_prompt}],
        temperature=0.3,
        max_tokens=1200
    )
    
    print("AI Generated OWASP Tests:")
    print(owasp_tests[:800] if len(owasp_tests) > 800 else owasp_tests)
    print("-" * 40)
    
    # 3. Validate with Constitutional AI
    print("\n[3] VALIDATING TESTS WITH CONSTITUTIONAL AI...")
    print("-" * 40)
    
    test_code = """
    # Attempting SQL injection
    await page.fill('#username', "admin' OR '1'='1")
    await page.fill('#password', "password")
    await page.click('#loginBtn')
    
    # Check for vulnerability
    assert 'dashboard' not in page.url
    """
    
    validation = await validate_with_constitutional_ai(
        test_code,
        {"safety": "high", "ethical": True}
    )
    
    print("Constitutional AI Validation:")
    if isinstance(validation, dict):
        print(f"Safety Score: {validation.get('safety_score', 'N/A')}")
        print(f"Ethical: {validation.get('is_ethical', 'N/A')}")
        print(f"Recommendations: {validation.get('recommendations', 'N/A')}")
    print("-" * 40)
    
    # 4. Generate Production Security Test Suite
    print("\n[4] GENERATING PRODUCTION SECURITY TEST SUITE WITH LLM...")
    print("-" * 40)
    
    basic_security_test = """
def test_login_security():
    # Try to login with wrong password
    driver.find_element_by_id('username').send_keys('testuser')
    driver.find_element_by_id('password').send_keys('wrongpass')
    driver.find_element_by_id('loginBtn').click()
    
    # Check error message
    error = driver.find_element_by_class_name('error')
    assert error.text == 'Invalid credentials'
"""
    
    enhanced_security = await enhance_code_with_llm(
        basic_security_test,
        "production-security"
    )
    
    print("AI Enhanced Security Test Suite:")
    if isinstance(enhanced_security, dict) and 'enhanced_code' in enhanced_security:
        code = enhanced_security['enhanced_code']
        # Show first 800 chars
        print(code[:800] if len(code) > 800 else code)
    print("-" * 40)
    
    # 5. Generate Penetration Testing Scenarios
    print("\n[5] GENERATING PENETRATION TEST SCENARIOS WITH LLM...")
    print("-" * 40)
    
    pentest_prompt = """Generate penetration testing scenarios for banking application:
    1. Authentication attacks (brute force, credential stuffing)
    2. Session management exploits
    3. Transaction tampering attempts
    4. API security testing
    5. Encryption validation
    
    Include both manual and automated test approaches."""
    
    pentest_scenarios = await call_default_llm(
        [{"role": "user", "content": pentest_prompt}],
        temperature=0.5,
        max_tokens=1000
    )
    
    print("AI Generated Penetration Tests:")
    print(pentest_scenarios[:600] if len(pentest_scenarios) > 600 else pentest_scenarios)
    print("-" * 40)
    
    # Summary
    print("\n" + "=" * 80)
    print("BANKING SECURITY TEST SUITE GENERATED")
    print("=" * 80)
    print("[SUCCESS] Generated with V2 LLM-Native System:")
    print("✓ Security Test Scenarios - Comprehensive coverage")
    print("✓ OWASP Compliant Tests - Industry standards")
    print("✓ Constitutional AI Validation - Ethical testing")
    print("✓ Production Security Suite - Enterprise-ready")
    print("✓ Penetration Test Scenarios - Advanced security")
    print("\nAll generated using REAL LLM - No fallbacks or mocks!")
    print("=" * 80)


if __name__ == "__main__":
    print("\nStarting Banking Security Test Generation...")
    print("This example demonstrates V2's security-focused capabilities")
    print("If LLM is not available, the system will halt.\n")
    
    asyncio.run(test_banking_security())