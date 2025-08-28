#!/usr/bin/env python3
"""
Basic Test Case Generation Examples
==================================

This example demonstrates fundamental test case generation for common QA scenarios.
Run directly: python 01_basic_test_generation.py

No inputs required - all examples are self-contained.
"""

import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import query_llm, StrategyType
import json
from datetime import datetime


def generate_login_tests():
    """Generate comprehensive test cases for login functionality."""
    print("[LOGIN] GENERATING LOGIN TEST CASES")
    print("=" * 50)
    
    messages = [{
        "role": "user",
        "content": """
        Generate comprehensive test cases for a login form with:
        - Email field (required)
        - Password field (required, min 8 chars)
        - Remember Me checkbox (optional)
        - Login button
        - Forgot Password link
        
        Include positive, negative, and edge cases.
        Format as numbered list with Given-When-Then structure.
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT)
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    return response.content


def generate_shopping_cart_tests():
    """Generate test cases for shopping cart functionality."""
    print("[CART] GENERATING SHOPPING CART TEST CASES")
    print("=" * 50)
    
    messages = [{
        "role": "user",
        "content": """
        Generate test cases for an e-commerce shopping cart with:
        - Add items to cart
        - Remove items from cart  
        - Update quantities
        - Apply discount codes
        - Calculate tax and shipping
        - Proceed to checkout
        
        Focus on boundary conditions and error scenarios.
        Include test data examples.
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.TREE_OF_THOUGHTS)
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    return response.content


def generate_api_tests():
    """Generate API test cases for user management."""
    print("[API] GENERATING API TEST CASES")
    print("=" * 50)
    
    messages = [{
        "role": "user",
        "content": """
        Generate API test cases for user management endpoints:
        
        POST /api/users - Create user
        Request: {email, password, name}
        Response: {id, email, name, created_at}
        
        GET /api/users/{id} - Get user details
        Response: {id, email, name, created_at, last_login}
        
        PUT /api/users/{id} - Update user
        Request: {email?, name?}
        Response: {id, email, name, updated_at}
        
        DELETE /api/users/{id} - Delete user
        Response: 204 No Content
        
        Include status codes, error responses, and authentication tests.
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.DECOMPOSED)
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    return response.content


def generate_form_validation_tests():
    """Generate form validation test cases."""
    print("[FORM] GENERATING FORM VALIDATION TEST CASES")
    print("=" * 50)
    
    messages = [{
        "role": "user",
        "content": """
        Generate validation test cases for user registration form:
        
        Fields:
        - Email (required, valid format)
        - Password (required, min 8 chars, must contain uppercase, lowercase, number)
        - Confirm Password (required, must match password)
        - Phone Number (optional, format: +1-XXX-XXX-XXXX)
        - Age (required, 18-120)
        - Terms Checkbox (required)
        
        Generate specific test data for each validation rule.
        Include boundary value analysis.
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.SELF_CONSISTENCY)
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    return response.content


def generate_security_tests():
    """Generate security test cases (safe payloads only)."""
    print("[SECURITY] GENERATING SECURITY TEST CASES")
    print("=" * 50)
    
    messages = [{
        "role": "user",
        "content": """
        Generate security test cases for a web application login form.
        Focus on common vulnerabilities but ONLY use safe test payloads.
        
        Cover:
        - SQL Injection attempts (safe test strings)
        - Cross-Site Scripting (XSS) prevention
        - Authentication bypass attempts
        - Brute force protection
        - Session management
        - Input sanitization
        
        Use only educational examples - no actual exploit code.
        """
    }]
    
    response = query_llm(
        messages, 
        strategy=StrategyType.CONSTITUTIONAL_AI,
        principles=["Only safe test payloads", "No actual exploitation", "Educational purpose only"]
    )
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    return response.content


def save_results(results, filename):
    """Save test results to file."""
    output_file = Path(__file__).parent / filename
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_test_suites": len(results),
        "test_suites": results,
        "generator": "Basic Test Generation Examples"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"[FILE] Results saved to: {output_file}")


def main():
    """Run all basic test generation examples."""
    print("[START] BASIC QA TEST GENERATION EXAMPLES")
    print("=========================================")
    print("Generating comprehensive test cases for common QA scenarios...")
    print()
    
    results = {}
    
    try:
        # Generate different types of test cases
        results["login_tests"] = generate_login_tests()
        results["shopping_cart_tests"] = generate_shopping_cart_tests()
        results["api_tests"] = generate_api_tests()
        results["form_validation_tests"] = generate_form_validation_tests()
        results["security_tests"] = generate_security_tests()
        
        # Save all results
        save_results(results, "basic_test_generation_results.json")
        
        print("[OK] SUCCESS: All test cases generated successfully!")
        print(f"[INFO] Generated {len(results)} test suites")
        print("[FILE] Check basic_test_generation_results.json for complete output")
        
    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()